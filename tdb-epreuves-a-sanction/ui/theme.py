# -*- coding: utf-8 -*-
"""
ui/theme.py - Charte graphique sobre conforme aux normes du Gouvernement du Québec (theme-quebec.css).
Interface professionnelle, accessible et libre de tout émoji.
"""

from typing import Dict, Any

# Palette officielle du Gouvernement du Québec
PRIMARY_QUEBEC: str = "#1472BF"    # Bleu standard
SECONDARY_QUEBEC: str = "#095797"  # Bleu foncé PIV
ACCENT_QUEBEC: str = "#f59e0b"     # Ambre / Or
DANGER_QUEBEC: str = "#ef4444"     # Rouge sobre
SUCCESS_QUEBEC: str = "#10b981"    # Vert validation
BG_QUEBEC: str = "#ffffff"         # Fenêtre principale blanche
SIDEBAR_QUEBEC: str = "#e8f4f6"    # Barre latérale bleu-vert pâle
PANEL_QUEBEC: str = "#ffffff"      # Fond des panneaux
BORDER_QUEBEC: str = "#cbd5e1"     # Bordures douces
TEXT_QUEBEC: str = "#0f172a"       # Texte principal
MUTED_QUEBEC: str = "#64748b"      # Texte secondaire

# Alias pour compatibilité
BLEU_QUEBEC = PRIMARY_QUEBEC
BLEU_QUEBEC_DARK = SECONDARY_QUEBEC
BLEU_QUEBEC_LIGHT = "#f0f7fd"
OR_QUEBEC = ACCENT_QUEBEC

# Couleurs d'état (Conformes WCAG AA, sobres, sans émoji)
STATUS_CONFIG: Dict[str, Dict[str, str]] = {
    "success": {
        "color": SUCCESS_QUEBEC,
        "bg": "#ecfdf5",
        "border": SUCCESS_QUEBEC,
        "icon": "",
        "symbol": "circle",
        "label": "Favorable"
    },
    "warning": {
        "color": ACCENT_QUEBEC,
        "bg": "#fffbeb",
        "border": ACCENT_QUEBEC,
        "icon": "",
        "symbol": "triangle-up",
        "label": "Vigilance"
    },
    "danger": {
        "color": DANGER_QUEBEC,
        "bg": "#fef2f2",
        "border": DANGER_QUEBEC,
        "icon": "",
        "symbol": "square",
        "label": "Alerte prioritaire"
    },
    "neutral": {
        "color": PRIMARY_QUEBEC,
        "bg": BLEU_QUEBEC_LIGHT,
        "border": PRIMARY_QUEBEC,
        "icon": "",
        "symbol": "diamond",
        "label": "Neutre"
    }
}

# Palette discrète daltonien-safe
PALETTE_ACCESSIBLE: list[str] = [
    PRIMARY_QUEBEC,    # Bleu Québec standard (#1472BF)
    SECONDARY_QUEBEC,  # Bleu PIV foncé (#095797)
    ACCENT_QUEBEC,     # Ambre / Accent (#f59e0b)
    SUCCESS_QUEBEC,    # Vert validation (#10b981)
    "#38bdf8",         # Bleu ciel
    MUTED_QUEBEC,      # Gris ardoise (#64748b)
    "#8b5cf6",         # Violet doux
    "#ec4899"          # Rose sobre
]

# Mapping direct des anomalies de modération pour Plotly (Sans émojis)
ANOMALIE_MAP: Dict[str, Dict[str, Any]] = {
    "Surévalué (Indulgence)": {
        "color": DANGER_QUEBEC,
        "symbol": "triangle-up",
        "icon": ""
    },
    "Sous-évalué (Sévérité)": {
        "color": PRIMARY_QUEBEC,
        "symbol": "triangle-down",
        "icon": ""
    },
    "Compression des notes": {
        "color": ACCENT_QUEBEC,
        "symbol": "diamond",
        "icon": ""
    },
    "Normal": {
        "color": MUTED_QUEBEC,
        "symbol": "circle",
        "icon": ""
    }
}

PLOTLY_LAYOUT_DEFAULTS: Dict[str, Any] = {
    "font": {"family": "system-ui, -apple-system, sans-serif", "size": 12, "color": TEXT_QUEBEC},
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(241, 245, 249, 0.6)",
    "margin": {"l": 40, "r": 30, "t": 50, "b": 40},
    "hovermode": "closest"
}

QUEBEC_CSS: str = """
/* Normes Gouvernement du Québec - Style sobre sans émoji */
:root {
    --bg: #ffffff;
    --sidebar-bg: #e8f4f6;
    --panel: #ffffff;
    --border: #cbd5e1;
    --text: #0f172a;
    --muted: #64748b;
    --primary: #1472BF;
    --secondary: #095797;
    --accent: #f59e0b;
    --danger: #ef4444;
    --success: #10b981;
}

body, .stApp {
    background-color: var(--bg) !important;
    color: var(--text);
    font-family: system-ui, -apple-system, sans-serif;
}

[data-testid="stHeader"] {
    background: var(--panel) !important;
    border-bottom: 3px solid var(--primary);
}

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: var(--secondary);
    font-weight: 700;
}

h1 {
    color: var(--secondary);
    font-weight: 700;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    margin-bottom: 16px;
}

h2, h3, h4 {
    color: var(--secondary);
    font-weight: 600;
}

.stButton > button[kind="primary"],
button[data-testid="baseButton-primary"] {
    background-color: var(--primary) !important;
    border-color: var(--primary) !important;
    color: #ffffff !important;
    border-radius: 4px !important;
    font-weight: 600 !important;
    transition: background-color 0.2s ease;
}

.stButton > button[kind="primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
    background-color: var(--secondary) !important;
    border-color: var(--secondary) !important;
}

.stButton > button[kind="secondary"],
button[data-testid="baseButton-secondary"] {
    background-color: #ffffff !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 4px !important;
    font-weight: 500 !important;
}

.stButton > button[kind="secondary"]:hover,
button[data-testid="baseButton-secondary"]:hover {
    background-color: #f1f5f9 !important;
    border-color: var(--primary) !important;
    color: var(--primary) !important;
}

button[data-baseweb="tab"] {
    font-family: system-ui, -apple-system, sans-serif !important;
    color: var(--muted) !important;
    font-weight: 500 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom-color: var(--primary) !important;
    font-weight: 700 !important;
}

[data-testid="stExpander"] {
    background: var(--panel);
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

[data-testid="stExpander"] summary {
    color: var(--secondary) !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"] {
    color: var(--secondary) !important;
    font-weight: 700 !important;
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.8rem !important;
}
"""


def inject_quebec_theme() -> None:
    """Injecte la feuille de style sobre conforme au Gouvernement du Québec."""
    try:
        import streamlit as st
        st.markdown(f"<style>{QUEBEC_CSS}</style>", unsafe_allow_html=True)
    except Exception:
        pass


