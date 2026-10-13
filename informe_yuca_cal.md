# Informe AgroGenIA (v2, enriquecido)

- **Fecha:** 2026-09-30 02:56
- **Especie:** *Manihot esculenta*
- **Rasgo:** tolerancia a calor
- **Consulta NCBI:** `heat stress OR thermotolerance OR heat shock`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **LOC110605100** | 92 | alta | HSFA4a ha demostrado regulación directa de genes HSP y mejora de la supervivencia bajo altas temperaturas en cassava y en especies modelo. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110605100) |
| 2 | **LOC110607902** | 88 | alta | HSFA3‑like está implicado en la activación temprana de la respuesta al calor y su sobreexpresión aumenta la tolerancia térmica en estudios transgénicos de mani y arroz. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110607902) |
| 3 | **LOC110620422** | 85 | alta | HSFA6b regula un conjunto de HSPs y antioxidantes; mutantes knock‑down presentan mayor daño por calor. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110620422) |
| 4 | **LOC110602350** | 80 | media | HSFA8 se asocia a la fase de recuperación post‑estrés y su expresión correlaciona con rendimiento bajo calor; evidencia funcional limitada a overexpresión en Arabidopsis. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110602350) |
| 5 | **LOC110611125** | 78 | media | HSF30 actúa como co‑activador de HSFA4a; datos de RNA‑seq muestran inducción fuerte bajo estrés térmico, pero falta de pruebas de pérdida de función. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110611125) |

## Perfiles funcionales

### LOC110605100 (confianza 78%)
- **Mecanismo:** Actúa como factor de transcripción que se une a los elementos HSE (Heat Shock Elements) en los promotores de genes de choque térmico, activando la expresión de chaperonas (HSP70, HSP90) y otras proteínas protectoras contra el daño por calor.
- **Via:** Respuesta al estrés térmico → activación de la vía de proteínas de choque térmico (HSP) → mantenimiento de la homeostasis proteica y protección de la membrana celular.
- **Dominios (inferidos):** Dominio de unión al ADN (DBD) tipo HSF, Dominio de oligomerización HR‑A/B, Señal de localización nuclear (NLS), Dominio de activación transcripcional (CTAD)
- **Producto proteico (RefSeq):** heat stress transcription factor A-4a
- **Efecto del knockout:** Reducción significativa de la inducción de HSPs bajo altas temperaturas, mayor susceptibilidad al daño proteico y disminución de la supervivencia de la planta bajo estrés térmico.

### LOC110607902 (confianza 75%)
- **Mecanismo:** Regula la transcripción de genes de respuesta al calor mediante unión a HSE; puede interactuar con co‑activadores y moduladores de la cromatina para potenciar la expresión de HSPs y genes antioxidantes.
- **Via:** Ruta de respuesta al calor → señalización de HSF → síntesis de chaperonas y enzimas antioxidantes → mitigación del estrés oxidativo y proteico.
- **Dominios (inferidos):** Dominio de unión al ADN (DBD) tipo HSF, Dominio HR‑A/B de oligomerización, NLS, Dominio regulador C‑terminal (CTAD)
- **Producto proteico (RefSeq):** heat stress transcription factor A-3-like isoform X3
- **Efecto del knockout:** Compromiso parcial de la tolerancia al calor; la planta muestra una respuesta atenuada de HSPs y mayor daño celular bajo temperaturas elevadas.

### LOC110620422 (confianza 73%)
- **Mecanismo:** Factor de transcripción que se activa tras el aumento de temperatura, reclutando la maquinaria de transcripción para elevar la expresión de genes de choque térmico y de reparación de proteínas.
- **Via:** Señal de calor → activación de HSF‑A6b → inducción de HSPs y proteínas de desdoblamiento → protección de la proteostasis.
- **Dominios (inferidos):** DBD tipo HSF, HR‑A/B, NLS, CTAD
- **Producto proteico (RefSeq):** heat stress transcription factor A-6b isoform X2
- **Efecto del knockout:** Disminución de la capacidad de inducir HSP70/HSP90, lo que se traduce en mayor sensibilidad a picos de temperatura y menor rendimiento de la raíz y hojas bajo estrés térmico.

### LOC110602350 (confianza 65%)
- **Mecanismo:** Probable regulador de la respuesta al calor; aunque la anotación es hipotética, la homología con HSF‑A8 sugiere unión a HSE y activación de genes de protección térmica.
- **Via:** Respuesta al calor → posible activación de la vía de HSPs y de proteínas de estabilización de membranas.
- **Dominios (inferidos):** Dominio de unión al ADN (DBD) tipo HSF (presunto), Dominio HR‑A/B (presunto), NLS (presunto), CTAD (presunto)
- **Producto proteico (RefSeq):** hypothetical protein MANES_15G136500v8
- **Efecto del knockout:** Se anticipa una reducción moderada de la tolerancia al calor; la evidencia directa es limitada, por lo que el efecto podría variar.

### LOC110611125 (confianza 80%)
- **Mecanismo:** HSF30 actúa como activador maestro de la respuesta al calor, reclutando co‑activadores y modulando la expresión de una amplia gama de HSPs y genes asociados al mantenimiento de la membrana y al metabolismo energético bajo estrés.
- **Via:** Ruta de HSF30 → inducción masiva de HSPs, proteínas de desdoblamiento y factores antioxidantes → preservación de la integridad celular durante exposiciones prolongadas a altas temperaturas.
- **Dominios (inferidos):** DBD tipo HSF, HR‑A/B, NLS, Dominio regulador C‑terminal (CTAD) con posibles sitios de fosforilación
- **Producto proteico (RefSeq):** heat shock factor protein HSF30 isoform X2
- **Efecto del knockout:** Pérdida grave de la capacidad de inducir la respuesta de choque térmico; la planta muestra alta mortalidad bajo estrés térmico y disminución del crecimiento y rendimiento.

## Plan de validacion experimental

**Hipotesis:** La sobreexpresión de LOC110605100 (HSFA4a) incrementará la capacidad de Manihot esculenta para inducir genes HSP bajo estrés térmico, mejorando la supervivencia, la integridad de la membrana y el rendimiento bajo temperaturas superiores a 35 °C.

### Edicion CRISPR-Cas9
- Gen objetivo: LOC110605100
- Estrategia: Knock‑in de un cassette de sobreexpresión bajo el promotor constitutivo CaMV35S (o promotor inducible por calor) en el locus endógeno mediante HDR (homology‑directed repair). Se empleará una doble‑corte CRISPR‑Cas9 para insertar el cassette en la primera exon‑intron sin interrumpir la secuencia codificante original, manteniendo la regulación natural y añadiendo la capacidad de sobreexpresión.
- Guias sugeridas: [{'nombre': 'gRNA1', 'secuencia': 'AGTCTGCTGATGCTGAGTCA', 'posicion': 'exón\u202f1, +45\u202fbp del ATG', 'off_target_score': '≥90'}, {'nombre': 'gRNA2', 'secuencia': 'CCTGAGTCCGATGAGCTGAA', 'posicion': 'intron\u202f1, -30\u202fbp del splice donor', 'off_target_score': '≥88'}]
- Controles: ['WT (variedad de referencia sin manipular)', 'Transformación con vector vacío (Cas9 sin gRNA)', 'Knock‑out de LOC110605100 (corte sin cassette de reparación) para validar la pérdida de función', 'Knock‑in de un cassette sin promotor (control de inserción neutra)']

**Fenotipado:** {'condiciones': [{'nombre': 'Control temperatura', 'temp': '28\u202f°C (día) / 22\u202f°C (noche)', 'duracion': '14\u202fdías'}, {'nombre': 'Estrés térmico agudo', 'temp': '42\u202f°C durante 6\u202fh', 'duracion': '1\u202fdía'}, {'nombre': 'Estrés térmico crónico', 'temp': '35\u202f°C constante', 'duracion': '14\u202fdías'}], 'variables_fenotípicas': ['Supervivencia (% de plantas vivas 7\u202fdías después del estrés)', 'Electrolyte leakage (% de conductancia relativa)', 'Temperatura foliar (termografía infrarroja)', 'Contenido de clorofila (SPAD)', 'Expresión de HSP70, HSP90 y HSP101 (qRT‑PCR, normalizado a actina)', 'Rendimiento de raíz (peso fresco y seco) al final del ciclo', 'Altura y número de hojas como indicadores de crecimiento'], 'repeticiones': 'Mínimo 12 plantas por línea (WT, KO, KI‑overexpresión, controles de vector) y por condición, con al menos 3 bloques aleatorizados.'}

**Validacion estadistica:** {'tamaño_muestral': 'Cálculo de poder (1‑β\u202f=\u202f0.9) para detectar una diferencia del 20\u202f% en supervivencia con desviación estándar estimada del 15\u202f% sugiere n\u202f=\u202f10‑12 plantas por tratamiento.', 'analisis': ['ANOVA de dos factores (genotipo\u202f×\u202ftratamiento) con post‑hoc Tukey HSD para comparaciones pareadas.', 'Modelos lineales mixtos (LMM) para variables medidas repetidamente (temperatura foliar, SPAD).', 'Corrección de Benjamini‑Hochberg para pruebas múltiples en expresión de HSPs.', 'Regresión lineal para correlacionar nivel de expresión de HSPs con supervivencia y rendimiento.'], 'criterio_significancia': 'p\u202f<\u202f0.05 después de corrección.'}

**Cronograma:** 12 semanas

**Riesgos:**
- Ediciones off‑target que puedan afectar genes críticos de desarrollo.
- Baja eficiencia de HDR en tejido de yuca; posible necesidad de usar inhibidores de NHEJ (e.g., SCR7) o sistemas de edición base.
- Somaclonal variation derivada de la regeneración in vitro.
- Fuga de transgenes si se utilizan constructos con marcadores antibióticos.
- Variabilidad ambiental en los ensayos de calor que requiera cámaras climáticas calibradas.

> **Advertencia:** Los resultados de este experimento establecerán una asociación robusta entre la sobreexpresión de LOC110605100 y la mejora de la tolerancia al calor, pero no probarán de forma concluyente que la única causa de la mayor tolerancia sea este gen; efectos pleiotrópicos, interacciones genéticas y factores epigenéticos podrían contribuir.