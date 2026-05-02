# Skills Necessários para Desenvolvimento PBZPA/PBZPH Builder

## 1. CONHECIMENTOS AERONÁUTICOS E REGULATÓRIOS

### Regulamentações Brasileiras
- **ICA 11-3** (Aeródromos Civis - Padrões e Recomendações) - COMAER
- **RBAC 154** (Projeto, Construção e Pouso de Helicópteros) - ANAC
- **Anexo 14 da OACI/ICAO** (Aeródromos - Desenho e Operações)
- **SYSAGA** - Sistema de Gerenciamento da Segurança Operacional Aérea

### Conceitos Aeronáuticos
- Classificação de pistas (Code Number 1-4, Code Letter A-F)
- Superfícies Limitadoras de Obstáculos (SLO)
- PBZPA (Plano Básico de Zona de Proteção de Aeródromo)
- PBZPH (Plano Básico de Zona de Proteção de Heliponto)
- OPEA (Objetos Projetados no Espaço Aéreo)
- SSPV (Setor de Serviço de Proteção em Voo)
- Tipos de operação: Visual, Non-Precision, Precision CAT-I/II/III
- Cabeceiras de pista (designadores, tipos de operação)
- Pistas Não-Operacionais e Setores de Serviço
- Padrões de aproximação e decolagem

### Superfícies Específicas
- Faixa de Pista (Runway Strip)
- Superfície Horizontal Interna (Inner Horizontal)
- Superfície Cônica (Conical)
- Superfície de Aproximação (Approach) — multi-seção
- Superfície de Transição (Transition)
- Superfície de Decolagem (Take-off climb)

---

## 2. CONHECIMENTOS GEOESPACIAIS E SIG (GIS)

### QGIS - QGIS Desktop & API
- Desenvolvimento de plugins QGIS em Python
- Arquitetura de plugins (inicialização, interface gráfica, ciclo de vida)
- QGIS Processing Framework (algoritmos, provedores de processamento)
- Manipulação de camadas vetoriais e raster
- Sistemas de referência de coordenadas (CRS)
- Transformações de coordenadas e reprojeção automática
- Geometrias 3D (PolygonZ, PointZ, LineStringZ)
- Atributos de camadas (fields, features)
- QgsVectorLayer, QgsRasterLayer, QgsFeature, QgsGeometry

### Dados Geoespaciais
- **WGS84** / **SIRGAS 2000** (referencial geodésico brasileiro)
- **UTM** (Universal Transverse Mercator)
- Zonas UTM no Brasil (zonas 18-25)
- Cálculo automático de zona UTM a partir de coordenadas
- Elevação e dados de altitude (AMSL - Above Mean Sea Level)
- Camadas raster georeferenciadas (GeoTIFF, WMS)
- Camadas vetoriais (shapefile, geopackage, etc.)

### Conceitos de SIG
- Reprojeção e transformação de coordenadas
- Geometria computacional (buffers, intersecções, unions)
- Análise espacial de conflitos
- Simbologia e estilos de camadas (QML)
- Renderização de geometrias 3D

---

## 3. ANÁLISE DE IMAGENS GEOESPACIAIS E SENSORIAMENTO REMOTO

### Processamento de Imagens
- Manipulação de imagens raster
- Normalização e redimensionamento de imagens
- Tiling de imagens grandes (ex.: 1024×1024 px com sobreposição)
- Detecção de bordas e artefatos de tile
- Georeferenciamento de imagens

### Visão Computacional com Machine Learning
- **ONNX Runtime** (inferência de modelos)
- **YOLOv8n** (detecção de objetos finetuned em edifícios)
- Bounding boxes (caixa delimitadora, confiança)
- Reprojeção de coordenadas pixel ↔ geoespaciais
- Modelos de visão pré-treinados e fine-tuning
- Datasets de sensoriamento remoto
- Detecção automática de:
  - Edificações
  - Torres e antenas
  - Vegetação
  - Estruturas diversas

### Análise de Conflito OPEA
- Comparação volumétrica: OPEA vs. Superfícies de Proteção
- Topo de estrutura vs. altura de superfície
- Relatórios de conflito e sugestões de altura mínima

---

## 4. PROGRAMAÇÃO E DESENVOLVIMENTO DE SOFTWARE

### Linguagens Principais
- **Python** (3.8+)
  - Dataclasses (@dataclass, frozen)
  - Enumerações (Enum)
  - Type hints e verificação de tipos
  - Context managers (with statements)
  - Decoradores
  - Logging
  - Tratamento de exceções

### Bibliotecas Python
- **QGIS Python API** (PyQGIS)
- **ezdxf** (exportação DXF)
- **onnxruntime** (inferência ML)
- **GDAL/OGR** (via QGIS)
- **json** (configuração, dados)

### Paradigmas de Programação
- Programação orientada a objetos (OOP)
- Programação funcional (map, filter, comprehensions)
- Design patterns (Factory, Builder, Provider)

### Controle de Versão
- Git e GitHub
- Commits semânticos
- Branches e pull requests
- Markdowndocumentation

---

## 5. EXPORTAÇÃO E FORMATOS DE DADOS

### Formatos Suportados
- **KML/KMZ** (Google Earth)
  - altitudeMode = 'absolute' para AMSL
  - Múltiplas camadas em KMZ
- **DXF** (AutoCAD Drawing Exchange Format)
  - Geometrias 3D
  - Layers e entidades
  - Metadados de design
- **DWG** (via ODA File Converter)
- **CSV** (dados tabulares, elevações)
- **HTML** (fichas informativas)

### Drivers e Converters
- GDAL/OGR drivers (KML, DXF, Shapefile)
- QgsVectorFileWriter (QGIS)
- ODA File Converter (DWG opcional)

---

## 6. INTERFACE GRÁFICA E UX

### Qt Framework
- **PyQt5** (via QGIS)
  - Widgets (QDialog, QComboBox, QLineEdit, QTableWidget)
  - Layouts (QVBoxLayout, QGridLayout)
  - Signals e slots
  - Validação de entrada

### UI Design
- Design de diálogos intuitivos
- Wizard (multi-step workflows)
- Feedback ao usuário (mensagens, progresso)
- Acessibilidade
- Internacionalização (i18n, .ts/.qm)

### Arquivo UI
- Qt Designer (.ui XML)
- Compilação de recursos (.qrc)

---

## 7. MATEMÁTICA E GEOMETRIA COMPUTACIONAL

### Geometria 3D
- Planos em 3D (superfícies horizontais, cônicas)
- Pontos, linhas, polígonos em coordenadas cartesianas (X, Y, Z)
- Transformações de coordenadas geográficas ↔ cartesianas

### Cálculos Geométricos
- Distâncias (Haversine para WGS84, Euclidiana em UTM)
- Ângulos e azimutes
- Buffers e offset de geometrias
- Intersecções volumétricas

### Matemática Aplicada
- Gradientes (inclinações de superfícies)
- Divergência (alargamento de superfícies de aproximação)
- Cálculo de elevação a partir de componentes (e.g., Z = elevation + height)

---

## 8. FERRAMENTAS E PLATAFORMAS

### Ambiente de Desenvolvimento
- **QGIS 3.44+** (instalação e configuração)
- Python do QGIS (embutido, não é o Python do sistema)
- IDE/Editor (VS Code, PyCharm, etc.)

### Geração e Documentação
- Markdown (documentação)
- Docstrings Python (PEP 257)
- Sphinx (geração de docs)

### Internacionalização
- Qt Linguist (.ts → .qm)
- Suporte multilíngue (português, inglês)

---

## 9. TESTES E VALIDAÇÃO

### Testes
- Testes unitários (unittest, pytest)
- Validação de parâmetros (bounds, enums)
- Testes de geração de geometrias
- Comparação de outputs esperados

### Qualidade de Código
- Type hints
- Linting (flake8, pylint)
- Code coverage
- Documentação de código

---

## 10. CONHECIMENTOS COMPLEMENTARES

### Workflows Aeronáuticos
- Processo de aprovação de PBZPA/PBZPH
- Revisão técnica e conformidade
- Exportação para sistema SYSAGA
- Documentação técnica de aeródromos

### Segurança e Compliance
- Aviação civil brasileira (ANAC)
- Segurança operacional aérea
- Confidencialidade de dados de aeródromos

### Performance e Otimização
- Tiling de imagens grandes
- Detecção de GPU (quando disponível)
- Cache de transformações de coordenadas
- Reprojeção eficiente

---

## MAPA DE APRENDIZADO RECOMENDADO

### Fase 1: Fundações (Semanas 1-4)
1. Regulamentações brasileiras (ICA 11-3, RBAC 154)
2. Conceitos de pistas e superfícies limitadoras
3. QGIS e PyQGIS basics
4. WGS84 e UTM

### Fase 2: Núcleo Técnico (Semanas 5-8)
1. Desenvolvimento de plugins QGIS
2. Geometria 3D e transformações de coordenadas
3. Cálculos de superfícies (horizontal, cônica, aproximação)
4. OPEA e análise de conflito

### Fase 3: Integração (Semanas 9-12)
1. Machine Learning com ONNX Runtime
2. Exportação (KML, DXF)
3. Integração SYSAGA
4. Testes e validação

### Fase 4: Especialização (Contínua)
1. Otimizações de performance
2. Novos modelos de ML
3. Conformidade com atualizações normativas
4. Suporte a novos formatos

---

## SKILLS TRANSVERSAIS

- **Comunicação técnica** em português (documentação, comentários)
- **Trabalho colaborativo** (Git, revisão de código)
- **Resolução de problemas** complexos em SIG
- **Aprendizado contínuo** de normas aeronáuticas e tecnologias
- **Atenção a detalhes** (cálculos de superfícies, conformidade regulatória)
