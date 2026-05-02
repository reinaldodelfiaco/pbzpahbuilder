# -*- coding: utf-8 -*-
"""Exportação para DXF usando :mod:`ezdxf` e (opcional) DWG via ODA File Converter.

Cada superfície vai para um *layer* DXF separado, com cor e nome conforme
convenções aeronáuticas/cartográficas. Os OPEA viram blocos *POINT* com
atributos estendidos (XDATA) contendo altura, cota e classificação.

Convenções de layer/cor (índice AutoCAD ACI):
- ``PBZPA_FAIXA_PISTA``      — cor 7 (branco)
- ``PBZPA_HORIZONTAL_INT``   — cor 4 (ciano)
- ``PBZPA_CONICA``           — cor 3 (verde)
- ``PBZPA_APROXIMACAO``      — cor 5 (azul)
- ``PBZPA_TRANSICAO``        — cor 6 (magenta)
- ``PBZPA_DECOLAGEM``        — cor 2 (amarelo)
- ``OPEA_CONFORME``          — cor 3 (verde)
- ``OPEA_LIMITROFE``         — cor 2 (amarelo)
- ``OPEA_VIOLACAO``          — cor 1 (vermelho)
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Iterable, Optional

from qgis.core import QgsFeature, QgsVectorLayer

LAYER_COLORS = {
    "FAIXA_PISTA": ("PBZPA_FAIXA_PISTA", 7),
    "HORIZONTAL_INTERNA": ("PBZPA_HORIZONTAL_INT", 4),
    "CONICA": ("PBZPA_CONICA", 3),
    "APROXIMACAO": ("PBZPA_APROXIMACAO", 5),
    "TRANSICAO": ("PBZPA_TRANSICAO", 6),
    "DECOLAGEM": ("PBZPA_DECOLAGEM", 2),
}

OPEA_LAYER_BY_STATUS = {
    "CONFORME": ("OPEA_CONFORME", 3),
    "LIMITROFE": ("OPEA_LIMITROFE", 2),
    "VIOLACAO": ("OPEA_VIOLACAO", 1),
    "FORA_PBZPA": ("OPEA_FORA", 8),
}


@dataclass
class DXFExportResult:
    dxf_path: str
    dwg_path: Optional[str]


def export_to_dxf(
    surfaces_layer: QgsVectorLayer,
    opea_layer: Optional[QgsVectorLayer],
    output_path: str,
    convert_to_dwg: bool = False,
    oda_converter_exe: Optional[str] = None,
) -> DXFExportResult:
    """Gera o DXF (e opcionalmente DWG) a partir das camadas.

    :param surfaces_layer: camada PolygonZ com as superfícies.
    :param opea_layer: camada PointZ com OPEA (opcional).
    :param output_path: caminho .dxf de saída.
    :param convert_to_dwg: se True, converte para DWG via ODA File Converter.
    :param oda_converter_exe: caminho do ODAFileConverter.exe (Windows) ou
        do binário Linux. Se None, busca no PATH.
    """
    try:
        import ezdxf  # noqa: WPS433
    except ImportError as exc:
        raise RuntimeError(
            "Biblioteca ezdxf não está instalada. Instale com "
            "`pip install ezdxf` no Python do QGIS (OSGeo4W Shell)."
        ) from exc

    if not output_path.lower().endswith(".dxf"):
        output_path += ".dxf"

    doc = ezdxf.new(setup=True)
    msp = doc.modelspace()

    # --- Superfícies ---
    for f in surfaces_layer.getFeatures():
        tipo = f["tipo"]
        layer_name, color = LAYER_COLORS.get(tipo, (f"PBZPA_{tipo}", 7))
        if layer_name not in doc.layers:
            doc.layers.add(name=layer_name, color=color)
        _add_feature_polygons(msp, f, layer_name)

    # --- OPEA ---
    if opea_layer is not None:
        for f in opea_layer.getFeatures():
            status = f["conflito"] or "FORA_PBZPA"
            layer_name, color = OPEA_LAYER_BY_STATUS.get(status, ("OPEA", 7))
            if layer_name not in doc.layers:
                doc.layers.add(name=layer_name, color=color)
            geom = f.geometry().constGet()
            try:
                x, y, z = geom.x(), geom.y(), geom.z()
            except AttributeError:
                continue
            point = msp.add_point((x, y, z), dxfattribs={"layer": layer_name})
            # Texto descritivo
            label = f"{f['tipo']} h={f['altura_m']:.1f}m"
            msp.add_text(
                label,
                dxfattribs={
                    "layer": layer_name,
                    "height": 5.0,
                    "insert": (x + 5, y + 5, z),
                },
            )

    doc.saveas(output_path)

    dwg_path = None
    if convert_to_dwg:
        dwg_path = _convert_dxf_to_dwg(output_path, oda_converter_exe)
    return DXFExportResult(dxf_path=output_path, dwg_path=dwg_path)


# ======================================================================
# Internos
# ======================================================================

def _add_feature_polygons(msp, feat: QgsFeature, layer_name: str) -> None:
    """Adiciona polígono(s) Z ao modelspace do ezdxf preservando furos como hatch.

    Para PBZPA usa-se 3DPOLYLINE para o contorno (closed) por polígono, dado
    que `LWPOLYLINE` é 2D. Se o polígono tem furos (anel interno, ex.: cônica
    e transição), cada anel é um 3DPOLYLINE separado.
    """
    geom = feat.geometry().constGet()
    polygons = []
    if geom.geometryType().lower().endswith("polygon"):
        # MultiPolygonZ ou PolygonZ
        if hasattr(geom, "numGeometries"):
            for i in range(geom.numGeometries()):
                polygons.append(geom.geometryN(i))
        else:
            polygons.append(geom)

    for poly in polygons:
        for ring_idx in range(poly.numInteriorRings() + 1):
            ring = poly.exteriorRing() if ring_idx == 0 else poly.interiorRing(ring_idx - 1)
            if ring is None:
                continue
            verts = []
            for i in range(ring.numPoints()):
                p = ring.pointN(i)
                verts.append((p.x(), p.y(), p.z()))
            if len(verts) < 2:
                continue
            msp.add_polyline3d(verts, close=True, dxfattribs={"layer": layer_name})


def _convert_dxf_to_dwg(dxf_path: str, oda_exe: Optional[str]) -> Optional[str]:
    """Tenta converter DXF→DWG usando o ODA File Converter (gratuito).

    O ODA usa interface por *batch*: requer pasta de entrada e saída.
    """
    exe = oda_exe or shutil.which("ODAFileConverter") or shutil.which("ODAFileConverter.exe")
    if exe is None:
        raise RuntimeError(
            "ODA File Converter não encontrado. Instale e/ou informe o caminho "
            "do executável (https://www.opendesign.com/guestfiles/oda_file_converter)."
        )
    src_dir = tempfile.mkdtemp(prefix="pbzpa_dxf_")
    dst_dir = tempfile.mkdtemp(prefix="pbzpa_dwg_")
    try:
        new_src = os.path.join(src_dir, os.path.basename(dxf_path))
        shutil.copy2(dxf_path, new_src)
        cmd = [exe, src_dir, dst_dir, "ACAD2018", "DWG", "0", "1"]
        subprocess.run(cmd, check=True, capture_output=True)
        out_dwg = os.path.join(
            dst_dir, os.path.splitext(os.path.basename(dxf_path))[0] + ".dwg"
        )
        if not os.path.exists(out_dwg):
            return None
        final = os.path.splitext(dxf_path)[0] + ".dwg"
        shutil.copy2(out_dwg, final)
        return final
    finally:
        shutil.rmtree(src_dir, ignore_errors=True)
        shutil.rmtree(dst_dir, ignore_errors=True)
