# -*- coding: utf-8 -*-
"""
pages/2_Diagnostic_des_epreuves.py - LAD Niveau 2 : Diagnostic des Épreuves & Compétences (MICRO).
Conçu selon Voyer (2011) / Dumaresq (2017) sous la charte officielle Bleu Québec.
Regroupe sans onglets les réussites aux disciplines et aux épreuves uniques,
la détection de la ségrégation intra-école (dispersion des groupes réguliers),
et l'analyse ciblée des groupes outliers d'écrasement ministériel.
"""

import sys
import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from core.schema import (
    clean_cd_orgns, ECOLES_LIST, SUBJECT_MAP, EPREUVES_MAP,
    CODE_TO_MATIERE, CODE_TO_EPREUVE, classify_group_type, ENRICHED_CODES
)
from core.state import get_df_main, get_teacher_opt_in
from core.metrics import wilson_interval, add_confidence_intervals
from core.privacy import filter_small_cells, sanitize_teacher_display
from ui.theme import BLEU_QUEBEC, BLEU_QUEBEC_LIGHT, PALETTE_ACCESSIBLE, inject_quebec_theme
from ui.kpi_cards import render_kpi_card
from ui.charts import (
    plot_rates_bar_with_ci, apply_standard_layout, download_csv_button
)
from ui.action_panel import render_action_panel
from ui.explainers import render_explainer, render_about_data
from core.data_loader import sanitize_df_for_stlite

st.set_page_config(
    page_title="3. Micro : Diagnostic des Épreuves & Classes",
    layout="wide"
)
inject_quebec_theme()

st.title("3. Micro : Diagnostic des Épreuves & Classes")
st.warning("🔬 **Axe d'analyse : Risque d'inégalité intra-muros & de rupture didactique** — Détecter la ségrégation pédagogique interne et les chocs d'évaluation locale face à l'examen standardisé.")

df_main = get_df_main()
if df_main.empty:
    st.info("Veuillez téléverser les données de la cohorte (CHAP060105.csv) depuis la page d'accueil.")
    st.stop()

# -----------------------------------------------------------------------------
# BARRE LATÉRALE : PARAMÈTRES ET FILTRES D'EXCLUSION
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Paramètres d'Analyse MICRO")

min_eleves_micro = st.sidebar.slider(
    "Taille minimale du groupe (Nb. élèves) :",
    min_value=0, max_value=24, value=16, step=1,
    help="Exclut les groupes trop restreints de l'analyse comparative pour éviter le bruit d'échantillonnage."
)

filtrer_enrichis = st.sidebar.checkbox(
    "Exclure les groupes enrichis (058404 / 058402)",
    value=False,
    help="Isole la performance des parcours réguliers pour éviter le biais d'excellence des cohortes enrichies."
)

selected_ecoles = st.sidebar.multiselect(
    "Sélection des établissements :",
    options=ECOLES_LIST,
    default=ECOLES_LIST,
    key="micro_ecoles"
)

allow_teacher = get_teacher_opt_in()

# -----------------------------------------------------------------------------
# FILTRAGE INITIAL ET NORMALISATION
# -----------------------------------------------------------------------------
df_sub = df_main.copy()
if selected_ecoles and "CD_ORGNS" in df_sub.columns:
    clean_sel = set(clean_cd_orgns(e) for e in selected_ecoles)
    df_sub = df_sub[df_sub["CD_ORGNS"].isin(clean_sel)]

if filtrer_enrichis and "CD_PERMN" in df_sub.columns and "CD_COURS_str" in df_sub.columns:
    enrichis_ids = set(df_sub.loc[df_sub["CD_COURS_str"].isin(["058404", "058402", "58404", "58402"]), "CD_PERMN"].unique())
    df_sub = df_sub[~df_sub["CD_PERMN"].isin(enrichis_ids)]

# Type de groupe
if "NO_GROUP_ELEVE" in df_sub.columns:
    df_sub["Type_Groupe"] = df_sub["NO_GROUP_ELEVE"].apply(classify_group_type)
else:
    df_sub["Type_Groupe"] = "Régulier"

# -----------------------------------------------------------------------------
# 1. RÉUSSITE AUX DISCIPLINES ET ÉPREUVES UNIQUES (SUR LA MÊME PAGE SANS ONGLETS)
# -----------------------------------------------------------------------------
st.subheader("1. Évaluation locale vs Épreuve unique : les examens d'école préparent-ils fidèlement au ministère ?")
st.caption("Comparaison directe de la réussite globale (évaluation continue) et des épreuves ministérielles avec intervalles de confiance Wilson (IC 95%).")

# A. Notes globales disciplines
if "Type_Cours" in df_sub.columns:
    mask_mat = (df_sub["Type_Cours"] == "Note globale") & df_sub["CD_COURS_str"].isin(CODE_TO_MATIERE.keys())
else:
    mask_mat = df_sub["CD_COURS_str"].isin(CODE_TO_MATIERE.keys())
df_mat_sub = df_sub[mask_mat].copy()
df_mat_sub["Nom_Matiere"] = df_mat_sub["CD_COURS_str"].map(CODE_TO_MATIERE)

stats_mat = pd.DataFrame()
if not df_mat_sub.empty and "CD_PERMN" in df_mat_sub.columns and "Reussite" in df_mat_sub.columns:
    stats_mat = df_mat_sub.groupby(["CD_ORGNS", "Nom_Matiere"], observed=True).agg(
        Reussite=("Reussite", "mean"),
        Effectif=("CD_PERMN", "nunique"),
        Succes=("Reussite", "sum")
    ).reset_index()
    stats_mat["École"] = stats_mat["CD_ORGNS"].apply(clean_cd_orgns)
    stats_mat["Echecs"] = (stats_mat["Effectif"] - stats_mat["Succes"]).astype(int)
    stats_mat["Taux de réussite (%)"] = (stats_mat["Reussite"] * 100.0).astype(float)
    stats_mat = add_confidence_intervals(stats_mat)

# B. Épreuves uniques
mask_epr = df_sub["CD_COURS_str"].isin(CODE_TO_EPREUVE.keys())
df_epr_sub = df_sub[mask_epr].copy()
df_epr_sub["Nom_Epreuve"] = df_epr_sub["CD_COURS_str"].map(CODE_TO_EPREUVE)

stats_epr = pd.DataFrame()
if not df_epr_sub.empty and "NOTE_MINST_CONVR" in df_epr_sub.columns:
    df_epr_sub["NOTE_MINST_CONVR"] = pd.to_numeric(df_epr_sub["NOTE_MINST_CONVR"], errors="coerce")
    df_epr_val = df_epr_sub.dropna(subset=["NOTE_MINST_CONVR"]).copy()
    df_epr_val["Reussite_Ep"] = df_epr_val["NOTE_MINST_CONVR"] >= 60

    stats_epr = df_epr_val.groupby(["CD_ORGNS", "Nom_Epreuve"], observed=True).agg(
        Reussite=("Reussite_Ep", "mean"),
        Effectif=("CD_PERMN", "nunique"),
        Succes=("Reussite_Ep", "sum")
    ).reset_index()
    stats_epr["École"] = stats_epr["CD_ORGNS"].apply(clean_cd_orgns)
    stats_epr["Echecs"] = (stats_epr["Effectif"] - stats_epr["Succes"]).astype(int)
    stats_epr["Taux de réussite (%)"] = (stats_epr["Reussite"] * 100.0).astype(float)
    stats_epr = add_confidence_intervals(stats_epr)

# Affichage superposé sur la même page
col_bar1, col_bar2 = st.columns(2)

with col_bar1:
    st.markdown("##### A. Réussite aux Disciplines (Évaluation Locale)")
    if not stats_mat.empty:
        stats_mat_vis, _ = filter_small_cells(stats_mat, count_col="Effectif", min_count=5)
        fig_mat = plot_rates_bar_with_ci(
            stats_mat_vis,
            x_col="École", y_col="Taux de réussite (%)", color_col="Nom_Matiere",
            title="Réussite globale par matière et établissement (IC 95%)"
        )
        st.plotly_chart(fig_mat, use_container_width=True)
    else:
        st.info("Données de disciplines non disponibles.")

with col_bar2:
    st.markdown("##### B. Réussite aux Épreuves Uniques (Ministère)")
    if not stats_epr.empty:
        stats_epr_vis, _ = filter_small_cells(stats_epr, count_col="Effectif", min_count=5)
        fig_epr = plot_rates_bar_with_ci(
            stats_epr_vis,
            x_col="École", y_col="Taux de réussite (%)", color_col="Nom_Epreuve",
            title="Réussite aux épreuves uniques par établissement (IC 95%)"
        )
        st.plotly_chart(fig_epr, use_container_width=True)
    else:
        st.info("Données d'épreuves uniques non disponibles.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. DÉTECTION DE LA SÉGRÉGATION INTRA-ÉCOLE (DISPERSION DES GROUPES RÉGULIERS)
# -----------------------------------------------------------------------------
st.subheader("2. Composition des classes : y a-t-il une ségrégation anormale entre groupes réguliers d'une même école ?")
st.markdown("""
**Principe docimologique :** Les groupes **80-85 (EHDAA)** et **90-99 (cas particuliers)** sont **exclus** de cette analyse.
On compare uniquement les taux de réussite des groupes réguliers au sein de chaque établissement.
Un écart-type élevé entre les groupes d'une même école révèle une constitution asymétrique des classes (ségrégation pédagogique interne).
""")

# Exclure les groupes 80 et 90
df_reguliers = df_sub[~df_sub["Type_Groupe"].isin(["EHDAA", "Cas particuliers"])].copy()

if not df_reguliers.empty and "Groupe_Virtuel" in df_reguliers.columns and "Reussite" in df_reguliers.columns:
    df_reguliers["Reussite_Num"] = df_reguliers["Reussite"].astype(int)

    # Calcul des taux par groupe
    grp_stats = df_reguliers.groupby(["CD_ORGNS", "Groupe_Virtuel"], observed=True).agg(
        Taux_Reussite=("Reussite_Num", "mean"),
        Effectif=("CD_PERMN", "nunique")
    ).reset_index()

    # Filtrer par taille minimale
    grp_stats = grp_stats[grp_stats["Effectif"] >= min_eleves_micro].copy()
    grp_stats["Taux_Reussite_Pct"] = grp_stats["Taux_Reussite"] * 100.0

    if not grp_stats.empty and grp_stats["CD_ORGNS"].nunique() > 0:
        # Strip plot / Box plot montrant l'écart entre groupes pour chaque école
        fig_seg = px.box(
            grp_stats,
            x="CD_ORGNS",
            y="Taux_Reussite_Pct",
            points="all",
            title=f"Dispersion des Taux de Réussite entre Groupes Réguliers (Groupes ≥ {min_eleves_micro} élèves)",
            labels={"CD_ORGNS": "Établissement", "Taux_Reussite_Pct": "Taux de Réussite du Groupe (%)"},
            color_discrete_sequence=[BLEU_QUEBEC]
        )
        fig_seg.update_xaxes(type="category", tickangle=45)
        st.plotly_chart(apply_standard_layout(fig_seg, height=420), use_container_width=True)

        # Calcul de l'écart-type inter-groupes par école
        ecole_disper = grp_stats.groupby("CD_ORGNS", observed=True)["Taux_Reussite_Pct"].agg(
            Ecart_Type="std",
            Taux_Min="min",
            Taux_Max="max",
            Nb_Groupes="count"
        ).reset_index()
        ecole_disper["Ecart_Type"] = ecole_disper["Ecart_Type"].fillna(0.0)
        ecole_disper["Ecart_Max_Min"] = (ecole_disper["Taux_Max"] - ecole_disper["Taux_Min"]).fillna(0.0)
        ecole_disper = ecole_disper.sort_values(by="Ecart_Type", ascending=False)

        col_t1, col_t2 = st.columns([1.5, 1.5])
        with col_t1:
            st.markdown("##### Écoles à Forte Hétérogénéité Inter-Groupes :")
            ecoles_alerte = ecole_disper[ecole_disper["Ecart_Type"] > 15.0]
            if not ecoles_alerte.empty:
                st.error(f"**{len(ecoles_alerte)} école(s)** présentent un écart-type inter-groupes > 15% (repère empirique de vigilance), signalant une asymétrie marquée dans la composition ou la notation des classes régulières.")
            else:
                st.success("Bonne homogénéité relative des groupes réguliers au sein des établissements (écart-type ≤ 15%).")
            st.caption("Note : Le seuil de 15% est un repère empirique de gestion pour orienter le forage, non une norme réglementaire ministérielle.")

        with col_t2:
            st.dataframe(sanitize_df_for_stlite(ecole_disper.rename(columns={
                "CD_ORGNS": "École",
                "Ecart_Type": "Écart-Type (σ %)",
                "Ecart_Max_Min": "Écart Max-Min (%)",
                "Nb_Groupes": "Nb Groupes Analysés"
            })), use_container_width=True)
    else:
        st.info(f"Aucun groupe régulier n'atteint l'effectif minimum de {min_eleves_micro} élèves.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 3. ANALYSE RAFFINÉE DE L'ÉCRASEMENT DES NOTES & OUTLIERS DE RATIO
# -----------------------------------------------------------------------------
st.subheader("3. Outliers de sanction : quelles classes profitent d'un écrasement massif ou subissent une pénalité critique ?")
st.markdown("""
**Objectif :** L'écrasement survient lorsque la note à l'épreuve ministérielle convertie ($NMC$) dépasse la note école modérée ($NEM$).
On calcule le ratio d'écrasement par groupe pour isoler les **valeurs extrêmes (Outliers)** :
* **Outliers Supérieurs (Écrasement très élevé) :** Groupes où l'évaluation locale a été excessivement sévère, créant un choc positif à l'épreuve.
* **Outliers Inférieurs (Écrasement très faible / Décote) :** Groupes où la note école a été rabaissée sans bénéficier d'aucun écrasement ministériel.
""")

if "NOTE_MINST_CONVR" in df_sub.columns and "NOTE_ECOLE_MODR" in df_sub.columns and "Groupe_Virtuel" in df_sub.columns:
    df_ecras_in = df_sub.dropna(subset=["NOTE_MINST_CONVR", "NOTE_ECOLE_MODR"]).copy()
    df_ecras_in["NOTE_MINST_CONVR"] = pd.to_numeric(df_ecras_in["NOTE_MINST_CONVR"], errors="coerce")
    df_ecras_in["NOTE_ECOLE_MODR"] = pd.to_numeric(df_ecras_in["NOTE_ECOLE_MODR"], errors="coerce")
    df_ecras_in["Ecrasee"] = df_ecras_in["NOTE_MINST_CONVR"] >= df_ecras_in["NOTE_ECOLE_MODR"]
    df_ecras_in["Discipline"] = df_ecras_in.get("Nom_Matiere", df_ecras_in["CD_COURS_str"]).astype(str)

    grp_ecras = df_ecras_in.groupby(["CD_ORGNS", "Groupe_Virtuel", "Discipline"], observed=True).agg(
        Total_Eleves=("Ecrasee", "count"),
        Nb_Ecrasees=("Ecrasee", "sum"),
        Moy_NMC=("NOTE_MINST_CONVR", "mean"),
        Moy_NEM=("NOTE_ECOLE_MODR", "mean")
    ).reset_index()

    grp_ecras = grp_ecras[grp_ecras["Total_Eleves"] >= min_eleves_micro].copy()
    if not grp_ecras.empty:
        grp_ecras["Ratio_Ecrasement_Pct"] = (grp_ecras["Nb_Ecrasees"] / grp_ecras["Total_Eleves"]) * 100.0

        mu_ecras = grp_ecras["Ratio_Ecrasement_Pct"].mean()
        sigma_ecras = grp_ecras["Ratio_Ecrasement_Pct"].std()
        if pd.isna(sigma_ecras) or sigma_ecras == 0:
            sigma_ecras = 10.0

        grp_ecras["Score_Z"] = (grp_ecras["Ratio_Ecrasement_Pct"] - mu_ecras) / sigma_ecras

        # Détection des Outliers (seuil 1.5 sigma)
        outliers_haut = grp_ecras[grp_ecras["Score_Z"] > 1.5].sort_values(by="Ratio_Ecrasement_Pct", ascending=False)
        outliers_bas = grp_ecras[grp_ecras["Score_Z"] < -1.5].sort_values(by="Ratio_Ecrasement_Pct", ascending=True)

        col_ec1, col_ec2 = st.columns(2)
        with col_ec1:
            st.markdown(f"##### Pratiques Sévères / Surperformance Épreuve (+1.5σ) : {len(outliers_haut)} groupe(s)")
            if not outliers_haut.empty:
                st.dataframe(sanitize_df_for_stlite(outliers_haut[["CD_ORGNS", "Groupe_Virtuel", "Discipline", "Total_Eleves", "Ratio_Ecrasement_Pct", "Moy_NEM", "Moy_NMC"]].rename(columns={
                    "CD_ORGNS": "École", "Groupe_Virtuel": "Groupe", "Total_Eleves": "N", "Ratio_Ecrasement_Pct": "% Écrasées", "Moy_NEM": "Moy. NEM", "Moy_NMC": "Moy. NMC"
                })), use_container_width=True)
            else:
                st.info("Aucun groupe en surperformance extrême.")

        with col_ec2:
            st.markdown(f"##### Pratiques Indulgentes / Décote Sévère (-1.5σ) : {len(outliers_bas)} groupe(s)")
            if not outliers_bas.empty:
                st.dataframe(sanitize_df_for_stlite(outliers_bas[["CD_ORGNS", "Groupe_Virtuel", "Discipline", "Total_Eleves", "Ratio_Ecrasement_Pct", "Moy_NEM", "Moy_NMC"]].rename(columns={
                    "CD_ORGNS": "École", "Groupe_Virtuel": "Groupe", "Total_Eleves": "N", "Ratio_Ecrasement_Pct": "% Écrasées", "Moy_NEM": "Moy. NEM", "Moy_NMC": "Moy. NMC"
                })), use_container_width=True)
            else:
                st.info("Aucun groupe en décote extrême.")

        download_csv_button(grp_ecras, "outliers_ecrasement_groupes.csv", "Exporter les ratios d'écrasement par groupe (CSV)")
else:
    st.info("Données NOTE_MINST_CONVR et NOTE_ECOLE_MODR requises pour analyser les outliers d'écrasement.")

# -----------------------------------------------------------------------------
# 4. PANNEAU D'ACTION DYNAMIQUE (LAD P2)
# -----------------------------------------------------------------------------
st.markdown("---")
render_action_panel(
    question="Quelles classes présentent une ségrégation interne anormale ou un décalage critique d'écrasement face aux épreuves ?",
    constat_dynamique=(
        f"L'analyse des groupes réguliers (seuil N ≥ {min_eleves_micro}) permet d'isoler les établissements où l'écart inter-groupes dépasse la norme, "
        "ainsi que les groupes dont l'évaluation continue s'écarte radicalement des exigences ministérielles."
    ),
    pistes=[
        "**Rééquilibrage de la composition des groupes :** Pour les écoles où l'écart-type entre classes régulières dépasse 15%, réviser les critères de répartition des élèves à la rentrée scolaire pour éviter la ségrégation pédagogique.",
        "**Étalonnage des groupes outliers d'écrasement :** Les groupes où 100% des notes sont écrasées doivent faire l'objet d'un retour d'expérience avec l'enseignant afin d'adoucir la notation continue en cours d'année.",
        "**Soutien aux groupes à décote sévère :** Offrir un accompagnement didactique aux enseignants dont les groupes subissent un effondrement des notes à l'épreuve unique."
    ],
    context_tag=f"Seuil N ≥ {min_eleves_micro}"
)

render_explainer("ecrasement")
render_about_data(
    source_name="Fichier cohorte CHAP060105.csv",
    limits=[
        "Les groupes EHDAA (80-85) et cas particuliers (90-99) sont exclus de l'analyse de ségrégation pour isoler les dynamiques des classes ordinaires.",
        "L'écrasement des notes est une mesure de sanction ministérielle appliquée à l'avantage de l'élève ($NMC \\ge NEM$)."
    ]
)
