#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construye Pfam-estres.hmm: una sub-base de Pfam con solo las familias
de dominios asociados a respuesta al estres en plantas y microorganismos.

Uso:  python construir_pfam_estres.py
Resultado: ~/agrogenia/dbs/Pfam-estres.hmm  (~200-600 familias vs 19,000)
Beneficio: hmmscan ~50x mas rapido en el pipeline AgroGenIA.
"""
import os
import sys

PFAM_FULL = os.path.expanduser("~/agrogenia/dbs/Pfam-A.hmm")
PFAM_SUB  = os.path.expanduser("~/agrogenia/dbs/Pfam-estres.hmm")

# Patrones (substring, case-insensitive) contra el campo NAME de cada modelo HMM.
# Sobre-inclusion deliberada: mejor 500 familias que perder una relevante.
PATRONES = [
    # --- Factores de transcripcion de estres ---
    "AP2", "ERF", "WRKY", "NAC", "bZIP", "DREB", "C2H2", "CCCH", "MYB",
    "HSF", "AREB", "ABF", "ANAC", "SNF2", "GRAS", "TCP", "WOX",
    # --- Proteccion contra desecacion / osmoprotectores ---
    "LEA", "Dehydrin", "DHN", "TPP", "TPS", "TreB", "TreF",
    "Galactinol", "Raffinose", "Stachyose", "P5CS", "ProB", "ProA",
    "BetA", "BetB", "EctA", "EctB", "EctC", "GPD", "Gpp", "OsmC",
    # --- Chaperonas / proteostasis ---
    "HSP", "Chaperone", "GroEL", "GroES", "DnaJ", "DnaK", "GrpE",
    "ClpB", "Hsp33", "Small_HSP", "sHSP", "TRiC", "CCT", "Hsp70",
    "Hsp90", "Hsp40", "Hsp20", "Hsp21", "Hsp22", "BiP", "Calnexin",
    "Calreticulin", "Ervin", "PDI",
    # --- Senalizacion: quinasas, fosfatasas, calcio ---
    "Pkinase", "PKC", "MAPK", "SnRK", "SRK", "CIPK", "CDPK",
    "Calcineurin", "CaM", "Calmodulin", "CBL", "PP2C", "PPM",
    "Protein_Phosphatase", "PPP", "PTP", "HisKA", "Hpt",
    "Response_regulator", "CheY", "CheA", "MAMP", "RLK",
    # --- Transporte de iones y osmolitos ---
    "ABC2", "ABC_tran", "Na_H_Exchanger", "NHX", "HKT", "CHX",
    "AQP", "Aquaporin", "MIP", "P-type_ATPase", "V-type", "F-type",
    "ATP_synth", "SWEET", "STP", "SUT", "NPF", "NRT", "PHT",
    # --- Percepcion de senal ---
    "LRR", "Pelle", "Receptor", "G-protein", "GPCR", "7tm",
    "Rhs", "F-box", "Kelch", "WD40", "Beta_prop",
    # --- Senalizacion lipidica / segunda senal ---
    "PAP2", "PLD", "DGK", "PLC", "IPMC", "LOX", "Allene", "CYP",
    "NACHT", "NB-ARC", "TIR", "NLR", "CC-TIR", "SAM",
    # --- Estres oxidativo / antioxidantes ---
    "Catalase", "SOD", "Peroxiredoxin", "Prx", "Trx", "Thioredoxin",
    "Glutathione", "GST", "APX", "Ascorbate", "Ferritin", "NADPH",
    "Cytochrome", "Alternative_oxidase", "AOX",
    # --- Hormonas de estres ---
    "NCED", "ABA", "AAO", "ACS", "ACO", "ETR", "GA20", "GA3",
    "JAZ", "TIFY", "PYL", "RCAR",
    # --- Reparacion de ADN / resistencia a desecacion ---
    "DNA_repair", "RecA", "Rad51", "Dps", "Mre11", "Ku", "Ligase",
    "Helicase", "AddA", "AddB", "SbcC", "SbcD", "UvrA", "UvrB",
    # --- Esporulacion / supervivencia bacteriana ---
    "Spo", "Sigma", "SigA", "SigB", "SigE", "SigF", "Ger",
    "DPA", "SASP", "Cot", "Spore",
    # --- Biofilm / EPS (rizosfera) ---
    "Eps", "Wzx", "Wzy", "Glycosyl_trans", "Polysaccharide",
    "Cellulose", "Expansin", "Extensin", "XTH", "Pectate",
    "Pectin", "Xyloglucan",
]

def main():
    if not os.path.exists(PFAM_FULL):
        sys.exit("No existe " + PFAM_FULL + " — descarga Pfam-A.hmm primero.")

    print("Construyendo sub-base de estres...")
    print("  Fuente : " + PFAM_FULL)
    print("  Destino: " + PFAM_SUB)
    print("  Patrones: " + str(len(PATRONES)))
    print("")

    incluidos = 0
    total = 0
    nombres_incluidos = []
    bloque = []
    nombre = ""

    with open(PFAM_FULL, "r", encoding="utf-8", errors="ignore") as fin, \
         open(PFAM_SUB, "w", encoding="utf-8") as fout:
        for linea in fin:
            bloque.append(linea)
            if linea.startswith("NAME"):
                nombre = linea.split(None, 1)[1].strip()
            elif linea.strip() == "//":
                total += 1
                nombre_low = nombre.lower()
                if any(p.lower() in nombre_low for p in PATRONES):
                    fout.writelines(bloque)
                    incluidos += 1
                    nombres_incluidos.append(nombre)
                bloque = []
                nombre = ""

    print("Familias totales en Pfam-A : " + str(total))
    print("Familias incluidas (estres): " + str(incluidos))
    print("Reduccion esperada de tiempo hmmscan: ~" +
          str(max(1, total // max(1, incluidos))) + "x")
    print("")
    print("Tamano sub-base: " +
          str(round(os.path.getsize(PFAM_SUB) / 1e6, 1)) + " MB  (Pfam completo: ~1.5 GB)")
    print("")
    print("Primeras 30 familias incluidas:")
    for n in nombres_incluidos[:30]:
        print("  - " + n)
    print("  ... y " + str(max(0, len(nombres_incluidos) - 30)) + " mas.")
    print("")
    print("OK. El pipeline usara automaticamente " + PFAM_SUB + " si existe.")

if __name__ == "__main__":
    main()