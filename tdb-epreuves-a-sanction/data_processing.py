# -*- coding: utf-8 -*-
"""
data_processing.py - Module de transition et compatibilité ascendante.
Redirige les appels historiques vers l'architecture modulaire core (schema, data_loader, metrics, state).
"""

from core.schema import (
    SUBJECT_MAP, ECOLES_LIST, ECOLES_OPTIONS, ECOLES_SECTEURS,
    clean_cd_orgns, ENRICHED_CODES, CODE_TO_MATIERE, CODE_TO_MATIERE_COURT,
    CODE_TO_EPREUVE, EPREUVE_TO_MATIERE, MATIERES_LIST, MATIERES_CIBLES_FULL,
    SANCTION_MATIERES_MAP, SANCTION_4E_MATIERES
)
from core.data_loader import (
    optimize_dataframe_memory, sanitize_df_for_stlite,
    load_csv_robust, parse_pdf_to_df, clean_and_merge_data,
    map_moderation_columns, clean_moderation_df, apply_filters,
    PDFPLUMBER_AVAILABLE
)
from core.state import (
    get_df_main, set_df_main, get_df_moderation, set_df_moderation
)
from core.metrics import (
    wilson_interval, compute_success_rate, compute_cohen_d,
    compute_dispersion_ratio, classify_moderation_anomaly,
    add_confidence_intervals
)
import pandas as pd
import numpy as np


def analyze_moderation_df(df: pd.DataFrame, seuil_cohen: float = 0.8, seuil_dispersion: float = 0.6) -> pd.DataFrame:
    """Fonction historique d'analyse de modération avec colonnes calculées."""
    if df is None or df.empty:
        return pd.DataFrame()
    df_clean = clean_moderation_df(df)
    if df_clean.empty:
        return df_clean

    df_clean["Delta_Moyenne"] = (df_clean["Moyenne_ecole"] - df_clean["Moyenne_min"]).astype("float32")
    et_min_safe = df_clean.get("ET_min", 10.0).replace(0, np.nan)
    df_clean["Ratio_ET"] = (df_clean.get("ET_ecole", 10.0) / et_min_safe).fillna(1.0).astype("float32")

    var_p = (df_clean.get("ET_ecole", 10.0)**2 + df_clean.get("ET_min", 10.0)**2) / 2.0
    df_clean["Cohen_D"] = (df_clean["Delta_Moyenne"] / np.sqrt(var_p)).fillna(0.0).astype("float32")

    df_clean["Type_Anomalie"] = [
        classify_moderation_anomaly(row["Cohen_D"], row["Ratio_ET"], seuil_cohen, seuil_dispersion)
        for _, row in df_clean.iterrows()
    ]
    df_clean["Label_Groupe"] = "École " + df_clean["Organisme"].astype(str) + " - Gr. " + df_clean["Groupe"].astype(str)
    return optimize_dataframe_memory(df_clean)


def compute_moderation_stats(df: pd.DataFrame, seuil_cohen: float = 0.8, seuil_dispersion: float = 0.6) -> pd.DataFrame:
    return analyze_moderation_df(df, seuil_cohen, seuil_dispersion)


def compute_school_subject_rates(df, code_to_matiere, filter_enriched=False, _enriched_list=None):
    """Agrégation historique des taux par école et matière."""
    mask = (df["Type_Cours"] == "Note globale")
    if filter_enriched and _enriched_list is not None:
        mask &= (~df["CD_PERMN"].isin(_enriched_list))

    cols_needed = ["CD_ORGNS", "CD_COURS_str", "Reussite", "CD_PERMN"]
    sub_df = df.loc[mask, [c for c in cols_needed if c in df.columns]].copy()
    sub_df["Nom_Matiere"] = sub_df["CD_COURS_str"].map(code_to_matiere)
    stats_df = sub_df.groupby(["CD_ORGNS", "Nom_Matiere"], observed=True).agg(
        Reussite=("Reussite", "mean"),
        Effectif=("CD_PERMN", "nunique"),
        Succes=("Reussite", "sum")
    ).reset_index()
    stats_df["Echecs"] = (stats_df["Effectif"] - stats_df["Succes"]).astype("int32")
    stats_df["Texte_Echecs"] = stats_df["Echecs"].apply(lambda x: f"{int(x)} échec(s)")
    stats_df["Taux (%)"] = (stats_df["Reussite"] * 100.0).astype("float32")
    stats_df["Taux de réussite (%)"] = stats_df["Taux (%)"]
    stats_df["École"] = stats_df["CD_ORGNS"].apply(clean_cd_orgns)
    return stats_df


def compute_epreuve_rates(df, code_to_epreuve, filter_enriched=False, _enriched_list=None):
    """Agrégation historique des taux aux épreuves uniques."""
    mask = df["CD_COURS_str"].isin(code_to_epreuve.keys())
    if filter_enriched and _enriched_list is not None:
        mask &= (~df["CD_PERMN"].isin(_enriched_list))

    cols_needed = ["CD_ORGNS", "CD_COURS_str", "NOTE_MINST_CONVR", "CD_PERMN"]
    df_ep = df.loc[mask, [c for c in cols_needed if c in df.columns]].copy()
    df_ep["Nom_Epreuve"] = df_ep["CD_COURS_str"].map(code_to_epreuve)
    df_ep["NOTE_MINST_CONVR"] = pd.to_numeric(df_ep["NOTE_MINST_CONVR"], errors="coerce")
    df_ep_val = df_ep.dropna(subset=["NOTE_MINST_CONVR"]).copy()
    df_ep_val["Reussite_Epreuve"] = df_ep_val["NOTE_MINST_CONVR"] >= 60
    stats_df = df_ep_val.groupby(["CD_ORGNS", "Nom_Epreuve"], observed=True).agg(
        Reussite=("Reussite_Epreuve", "mean"),
        Effectif=("CD_PERMN", "nunique"),
        Succes=("Reussite_Epreuve", "sum")
    ).reset_index()
    stats_df["Echecs"] = (stats_df["Effectif"] - stats_df["Succes"]).astype("int32")
    stats_df["Texte_Echecs"] = stats_df["Echecs"].apply(lambda x: f"{int(x)} échec(s)")
    stats_df["Taux (%)"] = (stats_df["Reussite"] * 100.0).astype("float32")
    stats_df["Taux de réussite (%)"] = stats_df["Taux (%)"]
    stats_df["École"] = stats_df["CD_ORGNS"].apply(clean_cd_orgns)
    return stats_df
