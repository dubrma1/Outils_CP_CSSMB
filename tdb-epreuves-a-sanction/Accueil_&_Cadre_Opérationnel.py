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
    set_df_primaire, set_df_aout,
    get_df_profs, set_df_profs,
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
file_primaire = st.sidebar.file_uploader("Données primaires Élèves & Assiduité (CSV)", type=["csv"])
file_aout = st.sidebar.file_uploader("5. Optionnel - Données globales CHAP060105 - Août (CSV)", type=["csv"])

if st.sidebar.button("Traiter les fichiers", type="primary"):
    if not (file_105 or file_chs or file_profs or file_primaire or file_aout):
        st.sidebar.error("Veuillez téléverser au moins un fichier.")
    else:
        with st.spinner("Traitement et indexation des données en mémoire locale..."):
            df_105_raw = load_csv_robust(file_105) if file_105 else None
            df_profs_raw = load_csv_robust(file_profs) if file_profs else None
            df_prim = load_csv_robust(file_primaire) if file_primaire else None

            # Détection de permutation accidentelle : fichier profs déposé dans le champ 1 (sans CD_PERMN)
            if df_105_raw is not None and not df_105_raw.empty:
                cols_upper = [str(c).replace("\ufeff", "").strip().upper() for c in df_105_raw.columns]
                if "CD_PERMN" not in cols_upper and any(k in cols_upper for k in ["ENSEIGN", "ENSEIGNANT", "PROF", "TEACHER"]):
                    st.sidebar.warning("⚠️ Le fichier déposé dans le champ 1 semble être la liste d'enseignants (colonne ENSEIGN détectée, absence de CD_PERMN). Il a été automatiquement réaffecté au champ 3.")
                    if df_profs_raw is None or df_profs_raw.empty:
                        df_profs_raw = df_105_raw
                    df_105_raw = None

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

            if df_profs_raw is not None and not df_profs_raw.empty:
                set_df_profs(df_profs_raw)

            if df_105_raw is not None or df_chs is not None:
                df_merged = clean_and_merge_data(df_105_raw, None, df_chs, df_profs_raw, df_prim)
                set_df_main(df_merged)
                if df_prim is not None and not df_prim.empty:
                    set_df_primaire(df_prim)
                if df_chs is not None and not df_chs.empty:
                    set_df_moderation(df_chs)
                if file_aout:
                    df_ao = load_csv_robust(file_aout)
                    if not df_ao.empty:
                        set_df_aout(df_ao)

                success_msg = f"✅ Données scolaires chargées ({len(df_merged):,} lignes élèves/notes) !"
                if "ENSEIGN" in df_merged.columns:
                    nb_matched = int(df_merged["ENSEIGN"].dropna().count())
                    pct = (nb_matched / len(df_merged) * 100) if len(df_merged) > 0 else 0
                    success_msg += f"\n- {nb_matched:,} attributions enseignants appariées ({pct:.1f}%)."
                st.sidebar.success(success_msg)
            elif df_profs_raw is not None and not df_profs_raw.empty:
                nb_groupes = len(df_profs_raw)
                col_ens = next((c for c in df_profs_raw.columns if "ENSEIGN" in str(c).upper()), None)
                nb_ens = df_profs_raw[col_ens].nunique() if col_ens else 0
                st.sidebar.success(f"✅ Liste enseignants chargée : {nb_groupes:,} groupes ({nb_ens} enseignants uniques).")
                st.sidebar.info("💡 Pour débloquer les analyses macro/méso/micro, téléversez maintenant le fichier CHAP060105 (champ 1) ou CHS040506R (champ 2).")
            elif df_prim is not None and not df_prim.empty:
                set_df_primaire(df_prim)
                st.sidebar.success(f"✅ Données primaires chargées : {len(df_prim):,} élèves.")
                st.sidebar.info("💡 Téléversez également le fichier CHAP060105 (champ 1) pour croiser les profils Janosz avec les résultats.")
            else:
                st.sidebar.error("Veuillez téléverser au moins un fichier de notes (CHAP060105 ou CHS040506R).")

            import gc
            del df_105_raw, df_chs
            gc.collect()

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
st.markdown("##### Outil d'Analyse Stratégique, Docimologique et Prescriptive — Cadre Dumaresq (2017) & Voyer (2011)")

# -----------------------------------------------------------------------------
# 2. DÉFINITION DES ANALYSES MACRO, MÉSO, MICRO ET GPS (TABLEAU CENTRAL)
# -----------------------------------------------------------------------------

st.info("""
🧭 **Au palier Macro — Pilotage Systémique & Diplomation :**
Le tableau de bord met en lumière les situations critiques où les difficultés dans une matière déclenchent des **échecs en cascade** compromettant la trajectoire vers la diplomation.
* **Indicateurs pivots :** Dénombrement et caractérisation des élèves cumulant **2 et 3 échecs** aux matières à sanction ministérielle de 4ᵉ et 5ᵉ secondaire (Français, Mathématiques CST/SN/TS, Science ST/ATS, Histoire, Anglais).
* **Analyses différentielles :** Croisement systématique selon le genre (Garçons vs Filles) et la vulnérabilité (Élèves avec Plan d'intervention actif / codes de difficultés EHDAA). Modélisation matricielle et diagrammes de Venn identifiant les carrefours disciplinaires d'échecs les plus pénalisants.
* **Rôle d'action :** Il revient à la Direction générale et à la Direction des services éducatifs d'orchestrer l'allocation ciblée des ressources d'appui, de lever les freins structurels à la diplomation et de converger vers les cibles du Plan d'engagement vers la réussite (PEVR).
""")

st.info("""
⚖️ **Au palier Méso — Équité & Modération des Notes :**
Le tableau de bord détecte et objective les **distorsions évaluatives** entre le jugement professionnel de l'école et l'épreuve externe ministérielle, protégeant l'équité des élèves lors de la conversion statistique des notes (CHS040506R).
* **Indicateurs pivots :** Détection d'anomalies par la **taille de l'effet ($d$ de Cohen)** et le **ratio de dispersion ($R$)** :
  - *Groupes surévalués (Indulgence, $d > +0{,}8$) :* Notation école nettement plus généreuse que l'épreuve externe, exposant les élèves à une décote statistique sévère lors de la modération.
  - *Groupes sous-évalués (Sévérité, $d < -0{,}8$) :* Notation école anormalement sévère par rapport à la performance ministérielle externe.
  - *Homogénéisation artificielle ($R < 0{,}6$) :* Écrasement ou compression de la notation interne autour de la moyenne, gommant la discrimination des compétences réelles.
* **Rôle d'action :** Les directions d'école, accompagnées des conseillers pédagogiques, ont la responsabilité de réguler les pratiques évaluatives d'équipe pour harmoniser les barèmes sommatifs avec le niveau de rigueur ministériel.
""")

st.info("""
🔬 **Au palier Micro — Diagnostic Didactique des Épreuves & Classes :**
Le tableau de bord sonde la **cohérence didactique interne** et les conditions réelles d'évaluation au sein de chaque établissement et groupe-classe.
* **Indicateur pivot :** Analyse diagnostique approfondie de l'**écart significatif entre les compétences d'une même matière** :
  - *Mathématiques (4e sec.) :* Écart critique entre **Résoudre une situation-problème (C1)** et **Utiliser un raisonnement mathématique (C2)** au sein de chaque groupe-école.
  - *Sciences & Technologies (4e sec.) :* Comparaison fine entre le **Volet pratique (Laboratoire / C1)** et le **Volet théorique (C2)**.
  - *Français (Langue d'enseignement 4e/5e sec.) :* Analyse croisée de la **Communication orale (C1)**, de la **Lecture / Compréhension (C2)** et de l'**Écriture / Rédaction (C3)**.
* **Effets détectés :** Mise en évidence des ruptures d'apprentissage et des biais d'étalonnage où une compétence locale sert de « coussin compensatoire » artificiel masquant les lacunes d'une compétence ministérielle. Permet de réétalonner les épreuves locales avec les cadres d'évaluation du MEQ.
""")

st.info("""
🎯 **Le module Prescription — Triage GPS & Typologie de Risque Janosz :**
Le module opérationnel cible en amont les élèves vulnérables pour intervenir avec précision et prévenir le redoublement complet.
* **Zone frontière (55 % - 59 %) :** Aiguillage stratégique vers l'école d'été, validation ciblée des acquis par distillation des compétences et préparation individualisée aux reprises d'épreuves.
* **Typologie de dépistage reconnue par le MEQ (Modèle Janosz / Potvin) :** Croisement du rendement académique et de l'engagement comportemental (absentéisme, retards, incidents disciplinaires) :
  - 🟢 *Élèves sans risque élevé :* Profil conforme et sécurisé.
  - 🔵 *Discrets (~40 %) :* Rendement fragile ou frontière sans signe comportemental annonciateur (difficultés invisibles requérant un dépistage fin).
  - 🟡 *Désengagés (~33 %) :* Rupture du lien scolaire, absentéisme élevé et retards répétés.
  - 🟠 *Sous-performants (~17 %) :* Rendement déficitaire persistant malgré une présence assidue.
  - 🔴 *Inadaptés (~10 %) :* Cumul d'échecs sévères, absentéisme chronique et signalements comportementaux.
* **Matrice 2D interactive :** Cartographie dynamique croisant note globale et assiduité pour prioriser les plans d'intervention individualisés.
""")

# -----------------------------------------------------------------------------
# 3. BANDEAU DE CONFORMITÉ LOI 25, ÉTHIQUE & PERFORMANCE
# -----------------------------------------------------------------------------
st.info("""
🔒 **Gouvernance Éthique, Conformité stricte Loi 25 & Performance WebAssembly :**
* **Confidentialité absolue :** Aucune donnée nominative ni ministérielle ne quitte votre poste de travail. L'ingestion, le nettoyage, l'anonymisation et l'ensemble des analyses s'exécutent intégralement et exclusivement dans la mémoire vive de votre navigateur via **WebAssembly / Pyodide (Stlite)**.
* **Protection de l'identité des élèves :** Application rigoureuse de la règle de **suppression automatique des petites cellules ($N < 5$ élèves)** dans tous les tableaux, graphiques et métriques.
* **Déontologie et accompagnement des enseignants :** Désensibilisation automatique des noms d'enseignants par défaut (`[Enseignant masqué]`). L'affichage nominatif est soumis à un consentement explicite (*opt-in*) engageant la responsabilité professionnelle du gestionnaire dans une posture d'accompagnement bienveillant.
""")

# -----------------------------------------------------------------------------
# 4. APERÇU DES DONNÉES DÉSENSIBILISÉES (SI CHARGÉES)
# -----------------------------------------------------------------------------
if not df_main.empty:
    st.success("Données chargées avec succès ! Naviguez via le menu latéral pour consulter les modules.")
    st.subheader("Aperçu des 10 premières lignes (Données désensibilisées)")
    df_disp = st.session_state.get("df_filtered", df_main)
    st.dataframe(sanitize_df_for_stlite(df_disp.head(10)), use_container_width=True)

df_profs_loaded = get_df_profs()
if not df_profs_loaded.empty:
    with st.expander("👨‍🏫 Structure Enseignants / Groupes importée en mémoire", expanded=df_main.empty):
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Affectations (groupes)", f"{len(df_profs_loaded):,}")
        col_ens = next((c for c in df_profs_loaded.columns if "ENSEIGN" in str(c).upper()), None)
        col_p2.metric("Enseignants uniques", f"{df_profs_loaded[col_ens].nunique():,}" if col_ens else "N/A")
        col_org = next((c for c in df_profs_loaded.columns if any(k in str(c).upper() for k in ["CD_ORGNS", "ECOLE", "ÉCOLE"])), None)
        col_p3.metric("Écoles couvertes", f"{df_profs_loaded[col_org].nunique():,}" if col_org else "N/A")
        st.dataframe(sanitize_df_for_stlite(df_profs_loaded.head(15)), use_container_width=True)
        st.caption("🔒 Conformité Loi 25 : Les noms d'enseignants sont désensibilisés par défaut dans les rapports et graphiques. Activez l'opt-in dans la barre latérale des pages d'analyse pour les afficher.")

render_about_data(
    source_name="Fichiers ministériels CHAP060105 (Notes élèves) et CHS040506R (Tables de modération)",
    limits=[
        "Le tableau de bord opère sur les extractions de sessions régulières.",
        "Les règles de suppression des petites cellules (< 5 élèves) sont automatiquement appliquées dans tous les modules."
    ]
)
