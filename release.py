#!/usr/bin/env python3
"""
Script de Release - PBZPA/PBZPH Builder

Automatiza a criação de releases para submissão ao repositório QGIS:
1. Valida estrutura do plugin
2. Cria ZIP conforme especificação (forward slashes)
3. Verifica integridade
4. Atualiza changelogs
5. Cria tag Git (opcional)

Uso:
    python release.py 0.3.1
    python release.py 0.4.0 --create-tag
"""

import os
import sys
import zipfile
import re
from pathlib import Path
from datetime import datetime

def validate_plugin_structure(plugin_dir: Path) -> bool:
    """Valida estrutura mínima do plugin."""
    required_files = [
        "metadata.txt",
        "__init__.py",
        "pbzpa_plugin.py",
        "pbzpa_dialog.py",
        "LICENSE",
    ]
    
    missing = []
    for req_file in required_files:
        if not (plugin_dir / req_file).exists():
            missing.append(req_file)
    
    if missing:
        print(f"❌ Arquivos obrigatórios faltando:")
        for f in missing:
            print(f"   - {f}")
        return False
    
    return True

def validate_metadata(metadata_path: Path, version: str) -> bool:
    """Valida metadata.txt e versão."""
    with open(metadata_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar campos obrigatórios
    required_fields = ['name', 'version', 'description', 'author', 'email', 'license', 'qgisMinimumVersion']
    missing = []
    for field in required_fields:
        if f"{field}=" not in content:
            missing.append(field)
    
    if missing:
        print(f"❌ Campos faltando em metadata.txt:")
        for f in missing:
            print(f"   - {f}")
        return False
    
    # Verificar se versão está correta
    version_match = re.search(r'^version=(.+)$', content, re.MULTILINE)
    if not version_match or version_match.group(1).strip() != version:
        print(f"⚠️  Versão em metadata.txt ({version_match.group(1) if version_match else 'N/A'}) != argumento ({version})")
        print(f"   Atualize metadata.txt antes de continuar")
        return False
    
    # Verificar licença
    if "license=" not in content:
        print(f"❌ Licença não definida em metadata.txt")
        return False
    
    if "GPL" not in content and "MIT" not in content and "license=" in content:
        license_match = re.search(r'^license=(.+)$', content, re.MULTILINE)
        if license_match:
            print(f"⚠️  Licença encontrada: {license_match.group(1)}")
    
    return True

def create_plugin_zip(repo_root: Path, version: str) -> Path:
    """Cria ZIP do plugin com forward slashes."""
    plugin_dir = repo_root / "pbzpa_qgis"
    output_zip = repo_root / f"pbzpa_qgis-{version}.zip"
    
    print(f"📦 Criando ZIP: {output_zip.name}")
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        file_count = 0
        for root, dirs, files in os.walk(plugin_dir):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if file.endswith(('.pyc', '.pyo')):
                    continue
                
                file_path = root_path / file
                rel_path = file_path.relative_to(repo_root)
                arcname = rel_path.as_posix()  # Forward slashes
                
                zf.write(file_path, arcname)
                file_count += 1
    
    print(f"   ✓ {file_count} arquivos")
    print(f"   ✓ Tamanho: {output_zip.stat().st_size / 1024:.1f} KB")
    
    return output_zip

def validate_zip(zip_path: Path) -> bool:
    """Valida integridade do ZIP."""
    print(f"🔍 Validando ZIP...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Verificar backslashes
            for name in zf.namelist():
                if '\\' in name:
                    print(f"   ❌ ERRO: Backslash encontrado: {name}")
                    return False
            
            # Verificar arquivos obrigatórios
            required = ['pbzpa_qgis/metadata.txt', 'pbzpa_qgis/__init__.py', 'pbzpa_qgis/LICENSE']
            namelist = zf.namelist()
            for req in required:
                if req not in namelist:
                    print(f"   ❌ ERRO: {req} não encontrado no ZIP")
                    return False
            
            print(f"   ✅ ZIP válido ({len(namelist)} arquivos)")
            return True
    
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: python release.py <versão> [--create-tag]")
        print("Exemplo: python release.py 0.3.1")
        print("         python release.py 0.4.0 --create-tag")
        sys.exit(1)
    
    version = sys.argv[1]
    create_tag = "--create-tag" in sys.argv
    
    repo_root = Path(__file__).parent
    plugin_dir = repo_root / "pbzpa_qgis"
    
    print("=" * 70)
    print(f"RELEASE BUILDER - PBZPA/PBZPH Builder")
    print("=" * 70)
    print(f"Version: {version}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # 1. Validar estrutura
    print("1️⃣  Validando estrutura do plugin...")
    if not validate_plugin_structure(plugin_dir):
        sys.exit(1)
    print("   ✅ Estrutura OK")
    print()
    
    # 2. Validar metadata
    print("2️⃣  Validando metadata.txt...")
    if not validate_metadata(plugin_dir / "metadata.txt", version):
        sys.exit(1)
    print("   ✅ Metadata OK")
    print()
    
    # 3. Criar ZIP
    print("3️⃣  Criando arquivo ZIP...")
    zip_path = create_plugin_zip(repo_root, version)
    print()
    
    # 4. Validar ZIP
    print("4️⃣  Validando arquivo ZIP...")
    if not validate_zip(zip_path):
        sys.exit(1)
    print()
    
    # 5. Resumo
    print("=" * 70)
    print("✅ RELEASE PRONTO PARA SUBMISSÃO")
    print("=" * 70)
    print()
    print(f"Arquivo: {zip_path.name}")
    print(f"Caminho: {zip_path}")
    print(f"Tamanho: {zip_path.stat().st_size / 1024:.1f} KB")
    print()
    print("Próximos passos:")
    print("1. Subir para GitHub: git add pbzpa_qgis-{version}.zip && git commit -m 'Release {version}'")
    print("2. Criar tag: git tag v{version} && git push origin v{version}")
    print("3. Submeter ao QGIS: https://plugins.qgis.org/manage/admin/")
    print("4. Upload ZIP via formulário web")
    print()
    
    if create_tag:
        print("Criando tag Git...")
        os.system(f"git tag v{version}")
        print(f"✓ Tag criada: v{version}")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
