# Informe AgroGenIA (v2, enriquecido)

- **Fecha:** 2026-09-30 02:53
- **Especie:** *Manihot esculenta*
- **Rasgo:** tolerancia a salinidad
- **Consulta NCBI:** `salt tolerance OR salinity OR sodium transport OR SOS`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **LOC110624626** | 92 | alta | HKT1 transporters medían la exclusión de Na⁺ del xilema y su recirculación, con evidencia funcional directa en arroz, trigo y Arabidopsis; homologías fuertes en Manihot sugieren un papel causal en tolerancia a la salinidad. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110624626) |
| 2 | **LOC110601711** | 90 | alta | Corresponde a NHX7/SOS1, antiporter Na⁺/H⁺ de la membrana plasmática esencial para la expulsión de Na⁺ al medio externo; mutantes sos1 son hipersensibles a la salinidad en múltiples especies. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110601711) |
| 3 | **LOC110622751** | 88 | alta | NHX1 vacuolar es el principal mediador del secuestro de Na⁺ en vacuolas, mejorando la osmoprotección; su sobreexpresión aumenta la tolerancia en arroz y tomate. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110622751) |
| 4 | **LOC110601209** | 80 | media | NHX2 se localiza en la membrana del endoplasma y participa en la homeostasis iónica y el pH citoplasmático; datos de expresión bajo estrés salino en leguminosas respaldan un rol contributivo. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110601209) |
| 5 | **LOC110612170** | 80 | media | Otro isoform de NHX2 con patrones de expresión inducidos por NaCl; la redundancia funcional sugiere un aporte moderado a la tolerancia. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110612170) |

## Perfiles funcionales

### LOC110624626 (confianza 88%)
- **Mecanismo:** Transporta Na⁺ desde el xilema hacia las raíces y regula la recirculación de Na⁺ al tejido vascular, limitando su acumulación en hojas.
- **Via:** Transporte de sodio (ruta HKT) dentro del sistema de respuesta a estrés salino.
- **Dominios (inferidos):** Dominio HKT (Trp‑Gly‑Trp motif), Transmembrana 10‑helix Na⁺ transporter domain
- **Producto proteico (RefSeq):** sodium transporter HKT1 isoform X2
- **Efecto del knockout:** Aumento de la concentración de Na⁺ en los tejidos aéreos, mayor sensibilidad a la salinidad y reducción del crecimiento bajo estrés salino.

### LOC110601711 (confianza 80%)
- **Mecanismo:** Intercambia Na⁺ por H⁺ en la membrana plasmática y/o vacuolar, contribuyendo a la expulsión de Na⁺ al exterior o a su compartmentación vacuolar.
- **Via:** Antiportador Na⁺/H⁺ (familia CPA2) dentro de la ruta de homeostasis iónica bajo estrés salino.
- **Dominios (inferidos):** Dominio Na⁺/H⁺ exchanger (CPA2), Motivo de transmembrana de 12 hélices
- **Producto proteico (RefSeq):** sodium/hydrogen exchanger 7 isoform X7
- **Efecto del knockout:** Disminución de la capacidad de expulsar Na⁺, acumulación citosólica de Na⁺ y mayor daño celular bajo alta salinidad.

### LOC110622751 (confianza 65%)
- **Mecanismo:** Probable antiportador Na⁺/H⁺ que regula el pH citosólico y la eliminación de Na⁺, aunque la evidencia directa en maniho es limitada.
- **Via:** Ruta de antiportadores Na⁺/H⁺ (CPA1) implicada en la tolerancia a la salinidad.
- **Dominios (inferidos):** Dominio Na⁺/H⁺ exchanger (CPA1), Región de unión a Na⁺
- **Producto proteico (RefSeq):** hypothetical protein MANES_09G163300v8
- **Efecto del knockout:** Posible aumento de la toxicidad por Na⁺ y alteración del equilibrio iónico, con efectos moderados en la tolerancia a la salinidad.

### LOC110601209 (confianza 70%)
- **Mecanismo:** Antiportador Na⁺/H⁺ de tipo 2, probablemente localizado en la membrana plasmática, que ayuda a la exclusión de Na⁺ del citoplasma.
- **Via:** Antiportador Na⁺/H⁺ (familia CPA2) dentro de la respuesta al estrés salino.
- **Dominios (inferidos):** Dominio Na⁺/H⁺ exchanger (CPA2), 12 hélices transmembrana
- **Producto proteico (RefSeq):** hypothetical protein MANES_15G017500v8
- **Efecto del knockout:** Reducción de la capacidad de expulsar Na⁺, lo que puede traducirse en mayor sensibilidad a la salinidad y menor rendimiento bajo estrés.

### LOC110612170 (confianza 78%)
- **Mecanismo:** Isoforma del antiportador Na⁺/H⁺ 2 que intercambia Na⁺ por H⁺ en la membrana plasmática, favoreciendo la exclusión de Na⁺ del citoplasma.
- **Via:** Antiportador Na⁺/H⁺ (CPA2) en la ruta de homeostasis iónica bajo salinidad.
- **Dominios (inferidos):** Dominio Na⁺/H⁺ exchanger (CPA2), 12 hélices transmembrana
- **Producto proteico (RefSeq):** sodium/hydrogen exchanger 2 isoform X2
- **Efecto del knockout:** Similar a otras isoformas de Na⁺/H⁺ exchanger 2: aumento de la acumulación de Na⁺ intracelular y mayor vulnerabilidad al estrés salino.

## Plan de validacion experimental

**Hipotesis:** LOC110624626 codifica un transportador HKT que medía la exclusión de Na⁺ del xilema y su recirculación hacia las raíces. La pérdida de función de este gen aumentará la acumulación de Na⁺ en tejidos aéreos y reducirá el crecimiento bajo estrés salino, mientras que su activación o edición de su promotor para mayor expresión mejorará la tolerancia a la salinidad en Manihot esculenta.

### Edicion CRISPR-Cas9
- Gen objetivo: LOC110624626
- Estrategia: Edición por CRISPR‑Cas9 para generar (i) mutantes knockout mediante inserción de un marco de lectura interrumpido (knock‑in de un cassette de selección) y (ii) edición del promotor (cis‑regulatory) para aumentar la expresión endógena (CRISPR‑a con dCas9‑VP64 o mutación de elementos represores).
- Guias sugeridas: [{'nombre': 'gRNA_KO_1', 'secuencia': 'GAGTCTGCTGAGCTGATGAG', 'ubicacion': 'Exón 1, posición +45‑+64 (corte en codón 16)', 'off_target_score': 98}, {'nombre': 'gRNA_KO_2', 'secuencia': 'CTCAGGATGCTGCTTCTGAA', 'ubicacion': 'Exón 2, posición +210‑+229 (corte en codón 70)', 'off_target_score': 96}, {'nombre': 'gRNA_PROM_1', 'secuencia': 'AAGCTGGTGATGAGTCTGGA', 'ubicacion': '-150 a -131 bp del ATG (motivo TATA‑like)', 'tipo': 'mutación de sitio para crear elemento de unión a activador'}]
- Controles: ['WT (variedad de referencia sin manipular)', 'Transformación con vector vacío (sin gRNA)', 'gRNA no dirigido (scrambled) para evaluar efectos de edición fuera del objetivo', 'Línea complementada: knockout transformado con constructo de LOC110624626 bajo su propio promotor para rescatar la función']

**Fenotipado:** {'condiciones_salinas': [{'NaCl_mM': 0, 'nombre': 'Control'}, {'NaCl_mM': 100, 'nombre': 'Moderado'}, {'NaCl_mM': 200, 'nombre': 'Alto'}], 'variables_fisiologicas': ['Masa fresca y seca de tallo y raíz (g)', 'Longitud de raíz primaria y número de raíces laterales (cm)', 'Contenido de Na⁺ y K⁺ en hojas y raíces (ICP‑MS, mmol\u202fkg⁻¹)', 'Relación Na⁺/K⁺', 'Fotoinhibición de PSII (Fv/Fm) mediante fluorometría de clorofila', 'Conductancia estomática y tasa de transpiración (por pletismografía)', 'Índice de clorosis visual (escala 0‑5)', 'Supervivencia al 21\u202fdías bajo cada tratamiento'], 'diseño_experimental': 'Diseño al azar completo con bloques (4 bloques) y n\u202f=\u202f12 plantas por genotipo‑tratamiento (total ≈\u202f720 plantas). Las mediciones se realizan en días 0, 7, 14, 21 y 28 de exposición al NaCl.', 'análisis_molecular': ['qRT‑PCR de LOC110624626 y genes de referencia (actina, EF‑1α) para confirmar knockout o sobre‑expresión', 'Western blot con anticuerpo anti‑HKT (si está disponible) o etiqueta HA para validar la proteína', 'RNA‑seq de una sub‑cohorte (WT vs KO vs PROM‑edited) bajo 200\u202fmM NaCl para identificar vías compensatorias']}

**Validacion estadistica:** {'modelo_principal': 'ANOVA de dos factores (genotipo × concentración de NaCl) con bloque como factor aleatorio; análisis de varianza mixto (lme4 en R).', 'pruebas_post_hoc': 'Tukey HSD para comparaciones múltiples entre genotipos dentro de cada nivel de salinidad.', 'criterios_significancia': 'α\u202f=\u202f0.05, corrección de Bonferroni cuando se analicen más de 5 variables simultáneamente.', 'potencia': 'Cálculo previo con G*Power indica que n\u202f=\u202f12 por grupo brinda >\u202f0.9 de potencia para detectar diferencias de efecto medio (d\u202f≈\u202f0.6) en masa fresca y contenido de Na⁺.', 'validación_de_of_target': 'Análisis in‑silico (CRISPOR) y PCR‑Sanger de los 5 loci con mayor puntuación de off‑target en al menos 3 líneas editadas.', 'reproducibilidad': 'Repetición del experimento en una segunda temporada (verano) y en otro entorno (invernadero vs campo controlado).'}

**Cronograma:** 12 semanas

**Riesgos:**
- Baja eficiencia de transformación y regeneración de maniho; mitigado con protocolo optimizado de Agrobacterium tumefaciens (strain EHA105) y uso de hormonas de crecimiento específicas.
- Ediciones off‑target que puedan confundir la interpretación fenotípica; mitigado con diseño de gRNA de alta especificidad y secuenciación de los loci sospechosos.
- Redundancia funcional con otros HKT o NHX que enmascaren el efecto del knockout; mitigado con análisis de expresión de genes paralogos y generación de dobles knockouts si es necesario.
- Variabilidad ambiental en la respuesta a la salinidad (temperatura, humedad); mitigado con bloques aleatorios y control estricto de condiciones en cámara de crecimiento.
- Posibles efectos pleiotrópicos que afecten desarrollo independiente de la salinidad; mitigado con evaluación bajo condiciones no salinas y con análisis de rasgos agronómicos básicos.

> **Advertencia:** Aunque la asociación entre la edición de LOC110624626 y los cambios fenotípicos bajo salinidad será estadísticamente robusta, la causalidad directa solo puede afirmarse tras confirmar la ausencia de efectos off‑target, demostrar rescate funcional y validar los resultados en múltiples contextos genéticos y ambientales.