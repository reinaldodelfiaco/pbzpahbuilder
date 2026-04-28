<!DOCTYPE qgis>
<!--
Estilo categorizado por 'tipo' para a camada de Superfícies do PBZPA.
Cores em conformidade com convenções aeronáuticas e cartas do EB (T 34-700):
  FAIXA_PISTA          → cinza médio, hachura diagonal 45°
  HORIZONTAL_INTERNA   → ciano translúcido
  CONICA               → verde-mar translúcido
  APROXIMACAO          → azul translúcido
  TRANSICAO            → magenta translúcido
  DECOLAGEM            → amarelo translúcido
-->
<qgis version="3.44" styleCategories="Symbology|Labeling">
  <renderer-v2 type="categorizedSymbol" attr="tipo">
    <categories>
      <category symbol="0" value="FAIXA_PISTA" label="Faixa de pista"/>
      <category symbol="1" value="HORIZONTAL_INTERNA" label="Horizontal Interna"/>
      <category symbol="2" value="CONICA" label="Cônica"/>
      <category symbol="3" value="APROXIMACAO" label="Aproximação"/>
      <category symbol="4" value="TRANSICAO" label="Transição"/>
      <category symbol="5" value="DECOLAGEM" label="Decolagem"/>
    </categories>
    <symbols>
      <symbol name="0" type="fill" alpha="0.4">
        <layer class="SimpleFill"><prop k="color" v="120,120,120,150"/><prop k="outline_color" v="60,60,60,255"/><prop k="outline_width" v="0.5"/></layer>
      </symbol>
      <symbol name="1" type="fill" alpha="0.25">
        <layer class="SimpleFill"><prop k="color" v="0,200,230,80"/><prop k="outline_color" v="0,140,170,255"/><prop k="outline_width" v="0.5"/></layer>
      </symbol>
      <symbol name="2" type="fill" alpha="0.25">
        <layer class="SimpleFill"><prop k="color" v="0,170,90,80"/><prop k="outline_color" v="0,110,60,255"/><prop k="outline_width" v="0.5"/></layer>
      </symbol>
      <symbol name="3" type="fill" alpha="0.30">
        <layer class="SimpleFill"><prop k="color" v="40,80,210,90"/><prop k="outline_color" v="20,40,140,255"/><prop k="outline_width" v="0.5"/></layer>
      </symbol>
      <symbol name="4" type="fill" alpha="0.30">
        <layer class="SimpleFill"><prop k="color" v="190,70,180,90"/><prop k="outline_color" v="120,30,110,255"/><prop k="outline_width" v="0.5"/></layer>
      </symbol>
      <symbol name="5" type="fill" alpha="0.30">
        <layer class="SimpleFill"><prop k="color" v="240,210,40,110"/><prop k="outline_color" v="170,140,0,255"/><prop k="outline_width" v="0.5"/></layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <labeling type="simple">
    <settings fieldName="tipo">
      <text-style fontSize="9" textColor="40,40,40,255"/>
      <placement placement="0"/>
    </settings>
  </labeling>
</qgis>
