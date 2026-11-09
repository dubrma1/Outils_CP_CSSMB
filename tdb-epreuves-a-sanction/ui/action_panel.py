# -*- coding: utf-8 -*-
"""
ui/action_panel.py - Panneau d'action décisionnelle dynamique LAD.
Applique le principe P2 (Donnée -> Insight -> Action) en remplaçant les blocs d'information
génériques par un panneau structuré dont le constat est calculé à partir des données filtrées.
"""

from typing import List, Optional
import streamlit as st


def render_action_panel(
    question: str,
    constat_dynamique: str,
    pistes: List[str],
    context_tag: Optional[str] = None
) -> None:
    """
    Affiche un panneau décisionnel conforme LAD :
    - Question décisionnelle explicite (Pourquoi regarde-t-on ce graphique ?)
    - Constat calculé dynamiquement sur la sélection active
    - Pistes d'action concrètes et bienveillantes (diagnostic collectif non stigmatisant)
    """
    tag_html = f"<span style='background:#e2e8f0; color:#334155; font-size:0.75rem; padding:2px 8px; border-radius:12px; margin-left:8px; font-weight:600;'>{context_tag}</span>" if context_tag else ""

    pistes_html = "".join([f"<li style='margin-bottom: 6px; color: #1e293b;'>{p}</li>" for p in pistes])

    panel_html = (
        "<div style='background: #ffffff; border: 1px solid #cbd5e1; border-left: 5px solid #1472BF; "
        "border-radius: 8px; padding: 16px 20px; margin: 16px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.03);'>"
        "<div style='display: flex; align-items: center; margin-bottom: 8px;'>"
        "<span style='font-size: 0.9rem; font-weight: 700; color: #095797; text-transform: uppercase; letter-spacing: 0.5px;'>Question décisionnelle</span>"
        f"{tag_html}"
        "</div>"
        f"<div style='font-size: 1.05rem; font-weight: 600; color: #0f172a; margin-bottom: 12px; line-height: 1.4;'>{question}</div>"
        "<div style='background-color: #f1f5f9; border-left: 3px solid #1472BF; padding: 10px 14px; border-radius: 4px; margin-bottom: 12px; font-size: 0.92rem; color: #0f172a; line-height: 1.45;'>"
        f"<strong>Constat diagnostique :</strong> {constat_dynamique}"
        "</div>"
        "<div style='font-size: 0.88rem; font-weight: 700; color: #475569; margin-bottom: 6px; text-transform: uppercase;'>Pistes d'accompagnement et leviers d'action :</div>"
        f"<ul style='margin-left: 20px; padding-left: 0; font-size: 0.92rem; line-height: 1.45;'>{pistes_html}</ul>"
        "</div>"
    )
    if hasattr(st, "html"):
        st.html(panel_html)
    else:
        st.markdown(panel_html, unsafe_allow_html=True)
