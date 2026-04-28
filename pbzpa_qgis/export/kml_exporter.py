# -*- coding: utf-8 -*-
"""Exportação para KML (Google Earth) das camadas geradas pelo plugin.

Usa o driver ``LIBKML`` (ou ``KML``, fallback) do GDAL/OGR via
``QgsVectorFileWriter``. As camadas Polygon Z são convertidas com
``altitudeMode = 'absolute'`` para refletir a cota AMSL.
"""
from __future__ import annotations

import os
from typing import Iterable, Optional

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransformContext,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsWkbTypes,
)


def export_layers_to_kml(layers: Iterable[QgsVectorLayer], output_path: str) -> str:
    """Exporta as camadas para um único KML/KMZ.

    Estratégia: o driver KML do OGR só permite uma camada por arquivo.
    Para empacotar múltiplas, usamos KMZ (zip de doc.kml). Fallback simples:
    se houver apenas uma camada, gera KML; senão, escreve KMZ via doc.kml +
    pastas auxiliares.
    """
    layers = list(layers)
    if not layers:
        raise ValueError("Nenhuma camada para exportar.")

    output_path = os.fspath(output_path)
    if not output_path.lower().endswith((".kml", ".kmz")):
        output_path += ".kmz" if len(layers) > 1 else ".kml"

    crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
    options_base = QgsVectorFileWriter.SaveVectorOptions()
    options_base.driverName = "LIBKML"
    options_base.fileEncoding = "UTF-8"
    options_base.ct = None  # reprojeção decidida abaixo
    options_base.destCRS = crs_wgs84
    options_base.layerOptions = ["ALTITUDE_MODE=absolute"]

    if len(layers) == 1:
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "LIBKML"
        opts.fileEncoding = "UTF-8"
        opts.destCRS = crs_wgs84
        opts.layerName = layers[0].name()
        opts.layerOptions = ["ALTITUDE_MODE=absolute"]
        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            layers[0], output_path, QgsCoordinateTransformContext(), opts
        )
        if result[0] != QgsVectorFileWriter.NoError:
            raise RuntimeError(f"Falha ao exportar KML: {result[1]}")
        return output_path

    # Múltiplas camadas → KMZ
    for i, lyr in enumerate(layers):
        opts = QgsVectorFileWriter.SaveVectorOptions()
        opts.driverName = "LIBKML"
        opts.fileEncoding = "UTF-8"
        opts.destCRS = crs_wgs84
        opts.layerName = lyr.name()
        opts.layerOptions = ["ALTITUDE_MODE=absolute"]
        opts.actionOnExistingFile = (
            QgsVectorFileWriter.CreateOrOverwriteFile if i == 0
            else QgsVectorFileWriter.CreateOrOverwriteLayer
        )
        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            lyr, output_path, QgsCoordinateTransformContext(), opts
        )
        if result[0] != QgsVectorFileWriter.NoError:
            raise RuntimeError(
                f"Falha ao adicionar camada '{lyr.name()}' ao KMZ: {result[1]}"
            )
    return output_path
