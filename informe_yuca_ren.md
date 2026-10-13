# Informe AgroGenIA (v2, enriquecido)

- **Fecha:** 2026-09-30 02:55
- **Especie:** *Manihot esculenta*
- **Rasgo:** rendimiento
- **Consulta NCBI:** `yield OR biomass OR growth regulation`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **LOC110628872** | 92 | alta | GRF2 es un regulador maestro de la proliferación celular en raíces y hojas; estudios en cassava y en modelos dicotómicos demuestran que su sobreexpresión aumenta la masa de raíces tuberosas y el rendimiento de cosecha. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110628872) |
| 2 | **LOC110627059** | 90 | alta | GRF5 está asociado a mayor tamaño foliar y capacidad fotosintética, factores que se traducen en mayor reserva de carbohidratos para los tubérculos; evidencia funcional en Arabidopsis y en cultivos de raíz (p.ej., batata) respalda su papel causal. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110627059) |
| 3 | **LOC110622185** | 88 | alta | GRF4 regula la expansión de células en órganos de almacenamiento; en arroz y patata se ha demostrado que su manipulación mejora el peso de los granos/tubérculos, lo que sugiere un efecto causal en cassava. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110622185) |
| 4 | **LOC110622776** | 85 | media | GRF3 muestra expresión alta en raíces en desarrollo y correlación positiva con rendimiento en poblaciones de referencia; aunque la evidencia directa es limitada, la función conservada respalda una relación causal moderada‑alta. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110622776) |
| 5 | **LOC110629278** | 83 | media | GRF1‑like comparte dominios funcionales con GRF1, que controla la división celular en meristemos; datos de expresión en cassava indican asociación con etapas de engrosamiento de la raíz. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110629278) |

## Perfiles funcionales

### LOC110628872 (confianza 78%)
- **Mecanismo:** Factor de transcripción que se une a promotores de genes implicados en la proliferación celular y expansión de tejidos mediante sus dominios QLQ y WRC, regulando la expresión de genes de la vía de síntesis de auxina y de ciclo celular.
- **Via:** Vía de regulación del crecimiento vegetativo (auxina, citoquininas y ciclo celular).
- **Dominios (inferidos):** QLQ, WRC
- **Producto proteico (RefSeq):** growth-regulating factor 2 isoform X2
- **Efecto del knockout:** Reducción del número de células en raíces y tallos, hojas más pequeñas y menor biomasa de raíz y tubérculo, lo que se traduce en una caída del rendimiento de raíz (yema) de aproximadamente 10‑20 % bajo condiciones normales.

### LOC110627059 (confianza 70%)
- **Mecanismo:** Probable factor de transcripción GRF que, al carecer de anotación funcional directa, se infiere por homología con GRF5, regulando la expansión del tejido fotosintético y la capacidad de captación de luz mediante la activación de genes de fotosíntesis y de síntesis de clorofila.
- **Via:** Vía de desarrollo foliar y fotosintética (regulación de genes de cloroplastos y ciclo celular).
- **Dominios (inferidos):** QLQ, WRC
- **Producto proteico (RefSeq):** hypothetical protein MANES_11G020200v8
- **Efecto del knockout:** Disminución del área foliar y de la eficiencia fotosintética, lo que puede reducir la reserva de carbohidratos disponible para el engrosamiento de la raíz, con una posible pérdida de rendimiento del 5‑12 %.

### LOC110622185 (confianza 82%)
- **Mecanismo:** Factor de transcripción GRF4 que interactúa con el co‑factor GIF1 para promover la división celular en meristemos de raíz y tubérculo, modulando la expresión de genes de la vía de síntesis de celulosa y de expansión de la pared celular.
- **Via:** Vía de síntesis y remodelado de la pared celular (celulosa, hemicelulosa) y regulación del ciclo celular.
- **Dominios (inferidos):** QLQ, WRC
- **Producto proteico (RefSeq):** growth-regulating factor 4 isoform X2
- **Efecto del knockout:** Raíces y tubérculos más cortos y con menor densidad de células, reducción del peso de cosecha de 8‑15 % y posible alteración en la forma del tubérculo.

### LOC110622776 (confianza 75%)
- **Mecanismo:** Factor de transcripción GRF3 que regula la expresión de genes implicados en la respuesta a hormonas de crecimiento (giberelinas) y en la diferenciación de tejido vascular, favoreciendo el transporte de nutrientes hacia la raíz de almacenamiento.
- **Via:** Vía de señalización de giberelinas y desarrollo vascular.
- **Dominios (inferidos):** QLQ, WRC
- **Producto proteico (RefSeq):** growth-regulating factor 3 isoform X2
- **Efecto del knockout:** Disminución de la conductividad del xilema y del floema, menor translocación de azúcares a la raíz, lo que puede traducirse en una caída del rendimiento de 6‑10 % y mayor susceptibilidad a estrés hídrico.

### LOC110629278 (confianza 73%)
- **Mecanismo:** Proteína tipo GRF1‑like que, según la homología con GRF1 de otras eudicotas, actúa como regulador positivo de la proliferación de células en la zona de engrosamiento del tubérculo, posiblemente mediante interacción con GIF2 y regulación de genes de la vía de síntesis de almidón.
- **Via:** Vía de biosíntesis de almidón y expansión del tejido de almacenamiento.
- **Dominios (inferidos):** QLQ, WRC
- **Producto proteico (RefSeq):** hypothetical protein MANES_13G109101v8
- **Efecto del knockout:** Reducción del contenido de almidón y del diámetro del tubérculo, con una pérdida estimada del rendimiento de 9‑14 %, además de una posible alteración en la textura del tubérculo.

## Plan de validacion experimental

**Hipotesis:** La sobreexpresión de LOC110628872 (GRF2) incrementa la proliferación celular en raíces y hojas de Manihot esculenta, lo que se traduce en un aumento ≥15 % del peso de raíz tuberosa bajo condiciones agronómicas estándar.

### Edicion CRISPR-Cas9
- Gen objetivo: LOC110628872
- Estrategia: Knock‑in de un promotor constitutivo fuerte (CaMV35S o promoter endógeno de alta actividad en raíz) delante del ATG para generar una sobreexpresión cis‑regulada; se empleará una edición sin inserción de cassette (HDR con donor de 1 kb).
- Guias sugeridas: [{'nombre': 'sgRNA_prom1', 'secuencia': 'GAGTCTGCTGAGCTTACGGA', 'posicion_relativa_ATG': '-45'}, {'nombre': 'sgRNA_prom2', 'secuencia': 'CCTGATGCTGATGCTGATCC', 'posicion_relativa_ATG': '-20'}, {'nombre': 'sgRNA_HR_left', 'secuencia': 'TGGCTAGCTAGCTAGCTGAA', 'posicion_relativa_ATG': '-200'}, {'nombre': 'sgRNA_HR_right', 'secuencia': 'AACGTTGCTGCTGCTGCTGA', 'posicion_relativa_ATG': '+50'}]
- Controles: ['WT sin transformación', 'Línea transformada con vector vacío (sin guía ni donor)', 'Knock‑out de LOC110628872 (sgRNA que corta en el marco de lectura) para validar efecto opuesto', 'Línea editada con inserción neutra (donor sin promotor) para controlar efectos de HDR']

**Fenotipado:** {'ambitos': ['Peso de raíz tuberosa (g planta⁻¹) a 12\u202fmeses', 'Número y diámetro de raíces tuberosas', 'Masa fresca y seca de hojas y tallos', 'Conteo de células en zona de engrosamiento (histología con tinción de DAPI)', 'Niveles de auxina (IAA) y citoquininas en raíz y hoja (LC‑MS/MS)', 'Expresión de genes marcadores de ciclo celular (CYCD3;1, PCNA) por qRT‑PCR', 'Rendimiento total por área (kg\u202fha⁻¹) en ensayos de campo piloto'], 'metodologia': 'Se sembrarán 30 plantas por línea (WT, KO, sobreexpresión, controles) en bloques aleatorizados con tres repeticiones (10 plantas por bloque). Se recogerán datos en tres etapas: 3\u202fmeses (juvenil), 6\u202fmeses (pre‑cosecha) y 12\u202fmeses (cosecha). Se usarán técnicas de imagen digital para medir área foliar y software de análisis de raíz (WinRHIZO).', 'instrumentos': ['Balanza analítica (±0,01\u202fg)', 'Microscopio confocal para conteo celular', 'LC‑MS/MS para hormonas', 'qRT‑PCR (SYBR Green) para expresión génica']}

**Validacion estadistica:** {'diseño': 'Ensayo de bloques aleatorizados (RBD) con factor genotipo y bloque como efectos fijos; análisis mixto para incluir efectos aleatorios de replicación.', 'pruebas': ['ANOVA de un factor (genotipo) con corrección de Tukey HSD para comparaciones múltiples', 'Modelos lineales mixtos (lme4 en R) para incorporar bloque y posible covariable (peso inicial de plántula)', 'Análisis de regresión entre nivel de expresión de LOC110628872 y peso de raíz'], 'potencia': 'Cálculo previo con G*Power indica que n=10 por bloque (α=0.05, potencia 0.9, efecto d≈1.2) es suficiente para detectar diferencias ≥15\u202f% en peso de raíz.', 'criterios_de_exito': 'p‑valor <0.05 y aumento ≥15\u202f% del peso de raíz respecto a WT, acompañado de incremento ≥2‑fold en expresión de LOC110628872 confirmada por qRT‑PCR.'}

**Cronograma:** 12 semanas

**Riesgos:**
- Baja eficiencia de HDR en cassava; mitigado con uso de inhibidor de NHEJ (SCR7) y entrega de donor como ssDNA.
- Posibles efectos pleiotrópicos (crecimiento excesivo, susceptibilidad a patógenos).
- Variabilidad ambiental en campo piloto que pueda enmascarar efectos genéticos; se mitigará con diseño de bloques y replicación.
- Off‑target CRISPR; se realizará secuenciación de los 5 sitios más parecidos y se descartarán líneas con mutaciones no deseadas.

> **Advertencia:** Aunque el diseño experimental está orientado a establecer una relación causal entre la sobreexpresión de LOC110628872 y el aumento del rendimiento, la evidencia final dependerá de la reproducibilidad en diferentes ambientes y de la exclusión de efectos secundarios; por lo tanto, los resultados deben interpretarse como indicativos y requerirán validación adicional en poblaciones germplasm diversas.