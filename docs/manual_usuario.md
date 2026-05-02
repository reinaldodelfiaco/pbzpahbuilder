# Manual do Usuario - PBZPA-QGIS

Versao do manual: **0.3.0**

Este manual orienta a instalacao e o uso do plugin PBZPA-QGIS para gerar superficies de protecao, analisar OPEA e preparar arquivos auxiliares para conferencia no SYSAGA.

## 1. Objetivo do Sistema

O PBZPA-QGIS auxilia na elaboracao de produtos tecnicos relacionados a PBZPA/PBZPH dentro do QGIS. O sistema gera geometrias 3D das superficies limitadoras, permite registrar obstaculos, executa uma analise preliminar de conflito e exporta produtos de apoio.

O sistema nao substitui a conferencia tecnica do responsavel pelo processo. As coordenadas, elevacoes, parametros normativos, enquadramento operacional e produtos finais devem ser revisados antes de protocolo ou envio ao SYSAGA.

## 2. Requisitos

- Windows com QGIS 3.44 ou superior.
- Plugin `pbzpa_qgis` instalado no perfil do QGIS.
- Para exportar DXF: biblioteca `ezdxf` instalada no Python do QGIS.
- Para conversao DWG: ODA File Converter instalado e disponivel no PATH.
- Para deteccao automatica de OPEA: `onnxruntime` e modelo ONNX configurado.

## 3. Instalacao

1. Feche o QGIS.
2. Copie ou vincule a pasta `pbzpa_qgis` para:

   ```cmd
   %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
   ```

3. Exemplo com link simbolico:

   ```cmd
   mklink /D "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\pbzpa_qgis" "C:\Users\Reinaldo\OneDrive\Documentos\GitHub\pbzpahbuilder\pbzpa_qgis"
   ```

4. Abra o QGIS.
5. Va em **Complementos > Gerenciar e Instalar Complementos > Instalados**.
6. Ative **PBZPA/PBZPH**.

## 4. Abrindo o Plugin

No QGIS, acesse o menu **PBZPA/PBZPH** ou clique no icone do plugin na barra de ferramentas.

O dialogo principal possui abas para:

- Aerodromo.
- Imagem & OPEA.
- Analise.
- Exportacao.
- SYSAGA.

## 5. Aba Aerodromo

Nesta aba sao informados o tipo de projeto e os dados geometricos usados para gerar as superficies.

### 5.1 Primeira etapa: tipo de projeto

Antes de preencher os demais campos, selecione:

- **Aerodromo (PBZPA)**;
- **Heliponto (PBZPH)**.

Na versao 0.3.0, o fluxo PBZPA esta operacional. O modo PBZPH foi incluido como primeira classificacao do projeto, mas a geracao do desenho e da ficha de heliponto esta bloqueada ate a conferencia dos campos autenticados do Anexo B do SYSAGA.

Tentativa de acesso realizada em 2 de maio de 2026:

- URL consultada: `https://sysaga.decea.mil.br/sysagaanexob/52307761`;
- resultado: redirecionamento para tela de **Login** do SYSAGA/gov.br;
- consequencia: os campos internos do formulario PBZPH nao puderam ser confirmados sem sessao autenticada.

Essa trava evita gerar ficha informativa ou desenho PBZPH com estrutura presumida.

### 5.2 Campos principais para Aerodromo (PBZPA)

**Designativo OACI**

Informe o codigo do aerodromo, por exemplo `SBSJ`, `SBGR` ou `SBGL`.

**Cabeceira A e Cabeceira B**

Para cada cabeceira, informe:

- designativo, por exemplo `09`, `27`, `15`, `33`;
- longitude em graus decimais;
- latitude em graus decimais;
- elevacao em metros.

Use ponto ou virgula como separador decimal. O sistema converte virgula para ponto internamente.

**Code Number**

Selecione o numero de codigo da pista: `1`, `2`, `3` ou `4`.

**Code Letter**

Selecione a letra de codigo: `A`, `B`, `C`, `D`, `E` ou `F`.

**Tipo de pista**

Selecione:

- `Nao instrumento`;
- `Instrumento`.

**Operacao cabeceira A / B**

Selecione o tipo de operacao para cada cabeceira:

- `Nao opera`;
- `Visual`;
- `Nao precisao`;
- `Precisao CAT I`;
- `Precisao CAT II`;
- `Precisao CAT III`.

Quando `Nao opera` for selecionado para uma cabeceira, o plugin nao gera as superficies de aproximacao e decolagem daquele setor. As superficies comuns da pista, como faixa, transicao, horizontal interna e conica, continuam sendo geradas.

**Largura fisica da pista**

Informe a largura fisica em metros.

**Setor SSPV**

Selecione uma das opcoes:

- `Sem SSPV`;
- `Somente setor da cabeceira A`;
- `Somente setor da cabeceira B`;
- `Ambos os setores`.

Este campo registra o enquadramento para a ficha informativa e conferencia do processo. Ele nao altera, nesta versao, a geometria das superficies.

### 5.3 Gerar superficies

Clique em **Gerar superficies**.

O plugin cria:

- uma camada `PBZPA - Superficies`;
- uma camada `OPEA`, caso ainda nao exista.

As superficies sao geradas em SIRGAS 2000 / UTM, com zona detectada automaticamente a partir do ponto medio da pista.

Se o tipo de projeto selecionado for **Heliponto (PBZPH)**, o plugin exibe aviso e nao gera superficies nesta versao.

## 6. Aba Imagem & OPEA

Esta aba permite selecionar um raster de apoio e preparar a revisao de obstaculos.

### 6.1 Selecionar imagem

Clique no botao `...` e selecione uma imagem raster, como:

- `.tif`;
- `.tiff`;
- `.img`;
- `.vrt`.

### 6.2 Camada OPEA

A camada OPEA deve conter os objetos projetados no espaco aereo. O operador pode inserir ou revisar manualmente os pontos no QGIS.

Quando a deteccao automatica estiver configurada, a funcao de ML pode sugerir candidatos. Mesmo nesse caso, a revisao manual e obrigatoria.

## 7. Aba Analise

Clique em **Rodar analise OPEA x superficies**.

O sistema compara os OPEA com as superficies geradas e atualiza a classificacao na tabela de atributos.

Classificacoes previstas:

- `CONFORME`;
- `LIMITROFE`;
- `VIOLACAO`;
- `FORA_PBZPA`.

Revise os resultados em mapa e na tabela de atributos antes de usar em relatorio tecnico.

## 8. Aba Exportacao

### 8.1 Exportar KML/KMZ

Use **Exportar KML/KMZ** para gerar arquivo visualizavel no Google Earth.

O arquivo inclui as superficies e, se existir, a camada OPEA.

### 8.2 Exportar DXF

Use **Exportar DXF** para gerar arquivo CAD.

O DXF organiza as entidades em layers por tipo de superficie e por classificacao de OPEA.

### 8.3 Converter para DWG

Marque **Converter para DWG (ODA)** caso o ODA File Converter esteja instalado.

Se o conversor nao for encontrado, o plugin informa erro e mantem o DXF gerado.

## 9. Aba SYSAGA

A aba SYSAGA foi criada para apoiar a conferencia dos dados que acompanham o desenho do PBZPA.

### 9.1 Visualizar ficha informativa

Clique em **Visualizar ficha informativa**.

O painel exibe uma ficha em HTML com:

- designativo OACI;
- codigo de referencia;
- tipo de pista;
- largura;
- dados da cabeceira A;
- dados da cabeceira B;
- tipo de operacao por cabeceira;
- setor SSPV;
- elevacao de referencia.

### 9.2 Visualizar planilha de elevacoes

Clique em **Visualizar planilha de elevacoes**.

Antes disso, gere as superficies na aba Aerodromo.

A planilha exibe:

- `id`;
- `tipo`;
- `subtipo`;
- `cota_min_m`;
- `cota_max_m`;
- `gradiente`;
- `origem`.

### 9.3 Exportar ficha e planilha

Clique em **Exportar ficha e planilha** e selecione a pasta de saida.

O plugin gera:

- `<icao>_ficha_informativa.html`;
- `<icao>_planilha_elevacoes.csv`.

O CSV usa ponto e virgula como separador, formato comum para abertura em Excel em configuracoes regionais brasileiras.

## 10. Fluxo Recomendado de Trabalho

1. Conferir dados oficiais do aerodromo.
2. Abrir o QGIS e carregar imagens/camadas de apoio.
3. Abrir o PBZPA-QGIS.
4. Selecionar **Aerodromo (PBZPA)** ou **Heliponto (PBZPH)** como primeira etapa.
5. Para PBZPA, preencher a aba Aerodromo.
6. Marcar corretamente cabeceiras sem operacao, se houver.
7. Definir setor SSPV.
8. Gerar superficies.
9. Revisar geometrias no mapa.
10. Inserir ou revisar OPEA.
11. Rodar analise.
12. Revisar resultados de conflito.
13. Exportar KML/KMZ e DXF.
14. Visualizar ficha e planilha na aba SYSAGA.
15. Exportar ficha informativa e planilha de elevacoes.
16. Conferir todos os produtos antes de envio.

## 11. Cuidados Tecnicos

- Verifique se latitude e longitude estao na ordem correta.
- Use elevacoes em metros.
- Confirme se o datum de origem e compativel com SIRGAS 2000/WGS84.
- Confira o code number e code letter contra a documentacao oficial.
- Nao use a opcao `Nao opera` apenas para esconder uma superficie: use-a somente quando a cabeceira realmente nao for operacional para o caso analisado.
- A selecao SSPV e informativa nesta versao; confira a necessidade de desenho setorial conforme o processo e a norma aplicavel.
- Antes de protocolar, compare os dados exportados com as exigencias vigentes do SYSAGA.

## 12. Solucao de Problemas

**Os combos de operacao aparecem vazios**

Reinstale ou recarregue o plugin. A versao 0.2.0 preenche esses campos automaticamente ao abrir o dialogo.

**Erro ao exportar DXF**

Instale `ezdxf` no Python do QGIS:

```powershell
python -m pip install ezdxf
```

Execute o comando no ambiente Python usado pelo QGIS, preferencialmente pelo OSGeo4W Shell.

**Erro ao converter DWG**

Instale o ODA File Converter e confirme se o executavel esta disponivel no PATH.

**Planilha de elevacoes vazia**

Gere as superficies antes de visualizar ou exportar a planilha.

**O comando python no Windows abre a Microsoft Store ou falha**

Instale o Python global ou desative os aliases de execucao de aplicativo do Windows para `python.exe` e `python3.exe`.

## 13. Produtos e Formatos

| Produto | Formato | Uso |
| --- | --- | --- |
| Superficies PBZPA | Camada QGIS PolygonZ | Analise e visualizacao |
| OPEA | Camada QGIS PointZ | Registro e classificacao de obstaculos |
| Desenho Google Earth | KML/KMZ | Conferencia visual |
| Desenho CAD | DXF/DWG | Compatibilidade com CAD |
| Ficha informativa | HTML | Conferencia e impressao |
| Planilha de elevacoes | CSV | Conferencia tabular |

## 14. Limitacoes da Versao 0.2.0

- A integracao com o SYSAGA nao e automatica; os arquivos gerados sao de apoio a conferencia.
- A pagina autenticada do SYSAGA deve ser conferida manualmente pelo operador.
- O Anexo B do SYSAGA para PBZPH redirecionou para login gov.br quando consultado sem sessao autenticada; por isso, ficha e desenho PBZPH ficam bloqueados nesta versao.
- O setor SSPV e registrado na ficha, mas nao altera automaticamente geometrias nesta versao.
- A deteccao de OPEA por ML depende de modelo e bibliotecas externas.

## 15. Historico de Versoes

### 0.3.0

- Primeira etapa com selecao do tipo de projeto: Aerodromo (PBZPA) ou Heliponto (PBZPH).
- Registro da tentativa de conferencia do Anexo B do SYSAGA.
- Bloqueio conservador da geracao/exportacao PBZPH ate verificacao autenticada dos campos oficiais.

### 0.2.0

- Opcao `Nao opera` por cabeceira.
- Selecao de setor SSPV.
- Aba SYSAGA.
- Visualizacao/exportacao da ficha informativa.
- Visualizacao/exportacao da planilha de elevacoes.
- Correcoes no preenchimento dos combos do dialogo.

### 0.1.0

- Geracao inicial de superficies PBZPA/PBZPH.
- Analise OPEA x superficies.
- Exportacao KML/KMZ e DXF.
