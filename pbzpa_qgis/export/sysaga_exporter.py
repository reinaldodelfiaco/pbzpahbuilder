# -*- coding: utf-8 -*-
"""Relatorios auxiliares para conferencia e lancamento no SYSAGA.

O SYSAGA recebe, alem do desenho, dados tabulares que normalmente sao
conferidos pelo operador antes do envio: ficha informativa do aerodromo e
planilha de elevacoes das superficies. Este modulo gera arquivos simples
(HTML/CSV) que podem ser visualizados no QGIS ou abertos em planilha.
"""
from __future__ import annotations

import csv
import html
import os
from dataclasses import dataclass
from typing import Optional

from qgis.core import QgsVectorLayer

from ..core.runway import ApproachType, ProjectType, Runway, RunwayType, SSPVSector


APPROACH_LABELS = {
    ApproachType.NOT_OPERATIONAL: "Nao opera",
    ApproachType.VISUAL: "Visual",
    ApproachType.NON_PRECISION: "Nao precisao",
    ApproachType.PRECISION_CAT_I: "Precisao CAT I",
    ApproachType.PRECISION_CAT_II: "Precisao CAT II",
    ApproachType.PRECISION_CAT_III: "Precisao CAT III",
}

RUNWAY_TYPE_LABELS = {
    RunwayType.NON_INSTRUMENT: "Nao instrumento",
    RunwayType.INSTRUMENT: "Instrumento",
}

SSPV_LABELS = {
    SSPVSector.NONE: "Sem SSPV",
    SSPVSector.SECTOR_A: "Somente setor da cabeceira A",
    SSPVSector.SECTOR_B: "Somente setor da cabeceira B",
    SSPVSector.BOTH: "Ambos os setores",
}

PROJECT_TYPE_LABELS = {
    ProjectType.AERODROME: "Aerodromo (PBZPA)",
    ProjectType.HELIPORT: "Heliponto (PBZPH)",
}


@dataclass(frozen=True)
class SysagaPackage:
    info_html_path: str
    elevations_csv_path: str


def informational_sheet_html(runway: Runway) -> str:
    rows = [
        ("Tipo de projeto", PROJECT_TYPE_LABELS[runway.project_type]),
        ("Designativo OACI", runway.icao_code),
        ("Codigo de referencia", f"{runway.code_number}{runway.code_letter.upper()}"),
        ("Tipo de pista", RUNWAY_TYPE_LABELS[runway.runway_type]),
        ("Largura fisica da pista (m)", f"{runway.width_m:.2f}"),
        ("Cabeceira A", runway.threshold_a.designator),
        ("Latitude A", f"{runway.threshold_a.latitude:.8f}"),
        ("Longitude A", f"{runway.threshold_a.longitude:.8f}"),
        ("Elevacao A (m)", f"{runway.threshold_a.elevation_m:.2f}"),
        ("Operacao A", APPROACH_LABELS[runway.approach_type_a]),
        ("Cabeceira B", runway.threshold_b.designator),
        ("Latitude B", f"{runway.threshold_b.latitude:.8f}"),
        ("Longitude B", f"{runway.threshold_b.longitude:.8f}"),
        ("Elevacao B (m)", f"{runway.threshold_b.elevation_m:.2f}"),
        ("Operacao B", APPROACH_LABELS[runway.approach_type_b]),
        ("Setor SSPV", SSPV_LABELS[runway.sspv_sector]),
        ("Elevacao de referencia ARP (m)", f"{runway.reference_elevation_m:.2f}"),
    ]
    body = "\n".join(
        "<tr><th>{}</th><td>{}</td></tr>".format(html.escape(label), html.escape(value))
        for label, value in rows
    )
    title = f"Ficha informativa - {html.escape(runway.icao_code)}"
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; color: #202124; }}
    h1 {{ font-size: 20px; margin: 0 0 16px; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 900px; }}
    th, td {{ border: 1px solid #c9ced6; padding: 7px 9px; text-align: left; }}
    th {{ width: 34%; background: #f3f5f7; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <table>{body}</table>
</body>
</html>
"""


def elevations_rows(surfaces_layer: Optional[QgsVectorLayer]) -> list[dict[str, str]]:
    if surfaces_layer is None:
        return []
    rows: list[dict[str, str]] = []
    for feature in surfaces_layer.getFeatures():
        rows.append(
            {
                "id": str(feature["id"]),
                "tipo": str(feature["tipo"]),
                "subtipo": str(feature["subtipo"] or ""),
                "cota_min_m": _format_number(feature["cota_min_m"]),
                "cota_max_m": _format_number(feature["cota_max_m"]),
                "gradiente": _format_number(feature["gradiente"]),
                "origem": str(feature["origem"] or ""),
            }
        )
    return rows


def elevations_csv_text(surfaces_layer: Optional[QgsVectorLayer]) -> str:
    fieldnames = ["id", "tipo", "subtipo", "cota_min_m", "cota_max_m", "gradiente", "origem"]
    rows = elevations_rows(surfaces_layer)
    lines = [";".join(fieldnames)]
    for row in rows:
        lines.append(";".join(row[name] for name in fieldnames))
    return "\n".join(lines) + "\n"


def export_sysaga_package(
    runway: Runway,
    surfaces_layer: Optional[QgsVectorLayer],
    output_dir: str,
) -> SysagaPackage:
    os.makedirs(output_dir, exist_ok=True)
    prefix = runway.icao_code.lower() or "pbzpa"
    info_path = os.path.join(output_dir, f"{prefix}_ficha_informativa.html")
    elevations_path = os.path.join(output_dir, f"{prefix}_planilha_elevacoes.csv")

    with open(info_path, "w", encoding="utf-8", newline="") as fh:
        fh.write(informational_sheet_html(runway))

    rows = elevations_rows(surfaces_layer)
    with open(elevations_path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["id", "tipo", "subtipo", "cota_min_m", "cota_max_m", "gradiente", "origem"],
            delimiter=";",
        )
        writer.writeheader()
        writer.writerows(rows)

    return SysagaPackage(info_html_path=info_path, elevations_csv_path=elevations_path)


def _format_number(value) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.3f}"
    except (TypeError, ValueError):
        return str(value)
