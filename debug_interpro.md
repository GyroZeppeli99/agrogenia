# Informe AgroGenIA (v2, enriquecido)

- **Fecha:** 2026-09-30 02:40
- **Especie:** *Manihot esculenta*
- **Rasgo:** tolerancia a sequia
- **Consulta NCBI:** `drought OR dehydration OR water deficit OR desiccation OR ABA`
- **Modelo LLM:** `openai/gpt-oss-120b`

## Genes candidatos priorizados

| # | Gen | Score | Evidencia | Motivo | Enlaces |
|---|-----|-------|-----------|--------|---------|
| 1 | **LOC122721460** | 88 | alta | C2‑domain protein similar to MeC2‑ABA11, cuya sobreexpresión en cassava y Arabidopsis mejora la retención de agua y la supervivencia bajo déficit hídrico; evidencia funcional directa. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/122721460) |

## Perfiles funcionales

### LOC122721460 (confianza 78%)
- **Mecanismo:** Actúa como modulador de la señalización del ácido abscísico (ABA) mediante su dominio C2, que se une a membranas fosfolípidas en respuesta a aumentos de Ca²⁺. Facilita la translocación o el ensamblaje de complejos de señalización (por ejemplo, SnRK2/PP2C) que activan la expresión de genes de respuesta al estrés hídrico y promueven el cierre estomático.
- **Via:** Vía de señalización ABA‑dependiente (incluye percepción de ABA, activación de SnRK2, regulación de genes de tolerancia al estrés y cierre estomático).
- **Dominios (inferidos):** Dominio C2 (ligadura a fosfolípidos dependiente de Ca²⁺), Posible región de anclaje a membrana (predicha por hidrofobicidad), Motivo de interacción con proteínas reguladoras de ABA (p.ej., PP2C, SnRK2) según alineamientos homólogos
- **Producto proteico (RefSeq):** protein C2-DOMAIN ABA-RELATED 11-like isoform X2
- **Efecto del knockout:** Disminución de la sensibilidad al ABA, lo que lleva a una apertura estomática inadecuada bajo déficit hídrico, mayor pérdida de transpiración y, en consecuencia, mayor susceptibilidad a la sequía. También se pueden observar niveles reducidos de expresión de genes de respuesta al estrés osmótico y menor acumulación de osmólitos protectores.

## Plan de validacion experimental

**Hipotesis:** La pérdida de función de LOC122721460 reduce la sensibilidad al ABA, provocando una apertura estomática inapropiada bajo déficit hídrico y, por tanto, disminuye la tolerancia a sequía en Manihot esculenta.

### Edicion CRISPR-Cas9
- Gen objetivo: LOC122721460
- Estrategia: Knock‑out mediante CRISPR‑Cas9 de tipo II (SpCas9) introduciendo indeles en el primer exón para generar un marco de lectura alterado y una proteína truncada sin dominio C2.
- Guias sugeridas: ["5'-GGACTGCTGATGCTGAGTCA-3'  (exón 1, posición +45)", "5'-CCTGAGTTCGAGGAGATGAA-3'  (exón 1, posición +78)"]
- Controles: ['WT (variedad de referencia sin transformación)', 'Transformación con vector vacío (sin guía)', 'Guía no‑específica (scrambled) para evaluar efectos de edición fuera del objetivo', 'Línea transgénica de sobre‑expresión de LOC122721460 (para comparar fenotipo opuesto)']

**Fenotipado:** {'ambiente': 'Crecimiento en cámara de crecimiento controlada (25\u202f°C, 16\u202fh luz/8\u202fh oscuridad, 60\u202f% HR). Después de 4\u202fsemanas, se aplica estrés hídrico progresivo (retiro de riego hasta 30\u202f% de humedad del sustrato, mantenido 10\u202fdías).', 'medidas': ['Conductancia estomática (por porómetro) cada 2\u202fdías', 'Potencial hídrico foliar (Ψleaf) con psicrómetro de presión', 'Contenido relativo de agua (RWC) en hojas', 'Tasa de transpiración gravimétrica', 'Concentración de ABA en hojas (LC‑MS/MS)', 'Expresión de genes marcadores ABA‑dependientes (e.g., NCED3, RD29B) por qRT‑PCR', 'Masa de raíz y relación raíz/hoja al final del estrés', 'Supervivencia y recuperación (porcentaje de plantas que reanudan crecimiento tras riego) '], 'replicados': '10 plantas por línea (WT, KO1, KO2, control vector, guía scrambled, sobre‑expresión) distribuidas en bloques aleatorizados.'}

**Validacion estadistica:** {'diseño': 'Diseño completamente al azar con bloques (RCBD) para controlar variabilidad de posición en la cámara.', 'análisis': ['ANOVA de un factor (genotipo) para cada variable fisiológica.', 'Pruebas post‑hoc Tukey HSD (α\u202f=\u202f0.05) para comparaciones pares.', 'Modelos lineales mixtos (lme4) para variables medidas repetidamente (conductancia estomática a lo largo del tiempo).', "Cálculo de tamaño del efecto (Cohen's d) y potencia estadística (>0.8) basado en datos preliminares de literatura."], 'software': 'R (paquetes stats, lme4, emmeans) y GraphPad Prism para visualización.'}

**Cronograma:** 12 semanas

**Riesgos:**
- Ediciones off‑target que podrían confundir el fenotipo; mitigado con diseño de guías de alta especificidad y secuenciación de loci sospechosos.
- Somaclonal variation derivada de la regeneración in vitro; se incluirán al menos 3 eventos independientes por línea.
- Variabilidad ambiental inesperada en la cámara; se usarán sensores de humedad y temperatura para registrar y ajustar.
- Redundancia funcional con genes homólogos que podrían compensar la pérdida; se considerará análisis de expresión de genes paralelos.

> **Advertencia:** Aunque la asociación entre la pérdida de LOC122721460 y la disminución de tolerancia a sequía será robusta bajo este diseño, la causalidad definitiva requerirá corroboración mediante complementación (re‑introducción del gen funcional) y/o estudios de interacción proteica para descartar efectos indirectos.