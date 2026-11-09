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
from core.state import get_df_main, get_df_sexe, get_df_pi, get_teacher_opt_in
from core.privacy import sanitize_teacher_display, filter_small_cells
from ui.theme import BLEU_QUEBEC, BLEU_QUEBEC_LIGHT, inject_quebec_theme
from ui.kpi_cards import render_kpi_card
from ui.charts import download_csv_button
from ui.action_panel import render_action_panel
from ui.explainers import render_about_data
from ui.filters import render_sidebar_filters
from core.data_loader import sanitize_df_for_stlite

st.set_page_config(page_title="4. Prescription : Triage GPS & Diplomation", layout="wide")
inject_quebec_theme()

st.title("4. Prescription : Triage GPS & Diplomation")
st.markdown("**Outil de suivi individualisé GPS (Guide Pédagogique Stratégique)** — Triage prescriptif des élèves pour l'école d'été et la diplomation rapide.")

df_main = get_df_main()
if df_main.empty:
    st.info("Veuillez importer les données de la cohorte (CHAP060105.csv) depuis la page d'accueil pour utiliser le module de triage.")
    st.stop()

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
# 1. PRÉPARATION DES DONNÉES ET KPIS DE TRIAGE
# -----------------------------------------------------------------------------
df_sub = df_main.copy()
if selected_retac and selected_retac != "Tous":
    from core.schema import get_ecoles_for_retac
    ecoles_retac = set(get_ecoles_for_retac(selected_retac))
    if "CD_ORGNS" in df_sub.columns:
        df_sub = df_sub[df_sub["CD_ORGNS"].isin(ecoles_retac)]

if selected_ecoles and "CD_ORGNS" in df_sub.columns:
    clean_sel = set(clean_cd_orgns(e) for e in selected_ecoles)
    df_sub = df_sub[df_sub["CD_ORGNS"].isin(clean_sel)]

if filter_enriched and "CD_PERMN" in df_sub.columns:
    from core.schema import ENRICHED_CODES
    if "CD_COURS_str" in df_sub.columns:
        enr_ids = set(df_sub.loc[df_sub["CD_COURS_str"].isin(ENRICHED_CODES), "CD_PERMN"].unique())
        df_sub = df_sub[~df_sub["CD_PERMN"].isin(enr_ids)]

# Filtrer sur les matières cibles officielles
df_sub = df_sub[df_sub["CD_COURS_str"].isin(CODE_TO_MATIERE_COURT.keys())].copy()
df_sub["Matiere_Nom"] = df_sub["CD_COURS_str"].map(CODE_TO_MATIERE_COURT)

if selected_matiere and selected_matiere != "Toutes":
    df_sub = df_sub[df_sub["Matiere_Nom"] == selected_matiere]

# Sliders What-If de ciblage
st.sidebar.markdown("---")
st.sidebar.subheader("Ciblage Docimologique (What-If)")
plage_notes = st.sidebar.slider(
    "Plage de note finale des élèves ciblés (%) :",
    min_value=0, max_value=59, value=(50, 59),
    help="Sélectionnez les notes frontières (ex: 55-59% pour identifier les candidats idéaux à un examen de reprise)."
)
seuil_bas, seuil_haut = plage_notes

# Identification des élèves en échec dans la plage
mask_notes = (df_sub["RESLT_FINAL"] >= seuil_bas) & (df_sub["RESLT_FINAL"] <= seuil_haut)
df_echecs_plage = df_sub[mask_notes].copy()

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
# 2. TABLEAU DE TRIAGE PRIORISÉ ET PRESCRIPTIONS RECOMMANDÉES
# -----------------------------------------------------------------------------
st.subheader(f"Tableau de Triage et Prescriptions ({nb_total_eleves_echec} élèves ciblés)")

if not df_echecs_plage.empty:
    def prescrire_action(row):
        note = row.get("RESLT_FINAL", 0)
        nb_ech = row.get("Nb_Echecs_Total", 1)
        if note >= 55 and nb_ech == 1:
            return "Priorité 1 : Examen de reprise / Tutorat intensif court"
        elif note >= 50 and nb_ech == 1:
            return "Priorité 2 : Cours d'été régulier (1 matière)"
        elif nb_ech >= 2:
            return "Priorité 3 : Plan concerté multi-matières & arbitrage école d'été"
        else:
            return "Soutien standard"

    # Synthèse par élève et par matière
    df_triage = df_echecs_plage[["CD_PERMN", "CD_ORGNS", "Matiere_Nom", "RESLT_FINAL", "Groupe_Virtuel"]].copy()
    echec_counts = df_echecs_plage.groupby("CD_PERMN")["Matiere_Nom"].nunique()
    df_triage["Nb_Echecs_Total"] = df_triage["CD_PERMN"].map(echec_counts)
    df_triage["Prescription"] = df_triage.apply(prescrire_action, axis=1)

    # Croisement avec Sexe si disponible
    df_sexe_loaded = get_df_sexe()
    if not df_sexe_loaded.empty and "CD_PERMN" in df_sexe_loaded.columns and "SEXE" in df_sexe_loaded.columns:
        df_triage = pd.merge(df_triage, df_sexe_loaded[["CD_PERMN", "SEXE"]], on="CD_PERMN", how="left")
        df_triage["SEXE"] = df_triage["SEXE"].fillna("Inconnu")

    # Croisement avec Plan d'intervention si disponible
    df_pi_loaded = get_df_pi()
    if not df_pi_loaded.empty and "CD_PERMN" in df_pi_loaded.columns:
        pi_col = "PI" if "PI" in df_pi_loaded.columns else df_pi_loaded.columns[1]
        df_triage = pd.merge(df_triage, df_pi_loaded[["CD_PERMN", pi_col]], on="CD_PERMN", how="left")
        df_triage["PI / EHDAA"] = np.where(df_triage[pi_col].notna() & (df_triage[pi_col].astype(str) != ""), "Oui", "Non")
        if pi_col != "PI / EHDAA" and pi_col in df_triage.columns:
            df_triage = df_triage.drop(columns=[pi_col])

    if not allow_teacher and "Groupe_Virtuel" in df_triage.columns:
        df_triage["Groupe_Virtuel"] = df_triage["Groupe_Virtuel"].apply(lambda s: sanitize_teacher_display(s, allow_teacher))

    # Masquer l'identifiant nominatif si effectif trop restreint
    rename_cols = {
        "CD_PERMN": "Code Permanent Élève",
        "CD_ORGNS": "École",
        "Matiere_Nom": "Matière en Échec",
        "RESLT_FINAL": "Note Finale (%)",
        "Nb_Echecs_Total": "Nb Échecs Actifs",
        "Groupe_Virtuel": "Groupe",
        "Prescription": "Recommandation d'Intervention"
    }
    if "SEXE" in df_triage.columns:
        rename_cols["SEXE"] = "Sexe"
    if "PI / EHDAA" in df_triage.columns:
        rename_cols["PI / EHDAA"] = "Plan d'intervention (PI)"

    df_triage_disp = df_triage.rename(columns=rename_cols).sort_values(by=["Nb Échecs Actifs", "Note Finale (%)"], ascending=[False, False])

    st.dataframe(sanitize_df_for_stlite(df_triage_disp.reset_index(drop=True)), use_container_width=True)
    download_csv_button(df_triage_disp, "triage_prescription_ete.csv", "Exporter la liste de triage (CSV)")
else:
    st.success("Aucun élève ne correspond aux critères d'échec dans cette plage de notes.")

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

