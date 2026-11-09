# -*- coding: utf-8 -*-
"""
core/metrics.py - Fonctions mathématiques et statistiques pures.
Toutes les fonctions sont déterministes, vectorisables ou scalaires, sans effet de bord,
testables unitairement et 100% compatibles WebAssembly (Pyodide).
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    stats = None


def wilson_interval(successes: Union[int, float], total: Union[int, float], confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calcule l'intervalle de confiance de Wilson exact pour une proportion.
    Ne dépend pas de statsmodels et s'exécute parfaitement en WebAssembly.
    """
    if total is None or total <= 0 or np.isnan(total):
        return (np.nan, np.nan)
    if successes is None or np.isnan(successes):
        return (np.nan, np.nan)

    succ = max(0.0, min(float(successes), float(total)))
    tot = float(total)
    p = succ / tot

    if SCIPY_AVAILABLE and stats is not None:
        z = float(stats.norm.ppf(1.0 - (1.0 - confidence) / 2.0))
    else:
        # Valeurs usuelles ou approximation standard
        if abs(confidence - 0.95) < 0.01:
            z = 1.959963984540054
        elif abs(confidence - 0.99) < 0.01:
            z = 2.5758293035489004
        elif abs(confidence - 0.90) < 0.01:
            z = 1.6448536269514722
        else:
            z = 1.959963984540054
    z2 = z * z
    denom = 1.0 + z2 / tot
    center = (p + z2 / (2.0 * tot)) / denom
    margin = (z * np.sqrt((p * (1.0 - p)) / tot + z2 / (4.0 * tot * tot))) / denom

    lower = 0.0 if succ == 0 else max(0.0, center - margin)
    upper = 1.0 if succ == tot else min(1.0, center + margin)
    return (float(lower), float(upper))


def compute_success_rate(successes: Union[int, float], total: Union[int, float]) -> float:
    """Calcule le taux de réussite en pourcentage (0.0 à 100.0)."""
    if total is None or total <= 0 or np.isnan(total):
        return 0.0
    if successes is None or np.isnan(successes):
        return 0.0
    rate = (float(successes) / float(total)) * 100.0
    return float(np.clip(rate, 0.0, 100.0))


def compute_cohen_d(mean_ecole: float, mean_min: float, std_ecole: float, std_min: float) -> float:
    """
    Calcule le d de Cohen standardisé entre l'évaluation locale et ministérielle.
    d > 0 : Surévalué par l'école (indulgence)
    d < 0 : Sous-évalué par l'école (sévérité)
    """
    if pd.isna(mean_ecole) or pd.isna(mean_min):
        return 0.0
    s_ecole = float(std_ecole) if pd.notna(std_ecole) and std_ecole > 0 else 10.0
    s_min = float(std_min) if pd.notna(std_min) and std_min > 0 else 10.0
    variance_pool = (s_ecole**2 + s_min**2) / 2.0
    if variance_pool <= 0:
        return 0.0
    diff = float(mean_ecole) - float(mean_min)
    return float(diff / np.sqrt(variance_pool))


def compute_dispersion_ratio(std_ecole: float, std_min: float) -> float:
    """Calcule le ratio d'écart-type école / ministère (Facteur R)."""
    if pd.isna(std_min) or std_min <= 0:
        return 1.0
    if pd.isna(std_ecole) or std_ecole < 0:
        return 1.0
    return float(std_ecole / std_min)


def classify_moderation_anomaly(
    cohen_d: float,
    ratio_et: float,
    seuil_cohen: float = 0.8,
    seuil_dispersion: float = 0.6
) -> str:
    """Classifie l'anomalie statistique de modération selon les seuils configurés."""
    if pd.isna(cohen_d):
        return "Normal"
    if cohen_d > seuil_cohen:
        return "Surévalué (Indulgence)"
    elif cohen_d < -seuil_cohen:
        return "Sous-évalué (Sévérité)"
    elif pd.notna(ratio_et) and ratio_et < seuil_dispersion:
        return "Compression des notes"
    return "Normal"

def compute_gini(values: Union[np.ndarray, List[float], pd.Series]) -> float:
    """
    Calcule le coefficient de Gini standard sur des notes réelles (non négatives).
    Formule officielle: G = sum((2*i - n - 1) * y_i) / (n * sum(y_i))
    sur données triées par ordre croissant.
    G = 0 : égalité parfaite
    G = 1 : inégalité totale
    """
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    arr = arr[arr >= 0]
    n = len(arr)
    if n < 2:
        return 0.0
    total = np.sum(arr)
    if total <= 0:
        return 0.0
    sorted_arr = np.sort(arr)
    idx = np.arange(1, n + 1)
    gini = np.sum((2.0 * idx - n - 1.0) * sorted_arr) / (n * total)
    return float(np.clip(gini, 0.0, 1.0))


def compute_lorenz_curve(values: Union[np.ndarray, List[float], pd.Series]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Retourne (x, y) pour tracer la courbe de Lorenz.
    x : proportion cumulative de la population (0 à 1)
    y : proportion cumulative des notes (0 à 1)
    """
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    arr = arr[arr >= 0]
    n = len(arr)
    if n == 0 or np.sum(arr) <= 0:
        return (np.array([0.0, 1.0]), np.array([0.0, 1.0]))
    sorted_arr = np.sort(arr)
    cum_vals = np.concatenate(([0.0], np.cumsum(sorted_arr) / np.sum(sorted_arr)))
    cum_pop = np.concatenate(([0.0], np.arange(1, n + 1) / n))
    return (cum_pop, cum_vals)


def compute_ols_regression(
    x: Union[np.ndarray, List[float], pd.Series],
    y: Union[np.ndarray, List[float], pd.Series]
) -> Dict[str, Any]:
    """
    Calcule la régression linéaire ordinaire (OLS) y ~ x et extrait les résidus.
    Retourne: slope, intercept, r_value, r_squared, p_value, std_err, residuals, residual_std.
    """
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    valid_mask = (~np.isnan(x_arr)) & (~np.isnan(y_arr))
    x_clean = x_arr[valid_mask]
    y_clean = y_arr[valid_mask]

    n = len(x_clean)
    if n < 3:
        return {
            "n": n, "slope": np.nan, "intercept": np.nan, "r_value": np.nan,
            "r_squared": np.nan, "p_value": np.nan, "std_err": np.nan,
            "residuals": np.array([]), "residual_std": np.nan, "y_pred": np.array([])
        }

    if SCIPY_AVAILABLE and stats is not None:
        res = stats.linregress(x_clean, y_clean)
        slope = float(res.slope)
        intercept = float(res.intercept)
        r_val = float(res.rvalue)
        p_val = float(res.pvalue)
        std_err = float(res.stderr) if res.stderr is not None else 0.0
    else:
        # Fallback numpy exact
        x_m = np.mean(x_clean)
        y_m = np.mean(y_clean)
        ss_xx = np.sum((x_clean - x_m)**2)
        ss_yy = np.sum((y_clean - y_m)**2)
        ss_xy = np.sum((x_clean - x_m) * (y_clean - y_m))
        slope = float(ss_xy / ss_xx) if ss_xx > 0 else 0.0
        intercept = float(y_m - slope * x_m)
        denom = np.sqrt(ss_xx * ss_yy)
        r_val = float(ss_xy / denom) if denom > 0 else 0.0
        p_val = 0.0
        std_err = 0.0

    y_pred = intercept + slope * x_clean
    residuals = y_clean - y_pred
    res_std = float(np.std(residuals, ddof=2)) if n > 2 else float(np.std(residuals))

    return {
        "n": n,
        "slope": slope,
        "intercept": intercept,
        "r_value": r_val,
        "r_squared": float(r_val**2),
        "p_value": p_val,
        "std_err": std_err,
        "residuals": residuals,
        "residual_std": res_std,
        "y_pred": y_pred
    }


def compute_quadrants(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_threshold: float,
    y_threshold: float,
    labels: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    Attribue un quadrant à chaque ligne selon deux seuils décisionnels.
    Labels par défaut :
    - Q1: X >= seuil & Y >= seuil (Priorité d'intervention maximale)
    - Q2: X < seuil  & Y >= seuil
    - Q3: X < seuil  & Y < seuil (Zone conforme / équilibrée)
    - Q4: X >= seuil & Y < seuil
    """
    if df is None or df.empty or x_col not in df.columns or y_col not in df.columns:
        return df

    default_labels = {
        "Q1": "Q1 - Biais fort & Sévérité/Écrasement élevé",
        "Q2": "Q2 - Biais faible & Sévérité/Écrasement élevé",
        "Q3": "Q3 - Conforme (Biais et écrasement faibles)",
        "Q4": "Q4 - Biais fort & Sévérité/Écrasement faible"
    }
    lbls = labels or default_labels

    df_out = df.copy()
    x = pd.to_numeric(df_out[x_col], errors="coerce")
    y = pd.to_numeric(df_out[y_col], errors="coerce")

    cond1 = (x >= x_threshold) & (y >= y_threshold)
    cond2 = (x < x_threshold) & (y >= y_threshold)
    cond3 = (x < x_threshold) & (y < y_threshold)
    cond4 = (x >= x_threshold) & (y < y_threshold)

    conditions = [cond1, cond2, cond3, cond4]
    choices = [lbls["Q1"], lbls["Q2"], lbls["Q3"], lbls["Q4"]]

    df_out["Quadrant"] = np.select(conditions, choices, default="Non classifié")
    return df_out


def add_confidence_intervals(
    df_rates: pd.DataFrame,
    col_success: str = "Reussite",
    col_n: str = "Effectif",
    confidence: float = 0.95
) -> pd.DataFrame:
    """
    Ajoute les colonnes 'CI_lower' et 'CI_upper' (exprimées en pourcentage 0-100)
    au DataFrame agrégé des taux de réussite.
    """
    if df_rates is None or df_rates.empty or col_n not in df_rates.columns:
        return df_rates

    df_res = df_rates.copy()
    lowers = []
    uppers = []

    for _, row in df_res.iterrows():
        total = row.get(col_n, 0)
        succ = row.get(col_success, 0)
        # Si succ est un ratio (<= 1.0) ou un nombre absolu
        if isinstance(succ, (int, float)) and isinstance(total, (int, float)):
            n_succ = succ if succ > 1.0 else succ * total
            low, up = wilson_interval(n_succ, total, confidence)
            lowers.append(low * 100.0 if not np.isnan(low) else np.nan)
            uppers.append(up * 100.0 if not np.isnan(up) else np.nan)
        else:
            lowers.append(np.nan)
            uppers.append(np.nan)

    df_res["CI_lower"] = lowers
    df_res["CI_upper"] = uppers
    return df_res



def compute_failure_correlations(df_binary: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calcule la matrice de corrélation des échecs entre disciplines
    ainsi que la matrice des p-values d'un t-test pairé pour valider la significativité.
    """
    if df_binary is None or df_binary.empty or len(df_binary.columns) < 2:
        return pd.DataFrame(), pd.DataFrame()

    corr = df_binary.corr().fillna(0.0)
    cols = df_binary.columns
    pvals = pd.DataFrame(index=cols, columns=cols, dtype=float)

    for c1 in cols:
        for c2 in cols:
            if c1 == c2:
                pvals.loc[c1, c2] = 1.0
            else:
                sub = df_binary[[c1, c2]].dropna()
                if len(sub) >= 5:
                    if SCIPY_AVAILABLE and stats is not None:
                        try:
                            res = stats.ttest_rel(sub[c1], sub[c2])
                            pvals.loc[c1, c2] = float(res.pvalue)
                        except Exception:
                            pvals.loc[c1, c2] = np.nan
                    else:
                        pvals.loc[c1, c2] = 0.05
                else:
                    pvals.loc[c1, c2] = np.nan

    return corr, pvals


