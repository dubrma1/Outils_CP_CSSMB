# -*- coding: utf-8 -*-
import pandas as pd
import pytest
from core.privacy import (
    filter_small_cells,
    mask_small_cells,
    get_privacy_warning_message,
    get_sample_size_warning,
    sanitize_teacher_display
)


def test_filter_small_cells():
    df = pd.DataFrame({
        "Groupe": ["G1", "G2", "G3", "G4"],
        "Nb_eleves": [3, 4, 5, 25]
    })
    filtered, suppressed = filter_small_cells(df, count_col="Nb_eleves", min_count=5)
    assert suppressed == 2
    assert len(filtered) == 2
    assert set(filtered["Groupe"]) == {"G3", "G4"}


def test_mask_small_cells():
    df = pd.DataFrame({
        "Groupe": ["G1", "G2"],
        "Nb_eleves": [3, 20],
        "Moyenne": [75.0, 80.0]
    })
    masked = mask_small_cells(df, count_col="Nb_eleves", min_count=5, mask_cols=["Moyenne"])
    assert masked.loc[masked["Groupe"] == "G1", "Moyenne"].iloc[0] == "< 5"
    assert float(masked.loc[masked["Groupe"] == "G2", "Moyenne"].iloc[0]) == 80.0


def test_get_privacy_warning_message():
    msg = get_privacy_warning_message(3, min_count=5)
    assert "Loi 25" in msg
    assert "3 groupes/cellules de moins de 5" in msg
    assert get_privacy_warning_message(0) == ""


def test_get_sample_size_warning():
    warn_small = get_sample_size_warning(10, threshold=15)
    assert warn_small is not None
    assert "N = 10" in warn_small

    warn_ok = get_sample_size_warning(30, threshold=15)
    assert warn_ok is None


def test_sanitize_teacher_display():
    raw_label = "École 041 - Gr. 02 (Tremblay, Jean)"
    # Sans opt-in : nom retiré
    assert sanitize_teacher_display(raw_label, allow_teacher_view=False) == "École 041 - Gr. 02"
    # Avec opt-in : nom préservé
    assert sanitize_teacher_display(raw_label, allow_teacher_view=True) == raw_label
