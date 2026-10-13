#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgroGenIA v3 - MODO DESCUBRIMIENTO (embudo invertido)
=======================================================
En lugar de buscar genes ya estudiados por palabra clave, parte del
proteoma completo, filtra proteinas NO caracterizadas, las anota con
dominios y estructuras predichas, y prioriza candidatos NOVELES.

Dos brazos:
  BRAZO A (literatura)  : flujo clasico NCBI -> genes conocidos
  BRAZO B (proteoma)    : proteoma -> filtrado -> candidatos virgenes
Luego cruza ambos (convergencia) y verifica novedad en PMC.

Fuentes (todas gratuitas, sin clave):
  - Proteoma            : NCBI Datasets API v2
  - Estructuras         : AlphaFold DB + ESMAtlas (fallback)
  - Dominios            : HMMER/Pfam local (opcional) o descripcion
  - Novedad             : NCBI PMC full-text
  - Razonamiento        : Groq (orquestador LLM)
"""
import os
import sys
import io
import json
import time
import zipfile
import argparse
import shutil
import subprocess
import tempfile
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
    "tolerancia a sequia":       "drought OR dehydration OR water deficit OR desiccation OR ABA",
    "tolerancia a sequía":       "drought OR dehydration OR water deficit OR desiccation OR ABA",
    "tolerancia a salinidad":    "salt tolerance OR salinity OR sodium transport OR SOS",
    "resistencia a enfermedades": "disease resistance OR pathogen OR defense OR R protein",
    "eficiencia de nitrogeno":   "nitrogen use OR nitrate OR ammonium assimilation",
    "rendimiento":               "yield OR biomass OR growth regulation",
    "tolerancia a calor":        "heat stress OR thermotolerance OR heat shock",
}

# Palabras clave que marcan una proteina como NO caracterizada
KEYWORDS_NO_CARACT = [
    "hypothetical", "uncharacterized", "unknown", "predicted protein",
    "putative protein", "expressed protein", "DUF", "probable protein",
]

# Descartar fragmentos y transposones
KEYWORDS_EXCLUIR = [
    "transposable element", "transposon", "retrotransposon",
    "fragment", "pseudogene",
]

# Dominios Pfam asociados a estres (para filtrar el Brazo B)
DOMINIOS_ESTRES = {
    "AP2": "respuesta a estres / desarrollo (familia AP2/ERF)",
    "ERF": "etileno y estres abiotico",
    "bZIP_1": "factores bZIP, via ABA",
    "bZIP_2": "factores bZIP, via ABA",
    "NAM": "familia NAC, senescencia y estres",
    "LEA_1": "proteinas LEA, deshidratacion",
    "LEA_2": "proteinas LEA, deshidratacion",
    "LEA_3": "proteinas LEA, deshidratacion",
    "C2": "dominio C2, senalizacion calcio/ABA",
    "HSF_DNA-bind": "factor de choque termico",
    "Pkinase": "quinasa, senalizacion",
    "RRM_1": "union a ARN, estabilidad de transcriptos",
    "Aquaporin": "acuaporina, transporte de agua",
    "NBS": "resistencia a enfermedades (NBS-LRR)",
    "LRR_1": "repeticiones ricas en leucina, defensa",
    "WRKY": "factor WRKY, defensa",
    "PPR": "pentatricopeptido, organulos",
    "zf-C2H2": "dedo de zinc, regulacion transcripcional",
}

# ============================ UTILIDADES ============================
def banner():
    print("")
    print("=" * 66)
    print("  AgroGenIA v3 - MODO DESCUBRIMIENTO (embudo invertido)")
    print("  Proteoma -> proteinas virgenes -> candidatos noveles")
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
    """Quita acentos para comparar claves de rasgos."""
    mapa = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAeiouNn")
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


# ============================ FASE 1 - INGESTA INVERTIDA ============================
def obtener_accession_genoma(tax_id):
    """Busca el accession del genoma de referencia en NCBI Datasets."""
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
        log("No se pudo obtener el accession del genoma: " + str(e), "warn")
        return None


def descargar_proteoma(accession, destino):
    """Descarga el proteoma (FASTA) desde NCBI Datasets como ZIP."""
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
    """Lee un FASTA y devuelve lista de proteinas."""
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
    # quitar la especie entre corchetes
    import re as _re
    resto = _re.sub(r"\s*\[[^\]]*\]\s*$", "", resto).strip()
    lista.append({
        "accession": accession,
        "descripcion": resto,
        "secuencia": seq,
        "longitud": len(seq),
    })


# ============================ FASE 2 - FILTRADO ============================
def filtrar_no_caracterizadas(proteinas, min_len=80):
    total = len(proteinas)
    candidatas, excluidas = [], 0
    for p in proteinas:
        desc = p["descripcion"].lower()
        # excluir fragmentos/transposones
        if any(k in desc for k in KEYWORDS_EXCLUIR):
            excluidas += 1
            continue
        if p["longitud"] < min_len:
            excluidas += 1
            continue
        # incluir si es no caracterizada
        if any(k.lower() in desc for k in KEYWORDS_NO_CARACT):
            candidatas.append(p)
    log("Proteomas totales           : " + str(total))
    log("Excluidas (fragmentos/transp): " + str(excluidas))
    log("No caracterizadas (virgenes): " + str(len(candidatas)), "ok")
    return candidatas


# ============================ FASE 3 - ESTRUCTURAS PREDICHAS ============================
def contar_estructuras_alphafold(tax_id):
    """Cuenta cuantas proteinas de la especie tienen estructura en AlphaFold DB."""
    try:
        r = requests.get(ALPHAFOLD + "/api/predictions",
                         params={"tax_id": tax_id, "size": 1}, timeout=60)
        if r.status_code != 200:
            return None
        data = r.json()
        if isinstance(data, dict):
            return data.get("total", data.get("totalHits"))
        if isinstance(data, list):
            return len(data)
        return None
    except Exception:
        return None


def buscar_estructura_candidata(p, tax_id):
    """Best-effort: intenta localizar estructura predicha para una candidata.
    1) UniProt por descripcion/gen -> AlphaFold
    2) ESMAtlas por accession como fallback."""
    # Intento 1: extraer posible gen de la descripcion (ej. MANES_15G136500v8)
    import re as _re
    m = _re.search(r"([A-Za-z0-9_]{6,25})", p["descripcion"])
    gen = m.group(1) if m else None
    if gen:
        try:
            q = "(gene_exact:" + gen + " OR gene:" + gen + ") AND taxonomy_id:" + str(tax_id)
            r = requests.get(UNIPROT + "/uniprotkb/search",
                             params={"query": q, "format": "json", "size": 1,
                                     "fields": "accession"}, timeout=45)
            if r.status_code == 200:
                res = r.json().get("results", [])
                if res:
                    acc = res[0].get("primaryAccession")
                    if acc:
                        return {"fuente": "AlphaFold DB",
                                "url": ALPHAFOLD + "/entry/" + acc}
        except Exception:
            pass
    # Intento 2: ESMAtlas (fallback, por accession NCBI)
    return {"fuente": "ESMAtlas (verificar manualmente)",
            "url": ESMATLAS + "/search?q=" + p["accession"]}


# ============================ FASE 4 - DOMINIOS (HMMER o fallback) ============================
def hmmer_disponible():
    return shutil.which("hmmscan") is not None and os.path.exists(PFAM_DB)


def escanear_dominios_hmmer(proteinas, salida_base):
    """Corre hmmscan contra Pfam para una lista de proteinas."""
    dominios_por_prot = {}
    with tempfile.NamedTemporaryFile("w", suffix=".fasta", delete=False) as fd:
        for p in proteinas:
            fd.write(">" + p["accession"] + "\n" + p["secuencia"] + "\n")
        fasta = fd.name
    domtbl = fasta + ".domtbl"
    try:
        subprocess.run(["hmmscan", "--domtblout", domtbl,
                        "-E", "1e-3", "--domE", "1e-3",
                        "--cpu", "4", PFAM_DB, fasta],
                       check=True, capture_output=True, timeout=3600)
        with open(domtbl) as fh:
            for linea in fh:
                if linea.startswith("#"):
                    continue
                campos = linea.split()
                if len(campos) < 4:
                    continue
                dom = campos[0]      # nombre del dominio
                acc = campos[1]
                # la query accession suele estar en campos[3]
                query = campos[3]
                dominios_por_prot.setdefault(query, []).append(
                    {"dominio": dom, "accession": acc})
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


def tiene_dominio_estres(lista_doms):
    """Devuelve los dominios de estres presentes en una lista."""
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


def anotar_dominios(candidatas, max_hmmer):
    """Anota dominios. Usa HMMER si esta disponible, sino solo descripcion."""
    if hmmer_disponible():
        n = min(len(candidatas), max_hmmer)
        log("HMMER detectado. Escaneando " + str(n) + " proteinas contra Pfam ...", "ok")
        sub = candidatas[:n]
        doms = escanear_dominios_hmmer(sub, "hmmer")
        for p in sub:
            p["dominios_raw"] = doms.get(p["accession"], [])
            p["dominios_estres"] = tiene_dominio_estres(p["dominios_raw"])
        return candidatas, True
    else:
        log("HMMER/Pfam no disponible; usando solo descripcion.", "warn")
        for p in candidatas:
            p["dominios_raw"] = []
            p["dominios_estres"] = []
        return candidatas, False


# ============================ BRAZO A - LITERATURA (flujo clasico) ============================
def brazo_a_literatura(especie, terminos, rasgo, modelo, max_genes=10):
    """Flujo clasico: NCBI keyword -> priorizacion. Devuelve genes conocidos."""
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


# ============================ FASE 5 - PRIORIZACION BRAZO B ============================
def priorizar_noveles(candidatas, rasgo, especie, modelo, historial, top_novel):
    """El LLM puntua las proteinas virgenes con pistas funcionales."""
    # Preferir las que tienen dominios de estres
    con_dom = [c for c in candidatas if c.get("dominios_estres")]
    sin_dom = [c for c in candidatas if not c.get("dominios_estres")]
    pool = (con_dom + sin_dom)[:max(top_novel * 3, 30)]

    listado = ""
    for i, p in enumerate(pool):
        doms = ", ".join(d["dominio"] for d in p.get("dominios_estres", [])) or "ninguno conocido"
        listado += (str(i + 1) + ". " + p["accession"] +
                    " | desc: " + (p["descripcion"] or "sin descripcion") +
                    " | dominios estres: " + doms + "\n")

    hist_txt = ""
    if historial:
        hist_txt = "\nDescubrimientos previos (retroalimentacion):\n" + json.dumps(
            historial[:5], ensure_ascii=False, indent=1) + "\n"

    system = ("Eres experto en genomica funcional de plantas. Priorizas proteinas NO "
              "caracterizadas como candidatos noveles para un rasgo, usando dominios, "
              "descripcion y evidencia indirecta. Eres conservador: indicas incertidumbre.")
    user = ("Prioriza estas proteinas NO caracterizadas de " + especie["nombre"] +
            " como candidatos NOVELES para el rasgo \"" + rasgo + "\".\n" +
            hist_txt + "\nCandidatas virgenes:\n" + listado +
            "\nInstrucciones:\n" +
            "1. Puntua cada una de 0 a 100 como candidato NOVEL plausible.\n" +
            "2. Indica la pista funcional principal (dominio, descripcion).\n" +
            "3. Senala el nivel de especulacion (alta/media/baja).\n\n" +
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
    return pool[:top_novel]


# ============================ FASE 6 - CONVERGENCIA + NOVEDAD ============================
def verificar_novedad_pmc(candidatos):
    """Busca en PMC si el accession/gen ha sido mencionado en la literatura."""
    for c in candidatos:
        # usar el accession y posibles genes de la descripcion
        import re as _re
        terminos = [c["accession"]]
        m = _re.search(r"([A-Za-z0-9_]{6,25})", c.get("descripcion", ""))
        if m:
            terminos.append(m.group(1))
        total = 0
        for t in terminos:
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
        log("  PMC " + c["accession"] + ": " + estado,
            "ok" if total == 0 else "warn")
    return candidatos


def analisis_convergencia(noveles, conocidos, rasgo, especie, modelo):
    """El LLM cruza Brazo A vs Brazo B."""
    nov_txt = json.dumps([{"accession": n["accession"], "pista": n.get("pista", ""),
                           "dominios": [d["dominio"] for d in n.get("dominios_estres", [])]}
                          for n in noveles], ensure_ascii=False, indent=1)
    con_txt = json.dumps([{"simbolo": k["simbolo"], "descripcion": k["descripcion"]}
                          for k in conocidos], ensure_ascii=False, indent=1)
    system = ("Eres experto en genomica comparada. Analizas convergencia funcional entre "
              "candidatos noveles (no caracterizados) y genes conocidos para un rasgo.")
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
def escribir_informe_v3(ruta, informe):
    ruta = Path(ruta)
    ruta.with_suffix(".json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# Descubrimiento AgroGenIA v3",
          "",
          "- **Fecha:** " + informe["fecha"],
          "- **Especie:** *" + informe["especie"] + "*",
          "- **Rasgo:** " + informe["rasgo"],
          "- **Proteoma total:** " + str(informe["embudo"]["total"]),
          "- **No caracterizadas:** " + str(informe["embudo"]["no_caracterizadas"]),
          "- **Noveles priorizados:** " + str(len(informe["noveles"])),
          "",
          "## Embudo de filtrado",
          "",
          "| Etapa | Cantidad |",
          "|---|---|",
          "| Proteoma total | " + str(informe["embudo"]["total"]) + " |",
          "| Excluidas (fragmentos/transp) | " + str(informe["embudo"]["excluidas"]) + " |",
          "| No caracterizadas | " + str(informe["embudo"]["no_caracterizadas"]) + " |",
          "| Con dominios de estres | " + str(informe["embudo"]["con_dominios"]) + " |",
          "| Noveles priorizados | " + str(len(informe["noveles"])) + " |",
          "",
          "## Candidatos noveles",
          "",
          "| # | Accession | Score | Especulacion | Pista | Dominios | PMC | Novel |",
          "|---|---|---|---|---|---|---|---|"]
    for i, n in enumerate(informe["noveles"], 1):
        doms = ", ".join(d["dominio"] for d in n.get("dominios_estres", [])) or "-"
        md.append("| " + str(i) + " | " + n["accession"] +
                  " | " + str(n.get("score_novel", 0)) +
                  " | " + str(n.get("especulacion", "-")) +
                  " | " + str(n.get("pista", "-")) +
                  " | " + doms +
                  " | " + str(n.get("menciones_pmc", "?")) +
                  " | " + ("SI" if n.get("es_novel") else "no") + " |")
    md.append("")
    md.append("## Convergencia con genes conocidos (Brazo A)")
    md.append("")
    for cv in informe.get("convergencias", []):
        md.append("### " + cv.get("accession", "?"))
        md.append("- **Converge con:** " + cv.get("converge_con", "ninguno"))
        md.append("- **Tipo:** " + cv.get("tipo_convergencia", "ninguna"))
        md.append("- **Hipotesis:** " + cv.get("hipotesis", "n/d"))
        md.append("- **Confianza:** " + str(cv.get("confianza", "?")) + "%")
        md.append("")
    md.append("> Los candidatos marcados como NOVEL (0 menciones en PMC) son los de mayor interes.")
    ruta.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
    return ruta.with_suffix(".json"), ruta.with_suffix(".md")


# ============================ HISTORIAL (retroalimentacion) ============================
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
    # conservar solo los ultimos 50
    historial = historial[-50:]
    Path(ruta).write_text(json.dumps(historial, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    return historial


# ============================ MAIN ============================
def main():
    p = argparse.ArgumentParser(
        description="AgroGenIA v3 - Modo descubrimiento (embudo invertido)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--rasgo", default="tolerancia a sequia")
    p.add_argument("--especie", default="yuca", choices=list(ESPECIES))
    p.add_argument("--top-novel", type=int, default=10,
                   help="Candidatos noveles a priorizar")
    p.add_argument("--max-hmmer", type=int, default=150,
                   help="Max proteinas a escanear con HMMER")
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
    log("Historial previo (retroalimentacion): " + str(len(historial)) + " entradas")

    # ── FASE 1 - INGESTA INVERTIDA ──
    fase_titulo(1, "INGESTA INVERTIDA - descarga del proteoma")
    proteoma_path = Path("proteoma_" + a.especie + ".faa")
    if a.proteoma_local and os.path.exists(a.proteoma_local):
        proteoma_path = Path(a.proteoma_local)
        log("Usando proteoma local: " + str(proteoma_path))
    else:
        if proteoma_path.exists():
            log("Proteoma ya descargado previamente: " + str(proteoma_path))
        else:
            acc = obtener_accession_genoma(especie["tax_id"])
            if not acc:
                sys.exit("No se encontro genoma de referencia para esta especie.")
            log("Genoma de referencia: " + acc)
            if not descargar_proteoma(acc, proteoma_path):
                sys.exit("Fallo la descarga del proteoma.")
    proteinas = parsear_fasta(proteoma_path)
    log("Proteinas parseadas: " + str(len(proteinas)), "ok")
    n_alf = contar_estructuras_alphafold(especie["tax_id"])
    if n_alf is not None:
        log("Estructuras predichas en AlphaFold DB para la especie: " + str(n_alf))

    # ── FASE 2 - FILTRADO ──
    fase_titulo(2, "FILTRADO - proteinas no caracterizadas")
    candidatas = filtrar_no_caracterizadas(proteinas)
    if not candidatas:
        sys.exit("No se encontraron proteinas no caracterizadas.")

    # ── FASE 3/4 - DOMINIOS ──
    fase_titulo(3, "DOMINIOS - anotacion funcional")
    candidatas, uso_hmmer = anotar_dominios(candidatas, a.max_hmmer)
    con_dom = [c for c in candidatas if c.get("dominios_estres")]
    log("Candidatas con dominios de estres: " + str(len(con_dom)), "ok")

    # ── FASE 5 - PRIORIZACION BRAZO B ──
    fase_titulo(4, "PRIORIZACION BRAZO B - candidatos noveles")
    noveles = priorizar_noveles(candidatas, a.rasgo, especie, modelo,
                                historial, a.top_novel)
    for n in noveles[:a.top_novel]:
        log(n["accession"] + "  score " + str(n.get("score_novel", 0)) +
            "  (" + str(n.get("especulacion", "")) + ")")

    # ── ESTRUCTURAS para los top ──
    fase_titulo(5, "ESTRUCTURAS PREDICHAS (AlphaFold/ESMAtlas)")
    for n in noveles[:a.top_novel]:
        n["estructura"] = buscar_estructura_candidata(n, especie["tax_id"])
        log(n["accession"] + " -> " + n["estructura"]["fuente"])

    # ── NOVEDAD PMC ──
    if not a.saltar_pmc:
        fase_titulo(6, "NOVEDAD - verificacion en PMC")
        noveles = verificar_novedad_pmc(noveles[:a.top_novel])

    # ── CONVERGENCIA con Brazo A ──
    fase_titulo(7, "CONVERGENCIA - Brazo A vs Brazo B")
    conocidos = brazo_a_literatura(especie, terminos, a.rasgo, modelo, max_genes=10)
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
        "embudo": {
            "total": len(proteinas),
            "excluidas": len(proteinas) - len(candidatas),
            "no_caracterizadas": len(candidatas),
            "con_dominios": len(con_dom),
            "uso_hmmer": uso_hmmer,
        },
        "noveles": noveles,
        "conocidos_brazo_a": conocidos,
        "convergencias": convergencias,
        "nota": "Modo descubrimiento. Correlacion != causalidad; validar experimentalmente.",
    }
    f_json, f_md = escribir_informe_v3(a.salida, informe)

    nuevos = [{"accession": n["accession"], "rasgo": a.rasgo,
               "especie": especie["nombre"], "score": n.get("score_novel", 0),
               "fecha": informe["fecha"]} for n in noveles[:3]]
    guardar_historial(a.historial, historial, nuevos)

    print("")
    print("=" * 62)
    log("Pipeline v3 completado en " + str(round(time.time() - t_inicio, 1)) + " s", "ok")
    if noveles:
        top = noveles[0]
        log("Candidato novel principal: " + top["accession"] +
            " (score " + str(top.get("score_novel", 0)) + ")", "ok")
        if top.get("es_novel"):
            log("VERIFICADO como NOVEL (0 menciones en PMC)", "ok")
    log("Informe JSON : " + str(f_json), "ok")
    log("Informe MD   : " + str(f_md), "ok")
    print("=" * 62)
    print("")


if __name__ == "__main__":
    main()