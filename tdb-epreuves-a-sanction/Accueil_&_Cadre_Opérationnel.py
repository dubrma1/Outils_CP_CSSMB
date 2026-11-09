# -*- coding: utf-8 -*-
"""
Accueil_&_Cadre_Opérationnel.py - Page d'atterrissage et cadre opérationnel LAD.
Architecture stratégique selon le cadre docimologique de Voyer (2011) et Dumaresq (2017).
Gère l'ingestion mémoire (Loi 25), la matrice de cohérence opérationnelle et l'aiguillage.
"""

import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
if "." not in sys.path:
    sys.path.insert(0, ".")

import boot
boot.warmup_runtime()

import streamlit as st
import pandas as pd

from core.schema import MATIERES_LIST, ECOLES_OPTIONS
from core.state import (
    init_session_state, get_df_main, set_df_main,
    get_df_moderation, set_df_moderation,
    update_global_filter, get_global_filters
)
from core.data_loader import (
    clean_and_merge_data, apply_filters, load_csv_robust,
    sanitize_df_for_stlite, parse_pdf_to_df, PDFPLUMBER_AVAILABLE
)
from ui.explainers import render_about_data
from ui.theme import inject_quebec_theme

st.set_page_config(
    page_title="Accueil & Cadre Opérationnel",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_quebec_theme()

init_session_state()

# -----------------------------------------------------------------------------
# BARRE LATÉRALE : TÉLÉVERSEMENT DES DONNÉES & FILTRES GLOBAUX
# -----------------------------------------------------------------------------
st.sidebar.title("Téléversement des données")
st.sidebar.info("Chargez vos extractions ministérielles de session régulière, puis cliquez sur 'Traiter les fichiers'.")

file_105 = st.sidebar.file_uploader("1. Données globales CHAP060105 - Juin (CSV)", type=["csv"])
file_chs = st.sidebar.file_uploader("2. Tables de modération CHS040506R (CSV recommandé, ou PDF)", type=["csv", "pdf"])
file_profs = st.sidebar.file_uploader("3. Liste enseignants / groupes (CSV - Optionnel)", type=["csv"])
file_sexe = st.sidebar.file_uploader("4. Optionnel - CD_PERMN, SEXE (CSV)", type=["csv"])
file_pi = st.sidebar.file_uploader("5. Optionnel - Plan d'intervention / EHDAA (CSV)", type=["csv"])
file_aout = st.sidebar.file_uploader("6. Optionnel - Données globales CHAP060105 - Août (CSV)", type=["csv"])

if st.sidebar.button("Traiter les fichiers", type="primary"):
    if not (file_105 or file_chs):
        st.sidebar.error("Veuillez téléverser au moins un fichier (CHAP060105 ou CHS040506R).")
    else:
        with st.spinner("Traitement et indexation des données en mémoire locale..."):
            df_105 = load_csv_robust(file_105) if file_105 else None
            df_profs = load_csv_robust(file_profs) if file_profs else None

            df_chs = None
            if file_chs:
                fname_lower = file_chs.name.lower()
                if fname_lower.endswith((".csv", ".txt")):
                    df_chs = load_csv_robust(file_chs)
                elif fname_lower.endswith(".pdf"):
                    try:
                        if not PDFPLUMBER_AVAILABLE:
                            st.sidebar.warning("L'extraction PDF nécessite 'pdfplumber', non disponible dans le runtime WebAssembly. Veuillez utiliser le fichier CSV (CHS040506R.csv).")
                        else:
                            df_chs = parse_pdf_to_df(file_chs)
                    except Exception as e:
                        st.sidebar.warning(f"Lecture PDF : {e}")

            df_merged = clean_and_merge_data(df_105, None, df_chs, df_profs)
            set_df_main(df_merged)
            if df_chs is not None and not df_chs.empty:
                set_df_moderation(df_chs)
            if file_sexe:
                df_s = load_csv_robust(file_sexe)
                if not df_s.empty:
                    from core.state import set_df_sexe
                    set_df_sexe(df_s)
            if file_pi:
                df_p = load_csv_robust(file_pi)
                if not df_p.empty:
                    from core.state import set_df_pi
                    set_df_pi(df_p)
            if file_aout:
                df_ao = load_csv_robust(file_aout)
                if not df_ao.empty:
                    from core.state import set_df_aout
                    set_df_aout(df_ao)

            import gc
            del df_105, df_profs, df_chs, df_merged
            gc.collect()
            st.sidebar.success("Fichiers chargés avec succès en mémoire vive !")

df_main = get_df_main()
if not df_main.empty:
    st.sidebar.markdown("---")
    st.sidebar.title("Filtres globaux")
    cur_filters = get_global_filters()
    selected_matiere = st.sidebar.selectbox("Matière cible :", MATIERES_LIST, index=0)
    selected_ecole = st.sidebar.selectbox("Établissement / École :", ECOLES_OPTIONS, index=0)

    if st.sidebar.button("Appliquer les filtres globaux", type="primary"):
        update_global_filter("selected_matiere", selected_matiere)
        update_global_filter("selected_ecole", selected_ecole)
        st.session_state["df_filtered"] = apply_filters(
            df_main,
            annee="Toutes",
            matiere=selected_matiere,
            ecole=selected_ecole,
            parcours="Tous"
        )
        st.sidebar.success("Filtres appliqués pour l'ensemble des modules !")

# -----------------------------------------------------------------------------
# 1. EN-TÊTE INSTITUTIONNEL
# -----------------------------------------------------------------------------
st.title("Tableau de Bord : Suivi des Matières à Sanction")
st.markdown("##### Outil d'Analyse Stratégique Macro, Méso et Micro — Dumaresq (2017)")

# -----------------------------------------------------------------------------
# 2. DÉFINITION DES ANALYSES MACRO, MÉSO ET MICRO (TABLEAU CENTRAL)
# -----------------------------------------------------------------------------

st.info("""
**Au palier Macro**, le tableau de bord met en lumière les situations où les difficultés dans une matière déclenchent des échecs en cascade. L'indicateur pivot dénombre les élèves cumulant 2 et 3 échecs aux matières à sanction de 4e secondaire. Il revient à la Direction générale et à la Direction des services éducatifs d’orchestrer l'allocation des ressources afin de lever les freins structurels à la diplomation et de converger vers les cibles du Plan d'engagement vers la réussite (PEVR).
""")

st.info("""
**Au palier Méso**, le tableau de bord détecte les distorsions évaluatives qui se produisent lorsque des pratiques indulgentes ou sévères exposent des groupes à une décote statistique lors de la modération ministérielle. Les directions d'école, appuyées par les conseillers pédagogiques, ont la responsabilité de réguler les pratiques évaluatives pour atténuer les effets de cette correction. L'indicateur pivot isole les groupes critiques qui conjuguent un fort écart théorique et une sévérité pratique subie par les élèves.
""")

st.info("""
**Au palier Micro**, le tableau de bord sonde la cohérence didactique et les conditions d'apprentissage au sein même de chaque école. La collaboration étroite entre équipes disciplinaires et conseillers pédagogiques permet de réétalonner les épreuves sommatives locales, garantissant leur conformité avec les exigences et la complexité des cadres d'évaluation ministériels.
""")

st.info("""
**Le module GPS**, quant à lui, cible prioritairement les élèves situés en zone frontière (55-59 %). Prévenir le redoublement complet est impératif pour ces profils vulnérables : l'aiguillage rapide vers l'école d'été, la validation des acquis par distillation des compétences et une préparation ciblée aux reprises constituent les leviers privilégiés pour sécuriser leur diplomation.
""")

# -----------------------------------------------------------------------------
# 3. BANDEAU DE CONFORMITÉ LOI 25 & PERFORMANCE
# -----------------------------------------------------------------------------
st.info("""
**Conformité stricte Loi 25 (Québec) & Performance WebAssembly :**
Aucune donnée ne quitte votre poste de travail. L'ingestion, le nettoyage, l'anonymisation et l'ensemble des analyses s'exécutent intégralement et exclusivement dans la mémoire vive de votre navigateur via WebAssembly / Pyodide. Les règles d'anonymisation et de suppression automatique des petites cellules ($N < 5$ élèves) sont rigoureusement appliquées dans l'ensemble des modules.
""")

# -----------------------------------------------------------------------------
# 4. APERÇU DES DONNÉES DÉSENSIBILISÉES (SI CHARGÉES)
# -----------------------------------------------------------------------------
if not df_main.empty:
    st.success("Données chargées avec succès ! Naviguez via le menu latéral pour consulter les modules.")
    st.subheader("Aperçu des 10 premières lignes (Données désensibilisées)")
    df_disp = st.session_state.get("df_filtered", df_main)
    st.dataframe(sanitize_df_for_stlite(df_disp.head(10)), use_container_width=True)

render_about_data(
    source_name="Fichiers ministériels CHAP060105 (Notes élèves) et CHS040506R (Tables de modération)",
    limits=[
        "Le tableau de bord opère sur les extractions de sessions régulières.",
        "Les règles de suppression des petites cellules (< 5 élèves) sont automatiquement appliquées dans tous les modules."
    ]
)
