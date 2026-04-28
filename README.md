# PBZPA-QGIS

**Complemento (plugin) QGIS para geração de Planos Básicos de Zona de Proteção de Aeródromo (PBZPA) e de Heliponto (PBZPH)** a partir da análise de imagem de satélite, em conformidade com as normas do Comando da Aeronáutica (ICA 11-3, ICA 11-408, ICA 63-19), da ANAC (RBAC 154 e 155) e seguindo as convenções cartográficas do Exército Brasileiro (T 34-700).

## Funcionalidades

- Geração paramétrica das superfícies limitadoras de obstáculos (faixa de pista, horizontal interna, cônica, aproximação, transição e decolagem) a partir das coordenadas das cabeceiras, classe e tipo de operação da pista.
- Detecção híbrida de Objetos Projetados no Espaço Aéreo (OPEA) sobre imagem de satélite: sugestão automática por modelo de visão computacional (ONNX) e revisão manual pelo operador.
- Análise de conflito OPEA × superfícies, com classificação (conforme / em violação / sob estudo) e relatório.
- Simbologia cartográfica conforme T 34-700 e convenções aeronáuticas (arquivos `.qml`).
- Exportação para **KML** (Google Earth) e **DXF** (compatível com AutoCAD via ODA File Converter para DWG).
- Reprojeção automática para SIRGAS 2000 / UTM com base na coordenada do aeródromo.

## Estrutura do repositório

```
PBZPH/
├── pbzpa_qgis/                # Código-fonte do plugin
│   ├── metadata.txt
│   ├── __init__.py
│   ├── pbzpa_plugin.py        # Classe principal (classFactory)
│   ├── pbzpa_dialog.py        # Lógica do diálogo
│   ├── core/                  # Geometria, detecção, análise
│   │   ├── __init__.py
│   │   ├── surfaces.py
│   │   ├── utm_utils.py
│   │   ├── opea_detection.py
│   │   └── conflict_analysis.py
│   ├── export/                # Exportadores KML / DXF
│   │   ├── __init__.py
│   │   ├── kml_exporter.py
│   │   └── dxf_exporter.py
│   ├── ui/
│   │   └── pbzpa_dialog.ui    # Diálogo Qt Designer
│   ├── styles/                # Estilos .qml
│   ├── resources/             # Ícones, recursos
│   ├── i18n/                  # Traduções
│   └── tests/                 # Testes unitários
├── docs/
│   └── superficies_limitadoras_obstaculos.md
├── .gitignore
├── LICENSE
└── README.md
```

## Instalação (desenvolvimento)

1. Localize a pasta de plugins do QGIS no Windows:
   `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
2. Crie um link simbólico (ou copie) a pasta `pbzpa_qgis/` para esse diretório.
   ```cmd
   mklink /D "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\pbzpa_qgis" "C:\Users\Reinaldo\OneDrive\Documentos\Claude\Projects\PBZPA\PBZPH\pbzpa_qgis"
   ```
3. Reinicie o QGIS, vá em *Complementos → Gerenciar e Instalar Complementos → Instalados* e ative **PBZPA/PBZPH**.

## Dependências

- QGIS 3.44 (LTR ou superior).
- Python 3.9+ (já incluso no QGIS).
- Bibliotecas adicionais (instaladas via *OSGeo4W Shell* com `python -m pip install`):
  - `ezdxf >= 1.2` — exportação DXF.
  - `onnxruntime` — inferência do detector de OPEA.
  - `numpy` (já vem com QGIS).

## Versão DWG

A exportação nativa é em **DXF**. Para gerar **DWG**, instale o
[ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter)
(gratuito) e use o conversor diretamente, ou ative a opção *Converter para DWG*
no diálogo de exportação caso o executável seja detectado.

## Referências normativas

- ICA 11-3 — Plano Básico de Zona de Proteção de Aeródromos.
- ICA 11-408 — Plano Básico de Zona de Proteção de Helipontos.
- ICA 63-19 — Cartas Aeronáuticas.
- RBAC 154 — Projeto de Aeródromos (ANAC).
- RBAC 155 — Heliportos (ANAC).
- T 34-700 — Manual Técnico de Convenções Cartográficas (Exército Brasileiro).
- Anexo 14 da OACI — Aerodromes.
- [PyQGIS Developer Cookbook 3.44](https://docs.qgis.org/3.44/en/docs/pyqgis_developer_cookbook/).

## Licença

Distribuído sob a licença **GPLv3**. Veja o arquivo [LICENSE](./LICENSE).
