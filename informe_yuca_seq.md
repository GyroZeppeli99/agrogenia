# Informe AgroGenIA (v2, enriquecido)

- **Fecha:** 2026-09-30 02:52
- **Especie:** *Manihot esculenta*
- **Rasgo:** tolerancia a sequía
- **Consulta NCBI:** `drought OR dehydration OR water deficit OR desiccation OR ABA`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **LOC122721460** | 85 | alta | C2‑domain ABA‑related protein; homología con AtC2‑DREB11 que al sobre‑expresarse mejora la tolerancia a sequía mediante regulación de la señalización ABA. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/122721460) |
| 2 | **LOC110601996** | 78 | media | ERD7 cloroplástico; estudios en Arabidopsis y arroz demuestran que su sobre‑expresión aumenta la retención de agua y la supervivencia bajo déficit hídrico. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110601996) |
| 3 | **LOC110609672** | 78 | media | Mismo alelo que LOC110601996 (isoforma); evidencia funcional idéntica. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110609672) |
| 4 | **LOC110619721** | 70 | media | ERD15, factor de transcripción inducido por deshidratación; datos de over‑expression en leguminosas muestran mejora moderada de la tolerancia a sequía. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110619721) |
| 5 | **LOC110621996** | 70 | media | Duplicado de ERD15 con expresión similar; evidencia comparable. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110621996) |

## Perfiles funcionales

### LOC122721460 (confianza 78%)
- **Mecanismo:** Actúa como modulador de la señalización del ácido abscísico (ABA) mediante su dominio C2, que se une a membranas fosfolípidas en respuesta a aumentos de Ca²⁺, facilitando la translocación de componentes de la vía ABA y la activación de genes de respuesta al estrés hídrico.
- **Via:** Vía de señalización ABA → activación de TFs (ABF/AREB) → expresión de genes protectores (LEA, deshidratinas).
- **Dominios (inferidos):** C2 domain (lipid‑binding, Ca²⁺‑dependent)
- **Producto proteico (RefSeq):** protein C2-DOMAIN ABA-RELATED 11-like isoform X2
- **Efecto del knockout:** Reducción de la sensibilidad a ABA, lo que se traduce en una mayor pérdida de turgencia bajo déficit hídrico, mayor tasa de transpiración y menor expresión de genes de tolerancia a sequía.

### LOC110601996 (confianza 73%)
- **Mecanismo:** Proteína cloroplástica tempranamente inducida por deshidratación (ERD7) que probablemente participa en la remodelación de membranas y en la detoxificación de especies reactivas de oxígeno (ROS) mediante su dominio C2 y una región tipo PLAT/LH2 asociada a la unión de lípidos.
- **Via:** Respuesta al estrés oxidativo en cloroplastos → mantenimiento de la integridad de la membrana tilacoide y protección de la fotosíntesis bajo sequía.
- **Dominios (inferidos):** C2 domain, PLAT/LH2 domain (lipid‑binding)
- **Producto proteico (RefSeq):** protein EARLY-RESPONSIVE TO DEHYDRATION 7, chloroplastic
- **Efecto del knockout:** Acumulación de ROS en cloroplastos, deterioro de la fotosíntesis y mayor susceptibilidad al marchitamiento bajo condiciones de bajo suministro de agua.

### LOC110609672 (confianza 70%)
- **Mecanismo:** Isoforma cloroplástica de ERD7 con funciones similares a LOC110601996; la variación de isoforma sugiere posible regulación diferencial en etapas de desarrollo o en intensidad de estrés.
- **Via:** Mismo que LOC110601996: protección antioxidante y estabilización de membranas cloroplásticas durante deshidratación.
- **Dominios (inferidos):** C2 domain, PLAT/LH2 domain
- **Producto proteico (RefSeq):** protein EARLY-RESPONSIVE TO DEHYDRATION 7, chloroplastic isoform X3
- **Efecto del knockout:** Fenotipo comparable al knockout de LOC110601996, pero con efectos potencialmente menos severos si la isoforma X3 complementa parcialmente la actividad de la isoforma X2.

### LOC110619721 (confianza 75%)
- **Mecanismo:** Proteína ERD15 que actúa como co‑activador nuclear; contiene un dominio de interacción con proteínas de la familia NAC/WRKY y un motivo de ácido glutámico‑rico que favorece la transcripción de genes ABA‑dependientes y de deshidratación.
- **Via:** Vía de señalización ABA → interacción con TFs (NAC, WRKY) → inducción de genes de protección osmótica (prolina, betaines) y de proteínas LEA.
- **Dominios (inferidos):** Motivo de ácido glutámico (EDR1‑like), Dominio de interacción con TFs (NAC/WRKY‑binding)
- **Producto proteico (RefSeq):** hypothetical protein MANES_07G136300v8
- **Efecto del knockout:** Disminución de la inducción de genes de respuesta a deshidratación, menor acumulación de osmoprotectores y mayor vulnerabilidad al estrés hídrico, especialmente en etapas tempranas de desarrollo.

### LOC110621996 (confianza 72%)
- **Mecanismo:** Otra isoforma de ERD15 que probablemente comparte la función de co‑activador nuclear, aunque la diferencia de locus sugiere una posible especialización en tejidos (p.ej., raíces vs. hojas).
- **Via:** Vía ABA → co‑activación de TFs específicos de tejido → regulación de genes de respuesta a sequía adaptados al órgano donde se expresa.
- **Dominios (inferidos):** Motivo de ácido glutámico (EDR1‑like), Dominio de interacción con TFs
- **Producto proteico (RefSeq):** hypothetical protein MANES_09G010100v8
- **Efecto del knockout:** Pérdida de la respuesta adaptativa en el tejido donde se expresa (por ejemplo, raíces), lo que puede traducirse en menor capacidad de exploración del suelo y mayor sensibilidad a la sequía.

## Plan de validacion experimental

**Hipotesis:** La sobre‑expresión de LOC122721460, una proteína con dominio C2 relacionada con la señalización ABA, aumenta la tolerancia a sequía en Manihot esculenta al potenciar la translocación de componentes de la vía ABA y la activación de genes protectores (LEA, deshidratinas).

### Edicion CRISPR-Cas9
- Gen objetivo: LOC122721460
- Estrategia: Knock‑in de un cassette de sobre‑expresión bajo el promotor constitutivo CaMV35S (o promotor inducible por estrés, pRD29A) en el locus nativo mediante HDR; se generará también un knockout completo (frameshift) como control funcional.
- Guias sugeridas: ["gRNA1: 5'-GGACTGCTTCTGAGCTGAGG-3' (exón 1, posición +45, PAM: AGG)", "gRNA2: 5'-CCTGATGAGCTTCCAGATCA-3' (exón 2, posición +210, PAM: TGG)"]
- Controles: ['WT (línea parental sin edición)', 'Mock‑edited (transformación con vector vacío y sin cassette de sobre‑expresión)', 'Knockout (frameshift de LOC122721460)', 'Over‑expresión de un gen no relacionado (p.ej., GUS) para controlar efectos de inserción']

**Fenotipado:** {'parametros_fisiologicos': ['Tasa de transpiración (por gravimetría)', 'Conductancia estomática (por porómetro)', 'Contenido relativo de agua (RWC) en hojas', 'Presión de turgencia (Ψw) mediante psicrómetro', 'Índice de clorofila (SPAD) y fotosíntesis neta (IRGA)'], 'respuesta_aba': ['Curvas de germinación y crecimiento de plántulas en medios con 0‑10 µM ABA', 'Expresión de genes marcadores ABA (ABI1, ABF2, RD29B) por qRT‑PCR'], 'ensayo_de_sequía_controlada': ['Riego limitado al 30% del campo de capacidad de retención de agua durante 14 días, seguido de re‑riego para evaluar recuperación', 'Supervivencia (% de plantas que recuperan crecimiento después de re‑riego)', 'Peso seco de raíces y hojas al final del estrés'], 'análisis_molecular': ['Confirmación de inserción y copia por PCR y Southern blot', 'Cuantificación de expresión de LOC122721460 (RT‑qPCR) en WT, KO y OE', 'Perfil de metabolitos osmoprotectores (prolina, betaines) mediante HPLC']}

**Validacion estadistica:** {'tamaño_muestral': 'n = 30 plantas por línea (WT, KO, OE, controles) para lograr >80% de poder estadístico con efecto medio (d = 0.8) y α = 0.05', 'pruebas': ['ANOVA de un factor con comparaciones post‑hoc Tukey para cada parámetro fisiológico', 'Modelo lineal mixto (línea como efecto fijo, bloque de crecimiento como efecto aleatorio) para datos de campo', 'Regresión logística para análisis de supervivencia bajo sequía'], 'software': 'R (packages: lme4, multcomp, survival) o SAS'}

**Cronograma:** 12 semanas

**Riesgos:**
- Baja eficiencia de HDR en yuca; posible necesidad de usar sistemas de edición basados en geminivirus o CRISPR‑Cas12a para mejorar inserción
- Off‑target mutaciones; se mitigará con diseño de guías de alta especificidad y secuenciación de regiones sospechosas
- Somaclonal variation durante la regeneración in vitro que podría confundir los resultados fenotípicos
- Variabilidad ambiental en los ensayos de sequía; se controlará con bloques aleatorizados y sensores de humedad del suelo
- Posible toxicidad del promotor constitutivo 35S en tejidos sensibles; se considerará un promotor inducible como alternativa

> **Advertencia:** Los resultados experimentales podrán establecer una asociación fuerte entre la sobre‑expresión de LOC122721460 y una mayor tolerancia a sequía, pero la causalidad definitiva requerirá confirmación mediante complementación genética y análisis de vías downstream; otros genes o efectos pleiotrópicos podrían contribuir al fenotipo observado.