# -*- coding: utf-8 -*-
"""
core/data_loader.py - Chargement robuste, nettoyage, fusion et optimisation mémoire WASM.
Gère l'ingestion sans dépendance réseau des fichiers ministériels québécois (CHAP060105, CHS040506R).
"""

import io
import re
import unicodedata
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from core.schema import clean_cd_orgns
from core.metrics import assigner_typologie_janosz

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

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimise l'empreinte mémoire d'un DataFrame pour Pyodide/WebAssembly sans perte d'information:
    - Downcast float64 -> float32 (ex: PCT_ABSENCE, RESLT_FINAL)
    - Downcast int64 -> int32 / int16 (ex: AGE_30SEPT, NB_RETARDS, SIGNALEMENT_COMP, NB_CREDITS_CUMUL en int16 ; FLAG_PI en int32)
    - Colonnes textuelles répétitives -> category (ex: SEXE, CD_EHDAA, TYPE_PARCOURS, Profil_Janosz)
    - Colonnes booléennes -> int32 ou bool (neutralise le bug Arrow2 sous Stlite)
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return df

    cat_cols_fixed = {
        "CD_ORGNS", "CD_ORGNS_ORIGN", "Parcours", "Type_Cours", "Secteur",
        "École", "Statut", "Discipline", "Type_Anomalie", "Matiere",
        "Nom_Matiere", "Nom_Epreuve", "AN_SCOLAIRE", "Organisme", "Groupe",
        "Groupe_Virtuel", "SEXE", "CD_EHDAA", "TYPE_PARCOURS", "Profil_Janosz"
    }
    int16_cols_fixed = {
        "AGE_30SEPT", "NB_RETARDS", "SIGNALEMENT_COMP", "NB_CREDITS_CUMUL"
    }
    int32_cols_fixed = {
        "FLAG_PI"
    }
    float32_cols_fixed = {
        "PCT_ABSENCE", "RESLT_FINAL", "NOTE_MINST_CONVR"
    }

    for col in list(df.columns):
        col_type = df[col].dtype
        if col in int16_cols_fixed:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int16")
        elif col in int32_cols_fixed:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int32")
        elif col in float32_cols_fixed:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")
        elif col in cat_cols_fixed:
            if not isinstance(col_type, pd.CategoricalDtype):
                try:
                    s_clean = df[col].fillna("").astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
                    s_clean = s_clean.replace(["nan", "None"], "")
                    df[col] = s_clean.astype("category")
                except Exception:
                    pass
        elif pd.api.types.is_bool_dtype(col_type):
            continue
        elif isinstance(col_type, pd.CategoricalDtype):
            if pd.api.types.is_bool_dtype(df[col].cat.categories.dtype):
                df[col] = df[col].astype("int32")
        elif pd.api.types.is_float_dtype(col_type):
            df[col] = pd.to_numeric(df[col], downcast="float")
        elif pd.api.types.is_integer_dtype(col_type):
            df[col] = pd.to_numeric(df[col], downcast="integer")
        elif col_type == object:
            sample_non_null = df[col].dropna().head(20)
            if not sample_non_null.empty and all(isinstance(x, (bool, np.bool_)) for x in sample_non_null):
                df[col] = df[col].fillna(False).astype("int32")
    return df


def sanitize_df_for_stlite(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assure la compatibilité totale avec st.dataframe et le décodeur Arrow2 de Stlite:
    Convertit les colonnes booléennes ou catégories booléennes en int32 (1/0).
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return df
    df_clean = df.copy()
    for col in df_clean.columns:
        c_type = df_clean[col].dtype
        if pd.api.types.is_bool_dtype(c_type):
            df_clean[col] = df_clean[col].astype("int32")
        elif isinstance(c_type, pd.CategoricalDtype) and pd.api.types.is_bool_dtype(df_clean[col].cat.categories.dtype):
            df_clean[col] = df_clean[col].astype("int32")
    return df_clean


def load_csv_robust(file_or_buffer: Any) -> pd.DataFrame:
    """
    Charge un fichier CSV de façon ultra-robuste:
    - Encodages multiples (utf-8-sig, utf-8, cp1252, latin1)
    - Nettoyage automatique du BOM UTF-8 (\ufeff)
    - Détection automatique du séparateur (';', ',', '\t')
    - Noms de colonnes nettoyés
    """
    if hasattr(file_or_buffer, "seek"):
        try:
            file_or_buffer.seek(0)
        except Exception:
            pass

    raw_bytes = None
    if hasattr(file_or_buffer, "read"):
        raw_bytes = file_or_buffer.read()
        if hasattr(file_or_buffer, "seek"):
            try:
                file_or_buffer.seek(0)
            except Exception:
                pass
    elif isinstance(file_or_buffer, str):
        with open(file_or_buffer, "rb") as f:
            raw_bytes = f.read()
    elif isinstance(file_or_buffer, (bytes, bytearray)):
        raw_bytes = bytes(file_or_buffer)

    if raw_bytes is None or len(raw_bytes) == 0:
        return pd.DataFrame()

    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    delimiters = [";", ",", "\t"]

    df = None
    for enc in encodings:
        try:
            text = raw_bytes.decode(enc)
            text = text.lstrip("\ufeff\xef\xbb\xbf")

            first_line = ""
            for line in text.splitlines():
                if line.strip():
                    first_line = line
                    break

            counts = {d: first_line.count(d) for d in delimiters}
            best_sep = max(counts, key=counts.get)
            if counts[best_sep] == 0:
                best_sep = ";"

            df_candidate = pd.read_csv(io.StringIO(text), sep=best_sep, dtype=str)
            if df_candidate is not None and not df_candidate.empty and len(df_candidate.columns) > 1:
                df = df_candidate
                break
            elif df_candidate is not None and not df_candidate.empty and df is None:
                df = df_candidate
        except UnicodeDecodeError:
            continue
        except Exception:
            continue

    if df is None:
        try:
            if hasattr(file_or_buffer, "seek"):
                file_or_buffer.seek(0)
            df = pd.read_csv(file_or_buffer, sep=None, engine="python", dtype=str)
        except Exception:
            return pd.DataFrame()

    if df is not None and not df.empty:
        df.columns = [str(c).replace("\ufeff", "").strip() for c in df.columns]

    return df

def clean_and_merge_primary_data(
    df_main: pd.DataFrame,
    df_primaire: Optional[pd.DataFrame]
) -> pd.DataFrame:
    """
    Fusionne de manière vectorisée les données primaires d'élèves et d'assiduité sur CD_PERMN
    sans duplications mémoires (.copy() superflues évitées), applique le typage downcast
    et calcule la typologie de risque Janosz.
    """
    if df_main is None or not isinstance(df_main, pd.DataFrame) or df_main.empty:
        return df_main

    if df_primaire is not None and isinstance(df_primaire, pd.DataFrame) and not df_primaire.empty:
        df_primaire.columns = [str(c).strip() for c in df_primaire.columns]
        if "CD_PERMN" in df_primaire.columns and "CD_PERMN" in df_main.columns:
            cols_present = [c for c in PRIMARY_COLUMNS if c in df_primaire.columns]
            df_p_sub = df_primaire[cols_present].drop_duplicates(subset=["CD_PERMN"])
            df_p_sub["CD_PERMN"] = (
                df_p_sub["CD_PERMN"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
            )
            df_p_sub = optimize_dataframe_memory(df_p_sub)

            # Supprimer les colonnes primaires déjà présentes dans df_main avant le merge
            overlap_cols = [c for c in cols_present if c != "CD_PERMN" and c in df_main.columns]
            if overlap_cols:
                df_main = df_main.drop(columns=overlap_cols)

            df_main = pd.merge(df_main, df_p_sub, on="CD_PERMN", how="left")

    df_main = assigner_typologie_janosz(df_main)
    return optimize_dataframe_memory(df_main)


def clean_and_merge_data(
    df_105: Optional[pd.DataFrame],
    df_106: Optional[pd.DataFrame],
    df_chs: Optional[pd.DataFrame],
    df_profs: Optional[pd.DataFrame] = None,
    df_primaire: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Nettoie et fusionne les données scolaires sur le code permanent de l'élève (CD_PERMN).
    Crée le Groupe_Virtuel de manière vectorisée et optimise l'empreinte mémoire.
    """
    def to_numeric_safe(df_in, col):
        if col in df_in.columns:
            df_in[col] = pd.to_numeric(df_in[col], errors="coerce")
        return df_in

    def to_string_safe(df_in, col):
        if col in df_in.columns:
            df_in[col] = df_in[col].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
            df_in[col] = df_in[col].replace(["nan", "None", ""], np.nan)
            if col == "CD_ORGNS":
                df_in[col] = df_in[col].apply(clean_cd_orgns)
        return df_in

    dfs_to_concat = []
    for df in [df_105, df_106]:
        if df is not None and not df.empty:
            df_c = df.copy()
            df_c.columns = [str(c).replace("\ufeff", "").strip().upper() for c in df_c.columns]
            df_c = to_numeric_safe(df_c, "RESLT_FINAL")
            df_c = to_string_safe(df_c, "CD_COURS")
            df_c = to_string_safe(df_c, "CD_PERMN")
            df_c = to_string_safe(df_c, "CD_ORGNS")
            dedup_sub = [c for c in ["CD_PERMN", "CD_COURS"] if c in df_c.columns]
            df_dedup = df_c.drop_duplicates(subset=dedup_sub) if dedup_sub else df_c.drop_duplicates()
            dfs_to_concat.append(df_dedup)

    if df_chs is not None and not df_chs.empty:
        df_chs_c = df_chs.copy()
        df_chs_c.columns = [str(c).replace("\ufeff", "").strip().upper() for c in df_chs_c.columns]
        df_chs_c = to_numeric_safe(df_chs_c, "RESLT_FINAL")
        df_chs_c = to_numeric_safe(df_chs_c, "NOTE_MINST_CONVR")
        df_chs_c = to_string_safe(df_chs_c, "CD_COURS")
        df_chs_c = to_string_safe(df_chs_c, "CD_PERMN")
        df_chs_c = to_string_safe(df_chs_c, "CD_ORGNS")
        if "ORGANISME" in df_chs_c.columns:
            df_chs_c["ORGANISME"] = df_chs_c["ORGANISME"].apply(clean_cd_orgns)
        elif "Organisme" in df_chs_c.columns:
            df_chs_c["Organisme"] = df_chs_c["Organisme"].apply(clean_cd_orgns)
    else:
        df_chs_c = None

    if dfs_to_concat:
        df_notes = pd.concat(dfs_to_concat, ignore_index=True)
        dedup_notes = [c for c in ["CD_PERMN", "CD_COURS"] if c in df_notes.columns]
        df_notes = df_notes.drop_duplicates(subset=dedup_notes) if dedup_notes else df_notes.drop_duplicates()
    else:
        df_notes = pd.DataFrame()

    if df_chs_c is not None and not df_chs_c.empty and not df_notes.empty:
        merge_cols = []
        if "CD_PERMN" in df_chs_c.columns and "CD_PERMN" in df_notes.columns:
            merge_cols.append("CD_PERMN")
        if "CD_COURS" in df_chs_c.columns and "CD_COURS" in df_notes.columns:
            merge_cols.append("CD_COURS")

        if merge_cols:
            df_merged = pd.merge(df_notes, df_chs_c, on=merge_cols, how="outer", suffixes=("", "_chs"))
            if "RESLT_FINAL_chs" in df_merged.columns:
                df_merged["RESLT_FINAL"] = df_merged["RESLT_FINAL"].fillna(df_merged["RESLT_FINAL_chs"])
                df_merged = df_merged.drop(columns=["RESLT_FINAL_chs"])
        else:
            df_merged = df_notes
    elif not df_notes.empty:
        df_merged = df_notes
    elif df_chs_c is not None and not df_chs_c.empty:
        df_merged = df_chs_c
    else:
        return pd.DataFrame()

    if "NO_GROUP_ELEVE" not in df_merged.columns:
        for c in ["NO_GROUP", "CD_ORGNS_NO_GROUP", "NO_GROUPE", "GROUPE", "GROUP"]:
            if c in df_merged.columns:
                df_merged["NO_GROUP_ELEVE"] = df_merged[c]
                break

    def _norm_grp_str(val: Any) -> str:
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

    if "NO_GROUP_ELEVE" in df_merged.columns:
        df_merged["NO_GROUP_ELEVE"] = df_merged["NO_GROUP_ELEVE"].apply(_norm_grp_str)

    if df_profs is not None and not df_profs.empty:
        df_profs_c = df_profs.copy()
        df_profs_c.columns = df_profs_c.columns.str.strip().str.upper()

        if "NO_GROUP_ELEVE" not in df_profs_c.columns:
            for c in ["NO_GROUP", "CD_ORGNS_NO_GROUP", "NO_GROUPE", "GROUPE", "GROUP"]:
                if c in df_profs_c.columns:
                    df_profs_c["NO_GROUP_ELEVE"] = df_profs_c[c]
                    break
        if "NO_GROUP_ELEVE" in df_profs_c.columns:
            df_profs_c["NO_GROUP_ELEVE"] = df_profs_c["NO_GROUP_ELEVE"].apply(_norm_grp_str)

        if "CD_ORGNS" not in df_profs_c.columns:
            for c in ["ORGANISME", "ECOLE", "ÉCOLE", "CD_ECOLE"]:
                if c in df_profs_c.columns:
                    df_profs_c["CD_ORGNS"] = df_profs_c[c]
                    break
        if "CD_ORGNS" in df_profs_c.columns:
            df_profs_c["CD_ORGNS"] = df_profs_c["CD_ORGNS"].apply(clean_cd_orgns)

        if "CD_COURS" not in df_profs_c.columns:
            for c in ["COURS", "CODE_COURS", "DISCIPLINE"]:
                if c in df_profs_c.columns:
                    df_profs_c["CD_COURS"] = df_profs_c[c]
                    break

        if "ENSEIGN" not in df_profs_c.columns:
            for c in ["ENSEIGNANT", "ENSEIGNANTE", "PROF", "NOM_ENSEIGNANT", "NOM_PROF", "TEACHER"]:
                if c in df_profs_c.columns:
                    df_profs_c["ENSEIGN"] = df_profs_c[c]
                    break

        for col_p in ["CD_COURS", "NO_GROUP_ELEVE", "ENSEIGN"]:
            if col_p in df_profs_c.columns:
                df_profs_c[col_p] = df_profs_c[col_p].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()

        # Appariement canonique : tolérant au zéro initial de CD_COURS et au format du groupe
        join_keys = [k for k in ["CD_ORGNS", "CD_COURS", "NO_GROUP_ELEVE"] if k in df_profs_c.columns and k in df_merged.columns]
        if join_keys and "ENSEIGN" in df_profs_c.columns:
            df_merged["_k_org"] = df_merged["CD_ORGNS"].astype(str).apply(clean_cd_orgns)
            df_profs_c["_k_org"] = df_profs_c["CD_ORGNS"].astype(str).apply(clean_cd_orgns)
            merge_on = ["_k_org"]

            if "CD_COURS" in join_keys:
                df_merged["_k_cours"] = df_merged["CD_COURS"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.lstrip("0")
                df_profs_c["_k_cours"] = df_profs_c["CD_COURS"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.lstrip("0")
                merge_on.append("_k_cours")

            if "NO_GROUP_ELEVE" in join_keys:
                df_merged["_k_grp"] = df_merged["NO_GROUP_ELEVE"].astype(str).apply(_norm_grp_str)
                df_profs_c["_k_grp"] = df_profs_c["NO_GROUP_ELEVE"].astype(str).apply(_norm_grp_str)
                merge_on.append("_k_grp")

            df_profs_dedup = df_profs_c.drop_duplicates(subset=merge_on)
            cols_to_pull = merge_on + ["ENSEIGN"]
            df_merged = pd.merge(df_merged, df_profs_dedup[cols_to_pull], on=merge_on, how="left")
            df_merged = df_merged.drop(columns=[c for c in ["_k_org", "_k_cours", "_k_grp"] if c in df_merged.columns])

    if "CD_COURS" in df_merged.columns:
        df_merged["CD_COURS_str"] = df_merged["CD_COURS"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True).str.strip()

    if "CD_COURS_str" in df_merged.columns:
        from core.schema import ENRICHED_CODES
        if "CD_PERMN" in df_merged.columns:
            eleves_enrichis = set(df_merged.loc[df_merged["CD_COURS_str"].isin(ENRICHED_CODES), "CD_PERMN"].unique())
            df_merged["Parcours"] = pd.Categorical(np.where(
                df_merged["CD_PERMN"].isin(eleves_enrichis),
                "Enrichi",
                "Régulier"
            ))

        def classify_course(code):
            if pd.isna(code) or str(code).strip() in ["nan", "None", ""]:
                return "Inconnu"
            c = str(code).strip()
            if c.endswith("0"):
                return "Composante"
            elif c.endswith(("4", "6", "8")):
                return "Note globale"
            return "Autre"

        df_merged["Type_Cours"] = pd.Categorical(df_merged["CD_COURS_str"].apply(classify_course))

    if "RESLT_FINAL" in df_merged.columns:
        df_merged["RESLT_FINAL"] = pd.to_numeric(df_merged["RESLT_FINAL"], errors="coerce").astype("float32")
        df_merged["Reussite"] = df_merged["RESLT_FINAL"] >= 60

    if "NOTE_MINST_CONVR" in df_merged.columns:
        df_merged["NOTE_MINST_CONVR"] = pd.to_numeric(df_merged["NOTE_MINST_CONVR"], errors="coerce").astype("float32")

    if "CD_ORGNS" in df_merged.columns:
        df_merged["CD_ORGNS"] = df_merged["CD_ORGNS"].apply(clean_cd_orgns)

    # Création vectorisée de Groupe_Virtuel
    if "CD_ORGNS" in df_merged.columns and "NO_GROUP_ELEVE" in df_merged.columns:
        grp_str = df_merged["NO_GROUP_ELEVE"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        grp_fmt = grp_str.apply(lambda x: f"{int(x):02d}" if x.isdigit() else x)
        ecole_fmt = df_merged["CD_ORGNS"].fillna("").astype(str).str.strip()

        base_grp = np.where(
            (ecole_fmt != "") & (grp_fmt != ""),
            ecole_fmt + "-" + grp_fmt,
            np.where(ecole_fmt != "", ecole_fmt, np.where(grp_fmt != "", grp_fmt, "Inconnu"))
        )
        if "ENSEIGN" in df_merged.columns:
            ens_str = df_merged["ENSEIGN"].fillna("").astype(str).str.strip()
            has_ens = ~ens_str.isin(["", "nan", "None"])
            base_grp = np.where(has_ens, base_grp + " (" + ens_str + ")", base_grp)
        df_merged["Groupe_Virtuel"] = pd.Series(base_grp, index=df_merged.index).astype("category")
    else:
        df_merged["Groupe_Virtuel"] = "Inconnu"

    df_merged = clean_and_merge_primary_data(df_merged, df_primaire)
    return df_merged


def _norm_col_name(s: Any) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s).lower()) if unicodedata.category(c) != "Mn").strip()


def map_moderation_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Mappe tolérante des colonnes du rapport de modération CHS040506R."""
    if df is None or df.empty:
        return pd.DataFrame()
    mapping = {}
    for col in df.columns:
        n = _norm_col_name(col)
        if ("organisme" in n or "cd_orgns" in n or n == "ecole") and "Organisme" not in mapping.values():
            mapping[col] = "Organisme"
        elif "groupe" in n and "Groupe" not in mapping.values():
            mapping[col] = "Groupe"
        elif ("titre" in n or "matiere" in n or "discipline" in n) and "Matiere" not in mapping.values():
            mapping[col] = "Matiere"
        elif (("nb" in n and ("elev" in n or "etud" in n)) or n == "effectif") and "Nb_eleves" not in mapping.values():
            mapping[col] = "Nb_eleves"
        elif ("ecole" in n or "neb" in n) and ("moyenne" in n or "mean" in n or "brute" in n) and not ("ecart" in n or "et" in n or "lorsque" in n) and "Moyenne_ecole" not in mapping.values():
            mapping[col] = "Moyenne_ecole"
        elif ("ecole" in n or "neb" in n) and ("ecart" in n or "et" in n or "std" in n) and "ET_ecole" not in mapping.values():
            mapping[col] = "ET_ecole"
        elif ("min" in n or "minister" in n or "nmc" in n) and ("moyenne" in n or "mean" in n or "conv" in n) and not ("ecart" in n or "et" in n or "lorsque" in n) and "Moyenne_min" not in mapping.values():
            mapping[col] = "Moyenne_min"
        elif ("min" in n or "minister" in n or "nmc" in n) and ("ecart" in n or "et" in n or "std" in n) and "ET_min" not in mapping.values():
            mapping[col] = "ET_min"
        elif (re.search(r"facteur\s*[-_ ]*\s*r\b", n) or n == "r" or n == "facteur_r") and "Facteur_R" not in mapping.values():
            mapping[col] = "Facteur_R"
        elif (re.search(r"facteur\s*[-_ ]*\s*q\b", n) or n == "q" or n == "facteur_q") and "Facteur_Q" not in mapping.values():
            mapping[col] = "Facteur_Q"
        elif re.search(r"neb.*nem\s*=\s*60", n) and "NEB_60" not in mapping.values():
            mapping[col] = "NEB_60"
        elif re.search(r"nem.*neb\s*=\s*60", n) and "NEM_60" not in mapping.values():
            mapping[col] = "NEM_60"
        elif re.search(r"neb.*nem\s*=\s*100", n) and "NEB_100" not in mapping.values():
            mapping[col] = "NEB_100"

    return df.rename(columns=mapping)


def clean_moderation_df(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et prépare le DataFrame de modération pour les analyses."""
    if df is None or df.empty:
        return pd.DataFrame()
    df_clean = map_moderation_columns(df)

    colonnes_numeriques = [
        "Nb_eleves", "Moyenne_ecole", "ET_ecole", "Moyenne_min", "ET_min",
        "Facteur_R", "Facteur_Q", "NEB_60", "NEB_100", "NEM_60"
    ]
    for col in colonnes_numeriques:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(
                df_clean[col].astype(str).str.replace(",", ".", regex=False).str.strip().replace(["", "None", "nan", "NaN"], np.nan),
                errors="coerce"
            ).astype(np.float32)

    req_cols = ["Moyenne_ecole", "Moyenne_min"]
    for c in req_cols:
        if c not in df_clean.columns:
            return pd.DataFrame()

    df_clean = df_clean.dropna(subset=req_cols)
    if "Nb_eleves" not in df_clean.columns:
        df_clean["Nb_eleves"] = 1
    else:
        df_clean["Nb_eleves"] = df_clean["Nb_eleves"].fillna(1).astype(np.int32)

    if "Organisme" in df_clean.columns:
        df_clean["Organisme"] = df_clean["Organisme"].apply(clean_cd_orgns)
    else:
        df_clean["Organisme"] = ""

    if "Groupe" not in df_clean.columns:
        df_clean["Groupe"] = df_clean.index.astype(str)

    if "Matiere" not in df_clean.columns:
        df_clean["Matiere"] = "Discipline"

    return optimize_dataframe_memory(df_clean)


def apply_filters(
    df: pd.DataFrame,
    annee: str = "Toutes",
    matiere: str = "Toutes",
    ecole: str = "Toutes",
    parcours: str = "Tous"
) -> pd.DataFrame:
    """Filtre le DataFrame selon les critères sans mutation in-place."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()

    mask = pd.Series(True, index=df.index)

    if annee and "AN_SCOLAIRE" in df.columns and str(annee) != "Toutes":
        mask &= (df["AN_SCOLAIRE"].astype(str) == str(annee))

    if matiere and "CD_COURS_str" in df.columns and str(matiere) != "Toutes":
        m_match = re.search(r"\((\d+)\)", str(matiere))
        if m_match:
            code_target = m_match.group(1)
            # Préfixe de famille disciplinaire (ex: 1324, 1325, 634, 654, 644, 554, 574, 854)
            # pour conserver à la fois le cours global et ses composantes/compétences terminant par 0
            pfx = code_target[:-2] if len(code_target) >= 5 else code_target.rstrip("468")
            mask &= (
                df["CD_COURS_str"].astype(str).str.contains(code_target, na=False) |
                df["CD_COURS_str"].astype(str).str.contains(pfx, na=False)
            )
        else:
            mask &= df["CD_COURS_str"].astype(str).str.contains(str(matiere), na=False)

    if ecole and "CD_ORGNS" in df.columns and str(ecole) != "Toutes":
        ecole_clean = clean_cd_orgns(ecole)
        ecole_series = df["CD_ORGNS"].astype(str).apply(clean_cd_orgns)
        mask &= (ecole_series == ecole_clean)

    if parcours and "Parcours" in df.columns and str(parcours) != "Tous":
        mask &= (df["Parcours"].astype(str) == str(parcours))

    if mask.all():
        return df

    return df.loc[mask]



def parse_pdf_to_df(pdf_file: Any) -> pd.DataFrame:
    """
    Extrait les tables de modération CHS040506R depuis un PDF (mode local uniquement).
    Non disponible sous Stlite WebAssembly sans pdfplumber.
    """
    if not PDFPLUMBER_AVAILABLE:
        return pd.DataFrame()

    headers = [
        "Organisme", "Organisme_Complet", "Épreuve", "Volet", "Matiere", "Titre",
        "Groupe", "Nb. élèves",
        "Notes école brutes - Moyenne", "Notes école brutes - Écart type",
        "Notes min. conv. - Moyenne", "Notes min. conv. - Écart type",
        "Pourcentage lors du calcul - École", "Pourcentage lors du calcul - Ministère",
        "Facteur - R", "Facteur - Q",
        "Modération - NEB lorsque NEM = 60",
        "Modération - NEM lorsque NEB = 60",
        "Modération - NEB lorsque NEM = 1",
        "Modération - NEB lorsque NEM = 100"
    ]
    data = []

    def _parse_flt(v):
        if v is None:
            return None
        s = str(v).strip().replace(",", ".")
        if s.startswith("."):
            s = "0" + s
        elif s.startswith("-."):
            s = "-0" + s[2:]
        try:
            return float(s)
        except ValueError:
            return None

    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if not txt or "Tables de mod" not in txt:
                    continue

                org_m = re.search(r"Organisme\s+(\d+)", txt)
                epr_m = re.search(r"[ÉEé]preuve:\s*([0-9A-Za-z]+)\s+Titre:\s*([^\r\n]+)", txt)
                vol_m = re.search(r"Volet:\s*([0-9A-Za-z]+)?\s*Titre:\s*([^\r\n]*)", txt)

                org_complet = org_m.group(1).strip() if org_m else ""
                organisme = clean_cd_orgns(org_complet)
                epreuve = epr_m.group(1).strip() if epr_m else ""
                titre_epreuve = epr_m.group(2).strip() if epr_m else ""

                volet = ""
                titre_volet = ""
                if vol_m:
                    vol_code = vol_m.group(1)
                    if vol_code and vol_code.lower() != "titre:":
                        volet = vol_code.strip()
                    titre_volet = vol_m.group(2).strip()

                matiere_std = epreuve
                titre_complet = (f"{titre_epreuve} - {titre_volet}").strip(" -")

                m_grp = re.search(r"Groupe:\s*(\S+)", txt)
                groupe = m_grp.group(1).strip() if m_grp else ""

                m_nb = re.search(r"Nb\.\s*élèves:\s*(\d+)", txt)
                nb_eleves = int(m_nb.group(1)) if m_nb else None

                m_neb = re.search(r"Notes école brutes\s+([\d.,]+)\s+([\d.,]+)", txt)
                moy_brute = _parse_flt(m_neb.group(1)) if m_neb else None
                ecart_brute = _parse_flt(m_neb.group(2)) if m_neb else None

                m_nmc = re.search(r"Notes min\.\s*conv\.\s+([\d.,]+)\s+([\d.,]+)", txt)
                moy_conv = _parse_flt(m_nmc.group(1)) if m_nmc else None
                ecart_conv = _parse_flt(m_nmc.group(2)) if m_nmc else None

                m_pct = re.search(r"Pourcentage lors du calcul\s+([\d.,]+)\s+([\d.,]+)", txt)
                pct_ecole = _parse_flt(m_pct.group(1)) if m_pct else None
                pct_min = _parse_flt(m_pct.group(2)) if m_pct else None

                m_fact = re.search(r"Facteur\s+([\d.,-]+)\s+([\d.,-]+)", txt)
                facteur_r = _parse_flt(m_fact.group(1)) if m_fact else None
                facteur_q = _parse_flt(m_fact.group(2)) if m_fact else None

                data.append([
                    organisme, org_complet, epreuve, volet, matiere_std, titre_complet,
                    groupe, nb_eleves,
                    moy_brute, ecart_brute, moy_conv, ecart_conv,
                    pct_ecole, pct_min, facteur_r, facteur_q,
                    "", "", "", ""
                ])
        return pd.DataFrame(data, columns=headers)
    except Exception:
        return pd.DataFrame(columns=headers)

