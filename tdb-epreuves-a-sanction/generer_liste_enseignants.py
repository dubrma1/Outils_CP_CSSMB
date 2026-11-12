# -*- coding: utf-8 -*-
"""
generer_liste_enseignants.py - Générateur autonome de la liste des enseignants et groupes (Loi 25).
Script 100 % autonome (zéro dépendance externe autre que pandas et numpy).

Règles de génération :
  1. Un enseignant est TOUJOURS dans la même école (aucun enseignant n'est assigné à plusieurs écoles).
  2. Un enseignant peut enseigner plusieurs groupes d'une même matière (ex. Gr. 01, 02, 03 de Math CST).
  3. Cohérence totale avec le schéma d'ingestion et les extractions ministérielles CHAP060105.

Usage CLI :
  # Mode 1 : Génération synthétique complète (16 écoles CSSMB, cours de sanction 4e/5e)
  python generer_liste_enseignants.py

  # Mode 2 : Calibrage direct sur les écoles/cours/groupes réels d'un fichier CHAP060105
  python generer_liste_enseignants.py CHAP060105-Juin.csv liste_enseignants_groupes.csv
"""

import argparse
import io
import os
import re
import sys
import unicodedata
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

# Écoles officielles du réseau (CSSMB)
ECOLES_LIST: List[str] = [
    "037", "038", "040", "041", "042",
    "136", "138", "139", "142", "144",
    "236", "238", "240", "241", "243", "245"
]

# Matières à sanction ministérielle et codes cours officiels
COURS_SANCTION: Dict[str, Dict[str, Any]] = {
    "0132406": {"matiere": "Français 4", "famille": "Français", "default_groups": ["01", "02", "03", "04"]},
    "0132506": {"matiere": "Français 5", "famille": "Français", "default_groups": ["01", "02", "03"]},
    "063414": {"matiere": "Math CST 4", "famille": "Math", "default_groups": ["01", "02", "03"]},
    "065426": {"matiere": "Math SN 4", "famille": "Math", "default_groups": ["01", "02"]},
    "064426": {"matiere": "Math TS 4", "famille": "Math", "default_groups": ["01"]},
    "055444": {"matiere": "Science ST 4", "famille": "Science", "default_groups": ["01", "02", "03"]},
    "057406": {"matiere": "Science ATS 4", "famille": "Science", "default_groups": ["01"]},
    "085404": {"matiere": "Histoire 4", "famille": "Histoire", "default_groups": ["01", "02", "03", "04"]},
    "0134504": {"matiere": "Anglais 5 base", "famille": "Anglais", "default_groups": ["01", "02", "03"]},
}

# Banque de patronymes québécois réalistes
NOMS_FAMILLE: List[str] = [
    "Tremblay", "Gagnon", "Roy", "Côté", "Bouchard", "Gauthier", "Morin", "Lavoie",
    "Fortin", "Gagné", "Ouellet", "Pelletier", "Bélanger", "Lévesque", "Bergeron",
    "Leblanc", "Paquette", "Giroux", "Simard", "Boucher", "Caron", "Beaulieu",
    "Cloutier", "Dubé", "Poirier", "Fournier", "Lapointe", "Lebrun", "Rioux",
    "Desjardins", "Hébert", "Dion", "Martel", "Savard", "Nadeau", "Dufour",
    "Perreault", "Vachon", "Lemieux", "Moreau", "Bédard", "Plante", "Gravel",
    "Chouinard", "Tessier", "Leduc", "Gingras", "Dumont", "Demers", "Audet",
    "Blais", "Marcoux", "Baril", "Thibault", "Bernier", "Proulx", "Turcotte",
    "Mercier", "Bolduc", "St-Pierre", "Larouche", "Boily", "Brouillette", "Fontaine",
    "Lambert", "Bérubé", "Robitaille", "Rousseau", "Perron", "Gingras", "Drouin",
    "Landry", "Martineau", "Archambault", "Noël", "Lachance", "Brisson", "Renaud",
    "Vigneault", "Therrien", "Dallaire", "Gosselin", "Couture", "Tanguay", "Fillion",
    "Corriveau", "Charette", "Guay", "Benoit", "Marcotte", "Dufresne", "Picard",
    "Blanchet", "Duchesne", "Bisson", "Veilleux", "Paré", "Thivierge", "Gervais"
]

PRENOMS: List[str] = [
    "Martin", "Julie", "Pierre", "Sophie", "Alexandre", "Catherine", "Nicolas", "Isabelle",
    "François", "Valérie", "Vincent", "Marie", "Patrick", "Karine", "Sébastien", "Stéphanie",
    "Éric", "Geneviève", "Maxime", "Caroline", "David", "Annie", "Guillaume", "Mélanie",
    "Philippe", "Chantal", "Mathieu", "Anik", "Simon", "Nathalie", "Thomas", "Amélie",
    "Julien", "Hélène", "Antoine", "Emmanuelle", "Gabriel", "Claudia", "Marc", "Josée",
    "Jean-François", "Véronique", "Marc-André", "Christine", "Benoît", "Marie-Ève",
    "Louis", "Dominique", "Christian", "Patricia", "Luc", "Sylvie", "Daniel", "Danielle"
]


def clean_cd_orgns(val: Any) -> str:
    """Normalise un code d'organisme vers 3 chiffres (ex: '763041' -> '041')."""
    if val is None or pd.isna(val):
        return ""
    s = str(val).strip().replace(".0", "")
    if s.lower() in ["toutes", "tous", "all", "", "nan", "none", "0", "00", "000"]:
        return ""
    if len(s) == 6 and s.isdigit():
        return s[3:]
    if s.startswith("763") and len(s) > 3:
        return s[3:]
    if s.isdigit() and len(s) < 3:
        return s.zfill(3)
    if s.isdigit() and len(s) > 3:
        return s[-3:]
    return s


def clean_group_code(val: Any) -> str:
    """Normalise un code de groupe vers 2 chiffres (ex: '1' -> '01', '041-02' -> '02')."""
    if val is None or pd.isna(val):
        return "01"
    s = str(val).strip().replace(".0", "")
    if not s or s.lower() in ("nan", "none"):
        return "01"
    if "-" in s:
        s = s.split("-")[-1].strip()
    elif len(s) >= 5 and s.isdigit():
        s = s[-2:]
    return f"{int(s):02d}" if s.isdigit() else s


def load_csv_robust(file_path_or_buf: Any) -> pd.DataFrame:
    """Charge un fichier CSV avec détection d'encodage et de délimiteur."""
    if isinstance(file_path_or_buf, str):
        with open(file_path_or_buf, "rb") as f:
            raw_bytes = f.read()
    elif hasattr(file_path_or_buf, "read"):
        raw_bytes = file_path_or_buf.read()
        if hasattr(file_path_or_buf, "seek"):
            file_path_or_buf.seek(0)
    else:
        raw_bytes = bytes(file_path_or_buf)

    if not raw_bytes:
        return pd.DataFrame()

    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    delimiters = [";", ",", "\t"]

    for enc in encodings:
        try:
            text = raw_bytes.decode(enc).lstrip("\ufeff\xef\xbb\xbf")
            first_line = ""
            for line in text.splitlines():
                if line.strip():
                    first_line = line
                    break
            counts = {d: first_line.count(d) for d in delimiters}
            best_sep = max(counts, key=counts.get)
            if counts[best_sep] == 0:
                best_sep = ";"
            df = pd.read_csv(io.StringIO(text), sep=best_sep, dtype=str)
            if df is not None and not df.empty:
                df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]
                return df
        except Exception:
            continue

    try:
        return pd.read_csv(io.BytesIO(raw_bytes), sep=None, engine="python", dtype=str)
    except Exception:
        return pd.DataFrame()


class TeacherPool:
    """Gestionnaire déterministe d'enseignants garantissant l'unicité de l'école."""
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        # Générer des couples (Nom, Prénom) uniques
        all_combinations = [f"{nom}, {prenom}" for nom in NOMS_FAMILLE for prenom in PRENOMS]
        self.rng.shuffle(all_combinations)
        self.available_names = all_combinations
        self.assigned_teachers: Set[str] = set()
        self.teacher_to_school: Dict[str, str] = {}
        self.school_teachers: Dict[str, List[str]] = {}

    def get_teacher_for_school(self, school_code: str, index: int) -> str:
        """Retourne un enseignant assigné exclusivement à cette école."""
        if school_code not in self.school_teachers:
            self.school_teachers[school_code] = []

        pool = self.school_teachers[school_code]
        while len(pool) <= index:
            if not self.available_names:
                # Réserve de secours avec indice numérique
                cand = f"Enseignant_{school_code}_{len(pool) + 1}"
            else:
                cand = self.available_names.pop()
            if cand not in self.assigned_teachers:
                self.assigned_teachers.add(cand)
                self.teacher_to_school[cand] = school_code
                pool.append(cand)

        return pool[index]


def generate_teachers_dataframe(
    df_105: Optional[pd.DataFrame] = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Génère le DataFrame (CD_ORGNS, CD_COURS, NO_GROUP_ELEVE, ENSEIGN, MATIERE).
    Si df_105 est fourni, extrait les (écoles, cours, groupes) réels du fichier.
    Sinon, génère une structure synthétique complète pour les 16 écoles.
    """
    pool = TeacherPool(seed=seed)
    records: List[Dict[str, str]] = []

    if df_105 is not None and not df_105.empty:
        # 1. Extraction depuis données réelles CHAP060105
        df_w = df_105.copy()
        df_w.columns = [str(c).strip().upper() for c in df_w.columns]

        col_org = None
        for c in ["CD_ORGNS", "ORGANISME", "ECOLE", "ÉCOLE", "CD_ECOLE"]:
            if c in df_w.columns:
                col_org = c
                break

        col_cours = None
        for c in ["CD_COURS", "CD_COURS_STR", "COURS", "CODE_COURS"]:
            if c in df_w.columns:
                col_cours = c
                break

        col_grp = None
        for c in ["NO_GROUP_ELEVE", "CD_ORGNS_NO_GROUP", "NO_GROUP", "GROUPE", "GROUP"]:
            if c in df_w.columns:
                col_grp = c
                break

        if col_org and col_cours:
            df_w["_ecole"] = df_w[col_org].apply(clean_cd_orgns)
            df_w["_cours"] = df_w[col_cours].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
            if col_grp:
                df_w["_grp"] = df_w[col_grp].apply(clean_group_code)
            else:
                df_w["_grp"] = "01"

            # Ne conserver que les cours ministériels
            triplets = df_w[["_ecole", "_cours", "_grp"]].drop_duplicates().sort_values(by=["_ecole", "_cours", "_grp"])

            # Regrouper par école
            for ecole, grp_ecole in triplets.groupby("_ecole"):
                if not ecole:
                    continue
                prof_idx = 0
                for cours, grp_cours in grp_ecole.groupby("_cours"):
                    groups = sorted(grp_cours["_grp"].unique())
                    # Un enseignant prend 2 à 3 groupes de la même matière
                    for chunk_start in range(0, len(groups), 2):
                        chunk = groups[chunk_start:chunk_start + 2]
                        teacher_name = pool.get_teacher_for_school(ecole, prof_idx)
                        mat_nom = COURS_SANCTION.get(cours.zfill(6), {}).get("matiere", f"Cours {cours}")
                        for g in chunk:
                            records.append({
                                "CD_ORGNS": ecole,
                                "CD_COURS": cours,
                                "NO_GROUP_ELEVE": g,
                                "ENSEIGN": teacher_name,
                                "MATIERE": mat_nom
                            })
                        prof_idx += 1

    # Si aucun fichier fourni ou extraction vide, générer le modèle synthétique complet
    if not records:
        for ecole in ECOLES_LIST:
            prof_idx = 0
            for code_cours, cinfo in COURS_SANCTION.items():
                groups = list(cinfo["default_groups"])
                mat_nom = cinfo["matiere"]
                # Assigner 2 à 3 groupes par enseignant
                for i in range(0, len(groups), 2):
                    sub_groups = groups[i:i + 2]
                    teacher = pool.get_teacher_for_school(ecole, prof_idx)
                    for g in sub_groups:
                        records.append({
                            "CD_ORGNS": ecole,
                            "CD_COURS": code_cours,
                            "NO_GROUP_ELEVE": g,
                            "ENSEIGN": teacher,
                            "MATIERE": mat_nom
                        })
                    prof_idx += 1

    df_out = pd.DataFrame(records)
    return df_out


def main():
    parser = argparse.ArgumentParser(description="Générateur de liste enseignants / groupes (Loi 25 Québec).")
    parser.add_argument("input_csv", nargs="?", default=None, help="Chemin vers CHAP060105.csv (optionnel)")
    parser.add_argument("output_csv", nargs="?", default="liste_enseignants_groupes.csv", help="Chemin du CSV de sortie")
    args = parser.parse_args()

    df_105 = None
    if args.input_csv:
        if os.path.exists(args.input_csv):
            print(f"Chargement du fichier source : {args.input_csv} ...")
            df_105 = load_csv_robust(args.input_csv)
            print(f"Lignes chargées : {len(df_105)}")
        else:
            print(f"Avertissement : Fichier '{args.input_csv}' introuvable. Génération synthétique par défaut.")

    df_res = generate_teachers_dataframe(df_105)

    # Vérification stricte des contraintes
    # 1. Un enseignant est TOUJOURS dans la même école
    teachers_per_school = df_res.groupby("ENSEIGN")["CD_ORGNS"].nunique()
    multi_school = teachers_per_school[teachers_per_school > 1]
    assert len(multi_school) == 0, f"Erreur : Des enseignants sont dans plusieurs écoles : {multi_school}"

    # Sauvegarde du fichier
    df_res.to_csv(args.output_csv, index=False, encoding="utf-8-sig")
    print(f"Fichier généré avec succès : {args.output_csv}")
    print(f"  - Total d'affectations (groupes) : {len(df_res)}")
    print(f"  - Écoles couvertes : {df_res['CD_ORGNS'].nunique()}")
    print(f"  - Enseignants uniques : {df_res['ENSEIGN'].nunique()}")
    print(f"  - Groupes moyens par enseignant : {len(df_res) / df_res['ENSEIGN'].nunique():.2f}")

    # Si nom par défaut, copier également sous le nom descriptif alternatif
    alt_file = "enseignants_groupes_synthetiques.csv"
    if args.output_csv == "liste_enseignants_groupes.csv":
        df_res.to_csv(alt_file, index=False, encoding="utf-8-sig")
        print(f"Copie miroir créée : {alt_file}")


if __name__ == "__main__":
    main()
