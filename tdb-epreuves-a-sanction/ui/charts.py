# -*- coding: utf-8 -*-
"""
ui/charts.py - Moteur de graphiques Plotly accessible, thémé et conforme LAD.
Intègre la communication de l'incertitude (IC Wilson), la palette daltonien-safe,
les formes symboliques redondantes et les boutons d'export CSV/Excel.
"""

import io
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui.theme import (
    PALETTE_ACCESSIBLE,
    ANOMALIE_MAP,
    PLOTLY_LAYOUT_DEFAULTS,
    STATUS_CONFIG,
    PRIMARY_QUEBEC,
    SECONDARY_QUEBEC,
    MUTED_QUEBEC,
    DANGER_QUEBEC,
    SUCCESS_QUEBEC
)


def apply_standard_layout(fig: go.Figure, title: str = "", height: int = 450) -> go.Figure:
    """Applique le thème standard accessible sur une figure Plotly."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color=SECONDARY_QUEBEC, family="system-ui, -apple-system, sans-serif")),
        height=height,
        font=PLOTLY_LAYOUT_DEFAULTS["font"],
        paper_bgcolor=PLOTLY_LAYOUT_DEFAULTS["paper_bgcolor"],
        plot_bgcolor=PLOTLY_LAYOUT_DEFAULTS["plot_bgcolor"],
        margin=PLOTLY_LAYOUT_DEFAULTS["margin"],
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="system-ui, -apple-system, sans-serif")
    )
    fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0", zerolinecolor="#cbd5e1")
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0", zerolinecolor="#cbd5e1")
    return fig


def download_csv_button(df: pd.DataFrame, filename: str, button_text: str = "Télécharger les données (CSV)") -> None:
    """Bouton de téléchargement CSV UTF-8 avec BOM pour compatibilité Excel."""
    if df is None or df.empty:
        return
    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label=button_text,
        data=csv_bytes,
        file_name=filename,
        mime="text/csv"
    )


def download_excel_button(df: pd.DataFrame, filename: str, button_text: str = "Télécharger les données (Excel)") -> None:
    """Bouton de téléchargement Excel via openpyxl avec repli transparent vers CSV."""
    if df is None or df.empty:
        return
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Données")
        st.download_button(
            label=button_text,
            data=buffer.getvalue(),
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception:
        csv_name = filename.replace(".xlsx", ".csv")
        download_csv_button(df, csv_name, button_text=button_text)


def plot_with_export(fig: go.Figure, export_name: str, key_suffix: str = "", use_container_width: bool = True) -> None:
    """Affiche le graphique Plotly en pleine largeur."""
    st.plotly_chart(fig, use_container_width=use_container_width, key=f"fig_{key_suffix}" if key_suffix else None)


def display_plotly_with_info(fig: go.Figure, use_container_width: bool = True) -> None:
    """Affiche un graphique Plotly."""
    st.plotly_chart(fig, use_container_width=use_container_width)

def plot_rates_bar_with_ci(
    df_stats: pd.DataFrame,
    x_col: str = "École",
    y_col: str = "Taux de réussite (%)",
    color_col: str = "Nom_Matiere",
    title: str = "Taux de réussite avec intervalles de confiance à 95%",
    show_ci: bool = True
) -> go.Figure:
    """Diagramme en bandes accessible avec barres d'erreur Wilson IC 95% (LAD P4 & P6)."""
    if df_stats is None or df_stats.empty:
        fig = go.Figure()
        return apply_standard_layout(fig, title="Aucune donnée disponible")

    df_plot = df_stats.copy()
    if "Texte_Echecs" not in df_plot.columns and "Echecs" in df_plot.columns:
        df_plot["Texte_Echecs"] = df_plot["Echecs"].apply(lambda x: f"{int(x)} éch.")

    fig = px.bar(
        df_plot,
        x=x_col,
        y=y_col,
        color=color_col if color_col in df_plot.columns else None,
        barmode="group",
        text="Texte_Echecs" if "Texte_Echecs" in df_plot.columns else None,
        hover_data=[c for c in ["Effectif", "Echecs", "CI_lower", "CI_upper"] if c in df_plot.columns],
        color_discrete_sequence=PALETTE_ACCESSIBLE
    )

    if show_ci and "CI_upper" in df_plot.columns and "CI_lower" in df_plot.columns:
        for trace in fig.data:
            trace_mask = df_plot[color_col] == trace.name if color_col in df_plot.columns else [True] * len(df_plot)
            sub = df_plot[trace_mask]
            trace.error_y = dict(
                type="data",
                symmetric=False,
                array=(sub["CI_upper"] - sub[y_col]).clip(lower=0),
                arrayminus=(sub[y_col] - sub["CI_lower"]).clip(lower=0),
                color="#475569",
                thickness=1.5,
                width=3
            )

    fig.update_traces(textposition="outside")
    fig.update_xaxes(type="category", tickangle=45)
    fig.update_yaxes(range=[0, 115], title_text="Taux de réussite (%)")
    return apply_standard_layout(fig, title=title)


def plot_moderation_scatter(
    df: pd.DataFrame,
    x_col: str = "Moyenne_min",
    y_col: str = "Moyenne_ecole",
    anomaly_col: str = "Type_Anomalie",
    hover_name: str = "Label_Groupe",
    discipline_col: str = "Matiere",
    hide_normal_by_default: bool = True,
    title: str = "Analyse de Modération : Note École vs Note Ministère"
) -> go.Figure:
    """Nuage de points de modération avec ligne d'équilibre (y = x) et symboles/couleurs redondants."""
    if df is None or df.empty:
        return apply_standard_layout(go.Figure(), title="Aucune donnée de modération")

    fig = go.Figure()

    val_min = float(min(df[x_col].min(), df[y_col].min())) if not df.empty else 0.0
    val_max = float(max(df[x_col].max(), df[y_col].max())) if not df.empty else 100.0
    val_min = max(0.0, val_min - 5)
    val_max = min(100.0, val_max + 5)

    fig.add_shape(
        type="line",
        x0=val_min, y0=val_min, x1=val_max, y1=val_max,
        line=dict(color="#475569", dash="dash", width=1.5),
        layer="below"
    )

    groupes_anomalie = df.groupby(anomaly_col, observed=True) if anomaly_col in df.columns else [(None, df)]
    for nom_anomalie, grp in groupes_anomalie:
        cfg = ANOMALIE_MAP.get(nom_anomalie, {"color": MUTED_QUEBEC, "symbol": "circle", "icon": ""})
        is_normal = (nom_anomalie == "Normal")
        visible_param = "legendonly" if (is_normal and hide_normal_by_default) else True

        custom_data = grp[[discipline_col]] if discipline_col in grp.columns else None
        hover_template = (
            "<b>%{text}</b><br>"
            + ("Discipline : %{customdata[0]}<br>" if custom_data is not None else "")
            + "Moyenne Ministère : %{x:.1f}%<br>"
            "Moyenne École : %{y:.1f}%<br>"
            f"Statut : {nom_anomalie}<extra></extra>"
        )

        fig.add_trace(go.Scatter(
            x=grp[x_col],
            y=grp[y_col],
            mode="markers",
            name=nom_anomalie if nom_anomalie else "Données",
            visible=visible_param,
            marker=dict(
                size=9,
                color=cfg["color"],
                symbol=cfg["symbol"],
                line=dict(width=1, color="#1e293b")
            ),
            text=grp[hover_name] if hover_name in grp.columns else None,
            customdata=custom_data,
            hovertemplate=hover_template
        ))

    fig.update_xaxes(title_text="Moyenne de l'Épreuve Ministère (%)", range=[val_min, val_max])
    fig.update_yaxes(title_text="Moyenne de l'École (%)", range=[val_min, val_max])
    return apply_standard_layout(fig, title=title)


def plot_quadrants_matrix(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_threshold: float,
    y_threshold: float,
    label_col: str = "Label",
    title: str = "Matrice 4 Quadrants (Biais Docimologique × Sévérité Pratique)"
) -> go.Figure:
    """Matrice décisionnelle 4 quadrants pour le pilotage de direction (LAD Page 1)."""
    if df is None or df.empty:
        return apply_standard_layout(go.Figure(), title="Aucune donnée pour la matrice")

    fig = go.Figure()
    fig.add_vline(x=x_threshold, line=dict(color=MUTED_QUEBEC, dash="dot", width=1.5))
    fig.add_hline(y=y_threshold, line=dict(color=MUTED_QUEBEC, dash="dot", width=1.5))

    q1_mask = (df[x_col] >= x_threshold) & (df[y_col] >= y_threshold)

    df_q1 = df[q1_mask]
    if not df_q1.empty:
        fig.add_trace(go.Scatter(
            x=df_q1[x_col],
            y=df_q1[y_col],
            mode="markers+text" if len(df_q1) <= 10 else "markers",
            text=df_q1[label_col] if len(df_q1) <= 10 and label_col in df_q1.columns else None,
            textposition="top center",
            name="Priorité d'intervention (Q1)",
            marker=dict(size=11, color=DANGER_QUEBEC, symbol="square", line=dict(width=1, color="#000"))
        ))

    df_other = df[~q1_mask]
    if not df_other.empty:
        fig.add_trace(go.Scatter(
            x=df_other[x_col],
            y=df_other[y_col],
            mode="markers",
            name="Autres groupes",
            marker=dict(size=8, color=PRIMARY_QUEBEC, symbol="circle", opacity=0.7)
        ))

    fig.update_xaxes(title_text=x_col)
    fig.update_yaxes(title_text=y_col)
    return apply_standard_layout(fig, title=title)


def plot_venn2_plotly(set_a: Set[Any], set_b: Set[Any], label_a: str = "A", label_b: str = "B", title: str = "Diagramme de Venn (2 ensembles)") -> go.Figure:
    """Diagramme de Venn à 2 ensembles natif Plotly pour Stlite/WebAssembly."""
    only_a = len(set_a - set_b)
    only_b = len(set_b - set_a)
    both = len(set_a & set_b)

    fig = go.Figure()
    fig.add_shape(type="circle", xref="x", yref="y", x0=-0.8, y0=-0.8, x1=0.4, y1=0.4,
                  fillcolor="rgba(0, 114, 178, 0.4)", line_color="#0072B2", line_width=2)
    fig.add_shape(type="circle", xref="x", yref="y", x0=-0.4, y0=-0.8, x1=0.8, y1=0.4,
                  fillcolor="rgba(213, 94, 0, 0.4)", line_color="#D55E00", line_width=2)

    fig.add_annotation(x=-0.45, y=-0.2, text=f"<b>{only_a}</b>", showarrow=False, font=dict(size=14, color="#1e293b"))
    fig.add_annotation(x=0.0, y=-0.2, text=f"<b>{both}</b>", showarrow=False, font=dict(size=14, color="#1e293b"))
    fig.add_annotation(x=0.45, y=-0.2, text=f"<b>{only_b}</b>", showarrow=False, font=dict(size=14, color="#1e293b"))

    fig.add_annotation(x=-0.5, y=0.55, text=f"<b>{label_a}</b>", showarrow=False, font=dict(size=12, color="#0072B2"))
    fig.add_annotation(x=0.5, y=0.55, text=f"<b>{label_b}</b>", showarrow=False, font=dict(size=12, color="#D55E00"))

    fig.update_xaxes(visible=False, range=[-1.2, 1.2])
    fig.update_yaxes(visible=False, range=[-1.1, 0.8])
    return apply_standard_layout(fig, title=title, height=360)


def plot_venn3_plotly(
    set_a: Set[Any], set_b: Set[Any], set_c: Set[Any],
    label_a: str = "A", label_b: str = "B", label_c: str = "C",
    title: str = "Diagramme de Venn (3 ensembles)"
) -> go.Figure:
    """Diagramme de Venn à 3 ensembles natif Plotly pour Stlite/WebAssembly."""
    only_a = len(set_a - set_b - set_c)
    only_b = len(set_b - set_a - set_c)
    only_c = len(set_c - set_a - set_b)
    ab_only = len((set_a & set_b) - set_c)
    ac_only = len((set_a & set_c) - set_b)
    bc_only = len((set_b & set_c) - set_a)
    all_three = len(set_a & set_b & set_c)

    fig = go.Figure()
    fig.add_shape(type="circle", xref="x", yref="y", x0=-0.95, y0=-0.35, x1=0.25, y1=0.85,
                  fillcolor="rgba(0, 114, 178, 0.35)", line_color="#0072B2", line_width=2)
    fig.add_shape(type="circle", xref="x", yref="y", x0=-0.25, y0=-0.35, x1=0.95, y1=0.85,
                  fillcolor="rgba(213, 94, 0, 0.35)", line_color="#D55E00", line_width=2)
    fig.add_shape(type="circle", xref="x", yref="y", x0=-0.6, y0=-0.95, x1=0.6, y1=0.25,
                  fillcolor="rgba(0, 158, 115, 0.35)", line_color="#009E73", line_width=2)

    fig.add_annotation(x=-0.50, y=0.38, text=f"<b>{only_a}</b>", showarrow=False, font=dict(size=13, color="#1e293b"))
    fig.add_annotation(x=0.50, y=0.38, text=f"<b>{only_b}</b>", showarrow=False, font=dict(size=13, color="#1e293b"))
    fig.add_annotation(x=0.0, y=-0.55, text=f"<b>{only_c}</b>", showarrow=False, font=dict(size=13, color="#1e293b"))
    fig.add_annotation(x=0.0, y=0.45, text=f"<b>{ab_only}</b>", showarrow=False, font=dict(size=12, color="#1e293b"))
    fig.add_annotation(x=-0.32, y=-0.15, text=f"<b>{ac_only}</b>", showarrow=False, font=dict(size=12, color="#1e293b"))
    fig.add_annotation(x=0.32, y=-0.15, text=f"<b>{bc_only}</b>", showarrow=False, font=dict(size=12, color="#1e293b"))
    fig.add_annotation(x=0.0, y=0.08, text=f"<b>{all_three}</b>", showarrow=False, font=dict(size=14, color="#7c3aed"))

    fig.add_annotation(x=-0.55, y=0.95, text=f"<b>{label_a}</b>", showarrow=False, font=dict(size=12, color="#0072B2"))
    fig.add_annotation(x=0.55, y=0.95, text=f"<b>{label_b}</b>", showarrow=False, font=dict(size=12, color="#D55E00"))
    fig.add_annotation(x=0.0, y=-1.05, text=f"<b>{label_c}</b>", showarrow=False, font=dict(size=12, color="#009E73"))

    fig.update_xaxes(visible=False, range=[-1.3, 1.3])
    fig.update_yaxes(visible=False, range=[-1.2, 1.1])
    return apply_standard_layout(fig, title=title, height=420)


def plot_lorenz_curve(
    pop_cum: np.ndarray,
    vals_cum: np.ndarray,
    label: str = "Distribution observée",
    title: str = "Courbe de Lorenz & Égalité Parfaite"
) -> go.Figure:
    """Courbe de Lorenz avec diagonale d'égalité parfaite (LAD Page 5 - Labo)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0.0, 1.0], y=[0.0, 1.0],
        mode="lines",
        name="Égalité parfaite",
        line=dict(color="#64748b", dash="dash", width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=pop_cum, y=vals_cum,
        mode="lines",
        name=label,
        line=dict(color="#0072B2", width=2.5)
    ))
    fig.update_xaxes(title_text="Part cumulée des élèves (0 à 1)", range=[0, 1])
    fig.update_yaxes(title_text="Part cumulée des notes (0 à 1)", range=[0, 1])
    return apply_standard_layout(fig, title=title)


def plot_regression_residuals(
    df: pd.DataFrame,
    x_col: str = "Moyenne_min",
    y_col: str = "Moyenne_ecole",
    slope: float = 0.0,
    intercept: float = 0.0,
    residual_std: float = 0.0,
    k_thresh: float = 1.5,
    label_col: str = "Label",
    discipline_col: Optional[str] = "Discipline",
    title: str = "Comparaison à la Norme du Réseau"
) -> go.Figure:
    """Graphique de régression linéaire avec bandes de tolérance +/- k*sigma et outliers orienté Ministère (X) vs École (Y)."""
    if df is None or df.empty:
        return apply_standard_layout(go.Figure(), title="Aucune donnée pour la régression")

    fig = go.Figure()
    val_min = float(min(df[x_col].min(), df[y_col].min())) if not df.empty else 0.0
    val_max = float(max(df[x_col].max(), df[y_col].max())) if not df.empty else 100.0
    val_min = max(0.0, val_min - 5)
    val_max = min(100.0, val_max + 5)

    x_line = np.linspace(val_min, val_max, 100)
    y_line = intercept + slope * x_line

    # Bandes de tolérance +/- k*sigma
    upper_band = y_line + k_thresh * residual_std
    lower_band = y_line - k_thresh * residual_std

    fig.add_trace(go.Scatter(
        x=np.concatenate([x_line, x_line[::-1]]),
        y=np.concatenate([upper_band, lower_band[::-1]]),
        fill="toself",
        fillcolor="rgba(203, 213, 225, 0.35)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name=f"Zone de tolérance (±{k_thresh:.1f}σ)"
    ))

    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode="lines",
        name="Tendance générale du réseau",
        line=dict(color=SECONDARY_QUEBEC, width=2)
    ))

    # Points : normaux, outliers positifs (indulgence), outliers négatifs (sévérité)
    y_pred_pts = intercept + slope * df[x_col].values
    resids = df[y_col].values - y_pred_pts

    pos_outliers = resids > (k_thresh * residual_std)
    neg_outliers = resids < -(k_thresh * residual_std)
    normal_pts = (~pos_outliers) & (~neg_outliers)

    if np.any(normal_pts):
        sub_n = df[normal_pts]
        custom_n = sub_n[[discipline_col]] if (discipline_col and discipline_col in sub_n.columns) else None
        hover_n = (
            "<b>%{text}</b><br>"
            + ("Discipline : %{customdata[0]}<br>" if custom_n is not None else "")
            + "Moyenne Ministère : %{x:.1f}%<br>"
            "Moyenne École : %{y:.1f}%<br>"
            "Statut : Conforme (dans la tolérance)<extra></extra>"
        )
        fig.add_trace(go.Scatter(
            x=sub_n[x_col], y=sub_n[y_col],
            mode="markers",
            name="Conforme",
            visible="legendonly",
            marker=dict(size=7, color=MUTED_QUEBEC, symbol="circle", opacity=0.7),
            text=sub_n[label_col] if label_col in sub_n.columns else None,
            customdata=custom_n,
            hovertemplate=hover_n
        ))

    if np.any(pos_outliers):
        sub_pos = df[pos_outliers]
        custom_pos = sub_pos[[discipline_col]] if (discipline_col and discipline_col in sub_pos.columns) else None
        hover_pos = (
            "<b>%{text}</b><br>"
            + ("Discipline : %{customdata[0]}<br>" if custom_pos is not None else "")
            + "Moyenne Ministère : %{x:.1f}%<br>"
            "Moyenne École : %{y:.1f}%<br>"
            f"Statut : Indulgence critique (+{k_thresh:.1f}σ)<extra></extra>"
        )
        fig.add_trace(go.Scatter(
            x=sub_pos[x_col], y=sub_pos[y_col],
            mode="markers+text" if len(sub_pos) <= 8 else "markers",
            text=sub_pos[label_col] if len(sub_pos) <= 8 and label_col in sub_pos.columns else None,
            textposition="top center",
            name=f"Indulgence critique (+{k_thresh:.1f}σ)",
            marker=dict(size=10, color=DANGER_QUEBEC, symbol="triangle-up", line=dict(width=1, color="#000")),
            customdata=custom_pos,
            hovertemplate=hover_pos
        ))

    if np.any(neg_outliers):
        sub_neg = df[neg_outliers]
        custom_neg = sub_neg[[discipline_col]] if (discipline_col and discipline_col in sub_neg.columns) else None
        hover_neg = (
            "<b>%{text}</b><br>"
            + ("Discipline : %{customdata[0]}<br>" if custom_neg is not None else "")
            + "Moyenne Ministère : %{x:.1f}%<br>"
            "Moyenne École : %{y:.1f}%<br>"
            f"Statut : Sévérité critique (-{k_thresh:.1f}σ)<extra></extra>"
        )
        fig.add_trace(go.Scatter(
            x=sub_neg[x_col], y=sub_neg[y_col],
            mode="markers+text" if len(sub_neg) <= 8 else "markers",
            text=sub_neg[label_col] if len(sub_neg) <= 8 and label_col in sub_neg.columns else None,
            textposition="bottom center",
            name=f"Sévérité critique (-{k_thresh:.1f}σ)",
            marker=dict(size=10, color=PRIMARY_QUEBEC, symbol="triangle-down", line=dict(width=1, color="#000")),
            customdata=custom_neg,
            hovertemplate=hover_neg
        ))

    fig.update_xaxes(title_text="Moyenne de l'Épreuve Ministère (%)", range=[val_min, val_max])
    fig.update_yaxes(title_text="Moyenne de l'École (%)", range=[val_min, val_max])
    return apply_standard_layout(fig, title=title)

