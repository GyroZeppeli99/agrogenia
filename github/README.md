# 🧬 AgroGenIA

**AI-driven cross-species gene discovery for orphan crops**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/HMMER-3.3+-green" alt="HMMER">
  <img src="https://img.shields.io/badge/LLMs-Groq%20%7C%20Gemini%20%7C%20OpenRouter-purple" alt="LLMs">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="MIT">
  <img src="https://img.shields.io/badge/version-5.2-orange" alt="v5.2">
</p>

**AgroGenIA** is a computational pipeline that takes a natural-language agronomic trait (e.g., *"drought tolerance in strawberry"*) and returns auditable trans-species gene candidates with multi-source validation and biotechnological strategy assignment.

> 💡 **Core principle**: The LLM reasons, the databases provide the data. Every claim in the final report is traceable to NCBI, Europe PMC, STRING, or GEO.

---

## ✨ Key features

| Capability | Description |
|---|---|
| 🎯 **Dynamic receptor** | Any crop accepted — common name, scientific name, or forced tax_id |
| 🤖 **Multi-LLM router** | Groq → Gemini → OpenRouter cascade with model-level fallback |
| 🧩 **Hybrid donor panel** | Curated expert list + LLM-suggested species, deduplicated & cached |
| 🔬 **Structural-first annotation** | HMMER/Pfam as primary criterion (11× faster with trait-specific sub-databases) |
| 🏆 **Exhaustive pre-ranking** | Heuristic score + per-species interleaving + LLM batched evaluation |
| 👑 **Kingdom separation** | Plants vs microorganisms with honest biotech strategies |
| ✅ **Multi-source validation** | Europe PMC (novelty) + STRING (networks) + GEO (expression datasets) |

---

## 🚀 Quick start

### 1. Install

```bash
# Clone
git clone https://github.com/TU-USUARIO/agrogenia.git
cd agrogenia

# Python dependencies
pip install -r requirements.txt

# HMMER (Ubuntu/Debian)
sudo apt install hmmer