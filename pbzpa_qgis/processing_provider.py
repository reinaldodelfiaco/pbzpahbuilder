# -*- coding: utf-8 -*-
"""Processing Provider — disponibiliza algoritmos batch do plugin no Toolbox.

Permite gerar superfícies do PBZPA em modo *headless* via Modeler ou
processamento em lote.
"""
from __future__ import annotations

from qgis.core import (
    QgsProcessingAlgorithm,
    QgsProcessingProvider,
    QgsProcessingParameterString,
    QgsProcessingParameterNumber,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsFeatureSink,
    QgsWkbTypes,
)

from .core.runway import ApproachType, Runway, RunwayType, Threshold
from .core.surfaces import build_pbzpa_layer


class GeneratePBZPAAlgorithm(QgsProcessingAlgorithm):
    INPUTS = ("ICAO", "LON_A", "LAT_A", "ELEV_A", "LON_B", "LAT_B", "ELEV_B",
              "CODE_NUMBER", "CODE_LETTER", "RUNWAY_TYPE",
              "APPROACH_A", "APPROACH_B")
    OUTPUT = "OUTPUT"

    def name(self):
        return "generate_pbzpa"

    def displayName(self):
        return "Gerar Superfícies PBZPA"

    def group(self):
        return "PBZPA/PBZPH"

    def groupId(self):
        return "pbzpa"

    def createInstance(self):
        return GeneratePBZPAAlgorithm()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterString("ICAO", "Designativo OACI", "----"))
        self.addParameter(QgsProcessingParameterNumber("LON_A", "Longitude cabeceira A", QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber("LAT_A", "Latitude cabeceira A", QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber("ELEV_A", "Elevação A (m)", QgsProcessingParameterNumber.Double, 0.0))
        self.addParameter(QgsProcessingParameterNumber("LON_B", "Longitude cabeceira B", QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber("LAT_B", "Latitude cabeceira B", QgsProcessingParameterNumber.Double))
        self.addParameter(QgsProcessingParameterNumber("ELEV_B", "Elevação B (m)", QgsProcessingParameterNumber.Double, 0.0))
        self.addParameter(QgsProcessingParameterEnum("CODE_NUMBER", "Code Number", options=["1", "2", "3", "4"], defaultValue=3))
        self.addParameter(QgsProcessingParameterEnum("CODE_LETTER", "Code Letter", options=list("ABCDEF"), defaultValue=2))
        self.addParameter(QgsProcessingParameterEnum("RUNWAY_TYPE", "Tipo de pista", options=["non_instrument", "instrument"], defaultValue=1))
        self.addParameter(QgsProcessingParameterEnum("APPROACH_A", "Operação cabeceira A", options=[t.value for t in ApproachType], defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum("APPROACH_B", "Operação cabeceira B", options=[t.value for t in ApproachType], defaultValue=0))
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, "Superfícies PBZPA"))

    def processAlgorithm(self, parameters, context, feedback):
        runway = Runway(
            icao_code=self.parameterAsString(parameters, "ICAO", context),
            threshold_a=Threshold(
                "A",
                self.parameterAsDouble(parameters, "LON_A", context),
                self.parameterAsDouble(parameters, "LAT_A", context),
                self.parameterAsDouble(parameters, "ELEV_A", context),
            ),
            threshold_b=Threshold(
                "B",
                self.parameterAsDouble(parameters, "LON_B", context),
                self.parameterAsDouble(parameters, "LAT_B", context),
                self.parameterAsDouble(parameters, "ELEV_B", context),
            ),
            code_number=int(["1", "2", "3", "4"][self.parameterAsEnum(parameters, "CODE_NUMBER", context)]),
            code_letter=list("ABCDEF")[self.parameterAsEnum(parameters, "CODE_LETTER", context)],
            runway_type=RunwayType(["non_instrument", "instrument"][self.parameterAsEnum(parameters, "RUNWAY_TYPE", context)]),
            approach_type_a=list(ApproachType)[self.parameterAsEnum(parameters, "APPROACH_A", context)],
            approach_type_b=list(ApproachType)[self.parameterAsEnum(parameters, "APPROACH_B", context)],
        )

        layer = build_pbzpa_layer(runway)
        sink, dest_id = self.parameterAsSink(
            parameters, self.OUTPUT, context,
            layer.fields(), QgsWkbTypes.PolygonZ, layer.crs()
        )
        for feat in layer.getFeatures():
            sink.addFeature(feat, QgsFeatureSink.FastInsert)
        return {self.OUTPUT: dest_id}


class PBZPAProcessingProvider(QgsProcessingProvider):
    def id(self):
        return "pbzpa"

    def name(self):
        return "PBZPA/PBZPH"

    def loadAlgorithms(self):
        self.addAlgorithm(GeneratePBZPAAlgorithm())
