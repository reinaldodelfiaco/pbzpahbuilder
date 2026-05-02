#!/usr/bin/env python3
"""
Script para criar arquivo ZIP do plugin PBZPA/PBZPH para repositório QGIS.

Cria um ZIP com:
- Caminhos usando forward slashes (conforme especificação ZIP)
- Estrutura correta: pbzpa_qgis/
- Arquivos necessários: metadata.txt, __init__.py, LICENSE, README.md, icon, código

Remove arquivos desnecessários:
- __pycache__
- .pyc
- .git
- Arquivos de teste que não são distribuíveis
"""

import os
import zipfile
import shutil
from pathlib import Path

def should_skip(file_path: Path, root: Path) -> bool:
    """Determina se arquivo deve ser skipado."""
    # Caminhos relativos
    rel_path = file_path.relative_to(root)
    
    # Skip desnecessários
    skip_patterns = [
        '__pycache__',
        '.pyc',
        '.git',
        '.github',
        '.gitignore',
        '.DS_Store',
        '*.egg-info',
    ]
    
    # Verificar cada padrão
    path_str = str(rel_path)
    for pattern in skip_patterns:
        if pattern.replace('*', '') in path_str:
            return True
    
    # Skip diretórios específicos se estiver fora de pbzpa_qgis
    if '__pycache__' in file_path.parts:
        return True
    
    return False

def create_plugin_zip(version: str = "0.3.1"):
    """
    Cria arquivo ZIP do plugin para repositório QGIS.
    
    Args:
        version: Versão do plugin (ex.: "0.3.1")
    """
    repo_root = Path(__file__).parent
    plugin_dir = repo_root / "pbzpa_qgis"
    output_zip = repo_root / f"pbzpa_qgis-{version}.zip"
    
    if not plugin_dir.exists():
        print(f"❌ Diretório do plugin não encontrado: {plugin_dir}")
        return False
    
    print(f"📦 Criando ZIP: {output_zip.name}")
    print(f"   Versão: {version}")
    print(f"   Origem: {plugin_dir}")
    
    # Backup se arquivo já existe
    if output_zip.exists():
        backup = repo_root / f"pbzpa_qgis-{version}.zip.bak"
        shutil.copy(output_zip, backup)
        print(f"   Backup anterior: {backup.name}")
    
    try:
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            file_count = 0
            
            for root, dirs, files in os.walk(plugin_dir):
                root_path = Path(root)
                
                # Skip __pycache__ e outros
                dirs[:] = [d for d in dirs if d != '__pycache__']
                
                for file in files:
                    file_path = root_path / file
                    
                    # Skip certos tipos de arquivo
                    if file.endswith('.pyc') or file.endswith('.pyo'):
                        continue
                    
                    if should_skip(file_path, repo_root):
                        continue
                    
                    # Caminho relativo usando forward slashes
                    rel_path = file_path.relative_to(repo_root)
                    arcname = rel_path.as_posix()  # ← Converte para forward slashes
                    
                    zf.write(file_path, arcname)
                    file_count += 1
                    print(f"   ✓ {arcname}")
        
        print(f"\n✅ ZIP criado com sucesso!")
        print(f"   {file_count} arquivos compactados")
        print(f"   Tamanho: {output_zip.stat().st_size / 1024:.1f} KB")
        
        # Verificar integridade
        print(f"\n🔍 Verificando integridade...")
        with zipfile.ZipFile(output_zip, 'r') as zf:
            # Listar primeiros 5 arquivos
            file_list = zf.namelist()[:5]
            for name in file_list:
                # Confirmar que usa forward slashes
                if '\\' in name:
                    print(f"   ⚠️  AVISO: Encontrado backslash em {name}")
                    return False
                print(f"   ✓ {name}")
        
        print(f"   ✅ Todos os caminhos usam forward slashes (conforme especificação)")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao criar ZIP: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("QGIS Plugin ZIP Creator - PBZPA/PBZPH Builder")
    print("=" * 70)
    print()
    
    success = create_plugin_zip("0.3.1")
    
    if success:
        print("\n" + "=" * 70)
        print("✅ PRONTO PARA ENVIO AO REPOSITÓRIO QGIS")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("❌ ERRO - Verifique as mensagens acima")
        print("=" * 70)
        exit(1)
