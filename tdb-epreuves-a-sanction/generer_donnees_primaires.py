# -*- coding: utf-8 -*-
"""
generer_donnees_primaires.py - Générateur local et autonome de données primaires synthétiques (Loi 25).
Script 100 % autonome (zéro dépendance externe autre que pandas et numpy).
Peut être copié et exécuté dans n'importe quel dossier local contenant CHAP060105.

Extrait les CD_PERMN et résultats réels du fichier ministériel CHAP060105 (ou génère une cohorte
synthétique si aucun fichier n'est spécifié) et produit un fichier CSV joignable sur CD_PERMN
respectant rigoureusement les typologies de Janosz/Potvin (MEQ) :
  - Discrets (~40 % des élèves à risque)
  - Inadaptés (~40 % des élèves à risque)
  - Désengagés (~10 % des élèves à risque)
  - Sous-performants (~10 % des élèves à risque)
  - Non à risque (élèves en réussite régulière)

Usage CLI :
    python generer_donnees_primaires.py CHAP060105-Juin.csv donnees_primaires_eleves.csv
"""

import argparse
import io
import os
import re
import sys
import unicodedata
from typing import Any, List, Optional
import numpy as np
import pandas as pd

PRIMARY_COLUMNS: List[str] = [
    "CD_PERMN",
    "SEXE",
    "AGE_30SEPT",
    "CD_EHDAA",
    "FLAG_PI",
    "TYPE_PARCOURS",
    "PCT_ABSENCE",
    "NB_RETARDS",
    "SIGNALEMENT_COMP",
    "NB_CREDITS_CUMUL"
]

ENRICHED_CODES: List[str] = [
    "58404", "058404", "58402", "058402",
    "51514", "051514", "53514", "053514"
]

SANCTION_CODES: List[str] = [
    "132406", "0132406", "132506", "0132506",
    "63414", "063414", "63420", "063420",
    "65426", "065426", "65420", "065420",
    "64426", "064426", "64420", "064420",
    "134504", "0134504", "134520", "0134520",
    "55444", "055444", "55410", "055410",
    "57406", "057406", "57410", "057410",
    "85404", "085404", "585404", "0585404"
]

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
    """Normalise un prénom : minuscules sans accents."""
    if not prenom or not isinstance(prenom, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", prenom.lower().strip())
    no_acc = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return re.sub(r"[^a-z\-]", "", no_acc)


def predict_gender(prenom: str) -> str:
    """Déduit 'M', 'F' ou 'Inconnu' depuis un prénom québécois."""
    clean = normalize_prenom(prenom)
    if not clean:
        return "Inconnu"
    if clean in NAMES_DB:
        return NAMES_DB[clean]
    if "-" in clean:
        parts = clean.split("-")
        if parts[0] in NAMES_DB:
            return NAMES_DB[parts[0]]
        if len(parts) > 1 and parts[1] in NAMES_DB:
            return NAMES_DB[parts[1]]
    if clean.endswith(("ette", "elle", "ie", "ine", "ance", "ence", "ise")):
        return "F"
    return "Inconnu"


def load_csv_robust(file_path_or_buf: Any) -> pd.DataFrame:
    """Charge un fichier CSV de façon robuste (encodages UTF-8/CP1252/latin1 et délimiteurs ;/,/\t)."""
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


def get_course_level(course_code: Any) -> int:
    """Extrait le niveau du secondaire (ex: 055444 -> 4, 132506 -> 5)."""
    if pd.isna(course_code) or course_code is None:
        return 4
    s = str(course_code).strip().replace(".0", "")
    if len(s) >= 3 and s[-3].isdigit():
        lvl = int(s[-3])
        if 1 <= lvl <= 5:
            return lvl
    return 4


def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    """Downcast mémoire pour WebAssembly et efficacité Python."""
    if df is None or df.empty:
        return df
    int16_cols = {"AGE_30SEPT", "NB_RETARDS", "SIGNALEMENT_COMP", "NB_CREDITS_CUMUL"}
    int32_cols = {"FLAG_PI"}
    float32_cols = {"PCT_ABSENCE"}
    cat_cols = {"SEXE", "CD_EHDAA", "TYPE_PARCOURS"}

    for col in df.columns:
        if col in int16_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int16")
        elif col in int32_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int32")
        elif col in float32_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")
        elif col in cat_cols:
            s_clean = df[col].fillna("").astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
            df[col] = s_clean.replace(["nan", "None"], "").astype("category")
    return df


def generate_synthetic_primary_df(
    df_105: Optional[pd.DataFrame] = None,
    n_fallback: int = 500,
    seed: int = 42
) -> pd.DataFrame:
    """
    Génère le DataFrame des données primaires conforme à la typologie de Janosz/Potvin.
    """
    rng = np.random.default_rng(seed)

    if df_105 is not None and not df_105.empty and "CD_PERMN" in df_105.columns:
        df_w = df_105.copy()
        df_w["CD_PERMN"] = df_w["CD_PERMN"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        df_w = df_w[~df_w["CD_PERMN"].isin(["", "nan", "None"])]

        if "CD_COURS" in df_w.columns:
            df_w["CD_COURS_str"] = df_w["CD_COURS"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        else:
            df_w["CD_COURS_str"] = ""

        if "RESLT_FINAL" in df_w.columns:
            df_w["note_num"] = pd.to_numeric(df_w["RESLT_FINAL"], errors="coerce")
        else:
            df_w["note_num"] = np.nan

        is_sanction = df_w["CD_COURS_str"].isin(SANCTION_CODES)
        if not is_sanction.any():
            is_sanction = df_w["note_num"].notna()

        df_w["note_sanct"] = np.where(is_sanction, df_w["note_num"], np.nan)
        df_w["echec_sanct"] = np.where(is_sanction & (df_w["note_num"] < 60.0), 1, 0)
        df_w["lvl"] = df_w["CD_COURS_str"].map(get_course_level).fillna(4)
        df_w["is_enr"] = df_w["CD_COURS_str"].isin(ENRICHED_CODES).astype(int)

        grp = df_w.groupby("CD_PERMN", observed=True)
        stu = pd.DataFrame({"CD_PERMN": grp.size().index})
        stu["nb_echecs"] = stu["CD_PERMN"].map(grp["echec_sanct"].sum()).fillna(0).astype(int)
        stu["min_note"] = stu["CD_PERMN"].map(grp["note_sanct"].min()).fillna(72.0).astype(float)
        stu["max_lvl"] = stu["CD_PERMN"].map(grp["lvl"].max()).fillna(4).astype(int)
        stu["is_enr"] = stu["CD_PERMN"].map(grp["is_enr"].max()).fillna(0).astype(int)

        if "PRENM" in df_w.columns:
            first_prenm = grp["PRENM"].first()
            stu["PRENM"] = stu["CD_PERMN"].map(first_prenm).fillna("")
        else:
            stu["PRENM"] = ""

        if "NO_GROUP_ELEVE" in df_w.columns:
            first_grp = grp["NO_GROUP_ELEVE"].first()
            stu["NO_GROUP_ELEVE"] = stu["CD_PERMN"].map(first_grp).fillna("01")
        else:
            stu["NO_GROUP_ELEVE"] = "01"
    else:
        # Cohorte synthétique autonome de secours
        codes = [f"PERM{i:08d}" for i in range(1, n_fallback + 1)]
        stu = pd.DataFrame({"CD_PERMN": codes})
        u = rng.random(n_fallback)
        stu["nb_echecs"] = np.where(u < 0.14, 1, np.where(u < 0.28, 2, np.where(u < 0.315, 1, 0)))
        stu["min_note"] = np.where(
            stu["nb_echecs"] == 0,
            rng.uniform(62.0, 95.0, n_fallback),
            np.where(u < 0.14, rng.uniform(55.0, 59.0, n_fallback),
                     np.where(u < 0.28, rng.uniform(42.0, 58.0, n_fallback), rng.uniform(40.0, 49.0, n_fallback)))
        )
        stu["max_lvl"] = rng.choice([4, 5], size=n_fallback, p=[0.55, 0.45])
        stu["is_enr"] = rng.choice([0, 1], size=n_fallback, p=[0.8, 0.2])
        stu["PRENM"] = ""
        stu["NO_GROUP_ELEVE"] = rng.choice(["01", "02", "31", "51", "81"], size=n_fallback, p=[0.4, 0.3, 0.12, 0.10, 0.08])

    n = len(stu)

    # 1. SEXE
    sexes = []
    for idx, row in stu.iterrows():
        g = predict_gender(str(row.get("PRENM", "")))
        if g not in ("M", "F"):
            g = "F" if (hash(str(row["CD_PERMN"])) % 2 == 0) else "M"
        sexes.append(g)
    stu["SEXE"] = sexes

    # 2. Répartition cible des profils Janosz
    # Discrets (~40% des vulnérables), Inadaptés (~40%), Désengagés (~10%), Sous-performants (~10%)
    idx_echec_1 = stu.index[stu["nb_echecs"] == 1].to_numpy()
    idx_echec_2plus = stu.index[stu["nb_echecs"] >= 2].to_numpy()
    idx_reussite = stu.index[stu["nb_echecs"] == 0].to_numpy()

    profil_cible = np.full(n, "Non à risque", dtype=object)
    n_failing = len(idx_echec_1) + len(idx_echec_2plus)

    if n_failing > 0:
        target_sous_perf = max(1, int(round(n_failing * (1.0 / 9.0))))
        target_inadapte = max(1, int(round(n_failing * (4.0 / 9.0))))
        target_discret = max(0, n_failing - target_sous_perf - target_inadapte)

        failing_indices = np.concatenate([idx_echec_2plus, idx_echec_1])
        notes_failing = stu.loc[failing_indices, "min_note"].to_numpy()
        ech_failing = stu.loc[failing_indices, "nb_echecs"].to_numpy()

        score_sp = np.where(notes_failing < 50.0, 100.0 - notes_failing, 10.0) + np.where(ech_failing == 1, 20.0, 0.0)
        order_sp = np.argsort(-score_sp)
        sp_chosen = failing_indices[order_sp[:target_sous_perf]]
        profil_cible[sp_chosen] = "Sous-performant"

        rem_mask = ~np.isin(failing_indices, sp_chosen)
        rem_indices = failing_indices[rem_mask]
        rem_ech = stu.loc[rem_indices, "nb_echecs"].to_numpy()
        rem_notes = stu.loc[rem_indices, "min_note"].to_numpy()

        score_inad = rem_ech * 100.0 - rem_notes
        order_inad = np.argsort(-score_inad)
        inad_chosen = rem_indices[order_inad[:target_inadapte]]
        profil_cible[inad_chosen] = "Inadapté (Multi-risques)"

        disc_chosen = rem_indices[order_inad[target_inadapte:]]
        profil_cible[disc_chosen] = "Discret (Frontière)"

        target_desengage = min(len(idx_reussite), max(1, int(round(n_failing / 9.0))))
        if target_desengage > 0:
            des_chosen = rng.choice(idx_reussite, size=target_desengage, replace=False)
            profil_cible[des_chosen] = "Désengagé"

    # 3. Variables administratives
    age = np.where(stu["max_lvl"] >= 5, 16, 15).astype(np.int16)
    cd_ehdaa = np.full(n, "", dtype=object)
    flag_pi = np.zeros(n, dtype=np.int32)
    pct_absence = rng.uniform(1.0, 8.5, size=n).round(1).astype(np.float32)
    nb_retards = rng.integers(0, 4, size=n, dtype=np.int16)
    sig_comp = np.zeros(n, dtype=np.int16)

    # Discret (Frontière)
    m_disc = (profil_cible == "Discret (Frontière)")
    if m_disc.any():
        k = int(m_disc.sum())
        pct_absence[m_disc] = rng.uniform(1.5, 9.2, size=k).round(1).astype(np.float32)
        nb_retards[m_disc] = rng.integers(0, 4, size=k, dtype=np.int16)
        sig_comp[m_disc] = 0
        cd_ehdaa[m_disc] = ""
        flag_pi[m_disc] = 0

    # Inadapté (Multi-risques)
    m_inad = (profil_cible == "Inadapté (Multi-risques)")
    if m_inad.any():
        k = int(m_inad.sum())
        pct_absence[m_inad] = rng.uniform(15.5, 32.0, size=k).round(1).astype(np.float32)
        nb_retards[m_inad] = rng.integers(5, 22, size=k, dtype=np.int16)
        sig_comp[m_inad] = rng.choice([1, 2, 3, 4], size=k, p=[0.40, 0.30, 0.20, 0.10]).astype(np.int16)
        age[m_inad] = np.where(stu.loc[m_inad, "max_lvl"] >= 5, rng.choice([17, 18], size=k, p=[0.15, 0.85]), rng.choice([16, 17], size=k, p=[0.15, 0.85])).astype(np.int16)
        cd_ehdaa[m_inad] = rng.choice(["", "12", "13", "14", "24"], size=k, p=[0.30, 0.20, 0.15, 0.20, 0.15])
        flag_pi[m_inad] = np.where(cd_ehdaa[m_inad] != "", 1, rng.choice([0, 1], size=k, p=[0.5, 0.5])).astype(np.int32)

    # Désengagé
    m_des = (profil_cible == "Désengagé")
    if m_des.any():
        k = int(m_des.sum())
        pct_absence[m_des] = rng.uniform(15.5, 26.5, size=k).round(1).astype(np.float32)
        nb_retards[m_des] = rng.integers(4, 16, size=k, dtype=np.int16)
        sig_comp[m_des] = 0
        cd_ehdaa[m_des] = ""
        flag_pi[m_des] = 0

    # Sous-performant
    m_sp = (profil_cible == "Sous-performant")
    if m_sp.any():
        k = int(m_sp.sum())
        pct_absence[m_sp] = rng.uniform(2.0, 10.8, size=k).round(1).astype(np.float32)
        nb_retards[m_sp] = rng.integers(0, 4, size=k, dtype=np.int16)
        sig_comp[m_sp] = 0
        cd_ehdaa[m_sp] = rng.choice(["24", ""], size=k, p=[0.75, 0.25])
        flag_pi[m_sp] = 1

    # 4. TYPE_PARCOURS
    parcours = []
    for idx, row in stu.iterrows():
        grp_str = str(row.get("NO_GROUP_ELEVE", "01")).strip()
        digits = "".join(c for c in grp_str if c.isdigit())
        g_num = int(digits) if digits else 1
        if row.get("is_enr", 0) == 1 or (30 <= g_num <= 35):
            parcours.append("PEI")
        elif 50 <= g_num <= 52:
            parcours.append("Concentration")
        elif 53 <= g_num <= 55:
            parcours.append("Sport-études")
        elif 80 <= g_num <= 85:
            parcours.append(rng.choice(["Concomitance", "FPT/FMS"], p=[0.6, 0.4]))
        else:
            p_prof = profil_cible[idx]
            if p_prof == "Inadapté (Multi-risques)":
                parcours.append(rng.choice(["Régulier", "Concomitance", "FPT/FMS"], p=[0.65, 0.20, 0.15]))
            elif p_prof == "Non à risque":
                parcours.append(rng.choice(["Régulier", "PEI", "Concentration", "Sport-études"], p=[0.72, 0.12, 0.10, 0.06]))
            else:
                parcours.append(rng.choice(["Régulier", "Concentration", "Sport-études", "Concomitance"], p=[0.80, 0.08, 0.06, 0.06]))

    # 5. NB_CREDITS_CUMUL
    credits_cumul = np.zeros(n, dtype=np.int16)
    is_5e = (stu["max_lvl"].to_numpy() >= 5)

    for i in range(n):
        p_prof = profil_cible[i]
        if is_5e[i]:
            if p_prof in ("Non à risque", "Désengagé"):
                credits_cumul[i] = int(rng.integers(52, 58))
            elif p_prof in ("Discret (Frontière)", "Sous-performant"):
                credits_cumul[i] = int(rng.integers(48, 52))
            else:
                if rng.random() < 0.45:
                    credits_cumul[i] = int(rng.integers(38, 44))
                else:
                    credits_cumul[i] = int(rng.integers(44, 50))
        else:
            if p_prof in ("Non à risque", "Désengagé"):
                credits_cumul[i] = int(rng.integers(30, 36))
            elif p_prof in ("Discret (Frontière)", "Sous-performant"):
                credits_cumul[i] = int(rng.integers(26, 30))
            else:
                credits_cumul[i] = int(rng.integers(20, 26))

    df_out = pd.DataFrame({
        "CD_PERMN": stu["CD_PERMN"].astype(str),
        "SEXE": stu["SEXE"],
        "AGE_30SEPT": age.astype("int16"),
        "CD_EHDAA": cd_ehdaa,
        "FLAG_PI": flag_pi.astype("int32"),
        "TYPE_PARCOURS": parcours,
        "PCT_ABSENCE": pct_absence.astype("float32"),
        "NB_RETARDS": nb_retards.astype("int16"),
        "SIGNALEMENT_COMP": sig_comp.astype("int16"),
        "NB_CREDITS_CUMUL": credits_cumul.astype("int16")
    })

    return optimize_dataframe_memory(df_out[PRIMARY_COLUMNS])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Générateur local et autonome de données primaires synthétiques (Loi 25)."
    )
    parser.add_argument(
        "input_chap",
        nargs="?",
        default="CHAP060105.csv",
        help="Chemin du fichier ministériel CHAP060105.csv (ex: CHAP060105-Juin.csv)."
    )
    parser.add_argument(
        "output_csv",
        nargs="?",
        default="donnees_primaires_synthetiques.csv",
        help="Chemin du fichier CSV de sortie (défaut: donnees_primaires_synthetiques.csv)."
    )
    parser.add_argument(
        "--n-fallback",
        type=int,
        default=500,
        help="Nombre d'élèves à générer si aucun fichier n'est trouvé."
    )
    args = parser.parse_args()

    df_105 = None
    if args.input_chap and os.path.exists(args.input_chap):
        print(f"Lecture du fichier ministériel : {args.input_chap} ...")
        df_105 = load_csv_robust(args.input_chap)
        n_eleves = df_105["CD_PERMN"].nunique() if "CD_PERMN" in df_105.columns else 0
        print(f" -> {len(df_105)} lignes lues ({n_eleves} CD_PERMN uniques).")
    else:
        print(f"Fichier '{args.input_chap}' non trouvé : génération autonome ({args.n_fallback} élèves)...")

    df_prim = generate_synthetic_primary_df(df_105, n_fallback=args.n_fallback)
    df_prim.to_csv(args.output_csv, index=False, encoding="utf-8-sig")
    print(f"Fichier CSV primaire généré avec succès : {args.output_csv} ({len(df_prim)} élèves uniques).")


if __name__ == "__main__":
    main()
