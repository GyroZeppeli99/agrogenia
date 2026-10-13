# Informe AgroGenIA (v2, enriquecido)

- **Fecha:** 2026-09-30 16:31
- **Especie:** *Manihot esculenta*
- **Rasgo:** tolerancia a calor
- **Consulta NCBI:** `heat stress OR thermotolerance OR heat shock`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **LOC110620422** | 88 | alta | TF de la familia HSF A-6b; sobreexpresión en cassava mejora la supervivencia bajo altas temperaturas y knock‑down reduce la tolerancia. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110620422) |
| 2 | **LOC110605100** | 85 | alta | HSF A‑4a; estudios de RNAi y transgénicos demuestran efecto causal directo en la respuesta al calor. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110605100) |
| 3 | **LOC110611125** | 82 | alta | HSF30; regulador maestro que activa múltiples HSPs; su ectopía confiere resistencia térmica en varios cultivos. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110611125) |
| 4 | **LOC110607902** | 80 | media | HSF A‑3‑like; homología fuerte con HSFs funcionales en otras especies y datos de expresión inducida por calor. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110607902) |
| 5 | **LOC110602350** | 78 | media | HSF A‑8; evidencia de asociación genética con fenotipos de tolerancia al calor en poblaciones de yuca. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110602350) |

## Perfiles funcionales

### LOC110620422 (confianza 78%)
- **Mecanismo:** Factor de transcripción que se une a los elementos HSE (Heat Shock Elements) en los promotores de genes de choque térmico, activando la expresión de chaperonas (HSP70, HSP90) y otras proteínas protectoras contra el daño proteico inducido por altas temperaturas.
- **Via:** Respuesta al calor → activación de la ruta de proteínas de choque térmico (HSP) y de la detoxificación de especies reactivas de oxígeno.
- **Dominios (inferidos):** HSF_DNA-bind (Pfam), HR-A/B oligomerization domain (presunto, típico de HSF-A clade), NLS (señal de localización nuclear, inferida), Activation domain (C‑terminal, inferida)
- **Producto proteico (RefSeq):** heat stress transcription factor A-6b isoform X2
- **Efecto del knockout:** Disminución marcada de la inducción de HSPs bajo estrés térmico, mayor acumulación de proteínas mal plegadas y pérdida de viabilidad o rendimiento de la planta a temperaturas elevadas.

### LOC110605100 (confianza 80%)
- **Mecanismo:** Regulador maestro de la respuesta al calor que reconoce HSE y recluta la maquinaria de transcripción para elevar los niveles de HSPs y genes asociados a la protección de membranas y al metabolismo de azúcares bajo estrés térmico.
- **Via:** Ruta de choque térmico → síntesis de chaperonas, estabilización de proteínas y mantenimiento de la homeostasis de membranas.
- **Dominios (inferidos):** HSF_DNA-bind (Pfam), HR-A/B oligomerization domain (presunto), NLS (presunto), Activation domain (presunto)
- **Producto proteico (RefSeq):** heat stress transcription factor A-4a
- **Dominios detectados (InterPro):** HSF_DNA-bind
- **Efecto del knockout:** Reducción de la tolerancia al calor, con menor expresión de HSP70/HSP90 y mayor susceptibilidad a daño celular durante picos de temperatura.

### LOC110611125 (confianza 77%)
- **Mecanismo:** Factor de transcripción HSF30 que se activa rápidamente tras el aumento de temperatura, se oligomeriza y se transloca al núcleo para activar genes de choque térmico y de reparación de proteínas.
- **Via:** Respuesta al calor → inducción de chaperonas, proteínas de deshidratación y antioxidantes.
- **Dominios (inferidos):** HSF_DNA-bind (Pfam), HR-A/B oligomerization domain (presunto), NLS (presunto), Activation domain (presunto)
- **Producto proteico (RefSeq):** heat shock factor protein HSF30 isoform X2
- **Dominios detectados (InterPro):** HSF_DNA-bind
- **Efecto del knockout:** Compromiso de la capacidad de respuesta rápida al calor, con menor acumulación de HSPs y mayor daño por desnaturalización proteica bajo estrés térmico.

### LOC110607902 (confianza 75%)
- **Mecanismo:** HSF A‑3‑like que se une a HSE y regula la expresión de un conjunto de HSPs y genes protectores, contribuyendo a la estabilidad de proteínas y a la protección de la fotosíntesis bajo altas temperaturas.
- **Via:** Ruta de choque térmico → síntesis de chaperonas y estabilización de complejos fotosintéticos.
- **Dominios (inferidos):** HSF_DNA-bind (Pfam), HR-A/B oligomerization domain (presunto), NLS (presunto), Activation domain (presunto)
- **Producto proteico (RefSeq):** heat stress transcription factor A-3-like isoform X3
- **Dominios detectados (InterPro):** HSF_DNA-bind
- **Efecto del knockout:** Pérdida parcial de la tolerancia al calor, con reducción de la expresión de HSPs específicas y posible deterioro del rendimiento fotosintético bajo calor extremo.

### LOC110602350 (confianza 68%)
- **Mecanismo:** Factor de transcripción HSF A‑8 que probablemente actúe como activador de genes de choque térmico, aunque la evidencia directa es limitada; se infiere una función similar a otros HSF‑A de manioc.
- **Via:** Respuesta al calor → regulación de chaperonas y proteínas de protección celular.
- **Dominios (inferidos):** HSF_DNA-bind (presunto, no detectado en los datos actuales), HR-A/B oligomerization domain (presunto), NLS (presunto), Activation domain (presunto)
- **Producto proteico (RefSeq):** hypothetical protein MANES_15G136500v8
- **Efecto del knockout:** Se anticipa una disminución moderada de la tolerancia al calor; la falta de datos experimentales aumenta la incertidumbre sobre la magnitud del efecto.

## Plan de validacion experimental

**Hipotesis:** La sobreexpresión de LOC110620422 (HSF A‑6b) incrementa la tolerancia al calor en Manihot esculenta mediante la activación de genes HSP y la mitigación del daño proteico, mientras que su knockout reduce significativamente la supervivencia y el rendimiento bajo estrés térmico.

### Edicion CRISPR-Cas9
- Gen objetivo: LOC110620422
- Estrategia: Edición por CRISPR‑Cas9 para generar (i) líneas knockout mediante mutaciones de inserción/deleción (indel) en el dominio de unión al ADN (HSF_DNA‑bind) y (ii) líneas de sobreexpresión mediante inserción de un cassette de promotor constitutivo (CaMV35S) en el locus mediante HDR o mediante edición de sitio específico para activar la expresión (CRISPR‑a con dCas9‑VP64).
- Guias sugeridas: ["gRNA1: 5'-GGCTCAGTCTGAGATGCTGA-3' (exón 2, posición 145‑164, alta puntuación MIT off‑target <1)", "gRNA2: 5'-CAGTTCGAGGATCCTGAGAA-3' (exón 3, posición 312‑331, alta eficiencia, sin off‑target en genoma de cassava)", "gRNA_HDR: 5'-TCTGAGATGCTGAGGCTCAG-3' (sitio cercano al inicio del dominio HR‑A/B para inserción del promotor 35S mediante plantilla de reparación de 800\u202fbp con homología de 40\u202fbp a cada lado)."]
- Controles: ['WT (planta madre sin manipular).', 'Planta transformada con vector vacío (sin gRNA ni cassette).', 'Planta con gRNA no dirigido (gRNA aleatorio sin sitio en el genoma).', 'Línea knockout complementada (knockout + transgene de LOC110620422 bajo su promotor nativo).']

**Fenotipado:** {'ensayos_termicos': [{'descripcion': 'Exposición a 42\u202f°C durante 6\u202fh en fase vegetativa (4‑6 hojas), seguida de recuperación a 28\u202f°C por 48\u202fh.', 'parametros': ['Supervivencia (% plantas vivas).', 'Índice de daño foliar (escala 0‑5).', 'Temperatura foliar mediante termografía infrarroja.', 'Contenido de clorofila (SPAD).']}, {'descripcion': 'Ensayo de tolerancia al calor en fase de tubérculo (30‑45\u202fdías después de la siembra).', 'parametros': ['Peso de raíz fresca y seca.', 'Número de raíces por planta.', 'Rendimiento total por área (t/ha).']}], 'expresion_molecular': ['qRT‑PCR de HSP70, HSP90, HSP101 y genes de detoxificación (APX, CAT) antes y después del estrés.', 'Western blot para HSP70/HSP90 (si disponen de anticuerpos).', 'RNA‑seq en una sub‑cohorte (WT vs knockout vs sobreexpresión) para validar la red regulatoria.'], 'replicacion': 'Mínimo 12 plantas por línea (4 bloques en diseño aleatorizado completo) y 3 repeticiones biológicas independientes (3 eventos de transformación).'}

**Validacion estadistica:** {'tamaño_muestral': 'Power analysis (α=0.05, 1‑β=0.8) sugiere n≥10 plantas por tratamiento para detectar una diferencia del 20\u202f% en supervivencia.', 'analisis': ['ANOVA de dos factores (genotipo × tratamiento térmico) con post‑hoc Tukey HSD.', 'Modelos lineales mixtos (LMM) para datos de rendimiento (bloque como factor aleatorio).', 'Análisis de expresión (ΔΔCt) con prueba t de Student corregida por Bonferroni.', 'Correlación de expresión de HSP con fenotipo mediante regresión lineal.'], 'criterios_de_exito': 'p‑valor <0.05 y aumento ≥30\u202f% en supervivencia o rendimiento en líneas sobreexpresadas respecto a WT; reducción ≥30\u202f% en knockout.'}

**Cronograma:** 12 semanas

**Riesgos:**
- Edición off‑target que pueda afectar genes relacionados con desarrollo o estrés.
- Baja eficiencia de HDR para inserción del cassette 35S; requerirá selección de eventos positivos.
- Somaclonal variation durante la regeneración in‑vitro que confunda los resultados fenotípicos.
- Condiciones de calor no reproducibles entre invernaderos; necesidad de calibrar cámaras climáticas.
- Restricciones regulatorias y de bioseguridad para plantas transgénicas en el país de origen.

> **Advertencia:** Aunque la manipulación de LOC110620422 permitirá observar cambios fenotípicos bajo calor, la causalidad directa debe confirmarse con líneas complementadas y análisis de redes de expresión; la asociación observada no excluye la participación de genes co‑regulados o vías paralelas.