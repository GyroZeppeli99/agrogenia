#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consenso multi-corrida · AgroGenIA V5.2
========================================
Lee los JSON de multiples corridas y produce una tabla de candidatos
consenso ordenados por numero de corridas en las que aparecen.
"""
import json
import argparse
from pathlib import Path
from collections import defaultdict


def cargar_corridas(rutas):
    """Carga los JSON de las corridas y extrae candidatos."""
    corridas = {}
    for r in rutas:
        p = Path(r)
        if not p.exists():
            print("  ! " + str(p) + " no existe; omitiendo.")
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            corridas[str(p)] = {
                "fecha": data.get("fecha", "?"),
                "receptora": data.get("receptora", "?"),
                "rasgo": data.get("rasgo", "?"),
                "modo": data.get("modo", "?"),
                "panel": data.get("panel_modo", "?"),
                "candidatos": data.get("candidatos", []),
            }
            print("  + Cargada: " + p.name +
                  " (" + str(len(data.get("candidatos", []))) + " candidatos)")
        except Exception as e:
            print("  x Error en " + str(p) + ": " + str(e))
    return corridas


def construir_consenso(corridas, umbral_min=1):
    """Construye tabla de consenso: cuantas corridas ven cada accession."""
    por_acc = defaultdict(lambda: {
        "corridas": set(),
        "scores": [],
        "pre_scores": [],
        "especies": set(),
        "donante": None,
        "tipo": None,
        "mecanismos": set(),
        "estrategias": set(),
        "epmc_novels": 0,
        "soportes": [],
    })

    for ruta, data in corridas.items():
        for i, c in enumerate(data["candidatos"]):
            acc = c.get("accession")
            if not acc:
                continue
            entry = por_acc[acc]
            entry["corridas"].add(ruta)
            entry["scores"].append(c.get("score_transferencia", 0) or 0)
            entry["pre_scores"].append(c.get("pre_score", 0) or 0)
            entry["especies"].add(data["receptora"])
            if entry["donante"] is None:
                entry["donante"] = c.get("especie_donante", "?")
                entry["tipo"] = c.get("tipo_donante", "?")
            if c.get("mecanismo"):
                entry["mecanismos"].add(c["mecanismo"])
            if c.get("estrategia"):
                entry["estrategias"].add(c["estrategia"])
            epmc = c.get("val_epmc", {}) or {}
            if epmc.get("novel") is True:
                entry["epmc_novels"] += 1
            sop = c.get("soporte_multifuente", {}) or {}
            entry["soportes"].append(sop.get("score", 0) or 0)

    # Filtrar por umbral mínimo de corridas
    salida = []
    for acc, info in por_acc.items():
        n = len(info["corridas"])
        if n < umbral_min:
            continue
        score_consenso = (
            n * 100
            + (sum(info["scores"]) / max(1, len(info["scores"]))) * 0.5
            + (sum(info["pre_scores"]) / max(1, len(info["pre_scores"]))) * 0.2
            + (sum(info["soportes"]) / max(1, len(info["soportes"]))) * 0.3
        )
        salida.append({
            "accession": acc,
            "n_corridas": n,
            "n_receptoras": len(info["especies"]),
            "receptoras": sorted(info["especies"]),
            "score_consenso": round(score_consenso, 2),
            "score_llm_promedio": round(sum(info["scores"]) / max(1, len(info["scores"])), 1),
            "pre_score_promedio": round(sum(info["pre_scores"]) / max(1, len(info["pre_scores"])), 1),
            "soporte_promedio": round(sum(info["soportes"]) / max(1, len(info["soportes"])), 1),
            "epmc_novels": info["epmc_novels"],
            "epmc_total": n,
            "donante": info["donante"],
            "tipo": info["tipo"],
            "mecanismos": sorted(info["mecanismos"]),
            "estrategias": sorted(info["estrategias"]),
        })
    salida.sort(key=lambda x: (x["n_corridas"], x["score_consenso"]), reverse=True)
    return salida


def escribir_informe(ruta_salida, consenso, corridas):
    """Escribe informe JSON + MD del consenso."""
    # JSON
    out_json = Path(ruta_salida).with_suffix(".json")
    out_json.write_text(
        json.dumps({
            "corridas_consideradas": list(corridas.keys()),
            "total_candidatos_consenso": len(consenso),
            "candidatos": consenso,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # Markdown
    md = ["# Consenso multi-corrida · AgroGenIA V5.2",
          "",
          "## Corridas consideradas",
          ""]
    for ruta, data in corridas.items():
        md.append("- **" + Path(ruta).name + "**")
        md.append("  - Receptora: *" + data["receptora"] + "*")
        md.append("  - Rasgo: " + data["rasgo"])
        md.append("  - Modo: " + data["modo"] + " · Panel: " + data["panel"])
        md.append("  - Candidatos: " + str(len(data["candidatos"])))
        md.append("")

    # Tabla resumen
    md.append("## Candidatos consenso (aparecen en ≥2 corridas)")
    md.append("")
    md.append("| # | Accession | Donante | Tipo | Corridas | Receptores | Score cons. | LLM avg | Soporte avg | PMC novel |")
    md.append("|---:|---|---|---|---:|---:|---:|---:|---:|---:|")
    for i, c in enumerate(consenso, 1):
        if c["n_corridas"] < 2:
            continue
        md.append("| " + str(i)
                  + " | " + c["accession"]
                  + " | " + str(c["donante"])
                  + " | " + str(c["tipo"])
                  + " | " + str(c["n_corridas"])
                  + " | " + ", ".join(c["receptoras"])
                  + " | " + str(c["score_consenso"])
                  + " | " + str(c["score_llm_promedio"])
                  + " | " + str(c["soporte_promedio"])
                  + " | " + str(c["epmc_novels"]) + "/" + str(c["epmc_total"])
                  + " |")
    md.append("")

    # Detalles
    md.append("## Detalles por candidato consenso")
    md.append("")
    for c in consenso:
        if c["n_corridas"] < 2:
            continue
        md.append("### " + c["accession"] + " · " + str(c["donante"]))
        md.append("- **Aparece en** " + str(c["n_corridas"]) + " corridas")
        md.append("- **Receptoras:** " + ", ".join(c["receptoras"]))
        md.append("- **Score consenso:** " + str(c["score_consenso"]))
        md.append("- **Score LLM promedio:** " + str(c["score_llm_promedio"]))
        md.append("- **Pre-score promedio:** " + str(c["pre_score_promedio"]))
        md.append("- **Soporte multi-fuente:** " + str(c["soporte_promedio"]) + "/100")
        md.append("- **Europe PMC novel:** " + str(c["epmc_novels"]) + "/" + str(c["epmc_total"]))
        if c["mecanismos"]:
            md.append("- **Mecanismos sugeridos:** " + "; ".join(list(c["mecanismos"])[:3]))
        if c["estrategias"]:
            md.append("- **Estrategias:** " + ", ".join(c["estrategias"]))
        md.append("")

    # Top 15 tabla corta (útil para paper)
    md.append("## Top 15 para el paper (robustez cross-corrida)")
    md.append("")
    top15 = [c for c in consenso if c["n_corridas"] >= 2][:15]
    md.append("| Accession | Donante | Corridas | Score cons. | Estrategia |")
    md.append("|---|---|---:|---:|---|")
    for c in top15:
        estr = ", ".join(c["estrategias"][:2]) or "?"
        md.append("| " + c["accession"]
                  + " | " + str(c["donante"])
                  + " | " + str(c["n_corridas"])
                  + " | " + str(c["score_consenso"])
                  + " | " + estr + " |")
    md.append("")

    out_md = Path(ruta_salida).with_suffix(".md")
    out_md.write_text("\n".join(md), encoding="utf-8")
    return out_json, out_md


def main():
    p = argparse.ArgumentParser(description="Consenso multi-corrida AgroGenIA V5.2")
    p.add_argument("--corridas", nargs="+", required=True,
                   help="Rutas a archivos JSON de corridas a comparar.")
    p.add_argument("--umbral", type=int, default=1,
                   help="Numero minimo de corridas en las que debe aparecer un candidato (default 1).")
    p.add_argument("--salida", default="consenso_multi_corrida",
                   help="Nombre base del informe (sin extension).")
    a = p.parse_args()

    print("=" * 66)
    print("  Consenso multi-corrida · AgroGenIA V5.2")
    print("=" * 66)
    print("  Corridas a comparar: " + str(len(a.corridas)))
    corridas = cargar_corridas(a.corridas)
    if not corridas:
        print("  x Ninguna corrida valida. Abortando.")
        return
    consenso = construir_consenso(corridas, umbral_min=a.umbral)
    n_multi = sum(1 for c in consenso if c["n_corridas"] >= 2)
    print("  + Candidatos totales con accession unico: " + str(len(consenso)))
    print("  + Candidatos en 2 o mas corridas: " + str(n_multi))
    f_json, f_md = escribir_informe(a.salida, consenso, corridas)
    print("  + Informe JSON: " + str(f_json))
    print("  + Informe MD:   " + str(f_md))


if __name__ == "__main__":
    main()