<!DOCTYPE qgis>
<!--
Estilo categorizado por 'conflito' para a camada OPEA.
  CONFORME    → verde
  LIMITROFE   → amarelo
  VIOLACAO    → vermelho (triângulo invertido, símbolo aeronáutico de obstáculo)
  FORA_PBZPA  → cinza
-->
<qgis version="3.44" styleCategories="Symbology|Labeling">
  <renderer-v2 type="categorizedSymbol" attr="conflito">
    <categories>
      <category symbol="0" value="CONFORME" label="Conforme"/>
      <category symbol="1" value="LIMITROFE" label="Limítrofe"/>
      <category symbol="2" value="VIOLACAO" label="Em violação"/>
      <category symbol="3" value="FORA_PBZPA" label="Fora do PBZPA"/>
    </categories>
    <symbols>
      <symbol name="0" type="marker"><layer class="SimpleMarker"><prop k="name" v="circle"/><prop k="color" v="40,170,80,200"/><prop k="size" v="3"/></layer></symbol>
      <symbol name="1" type="marker"><layer class="SimpleMarker"><prop k="name" v="triangle"/><prop k="color" v="240,210,40,220"/><prop k="size" v="4"/></layer></symbol>
      <symbol name="2" type="marker"><layer class="SimpleMarker"><prop k="name" v="triangle"/><prop k="color" v="220,30,30,240"/><prop k="size" v="5"/><prop k="angle" v="180"/></layer></symbol>
      <symbol name="3" type="marker"><layer class="SimpleMarker"><prop k="name" v="circle"/><prop k="color" v="160,160,160,180"/><prop k="size" v="2.5"/></layer></symbol>
    </symbols>
  </renderer-v2>
  <labeling type="simple">
    <settings fieldName="altura_m">
      <text-style fontSize="8" textColor="0,0,0,255"/>
    </settings>
  </labeling>
</qgis>
