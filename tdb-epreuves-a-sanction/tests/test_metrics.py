# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pytest
from core.metrics import (
    wilson_interval,
    compute_success_rate,
    compute_cohen_d,
    compute_dispersion_ratio,
    classify_moderation_anomaly,
    compute_gini,
    compute_lorenz_curve,
    compute_ols_regression,
    compute_quadrants,
    add_confidence_intervals
)


def test_wilson_interval():
    # Cas nominal : 80 succès sur 100
    low, up = wilson_interval(80, 100, 0.95)
    assert 0.70 < low < 0.72
    assert 0.85 < up < 0.88
    assert low < 0.80 < up

    # Cas extrêmes : 0 et 100%
    low_0, up_0 = wilson_interval(0, 50, 0.95)
    assert low_0 == 0.0
    assert up_0 > 0.0

    low_100, up_100 = wilson_interval(50, 50, 0.95)
    assert low_100 < 1.0
    assert up_100 == 1.0

    # Cas d'erreur / effectif nul
    low_nan, up_nan = wilson_interval(0, 0, 0.95)
    assert np.isnan(low_nan) and np.isnan(up_nan)


def test_compute_success_rate():
    assert compute_success_rate(75, 100) == 75.0
    assert compute_success_rate(0, 50) == 0.0
    assert compute_success_rate(50, 50) == 100.0
    assert compute_success_rate(10, 0) == 0.0


def test_compute_cohen_d():
    # Cas école indulgente (+10 points d'avance)
    d_indulgent = compute_cohen_d(75.0, 65.0, 10.0, 10.0)
    assert d_indulgent == pytest.approx(1.0, 0.01)

    # Cas école sévère (-10 points de retard)
    d_severe = compute_cohen_d(65.0, 75.0, 10.0, 10.0)
    assert d_severe == pytest.approx(-1.0, 0.01)

    # Cas égalité
    assert compute_cohen_d(70.0, 70.0, 10.0, 10.0) == 0.0


def test_classify_moderation_anomaly():
    # Surévaluation
    assert classify_moderation_anomaly(0.9, 1.0, seuil_cohen=0.8) == "Surévalué (Indulgence)"
    # Sous-évaluation
    assert classify_moderation_anomaly(-0.85, 1.0, seuil_cohen=0.8) == "Sous-évalué (Sévérité)"
    # Compression de dispersion
    assert classify_moderation_anomaly(0.1, 0.5, seuil_cohen=0.8, seuil_dispersion=0.6) == "Compression des notes"
    # Normal
    assert classify_moderation_anomaly(0.2, 0.9, seuil_cohen=0.8, seuil_dispersion=0.6) == "Normal"


def test_compute_gini_standard():
    # Égalité parfaite -> Gini = 0.0
    assert compute_gini([60.0, 60.0, 60.0, 60.0]) == 0.0

    # Inégalité standard : valeurs croissantes
    g = compute_gini([0.0, 0.0, 0.0, 100.0])
    # Avec n=4, 3 zéros et un 100 : G = ((2*4 - 5)*100) / (4*100) = 3/4 = 0.75
    assert g == pytest.approx(0.75, 0.01)

    # Valeur scalaire unique ou vide -> 0.0
    assert compute_gini([75.0]) == 0.0
    assert compute_gini([]) == 0.0




def test_compute_failure_correlations():
    from core.metrics import compute_failure_correlations
    df_b = pd.DataFrame({
        "Math": [1, 1, 0, 0, 1, 0, 0, 1],
        "Science": [1, 1, 0, 0, 1, 0, 1, 1],
        "Histoire": [0, 0, 1, 1, 0, 0, 0, 0]
    })
    corr, pval = compute_failure_correlations(df_b)
    assert not corr.empty
    assert corr.shape == (3, 3)
    assert corr.loc["Math", "Math"] == pytest.approx(1.0)
    assert corr.loc["Math", "Science"] > 0.5

def test_compute_lorenz_curve():
    pop, vals = compute_lorenz_curve([50.0, 50.0, 50.0])
    assert len(pop) == 4
    assert pop[0] == 0.0 and pop[-1] == 1.0
    assert vals[0] == 0.0 and vals[-1] == 1.0
    # Égalité parfaite : ligne droite
    assert vals[1] == pytest.approx(1/3, 0.01)
    assert vals[2] == pytest.approx(2/3, 0.01)


def test_compute_ols_regression():
    x = np.array([50.0, 60.0, 70.0, 80.0, 90.0])
    y = np.array([55.0, 65.0, 75.0, 85.0, 95.0])
    reg = compute_ols_regression(x, y)
    assert reg["slope"] == pytest.approx(1.0, 0.001)
    assert reg["intercept"] == pytest.approx(5.0, 0.001)
    assert reg["r_squared"] == pytest.approx(1.0, 0.001)
    assert len(reg["residuals"]) == 5
    assert np.allclose(reg["residuals"], 0.0)


def test_compute_quadrants():
    df = pd.DataFrame({
        "Biais": [1.2, 0.2, -0.5, 0.9],
        "Ecrasement": [60.0, 20.0, 10.0, 15.0]
    })
    res = compute_quadrants(df, "Biais", "Ecrasement", x_threshold=0.8, y_threshold=40.0)
    assert "Quadrant" in res.columns
    assert "Q1" in res["Quadrant"].iloc[0]  # Biais >= 0.8 & Ecrasement >= 40
    assert "Q3" in res["Quadrant"].iloc[2]  # Biais < 0.8 & Ecrasement < 40
    assert "Q4" in res["Quadrant"].iloc[3]  # Biais >= 0.8 & Ecrasement < 40


def test_add_confidence_intervals():
    df = pd.DataFrame({
        "Reussite": [0.80, 0.50],
        "Effectif": [100, 20]
    })
    res = add_confidence_intervals(df)
    assert "CI_lower" in res.columns
    assert "CI_upper" in res.columns
    assert res["CI_lower"].iloc[0] < 80.0 < res["CI_upper"].iloc[0]
