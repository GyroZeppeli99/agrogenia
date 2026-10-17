# 🧬 AgroGenIA

**AI-driven cross-species gene discovery for orphan and non-orphan crops**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23330723.svg)](https://doi.org/10.5281/zenodo.23330723)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue?logo=python)
![HMMER 3.3+](https://img.shields.io/badge/HMMER-3.3%2B-green)
![License MIT](https://img.shields.io/badge/license-MIT-brightgreen)

AgroGenIA is a computational pipeline that takes a natural-language agronomic trait (e.g., *"drought tolerance in strawberry"*, *"resistance to coffee berry borer"*) and returns auditable trans-species gene candidates with multi-source validation and biotechnological strategy assignment.

> **Core principle**: The LLM reasons, the databases provide the data. Every claim in the final report is traceable to NCBI, Europe PMC, STRING, or GEO.

---

## ✨ Key features

| Capability | Description |
|---|---|
| 🎯 **Dynamic receptor** | Any crop: common name, scientific name, or forced tax_id |
| 🤖 **Multi-LLM router** | Groq → Gemini → OpenRouter cascade with model-level fallback |
| 🧩 **Hybrid donor panel** | Curated expert list + LLM-suggested species, deduplicated & cached |
| 🔬 **Structural-first annotation** | HMMER/Pfam as primary criterion with trait-specific sub-databases |
| 🏆 **Exhaustive pre-ranking** | Heuristic score + per-species interleaving + LLM batched evaluation |
| 👑 **Kingdom separation** | Plants vs microorganisms with honest biotech strategies |
| ✅ **Multi-source validation** | Europe PMC (novelty) + STRING (networks) + GEO (expression datasets) |
| 📊 **Cross-run consensus** | Robustness analysis across multiple independent runs |

---

## 🚀 Quick start

### 1. Install

```bash
git clone https://github.com/GyroZeppeli99/agrogenia.git
cd agrogenia
pip install -r requirements.txt

# HMMER (Ubuntu/Debian)
sudo apt install hmmer
```

### 2. Get API keys

Create a `.env` file (or export):

```bash
export GROQ_API_KEY="gsk_..."           # https://console.groq.com/keys
export GOOGLE_API_KEY="AIzaSy..."      # https://aistudio.google.com/app/apikey
export OPENROUTER_API_KEY="sk-or-..."  # https://openrouter.ai/settings/keys (optional)
```

### 3. Download Pfam and build trait-specific sub-bases

```bash
cd dbs
wget https://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz
gunzip Pfam-A.hmm.gz
hmmpress Pfam-A.hmm                    # ~5-10 min, one-time indexing
cd ..
python construir_pfam_subbases.py      # builds 8 trait sub-bases (data-driven)
```

### 4. Run

```bash
python pipeline_v5.2_dominios_y_consenso.py \
  --rasgo "tolerancia a sequia" \
  --receptora fresa \
  --estrategia B \
  --modo exhaustivo \
  --panel hibrido \
  --pfam auto \
  --hmmer-por-especie 5000 \
  --top 30 \
  --separar-reinos \
  --top-planta 20 --top-microbios 10 \
  --llm-provider auto \
  --salida v52_fresa
```

**Output**: `v52_fresa.json` + `v52_fresa.md` + `v52_fresa.estado` (live monitoring).

---

## 📊 Real results (validated runs)

### Cross-species robustness: candidates surviving multiple configurations

| Accession | Donor | Cassava V4.6.1 | Strawberry V5.1 | Strawberry V5.2 |
|---|---|:---:|:---:|:---:|
| `AAP22171.1` | *Xerophyta viscosa* | 90 | 95 | 82 |
| `AAZ72653.1` | *Craterostigma plantagineum* | — | 95 | 92 |
| `CAD36023.1` | *Craterostigma plantagineum* | — | 90 | 93 🥇 |
| `XP_021303416.1` | *Sorghum bicolor* | — | 84 | 70 |

### Coffee × berry borer: trait-specific sub-base vs generic stress

| Run | Pfam sub-base | Top microbe candidate | Score | Mechanism |
|---|---|---|---:|---|
| `v52_cafe_broca` | `estres` (generic) | Thioredoxin | 60 | Redox modulation (non-specific) |
| `v52_cafe_broca_v2` | `plagas` (trait-specific) | **Cry toxin** | **92** | Pore-forming insecticidal toxin ✅ |

**Cross-run consensus**: *Beauveria bassiana* RicinB lectin (`XP_008603317.1`) emerged in both exhaustive and exploratory modes, with anti-digestive mechanism validated in *Hypothenemus hampei* biocontrol literature.

---

## 🏗️ Pipeline architecture (9 phases)

```
PHASE 0 · ORCHESTRATION
  LLM + curated panel → hybrid donor species

PHASE 1 · RESOLUTION
  Name → NCBI tax_id → genome check → LLM alternative if missing

PHASE 2 · INGESTA
  Download proteomes (Datasets API → E-utilities fallback)
  + minimum-proteome filter

PHASE 3 · HMMER (primary structural criterion)
  Pfam trait-specific sub-base scan

PHASE 4 · PRIORITIZATION
  Heuristic pre-score + per-species interleaving + LLM batches
  + biological domain bonuses (V5.2)

PHASE 5 · MULTI-SOURCE VALIDATION
  Europe PMC (novelty) + STRING (interactions) + GEO (expression)

PHASE 6 · COMPATIBILITY
  LLM evaluates orthology → edition / transgenesis / elicitor
  + kingdom-aware heuristics (V5.1)

PHASE 7 · CONSTRUCT DESIGN
  Promoter + subcellular localization + codon optimization

PHASE 8 · ARM A — known genes in receptor
```

---

## 🔄 Reproducibility of Pfam sub-bases

Trait-specific Pfam sub-bases are built via a **reproducible data-driven method** (see [`dbs/subbases_manifest.json`](dbs/subbases_manifest.json)):

1. Single-pass scan of local `Pfam-A.hmm` (~20,795 families)
2. Selection by substring match in `DESC`/`NAME` fields against trait-specific terms
3. Curated layer for central signaling machinery (TFs, kinases, chaperones)
4. Extraction via `hmmfetch` + indexing via `hmmpress`

### Example: resistance to coffee berry borer

For the trait *"resistencia a broca"*, the `plagas` sub-base captures **158 anti-insect families** (terpene synthases, Cry toxins, lectins, cupins) and produces biologically relevant candidates:
- Cry toxins from *Bacillus thuringiensis* (score 92)
- Repellent terpene synthases (score 82-85)
- Anti-digestive lectins (score 70-80)

In contrast, the generic `estres` sub-base produces basal immunity mechanisms (CDPK kinases, LRR receptors) that are less specific for the target trait.

### Rebuilding sub-bases

```bash
python construir_pfam_subbases.py              # builds all 8 sub-bases
cat dbs/subbases_manifest.json                 # inspect terms and counts
python construir_pfam_subbases.py --traits sequia salinidad  # subset
```

---

## 📊 Cross-run consensus analysis

```bash
python consenso_multi_corrida.py \
  --corridas v52_run1.json v52_run2.json v52_run3.json \
  --salida consensus
```

Produces:
- `consensus.json` — raw data
- `consensus.md` — readable table with candidates appearing in ≥2 runs (robust findings)

---

## 📁 Project structure

```
agrogenia/
├── pipeline_v5.2_dominios_y_consenso.py    # Main pipeline
├── consenso_multi_corrida.py               # Cross-run consensus
├── construir_pfam_subbases.py              # Data-driven Pfam sub-base builder
├── estructura_3d_v5.py                     # Structural 3D evidence layer (AlphaFold DB + ESM Atlas)
├── dbs/
│   ├── Pfam-A.hmm                          # Full Pfam (download separately)
│   ├── Pfam-{sequia,salinidad,calor,...}.hmm  # Trait-specific sub-bases
│   └── subbases_manifest.json              # Audit trail (terms + counts + date)
├── proteomas_donantes/                     # Cached donor proteomes (gitignored)
├── proteomas_receptor/                     # Receptor proteomes (gitignored)
├── resultados/                             # Example reports
├── docs/                                   # Presentations
├── requirements.txt
├── CITATION.cff
├── LICENSE
└── README.md
```

---

## 🛡️ Defense in depth

Each layer catches what the previous one lets slip:

1. **Alias resolution** → prevents name ambiguity
2. **Anti-virus filter** → rejects pathogens masquerading as crops
3. **Content validation** → aborts on insufficient proteomes
4. **Multi-LLM fallback** → survives provider outages
5. **PMC retry + UNKNOWN state** → honest about data unavailability
6. **Heuristic fallback** → completes runs even when LLM quota is exhausted

---

## 📖 Version history

| Version | Key improvement |
|---|---|
| V2 | Keyword-based literature mining |
| V3.2 | Inverted funnel: unknown → HMMER → PMC novelty |
| V4.4 | LLM-orchestrated donors + HMMER as primary criterion |
| V4.6 | Curated donor panel + GEO/STRING integration |
| V4.6.1 | `.estado` disk monitoring + honest PMC UNKNOWN |
| V5.0 | Dynamic receptor + anti-virus filters |
| V5.1 | Multi-LLM router + kingdom separation |
| **V5.2** | **Data-driven Pfam sub-bases, domain bonuses, cross-run consensus** |

---

## 📄 Citation

If you use AgroGenIA in your research:

```bibtex
@software{agrogenia_v52_2026,
  author       = {GyroZeppeli99},
  title        = {AgroGenIA: AI-driven cross-species gene discovery for orphan crops},
  month        = oct,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v5.2},
  doi          = {10.5281/zenodo.23330723},
  url          = {https://doi.org/10.5281/zenodo.23330723}
}
```

---

## 🤝 Contributing

Issues and PRs welcome! Especially:
- New trait-specific Pfam sub-bases (heat, salt, cold, pathogens...)
- Additional LLM providers (Anthropic, Cohere...)
- Experimental validation partnerships with orphan-crop programs

---

## 📜 License

MIT © 2026. See [`LICENSE`](LICENSE).
