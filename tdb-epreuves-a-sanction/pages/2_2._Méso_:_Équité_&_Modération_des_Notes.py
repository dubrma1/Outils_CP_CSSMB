# -*- coding: utf-8 -*-
"""
pages/3_Moderation.py - LAD Niveau 3 : Modération des Notes-Écoles (Tableau de bord MÉSO).
Conçu selon Voyer (2011) / Dumaresq (2017) sous la charte officielle Bleu Québec.
Regroupe les 3 représentations NEB vs NMC (brut, OLS résiduels, compression),
la matrice 4 quadrants, et les comparaisons d'anomalies par matière, école et typologie de groupe.
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
    clean_cd_orgns, ECOLES_LIST, SUBJECT_MAP, classify_group_type
)
from core.state import get_df_moderation, set_df_moderation, get_teacher_opt_in
from core.data_loader import clean_moderation_df, load_csv_robust, sanitize_df_for_stlite
from core.metrics import (
    classify_moderation_anomaly, compute_ols_regression, compute_quadrants
)
from core.privacy import filter_small_cells, sanitize_teacher_display
from ui.theme import (
    BLEU_QUEBEC, BLEU_QUEBEC_LIGHT, PALETTE_ACCESSIBLE,
    PRIMARY_QUEBEC, SECONDARY_QUEBEC, ACCENT_QUEBEC, DANGER_QUEBEC, SUCCESS_QUEBEC,
    inject_quebec_theme
)
from ui.kpi_cards import render_kpi_card
from ui.charts import (
    plot_moderation_scatter, plot_regression_residuals, plot_quadrants_matrix,
    apply_standard_layout, download_csv_button
)
from ui.action_panel import render_action_panel
from ui.explainers import render_explainer, render_about_data
from ui.filters import render_sidebar_filters

st.set_page_config(
    page_title="2. Méso : Équité & Modération des Notes",
    layout="wide"
)
inject_quebec_theme()

st.title("2. Méso : Équité & Modération des Notes")
st.warning("⚖️ **Axe d'analyse : Risque de biais d'évaluation & de déstabilisation statistique** — Réguler l'écart entre la notation interne et l'épreuve externe pour protéger l'équité des élèves.")

df_mod_raw = get_df_moderation()

# Téléversement local de secours
if df_mod_raw.empty:
    st.info("Veuillez importer les tables de modération (CHS040506R.csv) ci-dessous ou depuis la page d'accueil.")
    mod_file = st.file_uploader("Importer le fichier CHS040506R (CSV)", type=["csv", "txt"], key="mod_page_upload")
    if mod_file:
        df_loaded = load_csv_robust(mod_file)
        if not df_loaded.empty:
            set_df_moderation(df_loaded)
            st.success("Données de modération chargées avec succès !")
            st.rerun()
    st.stop()

df_mod = clean_moderation_df(df_mod_raw)
if df_mod.empty:
    st.warning("Aucune donnée valide trouvée dans le rapport de modération.")
    st.stop()

# -----------------------------------------------------------------------------
# BARRE LATÉRALE : FILTRES ET SLIDERS ADAPTÉS
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Paramètres Docimologiques (MÉSO)")

# Slider de taille minimale de groupe : 0-24, défaut 16
min_eleves = st.sidebar.slider(
    "Taille minimale du groupe (Nb. élèves) :",
    min_value=0,
    max_value=24,
    value=16,
    step=1,
    help="Seuil d'effectif pour filtrer les micro-groupes soumis à une forte volatilité d'échantillonnage."
)

seuil_cohen = st.sidebar.slider(
    "Seuil d'anomalie |d de Cohen| :",
    min_value=0.2, max_value=2.0, value=0.8, step=0.1,
    help="0.8 = Écart majeur justifiant une harmonisation didactique."
)

seuil_dispersion = st.sidebar.slider(
    "Seuil de compression (Facteur R) :",
    min_value=0.2, max_value=1.5, value=0.6, step=0.1,
    help="R < 0.6 indique une dispersion interne comprimée par rapport à l'épreuve."
)

allow_teacher = get_teacher_opt_in()

# -----------------------------------------------------------------------------
# NORMALISATION DES COLONNES MÉTIER (ÉCOLE, GROUPE, DISCIPLINE)
# -----------------------------------------------------------------------------
# Remplir systématiquement École, Groupe, Discipline
if "Organisme" in df_mod.columns:
    df_mod["École"] = df_mod["Organisme"].apply(clean_cd_orgns)
else:
    df_mod["École"] = "Inconnue"

if "Groupe" not in df_mod.columns:
    df_mod["Groupe"] = "01"

if "Matiere" in df_mod.columns:
    df_mod["Discipline"] = df_mod["Matiere"].fillna(df_mod.get("Épreuve", "Discipline")).astype(str)
else:
    df_mod["Discipline"] = df_mod.get("Épreuve", "Discipline").astype(str)

df_mod["Type_Groupe"] = df_mod["Groupe"].apply(classify_group_type)

df_mod["Delta_Moyenne"] = (df_mod["Moyenne_ecole"] - df_mod["Moyenne_min"]).astype(np.float32)
et_min_safe = df_mod.get("ET_min", 10.0).replace(0, np.nan)
df_mod["Ratio_ET"] = (df_mod.get("ET_ecole", 10.0) / et_min_safe).fillna(1.0).astype(np.float32)

var_p = (df_mod.get("ET_ecole", 10.0)**2 + df_mod.get("ET_min", 10.0)**2) / 2.0
df_mod["Cohen_D"] = (df_mod["Delta_Moyenne"] / np.sqrt(var_p)).fillna(0.0).astype(np.float32)

df_mod["Type_Anomalie"] = [
    classify_moderation_anomaly(row["Cohen_D"], row["Ratio_ET"], seuil_cohen, seuil_dispersion)
    for _, row in df_mod.iterrows()
]

df_mod["Label_Groupe"] = "École " + df_mod["École"].astype(str) + " - Gr. " + df_mod["Groupe"].astype(str) + " (" + df_mod["Discipline"] + ")"
if not allow_teacher and "ENSEIGN" in df_mod.columns:
    df_mod["Label_Groupe"] = df_mod["Label_Groupe"].apply(lambda s: sanitize_teacher_display(s, allow_teacher))

# Filtrage par taille de groupe
df_filtered = df_mod[df_mod["Nb_eleves"] >= min_eleves].copy()
total_groupes = len(df_filtered)

# -----------------------------------------------------------------------------
# 1. BANDEAU DE SYNTHÈSE DES ANOMALIES
# -----------------------------------------------------------------------------
nb_sur = int((df_filtered["Type_Anomalie"] == "Surévalué (Indulgence)").sum())
nb_sous = int((df_filtered["Type_Anomalie"] == "Sous-évalué (Sévérité)").sum())
nb_comp = int((df_filtered["Type_Anomalie"] == "Compression des notes").sum())

pct_sur = (nb_sur / total_groupes * 100.0) if total_groupes > 0 else 0.0
pct_sous = (nb_sous / total_groupes * 100.0) if total_groupes > 0 else 0.0
pct_comp = (nb_comp / total_groupes * 100.0) if total_groupes > 0 else 0.0

k1, k2, k3 = st.columns(3)
with k1:
    stat_k1 = "danger" if pct_sur > 20 else ("warning" if pct_sur > 10 else "success")
    render_kpi_card(
        title="Groupes Surévalués (Indulgence)",
        value=f"{pct_sur:.1f}%",
        status=stat_k1,
        n=total_groupes,
        subtitle=f"{nb_sur} groupe(s) sur {total_groupes} (≥ {min_eleves} él.)",
        target="< 10.0%",
        help_text=f"Groupes avec d de Cohen > +{seuil_cohen:.1f} (notation école plus généreuse que l'épreuve)."
    )
with k2:
    stat_k2 = "danger" if pct_sous > 20 else ("warning" if pct_sous > 10 else "success")
    render_kpi_card(
        title="Groupes Sous-évalués (Sévérité)",
        value=f"{pct_sous:.1f}%",
        status=stat_k2,
        n=total_groupes,
        subtitle=f"{nb_sous} groupe(s) sur {total_groupes}",
        target="< 10.0%",
        help_text=f"Groupes avec d de Cohen < -{seuil_cohen:.1f} (notation école plus sévère que l'épreuve)."
    )
with k3:
    stat_k3 = "warning" if pct_comp > 15 else "success"
    render_kpi_card(
        title="Compression de Dispersion (R < 0.6)",
        value=f"{pct_comp:.1f}%",
        status=stat_k3,
        n=total_groupes,
        subtitle=f"{nb_comp} groupe(s) comprimé(s)",
        target="< 15.0%",
        help_text="Groupes où la dispersion école est resserrée artificiellement autour de la moyenne."
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. LES 3 REPRÉSENTATIONS SYNTHÉTIQUES DE NEB VS NMC
# -----------------------------------------------------------------------------
st.subheader(f"1. Synthèse des 3 Représentations NEB vs NMC (Groupes ≥ {min_eleves} élèves)")
st.caption("Masquage par défaut des groupes conformes dans la légende (cliquez sur la légende pour les afficher).")

# --- GRAPHIQUE A ---
st.markdown("#### A. Étalon ministériel : la notation de l'école est-elle globalement indulgente ou sévère ?")
st.markdown("*« La notation de cette école est-elle conforme à l'étalon ministériel ? »*")

col_ga, col_info_a = st.columns([2.2, 1.0])

with col_ga:
    fig_scat1 = plot_moderation_scatter(
        df_filtered,
        x_col="Moyenne_min",
        y_col="Moyenne_ecole",
        anomaly_col="Type_Anomalie",
        hover_name="Label_Groupe",
        discipline_col="Discipline",
        hide_normal_by_default=True,
        title="Écart à l'Épreuve Ministérielle (y = x)"
    )
    st.plotly_chart(fig_scat1, use_container_width=True)

with col_info_a:
    st.info("""
**Phénomènes détectés (diagnostic absolu) :**
- **Indulgence brute :** Points situés au-dessus de la droite ($y > x$), $d > +0{,}8$ (notes école plus généreuses que l'épreuve).
- **Sévérité brute :** Points situés sous la droite ($y < x$), $d < -0{,}8$ (notation école plus sévère que l'épreuve).
- **Compression d'échelle :** Variabilité interne tronquée ou resserrée artificiellement autour de la moyenne de groupe.
""")

st.markdown("---")

# --- GRAPHIQUE B ---
reg_stats = compute_ols_regression(df_filtered["Moyenne_min"], df_filtered["Moyenne_ecole"])
r2_val = reg_stats.get("r_squared")
r2_str = f"R² = {r2_val:.2f}" if r2_val is not None and not np.isnan(r2_val) else "N/D"

st.markdown("#### B. Cohérence réseau : quels groupes constituent des anomalies statistiques hors corridor (±1.5σ) ?")
st.markdown(
    f"*« Cette école s'écarte-t-elle anormalement du comportement moyen de l'ensemble du réseau ? »* "
    f"<span style='font-size:0.85rem; color:#64748b;'>(Cohérence du réseau : {r2_str})</span>",
    unsafe_allow_html=True
)

col_gb, col_info_b = st.columns([2.2, 1.0])

with col_gb:
    if not np.isnan(reg_stats["slope"]):
        fig_reg = plot_regression_residuals(
            df_filtered,
            x_col="Moyenne_min",
            y_col="Moyenne_ecole",
            slope=reg_stats["slope"],
            intercept=reg_stats["intercept"],
            residual_std=reg_stats["residual_std"],
            k_thresh=1.5,
            label_col="Label_Groupe",
            discipline_col="Discipline",
            title=f"Comparaison à la Norme du Réseau ({r2_str})"
        )
        st.plotly_chart(fig_reg, use_container_width=True)
    else:
        st.info("Données insuffisantes pour la régression du réseau.")

with col_info_b:
    st.info("""
**Phénomènes détectés (diagnostic statistique relatif) :**
- **Tendance générale du réseau :** Droite de régression représentant la relation moyenne réelle observée pour l'ensemble des écoles cette année ($Y_{\\text{école}} = a \\cdot X_{\\text{ministère}} + b$).
- **Groupes conformes :** Points situés dans le corridor de tolérance ($\pm 1{,}5\\sigma$).
- **Groupes atypiques / résiduels extrêmes :** Écoles en rupture statistique nette par rapport à la tendance globale du réseau (surperformance anormale ou indulgence critique nécessitant une modération prioritaire).
""")

# C. Compression des notes
st.markdown("##### C. Étalement des notes : l'évaluation locale compresse-t-elle artificiellement la variance des élèves ?")
render_explainer("compression")
render_explainer("regression")

st.markdown("---")

# -----------------------------------------------------------------------------
# 3. ANALYSE COMPARATIVE DES ANOMALIES D'INDULGENCE (SERVICES ÉD. & DGA)
# -----------------------------------------------------------------------------
st.subheader("2. Audit des écarts : surreprésentation des biais par discipline, par école et par type de regroupement")
st.markdown("Comparaison du nombre d'anomalies de surévaluation pour identifier les biais de matière, d'école et de regroupement.")

col_c1, col_c2, col_c3 = st.columns(3)

# A. Par Matière (Services éducatifs)
with col_c1:
    st.markdown("##### Par Matière / Discipline")
    df_anom_sur = df_filtered[df_filtered["Type_Anomalie"] == "Surévalué (Indulgence)"]
    if not df_anom_sur.empty:
        mat_counts = df_anom_sur["Discipline"].value_counts().reset_index()
        mat_counts.columns = ["Discipline", "Nb_Anomalies"]
        fig_mat = px.bar(
            mat_counts, x="Discipline", y="Nb_Anomalies",
            color_discrete_sequence=[PRIMARY_QUEBEC],
            title="Surévaluations par Discipline"
        )
        fig_mat.update_xaxes(tickangle=45)
        st.plotly_chart(apply_standard_layout(fig_mat, height=340), use_container_width=True)
    else:
        st.success("Aucune surévaluation par matière.")

# B. Par École (DGA)
with col_c2:
    st.markdown("##### Par Établissement (DGA)")
    if not df_anom_sur.empty:
        ecole_counts = df_anom_sur["École"].value_counts().reset_index()
        ecole_counts.columns = ["École", "Nb_Anomalies"]
        fig_ecole = px.bar(
            ecole_counts, x="École", y="Nb_Anomalies",
            color_discrete_sequence=[ACCENT_QUEBEC],
            title="Culture d'Indulgence par École"
        )
        fig_ecole.update_xaxes(type="category", tickangle=45)
        st.plotly_chart(apply_standard_layout(fig_ecole, height=340), use_container_width=True)
    else:
        st.success("Aucune surévaluation par établissement.")

# C. Par Typologie de Groupe
with col_c3:
    st.markdown("##### Par Type de Groupe")
    if not df_anom_sur.empty:
        grp_counts = df_anom_sur["Type_Groupe"].value_counts().reset_index()
        grp_counts.columns = ["Typologie", "Nb_Anomalies"]
        fig_grp = px.bar(
            grp_counts, x="Typologie", y="Nb_Anomalies",
            color_discrete_sequence=["#b91c1c"],
            title="Indulgence par Typologie"
        )
        fig_grp.update_xaxes(tickangle=30)
        st.plotly_chart(apply_standard_layout(fig_grp, height=340), use_container_width=True)
    else:
        st.success("Aucune surévaluation par type de groupe.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. MATRICE 4 QUADRANTS ET DRILL-DOWN DES GROUPES PRIORITAIRES
# -----------------------------------------------------------------------------
st.subheader("3. Cibles d'accompagnement : quels groupes subissent à la fois un fort biais et une lourde décote ?")
st.markdown("Croisement du biais théorique ($NEB - NMC$) et de la sévérité pratique ($NEB$ pour $NEM=60$) pour cibler les interventions.")

df_quad_in = df_filtered.copy()
df_quad_in["Biais_Theorique"] = df_quad_in["Delta_Moyenne"]
df_quad_in["Severite_Pratique"] = df_quad_in.get("NEB_60", df_quad_in["Delta_Moyenne"].abs())
df_quad_res = compute_quadrants(
    df_quad_in,
    x_col="Biais_Theorique",
    y_col="Severite_Pratique",
    x_threshold=2.0,
    y_threshold=60.0
)

col_q1, col_q2 = st.columns([1.2, 1.8])

with col_q1:
    fig_quad = plot_quadrants_matrix(
        df_quad_res,
        x_col="Biais_Theorique",
        y_col="Severite_Pratique",
        x_threshold=2.0,
        y_threshold=60.0,
        label_col="Label_Groupe",
        title="Matrice 4 Quadrants (Biais × Sévérité)"
    )
    st.plotly_chart(fig_quad, use_container_width=True)

with col_q2:
    st.markdown("##### Groupes Prioritaires à Accompagner (Quadrant 1)")
    q1_prioritaires = df_quad_res[
        (df_quad_res["Biais_Theorique"] >= 2.0) &
        (df_quad_res["Severite_Pratique"] >= 60.0)
    ].copy()

    if not q1_prioritaires.empty:
        cols_q1 = ["École", "Groupe", "Discipline", "Type_Groupe", "Nb_eleves", "Moyenne_ecole", "Moyenne_min", "Delta_Moyenne", "Type_Anomalie"]
        cols_avail = [c for c in cols_q1 if c in q1_prioritaires.columns]

        df_table_q1, n_supp = filter_small_cells(q1_prioritaires[cols_avail], count_col="Nb_eleves", min_count=5)
        df_display_q1 = df_table_q1.rename(columns={
            "Nb_eleves": "Effectif (N)",
            "Moyenne_ecole": "Moy. NEB (%)",
            "Moyenne_min": "Moy. NMC (%)",
            "Delta_Moyenne": "Écart Brut (%)",
            "Type_Anomalie": "Statut"
        }).sort_values(by="Écart Brut (%)", ascending=False)

        st.dataframe(sanitize_df_for_stlite(df_display_q1.reset_index(drop=True)), use_container_width=True)
        download_csv_button(df_display_q1, "groupes_prioritaires_q1.csv", "Exporter les Groupes Q1 (CSV)")
    else:
        st.success("Aucun groupe ne se situe dans la zone critique du Quadrant 1.")

# -----------------------------------------------------------------------------
# 5. PANNEAU D'ACTION DYNAMIQUE (LAD P2)
# -----------------------------------------------------------------------------
st.markdown("---")
constat_meso = (
    f"Sur les {total_groupes} groupes d'au moins {min_eleves} élèves analysés, {nb_sur} ({pct_sur:.1f}%) affichent une indulgence marquée, "
    f"et {nb_comp} ({pct_comp:.1f}%) une compression anormale de variance. "
    f"{len(q1_prioritaires)} groupe(s) cumulent un fort biais et une sévérité pratique (Quadrant 1)."
) if total_groupes > 0 else "Aucun groupe disponible pour ce seuil."

pistes_meso = [
    "**Harmonisation disciplinaire :** Les disciplines les plus touchées par l'indulgence doivent faire l'objet d'ateliers de correction croisée organisés par les conseillers pédagogiques.",
    "**Accompagnement réflexif des écoles :** Pour les écoles surreprésentées dans les anomalies, engager un dialogue constructif sur la fidélité des critères d'évaluation par rapport au Cadre ministériel.",
    "**Étalement de l'évaluation :** Sensibiliser les enseignants des groupes comprimés à diversifier les niveaux de difficulté des questions pour mieux discriminer les compétences réelles."
]

render_action_panel(
    question="Comment intervenir auprès des équipes didactiques et des écoles pour résorber les biais de surévaluation et harmoniser le jugement professionnel ?",
    constat_dynamique=constat_meso,
    pistes=pistes_meso,
    context_tag=f"Seuil N ≥ {min_eleves}"
)

render_explainer("moderation_rq")
render_explainer("quadrants")
render_about_data(
    source_name="Tables de modération ministérielles CHS040506R",
    limits=[
        "Le seuil de taille de groupe par défaut est fixé à 16 élèves (norme réseau) mais demeure ajustable de 0 à 24.",
        "Les libellés d'enseignants demeurent désensibilisés par défaut conformément aux exigences de la Loi 25."
    ]
)
