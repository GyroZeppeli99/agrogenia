# Descubrimiento AgroGenIA v3.2

- **Fecha:** 2026-10-01 00:50
- **Especie:** *Manihot esculenta*
- **Rasgo:** tolerancia a calor
- **Nivel de filtro usado:** Nivel 3
- **Proteoma total:** 59151
- **Candidatas tras filtro:** 31469
- **Loci unicos tras deduplicacion:** 31469
- **Escaneadas con HMMER:** 2000
- **Con dominios de estres:** 295
- **Noveles priorizados:** 10

## Embudo de filtrado

| Etapa | Cantidad |
|---|---|
| Proteoma total | 59151 |
| Excluidas (transp/fragmentos) | 27682 |
| Candidatas (nivel 3) | 31469 |
| Loci unicos (deduplicacion) | 31469 |
| Escaneadas con HMMER | 2000 |
| Con dominios de estres | 295 |
| Noveles priorizados | 10 |

## Candidatos noveles

| # | Locus | Accession | Score | Especulacion | Pista | Dominios | PMC | Novel |
|---|---|---|---|---|---|---|---|---|
| 1 | Manes.07G142400 | Manes.07G142400.1.p | 82 | baja | Domino WRKY (factor de transcripción asociado a respuestas de calor y estrés ... | WRKY | 2 | no |
| 2 | Manes.14G044700 | Manes.14G044700.1.p | 80 | baja | Domino AP2/ERF (familia de TF implicada en respuestas a calor y sequía) | AP2 | 1 | no |
| 3 | Manes.07G012700 | Manes.07G012700.1.p | 80 | baja | Domino WRKY (TF bien documentado en tolerancia a calor) | WRKY | 0 | SI |
| 4 | Manes.07G043100 | Manes.07G043100.5.p | 78 | media | Múltiples dominios zf‑C2H2 (zinc‑finger) típicos de reguladores de estrés tér... | zf-C2H2_jaz, zf-C2H2_jaz, zf-C2H2_jaz, zf-C2H2_jaz, zf-C2H2_jaz, zf-C2H2_jaz, zf-C2H2_jaz, zf-C2H2_jaz, zf-C2H2_2, zf-C2H2_2, zf-C2H2_2, zf-C2H2_2, zf-C2H2_2, zf-C2H2_2, zf-C2H2_2, zf-C2H2_2, zf-C2H2_2, zf-C2H2_2, zf-C2H2, zf-C2H2 | 0 | SI |
| 5 | Manes.14G106050 | Manes.14G106050.2.p | 75 | media | Domino Pkinase (posible MAPK o receptor‑like kinase involucrado en cascadas d... | Pkinase | 0 | SI |
| 6 | Manes.06G106900 | Manes.06G106900.2.p | 75 | media | Gran número de dominios LRR (probable receptor‑like protein que percibe señal... | LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_1, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_4, LRR_8, LRR_8, LRR_8, LRR_8, LRR_8, LRR_8, LRR_8, LRR_8, LRR_8, LRR_8, LRR_8, LRR_8 | 0 | SI |
| 7 | Manes.14G112600 | Manes.14G112600.1.p | 73 | media | Domino Pkinase (kinasa asociada a respuestas de estrés térmico) | Pkinase | 0 | SI |
| 8 | Manes.07G108800 | Manes.07G108800.1.p | 72 | media | Domino Pkinase (kinasa que podría participar en rutas de señalización de calor) | Pkinase | 0 | SI |
| 9 | Manes.07G017900 | Manes.07G017900.1.p | 71 | media | Domino Pkinase (posible regulador de la respuesta a altas temperaturas) | Pkinase | 0 | SI |
| 10 | Manes.14G095800 | Manes.14G095800.1.p | 70 | media | Dominios ABC2_membrane (transportadores que pueden eliminar metabolitos tóxic... | ABC2_membrane, ABC2_membrane_7, ABC2_membrane_7, ABC2_membrane_3 | 0 | SI |

## Convergencia con genes conocidos (Brazo A)

### Manes.07G142400.1.p
- **Converge con:** LOC110620422
- **Tipo:** via
- **Hipotesis:** El factor de transcripción WRKY podría regular genes de respuesta al calor de forma paralela a los HSF (por ejemplo HSFA‑6b), integrándose en la misma vía de señalización de estrés térmico.
- **Confianza:** 85%

### Manes.14G044700.1.p
- **Converge con:** LOC110620422
- **Tipo:** via
- **Hipotesis:** Los TF de la familia AP2/ERF participan en la regulación de genes de tolerancia al calor y sequía, funcionando en la misma red de respuesta que los HSF, aunque con dominios diferentes.
- **Confianza:** 80%

### Manes.07G012700.1.p
- **Converge con:** LOC110607902
- **Tipo:** via
- **Hipotesis:** Otro WRKY que podría actuar como regulador upstream o co‑activador de los HSF (HSFA‑3‑like), modulando la expresión de chaperonas y proteínas de protección térmica.
- **Confianza:** 85%

### Manes.07G043100.5.p
- **Converge con:** LOC110620422
- **Tipo:** via
- **Hipotesis:** Los múltiples dominios zf‑C2H2 son típicos de reguladores de estrés; podrían cooperar con los HSF en la activación de genes de choque térmico, constituyendo una vía paralela de control transcripcional.
- **Confianza:** 78%

### Manes.14G106050.2.p
- **Converge con:** LOC110611125
- **Tipo:** via
- **Hipotesis:** Una quinasa tipo MAPK puede fosforilar y activar HSF30 o sus co‑factores, integrándose en la cascada de señalización que lleva al inicio de la respuesta al calor.
- **Confianza:** 75%

### Manes.06G106900.2.p
- **Converge con:** LOC110611125
- **Tipo:** via
- **Hipotesis:** Los dominios LRR sugieren una proteína tipo receptor‑like que percibe cambios en la membrana bajo estrés térmico y activa cascadas de señalización que culminan en la activación de HSF30.
- **Confianza:** 70%

### Manes.14G112600.1.p
- **Converge con:** LOC110611125
- **Tipo:** via
- **Hipotesis:** Una quinasa de dominio Pkinase podría participar en la fosforilación de HSF30 o de sus reguladores, modulando la intensidad de la respuesta al calor.
- **Confianza:** 73%

### Manes.07G108800.1.p
- **Converge con:** LOC110611125
- **Tipo:** via
- **Hipotesis:** Similar al caso anterior, esta quinasa podría formar parte de la vía MAPK‑HSF que controla la expresión de HSP70/90 bajo altas temperaturas.
- **Confianza:** 73%

### Manes.07G017900.1.p
- **Converge con:** LOC110611125
- **Tipo:** via
- **Hipotesis:** Otra quinasa potencialmente involucrada en la cascada de señalización que lleva a la activación de los factores HSF y la síntesis de chaperonas.
- **Confianza:** 73%

### Manes.14G095800.1.p
- **Converge con:** LOC110626448
- **Tipo:** via
- **Hipotesis:** Los transportadores ABC pueden expulsar metabolitos tóxicos acumulados durante el estrés térmico, complementando la acción de pequeñas HSP como la de 17.4 kDa, aunque el vínculo es indirecto.
- **Confianza:** 55%

> Los candidatos marcados como NOVEL (0 menciones en PMC) son los de mayor interes.