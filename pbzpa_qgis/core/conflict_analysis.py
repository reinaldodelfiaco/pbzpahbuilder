# -*- coding: utf-8 -*-
"""Análise de conflito entre OPEA e Superfícies Limitadoras de Obstáculos.

Para cada feição da camada OPEA (PointZ) verifica-se:

1. Quais superfícies (PolygonZ) cobrem horizontalmente o ponto.
2. Para cada superfície coberta, calcula-se a altitude da superfície
   no ponto (interpolação linear da malha do polígono Z).
3. Compara-se a altitude do topo do OPEA (``cota_topo_m``) com a
   altitude da superfície:

   - ``excedente = cota_topo - cota_superficie``
   - ``conflito = 'VIOLACAO'`` se excedente > 0
   - ``conflito = 'CONFORME'`` se excedente ≤ 0
   - ``conflito = 'LIMITROFE'`` se -2 m ≤ excedente ≤ 0 (atenção)

A superfície que apresenta o menor *folga* (cota_superfície − cota_topo)
é registrada nos atributos do OPEA — pois é a mais restritiva.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from qgis.core import (
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsSpatialIndex,
    QgsVectorLayer,
)


@dataclass
class ConflictResult:
    superficie: str
    cota_superficie_m: float
    excedente_m: float
    classe: str  # CONFORME | LIMITROFE | VIOLACAO


def _surface_altitude_at(feat: QgsFeature, x: float, y: float) -> Optional[float]:
    """Calcula a altitude (Z) da superfície no ponto (x, y) por interpolação linear.

    Estratégia: se a superfície tem todos os Z iguais (plano horizontal),
    retorna esse Z. Caso contrário, ajusta um plano por mínimos quadrados
    aos vértices e avalia em (x, y). Aproximação aceitável dado que as
    superfícies do PBZPA são planas por construção (trapezoidais ou cônicas
    com Z constante por anel).
    """
    geom: QgsGeometry = feat.geometry()
    if geom.isEmpty() or not geom.constGet():
        return None

    # Coletar vértices Z
    abs_geom = geom.constGet()
    pts: List[Tuple[float, float, float]] = []
    for v in abs_geom.vertices():
        pts.append((v.x(), v.y(), v.z()))

    if not pts:
        return None

    zs = [p[2] for p in pts]
    if max(zs) - min(zs) < 1e-6:
        return zs[0]

    # Ajuste de plano z = a*x + b*y + c por mínimos quadrados manual.
    n = len(pts)
    sx = sum(p[0] for p in pts)
    sy = sum(p[1] for p in pts)
    sz = sum(p[2] for p in pts)
    sxx = sum(p[0] * p[0] for p in pts)
    syy = sum(p[1] * p[1] for p in pts)
    sxy = sum(p[0] * p[1] for p in pts)
    sxz = sum(p[0] * p[2] for p in pts)
    syz = sum(p[1] * p[2] for p in pts)

    # Sistema linear:
    # [sxx sxy sx ] [a]   [sxz]
    # [sxy syy sy ] [b] = [syz]
    # [ sx  sy  n ] [c]   [ sz]
    M = [
        [sxx, sxy, sx],
        [sxy, syy, sy],
        [sx, sy, n],
    ]
    Y = [sxz, syz, sz]
    a, b, c = _solve_3x3(M, Y)
    if a is None:
        return zs[0]
    return a * x + b * y + c


def _solve_3x3(m, y):
    """Resolve sistema linear 3×3 via Gauss simples; devolve (None, None, None) em caso singular."""
    det = (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )
    if abs(det) < 1e-12:
        return None, None, None
    inv_det = 1.0 / det
    a = (
        y[0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (y[1] * m[2][2] - m[1][2] * y[2])
        + m[0][2] * (y[1] * m[2][1] - m[1][1] * y[2])
    ) * inv_det
    b = (
        m[0][0] * (y[1] * m[2][2] - m[1][2] * y[2])
        - y[0] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * y[2] - y[1] * m[2][0])
    ) * inv_det
    c = (
        m[0][0] * (m[1][1] * y[2] - y[1] * m[2][1])
        - m[0][1] * (m[1][0] * y[2] - y[1] * m[2][0])
        + y[0] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    ) * inv_det
    return a, b, c


# ======================================================================
# Função pública
# ======================================================================

def analyze_conflicts(
    opea_layer: QgsVectorLayer,
    surfaces_layer: QgsVectorLayer,
    margem_limitrofe_m: float = 2.0,
) -> int:
    """Atualiza in-place a camada OPEA com a classificação de conflito.

    :param opea_layer: camada PointZ contendo OPEA.
    :param surfaces_layer: camada PolygonZ com as superfícies do PBZPA.
    :param margem_limitrofe_m: margem (m) abaixo da superfície para classificar
        como LIMITROFE.
    :return: número de OPEA em violação.
    """
    if not opea_layer.isValid() or not surfaces_layer.isValid():
        raise RuntimeError("Camadas inválidas para análise.")

    spatial_index = QgsSpatialIndex(surfaces_layer.getFeatures())
    surf_lookup = {f.id(): f for f in surfaces_layer.getFeatures()}

    field_idx = {n: opea_layer.fields().indexOf(n) for n in (
        "conflito", "superficie", "excedente_m"
    )}
    if any(v < 0 for v in field_idx.values()):
        raise RuntimeError(
            "Camada OPEA sem campos esperados (conflito, superficie, excedente_m)."
        )

    opea_layer.startEditing()
    violacoes = 0
    try:
        for feat in opea_layer.getFeatures():
            geom = feat.geometry()
            if geom.isEmpty():
                continue
            p = geom.constGet()
            x, y = p.x(), p.y()
            cota_topo = p.z()

            cand_ids = spatial_index.intersects(
                QgsGeometry.fromPointXY(QgsPointXY(x, y)).boundingBox()
            )
            pior: Optional[ConflictResult] = None
            for sid in cand_ids:
                surf = surf_lookup.get(sid)
                if surf is None:
                    continue
                if not surf.geometry().contains(QgsPointXY(x, y)):
                    continue
                z_surf = _surface_altitude_at(surf, x, y)
                if z_surf is None:
                    continue
                excedente = cota_topo - z_surf
                if excedente > 0:
                    classe = "VIOLACAO"
                elif excedente >= -margem_limitrofe_m:
                    classe = "LIMITROFE"
                else:
                    classe = "CONFORME"

                # Mais restritivo = excedente maior (ou menos negativo)
                if pior is None or excedente > pior.excedente_m:
                    pior = ConflictResult(
                        superficie=surf["tipo"],
                        cota_superficie_m=z_surf,
                        excedente_m=excedente,
                        classe=classe,
                    )

            if pior is None:
                opea_layer.changeAttributeValue(feat.id(), field_idx["conflito"], "FORA_PBZPA")
                opea_layer.changeAttributeValue(feat.id(), field_idx["superficie"], "")
                opea_layer.changeAttributeValue(feat.id(), field_idx["excedente_m"], 0.0)
            else:
                opea_layer.changeAttributeValue(feat.id(), field_idx["conflito"], pior.classe)
                opea_layer.changeAttributeValue(feat.id(), field_idx["superficie"], pior.superficie)
                opea_layer.changeAttributeValue(feat.id(), field_idx["excedente_m"], round(pior.excedente_m, 3))
                if pior.classe == "VIOLACAO":
                    violacoes += 1
        opea_layer.commitChanges()
    except Exception:
        opea_layer.rollBack()
        raise

    return violacoes
