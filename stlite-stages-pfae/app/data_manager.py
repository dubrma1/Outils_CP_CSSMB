"""
data_manager.py
Module de gestion des données pour le Tableau de bord PFAE - Suivi des Stages (CSSMB).
Adapté pour Stlite / Pyodide (WebAssembly) :
- Zéro dépendance à filelock (compatible WebAssembly mono-thread).
- Chemins relatifs normalisés vers le système de fichiers virtuel ./data/ (MEMFS).
- Sauvegarde en mémoire virtuelle avec fonction de téléchargement synchrone.
- Conformité Loi 25 (traitement 100 % local dans le navigateur).
"""

import builtins
import os
import io
import glob
import shutil
import datetime
from typing import Optional, Tuple, Dict, Any, List
import pandas as pd

# Sécurité globale Stlite/Pyodide pour st.data_editor
class _MockArrowSchema(tuple):
    @property
    def names(self):
        return []

class _MockArrowTable:
    schema = _MockArrowSchema()
    num_rows = 0
    num_columns = 0
    def __iter__(self):
        return iter(())
    def __len__(self):
        return 0

builtins.arrow_table = _MockArrowTable()

# Mapping institutionnel des établissements scolaires du CSSMB
ECOLE_MAPPING: Dict[Any, str] = {
    37: "SAS",
    "037": "SAS",
    "37": "SAS",
    135: "RVP (Rose-Virginie-Pelletier)",
    "135": "RVP (Rose-Virginie-Pelletier)",
    138: "Dalbé-Viau",
    "138": "Dalbé-Viau",
    139: "Cavelier-de-LaSalle",
    "139": "Cavelier-de-LaSalle",
    142: "Mgr-Richard",
    "142": "Mgr-Richard",
    236: "Des Sources",
    "236": "Des Sources",
    238: "Saint-Laurent / Pôle complémentaire",
    "238": "Saint-Laurent / Pôle complémentaire",
    241: "Dorval-Jean-XXIII",
    "241": "Dorval-Jean-XXIII",
    245: "de l'Altitude",
    "245": "de l'Altitude",
}

# Codes de cours associés spécifiquement aux stages
STAGE_COURSES_FMS = [196204]
STAGE_COURSES_FPT = [108230, 108234]
ALL_STAGE_COURSES = STAGE_COURSES_FMS + STAGE_COURSES_FPT

# Options des champs de suivi
OPTIONS_CARNET = ["Pas distribué", "En cours", "Complété", "Validé"]
OPTIONS_MI_STAGE = ["Non réalisée", "En cours", "Complétée"]

# Noms de colonnes originaux du CSV
RAW_COLUMNS = [
    "CD_ECOLE",
    "Description",
    "NO_ELEVE",
    "CODE_ENSEIGN",
    "NOM_ENSEIGN",
    "PARCOURS",
    "CD_COURS",
    "TITRE_COURS",
    "FONCTION",
    "Date de départ en stage",
    "Carnet de stage?",
    "Évaluation mi-stage",
    "Absentéisme",
    "Code_FGJ",
    "Metier_FMS",
    "Commentaires_Stage",
]

# Les 11 rôles officiels de la classe-atelier et du stage FMS
ROLES_CLASSE_ATELIER_FMS: List[Tuple[str, str, str]] = [
    ("Rôle 1", "Santé et sécurité au travail (SST)", "Appliquer rigoureusement les normes de prévention, d'hygiène et les règles SST en milieu de travail."),
    ("Rôle 2", "Outils, instruments et équipements", "Utiliser adéquatement et sécuritairement l'outillage et les équipements spécifiques du métier."),
    ("Rôle 3", "Consignes et standards de travail", "Respecter les directives techniques, les normes de fabrication et les standards de production."),
    ("Rôle 4", "Communication professionnelle", "Interagir efficacement, poliment et professionnellement avec ses pairs, supérieurs et clients."),
    ("Rôle 5", "Organisation et gestion du temps", "Organiser méthodiquement son poste de travail et respecter les cadences et échéanciers impartis."),
    ("Rôle 6", "Contrôle de la qualité", "Vérifier la conformité de ses réalisations et identifier les anomalies pour les corriger."),
    ("Rôle 7", "Adaptation aux imprévus", "Faire preuve de souplesse, de réactivité et de débrouillardise devant des imprévus courants."),
    ("Rôle 8", "Travail d'équipe et coopération", "Collaborer harmonieusement et participer activement à la dynamique collective de l'entreprise."),
    ("Rôle 9", "Éthique et posture professionnelle", "Démontrer assiduité, ponctualité, rigueur, tenue vestimentaire adaptée et attitude positive."),
    ("Rôle 10", "Autoévaluation et réflexivité", "Évaluer lucidement sa performance, reconnaître ses forces et intégrer la rétroaction constructive."),
    ("Rôle 11", "Préparation à l'insertion durable", "Consolider son identité professionnelle pour réussir une transition harmonieuse vers l'emploi."),
]


def find_rms_file(base_dir: Optional[str] = None) -> str:
    """
    Localise de manière robuste le fichier du répertoire des métiers semi-spécialisés du MEQ
    dans le dossier virtuel relatif ./data/ ou les dossiers parents.
    """
    standard_name = "repertoire_metiers_semi_specialises_meq.csv"
    candidates = []
    if base_dir:
        candidates.extend([
            os.path.join(base_dir, standard_name),
            os.path.join(base_dir, "data", standard_name),
        ])
    here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
    candidates.extend([
        os.path.join("data", standard_name),
        os.path.join(".", "data", standard_name),
        os.path.join(here, "..", "data", standard_name),
        os.path.join(here, "data", standard_name),
        os.path.join(here, standard_name),
        standard_name,
    ])
    for c in candidates:
        if os.path.exists(c):
            return c
        d = os.path.dirname(c) or "."
        if os.path.exists(d):
            matches = glob.glob(os.path.join(d, "*repertoire_metiers*.csv"))
            if matches:
                return matches[0]
    return os.path.join("data", standard_name)


def load_rms_referentiel(rms_path: Optional[str] = None) -> pd.DataFrame:
    """Charge le répertoire des métiers semi-spécialisés du MEQ (séparateur ;, encodage utf-8-sig)."""
    path = rms_path or find_rms_file()
    if not os.path.exists(path):
        return pd.DataFrame(columns=["Secteur", "Code_FGJ", "Metier", "METIER_LABEL"])
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            df = pd.read_csv(path, sep=";", encoding=enc, dtype=str)
            df.columns = [c.strip() for c in df.columns]
            df["Code_FGJ"] = df["Code_FGJ"].astype(str).str.strip()
            df["Metier"] = df["Metier"].astype(str).str.strip()
            df["Secteur"] = df["Secteur"].astype(str).str.strip()
            # Création du libellé officiel combiné : METIER_LABEL = Code_FGJ + " - " + Metier
            df["METIER_LABEL"] = df["Code_FGJ"] + " - " + df["Metier"]
            return df
        except Exception:
            continue
    return pd.DataFrame(columns=["Secteur", "Code_FGJ", "Metier", "METIER_LABEL"])


_RMS_CACHE: Dict[str, Any] = {}

def get_rms_lookup() -> Dict[str, Any]:
    """Retourne les dictionnaires de correspondance rapide pour les métiers RMS."""
    if _RMS_CACHE.get("ready"):
        return _RMS_CACHE

    df_rms = load_rms_referentiel()
    by_code = {}
    by_label = {}
    for _, r in df_rms.iterrows():
        code = str(r["Code_FGJ"]).strip()
        metier = str(r["Metier"]).strip()
        secteur = str(r["Secteur"]).strip()
        label = str(r["METIER_LABEL"]).strip()
        info = {
            "Code_FGJ": code,
            "Metier": metier,
            "Secteur": secteur,
            "METIER_LABEL": label,
        }
        by_code[code] = info
        by_label[label] = info

    labels = [""] + sorted(df_rms["METIER_LABEL"].unique().tolist())
    secteurs = sorted(df_rms["Secteur"].unique().tolist())

    _RMS_CACHE.update({
        "df": df_rms,
        "by_code": by_code,
        "by_label": by_label,
        "labels": labels,
        "secteurs": secteurs,
        "ready": True,
    })
    return _RMS_CACHE


def get_rms_options() -> List[str]:
    """Retourne la liste ordonnée des options pour le sélecteur de métiers."""
    lookup = get_rms_lookup()
    return lookup.get("labels", [""])


def get_school_name(cd_ecole: Any) -> str:
    """Retourne le nom de l'école correspondant au code."""
    try:
        cd_int = int(cd_ecole)
        if cd_int in ECOLE_MAPPING:
            return ECOLE_MAPPING[cd_int]
    except (ValueError, TypeError):
        pass
    cd_str = str(cd_ecole).strip()
    return ECOLE_MAPPING.get(cd_str, f"École {cd_str}")


def format_school_display(cd_ecole: Any) -> str:
    """Retourne le libellé formaté: 'Code - Nom' (ex. 138 - Dalbé-Viau)."""
    nom = get_school_name(cd_ecole)
    cd_str = str(cd_ecole).strip()
    return f"{cd_str} - {nom}"


def find_csv_file(base_dir: Optional[str] = None) -> str:
    """
    Localise de manière défensive le fichier CSV des listes d'élèves dans le dossier virtuel ./data/.
    Gère les chemins relatifs dans Pyodide (MEMFS) sans dépendre de disques physiques Windows.
    """
    standard_name = "Listes_profs_élèves_FMS-FPT_26-27.csv"
    candidates = []
    if base_dir:
        candidates.extend([
            os.path.join(base_dir, standard_name),
            os.path.join(base_dir, "data", standard_name),
        ])
    here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
    candidates.extend([
        os.path.join("data", standard_name),
        os.path.join(".", "data", standard_name),
        os.path.join(here, "..", "data", standard_name),
        os.path.join(here, "data", standard_name),
        os.path.join(here, standard_name),
        standard_name,
    ])
    for c in candidates:
        if os.path.exists(c):
            return c
        d = os.path.dirname(c) or "."
        if os.path.exists(d):
            matches = [f for f in glob.glob(os.path.join(d, "Listes_profs*.csv")) if not f.endswith(".bak")]
            if matches:
                return matches[0]

    return os.path.join("data", standard_name)


def parse_date_safe(val: Any) -> Optional[datetime.date]:
    """Parse une date de manière tolérante et sécurisée."""
    if val is None or pd.isna(val):
        return None
    if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
        return val
    if isinstance(val, (datetime.datetime, pd.Timestamp)):
        return val.date()
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("nan", "none", "nat", ""):
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(val_str, fmt).date()
        except ValueError:
            pass
    try:
        dt = pd.to_datetime(val_str, errors="coerce")
        if pd.notna(dt):
            return dt.date()
    except Exception:
        pass
    return None


def format_date_safe(d: Optional[datetime.date]) -> str:
    """Formate une date en chaîne ISO 'YYYY-MM-DD'."""
    if d is None:
        return ""
    if isinstance(d, (datetime.date, datetime.datetime, pd.Timestamp)):
        return d.strftime("%Y-%m-%d")
    return str(d).strip()


def load_raw_data(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Charge le fichier CSV brut (890 lignes) avec encodages usuels et séparateur ';'.
    """
    path = csv_path or find_csv_file()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Le fichier de données est introuvable : {path}")

    # Lecture avec gestion des encodages usuels
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1", "iso-8859-1"):
        try:
            df = pd.read_csv(
                path,
                sep=";",
                encoding=enc,
                dtype={
                    "CD_ECOLE": str,
                    "NO_ELEVE": str,
                    "CODE_ENSEIGN": str,
                },
            )
            # Nettoyage des noms de colonnes et suppression du BOM éventuel
            df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]

            # En pandas 3.0+, forcer le type object pour colonnes éditables
            colonnes_suivi = [
                "Date de départ en stage",
                "Carnet de stage?",
                "Évaluation mi-stage",
                "Absentéisme",
                "Code_FGJ",
                "Metier_FMS",
                "Commentaires_Stage",
            ]
            for col in colonnes_suivi:
                if col in df.columns:
                    df[col] = df[col].astype(object)
                else:
                    trouve = False
                    for c in df.columns:
                        if col.lower() in c.lower() or c.lower() in col.lower():
                            df[c] = df[c].astype(object)
                            trouve = True
                            break
                    if not trouve:
                        df[col] = ""

            # Nettoyage rigoureux de Code_FGJ (évite la conversion '4522' -> 4522.0)
            if "Code_FGJ" in df.columns:
                df["Code_FGJ"] = df["Code_FGJ"].fillna("").astype(str).str.strip()
                df["Code_FGJ"] = df["Code_FGJ"].str.replace(r"\.0$", "", regex=True)
                df["Code_FGJ"] = df["Code_FGJ"].replace({"nan": "", "None": "", "0": ""})

            if "Metier_FMS" in df.columns:
                df["Metier_FMS"] = df["Metier_FMS"].fillna("").astype(str).str.strip()
                df["Metier_FMS"] = df["Metier_FMS"].replace({"nan": "", "None": "", "0": ""})

            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la lecture du fichier CSV ({enc}) : {e}")

    raise ValueError("Impossible de décoder le fichier CSV avec les encodages supportés.")


def get_student_view(
    df_raw: pd.DataFrame,
    days_fms: int = 60,
    days_fpt: int = 100,
    ref_date: Optional[datetime.date] = None,
    critical_abs_threshold: float = 15.0,
    warning_abs_threshold: float = 8.0,
) -> pd.DataFrame:
    """
    Agrège les 890 lignes de cours brutes en une vue '1 ligne = 1 élève unique' (352 élèves).
    Calcule les indicateurs métiers et feux de circulation.
    """
    if ref_date is None:
        ref_date = datetime.date.today()

    records: List[Dict[str, Any]] = []

    # Regroupement par élève unique
    for no_eleve, group in df_raw.groupby("NO_ELEVE", sort=False):
        # 1. Analyse des cours de stage
        stage_rows = group[group["CD_COURS"].astype(str).isin([str(c) for c in ALL_STAGE_COURSES])]

        if len(stage_rows) > 0:
            main_row = stage_rows.iloc[0]
            # Enseignants associés au(x) cours de stage
            teachers = [
                str(t).strip()
                for t in stage_rows["NOM_ENSEIGN"].dropna().unique()
                if str(t).strip() and str(t).lower() != "nan"
            ]
            enseignant_stage = " / ".join(teachers) if teachers else "Non assigné"

            # Libellé des cours de stage
            courses_labels = []
            for _, r in stage_rows.iterrows():
                titre = r["TITRE_COURS"] if pd.notna(r["TITRE_COURS"]) and str(r["TITRE_COURS"]).strip() else r["Description"]
                courses_labels.append(f"{r['CD_COURS']} - {str(titre).strip()}")
            cours_stage = " | ".join(list(dict.fromkeys(courses_labels)))
            parcours = str(main_row["PARCOURS"]).strip()
            cd_ecole = str(main_row["CD_ECOLE"]).strip()
            a_cours_stage = True
        else:
            main_row = group.iloc[0]
            teachers = [
                str(t).strip()
                for t in group["NOM_ENSEIGN"].dropna().unique()
                if str(t).strip() and str(t).lower() != "nan"
            ]
            enseignant_stage = " / ".join(teachers) if teachers else "Non assigné"
            cours_stage = "Aucun cours de stage attitré"
            parcours = str(main_row["PARCOURS"]).strip()
            cd_ecole = str(main_row["CD_ECOLE"]).strip()
            a_cours_stage = False

        # Si l'élève est inscrit à l'école 236 (Des Sources), c'est son école d'attache
        if "236" in group["CD_ECOLE"].astype(str).values:
            cd_ecole = "236"

        nom_ecole = format_school_display(cd_ecole)

        # Liste de toutes les écoles et de tous les enseignants associés à l'élève
        all_schools = [str(e).strip() for e in group["CD_ECOLE"].dropna().unique() if str(e).strip()]
        all_teachers = [str(t).strip() for t in group["NOM_ENSEIGN"].dropna().unique() if str(t).strip()]

        # Récupération des cours détaillés de l'élève pour le drill-down
        cours_details = []
        for _, r in group.iterrows():
            titre = r["TITRE_COURS"] if pd.notna(r["TITRE_COURS"]) and str(r["TITRE_COURS"]).strip() else ""
            desc = r["Description"] if pd.notna(r["Description"]) else ""
            fonc = r["FONCTION"] if pd.notna(r["FONCTION"]) else ""
            ens = r["NOM_ENSEIGN"] if pd.notna(r["NOM_ENSEIGN"]) else ""
            cours_details.append({
                "CD_COURS": str(r["CD_COURS"]).strip(),
                "TITRE_COURS": titre,
                "Description": desc,
                "FONCTION": fonc,
                "NOM_ENSEIGN": ens,
                "CD_ECOLE": str(r["CD_ECOLE"]).strip(),
                "NOM_ECOLE": format_school_display(r["CD_ECOLE"]),
            })

        # 2. Champs de suivi opérationnel éditables
        # Date de départ en stage
        col_date = "Date de départ en stage"
        date_series = group[col_date].dropna() if col_date in group.columns else pd.Series()
        raw_date_val = date_series.iloc[0] if len(date_series) > 0 and pd.notna(date_series.iloc[0]) else None
        date_depart = parse_date_safe(raw_date_val)

        # Carnet de stage
        col_carnet = "Carnet de stage?"
        carnet_series = group[col_carnet].dropna() if col_carnet in group.columns else pd.Series()
        carnet_val = str(carnet_series.iloc[0]).strip() if len(carnet_series) > 0 and pd.notna(carnet_series.iloc[0]) else "Pas distribué"
        if carnet_val not in OPTIONS_CARNET:
            carnet_val = "Pas distribué"

        # Évaluation mi-stage
        col_mi = "Évaluation mi-stage"
        if col_mi not in group.columns:
            possible_mi = [c for c in group.columns if "valuation" in c.lower() or "mi-stage" in c.lower()]
            col_mi = possible_mi[0] if possible_mi else col_mi

        mi_series = group[col_mi].dropna() if col_mi in group.columns else pd.Series()
        mi_stage_val = str(mi_series.iloc[0]).strip() if len(mi_series) > 0 and pd.notna(mi_series.iloc[0]) else "Non réalisée"
        if mi_stage_val not in OPTIONS_MI_STAGE and mi_stage_val not in ("", "nan", "None"):
            if "compl" in mi_stage_val.lower() or "fait" in mi_stage_val.lower() or "oui" in mi_stage_val.lower():
                mi_stage_val = "Complétée"
            elif "cours" in mi_stage_val.lower():
                mi_stage_val = "En cours"
            elif mi_stage_val in ("", "nan", "None"):
                mi_stage_val = "Non réalisée"

        # Jours d'absence
        col_abs = "Absentéisme"
        if col_abs not in group.columns:
            possible_abs = [c for c in group.columns if "absent" in c.lower() or "absence" in c.lower()]
            col_abs = possible_abs[0] if possible_abs else col_abs

        abs_series = group[col_abs].dropna() if col_abs in group.columns else pd.Series()
        try:
            jours_absence = int(float(abs_series.iloc[0])) if len(abs_series) > 0 and pd.notna(abs_series.iloc[0]) else 0
        except (ValueError, TypeError):
            jours_absence = 0
        if jours_absence < 0:
            jours_absence = 0

        # Métier semi-spécialisé (FMS) et Code FGJ
        col_fgj = "Code_FGJ"
        col_metier = "Metier_FMS"

        fgj_series = group[col_fgj].dropna() if col_fgj in group.columns else pd.Series()
        raw_fgj = str(fgj_series.iloc[0]).strip() if len(fgj_series) > 0 and pd.notna(fgj_series.iloc[0]) else ""
        if raw_fgj.endswith(".0"):
            raw_fgj = raw_fgj[:-2]
        if raw_fgj.lower() in ("nan", "none", "0"):
            raw_fgj = ""

        metier_series = group[col_metier].dropna() if col_metier in group.columns else pd.Series()
        raw_metier = str(metier_series.iloc[0]).strip() if len(metier_series) > 0 and pd.notna(metier_series.iloc[0]) else ""
        if raw_metier.lower() in ("nan", "none", "0"):
            raw_metier = ""

        rms_lookup = get_rms_lookup()
        by_label = rms_lookup.get("by_label", {})
        by_code = rms_lookup.get("by_code", {})

        code_fgj = ""
        metier_fms = ""
        secteur_rms = ""

        if raw_metier in by_label:
            code_fgj = by_label[raw_metier]["Code_FGJ"]
            metier_fms = raw_metier
            secteur_rms = by_label[raw_metier]["Secteur"]
        elif raw_fgj in by_code:
            code_fgj = raw_fgj
            metier_fms = by_code[raw_fgj]["METIER_LABEL"]
            secteur_rms = by_code[raw_fgj]["Secteur"]
        elif raw_metier:
            found = False
            for lbl, info in by_label.items():
                if info["Code_FGJ"] == raw_fgj or info["Metier"].lower() == raw_metier.lower():
                    code_fgj = info["Code_FGJ"]
                    metier_fms = lbl
                    secteur_rms = info["Secteur"]
                    found = True
                    break
            if not found:
                metier_fms = raw_metier
                code_fgj = raw_fgj
        elif raw_fgj:
            code_fgj = raw_fgj

        col_comm = "Commentaires_Stage"
        comm_series = group[col_comm].dropna() if col_comm in group.columns else pd.Series()
        comm_val = str(comm_series.iloc[0]).strip() if len(comm_series) > 0 and pd.notna(comm_series.iloc[0]) else ""
        if comm_val.lower() in ("nan", "none"):
            comm_val = ""

        if parcours == "FPT" and not metier_fms:
            secteur_rms = "Non applicable (FPT)"

        # 3. Calculs des alertes et feux de circulation
        # --- Alerte Évaluation mi-stage ---
        if date_depart is None:
            alerte_mi_stage = "⚪ En attente de départ"
            statut_mi_code = "ATTENTE"
            jours_ecoules = 0
            semaines_ecoulees = 0.0
        elif date_depart > ref_date:
            diff_days = (date_depart - ref_date).days
            alerte_mi_stage = f"⚪ Départ prévu dans {diff_days} j."
            statut_mi_code = "FUTUR"
            jours_ecoules = -diff_days
            semaines_ecoulees = jours_ecoules / 7.0
        elif mi_stage_val == "Complétée":
            alerte_mi_stage = "🟢 Réalisée"
            statut_mi_code = "REALISEE"
            jours_ecoules = (ref_date - date_depart).days
            semaines_ecoulees = round(jours_ecoules / 7.0, 1)
        else:
            jours_ecoules = (ref_date - date_depart).days
            semaines_ecoulees = round(jours_ecoules / 7.0, 1)

            # Règle selon le parcours
            if parcours == "FMS":
                seuil_critique = 12.0  # semaines
                seuil_vigilance = 10.0
                if semaines_ecoulees > seuil_critique:
                    alerte_mi_stage = f"🔴 En retard (> 12 sem. : {semaines_ecoulees:.1f} sem.)"
                    statut_mi_code = "RETARD"
                elif semaines_ecoulees >= seuil_vigilance:
                    alerte_mi_stage = f"🟡 À planifier sous peu ({semaines_ecoulees:.1f} sem.)"
                    statut_mi_code = "A_PLANIFIER"
                else:
                    alerte_mi_stage = f"🟢 Dans les délais ({semaines_ecoulees:.1f} sem.)"
                    statut_mi_code = "DANS_DELAIS"
            else:
                # FPT / FPT3
                seuil_critique = 20.0  # semaines
                seuil_vigilance = 17.0
                if semaines_ecoulees > seuil_critique:
                    alerte_mi_stage = f"🔴 En retard (> 20 sem. : {semaines_ecoulees:.1f} sem.)"
                    statut_mi_code = "RETARD"
                elif semaines_ecoulees >= seuil_vigilance:
                    alerte_mi_stage = f"🟡 À planifier sous peu ({semaines_ecoulees:.1f} sem.)"
                    statut_mi_code = "A_PLANIFIER"
                else:
                    alerte_mi_stage = f"🟢 Dans les délais ({semaines_ecoulees:.1f} sem.)"
                    statut_mi_code = "DANS_DELAIS"

        # --- Alerte Absentéisme ---
        jours_prevus = days_fms if parcours == "FMS" else days_fpt
        if jours_prevus <= 0:
            jours_prevus = 60
        taux_absence = round((jours_absence / float(jours_prevus)) * 100.0, 1)

        if taux_absence > critical_abs_threshold:
            statut_absenteisme = f"🔴 Critique ({taux_absence:.1f} % - {jours_absence} j.)"
            statut_abs_code = "CRITIQUE"
        elif taux_absence >= warning_abs_threshold:
            statut_absenteisme = f"🟡 Vigilance ({taux_absence:.1f} % - {jours_absence} j.)"
            statut_abs_code = "VIGILANCE"
        else:
            statut_absenteisme = f"🟢 Normal ({taux_absence:.1f} % - {jours_absence} j.)"
            statut_abs_code = "NORMAL"

        # --- Statut Carnet ---
        badge_carnet_map = {
            "Validé": "🟢 Validé",
            "Complété": "🔵 Complété",
            "En cours": "🟡 En cours",
            "Pas distribué": "🔴 Pas distribué",
        }
        statut_carnet = badge_carnet_map.get(carnet_val, "🔴 Pas distribué")

        # Statut stage actif
        en_stage_actif = (date_depart is not None and date_depart <= ref_date)

        records.append({
            "NO_ELEVE": str(no_eleve).strip(),
            "CD_ECOLE": cd_ecole,
            "NOM_ECOLE": nom_ecole,
            "PARCOURS": parcours,
            "ENSEIGNANT_STAGE": enseignant_stage,
            "COURS_STAGE": cours_stage,
            "A_COURS_STAGE": a_cours_stage,
            "Date de départ en stage": date_depart,
            "Carnet de stage?": carnet_val,
            "Statut Carnet": statut_carnet,
            "Évaluation mi-stage": mi_stage_val,
            "Alerte Évaluation": alerte_mi_stage,
            "STATUT_MI_CODE": statut_mi_code,
            "Jours d'absence": int(jours_absence),
            "Taux d'absence (%)": taux_absence,
            "Statut Absentéisme": statut_absenteisme,
            "STATUT_ABS_CODE": statut_abs_code,
            "Code_FGJ": code_fgj,
            "Metier_FMS": metier_fms,
            "Secteur_RMS": secteur_rms,
            "JOURS_ECOULES": jours_ecoules,
            "SEMAINES_ECOULEES": semaines_ecoulees,
            "EN_STAGE_ACTIF": en_stage_actif,
            "LISTE_ECOLES": all_schools,
            "LISTE_ENSEIGNANTS": all_teachers,
            "COURS_DETAILS": cours_details,
            "Commentaires_Stage": comm_val,
        })

    df_result = pd.DataFrame(records)
    if not df_result.empty and "NO_ELEVE" in df_result.columns:
        df_result = df_result.sort_values("NO_ELEVE", ignore_index=True)
    return df_result


def save_student_data(
    df_edited: pd.DataFrame,
    csv_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Enregistre les modifications de manière synchrone dans le système de fichiers virtuel (MEMFS) de Stlite/Pyodide.
    - Met à jour les champs opérationnels sur toutes les lignes de l'élève (vue 890 lignes).
    - Maintient une copie de sauvegarde horodatée (.bak) en mémoire virtuelle.
    - Écriture atomique et fiable sans verrouillage système (environnement WebAssembly mono-thread).
    """
    path = csv_path or find_csv_file()
    base_dir = os.path.dirname(os.path.abspath(path)) if os.path.isabs(path) else os.path.dirname(path)
    if not base_dir:
        base_dir = "data"
    os.makedirs(base_dir, exist_ok=True)

    backup_dir = os.path.join(base_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    direct_bak = f"{path}.bak"
    dated_bak = os.path.join(backup_dir, f"{os.path.basename(path)}_{timestamp}.bak")

    # 1. Sauvegarde préventive (.bak) si le fichier existe
    if os.path.exists(path):
        try:
            shutil.copy2(path, direct_bak)
            shutil.copy2(path, dated_bak)
        except Exception:
            pass

    # 2. Chargement du DataFrame brut pour mettre à jour toutes les lignes élèves
    try:
        df_raw = load_raw_data(path)
    except Exception as e:
        return False, f"Impossible de charger le fichier d'origine : {e}"

    # Identifier les colonnes cibles dans le brut
    col_date = "Date de départ en stage"
    col_carnet = "Carnet de stage?"
    col_mi = "Évaluation mi-stage"
    col_abs = "Absentéisme"
    col_fgj = "Code_FGJ"
    col_metier = "Metier_FMS"
    col_comm = "Commentaires_Stage"

    for col in (col_fgj, col_metier, col_comm):
        if col not in df_raw.columns:
            df_raw[col] = ""

    # Dictionnaire rapide des modifications par NO_ELEVE
    rms_lookup = get_rms_lookup()
    by_label = rms_lookup.get("by_label", {})
    edit_dict = {}
    for _, row in df_edited.iterrows():
        no_eleve = str(row["NO_ELEVE"]).strip()
        d_val = format_date_safe(row.get("Date de départ en stage"))
        c_val = str(row.get("Carnet de stage?", "Pas distribué")).strip()
        m_val = str(row.get("Évaluation mi-stage", "Non réalisée")).strip()
        a_val = row.get("Jours d'absence", 0)
        try:
            a_int = int(a_val) if pd.notna(a_val) else 0
        except (ValueError, TypeError):
            a_int = 0

        # Extraction Code_FGJ et Metier_FMS
        m_fms_val = str(row.get("Metier_FMS", "")).strip()
        if m_fms_val in ("nan", "None", "0"):
            m_fms_val = ""

        fgj_val = str(row.get("Code_FGJ", "")).strip()
        if fgj_val in ("nan", "None", "0"):
            fgj_val = ""

        if not m_fms_val:
            fgj_val = ""
        elif " - " in m_fms_val:
            cand = m_fms_val.split(" - ")[0].strip()
            if cand.isdigit():
                fgj_val = cand
        elif m_fms_val in by_label:
            fgj_val = by_label[m_fms_val]["Code_FGJ"]

        comm_val = str(row.get("Commentaires_Stage", "")).strip() if pd.notna(row.get("Commentaires_Stage")) else ""
        if comm_val.lower() in ("nan", "none"):
            comm_val = ""

        edit_dict[no_eleve] = {
            "date": d_val,
            "carnet": c_val,
            "mi_stage": m_val,
            "absence": a_int if a_int > 0 else "",
            "code_fgj": fgj_val,
            "metier_fms": m_fms_val,
            "commentaires": comm_val,
        }

    # 3. Synchronisation multi-lignes dans df_raw
    for no_eleve, vals in edit_dict.items():
        mask = df_raw["NO_ELEVE"].astype(str) == str(no_eleve)
        if mask.any():
            df_raw.loc[mask, col_date] = vals["date"]
            df_raw.loc[mask, col_carnet] = vals["carnet"]
            df_raw.loc[mask, col_mi] = vals["mi_stage"]
            df_raw.loc[mask, col_abs] = vals["absence"]
            df_raw.loc[mask, col_fgj] = vals["code_fgj"]
            df_raw.loc[mask, col_metier] = vals["metier_fms"]
            df_raw.loc[mask, col_comm] = vals["commentaires"]

    # 4. Écriture dans le système de fichiers virtuel (MEMFS)
    temp_file = os.path.join(base_dir, f".tmp_save_{timestamp}.csv")
    try:
        df_raw.to_csv(
            temp_file,
            sep=";",
            encoding="utf-8-sig",
            index=False,
            na_rep="",
            lineterminator="\r\n",
        )
        if os.path.exists(path):
            os.replace(temp_file, path)
        else:
            shutil.move(temp_file, path)
    except Exception:
        # Fallback écriture directe
        try:
            df_raw.to_csv(
                path,
                sep=";",
                encoding="utf-8-sig",
                index=False,
                na_rep="",
                lineterminator="\r\n",
            )
        except Exception as e2:
            return False, f"Erreur d'écriture dans le système de fichiers virtuel : {e2}"

    # 5. Synchronisation automatique avec le stockage local du portable (localStorage)
    try:
        import js
        csv_bytes = get_latest_csv_bytes(path)
        csv_str = csv_bytes.decode("utf-8-sig", errors="ignore")
        if hasattr(js, "window") and hasattr(js.window, "pfaeSaveToLaptopStorage"):
            js.window.pfaeSaveToLaptopStorage(csv_str)
        elif hasattr(js, "localStorage"):
            js.localStorage.setItem("pfae_stages_saved_csv", csv_str)
            js.localStorage.setItem("pfae_stages_last_save", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except Exception:
        pass

    return True, f"Modifications enregistrées avec succès en mémoire locale et virtuelle ({len(edit_dict)} élève(s) mis à jour)."


def get_latest_csv_bytes(csv_path: Optional[str] = None) -> bytes:
    """
    Retourne le contenu binaire du fichier CSV maître actualisé pour téléchargement direct.
    """
    path = csv_path or find_csv_file()
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    df_raw = load_raw_data(path)
    return export_dataframe_to_csv(df_raw)


def export_dataframe_to_excel(df: pd.DataFrame) -> bytes:
    """Génère un fichier Excel stylisé en mémoire (bytes)."""
    output = io.BytesIO()
    cols_to_exclude = ["LISTE_ECOLES", "LISTE_ENSEIGNANTS", "COURS_DETAILS", "STATUT_MI_CODE", "STATUT_ABS_CODE", "EN_STAGE_ACTIF", "A_COURS_STAGE"]
    export_cols = [c for c in df.columns if c not in cols_to_exclude]
    df_clean = df[export_cols].copy()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_clean.to_excel(writer, sheet_name="Suivi_Stages_PFAE", index=False)

    return output.getvalue()


def export_dataframe_to_csv(df: pd.DataFrame) -> bytes:
    """Génère un CSV encodé en UTF-8 avec BOM pour une compatibilité parfaite avec Excel francophone."""
    cols_to_exclude = ["LISTE_ECOLES", "LISTE_ENSEIGNANTS", "COURS_DETAILS", "STATUT_MI_CODE", "STATUT_ABS_CODE", "EN_STAGE_ACTIF", "A_COURS_STAGE"]
    export_cols = [c for c in df.columns if c not in cols_to_exclude]
    df_clean = df[export_cols].copy()
    csv_str = df_clean.to_csv(sep=";", index=False, encoding="utf-8-sig")
    return csv_str.encode("utf-8-sig")


def get_teacher_summary(df_student_view: pd.DataFrame) -> pd.DataFrame:
    """
    Génère la grille de synthèse par enseignant (enseignant-*).
    Calcule pour chaque enseignant :
    - Nombre total d'élèves assignés
    - Répartition FMS / FPT
    - Nombre d'élèves en stage actif
    - Carnets validés / en cours / pas distribués
    - Évaluations mi-stage à jour / en retard
    - Absentéisme moyen
    """
    all_teachers_set = set()
    for profs in df_student_view["LISTE_ENSEIGNANTS"]:
        for p in profs:
            if p and str(p).strip() and str(p).lower() != "nan":
                all_teachers_set.add(str(p).strip())

    teachers_list = sorted(list(all_teachers_set))
    rows = []
    for prof in teachers_list:
        sub = df_student_view[df_student_view["LISTE_ENSEIGNANTS"].apply(lambda pl: prof in pl)]
        total = len(sub)
        nb_fms = int((sub["PARCOURS"] == "FMS").sum())
        nb_fpt = int((sub["PARCOURS"] == "FPT").sum())
        nb_actif = int(sub["EN_STAGE_ACTIF"].sum())
        nb_carnet_ok = int((sub["Carnet de stage?"] == "Validé").sum())
        nb_carnet_cours = int((sub["Carnet de stage?"] == "En cours").sum())
        nb_eval_ok = int((sub["STATUT_MI_CODE"] == "REALISEE").sum())
        nb_eval_retard = int((sub["STATUT_MI_CODE"] == "RETARD").sum())
        nb_abs_crit = int((sub["STATUT_ABS_CODE"] == "CRITIQUE").sum())
        avg_abs = round(float(sub["Jours d'absence"].mean()), 1) if total > 0 else 0.0

        # Établissement(s)
        ecoles = sorted(list(set(sub["NOM_ECOLE"].unique())))
        ecoles_str = ", ".join(ecoles) if ecoles else "Non spécifié"

        rows.append({
            "Enseignant": prof,
            "Établissement(s)": ecoles_str,
            "Total Élèves": total,
            "Élèves FMS": nb_fms,
            "Élèves FPT": nb_fpt,
            "En Stage Actif": nb_actif,
            "Carnets Validés": nb_carnet_ok,
            "Carnets En Cours": nb_carnet_cours,
            "Éval. Réalisées": nb_eval_ok,
            "Éval. en Retard": nb_eval_retard,
            "Abs. Critique (>15%)": nb_abs_crit,
            "Moy. Abs. (j)": avg_abs,
        })
    df_profs = pd.DataFrame(rows)
    if not df_profs.empty:
        df_profs = df_profs.sort_values("Enseignant", ignore_index=True)
    return df_profs


def add_new_student(
    student_id: str,
    school_code: str,
    parcours: str,
    teacher_name: str,
    course_code: str,
    course_title: str = "",
    csv_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """Ajoute manuellement une nouvelle fiche élève au fichier maître."""
    path = csv_path or find_csv_file()
    try:
        df_raw = load_raw_data(path)
    except Exception as e:
        return False, f"Erreur lors du chargement : {e}"

    # Vérification d'unicité
    if student_id in df_raw["NO_ELEVE"].astype(str).values:
        return False, f"L'élève '{student_id}' existe déjà dans le fichier."

    teacher_code = "ENS-00"
    if "-" in teacher_name:
        try:
            num = teacher_name.split("-")[1].strip()
            teacher_code = f"ENS-{num}"
        except Exception:
            pass

    new_row = {
        "CD_ECOLE": str(school_code).strip(),
        "Description": f"{course_title} {course_code}".strip(),
        "NO_ELEVE": str(student_id).strip(),
        "CODE_ENSEIGN": teacher_code,
        "NOM_ENSEIGN": str(teacher_name).strip(),
        "PARCOURS": str(parcours).strip(),
        "CD_COURS": str(course_code).strip(),
        "TITRE_COURS": str(course_title).strip(),
        "FONCTION": "Stage" if "stage" in str(course_title).lower() or str(course_code) in ["196204", "108234", "108230"] else "",
        "Date de départ en stage": "",
        "Carnet de stage?": "Pas distribué",
        "Évaluation mi-stage": "Non réalisée",
        "Absentéisme": "",
        "Code_FGJ": "",
        "Metier_FMS": "",
        "Commentaires_Stage": "",
    }
    df_raw = pd.concat([df_raw, pd.DataFrame([new_row])], ignore_index=True)

    try:
        df_raw.to_csv(path, sep=";", encoding="utf-8-sig", index=False, na_rep="", lineterminator="\r\n")
    except Exception as e:
        return False, f"Erreur d'écriture : {e}"

    # Synchronisation avec le stockage local
    try:
        import js
        csv_bytes = get_latest_csv_bytes(path)
        csv_str = csv_bytes.decode("utf-8-sig", errors="ignore")
        if hasattr(js, "window") and hasattr(js.window, "pfaeSaveToLaptopStorage"):
            js.window.pfaeSaveToLaptopStorage(csv_str)
        elif hasattr(js, "localStorage"):
            js.localStorage.setItem("pfae_stages_saved_csv", csv_str)
            js.localStorage.setItem("pfae_stages_last_save", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except Exception:
        pass

    return True, f"Fiche élève '{student_id}' créée avec succès !"

