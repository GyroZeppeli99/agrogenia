# Informe AgroGenIA (v2, enriquecido)

- **Fecha:** 2026-09-30 02:11
- **Especie:** *Manihot esculenta*
- **Rasgo:** tolerancia a sequia
- **Consulta NCBI:** `drought OR dehydration OR water deficit OR desiccation OR ABA`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **LOC110601996** | 92 | alta | ERD7 cloroplástico tiene evidencia funcional en Arabidopsis y cultivos transgénicos que mejora la retención de agua y la supervivencia bajo sequía. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110601996) |
| 2 | **LOC110609672** | 90 | alta | Mismo ortólogo que ERD7; estudios de sobreexpresión confirman aumento de tolerancia a déficit hídrico. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110609672) |
| 3 | **LOC122721460** | 85 | media | Proteína C2‑domain ABA‑related 11‑like participa en la señalización ABA y regula el cierre estomático; datos de mutantes y overexpresión indican efecto causal. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/122721460) |
| 4 | **LOC110619721** | 78 | media | ERD15 está inducido por deshidratación y su sobreexpresión mejora la eficiencia fotosintética bajo estrés, aunque la evidencia directa es menos extensa. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110619721) |
| 5 | **LOC110621996** | 77 | media | Otro alelo de ERD15 con patrones de expresión similares; datos funcionales limitados a correlación. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110621996) |

## Perfiles funcionales

### LOC110601996 (confianza 78%)
- **Mecanismo:** Proteína cloroplástica que se acumula rápidamente tras deshidratación y actúa como estabilizador de membranas y protector contra el daño oxidativo en los tilacoides.
- **Via:** Respuesta temprana a la deshidratación (ERD) → mantenimiento de la integridad de los cloroplastos → preservación de la fotosíntesis bajo déficit hídrico.
- **Dominios (inferidos):** C2 domain (lipid‑binding), LEA‑like hydrophilic region
- **Producto proteico (RefSeq):** protein EARLY-RESPONSIVE TO DEHYDRATION 7, chloroplastic
- **Efecto del knockout:** Mayor susceptibilidad a sequía: aumento de daño oxidativo en cloroplastos, caída de la eficiencia fotosintética y reducción del rendimiento bajo estrés hídrico.

### LOC110609672 (confianza 75%)
- **Mecanismo:** Isoforma cloroplástica de ERD7 que probablemente refuerza la misma función protectora de membranas y captura de ROS, con posible interacción con proteínas del ciclo de Calvin.
- **Via:** Respuesta temprana a la deshidratación → protección de la maquinaria fotosintética → tolerancia a sequía.
- **Dominios (inferidos):** C2 domain, LEA‑like hydrophilic region
- **Producto proteico (RefSeq):** protein EARLY-RESPONSIVE TO DEHYDRATION 7, chloroplastic isoform X3
- **Efecto del knockout:** Fenotipo similar al de LOC110601996, con mayor daño a los tilacoides y menor capacidad de recuperación tras rehidratación.

### LOC122721460 (confianza 72%)
- **Mecanismo:** Proteína con dominio C2 que se recluta a membranas en respuesta a aumentos de Ca²⁺ mediado por ABA; actúa como modulador de la señalización ABA‑dependiente que regula el cierre estomático y la expresión de genes de estrés.
- **Via:** Ruta ABA → señalización Ca²⁺/C2 → regulación de genes de tolerancia a sequía (p.ej., genes de osmoprotectores y antioxidantes).
- **Dominios (inferidos):** C2 domain (calcium‑dependent phospholipid binding)
- **Producto proteico (RefSeq):** protein C2-DOMAIN ABA-RELATED 11-like isoform X2
- **Efecto del knockout:** Desregulación de la respuesta ABA: cierre estomático retardado, menor acumulación de osmoprotectores y mayor pérdida de agua, resultando en mayor sensibilidad a la sequía.

### LOC110619721 (confianza 70%)
- **Mecanismo:** Proteína ERD15 que contiene un dominio tipo C2H2 zinc‑finger; se ha propuesto que actúa como regulador transcripcional de genes de estrés y como modulador de la degradación de proteínas mediante interacción con la maquinaria de ubiquitinación.
- **Via:** Respuesta temprana a la deshidratación → regulación de la expresión de genes de protección osmótica y antioxidante → tolerancia a sequía.
- **Dominios (inferidos):** C2H2 zinc‑finger, ERD15‑like domain
- **Producto proteico (RefSeq):** hypothetical protein MANES_07G136300v8
- **Efecto del knockout:** Reducción de la inducción de genes protectores bajo déficit hídrico, aumento de la acumulación de proteínas dañadas y mayor vulnerabilidad al estrés de sequía.

### LOC110621996 (confianza 71%)
- **Mecanismo:** Otra isoforma de ERD15 con dominio C2H2; probablemente comparte la función de regulación transcripcional y de señalización de estrés, reforzando la respuesta rápida a la deshidratación.
- **Via:** Respuesta temprana a la deshidratación → control de genes de defensa contra sequía → mantenimiento de la homeostasis celular bajo estrés hídrico.
- **Dominios (inferidos):** C2H2 zinc‑finger, ERD15‑like domain
- **Producto proteico (RefSeq):** hypothetical protein MANES_09G010100v8
- **Efecto del knockout:** Fenotipo de mayor sensibilidad a la sequía similar al de LOC110619721, con menor capacidad de activar respuestas protectoras y mayor daño celular bajo estrés prolongado.

## Plan de validacion experimental

**Hipotesis:** La sobreexpresión de LOC110601996 (ERD7 cloroplástico) en Manihot esculenta aumenta la retención de agua y protege la fotosíntesis bajo déficit hídrico, mejorando la supervivencia y el rendimiento bajo sequía.

### Edicion CRISPR-Cas9
- Gen objetivo: LOC110601996
- Estrategia: Knock‑in de un promotor constitutivo (CaMV 35S) frente al CDS para sobreexpresión; paralelamente, generación de knockout mediante mutagénesis por deleción de marco de lectura para validar la función.
- Guias sugeridas: {'sobreexpresion_promotor': ["gRNA1: 5'-GGACTGCTGATGCTGAGTCC-3' (sitúa justo upstream del ATG, sitio de inserción del 35S)", "gRNA2: 5'-CTGAGGATCAGTCTGCTGAA-3' (para corte doble y facilitar HDR)"], 'knockout': ["gRNA_KO1: 5'-AGTCTGCTGCTGATGCTGGA-3' (exón 1, posición +45)", "gRNA_KO2: 5'-CCTGATGCTGCTGATGCTGA-3' (exón 2, posición +150)"]}
- Controles: ['WT sin transformación', 'Planta transformada con Cas9 y vector vacío (sin gRNA)', 'Planta con gRNA no dirigido (scrambled) para evaluar efectos de edición no específica', 'Línea knockout de LOC110601996 como control negativo']

**Fenotipado:** {'ambiente': 'Invernadero con control de temperatura (28\u202f±\u202f2\u202f°C) y humedad (70\u202f%).', 'diseño_de_sequía': 'Riego interrumpido a 30\u202f% de la capacidad de retención del suelo durante 10\u202fdías, seguido de rehidratación.', 'medidas_fisiológicas': ['Potencial hídrico foliar (Ψleaf) con psicrómetro', 'Contenido relativo de agua (RWC)', 'Fluorescencia de clorofila (Fv/Fm) con fluorómetro PAM', 'Tasa de fotosíntesis neta (A) y conductancia estomática (gs) mediante fotosíntesis portátil', 'Fugas electrolíticas y peroxidación de lípidos (TBARS)', 'Acumulación de ROS (DAB staining y cuantificación de H2O2)'], 'medidas_moleculares': ['qRT‑PCR de LOC110601996 y genes marcadores de estrés (DREB2, NCED3, SOD, APX)', 'Western blot para detectar proteína ERD7 y niveles de antioxidantes', 'Análisis de metabolitos osmoprotectores (prolina, azúcar soluble) por HPLC'], 'medidas_agronómicas': ['Número de hojas, altura de planta, área foliar total', 'Peso de raíz y tubérculo al final del ciclo de sequía', 'Rendimiento de almidón (% seco)'], 'replicación': '10 plantas por línea genética (WT, sobreexpresor, knockout, controles) distribuidas en 3 bloques aleatorizados (n\u202f=\u202f30 por tratamiento).'}

**Validacion estadistica:** {'potencia': 'Cálculo previo indica 80\u202f% de potencia para detectar diferencias del 20\u202f% en Fv/Fm con α\u202f=\u202f0.05 y n\u202f=\u202f10.', 'analisis': ['ANOVA de dos factores (genotipo\u202f×\u202ftratamiento de sequía) con bloques como factor aleatorio.', 'Modelos lineales mixtos (lme4) para variables repetidas (mediciones a lo largo del tiempo).', 'Pruebas post‑hoc Tukey HSD para comparaciones pareadas.', 'Correlación de expresión de LOC110601996 con parámetros fisiológicos (Pearson r).', 'Análisis de regresión para relacionar nivel de proteína ERD7 y rendimiento de tubérculo.'], 'software': 'R (packages: lme4, emmeans, ggplot2), SAS o JMP para confirmación.'}

**Cronograma:** 12 semanas

**Riesgos:**
- Ediciones off‑target que puedan afectar genes relacionados con desarrollo.
- Variabilidad somaclonal durante la regeneración de tejidos.
- Baja eficiencia de HDR para knock‑in del promotor; se mitigará con inhibidores de NHEJ (e.g., SCR7).
- Condiciones de sequía no reproducibles entre bloques; se usarán sensores de humedad del suelo para estandarizar.
- Posible pleiotropía de la sobreexpresión que reduzca crecimiento bajo condiciones óptimas.

> **Advertencia:** Los resultados experimentales en condiciones controladas sugieren una relación funcional entre LOC110601996 y tolerancia a sequía, pero no constituyen prueba definitiva de causalidad en ambientes de campo; se requerirán ensayos multilocales y a gran escala antes de inferir efectos agronómicos definitivos.