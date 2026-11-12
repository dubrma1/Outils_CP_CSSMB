# -*- coding: utf-8 -*-
"""
core/state.py - Gestionnaire centralisé du st.session_state et filtres globaux.
Assure une source unique de vérité (SSOT) sans duplications mémoires (.copy() évitées),
partage les filtres entre toutes les pages et gère l'opt-in de confidentialité.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

from core.data_loader import optimize_dataframe_memory, apply_filters, clean_and_merge_primary_data, PRIMARY_COLUMNS
from core.schema import clean_cd_orgns

KEY_DF_RAW = "df_raw"
KEY_DF_FILTERED = "df_filtered"
KEY_DF_GLOBAL = "df_global"
KEY_DF_MODERATION = "df_moderation_raw"
KEY_DF_PRIMAIRE = "df_primaire"
KEY_DF_SEXE = "df_sexe"
KEY_DF_PI = "df_pi"
KEY_DF_PROFS = "df_profs"
KEY_DF_AOUT = "df_aout"
KEY_FILTERS = "global_filters"
KEY_TEACHER_OPT_IN = "teacher_opt_in"


def init_session_state() -> None:
    """Initialise les clés d'état globales si elles n'existent pas encore."""
    if KEY_DF_RAW not in st.session_state:
        st.session_state[KEY_DF_RAW] = pd.DataFrame()
    if KEY_DF_FILTERED not in st.session_state:
        st.session_state[KEY_DF_FILTERED] = pd.DataFrame()
    if KEY_DF_GLOBAL not in st.session_state:
        st.session_state[KEY_DF_GLOBAL] = pd.DataFrame()
    if KEY_DF_MODERATION not in st.session_state:
        st.session_state[KEY_DF_MODERATION] = pd.DataFrame()
    if KEY_DF_PRIMAIRE not in st.session_state:
        st.session_state[KEY_DF_PRIMAIRE] = pd.DataFrame()
    if KEY_DF_SEXE not in st.session_state:
        st.session_state[KEY_DF_SEXE] = pd.DataFrame()
    if KEY_DF_PI not in st.session_state:
        st.session_state[KEY_DF_PI] = pd.DataFrame()
    if KEY_DF_PROFS not in st.session_state:
        st.session_state[KEY_DF_PROFS] = pd.DataFrame()
    if KEY_DF_AOUT not in st.session_state:
        st.session_state[KEY_DF_AOUT] = pd.DataFrame()
    if KEY_FILTERS not in st.session_state:
        st.session_state[KEY_FILTERS] = {
            "selected_retac": "Tous",
            "selected_ecole": "Toutes",
            "selected_ecoles": [],
            "selected_matiere": "Toutes",
            "selected_matieres": [],
            "filter_enriched": False,
            "min_effectif": 5
        }
    if KEY_TEACHER_OPT_IN not in st.session_state:
        st.session_state[KEY_TEACHER_OPT_IN] = False


def render_primary_data_uploader() -> Any:
    """Rend le chargeur optionnel des données primaires dans la barre latérale."""
    file_primaire = st.sidebar.file_uploader("Données primaires Élèves & Assiduité (CSV)", type=["csv"])
    return file_primaire


def get_df_primaire() -> pd.DataFrame:
    init_session_state()
    return st.session_state.get(KEY_DF_PRIMAIRE, pd.DataFrame())


def set_df_primaire(df: pd.DataFrame) -> None:
    """
    Enregistre le DataFrame des données primaires optimisé, alimente df_sexe et df_pi
    en arrière-plan pour la compatibilité ascendante, et enrichit df_main si présent.
    """
    init_session_state()
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        st.session_state[KEY_DF_PRIMAIRE] = pd.DataFrame()
        return

    df_opt = optimize_dataframe_memory(df)
    st.session_state[KEY_DF_PRIMAIRE] = df_opt

    if "CD_PERMN" in df_opt.columns:
        if "SEXE" in df_opt.columns:
            st.session_state[KEY_DF_SEXE] = df_opt[["CD_PERMN", "SEXE"]]
        if "FLAG_PI" in df_opt.columns or "CD_EHDAA" in df_opt.columns:
            flag_s = pd.to_numeric(df_opt["FLAG_PI"], errors="coerce").fillna(0) > 0 if "FLAG_PI" in df_opt.columns else pd.Series(False, index=df_opt.index)
            ehdaa_s = (~df_opt["CD_EHDAA"].astype(str).isin(["", "nan", "None", "Ordinaire"])) if "CD_EHDAA" in df_opt.columns else pd.Series(False, index=df_opt.index)
            df_pi_compat = pd.DataFrame({
                "CD_PERMN": df_opt["CD_PERMN"],
                "PI": pd.Series(flag_s | ehdaa_s, index=df_opt.index).map({True: "Oui", False: ""})
            })
            st.session_state[KEY_DF_PI] = optimize_dataframe_memory(df_pi_compat)

    df_main = get_df_main()
    if not df_main.empty:
        df_enriched = clean_and_merge_primary_data(df_main, df_opt)
        set_df_main(df_enriched)


def get_df_sexe() -> pd.DataFrame:
    init_session_state()
    return st.session_state.get(KEY_DF_SEXE, pd.DataFrame())


def set_df_sexe(df: pd.DataFrame) -> None:
    init_session_state()
    st.session_state[KEY_DF_SEXE] = optimize_dataframe_memory(df)


def get_df_pi() -> pd.DataFrame:
    init_session_state()
    return st.session_state.get(KEY_DF_PI, pd.DataFrame())


def set_df_pi(df: pd.DataFrame) -> None:
    init_session_state()
    st.session_state[KEY_DF_PI] = optimize_dataframe_memory(df)


def get_df_profs() -> pd.DataFrame:
    init_session_state()
    return st.session_state.get(KEY_DF_PROFS, pd.DataFrame())


def set_df_profs(df: pd.DataFrame) -> None:
    init_session_state()
    st.session_state[KEY_DF_PROFS] = optimize_dataframe_memory(df)


def get_df_aout() -> pd.DataFrame:
    init_session_state()
    return st.session_state.get(KEY_DF_AOUT, pd.DataFrame())


def set_df_aout(df: pd.DataFrame) -> None:
    init_session_state()
    st.session_state[KEY_DF_AOUT] = optimize_dataframe_memory(df)


def get_df_main() -> pd.DataFrame:
    """
    Retourne la source unique de vérité du DataFrame principal depuis st.session_state
    sans clonage mémoire (.copy()).
    """
    init_session_state()
    for key in [KEY_DF_RAW, KEY_DF_FILTERED, KEY_DF_GLOBAL]:
        df = st.session_state.get(key)
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    return pd.DataFrame()


def set_df_main(df: pd.DataFrame) -> None:
    """
    Enregistre le DataFrame principal comme Single Source of Truth dans st.session_state,
    optimise son empreinte mémoire et lie les alias historiques sans créer de copies redondantes.
    """
    init_session_state()
    df_opt = optimize_dataframe_memory(df)
    st.session_state[KEY_DF_RAW] = df_opt
    st.session_state[KEY_DF_FILTERED] = df_opt
    st.session_state[KEY_DF_GLOBAL] = df_opt


def get_df_moderation() -> pd.DataFrame:
    """Retourne le DataFrame de modération depuis st.session_state sans clonage."""
    init_session_state()
    df = st.session_state.get(KEY_DF_MODERATION)
    if isinstance(df, pd.DataFrame) and not df.empty:
        return df
    return pd.DataFrame()


def set_df_moderation(df: pd.DataFrame) -> None:
    """Enregistre le DataFrame de modération optimisé dans st.session_state."""
    init_session_state()
    df_opt = optimize_dataframe_memory(df)
    st.session_state[KEY_DF_MODERATION] = df_opt


def get_global_filters() -> Dict[str, Any]:
    """Retourne le dictionnaire des filtres globaux persistants."""
    init_session_state()
    return st.session_state.get(KEY_FILTERS, {})


def set_global_filters(filters: Dict[str, Any]) -> None:
    """Met à jour l'ensemble des filtres globaux."""
    init_session_state()
    current = st.session_state.get(KEY_FILTERS, {})
    current.update(filters)
    st.session_state[KEY_FILTERS] = current


def update_global_filter(key: str, value: Any) -> None:
    """Met à jour un filtre global spécifique."""
    init_session_state()
    st.session_state[KEY_FILTERS][key] = value


def get_teacher_opt_in() -> bool:
    """Indique si l'utilisateur a explicitement consenti à afficher les noms d'enseignants."""
    init_session_state()
    return bool(st.session_state.get(KEY_TEACHER_OPT_IN, False))


def set_teacher_opt_in(opt_in: bool) -> None:
    """Enregistre le consentement de l'utilisateur pour l'affichage des enseignants."""
    init_session_state()
    st.session_state[KEY_TEACHER_OPT_IN] = bool(opt_in)


def get_filtered_main_df(
    selected_ecoles: Optional[List[str]] = None,
    selected_matieres: Optional[List[str]] = None,
    filter_enriched: bool = False
) -> pd.DataFrame:
    """
    Applique les filtres sélectionnés sur df_main sans aucune mutation du DataFrame source.
    """
    df = get_df_main()
    if df.empty:
        return df

    mask = pd.Series(True, index=df.index)

    if selected_ecoles:
        clean_ecoles = set(clean_cd_orgns(e) for e in selected_ecoles if clean_cd_orgns(e))
        if clean_ecoles and "CD_ORGNS" in df.columns:
            mask &= df["CD_ORGNS"].astype(str).isin(clean_ecoles)

    if filter_enriched:
        from core.schema import ENRICHED_CODES
        if "CD_PERMN" in df.columns and "CD_COURS_str" in df.columns:
            enriched_students = set(df.loc[df["CD_COURS_str"].isin(ENRICHED_CODES), "CD_PERMN"].unique())
            mask &= (~df["CD_PERMN"].isin(enriched_students))

    if mask.all():
        return df

    return df.loc[mask]
