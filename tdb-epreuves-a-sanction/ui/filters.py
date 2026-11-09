# -*- coding: utf-8 -*-
"""
ui/filters.py - Filtres globaux interactifs et persistants dans la barre latérale (LAD P5).
Gère la persistance de la sélection entre les pages et le consentement d'affichage éthique.
"""

from typing import Any, Dict, List, Optional
import streamlit as st
from core.schema import (
    ECOLES_LIST, ECOLES_OPTIONS, SUBJECT_MAP, MATIERES_LIST, clean_cd_orgns,
    RETAC_LIST, get_ecoles_for_retac
)
from core.state import (
    get_global_filters,
    update_global_filter,
    get_teacher_opt_in,
    set_teacher_opt_in,
    get_df_main,
    get_df_moderation
)


def render_sidebar_filters(
    show_retac: bool = True,
    show_ecoles: bool = True,
    show_matieres: bool = True,
    show_enriched: bool = True,
    show_thresholds: bool = False,
    show_teacher_opt_in: bool = False,
    multi_ecoles: bool = False,
    multi_matieres: bool = False,
    available_ecoles: Optional[List[str]] = None,
    available_matieres: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Rend la barre de filtres unifiée et synchronisée dans la barre latérale.
    Retourne l'état actuel des filtres.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("Paramètres et filtres")

    current_filters = get_global_filters()
    selected = {}

    # 0. Filtre RETAC territorial
    active_ecoles_pool = available_ecoles if available_ecoles else ECOLES_LIST
    if show_retac:
        saved_retac = current_filters.get("selected_retac", "Tous")
        idx_retac = RETAC_LIST.index(saved_retac) if saved_retac in RETAC_LIST else 0
        sel_retac = st.sidebar.selectbox(
            "Bassin / RETAC :",
            options=RETAC_LIST,
            index=idx_retac,
            key="sb_retac"
        )
        update_global_filter("selected_retac", sel_retac)
        selected["selected_retac"] = sel_retac
        if sel_retac != "Tous":
            retac_ecoles = set(get_ecoles_for_retac(sel_retac))
            active_ecoles_pool = [e for e in active_ecoles_pool if e in retac_ecoles]

    # 1. Filtre Écoles
    if show_ecoles:
        ecoles_ref = active_ecoles_pool
        if multi_ecoles:
            saved_multi = current_filters.get("selected_ecoles", [])
            valid_default = [e for e in saved_multi if e in ecoles_ref] or ecoles_ref
            sel_ecoles = st.sidebar.multiselect(
                "Établissements / Écoles :",
                options=ecoles_ref,
                default=valid_default,
                key="sb_multi_ecoles"
            )
            update_global_filter("selected_ecoles", sel_ecoles)
            selected["selected_ecoles"] = sel_ecoles
        else:
            options_single = ["Toutes"] + ecoles_ref
            saved_single = current_filters.get("selected_ecole", "Toutes")
            idx = options_single.index(saved_single) if saved_single in options_single else 0
            sel_ecole = st.sidebar.selectbox(
                "Établissement / École :",
                options=options_single,
                index=idx,
                key="sb_single_ecole"
            )
            update_global_filter("selected_ecole", sel_ecole)
            selected["selected_ecole"] = sel_ecole

    # 2. Filtre Matières
    if show_matieres:
        mat_ref = available_matieres if available_matieres else list(SUBJECT_MAP.keys())
        if multi_matieres:
            saved_mat_multi = current_filters.get("selected_matieres", [])
            valid_mat_default = [m for m in saved_mat_multi if m in mat_ref] or mat_ref
            sel_mats = st.sidebar.multiselect(
                "Matières / Disciplines :",
                options=mat_ref,
                default=valid_mat_default,
                key="sb_multi_matieres"
            )
            update_global_filter("selected_matieres", sel_mats)
            selected["selected_matieres"] = sel_mats
        else:
            options_mat_single = ["Toutes"] + mat_ref
            saved_mat_single = current_filters.get("selected_matiere", "Toutes")
            idx_m = options_mat_single.index(saved_mat_single) if saved_mat_single in options_mat_single else 0
            sel_mat = st.sidebar.selectbox(
                "Matière / Discipline :",
                options=options_mat_single,
                index=idx_m,
                key="sb_single_matiere"
            )
            update_global_filter("selected_matiere", sel_mat)
            selected["selected_matiere"] = sel_mat

    # 3. Élèves du régulier seulement (exclure enrichis)
    if show_enriched:
        saved_reg = current_filters.get("filter_enriched", False)
        sel_reg = st.sidebar.checkbox(
            "Élèves du régulier seulement (exclure enrichi)",
            value=saved_reg,
            key="sb_filter_enriched",
            help="Exclut les élèves inscrits à des codes enrichis (51514, 53514, 058404, etc.)"
        )
        update_global_filter("filter_enriched", sel_reg)
        selected["filter_enriched"] = sel_reg

    # 4. Sliders docimologiques What-If
    if show_thresholds:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Seuils d'alerte (What-If)")
        cohen_val = st.sidebar.slider(
            "Seuil d'anomalie |Taille de l'effet| :",
            min_value=0.2, max_value=2.0, value=0.8, step=0.1,
            key="sb_thresh_cohen",
            help="La taille de l'effet (d de Cohen) mesure l'ampleur pratique de l'écart entre la note de l'école et celle du ministère, indépendamment de la taille du groupe. Un seuil de 0.8 correspond à un décalage majeur de notation (~8-10%) ne relevant pas du hasard."
        )
        selected["seuil_cohen"] = cohen_val

        disp_val = st.sidebar.slider(
            "Seuil de compression (Facteur R) :",
            min_value=0.2, max_value=1.5, value=0.6, step=0.1,
            key="sb_thresh_disp",
            help="R < 0.6 indique une dispersion interne fortement comprimée par rapport à l'épreuve."
        )
        selected["seuil_dispersion"] = disp_val

    # 5. Opt-in enseignant avec avertissement éthique
    if show_teacher_opt_in:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Confidentialité (Loi 25)")
        cur_opt_in = get_teacher_opt_in()
        new_opt_in = st.sidebar.checkbox(
            "Afficher les noms d'enseignants",
            value=cur_opt_in,
            key="sb_teacher_opt_in",
            help="Par défaut masqué. L'affichage nominatif engage la responsabilité professionnelle du gestionnaire."
        )
        if new_opt_in != cur_opt_in:
            set_teacher_opt_in(new_opt_in)
        selected["teacher_opt_in"] = new_opt_in
        if new_opt_in:
            st.sidebar.warning("**Avertissement éthique** : Les données nominatives par enseignant doivent être utilisées à des fins d'accompagnement professionnel uniquement.")

    return selected
