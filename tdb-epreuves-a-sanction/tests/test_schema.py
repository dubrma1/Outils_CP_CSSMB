# -*- coding: utf-8 -*-
import pytest
from core.schema import (
    clean_cd_orgns,
    ECOLES_LIST,
    ECOLES_SECTEURS,
    ENRICHED_CODES,
    SUBJECT_MAP,
    EPREUVES_MAP,
    CODE_TO_MATIERE,
    CODE_TO_EPREUVE,
    get_course_level,
    classify_group_type
)


def test_clean_cd_orgns():
    assert clean_cd_orgns("763041") == "041"
    assert clean_cd_orgns("763245") == "245"
    assert clean_cd_orgns("41") == "041"
    assert clean_cd_orgns("136") == "136"
    assert clean_cd_orgns(None) == ""
    assert clean_cd_orgns("Toutes") == ""
    assert clean_cd_orgns("000") == ""


def test_ecoles_and_secteurs():
    assert len(ECOLES_LIST) == 16
    for ecole in ECOLES_LIST:
        assert ecole in ECOLES_SECTEURS
        assert ECOLES_SECTEURS[ecole] in ["NORD", "SUD", "OUEST"]


def test_enriched_codes_consistency():
    # Codes enrichis unifiés
    for code in ["58404", "058404", "58402", "058402", "51514", "051514", "53514", "053514"]:
        assert code in ENRICHED_CODES


def test_math_raisonner_vs_resoudre_epreuve_unique():
    """
    Vérification critique de la non-régression et de la correction de bug docimologique :
    Pour les mathématiques du secondaire, l'épreuve unique ministérielle porte sur
    la compétence 'Raisonner' (codes 63420, 65420, 64420) et NON 'Résoudre' (63410, 65410, 64410).
    """
    assert "63420" in EPREUVES_MAP["Math CST (Raisonner)"]
    assert "65420" in EPREUVES_MAP["Math SN (Raisonner)"]
    assert "64420" in EPREUVES_MAP["Math TS (Raisonner)"]

    assert CODE_TO_EPREUVE["63420"] == "Math CST (Raisonner)"
    assert CODE_TO_EPREUVE["65420"] == "Math SN (Raisonner)"
    assert CODE_TO_EPREUVE["64420"] == "Math TS (Raisonner)"



def test_get_course_level():
    assert get_course_level("055444") == 4
    assert get_course_level("65426") == 4
    assert get_course_level("132506") == 5
    assert get_course_level("85404") == 4
    assert get_course_level("123306") == 3
    assert get_course_level("12") is None


def test_classify_group_type():
    assert classify_group_type("01") == "Régulier"
    assert classify_group_type("12") == "Régulier"
    assert classify_group_type("32") == "PEI"
    assert classify_group_type("54") == "Concentration"
    assert classify_group_type("81") == "EHDAA"
    assert classify_group_type("92") == "Cas particuliers"
    assert classify_group_type("22") == "Autre"

    # 'Résoudre' n'est PAS l'épreuve unique
    assert "63410" not in CODE_TO_EPREUVE
    assert "65410" not in CODE_TO_EPREUVE
    assert "64410" not in CODE_TO_EPREUVE


def test_subject_map_coherence():
    # Toutes les matières principales sont présentes
    assert "Français 4 (132406)" in SUBJECT_MAP
    assert "Français 5 (132506)" in SUBJECT_MAP
    assert "Math CST (63414)" in SUBJECT_MAP
    assert "Science ST (55444)" in SUBJECT_MAP
    assert "Histoire QC-Canada (85404)" in SUBJECT_MAP
