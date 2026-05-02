# Submissão ao Repositório QGIS - Guia Completo

## ✅ Status Atual (v0.3.1)

### Problema Corrigido
❌ **ANTES:** ZIPs continham backslashes nos caminhos internos (Windows)
```
pbzpa_qgis\LICENSE  ← Não permitido pela especificação ZIP
pbzpa_qgis\metadata.txt  ← Inválido
```

✅ **AGORA:** ZIP gerado com forward slashes (conforme QGIS)
```
pbzpa_qgis/LICENSE  ← Correto
pbzpa_qgis/metadata.txt  ← Válido
```

### Arquivo Válido
- **File:** `pbzpa_qgis-0.3.1.zip`
- **Size:** 39.7 KB
- **Format:** ZIP conforme especificação QGIS
- **Status:** ✅ Pronto para envio

---

## 📋 Checklist Pré-Submissão

### Licença ✅
- [x] Licença definida em `metadata.txt`: **GPL-3.0-or-later**
- [x] Arquivo `pbzpa_qgis/LICENSE` presente (texto integral)
- [x] Autor atribuído: **Fiaco** (cmtefiaco@gmail.com)
- [x] Copyright: **2026 Fiaco**

### Estrutura ✅
- [x] `metadata.txt` com todos os campos obrigatórios
- [x] `__init__.py` com `classFactory()`
- [x] `pbzpa_plugin.py` com classe `PBZPAPlugin`
- [x] `pbzpa_dialog.py` com interface principal
- [x] Ícone: `resources/icon.png`
- [x] README.md com documentação
- [x] Código bem organizado em módulos

### Configuração ✅
- [x] `qgisMinimumVersion=3.22`
- [x] `qgisMaximumVersion=3.99`
- [x] Versão atualizada: 0.3.1
- [x] Categoria: Vector
- [x] Flags: `experimental=True`, `deprecated=False`
- [x] Processing provider registrado

### ZIP ✅
- [x] Caminhos com forward slashes (não backslashes)
- [x] Estrutura: `pbzpa_qgis/` como root
- [x] Sem arquivos desnecessários (__pycache__, .pyc, etc.)
- [x] Sem diretórios .git ou .github
- [x] 27 arquivos compactados

### Documentação ✅
- [x] README.md (português)
- [x] user_manual.md (inglês)
- [x] superficies_limitadoras_obstaculos.md (referência técnica)
- [x] Comentários em docstrings
- [x] Type hints no código

### Teste ✅
- [x] Plugin instalável via symlink (instrução no README)
- [x] Testado em QGIS 3.44
- [x] Processing Provider funcional
- [x] Exemplos fornecidos (4 aeródromos)

---

## 🚀 Como Submeter ao QGIS Repository

### Passo 1: Preparar Repositório Git
```bash
# No seu repositório GitHub
cd pbzpahbuilder

# Certificar que está sincronizado
git status
git pull

# Criar branch para submissão (opcional)
git checkout -b qgis-submission/v0.3.1
```

### Passo 2: Gerar ZIP Conforme Especificação

**Opção A:** Usar script Python (recomendado)
```bash
python create_plugin_zip.py
# Gera: pbzpa_qgis-0.3.1.zip
```

**Opção B:** Manual via linha de comando (Windows PowerShell)
```powershell
# NÃO use compressão nativa do Windows (cria backslashes)
# Use 7-Zip, WinRAR ou similar com opção "Unix paths"
# OU use Python (mais seguro)
```

### Passo 3: Validar ZIP
```bash
# Verificar que não tem backslashes
python -c "
import zipfile
with zipfile.ZipFile('pbzpa_qgis-0.3.1.zip') as z:
    for name in z.namelist()[:5]:
        if '\\\\' in name:
            print(f'❌ ERRO: Backslash em {name}')
            exit(1)
        print(f'✓ {name}')
    print('✅ ZIP válido para QGIS')
"
```

### Passo 4: Acessar QGIS Plugin Repository

1. Abra: https://plugins.qgis.org/manage/admin/
2. Faça login com sua conta (criar se necessário)
3. Clique em **Upload Plugin** ou **Submit New Plugin**

### Passo 5: Preencher Formulário de Submissão

**Informações do Plugin:**
- **Name:** PBZPA/PBZPH
- **Description:** Generates Brazilian aerodrome and heliport protection plans (PBZPA/PBZPH), obstacle surfaces, OPEA checks, CAD/KML exports, and SYSAGA support sheets.
- **Version:** 0.3.1
- **Tags:** aviation, airport, heliport, aerodrome, PBZPA, PBZPH, obstacle, CAD, KML, DXF, DWG, brazil
- **Category:** Vector
- **License:** GNU General Public License v3 or later (GPLv3+)
- **Author:** Fiaco
- **Email:** cmtefiaco@gmail.com
- **Repository:** https://github.com/reinaldodelfiaco/pbzpahbuilder
- **Issue Tracker:** https://github.com/reinaldodelfiaco/pbzpahbuilder/issues
- **Homepage:** https://github.com/reinaldodelfiaco/pbzpahbuilder#readme
- **Minimum QGIS Version:** 3.22
- **Maximum QGIS Version:** 3.99

**Flags:**
- [x] Experimental: **Sim** (bloqueio PBZPH até autenticação SYSAGA)
- [ ] Deprecated: **Não**

**Changelog:**
```
0.3.1 - Prepare metadata, package documentation and license for QGIS plugin repository submission.
0.3.0 - Add PBZPA/PBZPH project type selector and conservative PBZPH blocking pending authenticated SYSAGA Annex B verification.
0.2.0 - Add inactive runway end option, SSPV sector selector, SYSAGA support sheet and elevation table exports.
0.1.0 - Initial PBZPA surface generation, OPEA analysis and KML/DXF export.
```

**Upload ZIP:**
- Selecione: `pbzpa_qgis-0.3.1.zip`
- O sistema vai validar automaticamente

### Passo 6: Revisão Automática

O repositório QGIS vai:
1. ✅ Extrair o ZIP
2. ✅ Validar `metadata.txt`
3. ✅ Verificar `__init__.py` e `classFactory()`
4. ✅ Confirmar licença
5. ✅ Testar se o plugin carrega

Se houver erro, você receberá:
- Email com detalhes do problema
- Opção para corrigir e reenviar

### Passo 7: Aprovação

Após envio bem-sucedido:
- Plugin fica em status "awaiting review" (24-48h)
- Revisor da comunidade valida:
  - Código
  - Funcionalidade
  - Documentação
  - Conformidade com QGIS
- Se aprovado: ✅ Publicado no repositório oficial

---

## 🔧 Troubleshooting

### Erro: "Backslashes in file names"

**Causa:** ZIP criado com caminho errado

**Solução:**
```bash
# Use script Python
python create_plugin_zip.py

# OU verifique o ZIP
python -c "import zipfile; print([f for f in zipfile.ZipFile('seu_arquivo.zip').namelist() if '\\\\' in f])"
```

### Erro: "metadata.txt not found"

**Causa:** ZIP não contém estrutura `pbzpa_qgis/`

**Solução:**
```bash
# ZIP deve ter: pbzpa_qgis/metadata.txt (não só metadata.txt)
# Use create_plugin_zip.py que faz isto automaticamente
```

### Erro: "LICENSE file missing"

**Causa:** Arquivo de licença não incluído

**Solução:**
```bash
# Certifique que pbzpa_qgis/LICENSE existe
ls -la pbzpa_qgis/LICENSE

# Se falta, adicione (ver Passo Adicional abaixo)
```

### Plugin não carrega após instalação

**Causa:** Erro na estrutura ou importação

**Solução:**
1. Verificar console de erros do QGIS (Plugins > Python Console)
2. Verificar que `__init__.py` tem `classFactory()`
3. Certificar que não há imports circulares

---

## 📚 Passo Adicional: Se Faltar LICENSE

Se o arquivo LICENSE não estiver em `pbzpa_qgis/`:

```bash
cd pbzpa_qgis
# Copiar do repositório raiz
cp ../LICENSE LICENSE

# Verificar
ls -la LICENSE

# Regenerar ZIP
cd ..
python create_plugin_zip.py
```

---

## 📞 Contato Suporte QGIS

Se houver problemas após submissão:

- **Email:** plugins@qgis.org
- **Forum:** https://community.qgis.org/
- **GitHub Issues:** https://github.com/qgis/plugins.qgis.org/issues
- **Community Chat:** https://qgis.org/community/

Inclua na mensagem:
- Plugin name: PBZPA/PBZPH
- Version: 0.3.1
- Descrição do problema
- Linha de erro (se disponível)

---

## 📊 Resumo da Licença

```
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2026 Fiaco

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

License text: https://www.gnu.org/licenses/gpl-3.0.txt
```

**Permissões:**
- ✅ Usar comercialmente
- ✅ Modificar
- ✅ Distribuir
- ✅ Usar em obra privada

**Obrigações:**
- 📋 Informar mudanças
- 📋 Disclouse código-fonte
- 📋 Incluir licença
- 📋 Avisar sobre alterações

---

## ✅ Pronto para Submissão!

**Arquivo:** `pbzpa_qgis-0.3.1.zip` (39.7 KB)  
**Status:** ✅ Conforme especificação QGIS  
**Licença:** ✅ GNU GPLv3 (atribuída a Fiaco, 2026)  
**Data:** 2 de maio de 2026  

**Próximo passo:** Acessar https://plugins.qgis.org/manage/admin/ e fazer upload do ZIP

---

*Guia de Submissão - PBZPA/PBZPH Builder v0.3.1*  
*Última atualização: 2 de maio de 2026*
