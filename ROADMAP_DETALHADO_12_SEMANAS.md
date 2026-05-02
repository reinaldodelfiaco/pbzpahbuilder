# Roadmap de Desenvolvimento de Competências
## PBZPA/PBZPH Builder - Plano de 12 Semanas

---

## FASE 1: FUNDAÇÕES (Semanas 1-4)

### Sprint 1.1: Regulamentações Aeronáuticas (Semanas 1-2)

**Objetivo:** Compreender o contexto regulatório brasileiro para proteção de espaço aéreo

**Deliverables:**
- [ ] Leitura completa da ICA 11-3 (seções relevantes)
- [ ] Resumo das 6 superfícies limitadoras de obstáculos
- [ ] Tabelas de parâmetros: code number (1-4) e code letter (A-F)
- [ ] Mapeamento: tipos de operação → parâmetros

**Atividades:**
```python
# Exemplo: Implementar enumerações de classificação
from enum import Enum

class CodeNumber(Enum):
    CODE_1 = (1, "< 800 m")
    CODE_2 = (2, "800-1200 m")
    CODE_3 = (3, "1200-1800 m")
    CODE_4 = (4, ">= 1800 m")

class ApproachType(Enum):
    VISUAL = "visual"
    NON_PRECISION = "non_precision"
    PRECISION_CAT_I = "precision_cat_i"
```

**Recursos:**
- ICA 11-3 (COMAER)
- RBAC 154 (ANAC)
- Anexo 14 OACI
- Arquivo: `docs/superficies_limitadoras_obstaculos.md` (já no projeto)

---

### Sprint 1.2: Python Avançado (Semanas 2-3)

**Objetivo:** Dominar padrões Python usados no projeto

**Deliverables:**
- [ ] Type hints completos em novo arquivo
- [ ] Dataclasses congeladas (frozen=True)
- [ ] Enumerações (Enum)
- [ ] Logging configurado
- [ ] Tratamento de exceções customizadas

**Código de Exemplo:**
```python
from dataclasses import dataclass
from enum import Enum
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

class RunwayType(str, Enum):
    NON_INSTRUMENT = "non_instrument"
    INSTRUMENT = "instrument"

@dataclass(frozen=True)
class Threshold:
    """Cabeceira de pista (imutável)."""
    designator: str            # Ex.: "09L"
    longitude: float           # Graus decimais
    latitude: float            # Graus decimais
    elevation_m: float         # Metros AMSL
    
    def __post_init__(self):
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Longitude inválida: {self.longitude}")
```

**Atividades:**
- [ ] Refatorar classe `Runway` com type hints completos
- [ ] Criar testes unitários para validações
- [ ] Documentar com docstrings (PEP 257)

---

### Sprint 1.3: QGIS & Sistemas de Coordenadas (Semanas 3-4)

**Objetivo:** Compreender SRC, transformações e operações QGIS básicas

**Deliverables:**
- [ ] Projeto QGIS com 3 camadas de exemplo
- [ ] Script que reprojeita WGS84 → UTM
- [ ] Cálculo automático de zona UTM
- [ ] Transformação de coordenadas via QGIS

**Código de Exemplo:**
```python
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsPointXY,
    QgsProject
)

# WGS84 (lat/lon)
crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")

# SIRGAS 2000 UTM zona 23S (exemplo: São Paulo)
crs_utm23s = QgsCoordinateReferenceSystem("EPSG:31983")

# Transformação
pt_wgs84 = QgsPointXY(-46.5, -23.5)  # Lon, Lat (São Paulo)
transform = QgsCoordinateTransform(crs_wgs84, crs_utm23s, QgsProject.instance())
pt_utm = transform.transform(pt_wgs84)
print(f"UTM: {pt_utm.x()}, {pt_utm.y()}")
```

**Atividades:**
- [ ] Estudar módulo `utm_utils.py` do projeto
- [ ] Calcular zona UTM para 5 aeródromos brasileiros
- [ ] Implementar função: `calcular_epsg_utm(lat, lon) → epsg_code`
- [ ] Testar transformações com dados reais

---

## FASE 2: NÚCLEO TÉCNICO (Semanas 5-8)

### Sprint 2.1: QGIS Plugin Architecture (Semana 5)

**Objetivo:** Dominar ciclo de vida e estrutura de plugins QGIS

**Deliverables:**
- [ ] Plugin "Hello World" funcionando em QGIS
- [ ] Menu, ícone e atalho configurados
- [ ] Dialog com campos de entrada
- [ ] Processing Provider básico

**Estrutura Base:**
```python
# pbzpa_plugin.py
class PBZPAPlugin:
    def __init__(self, iface):
        self.iface = iface
        self._dialog = None
    
    def initGui(self):
        """Cria menu e toolbar."""
        action = QAction("Gerar PBZPA", self.iface.mainWindow())
        action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&PBZPA", action)
    
    def run(self):
        """Abre o diálogo principal."""
        if not self._dialog:
            from .pbzpa_dialog import PBZPADialog
            self._dialog = PBZPADialog(self.iface)
        self._dialog.show()
    
    def unload(self):
        """Limpa ao descarregar."""
        pass
```

**Atividades:**
- [ ] Criar novo plugin do zero
- [ ] Registrar em metadata.txt
- [ ] Testar em QGIS 3.44+
- [ ] Adicionar logging

---

### Sprint 2.2: Geometria Computacional - Superfícies (Semanas 5-6)

**Objetivo:** Implementar cálculo das 6 superfícies limitadoras

**Deliverables:**
- [ ] Superfície Horizontal Interna (círculo)
- [ ] Superfície Cônica (cone)
- [ ] Superfície de Aproximação (multi-seção, complexa)
- [ ] Superfície de Transição
- [ ] Superfície de Decolagem
- [ ] Faixa de Pista

**Exemplo: Horizontal Interna**
```python
def gerar_horizontal_interna(
    threshold_a: Threshold,
    threshold_b: Threshold,
    raio_m: float,
    altura_m: float,
    crs_utm: QgsCoordinateReferenceSystem
) -> QgsGeometry:
    """
    Superfície Horizontal Interna: união de dois semicírculos
    conectados por tangentes.
    """
    # 1. Converter threshold para UTM
    # 2. Calcular centros e raio em metros
    # 3. Gerar 2 semicírculos + conectivos
    # 4. Criar PolygonZ com altura constante
    # 5. Retornar QgsGeometry 3D
    pass
```

**Atividades:**
- [ ] Estudar `core/surfaces.py` completamente
- [ ] Implementar cada superfície iterativamente
- [ ] Testar com dados de exemplo (sbgl_galeao, sbgr)
- [ ] Validar contra figuras da ICA 11-3

---

### Sprint 2.3: Análise de Conflito OPEA (Semana 7)

**Objetivo:** Implementar detecção de conflitos entre objetos e superfícies

**Deliverables:**
- [ ] Importação de camada OPEA (pontos/polígonos)
- [ ] Cálculo de altura de topo (cota_base + altura)
- [ ] Comparação: topo OPEA vs altura da superfície no ponto
- [ ] Relatório de conflitos

**Código:**
```python
def analisar_conflito(
    opea_features: List[QgsFeature],
    surface_layer: QgsVectorLayer,
    elevacao_base_m: float
) -> List[ConflictReport]:
    """
    Para cada OPEA:
    1. Extrair posição (X, Y) e altura
    2. Calcular Z da superfície no ponto (interpolação)
    3. Comparar cota_topo_opea vs altura_superficie
    4. Registrar conflito se topo > superfície
    """
    conflitos = []
    for opea in opea_features:
        altura_topo = opea['cota_base_m'] + opea['altura_m']
        altura_superficie = interpolar_superficie(opea.geometry())
        
        if altura_topo > altura_superficie:
            conflitos.append(ConflictReport(
                opea_id=opea['id'],
                altura_excesso_m=altura_topo - altura_superficie
            ))
    return conflitos
```

**Atividades:**
- [ ] Estudar `core/conflict_analysis.py`
- [ ] Implementar interpolação 3D
- [ ] Testar com dados reais
- [ ] Gerar relatório visual

---

### Sprint 2.4: Exportação de Dados (Semana 8)

**Objetivo:** Dominar exportação para KML e DXF

**Deliverables:**
- [ ] Exportação KML com altitudeMode=absolute
- [ ] Exportação DXF em 3D
- [ ] Conversão DXF → DWG via ODA
- [ ] Validação de outputs

**Código:**
```python
from qgis.core import QgsVectorFileWriter, QgsCoordinateReferenceSystem

def exportar_para_kml(layers, output_path):
    crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "LIBKML"
    options.destCRS = crs_wgs84
    options.layerOptions = ["ALTITUDE_MODE=absolute"]
    
    for layer in layers:
        result = QgsVectorFileWriter.writeAsVectorFormatV3(
            layer, f"{output_path}_{layer.name()}.kml", 
            QgsCoordinateTransformContext(), options
        )
        if result[0] != QgsVectorFileWriter.NoError:
            raise RuntimeError(f"Erro: {result[1]}")
```

**Atividades:**
- [ ] Estudar `export/kml_exporter.py` e `dxf_exporter.py`
- [ ] Testar KML em Google Earth
- [ ] Testar DXF em AutoCAD
- [ ] Documentar parâmetros

---

## FASE 3: INTEGRAÇÃO (Semanas 9-12)

### Sprint 3.1: Visão Computacional & Machine Learning (Semanas 9-10)

**Objetivo:** Integrar detecção automática de OPEA com ML

**Deliverables:**
- [ ] Download/instalação de YOLOv8n (ONNX)
- [ ] Carregamento e inferência do modelo
- [ ] Reprojeção de bounding boxes (pixel → geo)
- [ ] Camada OPEA sugerida

**Código:**
```python
import onnxruntime as ort
import numpy as np

class OPEADetector:
    def __init__(self, model_path: str):
        """Carrega modelo YOLOv8n em ONNX."""
        self.session = ort.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
    
    def detectar_obstaculos(self, image_path: str) -> List[BoundingBox]:
        """
        1. Carregar imagem GeoTIFF
        2. Dividir em tiles (1024x1024)
        3. Inferência em cada tile
        4. Agregar resultados
        5. Reprojetar para coordenadas geoespaciais
        """
        pass
```

**Atividades:**
- [ ] Estudar `core/opea_detection.py`
- [ ] Testar com imagem de exemplo
- [ ] Implementar tiling e reprojeção
- [ ] Comparar detecções automáticas vs manuais

---

### Sprint 3.2: Interface Gráfica Completa (Semana 11)

**Objetivo:** Implementar diálogo de entrada e configuração

**Deliverables:**
- [ ] Dialog com abas: Tipo, Pista, SSPV, SYSAGA
- [ ] Validação de campos (lat/lon, elevação, etc.)
- [ ] Feedback ao usuário (barra de progresso)
- [ ] Internacionalização (português/inglês)

**Estrutura Base (Qt Designer):**
```xml
<!-- pbzpa_dialog.ui -->
<ui version="4.0">
  <class>PBZPADialog</class>
  <widget class="QDialog">
    <layout class="QVBoxLayout">
      <widget class="QTabWidget">
        <widget class="QWidget"> <!-- Tab: Tipo -->
          <layout>
            <widget class="QComboBox" name="cbProjectType">
              <item>Aeródromo (PBZPA)</item>
              <item>Heliponto (PBZPH)</item>
            </widget>
          </layout>
        </widget>
        <widget class="QWidget"> <!-- Tab: Pista -->
          ...
        </widget>
      </widget>
      <widget class="QPushButton" name="btnGenerate">Gerar</widget>
    </layout>
  </widget>
</ui>
```

**Atividades:**
- [ ] Replicar layout do projeto atual
- [ ] Implementar validações
- [ ] Testar em QGIS
- [ ] Adicionar i18n

---

### Sprint 3.3: Integração SYSAGA & Documentação (Semana 12)

**Objetivo:** Finalizar e documentar

**Deliverables:**
- [ ] Exportação de ficha informativa (HTML)
- [ ] Exportação de planilha de elevações (CSV)
- [ ] Documentação técnica completa
- [ ] Testes automatizados

**Atividades:**
- [ ] Estudar `export/sysaga_exporter.py`
- [ ] Implementar geradores HTML/CSV
- [ ] Escrever docstrings em todas as funções
- [ ] Criar testes unitários (unittest)
- [ ] Code review e cleanup

---

## RECURSOS POR SPRINT

### Sprint 1.1 (Regulamentações)
- Documentos: ICA 11-3, RBAC 154, Anexo 14
- Projeto: `docs/superficies_limitadoras_obstaculos.md`

### Sprint 1.2 (Python)
- Recursos: PEP 257 (docstrings), PEP 484 (type hints)
- Tutoriais: Real Python (dataclasses, enums)

### Sprint 1.3 (SIG)
- Código: `pbzpa_qgis/core/utm_utils.py`
- QGIS: [PyQGIS API](https://qgis.org/pyqgis/)

### Sprint 2.1 (QGIS Plugins)
- Documentação: [QGIS Plugin Development](https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/)
- Exemplo: Projeto atual

### Sprint 2.2 (Superfícies)
- Código: `pbzpa_qgis/core/surfaces.py`, `runway.py`
- Referência: `docs/superficies_limitadoras_obstaculos.md`

### Sprint 2.3 (Conflito)
- Código: `pbzpa_qgis/core/conflict_analysis.py`

### Sprint 2.4 (Exportação)
- Código: `pbzpa_qgis/export/kml_exporter.py`, `dxf_exporter.py`
- Docs: GDAL/OGR, ezdxf

### Sprint 3.1 (ML)
- Código: `pbzpa_qgis/core/opea_detection.py`
- Docs: [ONNX Runtime](https://onnxruntime.ai/), [YOLOv8](https://docs.ultralytics.com/)

### Sprint 3.2 (UI)
- Código: `pbzpa_qgis/ui/pbzpa_dialog.py`, `pbzpa_dialog.ui`
- Docs: PyQt5, Qt Designer

### Sprint 3.3 (Integração)
- Código: `pbzpa_qgis/export/sysaga_exporter.py`
- Testes: `pbzpa_qgis/tests/`

---

## MÉTRICAS DE PROGRESSO

| Semana | Milestone | Critério de Aceite |
|--------|-----------|-------------------|
| 2 | Regulamentações OK | Resumo das 6 superfícies + tabelas |
| 4 | Python + SIG OK | Plugin "Hello World" + transformação UTM funcional |
| 6 | Superfícies OK | Todas as 6 superfícies gerando geometrias válidas |
| 8 | Exportação OK | KML/DXF testados em ferramentas externas |
| 10 | ML OK | Detecção de OPEA com confiança > 75% |
| 12 | Pronto para Produção | Testes passando, documentação completa, code review positivo |

---

## DESAFIOS ESPERADOS & MITIGATION

| Desafio | Causa | Solução |
|---------|-------|---------|
| Complexidade de superfícies | Matemática 3D intrincada | Começar por superfícies simples, incremental |
| Regulamentações obscuras | Documentos técnicos densos | Estudar exemplos do projeto, consultar especialistas |
| Performance com imagens grandes | Tiling e ML custosos | Otimizar ao final, não prematuramente |
| Dependências QGIS específicas | Versão Python/GDAL | Testar em QGIS 3.44+ desde o início |
| Internacionalização | i18n complexa | Usar template Qt Linguist do projeto |

---

## CHECKLIST FINAL (Semana 12)

- [ ] Todos os 9 sprints completados
- [ ] Código testado (unittest coverage > 70%)
- [ ] Documentação atualizada (docstrings + README)
- [ ] Code review aprovado
- [ ] Plugin instalado e testado em QGIS
- [ ] Exemplos replicados com sucesso
- [ ] Contribuição ao repositório via Git
