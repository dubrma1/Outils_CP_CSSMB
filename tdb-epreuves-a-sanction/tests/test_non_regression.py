# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pytest
from core.data_loader import clean_and_merge_data, clean_moderation_df
from core.metrics import compute_success_rate, wilson_interval, compute_cohen_d
from data_processing import analyze_moderation_df, wilson_interval as old_wilson


def test_wilson_interval_non_regression():
    for succ, tot in [(80, 100), (45, 50), (12, 15), (0, 30), (30, 30)]:
        new_low, new_up = wilson_interval(succ, tot, 0.95)
        old_low, old_up = old_wilson(succ, tot, 0.95)
        assert new_low == pytest.approx(old_low, rel=1e-4)
        assert new_up == pytest.approx(old_up, rel=1e-4)


def test_moderation_analysis_non_regression():
    data = {
        "Organisme": ["763041", "763245", "763136"],
        "Groupe": ["01", "02", "03"],
        "Matiere": ["Français 5", "Math CST", "Science ST"],
        "Nb_eleves": [25, 30, 18],
        "Moyenne_ecole": [74.5, 62.0, 81.0],
        "ET_ecole": [9.0, 12.0, 8.5],
        "Moyenne_min": [68.0, 65.0, 80.0],
        "ET_min": [10.0, 11.0, 9.0]
    }
    df = pd.DataFrame(data)

    df_old = analyze_moderation_df(df.copy(), seuil_cohen=0.8, seuil_dispersion=0.6)
    df_new = clean_moderation_df(df.copy())
    df_new["Delta_Moyenne"] = (df_new["Moyenne_ecole"] - df_new["Moyenne_min"]).astype("float32")
    var_p = (df_new["ET_ecole"]**2 + df_new["ET_min"]**2) / 2.0
    df_new["Cohen_D"] = (df_new["Delta_Moyenne"] / np.sqrt(var_p)).astype("float32")

    # Comparer les deltas et les d de Cohen
    assert np.allclose(df_old["Delta_Moyenne"].values, df_new["Delta_Moyenne"].values, atol=1e-3)
    assert np.allclose(df_old["Cohen_D"].values, df_new["Cohen_D"].values, atol=1e-3)



def test_clean_and_merge_data_type_cours_and_parcours():
    df_105 = pd.DataFrame({
        "CD_ORGNS": ["763041", "763041", "763041"],
        "CD_PERMN": ["STUDENT1", "STUDENT2", "STUDENT3"],
        "CD_COURS": ["132406", "132410", "058404"],
        "RESLT_FINAL": [75.0, 80.0, 65.0]
    })
    merged = clean_and_merge_data(df_105, None, None)
    assert "Type_Cours" in merged.columns
    assert "Parcours" in merged.columns
    # 132406 ends in 6 -> Note globale
    assert merged.loc[merged["CD_PERMN"] == "STUDENT1", "Type_Cours"].iloc[0] == "Note globale"
    # 132410 ends in 0 -> Composante
    assert merged.loc[merged["CD_PERMN"] == "STUDENT2", "Type_Cours"].iloc[0] == "Composante"
    # 058404 is enriched
    assert merged.loc[merged["CD_PERMN"] == "STUDENT3", "Parcours"].iloc[0] == "Enrichi"


def test_failure_pairs_with_nan_mixed_types():
    # Test non-régression pour éviter TypeError: '<' not supported between instances of 'str' and 'float'
    from itertools import combinations
    from core.schema import SANCTION_4E_MATIERES

    df_test = pd.DataFrame({
        "CD_PERMN": ["E1", "E1", "E1", "E2", "E2"],
        "Matiere_Simple": ["Science ST", np.nan, "Math CST", "Histoire 4", "Histoire 4"],
        "RESLT_FINAL": [50.0, 45.0, 55.0, 40.0, 52.0]
    })

    df_sanction = df_test[df_test["Matiere_Simple"].isin(SANCTION_4E_MATIERES)].copy()
    paires_list = []
    eleves_grouped = df_sanction.groupby("CD_PERMN")["Matiere_Simple"].unique()
    for mats in eleves_grouped:
        valid_mats = sorted([str(m).strip() for m in mats if pd.notna(m) and str(m).strip() not in ["", "nan", "None"]])
        if len(valid_mats) >= 2:
            for pair in combinations(valid_mats, 2):
                paires_list.append(" & ".join(pair))

    assert len(paires_list) == 1
    assert paires_list[0] == "Math CST & Science ST"
