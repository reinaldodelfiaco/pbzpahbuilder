#!/usr/bin/env python3
"""
Script para limpar ZIPs antigos com problema de backslashes.
Mantém apenas o ZIP correto (0.3.1).
"""

import os
from pathlib import Path

repo_root = Path(__file__).parent

# ZIPs antigos a remover (com problema)
old_zips = [
    "pbzpa_qgis (2).zip",
    "pbzpa_qgis-0.2.0.zip",
    "pbzpa_qgis-0.3.0.zip",
]

# ZIP backup (pode manter como referência)
backup_file = "pbzpa_qgis-0.3.1.zip.bak"

print("=" * 70)
print("LIMPEZA DE ARQUIVOS ZIP - PBZPA/PBZPH Builder")
print("=" * 70)
print()

# Remover antigos
removed_count = 0
for old_zip in old_zips:
    path = repo_root / old_zip
    if path.exists():
        try:
            os.remove(path)
            print(f"✓ Removido: {old_zip}")
            removed_count += 1
        except Exception as e:
            print(f"✗ Erro ao remover {old_zip}: {e}")

print()
print("ZIP final disponível:")
print()

# Listar ZIPs restantes
zips = sorted(repo_root.glob("*.zip"))
if zips:
    for zf in zips:
        size_kb = zf.stat().st_size / 1024
        print(f"  ✓ {zf.name:<35} ({size_kb:>6.1f} KB)")
else:
    print("  Nenhum arquivo ZIP encontrado")

print()
print("=" * 70)
print(f"✅ Removidos {removed_count} arquivo(s) obsoleto(s)")
print("=" * 70)
