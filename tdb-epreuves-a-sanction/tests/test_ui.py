# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pytest
from ui.theme import STATUS_CONFIG, ANOMALIE_MAP, QUEBEC_CSS, PRIMARY_QUEBEC, SECONDARY_QUEBEC, ACCENT_QUEBEC, DANGER_QUEBEC, SUCCESS_QUEBEC, inject_quebec_theme
from ui.charts import (
    plot_rates_bar_with_ci,
    plot_moderation_scatter,
    plot_quadrants_matrix,
    plot_venn2_plotly,
    plot_venn3_plotly,
    plot_lorenz_curve,
    plot_regression_residuals
)


def test_theme_wcag_and_symbols():
    # Vérifie que chaque statut possède une icône, un symbole et une couleur
    for status, conf in STATUS_CONFIG.items():
        assert "icon" in conf
        assert "symbol" in conf
        assert "color" in conf
        assert "label" in conf

    # Vérifie les anomalies de modération
    for anomalie, conf in ANOMALIE_MAP.items():
        assert "symbol" in conf
        assert "color" in conf
        assert "icon" in conf


def test_charts_creation_smoke():
    # Bar chart avec CI
    df_rates = pd.DataFrame({
        "École": ["041", "245"],
        "Taux de réussite (%)": [85.0, 72.0],
        "Nom_Matiere": ["Français 5", "Math CST"],
        "CI_lower": [75.0, 60.0],
        "CI_upper": [92.0, 81.0],
        "Effectif": [50, 40],
        "Echecs": [7, 11]
    })
    fig_bar = plot_rates_bar_with_ci(df_rates)
    assert fig_bar is not None
    assert len(fig_bar.data) > 0

    # Scatter de modération
    df_mod = pd.DataFrame({
        "Moyenne_min": [65.0, 75.0],
        "Moyenne_ecole": [70.0, 68.0],
        "Type_Anomalie": ["Surévalué (Indulgence)", "Sous-évalué (Sévérité)"],
        "Label_Groupe": ["École 041 - Gr. 01", "École 245 - Gr. 02"]
    })
    fig_scatter = plot_moderation_scatter(df_mod)
    assert fig_scatter is not None
    assert len(fig_scatter.data) == 2  # Deux anomalies distinctes

    # Matrice quadrants
    df_quad = pd.DataFrame({
        "Biais": [1.2, -0.4],
        "Ecrasement": [55.0, 15.0],
        "Label": ["Gr1", "Gr2"]
    })
    fig_quad = plot_quadrants_matrix(df_quad, "Biais", "Ecrasement", 0.8, 40.0)
    assert fig_quad is not None

    # Diagrammes de Venn
    fig_v2 = plot_venn2_plotly({1, 2, 3}, {2, 3, 4})
    assert fig_v2 is not None

    fig_v3 = plot_venn3_plotly({1, 2}, {2, 3}, {2, 4})
    assert fig_v3 is not None


def test_quebec_theme_variables_and_no_emojis():
    assert PRIMARY_QUEBEC == "#1472BF"
    assert SECONDARY_QUEBEC == "#095797"
    assert ACCENT_QUEBEC == "#f59e0b"
    assert DANGER_QUEBEC == "#ef4444"
    assert SUCCESS_QUEBEC == "#10b981"
    assert "--primary: #1472BF" in QUEBEC_CSS
    assert "--secondary: #095797" in QUEBEC_CSS
    assert "--accent: #f59e0b" in QUEBEC_CSS
    for status, conf in STATUS_CONFIG.items():
        assert conf["icon"] == ""
    for anomalie, conf in ANOMALIE_MAP.items():
        assert conf["icon"] == ""
    inject_quebec_theme()


def test_plot_regression_residuals_quebec_spec():
    # Test docimologique Graphique B (X = Ministère, Y = École)
    df = pd.DataFrame({
        "Moyenne_min": [60.0, 70.0, 80.0],
        # y = 1.0 * x + 0.
        # With std = 2.0:
        # For x=60, expected=60: actual=70 (+10 > +3.0) -> Indulgence critique
        # For x=70, expected=70: actual=70 (diff=0) -> Conforme
        # For x=80, expected=80: actual=70 (-10 < -3.0) -> Sévérité critique
        "Moyenne_ecole": [70.0, 70.0, 70.0],
        "Label_Groupe": ["Gr_Indulgent", "Gr_Conforme", "Gr_Severe"],
        "Discipline": ["Français", "Math", "Sciences"]
    })

    fig = plot_regression_residuals(
        df,
        x_col="Moyenne_min",
        y_col="Moyenne_ecole",
        slope=1.0,
        intercept=0.0,
        residual_std=2.0,
        k_thresh=1.5,
        label_col="Label_Groupe",
        discipline_col="Discipline",
        title="Test B"
    )

    assert fig is not None
    assert fig.layout.xaxis.title.text == "Moyenne de l'Épreuve Ministère (%)"
    assert fig.layout.yaxis.title.text == "Moyenne de l'École (%)"

    trace_names = [t.name for t in fig.data]
    assert "Zone de tolérance (±1.5σ)" in trace_names
    assert "Tendance générale du réseau" in trace_names
    assert "Indulgence critique (+1.5σ)" in trace_names
    assert "Sévérité critique (-1.5σ)" in trace_names
    assert "Conforme" in trace_names

    conforme_trace = next(t for t in fig.data if t.name == "Conforme")
    assert conforme_trace.visible == "legendonly"


def test_sidebar_pages_hierarchy_and_naming():
    from pathlib import Path
    import streamlit.source_util as su

    expected_labels = [
        "1. Macro : Pilotage Systémique & Diplomation",
        "2. Méso : Équité & Modération des Notes",
        "3. Micro : Diagnostic des Épreuves & Classes",
        "4. Prescription : Triage GPS & Diplomation"
    ]

    pages_dir = Path(__file__).resolve().parent.parent / "pages"
    py_files = sorted([f for f in pages_dir.glob("*.py") if f.name != "__init__.py"])
    assert len(py_files) == 4

    resolved_labels = []
    for f in py_files:
        _, name = su.page_icon_and_name(f)
        resolved_labels.append(name.replace("_", " "))

    assert resolved_labels == expected_labels



