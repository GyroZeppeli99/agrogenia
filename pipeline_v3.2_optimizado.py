#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgroGenIA v3.2 - MODO DESCUBRIMIENTO - OPTIMIZADO
===================================================
Mejoras sobre v3.1:
  1. Deduplicacion por locus (elimina isoformas redundantes)
  2. Muestreo inteligente pre-HMMER (prioriza proteinas con pistas de dominio)
  3. Deduplicacion post-LLM (ranking final con loci unicos)

Busqueda SOLO en la especie de interes.
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
ALPHAFOLD = "https://alphafold.ebi.ac.uk"
ESMATLAS  = "https://esmatlas.com"
PFAM_DB   = os.path.expanduser("~/agrogenia/dbs/Pfam-A.hmm")

ESPECIES = {
    "arabidopsis": {"tax_id": 3702, "nombre": "Arabidopsis thaliana"},
    "arroz":       {"tax_id": 4530, "nombre": "Oryza sativa"},
    "tomate":      {"tax_id": 4081, "nombre": "Solanum lycopersicum"},
    "yuca":        {"tax_id": 3983, "nombre": "Manihot esculenta"},
}

CONSULTAS_PREDEFINIDAS = {
    "tolerancia a sequia":        "drought OR dehydration OR water deficit OR desiccation OR ABA",
    "tolerancia a salinidad":     "salt tolerance OR salinity OR sodium transport OR SOS",
    "resistencia a enfermedades": "disease resistance OR pathogen OR defense OR R protein",
    "eficiencia de nitrogeno":    "nitrogen use OR nitrate OR ammonium assimilation",
    "rendimiento":                "yield OR biomass OR growth regulation",
    "tolerancia a calor":         "heat stress OR thermotolerance OR heat shock",
}

# Palabras clave para filtro adaptativo
KEYWORDS_NIVEL1 = [
    "hypothetical protein", "hypothetical", "uncharacterized protein",
    "uncharacterized", "protein of unknown function", "unknown function",
    "unnamed protein product", "predicted protein", "putative protein",
    "probable protein", "expressed protein",
]

KEYWORDS_NIVEL2 = [
    "DUF", "domain-containing protein", "domain containing",
    "conserved protein", "conserved hypothetical", "membrane protein",
    "protein kinase", "zinc finger", "F-box", "WD40", "ankyrin",
    "repeat-containing", "repeat containing",
]

KEYWORDS_EXCLUIR = [
    "transposable element", "transposon", "retrotransposon",
    "fragment", "pseudogene", "reverse transcriptase", "integrase",
]

# ── NUEVO v3.2: keywords para muestreo inteligente ──
KEYWORDS_PISTA_DOMINIO = [
    "domain", "kinase", "binding", "repeat", "factor",
    "receptor", "synthase", "transferase", "oxidase",
    "protein", "enzyme", "channel", "transporter",
    "regulator", "responsive", "stress", "dehydration",
]

MIN_CANDIDATAS = 30

DOMINIOS_ESTRES = {
    "AP2": "respuesta a estres / desarrollo (familia AP2/ERF)",
    "ERF": "etileno y estres abiotico",
    "bZIP": "factores bZIP, via ABA",
    "NAM": "familia NAC, senescencia y estres",
    "NAC": "familia NAC, senescencia y estres",
    "LEA": "proteinas LEA, deshidratacion",
    "C2": "dominio C2, senalizacion calcio/ABA",
    "HSF_DNA-bind": "factor de choque termico",
    "Pkinase": "quinasa, senalizacion",
    "RRM": "union a ARN, estabilidad de transcriptos",
    "Aquaporin": "acuaporina, transporte de agua",
    "NBS": "resistencia a enfermedades (NBS-LRR)",
    "LRR": "repeticiones ricas en leucina, defensa",
    "WRKY": "factor WRKY, defensa",
    "PPR": "pentatricopeptido, organulos",
    "zf-C2H2": "dedo de zinc, regulacion transcripcional",
    "DREB": "respuesta a deshidratacion",
    "SNF2-rel_dom": "remodelacion de cromatina",
    "STAS": "transportador de sulfato, estres",
    "DHN": "deshidrina, proteccion celular",
}

# ============================ UTILIDADES ============================
def banner():
    print("")
    print("=" * 66)
    print("  AgroGenIA v3.2 - MODO DESCUBRIMIENTO (optimizado)")
    print("  + Deduplicacion por locus")
    print("  + Muestreo inteligente pre-HMMER")
    print("  + Ranking final sin redundancias")
    print("=" * 66)


def log(msg, nivel="dato"):
    iconos = {"fase": "#", "ok": "+", "warn": "!", "error": "x", "dato": "-"}
    print("  " + iconos.get(nivel, "-") + " " + msg)


def fase_titulo(n, titulo):
    print("")
    print("-" * 62)
    print("  FASE " + str(n) + " - " + titulo)
    print("-" * 62)


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
    return json.loads(texto[ini:fin + 1])


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
# MEJORA 1: DEDUPLICACION POR LOCUS
# ─────────────────────────────────────────────────────────────────────
def extraer_locus_base(accession):
    """Extrae el locus base de un accession, eliminando sufijos de isoforma.

    Ejemplos:
      Manes.14G053100.4.p  -> Manes.14G053100
      Manes.14G053100.12.p -> Manes.14G053100
      XP_043817031.1       -> XP_043817031.1  (sin cambio)
    """
    # Formato Phytozome/JGI: Manes.CHROMgGENEID.ISOFORM.p
    m = re.match(r'^(Manes\.\d+G\d+)\.\d+\.\w$', accession)
    if m:
        return m.group(1)
    # Formato generico: algo.N.p donde N es numero de isoforma
    m = re.match(r'^(.+)\.\d+\.p$', accession, re.IGNORECASE)
    if m:
        return m.group(1)
    return accession


def deduplicar_por_locus(proteinas):
    """Elimina isoformas redundantes, conservando la mas larga por locus.

    Si dos isoformas tienen la misma longitud, conserva la de menor
    numero de isoforma (ej. .1.p antes que .4.p).
    """
    loci = {}
    for p in proteinas:
        locus = extraer_locus_base(p["accession"])
        p["locus_base"] = locus
        if locus not in loci:
            loci[locus] = p
        else:
            # Conservar la mas larga; si empate, la de accession mas corto
            existente = loci[locus]
            if p["longitud"] > existente["longitud"]:
                loci[locus] = p
            elif p["longitud"] == existente["longitud"]:
                if len(p["accession"]) < len(existente["accession"]):
                    loci[locus] = p

    resultado = list(loci.values())
    eliminadas = len(proteinas) - len(resultado)
    if eliminadas > 0:
        log("Deduplicacion: " + str(eliminadas) + " isoformas redundantes eliminadas, " +
            str(len(resultado)) + " loci unicos.", "ok")
    return resultado


# ─────────────────────────────────────────────────────────────────────
# MEJORA 2: MUESTREO INTELIGENTE PRE-HMMER
# ─────────────────────────────────────────────────────────────────────
def muestreo_inteligente(candidatas, n, seed=42):
    """Muestreo inteligente: 70% proteinas con pistas de dominio + 30% aleatorio.

    Esto aumenta la probabilidad de que HMMER encuentre dominios relevantes,
    ya que las proteinas con palabras como 'kinase', 'binding', 'domain' en
    su descripcion tienen mas probabilidad de tener dominios Pfam detectables.
    """
    random.seed(seed)

    con_pistas = []
    sin_pistas = []
    for p in candidatas:
        desc = p.get("descripcion", "").lower()
        if any(k.lower() in desc for k in KEYWORDS_PISTA_DOMINIO):
            con_pistas.append(p)
        else:
            sin_pistas.append(p)

    n_pistas = min(int(n * 0.7), len(con_pistas))
    n_random = n - n_pistas

    if con_pistas:
        seleccion = random.sample(con_pistas, n_pistas)
    else:
        seleccion = []

    accs_seleccion = set(p["accession"] for p in seleccion)
    restantes = [p for p in candidatas if p["accession"] not in accs_seleccion]

    if len(restantes) >= n_random:
        seleccion += random.sample(restantes, n_random)
    else:
        seleccion += restantes

    log("Muestreo inteligente: " + str(n_pistas) + " con pistas de dominio + " +
        str(len(seleccion) - n_pistas) + " aleatorias = " + str(len(seleccion)) +
        " proteinas para HMMER", "ok")
    return seleccion[:n]


# ============================ FASE 1 - INGESTA ============================
def obtener_accession_genoma(tax_id):
    url = NCBI_DATA + "/genome/taxon/" + str(tax_id) + "/dataset_report"
    try:
        r = requests.get(url, params={"reference": "reference"}, timeout=60)
        if r.status_code != 200:
            r = requests.get(url, timeout=60)
        r.raise_for_status()
        reports = r.json().get("reports", [])
        if not reports:
            return None
        return reports[0].get("accession")
    except Exception as e:
        log("No se pudo obtener el accession: " + str(e), "warn")
        return None


def descargar_proteoma(accession, destino):
    url = NCBI_DATA + "/genome/accession/" + accession + "/download"
    params = {"include": "proteome:fasta"}
    log("Descargando proteoma (accession " + accession + ") ...")
    try:
        r = requests.get(url, params=params, timeout=300, stream=True)
        r.raise_for_status()
        contenido = io.BytesIO(r.content)
        with zipfile.ZipFile(contenido) as z:
            faa = None
            for nombre in z.namelist():
                if nombre.endswith(".faa"):
                    faa = nombre
                    break
            if not faa:
                log("El ZIP no contiene archivo .faa", "error")
                return None
            with z.open(faa) as fsrc, open(destino, "wb") as fdst:
                fdst.write(fsrc.read())
        log("Proteoma guardado en " + str(destino), "ok")
        return destino
    except Exception as e:
        log("Error descargando proteoma: " + str(e), "error")
        return None


def parsear_fasta(ruta):
    proteinas = []
    header = None
    seq = []
    with open(ruta, "r", encoding="utf-8", errors="ignore") as fh:
        for linea in fh:
            linea = linea.rstrip("\n")
            if linea.startswith(">"):
                if header is not None:
                    _guardar_proteina(proteinas, header, "".join(seq))
                header = linea[1:].strip()
                seq = []
            else:
                seq.append(linea.strip())
        if header is not None:
            _guardar_proteina(proteinas, header, "".join(seq))
    return proteinas


def _guardar_proteina(lista, header, seq):
    seq = seq.upper()
    if not seq:
        return
    partes = header.split(None, 1)
    accession = partes[0]
    resto = partes[1] if len(partes) > 1 else ""
    resto = re.sub(r"\s*\[[^\]]*\]\s*$", "", resto).strip()
    lista.append({
        "accession": accession,
        "descripcion": resto,
        "secuencia": seq,
        "longitud": len(seq),
    })


# ============================ FASE 2 - FILTRADO ADAPTATIVO ============================
def _es_excluida(desc):
    d = desc.lower()
    return any(k.lower() in d for k in KEYWORDS_EXCLUIR)


def _match_keywords(desc, keywords):
    d = desc.lower()
    return any(k.lower() in d for k in keywords)


def filtrar_no_caracterizadas(proteinas, min_len=80):
    """Filtro adaptativo en 3 niveles. Se relaja hasta encontrar candidatas."""
    total = len(proteinas)

    limpias = []
    excluidas = 0
    for p in proteinas:
        if _es_excluida(p["descripcion"]) or p["longitud"] < min_len:
            excluidas += 1
        else:
            limpias.append(p)

    log("Proteomas totales              : " + str(total))
    log("Excluidas (transp/fragmentos)  : " + str(excluidas))
    log("Limpias tras pre-filtro        : " + str(len(limpias)))

    # NIVEL 1: keywords estrictas
    nivel1 = [p for p in limpias if _match_keywords(p["descripcion"], KEYWORDS_NIVEL1)]
    log("Nivel 1 (estricto)             : " + str(len(nivel1)))
    if len(nivel1) >= MIN_CANDIDATAS:
        log("Filtro estricto suficiente. Usando Nivel 1.", "ok")
        return nivel1, 1

    # NIVEL 2: sumar keywords intermedias
    nivel2 = [p for p in limpias
              if _match_keywords(p["descripcion"], KEYWORDS_NIVEL1)
              or _match_keywords(p["descripcion"], KEYWORDS_NIVEL2)]
    log("Nivel 2 (intermedio)           : " + str(len(nivel2)))
    if len(nivel2) >= MIN_CANDIDATAS:
        log("Filtro intermedio suficiente. Usando Nivel 2.", "ok")
        return nivel2, 2

    # NIVEL 3: fallback - todas las limpias
    log("Pocas candidatas en niveles 1-2. Fallback: usando todas las limpias.", "warn")
    log("El filtrado por dominios (HMMER) refinara la seleccion.", "warn")
    return limpias, 3


# ============================ FASE 3 - DOMINIOS (HMMER) ============================
def hmmer_disponible():
    return shutil.which("hmmscan") is not None and os.path.exists(PFAM_DB)


def escanear_dominios_hmmer(proteinas):
    """Corre hmmscan contra Pfam para una lista de proteinas."""
    dominios_por_prot = {}
    with tempfile.NamedTemporaryFile("w", suffix=".fasta", delete=False) as fd:
        for p in proteinas:
            fd.write(">" + p["accession"] + "\n" + p["secuencia"] + "\n")
        fasta = fd.name
    domtbl = fasta + ".domtbl"

    t_inicio = time.time()
    log("Iniciando hmmscan contra Pfam (" + str(len(proteinas)) + " proteinas)...")

    try:
        proc = subprocess.run(
            ["hmmscan", "--domtblout", domtbl,
             "-E", "1e-3", "--domE", "1e-3",
             "--cpu", "4", PFAM_DB, fasta],
            check=True, capture_output=True, timeout=7200)
        elapsed = time.time() - t_inicio
        log("hmmscan completado en " + str(round(elapsed, 1)) + " s", "ok")

        with open(domtbl) as fh:
            for linea in fh:
                if linea.startswith("#"):
                    continue
                campos = linea.split()
                if len(campos) < 4:
                    continue
                dom = campos[0]
                acc = campos[1]
                query = campos[3]
                dominios_por_prot.setdefault(query, []).append(
                    {"dominio": dom, "accession": acc})

        n_con_dom = sum(1 for v in dominios_por_prot.values() if v)
        log("Proteinas con al menos un dominio Pfam: " + str(n_con_dom) +
            " / " + str(len(proteinas)), "ok")

    except subprocess.TimeoutExpired:
        log("HMMER: timeout (2 horas). Reduce --max-hmmer.", "warn")
    except Exception as e:
        log("HMMER error: " + str(e), "warn")
    finally:
        for f in (fasta, domtbl):
            if os.path.exists(f):
                try: os.unlink(f)
                except OSError: pass

    return dominios_por_prot


def tiene_dominio_estres(lista_doms):
    if not lista_doms:
        return []
    hits = []
    for d in lista_doms:
        nombre = d.get("dominio", "")
        for clave in DOMINIOS_ESTRES:
            if clave in nombre:
                hits.append({"dominio": nombre,
                             "funcion": DOMINIOS_ESTRES[clave]})
    return hits


def anotar_dominios(candidatas, max_hmmer, seed=42):
    """Anota dominios usando HMMER con muestreo inteligente (MEJORA 2)."""
    if hmmer_disponible():
        # MEJORA 2: muestreo inteligente en lugar de primeras N
        seleccion = muestreo_inteligente(candidatas, max_hmmer, seed)
        doms = escanear_dominios_hmmer(seleccion)

        for p in seleccion:
            p["dominios_raw"] = doms.get(p["accession"], [])
            p["dominios_estres"] = tiene_dominio_estres(p["dominios_raw"])

        # Las que no se escanearon se marcan como sin datos
        accs_escaneadas = set(p["accession"] for p in seleccion)
        for p in candidatas:
            if p["accession"] not in accs_escaneadas:
                p["dominios_raw"] = []
                p["dominios_estres"] = []

        return candidatas, True
    else:
        log("HMMER/Pfam no disponible; usando solo descripcion.", "warn")
        for p in candidatas:
            p["dominios_raw"] = []
            p["dominios_estres"] = []
        return candidatas, False


# ============================ BRAZO A - LITERATURA ============================
def brazo_a_literatura(especie, terminos, modelo, max_genes=10):
    log("Brazo A: buscando genes conocidos en NCBI ...")
    term = "(" + terminos + ") AND txid" + str(especie["tax_id"]) + "[Organism]"
    try:
        r = requests.get(NCBI + "/esearch.fcgi",
                         params={"db": "gene", "term": term, "retmax": max_genes * 3,
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
            if len(genes) >= max_genes:
                break
        return genes
    except Exception as e:
        log("Brazo A fallo: " + str(e), "warn")
        return []


# ============================ FASE 4 - PRIORIZACION BRAZO B ============================
def priorizar_noveles(candidatas, rasgo, especie, modelo, historial, top_novel):
    """Prioriza candidatos noveles con el LLM.

    MEJORA 3: antes de enviar al LLM, deduplica por locus para evitar
    que multiples isoformas del mismo gen ocupen slots del ranking.
    """
    # MEJORA 3: deduplicar antes de priorizar
    candidatas_unicas = deduplicar_por_locus(candidatas)

    # Ordenar: primero las que tienen dominios de estres
    con_dom = [c for c in candidatas_unicas if c.get("dominios_estres")]
    sin_dom = [c for c in candidatas_unicas if not c.get("dominios_estres")]
    pool = (con_dom + sin_dom)[:max(top_novel * 3, 30)]

    listado = ""
    for i, p in enumerate(pool):
        doms = ", ".join(d["dominio"] for d in p.get("dominios_estres", [])) or "ninguno conocido"
        desc_corta = (p["descripcion"] or "sin descripcion")[:120]
        listado += (str(i + 1) + ". " + p["accession"] +
                    " | locus: " + p.get("locus_base", "?") +
                    " | desc: " + desc_corta +
                    " | dominios estres: " + doms + "\n")

    hist_txt = ""
    if historial:
        hist_txt = "\nDescubrimientos previos (retroalimentacion):\n" + json.dumps(
            historial[:5], ensure_ascii=False, indent=1) + "\n"

    system = ("Eres experto en genomica funcional de plantas. Priorizas proteinas poco "
              "caracterizadas como candidatos noveles para un rasgo, usando dominios, "
              "descripcion y evidencia indirecta. Eres conservador: indicas incertidumbre. "
              "IMPORTANTE: trata cada locus como un gen independiente; no repitas loci.")
    user = ("Prioriza estas proteinas poco caracterizadas de " + especie["nombre"] +
            " como candidatos NOVELES para el rasgo \"" + rasgo + "\".\n" +
            hist_txt + "\nCandidatas:\n" + listado +
            "\nInstrucciones:\n" +
            "1. Puntua cada una de 0 a 100 como candidato NOVEL plausible.\n" +
            "2. Indica la pista funcional principal (dominio, descripcion).\n" +
            "3. Senala el nivel de especulacion (alta/media/baja).\n" +
            "4. NO repitas el mismo locus; cada entrada debe ser un gen distinto.\n\n" +
            "Devuelve SOLO JSON:\n" +
            '{"ranking":[{"accession":"...","score":70,"pista":"...","especulacion":"media"}]}')

    data = groq_json(system, user, modelo)
    scores = {}
    for x in data.get("ranking", []):
        if isinstance(x, dict) and "accession" in x:
            scores[x["accession"]] = x

    for p in pool:
        m = scores.get(p["accession"])
        p["score_novel"] = int(m.get("score", 0)) if m else 0
        p["pista"] = (m or {}).get("pista", "")
        p["especulacion"] = (m or {}).get("especulacion", "")

    pool.sort(key=lambda x: x["score_novel"], reverse=True)

    # MEJORA 3: deduplicacion final por locus en el ranking
    resultado_final = []
    loci_vistos = set()
    for p in pool:
        locus = p.get("locus_base", p["accession"])
        if locus not in loci_vistos:
            loci_vistos.add(locus)
            resultado_final.append(p)
        if len(resultado_final) >= top_novel:
            break

    return resultado_final


# ============================ FASE 5 - NOVEDAD + CONVERGENCIA ============================
def verificar_novedad_pmc(candidatos):
    for c in candidatos:
        terminos_busqueda = [c["accession"]]
        locus = c.get("locus_base", "")
        if locus:
            terminos_busqueda.append(locus)
        total = 0
        for t in terminos_busqueda:
            try:
                r = requests.get(NCBI + "/esearch.fcgi",
                                 params={"db": "pmc", "term": '"' + t + '"',
                                         "retmode": "json"}, timeout=45)
                if r.status_code == 200:
                    total += int(r.json()["esearchresult"].get("count", 0))
            except Exception:
                pass
            time.sleep(0.4)
        c["menciones_pmc"] = total
        c["es_novel"] = (total == 0)
        estado = "NOVEL (0 menciones)" if total == 0 else str(total) + " menciones"
        log("  PMC " + c.get("locus_base", c["accession"]) + ": " + estado,
            "ok" if total == 0 else "warn")
    return candidatos


def analisis_convergencia(noveles, conocidos, rasgo, especie, modelo):
    nov_txt = json.dumps([{"accession": n["accession"],
                           "locus": n.get("locus_base", ""),
                           "pista": n.get("pista", ""),
                           "dominios": [d["dominio"] for d in n.get("dominios_estres", [])]}
                          for n in noveles], ensure_ascii=False, indent=1)
    con_txt = json.dumps([{"simbolo": k["simbolo"], "descripcion": k["descripcion"]}
                          for k in conocidos], ensure_ascii=False, indent=1)
    system = ("Eres experto en genomica comparada. Analizas convergencia funcional entre "
              "candidatos noveles (poco caracterizados) y genes conocidos para un rasgo.")
    user = ("Rasgo: \"" + rasgo + "\" en " + especie["nombre"] + "\n\n" +
            "CANDIDATOS NOVELES (Brazo B):\n" + nov_txt + "\n\n" +
            "GENES CONOCIDOS (Brazo A):\n" + con_txt + "\n\n" +
            "Para cada candidato novel indica si converge con algun gen conocido " +
            "(mismo dominio, misma via, ortologia probable) y genera una hipotesis " +
            "integrada. Devuelve SOLO JSON:\n" +
            '{"convergencias":[{"accession":"...","converge_con":"...",' +
            '"tipo_convergencia":"dominio|via|ortologia|ninguna",' +
            '"hipotesis":"...","confianza":60}]}')
    return groq_json(system, user, modelo, temperature=0.3)


# ============================ INFORME ============================
def _s(valor, default):
    """Devuelve default si valor es None o vacio; si no, lo convierte a str."""
    if valor is None:
        return default
    valor_str = str(valor)
    return valor_str if valor_str.strip() else default


def escribir_informe_v3(ruta, informe):
    ruta = Path(ruta)
    ruta.with_suffix(".json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")

    emb = informe.get("embudo", {})
    md = ["# Descubrimiento AgroGenIA v3.2",
          "",
          "- **Fecha:** " + _s(informe.get("fecha"), "?"),
          "- **Especie:** *" + _s(informe.get("especie"), "?") + "*",
          "- **Rasgo:** " + _s(informe.get("rasgo"), "?"),
          "- **Nivel de filtro usado:** Nivel " + _s(emb.get("nivel_filtro"), "?"),
          "- **Proteoma total:** " + _s(emb.get("total"), "?"),
          "- **Candidatas tras filtro:** " + _s(emb.get("candidatas"), "?"),
          "- **Loci unicos tras deduplicacion:** " + _s(emb.get("loci_unicos"), "?"),
          "- **Escaneadas con HMMER:** " + _s(emb.get("escaneadas_hmmer"), "?"),
          "- **Con dominios de estres:** " + _s(emb.get("con_dominios"), "?"),
          "- **Noveles priorizados:** " + str(len(informe.get("noveles", []))),
          "",
          "## Embudo de filtrado",
          "",
          "| Etapa | Cantidad |",
          "|---|---|",
          "| Proteoma total | " + _s(emb.get("total"), "?") + " |",
          "| Excluidas (transp/fragmentos) | " + _s(emb.get("excluidas"), "?") + " |",
          "| Candidatas (nivel " + _s(emb.get("nivel_filtro"), "?") + ") | " + _s(emb.get("candidatas"), "?") + " |",
          "| Loci unicos (deduplicacion) | " + _s(emb.get("loci_unicos"), "?") + " |",
          "| Escaneadas con HMMER | " + _s(emb.get("escaneadas_hmmer"), "?") + " |",
          "| Con dominios de estres | " + _s(emb.get("con_dominios"), "?") + " |",
          "| Noveles priorizados | " + str(len(informe.get("noveles", []))) + " |",
          "",
          "## Candidatos noveles",
          "",
          "| # | Locus | Accession | Score | Especulacion | Pista | Dominios | PMC | Novel |",
          "|---|---|---|---|---|---|---|---|---|"]

    for i, n in enumerate(informe.get("noveles", []), 1):
        doms_list = [d.get("dominio", "?") for d in n.get("dominios_estres", [])]
        doms = ", ".join(doms_list) if doms_list else "-"
        pista = _s(n.get("pista"), "-")
        if len(pista) > 80:
            pista = pista[:77] + "..."
        md.append("| " + str(i) +
                  " | " + _s(n.get("locus_base"), "?") +
                  " | " + _s(n.get("accession"), "?") +
                  " | " + _s(n.get("score_novel"), "0") +
                  " | " + _s(n.get("especulacion"), "-") +
                  " | " + pista +
                  " | " + doms +
                  " | " + _s(n.get("menciones_pmc"), "?") +
                  " | " + ("SI" if n.get("es_novel") else "no") + " |")

    md.append("")
    md.append("## Convergencia con genes conocidos (Brazo A)")
    md.append("")

    convergencias = informe.get("convergencias", [])
    if not convergencias:
        md.append("_No se generaron analisis de convergencia._")
    else:
        for cv in convergencias:
            if not isinstance(cv, dict):
                continue
            md.append("### " + _s(cv.get("accession"), "?"))
            md.append("- **Converge con:** " + _s(cv.get("converge_con"), "ninguno"))
            md.append("- **Tipo:** " + _s(cv.get("tipo_convergencia"), "ninguna"))
            md.append("- **Hipotesis:** " + _s(cv.get("hipotesis"), "n/d"))
            md.append("- **Confianza:** " + _s(cv.get("confianza"), "?") + "%")
            md.append("")

    md.append("> Los candidatos marcados como NOVEL (0 menciones en PMC) son los de mayor interes.")
    ruta.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
    return ruta.with_suffix(".json"), ruta.with_suffix(".md")


# ============================ HISTORIAL ============================
def cargar_historial(ruta):
    p = Path(ruta)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def guardar_historial(ruta, historial, nuevos):
    historial.extend(nuevos)
    historial = historial[-50:]
    Path(ruta).write_text(json.dumps(historial, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    return historial


# ============================ MAIN ============================
def main():
    p = argparse.ArgumentParser(
        description="AgroGenIA v3.2 - Modo descubrimiento (optimizado)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--rasgo", default="tolerancia a sequia")
    p.add_argument("--especie", default="yuca", choices=list(ESPECIES))
    p.add_argument("--top-novel", type=int, default=10,
                   help="Candidatos noveles a priorizar")
    p.add_argument("--max-hmmer", type=int, default=500,
                   help="Max proteinas a escanear con HMMER (aumentado en v3.2)")
    p.add_argument("--seed", type=int, default=42,
                   help="Semilla para muestreo reproducible")
    p.add_argument("--proteoma-local", default="",
                   help="Usar un FASTA local en vez de descargar")
    p.add_argument("--saltar-pmc", action="store_true",
                   help="No verificar novedad en PMC")
    p.add_argument("--modelo", default="calidad", choices=list(MODELOS))
    p.add_argument("--historial", default="historial_agrogenia.json")
    p.add_argument("--salida", default="descubrimiento_agrogenia")
    a = p.parse_args()

    banner()
    modelo = MODELOS[a.modelo]
    especie = ESPECIES[a.especie]
    t_inicio = time.time()

    # ── FASE 0 - PLANIFICACION ──
    fase_titulo(0, "PLANIFICACION")
    clave = normalizar(a.rasgo.lower().strip())
    terminos = CONSULTAS_PREDEFINIDAS.get(clave, a.rasgo)
    log('Consulta: "Genes de ' + a.rasgo + " en " + especie["nombre"] + '"', "fase")
    log("Terminos (Brazo A): " + terminos)
    historial = cargar_historial(a.historial)
    log("Historial previo: " + str(len(historial)) + " entradas")

    # ── FASE 1 - INGESTA ──
    fase_titulo(1, "INGESTA - carga del proteoma")
    proteoma_path = Path("proteoma_" + a.especie + ".faa")
    if a.proteoma_local and os.path.exists(a.proteoma_local):
        proteoma_path = Path(a.proteoma_local)
        log("Usando proteoma local: " + str(proteoma_path))
    else:
        if proteoma_path.exists():
            log("Proteoma ya descargado: " + str(proteoma_path))
        else:
            acc = obtener_accession_genoma(especie["tax_id"])
            if not acc:
                sys.exit("No se encontro genoma de referencia para esta especie.")
            log("Genoma de referencia: " + acc)
            if not descargar_proteoma(acc, proteoma_path):
                sys.exit("Fallo la descarga del proteoma.")
    proteinas = parsear_fasta(proteoma_path)
    log("Proteinas parseadas: " + str(len(proteinas)), "ok")

    # ── FASE 2 - FILTRADO ADAPTATIVO ──
    fase_titulo(2, "FILTRADO ADAPTATIVO + DEDUPLICACION")
    candidatas, nivel_filtro = filtrar_no_caracterizadas(proteinas)

    # MEJORA 1: deduplicar por locus ANTES de HMMER
    candidatas = deduplicar_por_locus(candidatas)
    n_loci_unicos = len(candidatas)
    log("Candidatas tras deduplicacion: " + str(n_loci_unicos) + " loci unicos", "ok")

    # ── FASE 3 - DOMINIOS con muestreo inteligente ──
    fase_titulo(3, "DOMINIOS - HMMER con muestreo inteligente")
    candidatas, uso_hmmer = anotar_dominios(candidatas, a.max_hmmer, a.seed)
    con_dom = [c for c in candidatas if c.get("dominios_estres")]
    log("Candidatas con dominios de estres: " + str(len(con_dom)), "ok")
    if con_dom:
        log("Ejemplo: " + con_dom[0].get("locus_base", "?") + " -> " +
            ", ".join(d["dominio"] for d in con_dom[0]["dominios_estres"][:3]))

    # ── FASE 4 - PRIORIZACION BRAZO B ──
    fase_titulo(4, "PRIORIZACION BRAZO B - candidatos noveles (sin redundancias)")
    noveles = priorizar_noveles(candidatas, a.rasgo, especie, modelo,
                                historial, a.top_novel)
    for n in noveles:
        log(n.get("locus_base", n["accession"]) + "  score " +
            str(n.get("score_novel", 0)) +
            "  (" + str(n.get("especulacion", "")) + ")")

    # ── ESTRUCTURAS para los top ──
    fase_titulo(5, "ESTRUCTURAS PREDICHAS (AlphaFold/ESMAtlas)")
    for n in noveles:
        # Buscar en UniProt por locus
        m = re.search(r"([A-Za-z0-9_]{6,25})", n.get("descripcion", ""))
        gen_hint = m.group(1) if m else None
        if gen_hint:
            try:
                q = "(gene_exact:" + gen_hint + " OR gene:" + gen_hint + \
                    ") AND taxonomy_id:" + str(especie["tax_id"])
                r = requests.get(UNIPROT + "/uniprotkb/search",
                                 params={"query": q, "format": "json", "size": 1,
                                         "fields": "accession"}, timeout=45)
                if r.status_code == 200:
                    res = r.json().get("results", [])
                    if res:
                        acc = res[0].get("primaryAccession")
                        if acc:
                            n["estructura"] = {"fuente": "AlphaFold DB",
                                               "url": ALPHAFOLD + "/entry/" + acc}
                            log(n.get("locus_base", "?") + " -> AlphaFold: " + acc, "ok")
                            continue
            except Exception:
                pass
        n["estructura"] = {"fuente": "ESMAtlas (verificar)",
                           "url": ESMATLAS + "/search?q=" + n["accession"]}
        log(n.get("locus_base", "?") + " -> ESMAtlas (verificar manualmente)")

    # ── NOVEDAD PMC ──
    if not a.saltar_pmc:
        fase_titulo(6, "NOVEDAD - verificacion en PMC")
        noveles = verificar_novedad_pmc(noveles)

    # ── CONVERGENCIA con Brazo A ──
    fase_titulo(7, "CONVERGENCIA - Brazo A vs Brazo B")
    conocidos = brazo_a_literatura(especie, terminos, modelo, max_genes=10)
    log("Genes conocidos (Brazo A): " + str(len(conocidos)))
    conv = {"convergencias": []}
    if conocidos and noveles:
        try:
            conv = analisis_convergencia(noveles, conocidos, a.rasgo, especie, modelo)
        except Exception as e:
            log("Analisis de convergencia fallo: " + str(e), "warn")
    convergencias = conv.get("convergencias", [])

    # ── INFORME + HISTORIAL ──
    informe = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "especie": especie["nombre"],
        "tax_id": especie["tax_id"],
        "rasgo": a.rasgo,
        "terminos_brazo_a": terminos,
        "modelo": modelo,
        "version": "3.2",
        "embudo": {
            "total": len(proteinas),
            "excluidas": len(proteinas) - n_loci_unicos,
            "candidatas": n_loci_unicos,
            "nivel_filtro": nivel_filtro,
            "loci_unicos": n_loci_unicos,
            "escaneadas_hmmer": min(a.max_hmmer, n_loci_unicos),
            "con_dominios": len(con_dom),
            "uso_hmmer": uso_hmmer,
        },
        "noveles": noveles,
        "conocidos_brazo_a": conocidos,
        "convergencias": convergencias,
        "nota": "Modo descubrimiento v3.2. Correlacion != causalidad; validar experimentalmente.",
    }
    f_json, f_md = escribir_informe_v3(a.salida, informe)

    nuevos = [{"accession": n["accession"],
               "locus": n.get("locus_base", ""),
               "rasgo": a.rasgo,
               "especie": especie["nombre"],
               "score": n.get("score_novel", 0),
               "fecha": informe["fecha"]} for n in noveles[:3]]
    guardar_historial(a.historial, historial, nuevos)

    print("")
    print("=" * 62)
    log("Pipeline v3.2 completado en " + str(round(time.time() - t_inicio, 1)) + " s", "ok")
    if noveles:
        top = noveles[0]
        log("Candidato novel principal: " + top.get("locus_base", top["accession"]) +
            " (score " + str(top.get("score_novel", 0)) + ")", "ok")
        if top.get("es_novel"):
            log("VERIFICADO como NOVEL (0 menciones en PMC)", "ok")
    log("Informe JSON : " + str(f_json), "ok")
    log("Informe MD   : " + str(f_md), "ok")
    print("=" * 62)
    print("")


if __name__ == "__main__":
    main()