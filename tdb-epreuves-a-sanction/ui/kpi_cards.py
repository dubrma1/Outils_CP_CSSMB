# -*- coding: utf-8 -*-
"""
ui/kpi_cards.py - Cartes KPI conformes aux principes LAD.
Affiche la valeur clé, le statut visuel (icône + couleur + libellé), l'effectif N,
l'intervalle de confiance (Wilson IC 95%) et une mise en garde automatique si N < 15.
"""

from typing import Any, Optional, Tuple, Union
import streamlit as st
from ui.theme import STATUS_CONFIG
from core.privacy import get_sample_size_warning


def render_kpi_card(
    title: str,
    value: Union[str, float, int],
    status: str = "neutral",
    n: Optional[int] = None,
    ci: Optional[Tuple[float, float]] = None,
    subtitle: Optional[str] = None,
    help_text: Optional[str] = None,
    target: Optional[str] = None
) -> None:
    """
    Rend une carte KPI enrichie accessible :
    - Statut tricolore avec icône distincte (P3/P6)
    - Affichage explicite de l'effectif N (P4)
    - Intervalle de confiance Wilson si disponible (P4)
    - Avertissement automatique de volatilité si N < 15 (P4)
    """
    cfg = STATUS_CONFIG.get(status, STATUS_CONFIG["neutral"])
    color = cfg["color"]
    bg = cfg["bg"]
    border = cfg["border"]
    icon = cfg["icon"]
    status_label = cfg["label"]

    val_str = f"{value:.1f}%" if isinstance(value, float) and "%" not in str(value) else str(value)

    ci_html = ""
    if ci is not None and not (ci[0] is None or (isinstance(ci[0], float) and np_isnan(ci[0]))):
        low, up = ci
        ci_html = f"<div style='font-size: 0.8rem; color: #475569; margin-top: 2px;'>IC 95% : [{low:.1f}% – {up:.1f}%]</div>"

    n_html = ""
    if n is not None and n > 0:
        volatil_txt = " <span style='font-size:0.75rem; color:#b45309; font-weight:normal;'>(N < 15 : volatilité accrue)</span>" if n < 15 else ""
        n_html = f"<div style='font-size: 0.82rem; font-weight: 600; color: #334155;'>Effectif (N) : {n}{volatil_txt}</div>"

    sub_html = f"<div style='font-size: 0.85rem; color: #64748b; margin-top: 4px;'>{subtitle}</div>" if subtitle else ""
    target_html = f"<div style='font-size: 0.8rem; color: {color}; font-weight: 600; margin-top: 2px;'>{target}</div>" if target else ""

    card_html = (
        f"<div style='background-color: {bg}; border-left: 5px solid {border}; border-radius: 8px; "
        "padding: 12px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 12px; height: 100%; "
        "display: flex; flex-direction: column; justify-content: space-between;'>"
        "<div>"
        "<div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'>"
        f"<span style='font-size: 0.85rem; font-weight: 600; color: #1e293b; text-transform: uppercase; letter-spacing: 0.5px;'>{title}</span>"
        f"<span style='font-size: 0.75rem; font-weight: 600; color: {color}; background: white; padding: 2px 8px; border-radius: 12px; border: 1px solid {border};'>{status_label}</span>"
        "</div>"
        f"<div style='font-size: 1.85rem; font-weight: 700; color: #0f172a; line-height: 1.2;'>{val_str}</div>"
        f"{sub_html}"
        f"{target_html}"
        "</div>"
        "<div style='margin-top: 10px; padding-top: 6px; border-top: 1px dashed rgba(0,0,0,0.1);'>"
        f"{n_html}"
        f"{ci_html}"
        "</div>"
        "</div>"
    )
    if hasattr(st, "html"):
        st.html(card_html)
    else:
        st.markdown(card_html, unsafe_allow_html=True)
    if help_text:
        st.caption(f"{help_text}")


def np_isnan(val: Any) -> bool:
    try:
        import numpy as np
        return bool(np.isnan(val))
    except Exception:
        return False
