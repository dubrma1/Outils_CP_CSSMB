# -*- coding: utf-8 -*-
"""
Planificateur PFAE (FPT 1, 2, 3 & FMS)
Application Web interactive basée sur Streamlit et stlite pour Azure Static Web Apps.
Conforme aux programmes québécois du PFAE et aux documents de référence (Dalbé-Viau, etc.).
"""

import streamlit as st
import json
import os
import copy
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Planificateur PFAE - FPT & FMS",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé pour l'interface et l'impression
st.markdown("""
<style>
    /* Titre et badges */
    .main-header {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #4B5563;
        font-size: 1.05rem;
        margin-bottom: 1.2rem;
    }
    .badge-parcours {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    /* Cartes des étapes */
    .etape-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 10px 14px;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        font-size: 1.05rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .etape-header-2 {
        background: linear-gradient(135deg, #0D9488 0%, #14B8A6 100%);
    }
    .etape-header-3 {
        background: linear-gradient(135deg, #7C3AED 0%, #8B5CF6 100%);
    }
    
    .theme-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-left: 5px solid #3B82F6;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .theme-card:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.08);
        border-left-color: #1D4ED8;
    }
    
    .theme-title {
        font-weight: 700;
        font-size: 1rem;
        color: #111827;
        margin-bottom: 4px;
    }
    .theme-desc {
        font-size: 0.88rem;
        color: #4B5563;
        margin-bottom: 8px;
        line-height: 1.35;
    }
    .theme-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 8px;
        font-size: 0.78rem;
    }
    .tag-comp {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 2px 7px;
        border-radius: 4px;
        font-weight: 600;
    }
    .tag-axe {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 2px 7px;
        border-radius: 4px;
    }
    .tag-duree {
        background-color: #F3F4F6;
        color: #374151;
        padding: 2px 7px;
        border-radius: 4px;
    }
    .tag-sae {
        background-color: #DCFCE7;
        color: #166534;
        padding: 2px 7px;
        border-radius: 4px;
        font-style: italic;
    }
    
    /* Table globale */
    .globale-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        font-size: 0.85rem;
    }
    .globale-table th, .globale-table td {
        border: 1px solid #D1D5DB;
        padding: 8px 10px;
        vertical-align: top;
    }
    .globale-table th {
        background-color: #1E3A8A;
        color: white;
        text-align: left;
    }
    .globale-table tr:nth-child(even) {
        background-color: #F9FAFB;
    }
    
    /* Boutons compacts */
    div[data-testid="stHorizontalBlock"] button {
        padding: 0.2rem 0.4rem;
        font-size: 0.8rem;
    }
    
    @media print {
        header, footer, [data-testid="stSidebar"], .stButton, div[data-testid="stToolbar"] {
            display: none !important;
        }
        body, .main {
            background-color: white !important;
            color: black !important;
        }
        .theme-card {
            border: 1px solid #999 !important;
            box-shadow: none !important;
            page-break-inside: avoid;
        }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_default_curriculum():
    """Charge les données de référence à partir du fichier JSON."""
    json_path = "curriculum_data.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        st.error(f"Fichier {json_path} introuvable. Veuillez exécuter enrich_curriculum.py.")
        return {"parcours": {}, "themes_integres": []}


# Initialisation de session_state pour la persistance des modifications
if "curriculum" not in st.session_state:
    st.session_state.curriculum = copy.deepcopy(load_default_curriculum())

if "selected_parcours" not in st.session_state:
    st.session_state.selected_parcours = "FPT1"

if "selected_matiere" not in st.session_state:
    st.session_state.selected_matiere = "francais"

if "editing_theme_id" not in st.session_state:
    st.session_state.editing_theme_id = None


# Fonctions utilitaires de manipulation de données
def get_current_parcours_data():
    p_key = st.session_state.selected_parcours
    return st.session_state.curriculum.get("parcours", {}).get(p_key, {})

def get_current_matiere_data():
    p_data = get_current_parcours_data()
    m_key = st.session_state.selected_matiere
    matieres = p_data.get("matieres", {})
    if m_key not in matieres and matieres:
        st.session_state.selected_matiere = list(matieres.keys())[0]
        m_key = st.session_state.selected_matiere
    return matieres.get(m_key, {})

def move_theme_step(matiere_key, from_step, to_step, theme_idx):
    """Déplace un thème d'une étape à une autre."""
    p_key = st.session_state.selected_parcours
    etapes = st.session_state.curriculum["parcours"][p_key]["matieres"][matiere_key]["etapes"]
    if 0 <= theme_idx < len(etapes[from_step]):
        theme = etapes[from_step].pop(theme_idx)
        etapes[to_step].append(theme)

def reorder_theme(matiere_key, step, theme_idx, direction):
    """Déplace la position d'un thème à l'intérieur de sa colonne (haut/bas)."""
    p_key = st.session_state.selected_parcours
    theme_list = st.session_state.curriculum["parcours"][p_key]["matieres"][matiere_key]["etapes"][step]
    new_idx = theme_idx + direction
    if 0 <= new_idx < len(theme_list):
        theme_list[theme_idx], theme_list[new_idx] = theme_list[new_idx], theme_list[theme_idx]

def delete_theme(matiere_key, step, theme_idx):
    """Supprime un thème."""
    p_key = st.session_state.selected_parcours
    etapes = st.session_state.curriculum["parcours"][p_key]["matieres"][matiere_key]["etapes"]
    if 0 <= theme_idx < len(etapes[step]):
        etapes[step].pop(theme_idx)

def add_new_theme(matiere_key, step, titre, desc, comp_list, duree, axe, sae, ressources):
    """Ajoute un nouveau thème personnalisé."""
    p_key = st.session_state.selected_parcours
    etapes = st.session_state.curriculum["parcours"][p_key]["matieres"][matiere_key]["etapes"]
    import uuid
    new_id = f"custom_{str(uuid.uuid4())[:8]}"
    new_theme = {
        "id": new_id,
        "titre": titre.strip() if titre else "Nouveau thème",
        "description": desc.strip(),
        "competences": comp_list,
        "duree_semaines": int(duree) if duree else 4,
        "axe_thematique": axe.strip() if axe else "Général",
        "sae_projet": sae.strip() if sae else "",
        "ressources": ressources.strip() if ressources else ""
    }
    etapes[step].append(new_theme)


# ==================== BARRE LATÉRALE (SIDEBAR) ====================
with st.sidebar:
    st.markdown("## 🧭 Parcours PFAE")
    
    parcours_options = {
        "FPT1": "🎓 FPT 1 (An 1 - Transition & Ateliers)",
        "FPT2": "🛠️ FPT 2 (An 2 - Stages 1-2 jours)",
        "FPT3": "💼 FPT 3 (An 3 - Stages intensifs 3 jours)",
        "FMS": "📜 FMS (Métier semi-spécialisé - 1 an)"
    }
    
    selected_p = st.selectbox(
        "Sélectionnez le parcours :",
        options=list(parcours_options.keys()),
        format_func=lambda x: parcours_options[x],
        index=list(parcours_options.keys()).index(st.session_state.selected_parcours)
    )
    if selected_p != st.session_state.selected_parcours:
        st.session_state.selected_parcours = selected_p
        # Réinitialiser la matière sélectionnée si elle n'existe pas dans le nouveau parcours
        p_matieres = st.session_state.curriculum["parcours"][selected_p].get("matieres", {})
        if st.session_state.selected_matiere not in p_matieres and p_matieres:
            st.session_state.selected_matiere = list(p_matieres.keys())[0]
        st.rerun()

    st.markdown("---")
    st.markdown("## 📑 Mode d'affichage")
    view_mode = st.radio(
        "Mode de consultation :",
        ["📋 Planification par matière (3 étapes)", "🌐 Vue intégrée annuelle (Globale)", "💾 Sauvegarde & Téléversement"]
    )
    
    st.markdown("---")
    # Résumé rapide du parcours
    current_p_data = get_current_parcours_data()
    matieres_dict = current_p_data.get("matieres", {})
    total_themes_p = sum(sum(len(m["etapes"][e]) for e in ["etape1", "etape2", "etape3"]) for m in matieres_dict.values())
    
    st.markdown(f"**Parcours actif :** `{st.session_state.selected_parcours}`")
    st.markdown(f"**Matières au programme :** `{len(matieres_dict)}`")
    st.markdown(f"**Thèmes d'apprentissage :** `{total_themes_p}`")
    
    st.caption("Planificateur conforme aux PFEQ / PFAE du Ministère de l'Éducation du Québec et aux planifications Dalbé-Viau.")


# ==================== EN-TÊTE PRINCIPAL ====================
col_title, col_stat = st.columns([3, 1])
with col_title:
    st.markdown(f"<h1 class='main-header'>Planificateur PFAE : {current_p_data.get('titre', 'Formation')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>{current_p_data.get('description', '')}</p>", unsafe_allow_html=True)

with col_stat:
    st.markdown(f"""
    <div style="background-color: #F3F4F6; padding: 10px 14px; border-radius: 8px; text-align: center; border: 1px solid #E5E7EB;">
        <span style="font-size: 0.85rem; color: #4B5563; font-weight: 600;">Parcours en cours</span><br>
        <span style="font-size: 1.4rem; color: #1E3A8A; font-weight: bold;">{st.session_state.selected_parcours}</span>
    </div>
    """, unsafe_allow_html=True)


# ==================== VUE 1 : PLANIFICATION PAR MATIÈRE (3 ÉTAPES) ====================
if view_mode == "📋 Planification par matière (3 étapes)":
    
    # Sélecteur de matière
    matieres_keys = list(matieres_dict.keys())
    if not matieres_keys:
        st.warning("Aucune matière configurée pour ce parcours.")
    else:
        # Sélecteur en onglets ou boutons radio horizontaux
        cols_m = st.columns(min(len(matieres_keys), 6))
        
        # Selectbox convivial pour la matière
        def format_m(key):
            m_info = matieres_dict.get(key, {})
            return f"{m_info.get('nom', key)} ({m_info.get('code', '')})"

        selected_m = st.selectbox(
            "Sélectionnez la matière à planifier :",
            options=matieres_keys,
            format_func=format_m,
            index=matieres_keys.index(st.session_state.selected_matiere) if st.session_state.selected_matiere in matieres_keys else 0
        )
        if selected_m != st.session_state.selected_matiere:
            st.session_state.selected_matiere = selected_m
            st.rerun()

        m_data = get_current_matiere_data()
        
        # Encart d'information sur la matière
        with st.expander(f"ℹ️ Références et compétences de : **{m_data.get('nom')}** ({m_data.get('code')})", expanded=False):
            st.markdown(f"**Enseignant(e)s / Document de référence :** {m_data.get('enseignant_ref', 'Planification officielle')}")
            
            # Compétences du programme
            st.markdown("**Compétences ciblées au programme :**")
            for c in m_data.get("competences", []):
                st.markdown(f"- **{c.get('code')}** - *{c.get('titre')}* : {c.get('desc')}")
                
            # Pondération aux bulletins scolaires
            pond = m_data.get("ponderation", {})
            st.markdown(f"""
            **Pondération officielle aux bulletins :**
            - **1re étape :** `{pond.get('etape1', '20 %')}`
            - **2e étape :** `{pond.get('etape2', '20 %')}`
            - **3e étape :** `{pond.get('etape3', '60 %')}`
            """)
            if m_data.get("evaluations_desc"):
                st.caption(f"Modalités : {m_data.get('evaluations_desc')}")

        st.markdown("---")
        
        # AFFICHAGE DES 3 COLONNES D'ÉTAPES (Dalbé-Viau style)
        col1, col2, col3 = st.columns(3)
        
        etapes_info = [
            ("etape1", "Étape 1 (Automne)", "20 %", col1, "etape-header"),
            ("etape2", "Étape 2 (Hiver)", "20 %", col2, "etape-header etape-header-2"),
            ("etape3", "Étape 3 (Printemps / Bilan)", "60 %", col3, "etape-header etape-header-3")
        ]
        
        for step_key, step_title, step_weight, col_obj, header_class in etapes_info:
            with col_obj:
                themes_in_step = m_data.get("etapes", {}).get(step_key, [])
                
                # En-tête de colonne avec compte et pondération
                st.markdown(f"""
                <div class='{header_class}'>
                    <span>{step_title}</span>
                    <span style='background: rgba(255,255,255,0.25); padding: 2px 8px; border-radius: 12px; font-size: 0.82rem;'>{step_weight} | {len(themes_in_step)} thèmes</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Bouton pour ajouter un nouveau thème dans cette étape
                with st.popover(f"➕ Ajouter un thème à l'{step_title.split(' ')[0]}", use_container_width=True):
                    with st.form(key=f"form_add_{st.session_state.selected_matiere}_{step_key}"):
                        st.markdown(f"**Ajouter un thème d'apprentissage - {step_title}**")
                        new_titre = st.text_input("Titre du thème ou du projet :", placeholder="ex: SAE Entretien du matériel")
                        new_desc = st.text_area("Description détaillée des activités / savoirs :", placeholder="Contenu de la situation d'apprentissage...")
                        
                        # Sélection des compétences
                        available_comps = [c.get("code") for c in m_data.get("competences", [])]
                        if not available_comps:
                            available_comps = ["C1", "C2", "C3"]
                        new_comps = st.multiselect("Compétences ciblées :", options=available_comps, default=available_comps[:1])
                        
                        col_f1, col_f2 = st.columns(2)
                        with col_f1:
                            new_duree = st.number_input("Durée estimée (semaines) :", min_value=1, max_value=20, value=4)
                        with col_f2:
                            new_axe = st.text_input("Axe thématique intégré :", value="Monde du travail / Atelier")
                            
                        new_sae = st.text_input("Nom de la SAE / Projet :", placeholder="ex: Projet Mobilier classe")
                        new_ressources = st.text_input("Ressources / Matériel :", placeholder="ex: Cahier maison, vidéos")
                        
                        btn_submit = st.form_submit_button("Ajouter à la planification", use_container_width=True)
                        if btn_submit:
                            if new_titre:
                                add_new_theme(
                                    st.session_state.selected_matiere,
                                    step_key,
                                    new_titre,
                                    new_desc,
                                    new_comps,
                                    new_duree,
                                    new_axe,
                                    new_sae,
                                    new_ressources
                                )
                                st.success("Thème ajouté avec succès !")
                                st.rerun()
                            else:
                                st.error("Le titre est obligatoire.")

                # Liste des cartes de thèmes pour cette étape
                for idx, theme in enumerate(themes_in_step):
                    theme_id = theme.get("id", f"{step_key}_{idx}")
                    
                    # Construction des badges de compétences
                    comp_badges = "".join([f"<span class='tag-comp'>{c}</span>" for c in theme.get("competences", [])])
                    axe_badge = f"<span class='tag-axe'>{theme.get('axe_thematique', '')}</span>" if theme.get("axe_thematique") else ""
                    duree_badge = f"<span class='tag-duree'>⏱️ {theme.get('duree_semaines', 4)} sem.</span>"
                    sae_badge = f"<span class='tag-sae'>📁 {theme.get('sae_projet', '')}</span>" if theme.get("sae_projet") else ""
                    
                    # Rendu de la carte
                    st.markdown(f"""
                    <div class='theme-card'>
                        <div class='theme-title'>{idx+1}. {theme.get('titre')}</div>
                        <div class='theme-desc'>{theme.get('description', '')}</div>
                        <div class='theme-meta'>
                            {comp_badges}
                            {duree_badge}
                            {axe_badge}
                            {sae_badge}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Barre d'actions sous chaque carte (Déplacer entre colonnes, réordonner, modifier, supprimer)
                    col_act1, col_act2, col_act3, col_act4, col_act5 = st.columns([1, 1, 1.2, 1, 1])
                    
                    # Déplacer vers la colonne précédente
                    with col_act1:
                        target_prev = "etape1" if step_key == "etape2" else ("etape2" if step_key == "etape3" else None)
                        if target_prev:
                            if st.button("⬅️", key=f"move_prev_{theme_id}_{idx}", help=f"Déplacer vers l'{target_prev.replace('etape', 'Étape ')}"):
                                move_theme_step(st.session_state.selected_matiere, step_key, target_prev, idx)
                                st.rerun()
                                
                    # Déplacer vers la colonne suivante
                    with col_act2:
                        target_next = "etape2" if step_key == "etape1" else ("etape3" if step_key == "etape2" else None)
                        if target_next:
                            if st.button("➡️", key=f"move_next_{theme_id}_{idx}", help=f"Déplacer vers l'{target_next.replace('etape', 'Étape ')}"):
                                move_theme_step(st.session_state.selected_matiere, step_key, target_next, idx)
                                st.rerun()

                    # Monter / Descendre dans la même colonne
                    with col_act3:
                        sub_c1, sub_c2 = st.columns(2)
                        with sub_c1:
                            if idx > 0:
                                if st.button("⬆️", key=f"up_{theme_id}_{idx}", help="Monter"):
                                    reorder_theme(st.session_state.selected_matiere, step_key, idx, -1)
                                    st.rerun()
                        with sub_c2:
                            if idx < len(themes_in_step) - 1:
                                if st.button("⬇️", key=f"down_{theme_id}_{idx}", help="Descendre"):
                                    reorder_theme(st.session_state.selected_matiere, step_key, idx, 1)
                                    st.rerun()

                    # Modifier le thème
                    with col_act4:
                        with st.popover("✏️", help="Modifier"):
                            with st.form(key=f"edit_form_{theme_id}_{idx}"):
                                st.markdown(f"**Modifier le thème : {theme.get('titre')}**")
                                ed_titre = st.text_input("Titre :", value=theme.get("titre", ""))
                                ed_desc = st.text_area("Description :", value=theme.get("description", ""))
                                
                                available_comps = [c.get("code") for c in m_data.get("competences", [])]
                                if not available_comps:
                                    available_comps = ["C1", "C2", "C3"]
                                current_comps = [c for c in theme.get("competences", []) if c in available_comps]
                                ed_comps = st.multiselect("Compétences :", options=available_comps, default=current_comps)
                                
                                ed_duree = st.number_input("Durée (semaines) :", min_value=1, max_value=20, value=int(theme.get("duree_semaines", 4)))
                                ed_axe = st.text_input("Axe thématique :", value=theme.get("axe_thematique", ""))
                                ed_sae = st.text_input("SAE / Projet :", value=theme.get("sae_projet", ""))
                                ed_ressources = st.text_input("Ressources :", value=theme.get("ressources", ""))
                                
                                if st.form_submit_button("Enregistrer les modifications", use_container_width=True):
                                    theme["titre"] = ed_titre
                                    theme["description"] = ed_desc
                                    theme["competences"] = ed_comps
                                    theme["duree_semaines"] = ed_duree
                                    theme["axe_thematique"] = ed_axe
                                    theme["sae_projet"] = ed_sae
                                    theme["ressources"] = ed_ressources
                                    st.success("Modifications enregistrées !")
                                    st.rerun()

                    # Supprimer le thème
                    with col_act5:
                        with st.popover("🗑️", help="Supprimer"):
                            st.write(f"Supprimer définitivement **{theme.get('titre')}** ?")
                            if st.button("Confirmer la suppression", key=f"del_confirm_{theme_id}_{idx}", type="primary"):
                                delete_theme(st.session_state.selected_matiere, step_key, idx)
                                st.rerun()


# ==================== VUE 2 : VUE INTÉGRÉE ANNUELLE (GLOBALE) ====================
elif view_mode == "🌐 Vue intégrée annuelle (Globale)":
    st.markdown("### 🌐 Planification Globale Annuelle Interdisciplinaire")
    st.markdown("""
    Cette vue intégrée synthétise l'ensemble des matières par grand axe thématique ou par étape de bulletin,
    à l'image des matrices de **Planification Globale Année** de référence.
    """)
    
    # Filtres de visualisation
    col_filtre1, col_filtre2 = st.columns([1, 2])
    with col_filtre1:
        filtre_etape = st.selectbox(
            "Filtrer par étape de bulletin :",
            ["Toutes les étapes (Vue annuelle complète)", "Étape 1 (Automne)", "Étape 2 (Hiver)", "Étape 3 (Printemps / Bilan)"]
        )
    with col_filtre2:
        recherche_mot = st.text_input("🔍 Rechercher un projet, une SAE ou un mot-clé :", placeholder="ex: Budget, Recette, SIMDUT, CV...")

    # Tableau croisé : Matières × Étapes
    st.markdown("#### 📊 Tableau synoptique par matière et étape")
    
    matieres_p = current_p_data.get("matieres", {})
    
    steps_to_show = ["etape1", "etape2", "etape3"]
    if "Étape 1" in filtre_etape:
        steps_to_show = ["etape1"]
    elif "Étape 2" in filtre_etape:
        steps_to_show = ["etape2"]
    elif "Étape 3" in filtre_etape:
        steps_to_show = ["etape3"]
        
    step_labels = {
        "etape1": "Étape 1 (20 %)",
        "etape2": "Étape 2 (20 %)",
        "etape3": "Étape 3 (60 %)"
    }
    
    # Construction du tableau HTML interactif et imprimable
    html_table = [
        "<div style='overflow-x: auto;'>",
        "<table class='globale-table'>",
        "<thead><tr><th style='width: 18%;'>Discipline</th>"
    ]
    for s in steps_to_show:
        html_table.append(f"<th style='width: {82//len(steps_to_show)}%;'>{step_labels[s]}</th>")
    html_table.append("</tr></thead><tbody>")
    
    for m_key, m_info in matieres_p.items():
        html_table.append(f"<tr><td><strong>{m_info.get('nom')}</strong><br><small style='color: #6B7280;'>{m_info.get('code')}</small></td>")
        for s in steps_to_show:
            themes = m_info.get("etapes", {}).get(s, [])
            cell_items = []
            for t in themes:
                # Filtrage par mot-clé
                if recherche_mot:
                    mot = recherche_mot.lower()
                    if mot not in t.get("titre", "").lower() and mot not in t.get("description", "").lower() and mot not in t.get("sae_projet", "").lower():
                        continue
                        
                comps = ", ".join(t.get("competences", []))
                sae_text = f"<em>({t.get('sae_projet')})</em>" if t.get("sae_projet") else ""
                cell_items.append(f"<li><strong>{t.get('titre')}</strong> {sae_text} <span style='color: #B45309; font-size: 0.75rem;'>[{comps}]</span><br><small style='color: #4B5563;'>{t.get('description')}</small></li>")
            
            if cell_items:
                html_table.append(f"<td><ul style='margin: 0; padding-left: 18px;'>{''.join(cell_items)}</ul></td>")
            else:
                html_table.append("<td style='color: #9CA3AF; font-style: italic;'>Aucun thème correspondant</td>")
        html_table.append("</tr>")
        
    html_table.append("</tbody></table></div>")
    
    st.markdown("".join(html_table), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # MATRICE CROISÉE PAR AXE THÉMATIQUE (Style Planification-globale-annee-1.docx)
    st.markdown("#### 🧩 Matrice des Projets Intégrés et Thèmes Ministériels")
    st.caption("Croisement entre les axes thématiques (Santé, Monde du travail, Autonomie financière...) et les disciplines.")
    
    themes_integres = st.session_state.curriculum.get("themes_integres", [])
    
    # Pour chaque axe thématique, on liste les projets dans les différentes matières
    for axe in themes_integres:
        axe_name = axe.get("nom")
        with st.expander(f"📁 Axe : {axe_name}", expanded=False):
            st.markdown(f"**Sous-thèmes ministériels :** {', '.join(axe.get('sous_themes', []))}")
            
            # Recherche des thèmes correspondants dans toutes les matières du parcours actuel
            found_count = 0
            cols_grid = st.columns(3)
            col_idx = 0
            
            for m_key, m_info in matieres_p.items():
                m_matches = []
                for s_key in ["etape1", "etape2", "etape3"]:
                    for t in m_info.get("etapes", {}).get(s_key, []):
                        axe_th = t.get("axe_thematique", "").lower()
                        axe_kw = axe_name.lower().split(" ")[0]
                        if axe_kw in axe_th or any(st.lower() in t.get("titre", "").lower() for st in axe.get("sous_themes", [])):
                            m_matches.append((s_key, t))
                            
                if m_matches:
                    found_count += 1
                    target_col = cols_grid[col_idx % 3]
                    with target_col:
                        st.markdown(f"**{m_info.get('nom')}**")
                        for s_key, t in m_matches:
                            st.markdown(f"- `{step_labels[s_key].split(' ')[0]}` **{t.get('titre')}**")
                            if t.get("sae_projet"):
                                st.caption(f"Projet : {t.get('sae_projet')}")
                    col_idx += 1
                    
            if found_count == 0:
                st.info("Aucun projet spécifiquement étiqueté pour cet axe dans ce parcours.")

    # Bouton d'impression
    st.markdown("---")
    col_p1, col_p2 = st.columns([1, 4])
    with col_p1:
        st.button("🖨️ Imprimer la vue intégrée", on_click=None, help="Utilisez Ctrl+P dans votre navigateur pour imprimer ou exporter en PDF.", use_container_width=True)
    with col_p2:
        st.info("💡 Astuce : Utilisez le raccourci **Ctrl+P** (ou Cmd+P sur Mac) pour générer un PDF de votre planification intégrée au format paysage.")


# ==================== VUE 3 : SAUVEGARDE & TÉLÉVERSEMENT ====================
elif view_mode == "💾 Sauvegarde & Téléversement":
    st.markdown("### 💾 Gestion, Sauvegarde et Téléversement de votre Planification")
    st.markdown("""
    Sauvegardez l'ensemble de vos choix dans un fichier JSON pour les conserver ou les partager.
    Vous pourrez ensuite réimporter votre fichier à tout moment pour reprendre votre édition.
    """)
    
    col_export, col_import = st.columns(2)
    
    with col_export:
        st.markdown("#### 📤 Exporter ma planification")
        st.markdown("Téléchargez une copie complète contenant vos personnalisations pour tous les parcours (FPT1, FPT2, FPT3, FMS).")
        
        json_data_str = json.dumps(st.session_state.curriculum, ensure_ascii=False, indent=2)
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_name = f"planification_pfae_{st.session_state.selected_parcours.lower()}_{date_str}.json"
        
        st.download_button(
            label=f"💾 Télécharger ma planification ({st.session_state.selected_parcours}) en JSON",
            data=json_data_str,
            file_name=file_name,
            mime="application/json",
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("##### 📄 Export récapitulatif en Markdown")
        # Génération d'un résumé markdown
        md_lines = [f"# Planification Annuelle PFAE - {current_p_data.get('titre')}\n\n"]
        for m_k, m_v in matieres_p.items():
            md_lines.append(f"## {m_v.get('nom')} ({m_v.get('code')})\n")
            for s_k, s_l in [("etape1", "Étape 1 (20%)"), ("etape2", "Étape 2 (20%)"), ("etape3", "Étape 3 (60%)")]:
                md_lines.append(f"### {s_l}\n")
                for t in m_v.get("etapes", {}).get(s_k, []):
                    comps = ", ".join(t.get("competences", []))
                    md_lines.append(f"- **{t.get('titre')}** [{comps}] ({t.get('duree_semaines', 4)} sem.) : {t.get('description')}\n")
                md_lines.append("\n")
        
        st.download_button(
            label="📝 Télécharger le rapport récapitulatif en Markdown (.md)",
            data="".join(md_lines),
            file_name=f"rapport_planif_{st.session_state.selected_parcours.lower()}_{date_str}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col_import:
        st.markdown("#### 📥 Téléverser / Reprendre une planification")
        st.markdown("Sélectionnez un fichier JSON préalablement sauvegardé pour recharger vos thèmes et ordonnancements.")
        
        uploaded_file = st.file_uploader("Choisir un fichier de planification JSON :", type=["json"])
        if uploaded_file is not None:
            try:
                uploaded_content = json.load(uploaded_file)
                if "parcours" in uploaded_content:
                    if st.button("🚀 Restaurer cette planification", type="primary", use_container_width=True):
                        st.session_state.curriculum = copy.deepcopy(uploaded_content)
                        st.success("Planification restaurée avec succès !")
                        st.rerun()
                else:
                    st.error("Le fichier JSON téléversé ne possède pas la structure requise (clé 'parcours' manquante).")
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier : {e}")

    st.markdown("---")
    
    # Section de réinitialisation
    st.markdown("#### 🔄 Réinitialisation aux valeurs par défaut")
    st.caption("Attention : Cette action effacera vos modifications et rétablira les données modèles tirées des documents de référence.")
    
    col_reset1, col_reset2 = st.columns([1, 3])
    with col_reset1:
        with st.popover("⚠️ Rétablir les valeurs par défaut", use_container_width=True):
            st.write("Voulez-vous vraiment écraser toutes vos modifications ?")
            if st.button("Oui, réinitialiser tout", type="primary"):
                st.session_state.curriculum = copy.deepcopy(load_default_curriculum())
                st.success("Toutes les données ont été réinitialisées.")
                st.rerun()


# ==================== PIED DE PAGE ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.85rem; padding: 10px 0;">
    <strong>Planificateur PFAE (FPT & FMS)</strong> — Conçu pour Azure Static Web Apps avec Python et Stlite (WebAssembly) |
    Basé sur les programmes du Ministère de l'Éducation du Québec et les planifications modèles de l'école Dalbé-Viau.
</div>
""", unsafe_allow_html=True)
