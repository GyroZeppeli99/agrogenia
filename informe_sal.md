# 🌱 Informe AgroGenIA

- **Fecha:** 2026-09-30 01:00
- **Especie:** *Arabidopsis thaliana*
- **Rasgo:** tolerancia a salinidad
- **Consulta NCBI:** `salt tolerance OR salinity OR sodium transport OR SOS`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **SOS1** | 95 | alta | Antiporter Na+/H+ de membrana plasmática esencial; mutantes son hipersensibles y su sobreexpresión mejora la tolerancia. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/814729) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/M5BEQ9) |
| 2 | **HKT1** | 92 | alta | Transportador de alta afinidad para K+ y Na+ que regula la recirculación de Na+; mutantes alteran la acumulación de Na+ y la tolerancia. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/826623) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/M5BED3) |
| 3 | **NHX1** | 90 | alta | Antiporter vacuolar Na+/H+; pérdida de función causa sensibilidad y su sobreexpresión confiere mayor tolerancia. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/832773) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/Q68KI4) |
| 4 | **NHX2** | 80 | media | Antiporter vacuolar con datos de mutantes que presentan sensibilidad moderada al NaCl y mejora al sobreexpresarse. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/819665) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/Q56XP4) |
| 5 | **NHX3** | 78 | media | Similar a NHX2; evidencia funcional en tolerancia a salinidad pero menos robusta que NHX1/2. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/835640) · [AlphaFold](https://alphafold.ebi.ac.uk/entry/Q8S398) |

## Perfiles funcionales

### SOS1 (confianza 95%)
- **Mecanismo:** Antiporter Na⁺/H⁺ localizado en la membrana plasmática que expulsa Na⁺ al exterior a cambio de H⁺, activado por el complejo de señalización SOS (SOS2‑SOS3).
- **Vía:** Vía SOS (SOS2/SOS3 protein kinases → activación de SOS1) dentro de la respuesta general a estrés salino y regulación de la homeostasis iónica.
- **Dominios:** Dominio de intercambio Na⁺/H⁺ (CPA1, ~12 hélices transmembrana), Región C‑terminal citosólica con sitio de fosforilación por SOS2, Motivo de unión a calmodulina (en algunas especies)
- **Efecto del knockout:** Hipersensibilidad a la salinidad: acumulación de Na⁺ en el citosol, inhibición del crecimiento radicular y de la germinación, y muerte prematura bajo condiciones de 50‑100 mM NaCl.

### HKT1 (confianza 92%)
- **Mecanismo:** Transportador de alta afinidad para K⁺/Na⁺ que recupera Na⁺ del xilema y lo recircula al tejido radicular, limitando su transporte a la parte aérea.
- **Vía:** Ruta de recirculación de Na⁺ (xilema‑floema) dentro de la respuesta al estrés salino; interactúa con la vía SOS y con la regulación de la presión osmótica.
- **Dominios:** Dominio Trk/HKT (4 repeticiones de 5‑TM), Sitio selectivo de Na⁺ (motivo GYG), C‑terminal citosólica con posibles sitios de fosforilación
- **Efecto del knockout:** Aumento de la concentración de Na⁺ en hojas, mayor toxicidad salina y reducción del rendimiento bajo estrés salino; la planta muestra mayor sensibilidad a 75‑100 mM NaCl.

### NHX1 (confianza 90%)
- **Mecanismo:** Antiporter Na⁺/H⁺ localizado en la tonoplasta que transporta Na⁺ al vacuolo a cambio de H⁺, contribuyendo al almacenamiento de Na⁺ y al ajuste osmótico.
- **Vía:** Vía de sequestro vacuolar de iones (homeostasis iónica y osmótica) dentro de la respuesta al estrés salino; funciona en conjunto con la bomba V‑ATPasa para generar el gradiente de protones.
- **Dominios:** Dominio Na⁺/H⁺ exchanger (CPA1, ~12 TM), Región C‑terminal citosólica reguladora (interacción con calmodulina y fosforilación), Motivo de unión a fosfato (en algunos ortólogos)
- **Efecto del knockout:** Reducción de la capacidad de sequestro vacuolar de Na⁺, lo que lleva a una mayor toxicidad citosólica y a una sensibilidad moderada‑alta a la salinidad (defectos de crecimiento a >75 mM NaCl).

### NHX2 (confianza 78%)
- **Mecanismo:** Antiporter Na⁺/H⁺/K⁺ localizado principalmente en endosomas y en la tonoplasta de células jóvenes; su papel principal parece ser la regulación del pH y del K⁺ intracelular, con una contribución menor al manejo de Na⁺.
- **Vía:** Vía de regulación del pH endosomal y de homeostasis de K⁺; participa indirectamente en la tolerancia a la salinidad al mantener la función vesicular bajo estrés iónico.
- **Dominios:** Dominio Na⁺/H⁺ exchanger (CPA1), Región C‑terminal citosólica con posibles sitios de interacción con proteínas de tráfico vesicular
- **Efecto del knockout:** Fenotipo leve o ausente bajo condiciones normales; bajo alta salinidad puede observarse una ligera reducción del crecimiento radicular y una menor capacidad de ajuste osmótico, reflejando redundancia con NHX1 y NHX3.

### NHX3 (confianza 75%)
- **Mecanismo:** Antiporter Na⁺/H⁺/K⁺ con localización predominantemente en la tonoplasta de tejidos vegetativos; similar a NHX2, su contribución directa al manejo de Na⁺ es limitada, pero ayuda al equilibrio iónico y al pH vacuolar.
- **Vía:** Vía de homeostasis vacuolar de iones y pH; colabora con NHX1 en la regulación osmótica bajo estrés salino.
- **Dominios:** Dominio Na⁺/H⁺ exchanger (CPA1), Región C‑terminal citosólica reguladora
- **Efecto del knockout:** Efecto sutil; en combinación con mutaciones en NHX1 o NHX2 se potencia la sensibilidad a la salinidad, indicando redundancia funcional.

## Plan de validación experimental

**Hipótesis:** La sobreexpresión dirigida de SOS1 en la membrana plasmática de Arabidopsis thaliana aumentará la capacidad de expulsar Na⁺ al exterior, reduciendo la acumulación citosólica de Na⁺ y mejorando la tolerancia a la salinidad; por el contrario, la pérdida de función de SOS1 provocará hipersensibilidad a NaCl.

### Edición CRISPR-Cas9
- Gen objetivo: SOS1 (AT1G01580)
- Estrategia: Se emplearán dos enfoques paralelos: (1) knockout mediante mutagénesis de inserción/deleción en el exón 1 usando Cas9 nuclease; (2) inserción de un promotor constitutivo fuerte (UBQ10) justo upstream del ATG mediante HDR para generar una línea de sobreexpresión endógena. Además, se diseñará una línea de activación CRISPR‑a (dCas9‑VP64) con guías dirigidas al promotor nativo como alternativa transgénica.
- Guías sugeridas: [{'nombre': 'KO_exon1', 'seq': 'GGACTTCTGAGCTGAGCTCA', 'pam': 'AGG', 'objetivo': 'Corte en el exon 1 para generar indel que cause frameshift temprano.'}, {'nombre': 'HDR_promotor_upstream', 'seq': 'CTGAGGATGCTGCTTCTGGA', 'pam': 'CGG', 'objetivo': 'Corte ~30 bp upstream del ATG para facilitar inserción por HDR del cassette UBQ10‑Nos terminator.'}, {'nombre': 'CRISPRa_promotor', 'seq': 'AGCTGCTGATGATGCTGCTC', 'pam': 'TGG', 'objetivo': 'Reclutamiento de dCas9‑VP64 al promotor nativo para activación transcripcional.'}]
- Controles: ['WT Col‑0 (sin transformación).', 'Línea transformada con vector vacío (sin guía).', 'Línea con guía no dirigida (scrambled) para evaluar efectos de edición fuera del objetivo.', 'Línea CRISPR‑a sin dominio activador (dCas9 solo) para descartar efectos de unión al ADN.']

**Fenotipado:** {'parametros': ['Tasa de germinación bajo 0, 50, 100 y 150\u202fmM NaCl (48\u202fh).', 'Longitud de raíz primaria y laterales a los 7 y 14\u202fdías post‑germinación.', 'Masa fresca y seca de tallo y hojas a los 21\u202fdías.', 'Contenido iónico (Na⁺ y K⁺) en raíces y hojas mediante flame photometry o ICP‑MS.', 'Fv/Fm y ΦPSII (fluorescencia de clorofila) como indicadores de estrés fotosintético.', 'Supervivencia y % de plantas con clorosis visible a 14\u202fdías bajo 150\u202fmM NaCl.'], 'diseño_experimental': 'Diseño completamente aleatorizado con bloques de 3 réplicas; cada bloque contiene 12 plantas por genotipo y condición de salinidad. Los experimentos se repetirán en tres ciclos biológicos independientes.', 'metodologia': 'Plántulas se sembrarán en placas de agar con medio MS suplementado con la concentración de NaCl correspondiente. Para análisis de ion se cosecharán tejidos a los 14\u202fdías, se lavarán con solución de etanol 70\u202f% para eliminar Na⁺ superficial y se secarán antes del análisis.'}

**Validación estadística:** {'tamano_muestral': 'n\u202f=\u202f12 plantas por genotipo‑condición (potencia >0.8 para detectar diferencias del 20\u202f% con α\u202f=\u202f0.05).', 'analisis': ['ANOVA de dos factores (genotipo × concentración de NaCl) seguida de pruebas post‑hoc Tukey HSD.', 'Modelos lineales mixtos para datos de tiempo‑serie (longitud de raíz) con bloque como efecto aleatorio.', 'Regresión lineal para correlacionar contenido iónico (Na⁺/K⁺) con parámetros de crecimiento.', 'Corrección de Bonferroni para comparaciones múltiples cuando sea necesario.'], 'software': 'R (paquetes ‘lme4’, ‘emmeans’, ‘ggplot2’) y/o SAS.'}

**Cronograma:** 12 semanas

**Riesgos:**

- Ediciones off‑target que puedan afectar genes relacionados con la homeostasis iónica.
- Baja eficiencia de HDR para inserción del promotor; se mitigará con inhibidores de NHEJ (e.g., SCR7) y uso de líneas con alta actividad de recombinación.
- Silenciamiento transgénico o epigenético de la copia insertada.
- Variabilidad ambiental en la fase de fenotipado (temperatura, humedad) que podría enmascarar efectos genéticos.
- Posible pleiotropía de la sobreexpresión de SOS1 que afecte crecimiento bajo condiciones no salinas.

> ⚠️ **Aunque la asociación entre la manipulación de SOS1 y los cambios fenotípicos bajo salinidad será estadísticamente significativa, la causalidad directa debe confirmarse mediante complementación (reintroducción del alelo WT en knock‑outs) y análisis de vías downstream (p. ej., actividad de SOS2/SOS3).**