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
import json
import math
from typing import Optional
from datetime import date
from urllib.parse import urlencode
from urllib.request import urlopen

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsMessageLog,
    QgsPointXY,
    QgsProject,
    QgsRaster,
    QgsRasterLayer,
    Qgis,
)
from qgis.gui import QgsMapToolEmitPoint

from .coordinate_widget import CoordinateFieldWidget, ElevationFieldWidget
from .core.runway import (
    ApproachType,
    Heliponto,
    ProjectType,
    Runway,
    RunwayType,
    SSPVSector,
    Threshold,
)
from .core.surfaces import build_pbzpa_layer, build_pbzph_layer
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
    _NOAA_GEOMAG_KEY = "zNEw7"

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.iface = iface
        self._surfaces_layer = None
        self._opea_layer = None

        # Substituir campos de coordenadas por widgets com mira
        self._setup_coordinate_widgets()
        self._setup_reference_combos()
        self._setup_sysaga_controls()
        self._capture_target: Optional[str] = None
        self._previous_map_tool = None
        self._capture_tool = QgsMapToolEmitPoint(self.iface.mapCanvas())
        self._capture_tool.canvasClicked.connect(self._on_canvas_clicked)

        # Conexões (objectName setado no .ui)
        self.btnGerarSuperficies.clicked.connect(self.on_generate_surfaces)
        self.btnRodarAnalise.clicked.connect(self.on_run_analysis)
        self.btnExportarKML.clicked.connect(self.on_export_kml)
        self.btnExportarDXF.clicked.connect(self.on_export_dxf)
        self.btnSelecionarRaster.clicked.connect(self.on_select_raster)
        self.btnCarregarJSON.clicked.connect(self.on_load_example_json)
        self.btnAlvoA.clicked.connect(lambda: self._start_capture("A"))
        self.btnAlvoB.clicked.connect(lambda: self._start_capture("B"))
        self.btnAlvoHRP.clicked.connect(lambda: self._start_capture("HRP"))
        self.cmbTipoAerodromo.currentIndexChanged.connect(self._refresh_mode_controls)
        self._refresh_mode_controls()

    def _setup_coordinate_widgets(self) -> None:
        """Substitui campos de coordenadas simples por widgets com mira."""
        canvas = self.iface.mapCanvas()
        
        # Criar widgets para coordenadas da cabeceira A
        self.lonA_widget = CoordinateFieldWidget(canvas=canvas, is_longitude=True)
        self.latA_widget = CoordinateFieldWidget(canvas=canvas, is_longitude=False)

        # Criar widgets para coordenadas da cabeceira B
        self.lonB_widget = CoordinateFieldWidget(canvas=canvas, is_longitude=True)
        self.latB_widget = CoordinateFieldWidget(canvas=canvas, is_longitude=False)

        # Criar widgets de elevação com captura de raster
        self.elevA_widget = ElevationFieldWidget(canvas=canvas)
        self.elevB_widget = ElevationFieldWidget(canvas=canvas)
        
        # Substituir campos originais (do .ui) pelos novos widgets
        replacements = {
            self.lineLonA: ("lonA", self.lonA_widget),
            self.lineLatA: ("latA", self.latA_widget),
            self.lineLonB: ("lonB", self.lonB_widget),
            self.lineLatB: ("latB", self.latB_widget),
            self.lineElevA: ("elevA", self.elevA_widget),
            self.lineElevB: ("elevB", self.elevB_widget),
        }

        def _replace_widget(original: QLineEdit, new_widget: QWidget) -> bool:
            parent = original.parentWidget()
            if parent is None:
                return False
            layout = parent.layout()
            if layout is None:
                return False
            if layout.indexOf(original) < 0:
                return False
            layout.replaceWidget(original, new_widget)
            original.hide()
            original.setParent(None)
            return True

        for original, (attr_name, new_widget) in replacements.items():
            if _replace_widget(original, new_widget):
                setattr(self, f"line{attr_name[0].upper()}{attr_name[1:]}", new_widget)
    
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
        # Compatibilidade com UI novo (cmbTipoAerodromo já existe) e antigo.
        if hasattr(self, "cmbTipoAerodromo"):
            self.cmbProjectType = self.cmbTipoAerodromo
            self.cmbProjectType.clear()
            self.cmbProjectType.addItem("Aerodromo (PBZPA)", ProjectType.AERODROME.value)
            self.cmbProjectType.addItem("Heliponto (PBZPH)", ProjectType.HELIPORT.value)
        else:
            self.cmbProjectType = QComboBox(self)
            self.cmbProjectType.addItem("Aerodromo (PBZPA)", ProjectType.AERODROME.value)
            self.cmbProjectType.addItem("Heliponto (PBZPH)", ProjectType.HELIPORT.value)
            if hasattr(self, "formAerodromo"):
                self.formAerodromo.insertRow(0, "Tipo de projeto:", self.cmbProjectType)

        self.cmbSSPV = QComboBox(self)
        self.cmbSSPV.addItem("Sem SSPV", SSPVSector.NONE.value)
        self.cmbSSPV.addItem("Somente setor da cabeceira A", SSPVSector.SECTOR_A.value)
        self.cmbSSPV.addItem("Somente setor da cabeceira B", SSPVSector.SECTOR_B.value)
        self.cmbSSPV.addItem("Ambos os setores", SSPVSector.BOTH.value)
        self.cmbSSPV.setCurrentIndex(3)
        if hasattr(self, "formAerodromo"):
            self.formAerodromo.insertRow(16, "Setor SSPV:", self.cmbSSPV)
        elif hasattr(self, "gridClassificacao"):
            row = max(7, self.gridClassificacao.rowCount())
            self.gridClassificacao.addWidget(QLabel("Setor SSPV:"), row, 0)
            self.gridClassificacao.addWidget(self.cmbSSPV, row, 1)

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
    def _is_heliponto_mode(self) -> bool:
        return self.cmbTipoAerodromo.currentIndex() == 1

    def _refresh_mode_controls(self, *_args) -> None:
        heli_mode = self._is_heliponto_mode()
        self.groupCabA.setEnabled(not heli_mode)
        self.groupCabB.setEnabled(not heli_mode)
        self.groupClassificacao.setEnabled(not heli_mode)
        self.groupHeliponto.setEnabled(heli_mode)

    def _build_runway(self) -> Optional[Runway]:
        try:
            project_data = self.cmbProjectType.currentData() if hasattr(self, "cmbProjectType") else None
            if project_data is None:
                project_type = ProjectType.HELIPORT if self._is_heliponto_mode() else ProjectType.AERODROME
            else:
                project_type = ProjectType(project_data)

            sspv_data = self.cmbSSPV.currentData() if hasattr(self, "cmbSSPV") else None
            sspv_sector = SSPVSector(sspv_data) if sspv_data is not None else SSPVSector.BOTH
            designator_a = self._runway_designator_from_heading(self.lineCabA.text(), "A")
            designator_b = self._runway_designator_from_heading(self.lineCabB.text(), "B")

            th_a = Threshold(
                designator=designator_a,
                longitude=float(self.lineLonA.text().replace(",", ".")),
                latitude=float(self.lineLatA.text().replace(",", ".")),
                elevation_m=float(self.lineElevA.text().replace(",", ".")),
            )
            th_b = Threshold(
                designator=designator_b,
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
                project_type=project_type,
                approach_type_a=ApproachType(self.cmbApproachA.currentData()),
                approach_type_b=ApproachType(self.cmbApproachB.currentData()),
                runway_type=RunwayType(self.cmbRunwayType.currentData()),
                sspv_sector=sspv_sector,
                width_m=float(self.lineLargura.text().replace(",", ".") or 45),
            )
            return rwy
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Dados inválidos", f"Verifique os campos: {exc}")
            return None

    def _build_heliponto(self) -> Optional[Heliponto]:
        try:
            hrp = Threshold(
                designator="HRP",
                longitude=float(self.lineHrpLon.text().replace(",", ".")),
                latitude=float(self.lineHrpLat.text().replace(",", ".")),
                elevation_m=float(self.lineHrpElev.text().replace(",", ".")),
            )
            tlof_diameter = float(self.lineTlofDiameter.text().replace(",", ".") or 25)
            fmgo_diameter = float(self.lineFmgoDiameter.text().replace(",", ".") or 30)
            return Heliponto(
                name=self.lineICAO.text().strip().upper() or "PBZPH",
                hrp=hrp,
                tlof_diameter_m=tlof_diameter,
                fmgo_diameter_m=fmgo_diameter,
            )
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Dados inválidos", f"Verifique os campos do heliponto: {exc}")
            return None

    def _log(self, msg: str, level=Qgis.Info) -> None:
        QgsMessageLog.logMessage(msg, "PBZPA/PBZPH", level=level)

    def _start_capture(self, target: str) -> None:
        self._capture_target = target
        self._previous_map_tool = self.iface.mapCanvas().mapTool()
        self.iface.mapCanvas().setMapTool(self._capture_tool)
        self.iface.messageBar().pushInfo(
            "PBZPA/PBZPH",
            f"Clique no mapa para capturar a cabeceira {target} (longitude, latitude, elevação e declinação magnética).",
        )

    def _restore_map_tool(self) -> None:
        if self._previous_map_tool is not None:
            self.iface.mapCanvas().setMapTool(self._previous_map_tool)
        self._previous_map_tool = None

    def _target_fields(self, target: str):
        if target == "A":
            return self.lineLonA, self.lineLatA, self.lineElevA, self.lineDeclinA
        if target == "HRP":
            return self.lineHrpLon, self.lineHrpLat, self.lineHrpElev, self.lineHrpDecl
        return self.lineLonB, self.lineLatB, self.lineElevB, self.lineDeclinB

    def _format_number(self, value: float, decimals: int) -> str:
        return f"{value:.{decimals}f}"

    def _parse_float(self, text: str) -> Optional[float]:
        raw = text.strip().replace(",", ".")
        if not raw:
            return None
        try:
            return float(raw)
        except ValueError:
            return None

    def _normalize_heading(self, heading_deg: float) -> float:
        return heading_deg % 360.0

    def _true_bearing(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """Retorna rumo verdadeiro inicial de (lon1,lat1) para (lon2,lat2) em graus."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dlon = math.radians(lon2 - lon1)
        y = math.sin(dlon) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlon)
        brng = math.degrees(math.atan2(y, x))
        return self._normalize_heading(brng)

    def _runway_designator_from_heading(self, heading_text: str, fallback: str) -> str:
        heading = self._parse_float(heading_text)
        if heading is None:
            return fallback
        num = int(round(self._normalize_heading(heading) / 10.0))
        if num == 0:
            num = 36
        if num > 36:
            num = 36
        return f"{num:02d}"

    def _fetch_magnetic_declination(self, lon: float, lat: float) -> Optional[float]:
        """Consulta declinação magnética no NOAA Geomag Web API (WMM)."""
        today = date.today()
        params = {
            "lat1": f"{lat:.8f}",
            "lon1": f"{lon:.8f}",
            "startYear": today.year,
            "startMonth": today.month,
            "startDay": today.day,
            "resultFormat": "json",
            "key": self._NOAA_GEOMAG_KEY,
        }
        url = "https://www.ngdc.noaa.gov/geomag-web/calculators/calculateDeclination?" + urlencode(params)
        try:
            with urlopen(url, timeout=6) as response:
                payload = json.loads(response.read().decode("utf-8"))
            result = payload.get("result")
            if isinstance(result, list) and result:
                value = result[0].get("declination")
                if value is not None:
                    return float(value)
            value = payload.get("declination")
            if value is not None:
                return float(value)
        except Exception as exc:  # noqa: BLE001
            self._log(f"Falha ao consultar declinação magnética: {exc}", Qgis.Warning)
        return None

    def _update_runway_magnetic_headings(self) -> None:
        lon_a = self._parse_float(self.lineLonA.text())
        lat_a = self._parse_float(self.lineLatA.text())
        lon_b = self._parse_float(self.lineLonB.text())
        lat_b = self._parse_float(self.lineLatB.text())
        decl_a = self._parse_float(self.lineDeclinA.text())
        decl_b = self._parse_float(self.lineDeclinB.text())

        if None in (lon_a, lat_a, lon_b, lat_b, decl_a, decl_b):
            return

        true_a = self._true_bearing(lon_a, lat_a, lon_b, lat_b)
        true_b = self._true_bearing(lon_b, lat_b, lon_a, lat_a)
        mag_a = self._normalize_heading(true_a + decl_a)
        mag_b = self._normalize_heading(true_b + decl_b)

        self.lineCabA.setText(self._format_number(mag_a, 1))
        self.lineCabB.setText(self._format_number(mag_b, 1))

    def _set_combo_value(self, combo, value: str) -> None:
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _clear_runway_fields(self) -> None:
        self.lineCabA.clear()
        self.lineLonA.clear()
        self.lineLatA.clear()
        self.lineElevA.clear()
        self.lineDeclinA.clear()
        self.lineCabB.clear()
        self.lineLonB.clear()
        self.lineLatB.clear()
        self.lineElevB.clear()
        self.lineDeclinB.clear()

    def _clear_heliponto_fields(self) -> None:
        self.lineHrpLon.clear()
        self.lineHrpLat.clear()
        self.lineHrpElev.clear()
        self.lineHrpDecl.clear()
        self.lineTlofDiameter.clear()
        self.lineFmgoDiameter.clear()

    def on_load_example_json(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Carregar JSON de exemplo", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro", f"Falha ao ler JSON: {exc}")
            return

        tipo = str(payload.get("tipo", "")).lower()
        if tipo == "heliponto" or "tlof" in payload:
            self.cmbTipoAerodromo.setCurrentIndex(1)
            self._clear_heliponto_fields()
            self.lineICAO.setText(payload.get("icao_code", payload.get("name", "PBZPH")))
            tlof = payload.get("tlof", {}).get("centro", {})
            self.lineHrpLon.setText(str(tlof.get("longitude", "")))
            self.lineHrpLat.setText(str(tlof.get("latitude", "")))
            self.lineHrpElev.setText(str(tlof.get("elevation_m", "")))
            self.lineHrpDecl.clear()
            self.lineTlofDiameter.setText(str(payload.get("tlof", {}).get("diametro_m", 25)))
            self.lineFmgoDiameter.setText(str(payload.get("fmgo", {}).get("diametro_m", 30)))
            return

        thresholds = payload.get("thresholds", {})
        self.cmbTipoAerodromo.setCurrentIndex(0)
        self._clear_runway_fields()
        self.lineICAO.setText(payload.get("icao_code", "----"))
        self.lineCabA.setText(str(thresholds.get("A", {}).get("rumo_magnetico", thresholds.get("A", {}).get("magnetic_heading_deg", ""))))
        self.lineLonA.setText(str(thresholds.get("A", {}).get("longitude", "")))
        self.lineLatA.setText(str(thresholds.get("A", {}).get("latitude", "")))
        self.lineElevA.setText(str(thresholds.get("A", {}).get("elevation_m", "")))
        self.lineCabB.setText(str(thresholds.get("B", {}).get("rumo_magnetico", thresholds.get("B", {}).get("magnetic_heading_deg", ""))))
        self.lineLonB.setText(str(thresholds.get("B", {}).get("longitude", "")))
        self.lineLatB.setText(str(thresholds.get("B", {}).get("latitude", "")))
        self.lineElevB.setText(str(thresholds.get("B", {}).get("elevation_m", "")))
        self.lineDeclinA.clear()
        self.lineDeclinB.clear()
        self._set_combo_value(self.cmbCodeNumber, str(payload.get("code_number", 1)))
        self._set_combo_value(self.cmbCodeLetter, str(payload.get("code_letter", "A")).upper())
        self._set_combo_value(self.cmbRunwayType, str(payload.get("runway_type", "non_instrument")))
        self._set_combo_value(self.cmbApproachA, str(thresholds.get("A", {}).get("approach_type", "visual")))
        self._set_combo_value(self.cmbApproachB, str(thresholds.get("B", {}).get("approach_type", "visual")))
        self._update_runway_magnetic_headings()

    def _find_raster_layer(self) -> Optional[QgsRasterLayer]:
        path = self.lineRaster.text().strip()
        if path:
            raster = QgsRasterLayer(path, os.path.basename(path) or "pbzpa_raster")
            if raster.isValid():
                return raster
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsRasterLayer) and layer.isValid():
                return layer
        return None

    def _sample_elevation(self, point: QgsPointXY) -> Optional[float]:
        raster = self._find_raster_layer()
        if raster is None:
            return None
        try:
            canvas_crs = self.iface.mapCanvas().mapSettings().destinationCrs()
            to_raster = QgsCoordinateTransform(canvas_crs, raster.crs(), QgsProject.instance())
            raster_point = to_raster.transform(point)
            result = raster.dataProvider().identify(raster_point, QgsRaster.IdentifyFormatValue)
            if not result.isValid():
                return None
            values = result.results()
            for band in sorted(values):
                value = values[band]
                if value is None:
                    continue
                try:
                    return float(value)
                except (TypeError, ValueError):
                    continue
        except Exception as exc:  # noqa: BLE001
            self._log(f"Falha ao amostrar elevação: {exc}", Qgis.Warning)
        return None

    def _on_canvas_clicked(self, point, button) -> None:
        if self._capture_target is None or button != Qt.LeftButton:
            return

        try:
            canvas = self.iface.mapCanvas()
            to_geo = QgsCoordinateTransform(
                canvas.mapSettings().destinationCrs(),
                QgsCoordinateReferenceSystem("EPSG:4326"),
                QgsProject.instance(),
            )
            geo_point = to_geo.transform(point)
            elevation = self._sample_elevation(point)
            lon_field, lat_field, elev_field, decl_field = self._target_fields(self._capture_target)
            lon_field.setText(self._format_number(geo_point.x(), 8))
            lat_field.setText(self._format_number(geo_point.y(), 8))
            if elevation is not None:
                elev_field.setText(self._format_number(elevation, 2))
            else:
                QMessageBox.information(
                    self,
                    "Elevação não encontrada",
                    "As coordenadas foram preenchidas, mas não foi possível extrair a elevação do raster disponível.",
                )

            declination = self._fetch_magnetic_declination(geo_point.x(), geo_point.y())
            if declination is not None:
                decl_field.setText(self._format_number(declination, 2))
            else:
                decl_field.setText("")
                QMessageBox.warning(
                    self,
                    "Declinação indisponível",
                    "Não foi possível obter a declinação magnética para o ponto selecionado.",
                )

            if self._capture_target in ("A", "B"):
                self._update_runway_magnetic_headings()
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, "Erro", f"Falha ao capturar ponto no mapa: {exc}")
        finally:
            self._capture_target = None
            self._restore_map_tool()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def on_generate_surfaces(self) -> None:
        try:
            if self._is_heliponto_mode():
                heliport = self._build_heliponto()
                if heliport is None:
                    return
                layer = build_pbzph_layer(heliport)
            else:
                runway = self._build_runway()
                if runway is None:
                    return
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
            # Propagar caminho do raster para widgets de elevação
            if hasattr(self, "elevA_widget"):
                self.elevA_widget.set_raster_path(path)
            if hasattr(self, "elevB_widget"):
                self.elevB_widget.set_raster_path(path)

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
