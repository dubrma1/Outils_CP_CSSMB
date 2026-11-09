# -*- coding: utf-8 -*-
"""
core/privacy.py - Règles de confidentialité, Loi 25 (Québec) et suppression des petites cellules.
Garantit qu'aucun groupe < 5 élèves n'est divulgué individuellement,
qu'aucune donnée nominative n'apparaît par défaut, et prévient des biais d'échantillon (N < 15).
"""

from typing import List, Optional, Tuple, Union
import numpy as np
import pandas as pd

MIN_CELL_COUNT: int = 5
RELIABILITY_THRESHOLD: int = 15


def filter_small_cells(
    df: pd.DataFrame,
    count_col: str = "Nb_eleves",
    min_count: int = MIN_CELL_COUNT
) -> Tuple[pd.DataFrame, int]:
    """
    Filtre les entités dont l'effectif est strictement inférieur à min_count.
    Retourne le DataFrame filtré et le nombre d'entités masquées.
    """
    if df is None or df.empty or count_col not in df.columns:
        return df if df is not None else pd.DataFrame(), 0

    counts = pd.to_numeric(df[count_col], errors="coerce").fillna(0)
    mask = counts >= min_count
    suppressed_count = int((~mask).sum())
    return df.loc[mask].copy(), suppressed_count


def mask_small_cells(
    df: pd.DataFrame,
    count_col: str = "Nb_eleves",
    min_count: int = MIN_CELL_COUNT,
    mask_cols: Optional[List[str]] = None,
    mask_value: str = "< 5"
) -> pd.DataFrame:
    """
    Masque les valeurs des colonnes sensibles pour les effectifs < min_count.
    Préserve la structure du tableau tout en empêchant la ré-identification.
    """
    if df is None or df.empty or count_col not in df.columns:
        return df if df is not None else pd.DataFrame()

    df_masked = df.copy()
    counts = pd.to_numeric(df_masked[count_col], errors="coerce").fillna(0)
    small_mask = counts < min_count

    cols_to_mask = mask_cols if mask_cols else [count_col]
    for col in cols_to_mask:
        if col in df_masked.columns:
            # Conversion en type object/string si nécessaire pour accueillir le libellé masqué
            df_masked[col] = df_masked[col].astype(str)
            df_masked.loc[small_mask, col] = mask_value

    return df_masked


def get_privacy_warning_message(suppressed_count: int, min_count: int = MIN_CELL_COUNT) -> str:
    """Génère la mention explicite de conformité à la Loi 25 lorsque des cellules sont masquées."""
    if suppressed_count <= 0:
        return ""
    entite = "groupe/cellule" if suppressed_count == 1 else "groupes/cellules"
    return (
        f"**Protection des renseignements personnels (Loi 25)** : {suppressed_count} {entite} "
        f"de moins de {min_count} élèves a/ont été exclu(s) ou agrégé(s) pour prévenir tout risque "
        "d'identification indirecte."
    )


def get_sample_size_warning(n: Union[int, float], threshold: int = RELIABILITY_THRESHOLD) -> Optional[str]:
    """Retourne un message de prudence docimologique si la taille d'échantillon est restreinte."""
    if pd.isna(n) or n <= 0:
        return None
    if n < threshold:
        return (
            f"**Effectif restreint (N = {int(n)})** : Un effectif inférieur à {threshold} élèves "
            "entraîne une volatilité statistique accrue. Les résultats doivent être interprétés avec discernement."
        )
    return None


def sanitize_teacher_display(
    label: str,
    allow_teacher_view: bool = False,
    placeholder: str = "[Enseignant masqué]"
) -> str:
    """
    Anonymise les mentions d'enseignants dans les étiquettes de groupes sauf si l'opt-in est activé.
    Format attendu du libellé : 'École XXX - Gr. YY (Nom Enseignant)' -> 'École XXX - Gr. YY'
    """
    if allow_teacher_view or not label:
        return label
    import re
    # Supprime la parenthèse finale contenant le nom de l'enseignant
    return re.sub(r"\s*\([^)]*\)$", "", str(label)).strip()
