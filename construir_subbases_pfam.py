#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constructor de sub-bases Pfam por rasgo para AgroGenIA.

Genera archivos tipo:
  ~/agrogenia/dbs/Pfam-estres.hmm
  ~/agrogenia/dbs/Pfam-sequia.hmm
  ~/agrogenia/dbs/Pfam-salinidad.hmm
  ~/agrogenia/dbs/Pfam-calor.hmm
  ~/agrogenia/dbs/Pfam-frio.hmm
  ~/agrogenia/dbs/Pfam-inundacion.hmm
  ~/agrogenia/dbs/Pfam-oxidativo.hmm
  ~/agrogenia/dbs/Pfam-nutricion.hmm

Uso:
  python construir_subbases_pfam.py --todos
  python construir_subbases_pfam.py --solo sequia salinidad calor
  python construir_subbases_pfam.py --listar
"""

import os
import sys
import argparse
from pathlib import Path

PFAM_FULL = Path.home() / "agrogenia" / "dbs" / "Pfam-A.hmm"
OUT_DIR = Path.home() / "agrogenia" / "dbs"

# ----------------------------------------------------------------------
# Patrones por rasgo.
# Se hace matching case-insensitive contra el campo NAME de Pfam.
# Es deliberadamente amplio: preferimos sobre-incluir antes que perder
# una familia relevante.
# ----------------------------------------------------------------------

NUCLEO_ESTRES = [
    # Factores de transcripción y regulación
    "AP2", "ERF", "WRKY", "NAC", "bZIP", "zf-C2H2", "CCCH", "MYB",
    "HSF", "AREB", "ABF", "ANAC", "SNF2", "GRAS", "TCP", "WOX",
    "Tify", "JAZ", "COI1", "Jasmonate",

    # Chaperonas / proteostasis
    "HSP", "Hsp", "Chaperone", "GroEL", "GroES", "DnaJ", "DnaK",
    "GrpE", "ClpB", "Hsp33", "Small_HSP", "sHSP", "TRiC", "CCT",
    "Hsp70", "Hsp90", "Hsp40", "Hsp20", "Hsp21", "Hsp22", "BiP",
    "Calnexin", "Calreticulin", "Ervin", "PDI", "Protein_disulfide",

    # Señalización básica
    "Pkinase", "Protein_kinase", "MAPK", "SnRK", "SRK", "CIPK",
    "CDPK", "Calcineurin", "Calmodulin", "CaM", "CBL", "EF-hand",
    "PP2C", "PPM", "Protein_Phosphatase", "PPP", "PTP",
    "HisKA", "Hpt", "Response_regulator", "CheY", "CheA",
    "RLK", "Receptor_like", "Pelle", "G_protein", "GPCR", "7tm",

    # Transporte y homeostasis
    "ABC2", "ABC_tran", "Aquaporin", "MIP", "Major_facilitator",
    "SWEET", "STP", "NPF", "NRT", "PHT", "KUP", "HAK", "AKT",
    "CNGC", "CLC", "CAX", "MGT", "ZIP", "NRAMP", "MTP",
    "Na_H_Exchanger", "NHX", "HKT", "CHX", "P_type_ATPase",
    "V_type", "F_type", "ATP_synth",

    # Protección osmótica / desecación
    "LEA", "Dehydrin", "DHN", "TPP", "TPS", "TreB", "TreF",
    "Trehalose", "Galactinol", "Raffinose", "Stachyose",
    "P5CS", "ProB", "ProA", "Proline", "BetA", "BetB",
    "Glycine_betaine", "EctA", "EctB", "EctC", "Ectoine",
    "GPD", "Gpp", "OsmC", "Osmotic",

    # Señalización lipídica / segunda señal
    "PAP2", "PLD", "DGK", "PLC", "IPMC", "LOX", "Allene",
    "CYP", "Cytochrome_P450", "Oxidase", "Dehydrogenase",

    # Defensa / percepción
    "NACHT", "NB_ARC", "TIR", "NLR", "CC_TIR", "LRR",
    "LRR_1", "LRR_2", "LRR_4", "LRR_6", "LRR_8", "LRRNT",
    "Receptor", "Sensor", "Kinase",

    # Estrés oxidativo
    "Catalase", "SOD", "Superoxide", "Peroxiredoxin", "Prx",
    "Thioredoxin", "Trx", "Glutaredoxin", "Grx",
    "Glutathione", "GST", "APX", "Ascorbate", "Ferritin",
    "NADPH", "Cytochrome", "Alternative_oxidase", "AOX",
    "Peroxidase", "Laccase", "Polyphenol",
]

PATRONES = {
    "estres": NUCLEO_ESTRES,

    "sequia": NUCLEO_ESTRES + [
        "ABA", "NCED", "AAO", "PYL", "RCAR", "SnRK2", "PP2C",
        "DREB", "ERF", "AP2", "LEA", "Dehydrin", "DHN",
        "TPP", "TPS", "TreB", "TreF", "Trehalose",
        "Galactinol", "Raffinose", "Stachyose",
        "P5CS", "ProB", "ProA", "Proline",
        "BetA", "BetB", "Glycine_betaine",
        "EctA", "EctB", "EctC", "Ectoine",
        "GPD", "Gpp", "OsmC", "Osmotic",
        "Aquaporin", "MIP", "SWEET", "STP", "NPF",
        "PAP2", "PLD", "DGK", "LOX", "Allene", "CYP",
        "JAZ", "Tify", "ETR",
    ],

    "salinidad": NUCLEO_ESTRES + [
        "Na_H_Exchanger", "NHX", "HKT", "CHX", "SOS",
        "Salt", "Sodium", "Ion_transport",
        "V_type", "F_type", "ATP_synth", "P_type_ATPase",
        "Aquaporin", "MIP", "SWEET", "STP", "NPF",
        "PAP2", "PLD", "DGK", "CBL", "CIPK", "CDPK",
        "Calmodulin", "CaM", "EF_hand",
        "Proline", "Betaine", "Trehalose", "Galactinol",
    ],

    "calor": NUCLEO_ESTRES + [
        "HSP20", "HSP70", "HSP90", "Chaperone", "GroEL",
        "GroES", "DnaJ", "DnaK", "ClpB", "Small_HSP", "sHSP",
        "BiP", "Calnexin", "Calreticulin", "PDI",
        "HSF", "WRKY", "NAC", "bZIP", "AP2", "ERF",
        "Pkinase", "MAPK", "SnRK", "PP2C",
        "Ubiquitin", "Proteasome", "Tubulin",
        "Trehalose", "Galactinol", "HSP",
    ],

    "frio": NUCLEO_ESTRES + [
        "CBF", "DREB", "AP2", "WRKY", "NAC", "bZIP", "HSF",
        "Lipid_desaturase", "Fatty_acid", "Hydroxylase", "CYP",
        "Aquaporin", "MIP", "Sugar_transport", "SWEET", "STP",
        "NPF", "Trehalose", "Galactinol", "Raffinose",
        "ICE1", "COR", "Cold",
    ],

    "inundacion": NUCLEO_ESTRES + [
        "ADH", "Alcohol_dehydrogenase", "PDC", "Pyruvate_decarboxylase",
        "Fermentation", "Hypoxia", "Anaerobic", "ERF_VII",
        "N_degron", "PCNA", "LDH", "Lactate_dehydrogenase",
        "Alanine_dehydrogenase", "Sucrose_synthase", "Sus",
        "Pkinase", "MAPK", "WRKY", "NAC", "bZIP",
        "Aquaporin", "MIP",
    ],

    "oxidativo": NUCLEO_ESTRES + [
        "Catalase", "SOD", "Superoxide", "Peroxiredoxin", "Prx",
        "Thioredoxin", "Trx", "Glutaredoxin", "Grx",
        "Glutathione", "GST", "APX", "Ascorbate",
        "Ferritin", "NADPH", "Cytochrome", "Alternative_oxidase",
        "AOX", "Peroxidase", "Laccase", "Polyphenol",
        "Oxidoreductase", "Oxidase", "Dehydrogenase",
    ],

    "nutricion": NUCLEO_ESTRES + [
        "NRT", "Nitrate", "AMT", "Ammonium", "PHT", "Phosphate",
        "PHO", "SULTR", "Sulfate", "Sulfur", "Cysteine", "Methionine",
        "ZIP", "Iron", "FRO", "Nicotianamine", "MTP", "NRAMP",
        "Metal_transporter", "Potassium", "KUP", "HAK", "AKT",
        "CNGC", "CLC", "Boron", "NIP", "Silicon", "LSI",
        "Zinc", "Copper", "Magnesium", "MGT", "Calcium", "CAX",
        "Peptide", "OPT", "Oligopeptide", "DUR", "Urea",
        "Allantoin", "Purine", "Pyrimidine",
        "Thiamine", "Riboflavin", "Biotin", "Vitamin",
    ],
}

OPCIONES = list(PATRONES.keys())


def normalizar(texto):
    mapa = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUNn")
    return texto.translate(mapa)


def listar():
    print("")
    print("Sub-bases Pfam configuradas:")
    for k in OPCIONES:
        print("  - " + k + "  ->  " + str(OUT_DIR / ("Pfam-" + k + ".hmm")))
    print("")
    print("Fuente:")
    print("  - Pfam completo: " + str(PFAM_FULL))
    print("")


def construir(seleccion):
    if not PFAM_FULL.exists():
        sys.exit("No existe el Pfam completo en: " + str(PFAM_FULL))

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rutas = {}
    handles = {}
    contadores = {}

    for trait in seleccion:
        ruta = OUT_DIR / ("Pfam-" + trait + ".hmm")
        rutas[trait] = ruta
        handles[trait] = open(ruta, "w", encoding="utf-8")
        contadores[trait] = 0

    print("")
    print("Construyendo sub-bases Pfam...")
    print("  Fuente : " + str(PFAM_FULL))
    print("  Salida : " + str(OUT_DIR))
    print("  Traits : " + ", ".join(seleccion))
    print("")

    total_modelos = 0
    bloque = []
    nombre = ""

    with open(PFAM_FULL, "r", encoding="utf-8", errors="ignore") as fin:
        for linea in fin:
            bloque.append(linea)

            if linea.startswith("NAME"):
                nombre = linea.split(None, 1)[1].strip()

            elif linea.strip() == "//":
                total_modelos += 1
                nombre_low = normalizar(nombre.lower())

                for trait in seleccion:
                    patrones = [normalizar(p.lower()) for p in PATRONES[trait]]
                    if any(p in nombre_low for p in patrones):
                        handles[trait].writelines(bloque)
                        contadores[trait] += 1

                bloque = []
                nombre = ""

    for h in handles.values():
        h.close()

    # Presionar cada sub-base (hmmscan requiere indices .h3m/.h1f/.h3i/.h1i)
    import subprocess
    for trait in seleccion:
        ruta = rutas[trait]
        print("  presionando " + ruta.name + " ...")
        subprocess.run(["hmmpress", str(ruta)], check=True)        

    print("Familias totales en Pfam-A: " + str(total_modelos))
    print("")
    print("Resultados:")
    for trait in seleccion:
        size_mb = round(os.path.getsize(rutas[trait]) / 1e6, 1)
        reduction = max(1, total_modelos // max(1, contadores[trait]))
        print("  - " + trait.ljust(12) + ": " +
              str(contadores[trait]).rjust(5) + " familias | " +
              str(size_mb).rjust(6) + " MB | reducción ~" +
              str(reduction) + "x")
    print("")
    print("Listo.")
    print("")


def main():
    p = argparse.ArgumentParser(description="Constructor de sub-bases Pfam por rasgo")
    p.add_argument("--todos", action="store_true", help="Construir todas las sub-bases")
    p.add_argument("--solo", nargs="+", choices=OPCIONES, help="Construir solo algunas")
    p.add_argument("--listar", action="store_true", help="Listar opciones y salir")
    a = p.parse_args()

    if a.listar:
        listar()
        return

    if a.todos:
        seleccion = OPCIONES
    elif a.solo:
        seleccion = a.solo
    else:
        listar()
        sys.exit("Usa --todos o --solo <traits...>")

    construir(seleccion)


if __name__ == "__main__":
    main()