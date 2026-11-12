# -*- coding: utf-8 -*-
"""
pages/1_Pilotage_Strategique_Equite.py - LAD Niveau 1 : Tableau de bord MACRO (Direction générale & DSE).
Conçu selon Voyer (2011) / Dumaresq (2017) sous la charte officielle Bleu Québec.
Répond aux 4 questions stratégiques : cibles PEVR, portrait des vulnérables, synergie des matières, priorités d'intervention.
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
    clean_cd_orgns, ECOLES_LIST, SUBJECT_MAP, CODE_TO_MATIERE_COURT,
    get_course_level, ENRICHED_CODES, RETAC_LIST, get_ecoles_for_retac,
    get_retac_for_ecole, SANCTION_4E_MATIERES, ECOLES_NOMS, ECOLES_ADAPTATION,
    get_ecole_nom
)
from core.state import (
    get_df_main, get_df_moderation, get_df_aout, set_df_aout
)
from core.metrics import (
    wilson_interval, compute_cohen_d, compute_failure_correlations
)
from core.privacy import filter_small_cells
from core.data_loader import clean_moderation_df, sanitize_df_for_stlite, load_csv_robust
from ui.theme import (
    BLEU_QUEBEC, BLEU_QUEBEC_LIGHT, PALETTE_ACCESSIBLE,
    PRIMARY_QUEBEC, SECONDARY_QUEBEC, ACCENT_QUEBEC, DANGER_QUEBEC, SUCCESS_QUEBEC,
    inject_quebec_theme
)
from ui.kpi_cards import render_kpi_card
from ui.charts import (
    plot_venn3_plotly, apply_standard_layout, download_csv_button,
    plot_janosz_bars, plot_janosz_matrix_2d
)
from ui.action_panel import render_action_panel
from ui.explainers import render_explainer, render_about_data
from ui.filters import render_sidebar_filters

st.set_page_config(
    page_title="1. Macro : Pilotage Systémique & Diplomation",
    layout="wide"
)
inject_quebec_theme()

st.title("1. Macro : Pilotage Systémique & Diplomation")
st.warning("🎯 **Axe d'analyse : Risque d'échec systémique & de contagion disciplinaire** — Identifier les goulots d'étranglement bloquant l'atteinte des cibles du PEVR.")

df_main = get_df_main()
df_mod_raw = get_df_moderation()

if df_main.empty and df_mod_raw.empty:
    st.info("Veuillez téléverser vos fichiers scolaires (CHAP060105 et/ou CHS040506R) depuis la page d'accueil pour générer le tableau de bord.")
    st.stop()

# -----------------------------------------------------------------------------
# FILTRES PERSISTANTS DANS LA BARRE LATÉRALE
# -----------------------------------------------------------------------------
filters = render_sidebar_filters(
    show_retac=True,
    show_ecoles=True,
    show_matieres=False,
    show_enriched=True,
    show_thresholds=True,
    show_teacher_opt_in=False,
    multi_ecoles=False
)

selected_retac = filters.get("selected_retac", "Tous")
selected_ecole = filters.get("selected_ecole", "Toutes")
filter_enriched = filters.get("filter_enriched", False)
seuil_effet = filters.get("seuil_cohen", 0.8)

# Slider de filtrage des petits groupes pour stabiliser les calculs de taux et pourcentages
st.sidebar.markdown("---")
st.sidebar.subheader("Échantillonnage & Seuils (Macro)")
min_group_size = st.sidebar.slider(
    "Taille minimale des groupes (Nb. élèves) :",
    min_value=0,
    max_value=20,
    value=16,
    step=1,
    help="Filtre les micro-groupes ou effectifs inférieurs à ce seuil (0 à 20, défaut 16) dans les calculs de pourcentages et taux d'échec pour stabiliser les distributions statistiques."
)

# -----------------------------------------------------------------------------
# 1. QUESTION PEVR & BANDEAU DES 3 KPIS STRATÉGIQUES
# -----------------------------------------------------------------------------
st.markdown("### 1. Écart aux cibles PEVR et volume global d'élèves sous le seuil de passage")

taux_reussite = 0.0
total_eleves = 0
ci_reussite = (0.0, 0.0)

df_f = df_main.copy() if not df_main.empty else pd.DataFrame()
if not df_f.empty:
    # Filtrage RETAC
    if selected_retac != "Tous" and "CD_ORGNS" in df_f.columns:
        retac_ecoles = set(get_ecoles_for_retac(selected_retac))
        df_f = df_f[df_f["CD_ORGNS"].isin(retac_ecoles)]

    if selected_ecole != "Toutes" and "CD_ORGNS" in df_f.columns:
        df_f = df_f[df_f["CD_ORGNS"] == selected_ecole]

    if filter_enriched and "CD_PERMN" in df_f.columns and "CD_COURS_str" in df_f.columns:
        enr_set = set(df_f.loc[df_f["CD_COURS_str"].isin(ENRICHED_CODES), "CD_PERMN"].unique())
        df_f = df_f[~df_f["CD_PERMN"].isin(enr_set)]

    if "Reussite" in df_f.columns and "CD_PERMN" in df_f.columns:
        if "Type_Cours" in df_f.columns:
            df_final = df_f[df_f["Type_Cours"] == "Note globale"].drop_duplicates(subset=["CD_PERMN"])
        else:
            df_final = pd.DataFrame()
        if df_final.empty:
            df_final = df_f.drop_duplicates(subset=["CD_PERMN"])
        if not df_final.empty:
            succ = int(df_final["Reussite"].sum())
            total_eleves = int(df_final["CD_PERMN"].nunique())
            taux_reussite = (succ / total_eleves) * 100.0 if total_eleves > 0 else 0.0
            ci_reussite = wilson_interval(succ, total_eleves, 0.95)
            ci_reussite = (ci_reussite[0] * 100.0, ci_reussite[1] * 100.0)

df_mod = clean_moderation_df(df_mod_raw) if not df_mod_raw.empty else pd.DataFrame()
if not df_mod.empty:
    if selected_retac != "Tous" and "Organisme" in df_mod.columns:
        retac_ecoles = set(get_ecoles_for_retac(selected_retac))
        df_mod = df_mod[df_mod["Organisme"].isin(retac_ecoles)]
    if selected_ecole != "Toutes" and "Organisme" in df_mod.columns:
        df_mod = df_mod[df_mod["Organisme"] == selected_ecole]

ecart_moyen_mod = 0.0
pct_ecrasement = 0.0
total_groupes_mod = 0

if not df_mod.empty and "Moyenne_ecole" in df_mod.columns and "Moyenne_min" in df_mod.columns:
    df_mod["Delta_Moyenne"] = df_mod["Moyenne_ecole"] - df_mod["Moyenne_min"]
    ecart_moyen_mod = float(df_mod["Delta_Moyenne"].mean())
    total_groupes_mod = len(df_mod)

    if "NEB_60" in df_mod.columns:
        nb_ecrase = int((df_mod["NEB_60"] > 60).sum())
        pct_ecrasement = (nb_ecrase / total_groupes_mod) * 100.0 if total_groupes_mod > 0 else 0.0
    else:
        nb_ecrase = int((df_mod["Delta_Moyenne"] < -2.0).sum())
        pct_ecrasement = (nb_ecrase / total_groupes_mod) * 100.0 if total_groupes_mod > 0 else 0.0

stat_reussite = "success" if taux_reussite >= 80.0 else ("warning" if taux_reussite >= 70.0 else "danger")
stat_mod = "success" if abs(ecart_moyen_mod) <= 2.0 else ("warning" if abs(ecart_moyen_mod) <= 5.0 else "danger")
stat_ecras = "success" if pct_ecrasement < 20.0 else ("warning" if pct_ecrasement <= 40.0 else "danger")

# Calcul du Taux de diplomation brute et accès au bloc de sanction de 4e
# (Proportion d'élèves de 4e sec. validant simultanément Maths CST/SN/TS, Sciences ST/ATS et Histoire QC-Canada)
taux_bloc_4e = 0.0
total_bloc_4e = 0
succ_bloc_4e = 0
ci_bloc_4e = (0.0, 0.0)

if not df_f.empty and "CD_COURS_str" in df_f.columns and "RESLT_FINAL" in df_f.columns and "CD_PERMN" in df_f.columns:
    df_f["Niveau_Sec"] = df_f["CD_COURS_str"].apply(get_course_level)
    df_f["Matiere_Simple"] = df_f["CD_COURS_str"].map(CODE_TO_MATIERE_COURT)
    df_sanct_4 = df_f[df_f["Matiere_Simple"].isin(SANCTION_4E_MATIERES)].copy()
    if not df_sanct_4.empty:
        df_sanct_4["RESLT_FINAL"] = pd.to_numeric(df_sanct_4["RESLT_FINAL"], errors="coerce")
        inscr_m = set(df_sanct_4[df_sanct_4["Matiere_Simple"].isin(["Math CST", "Math SN", "Math TS"])]["CD_PERMN"])
        inscr_s = set(df_sanct_4[df_sanct_4["Matiere_Simple"].isin(["Science ST", "Science ATS"])]["CD_PERMN"])
        inscr_h = set(df_sanct_4[df_sanct_4["Matiere_Simple"] == "Histoire 4"]["CD_PERMN"])

        pass_m = set(df_sanct_4[(df_sanct_4["Matiere_Simple"].isin(["Math CST", "Math SN", "Math TS"])) & (df_sanct_4["RESLT_FINAL"] >= 60.0)]["CD_PERMN"])
        pass_s = set(df_sanct_4[(df_sanct_4["Matiere_Simple"].isin(["Science ST", "Science ATS"])) & (df_sanct_4["RESLT_FINAL"] >= 60.0)]["CD_PERMN"])
        pass_h = set(df_sanct_4[(df_sanct_4["Matiere_Simple"] == "Histoire 4") & (df_sanct_4["RESLT_FINAL"] >= 60.0)]["CD_PERMN"])

        eleves_3_blocs = inscr_m & inscr_s & inscr_h
        if len(eleves_3_blocs) > 0:
            total_bloc_4e = len(eleves_3_blocs)
            succ_bloc_4e = len(pass_m & pass_s & pass_h & eleves_3_blocs)
        else:
            # Fallback si un sous-ensemble de matières seulement est présent dans l'extrait
            all_4e_ids = set(df_sanct_4["CD_PERMN"].unique())
            fail_4e_ids = set(df_sanct_4[df_sanct_4["RESLT_FINAL"] < 60.0]["CD_PERMN"].unique())
            total_bloc_4e = len(all_4e_ids)
            succ_bloc_4e = len(all_4e_ids - fail_4e_ids)

        if total_bloc_4e > 0:
            taux_bloc_4e = (succ_bloc_4e / total_bloc_4e) * 100.0
            ci_b4 = wilson_interval(succ_bloc_4e, total_bloc_4e, 0.95)
            ci_bloc_4e = (ci_b4[0] * 100.0, ci_b4[1] * 100.0)

stat_bloc_4e = "success" if taux_bloc_4e >= 80.0 else ("warning" if taux_bloc_4e >= 70.0 else "danger")

k1, k2, k3, k4 = st.columns(4)
with k1:
    render_kpi_card(
        title="Taux de réussite global",
        value=taux_reussite,
        status=stat_reussite,
        n=total_eleves,
        ci=ci_reussite if total_eleves > 0 else None,
        subtitle="Proportion ayant réussi la note globale (60%)",
        target="Cible PEVR : ≥ 80.0%",
        help_text="Matières considérées : Français 4/5, Math CST/SN/TS, Science ST/ATS, Histoire, Anglais."
    )

with k2:
    render_kpi_card(
        title="Validation simultanée du Bloc 4e",
        value=taux_bloc_4e,
        status=stat_bloc_4e,
        n=total_bloc_4e,
        ci=ci_bloc_4e if total_bloc_4e > 0 else None,
        subtitle="Réussite conjointe Maths + Sciences + Histoire",
        target="Cible PEVR : ≥ 80.0%",
        help_text="Proportion d'élèves de 4e secondaire validant simultanément Maths (CST/SN/TS), Sciences (ST/ATS) et Histoire QC-Canada (IC Wilson 95%)."
    )

with k3:
    render_kpi_card(
        title="Écart moyen de modération (NEB - NMC)",
        value=f"{ecart_moyen_mod:+.1f}%",
        status=stat_mod,
        n=total_groupes_mod,
        subtitle="Écart évaluation locale vs épreuve ministérielle",
        target="Cible : ±2.0%",
        help_text="Matières considérées : Épreuves uniques ministérielles (Français, Maths, Sciences, Histoire)."
    )

with k4:
    render_kpi_card(
        title="Groupes soumis à décote / écrasement",
        value=pct_ecrasement,
        status=stat_ecras,
        n=total_groupes_mod,
        subtitle="Proportion avec note école diminuée",
        target="Cible : < 20.0%",
        help_text="Matières considérées : Épreuves uniques ministérielles."
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. PROFILS DES ÉCHECS AUX MATIÈRES À SANCTION (4E ET 5E SECONDAIRE)
# -----------------------------------------------------------------------------
st.markdown("### 2. Cumul des vulnérabilités : combien d'élèves échouent dans 1, 2 ou 3 matières à sanction ?")

if not df_f.empty and "CD_COURS_str" in df_f.columns and "RESLT_FINAL" in df_f.columns:
    df_f["Niveau_Sec"] = df_f["CD_COURS_str"].apply(get_course_level)
    df_f["Matiere_Simple"] = df_f["CD_COURS_str"].map(CODE_TO_MATIERE_COURT)

    tab_4e, tab_5e = st.tabs(["4e Secondaire (Sciences / Maths / Histoire)", "5e Secondaire (Français / Anglais / Maths)"])

    # --- VOLET 4E SECONDAIRE ---
    with tab_4e:
        df_4e = df_f[df_f["Niveau_Sec"] == 4].copy()
        df_echecs_4e = df_4e[df_4e["RESLT_FINAL"] < 60].copy()

        set_sci = set(df_echecs_4e[df_echecs_4e["Matiere_Simple"].isin(["Science ST", "Science ATS"])]["CD_PERMN"])
        set_math = set(df_echecs_4e[df_echecs_4e["Matiere_Simple"].isin(["Math CST", "Math SN", "Math TS"])]["CD_PERMN"])
        set_hist = set(df_echecs_4e[df_echecs_4e["Matiere_Simple"] == "Histoire 4"]["CD_PERMN"])

        col_venn4, col_bilan4 = st.columns([1.2, 1.8])
        with col_venn4:
            fig_venn4 = plot_venn3_plotly(
                set_sci, set_math, set_hist,
                label_a="Sciences (ST/ATS)",
                label_b="Maths (CST/SN/TS)",
                label_c="Histoire 4",
                title="Venn des Échecs de 4e Secondaire"
            )
            st.plotly_chart(fig_venn4, use_container_width=True)

        with col_bilan4:
            tot_4e = len(set_sci | set_math | set_hist)
            ech_3 = len(set_sci & set_math & set_hist)
            ech_2 = len(((set_sci & set_math) | (set_sci & set_hist) | (set_math & set_hist)) - (set_sci & set_math & set_hist))
            ech_1 = tot_4e - ech_2 - ech_3

            st.markdown(f"""
            <div style='background:{BLEU_QUEBEC_LIGHT}; border-left:4px solid {BLEU_QUEBEC}; padding:14px; border-radius:6px; margin-bottom:12px;'>
                <h4 style='color:{BLEU_QUEBEC}; margin-top:0;'>Bilan de diplomation (4e secondaire) :</h4>
                <ul style='font-size:0.95rem; margin-bottom:0;'>
                    <li><strong>{tot_4e}</strong> élève(s) en échec dans au moins une matière à sanction de 4e</li>
                    <li><strong>{ech_3}</strong> élève(s) cumulant <strong>3 échecs</strong> (Vulnérabilité systémique critique)</li>
                    <li><strong>{ech_2}</strong> élève(s) avec <strong>2 échecs simultanés</strong></li>
                    <li><strong>{ech_1}</strong> élève(s) avec <strong>1 échec simple</strong> (Candidats de repêchage prioritaire)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # Identification dynamique des matières les plus vulnérables parmi les matières à sanction de 4e
            df_echecs_4e_sanction = df_echecs_4e[df_echecs_4e["Matiere_Simple"].isin(SANCTION_4E_MATIERES)].copy()
            counts_by_mat = df_echecs_4e_sanction["Matiere_Simple"].value_counts()
            pire_mat = counts_by_mat.index[0] if not counts_by_mat.empty else "N/A"
            pire_nb = counts_by_mat.iloc[0] if not counts_by_mat.empty else 0

            # Paire la plus fréquente (calcul robuste sans risque de comparaison str / float)
            from itertools import combinations
            paires_list = []
            eleves_grouped = df_echecs_4e_sanction.groupby("CD_PERMN")["Matiere_Simple"].unique()
            for mats in eleves_grouped:
                valid_mats = sorted([str(m).strip() for m in mats if pd.notna(m) and str(m).strip() not in ["", "nan", "None"]])
                if len(valid_mats) >= 2:
                    for pair in combinations(valid_mats, 2):
                        paires_list.append(" & ".join(pair))
            pire_paire = pd.Series(paires_list).value_counts().index[0] if paires_list else "Maths & Sciences"

            st.markdown(f"""
            <div style='background:#fef9ee; border-left:4px solid {ACCENT_QUEBEC}; padding:12px; border-radius:6px; font-size:0.9rem;'>
                <strong>Questionnement stratégique pour la Direction :</strong>
                <ul style='margin-bottom:0;'>
                    <li><em>Comment intervenir sur <strong>{pire_mat}</strong> ({pire_nb} échecs), qui représente le volume de vulnérabilité le plus lourd ?</em></li>
                    <li><em>Quelles mesures didactiques mettre en place pour soutenir les élèves cumulant deux échecs en <strong>{pire_paire}</strong> ?</em></li>
                    <li><em>Quel principe concerté devrait orienter le classement des <strong>{ech_3}</strong> élèves les plus vulnérables avec 3 échecs aux matières à sanction ?</em></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # --- VOLET 5E SECONDAIRE ---
    with tab_5e:
        df_5e = df_f[df_f["Niveau_Sec"] == 5].copy()
        df_echecs_5e = df_5e[df_5e["RESLT_FINAL"] < 60].copy()

        set_fr5 = set(df_echecs_5e[df_echecs_5e["Matiere_Simple"] == "Français 5"]["CD_PERMN"])
        set_ang5 = set(df_echecs_5e[df_echecs_5e["Matiere_Simple"] == "Anglais 5 base"]["CD_PERMN"])
        set_math5 = set(df_echecs_5e[df_echecs_5e["Matiere_Simple"].str.contains("Math", na=False)]["CD_PERMN"])

        col_v5, col_b5 = st.columns([1.2, 1.8])
        with col_v5:
            fig_venn5 = plot_venn3_plotly(
                set_fr5, set_ang5, set_math5,
                label_a="Français 5",
                label_b="Anglais 5",
                label_c="Mathématiques 5",
                title="Venn des Échecs de 5e Secondaire"
            )
            st.plotly_chart(fig_venn5, use_container_width=True)

        with col_b5:
            tot_5e = len(set_fr5 | set_ang5 | set_math5)
            ech_3_5 = len(set_fr5 & set_ang5 & set_math5)
            ech_2_5 = len(((set_fr5 & set_ang5) | (set_fr5 & set_math5) | (set_ang5 & set_math5)) - (set_fr5 & set_ang5 & set_math5))
            ech_1_5 = tot_5e - ech_2_5 - ech_3_5

            st.markdown(f"""
            <div style='background:{BLEU_QUEBEC_LIGHT}; border-left:4px solid {BLEU_QUEBEC}; padding:14px; border-radius:6px;'>
                <h4 style='color:{BLEU_QUEBEC}; margin-top:0;'>Bilan de diplomation immédiate (5e secondaire) :</h4>
                <ul style='font-size:0.95rem; margin-bottom:0;'>
                    <li><strong>{tot_5e}</strong> finissant(s) en situation d'échec dans une matière de 5e</li>
                    <li><strong>{ech_1_5}</strong> élève(s) avec <strong>1 échec simple</strong> (Candidats prioritaires à la diplomation d'août)</li>
                    <li><strong>{ech_2_5 + ech_3_5}</strong> élève(s) avec échecs multiples de 5e</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # --- VISUALISATION DE LA MATRICE DE JANOSZ (PROFIL DE RISQUE & EFFECTIFS) ---
    if "Profil_Janosz" in df_f.columns:
        st.markdown("#### Portrait systémique selon la Matrice de Janosz (Profils de risque & Effectifs)")
        st.plotly_chart(
            plot_janosz_matrix_2d(
                df_f,
                title="Matrice 2D de Janosz (Rendement Académique × Assiduité — Effectifs à risque)",
                height=580
            ),
            use_container_width=True
        )
        with st.expander("📊 Ventilation détaillée des effectifs par catégorie de Janosz", expanded=False):
            incl_nr_m = st.checkbox(
                "Inclure 'Non à risque' dans le dénombrement",
                value=False,
                key="chk_janosz_macro"
            )
            st.plotly_chart(
                plot_janosz_bars(
                    df_f,
                    include_non_risque=incl_nr_m,
                    title="Nombre d'élèves par catégorie de Janosz",
                    height=380
                ),
                use_container_width=True
            )

    # -------------------------------------------------------------------------
    # MATRICE DE CORRÉLATION DES ÉCHECS (COEFFICIENT PHI DE PEARSON & T-TEST)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 3. Dépendance des échecs : quelles disciplines partagent les mêmes difficultés d'apprentissage ?")
    st.caption("""
    **Critères d'analyse stricts :**
    * Filtre **Élèves du régulier seulement** appliqué.
    * **Math SN et TS sont exclues** pour isoler le tronc commun.
    * **Matières ciblées :** Science ST théorie (codes 055410/55410), Science ATS théorie (057410/57410), Math CST et Histoire.
    * Les valeurs diagonales (1.0) et quasi-nulles sont atténuées sur fond pâle. La corrélation significative la plus forte est mise en relief pour guider la décision.
    """)

    # Sélection stricte pour la matrice de corrélation
    # Sciences ST/ATS théorie (se terminant par 410), Math CST et Histoire
    df_regulier_corr = df_f[df_f.get("Parcours", "Régulier") == "Régulier"].copy() if "Parcours" in df_f.columns else df_f.copy()
    
    def normalize_subject_for_corr(row):
        code = str(row.get("CD_COURS_str", "")).strip()
        # Science ST théorie
        if code in ["55410", "055410"]:
            return "Science ST (Théorie)"
        # Science ATS théorie
        elif code in ["57410", "057410"]:
            return "Science ATS (Théorie)"
        # Math CST (exclure SN/TS)
        elif code in ["63414", "063414", "63420", "063420"]:
            return "Math CST"
        # Histoire 4
        elif code in ["85404", "085404", "585404", "0585404"]:
            return "Histoire 4"
        return None

    df_regulier_corr["Matiere_Corr"] = df_regulier_corr.apply(normalize_subject_for_corr, axis=1)
    df_regulier_corr = df_regulier_corr.dropna(subset=["Matiere_Corr"])

    matieres_matrice = ["Math CST", "Science ST (Théorie)", "Science ATS (Théorie)", "Histoire 4"]
    dispo_mats = [m for m in matieres_matrice if m in df_regulier_corr["Matiere_Corr"].unique()]

    if len(dispo_mats) >= 2:
        eleves_corr = df_regulier_corr["CD_PERMN"].unique()
        df_bin = pd.DataFrame({"CD_PERMN": eleves_corr})
        for m in dispo_mats:
            echec_ids = set(df_regulier_corr[(df_regulier_corr["Matiere_Corr"] == m) & (df_regulier_corr["RESLT_FINAL"] < 60)]["CD_PERMN"])
            inscrit_ids = set(df_regulier_corr[df_regulier_corr["Matiere_Corr"] == m]["CD_PERMN"])
            df_bin[m] = df_bin["CD_PERMN"].apply(lambda pid: 1 if pid in echec_ids else (0 if pid in inscrit_ids else np.nan))

        df_bin_calc = df_bin.set_index("CD_PERMN").dropna(how="all")
        corr_matrix, pval_matrix = compute_failure_correlations(df_bin_calc)

        if not corr_matrix.empty:
            # Identifier la corrélation la plus haute hors diagonale
            corr_no_diag = corr_matrix.copy()
            np.fill_diagonal(corr_no_diag.values, -999)
            max_corr_val = float(corr_no_diag.max().max())

            col_hm, col_pt = st.columns([1.6, 1.4])
            with col_hm:
                # Heatmap avec palette personnalisée : diagonale et 0 atténués
                fig_hm = px.imshow(
                    corr_matrix,
                    text_auto=".2f",
                    color_continuous_scale=[[0, "#f8fafc"], [0.2, "#e2ecf5"], [0.5, "#38bdf8"], [1, "#b91c1c"]],
                    title="Matrice de Corrélation des Échecs (Coefficient Φ de Pearson)"
                )
                fig_hm.update_layout(coloraxis_colorbar=dict(title="Φ"))
                st.plotly_chart(apply_standard_layout(fig_hm, height=360), use_container_width=True)

            with col_pt:
                st.markdown("**Tests d'association (Test t pairé - p-values) :**")
                pvals_display = pval_matrix.map(lambda v: f"{v:.4f} {'*' if v < 0.05 else ''}" if pd.notna(v) else "-")
                st.dataframe(pvals_display, use_container_width=True)
                st.markdown(f"""
                <div style='background:#fef2f2; border-left:4px solid #b91c1c; padding:10px; border-radius:4px; font-size:0.88rem;'>
                    <strong>Point de mire docimologique :</strong> La corrélation la plus élevée est de <strong>Φ = {max_corr_val:.2f}</strong>.
                    Une valeur Φ > 0.30 (* p < 0.05) indique une interdépendance systémique des échecs justifiant une remédiation croisée.
                </div>
                """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. VENTILATIONS DU VOLUME D'ÉCHECS (3, 2, 1) & QUADRANTS D'ÉTABLISSEMENT
    # -----------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 4. Priorisation SRÉ : quelles écoles combinent fort volume et haut taux d'échec ?")

    # Calcul du nombre d'échecs par élève (4e secondaire - matières à sanction)
    echecs_counts_per_student = df_echecs_4e_sanction.groupby("CD_PERMN")["Matiere_Simple"].nunique()
    df_eleves_summary = df_4e.drop_duplicates(subset=["CD_PERMN"])[["CD_PERMN", "CD_ORGNS"]].copy()
    df_eleves_summary["Nb_Echecs"] = df_eleves_summary["CD_PERMN"].map(echecs_counts_per_student).fillna(0).astype(int)
    df_eleves_summary["Categorie_Echec"] = df_eleves_summary["Nb_Echecs"].map({
        3: "3 échecs", 2: "2 échecs", 1: "1 échec", 0: "0 échec"
    }).fillna("0 échec")

    # A. Graphique en barres ordonné par NOMBRE DÉCROISSANT DE 1 ÉCHEC (hors 0 échec)
    df_ech_only = df_eleves_summary[df_eleves_summary["Nb_Echecs"] > 0].copy()
    if not df_ech_only.empty:
        # Déterminer l'ordre des écoles par nombre de 1 échec décroissant
        ordre_ecoles = df_ech_only[df_ech_only["Nb_Echecs"] == 1]["CD_ORGNS"].value_counts().index.tolist()
        autres_ecoles = [ec for ec in df_ech_only["CD_ORGNS"].unique() if ec not in ordre_ecoles]
        ordre_total = ordre_ecoles + autres_ecoles

        df_ecole_ech = df_ech_only.groupby(["CD_ORGNS", "Categorie_Echec"], observed=True).size().reset_index(name="Nb_Eleves")

        fig_ec = px.bar(
            df_ecole_ech,
            x="CD_ORGNS",
            y="Nb_Eleves",
            color="Categorie_Echec",
            barmode="stack",
            category_orders={"CD_ORGNS": ordre_total},
            title="Volume d'Échecs par Établissement (Ordonné par nombre d'échecs simples)",
            color_discrete_map={
                "1 échec": PRIMARY_QUEBEC,
                "2 échecs": ACCENT_QUEBEC,
                "3 échecs": DANGER_QUEBEC
            }
        )
        fig_ec.update_xaxes(type="category", title_text="Établissement")
        fig_ec.update_yaxes(title_text="Nombre d'élèves en échec")

        # Calcul dynamique des statistiques pour le bloc d'aide à l'interprétation
        stats_par_ecole = []
        for cd_ec, grp_ec in df_eleves_summary.groupby("CD_ORGNS"):
            tot_ec = len(grp_ec)
            nb_3 = int((grp_ec["Nb_Echecs"] == 3).sum())
            nb_2 = int((grp_ec["Nb_Echecs"] == 2).sum())
            nb_multi = nb_3 + nb_2
            pct_multi = (nb_multi / tot_ec * 100.0) if tot_ec > 0 else 0.0
            is_adapt = cd_ec in ECOLES_ADAPTATION
            stats_par_ecole.append({
                "CD_ORGNS": cd_ec,
                "Nom": get_ecole_nom(cd_ec),
                "Total": tot_ec,
                "Nb_3": nb_3,
                "Nb_2": nb_2,
                "Nb_Multi": nb_multi,
                "Pct_Multi": pct_multi,
                "Is_Adapt": is_adapt
            })
        df_stats_ec = pd.DataFrame(stats_par_ecole)

        # 1. École avec le plus grand nombre absolu de 3 échecs
        top_ec_vol3 = df_stats_ec.sort_values(by=["Nb_3", "Nb_Multi"], ascending=[False, False]).iloc[0] if not df_stats_ec.empty else None

        # 2. École avec la plus grande proportion (%) de multi-échecs (2 et 3 échecs)
        # Exclure les écoles d'adaptation scolaire (special ed) dont les pourcentages sont biaisés par de faibles N,
        # et appliquer le filtre de taille minimale de groupe
        df_stats_reg = df_stats_ec[(df_stats_ec["Total"] >= min_group_size) & (~df_stats_ec["Is_Adapt"])]
        if df_stats_reg.empty:
            df_stats_reg = df_stats_ec[df_stats_ec["Total"] >= min_group_size]
        if df_stats_reg.empty:
            df_stats_reg = df_stats_ec
        top_ec_pct_multi = df_stats_reg.sort_values(by=["Pct_Multi", "Nb_Multi"], ascending=[False, False]).iloc[0] if not df_stats_reg.empty else None

        col_sre_fig, col_sre_help = st.columns([2, 1])
        with col_sre_fig:
            st.plotly_chart(apply_standard_layout(fig_ec, height=400), use_container_width=True)

        with col_sre_help:
            st.markdown(f"""
            <div style="background-color: #f8fafc; border-left: 4px solid #1472BF; border-radius: 6px; padding: 16px; font-size: 0.90rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;">
                <h4 style="margin-top:0; color: #095797; font-size: 1.05rem;">🎯 Aide à la Priorisation SRÉ</h4>
                <div style="margin-bottom: 14px;">
                    <span style="font-weight: 700; color: #b91c1c;">Volume maximal de 3 échecs :</span><br>
                    <strong>École {top_ec_vol3['CD_ORGNS']} — {top_ec_vol3['Nom']}</strong><br>
                    <span style="font-size: 1.25rem; font-weight: 800; color: #b91c1c;">{top_ec_vol3['Nb_3']} élève(s)</span>
                    <div style="font-size: 0.80rem; color: #64748b; margin-top:2px;">
                        Cumulent Math, Science et Histoire. Risque aigu de décrochage. Cible n°1 pour tutorat d'urgence et brigades DSE.
                    </div>
                </div>
                <div style="margin-bottom: 14px;">
                    <span style="font-weight: 700; color: #d97706;">Proportion maximale de 2 et 3 échecs :</span><br>
                    <strong>École {top_ec_pct_multi['CD_ORGNS']} — {top_ec_pct_multi['Nom']}</strong><br>
                    <span style="font-size: 1.25rem; font-weight: 800; color: #d97706;">{top_ec_pct_multi['Pct_Multi']:.1f} %</span> ({top_ec_pct_multi['Nb_Multi']} sur {top_ec_pct_multi['Total']} élèves)
                    <div style="font-size: 0.80rem; color: #64748b; margin-top:2px;">
                        Taux mesuré sur les établissements réguliers (N ≥ {min_group_size} élèves, hors écoles d'adaptation scolaire).
                    </div>
                </div>
                <hr style="margin: 10px 0; border: 0; border-top: 1px solid #e2e8f0;">
                <div style="font-size: 0.81rem; color: #334155; line-height: 1.4;">
                    <strong>Arbitrage stratégique :</strong> Déployer en priorité les mesures de redressement vers ces deux pôles pour résorber les freins majeurs à la diplomation.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # B. Graphique 4 Quadrants des Établissements (Proportion d'élèves vs Multi-échecs)
    st.markdown("#### Matrice 4 Quadrants des Établissements par Matière")
    st.caption(f"Puces = Établissement — Matière (seuil N ≥ {min_group_size} élèves). Axe X = Taux de multi-échecs (2+ matières) | Axe Y = Taux global d'élèves en échec.")

    # Agréger par école et par matière à sanction
    df_4e_sanction = df_4e[df_4e["Matiere_Simple"].isin(SANCTION_4E_MATIERES)].copy()
    df_quad_ecoles = df_4e_sanction.groupby(["CD_ORGNS", "Matiere_Simple"], observed=True).agg(
        Total_Inscrits=("CD_PERMN", "nunique"),
        Nb_Echecs=("RESLT_FINAL", lambda s: (s < 60).sum())
    ).reset_index()

    # Application du slider de taille minimale de groupe
    df_quad_ecoles = df_quad_ecoles[df_quad_ecoles["Total_Inscrits"] >= min_group_size].copy()

    if not df_quad_ecoles.empty and len(df_quad_ecoles) >= 2:
        df_quad_ecoles["Taux_Echec_Pct"] = (df_quad_ecoles["Nb_Echecs"] / df_quad_ecoles["Total_Inscrits"]) * 100.0

        # Croiser avec le nombre de multi-échecs de l'école
        multi_ech_par_ecole = df_ech_only[df_ech_only["Nb_Echecs"] >= 2].groupby("CD_ORGNS").size()
        df_quad_ecoles["Multi_Echecs_Ecole"] = df_quad_ecoles["CD_ORGNS"].map(multi_ech_par_ecole).fillna(0).astype(int)
        df_quad_ecoles["Label_Puce"] = "Éc. " + df_quad_ecoles["CD_ORGNS"].astype(str) + " — " + df_quad_ecoles["Matiere_Simple"].astype(str)

        med_x = float(df_quad_ecoles["Multi_Echecs_Ecole"].median())
        med_y = float(df_quad_ecoles["Taux_Echec_Pct"].median())

        fig_quad_ec = px.scatter(
            df_quad_ecoles,
            x="Multi_Echecs_Ecole",
            y="Taux_Echec_Pct",
            color="Matiere_Simple",
            text="CD_ORGNS",
            hover_name="Label_Puce",
            hover_data={"Total_Inscrits": True, "Nb_Echecs": True, "Taux_Echec_Pct": ":.1f%"},
            title="Matrice 4 Quadrants : Vulnérabilité Globale vs Multi-Échecs",
            color_discrete_sequence=PALETTE_ACCESSIBLE
        )
        fig_quad_ec.add_vline(x=med_x, line=dict(color="#64748b", dash="dot"))
        fig_quad_ec.add_hline(y=med_y, line=dict(color="#64748b", dash="dot"))
        fig_quad_ec.update_traces(textposition="top center", marker=dict(size=11, line=dict(width=1, color="#000")))
        fig_quad_ec.update_xaxes(title_text="Nombre d'élèves en échecs multiples (2 et 3) dans l'école")
        fig_quad_ec.update_yaxes(title_text="Taux d'échec de la discipline (%)")

        col_quad_fig, col_quad_help = st.columns([2, 1])
        with col_quad_fig:
            st.plotly_chart(apply_standard_layout(fig_quad_ec, height=440), use_container_width=True)

        with col_quad_help:
            st.markdown("""
            <div style="background-color: #f8fafc; border-left: 4px solid #095797; border-radius: 6px; padding: 16px; font-size: 0.88rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05); height: 100%;">
                <h4 style="margin-top:0; color: #095797; font-size: 1.02rem;">🧭 Soutien à l'Interprétation</h4>
                <div style="margin-bottom: 10px;">
                    <span style="font-weight: 700; color: #b91c1c;">Haut-Droit (Priorité absolue) :</span><br>
                    Taux d'échec élevé dans la discipline <em>ET</em> fort volume d'élèves multi-échecs dans l'école. Nécessite une intervention concertée didactique et d'encadrement.
                </div>
                <div style="margin-bottom: 10px;">
                    <span style="font-weight: 700; color: #d97706;">Haut-Gauche (Fragilité disciplinaire) :</span><br>
                    Taux d'échec élevé circonscrit à cette matière, alors que l'école a peu de multi-échecs. Révèle un enjeu didactique interne au département.
                </div>
                <div style="margin-bottom: 10px;">
                    <span style="font-weight: 700; color: #7c3aed;">Bas-Droit (Pression d'établissement) :</span><br>
                    Taux d'échec modéré, mais au sein d'une école accueillant un fort volume d'élèves vulnérables.
                </div>
                <div style="margin-bottom: 0;">
                    <span style="font-weight: 700; color: #059669;">Bas-Gauche (Zone de réussite stable) :</span><br>
                    Discipline et établissement sous les médianes de risque (climat d'apprentissage sécurisé).
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(f"Effectif insuffisant pour afficher la matrice 4 quadrants avec le seuil actuel (N ≥ {min_group_size} élèves). Ajustez le curseur dans la barre latérale.")

    # -------------------------------------------------------------------------
    # C. INDICE DE VULNÉRABILITÉ DE CHEVAUCHEMENT D'ANNÉES (4E / 5E SECONDAIRE)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 5. Indice de vulnérabilité de chevauchement d'années (4e / 5e secondaire)")
    st.caption(
        "Dénombrement des élèves inscrits en 5e secondaire ayant un échec actif à une matière à sanction ministérielle de 4e secondaire "
        "(échec < 60% en Mathématiques CST/SN/TS, Sciences ST/ATS ou Histoire du Québec et du Canada)."
    )

    eleves_5e_ids = set(df_5e["CD_PERMN"].unique()) if not df_5e.empty else set()
    if eleves_5e_ids:
        echecs_4e_ids = set(df_echecs_4e_sanction["CD_PERMN"].unique()) if not df_echecs_4e_sanction.empty else set()
        df_5e_uniq = df_5e.drop_duplicates(subset=["CD_PERMN"]).copy()
        df_5e_uniq["Has_Echec_4e"] = df_5e_uniq["CD_PERMN"].isin(echecs_4e_ids)

        # Conserver exclusivement les élèves de 5e avec échec à une matière de sanction de 4e
        df_chev = df_5e_uniq[df_5e_uniq["Has_Echec_4e"]].copy()

        nb_chev_total = len(df_chev)
        nb_5e_total = len(df_5e_uniq)
        pct_chev = (nb_chev_total / nb_5e_total * 100.0) if nb_5e_total > 0 else 0.0
        ci_chev = wilson_interval(nb_chev_total, nb_5e_total, 0.95)
        ci_chev_pct = (ci_chev[0] * 100.0, ci_chev[1] * 100.0) if nb_5e_total > 0 else None

        # Disposition systématique : Visualisation à GAUCHE (2/3) et Boite d'explication / KPI à DROITE (1/3)
        col_chev_fig, col_chev_kpi = st.columns([2.0, 1.0])

        with col_chev_fig:
            if not df_chev.empty and "CD_ORGNS" in df_chev.columns:
                df_chev["Bassin_RETAC"] = df_chev["CD_ORGNS"].apply(get_retac_for_ecole)
                df_chev_agg = df_chev.groupby(["Bassin_RETAC", "CD_ORGNS"], observed=True).size().reset_index(name="Nb_Eleves")

                # Tri des écoles par volume décroissant d'élèves en échec de 4e
                ordre_ecoles_chev = df_chev["CD_ORGNS"].value_counts().index.tolist()

                fig_chev = px.bar(
                    df_chev_agg,
                    x="CD_ORGNS",
                    y="Nb_Eleves",
                    color="Bassin_RETAC",
                    text="Nb_Eleves",
                    category_orders={"CD_ORGNS": ordre_ecoles_chev},
                    title="Élèves de 5e sec. avec échec en sanction de 4e par Établissement et Bassin RÉTAC",
                    color_discrete_sequence=PALETTE_ACCESSIBLE,
                    labels={
                        "CD_ORGNS": "Établissement",
                        "Nb_Eleves": "Élèves (Échec sanction 4e)",
                        "Bassin_RETAC": "Bassin RÉTAC"
                    }
                )
                fig_chev.update_traces(textposition="outside")
                fig_chev.update_xaxes(type="category", tickangle=0)
                st.plotly_chart(apply_standard_layout(fig_chev, height=360), use_container_width=True)
            else:
                st.success("Aucun élève de 5e secondaire en situation d'échec à une matière de sanction de 4e détecté pour la sélection active.")

        with col_chev_kpi:
            render_kpi_card(
                title="Échec sanction 4e en 5e sec.",
                value=pct_chev,
                status="danger" if pct_chev > 10.0 else ("warning" if pct_chev > 4.0 else "success"),
                n=nb_5e_total,
                ci=ci_chev_pct,
                subtitle=f"{nb_chev_total} élève(s) bloqué(s) par une matière de 4e",
                target="Cible : < 3.0%",
                help_text="Proportion d'élèves inscrits en 5e secondaire ayant un échec actif à une matière à sanction ministérielle de 4e secondaire (Maths CST/SN/TS, Sciences ST/ATS ou Histoire)."
            )
            st.markdown("""
            <div style="background-color: #f8fafc; border-left: 4px solid #1472BF; border-radius: 6px; padding: 14px; margin-top: 10px; font-size: 0.85rem; color: #334155; line-height: 1.45; box-shadow: 0 1px 2px rgba(0,0,0,0.04);">
                <strong style="color: #095797; font-size: 0.90rem;">🎯 Enjeu stratégique de diplomation :</strong><br>
                Ces élèves risquent de voir leur diplomation bloquée à la fin de la 5e secondaire en raison d'une dette de crédits ministériels de 4e non résorbée, malgré la réussite de leurs cours de 5e.
                <div style="margin-top: 8px; font-weight: 600; color: #b91c1c;">
                    Piste d'action : Inscription prioritaire aux reprises d'épreuves et tutorat intensif sur la matière de 4e manquante.
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucun élève inscrit en 5e secondaire dans le périmètre filtré.")

    # -------------------------------------------------------------------------
    # D. ANALYSE DOCIMOLOGIQUE DU SEUIL DE PASSAGE (ZONE CRITIQUE 55-65%)
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 6. Analyse docimologique du seuil de passage (Zone critique 55 % – 65 %)")
    st.caption(
        "Distribution fine des résultats finaux autour du seuil ministériel de sanction (60 %) pour détecter "
        "les discontinuités docimologiques (creux à 58-59 % et pic de complaisance / repêchage local à 60 %)."
    )

    notes_globales_df = df_f[df_f["Type_Cours"] == "Note globale"] if "Type_Cours" in df_f.columns else df_f
    if notes_globales_df.empty:
        notes_globales_df = df_f
    notes_seuil = pd.to_numeric(notes_globales_df["RESLT_FINAL"], errors="coerce").dropna()
    notes_zone_55_65 = notes_seuil[(notes_seuil >= 55.0) & (notes_seuil <= 65.0)].round().astype(int)

    if not notes_zone_55_65.empty:
        bins_range = list(range(55, 66))
        counts_seuil = notes_zone_55_65.value_counts().reindex(bins_range, fill_value=0).reset_index()
        counts_seuil.columns = ["Note_Finale", "Effectif"]
        counts_seuil["Statut_Seuil"] = np.where(
            counts_seuil["Note_Finale"] < 60,
            "Sous le seuil (55-59 % : Zone frontière)",
            "Au seuil ou au-dessus (60-65 % : Réussite)"
        )

        n_59 = int(counts_seuil.loc[counts_seuil["Note_Finale"] == 59, "Effectif"].iloc[0])
        n_60 = int(counts_seuil.loc[counts_seuil["Note_Finale"] == 60, "Effectif"].iloc[0])
        ratio_discont = (n_60 / max(1, n_59))

        col_hist_s, col_diag_s = st.columns([2.0, 1.0])
        with col_hist_s:
            fig_seuil = px.bar(
                counts_seuil,
                x="Note_Finale",
                y="Effectif",
                color="Statut_Seuil",
                text="Effectif",
                title="Histogramme docimologique de la zone critique [55 % – 65 %]",
                color_discrete_map={
                    "Sous le seuil (55-59 % : Zone frontière)": ACCENT_QUEBEC,
                    "Au seuil ou au-dessus (60-65 % : Réussite)": PRIMARY_QUEBEC
                },
                labels={
                    "Note_Finale": "Résultat final (RESLT_FINAL %)",
                    "Effectif": "Nombre de résultats",
                    "Statut_Seuil": "Zone docimologique"
                }
            )
            fig_seuil.add_vline(
                x=59.5,
                line=dict(color=DANGER_QUEBEC, width=2, dash="dash"),
                annotation_text="Seuil de passage (60 %)",
                annotation_position="top right"
            )
            fig_seuil.update_xaxes(tickmode="linear", tick0=55, dtick=1)
            fig_seuil.update_traces(textposition="outside")
            st.plotly_chart(apply_standard_layout(fig_seuil, height=360), use_container_width=True)

        with col_diag_s:
            nb_55_59 = int(counts_seuil.loc[counts_seuil["Note_Finale"] < 60, "Effectif"].sum())
            nb_60_65 = int(counts_seuil.loc[counts_seuil["Note_Finale"] >= 60, "Effectif"].sum())
            st.markdown(f"""
            <div style='background:{BLEU_QUEBEC_LIGHT}; border-left:4px solid {BLEU_QUEBEC}; padding:14px; border-radius:6px;'>
                <h4 style='color:{BLEU_QUEBEC}; margin-top:0;'>Diagnostic de discontinuité au seuil :</h4>
                <ul style='font-size:0.92rem; margin-bottom:0;'>
                    <li><strong>Zone frontière [55-59 %] :</strong> {nb_55_59} résultat(s) en échec de repêchage</li>
                    <li><strong>Zone de passage [60-65 %] :</strong> {nb_60_65} résultat(s) validés de justesse</li>
                    <li><strong>Effectif à 59 % vs 60 % :</strong> {n_59} vs {n_60} (Ratio 60%/59% = <strong>{ratio_discont:.2f}x</strong>)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucun résultat final situé dans l'intervalle [55 %, 65 %] pour les filtres sélectionnés.")

# -----------------------------------------------------------------------------
# 4. INDICATEUR STRATÉGIQUE GPS DE DIPLOMATION & RENDEMENT ESTIVAL (POST-AOÛT)
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 7. Récupération estivale et taux de conversion post-août : quel effectif sauvé du redoublement ?")
st.markdown("""
**Vue d'ensemble de la trajectoire de persévérance pour planifier les ressources d'accompagnement pour l’année scolaire qui s’amorce.**
Permet d'évaluer le rendement de l'école d'été (comparaison juin vs août) et de calibrer les besoins d'automne.
""")

# Uploader optionnel de résultats d'août post-école d'été
df_aout_loaded = get_df_aout()
if df_aout_loaded.empty:
    with st.expander("Téléverser une extraction post-école d'été (CHAP*.csv session d'août)", expanded=False):
        up_ao = st.file_uploader("Fichier CHAP* août (CSV)", type=["csv"], key="up_ao_macro")
        if up_ao:
            df_loaded_ao = load_csv_robust(up_ao)
            if not df_loaded_ao.empty:
                set_df_aout(df_loaded_ao)
                st.success("Résultats d'août intégrés avec succès !")
                st.rerun()

# Comparaison de l'état des échecs Juin vs Août (Rendement de la récupération estivale)
if not df_aout_loaded.empty and not df_f.empty and "CD_PERMN" in df_f.columns and "RESLT_FINAL" in df_f.columns:
    df_ao_clean = df_aout_loaded.copy()
    if "CD_ORGNS" in df_ao_clean.columns:
        df_ao_clean["CD_ORGNS"] = df_ao_clean["CD_ORGNS"].apply(clean_cd_orgns)
        if selected_retac != "Tous":
            df_ao_clean = df_ao_clean[df_ao_clean["CD_ORGNS"].isin(set(get_ecoles_for_retac(selected_retac)))]
        if selected_ecole != "Toutes":
            df_ao_clean = df_ao_clean[df_ao_clean["CD_ORGNS"] == selected_ecole]
    if "CD_PERMN" in df_ao_clean.columns:
        df_ao_clean["CD_PERMN"] = df_ao_clean["CD_PERMN"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    if "RESLT_FINAL" in df_ao_clean.columns:
        df_ao_clean["RESLT_FINAL"] = pd.to_numeric(df_ao_clean["RESLT_FINAL"], errors="coerce")

    echecs_juin_ids = set(df_f[pd.to_numeric(df_f["RESLT_FINAL"], errors="coerce") < 60.0]["CD_PERMN"].unique())
    echecs_aout_ids = set(df_ao_clean[df_ao_clean["RESLT_FINAL"] < 60.0]["CD_PERMN"].unique()) if "RESLT_FINAL" in df_ao_clean.columns else set()
    presents_aout_ids = set(df_ao_clean["CD_PERMN"].unique()) if "CD_PERMN" in df_ao_clean.columns else set()

    # Un élève en échec en juin est sauvé en août s'il n'est plus en échec dans le fichier consolidé d'août
    # ou s'il a réussi ses reprises d'août
    reussis_aout_ids = set(df_ao_clean[df_ao_clean["RESLT_FINAL"] >= 60.0]["CD_PERMN"].unique()) if "RESLT_FINAL" in df_ao_clean.columns else set()
    sauves_ids = (echecs_juin_ids - echecs_aout_ids) if len(presents_aout_ids & echecs_juin_ids) > 0 else (echecs_juin_ids & reussis_aout_ids)

    nb_ech_juin = len(echecs_juin_ids)
    nb_sauves = len(sauves_ids)
    nb_ech_restants = max(0, nb_ech_juin - nb_sauves)
    taux_conv_ete = (nb_sauves / nb_ech_juin * 100.0) if nb_ech_juin > 0 else 0.0
    ci_conv = wilson_interval(nb_sauves, nb_ech_juin, 0.95)
    ci_conv_pct = (ci_conv[0] * 100.0, ci_conv[1] * 100.0) if nb_ech_juin > 0 else None

    c_ete1, c_ete2 = st.columns([1.0, 2.0])
    with c_ete1:
        render_kpi_card(
            title="Rendement Récupération Estivale",
            value=taux_conv_ete,
            status="success" if taux_conv_ete >= 50.0 else ("warning" if taux_conv_ete >= 25.0 else "danger"),
            n=nb_ech_juin,
            ci=ci_conv_pct,
            subtitle=f"{nb_sauves} élève(s) sauvé(s) sur {nb_ech_juin} en échec en juin",
            target="Taux de conversion post-août",
            help_text="Pourcentage net d'élèves en échec à la session de juin ayant régularisé leur situation après la session d'août."
        )
    with c_ete2:
        df_comp_ete = pd.DataFrame({
            "Session": ["Session de Juin (Avant école d'été)", "Session d'Août (Post-récupération)", "Élèves sauvés du redoublement"],
            "Effectif": [nb_ech_juin, nb_ech_restants, nb_sauves],
            "Catégorie": ["Échecs initiaux (Juin)", "Échecs résiduels (Août)", "Conversion réussie (Sauvés)"]
        })
        fig_ete = px.bar(
            df_comp_ete,
            x="Session",
            y="Effectif",
            color="Catégorie",
            text="Effectif",
            title="Bilan de conversion estivale : Échecs de Juin vs Août",
            color_discrete_map={
                "Échecs initiaux (Juin)": DANGER_QUEBEC,
                "Échecs résiduels (Août)": ACCENT_QUEBEC,
                "Conversion réussie (Sauvés)": SUCCESS_QUEBEC
            }
        )
        fig_ete.update_traces(textposition="outside")
        st.plotly_chart(apply_standard_layout(fig_ete, height=300), use_container_width=True)
elif not df_f.empty:
    st.caption("ℹ️ *Chargez le fichier CHAP060105 d'août pour activer le calcul automatique du **Rendement de la récupération estivale (Taux de conversion post-août)**.*")

# Source active pour le GPS (session d'août si dispo, sinon session régulière de juin)
df_gps_source = df_aout_loaded if not df_aout_loaded.empty else df_f
if not df_aout_loaded.empty:
    st.info("**Données actives : Session d'août (post-école d'été)** — Analyse de la persévérance consolidée.")

if not df_gps_source.empty and "RESLT_FINAL" in df_gps_source.columns:
    df_gps_source["RESLT_FINAL"] = pd.to_numeric(df_gps_source["RESLT_FINAL"], errors="coerce")

    # Slider pour la marge de distillation par compétences (1 à 5 points)
    marge_distillation = st.slider(
        "Marge d'écart pour distillation par compétences (Points sous 60%) :",
        min_value=1, max_value=5, value=5, step=1,
        help="Définit la zone frontière (ex. 55-59% si marge = 5) des élèves à fort potentiel de diplomation rapide."
    )
    seuil_min_gps1 = 60 - marge_distillation

    nb_gps1 = df_gps_source[(df_gps_source["RESLT_FINAL"] >= seuil_min_gps1) & (df_gps_source["RESLT_FINAL"] < 60)]["CD_PERMN"].nunique()
    nb_gps2 = df_gps_source[(df_gps_source["RESLT_FINAL"] >= 50) & (df_gps_source["RESLT_FINAL"] < seuil_min_gps1)]["CD_PERMN"].nunique()
    nb_gps3 = df_gps_source[df_gps_source["RESLT_FINAL"] < 50]["CD_PERMN"].nunique()

    p1, p2, p3 = st.columns(3)
    with p1:
        render_kpi_card(
            title=f"GPS 1 : Candidats RÉUSSITE SANS Reprise ({seuil_min_gps1}-59%)",
            value=nb_gps1,
            status="success" if nb_gps1 > 0 else "neutral",
            subtitle="Distillation par compétences",
            target="Repêchage immédiat",
            help_text=f"Élèves à moins de {marge_distillation} points du seuil de passage pour la compétence évaluée localement."
        )

    with p2:
        render_kpi_card(
            title="GPS 2 : Candidats Reprise Janvier (Sans reprise d'année)",
            value=nb_gps2,
            status="warning" if nb_gps2 > 0 else "neutral",
            subtitle="Réactivation des savoirs essentiels",
            target="Reprise ciblée",
            help_text="Élèves nécessitant un tutorat d'automne pour réussir l'épreuve de reprise de janvier sans refaire leur année."
        )

    with p3:
        render_kpi_card(
            title="GPS 3 : Candidats Reprise d'ANNÉE (< 50%)",
            value=nb_gps3,
            status="danger" if nb_gps3 > 10 else "neutral",
            subtitle="Lacunes structurelles (Reprise 4e sec.)",
            target="Accompagnement intensif",
            help_text="Élèves cumulant des difficultés lourdes justifiant une reprise de niveau scolaire."
        )

    st.info("**Navigation GPS** : Pour consulter la liste nominative priorisée et prescrire les interventions élèves par élève, rendez-vous dans le module **4. Triage & Prescription GPS**.")

# -----------------------------------------------------------------------------
# 5. PANNEAU D'ACTION DYNAMIQUE (LAD P2)
# -----------------------------------------------------------------------------
st.markdown("---")
constat_macro = (
    f"Pour l'établissement ou le réseau sélectionné ({selected_ecole} / RETAC: {selected_retac}), le taux de réussite global s'élève à {taux_reussite:.1f}% "
    f"(IC 95%: [{ci_reussite[0]:.1f}% - {ci_reussite[1]:.1f}%]). "
    f"{tot_4e if 'tot_4e' in locals() else 0} élève(s) sont en échec de 4e secondaire, dont {ech_3 if 'ech_3' in locals() else 0} cumulant 3 matières bloquantes."
)

pistes_macro = [
    f"**Concertation didactique prioritaire sur {pire_mat if 'pire_mat' in locals() else 'la matière la plus touchée'} :** Mobiliser les conseillers pédagogiques pour cibler en priorité les départements présentant le plus lourd volume d'échecs.",
    "**Stratégie GPS d'automne :** Déployer immédiatement les mesures de distillation par compétences pour le palier GPS 1, et organiser des cliniques de préparation pour l'épreuve de janvier (GPS 2).",
    "**Arbitrage des ressources par RETAC :** Allouer les ressources d'intervention intensive aux établissements situés dans le quadrant supérieur droit de la matrice d'établissements."
]

render_action_panel(
    question="Comment orchestrer les leviers d'intervention réseau pour maximiser la diplomation et prévenir le décrochage scolaire en 4e et 5e secondaire ?",
    constat_dynamique=constat_macro,
    pistes=pistes_macro,
    context_tag=f"RETAC {selected_retac} | École {selected_ecole}"
)

render_about_data(
    source_name="Fichiers ministériels CHAP060105 et CHS040506R",
    limits=[
        "La détection du niveau repose sur la norme ministérielle (3e chiffre depuis la droite du code cours).",
        "La matrice de corrélation isole les cours de tronc commun régulier (hors SN/TS).",
        "Les ventilations transversales (Sexe et Plan d'intervention) sont consultables dans le module 3. Modération (MÉSO)."
    ]
)
