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
    CODE_TO_MATIERE, CODE_TO_EPREUVE, classify_group_type, ENRICHED_CODES,
    ECOLES_ADAPTATION
)
from core.state import get_df_main, get_teacher_opt_in
from core.metrics import (
    wilson_interval, add_confidence_intervals, compute_competency_gaps_by_group,
    COMPETENCY_SUFFIX_MAP, _map_code_to_comp
)
from core.privacy import filter_small_cells, sanitize_teacher_display
from ui.theme import (
    BLEU_QUEBEC, BLEU_QUEBEC_LIGHT, PALETTE_ACCESSIBLE,
    PRIMARY_QUEBEC, SECONDARY_QUEBEC, ACCENT_QUEBEC, DANGER_QUEBEC, SUCCESS_QUEBEC,
    inject_quebec_theme
)
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

seuil_ecart_comp = st.sidebar.slider(
    "Seuil d'écart significatif inter-compétences (pts) :",
    min_value=4.0, max_value=20.0, value=8.0, step=1.0,
    help="Écart moyen minimal (en points de %) entre deux compétences d'un même groupe-école pour signaler une distorsion didactique (combiné à p < 0.05)."
)

seuil_cohen_comp = st.sidebar.slider(
    "Seuil de taille d'effet inter-compétences |d de Cohen| :",
    min_value=0.3, max_value=1.5, value=0.6, step=0.1,
    help="Taille d'effet intra-groupe minimale entre deux compétences."
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

if "NO_GROUP_ELEVE" not in df_sub.columns and "NO_GROUP" in df_sub.columns:
    df_sub["NO_GROUP_ELEVE"] = df_sub["NO_GROUP"]

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

# C. Compétences disciplinaires ministérielles : Taux de réussite (%) et Moyennes (%) par établissement
st.markdown("##### C. Visualisation des Compétences Disciplinaires par Établissement (Taux de Réussite & Moyennes)")
st.caption("Profil comparatif des compétences d'évaluation : Mathématiques (Résoudre C1 vs Raisonner C2), Sciences (Pratique C1 vs Théorie C2) et Français (Oral C1, Lecture C2, Écriture C3).")

# Extraction des composantes de compétences (tolérant aux filtres amont)
df_comp_in = df_sub.copy()
has_comp = False
if "CD_COURS_str" in df_comp_in.columns:
    has_comp = df_comp_in["CD_COURS_str"].astype(str).str.endswith("0").any()
if not has_comp and not df_main.empty:
    df_comp_in = df_main.copy()
    if selected_ecoles and "CD_ORGNS" in df_comp_in.columns:
        clean_sel = set(clean_cd_orgns(e) for e in selected_ecoles)
        df_comp_in = df_comp_in[df_comp_in["CD_ORGNS"].isin(clean_sel)]
    if filtrer_enrichis and "CD_PERMN" in df_comp_in.columns and "CD_COURS_str" in df_comp_in.columns:
        enrichis_ids = set(df_comp_in.loc[df_comp_in["CD_COURS_str"].isin(["058404", "058402", "58404", "58402"]), "CD_PERMN"].unique())
        df_comp_in = df_comp_in[~df_comp_in["CD_PERMN"].isin(enrichis_ids)]

s_c_code = df_comp_in["CD_COURS_str"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip() if "CD_COURS_str" in df_comp_in.columns else pd.Series(index=df_comp_in.index)
mapped_c = s_c_code.map(_map_code_to_comp)

s_c_note = pd.to_numeric(df_comp_in["RESLT_FINAL"].astype(str).str.replace(",", "."), errors="coerce") if "RESLT_FINAL" in df_comp_in.columns else pd.Series(np.nan, index=df_comp_in.index)
for fb in ("NOTE_ECOLE_BRUT", "NOTE_ECOLE_BRUTE", "NOTE_ECOLE_MODR", "NOTE_MINST_CONVR"):
    if fb in df_comp_in.columns:
        s_c_note = s_c_note.fillna(pd.to_numeric(df_comp_in[fb].astype(str).str.replace(",", "."), errors="coerce"))

mask_c = mapped_c.notna() & s_c_note.notna()
if mask_c.any():
    df_comp_vis = pd.DataFrame({
        "CD_PERMN": df_comp_in.loc[mask_c, "CD_PERMN"].astype(str).str.strip(),
        "École": df_comp_in.loc[mask_c, "CD_ORGNS"].apply(clean_cd_orgns),
        "Note": s_c_note.loc[mask_c].astype("float32"),
        "Tuple_Map": mapped_c.loc[mask_c]
    }, index=df_comp_in.index[mask_c])

    df_comp_vis["Famille"] = [t[0] for t in df_comp_vis["Tuple_Map"]]
    df_comp_vis["Matiere"] = [t[1] for t in df_comp_vis["Tuple_Map"]]
    df_comp_vis["Competence"] = [t[2] for t in df_comp_vis["Tuple_Map"]]
    df_comp_vis = df_comp_vis[df_comp_vis["Competence"] != "Global"]
    df_comp_vis["Reussite_Bool"] = (df_comp_vis["Note"] >= 60.0).astype(int)

    familles_dispo = sorted(df_comp_vis["Famille"].unique().tolist())
    fam_labels = {
        "Mathématiques": "📐 Mathématiques (C1 Résoudre vs C2 Raisonner)",
        "Sciences": "🧪 Sciences (C1 Pratique vs C2 Théorie)",
        "Français": "📖 Français (C1 Oral, C2 Lecture, C3 Écriture)"
    }
    opts_fam = [f for f in ["Mathématiques", "Sciences", "Français"] if f in familles_dispo]
    if not opts_fam:
        opts_fam = familles_dispo

    sel_fam = st.radio(
        "Sélectionner la discipline pour les compétences :",
        options=opts_fam,
        format_func=lambda x: fam_labels.get(x, x),
        horizontal=True,
        key="radio_famille_comp_bars"
    )

    df_fam_sub = df_comp_vis[df_comp_vis["Famille"] == sel_fam].copy()
    if not df_fam_sub.empty:
        agg_comp = df_fam_sub.groupby(["École", "Competence"], observed=True).agg(
            Taux=("Reussite_Bool", "mean"),
            Moyenne=("Note", "mean"),
            Effectif=("CD_PERMN", "nunique")
        ).reset_index()
        agg_comp["Taux de réussite (%)"] = (agg_comp["Taux"] * 100.0).round(1)
        agg_comp["Note moyenne (%)"] = agg_comp["Moyenne"].round(1)

        # Règle de confidentialité N >= 5
        agg_comp_vis, _ = filter_small_cells(agg_comp, count_col="Effectif", min_count=5)
        agg_comp_vis["École"] = agg_comp_vis["École"].astype(str)

        col_c_taux, col_c_moy = st.columns(2)

        # Palette à haut contraste pour distinguer nettement les compétences
        comp_palette = {
            "Résoudre": "#095797",   # Bleu marine Québec profond (C1)
            "Raisonner": "#ea580c",  # Ambre cuivré / Orange vif contrasté (C2)
            "Pratique": "#059669",   # Vert émeraude laboratoire (C1)
            "Théorie": "#7c3aed",    # Violet impérial soutenu (C2)
            "Oral": "#059669",       # Vert émeraude (C1)
            "Lecture": "#0284c7",    # Bleu ciel azur (C2)
            "Écriture": "#dc2626"    # Rouge cramoisi (C3)
        }

        with col_c_taux:
            fig_c_taux = px.bar(
                agg_comp_vis,
                x="École",
                y="Taux de réussite (%)",
                color="Competence",
                barmode="group",
                color_discrete_map=comp_palette,
                title=f"Taux de réussite par compétence — {sel_fam} (seuil ≥ 60%)",
                labels={"École": "Établissement", "Taux de réussite (%)": "Taux de Réussite (%)", "Competence": "Compétence"}
            )
            fig_c_taux.update_yaxes(range=[0, 105])
            fig_c_taux.add_hline(y=60, line_dash="dot", line_color=DANGER_QUEBEC, annotation_text="Cible 60%")
            fig_c_taux = apply_standard_layout(fig_c_taux, height=380)
            fig_c_taux.update_xaxes(type="category", categoryorder="category ascending")
            st.plotly_chart(fig_c_taux, use_container_width=True)

        with col_c_moy:
            fig_c_moy = px.bar(
                agg_comp_vis,
                x="École",
                y="Note moyenne (%)",
                color="Competence",
                barmode="group",
                color_discrete_map=comp_palette,
                title=f"Moyenne des notes par compétence — {sel_fam} (%)",
                labels={"École": "Établissement", "Note moyenne (%)": "Note moyenne (%)", "Competence": "Compétence"}
            )
            fig_c_moy.update_yaxes(range=[0, 100])
            fig_c_moy.add_hline(y=60, line_dash="dot", line_color=DANGER_QUEBEC, annotation_text="Seuil 60%")
            fig_c_moy = apply_standard_layout(fig_c_moy, height=380)
            fig_c_moy.update_xaxes(type="category", categoryorder="category ascending")
            st.plotly_chart(fig_c_moy, use_container_width=True)
    else:
        st.info(f"Aucune donnée de compétences pour {sel_fam}.")
else:
    st.info("Données de compétences disciplinaires non disponibles pour les filtres actifs.")

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. ANALYSE DES ÉCARTS SIGNIFICATIFS ENTRE LES COMPÉTENCES D'UNE MÊME MATIÈRE
# -----------------------------------------------------------------------------
st.subheader("2. Cohérence intra-matière : quels groupes-écoles présentent un écart significatif entre les compétences d'une même discipline ?")
st.markdown(
    "Analyse comparative au sein des groupes-écoles pour détecter les ruptures didactiques et les effets de compensation "
    f"entre compétences d'une même matière (seuil d'écart $|\\Delta| \\ge {seuil_ecart_comp:.0f}\\text{{ pts}}$ ou $|d| \\ge {seuil_cohen_comp:.1f}$, test $t$ apparié $p < 0{{,}}05$) : "
    "**Mathématiques** (*Résoudre* vs *Raisonner*), **Sciences** (*Pratique* vs *Théorie*) et **Français** (*Oral*, *Lecture* et *Écriture*)."
)

comp_gaps = compute_competency_gaps_by_group(
    df_comp_in,
    min_eleves=max(5, min_eleves_micro),
    seuil_delta=seuil_ecart_comp,
    seuil_cohen=seuil_cohen_comp
)
df_comp_math = comp_gaps["math"]
df_comp_sci = comp_gaps["science"]
df_comp_fra = comp_gaps["francais"]

single_school_micro = (len(selected_ecoles) == 1)


def _render_micro_comp_card(
    title: str,
    nb_sig: int,
    nb_tot: int,
    desc_text: str,
    stats_line: str,
    cibles_line: str,
    border_col: str,
    bg_col: str,
    badge_lbl: str
) -> None:
    html = (
        f"<div style='background-color: {bg_col}; border-left: 6px solid {border_col}; border-radius: 8px; "
        "padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 12px; height: 100%;'>"
        "<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>"
        f"<span style='font-size: 0.95rem; font-weight: 700; color: #0f172a;'>{title}</span>"
        f"<span style='font-size: 0.75rem; font-weight: 600; color: {border_col}; background: #ffffff; "
        f"padding: 2px 8px; border-radius: 12px; border: 1px solid {border_col};'>{badge_lbl}</span>"
        "</div>"
        f"<div style='font-size: 1.12rem; font-weight: 700; color: #0f172a; margin-bottom: 4px;'>"
        f"<span style='font-size: 1.6rem; color: {border_col};'>{nb_sig}</span> {desc_text} "
        f"<span style='font-size: 0.85rem; font-weight: 500; color: #64748b;'>(sur {nb_tot} groupes analysés)</span>"
        "</div>"
        f"<div style='font-size: 0.86rem; color: #334155; font-weight: 500; margin-bottom: 8px;'>{stats_line}</div>"
        "<div style='margin-top: 8px; padding-top: 8px; border-top: 1px dashed rgba(15,23,42,0.15); "
        "font-size: 0.84rem; color: #1e293b; line-height: 1.5;'>"
        f"{cibles_line}"
        "</div>"
        "</div>"
    )
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


def _format_cibles_comp(df_c: pd.DataFrame, single_ec: bool) -> str:
    if df_c.empty:
        return "<strong>Cibles :</strong> Aucun groupe en écart significatif"
    df_sig = df_c[df_c["Ecart_Significatif"]].copy()
    if df_sig.empty:
        return "<strong>Cibles :</strong> Aucun groupe ne dépasse le seuil configuré"
    vc_m = df_sig["Matiere"].astype(str).value_counts()
    m_str = " &gt; ".join(vc_m.head(5).index.tolist())
    line1 = f"<div><strong>{len(vc_m)} Cours :</strong> {m_str}</div>"
    if single_ec:
        top_g = df_sig["Matiere_Groupe"].astype(str).head(5).tolist()
        line2 = f"<div style='margin-top:2px;'><strong>{len(top_g)} Groupes :</strong> {' &gt; '.join(top_g)}</div>"
    else:
        vc_e = df_sig["École"].astype(str).value_counts().head(5)
        top_g = df_sig["Groupe"].astype(str).head(5).tolist()
        line2 = (
            f"<div style='margin-top:2px;'><strong>{len(vc_e)} Écoles :</strong> {' &gt; '.join(vc_e.index.tolist())} "
            f"| <strong>Top groupes :</strong> {', '.join(top_g[:3])}</div>"
        )
    return line1 + line2


# Bandeau des 3 cartes de synthèse par famille disciplinaire
cm1, cm2, cm3 = st.columns(3)
with cm1:
    nb_m_tot = len(df_comp_math)
    nb_m_sig = int(df_comp_math["Ecart_Significatif"].sum()) if not df_comp_math.empty else 0
    if not df_comp_math.empty:
        moy_res_net = df_comp_math["Moy_Resoudre"].mean()
        moy_rai_net = df_comp_math["Moy_Raisonner"].mean()
        stat_m_txt = f"Moyennes groupes : Résoudre {moy_res_net:.1f} % vs Raisonner {moy_rai_net:.1f} % (Écart moyen : {moy_res_net - moy_rai_net:+.1f} pts)"
    else:
        stat_m_txt = "Aucune donnée de compétences Mathématiques (63410/63420, 65410/65420, 64410/64420)."
    _render_micro_comp_card(
        title="📐 Mathématiques : Résoudre vs Raisonner",
        nb_sig=nb_m_sig,
        nb_tot=nb_m_tot,
        desc_text="groupes avec écart significatif entre Résoudre (30%) et Raisonner (70%)",
        stats_line=stat_m_txt,
        cibles_line=_format_cibles_comp(df_comp_math, single_school_micro),
        border_col="#1472BF",
        bg_col="#f0f7ff",
        badge_lbl="C1 vs C2"
    )

with cm2:
    nb_s_tot = len(df_comp_sci)
    nb_s_sig = int(df_comp_sci["Ecart_Significatif"].sum()) if not df_comp_sci.empty else 0
    if not df_comp_sci.empty:
        moy_pra_net = df_comp_sci["Moy_Pratique"].mean()
        moy_the_net = df_comp_sci["Moy_Théorie"].mean() if "Moy_Théorie" in df_comp_sci.columns else df_comp_sci["Moy_Theorie"].mean()
        stat_s_txt = f"Moyennes groupes : Pratique {moy_pra_net:.1f} % vs Théorie {moy_the_net:.1f} % (Écart moyen : {moy_pra_net - moy_the_net:+.1f} pts)"
    else:
        stat_s_txt = "Aucune donnée de compétences Sciences (55410/55420, 57410/57420)."
    _render_micro_comp_card(
        title="🧪 Sciences : Pratique vs Théorie",
        nb_sig=nb_s_sig,
        nb_tot=nb_s_tot,
        desc_text="groupes avec écart significatif entre Pratique (40%) et Théorie (60%)",
        stats_line=stat_s_txt,
        cibles_line=_format_cibles_comp(df_comp_sci, single_school_micro),
        border_col="#d97706",
        bg_col="#fffbeb",
        badge_lbl="Labo vs Théorie"
    )

with cm3:
    nb_f_tot = len(df_comp_fra)
    nb_f_sig = int(df_comp_fra["Ecart_Significatif"].sum()) if not df_comp_fra.empty else 0
    if not df_comp_fra.empty:
        m_o = df_comp_fra["Moy_Oral"].mean()
        m_l = df_comp_fra["Moy_Lecture"].mean()
        m_e = df_comp_fra["Moy_Ecriture"].mean()
        amp_m = df_comp_fra["Amplitude_Max"].mean()
        stat_f_txt = f"Moyennes : Oral {m_o:.1f} % | Lecture {m_l:.1f} % | Écriture {m_e:.1f} % (Amplitude moy. : {amp_m:.1f} pts)"
    else:
        stat_f_txt = "Aucune donnée de compétences Français (Lecture 10, Écriture 20, Oral 30)."
    _render_micro_comp_card(
        title="📖 Français : Oral, Lecture & Écriture",
        nb_sig=nb_f_sig,
        nb_tot=nb_f_tot,
        desc_text="groupes avec distorsion significative entre Oral (20%), Lecture (40%) et Écriture (40%)",
        stats_line=stat_f_txt,
        cibles_line=_format_cibles_comp(df_comp_fra, single_school_micro),
        border_col="#dc2626",
        bg_col="#fef2f2",
        badge_lbl="Tripartite"
    )

# --- SOUS-SECTION 2.A : MATHÉMATIQUES (RÉSOUDRE VS RAISONNER) ---
st.markdown("#### A. Mathématiques (CST, SN, TS) : Comparaison Résoudre (C1 — 30 %) vs Raisonner (C2 — 70 %) dans les groupes-écoles")
if not df_comp_math.empty:
    col_m_left, col_m_right = st.columns([1.15, 1.0])
    with col_m_left:
        df_m_plot = df_comp_math.head(30).copy()
        df_m_plot["Label_Court"] = df_m_plot["Groupe"].astype(str) + " (" + df_m_plot["Matiere"].astype(str) + ")"
        df_m_plot["Statut_Visuel"] = np.where(
            ~df_m_plot["Ecart_Significatif"],
            "Cohérent (Écart normal)",
            np.where(
                df_m_plot["Ecart_Pts"] > 0,
                "Résoudre >> Raisonner (Sur-notation C1)",
                "Résoudre << Raisonner (Sévérité C1)"
            )
        )
        fig_m_bar = px.bar(
            df_m_plot.sort_values(by="Ecart_Pts", ascending=True),
            x="Ecart_Pts",
            y="Label_Court",
            color="Statut_Visuel",
            orientation="h",
            color_discrete_map={
                "Résoudre >> Raisonner (Sur-notation C1)": DANGER_QUEBEC,
                "Résoudre << Raisonner (Sévérité C1)": SECONDARY_QUEBEC,
                "Cohérent (Écart normal)": "#94a3b8"
            },
            hover_data=["École", "Effectif", "Moy_Resoudre", "Moy_Raisonner", "Cohen_D", "P_Value"],
            labels={
                "Ecart_Pts": "Écart Δ = Moy. Résoudre − Moy. Raisonner (pts)",
                "Label_Court": "Groupe-École (Cours)",
                "Statut_Visuel": "Diagnostic C1 vs C2"
            },
            title="Écart entre Résoudre (C1) et Raisonner (C2) par groupe-école (Top 30 écarts)"
        )
        fig_m_bar.add_vline(x=seuil_ecart_comp, line_dash="dash", line_color=DANGER_QUEBEC)
        fig_m_bar.add_vline(x=-seuil_ecart_comp, line_dash="dash", line_color=SECONDARY_QUEBEC)
        fig_m_bar.add_vline(x=0, line_color="#334155")
        st.plotly_chart(apply_standard_layout(fig_m_bar, height=460), use_container_width=True)

    with col_m_right:
        fig_m_scat = px.scatter(
            df_comp_math,
            x="Moy_Raisonner",
            y="Moy_Resoudre",
            color="Matiere",
            symbol="Ecart_Significatif",
            size="Effectif",
            hover_name="Groupe",
            hover_data=["École", "Ecart_Pts", "Cohen_D", "P_Value", "Diagnostic"],
            labels={
                "Moy_Raisonner": "Moyenne C2 — Raisonner (%)",
                "Moy_Resoudre": "Moyenne C1 — Résoudre (%)",
                "Ecart_Significatif": "Écart significatif"
            },
            title="Croisement Résoudre (Y) vs Raisonner (X) par Groupe-École"
        )
        fig_m_scat.add_shape(type="line", x0=35, y0=35, x1=100, y1=100, line=dict(color="#475569", dash="dot"))
        fig_m_scat.add_shape(type="line", x0=35, y0=35 + seuil_ecart_comp, x1=100 - seuil_ecart_comp, y1=100, line=dict(color=DANGER_QUEBEC, dash="dash", width=1))
        fig_m_scat.add_shape(type="line", x0=35 + seuil_ecart_comp, y0=35, x1=100, y1=100 - seuil_ecart_comp, line=dict(color=SECONDARY_QUEBEC, dash="dash", width=1))
        st.plotly_chart(apply_standard_layout(fig_m_scat, height=460), use_container_width=True)

    df_m_sig = df_comp_math[df_comp_math["Ecart_Significatif"]].copy()
    if not df_m_sig.empty:
        with st.expander(f"Consulter les {len(df_m_sig)} groupe(s) de Mathématiques avec écart significatif Résoudre vs Raisonner", expanded=False):
            st.dataframe(sanitize_df_for_stlite(df_m_sig[[
                "École", "Groupe", "Matiere", "Effectif", "Moy_Resoudre", "Moy_Raisonner",
                "Ecart_Pts", "Cohen_D", "P_Value", "Diagnostic"
            ]].rename(columns={
                "Effectif": "N",
                "Moy_Resoudre": "Moy. Résoudre (%)",
                "Moy_Raisonner": "Moy. Raisonner (%)",
                "Ecart_Pts": "Écart C1-C2 (pts)",
                "Cohen_D": "d de Cohen",
                "P_Value": "p-value"
            })), use_container_width=True)
else:
    st.info("Aucune donnée de compétences Mathématiques (codes 63410/63420, 65410/65420, 64410/64420) détectée pour les filtres actifs.")

# --- SOUS-SECTION 2.B : SCIENCES (PRATIQUE VS THÉORIE) ---
st.markdown("#### B. Sciences (ST & ATS) : Comparaison Pratique (C1 — 40 %) vs Théorie (C2 — 60 %) dans les groupes-écoles")
if not df_comp_sci.empty:
    col_s_left, col_s_right = st.columns([1.15, 1.0])
    with col_s_left:
        df_s_plot = df_comp_sci.head(30).copy()
        df_s_plot["Label_Court"] = df_s_plot["Groupe"].astype(str) + " (" + df_s_plot["Matiere"].astype(str) + ")"
        df_s_plot["Statut_Visuel"] = np.where(
            ~df_s_plot["Ecart_Significatif"],
            "Cohérent (Écart normal)",
            np.where(
                df_s_plot["Ecart_Pts"] > 0,
                "Pratique >> Théorie (Effet coussin labo)",
                "Pratique << Théorie (Sévérité labo)"
            )
        )
        fig_s_bar = px.bar(
            df_s_plot.sort_values(by="Ecart_Pts", ascending=True),
            x="Ecart_Pts",
            y="Label_Court",
            color="Statut_Visuel",
            orientation="h",
            color_discrete_map={
                "Pratique >> Théorie (Effet coussin labo)": ACCENT_QUEBEC,
                "Pratique << Théorie (Sévérité labo)": SECONDARY_QUEBEC,
                "Cohérent (Écart normal)": "#94a3b8"
            },
            hover_data=["École", "Effectif", "Moy_Pratique", "Moy_Theorie", "Cohen_D", "P_Value"],
            labels={
                "Ecart_Pts": "Écart Δ = Moy. Pratique − Moy. Théorie (pts)",
                "Label_Court": "Groupe-École (Cours)",
                "Statut_Visuel": "Diagnostic Pratique vs Théorie"
            },
            title="Écart entre Pratique (40 %) et Théorie (60 %) par groupe-école (Top 30 écarts)"
        )
        fig_s_bar.add_vline(x=seuil_ecart_comp, line_dash="dash", line_color=ACCENT_QUEBEC)
        fig_s_bar.add_vline(x=-seuil_ecart_comp, line_dash="dash", line_color=SECONDARY_QUEBEC)
        fig_s_bar.add_vline(x=0, line_color="#334155")
        st.plotly_chart(apply_standard_layout(fig_s_bar, height=460), use_container_width=True)

    with col_s_right:
        fig_s_scat = px.scatter(
            df_comp_sci,
            x="Moy_Theorie",
            y="Moy_Pratique",
            color="Matiere",
            symbol="Ecart_Significatif",
            size="Effectif",
            hover_name="Groupe",
            hover_data=["École", "Ecart_Pts", "Cohen_D", "P_Value", "Diagnostic"],
            labels={
                "Moy_Theorie": "Moyenne C2 — Théorie (%)",
                "Moy_Pratique": "Moyenne C1 — Pratique (%)",
                "Ecart_Significatif": "Écart significatif"
            },
            title="Croisement Pratique (Y) vs Théorie (X) par Groupe-École"
        )
        fig_s_scat.add_shape(type="line", x0=35, y0=35, x1=100, y1=100, line=dict(color="#475569", dash="dot"))
        fig_s_scat.add_shape(type="line", x0=35, y0=35 + seuil_ecart_comp, x1=100 - seuil_ecart_comp, y1=100, line=dict(color=ACCENT_QUEBEC, dash="dash", width=1))
        fig_s_scat.add_shape(type="line", x0=35 + seuil_ecart_comp, y0=35, x1=100, y1=100 - seuil_ecart_comp, line=dict(color=SECONDARY_QUEBEC, dash="dash", width=1))
        st.plotly_chart(apply_standard_layout(fig_s_scat, height=460), use_container_width=True)

    df_s_sig = df_comp_sci[df_comp_sci["Ecart_Significatif"]].copy()
    if not df_s_sig.empty:
        with st.expander(f"Consulter les {len(df_s_sig)} groupe(s) de Sciences avec écart significatif Pratique vs Théorie", expanded=False):
            st.dataframe(sanitize_df_for_stlite(df_s_sig[[
                "École", "Groupe", "Matiere", "Effectif", "Moy_Pratique", "Moy_Theorie",
                "Ecart_Pts", "Cohen_D", "P_Value", "Diagnostic"
            ]].rename(columns={
                "Effectif": "N",
                "Moy_Pratique": "Moy. Pratique (%)",
                "Moy_Theorie": "Moy. Théorie (%)",
                "Ecart_Pts": "Écart Pratique-Théorie (pts)",
                "Cohen_D": "d de Cohen",
                "P_Value": "p-value"
            })), use_container_width=True)
else:
    st.info("Aucune donnée de compétences Sciences (codes 55410/55420, 57410/57420) détectée pour les filtres actifs.")

# --- SOUS-SECTION 2.C : FRANÇAIS (ORAL, LECTURE ET ÉCRITURE) ---
st.markdown("#### C. Français (4e & 5e sec.) : Comparaison tripartite Oral (20 %) — Lecture (40 %) — Écriture (40 %) dans les groupes-écoles")
if not df_comp_fra.empty:
    col_f_left, col_f_right = st.columns([1.15, 1.0])
    with col_f_left:
        df_f_top = df_comp_fra.head(25).copy()
        df_f_top["Label_Court"] = df_f_top["Groupe"].astype(str) + " (" + df_f_top["Matiere"].astype(str) + ")"
        df_f_melt = df_f_top.melt(
            id_vars=["Label_Court", "École", "Matiere", "Effectif", "Amplitude_Max", "Diagnostic"],
            value_vars=["Moy_Oral", "Moy_Lecture", "Moy_Ecriture"],
            var_name="Competence",
            value_name="Moyenne"
        )
        df_f_melt["Competence"] = df_f_melt["Competence"].replace({
            "Moy_Oral": "Oral (20 %)",
            "Moy_Lecture": "Lecture (40 %)",
            "Moy_Ecriture": "Écriture (40 %)"
        })
        fig_f_grp = px.bar(
            df_f_melt,
            x="Label_Court",
            y="Moyenne",
            color="Competence",
            barmode="group",
            color_discrete_map={
                "Oral (20 %)": "#0ea5e9",
                "Lecture (40 %)": PRIMARY_QUEBEC,
                "Écriture (40 %)": DANGER_QUEBEC
            },
            hover_data=["École", "Effectif", "Amplitude_Max", "Diagnostic"],
            labels={
                "Label_Court": "Groupe-École (Cours)",
                "Moyenne": "Moyenne du groupe (%)",
                "Competence": "Compétence"
            },
            title="Comparaison directe Oral, Lecture et Écriture par groupe-école (Top 25 distorsions)"
        )
        fig_f_grp.add_hline(y=60, line_dash="dot", line_color="#dc2626", annotation_text="Seuil 60 %")
        fig_f_grp.update_xaxes(tickangle=45)
        st.plotly_chart(apply_standard_layout(fig_f_grp, height=460), use_container_width=True)

    with col_f_right:
        df_f_ecarts = df_comp_fra.head(25).copy()
        df_f_ecarts["Label_Court"] = df_f_ecarts["Groupe"].astype(str) + " (" + df_f_ecarts["Matiere"].astype(str) + ")"
        df_f_ec_melt = df_f_ecarts.melt(
            id_vars=["Label_Court", "École", "Diagnostic"],
            value_vars=["Ecart_Oral_Ecriture", "Ecart_Lecture_Ecriture", "Ecart_Oral_Lecture"],
            var_name="Paire",
            value_name="Ecart_Pts"
        )
        df_f_ec_melt["Paire"] = df_f_ec_melt["Paire"].replace({
            "Ecart_Oral_Ecriture": "Oral − Écriture",
            "Ecart_Lecture_Ecriture": "Lecture − Écriture",
            "Ecart_Oral_Lecture": "Oral − Lecture"
        })
        fig_f_ec = px.bar(
            df_f_ec_melt,
            x="Ecart_Pts",
            y="Label_Court",
            color="Paire",
            barmode="group",
            orientation="h",
            color_discrete_map={
                "Oral − Écriture": DANGER_QUEBEC,
                "Lecture − Écriture": ACCENT_QUEBEC,
                "Oral − Lecture": SECONDARY_QUEBEC
            },
            labels={
                "Ecart_Pts": "Écart entre compétences (pts)",
                "Label_Court": "Groupe-École",
                "Paire": "Couple comparé"
            },
            title="Écarts croisés (Oral−Écriture, Lecture−Écriture, Oral−Lecture)"
        )
        fig_f_ec.add_vline(x=seuil_ecart_comp, line_dash="dash", line_color=DANGER_QUEBEC)
        fig_f_ec.add_vline(x=-seuil_ecart_comp, line_dash="dash", line_color=SECONDARY_QUEBEC)
        fig_f_ec.add_vline(x=0, line_color="#334155")
        st.plotly_chart(apply_standard_layout(fig_f_ec, height=460), use_container_width=True)

    df_f_sig = df_comp_fra[df_comp_fra["Ecart_Significatif"]].copy()
    if not df_f_sig.empty:
        with st.expander(f"Consulter les {len(df_f_sig)} groupe(s) de Français avec distorsion significative Oral / Lecture / Écriture", expanded=False):
            st.dataframe(sanitize_df_for_stlite(df_f_sig[[
                "École", "Groupe", "Matiere", "Effectif", "Moy_Oral", "Moy_Lecture", "Moy_Ecriture",
                "Ecart_Oral_Ecriture", "Ecart_Lecture_Ecriture", "Ecart_Oral_Lecture",
                "Amplitude_Max", "Cohen_D", "P_Value", "Diagnostic"
            ]].rename(columns={
                "Effectif": "N",
                "Moy_Oral": "Moy. Oral (%)",
                "Moy_Lecture": "Moy. Lecture (%)",
                "Moy_Ecriture": "Moy. Écriture (%)",
                "Ecart_Oral_Ecriture": "Δ Oral-Écr.",
                "Ecart_Lecture_Ecriture": "Δ Lect.-Écr.",
                "Ecart_Oral_Lecture": "Δ Oral-Lect.",
                "Amplitude_Max": "Amplitude Max (pts)",
                "Cohen_D": "d max",
                "P_Value": "p-value min"
            })), use_container_width=True)
else:
    st.info("Aucune donnée de compétences Français (codes 132410/20/30, 132510/20/30) détectée pour les filtres actifs.")

render_explainer("competences_micro")

st.markdown("---")

# -----------------------------------------------------------------------------
# 3. DÉTECTION DE LA SÉGRÉGATION INTRA-ÉCOLE (DISPERSION DES GROUPES RÉGULIERS)
# -----------------------------------------------------------------------------
st.subheader("3. Composition des classes : y a-t-il une ségrégation anormale entre groupes réguliers d'une même école ?")
st.markdown("""
**Principe docimologique :** Les groupes **80-85 (EHDAA)** et **90-99 (cas particuliers)** sont **exclus** de cette analyse.
On compare uniquement les taux de réussite des groupes réguliers au sein de chaque établissement.
Un écart-type élevé entre les groupes d'une même école révèle une constitution asymétrique des classes (ségrégation pédagogique interne).
""")

# Filtrer strictement les groupes réguliers pour les cours évalués (Note globale)
# Exclure les cours non sanctionnés / notes manquantes, les composantes et les écoles d'adaptation scolaire
mask_reg = (
    df_sub["RESLT_FINAL"].notna() &
    (df_sub["Type_Cours"] == "Note globale") &
    (df_sub["Type_Groupe"] == "Régulier") &
    (~df_sub["CD_ORGNS"].isin(ECOLES_ADAPTATION))
)
df_reguliers = df_sub[mask_reg].copy()

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
# 4. ANALYSE RAFFINÉE DE L'ÉCRASEMENT DES NOTES & OUTLIERS DE RATIO
# -----------------------------------------------------------------------------
st.subheader("4. Outliers de sanction : quelles classes profitent d'un écrasement massif ou subissent une pénalité critique ?")
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
# 5. PANNEAU D'ACTION DYNAMIQUE (LAD P2)
# -----------------------------------------------------------------------------
st.markdown("---")
render_action_panel(
    question="Quelles classes présentent un écart significatif entre compétences d'une même matière, une ségrégation interne ou un décalage critique d'écrasement ?",
    constat_dynamique=(
        f"L'analyse intra-matière par groupe-école (seuil Δ ≥ {seuil_ecart_comp:.0f} pts, N ≥ {min_eleves_micro}) révèle "
        f"{nb_m_sig} groupe(s) en écart significatif en Mathématiques (Résoudre vs Raisonner), "
        f"{nb_s_sig} groupe(s) en Sciences (Pratique vs Théorie) et "
        f"{nb_f_sig} groupe(s) en Français (Oral, Lecture et Écriture)."
    ),
    pistes=[
        "**Harmonisation Mathématiques (Résoudre vs Raisonner) :** Dans les groupes où Résoudre (C1) s'écarte significativement de Raisonner (C2), réviser le calibrage des situations-problèmes locales et la grille d'évaluation descriptive.",
        "**Régulation Sciences (Pratique vs Théorie) :** Lorsque la note Pratique dépasse fortement la Théorie (effet coussin de laboratoire), renforcer l'évaluation individuelle de la démarche scientifique et des concepts théoriques associés aux manipulations.",
        "**Rééquilibrage Français (Oral, Lecture et Écriture) :** Pour les groupes présentant une distorsion entre Oral, Lecture et Écriture, cibler les ateliers d'écriture et d'inférence en lecture tout en harmonisant les critères d'évaluation de la communication orale.",
        "**Rééquilibrage de la composition des groupes :** Pour les écoles où l'écart-type entre classes régulières dépasse 15%, réviser les critères de répartition des élèves à la rentrée scolaire."
    ],
    context_tag=f"Seuil N ≥ {min_eleves_micro} | Δ ≥ {seuil_ecart_comp:.0f} pts"
)

render_explainer("ecrasement")
render_about_data(
    source_name="Fichier cohorte CHAP060105.csv",
    limits=[
        "Les groupes EHDAA (80-85) et cas particuliers (90-99) sont exclus de l'analyse de ségrégation pour isoler les dynamiques des classes ordinaires.",
        "L'écrasement des notes est une mesure de sanction ministérielle appliquée à l'avantage de l'élève ($NMC \\ge NEM$)."
    ]
)
