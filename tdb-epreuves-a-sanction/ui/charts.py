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
    title: str = "Matrice 4 Quadrants (Biais Docimologique × Sévérité Pratique)",
    height: int = 580
) -> go.Figure:
    """Matrice décisionnelle 4 quadrants agrandie avec annotations docimologiques pour le pilotage (LAD Page 2)."""
    if df is None or df.empty:
        return apply_standard_layout(go.Figure(), title="Aucune donnée pour la matrice", height=height)

    fig = go.Figure()
    x_vals = pd.to_numeric(df[x_col], errors="coerce")
    y_vals = pd.to_numeric(df[y_col], errors="coerce")

    x_min = float(min(x_vals.min(), x_threshold - 5.0)) if not x_vals.dropna().empty else -10.0
    x_max = float(max(x_vals.max(), x_threshold + 5.0)) if not x_vals.dropna().empty else 15.0
    y_min = float(min(y_vals.min(), y_threshold - 5.0)) if not y_vals.dropna().empty else 45.0
    y_max = float(max(y_vals.max(), y_threshold + 5.0)) if not y_vals.dropna().empty else 75.0

    pad_x = max(1.5, (x_max - x_min) * 0.08)
    pad_y = max(1.5, (y_max - y_min) * 0.08)
    x_range = [x_min - pad_x, x_max + pad_x]
    y_range = [y_min - pad_y, y_max + pad_y]

    # Zones de fond subtiles pour différencier les 4 quadrants
    fig.add_shape(
        type="rect", x0=x_threshold, y0=y_threshold, x1=x_range[1], y1=y_range[1],
        fillcolor="rgba(239, 68, 68, 0.07)", line_width=0, layer="below"
    )
    fig.add_shape(
        type="rect", x0=x_range[0], y0=y_range[0], x1=x_threshold, y1=y_threshold,
        fillcolor="rgba(16, 185, 129, 0.06)", line_width=0, layer="below"
    )

    fig.add_vline(x=x_threshold, line=dict(color="#334155", dash="dash", width=2))
    fig.add_hline(y=y_threshold, line=dict(color="#334155", dash="dash", width=2))

    q1_mask = (x_vals >= x_threshold) & (y_vals >= y_threshold)
    q2_mask = (x_vals < x_threshold) & (y_vals >= y_threshold)
    q3_mask = (x_vals < x_threshold) & (y_vals < y_threshold)
    q4_mask = (x_vals >= x_threshold) & (y_vals < y_threshold)

    quad_specs = [
        (q1_mask, "Q1 — Priorité d'intervention (Indulgence + Décote)", DANGER_QUEBEC, "square", 12),
        (q2_mask, "Q2 — Vigilance (Faible biais mais seuil exigeant)", "#f59e0b", "diamond", 10),
        (q4_mask, "Q4 — Indulgence locale sans pénalité de seuil", "#0284c7", "triangle-up", 10),
        (q3_mask, "Q3 — Zone conforme & équilibrée", SUCCESS_QUEBEC, "circle", 9),
    ]

    for mask, q_name, q_color, q_sym, q_size in quad_specs:
        sub = df[mask]
        if not sub.empty:
            show_txt = (q_name.startswith("Q1") and len(sub) <= 18)
            hover_cols = [c for c in ["École", "Groupe", "Discipline", "Nb_eleves", "Moyenne_ecole", "Moyenne_min"] if c in sub.columns]
            custom_d = sub[hover_cols].values if hover_cols else None
            hover_tmpl = (
                "<b>%{text}</b><br>"
                f"{x_col} : %{{x:+.1f}} pts<br>"
                f"{y_col} : %{{y:.1f}} %<br>"
                f"Quadrant : {q_name}<extra></extra>"
            )
            fig.add_trace(go.Scatter(
                x=sub[x_col],
                y=sub[y_col],
                mode="markers+text" if show_txt else "markers",
                text=sub[label_col] if label_col in sub.columns else None,
                textposition="top center",
                name=f"{q_name} (n={len(sub)})",
                customdata=custom_d,
                hovertemplate=hover_tmpl,
                marker=dict(size=q_size, color=q_color, symbol=q_sym, opacity=0.88, line=dict(width=1, color="#0f172a"))
            ))

    # Annotations explicatives le long de la ligne de seuil 60 (y_threshold)
    # pour dégager complètement les extrémités supérieure (Q1/Q2) et inférieure (Q3/Q4)
    # Q1 (Haut-Droite) : le long de la ligne 60, juste au-dessus
    fig.add_annotation(
        x=x_range[1] - pad_x * 0.2, y=y_threshold + (pad_y * 0.15),
        text="<b>Q1 : Indulgence & Décote sévère</b><br><span style='font-size:11px'>Priorité d'accompagnement CP/Direction</span>",
        showarrow=False, xanchor="right", yanchor="bottom", align="right",
        bgcolor="rgba(254, 242, 242, 0.92)", bordercolor=DANGER_QUEBEC, borderwidth=1, borderpad=4,
        font=dict(size=11, color="#991b1b")
    )
    # Q2 (Haut-Gauche) : le long de la ligne 60, juste au-dessus
    fig.add_annotation(
        x=x_range[0] + pad_x * 0.2, y=y_threshold + (pad_y * 0.15),
        text="<b>Q2 : Sévérité / Tension au seuil</b><br><span style='font-size:11px'>NEB ≥ 60% requis pour réussir après modération</span>",
        showarrow=False, xanchor="left", yanchor="bottom", align="left",
        bgcolor="rgba(255, 251, 235, 0.92)", bordercolor="#f59e0b", borderwidth=1, borderpad=4,
        font=dict(size=11, color="#92400e")
    )
    # Q3 (Bas-Gauche) : le long de la ligne 60, juste en dessous
    fig.add_annotation(
        x=x_range[0] + pad_x * 0.2, y=y_threshold - (pad_y * 0.15),
        text="<b>Q3 : Zone Conforme & Équilibrée</b><br><span style='font-size:11px'>Alignement école-ministère optimal</span>",
        showarrow=False, xanchor="left", yanchor="top", align="left",
        bgcolor="rgba(236, 253, 245, 0.92)", bordercolor=SUCCESS_QUEBEC, borderwidth=1, borderpad=4,
        font=dict(size=11, color="#065f46")
    )
    # Q4 (Bas-Droite) : le long de la ligne 60, juste en dessous
    fig.add_annotation(
        x=x_range[1] - pad_x * 0.2, y=y_threshold - (pad_y * 0.15),
        text="<b>Q4 : Biais d'indulgence sans choc de seuil</b><br><span style='font-size:11px'>Écart de moyenne compensé par la dispersion</span>",
        showarrow=False, xanchor="right", yanchor="top", align="right",
        bgcolor="rgba(240, 249, 255, 0.92)", bordercolor="#0284c7", borderwidth=1, borderpad=4,
        font=dict(size=11, color="#075985")
    )

    fig.update_xaxes(
        title_text=f"{x_col} — Écart Moyenne École vs Ministère (NEB - NMC, seuil = +{x_threshold:.1f} pts)",
        range=x_range
    )
    fig.update_yaxes(
        title_text=f"{y_col} — Note école requise pour obtenir 60% modéré (seuil = {y_threshold:.1f}%)",
        range=y_range
    )
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
    return apply_standard_layout(fig, title=title, height=height)


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


JANOSZ_COLOR_MAP = {
    "Discret (Frontière)": "#0284c7",
    "Inadapté (Multi-risques)": DANGER_QUEBEC,
    "Désengagé": "#f59e0b",
    "Sous-performant": "#7c3aed",
    "Non à risque": SUCCESS_QUEBEC
}


def plot_janosz_bars(
    df_students: pd.DataFrame,
    include_non_risque: bool = True,
    title: str = "Effectifs par Profil de Risque (Typologie de Janosz / MEQ)",
    height: int = 380
) -> go.Figure:
    """Diagramme en barres affichant le nombre d'élèves et la proportion dans chaque catégorie de Janosz."""
    if df_students is None or df_students.empty or "Profil_Janosz" not in df_students.columns:
        return apply_standard_layout(go.Figure(), title="Aucune donnée de profil Janosz", height=height)

    stu_uniq = df_students.drop_duplicates(subset=["CD_PERMN"]) if "CD_PERMN" in df_students.columns else df_students
    s_prof = stu_uniq["Profil_Janosz"].astype(str)
    if not include_non_risque:
        s_prof = s_prof[s_prof != "Non à risque"]

    order = [
        "Discret (Frontière)",
        "Inadapté (Multi-risques)",
        "Désengagé",
        "Sous-performant"
    ] + (["Non à risque"] if include_non_risque else [])

    counts = s_prof.value_counts().reindex(order, fill_value=0).reset_index()
    counts.columns = ["Profil_Janosz", "Nb_Eleves"]
    total = max(1, int(counts["Nb_Eleves"].sum()))
    counts["Pct"] = (counts["Nb_Eleves"] / total) * 100.0
    counts["Label_Bar"] = counts.apply(lambda r: f"{int(r['Nb_Eleves'])} él. ({r['Pct']:.1f}%)", axis=1)

    fig = px.bar(
        counts,
        x="Profil_Janosz",
        y="Nb_Eleves",
        color="Profil_Janosz",
        text="Label_Bar",
        color_discrete_map=JANOSZ_COLOR_MAP,
        title=title,
        labels={"Profil_Janosz": "Catégorie de Janosz (MEQ)", "Nb_Eleves": "Nombre d'élèves uniques (N)"}
    )
    max_y = max(10, int(counts["Nb_Eleves"].max() * 1.22))
    fig.update_traces(textposition="outside")
    fig.update_yaxes(range=[0, max_y], title_text="Nombre d'élèves (N)")
    fig.update_xaxes(title_text="Catégorie de risque (Janosz / Potvin)")
    fig.update_layout(showlegend=False)
    return apply_standard_layout(fig, title=title, height=height)


def plot_janosz_matrix_2d(
    df: pd.DataFrame,
    title: str = "Matrice 2D de Janosz (Rendement Académique × Assiduité) & Effectifs par Catégorie",
    height: int = 580
) -> go.Figure:
    """
    Représentation matricielle 2x2 pleine largeur de la typologie de Janosz (Rendement académique vs Assiduité)
    affichant le nombre d'élèves (N et %) dans chaque quadrant de risque sans chevauchement de texte.
    """
    if df is None or df.empty or "Profil_Janosz" not in df.columns:
        return apply_standard_layout(go.Figure(), title="Aucune donnée pour la matrice de Janosz", height=height)

    stu_uniq = df.drop_duplicates(subset=["CD_PERMN"]) if "CD_PERMN" in df.columns else df
    s_prof = stu_uniq["Profil_Janosz"].astype(str)
    vc = s_prof.value_counts()

    n_disc = int(vc.get("Discret (Frontière)", 0))
    n_inad = int(vc.get("Inadapté (Multi-risques)", 0))
    n_des = int(vc.get("Désengagé", 0))
    n_sp = int(vc.get("Sous-performant", 0))
    n_non = int(vc.get("Non à risque", 0))
    tot_risque = max(1, n_disc + n_inad + n_des + n_sp)

    fig = go.Figure()

    # 4 quadrants de la Matrice conceptuelle de Janosz :
    boxes = [
        # Haut-Gauche : Inadapté (Multi-risques)
        dict(
            x0=0.02, x1=0.49, y0=0.52, y1=0.98,
            fill="rgba(239, 68, 68, 0.12)", border=DANGER_QUEBEC,
            cx=0.255, cy=0.75,
            title="Inadaptés (Multi-risques)",
            count=n_inad, pct=(n_inad / tot_risque * 100.0) if (n_disc + n_inad + n_des + n_sp) > 0 else 0.0,
            desc="≥ 2 échecs de sanction • Absence ≥ 15% ou incidents disciplinaires",
            prio="Priorité 3 : Plan concerté & art. 222 LIP"
        ),
        # Haut-Droite : Désengagé
        dict(
            x0=0.51, x1=0.98, y0=0.52, y1=0.98,
            fill="rgba(245, 158, 11, 0.12)", border="#f59e0b",
            cx=0.745, cy=0.75,
            title="Désengagés",
            count=n_des, pct=(n_des / tot_risque * 100.0) if (n_disc + n_inad + n_des + n_sp) > 0 else 0.0,
            desc="Réussite académique (≥ 60%) • Absentéisme chronique (≥ 15%)",
            prio="Priorité 4 : Suivi relationnel Check & Connect"
        ),
        # Bas-Gauche : Sous-performant
        dict(
            x0=0.02, x1=0.49, y0=0.02, y1=0.48,
            fill="rgba(124, 58, 237, 0.10)", border="#7c3aed",
            cx=0.255, cy=0.25,
            title="Sous-performants",
            count=n_sp, pct=(n_sp / tot_risque * 100.0) if (n_disc + n_inad + n_des + n_sp) > 0 else 0.0,
            desc="Échecs lourds (< 50%) ou PI/EHDAA actif • Assiduité régulière (< 12%)",
            prio="Priorité 2 : Cours d'été intensif"
        ),
        # Bas-Droite : Discret (Frontière)
        dict(
            x0=0.51, x1=0.98, y0=0.02, y1=0.48,
            fill="rgba(2, 132, 199, 0.10)", border="#0284c7",
            cx=0.745, cy=0.25,
            title="Discrets (Frontière)",
            count=n_disc, pct=(n_disc / tot_risque * 100.0) if (n_disc + n_inad + n_des + n_sp) > 0 else 0.0,
            desc="1 échec ou note 55-59% • Assiduité régulière (< 10%) • Aucun incident",
            prio="Priorité 1 : Reprise seule / Tutorat court"
        )
    ]

    for b in boxes:
        fig.add_shape(
            type="rect", x0=b["x0"], x1=b["x1"], y0=b["y0"], y1=b["y1"],
            fillcolor=b["fill"], line=dict(color=b["border"], width=2)
        )
        # Annotation aérée avec espacement vertical strict pour empêcher tout chevauchement
        fig.add_annotation(
            x=b["cx"], y=b["cy"],
            text=(
                f"<span style='font-size:15px; font-weight:700; color:#0f172a;'>{b['title']}</span><br><br>"
                f"<span style='font-size:24px; font-weight:800; color:{b['border']};'>{b['count']:,} élève(s)</span><br>"
                f"<span style='font-size:12.5px; font-weight:600; color:#475569;'>({b['pct']:.1f}% des profils à risque)</span><br><br>"
                f"<span style='font-size:11.5px; color:#334155;'>{b['desc']}</span><br><br>"
                f"<span style='font-size:11.5px; font-weight:700; color:{b['border']}; background-color:#ffffff; border:1px solid {b['border']}; border-radius:4px; padding:2px 8px;'>{b['prio']}</span>"
            ),
            showarrow=False, align="center"
        )

    fig.update_xaxes(
        range=[0, 1],
        tickvals=[0.255, 0.745],
        ticktext=[
            "<b>Difficultés académiques marquées</b><br>Multi-échecs aux matières à sanction",
            "<b>Rendement frontière ou suffisant</b><br>Zone frontière (55-59%) ou Réussite (≥ 60%)"
        ],
        tickangle=0,
        showgrid=False, zeroline=False,
        title_text="<b>Axe Académique</b> (Résultats aux matières à sanction) — <i>Élèves non à risque hors matrice : " + f"{n_non:,}</i>",
        title_font=dict(size=13, color="#1e293b")
    )
    fig.update_yaxes(
        range=[0, 1],
        tickvals=[0.25, 0.75],
        ticktext=[
            "<b>Assiduité régulière</b><br>Engagement maintenu",
            "<b>Absentéisme / Rupture</b><br>Désengagement (≥ 15%) ou Inadaptation"
        ],
        tickangle=0,
        showgrid=False, zeroline=False,
        title_text="<b>Axe Comportemental & Assiduité</b>",
        title_font=dict(size=13, color="#1e293b")
    )
    fig.update_layout(
        margin=dict(l=40, r=40, t=50, b=60),
        plot_bgcolor="#ffffff"
    )
    return apply_standard_layout(fig, title=title, height=height)


