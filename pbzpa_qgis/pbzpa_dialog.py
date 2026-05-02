# -*- coding: utf-8 -*-
"""Diálogo principal do plugin PBZPA/PBZPH.

Carrega o ``ui/pbzpa_dialog.ui`` (Qt Designer) e conecta os botões aos
módulos de geração, detecção e exportação. O diálogo contém abas:

1. **Aeródromo** — designação, código pista, cabeceiras, operação.
2. **Imagem & OPEA** — raster de entrada, modelo ML, importação alternativa.
3. **Superfícies** — gerar / visualizar / estilizar.
4. **Análise** — rodar conflito OPEA × superfícies.
5. **Exportação** — KML e DXF/DWG.
"""
from __future__ import annotations

import os
from typing import Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from qgis.core import (
    QgsMessageLog,
    QgsProject,
    Qgis,
)

from .core.runway import ApproachType, ProjectType, Runway, RunwayType, SSPVSector, Threshold
from .core.surfaces import build_pbzpa_layer
from .core.opea_detection import create_opea_layer
from .core.conflict_analysis import analyze_conflicts
from .export.kml_exporter import export_layers_to_kml
from .export.dxf_exporter import export_to_dxf
from .export.sysaga_exporter import (
    elevations_csv_text,
    export_sysaga_package,
    informational_sheet_html,
)

PLUGIN_DIR = os.path.dirname(__file__)
UI_PATH = os.path.join(PLUGIN_DIR, "ui", "pbzpa_dialog.ui")
FORM_CLASS, _ = uic.loadUiType(UI_PATH)


class PBZPADialog(QDialog, FORM_CLASS):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self._surfaces_layer = None
        self._opea_layer = None
        self._setup_reference_combos()
        self._setup_sysaga_controls()

        # Conexões (objectName setado no .ui)
        self.btnGerarSuperficies.clicked.connect(self.on_generate_surfaces)
        self.btnRodarAnalise.clicked.connect(self.on_run_analysis)
        self.btnExportarKML.clicked.connect(self.on_export_kml)
        self.btnExportarDXF.clicked.connect(self.on_export_dxf)
        self.btnSelecionarRaster.clicked.connect(self.on_select_raster)

    def _setup_reference_combos(self) -> None:
        """Preenche combos que o Qt Designer deixa vazios ou sem userData."""
        if self.cmbRunwayType.count() == 0:
            self.cmbRunwayType.addItem("Nao instrumento", RunwayType.NON_INSTRUMENT.value)
            self.cmbRunwayType.addItem("Instrumento", RunwayType.INSTRUMENT.value)

        for combo in (self.cmbApproachA, self.cmbApproachB):
            if combo.count() == 0:
                combo.addItem("Nao opera", ApproachType.NOT_OPERATIONAL.value)
                combo.addItem("Visual", ApproachType.VISUAL.value)
                combo.addItem("Nao precisao", ApproachType.NON_PRECISION.value)
                combo.addItem("Precisao CAT I", ApproachType.PRECISION_CAT_I.value)
                combo.addItem("Precisao CAT II", ApproachType.PRECISION_CAT_II.value)
                combo.addItem("Precisao CAT III", ApproachType.PRECISION_CAT_III.value)
                combo.setCurrentIndex(1)

    def _setup_sysaga_controls(self) -> None:
        """Adiciona campos/exportadores usados para conferir os dados do SYSAGA."""
        self.cmbProjectType = QComboBox(self)
        self.cmbProjectType.addItem("Aerodromo (PBZPA)", ProjectType.AERODROME.value)
        self.cmbProjectType.addItem("Heliponto (PBZPH)", ProjectType.HELIPORT.value)
        self.formAerodromo.insertRow(0, "Tipo de projeto:", self.cmbProjectType)

        self.cmbSSPV = QComboBox(self)
        self.cmbSSPV.addItem("Sem SSPV", SSPVSector.NONE.value)
        self.cmbSSPV.addItem("Somente setor da cabeceira A", SSPVSector.SECTOR_A.value)
        self.cmbSSPV.addItem("Somente setor da cabeceira B", SSPVSector.SECTOR_B.value)
        self.cmbSSPV.addItem("Ambos os setores", SSPVSector.BOTH.value)
        self.cmbSSPV.setCurrentIndex(3)
        self.formAerodromo.insertRow(16, "Setor SSPV:", self.cmbSSPV)

        self.tabSysaga = QWidget(self)
        layout = QVBoxLayout(self.tabSysaga)
        layout.addWidget(QLabel("Pre-visualizacao da ficha informativa e da planilha de elevacoes.", self.tabSysaga))
        actions = QHBoxLayout()
        self.btnVisualizarFicha = QPushButton("Visualizar ficha informativa", self.tabSysaga)
        self.btnVisualizarElevacoes = QPushButton("Visualizar planilha de elevacoes", self.tabSysaga)
        self.btnExportarSysaga = QPushButton("Exportar ficha e planilha", self.tabSysaga)
        actions.addWidget(self.btnVisualizarFicha)
        actions.addWidget(self.btnVisualizarElevacoes)
        actions.addWidget(self.btnExportarSysaga)
        layout.addLayout(actions)
        self.txtSysagaPreview = QTextEdit(self.tabSysaga)
        self.txtSysagaPreview.setReadOnly(True)
        layout.addWidget(self.txtSysagaPreview)
        self.tabWidget.addTab(self.tabSysaga, "5. SYSAGA")

        self.btnVisualizarFicha.clicked.connect(self.on_preview_info_sheet)
        self.btnVisualizarElevacoes.clicked.connect(self.on_preview_elevations)
        self.btnExportarSysaga.clicked.connect(self.on_export_sysaga)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_runway(self) -> Optional[Runway]:
        try:
            th_a = Threshold(
                designator=self.lineCabA.text().strip() or "A",
                longitude=float(self.lineLonA.text().replace(",", ".")),
                latitude=float(self.lineLatA.text().replace(",", ".")),
                elevation_m=float(self.lineElevA.text().replace(",", ".")),
            )
            th_b = Threshold(
                designator=self.lineCabB.text().strip() or "B",
                longitude=float(self.lineLonB.text().replace(",", ".")),
                latitude=float(self.lineLatB.text().replace(",", ".")),
                elevation_m=float(self.lineElevB.text().replace(",", ".")),
            )
            rwy = Runway(
                icao_code=self.lineICAO.text().strip().upper() or "----",
                threshold_a=th_a,
                threshold_b=th_b,
                code_number=int(self.cmbCodeNumber.currentText()),
                code_letter=self.cmbCodeLetter.currentText(),
                project_type=ProjectType(self.cmbProjectType.currentData()),
                approach_type_a=ApproachType(self.cmbApproachA.currentData()),
                approach_type_b=ApproachType(self.cmbApproachB.currentData()),
                runway_type=RunwayType(self.cmbRunwayType.currentData()),
                sspv_sector=SSPVSector(self.cmbSSPV.currentData()),
                width_m=float(self.lineLargura.text().replace(",", ".") or 45),
            )
            return rwy
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Dados inválidos", f"Verifique os campos: {exc}")
            return None

    def _log(self, msg: str, level=Qgis.Info) -> None:
        QgsMessageLog.logMessage(msg, "PBZPA/PBZPH", level=level)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def on_generate_surfaces(self) -> None:
        runway = self._build_runway()
        if runway is None:
            return
        if runway.project_type == ProjectType.HELIPORT:
            QMessageBox.warning(
                self,
                "PBZPH em conferência",
                "O modo Heliponto foi selecionado, mas a geração PBZPH está bloqueada "
                "até a conferência dos campos autenticados do Anexo B do SYSAGA.",
            )
            return
        try:
            layer = build_pbzpa_layer(runway)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro", f"Falha na geração: {exc}")
            self._log(str(exc), Qgis.Critical)
            return
        QgsProject.instance().addMapLayer(layer)
        self._surfaces_layer = layer

        # Cria camada OPEA vazia, alinhada ao mesmo CRS
        if self._opea_layer is None:
            self._opea_layer = create_opea_layer(layer.crs())
            QgsProject.instance().addMapLayer(self._opea_layer)
        QMessageBox.information(self, "OK", "Superfícies geradas. Edite a camada OPEA para incluir os obstáculos.")

    def on_select_raster(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar imagem de satélite",
            "", "Rasters (*.tif *.tiff *.img *.vrt)"
        )
        if path:
            self.lineRaster.setText(path)

    def on_run_analysis(self) -> None:
        if self._surfaces_layer is None or self._opea_layer is None:
            QMessageBox.warning(self, "Atenção", "Gere as superfícies e a camada OPEA antes da análise.")
            return
        try:
            n_violacoes = analyze_conflicts(self._opea_layer, self._surfaces_layer)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro", f"Falha na análise: {exc}")
            self._log(str(exc), Qgis.Critical)
            return
        QMessageBox.information(
            self, "Análise concluída",
            f"OPEAs em violação: {n_violacoes}.\nVeja a coluna 'conflito' na tabela de atributos."
        )

    def on_export_kml(self) -> None:
        if self._surfaces_layer is None:
            QMessageBox.warning(self, "Atenção", "Nada para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar KML/KMZ", "", "KML (*.kml);;KMZ (*.kmz)")
        if not path:
            return
        try:
            layers = [self._surfaces_layer]
            if self._opea_layer is not None:
                layers.append(self._opea_layer)
            out = export_layers_to_kml(layers, path)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro", f"Falha na exportação KML: {exc}")
            return
        QMessageBox.information(self, "Exportação", f"Arquivo gerado:\n{out}")

    def on_export_dxf(self) -> None:
        if self._surfaces_layer is None:
            QMessageBox.warning(self, "Atenção", "Nada para exportar.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Salvar DXF", "", "DXF (*.dxf)")
        if not path:
            return
        convert = self.chkConverterDWG.isChecked()
        try:
            res = export_to_dxf(
                self._surfaces_layer, self._opea_layer, path, convert_to_dwg=convert
            )
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro", f"Falha na exportação DXF: {exc}")
            return
        msg = f"DXF gerado em:\n{res.dxf_path}"
        if res.dwg_path:
            msg += f"\nDWG gerado em:\n{res.dwg_path}"
        QMessageBox.information(self, "Exportação", msg)

    def on_preview_info_sheet(self) -> None:
        runway = self._build_runway()
        if runway is None:
            return
        if runway.project_type == ProjectType.HELIPORT:
            QMessageBox.warning(
                self,
                "Ficha PBZPH em conferência",
                "A ficha de heliponto depende dos campos autenticados do Anexo B do SYSAGA. "
                "Como o SYSAGA redirecionou para login, a geração foi bloqueada para evitar dados incompatíveis.",
            )
            return
        self.txtSysagaPreview.setHtml(informational_sheet_html(runway))

    def on_preview_elevations(self) -> None:
        if self._surfaces_layer is None:
            QMessageBox.warning(self, "Atenção", "Gere as superfícies antes de visualizar a planilha.")
            return
        self.txtSysagaPreview.setPlainText(elevations_csv_text(self._surfaces_layer))

    def on_export_sysaga(self) -> None:
        runway = self._build_runway()
        if runway is None:
            return
        if runway.project_type == ProjectType.HELIPORT:
            QMessageBox.warning(
                self,
                "Exportação PBZPH em conferência",
                "A exportação da ficha e da planilha PBZPH está bloqueada até a conferência "
                "dos campos autenticados do Anexo B do SYSAGA.",
            )
            return
        if self._surfaces_layer is None:
            QMessageBox.warning(self, "Atenção", "Gere as superfícies antes de exportar a planilha de elevações.")
            return
        output_dir = QFileDialog.getExistingDirectory(self, "Selecionar pasta de saída")
        if not output_dir:
            return
        try:
            package = export_sysaga_package(runway, self._surfaces_layer, output_dir)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro", f"Falha ao exportar arquivos SYSAGA: {exc}")
            return
        QMessageBox.information(
            self,
            "Exportação SYSAGA",
            "Arquivos gerados:\n"
            f"{package.info_html_path}\n"
            f"{package.elevations_csv_path}",
        )
