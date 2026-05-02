# -*- coding: utf-8 -*-
"""Utilidades de detecção automática de zona UTM SIRGAS 2000.

Para o Brasil, o sistema oficial cartográfico é o **SIRGAS 2000**.
Os EPSG das zonas UTM SIRGAS 2000 hemisfério sul são contíguos:

    EPSG:31978 — UTM zona 18S
    EPSG:31979 — UTM zona 19S
    EPSG:31980 — UTM zona 20S
    EPSG:31981 — UTM zona 21S
    EPSG:31982 — UTM zona 22S
    EPSG:31983 — UTM zona 23S
    EPSG:31984 — UTM zona 24S
    EPSG:31985 — UTM zona 25S

E hemisfério norte (Roraima e Amapá):

    EPSG:31972 — UTM zona 18N
    EPSG:31973 — UTM zona 19N
    EPSG:31974 — UTM zona 20N
    EPSG:31975 — UTM zona 21N
    EPSG:31976 — UTM zona 22N
    EPSG:31977 — UTM zona 23N
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UTMZone:
    zone_number: int
    hemisphere: str  # "N" ou "S"
    epsg: int


# Tabela: (zona_n, hemisfério) -> EPSG SIRGAS 2000
_SIRGAS2000_UTM_EPSG: dict[tuple[int, str], int] = {
    # Hemisfério Norte
    (18, "N"): 31972,
    (19, "N"): 31973,
    (20, "N"): 31974,
    (21, "N"): 31975,
    (22, "N"): 31976,
    (23, "N"): 31977,
    # Hemisfério Sul
    (17, "S"): 31977,  # cuidado: zona 17S não tem código próprio em SIRGAS,
    # alguns autores usam 31977 para Acre extremo. Verificar caso a caso.
    (18, "S"): 31978,
    (19, "S"): 31979,
    (20, "S"): 31980,
    (21, "S"): 31981,
    (22, "S"): 31982,
    (23, "S"): 31983,
    (24, "S"): 31984,
    (25, "S"): 31985,
}


def utm_zone_from_lonlat(longitude: float, latitude: float) -> UTMZone:
    """Devolve a zona UTM SIRGAS 2000 que cobre a coordenada geográfica.

    Fórmula universal: zona = floor((lon + 180) / 6) + 1.
    """
    if not (-180.0 <= longitude <= 180.0):
        raise ValueError(f"Longitude fora do intervalo: {longitude}")
    if not (-90.0 <= latitude <= 90.0):
        raise ValueError(f"Latitude fora do intervalo: {latitude}")

    zone_number = int((longitude + 180.0) // 6) + 1
    hemisphere = "N" if latitude >= 0 else "S"
    epsg = _SIRGAS2000_UTM_EPSG.get((zone_number, hemisphere))

    if epsg is None:
        raise ValueError(
            f"Não há código EPSG SIRGAS 2000 catalogado para a zona "
            f"{zone_number}{hemisphere} (lon={longitude}, lat={latitude}). "
            "Considere usar WGS84/UTM (EPSG 327xx/326xx) como fallback."
        )
    return UTMZone(zone_number=zone_number, hemisphere=hemisphere, epsg=epsg)


def epsg_for_lonlat(longitude: float, latitude: float) -> int:
    """Atalho retornando apenas o código EPSG."""
    return utm_zone_from_lonlat(longitude, latitude).epsg
