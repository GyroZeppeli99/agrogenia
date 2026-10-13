# 🌱 Informe AgroGenIA

- **Fecha:** 2026-09-30 01:01
- **Especie:** *Arabidopsis thaliana*
- **Rasgo:** resistencia a enfermedades
- **Consulta NCBI:** `disease resistance OR pathogen OR defense OR R protein`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **SNC1** | 95 | alta | Mutaciones causan auto‑inmunidad y sobreexpresión confiere resistencia a varios patógenos; pruebas genéticas y de transgénesis robustas. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/827397) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/O23530) |
| 2 | **RPM1** | 93 | alta | R‑gene clásica que reconoce AvrRpm1/AvrB; mutantes pierden resistencia y transgenes restauran la respuesta. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/819889) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/L7S0N9) |
| 3 | **RPS5** | 92 | alta | Detecta la proteasa AvrPphB; evidencia de pérdida de función y de complemento funcional en plantas transgénicas. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/837775) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/Q38JZ6) |
| 4 | **RPS2** | 91 | alta | Reconoce AvrRpt2; mutantes son susceptibles y la reintroducción del gen restaura la resistencia. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/828715) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/A3FB66) |
| 5 | **RRS1** | 90 | alta | Funciona con RPS4 contra bacterias y hongos; estudios de mutantes y de interacción proteína‑proteína demuestran causalidad. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/834562) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/C4B7M5) |

## Perfiles funcionales

### SNC1 (confianza 88%)
- **Mecanismo:** Reconoce directamente o indirectamente avirulencia de patógenos a través de su dominio TIR, activando la señalización de inmunidad basada en SA y provocando la respuesta de hipersensibilidad (HR).
- **Vía:** Inmunidad mediada por receptores de resistencia (R) tipo TIR‑NBS‑LRR; ruta de señalización de ácido salicílico (SA) y MAPKs.
- **Dominios:** TIR, NB-ARC, LRR
- **Efecto del knockout:** Mayor susceptibilidad a patógenos como Pseudomonas syringae pv. maculicola y a ciertos hongos; reducción de la respuesta de HR y de la acumulación de SA.

### RPM1 (confianza 90%)
- **Mecanismo:** Detecta la presencia de los efectores bacterianos AvrRpm1 y AvrB mediante vigilancia indirecta de la fosforilación de la proteína RIN4, lo que desencadena la activación del dominio NB‑ARC y la señalización de ETI.
- **Vía:** Inmunidad basada en NBS‑LRR (clase CC‑NBS‑LRR); señalización a través de MAPKs y vía de SA/JA cruzada.
- **Dominios:** CC, NB-ARC, LRR
- **Efecto del knockout:** Pérdida de resistencia contra Pseudomonas syringae pv. tomato que porta AvrRpm1 o AvrB; aumento de la colonización bacteriana y ausencia de HR.

### RPS5 (confianza 87%)
- **Mecanismo:** Reconoce la modificación del objetivo de efecto AvrPphB (la quinasa PBS1) mediante vigilancia indirecta; la liberación de PBS1 activa el dominio NB‑ARC de RPS5 y desencadena la respuesta de ETI.
- **Vía:** Inmunidad CC‑NBS‑LRR; señalización de SA y activación de MAPK cascades que conducen a la expresión de genes de defensa.
- **Dominios:** CC, NB-ARC, LRR
- **Efecto del knockout:** Sensibilidad aumentada a Pseudomonas syringae que expresa AvrPphB; disminución de la HR y de la expresión de PR (proteínas de ruta) genes.

### RPS2 (confianza 86%)
- **Mecanismo:** Detecta la presencia del efectoor AvrRpt2 mediante vigilancia de la proteína objetivo RIN4; la degradación de RIN4 libera a RPS2 para activar su dominio NB‑ARC y la señalización de defensa.
- **Vía:** Inmunidad CC‑NBS‑LRR; vía de SA y generación de ROS (especies reactivas de oxígeno) como parte de la respuesta de ETI.
- **Dominios:** CC, NB-ARC, LRR
- **Efecto del knockout:** Mayor susceptibilidad a Pseudomonas syringae pv. tomato con AvrRpt2; reducción de la HR y de la acumulación de ROS y SA.

### RRS1 (confianza 84%)
- **Mecanismo:** Forma un complejo con la proteína WRKY41 (RRS1‑R) y detecta la presencia del efector AvrRps4 (bacteriano) o PopP2 (fungal) mediante interacción directa con su dominio TIR; la activación conduce a la señalización de ETI y a la transcripción de genes de defensa.
- **Vía:** Inmunidad TIR‑NBS‑LRR; señalización de SA y regulación de la transcripción mediante factores WRKY.
- **Dominios:** TIR, NB-ARC, LRR, WRKY (c-terminal)
- **Efecto del knockout:** Pérdida de resistencia contra bacterias que expresan AvrRps4 y contra el hongo Ralstonia solanacearum que secreta PopP2; aumento de la carga patógena y ausencia de respuesta de HR.

## Plan de validación experimental

**Hipótesis:** La activación o sobreexpresión de SNC1 confiere resistencia broad‑spectrum contra patógenos bacterianos y fúngicos en Arabidopsis thaliana mediante la vía TIR‑NBS‑LRR y la señalización de ácido salicílico (SA).

### Edición CRISPR-Cas9
- Gen objetivo: SNC1 (AT4G16950)
- Estrategia: Generar tres líneas: (1) knockout completo (frameshift) para confirmar la pérdida de resistencia; (2) sobreexpresión mediante inserción de un promotor 35S fuerte delante del CDS; (3) edición puntual de la variante autoactiva SNC1‑D (Gly→Asp en posición 169) para reproducir la resistencia sin efectos de auto‑inmunidad excesiva.
- Guías sugeridas: ["gRNA1: 5'-GGACTTCTGCTGCTGATGAG-3' (exón 2, sitio de corte +3 del codón de inicio, para knockout)", "gRNA2: 5'-CCTGAGCTTCTGAGGAGTCA-3' (exón 4, cerca del dominio NB‑ARC, para inserción de promotor 35S mediante HDR)", "gRNA3: 5'-ATGAGGAGGATGAGCTGCTC-3' (exón 7, posición 169, para sustitución G169D mediante HDR)"]
- Controles: ['WT Col‑0 (sin edición)', 'línea CRISPR‑Cas9 sin guía (vector vacío) para descartar efectos de transformación', 'knockout de un gen no relacionado (ej. ACT2) como control de edición off‑target']

**Fenotipado:** {'ensayos_de_enfermedad': [{'patógeno': 'Pseudomonas syringae pv. maculicola (DC3000)', 'metodo': 'infiltración de 10⁵ CFU/mL en hojas 4‑5, recuento de colonias a 0 y 3 dpi, evaluación de HR visual y fluorescencia de ROS (DCFDA).'}, {'patógeno': 'Botrytis cinerea', 'metodo': 'aplicación de 5 µL de esporas (10⁴ conidiosporas/mL) en discos de hoja, medida del diámetro de lesión a 72 hpi.'}], 'mediciones_moleculares': ['Cuantificación de SA libre y conjugada por LC‑MS/MS a 24 hpi.', 'Expresión de genes marcadores PR1, PR2 y NPR1 por qRT‑PCR (ΔΔCt) en hojas inoculadas.', 'Western blot de SNC1 (si se dispone de anticuerpo) para confirmar niveles de proteína.'], 'fenotipos_de_auto‑inmunidad': ['Observación de necrosis espontánea en plantas sin patógeno.', 'Medición de crecimiento vegetativo (altura, biomasa seca) como indicador de penalización de fitness.'], 'repeticiones': 'Mínimo 8 plantas por línea y condición, con tres experimentos biológicos independientes.'}

**Validación estadística:** {'analisis_principal': 'ANOVA de dos factores (genotipo × tratamiento) seguida de pruebas post‑hoc Tukey HSD para comparar cargas bacterianas, diámetros de lesión y niveles de SA.', 'pruebas_adicionales': 't‑test pareado para comparar WT vs knockout y WT vs sobreexpresión en cada patógeno; análisis de regresión lineal para correlacionar expresión de PR1 y carga patógena.', 'umbral_significancia': 'p < 0.05, corrección de Bonferroni cuando se realicen múltiples comparaciones.', 'software': 'R (packages: lme4, multcomp, ggplot2) y GraphPad Prism para visualización.'}

**Cronograma:** 12 semanas

**Riesgos:**

- Efectos de auto‑inmunidad excesiva en líneas sobreexpresoras que pueden reducir la viabilidad y confundir la interpretación de resistencia.
- Baja eficiencia de HDR en Arabidopsis; se mitigará con uso de constructos de reparación con homología larga (1‑2 kb) y selección de marcadores de resistencia a herbicida.
- Posibles off‑targets de CRISPR; se realizará secuenciación de los loci predichos y se usarán guías con puntuación alta (CFD).
- Variabilidad ambiental en los ensayos de patógenos; se mantendrán condiciones de crecimiento controladas (22 °C, 16 h luz/8 h oscuridad, humedad 60 %).

> ⚠️ **Los resultados experimentales podrán sugerir una asociación entre la actividad de SNC1 y la resistencia observada, pero la causalidad directa sólo se confirmará si los fenotipos de resistencia se reverten de manera consistente en los knockout y se reproducen en las líneas editadas sin efectos colaterales.**