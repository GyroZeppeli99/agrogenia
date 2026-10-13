#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgroGenIA · PILOTO v2 — con enriquecimiento funcional (Nivel 1)
Añade: proteina NCBI + dominios InterPro para genes sin anotacion UniProt.
"""
import os
import sys
import json
import time
import argparse
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
    sys.exit("Falta GROQ_API_KEY.  export GROQ_API_KEY=\"gsk_...\"")

client = Groq(api_key=GROQ_API_KEY)

MODELOS = {
    "calidad":   "openai/gpt-oss-120b",
    "rapido":    "openai/gpt-oss-20b",
    "razonador": "qwen/qwen3.8-27b",
}

NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UNIPROT = "https://rest.uniprot.org"
INTERPRO = "https://www.ebi.ac.uk/interpro/api"

ESPECIES = {
    "arabidopsis": {"tax_id": 3702, "nombre": "Arabidopsis thaliana"},
    "arroz":       {"tax_id": 4530, "nombre": "Oryza sativa"},
    "tomate":      {"tax_id": 4081, "nombre": "Solanum lycopersicum"},
    "yuca":        {"tax_id": 3983, "nombre": "Manihot esculenta"},
}

CONSULTAS_PREDEFINIDAS = {
    "tolerancia a sequia":       "drought OR dehydration OR water deficit OR desiccation OR ABA",
    "tolerancia a salinidad":    "salt tolerance OR salinity OR sodium transport OR SOS",
    "resistencia a enfermedades": "disease resistance OR pathogen OR defense OR R protein",
    "eficiencia de nitrogeno":   "nitrogen use OR nitrate OR ammonium assimilation",
    "rendimiento":               "yield OR biomass OR growth regulation",
    "tolerancia a calor":        "heat stress OR thermotolerance OR heat shock",
}


def banner():
    print("")
    print("==============================================================")
    print("  AgroGenIA - PILOTO v2 (enriquecimiento funcional)")
    print("  Genomica + IA para descubrimiento de genes en plantas")
    print("==============================================================")


def log(msg, nivel="dato"):
    iconos = {"fase": "#", "ok": "+", "warn": "!", "error": "x", "dato": "-"}
    print("  " + iconos.get(nivel, "-") + " " + msg)


def fase_titulo(n, titulo):
    print("")
    print("-" * 62)
    print("  FASE " + str(n) + " - " + titulo)
    print("-" * 62)


# ============================ CLIENTE GROQ ============================
def groq_chat(messages, modelo, temperature=0.2):
    for _intento in range(4):
        try:
            response = client.chat.completions.create(
                model=modelo,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            error_str = str(e)
            if "rate" in error_str.lower() or "429" in error_str:
                log("Limite de tasa alcanzado; esperando 30s ...", "warn")
                time.sleep(30)
                continue
            if "500" in error_str or "502" in error_str or "503" in error_str:
                log("Error temporal de Groq; reintentando ...", "warn")
                time.sleep(5)
                continue
            raise
    raise RuntimeError("Groq no respondio tras varios intentos.")


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
        bruto2 = groq_chat(mensajes, modelo, temperature=0.0)
        return extraer_json(bruto2)


def test_groq():
    log("Verificando conexion con Groq (libreria oficial)...")
    respuesta = groq_chat([{"role": "user",
                            "content": "Responde unicamente con la palabra: listo"}],
                          MODELOS["rapido"], temperature=0.0)
    log('Groq respondio: "' + respuesta.strip() + '"', "ok")
    log("Tu clave GROQ_API_KEY funciona correctamente.", "ok")


# ============================ FASE 0 - PLANIFICACION ============================
def fase0_planificar(rasgo, especie, modelo):
    clave = rasgo.lower().strip().replace("\u00ed", "i").replace("\u00f3", "o").replace("\u00e9", "e").replace("\u00e1", "a")
    if clave in CONSULTAS_PREDEFINIDAS:
        terminos = CONSULTAS_PREDEFINIDAS[clave]
        log("Terminos NCBI (predefinidos): " + terminos)
        return terminos

    system = ("Eres bioinformatico experto. Conviertes rasgos agronomicos en terminos "
              "de busqueda para NCBI Gene, en ingles, con sinonimos biologicos.")
    user = ('Rasgo: "' + rasgo + '"\nEspecie: ' + especie["nombre"] + "\n"
            "Devuelve UNA sola linea con terminos unidos por OR.\n"
            "Ejemplo: drought OR dehydration OR water deficit OR ABA")
    try:
        terminos = groq_chat([{"role": "system", "content": system},
                              {"role": "user", "content": user}],
                             modelo, temperature=0.1).strip().strip('"')
        log("Terminos NCBI (generados por el orquestador): " + terminos)
        return terminos
    except Exception as e:
        log("No se pudo planificar con el LLM (" + str(e) + "); usando el rasgo literal.", "warn")
        return rasgo


# ============================ FASE 1 - INGESTA ============================
def fase1_ingesta(especie, terminos, max_genes):
    term = "(" + terminos + ") AND txid" + str(especie["tax_id"]) + "[Organism]"
    params = {"db": "gene", "term": term, "retmax": max_genes * 3,
              "retmode": "json", "sort": "relevance"}
    r = requests.get(NCBI + "/esearch.fcgi", params=params, timeout=60)
    r.raise_for_status()
    ids = r.json()["esearchresult"]["idlist"]
    if not ids:
        return []

    time.sleep(0.4)
    r2 = requests.get(NCBI + "/esummary.fcgi",
                      params={"db": "gene", "id": ",".join(ids), "retmode": "json"},
                      timeout=60)
    r2.raise_for_status()
    resultados = r2.json().get("result", {})

    genes = []
    for gid in ids:
        d = resultados.get(gid)
        if not d:
            continue
        genes.append({
            "id_ncbi": gid,
            "simbolo": d.get("name", "?"),
            "nombre_oficial": d.get("nomenclaturesymbol") or d.get("name", ""),
            "descripcion": d.get("description", "sin descripcion"),
            "resumen": (d.get("summary") or "")[:500],
            "url_ncbi": "https://www.ncbi.nlm.nih.gov/gene/" + gid,
        })
        if len(genes) >= max_genes:
            break
    return genes


# ============================ FASE 2 - PRIORIZACION ============================
def fase2_priorizar(genes, rasgo, especie, modelo):
    listado = "\n".join("- " + g["simbolo"] + " | " + g["descripcion"] for g in genes)
    system = ("Eres genetista vegetal experto. Priorizas genes candidatos con rigor "
              "cientifico, distinguiendo evidencia causal de correlacion.")
    user = ('Prioriza estos genes de ' + especie["nombre"] + ' para el rasgo "' + rasgo + '".\n\n'
            "Genes candidatos:\n" + listado + "\n\n"
            "Instrucciones:\n"
            "1. Pontua cada gen de 0 a 100 segun probabilidad de relacion CAUSAL.\n"
            "2. Clasifica la evidencia como alta, media o baja.\n"
            "3. Incluye justificacion breve.\n\n"
            "Devuelve SOLO JSON:\n"
            '{"ranking":[{"simbolo":"...","score":87,"motivo":"...","evidencia":"alta"}]}')

    data = groq_json(system, user, modelo)
    scores = {}
    for x in data.get("ranking", []):
        if isinstance(x, dict) and "simbolo" in x:
            scores[x["simbolo"].upper()] = x

    for g in genes:
        m = scores.get(g["simbolo"].upper()) or scores.get(g["nombre_oficial"].upper())
        g["score"] = int(m.get("score", 0)) if m else 0
        g["motivo"] = (m or {}).get("motivo", "sin priorizar")
        g["evidencia"] = (m or {}).get("evidencia", "")

    genes.sort(key=lambda x: x["score"], reverse=True)
    return genes


# ============================ FASE 3 - INTEGRACION FUNCIONAL ============================
def buscar_uniprot(simbolo, tax_id):
    query = "(gene_exact:" + simbolo + " OR gene:" + simbolo + ") AND taxonomy_id:" + str(tax_id)
    params = {"query": query, "format": "json", "size": 1,
              "fields": "accession,gene_names,protein_name,cc_function,sequence,length"}
    try:
        r = requests.get(UNIPROT + "/uniprotkb/search", params=params, timeout=60)
        if r.status_code != 200:
            return None
        lista = r.json().get("results", [])
        if not lista:
            return None
        e = lista[0]
        return {
            "accession": e.get("primaryAccession") or e.get("accession", ""),
            "nombre_proteina": e.get("protein_name", ""),
            "funcion": e.get("cc_function", "")[:600],
            "longitud": e.get("length", 0),
        }
    except Exception:
        return None


def obtener_proteina_ncbi(id_ncbi):
    """Descarga la secuencia proteica de NCBI y extrae el nombre del producto.
    Para genes LOC*, el producto RefSeq suele ser muy informativo."""
    try:
        r = requests.get(NCBI + "/elink.fcgi",
                         params={"dbfrom": "gene", "db": "protein",
                                 "id": id_ncbi, "retmode": "json"},
                         timeout=30)
        if r.status_code != 200:
            return None
        links = r.json().get("linksets", [])
        prot_ids = []
        for ls in links:
            for ldb in ls.get("linksetdbs", []):
                if ldb.get("dbto") == "protein":
                    prot_ids = ldb.get("links", [])
                    break
            if prot_ids:
                break
        if not prot_ids:
            return None

        time.sleep(0.4)
        r2 = requests.get(NCBI + "/efetch.fcgi",
                          params={"db": "protein", "id": prot_ids[0],
                                  "rettype": "fasta", "retmode": "text"},
                          timeout=30)
        if r2.status_code != 200:
            return None
        lineas = r2.text.strip().split("\n")
        if len(lineas) < 2:
            return None
        header = lineas[0].lstrip(">").strip()
        partes = header.split(" ", 1)
        accession = partes[0]
        resto = partes[1] if len(partes) > 1 else ""
        producto = re.sub(r"\s*\[[^\]]*\]\s*$", "", resto).strip()
        secuencia = "".join(lineas[1:]).replace(" ", "").upper()
        return {"accession": accession,
                "producto": producto,
                "secuencia": secuencia,
                "longitud": len(secuencia)}
    except Exception:
        return None


def anotar_interpro(secuencia, timeout=120):
    """Version de DEPURACION: imprime la respuesta cruda de InterPro
    para descubrir la estructura real. Devuelve dominios si los encuentra."""
    if not secuencia or len(secuencia) < 20:
        return None

    url_submit = "https://www.ebi.ac.uk/interpro/api/search/sequence/"
    try:
        r = requests.post(url_submit,
                          data={"sequence": secuencia},
                          headers={"Accept": "application/json"},
                          timeout=timeout)
        log("InterPro HTTP " + str(r.status_code), "warn")
        # Mostrar los primeros 400 caracteres de la respuesta cruda
        log("InterPro crudo: " + r.text[:400].replace("\n", " "), "warn")

        if r.status_code not in (200, 201):
            return None
        data = r.json()
        log("Claves del JSON: " + str(list(data.keys())), "warn")

        # Intentar localizar resultados en varias estructuras posibles
        resultados = data.get("results", [])
        if not resultados and isinstance(data.get("payload"), dict):
            url_job = data["payload"].get("url")
            if url_job:
                log("InterPro es asincrono; polleando " + url_job, "warn")
                for _ in range(20):
                    time.sleep(3)
                    rj = requests.get(url_job, headers={"Accept": "application/json"}, timeout=timeout)
                    if rj.status_code == 200:
                        dj = rj.json()
                        resultados = dj.get("results", [])
                        if resultados:
                            break

        if not resultados:
            log("InterPro: sin resultados parseables.", "warn")
            return None

        # Mostrar la estructura del primer resultado para entenderla
        log("Primer resultado (claves): " + str(list(resultados[0].keys())), "warn")
        log("Primer resultado crudo: " + json.dumps(resultados[0])[:300], "warn")

        dominios = []
        go_terms = set()
        for res in resultados[:15]:
            metadata = res.get("metadata", {}) or {}
            nombre = metadata.get("name")
            tipo = metadata.get("type", "")
            if nombre:
                dominios.append({"tipo": tipo, "nombre": nombre,
                                 "accession": metadata.get("accession", "")})
        return {"dominios": dominios[:8], "go_terms": list(go_terms)[:10]}
    except Exception as e:
        log("InterPro error (" + e.__class__.__name__ + "): " + str(e), "warn")
        return None

def anotar_dominios_cdd(secuencia, timeout=90):
    """Busca dominios en NCBI CDD via Batch CD-Search (flujo asincrono real).
    1) POST la secuencia -> extrae el qrid (de JSON o del HTML)
    2) Pollea con el qrid hasta obtener los hits en JSON."""
    if not secuencia or len(secuencia) < 20:
        return None

    url = "https://www.ncbi.nlm.nih.gov/Structure/bwrpsb/bwrpsb.cgi"
    fasta = ">query\n" + secuencia

    try:
        # ── Paso 1: enviar la busqueda ──
        payload = {
            "cddef": "cdd",
            "queries": fasta,
            "useid10": "true",
            "maxhits": "20",
            "tdata": "hits",
        }
        r = requests.post(url, data=payload, timeout=timeout)
        log("CDD envio HTTP " + str(r.status_code) +
            " (Content-Type: " + r.headers.get("Content-Type", "?") + ")", "warn")

        qrid = None
        data = None

        # Intentar parsear como JSON primero
        try:
            data = r.json()
            qrid = data.get("qrid")
            log("CDD: respuesta JSON directa, qrid=" + str(qrid), "warn")
        except ValueError:
            # Es HTML: extraer el qrid con regex
            m = re.search(r'qrid["\s=:]+([A-Za-z0-9]+)', r.text, re.IGNORECASE)
            if not m:
                m = re.search(r'([A-F0-9]{20,})', r.text)
            if m:
                qrid = m.group(1)
                log("CDD: qrid extraido del HTML = " + qrid, "warn")
            else:
                log("CDD: no se encontro qrid en la respuesta.", "warn")
                return None

        # Si la respuesta JSON directa ya trae hits, usarlos
        if data and data.get("hits"):
            hits = data["hits"]
        else:
            if not qrid:
                return None
            # ── Paso 2: pollear los resultados con el qrid ──
            hits = None
            for intento in range(15):
                time.sleep(3)
                params = {"cddef": "cdd", "qrid": qrid, "tdata": "hits"}
                r2 = requests.get(url, params=params,
                                  headers={"Accept": "application/json"},
                                  timeout=timeout)
                log("CDD poll #" + str(intento + 1) + " HTTP " + str(r2.status_code) +
                    " (Content-Type: " + r2.headers.get("Content-Type", "?") + ")", "warn")
                try:
                    d2 = r2.json()
                except ValueError:
                    log("CDD poll crudo: " + r2.text[:200].replace("\n", " "), "warn")
                    continue
                status = d2.get("status")
                log("CDD status=" + str(status) +
                    " claves=" + str(list(d2.keys())), "warn")
                hits = d2.get("hits")
                if hits:
                    break

        if not hits:
            log("CDD: sin dominios tras el polling.", "warn")
            return None

        log("CDD primer hit (claves): " + str(list(hits[0].keys())), "warn")

        # ── Paso 3: parsear dominios ──
        dominios = []
        for h in hits[:15]:
            nombre = h.get("shortname") or h.get("title") or h.get("accession", "")
            titulo = h.get("title", "")
            acc = h.get("accession", "")
            evalue = h.get("evalue", "")
            if nombre:
                dominios.append({
                    "tipo": "CDD",
                    "nombre": nombre,
                    "titulo": titulo,
                    "accession": acc,
                    "evalue": str(evalue),
                })
        return {"dominios": dominios[:8], "go_terms": []}

    except Exception as e:
        log("CDD error (" + e.__class__.__name__ + "): " + str(e), "warn")
        return None

def enlace_tair(simbolo):
    if re.fullmatch(r"AT[1-5CM]G\d{5}", simbolo or "", re.IGNORECASE):
        return "https://www.arabidopsis.org/servlets/TairObject?type=locus&name=" + simbolo.upper()
    return None


def fase3_integrar(top_genes, rasgo, especie, modelo):
    for g in top_genes:
        log("Consultando UniProt para " + g["simbolo"] + " ...")
        g["uniprot"] = buscar_uniprot(g["simbolo"], especie["tax_id"])
        if not g["uniprot"] and g["nombre_oficial"] != g["simbolo"]:
            g["uniprot"] = buscar_uniprot(g["nombre_oficial"], especie["tax_id"])

        if g["uniprot"] and g["uniprot"]["accession"]:
            g["alphafold"] = "https://alphafold.ebi.ac.uk/entry/" + g["uniprot"]["accession"]
        else:
            # ---------- ENRIQUECIMIENTO FUNCIONAL (Nivel 1) ----------
            log("  -> Sin datos UniProt. Activando anotacion por secuencia...", "warn")
            prot = obtener_proteina_ncbi(g["id_ncbi"])
            if prot:
                g["proteina_ncbi"] = prot
                log("  -> Proteina NCBI: " + prot["accession"] + " (" + str(prot["longitud"]) + " aa)", "ok")
                if prot.get("producto"):
                    log("  -> Producto: " + prot["producto"][:90], "dato")
                log("  -> InterPro: buscando dominios funcionales...")
                interpro = anotar_dominios_cdd(prot["secuencia"])
                if interpro and interpro.get("dominios"):
                    g["interpro"] = interpro
                    d_txt = ", ".join(d["nombre"] for d in interpro["dominios"][:4])
                    log("  -> Dominios detectados: " + d_txt, "ok")
                else:
                    log("  -> InterPro sin dominios; se usara solo el producto proteico.", "warn")
                time.sleep(1.5)
            else:
                log("  -> No hay proteina asociada en NCBI para este gen.", "warn")

        g["tair"] = enlace_tair(g["simbolo"]) or enlace_tair(g["nombre_oficial"])
        time.sleep(0.3)

    # ---------- Contexto enriquecido para el LLM ----------
    contexto = ""
    for g in top_genes:
        u = g.get("uniprot") or {}
        prot = g.get("proteina_ncbi") or {}
        ip = g.get("interpro") or {}
        contexto += "\n## " + g["simbolo"] + "\n"
        contexto += "Descripcion NCBI: " + g["descripcion"] + "\n"
        if g.get("resumen"):
            contexto += "Resumen: " + g["resumen"][:300] + "\n"
        contexto += "Proteina UniProt: " + (u.get("nombre_proteina") or "n/d") + "\n"
        contexto += "Funcion anotada: " + (u.get("funcion") or "n/d") + "\n"
        if prot.get("producto"):
            contexto += "Producto proteico (RefSeq): " + prot["producto"] + "\n"
        if ip.get("dominios"):
            d_txt = "; ".join(d["nombre"] + " (" + d["tipo"] + ")" for d in ip["dominios"])
            contexto += "Dominios proteicos detectados: " + d_txt + "\n"
        if ip.get("go_terms"):
            contexto += "Terminos GO: " + ", ".join(ip["go_terms"][:6]) + "\n"

    system = ("Eres experto en biologia molecular de plantas. Elaboras perfiles "
              "funcionales precisos, indicando incertidumbre cuando la evidencia es limitada.")
    user = ('Con los datos de abajo, genera el perfil funcional de cada gen para el rasgo "'
            + rasgo + '" en ' + especie["nombre"] + '.\n' + contexto +
            "\nPara cada gen indica: mecanismo molecular, via metabolica, dominios estructurales y "
            "efecto esperado de un knockout.\n\n"
            "Devuelve SOLO JSON:\n"
            '{"perfiles":[{"simbolo":"...","mecanismo":"...","via":"...","dominios":["..."],"efecto_knockout":"...","confianza":80}]}')

    data = groq_json(system, user, modelo)
    perfiles = {}
    for p in data.get("perfiles", []):
        if isinstance(p, dict) and "simbolo" in p:
            perfiles[p["simbolo"].upper()] = p

    for g in top_genes:
        g["perfil"] = perfiles.get(g["simbolo"].upper()) or perfiles.get(g["nombre_oficial"].upper()) or {}
    return top_genes


# ============================ FASE 4 - VALIDACION ============================
def fase4_validar(top_genes, rasgo, especie, modelo):
    gen_top = top_genes[0]["simbolo"]
    contexto = json.dumps(
        [{"simbolo": g["simbolo"], "score": g["score"],
          "motivo": g.get("motivo", ""), "perfil": g.get("perfil", {})} for g in top_genes],
        ensure_ascii=False, indent=1)

    system = ("Eres investigador principal en mejora genetica vegetal. Disenas planes "
              "experimentales rigurosos, realistas y escalables.")
    user = ('Con base en estos candidatos para "' + rasgo + '" en ' + especie["nombre"] + ",\n"
            "disena un plan de validacion experimental enfocado en " + gen_top + ".\n\n"
            "Candidatos:\n" + contexto + "\n\n"
            "Devuelve SOLO JSON:\n"
            '{"hipotesis":"...",\n'
            ' "edicion_crispr":{"gen_objetivo":"...","estrategia":"...","guias_sugeridas":"...","controles":"..."},\n'
            ' "fenotipado":"...",\n'
            ' "validacion_estadistica":"...",\n'
            ' "cronograma_semanas":12,\n'
            ' "riesgos":["..."],\n'
            ' "advertencia_causalidad":"..."}')

    return groq_json(system, user, modelo, temperature=0.3)


# ============================ INFORME ============================
def escribir_informe(ruta, informe):
    ruta = Path(ruta)
    ruta.with_suffix(".json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")

    md = []
    md.append("# Informe AgroGenIA (v2, enriquecido)")
    md.append("")
    md.append("- **Fecha:** " + informe["fecha"])
    md.append("- **Especie:** *" + informe["especie"] + "*")
    md.append("- **Rasgo:** " + informe["rasgo"])
    md.append("- **Consulta NCBI:** `" + informe["terminos"] + "`")
    md.append("- **Modelo LLM:** `" + informe["modelo"] + "`")
    md.append("")
    md.append("## Genes candidatos priorizados")
    md.append("")
    md.append("| # | Gen | Score | Evidencia | Motivo | Enlaces |")
    md.append("|---|-----|-------|-----------|--------|---------|")
    for i, g in enumerate(informe["candidatos"], 1):
        enlaces = ["[NCBI](" + g["url_ncbi"] + ")"]
        if g.get("alphafold"):
            enlaces.append("[AlphaFold](" + g["alphafold"] + ")")
        if g.get("tair"):
            enlaces.append("[TAIR](" + g["tair"] + ")")
        md.append("| " + str(i) + " | **" + g["simbolo"] + "** | " + str(g["score"]) +
                  " | " + str(g.get("evidencia", "-")) + " | " + str(g.get("motivo", "-")) +
                  " | " + " · ".join(enlaces) + " |")

    md.append("")
    md.append("## Perfiles funcionales")
    md.append("")
    for g in informe["candidatos"]:
        p = g.get("perfil", {})
        prot = g.get("proteina_ncbi") or {}
        ip = g.get("interpro") or {}
        md.append("### " + g["simbolo"] + " (confianza " + str(p.get("confianza", "?")) + "%)")
        md.append("- **Mecanismo:** " + str(p.get("mecanismo", "n/d")))
        md.append("- **Via:** " + str(p.get("via", "n/d")))
        md.append("- **Dominios (inferidos):** " + (", ".join(p.get("dominios", [])) or "n/d"))
        if prot.get("producto"):
            md.append("- **Producto proteico (RefSeq):** " + prot["producto"])
        if ip.get("dominios"):
            md.append("- **Dominios detectados (InterPro):** " +
                      ", ".join(d["nombre"] for d in ip["dominios"]))
        if ip.get("go_terms"):
            md.append("- **Terminos GO:** " + ", ".join(ip["go_terms"][:6]))
        md.append("- **Efecto del knockout:** " + str(p.get("efecto_knockout", "n/d")))
        md.append("")

    v = informe["validacion"]
    md.append("## Plan de validacion experimental")
    md.append("")
    md.append("**Hipotesis:** " + str(v.get("hipotesis", "n/d")))
    md.append("")
    md.append("### Edicion CRISPR-Cas9")
    ec = v.get("edicion_crispr", {})
    md.append("- Gen objetivo: " + str(ec.get("gen_objetivo", "n/d")))
    md.append("- Estrategia: " + str(ec.get("estrategia", "n/d")))
    md.append("- Guias sugeridas: " + str(ec.get("guias_sugeridas", "n/d")))
    md.append("- Controles: " + str(ec.get("controles", "n/d")))
    md.append("")
    md.append("**Fenotipado:** " + str(v.get("fenotipado", "n/d")))
    md.append("")
    md.append("**Validacion estadistica:** " + str(v.get("validacion_estadistica", "n/d")))
    md.append("")
    md.append("**Cronograma:** " + str(v.get("cronograma_semanas", "?")) + " semanas")
    md.append("")
    md.append("**Riesgos:**")
    for rsk in v.get("riesgos", []):
        md.append("- " + str(rsk))
    md.append("")
    md.append("> **Advertencia:** " + str(v.get("advertencia_causalidad", "Correlacion != causalidad.")))

    ruta.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
    return ruta.with_suffix(".json"), ruta.with_suffix(".md")


# ============================ MAIN ============================
def main():
    p = argparse.ArgumentParser(
        description="AgroGenIA - Piloto v2 con enriquecimiento funcional",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--rasgo", default="tolerancia a sequia",
                   help="Ventaja agronomica buscada")
    p.add_argument("--especie", default="arabidopsis", choices=list(ESPECIES))
    p.add_argument("--max-genes", type=int, default=12, help="Genes a recuperar de NCBI")
    p.add_argument("--top", type=int, default=5, help="Candidatos a analizar en profundidad")
    p.add_argument("--modelo", default="calidad", choices=list(MODELOS))
    p.add_argument("--salida", default="informe_agrogenia", help="Nombre base del informe")
    p.add_argument("--test-groq", action="store_true", help="Solo verifica la clave de Groq")
    a = p.parse_args()

    banner()

    if a.test_groq:
        test_groq()
        return

    modelo = MODELOS[a.modelo]
    especie = ESPECIES[a.especie]
    t_inicio = time.time()

    fase_titulo(0, "PLANIFICACION")
    log('Consulta: "Genes de ' + a.rasgo + " en " + especie["nombre"] + '"', "fase")
    terminos = fase0_planificar(a.rasgo, especie, modelo)

    fase_titulo(1, "INGESTA - busqueda en NCBI Gene")
    genes = fase1_ingesta(especie, terminos, a.max_genes)
    if not genes:
        sys.exit("No se encontraron genes. Prueba con otro rasgo o especie.")
    log(str(len(genes)) + " genes recuperados de NCBI", "ok")

    fase_titulo(2, "PRIORIZACION - puntuacion con el orquestador LLM")
    genes = fase2_priorizar(genes, a.rasgo, especie, modelo)
    for g in genes[:a.top]:
        log(g["simbolo"].ljust(14) + " score " + str(g["score"]).rjust(3) +
            "  (" + str(g.get("evidencia", "")) + ")")

    fase_titulo(3, "INTEGRACION FUNCIONAL (enriquecida)")
    top_genes = fase3_integrar(genes[:a.top], a.rasgo, especie, modelo)
    for g in top_genes:
        if g.get("uniprot"):
            extra = "UniProt ok"
        elif g.get("interpro") or g.get("proteina_ncbi"):
            extra = "enriquecido (NCBI+InterPro)"
        else:
            extra = "sin datos"
        linea = g["simbolo"].ljust(14) + " " + extra
        if g.get("alphafold"):
            linea += " -> AlphaFold: " + g["alphafold"]
        log(linea)

    fase_titulo(4, "VALIDACION - diseno experimental")
    validacion = fase4_validar(top_genes, a.rasgo, especie, modelo)
    log("Hipotesis: " + str(validacion.get("hipotesis", "n/d"))[:140] + " ...", "ok")

    informe = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "especie": especie["nombre"],
        "tax_id": especie["tax_id"],
        "rasgo": a.rasgo,
        "terminos": terminos,
        "modelo": modelo,
        "candidatos": top_genes,
        "resto_genes": genes[a.top:],
        "validacion": validacion,
        "nota": "Piloto docente con enriquecimiento funcional. Correlacion != causalidad.",
    }
    f_json, f_md = escribir_informe(a.salida, informe)

    print("")
    print("=" * 62)
    log("Pipeline completado en " + str(round(time.time() - t_inicio, 1)) + " s", "ok")
    log("Candidato principal: " + top_genes[0]["simbolo"] +
        " (score " + str(top_genes[0]["score"]) + ")", "ok")
    log("Informe JSON : " + str(f_json), "ok")
    log("Informe MD   : " + str(f_md), "ok")
    print("=" * 62)
    print("")


if __name__ == "__main__":
    main()