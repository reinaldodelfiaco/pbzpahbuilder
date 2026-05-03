# Captura de Coordenadas com Mira

## Novo recurso adicionado na versão 0.3.2 (em desenvolvimento)

### Descrição

Os campos de coordenadas (latitude e longitude) das cabeceiras agora possuem um ícone de mira (**⊕**) que permite capturar coordenadas diretamente do mapa QGIS.

### Como usar

1. **Abra um mapa no QGIS** com a zona de proteção ou a imagem de satélite que deseja usar como referência.

2. **No diálogo PBZPA/PBZPH**, na aba "1. Aeródromo", localize os campos:
   - Lon A (graus dec.)
   - Lat A (graus dec.)
   - Lon B (graus dec.)
   - Lat B (graus dec.)

3. **Clique no ícone de mira** (⊕) ao lado do campo de coordenada que deseja preencher:
   - O cursor mudará para uma mira
   - O botão da mira ficará destacado em verde

4. **Clique no ponto** no mapa QGIS onde está localizada a cabeceira:
   - A coordenada será capturada automaticamente
   - Se o seu mapa estiver em outro sistema de coordenadas (ex: UTM), a ferramenta converterá automaticamente para WGS84 (graus decimais)
   - O valor será preenchido no campo com 6 casas decimais de precisão (~0.1 m)

5. **Repita para os demais campos** de coordenada (Lon B e Lat B).

### Detalhes técnicos

- **Conversão automática**: Se o projeto QGIS estiver em UTM ou outro CRS, as coordenadas serão automaticamente transformadas para WGS84 (EPSG:4326).
- **Precisão**: As coordenadas são capturadas com 6 casas decimais, oferecendo precisão de aproximadamente 0.1 metro em graus decimais.
- **Formato**: O valor é preenchido no formato decimal com vírgula (ex: -23,192345) para compatibilidade com o padrão brasileiro.
- **Interatividade**: Quando a mira está ativa, o botão fica verde. Após a seleção, volta ao normal.

### Arquivos modificados

- `pbzpa_dialog.py`: Integração dos widgets de coordenada
- `coordinate_widget.py`: Nova classe com widget de coordenada com mira

### Testes recomendados

- Testar com mapas em WGS84
- Testar com mapas em UTM (SIRGAS 2000 - zonas 18-25 brasileiras)
- Validar precisão do ponto capturado comparando com coordenadas conhecidas
