# -*- coding: utf-8 -*-
"""
PBZPA/PBZPH — plugin QGIS para geração de Planos Básicos de Zona de
Proteção de Aeródromo e de Heliponto.

Este módulo expõe o ponto de entrada exigido pelo QGIS (`classFactory`)
para instanciar a classe principal do plugin.

Referência: PyQGIS Developer Cookbook
https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/plugins/plugins.html
"""

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Carrega a classe principal do plugin.

    :param iface: instância de QgisInterface fornecida pelo QGIS.
    :return: instância de PBZPAPlugin.
    """
    from .pbzpa_plugin import PBZPAPlugin
    return PBZPAPlugin(iface)
