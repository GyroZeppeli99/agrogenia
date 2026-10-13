#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgroGenIA V4.1 · BUSQUEDA TRANS-ESPECIE ORQUESTADA
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
PFAM_DB   = os.path.expanduser("~/agrogenia/dbs/Pfam-A.hmm")

# Especie receptora por defecto
RECEPTORA = {
    "yuca":        {"tax_id": 3983, "nombre": "Manihot esculenta"},
    "arabidopsis": {"tax_id": 3702, "nombre": "Arabidopsis thaliana"},
    "arroz":       {"tax_id": 4530, "nombre": "Oryza sativa"},
    "tomate":      {"tax_id": 4081, "nombre": "Solanum lycopersicum"},
}

# Palabras clave por rasgo para filtrar candidatos (se normalizan acentos)
KEYWORDS_ESTRES = {
    "tolerancia a sequia": ["trehalose", "LEA", "dehydrin", "DREB", "dehydration",
                            "desiccation", "drought", "osmoprotectant", "ABA"],
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
                            "Pkinase", "ABC2_membrane", "PPR"],
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
    print("  AgroGenIA V4.1 · BUSQUEDA TRANS-ESPECIE ORQUESTADA")
    print("  LLM sugiere donantes -> resolucion -> descarga automatica")
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
# FASE 0 · ORQUESTACION: EL LLM SUGIERE DONANTES (NUEVO EN V4.1)
# ─────────────────────────────────────────────────────────────────────
def sugerir_donantes_llm(rasgo, receptora, modelo):
    """El LLM sugiere especies donantes para el rasgo objetivo."""
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
        return data.get("donantes", [])
    except Exception as e:
        log("El LLM no pudo sugerir donantes: " + str(e), "warn")
        return []


# ─────────────────────────────────────────────────────────────────────
# FASE 1 · RESOLUCION DE DONANTES (NUEVO EN V4.1)
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
def descargar_proteoma_especie(tax_id, nombre_limpio, destino_dir):
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
    resultado = _descargar_via_eutils(tax_id, nombre_limpio, destino)
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


def _descargar_via_eutils(tax_id, nombre_limpio, destino, max_proteins=50000):
    """Descarga proteinas RefSeq via E-utilities.
    Filtra por srcdb_refseq y aplica muestreo si excede el limite."""
    log("Buscando proteinas RefSeq del tax_id " + str(tax_id) + " ...")
    try:
        # Busqueda con filtro RefSeq (sin latest, que no aplica a protein)
        r = requests.get(NCBI + "/esearch.fcgi", params={
            "db": "protein",
            "term": "txid" + str(tax_id) + "[Organism] AND srcdb_refseq[PROP]",
            "retmax": str(max_proteins),
            "retmode": "json"
        }, timeout=120)
        r.raise_for_status()
        result = r.json().get("esearchresult", {})
        ids = result.get("idlist", [])
        total_encontradas = int(result.get("count", 0))

        log("  -> Encontradas " + str(total_encontradas) +
            " proteinas RefSeq; descargando hasta " + str(max_proteins))

        if not ids:
            log("  -> Sin proteinas RefSeq; intentando sin filtro ...", "warn")
            r = requests.get(NCBI + "/esearch.fcgi", params={
                "db": "protein",
                "term": "txid" + str(tax_id) + "[Organism]",
                "retmax": str(max_proteins),
                "retmode": "json"
            }, timeout=120)
            r.raise_for_status()
            ids = r.json().get("esearchresult", {}).get("idlist", [])
            if not ids:
                return None

        # Muestreo aleatorio reproducible si hay mas del limite
        if total_encontradas > max_proteins and len(ids) >= max_proteins:
            random.seed(tax_id)  # semilla reproducible por especie
            ids = random.sample(ids, max_proteins)
            log("  -> Muestreadas " + str(max_proteins) +
                " proteinas de " + str(total_encontradas), "warn")

        # Descarga por lotes de 500
        secuencias = []
        total_lotes = (len(ids) + 499) // 500
        for lote_num in range(total_lotes):
            inicio = lote_num * 500
            lote = ids[inicio:inicio + 500]
            if (lote_num + 1) % 20 == 0 or lote_num == 0 or lote_num == total_lotes - 1:
                log("  -> Lote " + str(lote_num + 1) + "/" + str(total_lotes))
            r2 = requests.get(NCBI + "/efetch.fcgi", params={
                "db": "protein",
                "id": ",".join(lote),
                "rettype": "fasta",
                "retmode": "text"
            }, timeout=120)
            if r2.status_code == 200 and r2.text:
                secuencias.append(r2.text)
            time.sleep(0.4)

        if not secuencias:
            return None

        with open(destino, "w", encoding="utf-8") as f:
            f.write("\n".join(secuencias))

        log("Proteoma guardado (" + str(len(ids)) + " proteinas)", "ok")
        return destino
    except Exception as e:
        log("  -> E-utilities error: " + str(e), "warn")
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
                    _guardar_prot(proteinas, header, "".join(seq))
                header = linea[1:].strip()
                seq = []
            else:
                seq.append(linea.strip())
        if header is not None:
            _guardar_prot(proteinas, header, "".join(seq))
    return proteinas


def _guardar_prot(lista, header, seq):
    seq = seq.upper()
    if not seq or len(seq) < 50:
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
    return shutil.which("hmmscan") is not None and os.path.exists(PFAM_DB)


def escanear_dominios_hmmer(proteinas, max_scan=200):
    dominios_por_prot = {}
    if not proteinas:
        return dominios_por_prot

    seleccion = proteinas[:max_scan]
    with tempfile.NamedTemporaryFile("w", suffix=".fasta", delete=False) as fd:
        for p in seleccion:
            fd.write(">" + p["accession"] + "\n" + p["secuencia"] + "\n")
        fasta = fd.name
    domtbl = fasta + ".domtbl"

    t_inicio = time.time()
    log("hmmscan contra Pfam (" + str(len(seleccion)) + " proteinas) ...")
    try:
        subprocess.run(["hmmscan", "--domtblout", domtbl,
                        "-E", "1e-3", "--domE", "1e-3",
                        "--cpu", "4", PFAM_DB, fasta],
                       check=True, capture_output=True, timeout=3600)
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
                query = campos[3]
                dominios_por_prot.setdefault(query, []).append({"dominio": dom})
    except subprocess.TimeoutExpired:
        log("HMMER: timeout", "warn")
    except Exception as e:
        log("HMMER error: " + str(e), "warn")
    finally:
        for f in (fasta, domtbl):
            if os.path.exists(f):
                try: os.unlink(f)
                except OSError: pass

    return dominios_por_prot


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


# ============================ FASE 4 · PRIORIZACION ============================
def priorizar_candidatos_donantes(candidatos, rasgo, especie_receptora, modelo, top=10):
    if not candidatos:
        return []

    listado = ""
    for i, p in enumerate(candidatos[:30]):
        desc_corta = (p.get("descripcion", "sin descripcion"))[:100]
        doms = ", ".join(p.get("dominios_relevantes", [])) or "ninguno"
        listado += (str(i + 1) + ". " + p["accession"] +
                    " | " + p.get("especie_donante", "?") +
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

    data = groq_json(system, user, modelo)
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


# ============================ INFORME ============================
def escribir_informe_v41(ruta, informe):
    ruta = Path(ruta)
    ruta.with_suffix(".json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# Busqueda Trans-especie Orquestada · AgroGenIA V4.1",
          "",
          "- **Fecha:** " + informe.get("fecha", "?"),
          "- **Rasgo objetivo:** " + informe.get("rasgo", "?"),
          "- **Especie receptora:** *" + informe.get("receptora", "?") + "*",
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
    md.append("| # | Accession | Donante | Score | Estrategia | Riesgo | Promotor |")
    md.append("|---|---|---|---|---|---|---|")

    for i, p in enumerate(informe.get("candidatos", []), 1):
        md.append("| " + str(i) +
                  " | " + p.get("accession", "?") +
                  " | " + p.get("especie_donante", "?") +
                  " | " + str(p.get("score_transferencia", 0)) +
                  " | " + p.get("estrategia", "?") +
                  " | " + p.get("riesgo_compatibility", "?") +
                  " | " + p.get("promotor", "?") + " |")

    md.append("")
    md.append("## Detalles de candidatos")
    md.append("")
    for i, p in enumerate(informe.get("candidatos", []), 1):
        md.append("### " + str(i) + ". " + p.get("accession", "?"))
        md.append("- **Especie donante:** " + p.get("especie_donante", "?"))
        md.append("- **Score de transferencia:** " + str(p.get("score_transferencia", 0)))
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


# ============================ MAIN ============================
def main():
    p = argparse.ArgumentParser(
        description="AgroGenIA V4.1 - Busqueda trans-especie orquestada",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--rasgo", default="tolerancia a sequia",
                   help="Rasgo objetivo (cualquier rasgo imaginable)")
    p.add_argument("--receptora", default="yuca", choices=list(RECEPTORA))
    p.add_argument("--max-por-especie", type=int, default=50,
                   help="Max proteinas por especie donante")
    p.add_argument("--max-hmmer", type=int, default=200,
                   help="Max proteinas a escanear con HMMER")
    p.add_argument("--top", type=int, default=10, help="Candidatos a priorizar")
    p.add_argument("--modelo", default="calidad", choices=list(MODELOS))
    p.add_argument("--salida", default="transespecie_orquestado")
    a = p.parse_args()

    banner()
    modelo = MODELOS[a.modelo]
    receptora = RECEPTORA[a.receptora]
    rasgo_norm = normalizar(a.rasgo.lower().strip())
    t_inicio = time.time()

    # ── FASE 0 · ORQUESTACION: LLM SUGIERE DONANTES ──
    fase_titulo(0, "ORQUESTACION - el LLM sugiere especies donantes")
    log('Rasgo objetivo: "' + a.rasgo + '"', "fase")
    log("Especie receptora: " + receptora["nombre"])

    sugerencias = sugerir_donantes_llm(a.rasgo, receptora, modelo)
    if not sugerencias:
        sys.exit("El LLM no pudo sugerir donantes. Verifica la conexion y reintenta.")

    log("El LLM sugirio " + str(len(sugerencias)) + " especies:", "ok")
    for s in sugerencias:
        log("  - " + s.get("nombre_cientifico", "?") +
            " (" + s.get("tipo", "?") + "): " + s.get("adaptacion", "?"))

    # ── FASE 1 · RESOLUCION DE DONANTES ──
    fase_titulo(1, "RESOLUCION - nombres a tax_ids + verificacion de genomas")
    validos, descartados = resolver_donantes(sugerencias, a.rasgo, modelo)

    log("Especies validas: " + str(len(validos)), "ok")
    log("Especies descartadas: " + str(len(descartados)), "warn")

    if not validos:
        sys.exit("No se pudieron resolver especies donantes con genoma disponible.")

    # ── FASE 2 · INGESTA MULTI-ESPECIE ──
    fase_titulo(2, "INGESTA MULTI-ESPECIE")
    destino_dir = Path("proteomas_donantes")
    destino_dir.mkdir(exist_ok=True)

    keywords = KEYWORDS_ESTRES.get(rasgo_norm, [])
    if not keywords:
        log("No hay keywords predefinidas para este rasgo; usando el rasgo literal", "warn")
        keywords = a.rasgo.split()

    candidatos_donantes = []
    for esp in validos:
        nombre_limpio = esp["nombre"].replace(" ", "_")
        log("Procesando: " + esp["nombre"] + " (" + esp.get("tipo", "?") + ")")
        prot_path = descargar_proteoma_especie(esp["tax_id"], nombre_limpio, destino_dir)
        if not prot_path:
            log("No se pudo descargar el proteoma de " + esp["nombre"], "warn")
            continue

        proteinas = parsear_fasta(prot_path)
        log("Proteinas parseadas: " + str(len(proteinas)))

        candidatos = filtrar_por_estres(proteinas, keywords)
        log("Candidatos con keywords de estres: " + str(len(candidatos)))

        if len(candidatos) > a.max_por_especie:
            random.seed(42)
            candidatos = random.sample(candidatos, a.max_por_especie)
            log("Muestreado a " + str(a.max_por_especie) + " proteinas", "warn")

        for c in candidatos:
            c["especie_donante"] = esp["nombre"]
            c["tipo_donante"] = esp.get("tipo", "")
        candidatos_donantes.extend(candidatos)

    log("Total de candidatos donantes: " + str(len(candidatos_donantes)), "ok")

    if not candidatos_donantes:
        log("No se encontraron candidatos con keywords. Continuando con todos ...", "warn")
        # Si no hay candidatos por keywords, usar una muestra de todas las proteinas
        for esp in validos:
            nombre_limpio = esp["nombre"].replace(" ", "_")
            prot_path = destino_dir / ("proteoma_" + nombre_limpio + ".faa")
            if prot_path.exists():
                proteinas = parsear_fasta(prot_path)
                muestra = proteinas[:a.max_por_especie]
                for c in muestra:
                    c["especie_donante"] = esp["nombre"]
                    c["tipo_donante"] = esp.get("tipo", "")
                candidatos_donantes.extend(muestra)
        log("Candidatos totales (sin filtro): " + str(len(candidatos_donantes)))

    if not candidatos_donantes:
        sys.exit("No se pudieron obtener candidatos. Verifica las especies y reintenta.")

    # ── FASE 3 · DOMINIOS ──
    fase_titulo(3, "ANOTACION DE DOMINIOS (HMMER)")
    dominios_estres = DOMINIOS_ESTRES.get(rasgo_norm, [])
    if hmmer_disponible():
        dominios = escanear_dominios_hmmer(candidatos_donantes, a.max_hmmer)
        for c in candidatos_donantes:
            c["dominios_raw"] = dominios.get(c["accession"], [])
            c["dominios_relevantes"] = tiene_dominios_relevantes(
                c["dominios_raw"], dominios_estres)
        n_con_dom = sum(1 for c in candidatos_donantes if c["dominios_relevantes"])
        log("Candidatos con dominios de estres: " + str(n_con_dom), "ok")
    else:
        log("HMMER no disponible; usando solo keywords", "warn")
        for c in candidatos_donantes:
            c["dominios_raw"] = []
            c["dominios_relevantes"] = []

    # ── FASE 4 · PRIORIZACION ──
    fase_titulo(4, "PRIORIZACION DE CANDIDATOS DONANTES")
    candidatos_priorizados = priorizar_candidatos_donantes(
        candidatos_donantes, a.rasgo, receptora, modelo, a.top)
    for c in candidatos_priorizados:
        log(c["accession"] + "  score " + str(c.get("score_transferencia", 0)) +
            "  (" + c.get("especie_donante", "?") + ")")

    # ── FASE 5 · COMPATIBILIDAD ──
    fase_titulo(5, "EVALUACION DE COMPATIBILIDAD")
    candidatos_compatibles = evaluar_compatibilidad(
        candidatos_priorizados, receptora, modelo)
    for c in candidatos_compatibles:
        log(c["accession"] + "  -> " + c.get("estrategia", "?") +
            "  (riesgo: " + c.get("riesgo_compatibility", "?") + ")")

    # ── FASE 6 · DISENO DE CONSTRUCTO ──
    fase_titulo(6, "DISENO DE CONSTRUCTO")
    candidatos_finales = disenar_constructos(candidatos_compatibles, receptora, modelo)
    for c in candidatos_finales[:5]:
        log(c["accession"] + "  -> promotor: " + c.get("promotor", "?"))

    # ── FASE 7 · BRAZO A ──
    fase_titulo(7, "BRAZO A - GENES CONOCIDOS EN RECEPTORA")
    genes_brazo_a = brazo_a_modelos(a.rasgo, receptora, keywords)
    log("Genes conocidos encontrados: " + str(len(genes_brazo_a)))

    # ── INFORME ──
    informe = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "rasgo": a.rasgo,
        "receptora": receptora["nombre"],
        "donantes_validos": validos,
        "donantes_descartados": descartados,
        "candidatos": candidatos_finales,
        "genes_brazo_a": genes_brazo_a,
        "nota": "Busqueda trans-especie V4.1 orquestada por LLM. Validacion experimental requerida.",
    }
    f_json, f_md = escribir_informe_v41(a.salida, informe)

    print("")
    print("=" * 66)
    log("Pipeline V4.1 completado en " + str(round(time.time() - t_inicio, 1)) + " s", "ok")
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