# Guia Rápido de Referência - Skills PBZPA/PBZPH

## 🎯 Resposta Rápida: Qual Skill Aprender Agora?

```
┌─────────────────────────────────────────────────────────────┐
│ SOU...                      → COMECE COM                     │
├─────────────────────────────────────────────────────────────┤
│ Programador Python          → QGIS & SIG (2-3 semanas)      │
│ Engenheiro Aeronáutico      → Python & QGIS (4-6 semanas)   │
│ Engenheiro SIG/GIS          → Regulamentações (1-2 semanas) │
│ Iniciante em tudo           → Python → QGIS → Aero (8 sem.) │
│ Experiente em programação   → QGIS → SIG → Aero (6 semanas) │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 Top 10 Conceitos Que Você PRECISA Dominar

| # | Conceito | Por Quê | Tempo |
|---|----------|--------|-------|
| 1 | **6 Superfícies Limitadoras** | Núcleo do projeto | 3-4 sem |
| 2 | **WGS84 → SIRGAS 2000 → UTM** | Conversão automática | 2-3 sem |
| 3 | **Geometrias 3D (PolygonZ)** | Superfícies com altitude | 2-3 sem |
| 4 | **PyQGIS Plugin Architecture** | Framework do projeto | 1-2 sem |
| 5 | **Code Number/Letter** | Parametrização de pistas | 1 sem |
| 6 | **OPEA Detection & Conflict** | Análise de obstáculos | 2 sem |
| 7 | **KML/DXF Export** | Entrega de resultados | 1-2 sem |
| 8 | **Python Dataclasses + Type Hints** | Qualidade de código | 1 sem |
| 9 | **Qt/PyQt5 Dialogs** | Interface do usuário | 2 sem |
| 10 | **ONNX Runtime + YOLOv8** | ML para OPEA | 2-3 sem |

---

## 🔑 Termos Técnicos Essenciais (Glossário)

### Aeronáutica
- **PBZPA** = Plano Básico de Zona de Proteção de Aeródromo
- **PBZPH** = Plano Básico de Zona de Proteção de Heliponto
- **OPEA** = Objetos Projetados no Espaço Aéreo
- **SSPV** = Setor de Serviço de Proteção em Voo
- **ICA 11-3** = Instrução do Comando da Aeronáutica (PBZPA)
- **RBAC 154** = Regulamento Brasileiro de Aviação Civil (Helicópteros)
- **Code Number** = Classificação por comprimento básico (1-4)
- **Code Letter** = Classificação por envergadura (A-F)
- **ARP** = Aerodrome Reference Point

### Geoespacial
- **CRS** = Coordinate Reference System (sistema de coordenadas)
- **EPSG** = European Petroleum Survey Group (código de projeção)
- **WGS84** = World Geodetic System 1984 (lat/lon global)
- **SIRGAS 2000** = Sistema de Referência Geocêntrico das Américas
- **UTM** = Universal Transverse Mercator (projeção em zonas)
- **AMSL** = Above Mean Sea Level (elevação acima do nível do mar)
- **GeoTIFF** = TIFF georeferenciado (imagem raster)
- **KML** = Keyhole Markup Language (Google Earth)
- **DXF** = Drawing Exchange Format (AutoCAD)

### Programação
- **PyQGIS** = Python API do QGIS
- **QgsVectorLayer** = Camada vetorial (pontos, linhas, polígonos)
- **QgsRasterLayer** = Camada raster (imagem, DEM)
- **QgsFeature** = Entidade individual (ex.: um polígono)
- **QgsGeometry** = Geometria (shape em formato QGIS)
- **PolygonZ** = Polígono 3D com altitude (Z)
- **PointZ** = Ponto 3D
- **GDAL/OGR** = Biblioteca para dados geoespaciais
- **ONNX** = Open Neural Network Exchange (formato de modelo ML)

### Superfícies (6 tipos)
1. **Runway Strip** = Faixa de pista (zona imediata)
2. **Inner Horizontal** = Superfície horizontal interna (plano)
3. **Conical** = Cônica (cone ascendente)
4. **Approach** = Aproximação (multi-seção, para pouso)
5. **Transition** = Transição (conecta superfícies)
6. **Take-off Climb** = Decolagem (para voo após decolagem)

---

## 💡 Padrões de Código Mais Frequentes

### Padrão 1: Criar Geometria 3D
```python
from qgis.core import QgsPoint, QgsPolygon, QgsGeometry

points = [
    QgsPoint(x1, y1, z1),
    QgsPoint(x2, y2, z2),
    QgsPoint(x3, y3, z3),
    QgsPoint(x1, y1, z1),  # Fechar polígono
]
polygon = QgsPolygon([points])
geometry = QgsGeometry(polygon)
```

### Padrão 2: Transformar Coordenadas
```python
from qgis.core import QgsCoordinateTransform, QgsPointXY

transform = QgsCoordinateTransform(crs_wgs84, crs_utm, project)
pt_wgs84 = QgsPointXY(-46.5, -23.5)
pt_utm = transform.transform(pt_wgs84)
```

### Padrão 3: Adicionar Feature à Camada
```python
from qgis.core import QgsFeature

feature = QgsFeature(layer.fields())
feature.setGeometry(geometry)
feature['tipo'] = 'HORIZONTAL'
feature['altura_m'] = 45.0
layer.addFeature(feature)
```

### Padrão 4: Enumerar e Validar
```python
from enum import Enum
from dataclasses import dataclass

class ApproachType(str, Enum):
    VISUAL = "visual"
    NON_PRECISION = "non_precision"

@dataclass(frozen=True)
class Threshold:
    designator: str
    longitude: float
    latitude: float
    elevation_m: float
    
    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Latitude inválida: {self.latitude}")
```

### Padrão 5: Processar Raster com Tiling
```python
def processar_imagem_grande(image_path, tile_size=1024):
    """Processa imagem em tiles para evitar timeout ML."""
    tiles = []
    image = rasterio.open(image_path)
    
    for x in range(0, image.width, tile_size):
        for y in range(0, image.height, tile_size):
            window = ((y, y+tile_size), (x, x+tile_size))
            tile = image.read(window=window)
            tiles.append((tile, x, y))
    
    return tiles
```

---

## 📖 Arquivos do Projeto - O Que Ler Primeiro

### Leitura Obrigatória (Ordem)
1. **README.md** (visão geral)
2. **docs/superficies_limitadoras_obstaculos.md** (referência normativa)
3. **pbzpa_qgis/core/runway.py** (modelos de dados)
4. **pbzpa_qgis/core/surfaces.py** (geração de geometrias)
5. **pbzpa_qgis/pbzpa_plugin.py** (ciclo de vida)
6. **pbzpa_qgis/pbzpa_dialog.py** (interface)
7. **pbzpa_qgis/core/conflict_analysis.py** (análise)
8. **pbzpa_qgis/export/** (exportação)

### Leitura Complementar
- `core/utm_utils.py` (transformação de coordenadas)
- `core/opea_detection.py` (detecção ML)
- `tests/test_utm_utils.py` (exemplos de teste)
- `metadata.txt` (configuração de plugin)

---

## ⚡ Comandos Rápidos (CLI/Terminal)

### Verificar Zona UTM (Python)
```python
from pbzpa_qgis.core.utm_utils import epsg_for_lonlat
epsg = epsg_for_lonlat(-46.5, -23.5)  # SBGR (São Paulo)
print(epsg)  # → 31983 (SIRGAS 2000 / UTM zone 23S)
```

### Instalar Plugin em Desenvolvimento
```bash
mklink /D "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\pbzpa_qgis" \
    "C:\Users\Reinaldo\OneDrive\Documentos\GitHub\pbzpahbuilder\pbzpa_qgis"
```

### Testar Exemplo SBGR (Guarulhos)
```bash
# Abrir QGIS, carregar exemplo: examples/sbgr_guarulhos/runway.json
# (Este é um JSON com coordenadas das cabeceiras)
```

---

## 🎓 Materiais de Estudo por Skill

| Skill | Requer | Duração | Curvas Típicas |
|-------|--------|---------|----------------|
| **ICA 11-3** | Nenhum | 2-3 sem | 📚 Documentação densa |
| **QGIS** | Python | 2-4 sem | 📈 Curva de aprendizado suave |
| **PyQGIS** | Python + QGIS | 2-3 sem | 📈 Exemplos práticos ajudam |
| **Coordenadas** | SIG + Matemática | 2-3 sem | 📊 Muita prática necessária |
| **Superfícies** | Matemática + SIG | 3-4 sem | ⛰️ Difícil, mas crucial |
| **OPEA/Conflito** | Superfícies + SIG | 2 sem | 📈 Lógica clara |
| **KML/DXF** | GDAL/OGR | 1-2 sem | 📚 Bem documentado |
| **ML (ONNX)** | Python | 2-3 sem | 📚 Frameworks abstraem detalhes |
| **PyQt5** | Python | 2-3 sem | 📈 Muitos exemplos online |
| **Git** | Nenhum | 1 sem | 📈 Muito fácil de aprender |

---

## 🚨 Armadilhas Comuns

| Armadilha | Como Evitar |
|-----------|------------|
| Confundir WGS84 lon/lat com x/y UTM | Usar `QgsPointXY(-46.5, -23.5)` para lon/lat |
| Esquecer que superfícies são 3D | Sempre retornar `PolygonZ`, não `Polygon` |
| Código sem validações de entrada | Usar `@dataclass` com `__post_init__` |
| Quebrar ao atualizar QGIS | Testar em múltiplas versões (3.22+) |
| Performance ruim com imagens grandes | Implementar tiling desde o início |
| Unidade errada (pés vs metros) | Tudo é **metros AMSL** no projeto |
| Zona UTM errada | Calcular automaticamente via `epsg_for_lonlat()` |

---

## 🏁 Checklist de Onboarding (1ª Semana)

- [ ] Clonar repositório e estudar README
- [ ] Ler ICA 11-3 (seções das 6 superfícies)
- [ ] Instalar QGIS 3.44+
- [ ] Configurar ambiente Python (venv)
- [ ] Executar projeto em desenvolvimento
- [ ] Abrir exemplos (sbgl_galeao, sbgr_guarulhos)
- [ ] Entender estrutura de camadas geradas
- [ ] Explorar código: `runway.py` → `surfaces.py`
- [ ] Fazer 1ª contribuição (bugfix ou doc)
- [ ] Agendar mentoria com desenvolvedor

---

## 📞 Quando Pedir Ajuda

| Situação | Ação |
|----------|------|
| "Qual é a zona UTM do meu aeródromo?" | Usar `epsg_for_lonlat(lon, lat)` |
| "Por que a superfície fica abaixo da topografia?" | Revisar valores da ICA 11-3 |
| "QGIS trava ao carregar imagem grande" | Implementar tiling (ex.: 1024×1024 px) |
| "Não entendo uma regulamentação" | Consultar especialista aeronáutico |
| "Como exportar para DWG?" | Usar ODA File Converter (opcional) |
| "ML não detecta prédios" | Verificar imagem (resolução mínima), model |
| "Plugin não aparece em QGIS" | Verificar metadata.txt, logs de erro |

---

## 🔗 Links Essenciais

### Oficiais
- [QGIS Documentation](https://docs.qgis.org/)
- [PyQGIS API](https://qgis.org/pyqgis/)
- [GDAL/OGR](https://gdal.org/)
- [PROJ Transformations](https://proj.org/)

### Regulatórios Brasileiros
- **ICA 11-3** (COMAER) - Publicado em Boletim do Comando da Aeronáutica
- **RBAC 154** (ANAC) - Publicado em Diário Oficial da União
- **SYSAGA** - Sistema da Secretaria de Aviação Civil

### Tecnologias
- [ONNX Runtime](https://onnxruntime.ai/)
- [YOLOv8](https://docs.ultralytics.com/models/yolov8/)
- [ezdxf](https://ezdxf.readthedocs.io/)
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)

### Comunidades
- [QGIS Brasil](https://www.facebook.com/groups/qgisbrasil/)
- [Stack Overflow (tag: qgis)](https://stackoverflow.com/questions/tagged/qgis)
- [GitHub Issues do Projeto](https://github.com/reinaldodelfiaco/pbzpahbuilder/issues)

---

## 📊 Correlação de Skills

```
                        PBZPA/PBZPH Developer
                                ▲
                    ┌───────────┼───────────┐
                    │           │           │
               QGIS API    Regulamentações  ML/Vision
                  ▲             ▲               ▲
          ┌───────┼──────┐      │           ┌───┴────┐
          │       │      │      │           │        │
       Python  Geom.   Coords  Aero       ONNX   Visão
       ▲        3D     Transform        Runtime Computa.
       │        ▲        ▲                ▲       ▲
       └────────┼────────┼────────────────┼───────┘
                └───────────────────────┘

Todos os caminhos levam a sucesso, mas alguns são mais rápidos
dependendo do seu background inicial.
```

---

## 🎯 Resumo: Sua Próxima Ação

**Dependendo do seu background, comece por:**

- **Python OK, GIS iniciante** → Estude QGIS 3.2.4 semanas
- **GIS OK, Python iniciante** → Estude Python 1-2 semanas
- **Ambos OK, Aero novo** → Estude ICA 11-3 2-3 semanas
- **Iniciante em tudo** → Comece com Python (semanas 1-2)

Depois: **Faça 1 pequeno PR** (bug simples ou documentação) para ganhar confiança.

---

*Documento atualizado: 2 de maio de 2026*  
*Projeto: PBZPA/PBZPH Builder v0.3.1*  
*Versão QGIS mínima: 3.22*
