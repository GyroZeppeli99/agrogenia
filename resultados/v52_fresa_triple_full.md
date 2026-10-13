# Busqueda Trans-especie Orquestada · AgroGenIA V5.2

- **Fecha:** 2026-10-12 17:04
- **Estrategia de seleccion:** B (diversidad equilibrada)
- **Panel de donantes:** hibrido
- **Max proteinas por especie:** 50000
- **Modo de busqueda:** exhaustivo: pre-ranqueo heuristico + LLM por lotes
- **Rasgo objetivo:** tolerancia a sequia
- **Receptora (input usuario):** fresa
- **Especie receptora resuelta:** *Fragaria vesca*
- **Tax_id receptora:** 57918
- **Tipo receptora:** eucariota
- **Proteoma receptora:** proteomas_receptor/proteoma_Fragaria_vesca.faa
- **Proteinas receptora:** 31492
- **Base Pfam:** sub-base:sequia
- **Modo Pfam:** auto
- **Especies donantes validas:** 13
- **Especies descartadas:** 3
- **Candidatos priorizados:** 30

## Especies donantes sugeridas por el LLM

### Aceptadas (con genoma disponible)

- **Xerophyta viscosa** (tax_id 90708)
  - Tipo: planta
  - Adaptacion: Planta resurrección que tolera desecación extrema mediante LEA, HSP y protección de membranas.
  - Genes clave: LEA, HSP90, DREB2A
- **Selaginella moellendorffii** (tax_id 88036) (alternativa de Selaginella lepidophylla)
  - Tipo: planta
  - Adaptacion: Planta resurrección con estabilización de membranas y protección antioxidante durante desecación.
  - Genes clave: LEA, sucrose phosphate synthase, antioxidant
- **Craterostigma plantagineum** (tax_id 4153)
  - Tipo: planta
  - Adaptacion: Planta resurrección modelo para tolerancia a desecación y recuperación tras rehidratación.
  - Genes clave: LEA, DREB, CPK
- **Eutrema salsugineum** (tax_id 72664)
  - Tipo: planta
  - Adaptacion: Crucífera halófita/xerófita con regulación osmótica y ABA eficiente.
  - Genes clave: DREB2A, NCED3, SOS1
- **Sorghum bicolor** (tax_id 4558)
  - Tipo: planta
  - Adaptacion: Cereal C4 tolerante a sequía con cierre estomático rápido y acumulación de osmólitos.
  - Genes clave: NAC, DREB, PP2C, TPP
- **Bacillus subtilis** (tax_id 1423)
  - Tipo: bacteria
  - Adaptacion: Bacteria del suelo productora de osmoprotectores, trehalosa, prolina y biofilm.
  - Genes clave: otsA, proP, betA, eps
- **Pseudomonas fluorescens** (tax_id 294)
  - Tipo: bacteria
  - Adaptacion: Rhizobacteria promotora del crecimiento que mejora retención de agua en rizosfera.
  - Genes clave: trehalose synthase, ACC deaminase, exopolysaccharide
- **Trichoderma harzianum** (tax_id 5544)
  - Tipo: hongo
  - Adaptacion: Hongo benéfico que induce tolerancia a sequía en plantas mediante señalización y osmoprotectores.
  - Genes clave: TPS1, HOG1, chaperone
- **Halobacterium salinarum** (tax_id 2242)
  - Tipo: arquea
  - Adaptacion: Arquea extrema con protección frente a desecación y estrés osmótico.
  - Genes clave: Dps, trehalose, bacteriorhodopsin, chaperone
- **Zea mays** (tax_id 4577)
  - Tipo: planta
  - Adaptacion: Evita la sequía mediante un sistema radicular profundo y ajuste osmótico
  - Genes clave: ZmDREB2A, ZmNCED1, ZmPIP1
- **Oryza sativa** (tax_id 4530)
  - Tipo: planta
  - Adaptacion: Tolerancia a la sequía a través de señalización ABA y expresión de proteínas LEA
  - Genes clave: OsDREB2B, OsNCED2, OsLEA3
- **Amaranthus hypochondriacus** (tax_id 28502) (alternativa de Salicornia europaea)
  - Tipo: planta
  - Adaptacion: Halofita con síntesis de osmólitos y uso eficiente del agua bajo condiciones salinas y secas
  - Genes clave: SeDREB2, SeNCED1, SePIP1
- **Selenicereus undatus** (tax_id 176265) (alternativa de Opuntia ficus-indica)
  - Tipo: planta
  - Adaptacion: Cacto suculento con fotosíntesis CAM y tejidos de almacenamiento de agua
  - Genes clave: OfDREB2A, OfNCED3, OfPIP2

### Descartadas

- ~~Selaginella lepidophylla~~ → Sin genoma; reemplazada por Selaginella moellendorffii
- ~~Salicornia europaea~~ → Sin genoma; reemplazada por Amaranthus hypochondriacus
- ~~Opuntia ficus-indica~~ → Sin genoma; reemplazada por Selenicereus undatus

## Ranking separado por reino (V5.1)

- **Top plantas solicitado:** 20
- **Top microorganismos solicitado:** 10
- **Plantas seleccionadas:** 25
- **Microorganismos seleccionados:** 5

### Top plantas

| #| Accession| Donante| Tipo| Grupo| Score| Pre-score| Soporte| Europe PMC| Estrategia| Riesgo|
|---:|---|---|---|---|---:|---:|---:|---|---|---|
| 1 | CAD36023.1 | *Craterostigma plantagineum* | planta | planta | 93 | 33 | ? | NOVEL | transgenesis | medio |
| 2 | AAZ72653.1 | *Craterostigma plantagineum* | planta | planta | 92 | 43 | ? | NOVEL | edicion_genica | medio |
| 3 | XP_025876545.2 | *Oryza sativa* | planta | planta | 90 | 318 | ? | NOVEL | edicion_genica | bajo |
| 4 | XP_006392370.1 | *Eutrema salsugineum* | planta | planta | 88 | 318 | ? | NOVEL | transgenesis | medio |
| 5 | AAZ72654.1 | *Craterostigma plantagineum* | planta | planta | 88 | 43 | ? | NOVEL | edicion_genica | medio |
| 6 | XP_002467609.2 | *Sorghum bicolor* | planta | planta | 85 | 538 | ? | NOVEL | edicion_genica | bajo |
| 7 | XP_024006402.1 | *Eutrema salsugineum* | planta | planta | 85 | 318 | ? | NOVEL | edicion_genica | bajo |
| 8 | XP_006400210.1 | *Eutrema salsugineum* | planta | planta | 85 | 293 | ? | NOVEL | edicion_genica | bajo |
| 9 | AAN34791.1 | *Xerophyta viscosa* | planta | planta | 85 | -2 | ? | NOVEL | edicion_genica | bajo |
| 10 | XP_024540135.1 | *Selaginella moellendorffii* | planta | planta | 82 | 318 | ? | NOVEL | edicion_genica | bajo |
| 11 | AAP22171.1 | *Xerophyta viscosa* | planta | planta | 82 | 3 | ? | 1 menciones | transgenesis | medio |
| 12 | NP_001130206.1 | *Zea mays* | planta | planta | 80 | 383 | ? | NOVEL | transgenesis | medio |
| 13 | XP_035815535.1 | *Zea mays* | planta | planta | 80 | 228 | ? | NOVEL | transgenesis | medio |
| 14 | XP_015612592.1 | *Oryza sativa* | planta | planta | 78 | 318 | ? | NOVEL | transgenesis | medio |
| 15 | XP_066161079.1 | *Oryza sativa* | planta | planta | 78 | 318 | ? | NOVEL | transgenesis | medio |
| 16 | XP_002451782.1 | *Sorghum bicolor* | planta | planta | 78 | 318 | ? | NOVEL | transgenesis | medio |
| 17 | XP_002459355.1 | *Sorghum bicolor* | planta | planta | 76 | 363 | ? | NOVEL | transgenesis | medio |
| 18 | XP_002966448.1 | *Selaginella moellendorffii* | planta | planta | 75 | 273 | ? | NOVEL | transgenesis | medio |
| 19 | XP_020405652.1 | *Zea mays* | planta | planta | 74 | 273 | ? | NOVEL | transgenesis | medio |
| 20 | XP_006416732.1 | *Eutrema salsugineum* | planta | planta | 72 | 363 | ? | NOVEL | transgenesis | medio |
| 21 | XP_002968645.2 | *Selaginella moellendorffii* | planta | planta | 70 | 338 | ? | NOVEL | transgenesis | medio |
| 22 | XP_021303416.1 | *Sorghum bicolor* | planta | planta | 70 | 318 | ? | NOVEL | transgenesis | medio |
| 23 | XP_002465909.2 | *Sorghum bicolor* | planta | planta | 68 | 418 | ? | NOVEL | transgenesis | medio |
| 24 | XP_035821990.1 | *Zea mays* | planta | planta | 65 | 318 | ? | NOVEL | transgenesis | medio |
| 25 | XP_024518211.1 | *Selaginella moellendorffii* | planta | planta | 60 | 318 | ? | NOVEL | transgenesis | medio |

### Top microorganismos

| #| Accession| Donante| Tipo| Grupo| Score| Pre-score| Soporte| Europe PMC| Estrategia| Riesgo|
|---:|---|---|---|---|---:|---:|---:|---|---|---|
| 1 | XP_024772657.1 | *Trichoderma harzianum* | hongo | microorganismo | 70 | 318 | ? | NOVEL | transgenesis | medio |
| 2 | XP_024772748.1 | *Trichoderma harzianum* | hongo | microorganismo | 65 | 318 | ? | NOVEL | transgenesis | medio |
| 3 | XP_024778146.1 | *Trichoderma harzianum* | hongo | microorganismo | 60 | 318 | ? | NOVEL | transgenesis | medio |
| 4 | WP_205251170.1 | *Halobacterium salinarum* | arquea | microorganismo | 60 | 298 | ? | NOVEL | transgenesis | medio |
| 5 | XP_024773116.1 | *Trichoderma harzianum* | hongo | microorganismo | 60 | 273 | ? | NOVEL | transgenesis | medio |

## Candidatos para transferencia (orden combinado)

| # | Accession | Donante | Score | Soporte | Europe PMC | Estrategia | Riesgo |
|---|---|---|---|---|---|---|---|
| 1 | CAD36023.1 | Craterostigma plantagineum | 93 | 35/100 | NOVEL | transgenesis | medio |
| 2 | AAZ72653.1 | Craterostigma plantagineum | 92 | 35/100 | NOVEL | edicion_genica | medio |
| 3 | XP_025876545.2 | Oryza sativa | 90 | 35/100 | NOVEL | edicion_genica | bajo |
| 4 | XP_006392370.1 | Eutrema salsugineum | 88 | 55/100 | NOVEL | transgenesis | medio |
| 5 | AAZ72654.1 | Craterostigma plantagineum | 88 | 35/100 | NOVEL | edicion_genica | medio |
| 6 | XP_002467609.2 | Sorghum bicolor | 85 | 35/100 | NOVEL | edicion_genica | bajo |
| 7 | XP_024006402.1 | Eutrema salsugineum | 85 | 15/100 | NOVEL | edicion_genica | bajo |
| 8 | XP_006400210.1 | Eutrema salsugineum | 85 | 55/100 | NOVEL | edicion_genica | bajo |
| 9 | AAN34791.1 | Xerophyta viscosa | 85 | 0/100 | NOVEL | edicion_genica | bajo |
| 10 | XP_024540135.1 | Selaginella moellendorffii | 82 | 0/100 | NOVEL | edicion_genica | bajo |
| 11 | AAP22171.1 | Xerophyta viscosa | 82 | 25/100 | 1 menciones | transgenesis | medio |
| 12 | NP_001130206.1 | Zea mays | 80 | 35/100 | NOVEL | transgenesis | medio |
| 13 | XP_035815535.1 | Zea mays | 80 | 35/100 | NOVEL | transgenesis | medio |
| 14 | XP_015612592.1 | Oryza sativa | 78 | 35/100 | NOVEL | transgenesis | medio |
| 15 | XP_066161079.1 | Oryza sativa | 78 | 35/100 | NOVEL | transgenesis | medio |
| 16 | XP_002451782.1 | Sorghum bicolor | 78 | 75/100 | NOVEL | transgenesis | medio |
| 17 | XP_002459355.1 | Sorghum bicolor | 76 | 75/100 | NOVEL | transgenesis | medio |
| 18 | XP_002966448.1 | Selaginella moellendorffii | 75 | 15/100 | NOVEL | transgenesis | medio |
| 19 | XP_020405652.1 | Zea mays | 74 | 35/100 | NOVEL | transgenesis | medio |
| 20 | XP_006416732.1 | Eutrema salsugineum | 72 | 55/100 | NOVEL | transgenesis | medio |
| 21 | XP_002968645.2 | Selaginella moellendorffii | 70 | 40/100 | NOVEL | transgenesis | medio |
| 22 | XP_021303416.1 | Sorghum bicolor | 70 | 75/100 | NOVEL | transgenesis | medio |
| 23 | XP_002465909.2 | Sorghum bicolor | 68 | 75/100 | NOVEL | transgenesis | medio |
| 24 | XP_035821990.1 | Zea mays | 65 | 35/100 | NOVEL | transgenesis | medio |
| 25 | XP_024518211.1 | Selaginella moellendorffii | 60 | 0/100 | NOVEL | transgenesis | medio |
| 26 | XP_024772657.1 | Trichoderma harzianum | 70 | 0/100 | NOVEL | transgenesis | medio |
| 27 | XP_024772748.1 | Trichoderma harzianum | 65 | 0/100 | NOVEL | transgenesis | medio |
| 28 | XP_024778146.1 | Trichoderma harzianum | 60 | 0/100 | NOVEL | transgenesis | medio |
| 29 | WP_205251170.1 | Halobacterium salinarum | 60 | 0/100 | NOVEL | transgenesis | medio |
| 30 | XP_024773116.1 | Trichoderma harzianum | 60 | 0/100 | NOVEL | transgenesis | medio |

## Detalles de candidatos

### 1. CAD36023.1
- **Especie donante:** Craterostigma plantagineum
- **Score de transferencia:** 93
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 13 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Factor de transcripción R18 de Craterostigma plantagineum activa redes de genes asociados a la tolerancia a la desecación, incluyendo proteínas LEA, vías de biosíntesis de osmoprotectores (prolina, trehalosa) y señalización ABA, reforzando la capacidad de la planta receptora para mantener la integridad celular bajo déficit hídrico.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** Factor R18 es un regulador específico de Craterostigma; no se ha identificado un ortólogo directo en Fragaria vesca, por lo que su introducción requeriría transgénesis. El riesgo es medio porque la sobreexpresión de un TF ajeno puede alterar redes de genes no previstas.
- **Promotor:** promotor inducible por sequía (pRD29A) o CaMV 35S si se desea expresión constitutiva moderada
- **Localizacion:** núcleo (añadir señal NLS al C‑terminus)
- **Codon optimization:** si
- **Riesgos potenciales:** Regulación ectópica de genes nativos de Fragaria vesca que pueden afectar el desarrollo y la producción de frutos., Posible alteración del balance hormonal (ABA, auxinas) provocando retraso en la floración o crecimiento., Carga metabólica por sobreexpresión de proteínas de respuesta al estrés.

### 2. AAZ72653.1
- **Especie donante:** Craterostigma plantagineum
- **Score de transferencia:** 92
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 13 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Factor de transcripción bZIP que regula genes sensibles a ABA, promueve la síntesis de osmoprotectores (prolina, azúcares), activa vías de antioxidantes y refuerza la arquitectura de la cutícula, confiriendo tolerancia a la sequía.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** medio
- **Justificacion:** Los bZIP son una familia amplia y existen varios miembros en F. vesca con alta similitud. Se puede editar el regulador endógeno (p.ej., mediante edición de promotores) para aumentar su actividad. El riesgo es medio por posibles efectos pleiotrópicos en la respuesta ABA.
- **Promotor:** promotor inducible por ABA (pABRC) o CaMV 35S de bajo nivel para minimizar efectos pleiotrópicos
- **Localizacion:** núcleo (señal NLS incorporada)
- **Codon optimization:** si
- **Riesgos potenciales:** Posible sobreexpresión de rutas de estrés que reduzca el crecimiento y rendimiento bajo condiciones no secas., Interferencia con la regulación endógena de bZIP en F. vesca, pudiendo alterar procesos de desarrollo floral.

### 3. XP_025876545.2
- **Especie donante:** Oryza sativa
- **Score de transferencia:** 90
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Glutatión S‑transferasa GSTU6 de Oryza sativa cataliza la conjugación de glutatión a metabolitos reactivos generados por estrés oxidativo durante la sequía, mejorando la detoxificación de peróxidos y manteniendo la homeostasis redox en tejidos fotosintéticos.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** GSTU6 pertenece a la subfamilia GSTU, presente en F. vesca (p.ej., FvGSTU1). La edición de la versión nativa para elevar su expresión es factible y con bajo riesgo, ya que los GST son enzimas de detoxificación bien conservadas.
- **Promotor:** promotor constitutivo CaMV 35S o promotor foliar (pRBCS) para alta expresión en tejidos fotosintéticos
- **Localizacion:** citosol (GSTU6 es citosólico); opción de añadir péptido de señal a cloroplasto si se desea detoxificación directa en el organelo
- **Codon optimization:** si
- **Riesgos potenciales:** Acumulación de conjugados de glutatión que podrían interferir con rutas metabólicas secundarias., Posible competencia con GSTs endógenas de Fragaria vesca, alterando la regulación natural del sistema antioxidante.

### 4. XP_006392370.1
- **Especie donante:** Eutrema salsugineum
- **Score de transferencia:** 88
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: V4KUZ8_EUTSA, V4LE23_EUTSA, V4M9J2_EUTSA, V4MFX4_EUTSA, V4KDT6_EUTSA
- **GEO:** 3 datasets de expresion disponibles
- **Soporte multi-fuente:** 55/100 (interacciones, expresion)
- **Mecanismo:** Probable elongation factor 1‑gamma 2 con dominios GST de Eutrema salsugineum actúa como GST no‑clásico, proporcionando capacidad de unión a glutatión y detoxificación de especies reactivas de oxígeno, lo que reduce el daño celular bajo déficit hídrico.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** La combinación de EF1‑gamma2 con dominios GST es poco común en rosáceas; no se ha encontrado un ortólogo claro en F. vesca. Su introducción como transgén puede aportar actividad GST, pero el riesgo es medio por posible interferencia con la traducción y la homeostasis de glutatión.
- **Promotor:** promotor constitutivo CaMV 35S o promotor de raíz (pRCc) si se busca protección en sistemas vasculares
- **Localizacion:** citosol (EF1‑γ2 con dominios GST actúa en el citosol)
- **Codon optimization:** si
- **Riesgos potenciales:** Posible interferencia con la maquinaria de traducción al sobreexpresar un factor de elongación., Riesgo de desequilibrio en la reserva de glutatión libre.

### 5. AAZ72654.1
- **Especie donante:** Craterostigma plantagineum
- **Score de transferencia:** 88
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 13 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Factor de transcripción bZIP1 que activa la vía de señalización ABA y regula genes de respuesta al estrés hídrico (osmoprotectantes, proteínas de choque, cierre estomático).
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** medio
- **Justificacion:** bZIP1 tiene varios paralogos en F. vesca. La edición del regulador endógeno (p.ej., activación de cis‑elementos) es viable; sin embargo, la modulación de la señal ABA puede producir efectos secundarios en el desarrollo, de ahí un riesgo medio.
- **Promotor:** promotor inducible por sequía/ABA (pRD29A) o CaMV 35S de bajo nivel
- **Localizacion:** núcleo (añadir NLS)
- **Codon optimization:** si
- **Riesgos potenciales:** Posibles efectos pleiotrópicos sobre desarrollo y floración por regulación de genes no‑deseados., Alteración del balance hormonal que podría reducir rendimiento bajo condiciones no estresantes.

### 6. XP_002467609.2
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 85
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Aumenta la capacidad antioxidante de la planta mediante la conjugación de glutatión a especies reactivas de oxígeno (ROS) y a metabolitos tóxicos generados durante el estrés hídrico; contribuye a la regulación de la señalización de ácido abscísico (ABA) y a la protección de proteínas y membranas.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** Los GST de tipo U están ampliamente conservados; F. vesca posee genes homólogos con >80 % de identidad. Mejorar su expresión mediante edición presenta bajo riesgo, pues la función antioxidante es esencial y bien tolerada.
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Posible sobrecarga del pool de glutatión, afectando otras rutas metabólicas., Interacción no prevista con GST endógenos de F. vesca que podría alterar la homeostasis redox.

### 7. XP_024006402.1
- **Especie donante:** Eutrema salsugineum
- **Score de transferencia:** 85
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 3 datasets de expresion disponibles
- **Soporte multi-fuente:** 15/100 (expresion)
- **Mecanismo:** GST F14 de Eutrema salsugineum aumenta la capacidad de conjugación de glutatión, detoxificando especies reactivas de oxígeno y productos de peroxidación lipídica generados durante la sequía; además modula la señalización hormonal (ABA) favoreciendo la retención de agua.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** GSTF14 es parte de la familia F de GST, presente en F. vesca. La edición del gen nativo para aumentar su actividad es segura y de bajo riesgo.
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Posible agotamiento de la reserva de glutatión si se sobreexpresa, Interferencia con la regulación endógena de GSTs de Fragaria vesca

### 8. XP_006400210.1
- **Especie donante:** Eutrema salsugineum
- **Score de transferencia:** 85
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: V4KNT4_EUTSA, V4N4G9_EUTSA, V4M0Q0_EUTSA, V4LRU6_EUTSA, V4MMF1_EUTSA
- **GEO:** 3 datasets de expresion disponibles
- **Soporte multi-fuente:** 55/100 (interacciones, expresion)
- **Mecanismo:** Glutatión S‑transferasa cloroplástica que detoxifica especies reactivas de oxígeno generadas durante la sequía mediante conjugación con glutatión, manteniendo la redox celular.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** Los GST cloroplásticos son conservados en rosáceas; existe un ortólogo en F. vesca con alta similitud. Su mejora mediante edición presenta bajo riesgo.
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Consumo excesivo de glutatión libre, pudiendo comprometer otras vías antioxidantes., Posible interacción con la vía de síntesis de glutatión de la fresa.

### 9. AAN34791.1
- **Especie donante:** Xerophyta viscosa
- **Score de transferencia:** 85
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 0/100 ()
- **Mecanismo:** Proteína HSP90 (Grp94) actúa como chaperona que estabiliza proteínas desnaturalizadas durante el estrés hídrico, mantiene la actividad de enzimas clave y facilita la señalización de receptores hormonales (p. ej., ABA).
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** HSP90/Grp94 es una chaperona esencial y altamente conservada; F. vesca posee varios genes HSP90. La edición para reforzar su expresión es de bajo riesgo.
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Expresión elevada de HSP90 puede consumir ATP y afectar la homeostasis energética., Riesgo de interacción no específica con proteínas nativas, generando posibles efectos dominantes negativos.

### 10. XP_024540135.1
- **Especie donante:** Selaginella moellendorffii
- **Score de transferencia:** 82
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 0/100 ()
- **Mecanismo:** Glutatión S‑transferasa 2 de Selaginella moellendorffii facilita la conjugación de glutatión a compuestos tóxicos y la eliminación de peróxidos, contribuyendo a la protección de la membrana y la fotosíntesis durante la sequía.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** GST2 es una clase de GST presente en F. vesca. La manipulación del gen nativo para mayor actividad antioxidante es segura y con bajo riesgo.
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Incompatibilidad parcial de señalización de localización subcelular (p.ej., citosol vs cloroplasto)., Posible sobrecarga del ciclo de glutatión.

### 11. AAP22171.1
- **Especie donante:** Xerophyta viscosa
- **Score de transferencia:** 82
- **Europe PMC:** 1 menciones
  - A molecular physiological review of vegetative desiccation tolerance in the resurrection plant Xerophyta viscosa (Baker) (2015)
- **STRING:** 0 interacciones
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 25/100 (literatura)
- **Mecanismo:** Dehidrina (proteína LEA) que se acumula en el citoplasma y en membranas, estabilizando estructuras celulares y previniendo la agregación de proteínas durante la desecación.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Sobre‑expresión podría modificar la osmolaridad intracelular y afectar la absorción de agua bajo riego normal.

### 12. NP_001130206.1
- **Especie donante:** Zea mays
- **Score de transferencia:** 80
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Detoxificación de compuestos oxidativos y de productos de peroxidación lipídica mediante actividad GST; mejora la respuesta al ABA y favorece la acumulación de osmólitos que mantienen la turgencia celular bajo déficit hídrico.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Expresión alta puede generar consumo energético excesivo., Riesgo de formación de conjugados de glutatión que interfieran con vías metabólicas secundarias.

### 13. XP_035815535.1
- **Especie donante:** Zea mays
- **Score de transferencia:** 80
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Glutatión deshidroascorbato reductasa que regenera ascorbato a partir de su forma oxidada, reforzando la capacidad antioxidante bajo estrés hídrico.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Desbalance en la relación ascorbato/ácido dehidroascorbico., Posible carga metabólica adicional en cloroplastos.

### 14. XP_015612592.1
- **Especie donante:** Oryza sativa
- **Score de transferencia:** 78
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** GSTU1 de arroz está implicada en la eliminación de peróxidos y en la modulación de la señalización de ABA, lo que reduce el daño celular durante sequías prolongadas.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Posible incompatibilidad con reguladores de GST propios de F. vesca., Riesgo de inmunogenicidad si la proteína es altamente divergente.

### 15. XP_066161079.1
- **Especie donante:** Oryza sativa
- **Score de transferencia:** 78
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Glutatión S‑transferasa (GSTU6) de arroz cataliza la conjugación de glutatión a compuestos reactivos y detoxifica especies de oxígeno reactivo (ROS) acumuladas bajo déficit hídrico, mejorando la capacidad antioxidante de la planta.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Acumulación de conjugados de glutatión que podrían interferir con el metabolismo secundario., Posible agotamiento de glutatión libre, comprometiendo otras vías de defensa.

### 16. XP_002451782.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 78
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: C5WWP8_SORBI, C5X4T4_SORBI, C5XE07_SORBI, SORBI_3K024000, A0A194YJY9
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 75/100 (interacciones, expresion)
- **Mecanismo:** Glutatión S‑transferasa que participa en la detoxificación de compuestos tóxicos y en la mitigación del estrés oxidativo asociado a la sequía.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Riesgo de agotamiento de glutatión si la expresión es muy alta., Posible interferencia con rutas metabólicas de fenilpropanoides en la fresa.

### 17. XP_002459355.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 76
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: C5YYX3_SORBI, A0A1Z5R0E4, A0A194YI68, C5X3B9_SORBI, A0A1B6PLA9
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 75/100 (interacciones, expresion)
- **Mecanismo:** GST de Sorghum bicolor con actividad amplia contra peróxidos y herbicidas; aumenta la capacidad de escudo antioxidante y protege membranas celulares durante la sequía.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Expresión heteróloga puede generar productos de conjugación no nativos que alteren la calidad del fruto., Riesgo de interacción con vías de detoxificación propias, provocando desequilibrios metabólicos.

### 18. XP_002966448.1
- **Especie donante:** Selaginella moellendorffii
- **Score de transferencia:** 75
- **Europe PMC:** NOVEL
- **STRING:** 3 interacciones
  - Partners: D8RPJ6_SELML, D8SMA1_SELML, DHAR1
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 15/100 (interacciones)
- **Mecanismo:** GST U19 de Selaginella moellendorffii provee actividad de transferencia de glutatión que neutraliza ROS y compuestos tóxicos acumulados bajo déficit hídrico, mejorando la estabilidad de membranas y la homeostasis redox.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Consumo elevado de glutatión y posibles efectos en la síntesis de compuestos secundarios, Riesgo de interacción no deseada con rutas de metabolismo de fenilpropanoides propias de la fresa

### 19. XP_020405652.1
- **Especie donante:** Zea mays
- **Score de transferencia:** 74
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** GST8 de maíz, similar a otras GST de clase Tau, participa en la eliminación de ROS y en la regulación de la señalización de hormonas de estrés, contribuyendo a la tolerancia a la sequía.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Posible competencia con GST nativas de F. vesca, reduciendo la eficiencia global del sistema antioxidante., Expresión excesiva puede afectar la síntesis de compuestos fenólicos.

### 20. XP_006416732.1
- **Especie donante:** Eutrema salsugineum
- **Score de transferencia:** 72
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: V4M5D0_EUTSA, V4M8P6_EUTSA, V4M8Z3_EUTSA, V4LPA0_EUTSA, V4KAW8_EUTSA
- **GEO:** 3 datasets de expresion disponibles
- **Soporte multi-fuente:** 55/100 (interacciones, expresion)
- **Mecanismo:** Glutatión S‑transferasa U25 que aumenta la capacidad de detoxificación de especies reactivas de oxígeno y de compuestos electófilos generados durante el estrés por sequía, manteniendo la homeostasis redox.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Consumo elevado de glutatión libre, pudiendo limitar otras rutas antioxidantes., Posible conjugación de metabolitos esenciales, alterando vías metabólicas secundarias.

### 21. XP_002968645.2
- **Especie donante:** Selaginella moellendorffii
- **Score de transferencia:** 70
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: D8SC66_SELML, D8S946_SELML, DHAR1, D8S7N0_SELML, D8T402_SELML
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 40/100 (interacciones)
- **Mecanismo:** GST de Selaginella ayuda a mantener la redox celular bajo estrés deshidratante y puede participar en la síntesis de compuestos protectores como flavonoides.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Dominio adicional de glutatión reductasa podría interferir con rutas nativas., Expresión en tejido frutal podría alterar el perfil de metabolitos secundarios.

### 22. XP_021303416.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 70
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: A0A1Z5R0E4, A0A194YI68, C5X3B9_SORBI, C5YYX3_SORBI, A0A1B6PLA9
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 75/100 (interacciones, expresion)
- **Mecanismo:** Proteína homóloga IN2‑1 B‑like de Sorghum bicolor contiene dominios GST que aumentan la capacidad de detoxificación de metabolitos de estrés y regulan la señalización de estrés abiótico mediante conjugación de glutatión.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Posible desbalance en la red de GSTs nativas, Carga metabólica adicional por síntesis de la proteína

### 23. XP_002465909.2
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 68
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: A0A1B6QR57, C5XZD3_SORBI, A0A1Z5R0E4, C5X3B9_SORBI, A0A194YU12
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 75/100 (interacciones, expresion)
- **Mecanismo:** Glutatión S‑transferasa F11 que participa en la eliminación de peróxidos y compuestos tóxicos generados por estrés hídrico, reforzando la defensa antioxidante.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Desbalance del pool de glutatión si la expresión es muy alta., Riesgo de interacción con rutas de metabolismo de fenilpropanoides propias de la fresa.

### 24. XP_035821990.1
- **Especie donante:** Zea mays
- **Score de transferencia:** 65
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Glutatión transferasa 7 que cataliza la conjugación de glutatión a metabolitos reactivos, reduciendo el daño oxidativo asociado a la sequía.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Posible agotamiento de glutatión bajo estrés prolongado., Efectos desconocidos sobre la síntesis de compuestos secundarios de la fresa.

### 25. XP_024518211.1
- **Especie donante:** Selaginella moellendorffii
- **Score de transferencia:** 60
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 0/100 ()
- **Mecanismo:** Glutatión S‑transferasa 2 que mejora la capacidad de detoxificación de especies reactivas y compuestos de estrés, contribuyendo a la tolerancia a la sequía.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Riesgo moderado de interferencia con rutas metabólicas propias de la planta., Posible carga metabólica por sobreexpresión sostenida.

### 26. XP_024772657.1
- **Especie donante:** Trichoderma harzianum
- **Score de transferencia:** 70
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 0/100 ()
- **Mecanismo:** GST hipotético de Trichoderma harzianum; aunque de origen fúngico, los GST de esta especie pueden aportar actividad de detoxificación de ROS y de metabolitos de estrés, mejorando la resiliencia hídrica.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Riesgo de incorrecto plegamiento o falta de cofactores en células vegetales., Posible respuesta inmunológica del huésped contra proteína fúngica.

### 27. XP_024772748.1
- **Especie donante:** Trichoderma harzianum
- **Score de transferencia:** 65
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 0/100 ()
- **Mecanismo:** GST hipotética de Trichoderma harzianum posee dominios GST que pueden aportar actividad de detoxificación de ROS y compuestos fenólicos, mejorando la tolerancia al estrés oxidativo asociado a la sequía.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Expresión en planta puede requerir adaptación de señal de localización (p.ej., secreción vs citosol)., Riesgo de respuesta inmunológica o alergenicidad por proteína fúngica.

### 28. XP_024778146.1
- **Especie donante:** Trichoderma harzianum
- **Score de transferencia:** 60
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 0/100 ()
- **Mecanismo:** GST fúngico puede aportar actividad de detoxificación de compuestos fenólicos y ROS, mejorando la tolerancia al estrés oxidativo asociado a la sequía.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Posible incorrecta plegadura o glicosilación en planta., Riesgo de activar respuestas de defensa contra hongos.

### 29. WP_205251170.1
- **Especie donante:** Halobacterium salinarum
- **Score de transferencia:** 60
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 0/100 ()
- **Mecanismo:** Glutatión S‑transferasa de origen arqueal que podría aportar actividad detoxificante frente a ROS, aunque su cinética y especificidad difieren de las GST vegetales.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Posible incorrecta plegadura o falta de cofactores en células vegetales., Riesgo inmunogénico o toxicidad por productos intermedios no nativos.

### 30. XP_024773116.1
- **Especie donante:** Trichoderma harzianum
- **Score de transferencia:** 60
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 0/100 ()
- **Mecanismo:** Proteína hipotética con dominios GST de Trichoderma harzianum puede aportar actividad de conjugación de glutatión que protege contra el daño oxidativo inducido por sequía y potencialmente secreta compuestos protectores al entorno radicular.
- **Tiene ortologo en receptora:** no_se
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** 
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Posible glicosilación o plegamiento incorrecto en células vegetales, Riesgo de respuesta inmunológica o alergenicidad

## Genes conocidos en receptora (Brazo A)

- **LOC105349251**: heat shock 70 kDa protein-like
- **LOC101312933**: heat shock cognate 70 kDa protein-like
- **LOC101312639**: heat shock cognate 70 kDa protein-like
- **LOC101297476**: heat shock cognate 70 kDa protein 2-like
- **LOC101294000**: heat shock 70 kDa protein
- **LOC101291669**: heat shock cognate 70 kDa protein 2-like
- **LOC101291093**: heat shock cognate 70 kDa protein 2
- **LOC101314995**: 18.1 kDa class I heat shock protein-like
- **LOC101314220**: 18.1 kDa class I heat shock protein-like
- **LOC101313245**: 15.7 kDa heat shock protein, peroxisomal

> La seleccion de donantes fue orquestada por el LLM. Los candidatos requieren validacion experimental antes de su uso.