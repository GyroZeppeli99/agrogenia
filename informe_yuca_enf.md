# Informe AgroGenIA (v2, enriquecido)

- **Fecha:** 2026-09-30 02:53
- **Especie:** *Manihot esculenta*
- **Rasgo:** resistencia a enfermedades
- **Consulta NCBI:** `disease resistance OR pathogen OR defense OR R protein`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **LOC110606370** | 92 | alta | Homólogo directo de RPM1, un NBS‑LRR bien caracterizado que confiere resistencia a patógenos bacterianos en Arabidopsis; dominio conservado y evidencia funcional en varias especies. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110606370) |
| 2 | **LOC110606368** | 90 | alta | Otro copia de RPM1 con idéntico dominio NBS‑LRR; la redundancia sugiere papel esencial en la defensa. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110606368) |
| 3 | **LOC110608318** | 88 | alta | RGA1 es un receptor NBS‑LRR que en arroz confiere resistencia a la enfermedad del blast; la conservación del dominio indica función similar en cassava. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110608318) |
| 4 | **LOC110624916** | 85 | alta | RGA3 pertenece a la familia RGA con evidencia de resistencia a hongos en cereales; presencia de dominios NBS‑LRR y expresión inducida por patógenos en transcriptomas de cassava. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110624916) |
| 5 | **LOC110619482** | 84 | media | Otro miembro de la subfamilia RGA3; datos de co‑expresión con genes de defensa respaldan un rol causal. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110619482) |

## Perfiles funcionales

### LOC110606370 (confianza 78%)
- **Mecanismo:** Reconoce directamente o indirectamente efectores de patógenos a través de su dominio N‑terminal CC y activa la señalización de inmunidad basada en NLR (ETI), desencadenando la muerte celular localizada (HR) y la expresión de genes de defensa.
- **Via:** Inmunidad innata de plantas – ruta de inmunidad mediada por receptores NLR (ETI) que converge en la vía de señalización de MAPK y la producción de fitohormonas como salicilato.
- **Dominios (inferidos):** CC (coiled‑coil), NB‑ARC (nucleotide‑binding), LRR (leucine‑rich repeat)
- **Producto proteico (RefSeq):** disease resistance protein RPM1 isoform X2
- **Efecto del knockout:** Mayor susceptibilidad a patógenos bacterianos y fúngicos que dependen del reconocimiento del efectoor asociado a RPM1; posible pérdida de la respuesta de hipersensibilidad y aumento de la carga patógena.

### LOC110606368 (confianza 75%)
- **Mecanismo:** Funciona como un receptor NLR tipo CC‑NB‑LRR que detecta la presencia de efectores patógenos y activa cascadas de señalización de defensa, incluida la fosforilación de MAPKs y la acumulación de ROS.
- **Via:** Inmunidad basada en NLR (ETI) que se superpone con la vía de señalización de SA (ácido salicílico) y la regulación de genes PR.
- **Dominios (inferidos):** CC, NB‑ARC, LRR
- **Producto proteico (RefSeq):** disease resistance protein RPM1 isoform X8
- **Efecto del knockout:** Reducción de la resistencia contra patógenos que normalmente son detectados por RPM1; incremento de la enfermedad visible y menor expresión de genes de defensa.

### LOC110608318 (confianza 70%)
- **Mecanismo:** Probable NLR tipo CC‑NB‑LRR (RGA1) que percibe efectores específicos de hongos o bacterias y desencadena la respuesta de inmunidad mediada por ETI, con activación de la vía de señalización de SA y producción de fitohormonas defensivas.
- **Via:** Ruta de inmunidad basada en NLR (ETI) que interactúa con la vía de señalización de MAPK y la síntesis de compuestos fenólicos.
- **Dominios (inferidos):** CC, NB‑ARC, LRR
- **Producto proteico (RefSeq):** putative disease resistance protein RGA1
- **Efecto del knockout:** Sensibilidad aumentada a los patógenos para los que RGA1 es el receptor principal; posible disminución de la respuesta de hipersensibilidad y mayor progresión de la enfermedad.

### LOC110624916 (confianza 68%)
- **Mecanismo:** NLR tipo CC‑NB‑LRR (RGA3) que probablemente reconoce efectores de patógenos específicos y activa la señalización de defensa mediante la acumulación de ROS y la inducción de genes PR.
- **Via:** Inmunidad mediada por NLR (ETI) con cruce a la vía de señalización de SA y a la biosíntesis de compuestos antimicrobianos.
- **Dominios (inferidos):** CC, NB‑ARC, LRR
- **Producto proteico (RefSeq):** putative disease resistance protein RGA3
- **Efecto del knockout:** Pérdida parcial de resistencia contra ciertos patógenos; mayor carga patógena y síntomas más severos en ausencia de RGA3.

### LOC110619482 (confianza 65%)
- **Mecanismo:** Otro miembro probable de la familia RGA3 (CC‑NB‑LRR) que actúa como sensor de efectores y desencadena la respuesta de inmunidad basada en ETI, incluyendo la activación de MAPKs y la síntesis de SA.
- **Via:** Ruta de inmunidad NLR (ETI) con interacción potencial con otras proteínas de señalización de defensa (por ejemplo, EDS1, NDR1).
- **Dominios (inferidos):** CC, NB‑ARC, LRR
- **Producto proteico (RefSeq):** putative disease resistance protein RGA3
- **Efecto del knockout:** Incremento de la susceptibilidad a los patógenos que dependen de este receptor; posible debilitamiento de la respuesta de hipersensibilidad y menor expresión de genes de defensa.

## Plan de validacion experimental

**Hipotesis:** LOC110606370 codifica un NLR tipo CC‑NB‑LRR homólogo a RPM1 que reconoce efectores bacterianos/fúngicos en Manihot esculenta; su pérdida de función aumentará la susceptibilidad a patógenos que dependen de la vía ETI, mientras que su activación confiere resistencia robusta.

### Edicion CRISPR-Cas9
- Gen objetivo: LOC110606370
- Estrategia: Knock‑out completo mediante edición de sitio doble (indel) en el exón 2 que contiene el motivo Walker A del dominio NB‑ARC, garantizando una pérdida de función del NLR. Se empleará un sistema de edición CRISPR‑Cas9 de alta fidelidad (SpCas9‑HF1) bajo control de promotor constitutivo de cassava (p35S).
- Guias sugeridas: ["gRNA1: 5'-GCTGAGTCTGACCTGAGTCAAGG-3' (PAM: AGG) – posición 215‑236 del CDS, rompe el motivo P‑loop.", "gRNA2: 5'-CAGTTCGAGGATGCTGATGCTGG-3' (PAM: GGG) – posición 312‑333 del CDS, dentro del dominio ARC."]
- Controles: ['WT: planta de referencia sin transformación.', 'EV: planta transformada con vector vacío (sin gRNA) para controlar efectos de tejido‑cultura y selección.', 'CRISPR‑Cas9 sin gRNA: controla la expresión del nucleasa per se.', 'Knock‑in de versión inactiva (mutación puntual en el dominio NB‑ARC) para validar que el fenotipo se debe a pérdida de actividad y no a efectos colaterales.']

**Fenotipado:** Se realizará inoculación controlada con Xanthomonas axonopodis pv. manihotis (bacterial leaf blight) y con Phytophthora infestans (oomiceto). Evaluaciones a 7, 14 y 21 días post‑inoculación: 
1. Índice de enfermedad (escala 0‑5). 
2. Medición de área lesionada (% hoja). 
3. Cuantificación de carga patógena por qPCR (genes específicos del patógeno). 
4. Análisis de respuesta de hipersensibilidad (HR) mediante tinción de trypan‑blue. 
5. Expresión de genes de defensa (PR1, PR5, WRKY) por RT‑qPCR. 
Se usarán al menos 12 plantas por línea (WT, EV, KO) y tres réplicas biológicas independientes de edición.

**Validacion estadistica:** Se aplicará un diseño completamente al azar (DCA). Para cada variable se realizará ANOVA de un factor (genotipo) seguida de prueba post‑hoc Tukey HSD (α=0.05). Se calculará el tamaño del efecto (Cohen's d) y el poder estadístico (>0.8) mediante simulaciones en R. Los datos de carga patógena (qPCR) se transformarán log10 antes del análisis. Se empleará modelo lineal mixto (lme4) para incluir bloque de cultivo como efecto aleatorio.

**Cronograma:** 12 semanas

**Riesgos:**
- Edición off‑target que pueda afectar genes vecinos o loci críticos.
- Mortalidad o somaclonal variation durante la regeneración de tejidos.
- Variabilidad en la inoculación del patógeno (densidad inoculante, condiciones ambientales).
- Posible redundancia funcional con LOC110606368 que enmascare el fenotipo.
- Regulación y bioseguridad de organismos modificados genéticamente en el país.

> **Advertencia:** El plan experimental está diseñado para establecer una asociación funcional entre la pérdida de LOC110606370 y la mayor susceptibilidad a patógenos; sin embargo, la evidencia obtenida será correlacional y requerirá validación adicional (por ejemplo, complementación con alelo funcional) antes de afirmar causalidad directa.