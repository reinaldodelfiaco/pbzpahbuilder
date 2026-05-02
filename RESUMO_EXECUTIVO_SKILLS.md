# Resumo Executivo - Skills PBZPA/PBZPH Builder

## Visão Geral

O **PBZPA/PBZPH Builder** é um plugin QGIS especializado que combina análise geoespacial, processamento de imagens com machine learning, geometria computacional 3D e regulamentações aeronáuticas brasileiras.

Para ser desenvolvedor competente neste projeto, é necessário dominar **7 pilares de conhecimento** que se interconectam de forma complexa.

---

## 🔴 SKILLS CRÍTICOS (Imprescindíveis)

### 1. Python Intermediário-Avançado
- Type hints, dataclasses, enumerações
- Logging, tratamento de exceções
- **Tempo de aprendizado:** 2-4 semanas (se background em programação)

### 2. QGIS & PyQGIS
- Desenvolvimento de plugins (lifecycle, interface gráfica)
- Geometrias vetoriais 3D (PolygonZ, PointZ, LineStringZ)
- Camadas, features, campos, transformações de coordenadas
- **Tempo de aprendizado:** 4-6 semanas (com prática)

### 3. Sistemas de Coordenadas Geoespaciais
- WGS84 (graus decimais), SIRGAS 2000, UTM
- Transformações automáticas entre projeções
- Cálculo de zona UTM a partir de lat/lon
- Elevação e cota AMSL
- **Tempo de aprendizado:** 3-4 semanas

### 4. Regulamentações Aeronáuticas Brasileiras
- ICA 11-3, RBAC 154, Anexo 14 OACI
- Superfícies limitadoras de obstáculos (6 tipos)
- Parâmetros tabulares (code number, code letter, tipo de operação)
- **Tempo de aprendizado:** 4-6 semanas (especializado)

### 5. Geometria Computacional 3D
- Planos horizontais, cônicas, superfícies multi-seção
- Cálculos de distâncias, ângulos, buffers
- Algoritmos de intersecção volumétrica
- **Tempo de aprendizado:** 4-8 semanas

---

## 🟠 SKILLS IMPORTANTES (Altamente Recomendados)

### 6. Visão Computacional & Machine Learning
- ONNX Runtime (inferência)
- YOLOv8 (detecção de objetos)
- Tiling de imagens, reprojeção pixel↔geo
- **Tempo de aprendizado:** 6-8 semanas

### 7. PyQt5 & Interface Gráfica
- Widgets, layouts, dialogs, signals/slots
- Validação de entrada, feedback ao usuário
- Internacionalização (i18n)
- **Tempo de aprendizado:** 3-4 semanas

### 8. Exportação de Dados Cartográficos
- KML/KMZ (Google Earth)
- DXF/DWG (AutoCAD, CAD tools)
- CSV/HTML (dados tabulares)
- **Tempo de aprendizado:** 2-3 semanas

---

## 🟡 SKILLS COMPLEMENTARES (Valorizados)

- Git & GitHub (versionamento, colaboração)
- Sphinx / Markdown (documentação técnica)
- Testes unitários (unittest, pytest)
- Performance e otimização
- AWS/Cloud GIS (opcional, futuro)

---

## 📊 Matriz de Dependência

```
Conhecimentos Aeronáuticos ◄─┐
                             ├─► Geometria Computacional 3D ◄─┐
Sistemas de Coordenadas ─────┤                              ├─► DESENVOLVEDOR
                             └─► Python + QGIS ────────────┤
                                 ▲                           │
                                 │                           │
Visão Computacional ────────────┘    Exportação de Dados ───┘

PyQt5 & UI ◄─── Python + QGIS
```

---

## ⏱️ Cronograma Recomendado de Aprendizado

| Fase | Duração | Foco | Atividades |
|------|---------|------|-----------|
| **Fundação** | Semanas 1-4 | Python, QGIS, Regulamentações | Tutoriais QGIS, leitura ICA 11-3, primeiros plugins |
| **Núcleo** | Semanas 5-8 | Coordenadas, Geometria, Superfícies | Desenvolvimento de superfícies, testes |
| **Integração** | Semanas 9-12 | ML, Exportação, OPEA | Detecção de objetos, exportação KML/DXF |
| **Especialização** | Contínua | Performance, Novas normas | Otimizações, conformidade com atualizações |

---

## 🎯 Recomendações Práticas

### Para Iniciantes em GIS
1. Comece com **Fundamentos QGIS** (interface, camadas, projeções)
2. Aprenda **Python com QGIS** (consola PyQGIS)
3. Depois, estude **Regulamentações Aeronáuticas**
4. Implemente primeiro uma **Superfície Simples** (Horizontal)
5. Progresso gradual para superfícies complexas

### Para Programadores Experientes
1. Foque em **QGIS Python API** (1-2 semanas)
2. Aprenda **Sistemas de Coordenadas** (2-3 semanas)
3. Imprima-se nas **Regulamentações** (3-4 semanas)
4. Implemente **Geometrias 3D** (2-4 semanas)

### Para Engenheiros Aeronáuticos
1. Já conhece as **Regulamentações** ✓
2. Aprenda **Python** (3-4 semanas)
3. Aprenda **QGIS & SIG** (4-6 semanas)
4. Progresso rápido em desenvolvimento

---

## 📚 Recursos de Aprendizado

### Oficial QGIS
- [QGIS Documentation](https://docs.qgis.org/)
- [PyQGIS API](https://qgis.org/pyqgis/)
- Plugin Development Guide

### Regulamentações Brasileiras
- **ICA 11-3** - COMAER (Aeródromos Civis)
- **RBAC 154** - ANAC (Helicópteros)
- **Anexo 14** - OACI (Aeródromos Internacionais)

### Geoespacial
- [PROJ.ORG](https://proj.org/) - Transformações de coordenadas
- [GDAL Documentation](https://gdal.org/) - Formatos geoespaciais
- Cursos online em SIG/GIS

### Visão Computacional
- [ONNX Runtime Docs](https://onnxruntime.ai/)
- [YOLOv8 Documentation](https://docs.ultralytics.com/models/yolov8/)
- OpenCV (processamento de imagens)

---

## 🏆 Competências Transversais Essenciais

1. **Atenção a Detalhes** — Regulamentações precisas, cálculos geométricos
2. **Pensamento Sistemático** — Compreensão de fluxos complexos
3. **Documentação** — Código bem comentado, docstrings
4. **Comunicação Técnica** — Português técnico claro
5. **Aprendizado Contínuo** — Atualizações normativas, novas tecnologias
6. **Resolução de Problemas** — Debug de geometrias, projeções

---

## 📋 Checklist de Competência

- [ ] Entender ICA 11-3 (superfícies, parâmetros)
- [ ] Dominar WGS84, SIRGAS 2000, UTM
- [ ] Desenvolver plugins QGIS funcionais
- [ ] Manipular geometrias 3D em Python
- [ ] Implementar geometria computacional básica
- [ ] Exportar para KML e DXF
- [ ] Usar ONNX Runtime para ML
- [ ] Criar interfaces PyQt5 intuitivas
- [ ] Escrever código testável e documentado
- [ ] Contribuir ao projeto via Git

---

## 🚀 Próximos Passos

1. **Selecionar caminho de aprendizado** (iniciante/experiente)
2. **Instalar QGIS 3.44+** e configurar ambiente de desenvolvimento
3. **Ler documentação** do projeto (README, superficies_limitadoras_obstaculos.md)
4. **Executar exemplos** (sbgl_galeao, sbgr_guarulhos)
5. **Estudar código existente** (modules: core, export, ui)
6. **Implementar primeira feature** sob supervisão
7. **Participar de code reviews** e feedback
