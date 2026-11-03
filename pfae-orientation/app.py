"""
=============================================================================
AIDE AU DISCERNEMENT CLINIQUE ET ÉTHIQUE — ORIENTATION PFAE & PRÉ-DEP
Centre de services scolaire Marguerite-Bourgeoys (CSSMB)
Garde-fou réglementaire du Régime pédagogique (LIP art. 23 et 23.3, 1°)
Bottin officiel des directions 2025-2026 & Matrice territoriale
=============================================================================
Application Streamlit 100% compatible stlite (Pyodide) et exécution locale.
"""

import streamlit as st
import datetime
import html
import json
import textwrap

def render_html(content: str):
    """Affiche du code HTML sans interférence du parseur Markdown (évite les blocs pre/code)."""
    clean = textwrap.dedent(content).strip()
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE & STYLES CSS
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Discernement PFAE & Pré-DEP | CSSMB",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
/* Style global et typographie */
@import url('https://fonts.googleapis.com/css2?family=Public+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Public Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* En-tête institutionnel */
.cssmb-header {
    background: linear-gradient(135deg, #0d3b66 0%, #001e3d 100%);
    color: white;
    padding: 1.6rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 14px rgba(13, 59, 102, 0.18);
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-left: 6px solid #f4a261;
}

.cssmb-header h1 {
    font-size: 1.75rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.02em;
    color: #ffffff;
}

.cssmb-header p {
    margin: 0.35rem 0 0 0;
    font-size: 0.95rem;
    color: #e0e7ee;
    font-weight: 400;
}

.cssmb-header .badge-legal {
    background: rgba(244, 162, 97, 0.2);
    border: 1px solid #f4a261;
    color: #f4a261;
    padding: 0.35rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    white-space: nowrap;
}

/* Cartes et conteneurs */
.clinical-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}

.card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0d3b66;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Badges d'impact territorial */
.badge-impact {
    display: inline-block;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.impact-none {
    background: #e6f7ec;
    color: #0d6832;
    border: 1px solid #a3e0b5;
}

.impact-pole {
    background: #e6f0fa;
    color: #0d4a8f;
    border: 1px solid #99c2ec;
}

.impact-specialized {
    background: #fbf0ea;
    color: #a44212;
    border: 1px solid #f5be9e;
}

/* Fiche synthèse imprimable */
@media print {
    body * {
        visibility: hidden !important;
    }
    #print-section, #print-section * {
        visibility: visible !important;
    }
    #print-section {
        position: absolute !important;
        left: 0 !important;
        top: 0 !important;
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
        background: white !important;
        color: black !important;
    }
    .no-print {
        display: none !important;
    }
}

.print-sheet {
    background: #ffffff;
    border: 2px solid #0d3b66;
    border-radius: 8px;
    padding: 2.5rem;
    color: #1a202c;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    margin: 1.5rem 0;
}

.print-header {
    border-bottom: 3px double #0d3b66;
    padding-bottom: 1.25rem;
    margin-bottom: 1.5rem;
}

.print-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
    margin-bottom: 1.25rem;
}

.print-box {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 0.85rem 1.1rem;
    background: #f8fafc;
}

.print-box h4 {
    margin: 0 0 0.5rem 0;
    font-size: 0.85rem;
    text-transform: uppercase;
    color: #475569;
    letter-spacing: 0.05em;
    font-weight: 700;
}

.print-signature-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid #cbd5e1;
}

.signature-box {
    border: 1px dashed #94a3b8;
    height: 95px;
    border-radius: 6px;
    padding: 0.5rem;
    font-size: 0.75rem;
    color: #64748b;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. BASES DE DONNÉES CSSMB : MATRICE TERRITORIALE ET BOTTIN 2025-2026
# ---------------------------------------------------------------------------

BOTTIN_DIRECTIONS = {
    "138-Cavelier-De LaSalle": {
        "ville": "LaSalle",
        "telephone": "514 855-4190",
        "contacts": [
            {"role": "Direction adjointe FPT", "nom": "Manuela Bugariu"},
            {"role": "Direction adjointe FMS / Pré-DEP", "nom": "Marjorie Côté"}
        ],
        "pole": "Sud",
        "programmes": ["FPT", "FMS", "Pré-DEP"],
        "clienteles": ["Régulier", "TSA (soutien)", "Troubles du langage (soutien)"]
    },
    "139-Dalbé-Viau": {
        "ville": "Lachine",
        "telephone": "514 855-4200",
        "contacts": [
            {"role": "Direction FMS / Pré-DEP / FPT", "nom": "Gabrielle Roy-Béliveau"}
        ],
        "pole": "Sud",
        "programmes": ["FPT", "Pré-DEP"],
        "clienteles": ["Régulier"]
    },
    "241-Dorval-Jean-XXIII": {
        "ville": "Dorval",
        "telephone": "514 855-4210",
        "contacts": [
            {"role": "Direction adjointe FPT", "nom": "Simplice Lambert"}
        ],
        "pole": "Sud",
        "programmes": ["FPT"],
        "clienteles": ["Régulier", "Ateliers FPT"]
    },
    "142-Monseigneur-Richard": {
        "ville": "Verdun",
        "telephone": "514 855-4220",
        "contacts": [
            {"role": "Direction de secteur FMS / Pré-DEP", "nom": "Stéphany-Pascale Gauthier / Anouk Bilodeau"}
        ],
        "pole": "Sud",
        "programmes": ["FMS", "Pré-DEP"],
        "clienteles": ["Régulier"]
    },
    "236-Des Sources": {
        "ville": "Dollard-des-Ormeaux",
        "telephone": "514 855-4230",
        "contacts": [
            {"role": "Direction adjointe FMS / Pré-DEP", "nom": "Nathalie Dubois / Valérie Gagnon"}
        ],
        "pole": "Ouest",
        "programmes": ["FMS", "Pré-DEP"],
        "clienteles": ["Régulier"]
    },
    "238-Rose-Virginie-Pelletier": {
        "ville": "Pierrefonds",
        "telephone": "514 855-4240",
        "contacts": [
            {"role": "Direction FPT / FMS / Pré-DEP", "nom": "Mireille Laliberté / Elsa Drouin"}
        ],
        "pole": "Ouest",
        "programmes": ["FPT", "FMS", "Pré-DEP"],
        "clienteles": ["Régulier", "Adaptation"]
    },
    "245-De l'Altitude": {
        "ville": "Pierrefonds",
        "telephone": "514 855-4250",
        "contacts": [
            {"role": "Direction de point de service FPT", "nom": "Nathalie Krumhorn"}
        ],
        "pole": "Ouest",
        "programmes": ["FPT"],
        "clienteles": ["Régulier", "FPT polyvalent"]
    },
    "037-SAS Outremont": {
        "ville": "Outremont",
        "telephone": "514 855-4260",
        "contacts": [
            {"role": "Direction (Groupes réguliers, TSA, Langage)", "nom": "José Bélanger"}
        ],
        "pole": "Centre / Est",
        "programmes": ["FPT", "FMS", "Pré-DEP"],
        "clienteles": ["Régulier adapté", "TSA (intensif)", "Troubles du langage (intensif)"],
        "is_hub_specialise": True
    }
}

ECOLES_ORIGINE_CSSMB = {
    # Pôle Centre / Est
    "037-SAS Outremont": {"pole": "Centre / Est", "ville": "Outremont", "point_service": True},
    "038-de la Traversée": {"pole": "Centre / Est", "ville": "Mont-Royal", "point_service": False},
    "040-Paul-Gérin-Lajoie-d'Outremont": {"pole": "Centre / Est", "ville": "Outremont", "point_service": False},
    "041-Saint-Laurent": {"pole": "Centre / Est", "ville": "Saint-Laurent", "point_service": False},
    "042-Pierre-Laporte": {"pole": "Centre / Est", "ville": "Mont-Royal", "point_service": False},

    # Pôle Sud
    "136-Collège Saint-Louis": {"pole": "Sud", "ville": "Lachine", "point_service": False},
    "138-Cavelier-De LaSalle": {"pole": "Sud", "ville": "LaSalle", "point_service": True},
    "139-Dalbé-Viau": {"pole": "Sud", "ville": "Lachine", "point_service": True},
    "142-Monseigneur-Richard": {"pole": "Sud", "ville": "Verdun", "point_service": True},
    "144-Caroline-Dawson": {"pole": "Sud", "ville": "Verdun", "point_service": False},
    "241-Dorval-Jean-XXIII": {"pole": "Sud", "ville": "Dorval", "point_service": True},

    # Pôle Ouest
    "236-Des Sources": {"pole": "Ouest", "ville": "Dollard-des-Ormeaux", "point_service": True},
    "238-Rose-Virginie-Pelletier": {"pole": "Ouest", "ville": "Pierrefonds", "point_service": True},
    "240-Félix-Leclerc": {"pole": "Ouest", "ville": "Pointe-Claire", "point_service": False},
    "243-Saint-Georges": {"pole": "Ouest", "ville": "Senneville", "point_service": False},
    "245-De l'Altitude": {"pole": "Ouest", "ville": "Pierrefonds", "point_service": True},
}

# ---------------------------------------------------------------------------
# 3. PROFILS TYPES CLINIQUES (DÉMO RAPIDE)
# ---------------------------------------------------------------------------

PROFILS_DEMO = {
    "cas_1_predep": {
        "titre": "Cas 1 • Pré-DEP : Alexandre (15 ans, Dalbé-Viau)",
        "desc": "Sec. 2 réussi en français et anglais. Vise un DEP en mécanique/carrosserie. Consentements élève et parents validés.",
        "data": {
            "code_eleve": "ELE-ALEX-01",
            "ecole_origine": "139-Dalbé-Viau",
            "date_naissance": datetime.date(2010, 4, 15),
            "profil_particulier": "Régulier / Difficultés courantes",
            "sec2_francais": True,
            "sec2_math": False,
            "sec2_anglais": True,
            "primaire_maitrise": "Atteints (Français et Mathématiques)",
            "secteur_vise": "Mécanique, entretien et conduite d'engins",
            "preference_pedago": "Atelier pratique & manipulation concrète",
            "motivation_stage": "Très forte et confirmée (veut un DEP)",
            "fatigue_cognitive": "Faible / Normale",
            "adaptations_efficacite": "Efficaces avec progrès notables",
            "apprentissage_contextualise": "Indispensable pour donner du sens",
            "autonomie_stm": "Autonome (prend le bus seul sans difficulté)",
            "maturite_adultes": "Mature et respectueuse",
            "endurance_physique": "Excellente (capable d'un quart complet)",
            "consentement_eleve": "Accord documenté et enthousiaste",
            "accord_parents": "Favorable (Accord documenté)"
        }
    },
    "cas_2_fms": {
        "titre": "Cas 2 • FMS : Sara (15 ans, Félix-Leclerc)",
        "desc": "Objectifs du primaire validés, échec des matières de Sec. 2. Très motivée par un stage en entreprise (375h).",
        "data": {
            "code_eleve": "ELE-SARA-02",
            "ecole_origine": "240-Félix-Leclerc",
            "date_naissance": datetime.date(2010, 2, 20),
            "profil_particulier": "Régulier / Difficultés courantes",
            "sec2_francais": False,
            "sec2_math": False,
            "sec2_anglais": False,
            "primaire_maitrise": "Atteints (Français et Mathématiques)",
            "secteur_vise": "Commerce, vente et service à la clientèle",
            "preference_pedago": "Atelier pratique & manipulation concrète",
            "motivation_stage": "Très forte et confirmée (veut un DEP)",
            "fatigue_cognitive": "Modérée en fin de journée",
            "adaptations_efficacite": "Partielles / Plafond atteint en classe ordinaire",
            "apprentissage_contextualise": "Indispensable pour donner du sens",
            "autonomie_stm": "En apprentissage (trajets connus)",
            "maturite_adultes": "En développement avec supervision bienveillante",
            "endurance_physique": "Moyenne avec pauses planifiées",
            "consentement_eleve": "Accord documenté et enthousiaste",
            "accord_parents": "Favorable (Accord documenté)"
        }
    },
    "cas_3_fpt_tsa": {
        "titre": "Cas 3 • FPT (Volet TSA) : Liam (15 ans, Saint-Laurent)",
        "desc": "Retard primaire marqué, diagnostic TSA. Nécessite encadrement adapté vers l'autonomie et insertion sociale.",
        "data": {
            "code_eleve": "ELE-LIAM-03",
            "ecole_origine": "041-Saint-Laurent",
            "date_naissance": datetime.date(2010, 6, 10),
            "profil_particulier": "Trouble du spectre de l'autisme (TSA)",
            "sec2_francais": False,
            "sec2_math": False,
            "sec2_anglais": False,
            "primaire_maitrise": "Non atteints en français et/ou mathématiques",
            "secteur_vise": "Exploration générale ouverte / Polyvalent",
            "preference_pedago": "Atelier pratique & manipulation concrète",
            "motivation_stage": "Modérée avec besoin d'encadrement rassurant",
            "fatigue_cognitive": "Sévère / Sensibilité aux surcharges sensorielles",
            "adaptations_efficacite": "Partielles / Plafond atteint en classe ordinaire",
            "apprentissage_contextualise": "Indispensable pour donner du sens",
            "autonomie_stm": "En apprentissage (trajets connus)",
            "maturite_adultes": "En développement avec supervision bienveillante",
            "endurance_physique": "Moyenne avec pauses planifiées",
            "consentement_eleve": "Accord documenté et enthousiaste",
            "accord_parents": "Favorable (Accord documenté)"
        }
    },
    "cas_4_under15": {
        "titre": "Cas 4 • Garde-Fou 1 (< 15 ans) : Maya (14 ans, Collège Saint-Louis)",
        "desc": "Moins de 15 ans au 30 septembre. Inadmissible au PFAE immédiat. Maintien 1er cycle et prospective.",
        "data": {
            "code_eleve": "ELE-MAYA-04",
            "ecole_origine": "136-Collège Saint-Louis",
            "date_naissance": datetime.date(2011, 11, 14),
            "profil_particulier": "Régulier / Difficultés courantes",
            "sec2_francais": False,
            "sec2_math": False,
            "sec2_anglais": False,
            "primaire_maitrise": "Atteints (Français et Mathématiques)",
            "secteur_vise": "Alimentation, cuisine et restauration",
            "preference_pedago": "Atelier pratique & manipulation concrète",
            "motivation_stage": "Très forte et confirmée (veut un DEP)",
            "fatigue_cognitive": "Modérée en fin de journée",
            "adaptations_efficacite": "Partielles / Plafond atteint en classe ordinaire",
            "apprentissage_contextualise": "Indispensable pour donner du sens",
            "autonomie_stm": "Autonome (prend le bus seul sans difficulté)",
            "maturite_adultes": "En développement avec supervision bienveillante",
            "endurance_physique": "Excellente (capable d'un quart complet)",
            "consentement_eleve": "Accord documenté et enthousiaste",
            "accord_parents": "Favorable (Accord documenté)"
        }
    },
    "cas_5_hesitation": {
        "titre": "Cas 5 • Garde-Fou 2 (Hésitation élève) : Jordan (15 ans, Cavelier)",
        "desc": "Élève craintif face au monde adulte et aux stages. Déclenchement du protocole exploratoire préalable.",
        "data": {
            "code_eleve": "ELE-JORDAN-05",
            "ecole_origine": "138-Cavelier-De LaSalle",
            "date_naissance": datetime.date(2010, 1, 12),
            "profil_particulier": "Régulier / Difficultés courantes",
            "sec2_francais": False,
            "sec2_math": False,
            "sec2_anglais": False,
            "primaire_maitrise": "Atteints (Français et Mathématiques)",
            "secteur_vise": "Bâtiment, construction et menuiserie",
            "preference_pedago": "Atelier pratique & manipulation concrète",
            "motivation_stage": "Faible / Anxiété marquée face au travail",
            "fatigue_cognitive": "Modérée en fin de journée",
            "adaptations_efficacite": "Partielles / Plafond atteint en classe ordinaire",
            "apprentissage_contextualise": "Indispensable pour donner du sens",
            "autonomie_stm": "En apprentissage (trajets connus)",
            "maturite_adultes": "Difficile / Vigilance relationnelle",
            "endurance_physique": "Moyenne avec pauses planifiées",
            "consentement_eleve": "Hésitation / Crainte vive de l'élève",
            "accord_parents": "Favorable (Accord documenté)"
        }
    },
    "cas_6_refus_parents": {
        "titre": "Cas 6 • Garde-Fou 3 (Refus parental) : Maxime (15 ans, Mgr-Richard)",
        "desc": "Admissible à la FMS sur le plan académique, mais refus formel des parents. Mesure alternative requise.",
        "data": {
            "code_eleve": "ELE-MAX-06",
            "ecole_origine": "142-Monseigneur-Richard",
            "date_naissance": datetime.date(2009, 12, 5),
            "profil_particulier": "Régulier / Difficultés courantes",
            "sec2_francais": False,
            "sec2_math": False,
            "sec2_anglais": False,
            "primaire_maitrise": "Atteints (Français et Mathématiques)",
            "secteur_vise": "Horticulture, paysagement et espaces verts",
            "preference_pedago": "Atelier pratique & manipulation concrète",
            "motivation_stage": "Très forte et confirmée (veut un DEP)",
            "fatigue_cognitive": "Faible / Normale",
            "adaptations_efficacite": "Inopérantes / Échec persistant",
            "apprentissage_contextualise": "Indispensable pour donner du sens",
            "autonomie_stm": "Autonome (prend le bus seul sans difficulté)",
            "maturite_adultes": "Mature et respectueuse",
            "endurance_physique": "Excellente (capable d'un quart complet)",
            "consentement_eleve": "Accord documenté et enthousiaste",
            "accord_parents": "Refus formel des parents"
        }
    }
}

# ---------------------------------------------------------------------------
# 4. FONCTIONS MÉTIER ET CALCULS RÉGLEMENTAIRES
# ---------------------------------------------------------------------------

def calculer_age_au_30_septembre(date_naissance: datetime.date, annee_cible: int) -> int:
    """Calcule l'âge exact de l'élève au 30 septembre de l'année scolaire de classement."""
    pivot = datetime.date(annee_cible, 9, 30)
    age = pivot.year - date_naissance.year
    if (pivot.month, pivot.day) < (date_naissance.month, date_naissance.day):
        age -= 1
    return age


def determiner_affectation_territoriale(
    ecole_origine: str,
    programme_code: str,
    profil_particulier: str
) -> dict:
    """
    Détermine l'établissement recommandé en minimisant l'impact d'extraction
    selon la matrice territoriale et les besoins spécifiques du CSSMB.
    """
    info_origine = ECOLES_ORIGINE_CSSMB.get(ecole_origine, {"pole": "Sud", "ville": "CSSMB", "point_service": False})
    pole_origine = info_origine["pole"]

    # Profil TSA ou Trouble primaire du langage lourd -> Pôle d'expertise spécialisé
    if "TSA" in profil_particulier or "langage" in profil_particulier.lower():
        # SAS Outremont est le centre d'expertise CSSMB dédié
        ecole_specialisee = "037-SAS Outremont"
        data_ecole = BOTTIN_DIRECTIONS[ecole_specialisee]
        
        # Si l'élève est déjà au Pôle Sud, Cavelier-De LaSalle offre aussi un volet de soutien
        autre_option = None
        if pole_origine == "Sud":
            autre_option = {
                "nom": "138-Cavelier-De LaSalle",
                "details": BOTTIN_DIRECTIONS["138-Cavelier-De LaSalle"],
                "note": "Point de service du Pôle Sud offrant un volet de soutien adapté pour élèves à besoins particuliers."
            }

        return {
            "niveau_impact": "specialized",
            "badge_texte": "🟣 Pôle d'expertise spécialisé CSSMB (Besoins particuliers)",
            "explication": (
                f"En raison du profil spécifique ({profil_particulier}), l'affectation privilégie un environnement "
                "adapté disposant de ratios réduits, d'intervenants spécialisés et de plateaux adaptés."
            ),
            "etablissement_principal": {
                "nom": ecole_specialisee,
                "details": data_ecole,
                "raison": "Centre d'expertise spécialisé CSSMB : groupes fermés adaptés et encadrement intensif."
            },
            "autre_option": autre_option
        }

    def _norm(c: str) -> str:
        return c.lower().replace("é", "e").replace("-", "").replace(" ", "")

    code_norm = _norm(programme_code)

    # Si l'école d'origine offre le programme retenu -> Impact nul !
    if ecole_origine in BOTTIN_DIRECTIONS:
        programmes_offerts = BOTTIN_DIRECTIONS[ecole_origine]["programmes"]
        prog_match = any(_norm(p) == code_norm for p in programmes_offerts)
        if prog_match:
            return {
                "niveau_impact": "none",
                "badge_texte": "🟢 Impact d'extraction nul : Maintien dans l'école d'origine",
                "explication": (
                    f"L'école d'origine ({ecole_origine}) dispense directement le parcours {programme_code.upper()}. "
                    "L'élève conserve ses repères, son réseau social et son milieu de vie."
                ),
                "etablissement_principal": {
                    "nom": ecole_origine,
                    "details": BOTTIN_DIRECTIONS[ecole_origine],
                    "raison": f"Point de service intégré à l'école d'origine offrant la filière {programme_code.upper()}."
                },
                "autre_option": None
            }

    # Sinon, recherche au sein du même pôle territorial (minimisation de l'extraction)
    ecoles_meme_pole = []
    for nom_ecole, data_b in BOTTIN_DIRECTIONS.items():
        if data_b["pole"].lower() == pole_origine.lower():
            if any(_norm(p) == code_norm for p in data_b["programmes"]):
                ecoles_meme_pole.append((nom_ecole, data_b))

    if ecoles_meme_pole:
        nom_choisi, data_choisie = ecoles_meme_pole[0]
        autres = ecoles_meme_pole[1:] if len(ecoles_meme_pole) > 1 else None
        autre_option_data = None
        if autres:
            autre_option_data = {
                "nom": autres[0][0],
                "details": autres[0][1],
                "note": f"Autre point de service disponible dans le Pôle {pole_origine}."
            }

        return {
            "niveau_impact": "pole",
            "badge_texte": f"🔵 Transfert de proximité : Pôle {pole_origine}",
            "explication": (
                f"L'école d'origine n'offre pas la filière {programme_code.upper()}. "
                f"L'élève est dirigé vers le point de service le plus proche au sein du même pôle géographique ({pole_origine})."
            ),
            "etablissement_principal": {
                "nom": nom_choisi,
                "details": data_choisie,
                "raison": f"Point de service de proximité Pôle {pole_origine} offrant {programme_code.upper()}."
            },
            "autre_option": autre_option_data
        }

    # Dernier recours : pôle central (SAS Outremont)
    return {
        "niveau_impact": "specialized",
        "badge_texte": "🟠 Pôle central CSSMB (Hors pôle d'origine)",
        "explication": (
            f"Aucun établissement du Pôle {pole_origine} n'offre le programme {programme_code.upper()}. "
            "Orientation vers le point de service central avec mesure de transport scolaire adapté."
        ),
        "etablissement_principal": {
            "nom": "037-SAS Outremont",
            "details": BOTTIN_DIRECTIONS["037-SAS Outremont"],
            "raison": "Point de service central CSSMB avec transport adapté."
        },
        "autre_option": None
    }


def executer_discernement(data_input: dict, annee_cible: int) -> dict:
    """
    Moteur complet d'évaluation clinique et d'arbre décisionnel.
    Intègre les 6 étapes séquentielles et les 3 garde-fous éthiques et réglementaires.
    """
    date_naissance = data_input["date_naissance"]
    age_30_sept = calculer_age_au_30_septembre(date_naissance, annee_cible)

    resultat = {
        "age_30_sept": age_30_sept,
        "annee_scolaire": f"{annee_cible}-{annee_cible + 1}",
        "garde_fou_1_statut": "valide",  # "bloque" ou "valide"
        "garde_fou_2_statut": "valide",  # "interrompu" ou "valide"
        "garde_fou_3_statut": "valide",  # "valide", "conditionnel", "bloque"
        "parcours_retenu": "",
        "code_parcours": "",
        "parcours_ecartes": [],
        "justification_23_3": "",
        "affectation": {},
        "alertes_cliniques": [],
        "protocole_special": None,
        "recommandations_pi": []
    }

    # -----------------------------------------------------------------------
    # GARDE-FOU 1 : ÂGE LÉGAL PIVOT (15 ANS AU 30 SEPTEMBRE)
    # -----------------------------------------------------------------------
    if age_30_sept < 15:
        resultat["garde_fou_1_statut"] = "bloque"
        resultat["parcours_retenu"] = "Maintien au 1er cycle du secondaire (Sec. 1 ou 2)"
        resultat["code_parcours"] = "maintien_1er_cycle"
        annee_15_ans = date_naissance.year + 15
        if datetime.date(annee_15_ans, 9, 30) < datetime.date(annee_15_ans, date_naissance.month, date_naissance.day):
            annee_15_ans += 1

        resultat["justification_23_3"] = (
            f"L'élève aura {age_30_sept} ans au 30 septembre {annee_cible}. En vertu de l'article 23 du Régime "
            "pédagogique de l'enseignement secondaire (LIP), l'accès aux parcours de formation axée sur l'emploi "
            "(FMS, FPT) et au Pré-DEP officiel est strictement subordonné à l'âge minimal de 15 ans au 30 septembre. "
            "Toute orientation en voie d'insertion professionnelle immédiate est légalement irrecevable."
        )

        resultat["parcours_ecartes"] = [
            {"nom": "Pré-DEP", "statut": "Écarté légalement", "motif": "Élève âgé de moins de 15 ans au 30 septembre."},
            {"nom": "FMS (Métier semi-spécialisé)", "statut": "Écarté légalement", "motif": "Condition d'âge minimale non atteinte."},
            {"nom": "FPT (Formation préparatoire au travail)", "statut": "Écarté légalement", "motif": "Condition d'âge minimale non atteinte."}
        ]

        resultat["protocole_special"] = {
            "type": "planification_prospective",
            "titre": f"Planification prospective vers 15 ans (Rentrée {annee_15_ans}-{annee_15_ans + 1})",
            "actions": [
                "Maintien au sein du milieu d'origine avec révision immédiate du Plan d'intervention (PI).",
                "Intensification des mesures d'adaptation (soutien orthopédagogique, flexibilité dans les tâches écrites).",
                "Amorce du continuum des COSP (Contenus en orientation scolaire et professionnelle) pour consolider la connaissance de soi.",
                "Visite préventive exploratoire d'un atelier ou d'un CFP au printemps précédant ses 15 ans."
            ]
        }

        # Affectation d'origine
        resultat["affectation"] = {
            "niveau_impact": "none",
            "badge_texte": "🟢 Maintien dans le milieu d'origine (1er cycle)",
            "explication": "L'élève poursuit son parcours régulier ou adapté au sein de son école d'origine.",
            "etablissement_principal": {
                "nom": data_input["ecole_origine"],
                "details": BOTTIN_DIRECTIONS.get(data_input["ecole_origine"], {
                    "ville": ECOLES_ORIGINE_CSSMB.get(data_input["ecole_origine"], {}).get("ville", "CSSMB"),
                    "telephone": "Voir secrétariat",
                    "contacts": [{"role": "Direction du 1er cycle", "nom": "Direction adjointe de niveau"}]
                }),
                "raison": "Continuité des apprentissages au 1er cycle du secondaire."
            },
            "autre_option": None
        }

        return resultat

    # -----------------------------------------------------------------------
    # GARDE-FOU 2 : CONSENTEMENT LIBRE ET ÉCLAIRÉ DE L'ADOLESCENT
    # -----------------------------------------------------------------------
    consentement_eleve = data_input.get("consentement_eleve", "")
    if consentement_eleve != "Accord documenté et enthousiaste":
        resultat["garde_fou_2_statut"] = "interrompu"
        resultat["parcours_retenu"] = "Interruption d'orientation — Démarche exploratoire préalable obligatoire"
        resultat["code_parcours"] = "demarche_exploratoire"

        resultat["justification_23_3"] = (
            f"L'évaluation relève un état de : « {consentement_eleve} ». L'article 23.3, 1° du Régime pédagogique "
            "exige que l'élève adhère pleinement et de façon éclairée à son projet d'orientation. Aucune filière "
            "axée sur le marché du travail ou des stages ne peut être imposée unilatéralement. Une démarche "
            "d'exploration clinique et expérientielle doit impérativement précéder tout classement formel."
        )

        resultat["parcours_ecartes"] = [
            {"nom": "Placement direct FMS / FPT", "statut": "Suspendu", "motif": "Absence d'adhésion affirmée de l'élève."},
            {"nom": "Pré-DEP direct", "statut": "Suspendu", "motif": "Besoin préalable de clarifier le projet vocationnel."}
        ]

        resultat["protocole_special"] = {
            "type": "demarche_exploratoire",
            "titre": "Protocole de Démarche Exploratoire Préalable (4 Volets)",
            "actions": [
                "Stage d'observation d'un jour sans évaluation en entreprise ou atelier partenaire.",
                "Visite guidée et immersion d'une demi-journée dans les ateliers d'un Centre de formation professionnelle (CFP).",
                "Jumelage et échange entre pairs avec un élève ambassadeur PFAE / Pré-DEP.",
                "Entretien clinique individuel approfondi avec le conseiller ou la conseillère d'orientation (c.o.).",
                "Nouvelle rencontre multidisciplinaire de réévaluation au terme de la démarche."
            ]
        }

        resultat["affectation"] = {
            "niveau_impact": "none",
            "badge_texte": "🟡 Maintien temporaire en école d'origine",
            "explication": "L'élève demeure dans son école d'origine le temps de compléter la démarche exploratoire.",
            "etablissement_principal": {
                "nom": data_input["ecole_origine"],
                "details": BOTTIN_DIRECTIONS.get(data_input["ecole_origine"], {
                    "ville": ECOLES_ORIGINE_CSSMB.get(data_input["ecole_origine"], {}).get("ville", "CSSMB"),
                    "telephone": "Voir secrétariat",
                    "contacts": [{"role": "Conseiller(ère) d'orientation", "nom": "Service d'orientation de l'école"}]
                }),
                "raison": "Pilotage de la démarche exploratoire par l'équipe multidisciplinaire d'origine."
            },
            "autre_option": None
        }

        return resultat

    # -----------------------------------------------------------------------
    # ANALYSE COMPARATIVE DES PARCOURS (ÉLÈVE ADMISSIBLE >= 15 ANS + ACCORD)
    # -----------------------------------------------------------------------
    # Comptage des matières de 2e sec réussies
    sec2_nb = sum([
        1 if data_input.get("sec2_francais") else 0,
        1 if data_input.get("sec2_math") else 0,
        1 if data_input.get("sec2_anglais") else 0
    ])
    primaire_ok = "Atteints" in data_input.get("primaire_maitrise", "")

    # Analyse d'orientation principale
    if sec2_nb >= 2:
        # Parcours Pré-DEP
        resultat["parcours_retenu"] = "Pré-DEP (Préparation à la formation professionnelle)"
        resultat["code_parcours"] = "pre-dep"
        mat_str = []
        if data_input.get("sec2_francais"): mat_str.append("Français")
        if data_input.get("sec2_math"): mat_str.append("Mathématiques")
        if data_input.get("sec2_anglais"): mat_str.append("Anglais")

        resultat["justification_23_3"] = (
            f"L'élève répond aux exigences du Pré-DEP : âgé de {age_30_sept} ans, il a validé {sec2_nb} matières de "
            f"base sur 3 en 2e secondaire ({', '.join(mat_str)}). Son profil démontre la capacité à franchir les "
            "préalables académiques de 3e et 4e secondaire nécessaires à l'admission dans un programme de DEP en CFP."
        )

        resultat["parcours_ecartes"] = [
            {
                "nom": "FMS (Métier semi-spécialisé)",
                "statut": "Écarté",
                "motif": "Sous-optimal : L'élève a les acquis pour viser une qualification de niveau DEP (diplôme d'études professionnelles) plus élevée."
            },
            {
                "nom": "FPT (Formation préparatoire au travail)",
                "statut": "Écarté",
                "motif": "Inadéquat : Les compétences académiques de l'élève dépassent largement les objectifs de base de la FPT."
            },
            {
                "nom": "Maintien au secteur général régulier",
                "statut": "Écarté",
                "motif": "Risque de démobilisation : L'élève exprime un projet vocationnel net nécessitant un continuum accéléré vers le CFP."
            }
        ]

    elif primaire_ok:
        # Parcours FMS
        resultat["parcours_retenu"] = "FMS (Formation menant à un métier semi-spécialisé — 1 an)"
        resultat["code_parcours"] = "fms"

        resultat["justification_23_3"] = (
            f"L'élève a {age_30_sept} ans et a maîtrisé les compétences fondamentales du 3e cycle du primaire en français "
            f"et en mathématiques, mais présente des échecs cumulés en 2e secondaire ({sec2_nb}/3 matière(s) validée(s)). "
            "La FMS offre une réponse directe et personnalisée : une qualification ministérielle rapide en un an (900 heures), "
            "dont 375 heures de stage supervisé en milieu de travail stimulant la valorisation et la réussite."
        )

        resultat["parcours_ecartes"] = [
            {
                "nom": "Pré-DEP",
                "statut": "Écarté",
                "motif": f"Préalables académiques insuffisants : Seulement {sec2_nb}/3 matière(s) de 2e sec réussie(s) (minimum requis : 2)."
            },
            {
                "nom": "FPT (Formation préparatoire au travail)",
                "statut": "Écarté",
                "motif": "Objectifs du primaire atteints. La FPT constituerait un ralentissement non justifié face à son potentiel d'insertion directe."
            },
            {
                "nom": "Maintien 1er cycle régulier",
                "statut": "Écarté",
                "motif": "Fatigue scolaire persistante et besoin urgent de contextualisation par le stage en entreprise."
            }
        ]

    else:
        # Parcours FPT
        resultat["parcours_retenu"] = "FPT (Formation préparatoire au travail — 3 ans)"
        resultat["code_parcours"] = "fpt"

        resultat["justification_23_3"] = (
            f"L'élève a {age_30_sept} ans et présente des retards importants avec non-atteinte des objectifs du primaire "
            "en langue d'enseignement et/ou en mathématiques. Le parcours FPT (FPT 1 à FPT 3) constitue l'alternative "
            "la plus inclusive et structurante : il sécurise le développement des compétences du quotidien, l'autonomie "
            "sociale et citoyenne, et une insertion professionnelle progressive par plateaux puis stages."
        )

        resultat["parcours_ecartes"] = [
            {
                "nom": "Pré-DEP",
                "statut": "Écarté",
                "motif": "Écart académique majeur : Préalables de 2e secondaire non maîtrisés."
            },
            {
                "nom": "FMS (Métier semi-spécialisé)",
                "statut": "Écarté",
                "motif": "Les compétences du primaire ne sont pas suffisamment consolidées pour un stage immédiat de 375h sans soutien préalable."
            },
            {
                "nom": "Classe ordinaire du régulier",
                "statut": "Écarté",
                "motif": "Incapacité à combler le retard sans rupture de l'estime personnelle; besoin d'un cadre à effectif réduit."
            }
        ]

    # -----------------------------------------------------------------------
    # GARDE-FOU 3 : ACCORD DES PARENTS & VALIDATION 23.3
    # -----------------------------------------------------------------------
    accord_parents = data_input.get("accord_parents", "")
    if accord_parents == "Refus formel des parents":
        resultat["garde_fou_3_statut"] = "bloque"
        resultat["alertes_cliniques"].append({
            "type": "error",
            "titre": "Garde-Fou 3 Activé : Refus formel de l'autorité parentale",
            "message": (
                "Conformément à la Loi sur l'instruction publique et à l'article 23.3, aucune dérogation "
                "ne permet d'inscrire l'élève en parcours PFAE sans le consentement des titulaires de l'autorité "
                "parentale. L'orientation est bloquée. Une mesure alternative obligatoire doit être mise en place."
            )
        })
        resultat["protocole_special"] = {
            "type": "mesure_alternative_parents",
            "titre": "Mesure alternative obligatoire (Maintien adapté en milieu d'origine)",
            "actions": [
                "Maintien impératif dans l'école d'origine de l'élève.",
                "Rencontre de concertation sous 10 jours avec la direction et le c.o. pour entendre les motifs du refus.",
                "Élaboration d'un plan d'intervention adapté renforcé (mesures d'appui, adaptations pédagogiques).",
                "Bilan de mi-étape et reconvocation des parents au printemps."
            ]
        }
    elif accord_parents == "En attente de la rencontre de Plan d'intervention (PI)":
        resultat["garde_fou_3_statut"] = "conditionnel"
        resultat["alertes_cliniques"].append({
            "type": "warning",
            "titre": "Orientation conditionnelle : Rencontre de PI requise",
            "message": (
                "Le discernement clinique recommande ce parcours, mais l'accord formel des parents doit être "
                "acté lors de la rencontre multidisciplinaire du Plan d'intervention (PI) avant transmission au comité."
            )
        })
    else:
        resultat["garde_fou_3_statut"] = "valide"

    # -----------------------------------------------------------------------
    # AFFECTATION TERRITORIALE & MINIMISATION DE L'EXTRACTION
    # -----------------------------------------------------------------------
    resultat["affectation"] = determiner_affectation_territoriale(
        data_input["ecole_origine"],
        resultat["code_parcours"],
        data_input.get("profil_particulier", "")
    )

    # Recommandations d'accompagnement clinique
    if "En apprentissage" in data_input.get("autonomie_stm", "") or "Dépendant" in data_input.get("autonomie_stm", ""):
        resultat["recommandations_pi"].append(
            "Plan de mobilité STM : Prévoir un entraînement supervisé aux trajets d'autobus avant le début du stage ou du transfert."
        )

    if "Difficile" in data_input.get("maturite_adultes", ""):
        resultat["recommandations_pi"].append(
            "Ateliers de savoir-être : Intégrer un module préparatoire aux codes relationnels en entreprise avec le psychoéducateur."
        )

    if "Sévère" in data_input.get("fatigue_cognitive", ""):
        resultat["recommandations_pi"].append(
            "Aménagement ergonomique et horaire : Prévoir des pauses sensorielles et un horaire de stage progressif."
        )

    return resultat


# ---------------------------------------------------------------------------
# 5. INITIALISATION DU SESSION STATE
# ---------------------------------------------------------------------------

DEFAULT_STATE = {
    "code_eleve": "ELE-2025-001",
    "annee_scolaire_cible": 2025,
    "ecole_origine": "139-Dalbé-Viau",
    "date_naissance": datetime.date(2010, 3, 14),
    "profil_particulier": "Régulier / Difficultés courantes",
    "sec2_francais": True,
    "sec2_math": False,
    "sec2_anglais": True,
    "primaire_maitrise": "Atteints (Français et Mathématiques)",
    "secteur_vise": "Mécanique, entretien et conduite d'engins",
    "preference_pedago": "Atelier pratique & manipulation concrète",
    "motivation_stage": "Très forte et confirmée (veut un DEP)",
    "fatigue_cognitive": "Faible / Normale",
    "adaptations_efficacite": "Efficaces avec progrès notables",
    "apprentissage_contextualise": "Indispensable pour donner du sens",
    "autonomie_stm": "Autonome (prend le bus seul sans difficulté)",
    "maturite_adultes": "Mature et respectueuse",
    "endurance_physique": "Excellente (capable d'un quart complet)",
    "consentement_eleve": "Accord documenté et enthousiaste",
    "accord_parents": "Favorable (Accord documenté)"
}

for k, v in DEFAULT_STATE.items():
    if k not in st.session_state:
        st.session_state[k] = v


def charger_profil_type(cle_profil: str):
    """Charge un profil type dans le session_state."""
    if cle_profil in PROFILS_DEMO:
        p_data = PROFILS_DEMO[cle_profil]["data"]
        for k, val in p_data.items():
            st.session_state[k] = val
        st.toast(f"Profil type chargé : {PROFILS_DEMO[cle_profil]['titre']}", icon="✅")


# ---------------------------------------------------------------------------
# 6. EN-TÊTE ET BARRE LATÉRALE
# ---------------------------------------------------------------------------

# En-tête CSSMB
render_html("""
<div class="cssmb-header">
    <div>
        <h1>Centre de services scolaire Marguerite-Bourgeoys</h1>
        <p>Aide au discernement clinique et éthique • PFAE (FMS / FPT), Pré-DEP & 1er Cycle</p>
    </div>
    <div style="text-align: right;">
        <span class="badge-legal">Régime pédagogique — Art. 23.3, 1°</span>
        <div style="font-size: 0.8rem; color: #d0e0ee; margin-top: 0.4rem;">Bottin officiel 2025-2026</div>
    </div>
</div>
""")

# Barre latérale : Outils rapides et démonstrations
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/fr/4/4b/Logo_CSSMB.png", width=180) if False else None
    st.markdown("### ⚡ Profils types cliniques")
    st.caption("Sélectionnez un cas pour charger instantanément les données d'évaluation et tester l'arbre décisionnel :")

    for k_demo, p_info in PROFILS_DEMO.items():
        if st.button(p_info["titre"], key=f"btn_demo_{k_demo}", use_container_width=True):
            charger_profil_type(k_demo)
            st.rerun()

    st.divider()

    st.markdown("### ⚙️ Année de classement")
    annee_choisie = st.selectbox(
        "Année scolaire ciblée :",
        options=[2025, 2026, 2027],
        index=0 if st.session_state["annee_scolaire_cible"] == 2025 else 1,
        help="L'âge est calculé au 30 septembre de cette année scolaire."
    )
    st.session_state["annee_scolaire_cible"] = annee_choisie

    st.divider()
    st.markdown("### ℹ️ Cadre d'application")
    st.info(
        "**Article 23.3, 1° :** Toute orientation en voie de qualification doit démontrer qu'elle "
        "est la plus susceptible de répondre aux intérêts, aux besoins et aux capacités de l'élève, "
        "avec son consentement libre et éclairé."
    )

    if st.button("🔄 Réinitialiser les données", use_container_width=True):
        for k, v in DEFAULT_STATE.items():
            st.session_state[k] = v
        st.toast("Formulaire réinitialisé.", icon="ℹ️")
        st.rerun()

# ---------------------------------------------------------------------------
# 7. ONGLETS DE NAVIGATION PRINCIPAUX
# ---------------------------------------------------------------------------

tab_evaluation, tab_synthese, tab_matrice, tab_legal = st.tabs([
    "🧭 Évaluation & Discernement",
    "📄 Fiche Synthèse Officielle (Art. 23.3)",
    "🗺️ Matrice Territoriale & Bottin",
    "⚖️ Cadre Légal & Éthique"
])

# ===========================================================================
# ONGLET 1 : ÉVALUATION ET FORMULAIRE MULTI-ÉTAPES
# ===========================================================================

with tab_evaluation:
    st.markdown("#### Parcours guidé de discernement multidisciplinaire")
    st.caption("Remplissez les 6 étapes cliniques. Le résultat et les garde-fous s'actualisent en temps réel.")

    col_form, col_result = st.columns([1.1, 1], gap="large")

    with col_form:
        # -------------------------------------------------------------------
        # Étape 1 : Portrait global & Identification
        # -------------------------------------------------------------------
        with st.expander("👤 Étape 1 : Portrait global & Recueil concerté", expanded=True):
            col_id1, col_id2 = st.columns(2)
            with col_id1:
                st.session_state["code_eleve"] = st.text_input(
                    "Code élève ou identifiant :",
                    value=st.session_state["code_eleve"],
                    help="Conserver l'anonymat si nécessaire (ex: ELE-4912)"
                )
            with col_id2:
                # Liste des écoles d'origine
                ecoles_keys = list(ECOLES_ORIGINE_CSSMB.keys())
                idx_ecole = ecoles_keys.index(st.session_state["ecole_origine"]) if st.session_state["ecole_origine"] in ecoles_keys else 0
                st.session_state["ecole_origine"] = st.selectbox(
                    "École d'origine CSSMB :",
                    options=ecoles_keys,
                    index=idx_ecole
                )

            col_dob, col_profil = st.columns(2)
            with col_dob:
                st.session_state["date_naissance"] = st.date_input(
                    "Date de naissance :",
                    value=st.session_state["date_naissance"],
                    min_value=datetime.date(2005, 1, 1),
                    max_value=datetime.date(2015, 12, 31)
                )
                # Calcul direct de l'âge
                age_calc = calculer_age_au_30_septembre(st.session_state["date_naissance"], st.session_state["annee_scolaire_cible"])
                if age_calc < 15:
                    st.error(f"Âge au 30 septembre {st.session_state['annee_scolaire_cible']} : **{age_calc} ans** (Moins de 15 ans)")
                else:
                    st.success(f"Âge au 30 septembre {st.session_state['annee_scolaire_cible']} : **{age_calc} ans** (Éligible analyse PFAE)")

            with col_profil:
                profils_options = [
                    "Régulier / Difficultés courantes",
                    "Trouble du spectre de l'autisme (TSA)",
                    "Trouble primaire du langage (TPL / dysphasie)"
                ]
                idx_p = profils_options.index(st.session_state["profil_particulier"]) if st.session_state["profil_particulier"] in profils_options else 0
                st.session_state["profil_particulier"] = st.selectbox(
                    "Profil particulier :",
                    options=profils_options,
                    index=idx_p
                )

        # -------------------------------------------------------------------
        # Étape 2 : Bilan académique (MEQ)
        # -------------------------------------------------------------------
        with st.expander("📚 Étape 2 : Acquis académiques (2e secondaire & Primaire)", expanded=True):
            st.markdown("**Matières de base de 2e secondaire réussies (pour Pré-DEP) :**")
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.session_state["sec2_francais"] = st.checkbox("Français (2e sec.)", value=st.session_state["sec2_francais"])
            with col_m2:
                st.session_state["sec2_math"] = st.checkbox("Mathématiques (2e sec.)", value=st.session_state["sec2_math"])
            with col_m3:
                st.session_state["sec2_anglais"] = st.checkbox("Anglais (2e sec.)", value=st.session_state["sec2_anglais"])

            nb_sec2 = sum([st.session_state["sec2_francais"], st.session_state["sec2_math"], st.session_state["sec2_anglais"]])
            if nb_sec2 >= 2:
                st.info(f"Critère académique Pré-DEP : **{nb_sec2} sur 3 matières validées** ✓")
            else:
                st.caption(f"Matières de 2e sec. : {nb_sec2} sur 3 (Moins de 2 : orienté vers FMS ou FPT)")

            st.markdown("**Acquis fondamentaux du 3e cycle du primaire :**")
            choix_primaire = [
                "Atteints (Français et Mathématiques)",
                "Non atteints en français et/ou mathématiques"
            ]
            idx_prim = choix_primaire.index(st.session_state["primaire_maitrise"]) if st.session_state["primaire_maitrise"] in choix_primaire else 0
            st.session_state["primaire_maitrise"] = st.radio(
                "Niveau de maîtrise du primaire :",
                options=choix_primaire,
                index=idx_prim,
                horizontal=True
            )

        # -------------------------------------------------------------------
        # Étape 3 : Continuum Vocationnel, Besoins & Adaptations
        # -------------------------------------------------------------------
        with st.expander("🛠️ Étape 3 : Intérêts, Besoins (PI) & Forces fonctionnelles", expanded=False):
            secteurs_options = [
                "Mécanique, entretien et conduite d'engins",
                "Commerce, vente et service à la clientèle",
                "Alimentation, cuisine et restauration",
                "Bâtiment, construction et menuiserie",
                "Horticulture, paysagement et espaces verts",
                "Soins esthétiques, entretien textile et blanchisserie",
                "Exploration générale ouverte / Polyvalent"
            ]
            idx_sec = secteurs_options.index(st.session_state["secteur_vise"]) if st.session_state["secteur_vise"] in secteurs_options else 0
            st.session_state["secteur_vise"] = st.selectbox("Secteur professionnel visé :", options=secteurs_options, index=idx_sec)

            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.session_state["preference_pedago"] = st.selectbox(
                    "Préférence pédagogique :",
                    options=[
                        "Atelier pratique & manipulation concrète",
                        "Cours théoriques et académiques en classe",
                        "Équilibre mi-temps théorie / mi-temps pratique"
                    ],
                    index=0
                )
                st.session_state["fatigue_cognitive"] = st.selectbox(
                    "Degré de fatigue cognitive (PI) :",
                    options=[
                        "Faible / Normale",
                        "Modérée en fin de journée",
                        "Sévère / Sensibilité aux surcharges sensorielles"
                    ],
                    index=0
                )
                st.session_state["autonomie_stm"] = st.selectbox(
                    "Autonomie transports (STM) :",
                    options=[
                        "Autonome (prend le bus seul sans difficulté)",
                        "En apprentissage (trajets connus)",
                        "Dépendant / Nécessite accompagnement strict"
                    ],
                    index=0
                )

            with col_v2:
                st.session_state["motivation_stage"] = st.selectbox(
                    "Motivation pour stage en milieu adulte :",
                    options=[
                        "Très forte et confirmée (veut un DEP)",
                        "Modérée avec besoin d'encadrement rassurant",
                        "Faible / Anxiété marquée face au travail"
                    ],
                    index=0
                )
                st.session_state["adaptations_efficacite"] = st.selectbox(
                    "Efficacité des adaptations actuelles :",
                    options=[
                        "Efficaces avec progrès notables",
                        "Partielles / Plafond atteint en classe ordinaire",
                        "Inopérantes / Échec persistant"
                    ],
                    index=0
                )
                st.session_state["endurance_physique"] = st.selectbox(
                    "Endurance physique (quart de 4h à 7h) :",
                    options=[
                        "Excellente (capable d'un quart complet)",
                        "Moyenne avec pauses planifiées",
                        "Faible / Restrictions médicales ou motrices"
                    ],
                    index=0
                )

            st.session_state["maturite_adultes"] = st.selectbox(
                "Maturité relationnelle avec collègues adultes :",
                options=[
                    "Mature et respectueuse",
                    "En développement avec supervision bienveillante",
                    "Difficile / Vigilance relationnelle"
                ],
                index=0
            )

        # -------------------------------------------------------------------
        # Étape 4 : Garde-Fou 2 — Consentement de l'élève
        # -------------------------------------------------------------------
        with st.expander("🤝 Étape 4 : Garde-Fou 2 — Consentement libre et éclairé de l'élève", expanded=True):
            st.caption("Article 23.3, 1° : L'élève doit adhérer activement et sans contrainte à son projet.")
            choix_consentement_eleve = [
                "Accord documenté et enthousiaste",
                "Hésitation / Crainte vive de l'élève",
                "Refus catégorique de l'élève"
            ]
            idx_ce = choix_consentement_eleve.index(st.session_state["consentement_eleve"]) if st.session_state["consentement_eleve"] in choix_consentement_eleve else 0
            st.session_state["consentement_eleve"] = st.radio(
                "Position de l'élève face à l'orientation et aux stages :",
                options=choix_consentement_eleve,
                index=idx_ce
            )

        # -------------------------------------------------------------------
        # Étape 5 : Accord des parents & Comité PI
        # -------------------------------------------------------------------
        with st.expander("👨‍👩‍👧 Étape 5 : Garde-Fou 3 — Accord des parents & Comité PI", expanded=True):
            choix_parents = [
                "Favorable (Accord documenté)",
                "En attente de la rencontre de Plan d'intervention (PI)",
                "Refus formel des parents"
            ]
            idx_par = choix_parents.index(st.session_state["accord_parents"]) if st.session_state["accord_parents"] in choix_parents else 0
            st.session_state["accord_parents"] = st.radio(
                "Statut de l'accord des titulaires de l'autorité parentale :",
                options=choix_parents,
                index=idx_par
            )

    # -----------------------------------------------------------------------
    # COLONNE DE DROITE : RÉSULTAT DU DISCERNEMENT EN DIRECT
    # -----------------------------------------------------------------------
    with col_result:
        st.markdown("#### Résultat de l'analyse clinique & juridique")

        # Exécution de l'algorithme
        eval_res = executer_discernement(st.session_state, st.session_state["annee_scolaire_cible"])

        # 1. Bannière de statut principal
        if eval_res["garde_fou_1_statut"] == "bloque":
            st.error(f"🛑 **GARDE-FOU 1 ACTIVÉ : Moins de 15 ans au 30 septembre**\n\n**Verdict :** {eval_res['parcours_retenu']}")
        elif eval_res["garde_fou_2_statut"] == "interrompu":
            st.warning(f"⚠️ **GARDE-FOU 2 ACTIVÉ : Consentement élève non établi**\n\n**Verdict :** {eval_res['parcours_retenu']}")
        elif eval_res["garde_fou_3_statut"] == "bloque":
            st.error(f"🛑 **GARDE-FOU 3 ACTIVÉ : Refus parental formel**\n\n**Verdict :** {eval_res['parcours_retenu']}")
        elif eval_res["garde_fou_3_statut"] == "conditionnel":
            st.warning(f"⏳ **ORIENTATION CONDITIONNELLE (Attente PI)**\n\n**Filière recommandée :** {eval_res['parcours_retenu']}")
        else:
            st.success(f"✅ **DOSSIER VALIDÉ POUR COMITÉ DE CLASSEMENT**\n\n**Filière retenue :** {eval_res['parcours_retenu']}")

        # 2. Alertes cliniques
        for alerte in eval_res["alertes_cliniques"]:
            if alerte["type"] == "error":
                st.error(f"**{alerte['titre']}** : {alerte['message']}")
            elif alerte["type"] == "warning":
                st.warning(f"**{alerte['titre']}** : {alerte['message']}")

        # 3. Badge d'impact territorial
        affectation = eval_res["affectation"]
        badge_cls = "impact-none" if affectation["niveau_impact"] == "none" else ("impact-pole" if affectation["niveau_impact"] == "pole" else "impact-specialized")
        render_html(f'<span class="badge-impact {badge_cls}">{affectation["badge_texte"]}</span>')
        st.write(affectation["explication"])

        # 4. Carte de l'établissement recommandé
        etab = affectation["etablissement_principal"]
        render_html(f"""
        <div class="clinical-card">
            <div class="card-title">🏫 Établissement recommandé : {etab['nom']}</div>
            <p><strong>Ville :</strong> {etab['details'].get('ville', 'CSSMB')} | <strong>Téléphone :</strong> {etab['details'].get('telephone', 'N/A')}</p>
            <p><strong>Motif de l'affectation :</strong> {etab['raison']}</p>
            <div style="background: #f1f5f9; padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem;">
                <strong style="color: #0d3b66;">Contacts de direction (Bottin 2025-2026) :</strong>
                <ul style="margin: 0.25rem 0 0 1.2rem; padding: 0;">
                    {''.join([f"<li>{c['role']} : <strong>{c['nom']}</strong></li>" for c in etab['details'].get('contacts', [])])}
                </ul>
            </div>
        </div>
        """)

        if affectation.get("autre_option"):
            ao = affectation["autre_option"]
            st.caption(f"Alternative envisageable : **{ao['nom']}** ({ao['details'].get('ville')}) — {ao['note']}")

        # 5. Justification 23.3 & Comparaison des parcours écartés
        with st.expander("⚖️ Justification légale (Art. 23.3) & Parcours écartés", expanded=True):
            st.write(eval_res["justification_23_3"])
            if eval_res["parcours_ecartes"]:
                st.markdown("**Parcours alternatifs analysés et écartés :**")
                for pe in eval_res["parcours_ecartes"]:
                    st.markdown(f"- **{pe['nom']}** ({pe['statut']}) : {pe['motif']}")

        # 6. Protocole spécial (si activé)
        if eval_res.get("protocole_special"):
            proto = eval_res["protocole_special"]
            render_html(f"""
            <div style="background: #fff8f0; border: 1px solid #fed7aa; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                <strong style="color: #c2410c;">📋 {proto['titre']}</strong>
                <ul style="margin: 0.5rem 0 0 1.2rem;">
                    {''.join([f"<li>{a}</li>" for a in proto['actions']])}
                </ul>
            </div>
            """)

        # 7. Recommandations PI
        if eval_res["recommandations_pi"]:
            with st.expander("🎯 Recommandations pour le Plan d'intervention (PI)", expanded=True):
                for rec in eval_res["recommandations_pi"]:
                    st.markdown(f"• {rec}")


# ===========================================================================
# ONGLET 2 : FICHE SYNTHÈSE OFFICIELLE (ART. 23.3) - IMPRIMABLE / PDF
# ===========================================================================

with tab_synthese:
    st.markdown("### Fiche officielle de discernement clinique & décision de classement")
    st.caption("Ce document est conforme aux exigences de l'Article 23.3, 1° du Régime pédagogique pour les comités de classement du CSSMB.")

    # Re-calcul des données actuelles
    eval_actuelle = executer_discernement(st.session_state, st.session_state["annee_scolaire_cible"])
    etab_rec = eval_actuelle["affectation"]["etablissement_principal"]

    # Bouton d'impression direct
    render_html("""
    <div class="no-print" style="margin-bottom: 1.25rem; display: flex; gap: 1rem; align-items: center;">
        <button onclick="window.print()" style="background-color: #0d3b66; color: #ffffff; border: none; padding: 0.65rem 1.4rem; border-radius: 6px; font-weight: 700; font-size: 0.95rem; cursor: pointer; display: inline-flex; align-items: center; gap: 0.5rem; box-shadow: 0 2px 6px rgba(13,59,102,0.25);">
            🖨️ Imprimer la fiche officielle (PDF)
        </button>
        <span style="color: #64748b; font-size: 0.85rem;">Prêt pour impression A4/Letter ou export PDF (Ctrl+P)</span>
    </div>
    """)

    # Contenu HTML formaté avec style print dédié
    fiche_html = f"""<div id="print-section" class="print-sheet">
<div class="print-header">
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
<div>
<h2 style="margin: 0; color: #0d3b66; font-size: 1.4rem;">CENTRE DE SERVICES SCOLAIRE MARGUERITE-BOURGEOYS</h2>
<h3 style="margin: 0.25rem 0 0 0; color: #475569; font-size: 1.1rem; font-weight: 600;">
Fiche de discernement clinique et éthique — Voies de qualification & PFAE
</h3>
<p style="margin: 0.25rem 0 0 0; font-size: 0.85rem; color: #64748b;">
Application du Régime pédagogique de l'enseignement secondaire (LIP, art. 23 et 23.3, 1°)
</p>
</div>
<div style="text-align: right; font-size: 0.85rem;">
<strong>Année scolaire :</strong> {eval_actuelle['annee_scolaire']}<br>
<strong>Date d'émission :</strong> {datetime.date.today().strftime('%d/%m/%Y')}<br>
<strong>Statut :</strong> <span style="font-weight: 700; color: #0d3b66;">{eval_actuelle['parcours_retenu']}</span>
</div>
</div>
</div>

<div class="print-grid">
<div class="print-box">
<h4>1. Identification de l'élève</h4>
<p style="margin: 0.2rem 0;"><strong>Identifiant élève :</strong> {html.escape(st.session_state['code_eleve'])}</p>
<p style="margin: 0.2rem 0;"><strong>Date de naissance :</strong> {st.session_state['date_naissance'].strftime('%d/%m/%Y')} ({eval_actuelle['age_30_sept']} ans au 30 sept.)</p>
<p style="margin: 0.2rem 0;"><strong>École d'origine :</strong> {html.escape(st.session_state['ecole_origine'])}</p>
<p style="margin: 0.2rem 0;"><strong>Profil diagnostique / particulier :</strong> {html.escape(st.session_state['profil_particulier'])}</p>
</div>
<div class="print-box">
<h4>2. Projet Vocationnel & Acquis</h4>
<p style="margin: 0.2rem 0;"><strong>Secteur visé :</strong> {html.escape(st.session_state['secteur_vise'])}</p>
<p style="margin: 0.2rem 0;"><strong>Matières de 2e sec. réussies :</strong> {'Français ' if st.session_state['sec2_francais'] else ''}{'Math ' if st.session_state['sec2_math'] else ''}{'Anglais' if st.session_state['sec2_anglais'] else ''} ({sum([st.session_state['sec2_francais'], st.session_state['sec2_math'], st.session_state['sec2_anglais']] )}/3)</p>
<p style="margin: 0.2rem 0;"><strong>Maîtrise du primaire :</strong> {html.escape(st.session_state['primaire_maitrise'])}</p>
<p style="margin: 0.2rem 0;"><strong>Autonomie transports :</strong> {html.escape(st.session_state['autonomie_stm'])}</p>
</div>
</div>

<div class="print-box" style="margin-bottom: 1.25rem;">
<h4>3. Démonstration clinique et légale (Régime pédagogique, art. 23.3, 1°)</h4>
<p style="margin: 0.35rem 0 0.75rem 0; line-height: 1.45; font-size: 0.9rem;">
{html.escape(eval_actuelle['justification_23_3'])}
</p>
<strong>Justification des parcours alternatifs écartés :</strong>
<ul style="margin: 0.3rem 0 0 1.2rem; font-size: 0.85rem; line-height: 1.4;">
{''.join([f"<li><strong>{html.escape(pe['nom'])}</strong> ({pe['statut']}) : {html.escape(pe['motif'])}</li>" for pe in eval_actuelle['parcours_ecartes']])}
</ul>
</div>

<div class="print-grid">
<div class="print-box">
<h4>4. Affectation recommandée & Minimisation de l'extraction</h4>
<p style="margin: 0.2rem 0;"><strong>Établissement proposé :</strong> {html.escape(etab_rec['nom'])} ({etab_rec['details'].get('ville', '')})</p>
<p style="margin: 0.2rem 0;"><strong>Impact d'extraction :</strong> {html.escape(eval_actuelle['affectation']['badge_texte'])}</p>
<p style="margin: 0.2rem 0;"><strong>Direction ressource :</strong> {', '.join([c['nom'] + ' (' + c['role'] + ')' for c in etab_rec['details'].get('contacts', [])])}</p>
<p style="margin: 0.2rem 0;"><strong>Téléphone :</strong> {etab_rec['details'].get('telephone', 'N/A')}</p>
</div>
<div class="print-box">
<h4>5. État des consentements (Adolescent & Parents)</h4>
<p style="margin: 0.2rem 0;"><strong>Adhésion de l'élève :</strong> {html.escape(st.session_state['consentement_eleve'])}</p>
<p style="margin: 0.2rem 0;"><strong>Accord parental :</strong> {html.escape(st.session_state['accord_parents'])}</p>
<p style="margin: 0.2rem 0;"><strong>Statut légal :</strong> {'Accord complet et libre documenté' if eval_actuelle['garde_fou_2_statut'] == 'valide' and eval_actuelle['garde_fou_3_statut'] == 'valide' else 'Action requise avant confirmation'}</p>
</div>
</div>

{'<div class="print-box" style="margin-top: 1.25rem;"><h4>6. Recommandations prioritaires pour le Plan d Intervention (PI)</h4><ul style="margin: 0.3rem 0 0 1.2rem; font-size: 0.85rem;">' + ''.join([f"<li>{html.escape(r)}</li>" for r in eval_actuelle['recommandations_pi']]) + '</ul></div>' if eval_actuelle['recommandations_pi'] else ''}

<div class="print-signature-grid">
<div class="signature-box">
<span>Direction d'école d'origine</span>
<span style="border-top: 1px solid #cbd5e1; padding-top: 2px;">Date & Signature</span>
</div>
<div class="signature-box">
<span>Conseiller(ère) d'orientation</span>
<span style="border-top: 1px solid #cbd5e1; padding-top: 2px;">Date & Signature</span>
</div>
<div class="signature-box">
<span>Titulaire / Orthopédagogue</span>
<span style="border-top: 1px solid #cbd5e1; padding-top: 2px;">Date & Signature</span>
</div>
<div class="signature-box">
<span>Parent(s) / Titulaire autorité</span>
<span style="border-top: 1px solid #cbd5e1; padding-top: 2px;">Date & Signature</span>
</div>
</div>
</div>
"""

    render_html(fiche_html)

    # Export Markdown
    fiche_markdown = f"""# CENTRE DE SERVICES SCOLAIRE MARGUERITE-BOURGEOYS
## Fiche officielle de discernement clinique & décision de classement (Art. 23.3)
**Année scolaire :** {eval_actuelle['annee_scolaire']}  
**Date d'émission :** {datetime.date.today().strftime('%d/%m/%Y')}  
**Statut du dossier :** {eval_actuelle['parcours_retenu']}

### 1. Portrait de l'élève
- **Identifiant :** {st.session_state['code_eleve']}
- **Date de naissance :** {st.session_state['date_naissance'].strftime('%d/%m/%Y')} ({eval_actuelle['age_30_sept']} ans au 30 sept.)
- **École d'origine :** {st.session_state['ecole_origine']}
- **Profil diagnostique :** {st.session_state['profil_particulier']}

### 2. Justification légale (Régime pédagogique, art. 23.3, 1°)
{eval_actuelle['justification_23_3']}

#### Parcours alternatifs analysés et écartés :
{chr(10).join([f"- **{pe['nom']}** ({pe['statut']}) : {pe['motif']}" for pe in eval_actuelle['parcours_ecartes']])}

### 3. Affectation recommandée
- **Établissement proposé :** {etab_rec['nom']} ({etab_rec['details'].get('ville', '')})
- **Impact territorial :** {eval_actuelle['affectation']['badge_texte']}
- **Direction ressource :** {', '.join([c['nom'] + ' (' + c['role'] + ')' for c in etab_rec['details'].get('contacts', [])])}
- **Téléphone :** {etab_rec['details'].get('telephone', 'N/A')}

### 4. Consentement & Décision
- **Adhésion élève :** {st.session_state['consentement_eleve']}
- **Accord parental :** {st.session_state['accord_parents']}
"""
    st.download_button(
        label="📥 Télécharger la fiche de synthèse (.md)",
        data=fiche_markdown,
        file_name=f"Synthese_23_3_{st.session_state['code_eleve']}.md",
        mime="text/markdown"
    )


# ===========================================================================
# ONGLET 3 : MATRICE TERRITORIALE & BOTTIN CSSMB 2025-2026
# ===========================================================================

with tab_matrice:
    st.markdown("### Bottin officiel des points de service PFAE & Pré-DEP (2025-2026)")
    st.caption("Cartographie territoriale et coordonnées officielles des directions de services pour le classement multidisciplinaire.")

    poles = ["Ouest", "Sud", "Centre / Est"]
    tab_p1, tab_p2, tab_p3 = st.tabs([f"Pôle {p}" for p in poles])

    for tab_pole, nom_pole in zip([tab_p1, tab_p2, tab_p3], poles):
        with tab_pole:
            st.markdown(f"#### Établissements et points de service du Pôle {nom_pole}")
            
            ecoles_ce_pole = {k: v for k, v in BOTTIN_DIRECTIONS.items() if v["pole"] == nom_pole}
            
            for nom_e, data_e in ecoles_ce_pole.items():
                with st.container():
                    render_html(f"""
                    <div class="clinical-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-size: 1.15rem; font-weight: 700; color: #0d3b66;">{nom_e} ({data_e['ville']})</div>
                            <div>
                                {' '.join([f'<span style="background: #e2e8f0; color: #1e293b; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">{prog}</span>' for prog in data_e['programmes']])}
                            </div>
                        </div>
                        <p style="margin: 0.5rem 0 0.25rem 0;"><strong>Téléphone :</strong> {data_e['telephone']}</p>
                        <p style="margin: 0.25rem 0;"><strong>Clientèles / Volets :</strong> {', '.join(data_e['clienteles'])}</p>
                        <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px dashed #cbd5e1;">
                            <strong>Direction(s) ressource(s) :</strong>
                            <ul style="margin: 0.2rem 0 0 1.2rem;">
                                {''.join([f"<li>{c['role']} : <strong>{c['nom']}</strong></li>" for c in data_e['contacts']])}
                            </ul>
                        </div>
                    </div>
                    """)


# ===========================================================================
# ONGLET 4 : CADRE LÉGAL & GUIDE ÉTHIQUE
# ===========================================================================

with tab_legal:
    st.markdown("### Cadre réglementaire : Article 23.3, 1° du Régime pédagogique")
    
    st.markdown("""
    > **Régime pédagogique de l'éducation préscolaire, de l'enseignement primaire et de l'enseignement secondaire**  
    > *(Loi sur l'instruction publique, RLRQ, c. I-13.3, r. 8)*
    >
    > **Article 23.3.** La commission scolaire [centre de services scolaire] qui propose à l'élève d'être admis à un parcours de formation axée sur l'emploi ou au pré-DEP doit :
    > 1° **démontrer que le parcours proposé est celui qui est le plus susceptible de répondre à l'intérêt, aux besoins et aux capacités de l'élève face à toutes les alternatives envisageables**, compte tenu des évaluations de ses compétences et des interventions pédagogiques antérieures;
    > 2° obtenir le **consentement libre et éclairé de l'élève**, s'il est âgé de 14 ans ou plus, et de ses parents.

    ---

    #### Les 3 Piliers du Discernement Clinique au CSSMB :

    1. **Le principe de proportionnalité et de moindre extraction :**
       L'orientation vers une voie de qualification (FMS, FPT) ne doit jamais être une mesure d'éviction académique. Elle doit être choisie parce que ses composantes (stages pratiques, contextualisation en atelier) correspondent au mode d'apprentissage optimal de l'adolescent. L'extraction hors de l'école d'origine doit être nulle ou minimale.

    2. **L'inviolabilité du consentement de l'adolescent (Garde-Fou 2) :**
       Un stage de 375 heures en entreprise (FMS) ou une insertion socioprofessionnelle (FPT) exige une collaboration active de l'élève. En cas de doute, d'anxiété ou de réticence, la démarche exploratoire préalable (immersion CFP, stage d'observation d'un jour, pair-aidance) s'impose obligatoirement avant toute décision de classement.

    3. **La transparence comparative envers les parents (Garde-Fou 3) :**
       Le comité doit être capable d'expliquer pourquoi les autres parcours ont été examinés puis écartés. La fiche de synthèse synthétise cette argumentation pour éclairer les parents lors de la rencontre du Plan d'intervention (PI).
    """)

    st.info(
        "💡 **Rappel aux directions et conseillers d'orientation :** "
        "Conservez une copie signée de la fiche synthèse au dossier d'aide particulière de l'élève (DAP) "
        "et annexez-la à la révision annuelle du Plan d'intervention (PI)."
    )
