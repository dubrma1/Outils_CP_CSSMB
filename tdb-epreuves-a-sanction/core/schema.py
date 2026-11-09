# -*- coding: utf-8 -*-
"""
core/schema.py - Nomenclature officielle et référentiels du tableau de bord.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import pandas as pd

# 1. ÉCOLES, SECTEURS ET RETAC
ECOLES_LIST: List[str] = [
    "037", "038", "040", "041", "042",
    "136", "138", "139", "142", "144",
    "236", "238", "240", "241", "243", "245"
]

ECOLES_OPTIONS: List[str] = ["Toutes"] + ECOLES_LIST

ECOLES_SECTEURS: Dict[str, str] = {
    "037": "NORD", "038": "NORD", "040": "NORD", "041": "NORD", "042": "NORD",
    "136": "SUD", "138": "SUD", "139": "SUD", "142": "SUD", "144": "SUD",
    "236": "OUEST", "238": "OUEST", "240": "OUEST", "241": "OUEST", "243": "OUEST", "245": "OUEST"
}

# Cartographie officielle des 4 RETAC du CSSMB
RETAC_LIST: List[str] = ["Tous", "OUEST", "Saint-Laurent", "Lachine", "EST"]

RETAC_ECOLES: Dict[str, List[str]] = {
    "OUEST": ["236", "238", "240", "241", "243", "245"],
    "Saint-Laurent": ["037", "038"],
    "Lachine": ["136", "138", "139", "142", "144"],
    "EST": ["040", "041", "042"]
}

ECOLE_TO_RETAC: Dict[str, str] = {}
for _retac_name, _ec_list in RETAC_ECOLES.items():
    for _ec in _ec_list:
        ECOLE_TO_RETAC[_ec] = _retac_name


def get_retac_for_ecole(cd_orgns: Any) -> str:
    """Retourne le nom du RETAC d'appartenance de l'école (OUEST, Saint-Laurent, Lachine, EST)."""
    clean_code = clean_cd_orgns(cd_orgns)
    return ECOLE_TO_RETAC.get(clean_code, "Autre")


def get_ecoles_for_retac(retac_name: str) -> List[str]:
    """Retourne la liste des codes d'écoles pour un RETAC donné, ou toutes les écoles si 'Tous'."""
    if not retac_name or retac_name == "Tous":
        return list(ECOLES_LIST)
    return RETAC_ECOLES.get(retac_name, list(ECOLES_LIST))


def clean_cd_orgns(val: Any) -> str:
    """Extrait les 3 chiffres de l'école (ex: '763041' -> '041', '41' -> '041')."""
    if pd.isna(val) or val is None:
        return ""
    s = str(val).strip().replace(".0", "")
    if s.lower() in ["toutes", "tous", "all", "", "nan", "none", "0", "00", "000"]:
        return ""
    if len(s) == 6 and s.isdigit():
        return s[3:]
    if s.startswith("763") and len(s) > 3:
        return s[3:]
    if s.isdigit() and len(s) < 3:
        return s.zfill(3)
    if s.isdigit() and len(s) > 3:
        return s[-3:]
    return s


def get_course_level(course_code: Any) -> Optional[int]:
    """
    Extrait le niveau du secondaire à partir du code de cours:
    Le chiffre à la 3e position depuis la droite indique le niveau
    (ex: 055444 -> 4, 65426 -> 4, 132506 -> 5, 85404 -> 4).
    """
    if pd.isna(course_code) or course_code is None:
        return None
    s = str(course_code).strip().replace(".0", "")
    if len(s) >= 3 and s[-3].isdigit():
        lvl = int(s[-3])
        if 1 <= lvl <= 5:
            return lvl
    return None


def classify_group_type(group_code: Any) -> str:
    """
    Classifie la typologie du groupe d'élèves à partir du numéro de groupe:
    - 01 à 12 : Régulier
    - 30 à 35 : PEI (Programme Éducation Internationale)
    - 50 à 55 : Concentration (musique, sport, etc.)
    - 80 à 85 : EHDAA (Élèves en difficultés d'apprentissage ou d'adaptation)
    - 90 à 99 : Cas particuliers (école à la maison, milieu hospitalier, etc.)
    - Autre
    """
    if pd.isna(group_code) or group_code is None:
        return "Inconnu"
    s = str(group_code).strip().replace(".0", "")
    import re
    digits = re.findall(r"\d+", s)
    if not digits:
        return "Autre"
    num = int(digits[0])
    if 1 <= num <= 12:
        return "Régulier"
    elif 30 <= num <= 35:
        return "PEI"
    elif 50 <= num <= 55:
        return "Concentration"
    elif 80 <= num <= 85:
        return "EHDAA"
    elif 90 <= num <= 99:
        return "Cas particuliers"
    return "Autre"


# 2. PARCOURS ENRICHIS
ENRICHED_CODES: List[str] = [
    "58404", "058404", "58402", "058402",
    "51514", "051514", "53514", "053514"
]

# 3. RÉFÉRENTIEL DES MATIÈRES (SUBJECT_MAP)
SUBJECT_MAP: Dict[str, Dict[str, Any]] = {
    "Français 4 (132406)": {
        "global": ["132406", "0132406"],
        "nom_court": "Français 4",
        "type": "Français",
        "epreuve_nom": "Français 4 (Écriture)",
        "comp_p": "Écriture",
        "composantes": [
            {"nom": "Lecture", "codes": ["132410", "0132410"], "poids": 40},
            {"nom": "Écriture", "codes": ["132420", "0132420"], "poids": 40, "epreuve_unique": True},
            {"nom": "Communication", "codes": ["132430", "0132430"], "poids": 20}
        ]
    },
    "Français 5 (132506)": {
        "global": ["132506", "0132506"],
        "nom_court": "Français 5",
        "type": "Français",
        "epreuve_nom": "Français 5 (Écriture)",
        "comp_p": "Écriture",
        "composantes": [
            {"nom": "Lecture", "codes": ["132510", "0132510"], "poids": 40},
            {"nom": "Écriture", "codes": ["132520", "0132520"], "poids": 40, "epreuve_unique": True},
            {"nom": "Communication", "codes": ["132530", "0132530"], "poids": 20}
        ]
    },
    "Math CST (63414)": {
        "global": ["63414", "063414"],
        "nom_court": "Math CST",
        "type": "Math",
        "epreuve_nom": "Math CST (Raisonner)",
        "comp_p": "Résoudre",
        "composantes": [
            {"nom": "Résoudre", "codes": ["63410", "063410"], "poids": 30},
            {"nom": "Raisonner", "codes": ["63420", "063420"], "poids": 70, "epreuve_unique": True}
        ]
    },
    "Math SN (65426)": {
        "global": ["65426", "065426"],
        "nom_court": "Math SN",
        "type": "Math",
        "epreuve_nom": "Math SN (Raisonner)",
        "comp_p": "Résoudre",
        "composantes": [
            {"nom": "Résoudre", "codes": ["65410", "065410"], "poids": 30},
            {"nom": "Raisonner", "codes": ["65420", "065420"], "poids": 70, "epreuve_unique": True}
        ]
    },
    "Math TS (64426)": {
        "global": ["64426", "064426"],
        "nom_court": "Math TS",
        "type": "Math",
        "epreuve_nom": "Math TS (Raisonner)",
        "comp_p": "Résoudre",
        "composantes": [
            {"nom": "Résoudre", "codes": ["64410", "064410"], "poids": 30},
            {"nom": "Raisonner", "codes": ["64420", "064420"], "poids": 70, "epreuve_unique": True}
        ]
    },
    "Anglais 5 base (134504)": {
        "global": ["134504", "0134504"],
        "nom_court": "Anglais 5 base",
        "type": "Anglais",
        "epreuve_nom": "Anglais 5 (Compréhension)",
        "comp_p": "Production",
        "composantes": [
            {"nom": "Interaction", "codes": ["134510", "0134510"], "poids": 40},
            {"nom": "Compréhension", "codes": ["134520", "0134520"], "poids": 30, "epreuve_unique": True},
            {"nom": "Production", "codes": ["134530", "0134530"], "poids": 30}
        ]
    },
    "Science ST (55444)": {
        "global": ["55444", "055444", "555444", "0555444"],
        "nom_court": "Science ST",
        "type": "Science",
        "epreuve_nom": "Science ST (Théorie)",
        "comp_p": "Pratique",
        "composantes": [
            {"nom": "Théorie", "codes": ["55410", "055410"], "poids": 60, "epreuve_unique": True},
            {"nom": "Pratique", "codes": ["55420", "055420"], "poids": 40}
        ]
    },
    "Science ATS (57406)": {
        "global": ["57406", "057406", "557406", "0557406", "57416", "057416"],
        "nom_court": "Science ATS",
        "type": "Science",
        "epreuve_nom": "Science ATS (Théorie)",
        "comp_p": "Pratique",
        "composantes": [
            {"nom": "Théorie", "codes": ["57410", "057410"], "poids": 60, "epreuve_unique": True},
            {"nom": "Pratique", "codes": ["57420", "057420"], "poids": 40}
        ]
    },
    "Histoire QC-Canada (85404)": {
        "global": ["85404", "085404", "585404", "0585404"],
        "nom_court": "Histoire 4",
        "type": "Histoire",
        "epreuve_nom": "Histoire QC-Canada (Épreuve)",
        "comp_p": None,
        "composantes": []
    }
}

MATIERES_LIST: List[str] = ["Toutes"] + list(SUBJECT_MAP.keys())

# =============================================================================
# 4. ÉPREUVES UNIQUES MINISTÉRIELLES (SOURCE UNIQUE & CORRIGÉE)
# =============================================================================
EPREUVES_MAP: Dict[str, List[str]] = {
    "Français 4 (Écriture)": ["132420", "0132420"],
    "Français 5 (Écriture)": ["132520", "0132520"],
    "Math CST (Raisonner)": ["63420", "063420"],
    "Math SN (Raisonner)": ["65420", "065420"],
    "Math TS (Raisonner)": ["64420", "064420"],
    "Science ST (Théorie)": ["55410", "055410"],
    "Science ATS (Théorie)": ["57410", "057410"],
    "Anglais 5 (Compréhension)": ["134520", "0134520"],
    "Histoire QC-Canada (Épreuve)": ["85404", "085404", "585404", "0585404"]
}

SANCTION_4E_MATIERES: List[str] = [
    "Histoire 4", "Science ST", "Science ATS", "Math CST", "Math SN", "Math TS"
]


def _build_code_mappings():
    code_to_mat: Dict[str, str] = {}
    code_to_mat_court: Dict[str, str] = {}
    matieres_cibles_full: Dict[str, Dict[str, Any]] = {}
    sanction_mat_map: Dict[str, Dict[str, Any]] = {}

    for mat_full, info in SUBJECT_MAP.items():
        nom_court = info["nom_court"]
        matieres_cibles_full[nom_court] = {
            "global": list(info["global"]),
            "composantes": list(info["composantes"]),
            "comp_p": info["comp_p"],
            "type": info["type"]
        }
        if nom_court == "Histoire 4":
            matieres_cibles_full["Histoire QC-Canada"] = matieres_cibles_full[nom_court]

        all_codes = list(info["global"])
        for comp in info["composantes"]:
            all_codes.extend(comp["codes"])
        sanction_mat_map[mat_full] = {
            "codes": all_codes,
            "labels": {c: c.lstrip("0") for c in all_codes}
        }

        for c in info["global"]:
            c_clean = str(c).strip().replace(".0", "")
            code_to_mat[c_clean] = mat_full
            code_to_mat[c_clean.lstrip("0")] = mat_full
            code_to_mat[c_clean.zfill(6)] = mat_full

            code_to_mat_court[c_clean] = nom_court
            code_to_mat_court[c_clean.lstrip("0")] = nom_court
            code_to_mat_court[c_clean.zfill(6)] = nom_court

    code_to_epr: Dict[str, str] = {}
    epr_to_mat: Dict[str, str] = {}

    for epr_name, codes in EPREUVES_MAP.items():
        for c in codes:
            c_clean = str(c).strip().replace(".0", "")
            code_to_epr[c_clean] = epr_name
            code_to_epr[c_clean.lstrip("0")] = epr_name
            code_to_epr[c_clean.zfill(6)] = epr_name

    for mat_full, info in SUBJECT_MAP.items():
        epr_name = info.get("epreuve_nom")
        if epr_name:
            epr_to_mat[epr_name] = mat_full

    return code_to_mat, code_to_mat_court, code_to_epr, epr_to_mat, matieres_cibles_full, sanction_mat_map


(
    CODE_TO_MATIERE,
    CODE_TO_MATIERE_COURT,
    CODE_TO_EPREUVE,
    EPREUVE_TO_MATIERE,
    MATIERES_CIBLES_FULL,
    SANCTION_MATIERES_MAP
) = _build_code_mappings()

