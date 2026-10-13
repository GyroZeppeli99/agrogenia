#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AgroGenIA · PILOTO con librería oficial de Groq
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
    sys.exit(f"❌ Falta una librería: {e}\nInstala con: pip install requests groq")

# ══════════════════════════ CONFIGURACIÓN ══════════════════════════
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

if not GROQ_API_KEY:
    sys.exit("❌ Falta GROQ_API_KEY.\n"
             "   export GROQ_API_KEY=\"gsk_...\"")

client = Groq(api_key=GROQ_API_KEY)

MODELOS = {
    "calidad":   "openai/gpt-oss-120b",
    "rapido":    "openai/gpt-oss-20b",
    "razonador": "qwen/qwen3.8-27b",
}

NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UNIPROT = "https://rest.uniprot.org"

ESPECIES = {
    "arabidopsis": {"tax_id": 3702, "nombre": "Arabidopsis thaliana"},
    "arroz":       {"tax_id": 4530, "nombre": "Oryza sativa"},
    "tomate":      {"tax_id": 4081, "nombre": "Solanum lycopersicum"},
    "yuca":        {"tax_id": 3983, "nombre": "Manihot esculenta"},
}

CONSULTAS_PREDEFINIDAS = {
    "tolerancia a sequía":      "drought OR dehydration OR water deficit OR desiccation OR ABA",
    "tolerancia a salinidad":   "salt tolerance OR salinity OR sodium transport OR SOS",
    "resistencia a enfermedades": "disease resistance OR pathogen OR defense OR R protein",
    "eficiencia de nitrógeno":  "nitrogen use OR nitrate OR ammonium assimilation",
    "rendimiento":              "yield OR biomass OR growth regulation",
    "tolerancia a calor":       "heat stress OR thermotolerance OR heat shock",
}


def banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║   🌱 AgroGenIA · PILOTO (librería oficial Groq)              ║
║   Genómica + IA para descubrimiento de genes en plantas      ║
╚══════════════════════════════════════════════════════════════╝""")


def log(msg, nivel="dato"):
    iconos = {"fase": "◆", "ok": "✔", "warn": "⚠", "error": "✖", "dato": "·"}
    print(f"  {iconos.get(nivel, '·')} {msg}")


def fase_titulo(n, titulo):
    print(f"\n{'─'*62}\n  FASE {n} · {titulo}\n{'─'*62}")


# ══════════════════════════ CLIENTE GROQ ══════════════════════════
def groq_chat(messages, modelo, temperature=0.2):
    """Usa la librería oficial de Groq."""
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
                log("Límite de tasa alcanzado; esperando 30s …", "warn")
                time.sleep(30)
                continue
            if "500" in error_str or "502" in error_str or "503" in error_str:
                log("Error temporal de Groq; reintentando …", "warn")
                time.sleep(5)
                continue
            raise
    raise RuntimeError("Groq no respondió tras varios intentos.")


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
                         "content": "Tu respuesta no era JSON válido. Devuelve SOLO el JSON."})
        bruto2 = groq_chat(mensajes, modelo, temperature=0.0)
        return extraer_json(bruto2)


def test_groq():
    log("Verificando conexión con Groq (librería oficial)…")
    respuesta = groq_chat([{"role": "user",
                            "content": "Responde únicamente con la palabra: listo"}],
                          MODELOS["rapido"], temperature=0.0)
    log(f'Groq respondió: "{respuesta.strip()}"', "ok")
    log("Tu clave GROQ_API_KEY funciona correctamente.", "ok")


# ══════════════════════ FASE 0 · PLANIFICACIÓN ══════════════════════
def fase0_planificar(rasgo, especie, modelo):
    clave = rasgo.lower().strip()
    if clave in CONSULTAS_PREDEFINIDAS:
        terminos = CONSULTAS_PREDEFINIDAS[clave]
        log(f"Términos NCBI (predefinidos): {terminos}")
        return terminos

    system = ("Eres bioinformático experto. Conviertes rasgos agronómicos en términos "
              "de búsqueda para NCBI Gene, en inglés, con sinónimos biológicos.")
    user = (f"Rasgo: \"{rasgo}\"\nEspecie: {especie['nombre']}\n"
            "Devuelve UNA sola línea con términos unidos por OR.\n"
            "Ejemplo: drought OR dehydration OR water deficit OR ABA")
    try:
        terminos = groq_chat([{"role": "system", "content": system},
                              {"role": "user", "content": user}],
                             modelo, temperature=0.1).strip().strip('"')
        log(f"Términos NCBI (generados por el orquestador): {terminos}")
        return terminos
    except Exception as e:
        log(f"No se pudo planificar con el LLM ({e}); usando el rasgo literal.", "warn")
        return rasgo


# ═══════════════════════ FASE 1 · INGESTA ═══════════════════════
def fase1_ingesta(especie, terminos, max_genes):
    term = f"({terminos}) AND txid{especie['tax_id']}[Organism]"
    params = {"db": "gene", "term": term, "retmax": max_genes * 3,
              "retmode": "json", "sort": "relevance"}
    r = requests.get(f"{NCBI}/esearch.fcgi", params=params, timeout=60)
    r.raise_for_status()
    ids = r.json()["esearchresult"]["idlist"]
    if not ids:
        return []

    time.sleep(0.4)
    r2 = requests.get(f"{NCBI}/esummary.fcgi",
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
            "descripcion": d.get("description", "sin descripción"),
            "resumen": (d.get("summary") or "")[:500],
            "url_ncbi": f"https://www.ncbi.nlm.nih.gov/gene/{gid}",
        })
        if len(genes) >= max_genes:
            break
    return genes


# ═══════════════════════ FASE 2 · PRIORIZACIÓN ═══════════════════════
def fase2_priorizar(genes, rasgo, especie, modelo):
    listado = "\n".join(f"- {g['simbolo']} | {g['descripcion']}" for g in genes)
    system = ("Eres genetista vegetal experto. Priorizas genes candidatos con rigor "
              "científico, distinguiendo evidencia causal de correlación.")
    user = f"""Prioriza estos genes de {especie['nombre']} para el rasgo "{rasgo}".

Genes candidatos:
{listado}

Instrucciones:
1. Puntúa cada gen de 0 a 100 según probabilidad de relación CAUSAL.
2. Clasifica la evidencia como alta, media o baja.
3. Incluye justificación breve.

Devuelve SOLO JSON:
{{"ranking":[{{"simbolo":"...","score":87,"motivo":"...","evidencia":"alta"}}]}}"""

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


# ════════════════════ FASE 3 · INTEGRACIÓN FUNCIONAL ════════════════════
def buscar_uniprot(simbolo, tax_id):
    query = f"(gene_exact:{simbolo} OR gene:{simbolo}) AND taxonomy_id:{tax_id}"
    params = {"query": query, "format": "json", "size": 1,
              "fields": "accession,gene_names,protein_name,cc_function,sequence,length"}
    try:
        r = requests.get(f"{UNIPROT}/uniprotkb/search", params=params, timeout=60)
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


def enlace_tair(simbolo):
    if re.fullmatch(r"AT[1-5CM]G\d{5}", simbolo or "", re.IGNORECASE):
        return f"https://www.arabidopsis.org/servlets/TairObject?type=locus&name={simbolo.upper()}"
    return None


def fase3_integrar(top_genes, rasgo, especie, modelo):
    for g in top_genes:
        log(f"Consultando UniProt para {g['simbolo']} …")
        g["uniprot"] = buscar_uniprot(g["simbolo"], especie["tax_id"])
        if not g["uniprot"] and g["nombre_oficial"] != g["simbolo"]:
            g["uniprot"] = buscar_uniprot(g["nombre_oficial"], especie["tax_id"])
        if g["uniprot"] and g["uniprot"]["accession"]:
            g["alphafold"] = f"https://alphafold.ebi.ac.uk/entry/{g['uniprot']['accession']}"
        g["tair"] = enlace_tair(g["simbolo"]) or enlace_tair(g["nombre_oficial"])
        time.sleep(0.3)

    contexto = ""
    for g in top_genes:
        u = g.get("uniprot") or {}
        contexto += (f"\n## {g['simbolo']}\n"
                     f"Descripción NCBI: {g['descripcion']}\n"
                     f"Proteína UniProt: {u.get('nombre_proteina', 'n/d')}\n"
                     f"Función anotada: {u.get('funcion', 'n/d')}\n")

    system = ("Eres experto en biología molecular de plantas. Elaboras perfiles "
              "funcionales precisos, indicando incertidumbre cuando la evidencia es limitada.")
    user = f"""Con los datos de abajo, genera el perfil funcional de cada gen para el
rasgo "{rasgo}" en {especie['nombre']}.
{contexto}
Para cada gen indica: mecanismo molecular, vía metabólica, dominios estructurales y
efecto esperado de un knockout.

Devuelve SOLO JSON:
{{"perfiles":[{{"simbolo":"...","mecanismo":"...","via":"...","dominios":["..."],"efecto_knockout":"...","confianza":80}}]}}"""

    data = groq_json(system, user, modelo)
    perfiles = {}
    for p in data.get("perfiles", []):
        if isinstance(p, dict) and "simbolo" in p:
            perfiles[p["simbolo"].upper()] = p

    for g in top_genes:
        g["perfil"] = perfiles.get(g["simbolo"].upper()) or perfiles.get(g["nombre_oficial"].upper()) or {}
    return top_genes


# ═══════════════════════ FASE 4 · VALIDACIÓN ═══════════════════════
def fase4_validar(top_genes, rasgo, especie, modelo):
    gen_top = top_genes[0]["simbolo"]
    contexto = json.dumps(
        [{"simbolo": g["simbolo"], "score": g["score"],
          "motivo": g.get("motivo", ""), "perfil": g.get("perfil", {})} for g in top_genes],
        ensure_ascii=False, indent=1)

    system = ("Eres investigador principal en mejora genética vegetal. Diseñas planes "
              "experimentales rigurosos, realistas y escalables.")
    user = f"""Con base en estos candidatos para "{rasgo}" en {especie['nombre']},
diseña un plan de validación experimental enfocado en {gen_top}.

Candidatos:
{contexto}

Devuelve SOLO JSON:
{{"hipotesis":"...",
  "edicion_crispr":{{"gen_objetivo":"...","estrategia":"...","guias_sugeridas":"...","controles":"..."}},
  "fenotipado":"...",
  "validacion_estadistica":"...",
  "cronograma_semanas":12,
  "riesgos":["..."],
  "advertencia_causalidad":"..."}}"""

    return groq_json(system, user, modelo, temperature=0.3)


# ══════════════════════════ INFORME ══════════════════════════
def escribir_informe(ruta, informe):
    ruta = Path(ruta)
    ruta.with_suffix(".json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [f"# 🌱 Informe AgroGenIA",
          f"\n- **Fecha:** {informe['fecha']}",
          f"- **Especie:** *{informe['especie']}*",
          f"- **Rasgo:** {informe['rasgo']}",
          f"- **Consulta NCBI:** `{informe['terminos']}`",
          f"- **Modelo LLM:** `{informe['modelo']}`\n",
          f"## Genes candidatos priorizados\n",
          "| # | Gen | Score | Evidencia | Motivo | Enlaces |",
          "|---|-----|-------|-----------|--------|---------|"]

    for i, g in enumerate(informe["candidatos"], 1):
        enlaces = [f"[NCBI]({g['url_ncbi']})"]
        if g.get("alphafold"):
            enlaces.append(f"[AlphaFold]({g['alphafold']})")
        if g.get("tair"):
            enlaces.append(f"[TAIR]({g['tair']})")
        md.append(f"| {i} | **{g['simbolo']}** | {g['score']} | {g.get('evidencia','-')} "
                  f"| {g.get('motivo','-')} | {' · '.join(enlaces)} |")

    md.append("\n## Perfiles funcionales\n")
    for g in informe["candidatos"]:
        p = g.get("perfil", {})
        md.append(f"### {g['simbolo']} (confianza {p.get('confianza', '?')}%)")
        md.append(f"- **Mecanismo:** {p.get('mecanismo', 'n/d')}")
        md.append(f"- **Vía:** {p.get('via', 'n/d')}")
        md.append(f"- **Dominios:** {', '.join(p.get('dominios', [])) or 'n/d'}")
        md.append(f"- **Efecto del knockout:** {p.get('efecto_knockout', 'n/d')}\n")

    v = informe["validacion"]
    md += ["## Plan de validación experimental\n",
           f"**Hipótesis:** {v.get('hipotesis', 'n/d')}\n",
           "### Edición CRISPR-Cas9",
           f"- Gen objetivo: {v.get('edicion_crispr', {}).get('gen_objetivo', 'n/d')}",
           f"- Estrategia: {v.get('edicion_crispr', {}).get('estrategia', 'n/d')}",
           f"- Guías sugeridas: {v.get('edicion_crispr', {}).get('guias_sugeridas', 'n/d')}",
           f"- Controles: {v.get('edicion_crispr', {}).get('controles', 'n/d')}\n",
           f"**Fenotipado:** {v.get('fenotipado', 'n/d')}\n",
           f"**Validación estadística:** {v.get('validacion_estadistica', 'n/d')}\n",
           f"**Cronograma:** {v.get('cronograma_semanas', '?')} semanas\n",
           "**Riesgos:**\n"]
    md += [f"- {r}" for r in v.get("riesgos", [])]
    md.append(f"\n> ⚠️ **{v.get('advertencia_causalidad', 'Correlación ≠ causalidad.')}**")

    ruta.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
    return ruta.with_suffix(".json"), ruta.with_suffix(".md")


# ══════════════════════════ MAIN ══════════════════════════
def main():
    p = argparse.ArgumentParser(
        description="AgroGenIA · Piloto con librería oficial de Groq",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--rasgo", default="tolerancia a sequía",
                   help="Ventaja agronómica buscada")
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

    # ── FASE 0 ──
    fase_titulo(0, "PLANIFICACIÓN")
    log(f'Consulta: "Genes de {a.rasgo} en {especie['nombre']}"', "fase")
    terminos = fase0_planificar(a.rasgo, especie, modelo)

    # ── FASE 1 ──
    fase_titulo(1, "INGESTA — búsqueda en NCBI Gene")
    genes = fase1_ingesta(especie, terminos, a.max_genes)
    if not genes:
        sys.exit("✖ No se encontraron genes. Prueba con otro rasgo o especie.")
    log(f"{len(genes)} genes recuperados de NCBI", "ok")

    # ── FASE 2 ──
    fase_titulo(2, "PRIORIZACIÓN — puntuación con el orquestador LLM")
    genes = fase2_priorizar(genes, a.rasgo, especie, modelo)
    for g in genes[:a.top]:
        log(f"{g['simbolo']:<12} score {g['score']:>3}  ({g.get('evidencia','')})")

    # ── FASE 3 ──
    fase_titulo(3, "INTEGRACIÓN FUNCIONAL")
    top_genes = fase3_integrar(genes[:a.top], a.rasgo, especie, modelo)
    for g in top_genes:
        extra = "UniProt ✓" if g.get("uniprot") else "sin datos UniProt"
        log(f"{g['simbolo']:<12} {extra}" + (f" → AlphaFold: {g['alphafold']}" if g.get("alphafold") else ""))

    # ── FASE 4 ──
    fase_titulo(4, "VALIDACIÓN — diseño experimental")
    validacion = fase4_validar(top_genes, a.rasgo, especie, modelo)
    log(f"Hipótesis: {validacion.get('hipotesis', 'n/d')[:140]} …", "ok")

    # ── INFORME ──
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
        "nota": "Piloto con fines docentes: correlación ≠ causalidad; validar experimentalmente.",
    }
    f_json, f_md = escribir_informe(a.salida, informe)

    print(f"\n{'═'*62}")
    log(f"Pipeline completado en {time.time()-t_inicio:.1f} s", "ok")
    log(f"Candidato principal: {top_genes[0]['simbolo']} (score {top_genes[0]['score']})", "ok")
    log(f"Informe JSON : {f_json}", "ok")
    log(f"Informe MD   : {f_md}", "ok")
    print(f"{'═'*62}\n")


if __name__ == "__main__":
    main()
