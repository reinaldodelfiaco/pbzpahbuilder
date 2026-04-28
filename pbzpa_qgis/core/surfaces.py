# -*- coding: utf-8 -*-
"""Geração paramétrica das Superfícies Limitadoras de Obstáculos (SLO).

Implementa as superfícies definidas pela ICA 11-3, RBAC 154 e Anexo 14 da
OACI:

* Faixa de pista (Runway Strip)
* Superfície Horizontal Interna (Inner Horizontal)
* Superfície Cônica (Conical)
* Superfície de Aproximação (Approach) — multi-seção
* Superfície de Transição (Transition)
* Superfície de Decolagem (Take-off climb)

Todas as geometrias são geradas em **PolygonZ** (3D) num sistema UTM
SIRGAS 2000 detectado automaticamente a partir da coordenada da pista.
A altitude (Z) é dada em metros acima do nível médio do mar (AMSL),
calculada a partir da elevação informada da pista somada à altura
relativa de cada superfície no ponto.

A camada de saída é construída pelo orquestrador `build_pbzpa_layers`
em :mod:`pbzpa_qgis.core.workflow`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsPoint,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

from .runway import ApproachType, Runway, RunwayType
from .utm_utils import epsg_for_lonlat


# ======================================================================
# Tabelas oficiais (ICA 11-3 / Anexo 14 OACI / RBAC 154)
# ======================================================================

@dataclass(frozen=True)
class _ApproachParams:
    """Parâmetros da Superfície de Aproximação."""
    inner_edge_m: float        # largura da borda interna
    distance_threshold_m: float  # distância do limiar
    divergence: float          # 0.10 = 10 %, 0.15 = 15 %
    sections: Sequence[Tuple[float, float]]
    # Lista de (comprimento_m, gradiente). gradiente=0 ⇒ horizontal.


@dataclass(frozen=True)
class _ConicalParams:
    slope: float
    height_m: float


@dataclass(frozen=True)
class _InnerHorizontalParams:
    radius_m: float
    height_m: float


@dataclass(frozen=True)
class _TransitionParams:
    slope: float


@dataclass(frozen=True)
class _TakeoffParams:
    inner_edge_m: float
    distance_runway_end_m: float
    divergence: float
    final_width_m: float
    length_m: float
    slope: float


# Inner Horizontal (raio em m, altura em m sobre ARP) ------------------
INNER_HORIZONTAL = {
    (1, RunwayType.NON_INSTRUMENT, ApproachType.VISUAL): _InnerHorizontalParams(2000, 45),
    (2, RunwayType.NON_INSTRUMENT, ApproachType.VISUAL): _InnerHorizontalParams(2500, 45),
    (3, RunwayType.NON_INSTRUMENT, ApproachType.VISUAL): _InnerHorizontalParams(4000, 45),
    (4, RunwayType.NON_INSTRUMENT, ApproachType.VISUAL): _InnerHorizontalParams(4000, 45),
    (1, RunwayType.INSTRUMENT, ApproachType.NON_PRECISION): _InnerHorizontalParams(3500, 45),
    (2, RunwayType.INSTRUMENT, ApproachType.NON_PRECISION): _InnerHorizontalParams(3500, 45),
    (3, RunwayType.INSTRUMENT, ApproachType.NON_PRECISION): _InnerHorizontalParams(4000, 45),
    (4, RunwayType.INSTRUMENT, ApproachType.NON_PRECISION): _InnerHorizontalParams(4000, 45),
    (3, RunwayType.INSTRUMENT, ApproachType.PRECISION_CAT_I): _InnerHorizontalParams(4000, 45),
    (4, RunwayType.INSTRUMENT, ApproachType.PRECISION_CAT_I): _InnerHorizontalParams(4000, 45),
    (3, RunwayType.INSTRUMENT, ApproachType.PRECISION_CAT_II): _InnerHorizontalParams(4000, 45),
    (4, RunwayType.INSTRUMENT, ApproachType.PRECISION_CAT_II): _InnerHorizontalParams(4000, 45),
    (3, RunwayType.INSTRUMENT, ApproachType.PRECISION_CAT_III): _InnerHorizontalParams(4000, 45),
    (4, RunwayType.INSTRUMENT, ApproachType.PRECISION_CAT_III): _InnerHorizontalParams(4000, 45),
}

# Cônica ---------------------------------------------------------------
CONICAL = {
    1: _ConicalParams(slope=0.05, height_m=35),
    2: _ConicalParams(slope=0.05, height_m=55),
    3: _ConicalParams(slope=0.05, height_m=75),
    4: _ConicalParams(slope=0.05, height_m=100),
}

# Aproximação ----------------------------------------------------------
APPROACH = {
    # Visual
    (1, ApproachType.VISUAL): _ApproachParams(60, 30, 0.10, [(1600, 0.05)]),
    (2, ApproachType.VISUAL): _ApproachParams(80, 60, 0.10, [(2500, 0.04)]),
    (3, ApproachType.VISUAL): _ApproachParams(150, 60, 0.10, [(3000, 0.0333)]),
    (4, ApproachType.VISUAL): _ApproachParams(150, 60, 0.10, [(3000, 0.025)]),
    # Não-precisão
    (1, ApproachType.NON_PRECISION): _ApproachParams(150, 60, 0.15, [(2500, 0.0333)]),
    (2, ApproachType.NON_PRECISION): _ApproachParams(150, 60, 0.15, [(2500, 0.0333)]),
    (3, ApproachType.NON_PRECISION): _ApproachParams(
        300, 60, 0.15, [(3000, 0.020), (3600, 0.025), (8400, 0.0)]
    ),
    (4, ApproachType.NON_PRECISION): _ApproachParams(
        300, 60, 0.15, [(3000, 0.020), (3600, 0.025), (8400, 0.0)]
    ),
    # Precisão CAT I
    (1, ApproachType.PRECISION_CAT_I): _ApproachParams(
        150, 60, 0.15, [(3000, 0.025), (12000, 0.030)]
    ),
    (2, ApproachType.PRECISION_CAT_I): _ApproachParams(
        150, 60, 0.15, [(3000, 0.025), (12000, 0.030)]
    ),
    (3, ApproachType.PRECISION_CAT_I): _ApproachParams(
        300, 60, 0.15, [(3000, 0.020), (3600, 0.025), (8400, 0.0)]
    ),
    (4, ApproachType.PRECISION_CAT_I): _ApproachParams(
        300, 60, 0.15, [(3000, 0.020), (3600, 0.025), (8400, 0.0)]
    ),
    # Precisão CAT II/III: mesmas dimensões da CAT I (code 3 e 4)
    (3, ApproachType.PRECISION_CAT_II): _ApproachParams(
        300, 60, 0.15, [(3000, 0.020), (3600, 0.025), (8400, 0.0)]
    ),
    (4, ApproachType.PRECISION_CAT_II): _ApproachParams(
        300, 60, 0.15, [(3000, 0.020), (3600, 0.025), (8400, 0.0)]
    ),
    (3, ApproachType.PRECISION_CAT_III): _ApproachParams(
        300, 60, 0.15, [(3000, 0.020), (3600, 0.025), (8400, 0.0)]
    ),
    (4, ApproachType.PRECISION_CAT_III): _ApproachParams(
        300, 60, 0.15, [(3000, 0.020), (3600, 0.025), (8400, 0.0)]
    ),
}

# Transição ------------------------------------------------------------
TRANSITION = {
    (1, RunwayType.NON_INSTRUMENT): _TransitionParams(0.20),
    (2, RunwayType.NON_INSTRUMENT): _TransitionParams(0.20),
    (3, RunwayType.NON_INSTRUMENT): _TransitionParams(0.143),
    (4, RunwayType.NON_INSTRUMENT): _TransitionParams(0.143),
    (1, RunwayType.INSTRUMENT): _TransitionParams(0.20),
    (2, RunwayType.INSTRUMENT): _TransitionParams(0.20),
    (3, RunwayType.INSTRUMENT): _TransitionParams(0.143),
    (4, RunwayType.INSTRUMENT): _TransitionParams(0.143),
}

# Decolagem ------------------------------------------------------------
TAKEOFF = {
    1: _TakeoffParams(60, 30, 0.10, 380, 1600, 0.05),
    2: _TakeoffParams(80, 60, 0.10, 580, 2500, 0.04),
    3: _TakeoffParams(180, 60, 0.125, 1800, 15000, 0.02),
    4: _TakeoffParams(180, 60, 0.125, 1800, 15000, 0.02),
}

# Faixa de pista (semi-largura por classe, em metros) ------------------
STRIP_HALF_WIDTH = {
    (1, RunwayType.NON_INSTRUMENT): 30,
    (2, RunwayType.NON_INSTRUMENT): 40,
    (3, RunwayType.NON_INSTRUMENT): 150,
    (4, RunwayType.NON_INSTRUMENT): 150,
    (1, RunwayType.INSTRUMENT): 75,
    (2, RunwayType.INSTRUMENT): 75,
    (3, RunwayType.INSTRUMENT): 150,
    (4, RunwayType.INSTRUMENT): 150,
}

STRIP_END_EXTENSION = {1: 30, 2: 60, 3: 60, 4: 60}


# ======================================================================
# Utilitários geométricos
# ======================================================================

def _project_lonlat_to_utm(lon: float, lat: float, transform: QgsCoordinateTransform) -> Tuple[float, float]:
    pt = transform.transform(QgsPointXY(lon, lat))
    return pt.x(), pt.y()


def _unit_vector(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    norm = math.hypot(dx, dy)
    if norm == 0:
        raise ValueError("Pontos coincidentes; não é possível extrair direção.")
    return dx / norm, dy / norm


def _perp(v: Tuple[float, float]) -> Tuple[float, float]:
    """Vetor perpendicular (rotação +90°)."""
    return -v[1], v[0]


def _add(p: Tuple[float, float], v: Tuple[float, float], scale: float = 1.0) -> Tuple[float, float]:
    return p[0] + v[0] * scale, p[1] + v[1] * scale


# ======================================================================
# Construção de QgsVectorLayer base
# ======================================================================

def _surface_fields() -> QgsFields:
    fields = QgsFields()
    fields.append(QgsField("id", QVariant.Int))
    fields.append(QgsField("tipo", QVariant.String))
    fields.append(QgsField("subtipo", QVariant.String))
    fields.append(QgsField("cota_min_m", QVariant.Double))
    fields.append(QgsField("cota_max_m", QVariant.Double))
    fields.append(QgsField("gradiente", QVariant.Double))
    fields.append(QgsField("origem", QVariant.String))
    return fields


def create_surfaces_layer(crs: QgsCoordinateReferenceSystem, name: str = "PBZPA - Superfícies") -> QgsVectorLayer:
    """Cria um QgsVectorLayer em memória, PolygonZ, com os campos padrão."""
    uri = f"PolygonZ?crs={crs.authid()}"
    layer = QgsVectorLayer(uri, name, "memory")
    pr = layer.dataProvider()
    pr.addAttributes(_surface_fields().toList())
    layer.updateFields()
    return layer


# ======================================================================
# Geração das superfícies
# ======================================================================

def generate_runway_strip(runway: Runway, transform: QgsCoordinateTransform, elev_arp: float) -> QgsFeature:
    """Faixa de pista: retângulo em torno da pista física, plano horizontal na cota da cabeceira."""
    half_w = STRIP_HALF_WIDTH[(runway.code_number, runway.runway_type)]
    end_ext = STRIP_END_EXTENSION[runway.code_number]

    a = _project_lonlat_to_utm(runway.threshold_a.longitude, runway.threshold_a.latitude, transform)
    b = _project_lonlat_to_utm(runway.threshold_b.longitude, runway.threshold_b.latitude, transform)
    u = _unit_vector(a, b)
    n = _perp(u)

    a_ext = _add(a, u, -end_ext)
    b_ext = _add(b, u, end_ext)

    p1 = _add(a_ext, n, half_w)
    p2 = _add(b_ext, n, half_w)
    p3 = _add(b_ext, n, -half_w)
    p4 = _add(a_ext, n, -half_w)

    z = elev_arp
    ring = [QgsPoint(p1[0], p1[1], z), QgsPoint(p2[0], p2[1], z),
            QgsPoint(p3[0], p3[1], z), QgsPoint(p4[0], p4[1], z),
            QgsPoint(p1[0], p1[1], z)]
    geom = QgsGeometry.fromPolygonXY([])  # placeholder
    geom = QgsGeometry(geom)
    # Construir PolygonZ via WKT para compatibilidade ampla
    wkt = "POLYGON Z((" + ", ".join(f"{p.x()} {p.y()} {p.z()}" for p in ring) + "))"
    geom = QgsGeometry.fromWkt(wkt)

    feat = QgsFeature(_surface_fields())
    feat.setGeometry(geom)
    feat.setAttributes([1, "FAIXA_PISTA", "", z, z, 0.0, "ICA 11-3"])
    return feat


def generate_inner_horizontal(runway: Runway, transform: QgsCoordinateTransform, elev_arp: float) -> QgsFeature:
    """Horizontal interna: envoltória de dois semicírculos centrados nas cabeceiras."""
    most_demanding = _most_demanding_approach(runway)
    params = INNER_HORIZONTAL[(runway.code_number, runway.runway_type, most_demanding)]
    r = params.radius_m
    z = elev_arp + params.height_m

    a = _project_lonlat_to_utm(runway.threshold_a.longitude, runway.threshold_a.latitude, transform)
    b = _project_lonlat_to_utm(runway.threshold_b.longitude, runway.threshold_b.latitude, transform)
    u = _unit_vector(a, b)
    heading = math.atan2(u[1], u[0])

    pts = _envelope_pts(a, b, heading, r, z)
    wkt = "POLYGON Z((" + ", ".join(f"{x} {y} {zz}" for x, y, zz in pts) + "))"
    feat = QgsFeature(_surface_fields())
    feat.setGeometry(QgsGeometry.fromWkt(wkt))
    feat.setAttributes([2, "HORIZONTAL_INTERNA", most_demanding.value, z, z, 0.0, "ICA 11-3"])
    return feat


def generate_conical(runway: Runway, transform: QgsCoordinateTransform, elev_arp: float) -> QgsFeature:
    """Cônica: anel ao redor da Horizontal Interna, ascendente em 5%."""
    most_demanding = _most_demanding_approach(runway)
    inner = INNER_HORIZONTAL[(runway.code_number, runway.runway_type, most_demanding)]
    cone = CONICAL[runway.code_number]

    r_inner = inner.radius_m
    r_outer = r_inner + cone.height_m / cone.slope  # cota base + h/i = comprimento horizontal

    a = _project_lonlat_to_utm(runway.threshold_a.longitude, runway.threshold_a.latitude, transform)
    b = _project_lonlat_to_utm(runway.threshold_b.longitude, runway.threshold_b.latitude, transform)
    u = _unit_vector(a, b)
    heading = math.atan2(u[1], u[0])

    z_inner = elev_arp + inner.height_m
    z_outer = z_inner + cone.height_m

    # Construir anel: contorno externo (sentido anti-horário) + interno (sentido horário)
    outer_pts = _envelope_pts(a, b, heading, r_outer, z_outer)
    inner_pts = list(reversed(_envelope_pts(a, b, heading, r_inner, z_inner)))

    wkt_outer = ", ".join(f"{x} {y} {z}" for x, y, z in outer_pts)
    wkt_inner = ", ".join(f"{x} {y} {z}" for x, y, z in inner_pts)
    wkt = f"POLYGON Z(({wkt_outer}), ({wkt_inner}))"

    feat = QgsFeature(_surface_fields())
    feat.setGeometry(QgsGeometry.fromWkt(wkt))
    feat.setAttributes([3, "CONICA", "", z_inner, z_outer, cone.slope, "ICA 11-3"])
    return feat


def generate_approach(runway: Runway, threshold: str, transform: QgsCoordinateTransform, elev_arp: float) -> List[QgsFeature]:
    """Aproximação para uma das cabeceiras ('A' ou 'B'). Pode ter múltiplas seções."""
    if threshold not in ("A", "B"):
        raise ValueError("threshold deve ser 'A' ou 'B'.")
    th = runway.threshold_a if threshold == "A" else runway.threshold_b
    other = runway.threshold_b if threshold == "A" else runway.threshold_a
    op = runway.approach_type_a if threshold == "A" else runway.approach_type_b

    params = APPROACH[(runway.code_number, op)]

    th_xy = _project_lonlat_to_utm(th.longitude, th.latitude, transform)
    other_xy = _project_lonlat_to_utm(other.longitude, other.latitude, transform)
    # `outward` aponta de `other` para `th` e, ao continuar nesta direção a partir
    # de `th`, afasta-se da pista — sentido correto para a aproximação.
    outward = _unit_vector(other_xy, th_xy)
    n = _perp(outward)

    feats: List[QgsFeature] = []
    z_start = th.elevation_m
    half_inner = params.inner_edge_m / 2.0
    cur_origin = _add(th_xy, outward, params.distance_threshold_m)
    cur_half = half_inner

    fid_base = 100 if threshold == "A" else 200
    for idx, (length_m, slope) in enumerate(params.sections, start=1):
        end_origin = _add(cur_origin, outward, length_m)
        end_half = cur_half + length_m * params.divergence
        z_end = z_start + length_m * slope

        p1 = _add(cur_origin, n, cur_half)
        p2 = _add(end_origin, n, end_half)
        p3 = _add(end_origin, n, -end_half)
        p4 = _add(cur_origin, n, -cur_half)

        wkt = (
            "POLYGON Z(("
            f"{p1[0]} {p1[1]} {z_start}, "
            f"{p2[0]} {p2[1]} {z_end}, "
            f"{p3[0]} {p3[1]} {z_end}, "
            f"{p4[0]} {p4[1]} {z_start}, "
            f"{p1[0]} {p1[1]} {z_start}))"
        )
        feat = QgsFeature(_surface_fields())
        feat.setGeometry(QgsGeometry.fromWkt(wkt))
        feat.setAttributes([
            fid_base + idx, "APROXIMACAO", f"{threshold}-S{idx}", z_start, z_end, slope, "ICA 11-3"
        ])
        feats.append(feat)

        cur_origin, cur_half, z_start = end_origin, end_half, z_end

    return feats


def generate_takeoff(runway: Runway, threshold: str, transform: QgsCoordinateTransform, elev_arp: float) -> QgsFeature:
    """Decolagem: trapézio simples de 2% (code 3-4) com 15 km."""
    if threshold not in ("A", "B"):
        raise ValueError("threshold deve ser 'A' ou 'B'.")
    th = runway.threshold_a if threshold == "A" else runway.threshold_b
    other = runway.threshold_b if threshold == "A" else runway.threshold_a
    params = TAKEOFF[runway.code_number]

    th_xy = _project_lonlat_to_utm(th.longitude, th.latitude, transform)
    other_xy = _project_lonlat_to_utm(other.longitude, other.latitude, transform)
    outward = _unit_vector(other_xy, th_xy)
    n = _perp(outward)

    z_start = th.elevation_m
    z_end = z_start + params.length_m * params.slope

    inner_origin = _add(th_xy, outward, params.distance_runway_end_m)
    end_origin = _add(inner_origin, outward, params.length_m)

    inner_half = params.inner_edge_m / 2.0
    final_half = params.final_width_m / 2.0

    p1 = _add(inner_origin, n, inner_half)
    p2 = _add(end_origin, n, final_half)
    p3 = _add(end_origin, n, -final_half)
    p4 = _add(inner_origin, n, -inner_half)

    wkt = (
        "POLYGON Z(("
        f"{p1[0]} {p1[1]} {z_start}, "
        f"{p2[0]} {p2[1]} {z_end}, "
        f"{p3[0]} {p3[1]} {z_end}, "
        f"{p4[0]} {p4[1]} {z_start}, "
        f"{p1[0]} {p1[1]} {z_start}))"
    )
    fid = 300 if threshold == "A" else 400
    feat = QgsFeature(_surface_fields())
    feat.setGeometry(QgsGeometry.fromWkt(wkt))
    feat.setAttributes([fid, "DECOLAGEM", threshold, z_start, z_end, params.slope, "ICA 11-3"])
    return feat


def generate_transition(runway: Runway, transform: QgsCoordinateTransform, elev_arp: float) -> QgsFeature:
    """Transição: faixa lateral à pista, ascendente até a Horizontal Interna.

    Implementação simplificada: anel paralelo à faixa de pista com largura
    horizontal igual a ``(altura_HI / inclinação_transição)``, plano com
    cota mínima ao nível da faixa e máxima na altura da HI.
    """
    most_demanding = _most_demanding_approach(runway)
    inner = INNER_HORIZONTAL[(runway.code_number, runway.runway_type, most_demanding)]
    transition = TRANSITION[(runway.code_number, runway.runway_type)]

    half_strip = STRIP_HALF_WIDTH[(runway.code_number, runway.runway_type)]
    horizontal_extent = inner.height_m / transition.slope  # m
    half_outer = half_strip + horizontal_extent

    end_ext = STRIP_END_EXTENSION[runway.code_number]

    a = _project_lonlat_to_utm(runway.threshold_a.longitude, runway.threshold_a.latitude, transform)
    b = _project_lonlat_to_utm(runway.threshold_b.longitude, runway.threshold_b.latitude, transform)
    u = _unit_vector(a, b)
    n = _perp(u)

    a_ext = _add(a, u, -end_ext)
    b_ext = _add(b, u, end_ext)

    z_strip = elev_arp
    z_top = elev_arp + inner.height_m

    # outer
    outer = [
        _add(a_ext, n, half_outer),
        _add(b_ext, n, half_outer),
        _add(b_ext, n, -half_outer),
        _add(a_ext, n, -half_outer),
    ]
    inner_ring = [
        _add(a_ext, n, half_strip),
        _add(b_ext, n, half_strip),
        _add(b_ext, n, -half_strip),
        _add(a_ext, n, -half_strip),
    ]

    z_pairs_outer = [(p, z_top) for p in outer]
    z_pairs_inner = [(p, z_strip) for p in inner_ring]
    outer_wkt = ", ".join(f"{p[0]} {p[1]} {z}" for p, z in z_pairs_outer + [z_pairs_outer[0]])
    inner_wkt = ", ".join(f"{p[0]} {p[1]} {z}" for p, z in list(reversed(z_pairs_inner)) + [list(reversed(z_pairs_inner))[0]])

    wkt = f"POLYGON Z(({outer_wkt}), ({inner_wkt}))"
    feat = QgsFeature(_surface_fields())
    feat.setGeometry(QgsGeometry.fromWkt(wkt))
    feat.setAttributes([4, "TRANSICAO", "", z_strip, z_top, transition.slope, "ICA 11-3"])
    return feat


# ======================================================================
# Helpers
# ======================================================================

def _most_demanding_approach(runway: Runway) -> ApproachType:
    """Devolve o tipo de operação mais restritivo entre as duas cabeceiras."""
    order = {
        ApproachType.VISUAL: 0,
        ApproachType.NON_PRECISION: 1,
        ApproachType.PRECISION_CAT_I: 2,
        ApproachType.PRECISION_CAT_II: 3,
        ApproachType.PRECISION_CAT_III: 4,
    }
    return max(
        (runway.approach_type_a, runway.approach_type_b),
        key=lambda t: order.get(t, 0),
    )


def _envelope_pts(
    a: Tuple[float, float],
    b: Tuple[float, float],
    heading: float,
    radius: float,
    z: float,
) -> List[Tuple[float, float, float]]:
    """Gera o contorno de uma 'envoltória de pista' a uma certa distância radial."""
    pts: List[Tuple[float, float, float]] = []
    # Semicírculo do lado A (orientado heading + 90° → heading + 270°)
    for i in range(65):
        t = math.pi / 2 + i * math.pi / 64
        ang = heading + t
        x = a[0] + radius * math.cos(ang)
        y = a[1] + radius * math.sin(ang)
        pts.append((x, y, z))
    # Semicírculo do lado B
    for i in range(65):
        t = -math.pi / 2 + i * math.pi / 64
        ang = heading + t
        x = b[0] + radius * math.cos(ang)
        y = b[1] + radius * math.sin(ang)
        pts.append((x, y, z))
    pts.append(pts[0])
    return pts


# ======================================================================
# Função-orquestradora
# ======================================================================

def build_pbzpa_layer(runway: Runway) -> QgsVectorLayer:
    """Gera todas as superfícies do PBZPA num único QgsVectorLayer 3D."""
    lon, lat = runway.midpoint_lonlat
    epsg = epsg_for_lonlat(lon, lat)
    src_crs = QgsCoordinateReferenceSystem("EPSG:4674")  # SIRGAS 2000 lat/lon
    dst_crs = QgsCoordinateReferenceSystem(f"EPSG:{epsg}")
    transform = QgsCoordinateTransform(src_crs, dst_crs, QgsProject.instance())

    layer = create_surfaces_layer(dst_crs)
    feats: List[QgsFeature] = []
    elev_arp = runway.reference_elevation_m

    feats.append(generate_runway_strip(runway, transform, elev_arp))
    feats.append(generate_transition(runway, transform, elev_arp))
    feats.append(generate_inner_horizontal(runway, transform, elev_arp))
    feats.append(generate_conical(runway, transform, elev_arp))
    feats.extend(generate_approach(runway, "A", transform, elev_arp))
    feats.extend(generate_approach(runway, "B", transform, elev_arp))
    feats.append(generate_takeoff(runway, "A", transform, elev_arp))
    feats.append(generate_takeoff(runway, "B", transform, elev_arp))

    layer.dataProvider().addFeatures(feats)
    layer.updateExtents()
    return layer
