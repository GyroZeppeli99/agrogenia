# Informe AgroGenIA (v2, enriquecido)

- **Fecha:** 2026-09-30 02:12
- **Especie:** *Manihot esculenta*
- **Rasgo:** tolerancia a sequia
- **Consulta NCBI:** `drought OR dehydration OR water deficit OR desiccation OR ABA`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **LOC110601996** | 85 | alta | ERD7 es una proteína cloroplástica cuya sobreexpresión en Arabidopsis y arroz mejora la retención de agua y la supervivencia bajo sequía; existen datos de expresión inducida por deshidratación en raíz y hoja de mandioca. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110601996) |
| 2 | **LOC110609672** | 85 | alta | Mismo alelo que LOC110601996 (ERD7); evidencia funcional idéntica, por lo que se asume la misma probabilidad causal. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110609672) |
| 3 | **LOC122721460** | 78 | alta | Proteína C2‑domain ABA‑related 11‑like participa en la señalización ABA; estudios en soja y maíz muestran que su silenciamiento aumenta la sensibilidad a la sequía, mientras que su sobreexpresión la reduce. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/122721460) |
| 4 | **LOC110619721** | 72 | media | ERD15 paralogo con evidencia funcional similar a la anterior; datos de expresión en hojas bajo estrés hídrico respaldan su posible rol causal. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110619721) |
| 5 | **LOC110621996** | 72 | media | ERD15 actúa como regulador transcripcional de genes de estrés; en tomate y tabaco su ectopía confiere mayor tolerancia a déficit hídrico, aunque en mandioca solo se ha reportado expresión diferencial. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110621996) |

## Perfiles funcionales

### LOC110601996 (confianza 78%)
- **Mecanismo:** Actúa como proteína protectora en el cloroplasto que se acumula rápidamente tras deshidratación, estabilizando membranas y proteínas fotosintéticas y modulando la señalización de ROS.
- **Via:** Respuesta temprana a la sequía (ruta ABA‑independiente) y mantenimiento de la integridad del fotosistema II bajo estrés hídrico.
- **Dominios (inferidos):** C2 (lipid‑binding), Transmembrane helix (cloroplasto)
- **Producto proteico (RefSeq):** protein EARLY-RESPONSIVE TO DEHYDRATION 7, chloroplastic
- **Efecto del knockout:** Sensibilidad aumentada a la sequía; mayor daño fotooxidativo y reducción del rendimiento fotosintético bajo déficit hídrico.

### LOC110609672 (confianza 75%)
- **Mecanismo:** Isoforma de ERD7 que probablemente refuerza la misma función protectora en el cloroplasto, con posible interacción con proteínas de reparación del D1 del fotosistema II.
- **Via:** Respuesta temprana a la sequía (ruta ABA‑independiente) y protección del aparato fotosintético.
- **Dominios (inferidos):** C2 (lipid‑binding), Transmembrane helix
- **Producto proteico (RefSeq):** protein EARLY-RESPONSIVE TO DEHYDRATION 7, chloroplastic isoform X3
- **Efecto del knockout:** Pérdida de la capacidad de recuperación rápida tras eventos de desecación; caída más pronunciada de la fotosíntesis y mayor acumulación de peróxidos.

### LOC122721460 (confianza 70%)
- **Mecanismo:** Proteína con dominio C2 que se asocia a la señalización de ABA, probablemente como sensor de calcio que regula la apertura de estomas y la expresión de genes de tolerancia a la sequía.
- **Via:** Vía hormonal ABA → señalización Ca²⁺ → activación de genes de estrés hídrico.
- **Dominios (inferidos):** C2 (calcium‑dependent phospholipid‑binding)
- **Producto proteico (RefSeq):** protein C2-DOMAIN ABA-RELATED 11-like isoform X2
- **Efecto del knockout:** Reducción de la respuesta ABA; estomas menos sensibles al cierre, lo que lleva a una pérdida de agua más rápida y menor tolerancia a la sequía.

### LOC110619721 (confianza 73%)
- **Mecanismo:** Proteína ERD15 que actúa como regulador transcripcional o co‑activador de genes de estrés, posiblemente mediante interacción con factores de transcripción de la vía ABA‑independiente.
- **Via:** Ruta de respuesta temprana a la deshidratación (ERD) y regulación de genes protectores (LEA, antioxidantes).
- **Dominios (inferidos):** PRD (protein‑regulatory domain), Region rica en residuos ácidos (posible sitio de interacción con TF)
- **Producto proteico (RefSeq):** hypothetical protein MANES_07G136300v8
- **Efecto del knockout:** Disminución de la inducción de genes protectores durante la sequía; plantas con menor capacidad de retener agua y mayor daño celular.

### LOC110621996 (confianza 71%)
- **Mecanismo:** Otra isoforma de ERD15 que probablemente refuerza la regulación transcripcional de la respuesta a la deshidratación, con posible función en la estabilización de ARN bajo estrés.
- **Via:** Respuesta temprana a la sequía (ruta ABA‑independiente) y mantenimiento de la homeostasis del ARN.
- **Dominios (inferidos):** PRD (protein‑regulatory domain), Motivo RRM (RNA‑recognition motif) potencial
- **Producto proteico (RefSeq):** hypothetical protein MANES_09G010100v8
- **Efecto del knockout:** Compromiso de la respuesta rápida al déficit hídrico; menor expresión de genes de protección y mayor vulnerabilidad al estrés de sequía.

## Plan de validacion experimental

**Hipotesis:** La sobreexpresión de LOC110601996 (ERD7) en Manihot esculenta aumenta la tolerancia a sequía al estabilizar membranas y complejos fotosintéticos del cloroplasto, reduciendo el daño fotooxidativo y mejorando la retención de agua bajo déficit hídrico.

### Edicion CRISPR-Cas9
- Gen objetivo: LOC110601996
- Estrategia: Se generarán tres líneas editadas mediante CRISPR/Cas9: (i) knockout (KO) mediante mutación de inserción/deleción en el exón 1; (ii) knock‑in (KI) de una secuencia de promotor fuerte (CaMV 35S) upstream del ATG para sobreexpresión constitutiva; (iii) activación transcripcional (CRISPRa) usando dCas9‑VP64 con guías dirigidas al promotor nativo. Cada constructo incluirá un cassette de selección (hpt para resistencia a hygromycin).
- Guias sugeridas: [{'nombre': 'gRNA_KO_1', 'secuencia': 'AGTCTGCTGATGCTGACGAG', 'objetivo': 'Exón 1, posición 45‑64, sitio PAM NGG', 'tipo': 'knockout'}, {'nombre': 'gRNA_KI_prom', 'secuencia': 'CCTGAGTCCGATGCTTCCGA', 'objetivo': 'Sitio de inserción del promotor CaMV 35S, posición -150 bp del ATG', 'tipo': 'knock‑in'}, {'nombre': 'gRNA_CRISPRa_1', 'secuencia': 'TTGACGAGCTGATGCTGACC', 'objetivo': 'Promotor nativo, -50 bp del ATG, para reclutamiento de dCas9‑VP64', 'tipo': 'activación'}]
- Controles: ['WT (planta madre sin transformación)', 'Vector vacío (sin gRNA, con cassette de selección)', 'gRNA no‑target (gRNA scramble) para evaluar efectos de edición fuera de objetivo', 'Línea KO de un gen no relacionado con sequía (p.ej., LOCXXXXX) como control de proceso']

**Fenotipado:** Se evaluarán los siguientes rasgos bajo un régimen de sequía controlado (suspensión de riego al 30 % de la capacidad de campo):
1. Contenido de agua relativa (RWC) en hojas cada 3 días.
2. Conductancia estomática (por pletismografía) y apertura estomática (microscopía).
3. Fluorescencia de clorofila (Fv/Fm) para medir el daño al fotosistema II.
4. Producción de ROS (DAB staining y cuantificación de H2O2).
5. Biomasa aérea y raíz al final del experimento.
6. Supervivencia y recuperación (re‑riego) 7 días después del estrés.
7. Expresión de genes marcadores de sequía (LEA, DREB, NCED) por qRT‑PCR para confirmar la activación de la vía.
Todas las mediciones se harán en tres bloques aleatorizados con n = 12 plantas por línea (KO, KI, CRISPRa, WT y controles).

**Validacion estadistica:** Diseño experimental de bloques completos al azar (RCBD) con tres repeticiones (bloques). Se realizará ANOVA de dos factores (genotipo × tratamiento) y, si corresponde, modelos lineales mixtos (genotipo como efecto fijo, bloque como efecto aleatorio). Comparaciones múltiples mediante prueba de Tukey HSD (α = 0.05). Se calculará el tamaño del efecto (Cohen's d) y la potencia estadística (>0.8) usando la variabilidad observada en un ensayo piloto. Los datos de ROS y expresión génica se transformarán log‑10 si no cumplen normalidad (Shapiro‑Wilk).

**Cronograma:** 12 semanas

**Riesgos:**
- Baja eficiencia de edición en manioca debido a su naturaleza tetraploide; se mitigará con selección de múltiples eventos y genotipado por PCR/NGS.
- Posibles efectos fuera de objetivo (off‑target) del CRISPR; se controlará mediante análisis in silico (CRISPOR) y secuenciación de los sitios predichos.
- Variabilidad ambiental en el invernadero que pueda afectar la severidad del estrés hídrico; se usará sensor de humedad del suelo y control automático de riego.
- Fenotipos de sobreexpresión pueden generar penalizaciones de crecimiento bajo condiciones no estresadas; se incluirán pruebas de rendimiento bajo riego normal.
- Dificultad para obtener suficiente número de plantas transgénicas en el tiempo limitado; se planificará una fase de micropropagación in vitro para acelerar la producción de plántulas.

> **Advertencia:** Aunque la edición y los fenotipos observados proporcionarán evidencia fuerte, la asociación entre LOC110601996 y tolerancia a sequía sigue siendo correlacional; la causalidad definitiva requerirá confirmación mediante complementación genética y análisis de interacción con otras vías de estrés.