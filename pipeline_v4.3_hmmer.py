#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgroGenIA V4.2 · BUSQUEDA TRANS-ESPECIE ORQUESTADA
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
    print("  AgroGenIA V4.2 · TRANS-ESPECIE + VALIDACION MULTI-FUENTE")
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
    """Descarga proteinas RefSeq via E-utilities con reintentos y rate limit robusto."""
    log("Buscando proteinas RefSeq del tax_id " + str(tax_id) + " ...")
    try:
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

        log("  -> Encontradas " + str(total_encontradas) + " proteinas RefSeq")

        if not ids:
            # Fallback: intentar sin filtro RefSeq
            log("  -> Sin RefSeq; intentando sin filtro ...", "warn")
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

        # Muestreo si excede el limite
        if total_encontradas > max_proteins and len(ids) >= max_proteins:
            random.seed(tax_id)
            ids = random.sample(ids, max_proteins)
            log("  -> Muestreadas " + str(max_proteins) + " de " + str(total_encontradas), "warn")

        # Descarga por lotes con REINTENTOS
        secuencias = []
        lotes_ok = 0
        lotes_fallidos = 0
        tamano_lote = 300  # reducido de 500 a 300 para evitar timeouts
        total_lotes = (len(ids) + tamano_lote - 1) // tamano_lote

        for lote_num in range(total_lotes):
            inicio = lote_num * tamano_lote
            lote = ids[inicio:inicio + tamano_lote]

            if (lote_num + 1) % 20 == 0 or lote_num == 0 or lote_num == total_lotes - 1:
                log("  -> Lote " + str(lote_num + 1) + "/" + str(total_lotes) +
                    " (ok:" + str(lotes_ok) + " fail:" + str(lotes_fallidos) + ")")

            # Reintentar hasta 3 veces por lote
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
                        time.sleep(2)  # esperar antes de reintentar
                except Exception:
                    time.sleep(2)

            if not exito:
                lotes_fallidos += 1

            time.sleep(1.0)  # rate limit conservador (1s entre lotes)

        log("  -> Lotes completados: " + str(lotes_ok) + " ok, " +
            str(lotes_fallidos) + " fallidos", "ok" if lotes_fallidos < 5 else "warn")

        if not secuencias:
            return None

        with open(destino, "w", encoding="utf-8") as f:
            f.write("\n".join(secuencias))

        log("Proteoma guardado (" + str(len(ids)) + " IDs solicitados)", "ok")
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
    if len(limpias) <= n:
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
    """Selecciona una muestra EQUILIBRADA por tipo de organismo ANTES de la
    priorizacion. No usa scores (aun no existen); solo garantiza que cada
    tipo de organismo tenga representacion en la muestra que vera el LLM."""
    por_tipo = {}
    for c in candidatos:
        tipo = c.get("tipo_donante", "") or "desconocido"
        por_tipo.setdefault(tipo, []).append(c)

    tipos = list(por_tipo.keys())
    n_tipos = len(tipos)
    if n_tipos == 0:
        return candidatos[:total_muestra]

    # Distribuir slots equitativamente entre los tipos
    slots_por_tipo = total_muestra // n_tipos
    resto = total_muestra % n_tipos

    seleccion = []
    for i, tipo in enumerate(tipos):
        # Los primeros tipos reciben 1 slot extra para cubrir el resto
        slots = slots_por_tipo + (1 if i < resto else 0)
        grupo = por_tipo[tipo]
        seleccion.extend(grupo[:slots])

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
    Europe PMC cubre PubMed + PMC + preprints (bioRxiv), por lo que es
    mas completo que NCBI PMC solo para verificar novedad."""
    resultados = {"menciones": 0, "novel": True, "articulos": []}
    try:
        query = '"' + accession + '"'
        r = requests.get(EUROPEPMC, params={
            "query": query,
            "format": "json",
            "pageSize": 5
        }, timeout=30)
        if r.status_code == 200:
            data = r.json()
            resultados["menciones"] = int(data.get("hitCount", 0))
            resultados["novel"] = (resultados["menciones"] == 0)
            lista = data.get("resultList", {}).get("result", [])
            for art in lista[:3]:
                resultados["articulos"].append({
                    "titulo": (art.get("title") or "")[:120],
                    "anio": art.get("pubYear", ""),
                    "fuente": art.get("source", ""),
                })
    except Exception as e:
        log("  Europe PMC error: " + str(e), "warn")
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

    # Europe PMC: el gen ha sido mencionado en literatura
    if epmc["menciones"] > 0:
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

        log("Validando " + acc + " (" + esp_donante + ") ...")

        # 1. Europe PMC (novedad + literatura)
        epmc = buscar_europepmc(acc_base, c.get("descripcion", ""))
        c["val_epmc"] = epmc
        estado = "NOVEL (0 menciones)" if epmc["novel"] else str(epmc["menciones"]) + " menciones"
        log("  Europe PMC: " + estado, "ok" if epmc["novel"] else "dato")
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
def escribir_informe_v42(ruta, informe):
    ruta = Path(ruta)
    ruta.with_suffix(".json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# Busqueda Trans-especie Orquestada · AgroGenIA V4.2",
          "",
          "- **Fecha:** " + informe.get("fecha", "?"),
          "- **Estrategia de seleccion:** " + informe.get("estrategia", "?"),
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
    md.append("| # | Accession | Donante | Score | Soporte | Europe PMC | Estrategia | Riesgo |")
    md.append("|---|---|---|---|---|---|---|---|")

    for i, p in enumerate(informe.get("candidatos", []), 1):
        epmc_t = p.get("val_epmc", {})
        soporte_t = p.get("soporte_multifuente", {})
        estado_t = "NOVEL" if epmc_t.get("novel") else str(epmc_t.get("menciones", 0)) + " menc."
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

        estado_epmc = "NOVEL" if epmc.get("novel") else str(epmc.get("menciones", 0)) + " menciones"
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


# ============================ MAIN ============================
def main():
    p = argparse.ArgumentParser(
        description="AgroGenIA V4.2 - Busqueda trans-especie orquestada",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--rasgo", default="tolerancia a sequia",
                   help="Rasgo objetivo (cualquier rasgo imaginable)")
    p.add_argument("--receptora", default="yuca", choices=list(RECEPTORA))
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
        # ── FASE 2 · INGESTA + MUESTREO PARA HMMER (criterio primario) ──
    fase_titulo(2, "INGESTA MULTI-ESPECIE + MUESTREO HMMER")
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

        prot_path = descargar_proteoma_especie(esp["tax_id"], nombre_limpio, destino_dir)
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

    # ── FASE 3 · HMMER PRIMARIO (estructura antes que texto) ──
    fase_titulo(3, "ANOTACION ESTRUCTURAL (HMMER como criterio primario)")
    dominios_estres = DOMINIOS_ESTRES.get(rasgo_norm, [])

    if hmmer_disponible():
        # Escaneo HMMER de toda la muestra (un solo hmmscan, carga Pfam 1 vez)
        dominios = escanear_dominios_hmmer(muestra_hmmer, max_scan=len(muestra_hmmer))
        for c in muestra_hmmer:
            c["dominios_raw"] = dominios.get(c["accession"], [])

        # FILTRO PRIMARIO: solo candidatos con dominios de estres
        candidatos_estructurales = filtrar_por_dominios_estres(
            muestra_hmmer, dominios_estres)
        log("Candidatos con dominios de estres (criterio primario): " +
            str(len(candidatos_estructurales)), "ok")

        # COMPLEMENTO SECUNDARIO: si hay pocos estructurales, anadir por keywords
        candidatos_finales = candidatos_estructurales
        accs_ya = set(c["accession"] for c in candidatos_finales)
        for c in candidatos_texto:
            if c["accession"] not in accs_ya:
                c.setdefault("dominios_relevantes", [])
                candidatos_finales.append(c)
                accs_ya.add(c["accession"])
        log("Candidatos combinados (estructura + texto): " +
            str(len(candidatos_finales)))

        # Limitar al top para el LLM
        max_final = a.max_por_especie * len(validos)
        if len(candidatos_finales) > max_final:
            # priorizar los que tienen dominios estructurales
            con_dom = [c for c in candidatos_finales if c.get("dominios_relevantes")]
            sin_dom = [c for c in candidatos_finales if not c.get("dominios_relevantes")]
            candidatos_finales = (con_dom + sin_dom)[:max_final]
            log("Limitado a " + str(max_final) +
                " candidatos (" + str(len(con_dom)) + " con dominios)", "warn")

        candidatos_donantes = candidatos_finales
    else:
        log("HMMER no disponible; usando SOLO keywords (criterio degradado)", "warn")
        candidatos_donantes = candidatos_texto
        for c in candidatos_donantes:
            c["dominios_raw"] = []
            c["dominios_relevantes"] = []

    if not candidatos_donantes:
        sys.exit("No se obtuvieron candidatos. Reintenta con mas muestra HMMER.")

    log("Candidatos finales para priorizar: " + str(len(candidatos_donantes)), "ok")

    # ── FASE 4 · PRIORIZACION + ESTRATEGIA DE SELECCION ──
    fase_titulo(4, "PRIORIZACION DE CANDIDATOS DONANTES")

    if a.estrategia == "B":
        # CLAVE: seleccionar muestra diversa ANTES de priorizar,
        # para que el LLM vea candidatos de todos los tipos de organismo
        log("Aplicando Estrategia B: DIVERSIDAD de donantes", "fase")
        muestra_diversa = seleccionar_muestra_diversa(candidatos_donantes, total_muestra=30)
        loguear_distribucion(muestra_diversa,
                             "Muestra diversa enviada al LLM (Estrategia B):")
        candidatos_priorizados = priorizar_candidatos_donantes(
            muestra_diversa, a.rasgo, receptora, modelo, a.top)
        loguear_distribucion(candidatos_priorizados,
                             "Distribucion final priorizada (Estrategia B):")
    else:
        log("Aplicando Estrategia A: priorizacion por ORTOLOGIA (sesgo natural)", "fase")
        candidatos_priorizados = priorizar_candidatos_donantes(
            candidatos_donantes, a.rasgo, receptora, modelo, a.top)
        loguear_distribucion(candidatos_priorizados,
                             "Distribucion final por tipo (Estrategia A):")

    for c in candidatos_priorizados:
        log(c["accession"] + "  score " + str(c.get("score_transferencia", 0)) +
            "  (" + c.get("especie_donante", "?") + " / " + c.get("tipo_donante", "?") + ")")

    # ── FASE 5 · VALIDACION MULTI-FUENTE (V4.2) ──
    fase_titulo(5, "VALIDACION MULTI-FUENTE (Europe PMC + STRING + GEO)")
    candidatos_validados = validar_multifuente(
        candidatos_priorizados, validos, a.rasgo)
    n_noveles = sum(1 for c in candidatos_validados if c.get("val_epmc", {}).get("novel"))
    log("Candidatos verificados como NOVEL en Europe PMC: " + str(n_noveles), "ok")


    # ── FASE 6 · COMPATIBILIDAD ──
    fase_titulo(6, "EVALUACION DE COMPATIBILIDAD")
    candidatos_compatibles = evaluar_compatibilidad(
        candidatos_validados, receptora, modelo)
    for c in candidatos_compatibles:
        log(c["accession"] + "  -> " + c.get("estrategia", "?") +
            "  (riesgo: " + c.get("riesgo_compatibility", "?") + ")")

    # ── FASE 7 · DISENO DE CONSTRUCTO ──
    fase_titulo(7, "DISENO DE CONSTRUCTO")
    candidatos_finales = disenar_constructos(candidatos_compatibles, receptora, modelo)
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
        "estrategia": ("B (diversidad equilibrada)" if a.estrategia == "B"
                       else "A (priorizacion por ortologia)"),
        "donantes_validos": validos,
        "donantes_descartados": descartados,
        "candidatos": candidatos_finales,
        "genes_brazo_a": genes_brazo_a,
        "nota": "Busqueda trans-especie V4.2 orquestada por LLM. Validacion experimental requerida.",
    }
    f_json, f_md = escribir_informe_v42(a.salida, informe)

    print("")
    print("=" * 66)
    log("Pipeline V4.2 completado en " + str(round(time.time() - t_inicio, 1)) + " s", "ok")
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