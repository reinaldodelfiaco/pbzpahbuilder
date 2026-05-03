# -*- coding: utf-8 -*-
"""Widgets de coordenada e elevação com captura direta no mapa QGIS."""

from __future__ import annotations

import os
from typing import Optional

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QColor, QIcon
from qgis.PyQt.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsMapLayer,
    QgsPointXY,
    QgsProject,
    QgsRasterLayer,
)
from qgis.gui import QgsMapCanvas, QgsMapToolEmitPoint

_PLUGIN_DIR = os.path.dirname(__file__)
_CROSSHAIR_SVG = os.path.join(_PLUGIN_DIR, "resources", "crosshair.svg")

# Limites geográficos aproximados do Brasil (WGS84)
_BRAZIL_LON_MIN = -74.0
_BRAZIL_LON_MAX = -28.5
_BRAZIL_LAT_MIN = -33.9
_BRAZIL_LAT_MAX = 5.4

_STYLE_OK = ""
_STYLE_WARN = "background-color: #FFF3CD; border: 1px solid #FFC107;"   # amarelo
_STYLE_ERR  = "background-color: #FDDEDE; border: 1px solid #DC3545;"   # vermelho


def _make_crosshair_icon() -> QIcon:
    """Carrega o SVG de mira do diretório resources do plugin."""
    if os.path.isfile(_CROSSHAIR_SVG):
        icon = QIcon(_CROSSHAIR_SVG)
        if not icon.isNull():
            return icon
    # Fallback: ícone nativo do QGIS
    icon = QIcon(":/images/themes/default/mActionSetProjection.svg")
    if not icon.isNull():
        return icon
    return QIcon()


class CoordinateMapTool(QgsMapToolEmitPoint):
    """Map tool: emite QgsPointXY em WGS84 ao clicar no mapa."""

    coordinate_selected = pyqtSignal(QgsPointXY)

    def __init__(self, canvas: QgsMapCanvas) -> None:
        super().__init__(canvas)
        self.setCursor(Qt.CrossCursor)

    def canvasReleaseEvent(self, event) -> None:  # noqa: N802
        point = self.toMapCoordinates(event.pos())
        project_crs = QgsProject.instance().crs()
        if project_crs and project_crs.isValid():
            wgs84 = QgsCoordinateReferenceSystem.fromEpsgId(4326)
            if wgs84.isValid() and project_crs.authid() != "EPSG:4326":
                try:
                    xform = QgsCoordinateTransform(
                        project_crs, wgs84, QgsProject.instance()
                    )
                    point = xform.transform(point)
                except Exception:
                    pass
        self.coordinate_selected.emit(point)


class RasterElevationMapTool(QgsMapToolEmitPoint):
    """Map tool: emite elevação amostrada do raster ao clicar no mapa."""

    elevation_selected = pyqtSignal(float)

    def __init__(self, canvas: QgsMapCanvas, raster_path: str = "") -> None:
        super().__init__(canvas)
        self.setCursor(Qt.CrossCursor)
        self.raster_path = raster_path  # caminho ao raster, pode ser atualizado

    def canvasReleaseEvent(self, event) -> None:  # noqa: N802
        map_point = self.toMapCoordinates(event.pos())

        # 1. Encontrar raster: primeiro o configurado, depois o primeiro da legenda
        raster_layer: Optional[QgsRasterLayer] = None
        if self.raster_path and os.path.isfile(self.raster_path):
            raster_layer = QgsRasterLayer(self.raster_path, "_elev_tmp", "gdal")

        if raster_layer is None or not raster_layer.isValid():
            for lyr in QgsProject.instance().mapLayers().values():
                if isinstance(lyr, QgsRasterLayer) and lyr.isValid():
                    raster_layer = lyr
                    break

        if raster_layer is None:
            return

        # 2. Transformar ponto para CRS do raster, se necessário
        sample_point = map_point
        project_crs = QgsProject.instance().crs()
        raster_crs = raster_layer.crs()
        if project_crs.isValid() and raster_crs.isValid() and project_crs != raster_crs:
            try:
                xform = QgsCoordinateTransform(
                    project_crs, raster_crs, QgsProject.instance()
                )
                sample_point = xform.transform(map_point)
            except Exception:
                pass

        # 3. Amostrar banda 1
        provider = raster_layer.dataProvider()
        result, ok = provider.sample(sample_point, 1)
        if ok and result is not None:
            self.elevation_selected.emit(float(result))


class CoordinateFieldWidget(QWidget):
    """QLineEdit + botão mira para longitude ou latitude.

    Validação em tempo real: fundo amarelo se fora dos limites do Brasil,
    fundo vermelho se o valor não pode ser interpretado como número.
    """

    value_changed = pyqtSignal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        canvas: Optional[QgsMapCanvas] = None,
        is_longitude: bool = True,
    ) -> None:
        super().__init__(parent)
        self.canvas = canvas
        self.map_tool: Optional[CoordinateMapTool] = None
        self._is_longitude = is_longitude

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText(
            "Longitude decimal..." if is_longitude else "Latitude decimal..."
        )
        self.input_field.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.input_field)

        self.btn_crosshair = QPushButton(self)
        self.btn_crosshair.setFixedSize(26, 26)
        self.btn_crosshair.setToolTip("Capturar coordenada clicando no mapa")
        icon = _make_crosshair_icon()
        if not icon.isNull():
            self.btn_crosshair.setIcon(icon)
        else:
            self.btn_crosshair.setText("⊕")
        self.btn_crosshair.clicked.connect(self.on_crosshair_clicked)
        layout.addWidget(self.btn_crosshair)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    # Validação de intervalo
    # ------------------------------------------------------------------
    def _on_text_changed(self, text: str) -> None:
        self._validate(text)
        self.value_changed.emit(text)

    def _validate(self, text: str) -> None:
        raw = text.strip().replace(",", ".")
        if not raw:
            self.input_field.setStyleSheet(_STYLE_OK)
            return
        try:
            val = float(raw)
        except ValueError:
            self.input_field.setStyleSheet(_STYLE_ERR)
            self.input_field.setToolTip("Valor inválido: use número decimal.")
            return

        if self._is_longitude:
            in_range = _BRAZIL_LON_MIN <= val <= _BRAZIL_LON_MAX
            tip = f"Longitude fora do Brasil ({_BRAZIL_LON_MIN} a {_BRAZIL_LON_MAX})"
        else:
            in_range = _BRAZIL_LAT_MIN <= val <= _BRAZIL_LAT_MAX
            tip = f"Latitude fora do Brasil ({_BRAZIL_LAT_MIN} a {_BRAZIL_LAT_MAX})"

        if in_range:
            self.input_field.setStyleSheet(_STYLE_OK)
            self.input_field.setToolTip("")
        else:
            self.input_field.setStyleSheet(_STYLE_WARN)
            self.input_field.setToolTip(tip)

    # ------------------------------------------------------------------
    # API pública compatível com QLineEdit
    # ------------------------------------------------------------------
    def setText(self, text: str) -> None:
        self.input_field.setText(text)

    def text(self) -> str:
        return self.input_field.text()

    def set_canvas(self, canvas: QgsMapCanvas) -> None:
        self.canvas = canvas

    def mark_as_latitude(self) -> None:
        self._is_longitude = False
        self.input_field.setPlaceholderText("Latitude decimal...")

    def mark_as_longitude(self) -> None:
        self._is_longitude = True
        self.input_field.setPlaceholderText("Longitude decimal...")

    # ------------------------------------------------------------------
    # Captura no mapa
    # ------------------------------------------------------------------
    def on_crosshair_clicked(self) -> None:
        if not self.canvas:
            return
        if self.map_tool is None:
            self.map_tool = CoordinateMapTool(self.canvas)
            self.map_tool.coordinate_selected.connect(self._on_coordinate_selected)
        self.canvas.setMapTool(self.map_tool)
        self.btn_crosshair.setStyleSheet("background-color: #90EE90;")

    def _on_coordinate_selected(self, point: QgsPointXY) -> None:
        coord_value = point.x() if self._is_longitude else point.y()
        self.setText(f"{coord_value:.6f}".replace(".", ","))
        self.btn_crosshair.setStyleSheet("")
        if self.canvas:
            self.canvas.unsetMapTool(self.map_tool)


class ElevationFieldWidget(QWidget):
    """QLineEdit + botão mira que amostra elevação no raster ao clicar.

    Se nenhum raster estiver carregado, o botão fica inativo e o campo
    funciona como entrada manual normal.
    """

    value_changed = pyqtSignal(str)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        canvas: Optional[QgsMapCanvas] = None,
        raster_path: str = "",
    ) -> None:
        super().__init__(parent)
        self.canvas = canvas
        self.raster_path = raster_path
        self.map_tool: Optional[RasterElevationMapTool] = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Elevação (m)...")
        self.input_field.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.input_field)

        self.btn_crosshair = QPushButton(self)
        self.btn_crosshair.setFixedSize(26, 26)
        self.btn_crosshair.setToolTip(
            "Capturar elevação do raster clicando no mapa\n"
            "(requer camada raster carregada ou selecionada na aba Imagem)"
        )
        icon = _make_crosshair_icon()
        if not icon.isNull():
            self.btn_crosshair.setIcon(icon)
        else:
            self.btn_crosshair.setText("⊕")
        self.btn_crosshair.clicked.connect(self.on_crosshair_clicked)
        layout.addWidget(self.btn_crosshair)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    # Validação básica (número não negativo razoável para aeródromos)
    # ------------------------------------------------------------------
    def _on_text_changed(self, text: str) -> None:
        raw = text.strip().replace(",", ".")
        if raw:
            try:
                val = float(raw)
                # Aeródromos brasileiros: -50m (abaixo do mar) a ~4000m
                if val < -50 or val > 4000:
                    self.input_field.setStyleSheet(_STYLE_WARN)
                    self.input_field.setToolTip("Elevação fora do intervalo esperado (-50 a 4000 m)")
                else:
                    self.input_field.setStyleSheet(_STYLE_OK)
                    self.input_field.setToolTip("")
            except ValueError:
                self.input_field.setStyleSheet(_STYLE_ERR)
                self.input_field.setToolTip("Valor inválido: use número decimal.")
        else:
            self.input_field.setStyleSheet(_STYLE_OK)
        self.value_changed.emit(text)

    # ------------------------------------------------------------------
    # API pública compatível com QLineEdit
    # ------------------------------------------------------------------
    def setText(self, text: str) -> None:
        self.input_field.setText(text)

    def text(self) -> str:
        return self.input_field.text()

    def set_canvas(self, canvas: QgsMapCanvas) -> None:
        self.canvas = canvas

    def set_raster_path(self, path: str) -> None:
        """Atualiza o caminho do raster usado para amostrar elevação."""
        self.raster_path = path
        if self.map_tool is not None:
            self.map_tool.raster_path = path

    # ------------------------------------------------------------------
    # Captura no mapa
    # ------------------------------------------------------------------
    def on_crosshair_clicked(self) -> None:
        if not self.canvas:
            return
        if self.map_tool is None:
            self.map_tool = RasterElevationMapTool(self.canvas, self.raster_path)
            self.map_tool.elevation_selected.connect(self._on_elevation_selected)
        else:
            self.map_tool.raster_path = self.raster_path
        self.canvas.setMapTool(self.map_tool)
        self.btn_crosshair.setStyleSheet("background-color: #90EE90;")

    def _on_elevation_selected(self, elevation: float) -> None:
        self.setText(f"{elevation:.2f}".replace(".", ","))
        self.btn_crosshair.setStyleSheet("")
        if self.canvas:
            self.canvas.unsetMapTool(self.map_tool)
