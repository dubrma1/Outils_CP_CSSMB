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


JANOSZ_CATEGORIES: List[str] = [
    "Discret (Frontière)",
    "Inadapté (Multi-risques)",
    "Désengagé",
    "Sous-performant",
    "Non à risque"
]


def assigner_typologie_janosz(df: pd.DataFrame) -> pd.DataFrame:
    """
    Catégorise de manière déterministe et vectorisée chaque élève selon la typologie
    de risque de décrochage (Janosz / Potvin / MEQ) :
      - 'Discret (Frontière)' : 1 échec en sanction ou note 55-59%, PCT_ABSENCE < 10%,
        SIGNALEMENT_COMP == 0, pas de code comportement.
      - 'Inadapté (Multi-risques)' : >= 2 échecs sanction, PCT_ABSENCE >= 15% ou
        SIGNALEMENT_COMP > 0, retard scolaire (âge >= 17 en 4e ou >= 18 en 5e).
      - 'Désengagé' : PCT_ABSENCE >= 15%, mais Réussite globale validée (notes >= 60%).
      - 'Sous-performant' : Notes < 50% ou FLAG_PI == 1, mais PCT_ABSENCE < 12%
        et SIGNALEMENT_COMP == 0.
      - 'Non à risque' : Réussite générale et assiduité régulière.

    Opère sans duplication mémoire inutile et retourne le DataFrame muni de la colonne
    catégorielle 'Profil_Janosz'.
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return df

    from core.schema import CODE_TO_MATIERE_COURT, get_course_level

    has_permn = "CD_PERMN" in df.columns
    has_reslt = "RESLT_FINAL" in df.columns

    if has_permn and has_reslt:
        notes_num = pd.to_numeric(df["RESLT_FINAL"], errors="coerce")

        # Cibler les cours à sanction / notes globales s'ils sont identifiables, sinon toutes les lignes avec note
        if "CD_COURS_str" in df.columns:
            c_str = df["CD_COURS_str"].astype(str).str.strip()
        elif "CD_COURS" in df.columns:
            c_str = df["CD_COURS"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        else:
            c_str = None

        if c_str is not None:
            is_sanction = c_str.isin(CODE_TO_MATIERE_COURT.keys())
            if not is_sanction.any() and "Type_Cours" in df.columns:
                is_sanction = (df["Type_Cours"] == "Note globale")
            if not is_sanction.any():
                is_sanction = notes_num.notna()
        else:
            is_sanction = notes_num.notna()

        # Agrégation vectorisée par CD_PERMN sur les cours pertinents
        df_tmp = pd.DataFrame({
            "CD_PERMN": df["CD_PERMN"],
            "note": np.where(is_sanction, notes_num, np.nan),
            "is_echec": np.where(is_sanction & (notes_num < 60.0), 1, 0),
            "is_55_59": np.where(is_sanction & (notes_num >= 55.0) & (notes_num < 60.0), 1, 0),
            "is_lt_50": np.where(is_sanction & (notes_num < 50.0), 1, 0)
        }, index=df.index)

        grp = df_tmp.groupby("CD_PERMN", observed=True)
        nb_echecs = df["CD_PERMN"].map(grp["is_echec"].sum()).fillna(0).astype("int16")
        min_note = df["CD_PERMN"].map(grp["note"].min()).fillna(notes_num).fillna(65.0).astype("float32")
        has_55_59 = df["CD_PERMN"].map(grp["is_55_59"].max()).fillna(0) > 0
        has_lt_50 = df["CD_PERMN"].map(grp["is_lt_50"].max()).fillna(0) > 0

        if c_str is not None:
            lvl_series = c_str.map(get_course_level).fillna(4)
            df_lvl = pd.DataFrame({"CD_PERMN": df["CD_PERMN"], "lvl": lvl_series}, index=df.index)
            niv_sec = df["CD_PERMN"].map(df_lvl.groupby("CD_PERMN", observed=True)["lvl"].max()).fillna(4).astype("int16")
        else:
            niv_sec = pd.Series(4, index=df.index, dtype="int16")
    elif has_reslt:
        notes_num = pd.to_numeric(df["RESLT_FINAL"], errors="coerce").fillna(65.0)
        nb_echecs = (notes_num < 60.0).astype("int16")
        min_note = notes_num.astype("float32")
        has_55_59 = (notes_num >= 55.0) & (notes_num < 60.0)
        has_lt_50 = notes_num < 50.0
        niv_sec = pd.Series(4, index=df.index, dtype="int16")
    else:
        age_tmp = pd.to_numeric(df["AGE_30SEPT"], errors="coerce").fillna(15) if "AGE_30SEPT" in df.columns else pd.Series(15, index=df.index)
        cred_tmp = pd.to_numeric(df["NB_CREDITS_CUMUL"], errors="coerce").fillna(32) if "NB_CREDITS_CUMUL" in df.columns else pd.Series(32, index=df.index)
        sig_tmp = pd.to_numeric(df["SIGNALEMENT_COMP"], errors="coerce").fillna(0) if "SIGNALEMENT_COMP" in df.columns else pd.Series(0, index=df.index)
        niv_sec = pd.Series(np.where((age_tmp >= 16) & (cred_tmp >= 36), 5, 4), index=df.index, dtype="int16")
        # Estimation du nombre d'échecs via le déficit de crédits ou les indicateurs de risque lorsque RESLT_FINAL est absent
        deficit_4e = (niv_sec == 4) & (cred_tmp < 30)
        deficit_5e = (niv_sec >= 5) & (cred_tmp < 52)
        multi_def = ((niv_sec == 4) & (cred_tmp < 26)) | ((niv_sec >= 5) & (cred_tmp < 46)) | (sig_tmp > 0) | (age_tmp >= 17)
        nb_echecs = pd.Series(np.where(multi_def, 2, np.where(deficit_4e | deficit_5e, 1, 0)), index=df.index, dtype="int16")
        min_note = pd.Series(np.where(nb_echecs >= 2, 48.0, np.where(nb_echecs == 1, 56.0, 72.0)), index=df.index, dtype="float32")
        has_55_59 = (nb_echecs == 1)
        has_lt_50 = pd.Series(False, index=df.index)

    pct_abs = pd.to_numeric(df["PCT_ABSENCE"], errors="coerce").fillna(0.0) if "PCT_ABSENCE" in df.columns else pd.Series(0.0, index=df.index)
    sig_comp = pd.to_numeric(df["SIGNALEMENT_COMP"], errors="coerce").fillna(0).astype("int16") if "SIGNALEMENT_COMP" in df.columns else pd.Series(0, index=df.index, dtype="int16")
    flag_pi = pd.to_numeric(df["FLAG_PI"], errors="coerce").fillna(0).astype("int32") if "FLAG_PI" in df.columns else pd.Series(0, index=df.index, dtype="int32")
    age_30s = pd.to_numeric(df["AGE_30SEPT"], errors="coerce").fillna(15).astype("int16") if "AGE_30SEPT" in df.columns else pd.Series(15, index=df.index, dtype="int16")

    if "CD_EHDAA" in df.columns:
        ehdaa_str = df["CD_EHDAA"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        ehdaa_str = ehdaa_str.replace(["nan", "None", "Ordinaire"], "")
    else:
        ehdaa_str = pd.Series("", index=df.index, dtype="object")

    has_code_comp = ehdaa_str.isin(["12", "13", "14"])
    retard_scolaire = ((niv_sec <= 4) & (age_30s >= 17)) | ((niv_sec >= 5) & (age_30s >= 18))
    reussite_globale = (nb_echecs == 0) & (min_note >= 60.0)

    # 1. Désengagé : PCT_ABSENCE >= 15%, mais Réussite globale validée (notes >= 60%), sans code comportement
    cond_desengage = (pct_abs >= 15.0) & reussite_globale & (~has_code_comp)

    # 2. Inadapté (Multi-risques) : >= 2 échecs sanction, PCT_ABSENCE >= 15% ou SIGNALEMENT_COMP > 0,
    #    retard scolaire (âge >= 17 en 4e ou >= 18 en 5e), ou multi-échecs avec facteurs comportementaux/absences
    cond_inadapte = (
        (nb_echecs >= 2) & ((pct_abs >= 15.0) | (sig_comp > 0) | retard_scolaire | has_code_comp)
    ) | (
        (nb_echecs >= 1) & ((pct_abs >= 15.0) | (sig_comp > 0) | has_code_comp)
    ) | (
        (nb_echecs >= 2) & (pct_abs >= 10.0)
    )

    # 3. Sous-performant : Notes < 50% ou FLAG_PI == 1 (avec échec ou sans note), mais PCT_ABSENCE < 12% et SIGNALEMENT_COMP == 0
    cond_sous_perf = (
        (has_lt_50 | ((flag_pi == 1) & (~reussite_globale | ~has_reslt)) | ((ehdaa_str != "") & (~has_code_comp) & (~reussite_globale)))
        & (pct_abs < 12.0)
        & (sig_comp == 0)
        & (~has_code_comp)
    )

    # 4. Discret (Frontière) : 1 échec en sanction ou note 55-59%, PCT_ABSENCE < 10%, SIGNALEMENT_COMP == 0, pas de code comportement
    cond_discret = (
        ((nb_echecs == 1) | has_55_59)
        & (pct_abs < 10.0)
        & (sig_comp == 0)
        & (~has_code_comp)
    )

    # Filets de sécurité pour éviter qu'un élève en échec ne tombe dans 'Non à risque'
    cond_inadapte_fallback = (nb_echecs >= 2) & (~cond_sous_perf) & (~cond_discret)
    cond_discret_fallback = (nb_echecs == 1) & (~cond_inadapte) & (~cond_sous_perf)

    conditions = [
        cond_desengage,
        cond_inadapte | cond_inadapte_fallback,
        cond_sous_perf,
        cond_discret | cond_discret_fallback
    ]
    choices = [
        "Désengagé",
        "Inadapté (Multi-risques)",
        "Sous-performant",
        "Discret (Frontière)"
    ]

    profil = np.select(conditions, choices, default="Non à risque")
    df["Profil_Janosz"] = pd.Categorical(profil, categories=JANOSZ_CATEGORIES)
    return df


# =============================================================================
# 7. DIAGNOSTIC MICRO DES ÉCARTS SIGNIFICATIFS ENTRE COMPÉTENCES PAR GROUPE-ÉCOLE
# =============================================================================
COMPETENCY_SUFFIX_MAP: Dict[str, Tuple[str, str, str]] = {
    # Mathématiques : Résoudre (30%) vs Raisonner (70%)
    "63410": ("Mathématiques", "Math CST", "Résoudre"),
    "63420": ("Mathématiques", "Math CST", "Raisonner"),
    "63414": ("Mathématiques", "Math CST", "Global"),
    "063410": ("Mathématiques", "Math CST", "Résoudre"),
    "063420": ("Mathématiques", "Math CST", "Raisonner"),
    "063414": ("Mathématiques", "Math CST", "Global"),
    "65410": ("Mathématiques", "Math SN", "Résoudre"),
    "65420": ("Mathématiques", "Math SN", "Raisonner"),
    "65426": ("Mathématiques", "Math SN", "Global"),
    "065410": ("Mathématiques", "Math SN", "Résoudre"),
    "065420": ("Mathématiques", "Math SN", "Raisonner"),
    "065426": ("Mathématiques", "Math SN", "Global"),
    "64410": ("Mathématiques", "Math TS", "Résoudre"),
    "64420": ("Mathématiques", "Math TS", "Raisonner"),
    "64426": ("Mathématiques", "Math TS", "Global"),
    "064410": ("Mathématiques", "Math TS", "Résoudre"),
    "064420": ("Mathématiques", "Math TS", "Raisonner"),
    "064426": ("Mathématiques", "Math TS", "Global"),
    # Sciences : Pratique (40%) vs Théorie (60%)
    "55420": ("Sciences", "Science ST", "Pratique"),
    "55410": ("Sciences", "Science ST", "Théorie"),
    "55444": ("Sciences", "Science ST", "Global"),
    "055420": ("Sciences", "Science ST", "Pratique"),
    "055410": ("Sciences", "Science ST", "Théorie"),
    "055444": ("Sciences", "Science ST", "Global"),
    "57420": ("Sciences", "Science ATS", "Pratique"),
    "57410": ("Sciences", "Science ATS", "Théorie"),
    "57406": ("Sciences", "Science ATS", "Global"),
    "57416": ("Sciences", "Science ATS", "Global"),
    "057420": ("Sciences", "Science ATS", "Pratique"),
    "057410": ("Sciences", "Science ATS", "Théorie"),
    "057406": ("Sciences", "Science ATS", "Global"),
    "057416": ("Sciences", "Science ATS", "Global"),
    # Français : Oral (20%), Lecture (40%) et Écriture (40%)
    "32410": ("Français", "Français 4", "Lecture"),
    "32420": ("Français", "Français 4", "Écriture"),
    "32430": ("Français", "Français 4", "Oral"),
    "32406": ("Français", "Français 4", "Global"),
    "132410": ("Français", "Français 4", "Lecture"),
    "132420": ("Français", "Français 4", "Écriture"),
    "132430": ("Français", "Français 4", "Oral"),
    "132406": ("Français", "Français 4", "Global"),
    "32510": ("Français", "Français 5", "Lecture"),
    "32520": ("Français", "Français 5", "Écriture"),
    "32530": ("Français", "Français 5", "Oral"),
    "32506": ("Français", "Français 5", "Global"),
    "132510": ("Français", "Français 5", "Lecture"),
    "132520": ("Français", "Français 5", "Écriture"),
    "132530": ("Français", "Français 5", "Oral"),
    "132506": ("Français", "Français 5", "Global"),
}


def _map_code_to_comp(c_val: Any) -> Optional[Tuple[str, str, str]]:
    if c_val is None or pd.isna(c_val):
        return None
    s = str(c_val).replace(".0", "").strip()
    if not s or s.lower() in ("nan", "none"):
        return None
    if s in COMPETENCY_SUFFIX_MAP:
        return COMPETENCY_SUFFIX_MAP[s]
    s5 = s[-5:] if len(s) >= 5 else s
    return COMPETENCY_SUFFIX_MAP.get(s5)


def _paired_cohen_and_p(a: pd.Series, b: pd.Series) -> Tuple[float, float]:
    """
    Calcule le d de Cohen et la p-value bilatérale (approximation normale / t apparié)
    entre deux séries de notes de compétences au sein d'un même groupe.
    """
    valid = pd.DataFrame({"a": pd.to_numeric(a, errors="coerce"), "b": pd.to_numeric(b, errors="coerce")}).dropna()
    n = len(valid)
    if n < 2:
        return 0.0, 1.0
    diff = valid["a"] - valid["b"]
    mean_diff = float(diff.mean())
    std_a = float(valid["a"].std(ddof=1))
    std_b = float(valid["b"].std(ddof=1))
    pooled_var = (std_a ** 2 + std_b ** 2) / 2.0
    cohen_d = mean_diff / np.sqrt(pooled_var) if pooled_var > 1e-6 else 0.0

    std_diff = float(diff.std(ddof=1))
    if std_diff <= 1e-6:
        p_val = 0.0 if abs(mean_diff) > 0 else 1.0
    else:
        t_stat = abs(mean_diff) / (std_diff / np.sqrt(n))
        # Approximation analytique robuste (sans dépendance lourde obligatoire) ou scipy si présent
        try:
            from scipy import stats as sp_stats
            p_val = float(2.0 * sp_stats.t.sf(t_stat, df=n - 1))
        except Exception:
            from math import erfc, sqrt
            p_val = float(erfc(t_stat / sqrt(2.0)))
    return float(cohen_d), float(p_val)


def compute_competency_gaps_by_group(
    df: pd.DataFrame,
    min_eleves: int = 10,
    seuil_delta: float = 8.0,
    seuil_cohen: float = 0.6
) -> Dict[str, pd.DataFrame]:
    """
    Analyse les écarts significatifs entre les notes des compétences d'une même matière
    au sein de chaque groupe-école :
      1. Mathématiques (CST, SN, TS) : Résoudre (C1 - 30%) vs Raisonner (C2 - 70%)
      2. Sciences (ST, ATS) : Pratique (C1 - 40%) vs Théorie (C2 - 60%)
      3. Français (4e et 5e sec.) : Oral (20%) vs Lecture (40%) vs Écriture (40%)

    Retourne un dictionnaire contenant les DataFrames agrégés par groupe-école :
      - 'math': Résoudre vs Raisonner
      - 'science': Pratique vs Théorie
      - 'francais': Oral vs Lecture vs Écriture
    """
    empty_res = {
        "math": pd.DataFrame(),
        "science": pd.DataFrame(),
        "francais": pd.DataFrame()
    }
    if df is None or not isinstance(df, pd.DataFrame) or df.empty or "CD_PERMN" not in df.columns:
        return empty_res

    course_col = "CD_COURS_str" if "CD_COURS_str" in df.columns else ("CD_COURS" if "CD_COURS" in df.columns else None)
    if course_col is None:
        return empty_res

    # Préparation vectorisée de la colonne de note (RESLT_FINAL, sinon NOTE_ECOLE_BRUT / NOTE_ECOLE_BRUTE / NOTE_ECOLE_MODR / NOTE_MINST_CONVR)
    if "RESLT_FINAL" in df.columns:
        s_note = pd.to_numeric(df["RESLT_FINAL"].astype(str).str.replace(",", "."), errors="coerce")
    else:
        s_note = pd.Series(np.nan, index=df.index)

    for fallback_col in ("NOTE_ECOLE_BRUT", "NOTE_ECOLE_BRUTE", "NOTE_ECOLE_MODR", "NOTE_MINST_CONVR"):
        if fallback_col in df.columns:
            s_fb = pd.to_numeric(df[fallback_col].astype(str).str.replace(",", "."), errors="coerce")
            s_note = s_note.fillna(s_fb)

    s_code = df[course_col].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    mapped = s_code.map(_map_code_to_comp)

    mask_valid = mapped.notna() & s_note.notna()
    if not mask_valid.any():
        return empty_res

    from core.schema import clean_cd_orgns
    import re

    clean_ec = df.loc[mask_valid, "CD_ORGNS"].apply(clean_cd_orgns).astype(str) if "CD_ORGNS" in df.columns else pd.Series("Inconnue", index=df.index[mask_valid])

    # Extraction robuste du groupe administratif sans interférence des libellés enseignants
    if "NO_GROUP_ELEVE" in df.columns:
        grp_num = df.loc[mask_valid, "NO_GROUP_ELEVE"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.zfill(2)
        grp_raw = clean_ec + "-" + grp_num
    elif "NO_GROUP" in df.columns:
        grp_num = df.loc[mask_valid, "NO_GROUP"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.zfill(2)
        grp_raw = clean_ec + "-" + grp_num
    elif "Groupe_Virtuel" in df.columns:
        grp_cleaned = df.loc[mask_valid, "Groupe_Virtuel"].astype(str).str.replace(r"\s*\([^)]*\)", "", regex=True).str.strip()
        grp_raw = grp_cleaned
    else:
        grp_raw = clean_ec + "-01"

    # Extraction optionnelle des enseignants pour enrichissement des infobulles/tableaux
    teacher_lookup = {}
    if "ENSEIGN" in df.columns:
        for idx in df.index[mask_valid]:
            t_val = str(df.loc[idx, "ENSEIGN"]).strip()
            if t_val and t_val not in ["nan", "None", "", "Inconnu"]:
                teacher_lookup[(str(clean_ec.loc[idx]), str(grp_raw.loc[idx]))] = t_val
    elif "Groupe_Virtuel" in df.columns:
        for idx in df.index[mask_valid]:
            gv_str = str(df.loc[idx, "Groupe_Virtuel"])
            if "(" in gv_str and ")" in gv_str:
                m_t = re.search(r"\(([^)]+)\)", gv_str)
                if m_t:
                    teacher_lookup[(str(clean_ec.loc[idx]), str(grp_raw.loc[idx]))] = m_t.group(1).strip()

    sub = pd.DataFrame({
        "CD_PERMN": df.loc[mask_valid, "CD_PERMN"].astype(str).str.strip(),
        "École": clean_ec,
        "Note": s_note.loc[mask_valid].astype("float32"),
        "Tuple_Map": mapped.loc[mask_valid]
    }, index=df.index[mask_valid])

    sub["Groupe"] = grp_raw.replace(["nan", "None", "", "Inconnu"], np.nan)
    sub["Famille"] = [t[0] for t in sub["Tuple_Map"]]
    sub["Matiere"] = [t[1] for t in sub["Tuple_Map"]]
    sub["Competence"] = [t[2] for t in sub["Tuple_Map"]]

    # Propagation du groupe et de l'école par (CD_PERMN, Matiere) au cas où le groupe ne figure que sur la note globale
    grp_lookup = (
        sub.dropna(subset=["Groupe"])
        .groupby(["CD_PERMN", "Matiere"], observed=True)["Groupe"]
        .first()
    )
    sub = sub.set_index(["CD_PERMN", "Matiere"])
    sub["Groupe"] = sub["Groupe"].fillna(grp_lookup)
    sub = sub.reset_index()
    sub["Groupe"] = sub["Groupe"].fillna(sub["École"] + "-01")

    # On garde uniquement les composantes (exclut 'Global' après propagation du groupe)
    sub_comp = sub[sub["Competence"] != "Global"].copy()
    if sub_comp.empty:
        return empty_res

    # Pivot par élève : une ligne par (Famille, Matiere, École, Groupe, CD_PERMN)
    piv = sub_comp.pivot_table(
        index=["Famille", "Matiere", "École", "Groupe", "CD_PERMN"],
        columns="Competence",
        values="Note",
        aggfunc="mean"
    ).reset_index()

    # -------------------------------------------------------------------------
    # A. MATHÉMATIQUES : RÉSOUDRE (C1) VS RAISONNER (C2)
    # -------------------------------------------------------------------------
    math_rows = []
    piv_math = piv[piv["Famille"] == "Mathématiques"].copy()
    if not piv_math.empty and "Résoudre" in piv_math.columns and "Raisonner" in piv_math.columns:
        piv_math = piv_math.dropna(subset=["Résoudre", "Raisonner"])
        for (mat, ec, grp), gdf in piv_math.groupby(["Matiere", "École", "Groupe"], observed=True):
            n_el = len(gdf)
            if n_el < min_eleves:
                continue
            m_res = float(gdf["Résoudre"].mean())
            m_rai = float(gdf["Raisonner"].mean())
            t_res = float((gdf["Résoudre"] >= 60.0).mean() * 100.0)
            t_rai = float((gdf["Raisonner"] >= 60.0).mean() * 100.0)
            delta = m_res - m_rai
            d_val, p_val = _paired_cohen_and_p(gdf["Résoudre"], gdf["Raisonner"])
            is_sig = bool((abs(delta) >= seuil_delta or abs(d_val) >= seuil_cohen) and p_val < 0.05)
            if is_sig and delta > 0:
                diag = "Résoudre >> Raisonner (Sur-notation C1 / Choc C2)"
            elif is_sig and delta < 0:
                diag = "Résoudre << Raisonner (Sévérité C1 Situations-problèmes)"
            else:
                diag = "Cohérent (Écart normal)"
            math_rows.append({
                "École": ec,
                "Groupe": grp,
                "Enseignant": teacher_lookup.get((str(ec), str(grp)), ""),
                "Matiere": mat,
                "Matiere_Groupe": f"{mat.replace(' ', '_')}-{grp.split('-')[-1]}",
                "Effectif": int(n_el),
                "Moy_Resoudre": round(m_res, 1),
                "Moy_Raisonner": round(m_rai, 1),
                "Taux_Resoudre": round(t_res, 1),
                "Taux_Raisonner": round(t_rai, 1),
                "Ecart_Pts": round(delta, 1),
                "Abs_Ecart": round(abs(delta), 1),
                "Cohen_D": round(d_val, 2),
                "P_Value": round(p_val, 4),
                "Ecart_Significatif": is_sig,
                "Diagnostic": diag
            })
    df_math_out = pd.DataFrame(math_rows)
    if not df_math_out.empty:
        df_math_out = df_math_out.sort_values(by="Abs_Ecart", ascending=False).reset_index(drop=True)

    # -------------------------------------------------------------------------
    # B. SCIENCES : PRATIQUE (C1 - 40%) VS THÉORIE (C2 - 60%)
    # -------------------------------------------------------------------------
    sci_rows = []
    piv_sci = piv[piv["Famille"] == "Sciences"].copy()
    if not piv_sci.empty and "Pratique" in piv_sci.columns and "Théorie" in piv_sci.columns:
        piv_sci = piv_sci.dropna(subset=["Pratique", "Théorie"])
        for (mat, ec, grp), gdf in piv_sci.groupby(["Matiere", "École", "Groupe"], observed=True):
            n_el = len(gdf)
            if n_el < min_eleves:
                continue
            m_pra = float(gdf["Pratique"].mean())
            m_the = float(gdf["Théorie"].mean())
            t_pra = float((gdf["Pratique"] >= 60.0).mean() * 100.0)
            t_the = float((gdf["Théorie"] >= 60.0).mean() * 100.0)
            delta = m_pra - m_the
            d_val, p_val = _paired_cohen_and_p(gdf["Pratique"], gdf["Théorie"])
            is_sig = bool((abs(delta) >= seuil_delta or abs(d_val) >= seuil_cohen) and p_val < 0.05)
            if is_sig and delta > 0:
                diag = "Pratique >> Théorie (Effet coussin labo / Fragilité théorique)"
            elif is_sig and delta < 0:
                diag = "Pratique << Théorie (Exigence élevée en laboratoire)"
            else:
                diag = "Cohérent (Écart normal)"
            sci_rows.append({
                "École": ec,
                "Groupe": grp,
                "Enseignant": teacher_lookup.get((str(ec), str(grp)), ""),
                "Matiere": mat,
                "Matiere_Groupe": f"{mat.replace(' ', '_')}-{grp.split('-')[-1]}",
                "Effectif": int(n_el),
                "Moy_Pratique": round(m_pra, 1),
                "Moy_Theorie": round(m_the, 1),
                "Taux_Pratique": round(t_pra, 1),
                "Taux_Theorie": round(t_the, 1),
                "Ecart_Pts": round(delta, 1),
                "Abs_Ecart": round(abs(delta), 1),
                "Cohen_D": round(d_val, 2),
                "P_Value": round(p_val, 4),
                "Ecart_Significatif": is_sig,
                "Diagnostic": diag
            })
    df_sci_out = pd.DataFrame(sci_rows)
    if not df_sci_out.empty:
        df_sci_out = df_sci_out.sort_values(by="Abs_Ecart", ascending=False).reset_index(drop=True)

    # -------------------------------------------------------------------------
    # C. FRANÇAIS : ORAL (20%) VS LECTURE (40%) VS ÉCRITURE (40%)
    # -------------------------------------------------------------------------
    fra_rows = []
    piv_fra = piv[piv["Famille"] == "Français"].copy()
    fra_cols = [c for c in ("Oral", "Lecture", "Écriture") if c in piv_fra.columns]
    if not piv_fra.empty and len(fra_cols) >= 2:
        piv_fra = piv_fra.dropna(subset=fra_cols, how="all")
        for (mat, ec, grp), gdf in piv_fra.groupby(["Matiere", "École", "Groupe"], observed=True):
            # Exiger au moins 2 compétences renseignées par élève
            gdf_valid = gdf.dropna(subset=fra_cols, thresh=2)
            n_el = len(gdf_valid)
            if n_el < min_eleves:
                continue
            m_ora = float(gdf_valid["Oral"].mean()) if "Oral" in gdf_valid.columns and gdf_valid["Oral"].notna().any() else np.nan
            m_lec = float(gdf_valid["Lecture"].mean()) if "Lecture" in gdf_valid.columns and gdf_valid["Lecture"].notna().any() else np.nan
            m_ecr = float(gdf_valid["Écriture"].mean()) if "Écriture" in gdf_valid.columns and gdf_valid["Écriture"].notna().any() else np.nan

            vals_map = {k: v for k, v in [("Oral", m_ora), ("Lecture", m_lec), ("Écriture", m_ecr)] if not np.isnan(v)}
            if len(vals_map) < 2:
                continue

            comp_max = max(vals_map, key=vals_map.get)
            comp_min = min(vals_map, key=vals_map.get)
            amp_max = vals_map[comp_max] - vals_map[comp_min]

            ec_ora_ecr = (m_ora - m_ecr) if (not np.isnan(m_ora) and not np.isnan(m_ecr)) else 0.0
            ec_lec_ecr = (m_lec - m_ecr) if (not np.isnan(m_lec) and not np.isnan(m_ecr)) else 0.0
            ec_ora_lec = (m_ora - m_lec) if (not np.isnan(m_ora) and not np.isnan(m_lec)) else 0.0

            pairs_stats = []
            for c1, c2 in [("Oral", "Écriture"), ("Lecture", "Écriture"), ("Oral", "Lecture")]:
                if c1 in gdf_valid.columns and c2 in gdf_valid.columns:
                    d_v, p_v = _paired_cohen_and_p(gdf_valid[c1], gdf_valid[c2])
                    pairs_stats.append((abs(d_v), p_v, f"{c1}-{c2}", d_v))

            if pairs_stats:
                best_pair = max(pairs_stats, key=lambda x: x[0])
                max_abs_d, p_min, pair_label, signed_d = best_pair
            else:
                max_abs_d, p_min, pair_label, signed_d = 0.0, 1.0, "N/D", 0.0

            is_sig = bool((amp_max >= seuil_delta or max_abs_d >= seuil_cohen) and p_min < 0.05)
            if is_sig:
                if comp_min == "Écriture" and comp_max == "Oral":
                    diag = "Oral >> Écriture (Effet coussin Oral / Choc Écriture)"
                elif comp_min == "Écriture" and comp_max == "Lecture":
                    diag = "Lecture >> Écriture (Décrochage en production écrite)"
                elif comp_min == "Lecture":
                    diag = f"{comp_max} >> Lecture (Déficit de compréhension en lecture)"
                else:
                    diag = f"Distorsion {comp_max} >> {comp_min} (+{amp_max:.1f} pts)"
            else:
                diag = "Profil tripartite équilibré"

            fra_rows.append({
                "École": ec,
                "Groupe": grp,
                "Enseignant": teacher_lookup.get((str(ec), str(grp)), ""),
                "Matiere": mat,
                "Matiere_Groupe": f"{mat.replace(' ', '')}-{grp.split('-')[-1]}",
                "Effectif": int(n_el),
                "Moy_Oral": round(m_ora, 1) if not np.isnan(m_ora) else np.nan,
                "Moy_Lecture": round(m_lec, 1) if not np.isnan(m_lec) else np.nan,
                "Moy_Ecriture": round(m_ecr, 1) if not np.isnan(m_ecr) else np.nan,
                "Ecart_Oral_Ecriture": round(ec_ora_ecr, 1),
                "Ecart_Lecture_Ecriture": round(ec_lec_ecr, 1),
                "Ecart_Oral_Lecture": round(ec_ora_lec, 1),
                "Amplitude_Max": round(amp_max, 1),
                "Paire_Critique": f"{comp_max} vs {comp_min}",
                "Cohen_D": round(signed_d, 2),
                "P_Value": round(p_min, 4),
                "Ecart_Significatif": is_sig,
                "Diagnostic": diag
            })
    df_fra_out = pd.DataFrame(fra_rows)
    if not df_fra_out.empty:
        df_fra_out = df_fra_out.sort_values(by="Amplitude_Max", ascending=False).reset_index(drop=True)

    return {
        "math": df_math_out,
        "science": df_sci_out,
        "francais": df_fra_out
    }




