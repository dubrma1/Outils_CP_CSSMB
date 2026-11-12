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
    clean_cd_orgns, ECOLES_LIST, SUBJECT_MAP, CODE_TO_MATIERE_COURT, classify_group_type
)
from core.state import (
    get_df_moderation, set_df_moderation, get_teacher_opt_in,
    get_global_filters, update_global_filter
)
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

# Normalisation préalable des colonnes École, Groupe, Discipline (conversion str sécurisée contre Categorical.fillna)
if "Organisme" in df_mod.columns:
    df_mod["École"] = df_mod["Organisme"].astype(str).apply(clean_cd_orgns)
else:
    df_mod["École"] = "Inconnue"

if "Groupe" not in df_mod.columns:
    df_mod["Groupe"] = "01"
else:
    df_mod["Groupe"] = df_mod["Groupe"].astype(str)

if "Matiere" in df_mod.columns:
    mat_s = df_mod["Matiere"].astype(str).replace(["nan", "None", ""], np.nan)
    epr_s = df_mod["Épreuve"].astype(str).replace(["nan", "None", ""], np.nan) if "Épreuve" in df_mod.columns else "Discipline"
    df_mod["Discipline"] = mat_s.fillna(epr_s).fillna("Discipline").astype(str)
else:
    df_mod["Discipline"] = df_mod["Épreuve"].astype(str) if "Épreuve" in df_mod.columns else "Discipline"

def _short_matiere_label(raw_val: str) -> str:
    """Normalise un libellé ou code de cours en nom court lisible (ex: Math CST, Histoire 4, Science ST)."""
    s = str(raw_val).strip()
    if not s or s in ("nan", "None"):
        return "Discipline"
    s_clean = s.replace(".0", "")
    if s_clean in CODE_TO_MATIERE_COURT:
        return CODE_TO_MATIERE_COURT[s_clean]
    if s in SUBJECT_MAP:
        return SUBJECT_MAP[s]["nom_court"]
    sl = s.lower()
    if "anglais" in sl and ("enrichi" in sl or "136" in sl):
        return "Anglais enrichi"
    if "anglais" in sl:
        return "Anglais 5"
    if "cst" in sl or "634" in sl:
        return "Math CST"
    if "sn" in sl or "654" in sl:
        return "Math SN"
    if "ts" in sl or "644" in sl:
        return "Math TS"
    if "hist" in sl or "854" in sl:
        return "Histoire 4"
    if "ats" in sl or "574" in sl:
        return "Science ATS"
    if "science" in sl or "st" in sl or "554" in sl:
        return "Science ST"
    if ("fran" in sl and "5" in sl) or "1325" in sl:
        return "Français 5"
    if ("fran" in sl and "4" in sl) or "1324" in sl:
        return "Français 4"
    # Nettoyage de parenthèses de code si présent
    return s.split("(")[0].strip() or s


def _slug_matiere_groupe(mat_label: str, grp_val: str) -> str:
    """Formate un couple Matière-Groupe compact (ex: Anglais5-03, Math_CST-01, Hist4-05, Science_ST-05)."""
    m = _short_matiere_label(mat_label)
    slug_map = {
        "Anglais 5": "Anglais5",
        "Anglais 5 base": "Anglais5",
        "Anglais enrichi": "Anglais_enr",
        "Math CST": "Math_CST",
        "Math SN": "Math_SN",
        "Math TS": "Math_TS",
        "Histoire 4": "Hist4",
        "Science ST": "Science_ST",
        "Science ATS": "Science_ATS",
        "Français 4": "Français4",
        "Français 5": "Français5",
    }
    m_slug = slug_map.get(m, m.replace(" ", "_"))
    g = str(grp_val).strip().replace(".0", "")
    if g.isdigit() and len(g) == 1:
        g = g.zfill(2)
    return f"{m_slug}-{g}"


df_mod["Discipline_Court"] = df_mod["Discipline"].apply(_short_matiere_label)
df_mod["Matiere_Groupe"] = [
    _slug_matiere_groupe(m, g)
    for m, g in zip(df_mod["Discipline_Court"], df_mod["Groupe"])
]
df_mod["Type_Groupe"] = df_mod["Groupe"].apply(classify_group_type)

# -----------------------------------------------------------------------------
# BARRE LATÉRALE : FILTRES ÉCOLE / MATIÈRE ET SLIDERS DOCIMOLOGIQUES
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Filtres Établissement & Matière (MÉSO)")

ecoles_dispo_meso = sorted([e for e in df_mod["École"].astype(str).unique() if e and e not in ("nan", "None")])
matieres_dispo_meso = sorted([m for m in df_mod["Discipline"].astype(str).unique() if m and m not in ("nan", "None")])

cur_global = get_global_filters()
saved_ecole = clean_cd_orgns(cur_global.get("selected_ecole", "Toutes"))
opts_ecole_meso = ["Toutes"] + ecoles_dispo_meso
default_ecole_idx = opts_ecole_meso.index(saved_ecole) if saved_ecole in opts_ecole_meso else 0

sel_ecole_meso = st.sidebar.selectbox(
    "Filtrer par Établissement / École (Filtre principal) :",
    options=opts_ecole_meso,
    index=default_ecole_idx,
    key="sb_meso_ecole"
)
update_global_filter("selected_ecole", sel_ecole_meso)

sel_matiere_meso = st.sidebar.selectbox(
    "Filtrer par Matière / Discipline :",
    options=["Toutes"] + matieres_dispo_meso,
    index=0,
    key="sb_meso_matiere"
)

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

# Filtrage par taille de groupe, école et matière
mask_meso = (df_mod["Nb_eleves"] >= min_eleves)
if sel_ecole_meso != "Toutes":
    mask_meso &= (df_mod["École"].astype(str) == sel_ecole_meso)
if sel_matiere_meso != "Toutes":
    mask_meso &= (df_mod["Discipline"].astype(str) == sel_matiere_meso)

df_filtered = df_mod[mask_meso].copy()
total_groupes = len(df_filtered)

# -----------------------------------------------------------------------------
# 1. BANDEAU DE SYNTHÈSE DES CIBLES (SANS POURCENTAGES DISTRAYANTS)
# -----------------------------------------------------------------------------
df_sur = df_filtered[df_filtered["Cohen_D"] > seuil_cohen].copy()
df_sous = df_filtered[df_filtered["Cohen_D"] < -seuil_cohen].copy()
df_comp = df_filtered[df_filtered["Ratio_ET"] < seuil_dispersion].copy()

nb_sur = len(df_sur)
nb_sous = len(df_sous)
nb_comp = len(df_comp)

is_single_ecole = (sel_ecole_meso != "Toutes")


def _build_ranking_lines(df_sub: pd.DataFrame, sort_col: str, ascending: bool, single_school: bool) -> tuple:
    """
    Construit les deux lignes de hiérarchie (Top 5 Matières et Top 5 Écoles ou Matière-Groupe)
    pour focaliser l'attention sur les cibles prioritaires.
    """
    if df_sub.empty:
        return ("0 Matière : Aucune", "0 Groupe : Aucun" if single_school else "0 École : Aucune")

    # 1. Top 5 Matières (ordonnées par nombre de groupes touchés décroissant)
    vc_mat = df_sub["Discipline_Court"].astype(str).value_counts()
    vc_mat = vc_mat[vc_mat > 0].head(5)
    n_mat = len(vc_mat)
    mat_chain = " > ".join(vc_mat.index.tolist())
    line_mat = f"<strong>{n_mat} Matière{'s' if n_mat > 1 else ''} :</strong> {mat_chain}"

    # 2. Top 5 Écoles (ou Matière-Groupe si une école est sélectionnée dans le filtre principal)
    if single_school:
        df_sorted = df_sub.sort_values(by=sort_col, ascending=ascending).head(5)
        grps = df_sorted["Matiere_Groupe"].astype(str).tolist()
        n_grp = len(grps)
        grp_chain = " &lt; ".join(grps) if ascending else " &gt; ".join(grps)
        line_ec = f"<strong>{n_grp} Matière-Groupe (École {sel_ecole_meso}) :</strong> {grp_chain}"
    else:
        vc_ec = df_sub["École"].astype(str).value_counts()
        vc_ec = vc_ec[vc_ec > 0].head(5)
        n_ec = len(vc_ec)
        ec_chain = " &gt; ".join(vc_ec.index.tolist())
        line_ec = f"<strong>{n_ec} École{'s' if n_ec > 1 else ''} :</strong> {ec_chain}"

    return line_mat, line_ec


def _render_meso_target_card(
    title: str,
    count_val: int,
    main_desc: str,
    effect_line: str,
    line_mat: str,
    line_ec: str,
    border_color: str,
    bg_color: str,
    badge_text: str
) -> None:
    effect_html = (
        f"<div style='font-size: 0.88rem; color: #334155; font-weight: 500; margin-bottom: 8px;'>{effect_line}</div>"
        if effect_line else ""
    )
    html = (
        f"<div style='background-color: {bg_color}; border-left: 6px solid {border_color}; border-radius: 8px; "
        "padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 12px; height: 100%;'>"
        "<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>"
        f"<span style='font-size: 0.95rem; font-weight: 700; color: #0f172a;'>{title}</span>"
        f"<span style='font-size: 0.75rem; font-weight: 600; color: {border_color}; background: #ffffff; "
        f"padding: 2px 8px; border-radius: 12px; border: 1px solid {border_color};'>{badge_text}</span>"
        "</div>"
        f"<div style='font-size: 1.15rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;'>"
        f"<span style='font-size: 1.65rem; color: {border_color};'>{count_val}</span> {main_desc}"
        "</div>"
        f"{effect_html}"
        "<div style='margin-top: 8px; padding-top: 8px; border-top: 1px dashed rgba(15,23,42,0.15); "
        "font-size: 0.85rem; color: #1e293b; line-height: 1.55;'>"
        f"<div>{line_mat}</div>"
        f"<div style='margin-top: 3px;'>{line_ec}</div>"
        "</div>"
        "</div>"
    )
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


mat_sur, ec_sur = _build_ranking_lines(df_sur, sort_col="Cohen_D", ascending=False, single_school=is_single_ecole)
mat_sous, ec_sous = _build_ranking_lines(df_sous, sort_col="Cohen_D", ascending=True, single_school=is_single_ecole)
mat_comp, ec_comp = _build_ranking_lines(df_comp, sort_col="Ratio_ET", ascending=True, single_school=is_single_ecole)

k1, k2, k3 = st.columns(3)
with k1:
    _render_meso_target_card(
        title="Groupes Surévalués (Indulgence)",
        count_val=nb_sur,
        main_desc="groupes avec une notation école plus généreuse que l'épreuve",
        effect_line=f"La taille de l'effet est importante (d de Cohen &gt; +{seuil_cohen:.1f})",
        line_mat=mat_sur,
        line_ec=ec_sur,
        border_color="#dc2626",
        bg_color="#fef2f2",
        badge_text="Indulgence"
    )
with k2:
    _render_meso_target_card(
        title="Groupes Sous-évalués (Sévérité)",
        count_val=nb_sous,
        main_desc="groupes avec une notation école plus sévère que l'épreuve",
        effect_line=f"La taille de l'effet est importante (d de Cohen &lt; -{seuil_cohen:.1f})",
        line_mat=mat_sous,
        line_ec=ec_sous,
        border_color="#095797",
        bg_color="#f0f7ff",
        badge_text="Sévérité"
    )
with k3:
    _render_meso_target_card(
        title="Homogénéisation artificielle des résultats",
        count_val=nb_comp,
        main_desc=f"groupes présentent des résultats anormalement regroupés autour de la moyenne de l'école (R &lt; {seuil_dispersion:.1f})",
        effect_line="Dispersion interne comprimée par rapport à l'épreuve ministérielle",
        line_mat=mat_comp,
        line_ec=ec_comp,
        border_color="#d97706",
        bg_color="#fffbeb",
        badge_text="Homogénéisation"
    )

st.info(
    "**Ce que cela signifie (Homogénéisation artificielle des résultats) :** "
    "Dans une classe ordinaire, on s'attend à voir des écarts naturels entre les élèves en difficulté "
    "et ceux qui performent très bien. Ici, les notes sont trop uniformes, ce qui peut suggérer une "
    "évaluation peu discriminante ou un nivellement des résultats."
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
- **Groupes conformes :** Points situés dans le corridor de tolérance ($\\pm 1{,}5\\sigma$).
- **Groupes atypiques / résiduels extrêmes :** Écoles en rupture statistique nette par rapport à la tendance globale du réseau (surperformance anormale ou indulgence critique nécessitant une modération prioritaire).
""")

# C. Homogénéisation artificielle des résultats (Compression des notes)
st.markdown("##### C. Homogénéisation artificielle des résultats : l'évaluation locale compresse-t-elle artificiellement la variance des élèves ?")
st.info(
    "**Ce que cela signifie :** Dans une classe ordinaire, on s'attend à voir des écarts naturels entre les élèves en difficulté "
    "et ceux qui performent très bien. Ici, les notes sont trop uniformes, ce qui peut suggérer une évaluation peu discriminante "
    "ou un nivellement des résultats."
)
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
# 4. MATRICE 4 QUADRANTS AGRANDIE, EXPLICATIONS DÉTAILLÉES & FILTRES LOCAUX
# -----------------------------------------------------------------------------
st.subheader("3. Cibles d'accompagnement : quels groupes subissent à la fois un fort biais et une lourde décote ?")
st.markdown(
    "Croisement du **Biais théorique** ($X = NEB - NMC$) et de la **Sévérité pratique au seuil de passage** "
    "($Y = NEB$ requis lorsque $NEM = 60$) pour isoler les groupes exposés à une décote ministérielle."
)

# Explications docimologiques détaillées de la Matrice 4 Quadrants
st.info("""
**Guide de lecture docimologique de la Matrice 4 Quadrants (Biais × Sévérité) :**
- **Axe horizontal ($X$ — Biais théorique = $NEB - NMC$, seuil à $+2{,}0\\text{ pts}$) :** Mesure l'écart entre la moyenne accordée par l'école ($NEB$) et la moyenne obtenue à l'épreuve ministérielle convertie ($NMC$). Plus un groupe est à droite ($X > +2{,}0$), plus la notation locale a été indulgente par rapport à l'étalon ministériel.
- **Axe vertical ($Y$ — Sévérité pratique = $NEB \\text{ lorsque } NEM = 60$, seuil à $60{,}0\\ \\%$) :** Indique la note école brute minimale qu'un élève devait détenir avant modération pour conserver la note de passage ($60\\ \\%$) après modération. Par exemple, si $Y = 66\\ \\%$, tout élève ayant entre $60\\ \\%$ et $65\\ \\%$ à l'école bascule en échec modéré si sa note à l'épreuve ne le sauve pas.
- **Quadrant 1 (Haut-Droite — Priorité d'intervention maximale, en rouge) :** Cumul d'une forte surévaluation locale ($X \\ge +2{,}0$) et d'une lourde pénalité au seuil de passage ($Y \\ge 60\\ \\%$). Ces groupes subissent une correction statistique sévère qui fragilise directement les élèves proches de $60\\ \\%$.
- **Quadrant 2 (Haut-Gauche — Vigilance de dispersion, en ambre) :** Écart de moyenne faible ou négatif ($X < +2{,}0$), mais seuil exigeant ($Y \\ge 60\\ \\%$) provoqué par une compression ou une asymétrie des notes école (Facteur $R$).
- **Quadrant 3 (Bas-Gauche — Zone conforme et équilibrée, en vert) :** Alignement optimal entre le jugement professionnel de l'enseignant et l'épreuve ministérielle ($X < +2{,}0$ et $Y < 60\\ \\%$).
- **Quadrant 4 (Bas-Droite — Indulgence amortie, en bleu) :** Moyenne école supérieure à l'épreuve ($X \\ge +2{,}0$), mais l'étalement interne des notes protège les élèves situés autour du seuil de passage ($Y < 60\\ \\%$).
""")

# Filtres dédiés Matière et École directement au-dessus de la Matrice 4 Quadrants
col_fq1, col_fq2 = st.columns(2)
with col_fq1:
    ecoles_quad_opts = sorted([e for e in df_filtered["École"].astype(str).unique() if e and e not in ("nan", "None")])
    sel_ecoles_quad = st.multiselect(
        "Filtrer la matrice par École(s) :",
        options=ecoles_quad_opts,
        default=ecoles_quad_opts,
        key="quad_filter_ecoles"
    )
with col_fq2:
    mats_quad_opts = sorted([m for m in df_filtered["Discipline"].astype(str).unique() if m and m not in ("nan", "None")])
    sel_mats_quad = st.multiselect(
        "Filtrer la matrice par Matière(s) / Discipline(s) :",
        options=mats_quad_opts,
        default=mats_quad_opts,
        key="quad_filter_matieres"
    )

df_quad_in = df_filtered.copy()
if sel_ecoles_quad:
    df_quad_in = df_quad_in[df_quad_in["École"].astype(str).isin(sel_ecoles_quad)]
if sel_mats_quad:
    df_quad_in = df_quad_in[df_quad_in["Discipline"].astype(str).isin(sel_mats_quad)]

df_quad_in["Biais_Theorique"] = df_quad_in["Delta_Moyenne"]
df_quad_in["Severite_Pratique"] = df_quad_in.get("NEB_60", 60.0 + df_quad_in["Delta_Moyenne"])
df_quad_res = compute_quadrants(
    df_quad_in,
    x_col="Biais_Theorique",
    y_col="Severite_Pratique",
    x_threshold=2.0,
    y_threshold=60.0
)

# Visualisation agrandie en pleine largeur (hauteur 620 px)
fig_quad = plot_quadrants_matrix(
    df_quad_res,
    x_col="Biais_Theorique",
    y_col="Severite_Pratique",
    x_threshold=2.0,
    y_threshold=60.0,
    label_col="Label_Groupe",
    title="Matrice 4 Quadrants Agrandie (Biais Théorique × Sévérité Pratique au Seuil de 60 %)",
    height=620
)
st.plotly_chart(fig_quad, use_container_width=True)

st.markdown("##### Groupes Prioritaires à Accompagner (Quadrant 1 — Indulgence & Décote sévère)")
q1_prioritaires = df_quad_res[
    (df_quad_res["Biais_Theorique"] >= 2.0) &
    (df_quad_res["Severite_Pratique"] >= 60.0)
].copy()

if not q1_prioritaires.empty:
    cols_q1 = ["École", "Groupe", "Discipline", "Type_Groupe", "Nb_eleves", "Moyenne_ecole", "Moyenne_min", "Delta_Moyenne", "Severite_Pratique", "Type_Anomalie"]
    cols_avail = [c for c in cols_q1 if c in q1_prioritaires.columns]

    df_table_q1, n_supp = filter_small_cells(q1_prioritaires[cols_avail], count_col="Nb_eleves", min_count=5)
    df_display_q1 = df_table_q1.rename(columns={
        "Nb_eleves": "Effectif (N)",
        "Moyenne_ecole": "Moy. NEB (%)",
        "Moyenne_min": "Moy. NMC (%)",
        "Delta_Moyenne": "Biais NEB-NMC (pts)",
        "Severite_Pratique": "Seuil NEB pour 60% (%)",
        "Type_Anomalie": "Statut"
    }).sort_values(by="Biais NEB-NMC (pts)", ascending=False)

    st.dataframe(sanitize_df_for_stlite(df_display_q1.reset_index(drop=True)), use_container_width=True)
    download_csv_button(df_display_q1, "groupes_prioritaires_q1.csv", "Exporter les Groupes Q1 (CSV)")
else:
    st.success("Aucun groupe ne se situe dans la zone critique du Quadrant 1 pour la sélection active.")

# -----------------------------------------------------------------------------
# 5. PANNEAU D'ACTION DYNAMIQUE (LAD P2)
# -----------------------------------------------------------------------------
st.markdown("---")
constat_meso = (
    f"Sur les {total_groupes} groupes d'au moins {min_eleves} élèves analysés, {nb_sur} groupes affichent une indulgence marquée (d > +{seuil_cohen:.1f}), "
    f"{nb_sous} groupes une sévérité marquée (d < -{seuil_cohen:.1f}), et {nb_comp} groupes une homogénéisation artificielle des résultats (R < {seuil_dispersion:.1f}). "
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
