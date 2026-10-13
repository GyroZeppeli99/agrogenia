**Informe AgroGenIA (v2, enriquecido)**  
- **Fecha:** 2026-09-30 02:54  
- **Especie:***Manihot esculenta*  
- **Rasgo:** eficiencia de nitrógeno  
- **Consulta NCBI:**nitrogen use OR nitrate OR ammonium assimilation  
- **Modelo LLM:**openai/gpt-oss-120b  
**Genes candidatos priorizados**  
| | | | | | |  
|-|-|-|-|-|-|  
| **#** | **Gen** | **Score** | **Evidencia** | **Motivo** | **Enlaces** |   
| 1 | **LOC110626356** | 85 | alta | Homólogo a AtNRT2.1, con mutantes que alteran la absorción de nitrato y la eficiencia de uso del nitrógeno en Arabidopsis y arroz. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110626356 "https://www.ncbi.nlm.nih.gov/gene/110626356") |   
| 2 | **LOC110608420** | 80 | alta | Nitrato reductasa NADH, enzima clave en la reducción de nitrato; pérdida de función reduce drásticamente la asimilación de nitrógeno. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110608420 "https://www.ncbi.nlm.nih.gov/gene/110608420") |   
| 3 | **LOC110608013** | 80 | alta | Segunda isoforma de nitrato reductasa NADH; evidencia funcional en especies modelo indica papel redundante pero esencial para la NUE. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110608013 "https://www.ncbi.nlm.nih.gov/gene/110608013") |   
| 4 | **LOC110631288** | 70 | media | Transportador de alta afinidad NRT3.1, asociado a la activación de NRT2; datos de expresión bajo déficit de nitrógeno en cassava. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110631288 "https://www.ncbi.nlm.nih.gov/gene/110631288") |   
| 5 | **LOC110617702** | 70 | media | Otro NRT3.1 con patrón de expresión similar; evidencia indirecta de participación en la captación de nitrato. | [NCBI](https://www.ncbi.nlm.nih.gov/gene/110617702 "https://www.ncbi.nlm.nih.gov/gene/110617702") |   
   
**Perfiles funcionales**  
**LOC110626356 (confianza 85%)**  
- **Mecanismo:** Transporte activo de nitrato desde el suelo al citoplasma de las células radiculares mediante un cotransporte dependiente de protones de alta afinidad.  
- **Via:** Asimilación de nitrato (ruta de absorción de nitrato, NRT2.1).  
- **Dominios (inferidos):** Dominio NRT2 (PF07690), Dominio MFS (Major Facilitator Superfamily, PF07690) con múltiples hélices transmembrana  
- **Producto proteico (RefSeq):** high-affinity nitrate transporter 2.1  
- **Efecto del knockout:** Reducción drástica de la capacidad de absorción de nitrato bajo condiciones de baja disponibilidad de nitrógeno, lo que disminuye la eficiencia de uso del nitrógeno, provoca menor crecimiento vegetativo y menor rendimiento de raíz y tubérculo.  
**LOC110608420 (confianza 90%)**  
- **Mecanismo:** Reducción del nitrato a nitrito en el citosol usando NADH como donador de electrones, paso clave de la asimilación de nitrato.  
- **Via:** Reducción de nitrato (nitrate reductase, NR) dentro de la ruta de asimilación de nitrógeno.  
- **Dominios (inferidos):** Dominio Mo-molybdopterin (PF00384), Dominio FAD/NAD(P)-binding (PF01494), Dominio NADH-binding (PF00175)  
- **Producto proteico (RefSeq):** nitrate reductase [NADH] isoform X2  
- **Efecto del knockout:** Acumulación de nitrato en la raíz y disminución de nitrito y amoníaco disponibles para la síntesis de aminoácidos, reduciendo la eficiencia de uso del nitrógeno y la productividad bajo fertilización con nitrato.  
**LOC110608013 (confianza 80%)**  
- **Mecanismo:** Cataliza la reducción del nitrato a nitrito usando NADH, similar a otras isoformas de nitrate reductase.  
- **Via:** Reducción de nitrato (nitrate reductase, NR) en la ruta de asimilación de nitrógeno.  
- **Dominios (inferidos):** Dominio Mo-molybdopterin (PF00384), Dominio FAD/NAD(P)-binding (PF01494), Dominio NADH-binding (PF00175)  
- **Producto proteico (RefSeq):** nitrate reductase [NADH]  
- **Efecto del knockout:** Efecto comparable al knockout de LOC110608420; posible compensación parcial si la isoforma X2 es menos abundante, pero en general se observa menor conversión de nitrato a nitrito y reducción de la eficiencia de nitrógeno.  
**LOC110631288 (confianza 80%)**  
- **Mecanismo:** Transporte de nitrato de alta afinidad mediante un cotransporte con protones, facilitando la captación de nitrato bajo escasez.  
- **Via:** Asimilación de nitrato (NRT2.3).  
- **Dominios (inferidos):** Dominio NRT2 (PF07690), Dominio MFS con múltiples hélices transmembrana  
- **Producto proteico (RefSeq):** high-affinity nitrate transporter 3.1  
- **Efecto del knockout:** Disminución de la capacidad de absorción de nitrato en condiciones de bajo nitrógeno, lo que puede traducirse en menor eficiencia de uso del nitrógeno y menor crecimiento de la planta, aunque la presencia de otras NRT2 paralogos puede mitigar parcialmente el efecto.  
**LOC110617702 (confianza 75%)**  
- **Mecanismo:** Transporte activo de nitrato de alta afinidad, similar a NRT2.3, mediante un cotransporte con protones.  
- **Via:** Asimilación de nitrato (NRT2.3).  
- **Dominios (inferidos):** Dominio NRT2 (PF07690), Dominio MFS con múltiples hélices transmembrana  
- **Producto proteico (RefSeq):** high-affinity nitrate transporter 3.1  
- **Efecto del knockout:** Reducción de la captación de nitrato bajo limitación de nitrógeno, potencialmente afectando la eficiencia de nitrógeno; la redundancia con LOC110631288 puede atenuar el fenotipo, pero se espera una ligera disminución del rendimiento bajo bajo suministro de nitrato.  
**Plan de validacion experimental**  
**Hipotesis:** La pérdida de función de LOC110626356 (homólogo a AtNRT2.1) reducirá significativamente la absorción de nitrato bajo disponibilidad limitada de nitrógeno, disminuyendo la eficiencia de uso del nitrógeno (NUE) y, en consecuencia, el crecimiento vegetativo y el rendimiento de tubérculos en Manihot esculenta.  
**Edicion CRISPR-Cas9**  
- Gen objetivo: LOC110626356  
- Estrategia: Knock‑out completo mediante mutagénesis por inserción/deleción (indel) usando CRISPR‑Cas9 de alta fidelidad (SpCas9‑HF1). Se generarán líneas homozygotas con marco de lectura interrumpido antes del dominio NRT2.  
- Guias sugeridas: ["gRNA1: 5'-GAGTCTGCTGATGCTGAGAA-3' (exón 2, posición +150, PAM: AGG)", "gRNA2: 5'-CTCAGGATCCTGTTGCTGTC-3' (exón 3, posición +378, PAM: CGG)", "gRNA3: 5'-ATGCTGCTGAGGAGTCTGGA-3' (exón 5, posición +620, PAM: GGG)"]  
- Controles: ['WT: planta de referencia sin transformación.', 'Mock‑CRISPR: transformación con Cas9 pero sin gRNA (control de efectos de la transformación).', 'Edición de sitio neutral: mutación de un locus no relacionado con N (p.ej., un gen de resistencia a antibiótico) para controlar efectos de edición fuera del objetivo.']  
**Fenotipado:** {'condiciones_de_cultivo': ['Nitrógeno bajo (30\u202fmg\u202fN\u202fL⁻¹ NO₃⁻)', 'Nitrógeno óptimo (120\u202fmg\u202fN\u202fL⁻¹ NO₃⁻)', 'Nitrógeno alto (300\u202fmg\u202fN\u202fL⁻¹ NO₃⁻)'], 'medidas': ['Tasa de absorción de nitrato (µmol NO₃⁻\u202fg⁻¹ raíz\u202fh⁻¹) mediante ¹⁵N‑nitrato.', 'Contenido total de N en hojas y raíces (Kjeldahl).', 'Crecimiento vegetativo: altura, número de hojas, biomasa aérea seca.', 'Rendimiento de tubérculo: número, peso total y peso medio por tubérculo.', 'Expresión de LOC110626356 y genes asociados (NRT2.3, NRT3.1) por qRT‑PCR.', 'Análisis de metabolitos de nitrógeno (nitrato, nitrito, amonio).'], 'repeticiones': 'Mínimo 12 plantas por línea (WT, Mock, KO) por cada nivel de N, total 144 plantas.'}  
**Validacion estadistica:** {'analisis_principal': 'ANOVA de dos factores (genotipo × nivel de N) con interacción, seguida de pruebas post‑hoc Tukey HSD.', 'tamaño_de_muestra': 'Cálculo a priori con poder estadístico 0.9, α=0.05, efecto esperado d=1.2 (basado en datos de Arabidopsis), resultando en n≥10 por grupo; se usarán 12 para cubrir pérdidas.', 'criterios_de_significancia': 'p < 0.05 para efectos principales e interacción.', 'validación_adicional': 'Regresión lineal entre absorción de ¹⁵N y contenido total de N; análisis de correlación entre expresión génica y fenotipo.'}  
**Cronograma:** 12 semanas  
**Riesgos:**  
- Baja eficiencia de transformación y regeneración de tejido en cassava.  
- Off‑target de CRISPR que pueda afectar genes de nitrato o crecimiento.  
- Mosaicismo en la primera generación T0 que requiera varias generaciones para obtener líneas homozygotas.  
- Variabilidad ambiental en la absorción de nitrato (pH del medio, microbioma del suelo).  
- Posible compensación por genes paralogos (NRT2.3, NRT3.1) que atenúe el fenotipo esperado.  
***Advertencia:*** * Los resultados de este experimento establecerá* *n una asociación fuerte entre la pérdida de LOC110626356 y la reducción de la eficiencia de uso del nitrógeno, pero la causalidad directa deberá confirmarse mediante complementación genética y análisis de posibles efectos compensatorios de genes paralogos.*  
