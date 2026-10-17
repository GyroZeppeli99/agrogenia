[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23330723.svg)](https://doi.org/10.5281/zenodo.23330723)


## Reproducibilidad de sub-bases Pfam

Las sub-bases Pfam se construyen mediante un método reproducible data-driven (ver `dbs/subbases_manifest.json`). 

### Ejemplo: resistencia a broca

Para el rasgo "resistencia a broca", la sub-base `plagas` captura **158 familias anti-insecto** (terpeno sintasas, toxinas Cry, lectinas, cupinas) y produce candidatos biológicamente relevantes:
- Toxinas Cry de *Bacillus thuringiensis* (score 92)
- Terpeno sintasas repelentes (score 82-85)
- Lectinas anti-digestivas (score 70-80)

En contraste, la sub-base genérica `estres` produce mecanismos de inmunidad basal (quinasas CDPK, receptores LRR) menos específicos para el rasgo objetivo.

### Construir sub-bases

```bash
python construir_pfam_subbases.py  # genera las 8 sub-bases
cat dbs/subbases_manifest.json     # ver términos y conteos
