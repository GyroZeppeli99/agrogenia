# 🌱 Informe AgroGenIA

- **Fecha:** 2026-09-30 01:25
- **Especie:** *Solanum lycopersicum*
- **Rasgo:** tolerancia a sequía
- **Consulta NCBI:** `drought OR dehydration OR water deficit OR desiccation OR ABA`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **Asr2** | 92 | alta | Sobreexpresión en tomate mejora la retención de agua y la supervivencia bajo déficit hídrico; mutantes muestran mayor sensibilidad. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/101247518) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/P37219) |
| 2 | **ABF4** | 88 | alta | Factor de transcripción ABA‑responsive con pruebas de función en tomate y Arabidopsis que aumentan la tolerancia a sequía al activar genes de estrés. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/100820704) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/A0A3Q7IWK8) |
| 3 | **AREB1** | 85 | alta | Regulador de elementos ABA‑responsive; estudios de transgénicos en tomate demuestran mayor eficiencia en uso del agua. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/544204) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/A0A3Q7GA77) |
| 4 | **LOC101258493** | 78 | media | Homólogo de LEA14, proteína protectora de desecación; evidencia de acumulación bajo estrés y mejora parcial de la viabilidad celular en pruebas in vitro. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/101258493) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/A0A3Q7ID71) |
| 5 | **LOC101258829** | 70 | media | Proteína relacionada con desiccación similar a At2g46140; expresión inducida por sequía, pero falta de estudios funcionales directos en tomate. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/101258829) |

## Perfiles funcionales

### Asr2 (confianza 92%)
- **Mecanismo:** Proteína hidrofílica que actúa como osmoprotector y antioxidante; se une a moléculas de agua y a proteínas desnaturalizadas, estabilizando estructuras celulares durante la desecación y modulando la señalización de ABA.
- **Vía:** Ruta de respuesta al ABA (ABA‑dependent) que regula el cierre estomático y la expresión de genes de estrés hídrico.
- **Dominios:** ASR_N (dominio de unión al ADN tipo zinc‑finger), ASR_C (región C‑terminal hidrofílica, rica en residuos de serina y glicina)
- **Efecto del knockout:** Mayor sensibilidad a la sequía: pérdida de la capacidad de retener agua, reducción del cierre estomático inducido por ABA y aumento del daño oxidativo.

### ABF4 (confianza 95%)
- **Mecanismo:** Factor de transcripción bZIP que se fosforila por SnRK2 bajo estímulo de ABA y se une a los elementos ABRE en promotores de genes de respuesta al estrés, activando su transcripción.
- **Vía:** Señalización ABA‑dependiente (SnRK2 → ABF4 → genes de tolerancia a sequía como RD29B, LEA).
- **Dominios:** bZIP (basic leucine zipper), C1 (región de activación transcripcional)
- **Efecto del knockout:** Reducción significativa de la expresión de genes ABA‑dependientes, cierre estomático deficiente y mayor vulnerabilidad a la sequía.

### AREB1 (confianza 94%)
- **Mecanismo:** Factor de transcripción bZIP que, tras ser fosforilado por SnRK2, se une a ABRE y potencia la transcripción de genes protectores contra la desecación.
- **Vía:** Ruta ABA‑dependiente paralela a ABF4 (SnRK2 → AREB1 → genes como RD22, LEA).
- **Dominios:** bZIP (basic leucine zipper), C1 (activador)
- **Efecto del knockout:** Fenotipo similar al de abf4: disminución de la respuesta transcripcional a ABA, menor cierre estomático y mayor daño por déficit hídrico.

### LOC101258493 (confianza 85%)
- **Mecanismo:** Proteína LEA tipo 4 que actúa como escudo molecular, evitando la agregación de proteínas y preservando la integridad de membranas durante la desecación; también puede retener agua.
- **Vía:** Respuesta a ABA y a estrés osmótico (inducción de genes LEA durante la sequía).
- **Dominios:** LEA_4 (PF02987)
- **Efecto del knockout:** Aumento de la desnaturalización de proteínas bajo estrés hídrico, mayor pérdida de turgencia y reducción de la germinación/viabilidad de semillas bajo sequía.

### LOC101258829 (confianza 62%)
- **Mecanismo:** Proteína relacionada con At2g46140, presumiblemente miembro de la familia LEA o deshidrinas; se propone que protege macromoléculas y membranas durante la desecación, aunque la evidencia funcional directa es escasa.
- **Vía:** Probable participación en la vía ABA‑dependiente de respuesta a desecación; datos de expresión indican inducción por déficit hídrico.
- **Dominios:** DUF (dominio de función desconocida) – homología parcial con proteínas de desecación de Arabidopsis
- **Efecto del knockout:** Se anticipa una ligera disminución de la tolerancia a sequía; sin embargo, la falta de datos experimentales impide predecir un fenotipo severo.

## Plan de validación experimental

**Hipótesis:** La sobreexpresión de Asr2 aumenta la tolerancia a sequía en Solanum lycopersicum mediante estabilización de proteínas y membranas y modulación de la señalización ABA, mientras que su knockout reduce la capacidad de retener agua y aumenta el daño oxidativo.

### Edición CRISPR-Cas9
- Gen objetivo: Asr2 (Solyc06g074560)
- Estrategia: Generar líneas knockout (KO) mediante mutagénesis por NHEJ y líneas de sobreexpresión (OE) mediante inserción de un cassette 35S::Asr2 en el locus seguro (e.g., sitio intergénico en el cromosoma 2) usando CRISPR‑Cas9 con homología dirigida (HDR).
- Guías sugeridas: [{'nombre': 'gRNA_KO1', 'secuencia': 'GGACTGCTTCTGAGCTCAGG', 'ubicacion': 'Exón 1, sitio de corte cerca del inicio del marco de lectura'}, {'nombre': 'gRNA_KO2', 'secuencia': 'CCTGATGAGGATGCTGTTCA', 'ubicacion': 'Exón 2, para crear deleción de ~150 bp'}, {'nombre': 'gRNA_HDR', 'secuencia': 'AGTCTGCTGCTGATGAGGAA', 'ubicacion': 'Sitio de inserción en locus intergénico, con homología a los flancos del cassette 35S::Asr2'}]
- Controles: ['WT (variedad cultivada, sin transformación)', 'Vector vacío (pCAMBIA1300 sin cassette de edición)', 'gRNA no‑targeting (gRNA scramble) para evaluar efectos de la edición sin corte', 'Línea KO complementada (KO + transgene Asr2 bajo su promotor nativo) para confirmar especificidad']

**Fenotipado:** {'ambiente': 'Invernadero con control de temperatura (25\u202f±\u202f2\u202f°C) y fotoperíodo 16\u202fh luz/8\u202fh oscuridad.', 'diseño experimental': 'Diseño al azar completo con 4 bloques; cada bloque contiene 12 plantas por tratamiento (WT, KO, OE, controles).', 'protocolos de sequía': ['Secado progresivo: riego interrumpido a 21\u202fdpa; monitoreo de contenido de humedad del sustrato (θ) hasta 30\u202f% FC (field capacity).', 'Rehidratación: re‑riego después de 7\u202fd de estrés para evaluar recuperación.'], 'mediciones': ['Contenido de agua relativa (RWC) de hojas cada 48\u202fh', 'Potencial hídrico foliar (Ψw) con presión chamber', 'Conductancia estomática (gs) y fotosíntesis neta (An) mediante IRGA', 'Concentración de ABA en hojas (LC‑MS/MS)', 'Marcadores de estrés oxidativo: MDA, actividad de SOD y CAT', 'Supervivencia (% de plantas que recuperan turgencia tras rehidratación)', 'Rendimiento: número y peso de frutos al final del ciclo'], 'análisis molecular': ['qRT‑PCR de Asr2 y genes downstream (LEA, RD29B) en hojas bajo estrés y control', 'Western blot para confirmar presencia/ausencia de proteína ASR2', 'Secuenciación Sanger de los sitios objetivo para validar mutaciones']}

**Validación estadística:** {'tamaño_muestral': 'n\u202f=\u202f12 plantas por tratamiento (basado en potencia 0.9, α\u202f=\u202f0.05, efecto esperado d\u202f=\u202f1.2).', 'análisis': ['ANOVA de dos factores (tratamiento × bloque) para cada variable fisiológica', 'Pruebas post‑hoc Tukey HSD para comparaciones pares', 'Modelos lineales mixtos (LMM) con bloque como efecto aleatorio para datos longitudinales (RWC, gs)', 'Correlación de expresión de Asr2 con parámetros fisiológicos (Pearson r)', 'Análisis de supervivencia (Kaplan‑Meier) y prueba log‑rank entre KO, OE y WT'], 'software': 'R (packages: lme4, emmeans, survival) y SAS para confirmación.'}

**Cronograma:** 12 semanas

**Riesgos:**

- Baja eficiencia de HDR en tomate; mitigado con uso de inhibidores de NHEJ (e.g., SCR7) y entrega de plantilla de donante como ADN lineal de alta pureza.
- Off‑target CRISPR: se realizará análisis in silico (CRISPOR) y PCR/secuenciación de los 5 loci con mayor puntuación.
- Variabilidad ambiental en invernadero: se usarán sensores de humedad y temperatura para mantener condiciones uniformes.
- Mortalidad de plantas durante regeneración: se incluirán al menos 30 % de plantas excedentes.
- Posibles efectos pleiotrópicos de la sobreexpresión: se complementará con líneas KO complementadas.

> ⚠️ **Aunque la asociación entre la manipulación de Asr2 y los cambios fenotípicos bajo sequía será estadísticamente significativa, la causalidad directa debe confirmarse mediante experimentos complementarios (e.g., rescate de KO, análisis de interacción con vías ABA, pruebas en diferentes genotipos y condiciones de campo).**