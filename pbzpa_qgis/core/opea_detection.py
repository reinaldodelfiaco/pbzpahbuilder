# -*- coding: utf-8 -*-
"""Detecção híbrida de Objetos Projetados no Espaço Aéreo (OPEA).

Estratégia
==========
1. **Detecção automática (sugestão):** o usuário fornece uma imagem
   raster georreferenciada (GeoTIFF / WMS exportado) e um modelo
   de visão computacional opcional (ONNX). O detector retorna
   bounding boxes em pixel + confiança, que são reprojetadas para
   o SRC do projeto (UTM SIRGAS 2000).
2. **Importação alternativa:** se o operador preferir, importa-se
   uma camada vetorial existente (OSM, IBGE, cadastro municipal)
   contendo as edificações, antenas e torres.
3. **Revisão manual:** todos os candidatos são depositados numa
   camada *PointZ* (ou *PolygonZ* em casos de edificações grandes)
   editável. O usuário ajusta posição, altura e tipo de OPEA antes
   da análise de conflito.

Esquema mínimo da camada OPEA
=============================
- ``id``           — inteiro
- ``tipo``         — "EDIFICACAO" | "TORRE" | "ANTENA" | "VEGETACAO" | "OUTRO"
- ``altura_m``     — altura da estrutura em relação ao terreno (m)
- ``cota_base_m``  — cota do terreno na base (m AMSL)
- ``cota_topo_m``  — cota_base + altura
- ``confianca``    — confiança da detecção (0..1) ou 1.0 se manual
- ``status``       — "SUGERIDO" | "VALIDADO" | "REJEITADO"
- ``fonte``        — "ML" | "MANUAL" | "OSM" | "IBGE" | ...

Observações de implementação
============================
- Para QGIS 3.44 usaremos `onnxruntime` (CPU) para inferência.
  O modelo padrão é um *YOLOv8n* finetuned em datasets de edifícios
  de sensoriamento remoto. Caso o pacote não esteja instalado, a
  detecção automática é desabilitada e apenas a importação manual
  fica disponível (o plugin não derruba a sessão do QGIS).
- A inferência opera em tiles (ex.: 1024×1024 px) para imagens grandes,
  com sobreposição de 128 px para mitigar borda.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsGeometry,
    QgsPoint,
    QgsRasterLayer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QVariant

logger = logging.getLogger(__name__)


@dataclass
class OPEACandidate:
    longitude: float        # ou X em UTM se já reprojetado
    latitude: float         # ou Y em UTM se já reprojetado
    altura_m: float
    cota_base_m: float
    tipo: str
    confianca: float
    fonte: str


def opea_fields() -> QgsFields:
    fields = QgsFields()
    fields.append(QgsField("id", QVariant.Int))
    fields.append(QgsField("tipo", QVariant.String))
    fields.append(QgsField("altura_m", QVariant.Double))
    fields.append(QgsField("cota_base_m", QVariant.Double))
    fields.append(QgsField("cota_topo_m", QVariant.Double))
    fields.append(QgsField("confianca", QVariant.Double))
    fields.append(QgsField("status", QVariant.String))
    fields.append(QgsField("fonte", QVariant.String))
    fields.append(QgsField("conflito", QVariant.String))
    fields.append(QgsField("superficie", QVariant.String))
    fields.append(QgsField("excedente_m", QVariant.Double))
    return fields


def create_opea_layer(crs: QgsCoordinateReferenceSystem, name: str = "OPEA") -> QgsVectorLayer:
    """Cria camada vetorial em memória PointZ para os OPEA."""
    uri = f"PointZ?crs={crs.authid()}"
    layer = QgsVectorLayer(uri, name, "memory")
    layer.dataProvider().addAttributes(opea_fields().toList())
    layer.updateFields()
    return layer


# ======================================================================
# Detector automático (placeholder com onnxruntime — opcional)
# ======================================================================

class OPEADetector:
    """Wrapper sobre o modelo ONNX. Descarrega para CPU se não houver GPU.

    O modelo padrão é fornecido em ``resources/models/yolov8n_buildings.onnx``.
    O usuário pode apontar para outro modelo via configuração.
    """

    def __init__(self, onnx_path: Optional[str] = None):
        self.onnx_path = onnx_path
        self.session = None
        self._maybe_init()

    def _maybe_init(self) -> None:
        if not self.onnx_path:
            logger.info("Modelo ONNX não informado; detector em modo manual.")
            return
        try:
            import onnxruntime as ort  # noqa: WPS433 (import opcional)
        except ImportError:
            logger.warning("onnxruntime ausente. Instale com `pip install onnxruntime`.")
            return
        try:
            self.session = ort.InferenceSession(
                self.onnx_path, providers=["CPUExecutionProvider"]
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Falha ao carregar modelo ONNX: %s", exc)
            self.session = None

    @property
    def available(self) -> bool:
        return self.session is not None

    def detect(self, raster: QgsRasterLayer) -> List[OPEACandidate]:
        """Executa o detector sobre a imagem raster e retorna candidatos.

        Implementação a ser feita: leitura por blocos, normalização,
        inferência, NMS e georreferenciamento dos bbox.
        """
        if not self.available:
            return []
        # TODO: implementar pipeline real de inferência por tiles.
        return []


# ======================================================================
# Importação a partir de camada existente
# ======================================================================

def candidates_from_layer(
    layer: QgsVectorLayer,
    altura_field: str,
    tipo_field: Optional[str] = None,
    cota_base_field: Optional[str] = None,
    fonte: str = "EXTERNO",
) -> Iterable[OPEACandidate]:
    """Converte uma camada existente (ex.: edificações OSM) em candidatos OPEA."""
    if altura_field not in layer.fields().names():
        raise ValueError(f"Campo de altura '{altura_field}' não encontrado.")
    for feat in layer.getFeatures():
        geom = feat.geometry()
        if geom.isEmpty():
            continue
        c = geom.centroid().asPoint()
        altura = float(feat[altura_field] or 0.0)
        cota_base = float(feat[cota_base_field]) if cota_base_field else 0.0
        tipo = str(feat[tipo_field]) if tipo_field else "EDIFICACAO"
        yield OPEACandidate(
            longitude=c.x(),
            latitude=c.y(),
            altura_m=altura,
            cota_base_m=cota_base,
            tipo=tipo,
            confianca=1.0,
            fonte=fonte,
        )


def populate_layer_from_candidates(
    layer: QgsVectorLayer,
    candidates: Iterable[OPEACandidate],
    status: str = "SUGERIDO",
) -> None:
    feats = []
    for i, c in enumerate(candidates, start=1):
        feat = QgsFeature(layer.fields())
        z = c.cota_base_m + c.altura_m
        feat.setGeometry(QgsGeometry(QgsPoint(c.longitude, c.latitude, z)))
        feat.setAttributes([
            i, c.tipo, c.altura_m, c.cota_base_m, z,
            c.confianca, status, c.fonte, "", "", 0.0,
        ])
        feats.append(feat)
    layer.dataProvider().addFeatures(feats)
    layer.updateExtents()
