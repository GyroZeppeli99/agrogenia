#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgroGenIA V5.0 · BUSQUEDA TRANS-ESPECIE ORQUESTADA
====================================================
Mejora sobre V4: la seleccion de especies donantes es ORQUESTADA
por el LLM en lugar de una lista fija. El flujo es:

  1. El LLM sugiere especies donantes segun el rasgo
  2. El script resuelve nombres cientificos a tax_ids (NCBI Taxonomy)
  3. Verifica que cada especie tenga genoma disponible (NCBI Datasets)
  4. Si una especie no tiene genoma, el LLM sugiere una alternativa
  5. Se descargan los proteomas de las especies validas

Esto permite consultar CUALQUIER rasgo sin editar el codigo.
"""
import os
import sys
import io
import json
import time
import random
import zipfile
import argparse
import shutil
import subprocess
import tempfile
import re
from pathlib import Path
from datetime import datetime

try:
    import requests
    from groq import Groq
except ImportError as e:
    sys.exit("Falta una libreria: " + str(e) + "  ->  pip install requests groq")

# ============================ CONFIGURACION ============================
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()
if not GROQ_API_KEY:
    sys.exit('Falta GROQ_API_KEY.  export GROQ_API_KEY="gsk_..."')

client = Groq(api_key=GROQ_API_KEY)

MODELOS = {
    "calidad":   "openai/gpt-oss-120b",
    "rapido":    "openai/gpt-oss-20b",
    "razonador": "qwen/qwen3.8-27b",
}

NCBI      = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_DATA = "https://api.ncbi.nlm.nih.gov/datasets/v2"
UNIPROT   = "https://rest.uniprot.org"

# ============================ BASES PFAM ============================
PFAM_DIR = Path.home() / "agrogenia" / "dbs"
PFAM_FULL = PFAM_DIR / "Pfam-A.hmm"
PFAM_GENERIC = PFAM_DIR / "Pfam-estres.hmm"

# Sub-bases por rasgo
PFAM_TRAITS = [
    "estres",
    "sequia",
    "salinidad",
    "calor",
    "frio",
    "inundacion",
    "oxidativo",
    "nutricion",
]

PFAM_POR_RASGO = {
    "tolerancia a sequia": "sequia",
    "sequia": "sequia",
    "drought": "sequia",

    "tolerancia a salinidad": "salinidad",
    "salinidad": "salinidad",
    "salt": "salinidad",

    "tolerancia a calor": "calor",
    "calor": "calor",
    "heat": "calor",

    "tolerancia a frio": "frio",
    "frio": "frio",
    "cold": "frio",

    "tolerancia a inundacion": "inundacion",
    "inundacion": "inundacion",
    "flooding": "inundacion",
    "hypoxia": "inundacion",

    "estres oxidativo": "oxidativo",
    "oxidativo": "oxidativo",
    "oxidative": "oxidativo",

    "nutricion": "nutricion",
    "deficiencia nutricional": "nutricion",
    "nutrient": "nutricion",
}

def ruta_pfam_trait(trait):
    return PFAM_DIR / ("Pfam-" + trait + ".hmm")


def inferir_trait_pfam(rasgo_norm):
    """Infere qué sub-base Pfam conviene según el rasgo normalizado."""
    t = normalizar(rasgo_norm.lower()).strip()

    # Mapeo directo
    if t in PFAM_POR_RASGO:
        return PFAM_POR_RASGO[t]

    # Heurísticas simples
    if any(k in t for k in ["sequ", "drought", "dehyd", "desicc", "osmot", "water deficit"]):
        return "sequia"
    if any(k in t for k in ["salin", "salt", "sodio", "sodium", "halo"]):
        return "salinidad"
    if any(k in t for k in ["calor", "heat", "termo", "high temperature"]):
        return "calor"
    if any(k in t for k in ["frio", "cold", "freezing", "low temperature"]):
        return "frio"
    if any(k in t for k in ["inund", "aneg", "flood", "submerg", "hypox", "anaerob"]):
        return "inundacion"
    if any(k in t for k in ["oxid", "ros", "peroxid", "radical"]):
        return "oxidativo"
    if any(k in t for k in ["nutri", "fertil", "deficiencia", "nitrogen", "fosforo", "potasio", "hierro", "zinc"]):
        return "nutricion"

    return "estres"


def listar_bases_pfam():
    print("")
    print("Bases Pfam disponibles:")
    print("  - completo : " + str(PFAM_FULL) + (" [OK]" if PFAM_FULL.exists() else " [FALTA]"))
    for trait in PFAM_TRAITS:
        ruta = ruta_pfam_trait(trait)
        print("  - " + trait.ljust(12) + ": " + str(ruta) + (" [OK]" if ruta.exists() else " [FALTA]"))
    print("")


def seleccionar_base_pfam(modo, rasgo_norm, ruta_custom=""):
    """
    Devuelve (ruta, etiqueta, es_subbase).

    modos:
      auto       -> sub-base del rasgo si existe, luego genérica, luego completa
      completo   -> Pfam-A.hmm
      estres     -> Pfam-estres.hmm
      sequia     -> Pfam-sequia.hmm
      ...        -> otras sub-bases
      custom     -> ruta_custom
    """
    if modo == "custom":
        if not ruta_custom:
            raise ValueError("--pfam custom requiere --pfam-ruta")
        ruta = Path(ruta_custom).expanduser()
        if not ruta.exists():
            raise FileNotFoundError("No existe la base Pfam personalizada: " + str(ruta))
        return ruta, "custom:" + ruta.name, True

    if modo == "completo":
        if not PFAM_FULL.exists():
            raise FileNotFoundError("No existe Pfam completo: " + str(PFAM_FULL))
        return PFAM_FULL, "Pfam-A completo", False

    if modo == "auto":
        trait = inferir_trait_pfam(rasgo_norm)

        # 1. sub-base específica del rasgo
        ruta_trait = ruta_pfam_trait(trait)
        if ruta_trait.exists():
            return ruta_trait, "sub-base:" + trait, True

        # 2. sub-base genérica de estrés
        if PFAM_GENERIC.exists():
            return PFAM_GENERIC, "sub-base:estres", True

        # 3. Pfam completo
        if PFAM_FULL.exists():
            return PFAM_FULL, "Pfam-A completo (fallback)", False

        raise FileNotFoundError("No hay ninguna base Pfam disponible.")

    # modo explícito: estres, sequia, salinidad, etc.
    if modo in PFAM_TRAITS:
        ruta = ruta_pfam_trait(modo)
        if ruta.exists():
            return ruta, "sub-base:" + modo, True
        # si no existe, fallback suave a completa
        if PFAM_FULL.exists():
            return PFAM_FULL, "Pfam-A completo (sub-base " + modo + " no existe)", False
        raise FileNotFoundError("No existe la sub-base " + modo + " ni Pfam completo.")

    raise ValueError("Modo Pfam no reconocido: " + str(modo))


# ── Bases de datos Tier 1 para validacion multi-fuente (V4.2) ──
EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
STRING_API = "https://string-db.org/api/json/interaction_partners"

# Terminos para busqueda de datasets de expresion en GEO por rasgo
TERMINOS_GEO = {
    "tolerancia a sequia":     "drought OR dehydration OR water deficit OR osmotic stress",
    "tolerancia a salinidad":  "salt stress OR salinity OR sodium chloride",
    "tolerancia a calor":      "heat stress OR heat shock OR high temperature",
    "tolerancia a frio":       "cold stress OR freezing OR low temperature",
    "tolerancia a inundacion": "flooding OR submergence OR hypoxia OR anaerobic",
}



# Especie receptora por defecto
RECEPTORA = {
    "yuca":        {"tax_id": 3983, "nombre": "Manihot esculenta"},
    "arabidopsis": {"tax_id": 3702, "nombre": "Arabidopsis thaliana"},
    "arroz":       {"tax_id": 4530, "nombre": "Oryza sativa"},
    "tomate":      {"tax_id": 4081, "nombre": "Solanum lycopersicum"},
}

# ─────────────────────────────────────────────────────────────────────
# PANEL CURADO DE DONANTES POR RASGO (MEJORA 3 · V4.6)
# ─────────────────────────────────────────────────────────────────────
PANEL_CURADO = {
    "tolerancia a sequia": [
        {
            "nombre_cientifico": "Xerophyta viscosa",
            "tipo": "planta",
            "adaptacion": "Planta resurrección que tolera desecación extrema mediante LEA, HSP y protección de membranas.",
            "genes_clave": ["LEA", "HSP90", "DREB2A"]
        },
        {
            "nombre_cientifico": "Selaginella lepidophylla",
            "tipo": "planta",
            "adaptacion": "Planta resurrección con estabilización de membranas y protección antioxidante durante desecación.",
            "genes_clave": ["LEA", "sucrose phosphate synthase", "antioxidant"]
        },
        {
            "nombre_cientifico": "Craterostigma plantagineum",
            "tipo": "planta",
            "adaptacion": "Planta resurrección modelo para tolerancia a desecación y recuperación tras rehidratación.",
            "genes_clave": ["LEA", "DREB", "CPK"]
        },
        {
            "nombre_cientifico": "Eutrema salsugineum",
            "tipo": "planta",
            "adaptacion": "Crucífera halófita/xerófita con regulación osmótica y ABA eficiente.",
            "genes_clave": ["DREB2A", "NCED3", "SOS1"]
        },
        {
            "nombre_cientifico": "Sorghum bicolor",
            "tipo": "planta",
            "adaptacion": "Cereal C4 tolerante a sequía con cierre estomático rápido y acumulación de osmólitos.",
            "genes_clave": ["NAC", "DREB", "PP2C", "TPP"]
        },
        {
            "nombre_cientifico": "Bacillus subtilis",
            "tipo": "bacteria",
            "adaptacion": "Bacteria del suelo productora de osmoprotectores, trehalosa, prolina y biofilm.",
            "genes_clave": ["otsA", "proP", "betA", "eps"]
        },
        {
            "nombre_cientifico": "Pseudomonas fluorescens",
            "tipo": "bacteria",
            "adaptacion": "Rhizobacteria promotora del crecimiento que mejora retención de agua en rizosfera.",
            "genes_clave": ["trehalose synthase", "ACC deaminase", "exopolysaccharide"]
        },
        {
            "nombre_cientifico": "Trichoderma harzianum",
            "tipo": "hongo",
            "adaptacion": "Hongo benéfico que induce tolerancia a sequía en plantas mediante señalización y osmoprotectores.",
            "genes_clave": ["TPS1", "HOG1", "chaperone"]
        },
        {
            "nombre_cientifico": "Halobacterium salinarum",
            "tipo": "arquea",
            "adaptacion": "Arquea extrema con protección frente a desecación y estrés osmótico.",
            "genes_clave": ["Dps", "trehalose", "bacteriorhodopsin", "chaperone"]
        }
    ],

    "tolerancia a salinidad": [
        {
            "nombre_cientifico": "Eutrema salsugineum",
            "tipo": "planta",
            "adaptacion": "Halófita modelo con exclusión iónica y compatibilización osmótica.",
            "genes_clave": ["SOS1", "NHX1", "HKT1"]
        },
        {
            "nombre_cientifico": "Thellungiella salsuginea",
            "tipo": "planta",
            "adaptacion": "Crucífera extremadamente tolerante a salinidad.",
            "genes_clave": ["NHX", "SOS", "LEA"]
        },
        {
            "nombre_cientifico": "Salicornia europaea",
            "tipo": "planta",
            "adaptacion": "Planta halófita suculenta que tolera altos niveles de NaCl.",
            "genes_clave": ["vacuolar Na+/H+ antiporter", "aquaporin"]
        },
        {
            "nombre_cientifico": "Halomonas elongata",
            "tipo": "bacteria",
            "adaptacion": "Bacteria halófila productora de ectoína como osmoprotector.",
            "genes_clave": ["ectA", "ectB", "ectC", "betaine"]
        },
        {
            "nombre_cientifico": "Bacillus subtilis",
            "tipo": "bacteria",
            "adaptacion": "Bacteria del suelo con respuesta a estrés osmótico y producción de solutos compatibles.",
            "genes_clave": ["proP", "betA", "otsA"]
        },
        {
            "nombre_cientifico": "Trichoderma harzianum",
            "tipo": "hongo",
            "adaptacion": "Hongo que mitiga estrés salino en plantas hospedadoras.",
            "genes_clave": ["HOG1", "TPS", "chaperone"]
        }
    ],

    "tolerancia a calor": [
        {
            "nombre_cientifico": "Thermus thermophilus",
            "tipo": "bacteria",
            "adaptacion": "Bacteria termófila con proteínas y enzimas estables a alta temperatura.",
            "genes_clave": ["HSP", "chaperone", "thermosome"]
        },
        {
            "nombre_cientifico": "Sorghum bicolor",
            "tipo": "planta",
            "adaptacion": "Cereal C4 con buena tolerancia a altas temperaturas y mantenimiento fotosintético.",
            "genes_clave": ["HSP70", "HSP90", "HSFA2"]
        },
        {
            "nombre_cientifico": "Arabidopsis thaliana",
            "tipo": "planta",
            "adaptacion": "Modelo con vía HSF/HSP bien caracterizada.",
            "genes_clave": ["HSFA2", "HSP101", "HSP70"]
        },
        {
            "nombre_cientifico": "Bacillus subtilis",
            "tipo": "bacteria",
            "adaptacion": "Bacteria con respuesta a choque térmico y chaperonas conservadas.",
            "genes_clave": ["DnaK", "GroEL", "ClpB"]
        },
        {
            "nombre_cientifico": "Saccharomyces cerevisiae",
            "tipo": "levadura",
            "adaptacion": "Levadura modelo con respuesta a heat shock bien caracterizada.",
            "genes_clave": ["HSP104", "HSP70", "HSF1"]
        }
    ],

    "tolerancia a frio": [
        {
            "nombre_cientifico": "Arabidopsis thaliana",
            "tipo": "planta",
            "adaptacion": "Modelo de respuesta a frio mediante CBF/DREB1.",
            "genes_clave": ["CBF1", "CBF2", "CBF3", "COR15"]
        },
        {
            "nombre_cientifico": "Oryza sativa",
            "tipo": "planta",
            "adaptacion": "Arroz con variantes de tolerancia a frio en etapas tempranas.",
            "genes_clave": ["Cold-responsive kinase", "LEA", "DREB"]
        },
        {
            "nombre_cientifico": "Psychrobacter arcticus",
            "tipo": "bacteria",
            "adaptacion": "Bacteria psicrofílica con enzimas y membranas adapadas a bajas temperaturas.",
            "genes_clave": ["cold shock protein", "desaturase"]
        },
        {
            "nombre_cientifico": "Shewanella putrefaciens",
            "tipo": "bacteria",
            "adaptacion": "Bacteria capaz de actividad metabólica a bajas temperaturas.",
            "genes_clave": ["cold shock", "electron transport"]
        }
    ],

    "tolerancia a inundacion": [
        {
            "nombre_cientifico": "Oryza sativa",
            "tipo": "planta",
            "adaptacion": "Arroz con genes SUB1/ERF-VII para tolerancia a submergencia.",
            "genes_clave": ["SUB1A", "ADH1", "PDC"]
        },
        {
            "nombre_cientifico": "Arabidopsis thaliana",
            "tipo": "planta",
            "adaptacion": "Modelo de respuesta a hipoxia mediante ERF-VII/N-degron.",
            "genes_clave": ["RAP2.12", "RAP2.2", "ADH1"]
        },
        {
            "nombre_cientifico": "Zea mays",
            "tipo": "planta",
            "adaptacion": "Maíz con variabilidad genética para tolerancia a encharcamiento.",
            "genes_clave": ["ADH", "PDC", "hypoxia-responsive"]
        },
        {
            "nombre_cientifico": "Clostridium acetobutylicum",
            "tipo": "bacteria",
            "adaptacion": "Bacteria anaerobia con fermentación y tolerancia a bajo oxígeno.",
            "genes_clave": ["adhE", "pdc", "fermentative"]
        }
    ],

    "estres oxidativo": [
        {
            "nombre_cientifico": "Deinococcus radiodurans",
            "tipo": "bacteria",
            "adaptacion": "Bacteria extremadamente resistente a oxidativo, radiación y desecación.",
            "genes_clave": ["Mn-SOD", "catalase", "recA", "ddrA"]
        },
        {
            "nombre_cientifico": "Thermus thermophilus",
            "tipo": "bacteria",
            "adaptacion": "Termófilo con sistemas antioxidantes robustos.",
            "genes_clave": ["SOD", "peroxiredoxin", "thioredoxin"]
        },
        {
            "nombre_cientifico": "Arabidopsis thaliana",
            "tipo": "planta",
            "adaptacion": "Modelo con APX, CAT, GST y redes redox bien caracterizadas.",
            "genes_clave": ["APX", "CAT", "GST", "Trx"]
        },
        {
            "nombre_cientifico": "Saccharomyces cerevisiae",
            "tipo": "levadura",
            "adaptacion": "Levadura con respuesta a estrés oxidativo vía Yap1.",
            "genes_clave": ["YAP1", "CTT1", "TSA1", "TRX2"]
        }
    ],

    "nutricion": [
        {
            "nombre_cientifico": "Arabidopsis thaliana",
            "tipo": "planta",
            "adaptacion": "Modelo de transporte y señalización nutricional.",
            "genes_clave": ["NRT", "PHT", "IRT1", "FRO2"]
        },
        {
            "nombre_cientifico": "Oryza sativa",
            "tipo": "planta",
            "adaptacion": "Arroz con genes de eficiencia en fósforo, nitrógeno y hierro.",
            "genes_clave": ["PHT1", "NRT", "NAS"]
        },
        {
            "nombre_cientifico": "Bacillus subtilis",
            "tipo": "bacteria",
            "adaptacion": "Bacteria rizosférica que moviliza nutrientes.",
            "genes_clave": ["phytase", "phosphate solubilization", "siderophore"]
        },
        {
            "nombre_cientifico": "Pseudomonas fluorescens",
            "tipo": "bacteria",
            "adaptacion": "Rhizobacteria promotora del crecimiento y solubilización de nutrientes.",
            "genes_clave": ["siderophore", "phosphate solubilization", "ACC deaminase"]
        }
    ],
}

def panel_curado_para_rasgo(rasgo_norm):
    """Devuelve una copia del panel curado para el rasgo normalizado."""
    clave = normalizar(str(rasgo_norm).lower().strip())
    panel = PANEL_CURADO.get(clave, [])
    return [dict(x) for x in panel]


def combinar_panels(curado, llm):
    """Combina panel curado + panel LLM, deduplicando por nombre científico."""
    vistos = set()
    salida = []

    for item in list(curado) + list(llm):
        nombre = str(item.get("nombre_cientifico", "")).strip()
        if not nombre:
            continue

        clave = normalizar(nombre.lower())
        if clave in vistos:
            continue

        vistos.add(clave)
        salida.append(item)

    return salida


def obtener_donantes_panel(rasgo, rasgo_norm, receptora, modelo, modo):
    """
    Devuelve el panel de donantes según el modo:
      - llm: solo LLM
      - curado: solo panel curado
      - hibrido: curado + LLM deduplicado
    """
    log("Modo panel de donantes: " + modo, "fase")

    curado = panel_curado_para_rasgo(rasgo_norm)

    if modo == "curado":
        if not curado:
            log("No hay panel curado para este rasgo; cayendo a LLM.", "warn")
            return sugerir_donantes_llm(rasgo, receptora, modelo)
        log("Usando panel curado: " + str(len(curado)) + " especies.", "ok")
        return curado

    if modo == "llm":
        return sugerir_donantes_llm(rasgo, receptora, modelo)

    if modo == "hibrido":
        llm = sugerir_donantes_llm(rasgo, receptora, modelo)
        combinado = combinar_panels(curado, llm)
        log("Panel hibrido: curado=" + str(len(curado)) +
            " | LLM=" + str(len(llm)) +
            " | combinado deduplicado=" + str(len(combinado)), "ok")
        return combinado

    # fallback seguro
    return sugerir_donantes_llm(rasgo, receptora, modelo)


# Palabras clave por rasgo para filtrar candidatos (se normalizan acentos)
KEYWORDS_ESTRES = {
   "tolerancia a sequia": ["trehalose", "LEA", "dehydrin", "DREB", "dehydration",
                        "desiccation", "drought", "osmoprotectant", "ABA",
                        "osmotic", "osmolyte", "compatible solute",
                        "proline", "glycine betaine", "ectoine",
                        "chaperone", "HSP", "heat shock", "cold shock",
                        "sigma factor", "spo0", "sporulation",
                        "oxidative stress", "ROS", "catalase", "superoxide",
                        "biofilm", "exopolysaccharide", "EPS"],
    "tolerancia a salinidad": ["ectoine", "antiporter", "HKT", "NHX", "SOS",
                               "salt", "halo", "sodium", "ion transport"],
    "tolerancia a calor": ["heat shock", "chaperon", "thermosome", "Hsp", "HSP",
                           "thermostable", "thermophilic"],
    "tolerancia a frio": ["CBF", "antifreeze", "cold", "freezing", "COR"],
    "tolerancia a inundacion": ["ADH", "alcohol dehydrogenase", "anaerobic",
                                "hypoxia", "fermentation", "ERF-VII"],
}

# Dominios Pfam por rasgo (para HMMER)
DOMINIOS_ESTRES = {
    "tolerancia a sequia": ["LEA", "DREB", "AP2", "zf-C2H2", "bZIP", "WRKY",
                            "Pkinase", "ABC2_membrane", "PPR", "TPP", "TPS",
                            "HSP20", "HSP70", "HSP90", "Chaperone", "DHN",
                            "ERF", "NAC", "SNF2-rel_dom", "PAP2", "LRR"],
    "tolerancia a salinidad": ["ABC2_membrane", "Pkinase", "WRKY", "zf-C2H2",
                               "AP2", "Na_H_Exchanger", "PAP2"],
    "tolerancia a calor": ["HSP20", "HSP70", "HSP90", "Chaperone", "Pkinase",
                           "WRKY", "AP2", "zf-C2H2"],
    "tolerancia a frio": ["AP2", "bZIP", "WRKY"],
    "tolerancia a inundacion": ["ADH", "Pkinase", "AP2", "WRKY"],
}

# ============================ UTILIDADES ============================
def banner():
    print("")
    print("=" * 66)
    print("  AgroGenIA V5.0 · TRANS-ESPECIE + VALIDACION MULTI-FUENTE")
    print("  LLM sugiere donantes -> resolucion -> descarga automatica")
    print("=" * 66)


def log(msg, nivel="dato"):
    iconos = {"fase": "#", "ok": "+", "warn": "!", "error": "x", "dato": "-"}
    print("  " + iconos.get(nivel, "-") + " " + msg)

# ============================ MONITOREO EN DISCO (V4.6.1) ============================
ESTADO_PATH = None

def estado(msg):
    """Escribe un evento de estado a disco con timestamp y flush inmediato.
    Independiente del buffering de stdout: permite monitorear corridas en nohup
    incluso mientras el proceso esta dentro de un subproceso (hmmscan)."""
    if not ESTADO_PATH:
        return
    try:
        linea = "[" + datetime.now().strftime("%H:%M:%S") + "] " + msg + "\n"
        with open(ESTADO_PATH, "a", encoding="utf-8") as f:
            f.write(linea)
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        pass  # el monitoreo nunca debe tumbar la corrida    


def fase_titulo(n, titulo):
    print("")
    print("-" * 62)
    print(" FASE " + str(n) + " - " + titulo)
    print("-" * 62)
    estado("FASE " + str(n) + " INICIO: " + titulo)


def normalizar(texto):
    mapa = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUNn")
    return texto.translate(mapa)


def extraer_json(texto):
    texto = texto.strip()
    if texto.startswith("```"):
        texto = texto.strip("`").strip()
        if texto.lower().startswith("json"):
            texto = texto[4:].strip()
    ini, fin = texto.find("{"), texto.rfind("}")
    if ini == -1 or fin == -1:
        raise ValueError("La respuesta no contiene JSON.")
    fragmento = texto[ini:fin + 1]

    # Intento 1: parsear directamente
    try:
        return json.loads(fragmento)
    except json.JSONDecodeError:
        pass

    # Intento 2: eliminar comas colgantes antes de } o ]
    fragmento_limpio = re.sub(r',\s*}', '}', fragmento)
    fragmento_limpio = re.sub(r',\s*]', ']', fragmento_limpio)
    try:
        return json.loads(fragmento_limpio)
    except json.JSONDecodeError:
        pass

    # Intento 3: extraer solo el array "ranking" o "perfiles" si existe
    for clave in ("ranking", "perfiles", "convergencias", "compatibilidad",
                  "constructos", "donantes"):
        m = re.search('"' + clave + '"\\s*:\\s*\\[', fragmento)
        if m:
            inicio_arr = fragmento.find('[', m.start())
            # buscar el ] de cierre balanceado
            profundidad = 0
            for idx in range(inicio_arr, len(fragmento)):
                if fragmento[idx] == '[':
                    profundidad += 1
                elif fragmento[idx] == ']':
                    profundidad -= 1
                    if profundidad == 0:
                        sub_array = fragmento[inicio_arr:idx + 1]
                        # limpiar comas colgantes en el array
                        sub_array = re.sub(r',\s*]', ']', sub_array)
                        try:
                            elementos = json.loads(sub_array)
                            return {clave: elementos}
                        except json.JSONDecodeError:
                            break
    raise ValueError("No se pudo parsear el JSON tras varios intentos.")


def groq_chat(messages, modelo, temperature=0.2):
    for _intento in range(4):
        try:
            response = client.chat.completions.create(
                model=modelo, messages=messages, temperature=temperature)
            return response.choices[0].message.content
        except Exception as e:
            s = str(e)
            if "rate" in s.lower() or "429" in s:
                log("Limite de tasa; esperando 30s ...", "warn")
                time.sleep(30); continue
            if "500" in s or "502" in s or "503" in s:
                log("Error temporal de Groq; reintentando ...", "warn")
                time.sleep(5); continue
            raise
    raise RuntimeError("Groq no respondio tras varios intentos.")


def groq_json(system, user, modelo, temperature=0.2):
    mensajes = [{"role": "system", "content": system},
                {"role": "user", "content": user}]
    bruto = groq_chat(mensajes, modelo, temperature=temperature)
    try:
        return extraer_json(bruto)
    except (ValueError, json.JSONDecodeError):
        mensajes.append({"role": "assistant", "content": bruto})
        mensajes.append({"role": "user",
                         "content": "Tu respuesta no era JSON valido. Devuelve SOLO el JSON."})
        return extraer_json(groq_chat(mensajes, modelo, temperature=0.0))


# ─────────────────────────────────────────────────────────────────────
# FASE 0 · ORQUESTACION: EL LLM SUGIERE DONANTES (NUEVO EN V4.2)
# ─────────────────────────────────────────────────────────────────────
def sugerir_donantes_llm(rasgo, receptora, modelo):
    """El LLM sugiere especies donantes para el rasgo objetivo.

    V4.6.1: cachea el panel en disco para que las corridas A/B y las
    comparaciones pfam auto/completo usen exactamente los mismos donantes.
    Para forzar un panel nuevo, borra el archivo panel_donantes_*.json.
    """
    rasgo_sano = "_".join(normalizar(rasgo).split())
    receptora_sana = "_".join(receptora["nombre"].split())
    panel_cache = Path("panel_donantes_" + rasgo_sano + "_" + receptora_sana + ".json")

    if panel_cache.exists():
        try:
            cached = json.loads(panel_cache.read_text(encoding="utf-8"))
            donantes = cached.get("donantes", [])
            if donantes:
                log("Usando panel de donantes cacheado: " + str(panel_cache), "ok")
                return donantes
        except Exception as e:
            log("Cache de donantes invalida (" + str(e) + "); regenerando ...", "warn")

    system = ("Eres experto en biologia de organismos extremos y mejoramiento "
              "genetico. Sugieres especies donantes cuyos genes podrian "
              "transferirse a una especie receptora para conferir un rasgo. "
              "Solo sugiere especies con nombre cientifico valido (genero y especie). "
              "Prioriza organismos con genoma secuenciado y bien anotado.")

    user = ("Rasgo objetivo: \"" + rasgo + "\"\n" +
            "Especie receptora: " + receptora["nombre"] + "\n\n" +
            "Sugiere entre 4 y 6 especies donantes (pueden ser plantas, bacterias, "
            "arqueas, hongos o levaduras) que tengan adaptaciones relevantes al rasgo. "
            "Para cada una indica:\n" +
            "- nombre_cientifico: nombre cientifico exacto (Genero especie)\n" +
            "- tipo: planta|bacteria|arquea|hongo|levadura\n" +
            "- adaptacion: descripcion breve de la adaptacion relevante\n" +
            "- genes_clave: lista de 1-3 genes o proteinas clave esperados\n\n" +
            "Devuelve SOLO JSON:\n" +
            '{"donantes":[{"nombre_cientifico":"...","tipo":"...",' +
            '"adaptacion":"...","genes_clave":["..."]}]}')

    try:
        data = groq_json(system, user, modelo, temperature=0.3)
        donantes = data.get("donantes", [])

        if donantes:
            try:
                panel_cache.write_text(
                    json.dumps({
                        "rasgo": rasgo,
                        "receptora": receptora["nombre"],
                        "donantes": donantes,
                    }, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                log("Panel de donantes guardado en cache: " + str(panel_cache), "ok")
            except Exception as e:
                log("No se pudo guardar cache de donantes: " + str(e), "warn")

        return donantes

    except Exception as e:
        log("El LLM no pudo sugerir donantes: " + str(e), "warn")
        return []


# ─────────────────────────────────────────────────────────────────────
# FASE 1 · RESOLUCION DE DONANTES (NUEVO EN V4.2)
# ─────────────────────────────────────────────────────────────────────
def resolver_tax_id(nombre_cientifico):
    """Resuelve un nombre cientifico a tax_id usando NCBI Taxonomy."""
    url = NCBI + "/esearch.fcgi"
    params = {"db": "taxonomy", "term": nombre_cientifico,
              "retmode": "json", "retmax": 1}
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if ids:
            return int(ids[0])
    except Exception as e:
        log("Error resolviendo tax_id de " + nombre_cientifico + ": " + str(e), "warn")
    return None


def verificar_genoma_disponible(tax_id):
    """Verifica si hay genoma de referencia disponible en NCBI Datasets."""
    url = NCBI_DATA + "/genome/taxon/" + str(tax_id) + "/dataset_report"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            reports = r.json().get("reports", [])
            return len(reports) > 0
    except Exception:
        pass
    return False


def sugerir_alternativa_llm(nombre_fallido, rasgo, modelo):
    """Si una especie no tiene genoma, el LLM sugiere una alternativa cercana."""
    system = ("Eres experto en taxonomia y genomica. Una especie sugerida no tiene "
              "genoma secuenciado disponible. Sugiere UNA especie filogeneticamente "
              "cercana que SI tenga genoma disponible y sea relevante para el rasgo. "
              "Solo devuelve el nombre cientifico.")
    user = ("La especie \"" + nombre_fallido + "\" no tiene genoma disponible.\n" +
            "Rasgo objetivo: \"" + rasgo + "\"\n" +
            "Sugiere una especie alternativa con genoma disponible.\n" +
            "Devuelve SOLO JSON: {\"alternativa\":\"Nombre cientifico\"}")
    try:
        data = groq_json(system, user, modelo, temperature=0.3)
        return data.get("alternativa", "")
    except Exception:
        return ""


def resolver_donantes(sugerencias, rasgo, modelo):
    """Orquesta la resolucion: nombre -> tax_id -> verificacion genoma.

    Devuelve una lista de donantes validos con tax_id confirmado y
    un registro de los descartados con la razon.
    """
    validos = []
    descartados = []
    nombres_vistos = set()

    for s in sugerencias:
        nombre = s.get("nombre_cientifico", "").strip()
        if not nombre:
            continue

        # Evitar duplicados
        nombre_norm = normalizar(nombre.lower())
        if nombre_norm in nombres_vistos:
            continue
        nombres_vistos.add(nombre_norm)

        log("Resolviendo: " + nombre)

        # Paso 1: resolver tax_id
        tax_id = resolver_tax_id(nombre)
        time.sleep(0.4)  # rate limit NCBI
        if not tax_id:
            log("  -> Nombre no encontrado en NCBI Taxonomy (posible alucinacion)", "warn")
            descartados.append({"nombre": nombre,
                                "razon": "No encontrado en NCBI Taxonomy"})
            continue

        # Paso 2: verificar genoma disponible
        tiene_genoma = verificar_genoma_disponible(tax_id)
        time.sleep(0.4)
        if tiene_genoma:
            log("  -> tax_id " + str(tax_id) + " con genoma disponible", "ok")
            validos.append({
                "nombre": nombre,
                "tax_id": tax_id,
                "tipo": s.get("tipo", ""),
                "adaptacion": s.get("adaptacion", ""),
                "genes_clave": s.get("genes_clave", []),
            })
            continue

        # Paso 3: no tiene genoma -> pedir alternativa al LLM
        log("  -> tax_id " + str(tax_id) + " SIN genoma disponible", "warn")
        log("  -> Solicitando alternativa al LLM ...")
        alternativa = sugerir_alternativa_llm(nombre, rasgo, modelo)
        if alternativa:
            log("  -> Alternativa sugerida: " + alternativa)
            tax_id_alt = resolver_tax_id(alternativa)
            time.sleep(0.4)
            if tax_id_alt and verificar_genoma_disponible(tax_id_alt):
                log("  -> Alternativa valida (tax_id " + str(tax_id_alt) + ")", "ok")
                validos.append({
                    "nombre": alternativa,
                    "tax_id": tax_id_alt,
                    "tipo": s.get("tipo", ""),
                    "adaptacion": s.get("adaptacion", ""),
                    "genes_clave": s.get("genes_clave", []),
                    "alternativa_de": nombre,
                })
                descartados.append({"nombre": nombre,
                                    "razon": "Sin genoma; reemplazada por " + alternativa})
            else:
                descartados.append({"nombre": nombre,
                                    "razon": "Sin genoma y alternativa no valida"})
        else:
            descartados.append({"nombre": nombre,
                                "razon": "Sin genoma disponible"})

    return validos, descartados


# ============================ FASE 2 · INGESTA ============================
def descargar_proteoma_especie(tax_id, nombre_limpio, destino_dir, max_proteinas=50000):
    """Descarga el proteoma de una especie donante.

    Usa dos estrategias en cascada:
      1. NCBI Datasets API (rapido, puede fallar con accessions GCA_)
      2. NCBI E-utilities (esearch+efetch, mas lento pero 100% confiable)
    """
    destino = destino_dir / ("proteoma_" + nombre_limpio + ".faa")
    if destino.exists() and destino.stat().st_size > 1000:
        log("Proteoma ya descargado: " + nombre_limpio)
        return destino

    # ── Estrategia 1: Datasets API ──
    log("Intentando Datasets API ...")
    resultado = _descargar_via_datasets(tax_id, nombre_limpio, destino)
    if resultado:
        return resultado

    # ── Estrategia 2: E-utilities (fallback confiable) ──
    log("Datasets API no funciono. Usando E-utilities ...", "warn")
    
    resultado = _descargar_via_eutils(
        tax_id,
        nombre_limpio,
        destino,
        max_proteins=max_proteinas
    )
    if resultado:
        return resultado

    log("No se pudo descargar el proteoma de " + nombre_limpio, "error")
    return None


def _descargar_via_datasets(tax_id, nombre_limpio, destino):
    """Estrategia 1: NCBI Datasets API."""
    url_report = NCBI_DATA + "/genome/taxon/" + str(tax_id) + "/dataset_report"
    try:
        r = requests.get(url_report, params={"reference": "true"}, timeout=60)
        if r.status_code != 200:
            r = requests.get(url_report, timeout=60)
        r.raise_for_status()
        reports = r.json().get("reports", [])
        if not reports:
            return None
        acc = reports[0].get("accession")
        if not acc:
            return None

        # Si es GCA_, intentar convertir a GCF_ (RefSeq)
        acc_descarga = acc
        if acc.startswith("GCA_"):
            acc_gcf = "GCF_" + acc[4:]
            log("  -> Convirtiendo " + acc + " a RefSeq " + acc_gcf)
            acc_descarga = acc_gcf

        url = (NCBI_DATA + "/genome/accession/" + acc_descarga +
               "/download?include=proteome:fasta")
        log("Descargando via Datasets (" + acc_descarga + ") ...")
        r = requests.get(url, timeout=300, headers={"Accept": "application/zip"})

        if r.status_code != 200 or len(r.content) < 10000:
            log("  -> Datasets API: ZIP vacio o error HTTP " + str(r.status_code), "warn")
            return None

        contenido = io.BytesIO(r.content)
        try:
            with zipfile.ZipFile(contenido) as z:
                faa = None
                for nombre_arch in z.namelist():
                    if nombre_arch.endswith(".faa"):
                        faa = nombre_arch
                        break
                if not faa:
                    log("  -> El ZIP no contiene .faa", "warn")
                    return None
                with z.open(faa) as fsrc, open(destino, "wb") as fdst:
                    fdst.write(fsrc.read())
            log("Proteoma descargado via Datasets API", "ok")
            return destino
        except zipfile.BadZipFile:
            return None
    except Exception as e:
        log("  -> Datasets API error: " + str(e), "warn")
        return None

def _obtener_ids_proteinas(tax_id, limite, refseq=True):
    """
    Obtiene IDs de proteinas desde NCBI Protein usando esearch por bloques.
    Si refseq=True, filtra por srcdb_refseq[PROP].
    limite <= 0 se interpreta como 1,000,000.
    """
    if limite <= 0:
        limite = 1000000

    term = "txid" + str(tax_id) + "[Organism]"
    if refseq:
        term += " AND srcdb_refseq[PROP]"

    ids = []
    total = 0
    retstart = 0
    chunk = 100000

    while len(ids) < limite:
        retmax_actual = min(chunk, limite - len(ids))

        params = {
            "db": "protein",
            "term": term,
            "retmode": "json",
            "retmax": str(retmax_actual),
            "retstart": str(retstart)
        }

        r = requests.get(NCBI + "/esearch.fcgi", params=params, timeout=120)
        r.raise_for_status()

        res = r.json().get("esearchresult", {})
        if not total:
            total = int(res.get("count", 0))

        batch = res.get("idlist", []) or []
        if not batch:
            break

        ids.extend(batch)
        retstart += len(batch)

        if len(batch) < retmax_actual:
            break

        time.sleep(0.5)

    return ids[:limite], total

def _descargar_via_eutils(tax_id, nombre_limpio, destino, max_proteins=50000):
    """Descarga proteinas RefSeq via E-utilities con control de limite."""
    log("Buscando proteinas RefSeq del tax_id " + str(tax_id) + " ...")

    try:
        limite_descarga = 1000000 if max_proteins <= 0 else max_proteins

        ids, total_encontradas = _obtener_ids_proteinas(
            tax_id,
            limite_descarga,
            refseq=True
        )

        log("  -> Encontradas " + str(total_encontradas) +
            " proteinas RefSeq; descargando hasta " + str(limite_descarga))

        if not ids:
            log("  -> Sin RefSeq; intentando sin filtro ...", "warn")
            ids, total_encontradas = _obtener_ids_proteinas(
                tax_id,
                limite_descarga,
                refseq=False
            )

        if not ids:
            return None

        if total_encontradas > limite_descarga and len(ids) >= limite_descarga:
            random.seed(tax_id)
            ids = random.sample(ids, limite_descarga)
            log("  -> Muestreadas " + str(limite_descarga) +
                " proteinas de " + str(total_encontradas), "warn")

        secuencias = []
        tamano_lote = 300
        total_lotes = (len(ids) + tamano_lote - 1) // tamano_lote
        lotes_ok = 0
        lotes_fallidos = 0

        for lote_num in range(total_lotes):
            inicio = lote_num * tamano_lote
            lote = ids[inicio:inicio + tamano_lote]

            if (lote_num + 1) % 20 == 0 or lote_num == 0 or lote_num == total_lotes - 1:
                log("  -> Lote " + str(lote_num + 1) + "/" + str(total_lotes) +
                    " (ok:" + str(lotes_ok) + " fail:" + str(lotes_fallidos) + ")")

            exito = False
            for intento in range(3):
                try:
                    r2 = requests.get(NCBI + "/efetch.fcgi", params={
                        "db": "protein",
                        "id": ",".join(lote),
                        "rettype": "fasta",
                        "retmode": "text"
                    }, timeout=120)

                    if r2.status_code == 200 and r2.text and ">" in r2.text:
                        secuencias.append(r2.text)
                        lotes_ok += 1
                        exito = True
                        break
                    else:
                        time.sleep(2)
                except Exception:
                    time.sleep(2)

            if not exito:
                lotes_fallidos += 1

            time.sleep(1.0)

        log("  -> Lotes completados: " + str(lotes_ok) + " ok, " +
            str(lotes_fallidos) + " fallidos",
            "ok" if lotes_fallidos < 5 else "warn")

        if not secuencias:
            return None

        with open(destino, "w", encoding="utf-8") as f:
            f.write("\n".join(secuencias))

        log("Proteoma guardado (" + str(len(ids)) + " proteinas descargadas)", "ok")
        return destino

    except Exception as e:
        log("  -> E-utilities error: " + str(e), "warn")
        return None


def parsear_fasta(ruta):
    """Parsea FASTA con manejo robusto de saltos de linea y secuencias cortas."""
    proteinas = []
    header = None
    seq_parts = []
    with open(ruta, "r", encoding="utf-8", errors="ignore") as fh:
        contenido = fh.read()

    # Normalizar saltos de linea y dividir por headers
    lineas = contenido.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
        if linea.startswith(">"):
            if header is not None:
                _guardar_prot(proteinas, header, "".join(seq_parts))
            header = linea[1:].strip()
            seq_parts = []
        else:
            seq_parts.append(linea)

    if header is not None:
        _guardar_prot(proteinas, header, "".join(seq_parts))

    return proteinas


def _guardar_prot(lista, header, seq):
    seq = seq.upper().replace("*", "")  # quitar stop codons
    if not seq or len(seq) < 30:  # minimo 30 aa (antes 50)
        return
    partes = header.split(None, 1)
    accession = partes[0]
    desc = partes[1] if len(partes) > 1 else ""
    desc = re.sub(r"\s*\[[^\]]*\]\s*$", "", desc).strip()
    lista.append({
        "accession": accession,
        "descripcion": desc,
        "secuencia": seq,
        "longitud": len(seq),
    })


def filtrar_por_estres(proteinas, keywords):
    """Filtra proteinas cuyas descripciones contienen keywords de estres."""
    candidatos = []
    for p in proteinas:
        desc_lower = p["descripcion"].lower()
        if any(k.lower() in desc_lower for k in keywords):
            candidatos.append(p)
    return candidatos


# ============================ FASE 3 · DOMINIOS ============================
def hmmer_disponible():
    return shutil.which("hmmscan") is not None and PFAM_FULL.exists()

def pfam_optima():
    """Sub-base genérica de estrés si existe; si no, Pfam completo.
    Mantenido solo por compatibilidad. La V4.6.1 usa seleccionar_base_pfam().
    """
    if PFAM_GENERIC.exists() and PFAM_GENERIC.stat().st_size > 100000:
        return PFAM_GENERIC, True
    return PFAM_FULL, False


def escanear_dominios_hmmer(proteinas, db_path, max_scan=200, etiqueta="Pfam"):
    """
    Escanea con hmmscan contra una base Pfam específica.
    Devuelve (dominios_por_prot, es_subbase).
    """
    dominios_por_prot = {}
    if not proteinas:
        return dominios_por_prot, str(db_path) != str(PFAM_FULL)

    seleccion = proteinas[:max_scan]

    with tempfile.NamedTemporaryFile("w", suffix=".fasta", delete=False) as fd:
        for p in seleccion:
            fd.write(">" + p["accession"] + "\n" + p["secuencia"] + "\n")
        fasta = fd.name

    domtbl = fasta + ".domtbl"
    es_subbase = str(db_path) != str(PFAM_FULL)

    t_inicio = time.time()
    log("hmmscan contra " + etiqueta + " (" + str(len(seleccion)) + " proteinas) ...")
    estado("HMMER INICIO: " + str(len(seleccion)) + " proteinas contra " + etiqueta +
           " (esto puede tardar minutos; el proceso hijo es hmmscan)")


    try:
        subprocess.run(
            [
                "hmmscan",
                "--domtblout", domtbl,
                "-E", "1e-3",
                "--domE", "1e-3",
                "--cpu", "4",
                str(db_path),
                fasta
            ],
            check=True,
            capture_output=True,
            timeout=3600
        )

        elapsed = time.time() - t_inicio
        log("hmmscan completado en " + str(round(elapsed, 1)) + " s", "ok")
        estado("HMMER FIN: " + str(round(elapsed, 1)) + " s")

        with open(domtbl) as fh:
            for linea in fh:
                if linea.startswith("#"):
                    continue
                campos = linea.split()
                if len(campos) < 4:
                    continue
                dom = campos[0]
                query = campos[3]
                dominios_por_prot.setdefault(query, []).append({"dominio": dom})

    except subprocess.TimeoutExpired:
        log("HMMER: timeout", "warn")
    except Exception as e:
        log("HMMER error: " + str(e), "warn")
    finally:
        for f in (fasta, domtbl):
            if os.path.exists(f):
                try:
                    os.unlink(f)
                except OSError:
                    pass

    return dominios_por_prot, es_subbase


def tiene_dominios_relevantes(dominios_lista, dominios_estres):
    if not dominios_lista:
        return []
    hits = []
    for d in dominios_lista:
        nombre = d.get("dominio", "")
        for clave in dominios_estres:
            if clave in nombre:
                hits.append(nombre)
    return hits

def preparar_muestra_hmmer(proteinas, n, seed=42):
    """Pre-filtro de calidad + muestreo reproducible para HMMER.
    NO usa keywords: la seleccion es estructuralmente agnostica."""
    EXCLUIR = ["transposable", "transposon", "retrotransposon",
               "fragment", "pseudogene", "hypothetical conserved"]
    limpias = []
    for p in proteinas:
        if p["longitud"] < 50:
            continue
        desc = p.get("descripcion", "").lower()
        if any(k in desc for k in EXCLUIR):
            continue
        limpias.append(p)
    if n <= 0 or len(limpias) <= n:
        return limpias
    random.seed(seed)
    return random.sample(limpias, n)


def filtrar_por_dominios_estres(candidatos, dominios_estres):
    """Devuelve solo candidatos con dominios de estres detectados por HMMER.
    Este es el CRITERIO PRIMARIO (estructural, no textual)."""
    resultado = []
    for c in candidatos:
        relevantes = tiene_dominios_relevantes(
            c.get("dominios_raw", []), dominios_estres)
        if relevantes:
            c["dominios_relevantes"] = relevantes
            resultado.append(c)
    return resultado



# ─────────────────────────────────────────────────────────────────────
# ESTRATEGIA DE SELECCION (NUEVO EN V4.2.1)
# ─────────────────────────────────────────────────────────────────────

def seleccionar_muestra_diversa(candidatos, total_muestra=30):
    """Selecciona muestra equilibrada por ESPECIE donante.

    Esto corrige el sesgo donde una especie procesada primero ocupaba
    todos los slots de su tipo/kingdom. Por ejemplo, si Xerophyta se
    procesa antes que Sorghum, ambas son 'planta', pero la version vieja
    podia llenar los 8 slots de planta solo con Xerophyta.
    """
    por_especie = {}
    for c in candidatos:
        esp = c.get("especie_donante") or c.get("tipo_donante") or "desconocido"
        por_especie.setdefault(esp, []).append(c)

    especies = list(por_especie.keys())
    n = len(especies)

    if n == 0:
        return candidatos[:total_muestra]

    slots_base = total_muestra // n
    resto = total_muestra % n

    seleccion = []
    for i, esp in enumerate(especies):
        slots = slots_base + (1 if i < resto else 0)
        seleccion.extend(por_especie[esp][:slots])

    return seleccion


def aplicar_estrategia_diversidad(candidatos, top):
    """Estrategia B: reordena candidatos para garantizar diversidad de tipos
    de organismo. Reserva al menos 1 slot por tipo presente y completa el
    resto con los de mayor score.

    La Estrategia A (sesgo) no necesita esta funcion: usa el ranking directo.
    """
    # Agrupar candidatos por tipo de organismo
    por_tipo = {}
    for c in candidatos:
        tipo = c.get("tipo_donante", "") or "desconocido"
        por_tipo.setdefault(tipo, []).append(c)

    # Ordenar cada grupo por score (mayor primero)
    for tipo in por_tipo:
        por_tipo[tipo].sort(key=lambda x: x.get("score_transferencia", 0), reverse=True)

    tipos_disponibles = list(por_tipo.keys())
    n_tipos = len(tipos_disponibles)

    if n_tipos == 0:
        return candidatos[:top]

    seleccion = []

    # Primera pasada: reservar 1 slot por tipo (el mejor de cada tipo)
    for tipo in tipos_disponibles:
        if por_tipo[tipo]:
            seleccion.append(por_tipo[tipo][0])

    # Si ya tenemos suficientes, recortar por score
    if len(seleccion) >= top:
        seleccion.sort(key=lambda x: x.get("score_transferencia", 0), reverse=True)
        return seleccion[:top]

    # Segunda pasada: completar con los mejores scores restantes
    restantes = []
    for tipo in tipos_disponibles:
        restantes.extend(por_tipo[tipo][1:])  # saltar el primero ya seleccionado
    restantes.sort(key=lambda x: x.get("score_transferencia", 0), reverse=True)

    slots_restantes = top - len(seleccion)
    seleccion.extend(restantes[:slots_restantes])

    # Ordenar seleccion final por score descendente
    seleccion.sort(key=lambda x: x.get("score_transferencia", 0), reverse=True)
    return seleccion[:top]


def loguear_distribucion(candidatos, titulo):
    """Muestra cuantos candidatos hay por tipo de organismo."""
    distribucion = {}
    for c in candidatos:
        tipo = c.get("tipo_donante", "") or "desconocido"
        distribucion[tipo] = distribucion.get(tipo, 0) + 1
    log(titulo, "ok")
    for tipo, cantidad in distribucion.items():
        log("  " + tipo + ": " + str(cantidad) + " candidatos")

def loguear_distribucion_especie(candidatos, titulo):
    """Muestra cuantos candidatos hay por especie donante."""
    dist = {}
    for c in candidatos:
        esp = c.get("especie_donante") or "desconocido"
        dist[esp] = dist.get(esp, 0) + 1

    log(titulo, "ok")
    for esp, cantidad in dist.items():
        log("  " + esp + ": " + str(cantidad) + " candidatos")




# ============================ FASE 4 · PRIORIZACION ============================
def priorizar_candidatos_donantes(candidatos, rasgo, especie_receptora, modelo, top=10):
    if not candidatos:
        return []

    # Limpieza: eliminar caracteres que pueden romper el JSON del LLM
    def limpiar(t):
        t = t.replace('"', "'")
        t = t.replace('\n', ' ')
        t = t.replace('\r', ' ')
        t = t.replace('\\', '/')
        return t.strip()

    listado = ""
    for i, p in enumerate(candidatos[:20]):  # reducido de 30 a 20
        desc_corta = limpiar(p.get("descripcion", "sin descripcion"))[:80]
        doms = ", ".join(p.get("dominios_relevantes", [])) or "ninguno"
        especie_d = limpiar(p.get("especie_donante", "?"))
        listado += (str(i + 1) + ". " + limpiar(p["accession"]) +
                    " | " + especie_d +
                    " | " + desc_corta +
                    " | dominios: " + doms + "\n")

    system = ("Eres experto en biologia sintetica y mejoramiento genetico. Evaluas genes "
              "de especies donantes extremas para determinar su potencial de transferencia "
              "a una especie receptora mediante ingenieria genetica.")
    user = ("Rasgo objetivo: \"" + rasgo + "\"\n" +
            "Especie receptora: " + especie_receptora["nombre"] + "\n\n" +
            "Candidatos de especies donantes:\n" + listado + "\n" +
            "Instrucciones:\n" +
            "1. Puntua cada gen de 0 a 100 segun su potencial para conferir el rasgo.\n" +
            "2. Indica el mecanismo de accion esperado.\n" +
            "3. Senala riesgos potenciales (toxicidad, incompatibilidad metabolica).\n\n" +
            "Devuelve SOLO JSON:\n" +
            '{"ranking":[{"accession":"...","score":85,"mecanismo":"...","riesgos":["..."],"especie_donante":"..."}]}')

    try:
        data = groq_json(system, user, modelo)
    except (ValueError, json.JSONDecodeError) as e:
        log("El LLM devolvio JSON invalido en priorizacion: " + str(e), "warn")
        log("Reintentando con modelo rapido ...", "warn")
        try:
            data = groq_json(system, user, MODELOS["rapido"])
        except Exception:
            log("No se pudo priorizar; continuando sin ranking LLM.", "error")
            return []
        
    scores = {}
    for x in data.get("ranking", []):
        if isinstance(x, dict) and "accession" in x:
            scores[x["accession"]] = x

    resultado = []
    for p in candidatos:
        m = scores.get(p["accession"])
        p["score_transferencia"] = int(m.get("score", 0)) if m else 0
        p["mecanismo"] = (m or {}).get("mecanismo", "")
        p["riesgos"] = (m or {}).get("riesgos", [])
        resultado.append(p)

    resultado.sort(key=lambda x: x["score_transferencia"], reverse=True)
    return resultado[:top]


# ============================ FASE 5 · COMPATIBILIDAD ============================
# ─────────────────────────────────────────────────────────────────────
# MODO EXHAUSTIVO: PRE-RANQUEO HEURISTICO + LLM POR LOTES
# ─────────────────────────────────────────────────────────────────────
def contar_keywords_desc(c, keywords):
    """Cuenta cuantas keywords del rasgo aparecen en la descripcion."""
    desc = normalizar(c.get("descripcion", "").lower())
    contador = 0
    for k in keywords:
        kk = normalizar(str(k).lower())
        if kk and kk in desc:
            contador += 1
    return contador


def calcular_pre_score(c, keywords):
    """Score heuristico barato, sin LLM.

    Idea:
      - dominios de estrés detectados por HMMER pesan mucho
      - keywords en descripcion ayudan como criterio secundario
      - longitud razonable da pequeno bonus
    """
    doms = c.get("dominios_relevantes", []) or []
    dom_uniq = len(set(doms))

    kw = contar_keywords_desc(c, keywords)

    longitud = int(c.get("longitud", 0) or 0)
    bonus_len = 0
    if 80 <= longitud <= 1200:
        bonus_len = 3
    elif 1200 < longitud <= 2000:
        bonus_len = 1

    score = (dom_uniq * 20) + (kw * 5) + bonus_len
    return int(score)


def pre_ranquear_candidatos(candidatos, keywords, top_por_especie=80):
    """Pre-ranquea candidatos por especie usando score heuristico.

    Devuelve una lista con los mejores 'top_por_especie' de cada especie.
    No usa LLM todavia.
    """
    por_especie = {}

    for c in candidatos:
        c["pre_score"] = calcular_pre_score(c, keywords)
        esp = c.get("especie_donante") or "desconocido"
        por_especie.setdefault(esp, []).append(c)

    seleccion = []
    for esp, lst in por_especie.items():
        lst.sort(key=lambda x: x.get("pre_score", 0), reverse=True)
        seleccion.extend(lst[:top_por_especie])

    seleccion.sort(key=lambda x: x.get("pre_score", 0), reverse=True)
    return seleccion


def intercalar_por_especie(candidatos):
    """Intercala candidatos por especie para que los lotes al LLM no
    queden dominados por una sola especie.

    Supone que cada lista interna ya esta ordenada por pre_score.
    """
    por_especie = {}
    for c in candidatos:
        esp = c.get("especie_donante") or "desconocido"
        por_especie.setdefault(esp, []).append(c)

    especies = list(por_especie.keys())
    if not especies:
        return []

    salida = []
    i = 0

    while any(por_especie.values()):
        esp = especies[i % len(especies)]
        if por_especie[esp]:
            salida.append(por_especie[esp].pop(0))
        i += 1

    return salida


def priorizar_candidatos_donantes_por_lotes(
    candidatos, rasgo, especie_receptora, modelo,
    top=10, lote=20, max_lotes=5
):
    """Envia candidatos al LLM en lotes pequenos y mergea rankings.

    Esto permite modo exhaustivo sin mandar 2000 candidatos de golpe.
    """
    if not candidatos:
        return []

    limite = min(len(candidatos), lote * max_lotes)
    candidatos = candidatos[:limite]

    log("Modo exhaustivo: evaluando " + str(limite) +
        " candidatos en lotes de " + str(lote) +
        " (max " + str(max_lotes) + " lotes)", "fase")

    todos_ranked = []

    for idx, inicio in enumerate(range(0, limite, lote), start=1):
        batch = candidatos[inicio:inicio + lote]
        log("  Lote LLM " + str(idx) + ": " + str(len(batch)) + " candidatos ...")
        estado("LOTE LLM " + str(idx) + " INICIO: " + str(len(batch)) + " candidatos")

        try:
            ranked = priorizar_candidatos_donantes(
                batch,
                rasgo,
                especie_receptora,
                modelo,
                top=len(batch)
            )
            todos_ranked.extend(ranked)
        except Exception as e:
            log("  Lote LLM " + str(idx) + " fallo: " + str(e), "warn")

        estado("LOTE LLM " + str(idx) + " FIN")
        time.sleep(1.0)

    if not todos_ranked:
        log("Ningun lote LLM exitoso; usando pre_score como ranking heuristico.", "warn")
        final = sorted(
            candidatos,
            key=lambda x: x.get("pre_score", 0),
            reverse=True
        )[:top]

        for c in final:
            c["score_transferencia"] = int(c.get("pre_score", 0))
            c.setdefault("mecanismo", "heuristico: dominios de estres + keywords")
            c.setdefault("riesgos", [])

        return final



    # Merge: conservar el mejor score por accession
    mejor = {}
    for c in todos_ranked:
        acc = c.get("accession")
        if not acc:
            continue
        if acc not in mejor:
            mejor[acc] = c
        else:
            if c.get("score_transferencia", 0) > mejor[acc].get("score_transferencia", 0):
                mejor[acc] = c

    final = sorted(
        mejor.values(),
        key=lambda x: x.get("score_transferencia", 0),
        reverse=True
    )

    return final[:top]



def evaluar_compatibilidad(candidatos, especie_receptora, modelo):
    listado = ""
    for i, p in enumerate(candidatos[:10]):
        listado += (str(i + 1) + ". " + p["accession"] +
                    " | " + p.get("especie_donante", "?") +
                    " | mecanismo: " + p.get("mecanismo", "?") +
                    " | score: " + str(p.get("score_transferencia", 0)) + "\n")

    system = ("Eres experto en compatibilidad genetica. Evalua si un gen de una especie "
              "donante puede transferirse funcionalmente a una especie receptora.")
    user = ("Especie receptora: " + especie_receptora["nombre"] + "\n\n" +
            "Candidatos a evaluar:\n" + listado + "\n" +
            "Para cada gen indica:\n" +
            "1. Si tiene ortologos conocidos en la receptora (si/no/no_se).\n" +
            "2. Estrategia recomendada: 'edicion_genica' si hay ortologo, 'transgenesis' si no.\n" +
            "3. Nivel de riesgo de toxicidad o incompatibilidad (bajo/medio/alto).\n" +
            "4. Justificacion breve.\n\n" +
            "Devuelve SOLO JSON:\n" +
            '{"compatibilidad":[{"accession":"...","tiene_ortologo":"si|no|no_se",' +
            '"estrategia":"edicion_genica|transgenesis","riesgo":"bajo|medio|alto",' +
            '"justificacion":"..."}]}')

    data = groq_json(system, user, modelo)
    compat = {}
    for x in data.get("compatibilidad", []):
        if isinstance(x, dict) and "accession" in x:
            compat[x["accession"]] = x

    for p in candidatos:
        c = compat.get(p["accession"], {})
        p["tiene_ortologo"] = c.get("tiene_ortologo", "no_se")
        p["estrategia"] = c.get("estrategia", "transgenesis")
        p["riesgo_compatibility"] = c.get("riesgo", "medio")
        p["justificacion_compat"] = c.get("justificacion", "")

    return candidatos


# ============================ FASE 6 · DISENO DE CONSTRUCTO ============================
def disenar_constructos(candidatos, especie_receptora, modelo):
    listado = ""
    for i, p in enumerate(candidatos[:5]):
        listado += (str(i + 1) + ". " + p["accession"] +
                    " | " + p.get("especie_donante", "?") +
                    " | estrategia: " + p.get("estrategia", "?") +
                    " | mecanismo: " + p.get("mecanismo", "?") + "\n")

    system = ("Eres experto en diseno de constructos geneticos para transformacion de plantas. "
              "Disenas constructos optimizados para expresion heterologa.")
    user = ("Especie receptora: " + especie_receptora["nombre"] + "\n\n" +
            "Candidatos para diseno de constructo:\n" + listado + "\n" +
            "Para cada gen indica:\n" +
            "1. Promotor recomendado (constitutivo, tejido-especifico, inducible).\n" +
            "2. Localizacion subcelular sugerida (citosol, cloroplasto, vacuola, membrana).\n" +
            "3. Necesidad de codon optimization (si/no).\n" +
            "4. Notas de diseno adicionales.\n\n" +
            "Devuelve SOLO JSON:\n" +
            '{"constructos":[{"accession":"...","promotor":"...","localizacion":"...",' +
            '"codon_opt":"si|no","notas":"..."}]}')

    data = groq_json(system, user, modelo)
    constructos = {}
    for x in data.get("constructos", []):
        if isinstance(x, dict) and "accession" in x:
            constructos[x["accession"]] = x

    for p in candidatos:
        c = constructos.get(p["accession"], {})
        p["promotor"] = c.get("promotor", "")
        p["localizacion"] = c.get("localizacion", "")
        p["codon_opt"] = c.get("codon_opt", "")
        p["notas_constructo"] = c.get("notas", "")

    return candidatos


# ============================ FASE 7 · BRAZO A ============================
def brazo_a_modelos(rasgo, especie_receptora, keywords):
    """Brazo A: genes conocidos en la especie receptora."""
    tax_id = especie_receptora["tax_id"]
    if not keywords:
        return []

    term = "(" + " OR ".join(keywords) + ") AND txid" + str(tax_id) + "[Organism]"
    try:
        r = requests.get(NCBI + "/esearch.fcgi",
                         params={"db": "gene", "term": term, "retmax": 30,
                                 "retmode": "json", "sort": "relevance"}, timeout=60)
        r.raise_for_status()
        ids = r.json()["esearchresult"]["idlist"]
        if not ids:
            return []
        time.sleep(0.4)
        r2 = requests.get(NCBI + "/esummary.fcgi",
                          params={"db": "gene", "id": ",".join(ids), "retmode": "json"},
                          timeout=60)
        r2.raise_for_status()
        res = r2.json().get("result", {})
        genes = []
        for gid in ids:
            d = res.get(gid)
            if not d:
                continue
            genes.append({"simbolo": d.get("name", "?"),
                          "descripcion": d.get("description", "")})
            if len(genes) >= 10:
                break
        return genes
    except Exception as e:
        log("Brazo A fallo: " + str(e), "warn")
        return []


# ─────────────────────────────────────────────────────────────────────
# FASE 5 · VALIDACION MULTI-FUENTE (NUEVO EN V4.2)
# ─────────────────────────────────────────────────────────────────────
def buscar_europepmc(accession, descripcion=""):
    """Busca menciones del gen/proteina en Europe PMC.

    V4.6.1: distingue tres estados:
      - NOVEL            -> consultado OK, 0 menciones (novedad confirmada)
      - <N> menciones    -> consultado OK, N menciones
      - UNKNOWN (...)    -> no se pudo consultar (timeout/error); NO se afirma novedad
    """
    resultados = {
        "menciones": 0,
        "novel": None,          # True / False / None (=UNKNOWN)
        "articulos": [],
        "estado": "UNKNOWN (sin consultar)",
        "consultado": False,
        "error": "",
    }

    query = '"' + accession + '"'
    ult_error = ""

    for intento in range(3):
        try:
            r = requests.get(
                EUROPEPMC,
                params={"query": query, "format": "json", "pageSize": 5},
                timeout=30,
            )

            if r.status_code == 200:
                data = r.json()
                menciones = int(data.get("hitCount", 0))
                resultados["menciones"] = menciones
                resultados["consultado"] = True

                if menciones == 0:
                    resultados["novel"] = True
                    resultados["estado"] = "NOVEL"
                else:
                    resultados["novel"] = False
                    resultados["estado"] = str(menciones) + " menciones"

                lista = data.get("resultList", {}).get("result", [])
                for art in lista[:3]:
                    resultados["articulos"].append({
                        "titulo": (art.get("title") or "")[:120],
                        "anio": art.get("pubYear", ""),
                        "fuente": art.get("source", ""),
                    })
                return resultados

            elif r.status_code == 429:
                ult_error = "HTTP 429 rate limit"
                log("  Europe PMC rate limit; reintento " + str(intento + 1) + " ...", "warn")
                time.sleep(5 * (intento + 1))
                continue
            else:
                ult_error = "HTTP " + str(r.status_code)
                log("  Europe PMC error " + ult_error + "; reintento " + str(intento + 1) + " ...", "warn")
                time.sleep(2 * (intento + 1))
                continue

        except Exception as e:
            ult_error = str(e)
            log("  Europe PMC fallo de red/intento " + str(intento + 1) + ": " + ult_error, "warn")
            time.sleep(3 * (intento + 1))

    # Llegó aquí => 3 intentos fallidos => NO podemos afirmar novedad
    resultados["menciones"] = 0
    resultados["novel"] = None
    resultados["consultado"] = False
    resultados["estado"] = "UNKNOWN (" + ult_error[:80] + ")"
    resultados["error"] = ult_error
    return resultados


def buscar_string(accession, tax_id):
    """Busca interacciones proteina-proteina en STRING.
    Devuelve el numero de partners y sus nombres para validar que la
    proteina participa en redes funcionales relevantes."""
    resultados = {"interacciones": 0, "partners": [], "encontrado": False}
    if not tax_id:
        return resultados
    try:
        r = requests.get(STRING_API, params={
            "identifiers": accession,
            "species": tax_id,
            "required_score": 400,
            "limit": 10
        }, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if data and isinstance(data, list):
                resultados["encontrado"] = True
                resultados["interacciones"] = len(data)
                for inter in data[:10]:
                    partner = inter.get("preferredName_B", "")
                    if partner:
                        resultados["partners"].append(partner)
    except Exception as e:
        log("  STRING error: " + str(e), "warn")
    return resultados


def buscar_geo(especie_nombre, rasgo):
    """Busca datasets de expresion en GEO para el organismo + rasgo.
    Indica si hay datos experimentales disponibles para validar el
    candidato (RNA-seq o microarrays bajo el estres de interes)."""
    resultados = {"datasets": 0, "ids": []}
    terminos = TERMINOS_GEO.get(normalizar(rasgo), rasgo)
    query = especie_nombre + "[Organism] AND (" + terminos + ")"
    try:
        r = requests.get(NCBI + "/esearch.fcgi", params={
            "db": "gds",
            "term": query,
            "retmode": "json",
            "retmax": 20
        }, timeout=30)
        if r.status_code == 200:
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            resultados["datasets"] = len(ids)
            resultados["ids"] = ids[:5]
    except Exception as e:
        log("  GEO error: " + str(e), "warn")
    return resultados


def calcular_soporte(epmc, string_res, geo):
    """Calcula un indice de validabilidad (0-100) combinando las 3 fuentes.
    Mide cuanta evidencia independiente existe para validar el candidato."""
    soporte = 0
    fuentes = []

    # Europe PMC: solo suma literatura si hubo menciones confirmadas
    if epmc.get("consultado") and epmc["menciones"] > 0:
        soporte += 25
        fuentes.append("literatura")

    # STRING: interacciones en red (hasta 40 puntos)
    if string_res["interacciones"] > 0:
        puntos = min(40, string_res["interacciones"] * 5)
        soporte += puntos
        fuentes.append("interacciones")

    # GEO: datasets de expresion disponibles (hasta 35 puntos)
    if geo["datasets"] > 0:
        puntos = min(35, geo["datasets"] * 5)
        soporte += puntos
        fuentes.append("expresion")

    return {"score": min(100, soporte), "fuentes": fuentes}


def validar_multifuente(candidatos, donantes_validos, rasgo):
    """Valida cada candidato priorizado con Europe PMC, STRING y GEO.
    Anade campos val_epmc, val_string, val_geo y soporte_multifuente."""
    # Mapa nombre de especie -> info del donante (para obtener tax_id)
    donantes_map = {}
    for d in donantes_validos:
        donantes_map[d["nombre"]] = d

    # Cache de GEO por (especie, rasgo) para no repetir busquedas
    geo_cache = {}

    for c in candidatos:
        acc = c.get("accession", "")
        acc_base = acc.split(".")[0]
        esp_donante = c.get("especie_donante", "")
        donante_info = donantes_map.get(esp_donante, {})
        tax_id_donante = donante_info.get("tax_id")

        log("Validando " + c["accession"] + " (" + c.get("especie_donante", "?") + ") ...")
        estado("VALIDANDO " + c["accession"] + " (" + c.get("especie_donante", "?") + ")")

        # 1. Europe PMC (novedad + literatura)
        epmc = buscar_europepmc(acc_base, c.get("descripcion", ""))
        c["val_epmc"] = epmc
        estado_pmc = epmc.get("estado", "UNKNOWN")
        if estado_pmc == "NOVEL":
            nivel_log = "ok"
        elif str(estado_pmc).startswith("UNKNOWN"):
            nivel_log = "warn"
        else:
            nivel_log = "dato"

        log("  Europe PMC: " + estado_pmc, nivel_log)
        time.sleep(0.3)

        # 2. STRING (interacciones proteicas)
        string_res = buscar_string(acc_base, tax_id_donante)
        c["val_string"] = string_res
        log("  STRING: " + str(string_res["interacciones"]) + " interacciones")
        time.sleep(0.3)

        # 3. GEO (datasets de expresion, cacheado por especie)
        clave_geo = esp_donante + "|" + rasgo
        if clave_geo not in geo_cache:
            geo_cache[clave_geo] = buscar_geo(esp_donante, rasgo)
            time.sleep(0.4)
        geo = geo_cache[clave_geo]
        c["val_geo"] = geo

        # Calcular indice de soporte combinado
        c["soporte_multifuente"] = calcular_soporte(epmc, string_res, geo)
        log("  GEO: " + str(geo["datasets"]) + " datasets | Soporte: " +
            str(c["soporte_multifuente"]["score"]) + "/100")

    return candidatos


# ============================ INFORME ============================
def escribir_informe_v50(ruta, informe):
    ruta = Path(ruta)
    ruta.with_suffix(".json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# Busqueda Trans-especie Orquestada · AgroGenIA V5.0",
          "",
          "- **Fecha:** " + informe.get("fecha", "?"),
          "- **Estrategia de seleccion:** " + informe.get("estrategia", "?"),
          "- **Panel de donantes:** " + informe.get("panel_modo", "?"),
          "- **Max proteinas por especie:** " + str(informe.get("max_proteinas_especie", "?")),
          "- **Modo de busqueda:** " + informe.get("modo_detalle", informe.get("modo", "?")),          
          "- **Rasgo objetivo:** " + informe.get("rasgo", "?"),
          "- **Receptora (input usuario):** " + informe.get("receptora_input", "?"),
          "- **Especie receptora resuelta:** *" + informe.get("receptora", "?") + "*",
          "- **Tax_id receptora:** " + str(informe.get("receptora_tax_id", "?")),
          "- **Tipo receptora:** " + informe.get("receptora_tipo", "?"),
          "- **Proteoma receptora:** " + (informe.get("receptora_proteoma") or "no descargado"),
          "- **Proteinas receptora:** " + str(informe.get("receptora_proteinas", 0)),
          "- **Base Pfam:** " + informe.get("pfam_base", "?"),
          "- **Modo Pfam:** " + informe.get("pfam_modo", "?"),
          "- **Especies donantes validas:** " + str(len(informe.get("donantes_validos", []))),
          "- **Especies descartadas:** " + str(len(informe.get("donantes_descartados", []))),
          "- **Candidatos priorizados:** " + str(len(informe.get("candidatos", []))),
          "",
          "## Especies donantes sugeridas por el LLM",
          ""]

    if informe.get("donantes_validos"):
        md.append("### Aceptadas (con genoma disponible)")
        md.append("")
        for d in informe["donantes_validos"]:
            alt = ""
            if d.get("alternativa_de"):
                alt = " (alternativa de " + d["alternativa_de"] + ")"
            md.append("- **" + d["nombre"] + "** (tax_id " + str(d["tax_id"]) + ")" + alt)
            md.append("  - Tipo: " + d.get("tipo", "?"))
            md.append("  - Adaptacion: " + d.get("adaptacion", "?"))
            md.append("  - Genes clave: " + ", ".join(d.get("genes_clave", [])))
        md.append("")

    if informe.get("donantes_descartados"):
        md.append("### Descartadas")
        md.append("")
        for d in informe["donantes_descartados"]:
            md.append("- ~~" + d["nombre"] + "~~ → " + d["razon"])
        md.append("")

    md.append("## Candidatos para transferencia")
    md.append("")
    md.append("| # | Accession | Donante | Score | Soporte | Europe PMC | Estrategia | Riesgo |")
    md.append("|---|---|---|---|---|---|---|---|")

    for i, p in enumerate(informe.get("candidatos", []), 1):
        epmc_t = p.get("val_epmc", {})
        soporte_t = p.get("soporte_multifuente", {})
        estado_t = epmc_t.get("estado") or (
            "NOVEL" if epmc_t.get("novel") is True
            else ("UNKNOWN" if epmc_t.get("novel") is None
                  else str(epmc_t.get("menciones", 0)) + " menc.")
        )
        md.append("| " + str(i) +
                  " | " + p.get("accession", "?") +
                  " | " + p.get("especie_donante", "?") +
                  " | " + str(p.get("score_transferencia", 0)) +
                  " | " + str(soporte_t.get("score", 0)) + "/100" +
                  " | " + estado_t +
                  " | " + p.get("estrategia", "?") +
                  " | " + p.get("riesgo_compatibility", "?") + " |")

    md.append("")
    md.append("## Detalles de candidatos")
    md.append("")
    for i, p in enumerate(informe.get("candidatos", []), 1):
        md.append("### " + str(i) + ". " + p.get("accession", "?"))
        md.append("- **Especie donante:** " + p.get("especie_donante", "?"))
        md.append("- **Score de transferencia:** " + str(p.get("score_transferencia", 0)))
        # ── Validacion multi-fuente (V4.2) ──
        epmc = p.get("val_epmc", {})
        string_v = p.get("val_string", {})
        geo_v = p.get("val_geo", {})
        soporte = p.get("soporte_multifuente", {})

        estado_epmc = epmc.get("estado") or (
            "NOVEL" if epmc.get("novel") is True
            else ("UNKNOWN" if epmc.get("novel") is None
                  else str(epmc.get("menciones", 0)) + " menciones")
        )
        md.append("- **Europe PMC:** " + estado_epmc)

        if epmc.get("articulos"):
            for art in epmc["articulos"][:2]:
                md.append("  - " + art.get("titulo", "") + " (" + str(art.get("anio", "")) + ")")
        md.append("- **STRING:** " + str(string_v.get("interacciones", 0)) + " interacciones")
        if string_v.get("partners"):
            md.append("  - Partners: " + ", ".join(string_v["partners"][:5]))
        md.append("- **GEO:** " + str(geo_v.get("datasets", 0)) + " datasets de expresion disponibles")
        md.append("- **Soporte multi-fuente:** " + str(soporte.get("score", 0)) + "/100 (" +
                  ", ".join(soporte.get("fuentes", [])) + ")")


        md.append("- **Mecanismo:** " + p.get("mecanismo", "?"))
        md.append("- **Tiene ortologo en receptora:** " + p.get("tiene_ortologo", "?"))
        md.append("- **Estrategia:** " + p.get("estrategia", "?"))
        md.append("- **Riesgo de compatibilidad:** " + p.get("riesgo_compatibility", "?"))
        md.append("- **Justificacion:** " + p.get("justificacion_compat", "?"))
        md.append("- **Promotor:** " + p.get("promotor", "?"))
        md.append("- **Localizacion:** " + p.get("localizacion", "?"))
        md.append("- **Codon optimization:** " + p.get("codon_opt", "?"))
        md.append("- **Riesgos potenciales:** " + ", ".join(p.get("riesgos", [])))
        md.append("")

    md.append("## Genes conocidos en receptora (Brazo A)")
    md.append("")
    if informe.get("genes_brazo_a"):
        for g in informe["genes_brazo_a"]:
            md.append("- **" + g.get("simbolo", "?") + "**: " + g.get("descripcion", "?"))
    else:
        md.append("_No se encontraron genes conocidos._")

    md.append("")
    md.append("> La seleccion de donantes fue orquestada por el LLM. "
              "Los candidatos requieren validacion experimental antes de su uso.")

    ruta.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
    return ruta.with_suffix(".json"), ruta.with_suffix(".md")

# ============================ RECEPTORA DINAMICA (V5.0) ============================

RECEPTORA_ALIASES = {
    # Yuca / mandioca
    "yuca": "Manihot esculenta",
    "mandioca": "Manihot esculenta",
    "casabe": "Manihot esculenta",
    "manihot": "Manihot esculenta",

    # Fresa
    "fresa": "Fragaria vesca",
    "strawberry": "Fragaria vesca",
    "wild strawberry": "Fragaria vesca",
    "woodland strawberry": "Fragaria vesca",
    "fresa silvestre": "Fragaria vesca",
    "fresa cultivada": "Fragaria × ananassa",
    "garden strawberry": "Fragaria × ananassa",
    "ananassa": "Fragaria × ananassa",

    # Modelos / cultivos comunes
    "arabidopsis": "Arabidopsis thaliana",
    "thaliana": "Arabidopsis thaliana",
    "arroz": "Oryza sativa",
    "rice": "Oryza sativa",
    "tomate": "Solanum lycopersicum",
    "tomate jitomate": "Solanum lycopersicum",
    "tomato": "Solanum lycopersicum",
    "maiz": "Zea mays",
    "corn": "Zea mays",
    "soya": "Glycine max",
    "soja": "Glycine max",
    "soybean": "Glycine max",
    "trigo": "Triticum aestivum",
    "wheat": "Triticum aestivum",
    "cebada": "Hordeum vulgare",
    "barley": "Hordeum vulgare",
    "patata": "Solanum tuberosum",
    "papa": "Solanum tuberosum",
    "potato": "Solanum tuberosum",
    "cafe": "Coffea arabica",
    "coffee": "Coffea arabica",
    "cacao": "Theobroma cacao",
    "cocoa": "Theobroma cacao",
    "platano": "Musa acuminata",
    "banano": "Musa acuminata",
    "banana": "Musa acuminata",
    "coco": "Cocos nucifera",
    "coconut": "Cocos nucifera",
    "pinon": "Pinus taeda",
    "eucalipto": "Eucalyptus grandis",
    "citricos": "Citrus sinensis",
    "naranja": "Citrus sinensis",
    "orange": "Citrus sinensis",
    "limon": "Citrus limon",
    "lemon": "Citrus limon",
    "vinifera": "Vitis vinifera",
    "uva": "Vitis vinifera",
    "grape": "Vitis vinifera",
}


def _limpiar_nombre_archivo(nombre):
    """Convierte un nombre científico en un nombre seguro para archivo."""
    s = str(nombre)
    s = s.replace("×", "x")
    s = s.replace("*", "")
    s = s.replace("/", "-")
    s = s.replace(" ", "_")
    s = normalizar(s)
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


def _unicar(lista):
    """Devuelve únicos preservando orden, usando nombre normalizado."""
    vistos = set()
    salida = []
    for x in lista:
        k = normalizar(str(x).lower())
        if k and k not in vistos:
            vistos.add(k)
            salida.append(x)
    return salida


def _ncbi_taxonomy_ids(query, retmax=5):
    """Busca tax_ids en NCBI Taxonomy."""
    try:
        r = requests.get(
            NCBI + "/esearch.fcgi",
            params={
                "db": "taxonomy",
                "term": query,
                "retmode": "json",
                "retmax": str(retmax),
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("esearchresult", {}).get("idlist", []) or []
    except Exception as e:
        log("NCBI Taxonomy esearch error: " + str(e), "warn")
        return []


def _ncbi_taxonomy_summary(tax_id):
    """Obtiene nombre científico y linaje desde NCBI Taxonomy."""
    try:
        r = requests.get(
            NCBI + "/esummary.fcgi",
            params={
                "db": "taxonomy",
                "id": str(tax_id),
                "retmode": "json",
            },
            timeout=30,
        )
        r.raise_for_status()
        res = r.json().get("result", {})
        d = res.get(str(tax_id)) or {}

        nombre = (
            d.get("scientificname")
            or d.get("scientificName")
            or d.get("OtherNames", {}).get("ScientificName", "")
            or ""
        )

        return {
            "tax_id": int(tax_id),
            "nombre": nombre,
            "lineage": d.get("lineage", ""),
            "rank": d.get("rank", ""),
        }
    except Exception as e:
        log("NCBI Taxonomy esummary error: " + str(e), "warn")
        return None


def _inferir_tipo_receptora(lineage):
    """Inferir tipo biológico grueso a partir del linaje NCBI."""
    lin = normalizar(str(lineage).lower())

    if "viridiplantae" in lin or "embryophyta" in lin or "magnoliophyta" in lin:
        return "planta"
    if "fungi" in lin:
        if "saccharomycetes" in lin or "yeast" in lin:
            return "levadura"
        return "hongo"
    if "bacteria" in lin:
        return "bacteria"
    if "archaea" in lin:
        return "arquea"
    return "eucariota"


def _score_coincidencia(nombre_objetivo, nombre_ncbi):
    """Puntúa qué tan bien coincide un nombre buscado con el nombre NCBI."""
    a = normalizar(str(nombre_objetivo).lower()).replace("×", "x")
    b = normalizar(str(nombre_ncbi).lower()).replace("×", "x")

    a = " ".join(a.split())
    b = " ".join(b.split())

    if not a or not b:
        return 0

    if a == b:
        return 100

    if b.startswith(a) or a.startswith(b):
        return 85

    pa = a.split()
    pb = b.split()

    if len(pa) >= 2 and len(pb) >= 2:
        if pa[0] == pb[0] and pa[1][:3] == pb[1][:3]:
            return 78
        if pa[0] == pb[0]:
            return 45

    if a in b or b in a:
        return 40

    return 0


def _variantes_nombre(nombre):
    """Genera variantes útiles para buscar en NCBI Taxonomy."""
    n = str(nombre).strip()
    variantes = [n]

    n2 = n.replace("×", "x").replace("*", "")
    if n2 != n:
        variantes.append(n2)

    partes = n2.split()
    if len(partes) == 3 and partes[1].lower() in ("x", "hybrid", "var"):
        variantes.append(partes[0] + " " + partes[2])

    if len(partes) >= 2:
        variantes.append(partes[0] + " " + partes[1])

    return _unicar(variantes)


def _resolver_tax_id_por_nombre(nombre):
    """
    Intenta resolver un nombre científico o común a un tax_id NCBI.
    Devuelve dict con tax_id, nombre, lineage, rank o None.
    """
    mejor = None
    mejor_score = -1

    for var in _variantes_nombre(nombre):
        queries = [
            '"' + var + '"[Organism]',
            var + "[Organism]",
            var + "[All Fields]",
        ]

        for q in queries:
            ids = _ncbi_taxonomy_ids(q, retmax=5)
            for tid in ids:
                summ = _ncbi_taxonomy_summary(tid)
                if not summ or not summ.get("nombre"):
                    continue

                score = _score_coincidencia(var, summ["nombre"])
                if score > mejor_score:
                    mejor_score = score
                    mejor = summ

                # Coincidencia fuerte: no seguir buscando
                if mejor_score >= 85:
                    return mejor

            time.sleep(0.34)

    if mejor and mejor_score >= 40:
        return mejor

    return None


def _sugerir_nombre_cientifico_receptora(keyword, modelo):
    """
    Usa el LLM solo para normalizar nombre común -> nombre científico.
    El resultado siempre se valida contra NCBI Taxonomy.
    """
    system = (
        "Eres experto en taxonomía botánica, zoológica y microbiana. "
        "Conviertes nombres comunes, aliases o términos ambiguos en nombres "
        "científicos aceptados. Respondes solo JSON válido."
    )

    user = (
        "Termino o nombre comun de especie receptora: \"" + str(keyword) + "\"\n\n"
        "Devuelve el nombre cientifico mas probable y aceptado para esa especie.\n"
        "Si es un cultivo, prioriza la especie domesticada o modelo mas usada en genomica.\n"
        "Devuelve SOLO JSON:\n"
        '{"nombre_cientifico":"Genero especie"}'
    )

    try:
        data = groq_json(system, user, modelo, temperature=0.0)
        nombre = str(data.get("nombre_cientifico", "")).strip()
        return nombre
    except Exception as e:
        log("LLM no pudo normalizar receptora: " + str(e), "warn")
        return ""


def resolver_receptora(valor, modelo, args):
    """
    V5.0: resuelve la especie receptora de forma dinamica.

    Acepta:
      - nombre comun: fresa, yuca, tomate
      - nombre cientifico: Fragaria vesca, Manihot esculenta
      - tax_id forzado con --receptora-tax-id

    AdemÃ¡s descarga o reutiliza el proteoma de la receptora.
    """
    valor = str(valor).strip()
    log("Resolviendo especie receptora: " + valor, "fase")
    estado("RECEPTORA INICIO: input=" + valor)

    tax_forzado = int(getattr(args, "receptora_tax_id", 0) or 0)

    if tax_forzado > 0:
        summ = _ncbi_taxonomy_summary(tax_forzado)
        if not summ or not summ.get("nombre"):
            sys.exit("No se pudo resolver el tax_id forzado de receptora: " + str(tax_forzado))
        nombre = summ["nombre"]
        tax_id = summ["tax_id"]
        lineage = summ.get("lineage", "")
        log("Usando tax_id forzado de receptora: " + str(tax_id), "ok")
    else:
        candidatos = []

        alias = RECEPTORA_ALIASES.get(normalizar(valor.lower()))
        if alias:
            candidatos.append(alias)
            log("Alias curado aplicado: " + valor + " -> " + alias, "ok")

        candidatos.append(valor)
        candidatos = _unicar(candidatos)

        summ = None
        for cand in candidatos:
            summ = _resolver_tax_id_por_nombre(cand)
            if summ:
                break

        # Fallback LLM solo si NCBI directo no resolvio bien
        if not summ and not getattr(args, "sin_llm_receptora", False):
            sug = _sugerir_nombre_cientifico_receptora(valor, modelo)
            if sug:
                log("LLM sugiere nombre cientifico para receptora: " + sug, "ok")
                summ = _resolver_tax_id_por_nombre(sug)

        # Ultimo intento: All Fields con el valor original
        if not summ:
            ids = _ncbi_taxonomy_ids(valor + "[All Fields]", retmax=5)
            mejor = None
            mejor_score = -1
            for tid in ids:
                s = _ncbi_taxonomy_summary(tid)
                if not s or not s.get("nombre"):
                    continue
                score = _score_coincidencia(valor, s["nombre"])
                if score > mejor_score:
                    mejor_score = score
                    mejor = s
            if mejor and mejor_score >= 35:
                summ = mejor

        if not summ:
            sys.exit(
                "No se pudo resolver la especie receptora: \"" + valor + "\". "
                "Prueba con nombre cientifico exacto o usa --receptora-tax-id."
            )

        nombre = summ["nombre"]
        tax_id = summ["tax_id"]
        lineage = summ.get("lineage", "")

    nombre_limpio = _limpiar_nombre_archivo(nombre)
    tipo = _inferir_tipo_receptora(lineage)

    log(
        "Receptora resuelta: " + nombre +
        " (tax_id " + str(tax_id) + ", tipo " + tipo + ")",
        "ok"
    )
    estado("RECEPTORA RESUELTA: " + nombre + " tax_id=" + str(tax_id))

    destino_dir = Path("proteomas_receptor")
    destino_dir.mkdir(exist_ok=True)

    proteoma_path = None
    proteinas_count = 0

    if getattr(args, "sin_proteoma_receptora", False):
        log("--sin-proteoma-receptora activo; no se descarga proteoma de receptora.", "warn")
        estado("RECEPTORA PROTEOMA OMITIDO por flag")
    else:
        archivo = destino_dir / ("proteoma_" + nombre_limpio + ".faa")

        if getattr(args, "forzar_proteoma_receptora", False) and archivo.exists():
            archivo.unlink()
            log("Proteoma de receptora marcado para re-descarga.", "warn")

        log("Descargando/reusing proteoma de receptora: " + nombre + " ...")
        estado("RECEPTORA PROTEOMA INICIO: " + nombre)

        proteoma_path = descargar_proteoma_especie(
            tax_id,
            nombre_limpio,
            destino_dir,
            max_proteinas=getattr(args, "max_proteinas_receptora", 100000)
        )

        if proteoma_path:
            try:
                plist = parsear_fasta(proteoma_path)
                proteinas_count = len(plist)
                log(
                    "Proteoma de receptora listo: " +
                    str(proteinas_count) + " proteinas",
                    "ok"
                )
                estado("RECEPTORA PROTEOMA FIN: " + str(proteinas_count) + " proteinas")
            except Exception as e:
                log("No se pudo parsear proteoma de receptora: " + str(e), "warn")
                estado("RECEPTORA PROTEOMA PARSEO FALLIDO: " + str(e))
        else:
            log(
                "No se pudo descargar proteoma de receptora. "
                "El flujo trans-especie puede continuar, pero no habra proteoma local de receptora.",
                "warn"
            )
            estado("RECEPTORA PROTEOMA FALLIDO")

    return {
        "nombre": nombre,
        "tax_id": tax_id,
        "nombre_limpio": nombre_limpio,
        "tipo": tipo,
        "lineage": lineage,
        "proteoma_path": str(proteoma_path or ""),
        "proteinas": proteinas_count,
        "input_original": valor,
    }


# ============================ MAIN ============================
def main():
    p = argparse.ArgumentParser(
        description="AgroGenIA V5.0 - Busqueda trans-especie orquestada",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--pfam", default="auto",
                   choices=["auto", "completo", "estres", "sequia", "salinidad",
                            "calor", "frio", "inundacion", "oxidativo",
                            "nutricion", "custom"],
                   help="Base Pfam a usar en HMMER")

    p.add_argument("--pfam-ruta", default="",
                   help="Ruta personalizada a archivo .hmm (requiere --pfam custom)")

    p.add_argument("--listar-pfam", action="store_true",
                   help="Lista bases Pfam disponibles y sale")
    
    p.add_argument("--rasgo", default="tolerancia a sequia",
                   help="Rasgo objetivo (cualquier rasgo imaginable)")
    p.add_argument("--receptora", default="yuca",
                   help="Nombre comun, alias o nombre cientifico de la especie receptora. "
                        "Ejemplos: fresa, Fragaria vesca, yuca, Manihot esculenta, tomate.")

    p.add_argument("--receptora-tax-id", type=int, default=0,
                   help="Forzar tax_id NCBI de la receptora. Si se usa, se evita la resolucion por nombre.")

    p.add_argument("--max-proteinas-receptora", type=int, default=100000,
                   help="Max proteinas RefSeq a descargar para la receptora. "
                        "0 = modo profundo (hasta 1,000,000; puede tardar mucho).")

    p.add_argument("--sin-proteoma-receptora", action="store_true",
                   help="No descargar proteoma de la receptora; solo resolver tax_id/nombre.")

    p.add_argument("--forzar-proteoma-receptora", action="store_true",
                   help="Re-descargar proteoma de receptora aunque exista en cache.")

    p.add_argument("--sin-llm-receptora", action="store_true",
                   help="No usar LLM para normalizar nombre comun de receptora; solo alias + NCBI.")

    p.add_argument("--solo-receptora", action="store_true",
                   help="Solo resolver receptora y descargar proteoma; no correr el pipeline completo.")
    p.add_argument("--max-por-especie", type=int, default=50,
                   help="Max proteinas por especie donante")
    p.add_argument("--max-hmmer", type=int, default=200,
                   help="Max proteinas a escanear con HMMER")
    p.add_argument("--hmmer-por-especie", type=int, default=1000,
                   help="Proteinas a escanear con HMMER por especie donante "
                        "(criterio primario estructural)")    
    p.add_argument("--top", type=int, default=10, help="Candidatos a priorizar")
    p.add_argument("--estrategia", default="A", choices=["A", "B"],
                   help="A: prioriza ortologos (sesgo natural hacia plantas). "
                        "B: fuerza diversidad reservando slots por tipo de organismo")
    p.add_argument("--modo", default="exploracion",
                   choices=["exploracion", "exhaustivo"],
                   help="exploracion: rapido y diverso. "
                        "exhaustivo: pre-ranqueo heuristico + LLM por lotes.")

    p.add_argument("--pre-top-por-especie", type=int, default=80,
                   help="En modo exhaustivo: max candidatos pre-ranqueados por especie "
                        "antes de enviar lotes al LLM.")

    p.add_argument("--lote-llm", type=int, default=20,
                   help="En modo exhaustivo: candidatos por lote enviados al LLM.")

    p.add_argument("--llm-lotes", type=int, default=5,
                   help="En modo exhaustivo: max numero de lotes LLM. "
                        "Total evaluado = lote-llm * llm-lotes.")
    p.add_argument("--no-compatibilidad", action="store_true",
                   help="Omite la evaluacion de compatibilidad por LLM y usa heuristica simple.")

    p.add_argument("--panel", default="llm",
                   choices=["llm", "curado", "hibrido"],
                   help="Origen del panel de donantes: llm, curado o hibrido.")

    p.add_argument("--max-proteinas-especie", type=int, default=50000,
                   help="Max proteinas RefSeq a descargar por especie donante. "
                        "0 = modo profundo (hasta 1,000,000; puede tardar mucho).")    

    p.add_argument("--no-constructos", action="store_true",
                   help="Omite el diseño de constructos por LLM y usa valores por defecto.")
            
    p.add_argument("--modelo", default="calidad", choices=list(MODELOS))
    p.add_argument("--salida", default="transespecie_orquestado")
    a = p.parse_args()

    if a.listar_pfam:
        listar_bases_pfam()
        return

    banner()
    modelo = MODELOS[a.modelo]
    rasgo_norm = normalizar(a.rasgo.lower().strip())
    t_inicio = time.time()

    global ESTADO_PATH
    ESTADO_PATH = str(a.salida) + ".estado"
    estado("INICIO · rasgo=" + a.rasgo +
           " · receptora_input=" + a.receptora +
           " · modo=" + a.modo +
           " · panel=" + a.panel +
           " · pfam=" + a.pfam +
           " · estrategia=" + a.estrategia +
           " · hmmer/esp=" + str(a.hmmer_por_especie) +
           " · maxprot_donante/esp=" + str(a.max_proteinas_especie) +
           " · maxprot_receptora=" + str(a.max_proteinas_receptora))

    receptora = resolver_receptora(a.receptora, modelo, a)

    if a.solo_receptora:
        log("Modo --solo-receptora: receptora resuelta y proteoma gestionado. Saliendo sin pipeline completo.", "ok")
        estado("SOLO_RECEPTORA FIN: " + receptora["nombre"] +
               " · proteinas=" + str(receptora.get("proteinas", 0)))
        return

    if hmmer_disponible():
        trait_hint = inferir_trait_pfam(rasgo_norm)
        if not ruta_pfam_trait(trait_hint).exists() and not PFAM_GENERIC.exists():
            log("No hay sub-base para '" + trait_hint + "'; --pfam auto usara Pfam completo.", "warn")



    # ── FASE 0 · ORQUESTACION: LLM SUGIERE DONANTES ──
    fase_titulo(0, "ORQUESTACION - el LLM sugiere especies donantes")
    log('Rasgo objetivo: "' + a.rasgo + '"', "fase")
    log("Especie receptora: " + receptora["nombre"])

    sugerencias = obtener_donantes_panel(
        a.rasgo,
        rasgo_norm,
        receptora,
        modelo,
        a.panel
    )

    log("Panel seleccionado: " + str(len(sugerencias)) + " especies candidatas.", "ok")

    if not sugerencias:
        sys.exit("El LLM no pudo sugerir donantes. Verifica la conexion y reintenta.")

    log("El LLM sugirio " + str(len(sugerencias)) + " especies:", "ok")
    for s in sugerencias:
        log("  - " + s.get("nombre_cientifico", "?") +
            " (" + s.get("tipo", "?") + "): " + s.get("adaptacion", "?"))

    # ── FASE 1 · RESOLUCION DE DONANTES ──
    fase_titulo(1, "RESOLUCION - nombres a tax_ids + verificacion de genomas")

    validos, descartados = resolver_donantes(sugerencias, a.rasgo, modelo)

    # V5.0: la receptora no debe aparecer como donante de si misma
    validos_filtrados = []
    for v in validos:
        if int(v.get("tax_id", 0)) == int(receptora["tax_id"]):
            descartados.append({
                "nombre": v.get("nombre", "?"),
                "razon": "Es la misma especie receptora"
            })
        else:
            validos_filtrados.append(v)

    if len(validos_filtrados) != len(validos):
        log("Donantes filtrados por ser iguales a la receptora: " +
            str(len(validos) - len(validos_filtrados)), "warn")

    validos = validos_filtrados

    log("Especies validas: " + str(len(validos)), "ok")
    log("Especies descartadas: " + str(len(descartados)), "warn")

    if not validos:
        sys.exit("No se pudieron resolver especies donantes con genoma disponible.")

    # ── FASE 2 · INGESTA MULTI-ESPECIE ──
        # ── FASE 2 · INGESTA + MUESTREO PARA HMMER (criterio primario) ──
    fase_titulo(2, "INGESTA MULTI-ESPECIE + MUESTREO HMMER")

    if a.max_proteinas_especie == 0:
        log("Modo proteoma profundo activo: hasta 1,000,000 proteinas por especie. "
            "Puede tardar mucho en bacterias grandes.", "warn")

    destino_dir = Path("proteomas_donantes")
    destino_dir.mkdir(exist_ok=True)
    keywords = KEYWORDS_ESTRES.get(rasgo_norm, [])
    if not keywords:
        log("No hay keywords predefinidas; usando el rasgo literal", "warn")
        keywords = a.rasgo.split()

    muestra_hmmer = []       # criterio primario: se escanea con HMMER
    candidatos_texto = []    # criterio secundario: keywords

    for esp in validos:
        nombre_limpio = esp["nombre"].replace(" ", "_")
        log("Procesando: " + esp["nombre"] + " (" + esp.get("tipo", "?") + ")")

        # Limpiar proteoma previo incompleto
        archivo_previo = destino_dir / ("proteoma_" + nombre_limpio + ".faa")
        if archivo_previo.exists() and archivo_previo.stat().st_size < 100000:
            log("Archivo previo incompleto; re-descargando", "warn")
            archivo_previo.unlink()

        prot_path = descargar_proteoma_especie(
            esp["tax_id"],
            nombre_limpio,
            destino_dir,
            max_proteinas=a.max_proteinas_especie
        )
        if not prot_path:
            log("No se pudo descargar el proteoma de " + esp["nombre"], "warn")
            continue

        proteinas = parsear_fasta(prot_path)
        log("Proteinas parseadas: " + str(len(proteinas)))

        if len(proteinas) < 1000:
            log("  -> Proteoma demasiado pequeno (" + str(len(proteinas)) +
                "). Anotacion pobre; se usara pero con baja confianza.", "warn")

        # CRITERIO PRIMARIO: muestra agnostica para HMMER
        muestra = preparar_muestra_hmmer(
            proteinas, a.hmmer_por_especie, seed=esp["tax_id"])
        for c in muestra:
            c["especie_donante"] = esp["nombre"]
            c["tipo_donante"] = esp.get("tipo", "")
        muestra_hmmer.extend(muestra)
        log("  -> Muestra para HMMER: " + str(len(muestra)))

        # CRITERIO SECUNDARIO: candidatos por keywords (complemento)
        por_texto = filtrar_por_estres(proteinas, keywords)
        for c in por_texto:
            c["especie_donante"] = esp["nombre"]
            c["tipo_donante"] = esp.get("tipo", "")
        candidatos_texto.extend(por_texto)
        log("  -> Candidatos por keywords: " + str(len(por_texto)))

    log("Total muestra HMMER: " + str(len(muestra_hmmer)), "ok")
    log("Total candidatos por keywords: " + str(len(candidatos_texto)))

    if not muestra_hmmer:
        sys.exit("No se pudo preparar la muestra HMMER. Reintenta.")

    # ── FASE 3 · HMMER PRIMARIO CONFIGURABLE ──
    fase_titulo(3, "ANOTACION ESTRUCTURAL (HMMER como criterio primario)")
    dominios_estres = DOMINIOS_ESTRES.get(rasgo_norm, [])

    if not hmmer_disponible():
        log("HMMER no disponible o Pfam completo ausente; usando solo keywords", "warn")
        for c in candidatos_donantes:
            c["dominios_raw"] = []
            c["dominios_relevantes"] = []
    else:
        try:
            db_pfam, etiqueta_pfam, es_subbase = seleccionar_base_pfam(
                a.pfam, rasgo_norm, a.pfam_ruta)
        except Exception as e:
            log("Error seleccionando base Pfam: " + str(e), "error")
            sys.exit(1)

        log("Base Pfam seleccionada: " + etiqueta_pfam, "ok")
        log("Ruta: " + str(db_pfam))

        # Escaneo HMMER de toda la muestra preparada
        dominios, es_subbase = escanear_dominios_hmmer(
            muestra_hmmer,
            db_path=db_pfam,
            max_scan=len(muestra_hmmer),
            etiqueta=etiqueta_pfam
        )

        for c in muestra_hmmer:
            c["dominios_raw"] = dominios.get(c["accession"], [])

            if es_subbase:
                # Con sub-base, todo dominio detectado es relevante por diseño
                c["dominios_relevantes"] = [d["dominio"] for d in c["dominios_raw"]]
            else:
                # Con Pfam completo, filtramos por dominios esperados del rasgo
                c["dominios_relevantes"] = tiene_dominios_relevantes(
                    c["dominios_raw"], dominios_estres)

        candidatos_estructurales = filtrar_por_dominios_estres(
            muestra_hmmer, dominios_estres) if not es_subbase else [
            c for c in muestra_hmmer if c.get("dominios_relevantes")
        ]

        log("Candidatos con dominios relevantes (" +
            ("sub-base" if es_subbase else "filtro por rasgo") +
            "): " + str(len(candidatos_estructurales)), "ok")

        # Combinar con candidatos por keywords como criterio secundario
        candidatos_finales = candidatos_estructurales
        accs_ya = set(c["accession"] for c in candidatos_finales)

        for c in candidatos_texto:
            if c["accession"] not in accs_ya:
                c.setdefault("dominios_relevantes", [])
                candidatos_finales.append(c)
                accs_ya.add(c["accession"])

        log("Candidatos combinados (estructura + texto): " +
            str(len(candidatos_finales)))

        # Limitar al top para el LLM, preservando diversidad por tipo
        max_final = a.max_por_especie * len(validos)
        if len(candidatos_finales) > max_final:
            con_dom = [c for c in candidatos_finales if c.get("dominios_relevantes")]
            sin_dom = [c for c in candidatos_finales if not c.get("dominios_relevantes")]
            slots_sin = max(0, max_final - len(con_dom))
            # intercalar sin_dom por tipo_donante para no monopolizar con 1-2 especies
            por_tipo = {}
            for c in sin_dom:
                por_tipo.setdefault(c.get("tipo_donante", "?"), []).append(c)
            tipos = list(por_tipo.keys())
            intercalados, i = [], 0
            while len(intercalados) < slots_sin and any(por_tipo.values()):
                t = tipos[i % len(tipos)]
                if por_tipo[t]:
                    intercalados.append(por_tipo[t].pop(0))
                i += 1
            candidatos_finales = con_dom + intercalados
            if len(candidatos_finales) > max_final:
                log("Sin recorte: " + str(len(con_dom)) + " estructurales superan el tope (" +
                    str(max_final) + "); se conservan todos para preservar diversidad "
                    "(el muestreo posterior reducira a 30 por tipo).", "warn")
            else:
                log("Limitado a " + str(max_final) + " candidatos (" + str(len(con_dom)) +
                    " con dominios, " + str(len(intercalados)) + " por keywords)", "warn")

        candidatos_donantes = candidatos_finales

    if not candidatos_donantes:
        sys.exit("No se obtuvieron candidatos. Reintenta con mas muestra HMMER o Pfam completo.")

    log("Candidatos finales para priorizar: " + str(len(candidatos_donantes)), "ok")


    # ── FASE 4 · PRIORIZACION + ESTRATEGIA + MODO ──
    fase_titulo(4, "PRIORIZACION DE CANDIDATOS DONANTES")

    if a.modo == "exhaustivo":
        log("Modo EXHAUSTIVO: pre-ranqueo heuristico + LLM por lotes", "fase")

        pre_top = pre_ranquear_candidatos(
            candidatos_donantes,
            keywords,
            top_por_especie=a.pre_top_por_especie
        )

        loguear_distribucion_especie(
            pre_top,
            "Pre-ranqueados por especie (antes de intercalar):"
        )

        pre_top = intercalar_por_especie(pre_top)

        loguear_distribucion_especie(
            pre_top[:a.lote_llm * a.llm_lotes],
            "Orden intercalado que entrara a lotes LLM:"
        )

        candidatos_priorizados = priorizar_candidatos_donantes_por_lotes(
            pre_top,
            a.rasgo,
            receptora,
            modelo,
            top=a.top,
            lote=a.lote_llm,
            max_lotes=a.llm_lotes
        )

        loguear_distribucion_especie(
            candidatos_priorizados,
            "Distribucion final por especie (modo exhaustivo):"
        )

    else:
        if a.estrategia == "B":
            log("Modo EXPLORACION + Estrategia B: diversidad por especie", "fase")

            muestra_diversa = seleccionar_muestra_diversa(
                candidatos_donantes,
                total_muestra=30
            )

            loguear_distribucion_especie(
                muestra_diversa,
                "Muestra diversa enviada al LLM (Estrategia B):"
            )

            candidatos_priorizados = priorizar_candidatos_donantes(
                muestra_diversa,
                a.rasgo,
                receptora,
                modelo,
                a.top
            )

            loguear_distribucion_especie(
                candidatos_priorizados,
                "Distribucion final por especie (Estrategia B):"
            )

        else:
            log("Modo EXPLORACION + Estrategia A: priorizacion por ortologia", "fase")

            candidatos_priorizados = priorizar_candidatos_donantes(
                candidatos_donantes,
                a.rasgo,
                receptora,
                modelo,
                a.top
            )

            loguear_distribucion_especie(
                candidatos_priorizados,
                "Distribucion final por especie (Estrategia A):"
            )

    for c in candidatos_priorizados:
        log(c["accession"] +
            "  score " + str(c.get("score_transferencia", 0)) +
            "  pre " + str(c.get("pre_score", 0)) +
            "  (" + c.get("especie_donante", "?") +
            " / " + c.get("tipo_donante", "?") + ")")

    # ── FASE 5 · VALIDACION MULTI-FUENTE (V4.2) ──
    fase_titulo(5, "VALIDACION MULTI-FUENTE (Europe PMC + STRING + GEO)")
    candidatos_validados = validar_multifuente(
        candidatos_priorizados, validos, a.rasgo)
    n_noveles = sum(
        1 for c in candidatos_validados
        if c.get("val_epmc", {}).get("novel") is True
    )
    n_unknown = sum(
        1 for c in candidatos_validados
        if c.get("val_epmc", {}).get("novel") is None
    )
    log("Candidatos verificados como NOVEL en Europe PMC: " + str(n_noveles), "ok")
    if n_unknown:
        log("Candidatos con Europe PMC UNKNOWN (timeout/error, novedad NO confirmada): "
            + str(n_unknown), "warn")


    # ── FASE 6 · EVALUACION DE COMPATIBILIDAD ──
    fase_titulo(6, "EVALUACION DE COMPATIBILIDAD")

    if a.no_compatibilidad:
        log("--no-compatibilidad activo; usando heuristica simple.", "warn")
        candidatos_compatibles = candidatos_validados
        for c in candidatos_compatibles:
            score_proxy = c.get("pre_score", c.get("score_transferencia", 0))
            tipo = c.get("tipo_donante", "")

            if tipo == "planta" and score_proxy >= 80:
                estrategia = "edicion_genica"
                riesgo = "bajo"
            elif score_proxy >= 60:
                estrategia = "edicion_genica"
                riesgo = "medio"
            else:
                estrategia = "transgenesis"
                riesgo = "medio"

            c.setdefault("tiene_ortologo", "no_se")
            c.setdefault("estrategia", estrategia)
            c.setdefault("riesgo_compatibility", riesgo)
            c.setdefault("justificacion_compat",
                         "Evaluacion LLM omitida por flag o limite de cuota. Revision manual requerida.")
    else:
        try:
            candidatos_compatibles = evaluar_compatibilidad(
                candidatos_validados, receptora, modelo)
        except Exception as e:
            log("Compatibilidad LLM fallo: " + str(e), "warn")
            log("Continuando con heuristica simple para no perder la corrida.", "warn")

            candidatos_compatibles = candidatos_validados
            for c in candidatos_compatibles:
                score_proxy = c.get("pre_score", c.get("score_transferencia", 0))
                tipo = c.get("tipo_donante", "")

                if tipo == "planta" and score_proxy >= 80:
                    estrategia = "edicion_genica"
                    riesgo = "bajo"
                elif score_proxy >= 60:
                    estrategia = "edicion_genica"
                    riesgo = "medio"
                else:
                    estrategia = "transgenesis"
                    riesgo = "medio"

                c.setdefault("tiene_ortologo", "no_se")
                c.setdefault("estrategia", estrategia)
                c.setdefault("riesgo_compatibility", riesgo)
                c.setdefault("justificacion_compat",
                             "Fallo de LLM en compatibilidad. Revision manual requerida.")

    for c in candidatos_compatibles:
        log(c["accession"] + "  -> " + c.get("estrategia", "?") +
            "  (riesgo: " + c.get("riesgo_compatibility", "?") + ")")

    # ── FASE 7 · DISENO DE CONSTRUCTO ──
    fase_titulo(7, "DISENO DE CONSTRUCTO")

    if a.no_constructos:
        log("--no-constructos activo; usando valores por defecto.", "warn")
        candidatos_finales = candidatos_compatibles
        for c in candidatos_finales:
            rasgo_l = normalizar(str(a.rasgo).lower())

            if "sequ" in rasgo_l or "drought" in rasgo_l or "desec" in rasgo_l:
                promotor = "rd29A (inducible por sequia/ABA) - pendiente de validacion"
            elif "salin" in rasgo_l or "salt" in rasgo_l:
                promotor = "promotor especifico de raiz o RD29A adaptado - pendiente de validacion"
            elif "calor" in rasgo_l or "heat" in rasgo_l:
                promotor = "HSP18.2 o promotor inducible por calor - pendiente de validacion"
            elif "frio" in rasgo_l or "cold" in rasgo_l:
                promotor = "CBF/DREB-responsive o promotor inducible por frio - pendiente de validacion"
            elif "inund" in rasgo_l or "flood" in rasgo_l or "hypox" in rasgo_l:
                promotor = "promotor hipoxia/ERF-VII responsive - pendiente de validacion"
            else:
                promotor = "promotor inducible por estres - pendiente de validacion"

            c.setdefault("promotor", promotor)
            c.setdefault("localizacion", "citosol - pendiente de validacion")
            c.setdefault("codon_opt", "si")
            c.setdefault("riesgos", ["Diseno LLM omitido; revision manual requerida."])
    else:
        try:
            candidatos_finales = disenar_constructos(
                candidatos_compatibles, receptora, modelo)
        except Exception as e:
            log("Diseno de constructos LLM fallo: " + str(e), "warn")
            log("Continuando con valores por defecto.", "warn")

            candidatos_finales = candidatos_compatibles
            for c in candidatos_finales:
                c.setdefault("promotor", "promotor inducible por estres - pendiente de validacion")
                c.setdefault("localizacion", "citosol - pendiente de validacion")
                c.setdefault("codon_opt", "si")
                c.setdefault("riesgos", ["Diseno LLM fallo; revision manual requerida."])

    for c in candidatos_finales[:5]:
        log(c["accession"] + "  -> promotor: " + c.get("promotor", "?"))

    # ── FASE 8 · BRAZO A ──
    fase_titulo(8, "BRAZO A - GENES CONOCIDOS EN RECEPTORA")
    genes_brazo_a = brazo_a_modelos(a.rasgo, receptora, keywords)
    log("Genes conocidos encontrados: " + str(len(genes_brazo_a)))

    # ── INFORME ──
    informe = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "rasgo": a.rasgo,
        "receptora": receptora["nombre"],
        "receptora_input": a.receptora,
        "receptora_tax_id": receptora["tax_id"],
        "receptora_tipo": receptora.get("tipo", "?"),
        "receptora_lineage": receptora.get("lineage", ""),
        "receptora_proteoma": receptora.get("proteoma_path", ""),
        "receptora_proteinas": receptora.get("proteinas", 0),        
        "estrategia": ("B (diversidad equilibrada)" if a.estrategia == "B"
                       else "A (priorizacion por ortologia)"),
        "modo": a.modo,
        "panel_modo": a.panel,
        "max_proteinas_especie": a.max_proteinas_especie,
        "modo_detalle": (
            "exhaustivo: pre-ranqueo heuristico + LLM por lotes"
            if a.modo == "exhaustivo"
            else "exploracion: muestreo diverso rapido"
        ),
        "pre_top_por_especie": a.pre_top_por_especie if a.modo == "exhaustivo" else None,
        "lote_llm": a.lote_llm if a.modo == "exhaustivo" else None,
        "llm_lotes": a.llm_lotes if a.modo == "exhaustivo" else None,                       
        "pfam_modo": a.pfam,
        "pfam_base": etiqueta_pfam if 'etiqueta_pfam' in locals() else "no aplicada",
        "pfam_ruta": str(db_pfam) if 'db_pfam' in locals() else "",                       
        "donantes_validos": validos,
        "donantes_descartados": descartados,
        "candidatos": candidatos_finales,
        "genes_brazo_a": genes_brazo_a,
        "nota": "Busqueda trans-especie V5.0 orquestada por LLM. Validacion experimental requerida.",
        
    }
    f_json, f_md = escribir_informe_v50(a.salida, informe)

    estado("FIN OK · " + str(round(time.time() - t_inicio, 1)) + " s · informe=" + str(f_md))    

    print("")
    print("=" * 66)
    log("Pipeline V5.0 completado en " + str(round(time.time() - t_inicio, 1)) + " s", "ok")
    if candidatos_finales:
        top = candidatos_finales[0]
        log("Candidato principal: " + top["accession"] +
            " (" + top.get("especie_donante", "?") + ")")
        log("Score de transferencia: " + str(top.get("score_transferencia", 0)))
    log("Informe JSON : " + str(f_json), "ok")
    log("Informe MD   : " + str(f_md), "ok")
    print("=" * 66)
    print("")


if __name__ == "__main__":
    main()