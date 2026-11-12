# -*- coding: utf-8 -*-
"""
ui_components.py - Module de compatibilité ascendante pour les fonctions visuelles historiques.
Délègue les tracés et composants vers le package modulaire ui (charts, kpi_cards, theme).
"""

import streamlit as st
from ui.charts import (
    download_csv_button, download_excel_button,
    display_plotly_with_info, plot_venn2_plotly, plot_venn3_plotly,
    plot_with_export
)
from ui.kpi_cards import render_kpi_card


def export_to_pdf_button():
    """Fonction neutralisée pour l'environnement client WebAssembly."""
    pass


def display_kpi(col, title, value, help_text=None):
    """Affiche un KPI dans une colonne Streamlit."""
    col.metric(label=title, value=value, help=help_text)


def apply_adaptive_bar_layout(fig, nb_series=1):
    """Ajuste les espacements et marges d'un diagramme en barres."""
    fig.update_layout(bargap=0.25, bargroupgap=0.1)
    return fig


def display_pyplot_with_info(fig, clear_figure=True, **kwargs):
    """Fonction neutralisée (Plotly est le seul moteur graphique WebAssembly)."""
    pass
