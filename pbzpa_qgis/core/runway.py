# -*- coding: utf-8 -*-
"""Modelagem de pista de pouso e decolagem (RWY).

A pista é descrita por suas duas cabeceiras (lat, lon, elevação) e por
parâmetros de classificação que determinam quais superfícies serão geradas:

- ``code_number`` (1-4) — comprimento de campo de referência.
- ``code_letter`` (A-F) — envergadura.
- ``approach_type`` — visual / non-precision / precision-CAT-I/II/III.
- ``runway_type`` — non-instrument / instrument.

Coordenadas em entrada: WGS84/SIRGAS 2000 geográficas (lat/lon).
Internamente o módulo de superfícies converte para UTM SIRGAS 2000 via
:mod:`pbzpa_qgis.core.utm_utils`.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class ApproachType(str, Enum):
    NOT_OPERATIONAL = "not_operational"
    VISUAL = "visual"
    NON_PRECISION = "non_precision"
    PRECISION_CAT_I = "precision_cat_i"
    PRECISION_CAT_II = "precision_cat_ii"
    PRECISION_CAT_III = "precision_cat_iii"


class RunwayType(str, Enum):
    NON_INSTRUMENT = "non_instrument"
    INSTRUMENT = "instrument"


class ProjectType(str, Enum):
    AERODROME = "aerodrome"
    HELIPORT = "heliport"


class SSPVSector(str, Enum):
    NONE = "none"
    SECTOR_A = "sector_a"
    SECTOR_B = "sector_b"
    BOTH = "both"


@dataclass(frozen=True)
class Threshold:
    """Cabeceira de pista."""
    designator: str            # ex.: "09", "27L"
    longitude: float            # graus decimais
    latitude: float             # graus decimais
    elevation_m: float          # metros AMSL


@dataclass
class Runway:
    """Pista de pouso e decolagem."""
    icao_code: str              # ex.: SBGR
    threshold_a: Threshold
    threshold_b: Threshold
    code_number: int            # 1, 2, 3, 4
    code_letter: str            # 'A'..'F'
    project_type: ProjectType = ProjectType.AERODROME
    approach_type_a: ApproachType = ApproachType.VISUAL  # operação na cabeceira A
    approach_type_b: ApproachType = ApproachType.VISUAL  # operação na cabeceira B
    runway_type: RunwayType = RunwayType.NON_INSTRUMENT
    sspv_sector: SSPVSector = SSPVSector.BOTH
    width_m: float = 45.0       # largura física da pista (m)

    def __post_init__(self):
        if self.code_number not in (1, 2, 3, 4):
            raise ValueError(f"code_number inválido: {self.code_number}")
        if self.code_letter.upper() not in tuple("ABCDEF"):
            raise ValueError(f"code_letter inválido: {self.code_letter}")

    @property
    def midpoint_lonlat(self) -> Tuple[float, float]:
        """Ponto médio da pista em coordenadas geográficas (lon, lat)."""
        return (
            0.5 * (self.threshold_a.longitude + self.threshold_b.longitude),
            0.5 * (self.threshold_a.latitude + self.threshold_b.latitude),
        )

    @property
    def reference_elevation_m(self) -> float:
        """Elevação de referência (média das cabeceiras), usada para o ARP."""
        return 0.5 * (self.threshold_a.elevation_m + self.threshold_b.elevation_m)
