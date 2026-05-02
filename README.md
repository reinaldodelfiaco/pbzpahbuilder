# PBZPA-QGIS

**PBZPA-QGIS** e um complemento para QGIS voltado a geracao de Planos Basicos de Zona de Protecao de Aerodromo (PBZPA) e de Heliponto (PBZPH), com apoio a analise de OPEA, exportacao cartografica e conferencia de anexos usados no SYSAGA.

Versao atual: **0.3.0**

## Principais Recursos

- Geracao parametrica das superficies limitadoras de obstaculos: faixa de pista, horizontal interna, conica, aproximacao, transicao e decolagem.
- Entrada das duas cabeceiras por designativo, latitude, longitude e elevacao.
- Primeira etapa de classificacao do projeto: **Aerodromo (PBZPA)** ou **Heliponto (PBZPH)**.
- Definicao do codigo de referencia da pista, tipo de pista e operacao por cabeceira.
- Opcao **Nao opera** para uma cabeceira. Quando selecionada, o plugin nao gera as superficies de aproximacao e decolagem daquele setor.
- Selecao de SSPV: sem SSPV, somente setor da cabeceira A, somente setor da cabeceira B ou ambos os setores.
- Criacao de camada OPEA para revisao manual e analise de conflito com as superficies.
- Exportacao do desenho para **KML/KMZ** e **DXF**; conversao opcional para DWG via ODA File Converter.
- Aba **SYSAGA** para visualizar e exportar:
  - ficha informativa do aerodromo em HTML;
  - planilha de elevacoes em CSV.
- Reprojecao automatica para SIRGAS 2000 / UTM com base na posicao do aerodromo.

## Novidades da Versao 0.3.0

- Adicionada a etapa inicial **Tipo de projeto**.
- Incluida a opcao **Heliponto (PBZPH)** como modo de projeto.
- Bloqueada a geracao/exportacao PBZPH enquanto os campos autenticados do Anexo B do SYSAGA nao forem conferidos.
- Documentada a limitacao de acesso ao Anexo B, que redireciona para login gov.br.

## Novidades da Versao 0.2.0

- Adicionada a opcao de cabeceira sem operacao.
- Adicionada a selecao de setor SSPV.
- Adicionada a aba SYSAGA.
- Adicionada exportacao da ficha informativa e da planilha de elevacoes.
- Corrigido o preenchimento dos combos de tipo de pista e tipo de operacao.

## Estrutura do Repositorio

```text
pbzpahbuilder/
├── pbzpa_qgis/
│   ├── metadata.txt
│   ├── pbzpa_plugin.py
│   ├── pbzpa_dialog.py
│   ├── core/
│   │   ├── runway.py
│   │   ├── surfaces.py
│   │   ├── utm_utils.py
│   │   ├── opea_detection.py
│   │   └── conflict_analysis.py
│   ├── export/
│   │   ├── kml_exporter.py
│   │   ├── dxf_exporter.py
│   │   └── sysaga_exporter.py
│   ├── ui/
│   │   └── pbzpa_dialog.ui
│   ├── styles/
│   ├── resources/
│   ├── i18n/
│   └── tests/
├── docs/
│   ├── manual_usuario.md
│   └── superficies_limitadoras_obstaculos.md
├── examples/
├── LICENSE
└── README.md
```

## Instalacao em Desenvolvimento

1. Localize a pasta de plugins do QGIS:

   ```cmd
   %APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
   ```

2. Crie um link simbolico ou copie a pasta `pbzpa_qgis/` para a pasta de plugins:

   ```cmd
   mklink /D "%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\pbzpa_qgis" "C:\Users\Reinaldo\OneDrive\Documentos\GitHub\pbzpahbuilder\pbzpa_qgis"
   ```

3. Reinicie o QGIS.
4. Acesse **Complementos > Gerenciar e Instalar Complementos > Instalados**.
5. Ative **PBZPA/PBZPH**.

## Dependencias

- QGIS 3.44 ou superior.
- Python do proprio QGIS.
- Para exportacao DXF:

  ```powershell
  python -m pip install ezdxf
  ```

- Para deteccao automatica de OPEA por modelo:

  ```powershell
  python -m pip install onnxruntime
  ```

O plugin tambem pode ser verificado com Python global para sintaxe, mas a execucao dentro do QGIS depende do ambiente Python embarcado no QGIS.

## Uso Basico

1. Abra o QGIS.
2. Clique no botao ou menu **PBZPA/PBZPH**.
3. Na aba **Aerodromo**, selecione primeiro se o projeto e **Aerodromo (PBZPA)** ou **Heliponto (PBZPH)**.
4. Para PBZPA, preencha os dados das cabeceiras e da pista.
5. Defina a operacao de cada cabeceira. Use **Nao opera** quando uma cabeceira nao deve gerar aproximacao/decolagem.
6. Defina o setor SSPV aplicavel.
7. Clique em **Gerar superficies**.
8. Edite ou alimente a camada OPEA.
9. Rode a analise de conflito.
10. Exporte o desenho em KML/KMZ ou DXF.
11. Na aba **SYSAGA**, visualize e exporte a ficha informativa e a planilha de elevacoes.

O modo **Heliponto (PBZPH)** esta disponivel como primeira classificacao do projeto, mas a geracao do desenho e da ficha PBZPH permanece bloqueada ate a conferencia dos campos oficiais do Anexo B do SYSAGA em ambiente autenticado.

Consulte o manual completo em [docs/manual_usuario.md](docs/manual_usuario.md).

## Saidas Geradas

- Camada `PBZPA - Superficies` em PolygonZ.
- Camada `OPEA` para obstaculos.
- KML/KMZ para visualizacao no Google Earth.
- DXF para CAD.
- HTML da ficha informativa.
- CSV da planilha de elevacoes.

## Referencias Normativas

- ICA 11-3: Plano Basico de Zona de Protecao de Aerodromos.
- ICA 11-408: Plano Basico de Zona de Protecao de Helipontos.
- ICA 63-19: Cartas Aeronauticas.
- RBAC 154: Projeto de Aerodromos.
- RBAC 155: Helipontos.
- T 34-700: Convencoes Cartograficas do Exercito Brasileiro.
- Anexo 14 da OACI: Aerodromes.

## Licenca

Distribuido sob a licenca **GPLv3**. Veja [LICENSE](LICENSE).
