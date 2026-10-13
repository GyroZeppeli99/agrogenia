# Busqueda Trans-especie Orquestada · AgroGenIA V4.4

- **Fecha:** 2026-10-11 03:43
- **Estrategia de seleccion:** B (diversidad equilibrada)
- **Rasgo objetivo:** tolerancia a sequia
- **Especie receptora:** *Manihot esculenta*
- **Base Pfam:** sub-base:sequia
- **Modo Pfam:** auto
- **Especies donantes validas:** 5
- **Especies descartadas:** 0
- **Candidatos priorizados:** 10

## Especies donantes sugeridas por el LLM

### Aceptadas (con genoma disponible)

- **Xerophyta viscosa** (tax_id 90708)
  - Tipo: planta
  - Adaptacion: Resurrection plant que sobrevive deshidratación extrema mediante acumulación de LEA y protección antioxidante.
  - Genes clave: XvLEA14, XvDREB2A, XvNCED3
- **Sorghum bicolor** (tax_id 4558)
  - Tipo: planta
  - Adaptacion: Cereal de sabana con alta tolerancia a sequía; regula la apertura estomática y la acumulación de osmólitos.
  - Genes clave: SbNAC111, SbPP2C68, SbDREB2A
- **Bacillus subtilis** (tax_id 1423)
  - Tipo: bacteria
  - Adaptacion: Productor de ACC desaminasa que reduce el etileno en raíces y promueve crecimiento bajo estrés hídrico.
  - Genes clave: acdS, cspB, otsA
- **Pseudomonas fluorescens** (tax_id 294)
  - Tipo: bacteria
  - Adaptacion: Rhizobacteria plantaria que sintetiza trehalosa y exopolímeros, mejorando la retención de agua en la zona radicular.
  - Genes clave: treS, exsA, gltA
- **Serendipita indica** (tax_id 65672)
  - Tipo: hongo
  - Adaptacion: Micorriza endofítica que aumenta la capacidad de la planta para acumular proline y trehalosa bajo déficit hídrico.
  - Genes clave: SiTPS1, SiP5CS, SiHSP70

## Candidatos para transferencia

| # | Accession | Donante | Score | Soporte | Europe PMC | Estrategia | Riesgo |
|---|---|---|---|---|---|---|---|
| 1 | AAP22171.1 | Xerophyta viscosa | 90 | 25/100 | 1 menc. | edicion_genica | bajo |
| 2 | XP_021305765.1 | Sorghum bicolor | 80 | 35/100 | NOVEL | edicion_genica | bajo |
| 3 | XP_021305764.1 | Sorghum bicolor | 80 | 75/100 | NOVEL | edicion_genica | bajo |
| 4 | XP_021306141.1 | Sorghum bicolor | 70 | 75/100 | NOVEL | edicion_genica | medio |
| 5 | XP_021305912.1 | Sorghum bicolor | 65 | 75/100 | NOVEL | edicion_genica | bajo |
| 6 | XP_021305891.1 | Sorghum bicolor | 65 | 75/100 | NOVEL | edicion_genica | bajo |
| 7 | XP_021306047.1 | Sorghum bicolor | 60 | 35/100 | NOVEL | edicion_genica | bajo |
| 8 | XP_021306046.1 | Sorghum bicolor | 60 | 60/100 | NOVEL | edicion_genica | bajo |
| 9 | NP_001410932.1 | Sorghum bicolor | 55 | 35/100 | NOVEL | transgenesis | medio |
| 10 | YP_899413.1 | Sorghum bicolor | 45 | 75/100 | NOVEL | edicion_genica | bajo |

## Detalles de candidatos

### 1. AAP22171.1
- **Especie donante:** Xerophyta viscosa
- **Score de transferencia:** 90
- **Europe PMC:** 1 menciones
  - A molecular physiological review of vegetative desiccation tolerance in the resurrection plant Xerophyta viscosa (Baker) (2015)
- **STRING:** 0 interacciones
- **GEO:** 0 datasets de expresion disponibles
- **Soporte multi-fuente:** 25/100 (literatura)
- **Mecanismo:** Proteína de tipo LEA (dehidrina) que se acumula durante la sequía; protege membranas y proteínas, estabiliza estructuras celulares y actúa como antioxidante, reduciendo el daño por estrés hídrico.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** Cassava posee múltiples genes LEA; la edición del promotor o aumento de copia puede mejorar la tolerancia sin introducir proteínas extrañas.
- **Promotor:** inducible_drought_RD29A
- **Localizacion:** citosol
- **Codon optimization:** si
- **Riesgos potenciales:** Posible interferencia con la regulación natural de deshidrinas del receptor, lo que podría alterar la germinación o el desarrollo bajo condiciones no estresantes., Acumulación excesiva puede afectar la osmolaridad celular y el crecimiento.

### 2. XP_021305765.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 80
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Isoforma paralela de la galactinol‑sucrose galactosiltransferasa con la misma función de producción de osmoprotectores rafinosas.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** Genes de galactinol‑sucrose galactosiltransferasa (raffinosa synthase) están presentes en Manihot; su sobreexpresión es una vía segura para elevar osmoprotectores.
- **Promotor:** constitutivo_CaMV35S
- **Localizacion:** citosol
- **Codon optimization:** si
- **Riesgos potenciales:** Mismos riesgos que la isoforma XP_021305764.1., Posible redundancia que genere sobreexpresión y efectos negativos en el metabolismo de azúcares.

### 3. XP_021305764.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 80
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: C5X1V2_SORBI, C5X6A1_SORBI, A0A1B6PFZ0, A0A1W0VUE2, C5Y7K3_SORBI
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 75/100 (interacciones, expresion)
- **Mecanismo:** Galactinol‑sucrose galactosiltransferasa que sintetiza galactinol y rafinosa, osmoprotectores de la familia de los oligosacáridos de rafinosa que estabilizan proteínas y membranas bajo déficit hídrico.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** Otra isoforma de la misma enzima; la cassava tiene ortólogos funcionales, por lo que la edición puntual es suficiente.
- **Promotor:** inducible_drought_RD29A
- **Localizacion:** citosol
- **Codon optimization:** si
- **Riesgos potenciales:** Desvío de flujos de carbono hacia la síntesis de rafinosa puede reducir el rendimiento de almidón en la raíz de yuca., Alteración del perfil de azúcares podría afectar la palatabilidad o la resistencia a patógenos.

### 4. XP_021306141.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 70
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: C5X7D7_SORBI, C5XSB8_SORBI, C5X2I5_SORBI, C5Z7L0_SORBI, C5YXJ4_SORBI
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 75/100 (interacciones, expresion)
- **Mecanismo:** Quinasa receptora tipo PERK con dominio rico en prolina; percibe señales extracelulares de estrés y activa cascadas de fosforilación que inducen genes de tolerancia a sequía y refuerzan la pared celular.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** medio
- **Justificacion:** Receptores tipo PERK existen en cassava, pero modificar una quinasa de señalización puede generar efectos pleiotrópicos en desarrollo y defensa.
- **Promotor:** inducible_drought_RD29A
- **Localizacion:** membrana_plasmática
- **Codon optimization:** si
- **Riesgos potenciales:** Activación constitutiva puede provocar crecimiento reducido o alteraciones en la arquitectura de la planta., Posible aumento de susceptibilidad a ciertos patógenos si la señalización de la pared celular se modifica.

### 5. XP_021305912.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 65
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: C5WVD3_SORBI, C5X4H2_SORBI, A0A1B6QIR3, C5YU58_SORBI, A0A194YRT0
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 75/100 (interacciones, expresion)
- **Mecanismo:** Proteína chaperona DnaJ mitocondrial que ayuda al plegamiento de proteínas bajo estrés oxidativo, manteniendo la funcionalidad de la cadena respiratoria durante la sequía.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** Chaperonas DnaJ mitocondriales son conservadas; su regulación mediante edición es poco invasiva.
- **Promotor:** constitutivo_CaMV35S
- **Localizacion:** mitocondria
- **Codon optimization:** si
- **Riesgos potenciales:** Sobreexpresión puede desbalancear la homeostasis de proteínas mitocondriales y afectar la respiración normal., Riesgo de interacción con proteínas nativas del receptor que no están adaptadas a niveles altos de DnaJ.

### 6. XP_021305891.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 65
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: A0A1Z5S8M8, C5Z1A2_SORBI, C5XSZ9_SORBI, C5YKV9_SORBI, A0A1B6QCD3
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 75/100 (interacciones, expresion)
- **Mecanismo:** Isoforma X2 de la misma chaperona DnaJ mitocondrial con función idéntica a la isoforma X1.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** Isoforma adicional de DnaJ ya presente en la planta, por lo que la edición del gen nativo es adecuada.
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Mismos riesgos que la isoforma X1., Posible carga metabólica adicional por expresión de dos isoformas similares.

### 7. XP_021306047.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 60
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Transferasa O‑galactosiltransferasa de hidroxi‑prolina que glicosila extensinas, reforzando la pared celular y reduciendo la pérdida de agua.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** O‑galactosiltransferasas de extensinas están anotadas en el genoma de cassava; su aumento de expresión refuerza la pared sin toxicidad.
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Modificación de la composición de la pared celular puede alterar la interacción con micorrizas y patógenos., Posible impacto negativo en la flexibilidad del tejido, afectando el desarrollo de tubérculos.

### 8. XP_021306046.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 60
- **Europe PMC:** NOVEL
- **STRING:** 5 interacciones
  - Partners: A0A1Z5R3D6, C5WPE2_SORBI, A0A1Z5R766, A0A1Z5R7Q0, A0A1Z5R7Z8
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 60/100 (interacciones, expresion)
- **Mecanismo:** Isoforma X1 de la misma O‑galactosiltransferasa con función idéntica a la isoforma X2.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** Isoforma X1 de la misma transferasa tiene ortólogo en cassava; la edición del regulador natural minimiza riesgos.
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Mismos riesgos que la isoforma X2., Riesgo de sobrecarga de la vía de glicosilación.

### 9. NP_001410932.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 55
- **Europe PMC:** NOVEL
- **STRING:** 0 interacciones
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 35/100 (expresion)
- **Mecanismo:** Tirosina N‑monooxigenasa que produce compuestos fenólicos y alcaloides que actúan como antioxidantes y pueden mejorar la tolerancia a estrés abiótico.
- **Tiene ortologo en receptora:** no
- **Estrategia:** transgenesis
- **Riesgo de compatibilidad:** medio
- **Justificacion:** Cassava carece de tirosina N‑monooxigenasa típica de rutas de alcaloides; su introducción puede generar metabolitos no habituales, requiriendo evaluación de toxicidad.
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Producción de metabolitos secundarios puede generar compuestos tóxicos o anti‑nutricionales para humanos o animales., Posible interferencia con rutas metabólicas nativas de fenilpropanoides.

### 10. YP_899413.1
- **Especie donante:** Sorghum bicolor
- **Score de transferencia:** 45
- **Europe PMC:** NOVEL
- **STRING:** 10 interacciones
  - Partners: atpF, atpA, atpB, atpI, atpH
- **GEO:** 20 datasets de expresion disponibles
- **Soporte multi-fuente:** 75/100 (interacciones, expresion)
- **Mecanismo:** Subunidad épsilon del ATP sintasa CF1 cloroplástico; mejora la eficiencia de la fotofosforilación bajo limitación de agua, manteniendo la producción de ATP.
- **Tiene ortologo en receptora:** si
- **Estrategia:** edicion_genica
- **Riesgo de compatibilidad:** bajo
- **Justificacion:** La subunidad epsilon de la ATP sintasa es altamente conservada; la edición del gen nativo para mejorar su expresión es segura.
- **Promotor:** 
- **Localizacion:** 
- **Codon optimization:** 
- **Riesgos potenciales:** Integración inadecuada puede desbalancear el complejo ATP sintasa y generar estrés fotooxidativo., Posible incompatibilidad con los reguladores nativos del receptor.

## Genes conocidos en receptora (Brazo A)

- **LOC110615233**: catalase isozyme 2
- **LOC110609185**: heat shock cognate 70 kDa protein 2
- **LOC110628482**: heat shock protein 90-6, mitochondrial
- **LOC110610426**: heat shock 70 kDa protein 16
- **LOC110626448**: 17.4 kDa class III heat shock protein
- **LOC110624838**: heat shock 70 kDa protein, mitochondrial
- **LOC110619268**: heat shock 70 kDa protein, mitochondrial
- **LOC110617327**: heat shock protein 90-5, chloroplastic
- **LOC110603605**: heat shock protein 83
- **LOC110599687**: heat shock protein 90-5, chloroplastic

> La seleccion de donantes fue orquestada por el LLM. Los candidatos requieren validacion experimental antes de su uso.