# 🌱 Informe AgroGenIA

- **Fecha:** 2026-09-30 01:34
- **Especie:** *Solanum lycopersicum*
- **Rasgo:** tolerancia a sequía
- **Consulta NCBI:** `drought OR dehydration OR water deficit OR desiccation OR ABA`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **Asr2** | 92 | alta | Sobreexpresión en tomate mejora la retención de agua y la supervivencia bajo sequía; localizado en QTL de tolerancia al estrés hídrico. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/101247518) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/P37219) |
| 2 | **ABF4** | 85 | alta | Factor de transcripción ABA‑responsive con estudios de transgénicos en tomate que aumentan la resistencia a la sequía. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/100820704) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/A0A3Q7IWK8) |
| 3 | **AREB1** | 80 | alta | Regulador de genes ABA‑dependientes; mutantes y líneas sobreexpresadas muestran cambios significativos en la respuesta al déficit hídrico. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/544204) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/A0A3Q7GA77) |
| 4 | **LOC101258493** | 70 | media | Homólogo de LEA14, proteína protectora de desecación; expresión inducida por sequía en varios estudios de transcriptómica de tomate. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/101258493) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/A0A3Q7ID71) |
| 5 | **LOC101258829** | 68 | media | Similar a la proteína desiccation‑related At2g46140; datos de expresión bajo estrés hídrico, pero falta de pruebas funcionales directas en tomate. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/101258829) |

## Perfiles funcionales

### Asr2 (confianza 90%)
- **Mecanismo:** Proteína hidrofílica que se acumula bajo estrés hídrico y se une a ácidos nucleicos, estabilizando ARN y proteínas y modulando la expresión de genes de respuesta al ABA.
- **Vía:** Ruta de señalización del ácido abscísico (ABA) → activación de genes de tolerancia a sequía y maduración de frutos.
- **Dominios:** LEA (Late Embryogenesis Abundant) domain, Zinc‑binding C2H2‑like motif (presente en algunos ASR)
- **Efecto del knockout:** Sensibilidad aumentada a la sequía, reducción de la capacidad de retener agua y menor expresión de genes ABA‑dependientes; posible retraso en la maduración del fruto bajo estrés hídrico.

### ABF4 (confianza 92%)
- **Mecanismo:** Factor de transcripción bZIP que se fosforila en respuesta al ABA y se une al elemento ABRE (ABA‑Responsive Element) en promotores de genes de estrés, activando su transcripción.
- **Vía:** Señalización ABA → activación de la cascada de MAPK y SnRK2 → fosforilación de ABF4 → regulación de genes de osmoprotectores, antioxidantes y proteínas LEA.
- **Dominios:** bZIP DNA‑binding domain, C‑terminal transactivation domain, SnRK2 phosphorylation sites
- **Efecto del knockout:** Disminución significativa de la respuesta transcripcional al ABA, mayor pérdida de turgencia, menor acumulación de osmólitos y mayor daño oxidativo bajo sequía.

### AREB1 (confianza 91%)
- **Mecanismo:** Factor de transcripción bZIP que reconoce el ABRE y, tras fosforilación por SnRK2, recluta co‑activadores para inducir genes de tolerancia al estrés hídrico.
- **Vía:** Ruta ABA → SnRK2 → fosforilación de AREB1 → activación de genes LEA, aquaporinas y enzimas antioxidantes.
- **Dominios:** bZIP DNA‑binding domain, C‑terminal activation domain, SnRK2 phosphorylation motifs
- **Efecto del knockout:** Reducción de la expresión de genes clave para la protección celular bajo sequía, mayor susceptibilidad al estrés hídrico y menor rendimiento bajo condiciones de déficit hídrico.

### LOC101258493 (confianza 75%)
- **Mecanismo:** Proteína protectora de desecación tipo LEA que actúa como chaperona osmótica, evitando la agregación de proteínas y estabilizando membranas durante la pérdida de agua.
- **Vía:** Respuesta de desecación independiente o parcialmente dependiente de ABA → acumulación de proteínas LEA tipo 14 → protección estructural de macromoléculas.
- **Dominios:** LEA group 14 domain (hydrophilic, intrinsically disordered), Motivos de repetición de aminoácidos glicina‑alanina
- **Efecto del knockout:** Aumento de la desnaturalización de proteínas y daño de membranas bajo sequía severa; posible reducción de la germinación y viabilidad de semillas bajo estrés hídrico.

### LOC101258829 (confianza 50%)
- **Mecanismo:** Proteína de origen desconocido con similitud a At2g46140; se hipotetiza que participa en la estabilización de estructuras celulares durante la desecación, aunque la evidencia experimental es escasa.
- **Vía:** Posible participación en la vía de respuesta a desecación/ABA, pero no está confirmada; podría actuar como co‑factor de proteínas LEA o como regulador de la expresión génica.
- **Dominios:** Sin dominios caracterizados en bases de datos públicas (predicción de región intrinsicamente desordenada)
- **Efecto del knockout:** La evidencia es limitada; se anticipa una ligera disminución de la tolerancia a sequía, pero el fenotipo podría ser sutil o compensado por genes paralelos.

## Plan de validación experimental

**Hipótesis:** La sobreexpresión de Asr2 en Solanum lycopersicum incrementa la retención de agua y la supervivencia bajo déficit hídrico mediante la estabilización de ARN/proteínas y la potenciación de la señalización ABA, mientras que la pérdida de función de Asr2 aumenta la sensibilidad a la sequía.

### Edición CRISPR-Cas9
- Gen objetivo: Asr2
- Estrategia: Se generarán dos tipos de líneas editadas: (i) knockout mediante mutagénesis por NHEJ usando Cas9 y guías dirigidas a exón 1 para introducir indeles que provoquen frameshift; (ii) sobreexpresión mediante sustitución del promotor nativo por el promotor constitutivo CaMV35S (o por un promotor inducible por estrés, pRD29A) usando HDR con una plantilla de reparación de doble cadena que incluya el nuevo promotor y una marca de selección (hpt).
- Guías sugeridas: ["gRNA1_Asr2_ex1_F: 5'-GGAGCTGCTGATGCTGATGA-3' (PAM: AGG) – objetivo exon 1, posición +45", "gRNA2_Asr2_ex1_R: 5'-CCTCAGTCTGCTGCTGATCT-3' (PAM: CGG) – objetivo exon 1, posición +78", "gRNA_prom_Asr2_up: 5'-ATGCTGCTGCTGCTGCTGAA-3' (PAM: GGG) – sitio de corte justo upstream del inicio del promotor nativo para HDR"]
- Controles: ['WT (variedad de referencia, pM82)', 'Transformación vacía (vector sin gRNA ni cassette de HDR)', 'gRNA no dirigido (gRNA aleatorio que no tiene sitio en el genoma del tomate)', 'Línea CRISPR‑KO de un gen no relacionado con sequía (ej. phytoene desaturase) para controlar efectos de edición fuera de objetivo']

**Fenotipado:** {'fase_preliminar (semanas 1‑4)': ['Confirmación molecular: PCR de genotipo, secuenciación Sanger de los sitios objetivo, qRT‑PCR para validar ausencia (KO) o aumento (>5‑fold) de expresión de Asr2 (sobreexpresión).', 'Detección de off‑target: PCR y secuenciación de los 5 loci con mayor puntuación de predicción.'], 'fase_fisiológica (semanas 5‑9)': ['Medición de contenido de agua del suelo (sensor de humedad capacitivo).', 'Potencial hídrico foliar (Ψleaf) con psicrómetro.', 'Contenido relativo de agua (RWC) en hojas.', 'Conductancia estomática y fotosíntesis neta (LICOR 6400).', 'Fluorescencia de clorofila (Fv/Fm) para estrés oxidativo.', 'Concentración de ABA en hojas (LC‑MS/MS).', 'Análisis de metabolitos osmoprotectores (prolina, azúcar soluble).'], 'fase_agronómica (semanas 10‑12)': ['Número de frutos, peso medio de fruto y contenido de licopeno bajo estrés y bajo riego normal.', 'Supervivencia de la planta después de 7 días sin riego y recuperación tras riego.', 'Índice de estrés visual (escala 0‑5).'], 'repeticiones': '10 plantas por línea (KO, OE, WT y controles) dispuestas en bloques al azar dentro de un diseño RCBD.'}

**Validación estadística:** {'diseño': 'Diseño experimental de bloques completos al azar (RCBD) con 4 bloques (replicaciones) y 10 plantas por tratamiento dentro de cada bloque.', 'análisis': ['ANOVA de dos factores (genotipo × tratamiento de riego) para cada variable fisiológica y agronómica.', 'Modelos lineales mixtos (lme4 en R) con bloque como efecto aleatorio.', 'Comparaciones múltiples mediante prueba de Tukey HSD (α = 0.05).', "Cálculo de tamaño del efecto (Cohen's d) y potencia estadística (>0.8) basado en datos preliminares de literatura (p.ej., diferencia esperada del 15% en RWC).", 'Corrección de falsos descubrimientos (FDR) para los análisis de expresión génica (RNA‑seq o qRT‑PCR).'], 'criterios_de_validacion': 'Un genotipo se considerará validado si muestra diferencias estadísticamente significativas (p < 0.05) y un tamaño de efecto ≥0.8 respecto al WT bajo déficit hídrico en al menos tres de los siguientes parámetros: RWC, Ψleaf, conductancia estomática, contenido de ABA y rendimiento de fruto.'}

**Cronograma:** 12 semanas

**Riesgos:**

- Baja eficiencia de HDR para la inserción del promotor; mitigado con uso de geminivirus replicón o edición basada en CRISPR‑Cas12a.
- Posibles efectos pleiotrópicos de la sobreexpresión constitutiva (p. ej., retraso en maduración); se incluirán líneas con promotor inducible por sequía.
- Off‑target mutaciones; se controlarán mediante secuenciación de loci predichos y se seleccionarán líneas sin mutaciones detectables.
- Variabilidad ambiental en el invernadero; se usarán sensores de humedad y temperatura para mantener condiciones homogéneas.
- Pérdida de vigor durante la regeneración de tejidos; se optimizará el medio de cultivo con hormonas adecuadas (zeatin, IAA).

> ⚠️ **Los resultados de este experimento establecerán correlaciones fuertes entre la manipulación de Asr2 y la tolerancia a sequía, pero la causalidad directa sólo podrá confirmarse mediante la combinación de knockout y sobreexpresión, junto con la exclusión de efectos off‑target y pleiotrópicos.**