# examples/

Casos de uso de referência para testar o plugin PBZPA/PBZPH.

Cada subpasta contém um arquivo `runway.json` com os dados de entrada
(designativo OACI, cabeceiras, code number/letter, tipo de operação)
e, quando disponível, um KML/DXF de saída esperada para validação.

| Caso | OACI | Descrição | Code |
|:-:|:-:|:--|:-:|
| `sbgr_guarulhos/` | SBGR | Aeroporto Internacional de Guarulhos (pista 09L/27R) | 4E (precisão CAT II) |
| `sbgl_galeao/`    | SBGL | Aeroporto Internacional do Galeão (pista 15/33)      | 4E (precisão CAT I) |
| `sbsj_sao_jose/`  | SBSJ | Aeroporto de São José dos Campos                     | 3D (não-precisão)   |
| `heli_demo/`      | —    | Heliponto demonstrativo (PBZPH)                       | —                   |

> Como rodar um caso:
> 1. Carregue o `runway.json` no diálogo do plugin (em desenvolvimento)
>    ou via Processing Toolbox: *PBZPA/PBZPH → Gerar Superfícies PBZPA*.
> 2. Compare as superfícies geradas com as imagens/KML de referência.
