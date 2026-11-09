# -*- coding: utf-8 -*-
"""
boot.py - Module de préchauffage (Warmup) Stlite / WebAssembly
Initialise et précharge en mémoire de manière stable les bibliothèques scientifiques
lourdes (numpy, pandas, scipy, plotly) via @st.cache_resource
pour éliminer les latences de chargement dynamique et prévenir les fuites mémoires en WASM.
"""

import streamlit as st


@st.cache_resource(show_spinner=False)
def warmup_runtime() -> bool:
    """
    Précharge les modules lourds dans le runtime Pyodide une seule fois par session globale.
    """
    try:
        import numpy as np
        import pandas as pd
        import scipy
        import scipy.stats
        import plotly.express as px
        import plotly.graph_objects as go
        return True
    except Exception:
        return False


# Exécution au chargement du module
_warmup_ok = warmup_runtime()
