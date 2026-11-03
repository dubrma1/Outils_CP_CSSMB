"""
Studio de séquences visuelles (TSA/TDL) - PFAE
Point d'entrée optionnel pour Streamlit standard ou Stlite (Pyodide WebAssembly).
"""

import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="Studio TSA/TDL - PFAE",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Chemin vers l'application autonome HTML
current_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(current_dir, "index.html")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    # Intégration plein écran du studio
    components.html(html_content, height=1200, scrolling=True)
else:
    st.error("Fichier index.html introuvable dans le dossier courant.")

