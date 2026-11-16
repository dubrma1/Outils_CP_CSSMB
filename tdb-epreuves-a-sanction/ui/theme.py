# -*- coding: utf-8 -*-
"""
ui/theme.py - Charte graphique sobre conforme aux normes du Gouvernement du Québec (theme-quebec.css).
Interface professionnelle, accessible et libre de tout émoji.
"""

import re
from typing import Any, Dict, Iterable, List
import unicodedata

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

# -----------------------------------------------------------------------------
# DICTIONNAIRES DE COULEURS COHÉRENTS (MATIÈRES, COMPÉTENCES & ÉCOLES)
# Garantit une couleur strictement identique d'un graphique à l'autre et d'une page à l'autre.
# -----------------------------------------------------------------------------
MATIERE_BASE_COLORS: Dict[str, str] = {
    "Science ST": "#1472BF",      # Bleu Québec
    "Science ATS": "#0284C7",     # Bleu azur
    "Math CST": "#10b981",        # Vert émeraude
    "Math SN": "#047857",         # Vert forêt
    "Math TS": "#0d9488",         # Sarcelle (Teal)
    "Histoire 4": "#f59e0b",      # Ambre / Or
    "Français 4": "#8b5cf6",      # Violet
    "Français 5": "#6d28d9",      # Indigo profond
    "Anglais 5 base": "#ec4899",  # Rose / Magenta sobre
    "Anglais enrichi": "#be185d", # Framboise profond
}

COMPETENCE_COLOR_MAP: Dict[str, str] = {
    "Science ST — Théorie": "#1472BF",
    "Science ST — Pratique": "#60a5fa",
    "Science ATS — Théorie": "#0284C7",
    "Science ATS — Pratique": "#38bdf8",
    "Math CST — Raisonner": "#10b981",
    "Math CST — Résoudre": "#6ee7b7",
    "Math SN — Raisonner": "#047857",
    "Math SN — Résoudre": "#34d399",
    "Math TS — Raisonner": "#0f766e",
    "Math TS — Résoudre": "#2dd4bf",
    "Histoire 4 — Épreuve": "#f59e0b",
    "Français 4 — Écriture": "#7c3aed",
    "Français 4 — Lecture": "#a78bfa",
    "Français 4 — Communication": "#c4b5fd",
    "Français 5 — Écriture": "#5b21b6",
    "Français 5 — Lecture": "#8b5cf6",
    "Français 5 — Communication": "#c084fc",
    "Anglais 5 base — Compréhension": "#db2777",
    "Anglais 5 base — Interaction": "#f472b6",
    "Anglais 5 base — Production": "#f9a8d4",
}

MATIERE_COLOR_MAP: Dict[str, str] = {
    # Noms courts
    "Science ST": MATIERE_BASE_COLORS["Science ST"],
    "Science ATS": MATIERE_BASE_COLORS["Science ATS"],
    "Math CST": MATIERE_BASE_COLORS["Math CST"],
    "Math SN": MATIERE_BASE_COLORS["Math SN"],
    "Math TS": MATIERE_BASE_COLORS["Math TS"],
    "Histoire 4": MATIERE_BASE_COLORS["Histoire 4"],
    "Histoire QC-Canada": MATIERE_BASE_COLORS["Histoire 4"],
    "Français 4": MATIERE_BASE_COLORS["Français 4"],
    "Français 5": MATIERE_BASE_COLORS["Français 5"],
    "Anglais 5 base": MATIERE_BASE_COLORS["Anglais 5 base"],
    "Anglais 5": MATIERE_BASE_COLORS["Anglais 5 base"],
    "Anglais enrichi": MATIERE_BASE_COLORS["Anglais enrichi"],

    # Clés complètes SUBJECT_MAP
    "Science ST (55444)": MATIERE_BASE_COLORS["Science ST"],
    "Science ATS (57406)": MATIERE_BASE_COLORS["Science ATS"],
    "Science ATS (57416)": MATIERE_BASE_COLORS["Science ATS"],
    "Math CST (63414)": MATIERE_BASE_COLORS["Math CST"],
    "Math SN (65426)": MATIERE_BASE_COLORS["Math SN"],
    "Math TS (64426)": MATIERE_BASE_COLORS["Math TS"],
    "Histoire QC-Canada (85404)": MATIERE_BASE_COLORS["Histoire 4"],
    "Histoire (85404)": MATIERE_BASE_COLORS["Histoire 4"],
    "Français 4 (132406)": MATIERE_BASE_COLORS["Français 4"],
    "Français 5 (132506)": MATIERE_BASE_COLORS["Français 5"],
    "Anglais 5 base (134504)": MATIERE_BASE_COLORS["Anglais 5 base"],

    # Noms d'épreuves uniques EPREUVES_MAP
    "Science ST (Théorie)": MATIERE_BASE_COLORS["Science ST"],
    "Science ATS (Théorie)": MATIERE_BASE_COLORS["Science ATS"],
    "Math CST (Raisonner)": MATIERE_BASE_COLORS["Math CST"],
    "Math SN (Raisonner)": MATIERE_BASE_COLORS["Math SN"],
    "Math TS (Raisonner)": MATIERE_BASE_COLORS["Math TS"],
    "Histoire QC-Canada (Épreuve)": MATIERE_BASE_COLORS["Histoire 4"],
    "Français 4 (Écriture)": MATIERE_BASE_COLORS["Français 4"],
    "Français 5 (Écriture)": MATIERE_BASE_COLORS["Français 5"],
    "Anglais 5 (Compréhension)": MATIERE_BASE_COLORS["Anglais 5 base"],

    # Groupements transversaux (Venn)
    "Sciences (ST/ATS)": MATIERE_BASE_COLORS["Science ST"],
    "Maths (CST/SN/TS)": MATIERE_BASE_COLORS["Math CST"],
    "Mathématiques 5": MATIERE_BASE_COLORS["Math CST"],

    # Fusion des compétences / volets
    **COMPETENCE_COLOR_MAP,
}

_BASE_ECOLE_COLORS: Dict[str, str] = {
    "037": "#1472BF",
    "038": "#095797",
    "040": "#0284C7",
    "041": "#0EA5E9",
    "042": "#2563EB",
    "135": "#16a34a",
    "136": "#10B981",
    "137": "#047857",
    "138": "#059669",
    "139": "#0D9488",
    "142": "#14B8A6",
    "144": "#65A30D",
    "236": "#F59E0B",
    "237": "#b45309",
    "238": "#D97706",
    "240": "#EA580C",
    "241": "#EF4444",
    "243": "#8B5CF6",
    "245": "#EC4899",
    "280": "#6366f1",
}

ECOLE_COLOR_MAP: Dict[str, str] = {
    **_BASE_ECOLE_COLORS,
    **{f"École {code}": color for code, color in _BASE_ECOLE_COLORS.items()},
}


def _norm_text_for_color(val: Any) -> str:
    """Normalise un libellé pour la correspondance de couleur (minuscule sans accent)."""
    s = unicodedata.normalize("NFD", str(val).strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def get_matiere_color(label: Any) -> str:
    """Retourne la couleur hexadécimale fixe associée à une matière, épreuve ou compétence."""
    if label is None:
        return MUTED_QUEBEC
    s = str(label).strip()
    if not s:
        return MUTED_QUEBEC
    if s in COMPETENCE_COLOR_MAP:
        return COMPETENCE_COLOR_MAP[s]
    if s in MATIERE_COLOR_MAP:
        return MATIERE_COLOR_MAP[s]

    s_low = _norm_text_for_color(s)

    # Correspondance par code ministériel (avec tolérance pour volets/composantes)
    if "554" in s_low or "555" in s_low:
        return COMPETENCE_COLOR_MAP["Science ST — Pratique"] if ("pratique" in s_low or "55420" in s_low) else MATIERE_BASE_COLORS["Science ST"]
    if "574" in s_low or "557" in s_low:
        return COMPETENCE_COLOR_MAP["Science ATS — Pratique"] if ("pratique" in s_low or "57420" in s_low) else MATIERE_BASE_COLORS["Science ATS"]
    if "634" in s_low:
        return COMPETENCE_COLOR_MAP["Math CST — Résoudre"] if ("resoudre" in s_low or "63410" in s_low) else MATIERE_BASE_COLORS["Math CST"]
    if "654" in s_low:
        return COMPETENCE_COLOR_MAP["Math SN — Résoudre"] if ("resoudre" in s_low or "65410" in s_low) else MATIERE_BASE_COLORS["Math SN"]
    if "644" in s_low:
        return COMPETENCE_COLOR_MAP["Math TS — Résoudre"] if ("resoudre" in s_low or "64410" in s_low) else MATIERE_BASE_COLORS["Math TS"]
    if "854" in s_low:
        return MATIERE_BASE_COLORS["Histoire 4"]
    if "1324" in s_low:
        return MATIERE_BASE_COLORS["Français 4"]
    if "1325" in s_low:
        return MATIERE_BASE_COLORS["Français 5"]
    if "1345" in s_low:
        return MATIERE_BASE_COLORS["Anglais 5 base"]

    # Correspondance par mot-clé disciplinaire (utile pour CHS040506R)
    if "science" in s_low:
        if "ats" in s_low or "applique" in s_low:
            return MATIERE_BASE_COLORS["Science ATS"]
        return MATIERE_BASE_COLORS["Science ST"]
    if "math" in s_low:
        if "sn" in s_low or "naturel" in s_low:
            return MATIERE_BASE_COLORS["Math SN"]
        if "ts" in s_low or "technico" in s_low:
            return MATIERE_BASE_COLORS["Math TS"]
        return MATIERE_BASE_COLORS["Math CST"]
    if "hist" in s_low:
        return MATIERE_BASE_COLORS["Histoire 4"]
    if "francais" in s_low:
        if "4" in s_low:
            return MATIERE_BASE_COLORS["Français 4"]
        return MATIERE_BASE_COLORS["Français 5"]
    if "anglais" in s_low:
        if "enrichi" in s_low:
            return MATIERE_BASE_COLORS["Anglais enrichi"]
        return MATIERE_BASE_COLORS["Anglais 5 base"]

    # Fallback déterministe dans la palette accessible
    idx = sum(ord(ch) for ch in s_low) % len(PALETTE_ACCESSIBLE)
    return PALETTE_ACCESSIBLE[idx]


def get_ecole_color(label: Any) -> str:
    """Retourne la couleur hexadécimale fixe associée à un établissement."""
    if label is None:
        return MUTED_QUEBEC
    s = str(label).strip()
    if s in ECOLE_COLOR_MAP:
        return ECOLE_COLOR_MAP[s]

    match_code = re.search(r"\b(\d{3})\b", s)
    if match_code and match_code.group(1) in _BASE_ECOLE_COLORS:
        return _BASE_ECOLE_COLORS[match_code.group(1)]

    digits = "".join(ch for ch in s if ch.isdigit())
    if len(digits) >= 3:
        code = digits[-3:]
    elif digits:
        code = digits.zfill(3)
    else:
        code = s

    if code in _BASE_ECOLE_COLORS:
        return _BASE_ECOLE_COLORS[code]

    idx = sum(ord(ch) for ch in s) % len(PALETTE_ACCESSIBLE)
    return PALETTE_ACCESSIBLE[idx]


def build_matiere_color_map(labels: Iterable[Any]) -> Dict[str, str]:
    """Construit un dictionnaire {libellé: couleur} cohérent pour une liste de matières/compétences."""
    return {str(lbl): get_matiere_color(lbl) for lbl in labels if lbl is not None}


def build_ecole_color_map(labels: Iterable[Any]) -> Dict[str, str]:
    """Construit un dictionnaire {libellé: couleur} cohérent pour une liste d'écoles."""
    return {str(lbl): get_ecole_color(lbl) for lbl in labels if lbl is not None}

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


