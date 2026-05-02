# Superfícies Limitadoras de Obstáculos — PBZPA

Referências: **ICA 11-3** (COMAER), **RBAC 154** (ANAC) e **Anexo 14** da OACI/ICAO. As tabelas abaixo consolidam os parâmetros oficiais utilizados pelo plugin para a geração paramétrica das superfícies. Os valores devem ser revisados a cada nova edição das normas.

> **Aviso técnico:** os valores expressos seguem o disposto na ICA 11-3 (4ª edição) e no RBAC 154 (Emenda 06). Em caso de conflito normativo, prevalece a edição vigente publicada no Boletim do Comando da Aeronáutica (BCA) e no Diário Oficial da União (DOU). O plugin fornece os parâmetros editáveis para acomodar atualizações.

## 1. Código de referência da pista

O código (number-letter) classifica a pista em função do comprimento básico para aeronave de projeto e da envergadura/distância entre rodas. Os parâmetros das superfícies dependem do *code number* (1-4) e do *code letter* (A-F), além do tipo de operação:

| Code number | Comprimento básico (m) |
|:-:|:-:|
| 1 | < 800 |
| 2 | 800 a < 1200 |
| 3 | 1200 a < 1800 |
| 4 | ≥ 1800 |

| Code letter | Envergadura (m) | Bitola (m) |
|:-:|:-:|:-:|
| A | < 15 | < 4,5 |
| B | 15 a < 24 | 4,5 a < 6 |
| C | 24 a < 36 | 6 a < 9 |
| D | 36 a < 52 | 9 a < 14 |
| E | 52 a < 65 | 9 a < 14 |
| F | 65 a < 80 | 14 a < 16 |

## 2. Superfície Horizontal Interna (Inner Horizontal)

Plano horizontal sobre o aeródromo e seus arredores. Forma: união de dois semicírculos centrados nas cabeceiras, conectados por tangentes (envelope).

| Code number | Altura sobre ARP (m) | Raio (m) |
|:-:|:-:|:-:|
| 1 (não-instr.) | 45 | 2 000 |
| 2 (não-instr.) | 45 | 2 500 |
| 3 (não-instr.) | 45 | 4 000 |
| 4 (não-instr.) | 45 | 4 000 |
| 1-2 (instr. não-precisão) | 45 | 3 500 |
| 3-4 (instr. não-precisão) | 45 | 4 000 |
| 3-4 (precisão CAT I/II/III) | 45 | 4 000 |

## 3. Superfície Cônica

Inclinação ascendente para fora a partir da periferia da Horizontal Interna.

| Code number | Inclinação | Altura (m) |
|:-:|:-:|:-:|
| 1 | 5 % | 35 |
| 2 | 5 % | 55 |
| 3 | 5 % | 75 |
| 4 | 5 % | 100 |

## 4. Superfície de Aproximação

Trapézio (e seções subsequentes) iniciando 60 m antes da cabeceira (faixa de pista). Inclinação medida em plano vertical contendo o eixo da pista.

### Pista de pouso visual

| Code number | Largura interna (m) | Distância da cabeceira (m) | Divergência | 1ª seção: comprimento × inclinação |
|:-:|:-:|:-:|:-:|:-:|
| 1 | 60 | 30 | 10 % | 1 600 m × 5,0 % |
| 2 | 80 | 60 | 10 % | 2 500 m × 4,0 % |
| 3 | 150 | 60 | 10 % | 3 000 m × 3,33 % |
| 4 | 150 | 60 | 10 % | 3 000 m × 2,5 % |

### Pista de aproximação por instrumento de não-precisão

| Code number | Largura interna (m) | Distância da cabeceira (m) | Divergência | 1ª seção | 2ª seção | Seção horizontal |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1, 2 | 150 | 60 | 15 % | 2 500 m × 3,33 % | — | — |
| 3 | 300 | 60 | 15 % | 3 000 m × 2,0 % | 3 600 m × 2,5 % | 8 400 m × 0 % |
| 4 | 300 | 60 | 15 % | 3 000 m × 2,0 % | 3 600 m × 2,5 % | 8 400 m × 0 % |

### Pista de aproximação de precisão CAT I

| Code number | Largura interna (m) | Distância da cabeceira (m) | Divergência | 1ª seção | 2ª seção | Seção horizontal | Comprimento total |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1, 2 | 150 | 60 | 15 % | 3 000 m × 2,5 % | 12 000 m × 3,0 % | — | 15 000 m |
| 3, 4 | 300 | 60 | 15 % | 3 000 m × 2,0 % | 3 600 m × 2,5 % | 8 400 m × 0 % | 15 000 m |

### Pista de aproximação de precisão CAT II/III

Igual à CAT I para o code 3-4 (largura 300 m, mesmas seções).

## 5. Superfície de Transição

Plano com inclinação a partir das laterais da faixa de pista e das laterais da aproximação até interceptar a Horizontal Interna.

| Code number | Inclinação |
|:-:|:-:|
| 1 (não-instr.) | 20 % |
| 2 (não-instr.) | 20 % |
| 3 (não-instr.) | 14,3 % |
| 4 (não-instr.) | 14,3 % |
| 1-2 (instr. não-precisão) | 20 % |
| 3-4 (instr. não-precisão) | 14,3 % |
| 1-2 (precisão) | 20 % |
| 3-4 (precisão) | 14,3 % |

## 6. Superfície de Decolagem (Take-off climb)

Trapézio com origem 60 m após o final da pista declarada (TODA).

| Code number | Largura interna (m) | Distância do final da pista (m) | Divergência | Largura final (m) | Comprimento (m) | Inclinação |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 60 | 30 | 10 % | 380 | 1 600 | 5,0 % |
| 2 | 80 | 60 | 10 % | 580 | 2 500 | 4,0 % |
| 3, 4 | 180 | 60 | 12,5 % | 1 200 (instr.) ou 1 800 (visual) | 15 000 | 2,0 % |

## 7. Faixa de pista

Extensão lateral e longitudinal além da pista física.

| Code number | Extensão além da cabeceira (m) | Largura total (não-instr.) | Largura total (instr.) |
|:-:|:-:|:-:|:-:|
| 1 | 30 ou 60 | 60 m | 150 m |
| 2 | 60 | 80 m | 150 m |
| 3, 4 | 60 | 300 m | 300 m |

## 8. Convenções para o plugin

- Coordenadas das cabeceiras informadas em **lat/long** (WGS84/SIRGAS 2000) e convertidas para **SIRGAS 2000 / UTM** (zona detectada automaticamente).
- Z (altitude) das superfícies é gerado em metros acima do nível do mar a partir da elevação do ARP/cabeceira informada.
- Cada superfície é exportada como `QgsVectorLayer` Polygon Z, com atributo `tipo`, `id`, `cota_min`, `cota_max`, `gradiente`.
- A análise de OPEA percorre cada feição da camada de obstáculos e amostra a altitude da superfície no ponto (interpolação) para classificar conforme/não-conforme/sob estudo.
