# -*- coding: utf-8 -*-
"""
predict_sexe.py - Script autonome de déduction du sexe depuis les prénoms québécois.
100 % local, sans dépendance externe ni appel réseau (Conforme Loi 25 Québec).
Dictionnaire basé sur la banque officielle des prénoms du Québec (Retraite Québec).
"""

import sys
import os
import re
import unicodedata
import argparse
import pandas as pd

NAMES_DB = {
    # Féminins
    "emma": "F", "lea": "F", "alice": "F", "olivia": "F", "florence": "F", "beatrice": "F",
    "charlotte": "F", "charlie": "F", "zoe": "F", "mia": "F", "juliette": "F", "chloe": "F",
    "rose": "F", "rosalie": "F", "jade": "F", "eva": "F", "victoria": "F", "laurence": "F",
    "clara": "F", "mila": "F", "amelia": "F", "eleonore": "F", "maya": "F", "sofia": "F",
    "sophie": "F", "sarah": "F", "camille": "F", "audrey": "F", "gabrielle": "F", "megane": "F",
    "annabelle": "F", "elizabeth": "F", "elise": "F", "ariane": "F", "justine": "F", "noemie": "F",
    "delphine": "F", "mathilde": "F", "alicia": "F", "marie": "F", "isabelle": "F", "catherine": "F",
    "stephanie": "F", "valerie": "F", "melanie": "F", "julie": "F", "caroline": "F", "genevieve": "F",
    "helene": "F", "annie": "F", "veronique": "F", "marilou": "F", "anouk": "F", "laurie": "F",
    "romane": "F", "adele": "F", "agathe": "F", "leonie": "F", "ophelie": "F", "aurelie": "F",
    "salma": "F", "nour": "F", "fatima": "F", "aya": "F", "yasmina": "F", "lina": "F", "amina": "F",

    # Masculins
    "thomas": "M", "liam": "M", "william": "M", "noah": "M", "felix": "M", "edouard": "M",
    "jacob": "M", "lucas": "M", "leo": "M", "samuel": "M", "gabriel": "M", "louis": "M",
    "alexis": "M", "arthur": "M", "adam": "M", "charles": "M", "benjamin": "M", "nathan": "M",
    "theodore": "M", "antoine": "M", "laurent": "M", "elliot": "M", "victor": "M", "hugo": "M",
    "emile": "M", "mathieu": "M", "alexandre": "M", "nicolas": "M", "simon": "M", "vincent": "M",
    "david": "M", "raphael": "M", "olivier": "M", "julien": "M", "sebastien": "M", "philippe": "M",
    "guillaume": "M", "etienne": "M", "francois": "M", "pierre": "M", "jean": "M", "marc": "M",
    "michel": "M", "daniel": "M", "patrick": "M", "martin": "M", "eric": "M", "alain": "M",
    "youssef": "M", "mohamed": "M", "ali": "M", "omar": "M", "rayan": "M", "mehdi": "M"
}


def normalize_prenom(prenom: str) -> str:
    """Normalise une chaîne de prénom : minuscule, suppression d'accents et caractères parasites."""
    if not prenom or not isinstance(prenom, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", prenom.lower().strip())
    no_acc = "".join([c for c in nfkd if not unicodedata.combining(c)])
    clean = re.sub(r"[^a-z\-]", "", no_acc)
    return clean


def predict_gender(prenom: str) -> str:
    """
    Déduit le sexe ('M', 'F' ou 'Inconnu') d'après le prénom québécois.
    Prend en compte les prénoms composés courants.
    """
    clean = normalize_prenom(prenom)
    if not clean:
        return "Inconnu"

    if clean in NAMES_DB:
        return NAMES_DB[clean]

    if "-" in clean:
        parts = clean.split("-")
        first = parts[0]
        if first in NAMES_DB:
            return NAMES_DB[first]
        second = parts[1]
        if second in NAMES_DB:
            return NAMES_DB[second]

    if clean.endswith(("ette", "elle", "ie", "ine", "ance", "ence", "ise")):
        return "F"

    return "Inconnu"


def process_csv_gender(input_csv: str, output_csv: str, id_col: str = "CD_PERMN", prenom_col: str = "PRENM") -> None:
    """Lit un CSV source et produit un fichier de correspondance CD_PERMN -> SEXE."""
    df = pd.read_csv(input_csv, dtype=str)
    if id_col not in df.columns:
        for c in df.columns:
            if "perm" in c.lower() or "id" in c.lower():
                id_col = c
                break

    if prenom_col not in df.columns:
        for c in df.columns:
            if "pren" in c.lower() or "nom" in c.lower() or "eleve" in c.lower():
                prenom_col = c
                break

    if id_col not in df.columns or prenom_col not in df.columns:
        print(f"Erreur : Impossible de trouver les colonnes requises ({id_col}, {prenom_col}) dans {input_csv}")
        return

    df_out = df[[id_col, prenom_col]].drop_duplicates(subset=[id_col]).copy()
    df_out["SEXE"] = df_out[prenom_col].apply(predict_gender)

    result_df = df_out[[id_col, "SEXE"]].rename(columns={id_col: "CD_PERMN"})
    result_df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"Fichier de correspondance généré : {output_csv} ({len(result_df)} élèves traités)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Déduction locale du sexe depuis le prénom (Loi 25 Québec).")
    parser.add_argument("input_csv", help="Chemin du CSV contenant CD_PERMN et PRENM")
    parser.add_argument("output_csv", nargs="?", default="correspondance_sexe.csv", help="Fichier de sortie")
    args = parser.parse_args()

    process_csv_gender(args.input_csv, args.output_csv)
