# -*- coding: utf-8 -*-
"""
Classe principal do plugin PBZPA/PBZPH.

Responsabilidades:
- Registrar a ação de menu/toolbar do QGIS.
- Instanciar o diálogo principal sob demanda.
- Registrar o Processing Provider (algoritmos batch).
- Internacionalização (i18n).
"""
from __future__ import annotations

import os
from typing import Optional

from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator, qVersion
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication, QgsMessageLog, Qgis

PLUGIN_NAME = "PBZPA/PBZPH"
PLUGIN_DIR = os.path.dirname(__file__)
ICON_PATH = os.path.join(PLUGIN_DIR, "resources", "icon.png")


class PBZPAPlugin:
    """Implementa a interface esperada pelo QGIS para um plugin Python."""

    def __init__(self, iface):
        self.iface = iface
        self.actions: list[QAction] = []
        self.menu = self.tr("&PBZPA/PBZPH")
        self._dialog = None  # criado sob demanda
        self._provider = None

        # i18n -----------------------------------------------------
        locale = QSettings().value("locale/userLocale", "pt_BR")[0:5]
        locale_path = os.path.join(PLUGIN_DIR, "i18n", f"pbzpa_{locale}.qm")
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > "4.3.3":
                QCoreApplication.installTranslator(self.translator)

    # ------------------------------------------------------------------
    # i18n helper
    # ------------------------------------------------------------------
    @staticmethod
    def tr(message: str) -> str:
        return QCoreApplication.translate("PBZPAPlugin", message)

    # ------------------------------------------------------------------
    # Ciclo de vida QGIS
    # ------------------------------------------------------------------
    def initGui(self):  # noqa: N802 (assinatura definida pelo QGIS)
        """Cria botões de toolbar e itens de menu."""
        icon = QIcon(ICON_PATH) if os.path.exists(ICON_PATH) else QIcon()
        action = QAction(icon, self.tr("Gerar PBZPA/PBZPH"), self.iface.mainWindow())
        action.triggered.connect(self.run)
        action.setEnabled(True)
        action.setStatusTip(self.tr("Abrir o diálogo de geração de PBZPA/PBZPH"))
        self.iface.addPluginToMenu(self.menu, action)
        self.iface.addToolBarIcon(action)
        self.actions.append(action)

        # Processing provider (algoritmos batch) ---------------------
        try:
            from .processing_provider import PBZPAProcessingProvider
            self._provider = PBZPAProcessingProvider()
            QgsApplication.processingRegistry().addProvider(self._provider)
        except Exception as exc:  # noqa: BLE001
            QgsMessageLog.logMessage(
                f"Falha ao registrar Processing Provider: {exc}",
                PLUGIN_NAME,
                level=Qgis.Warning,
            )

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        self.actions.clear()
        if self._provider is not None:
            QgsApplication.processingRegistry().removeProvider(self._provider)
            self._provider = None
        self._dialog = None

    # ------------------------------------------------------------------
    # Ação principal
    # ------------------------------------------------------------------
    def run(self):
        if self._dialog is None:
            from .pbzpa_dialog import PBZPADialog
            self._dialog = PBZPADialog(self.iface)
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()
