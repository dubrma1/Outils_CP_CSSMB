# -*- coding: utf-8 -*-
"""
pages/4_Triage_et_Prescription.py - LAD Niveau 4 : Triage & Prescription GPS (École d'été).
Outil de suivi individualisé GPS (Guide Pédagogique Stratégique) destiné aux coordonnateurs d'école d'été
pour prioriser les interventions (examen de reprise 55-59%, cours régulier 50-54%, plan multidisciplinaire).
"""

import sys
import os
import streamlit as st
import pandas as pd
import numpy as np

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from core.schema import clean_cd_orgns, ECOLES_LIST, CODE_TO_MATIERE_COURT
from core.state import (
    get_df_main, get_df_primaire, set_df_primaire,
    get_df_sexe, get_df_pi, get_teacher_opt_in
)
from core.metrics import assigner_typologie_janosz
from core.privacy import (
    sanitize_teacher_display, filter_small_cells,
    get_privacy_warning_message, MIN_CELL_COUNT
)
from ui.theme import BLEU_QUEBEC, BLEU_QUEBEC_LIGHT, inject_quebec_theme
from ui.kpi_cards import render_kpi_card
from ui.charts import download_csv_button, plot_janosz_bars, plot_janosz_matrix_2d
from ui.action_panel import render_action_panel
from ui.explainers import render_about_data
from ui.filters import render_sidebar_filters
from core.data_loader import sanitize_df_for_stlite, load_csv_robust

st.set_page_config(page_title="4. Prescription : Triage GPS & Diplomation", layout="wide")
inject_quebec_theme()

st.title("4. Prescription : Triage GPS & Diplomation")
st.markdown("**Outil de suivi individualisé GPS (Guide Pédagogique Stratégique)** — Triage prescriptif des élèves selon les typologies de risque (Janosz / MEQ) pour l'école d'été et la diplomation rapide.")

df_main = get_df_main()
if df_main.empty:
    st.info("Veuillez importer les données de la cohorte (CHAP060105.csv) depuis la page d'accueil pour utiliser le module de triage.")
    st.stop()

# Téléversement d'appoint des données primaires si non chargées à l'accueil
df_prim_loaded = get_df_primaire()
if df_prim_loaded.empty and "PCT_ABSENCE" not in df_main.columns:
    with st.expander("Enrichir avec le fichier Données primaires Élèves & Assiduité (CSV)", expanded=False):
        up_prim = st.file_uploader("Données primaires Élèves & Assiduité (CSV)", type=["csv"], key="up_prim_p4")
        if up_prim:
            df_p_load = load_csv_robust(up_prim)
            if not df_p_load.empty:
                set_df_primaire(df_p_load)
                st.success("Données primaires d'assiduité et de profil fusionnées avec succès !")
                st.rerun()

filters = render_sidebar_filters(
    show_retac=True,
    show_ecoles=True,
    show_matieres=True,
    show_enriched=True,
    show_teacher_opt_in=True,
    multi_ecoles=True
)

selected_retac = filters.get("selected_retac", "Tous")
selected_matiere = filters.get("selected_matiere", "Toutes")

selected_ecoles = filters.get("selected_ecoles", ECOLES_LIST)
filter_enriched = filters.get("filter_enriched", False)
allow_teacher = get_teacher_opt_in()

# -----------------------------------------------------------------------------
# NOUVEAUX FILTRES LATÉRAUX INTERACTIFS (JANOSZ, ADAPTATION, PARCOURS, SEXE, DES)
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Filtres de Profil & Triage GRS")

sel_profil_janosz = st.sidebar.selectbox(
    "Profil de risque (Janosz / MELS) :",
    options=[
        "Tous",
        "Discret (Frontière)",
        "Inadapté (Multi-risques)",
        "Désengagé",
        "Sous-performant",
        "Non à risque"
    ],
    index=0,
    key="sb_p4_janosz"
)

sel_statut_adapt = st.sidebar.selectbox(
    "Statut Adaptation scolaire :",
    options=["Tous", "Élèves avec PI / EHDAA", "Élèves ordinaires"],
    index=0,
    key="sb_p4_adapt"
)

sel_type_org = st.sidebar.selectbox(
    "Type d'organisation / Parcours :",
    options=[
        "Tous",
        "Régulier",
        "Projets particuliers (PEI/Concentration)",
        "Concomitance / Pré-DEP"
    ],
    index=0,
    key="sb_p4_parcours"
)

sel_sexe = st.sidebar.selectbox(
    "Sexe :",
    options=["Tous", "Masculin", "Féminin"],
    index=0,
    key="sb_p4_sexe"
)

sel_finissants_tension = st.sidebar.checkbox(
    "Finissants sous tension (DES immédiat)",
    value=False,
    key="sb_p4_finissants_des",
    help="Isole les élèves cumulant ≥ 48 crédits (NB_CREDITS_CUMUL >= 48) et à qui il ne manque que 1 ou 2 cours de sanction."
)

# Sliders What-If de ciblage
st.sidebar.markdown("---")
st.sidebar.subheader("Ciblage Docimologique (What-If)")
default_max_note = 100 if sel_profil_janosz in ("Désengagé", "Non à risque") else 59
default_min_note = 0 if sel_profil_janosz in ("Sous-performant", "Inadapté (Multi-risques)", "Désengagé", "Non à risque") else 50
plage_notes = st.sidebar.slider(
    "Plage de note finale des élèves ciblés (%) :",
    min_value=0, max_value=100, value=(default_min_note, default_max_note),
    help="Sélectionnez les notes cibles (ex: 55-59% pour examen de reprise, 0-59% pour l'ensemble des échecs, ou jusqu'à 100% pour suivre les Désengagés)."
)
seuil_bas, seuil_haut = plage_notes

# -----------------------------------------------------------------------------
# 1. PRÉPARATION DES DONNÉES ET KPIS DE TRIAGE
# -----------------------------------------------------------------------------
df_sub = df_main
if "Profil_Janosz" not in df_sub.columns:
    df_sub = assigner_typologie_janosz(df_sub.copy())

mask_base = pd.Series(True, index=df_sub.index)
if selected_retac and selected_retac != "Tous":
    from core.schema import get_ecoles_for_retac
    ecoles_retac = set(get_ecoles_for_retac(selected_retac))
    if "CD_ORGNS" in df_sub.columns:
        mask_base &= df_sub["CD_ORGNS"].isin(ecoles_retac)

if selected_ecoles and "CD_ORGNS" in df_sub.columns:
    clean_sel = set(clean_cd_orgns(e) for e in selected_ecoles)
    mask_base &= df_sub["CD_ORGNS"].isin(clean_sel)

if filter_enriched and "CD_PERMN" in df_sub.columns:
    from core.schema import ENRICHED_CODES
    if "CD_COURS_str" in df_sub.columns:
        enr_ids = set(df_sub.loc[df_sub["CD_COURS_str"].isin(ENRICHED_CODES), "CD_PERMN"].unique())
        mask_base &= (~df_sub["CD_PERMN"].isin(enr_ids))

# Filtrer sur les matières cibles officielles
if "CD_COURS_str" in df_sub.columns:
    mask_base &= df_sub["CD_COURS_str"].isin(CODE_TO_MATIERE_COURT.keys())

df_sub = df_sub.loc[mask_base].copy()
df_sub["Matiere_Nom"] = df_sub["CD_COURS_str"].map(CODE_TO_MATIERE_COURT)
df_sub["RESLT_FINAL"] = pd.to_numeric(df_sub["RESLT_FINAL"], errors="coerce")

# Calcul du nombre total d'échecs actifs aux matières à sanction par élève (avant filtre d'une seule matière)
echecs_all_sanction = df_sub[df_sub["RESLT_FINAL"] < 60.0].groupby("CD_PERMN")["Matiere_Nom"].nunique()
df_sub["Nb_Echecs_Total"] = df_sub["CD_PERMN"].map(echecs_all_sanction).fillna(0).astype("int16")

if selected_matiere and selected_matiere != "Toutes":
    m_court = CODE_TO_MATIERE_COURT.get(selected_matiere, selected_matiere)
    for k, v in CODE_TO_MATIERE_COURT.items():
        if k in str(selected_matiere) or v in str(selected_matiere):
            m_court = v
            break
    df_sub = df_sub[df_sub["Matiere_Nom"] == m_court]

# Croisement avec Sexe ou PI legacy si chargés séparément sans df_primaire
if "SEXE" not in df_sub.columns:
    df_sexe_loaded = get_df_sexe()
    if not df_sexe_loaded.empty and "CD_PERMN" in df_sexe_loaded.columns and "SEXE" in df_sexe_loaded.columns:
        df_sub = pd.merge(df_sub, df_sexe_loaded[["CD_PERMN", "SEXE"]].drop_duplicates("CD_PERMN"), on="CD_PERMN", how="left")

if "FLAG_PI" not in df_sub.columns:
    df_pi_loaded = get_df_pi()
    if not df_pi_loaded.empty and "CD_PERMN" in df_pi_loaded.columns:
        pi_col = "PI" if "PI" in df_pi_loaded.columns else df_pi_loaded.columns[1]
        pi_ids = set(df_pi_loaded.loc[df_pi_loaded[pi_col].notna() & (df_pi_loaded[pi_col].astype(str).str.strip() != ""), "CD_PERMN"])
        df_sub["FLAG_PI"] = np.where(df_sub["CD_PERMN"].isin(pi_ids), 1, 0).astype("int32")

# Application des 5 nouveaux filtres latéraux
mask_filt = pd.Series(True, index=df_sub.index)

# 1. Filtre Profil de risque (Janosz / MELS)
if sel_profil_janosz != "Tous" and "Profil_Janosz" in df_sub.columns:
    mask_filt &= (df_sub["Profil_Janosz"].astype(str) == sel_profil_janosz)

# 2. Filtre Statut Adaptation scolaire
if sel_statut_adapt != "Tous":
    has_pi = (pd.to_numeric(df_sub["FLAG_PI"], errors="coerce").fillna(0) == 1) if "FLAG_PI" in df_sub.columns else pd.Series(False, index=df_sub.index)
    has_ehdaa = (~df_sub["CD_EHDAA"].astype(str).str.strip().isin(["", "nan", "None", "Ordinaire"])) if "CD_EHDAA" in df_sub.columns else pd.Series(False, index=df_sub.index)
    is_adapt = has_pi | has_ehdaa
    if sel_statut_adapt == "Élèves avec PI / EHDAA":
        mask_filt &= is_adapt
    elif sel_statut_adapt == "Élèves ordinaires":
        mask_filt &= (~is_adapt)

# 3. Filtre Type d'organisation / Parcours
if sel_type_org != "Tous":
    col_parc = "TYPE_PARCOURS" if "TYPE_PARCOURS" in df_sub.columns else ("Parcours" if "Parcours" in df_sub.columns else None)
    if col_parc is not None:
        p_str = df_sub[col_parc].astype(str).str.strip()
        if sel_type_org == "Régulier":
            mask_filt &= (p_str == "Régulier")
        elif sel_type_org == "Projets particuliers (PEI/Concentration)":
            mask_filt &= p_str.isin(["PEI", "Sport-études", "Concentration", "Enrichi"])
        elif sel_type_org == "Concomitance / Pré-DEP":
            mask_filt &= p_str.isin(["Concomitance", "FPT/FMS", "Pré-DEP"])

# 4. Filtre Sexe
if sel_sexe != "Tous" and "SEXE" in df_sub.columns:
    s_target = "M" if sel_sexe == "Masculin" else "F"
    mask_filt &= (df_sub["SEXE"].astype(str).str.upper().str.strip() == s_target)

# 5. Case à cocher Finissants sous tension (DES immédiat : >= 48 crédits et 1 ou 2 cours de sanction manquants)
if sel_finissants_tension:
    cred_s = pd.to_numeric(df_sub["NB_CREDITS_CUMUL"], errors="coerce").fillna(0) if "NB_CREDITS_CUMUL" in df_sub.columns else pd.Series(48, index=df_sub.index)
    mask_filt &= (cred_s >= 48) & (df_sub["Nb_Echecs_Total"] >= 1) & (df_sub["Nb_Echecs_Total"] <= 2)

# Filtre de plage de notes
mask_notes = (df_sub["RESLT_FINAL"] >= seuil_bas) & (df_sub["RESLT_FINAL"] <= seuil_haut)
df_echecs_plage = df_sub.loc[mask_filt & mask_notes].copy()

# Calcul des profils d'échecs
eleves_echecs = df_echecs_plage.groupby("CD_PERMN")["Matiere_Nom"].apply(set)
nb_total_eleves_echec = len(eleves_echecs)

def count_mat_4e(s):
    return len(s.intersection({"Histoire 4", "Science ST", "Science ATS", "Math CST", "Math SN", "Math TS"}))

def is_critique_4e_5e(s):
    return ("Français 5" in s) and (count_mat_4e(s) >= 1)

nb_simple = sum(eleves_echecs.apply(lambda s: len(s) == 1))
nb_multiple = sum(eleves_echecs.apply(lambda s: len(s) >= 2))
nb_critique_diplomation = sum(eleves_echecs.apply(is_critique_4e_5e))

c1, c2, c3 = st.columns(3)
with c1:
    render_kpi_card(
        title="Échecs Simples (1 matière)",
        value=nb_simple,
        status="warning" if nb_simple > 0 else "neutral",
        n=nb_total_eleves_echec,
        subtitle=f"Notes entre {seuil_bas}% et {seuil_haut}%",
        help_text="Candidats hautement prioritaires pour une diplomation rapide via l'école d'été."
    )

with c2:
    render_kpi_card(
        title="Échecs Multiples (≥ 2 matières)",
        value=nb_multiple,
        status="danger" if nb_multiple > 10 else "warning",
        n=nb_total_eleves_echec,
        subtitle="Cumul de vulnérabilités didactiques",
        help_text="Élèves nécessitant un arbitrage de parcours ou un horaire d'été double."
    )

with c3:
    render_kpi_card(
        title="Risque Diplomation (Français 5 + 4e)",
        value=nb_critique_diplomation,
        status="danger" if nb_critique_diplomation > 0 else "success",
        n=nb_total_eleves_echec,
        subtitle="Blocage de diplomation immédiate",
        help_text="Élèves en 5e secondaire freinés par une matière de 4e non sanctionnée."
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 1B. VISUALISATION DE LA MATRICE DE JANOSZ (PROFIL DE RISQUE & EFFECTIFS)
# -----------------------------------------------------------------------------
st.subheader("Matrice de Janosz (Profils de risque MEQ) & Nombre d'élèves par catégorie")
st.caption(
    "Répartition des élèves selon le modèle de dépistage reconnu par le MEQ (Janosz / Potvin) croisant le rendement "
    "aux matières à sanction et l'engagement comportemental (assiduité, retards, signalements)."
)

# Source pour la vue d'ensemble de la matrice de Janosz (cohorte filtrée par école/matière/sexe/adaptation)
df_janosz_source = df_sub.loc[mask_filt] if not df_sub.loc[mask_filt].empty else df_sub
if not df_janosz_source.empty and "Profil_Janosz" in df_janosz_source.columns:
    # 1. Matrice 2D de Janosz pleine largeur pour lisibilité maximale
    fig_j_mat = plot_janosz_matrix_2d(
        df_janosz_source,
        title="Matrice 2D de Janosz (4 Profils à Risque — Effectifs & Prescriptions)",
        height=560
    )
    st.plotly_chart(fig_j_mat, use_container_width=True)

    # 2. Diagramme à bandes placé en dessous
    st.markdown("##### Effectifs détaillés par catégorie de Janosz (MEQ)")
    col_chk, _ = st.columns([1.5, 2.5])
    with col_chk:
        incl_non_risque = st.checkbox(
            "Inclure la catégorie 'Non à risque' dans l'histogramme",
            value=False,
            key="chk_janosz_non_risque_p4"
        )
    fig_j_bar = plot_janosz_bars(
        df_janosz_source,
        include_non_risque=incl_non_risque,
        title="Nombre d'élèves uniques par catégorie de Janosz",
        height=380
    )
    st.plotly_chart(fig_j_bar, use_container_width=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. MATRICE DE TRIAGE GPS ENRICHIE ET PRESCRIPTIONS RECOMMANDÉES
# -----------------------------------------------------------------------------
st.subheader(f"Matrice de Triage GPS Enrichie ({nb_total_eleves_echec} élèves ciblés)")

if not df_echecs_plage.empty:
    def prescrire_action_gps(row):
        note = float(row.get("RESLT_FINAL", 0) or 0)
        nb_ech = int(row.get("Nb_Echecs_Total", 1) or 1)
        profil = str(row.get("Profil_Janosz", "")).strip()
        pct_abs = float(row.get("PCT_ABSENCE", 0) or 0)

        if profil == "Désengagé" or (pct_abs >= 15.0 and note >= 60.0):
            return "Priorité 4 : Suivi d'assiduité / Mentorat de type Check & Connect"
        elif profil == "Inadapté (Multi-risques)" or nb_ech >= 2:
            return "Priorité 3 : Plan concerté multidiscipline & aménagement organisationnel (art. 222/concomitance)"
        elif (55.0 <= note <= 59.9) or profil == "Discret (Frontière)":
            if 50.0 <= note < 55.0:
                return "Priorité 2 : Cours d'été intensif (1 matière)"
            return "Priorité 1 : Examen de reprise seul / Tutorat court"
        elif (50.0 <= note < 55.0) or profil == "Sous-performant":
            return "Priorité 2 : Cours d'été intensif (1 matière)"
        else:
            return "Priorité 2 : Cours d'été intensif (1 matière)"

    # Préparation vectorisée des colonnes de la matrice de triage GPS enrichie
    df_triage = df_echecs_plage.copy()
    df_triage["Sexe"] = df_triage["SEXE"].astype(str).replace(["nan", "None", ""], "N/D") if "SEXE" in df_triage.columns else "N/D"
    df_triage["Âge"] = pd.to_numeric(df_triage["AGE_30SEPT"], errors="coerce").fillna(16).astype("int16") if "AGE_30SEPT" in df_triage.columns else 16
    df_triage["% Absence"] = pd.to_numeric(df_triage["PCT_ABSENCE"], errors="coerce").fillna(0.0).round(1).astype("float32") if "PCT_ABSENCE" in df_triage.columns else np.float32(0.0)
    df_triage["Retards"] = pd.to_numeric(df_triage["NB_RETARDS"], errors="coerce").fillna(0).astype("int16") if "NB_RETARDS" in df_triage.columns else 0
    df_triage["Profil Risque"] = df_triage["Profil_Janosz"].astype(str) if "Profil_Janosz" in df_triage.columns else "Non classifié"
    if "TYPE_PARCOURS" in df_triage.columns:
        df_triage["Type Parcours"] = df_triage["TYPE_PARCOURS"].astype(str).replace(["nan", "None", ""], "Régulier")
    elif "Parcours" in df_triage.columns:
        df_triage["Type Parcours"] = df_triage["Parcours"].astype(str)
    else:
        df_triage["Type Parcours"] = "Régulier"

    df_triage["Recommandation"] = df_triage.apply(prescrire_action_gps, axis=1)

    if not allow_teacher and "Groupe_Virtuel" in df_triage.columns:
        df_triage["Groupe_Virtuel"] = df_triage["Groupe_Virtuel"].apply(lambda s: sanitize_teacher_display(s, allow_teacher))

    cols_order = [
        "CD_PERMN", "CD_ORGNS", "Sexe", "Âge", "Type Parcours", "Profil Risque",
        "Matiere_Nom", "RESLT_FINAL", "Nb_Echecs_Total", "% Absence", "Retards",
        "NB_CREDITS_CUMUL", "Groupe_Virtuel", "Recommandation"
    ]
    cols_present = [c for c in cols_order if c in df_triage.columns]
    rename_cols = {
        "CD_PERMN": "Code Permanent Élève",
        "CD_ORGNS": "École",
        "Matiere_Nom": "Matière Ciblée",
        "RESLT_FINAL": "Note Finale (%)",
        "Nb_Echecs_Total": "Nb Échecs Actifs",
        "NB_CREDITS_CUMUL": "Crédits Cumulés",
        "Groupe_Virtuel": "Groupe"
    }

    df_triage_disp = (
        df_triage[cols_present]
        .rename(columns=rename_cols)
        .sort_values(by=["Nb Échecs Actifs", "Note Finale (%)"], ascending=[False, False])
    )

    st.dataframe(sanitize_df_for_stlite(df_triage_disp.reset_index(drop=True)), use_container_width=True)

    # Export CSV conforme Loi 25 : suppression automatique des petites cellules (N < 5 élèves par École)
    ecole_student_counts = df_triage_disp.groupby("École", observed=True)["Code Permanent Élève"].nunique()
    small_ecoles = set(ecole_student_counts[ecole_student_counts < MIN_CELL_COUNT].index)
    suppressed_cells_count = len(small_ecoles)
    df_export_loi25 = df_triage_disp[~df_triage_disp["École"].isin(small_ecoles)].copy()

    if suppressed_cells_count > 0:
        st.caption(get_privacy_warning_message(suppressed_cells_count, MIN_CELL_COUNT))

    download_csv_button(
        df_export_loi25,
        "triage_prescription_ete_loi25.csv",
        "Exporter la liste filtrée conforme Loi 25 (CSV - cellules N ≥ 5)"
    )
else:
    st.success("Aucun élève ne correspond aux critères de filtrage et de plage de notes sélectionnés.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 3. PANNEAU D'ACTION DYNAMIQUE (LAD P2)
# -----------------------------------------------------------------------------
constat_triage = (
    f"{nb_total_eleves_echec} élève(s) sont ciblés dans la plage de note {seuil_bas}% à {seuil_haut}%. "
    f"Parmi eux, {nb_simple} ont un échec unique ({nb_simple / nb_total_eleves_echec * 100:.1f}%), représentant le plus fort potentiel d'élévation rapide du taux de diplomation."
) if nb_total_eleves_echec > 0 else "Aucun élève ciblé."

pistes_triage = [
    "**Recrutement ciblé pour l'école d'été :** Contacter en priorité les parents des élèves à 55-59% ayant un échec unique pour garantir leur inscription immédiate à l'examen de reprise.",
    "**Arbitrage pédagogique des échecs multiples :** Pour les élèves ayant 2 échecs de 4e (ex: Math + Histoire), évaluer quelle matière est la plus bloquante pour l'accès aux cours de 5e secondaire.",
    "**Harmonisation avec le service d'été :** Transmettre aux enseignants de cours d'été les résultats précis aux compétences pour focaliser la révision sur les savoirs essentiels déficitaires."
]

render_action_panel(
    question="Comment optimiser l'offre de cours et d'examens d'été pour maximiser les diplômés dès la session d'août ?",
    constat_dynamique=constat_triage,
    pistes=pistes_triage,
    context_tag=f"Plage {seuil_bas}-{seuil_haut}%"
)

render_about_data(
    source_name="Fichier de cohorte ministérielle CHAP060105.csv",
    limits=[
        "Le statut de diplomation final dépend de l'ensemble des unités accumulées (54 crédits dont 20 de 5e sec.).",
        "L'export des données nominatives d'élèves est restreint aux coordonnateurs autorisés dans le respect de la Loi 25."
    ]
)

