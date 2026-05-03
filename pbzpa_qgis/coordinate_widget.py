# -*- coding: utf-8 -*-
"""Widget de campo de coordenada com botão de mira para seleção no mapa."""

from __future__ import annotations

from typing import Optional

from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QWidget,
    QLineEdit,
)
from qgis.core import QgsCoordinateTransform, QgsPointXY, QgsProject, QgsCoordinateReferenceSystem
from qgis.gui import QgsMapToolEmitPoint, QgsMapCanvas


class CoordinateMapTool(QgsMapToolEmitPoint):
    """Map tool para capturar coordenadas ao clicar no mapa."""
    
    coordinate_selected = pyqtSignal(QgsPointXY)
    
    def __init__(self, canvas: QgsMapCanvas):
        super().__init__(canvas)
        self.setCursor(Qt.CrossCursor)
    
    def canvasReleaseEvent(self, event):
        """Captura o ponto ao liberar o clique do mouse."""
        point = self.toMapCoordinates(event.pos())
        
        # Transforma para WGS84 (EPSG:4326) se necessário
        project_crs = QgsProject.instance().crs()
        if project_crs and project_crs.isValid():
            wgs84_crs = QgsCoordinateReferenceSystem.fromEpsgId(4326)
            if wgs84_crs.isValid() and project_crs.authid() != "EPSG:4326":
                try:
                    transform = QgsCoordinateTransform(
                        project_crs,
                        wgs84_crs,
                        QgsProject.instance()
                    )
                    point = transform.transform(point)
                except Exception:
                    # Se falhar, mantém o ponto original
                    pass
        
        self.coordinate_selected.emit(point)


class CoordinateFieldWidget(QWidget):
    """Widget com campo de entrada de coordenada e botão de mira."""
    
    value_changed = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None, canvas: Optional[QgsMapCanvas] = None):
        super().__init__(parent)
        self.canvas = canvas
        self.map_tool: Optional[CoordinateMapTool] = None
        self._is_longitude = True  # Padrão: assume longitude
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Valor decimal...")
        self.input_field.textChanged.connect(self.value_changed.emit)
        layout.addWidget(self.input_field)
        
        self.btn_crosshair = QPushButton(self)
        self.btn_crosshair.setMaximumWidth(32)
        self.btn_crosshair.setToolTip("Clicar no mapa para capturar coordenada")
        
        # Tenta usar ícone do QGIS, senão usa caractere
        try:
            icon = QIcon(":/images/themes/default/mActionEditTable.svg")
            if not icon.isNull():
                self.btn_crosshair.setIcon(icon)
        except Exception:
            pass
        
        if not self.btn_crosshair.icon() or self.btn_crosshair.icon().isNull():
            self.btn_crosshair.setText("⊕")
        
        self.btn_crosshair.clicked.connect(self.on_crosshair_clicked)
        layout.addWidget(self.btn_crosshair)
        
        self.setLayout(layout)
    
    def set_canvas(self, canvas: QgsMapCanvas) -> None:
        """Define o mapa para captura de coordenadas."""
        self.canvas = canvas
    
    def setText(self, text: str) -> None:
        """Define o texto do campo de entrada."""
        self.input_field.setText(text)
    
    def text(self) -> str:
        """Retorna o texto do campo de entrada."""
        return self.input_field.text()
    
    def on_crosshair_clicked(self) -> None:
        """Ativa o modo de seleção de coordenada no mapa."""
        if not self.canvas:
            return
        
        if self.map_tool is None:
            self.map_tool = CoordinateMapTool(self.canvas)
            self.map_tool.coordinate_selected.connect(self.on_coordinate_selected)
        
        self.canvas.setMapTool(self.map_tool)
        self.btn_crosshair.setStyleSheet("background-color: #90EE90;")
    
    def on_coordinate_selected(self, point: QgsPointXY) -> None:
        """Callback ao selecionar coordenada no mapa."""
        # Extrai x (longitude) ou y (latitude) baseado no tipo de campo
        if hasattr(self, '_is_longitude') and self._is_longitude:
            coord_value = point.x()
        else:
            coord_value = point.y()
        
        # Formata com 6 casas decimais (precisão até ~0.1m em graus decimais)
        formatted = f"{coord_value:.6f}"
        
        # Substitui ponto por vírgula se necessário (formato brasileiro)
        self.setText(formatted.replace(".", ","))
        
        # Remove destaque do botão
        self.btn_crosshair.setStyleSheet("")
        
        # Volta para ferramenta anterior se havia uma
        if self.canvas:
            self.canvas.unsetMapTool(self.map_tool)
    
    def mark_as_latitude(self) -> None:
        """Marca este widget como campo de latitude (não longitude)."""
        self._is_longitude = False
    
    def mark_as_longitude(self) -> None:
        """Marca este widget como campo de longitude."""
        self._is_longitude = True
