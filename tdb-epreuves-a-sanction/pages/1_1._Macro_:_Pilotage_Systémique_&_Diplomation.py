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
    SANCTION_4E_MATIERES
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
from ui.charts import plot_venn3_plotly, apply_standard_layout, download_csv_button
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

k1, k2, k3 = st.columns(3)
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
        title="Écart moyen de modération (NEB - NMC)",
        value=f"{ecart_moyen_mod:+.1f}%",
        status=stat_mod,
        n=total_groupes_mod,
        subtitle="Écart évaluation locale vs épreuve ministérielle",
        target="Cible : ±2.0%",
        help_text="Matières considérées : Épreuves uniques ministérielles (Français, Maths, Sciences, Histoire)."
    )

with k3:
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
        # Ajouter les écoles sans 1 échec mais avec 2 ou 3 échecs
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
            title="Volume d'Échecs par Établissement (Ordonné par nombre d'échecs simples décroissant)",
            color_discrete_map={
                "1 échec": PRIMARY_QUEBEC,
                "2 échecs": ACCENT_QUEBEC,
                "3 échecs": DANGER_QUEBEC
            }
        )
        fig_ec.update_xaxes(type="category", title_text="Établissement")
        fig_ec.update_yaxes(title_text="Nombre d'élèves en échec")
        st.plotly_chart(apply_standard_layout(fig_ec, height=380), use_container_width=True)

    # B. Graphique 4 Quadrants des Établissements (Proportion d'élèves vs Multi-échecs)
    st.markdown("#### Matrice 4 Quadrants des Établissements par Matière")
    st.caption("Puces = Établissement — Matière. Axe X = Taux de multi-échecs (2+ matières) | Axe Y = Taux global d'élèves en échec.")

    # Agréger par école et par matière à sanction
    df_4e_sanction = df_4e[df_4e["Matiere_Simple"].isin(SANCTION_4E_MATIERES)].copy()
    df_quad_ecoles = df_4e_sanction.groupby(["CD_ORGNS", "Matiere_Simple"], observed=True).agg(
        Total_Inscrits=("CD_PERMN", "nunique"),
        Nb_Echecs=("RESLT_FINAL", lambda s: (s < 60).sum())
    ).reset_index()

    if not df_quad_ecoles.empty and len(df_quad_ecoles) >= 4:
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
        st.plotly_chart(apply_standard_layout(fig_quad_ec, height=420), use_container_width=True)

# -----------------------------------------------------------------------------
# 4. INDICATEUR STRATÉGIQUE GPS DE DIPLOMATION (POST ÉCOLE D'ÉTÉ)
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### 5. Récupération estivale : quel effectif repêcher par compétence sans reprise complète d'année ?")
st.markdown("""
**Vue d'ensemble de la trajectoire de persévérance pour planifier les ressources d'accompagnement pour l’année scolaire qui s’amorce.**
Permet d'évaluer l'impact des mesures estivales et de calibrer les besoins d'automne.
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
