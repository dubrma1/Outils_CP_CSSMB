"""
app.py
Tableau de Bord PFAE - Suivi des Stages des Élèves (FMS et FPT3) - Année scolaire 2026-2027
Centre de services scolaire Marguerite-Bourgeoys (CSSMB)

Adapté pour WebAssembly / Stlite (Pyodide) & Azure Static Web Apps :
- Conforme à la Loi 25 : 100 % Local côté client dans le navigateur (Zéro télémétrie, zéro serveur backend).
- Persistance en mémoire virtuelle (MEMFS) avec téléchargement synchrone immédiat du CSV actualisé.
- Compatible Wasm : pas de filelock, chargement direct et réactif.
"""

import builtins
import os
import sys
import glob
import datetime
import importlib
import pandas as pd
import streamlit as st

# --- PATCH COMPATIBILITÉ STLITE / PYODIDE POUR ST.DATA_EDITOR ---
# Dans Streamlit 1.42+ / Stlite, le module data_editor fait référence à 'arrow_table.schema'
# et itère dessus (for field in arrow_schema:).
# En l'absence de pyarrow natif dans Stlite :
# 1) Si absent : lève NameError: name 'arrow_table' is not defined
# 2) Si schema est None : lève TypeError: 'NoneType' object is not iterable
# Ce mock itérable et le wrapper défensif résolvent intégralement ces deux problèmes.
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

try:
    import streamlit.elements.widgets.data_editor as _de
    _de.arrow_table = _MockArrowTable()
    if hasattr(_de, "_compute_data_editor_signature"):
        _orig_compute_sig = _de._compute_data_editor_signature
        def _safe_compute_sig(*args, **kwargs):
            if "arrow_schema" in kwargs and (kwargs["arrow_schema"] is None or not hasattr(kwargs["arrow_schema"], "__iter__")):
                kwargs["arrow_schema"] = _MockArrowSchema()
            try:
                return _orig_compute_sig(*args, **kwargs)
            except Exception:
                import hashlib
                df = kwargs.get("data_df")
                cols = str(list(df.columns)) if df is not None and hasattr(df, "columns") else ""
                return hashlib.md5(cols.encode()).hexdigest()
        _de._compute_data_editor_signature = _safe_compute_sig
except Exception:
    pass

# Priorité au répertoire local de l'application sur sys.path
_app_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
for p in (_app_dir, ".", "app"):
    if p and p not in sys.path:
        sys.path.insert(0, p)

import data_manager as dm
dm = importlib.reload(dm)

# --- CONFIGURATION STREAMLIT ---
st.set_page_config(
    page_title="TdB Stages PFAE 2026-2027 | CSSMB",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STYLE CSS LOCAL (CSSMB & THÈME ÉPURÉ) ---
st.markdown(
    """
    <style>
    /* Styles institutionnels CSSMB */
    :root {
        --cssmb-blue: #005596;
        --cssmb-dark: #1E293B;
        --cssmb-light: #F8FAFC;
        --cssmb-border: #E2E8F0;
        --cssmb-success: #16A34A;
        --cssmb-warning: #CA8A04;
        --cssmb-danger: #DC2626;
        --cssmb-info: #0284C7;
    }
    
    /* En-tête institutionnel */
    .cssmb-header {
        background: linear-gradient(135deg, #004075 0%, #005596 60%, #0284c7 100%);
        color: white;
        padding: 22px 28px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 85, 150, 0.15);
    }
    .cssmb-header h1 {
        margin: 0;
        font-size: 1.75rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
    }
    .cssmb-header p {
        margin: 6px 0 0 0;
        font-size: 0.95rem;
        color: #E0F2FE;
        opacity: 0.95;
    }
    .law25-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.35);
        color: #F8FAFC;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 10px;
    }

    /* Cartes KPI */
    .kpi-card {
        background-color: white;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
    }
    .kpi-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.1;
    }
    .kpi-subtitle {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 5px;
    }

    /* Boîtes d'alertes drill-down */
    .drilldown-card {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-left: 5px solid #005596;
        border-radius: 8px;
        padding: 18px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    
    .course-badge {
        display: inline-block;
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        border-radius: 6px;
        padding: 6px 10px;
        margin: 4px;
        font-size: 0.85rem;
    }

    /* Carte et badge Répertoire des Métiers Semi-spécialisés (RMS) */
    .rms-card {
        background: #F0F9FF;
        border: 1px solid #BAE6FD;
        border-left: 5px solid #0284C7;
        border-radius: 8px;
        padding: 14px 18px;
        margin-top: 12px;
        margin-bottom: 12px;
    }
    .rms-badge {
        display: inline-block;
        background: #0284C7;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    /* Boutons personnalisés */
    div.stButton > button:first-child {
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Mois en français pour un affichage uniforme sans dépendance de locale OS
MOIS_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre"
]

# --- CHARGEMENT DES DONNÉES AVEC CACHE ---
@st.cache_data(show_spinner=False)
def get_cached_raw_data(file_path: str, mtime: float) -> pd.DataFrame:
    """Charge le fichier brut avec mise en cache basée sur le timestamp du fichier."""
    return dm.load_raw_data(file_path)

csv_file_path = dm.find_csv_file()
csv_mtime = os.path.getmtime(csv_file_path) if os.path.exists(csv_file_path) else 0.0

try:
    df_raw = get_cached_raw_data(csv_file_path, csv_mtime)
except Exception as err:
    st.error(f"Erreur critique lors du chargement des données : {err}")
    st.stop()


# --- INITIALISATION DE L'ÉTAT DE SESSION ---
if "quick_filter" not in st.session_state:
    st.session_state.quick_filter = "ALL"
if "selected_student_id" not in st.session_state:
    st.session_state.selected_student_id = None
if "popup_student_id" not in st.session_state:
    st.session_state.popup_student_id = None
if "show_popup_dialog" not in st.session_state:
    st.session_state.show_popup_dialog = False
if "save_status_msg" not in st.session_state:
    st.session_state.save_status_msg = None
if "download_ready_csv_bytes" not in st.session_state:
    st.session_state.download_ready_csv_bytes = None
if "download_ready_filename" not in st.session_state:
    st.session_state.download_ready_filename = None
if "current_uploaded_name" not in st.session_state:
    st.session_state.current_uploaded_name = None


# --- BARRE LATÉRALE : FILTRES & PARAMÈTRES MÉTIERS ---
with st.sidebar:
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #004075 0%, #005596 100%); color: white; padding: 12px 14px; border-radius: 8px; text-align: center; margin-bottom: 15px; box-shadow: 0 2px 6px rgba(0,85,150,0.2);">
            <div style="font-weight: 800; font-size: 1.15rem; letter-spacing: 0.5px;">CSSMB</div>
            <div style="font-size: 0.72rem; color: #E0F2FE; margin-top: 2px;">Centre de services scolaire Marguerite-Bourgeoys</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### 🏫 Filtres PFAE")

    # 1. Filtre École
    ecoles_disponibles = sorted(
        [dm.format_school_display(c) for c in df_raw["CD_ECOLE"].unique()]
    )
    choix_ecole = st.selectbox(
        "Établissement scolaire :",
        options=["Toutes les écoles"] + ecoles_disponibles,
        index=0,
        help="Filtrer par établissement scolaire du CSSMB",
    )

    # 2. Filtre Parcours
    parcours_options = ["Tous", "FMS", "FPT"]
    choix_parcours = st.radio(
        "Parcours d'enseignement :",
        options=parcours_options,
        horizontal=True,
        index=0,
    )

    # Dérivation des enseignants disponibles selon école/parcours choisis
    df_profs_filtre = df_raw.copy()
    if choix_ecole != "Toutes les écoles":
        code_sel = choix_ecole.split(" - ")[0].strip()
        df_profs_filtre = df_profs_filtre[df_profs_filtre["CD_ECOLE"] == code_sel]
    if choix_parcours != "Tous":
        df_profs_filtre = df_profs_filtre[df_profs_filtre["PARCOURS"] == choix_parcours]

    enseignants_list = sorted(
        [
            str(p).strip()
            for p in df_profs_filtre["NOM_ENSEIGN"].dropna().unique()
            if str(p).strip() and str(p).lower() != "nan"
        ]
    )

    # 3. Filtre Enseignant
    choix_enseignant = st.selectbox(
        "Enseignant responsable :",
        options=["Tous les enseignants"] + enseignants_list,
        index=0,
        help="Filtrer selon l'enseignant associé à l'élève",
    )

    # 4. Filtre Secteur d'activité RMS
    rms_lookup = dm.get_rms_lookup()
    secteurs_rms_list = rms_lookup.get("secteurs", [])
    choix_secteurs_rms = st.multiselect(
        "Secteur d'activité économique (RMS) :",
        options=secteurs_rms_list,
        default=[],
        help="Filtrer les élèves selon les secteurs d'activité économique officiels du MEQ",
    )

    # 5. Recherche par numéro d'élève
    recherche_eleve = st.text_input(
        "🔍 Recherche par identifiant élève :",
        value="",
        placeholder="Ex: Élève-015, 042...",
        help="Saisissez tout ou partie de l'identifiant élève (ex: Élève-015).",
    )

    st.markdown("---")
    st.markdown("### ⚙️ Paramètres & Alertes")

    # Date de référence pour le calcul des délais
    today_date = datetime.date.today()
    ref_date = st.date_input(
        "Date de référence d'analyse :",
        value=today_date,
        help="Permet de simuler l'état des délais d'évaluation à une date précise de l'année scolaire 2026-2027.",
    )

    with st.expander("Jours prévus & Seuils", expanded=False):
        jours_fms = st.number_input(
            "Jours prévus en stage - FMS :",
            min_value=20,
            max_value=180,
            value=60,
            step=5,
            help="Base de calcul pour le taux d'absentéisme en FMS (défaut : 60 jours)",
        )
        jours_fpt = st.number_input(
            "Jours prévus en stage - FPT3 :",
            min_value=20,
            max_value=220,
            value=100,
            step=5,
            help="Base de calcul pour le taux d'absentéisme en FPT (défaut : 100 jours)",
        )
        seuil_critique_abs = st.slider(
            "Seuil absentéisme critique (%) :",
            min_value=10.0,
            max_value=25.0,
            value=15.0,
            step=0.5,
            help="Alerte rouge au-delà de ce taux d'absence (défaut : 15 %)",
        )
        seuil_vigilance_abs = st.slider(
            "Seuil vigilance absentéisme (%) :",
            min_value=5.0,
            max_value=14.0,
            value=8.0,
            step=0.5,
            help="Alerte jaune pour ce seuil de vigilance (défaut : 8 %)",
        )

    st.markdown("---")
    # Section persistance WebAssembly & Loi 25
    st.markdown("### 💾 Sauvegarde sur Portable")
    st.markdown(
        """
        <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 8px 10px; font-size: 0.78rem; color: #166534; margin-bottom: 10px;">
            ✅ <strong>Persistance locale active</strong> : Vos saisies manuelles sont conservées sur ce portable.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Bouton de téléchargement direct du fichier CSV actuel
    st.download_button(
        label="💾 Enregistrer CSV sur mon portable",
        data=dm.get_latest_csv_bytes(csv_file_path),
        file_name=f"Listes_profs_élèves_FMS-FPT_26-27_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
        help="Télécharger une copie complète du CSV maître sur votre ordinateur portable",
    )

    # File uploader pour restaurer ou mettre à jour un CSV lors d'une session ultérieure
    uploaded_csv = st.file_uploader(
        "📂 Charger un CSV actualisé :",
        type=["csv"],
        help="Importer un fichier CSV précédemment téléchargé pour reprendre vos saisies.",
        key="sidebar_csv_uploader",
    )
    if uploaded_csv is not None:
        if st.session_state.current_uploaded_name != uploaded_csv.name:
            with open(csv_file_path, "wb") as f:
                f.write(uploaded_csv.getvalue())
            st.session_state.current_uploaded_name = uploaded_csv.name
            st.cache_data.clear()
            st.toast(f"Données chargées depuis '{uploaded_csv.name}' !", icon="✅")
            st.rerun()

    if st.button("🔄 Rafraîchir l'affichage", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# --- AGRÉGATION EN VUE ÉLÈVE UNIQUE (352 ÉLÈVES) ---
df_student_view = dm.get_student_view(
    df_raw,
    days_fms=int(jours_fms),
    days_fpt=int(jours_fpt),
    ref_date=ref_date,
    critical_abs_threshold=float(seuil_critique_abs),
    warning_abs_threshold=float(seuil_vigilance_abs),
)


# --- DIALOG POPUP : FICHE D'IDENTIFICATION ÉLÈVE (FORMAT PORTRAIT) ---
@st.dialog("Fiche de Suivi Élève (Format Portrait)", width="small")
def afficher_fiche_id_popup(student_id: str):
    """Affiche une fiche d'identification portrait pour un élève unique et permet sa modification directe."""
    matches = df_student_view[df_student_view["NO_ELEVE"].astype(str) == str(student_id)]
    if len(matches) == 0:
        st.warning(f"Élève {student_id} introuvable.")
        return
    eleve_row = matches.iloc[0]

    # Données actuelles de l'élève
    curr_metier = str(eleve_row.get("Metier_FMS", "")).strip()
    if curr_metier in ("nan", "None", "0"):
        curr_metier = ""
    curr_fgj = str(eleve_row.get("Code_FGJ", "")).strip()
    if curr_fgj in ("nan", "None", "0"):
        curr_fgj = ""
    curr_secteur = str(eleve_row.get("Secteur_RMS", "")).strip()
    if curr_secteur in ("nan", "None", "0", "Non applicable (FPT)"):
        curr_secteur = ""

    # Données du référentiel RMS
    rms_lookup = dm.get_rms_lookup()
    df_rms = rms_lookup.get("df", pd.DataFrame())
    by_label = rms_lookup.get("by_label", {})
    all_secteurs = rms_lookup.get("secteurs", [])

    # Dérivation du secteur actuel si non défini mais que le métier est connu
    if not curr_secteur and curr_metier in by_label:
        curr_secteur = by_label[curr_metier].get("Secteur", "")

    # Libellés d'affichage pour la carte portrait
    metier_txt = curr_metier if curr_metier else "<em>Non assigné</em>"
    fgj_txt = curr_fgj if curr_fgj else "N/A"
    sect_txt = curr_secteur if curr_secteur else ("Polyvalent (FPT)" if eleve_row["PARCOURS"] == "FPT" else "En attente d'assignation")

    # En-tête institutionnel Portrait de la fiche ID
    header_html = (
        '<div style="background: linear-gradient(135deg, #004075 0%, #005596 100%); color: white; padding: 14px 16px; border-radius: 10px; text-align: center; margin-bottom: 14px; box-shadow: 0 3px 8px rgba(0,85,150,0.25);">'
        '<div style="font-size: 0.70rem; letter-spacing: 1px; text-transform: uppercase; color: #BAE6FD;">Centre de services scolaire Marguerite-Bourgeoys</div>'
        '<div style="font-weight: 800; font-size: 1.15rem; margin-top: 2px;">FICHE ID ÉLÈVE PFAE</div>'
        '<div style="display: inline-block; background: rgba(255,255,255,0.2); border-radius: 12px; padding: 2px 10px; font-size: 0.72rem; margin-top: 4px;">Année scolaire 2026-2027</div>'
        '</div>'
        '<div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 10px; padding: 14px; margin-bottom: 14px;">'
        '<div style="display: flex; align-items: center; gap: 14px; border-bottom: 1px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 10px;">'
        '<div style="background: #E2E8F0; width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.6rem; border: 2px solid #005596;">👤</div>'
        '<div>'
        '<div style="font-size: 0.72rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Numéro d\'Élève</div>'
        f'<div style="font-size: 1.4rem; font-weight: 800; color: #0F172A; line-height: 1.1;">{eleve_row["NO_ELEVE"]}</div>'
        f'<span style="background: #0284C7; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">Parcours {eleve_row["PARCOURS"]}</span>'
        '</div>'
        '</div>'
        '<div style="font-size: 0.84rem; line-height: 1.6; color: #334155;">'
        f'<div><strong>🏫 Établissement :</strong> {eleve_row["NOM_ECOLE"]}</div>'
        f'<div><strong>👨‍🏫 Enseignant responsable :</strong> {eleve_row["ENSEIGNANT_STAGE"]}</div>'
        f'<div><strong>📋 Cours de stage :</strong> {eleve_row["COURS_STAGE"]}</div>'
        '</div>'
        '<div style="margin-top: 8px; padding-top: 8px; border-top: 1px dashed #CBD5E1; font-size: 0.84rem; color: #334155;">'
        f'<div><strong>💼 Métier semi-spécialisé :</strong> {metier_txt}</div>'
        f'<div><strong>🏷️ Code FGJ :</strong> <span style="background: #E0F2FE; color: #0369A1; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-family: monospace;">{fgj_txt}</span> &nbsp;|&nbsp; <strong>🏢 Secteur :</strong> {sect_txt}</div>'
        '</div>'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # Feux de circulation
    st.markdown("##### 🚦 Feux de circulation & Alertes")
    c_ind1, c_ind2 = st.columns(2)
    with c_ind1:
        st.caption("Carnet de stage :")
        st.write(eleve_row["Statut Carnet"])
        st.caption("Évaluation mi-stage :")
        st.write(eleve_row["Alerte Évaluation"])
    with c_ind2:
        st.caption("Assiduité en stage :")
        st.write(eleve_row["Statut Absentéisme"])
        st.caption("En stage actif :")
        st.write("🟢 Oui" if eleve_row["EN_STAGE_ACTIF"] else "⚪ Non")

    st.markdown("---")
    # Champs modifiables dans le popup
    st.markdown("##### ✏️ Données opérationnelles & Métier RMS")

    # 1. Sélection du Secteur d'activité
    secteur_options = ["Tous les secteurs"] + all_secteurs
    init_secteur = curr_secteur if curr_secteur in all_secteurs else "Tous les secteurs"
    secteur_key = f"pop_secteur_{student_id}"

    if secteur_key not in st.session_state:
        st.session_state[secteur_key] = init_secteur

    idx_s = secteur_options.index(st.session_state[secteur_key]) if st.session_state[secteur_key] in secteur_options else 0
    pop_secteur = st.selectbox(
        "🏢 Secteur d'activité économique (RMS) :",
        options=secteur_options,
        index=idx_s,
        key=secteur_key,
        help="Filtrer la liste des métiers par secteur économique MEQ ou afficher tous les secteurs",
    )

    # 2. Sélection du Métier semi-spécialisé (filtré dynamiquement)
    if pop_secteur != "Tous les secteurs":
        df_sec = df_rms[df_rms["Secteur"] == pop_secteur]
        metiers_disponibles = [""] + sorted(df_sec["METIER_LABEL"].unique().tolist())
    else:
        metiers_disponibles = dm.get_rms_options()

    metier_key = f"pop_metier_{student_id}"
    if metier_key not in st.session_state:
        st.session_state[metier_key] = curr_metier if curr_metier in metiers_disponibles else ""

    curr_val = st.session_state.get(metier_key, "")
    if curr_val in metiers_disponibles:
        idx_m = metiers_disponibles.index(curr_val)
    elif curr_metier in metiers_disponibles:
        idx_m = metiers_disponibles.index(curr_metier)
    else:
        idx_m = 0

    pop_metier = st.selectbox(
        "💼 Métier semi-spécialisé officiel (MEQ) :",
        options=metiers_disponibles,
        index=idx_m,
        key=metier_key,
        help="Sélectionnez le métier semi-spécialisé officiel du répertoire MEQ pour cet élève",
    )

    if pop_metier:
        info_sel = by_label.get(pop_metier, {})
        sel_code = info_sel.get("Code_FGJ", "")
        sel_sec = info_sel.get("Secteur", "")
        st.markdown(
            f'<div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 6px 12px; margin-top: 2px; margin-bottom: 10px; font-size: 0.82rem; color: #166534;">'
            f'<strong>Code ministériel FGJ :</strong> <span style="font-family: monospace; font-weight: 700;">{sel_code}</span> &nbsp;|&nbsp; <strong>Secteur d\'activité :</strong> {sel_sec}'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.caption("ℹ️ *Aucun métier semi-spécialisé sélectionné (statut : Non assigné / Parcours d'insertion général).*")

    # 3. Champs opérationnels de stage
    pop_date = st.date_input(
        "Date de départ en stage :",
        value=eleve_row["Date de départ en stage"] if pd.notna(eleve_row["Date de départ en stage"]) else None,
        key=f"pop_date_{student_id}",
    )

    idx_carnet = dm.OPTIONS_CARNET.index(eleve_row["Carnet de stage?"]) if eleve_row["Carnet de stage?"] in dm.OPTIONS_CARNET else 0
    pop_carnet = st.selectbox(
        "Carnet de stage ?",
        options=dm.OPTIONS_CARNET,
        index=idx_carnet,
        key=f"pop_carnet_{student_id}",
    )

    idx_mi = dm.OPTIONS_MI_STAGE.index(eleve_row["Évaluation mi-stage"]) if eleve_row["Évaluation mi-stage"] in dm.OPTIONS_MI_STAGE else 0
    pop_mi = st.selectbox(
        "Évaluation mi-stage :",
        options=dm.OPTIONS_MI_STAGE,
        index=idx_mi,
        key=f"pop_mi_{student_id}",
    )

    pop_abs = st.number_input(
        "Jours d'absence cumulés :",
        min_value=0,
        max_value=150,
        value=int(eleve_row["Jours d'absence"]) if pd.notna(eleve_row["Jours d'absence"]) else 0,
        step=1,
        key=f"pop_abs_{student_id}",
    )

    pop_comm = st.text_area(
        "📝 Notes & Observations de stage :",
        value=str(eleve_row.get("Commentaires_Stage", "")),
        help="Saisie libre de commentaires, observations du superviseur ou de l'enseignant.",
        key=f"pop_comm_{student_id}",
    )

    st.write("")
    all_student_ids = filtered_df["NO_ELEVE"].tolist()
    curr_idx = all_student_ids.index(student_id) if student_id in all_student_ids else 0

    c_prev, c_save_pop, c_next, c_close_pop = st.columns([1.1, 2, 1.1, 1])

    with c_prev:
        if curr_idx > 0:
            if st.button("⏮️ Préc.", use_container_width=True, key=f"btn_prev_{student_id}"):
                st.session_state.popup_student_id = all_student_ids[curr_idx - 1]
                st.rerun()
        else:
            st.button("⏮️ Préc.", use_container_width=True, disabled=True, key=f"btn_prev_dis_{student_id}")

    with c_save_pop:
        if st.button("💾 Enregistrer la fiche", type="primary", use_container_width=True, key=f"btn_save_pop_{student_id}"):
            code_fgj_to_save = ""
            if pop_metier in by_label:
                code_fgj_to_save = by_label[pop_metier]["Code_FGJ"]
            elif " - " in pop_metier:
                cand = pop_metier.split(" - ")[0].strip()
                if cand.isdigit():
                    code_fgj_to_save = cand

            update_record = {
                "NO_ELEVE": student_id,
                "Metier_FMS": pop_metier,
                "Code_FGJ": code_fgj_to_save,
                "Date de départ en stage": pop_date,
                "Carnet de stage?": pop_carnet,
                "Évaluation mi-stage": pop_mi,
                "Jours d'absence": pop_abs,
                "Commentaires_Stage": pop_comm,
            }
            df_update = pd.DataFrame([update_record])
            with st.spinner("Enregistrement en mémoire locale et virtuelle..."):
                ok, msg = dm.save_student_data(df_update, csv_file_path)
                if ok:
                    st.session_state.save_status_msg = f"Fiche de {student_id} enregistrée avec succès !"
                    st.session_state.download_ready_csv_bytes = dm.get_latest_csv_bytes(csv_file_path)
                    st.session_state.download_ready_filename = f"Listes_profs_élèves_FMS-FPT_26-27_MAJ_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    st.session_state.show_popup_dialog = False
                    st.cache_data.clear()
                    st.toast(f"{student_id} mis à jour !", icon="✅")
                    st.rerun()
                else:
                    st.error(f"Erreur : {msg}")

    with c_next:
        if curr_idx < len(all_student_ids) - 1:
            if st.button("Suiv. ⏭️", use_container_width=True, key=f"btn_next_{student_id}"):
                st.session_state.popup_student_id = all_student_ids[curr_idx + 1]
                st.rerun()
        else:
            st.button("Suiv. ⏭️", use_container_width=True, disabled=True, key=f"btn_next_dis_{student_id}")

    with c_close_pop:
        if st.button("Fermer", use_container_width=True, key=f"btn_close_pop_{student_id}"):
            st.session_state.show_popup_dialog = False
            st.rerun()

    # Accordéon des 11 rôles pour FMS
    if eleve_row["PARCOURS"] == "FMS" or pop_metier or "196204" in str(eleve_row.get("COURS_STAGE", "")):
        with st.expander("🛠️ Les 11 rôles de la classe-atelier et du stage FMS", expanded=False):
            for role_num, role_title, role_desc in dm.ROLES_CLASSE_ATELIER_FMS:
                st.markdown(f"**{role_num} — {role_title}**  \n*{role_desc}*")

    # Accordéon des cours détaillés
    with st.expander("📚 Grille complète des cours inscrits", expanded=False):
        courses = eleve_row.get("COURS_DETAILS", [])
        if courses:
            for c in courses:
                titre = c["TITRE_COURS"] if c["TITRE_COURS"] else c["Description"]
                st.markdown(
                    f"• **{c['CD_COURS']}** — {titre}  \n"
                    f"  *Enseignant :* {c['NOM_ENSEIGN']} | *Établissement :* {c['NOM_ECOLE']}"
                )
        else:
            st.caption("Aucun cours inscrit.")


# --- APPLICATION DES FILTRES SUR LA VUE ÉLÈVE ---
filtered_df = df_student_view.copy()

# 1. Filtre École
if choix_ecole != "Toutes les écoles":
    filtered_df = filtered_df[filtered_df["NOM_ECOLE"] == choix_ecole]

# 2. Filtre Parcours
if choix_parcours != "Tous":
    filtered_df = filtered_df[filtered_df["PARCOURS"] == choix_parcours]

# 3. Filtre Enseignant
if choix_enseignant != "Tous les enseignants":
    filtered_df = filtered_df[
        filtered_df["LISTE_ENSEIGNANTS"].apply(lambda profs: choix_enseignant in profs)
    ]

# 4. Filtre Secteur d'activité RMS
if choix_secteurs_rms:
    filtered_df = filtered_df[
        filtered_df["Secteur_RMS"].isin(choix_secteurs_rms)
    ]

# 5. Filtre Recherche par N° d'élève
if recherche_eleve.strip():
    terme = recherche_eleve.strip()
    filtered_df = filtered_df[
        filtered_df["NO_ELEVE"].astype(str).str.contains(terme, na=False)
    ]

# Filtres rapides cliquables depuis les KPIs
if st.session_state.quick_filter == "RETARD":
    filtered_df = filtered_df[filtered_df["STATUT_MI_CODE"] == "RETARD"]
elif st.session_state.quick_filter == "CRITIQUE_ABS":
    filtered_df = filtered_df[filtered_df["STATUT_ABS_CODE"] == "CRITIQUE"]
elif st.session_state.quick_filter == "STAGE_ACTIF":
    filtered_df = filtered_df[filtered_df["EN_STAGE_ACTIF"] == True]
elif st.session_state.quick_filter == "VIGILANCE_ALL":
    filtered_df = filtered_df[
        (filtered_df["STATUT_MI_CODE"].isin(["RETARD", "A_PLANIFIER"]))
        | (filtered_df["STATUT_ABS_CODE"].isin(["CRITIQUE", "VIGILANCE"]))
    ]


# --- CALCUL DES MÉTRIQUES GLOBALES ---
total_eleves = len(df_student_view)
total_filtres = len(filtered_df)
eleves_en_stage = int(df_student_view["EN_STAGE_ACTIF"].sum())
nb_carnets_valides = int((df_student_view["Carnet de stage?"] == "Validé").sum())
pct_carnets_valides = round((nb_carnets_valides / total_eleves * 100.0), 1) if total_eleves > 0 else 0.0

nb_eval_retard = int((df_student_view["STATUT_MI_CODE"] == "RETARD").sum())
nb_abs_critique = int((df_student_view["STATUT_ABS_CODE"] == "CRITIQUE").sum())
nb_a_planifier = int((df_student_view["STATUT_MI_CODE"] == "A_PLANIFIER").sum())

date_analyse_formatee = f"{ref_date.day} {MOIS_FR[ref_date.month - 1]} {ref_date.year}"


# --- BANDEAU INSTITUTIONNEL SUPÉRIEUR ---
st.markdown(
    f"""
    <div class="cssmb-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
            <div>
                <h1>🎓 Suivi des Stages PFAE 2026-2027</h1>
                <p>Centre de services scolaire Marguerite-Bourgeoys | Suivi et Fiches de Stage (Version Anonymisée)</p>
                <div class="law25-badge">
                    <span>🔒 Données 100% Anonymisées (élève-* / enseignant-*)</span>
                    <span>•</span>
                    <span>💻 Sauvegarde Active sur ce Portable</span>
                    <span>•</span>
                    <span>⚡ Conforme Loi 25 (WebAssembly)</span>
                </div>
            </div>
            <div style="text-align: right; margin-top: 5px;">
                <span style="font-size: 0.85rem; color: #E0F2FE;">Date d'analyse :</span><br/>
                <strong style="font-size: 1.15rem; color: #FFFFFF;">{date_analyse_formatee}</strong>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --- BANDEAU SUPÉRIEUR KPI ---
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Élèves PFAE</div>
            <div class="kpi-value">{total_eleves}</div>
            <div class="kpi-subtitle">FMS : {(df_student_view['PARCOURS'] == 'FMS').sum()} | FPT : {(df_student_view['PARCOURS'] == 'FPT').sum()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col2:
    pct_en_stage = round((eleves_en_stage / total_eleves * 100), 1) if total_eleves > 0 else 0
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Élèves en Stage Actif</div>
            <div class="kpi-value" style="color: #0284C7;">{eleves_en_stage}</div>
            <div class="kpi-subtitle">{pct_en_stage} % des effectifs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Carnets Validés</div>
            <div class="kpi-value" style="color: #16A34A;">{pct_carnets_valides} %</div>
            <div class="kpi-subtitle">{nb_carnets_valides} carnets validés</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col4:
    color_retard = "#DC2626" if nb_eval_retard > 0 else "#16A34A"
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left: 4px solid {color_retard};">
            <div class="kpi-title">Mi-Stage en Retard</div>
            <div class="kpi-value" style="color: {color_retard};">{nb_eval_retard}</div>
            <div class="kpi-subtitle">{nb_a_planifier} à planifier sous peu</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_col5:
    color_abs = "#DC2626" if nb_abs_critique > 0 else "#16A34A"
    st.markdown(
        f"""
        <div class="kpi-card" style="border-left: 4px solid {color_abs};">
            <div class="kpi-title">Absentéisme Critique</div>
            <div class="kpi-value" style="color: {color_abs};">{nb_abs_critique}</div>
            <div class="kpi-subtitle">Taux > {seuil_critique_abs:.0f} % (seuil rupture)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# --- BARRE DE FILTRAGE RAPIDE INTERACTIF ---
quick_col1, quick_col2, quick_col3, quick_col4, quick_col5, quick_col6 = st.columns([1.5, 2.2, 2.2, 2, 2, 1.8])

with quick_col1:
    if st.button("Tous les élèves", use_container_width=True, type="primary" if st.session_state.quick_filter == "ALL" else "secondary"):
        st.session_state.quick_filter = "ALL"
        st.rerun()

with quick_col2:
    label_retard = f"🔴 Retards Mi-Stage ({nb_eval_retard})"
    if st.button(label_retard, use_container_width=True, type="primary" if st.session_state.quick_filter == "RETARD" else "secondary"):
        st.session_state.quick_filter = "RETARD"
        st.rerun()

with quick_col3:
    label_abs = f"🔴 Absentéisme Critique ({nb_abs_critique})"
    if st.button(label_abs, use_container_width=True, type="primary" if st.session_state.quick_filter == "CRITIQUE_ABS" else "secondary"):
        st.session_state.quick_filter = "CRITIQUE_ABS"
        st.rerun()

with quick_col4:
    label_stage = f"🔵 En Stage Actif ({eleves_en_stage})"
    if st.button(label_stage, use_container_width=True, type="primary" if st.session_state.quick_filter == "STAGE_ACTIF" else "secondary"):
        st.session_state.quick_filter = "STAGE_ACTIF"
        st.rerun()

with quick_col5:
    label_vig = "🟡 Vigilances globales"
    if st.button(label_vig, use_container_width=True, type="primary" if st.session_state.quick_filter == "VIGILANCE_ALL" else "secondary"):
        st.session_state.quick_filter = "VIGILANCE_ALL"
        st.rerun()

with quick_col6:
    if st.session_state.quick_filter != "ALL":
        if st.button("✖ Effacer filtre", use_container_width=True):
            st.session_state.quick_filter = "ALL"
            st.rerun()


# --- SECTION PRINCIPALE DU TABLEAU DE BORD ---
tabs = st.tabs(["📋 Grille Élèves (élève-*)", "👨‍🏫 Grille Enseignants (enseignant-*)", "📊 Répartition & Analyses", "💾 Sauvegardes sur Portable & Modèles"])

with tabs[0]:
    # Notification d'enregistrement
    if st.session_state.save_status_msg:
        st.success(st.session_state.save_status_msg, icon="💾")
        st.session_state.save_status_msg = None

    # Encart de téléchargement synchrone proposé immédiatement lors de toute modification
    if st.session_state.download_ready_csv_bytes:
        st.info(
            "💾 **Modifications enregistrées avec succès sur ce portable.**  \n"
            "Vos modifications sont conservées dans le stockage local de votre navigateur. "
            "Vous pouvez également télécharger une copie physique du fichier CSV actualisé :"
        )
        c_dl1, c_dl2 = st.columns([3, 1])
        with c_dl1:
            st.download_button(
                label="💾 Enregistrer le CSV sur mon portable",
                data=st.session_state.download_ready_csv_bytes,
                file_name=st.session_state.download_ready_filename or "Listes_profs_élèves_FMS-FPT_26-27_MAJ.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True,
                key="btn_download_saved_csv_tab0",
            )
        with c_dl2:
            if st.button("Masquer", use_container_width=True, key="btn_dismiss_save_alert"):
                st.session_state.download_ready_csv_bytes = None
                st.rerun()

    # Barre d'actions au-dessus du tableau
    action_left, action_right1, action_right2, action_save = st.columns([4, 1.4, 1.4, 2.2])

    with action_left:
        active_filter_desc = []
        if choix_ecole != "Toutes les écoles":
            active_filter_desc.append(choix_ecole)
        if choix_parcours != "Tous":
            active_filter_desc.append(f"Parcours {choix_parcours}")
        if choix_enseignant != "Tous les enseignants":
            active_filter_desc.append(f"Prof: {choix_enseignant}")
        if choix_secteurs_rms:
            active_filter_desc.append(f"Secteur(s) RMS: {', '.join(choix_secteurs_rms)}")
        if st.session_state.quick_filter != "ALL":
            active_filter_desc.append(f"Filtre rapide [{st.session_state.quick_filter}]")

        filter_txt = " | ".join(active_filter_desc) if active_filter_desc else "Aucun filtre actif (vue d'ensemble)"
        st.markdown(f"**Affichage :** `{len(filtered_df)} élève(s)` sur `{total_eleves}` — *{filter_txt}*")

    with action_right1:
        excel_data = dm.export_dataframe_to_excel(filtered_df)
        st.download_button(
            label="📥 Excel (.xlsx)",
            data=excel_data,
            file_name=f"Suivi_Stages_PFAE_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Télécharger les données filtrées au format Excel avec colonnes de suivi.",
        )

    with action_right2:
        csv_data = dm.export_dataframe_to_csv(filtered_df)
        st.download_button(
            label="📥 CSV (.csv)",
            data=csv_data,
            file_name=f"Suivi_Stages_PFAE_{datetime.date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Télécharger les données filtrées au format CSV (encodage UTF-8 BOM pour Excel francophone).",
        )

    # Barre d'accès rapide Fiche ID
    bar_col1, bar_col2, bar_col3 = st.columns([3.5, 3.5, 2])
    with bar_col1:
        st.markdown("💡 *Cochez la case **🔍 Fiche** en colonne A pour ouvrir la **Fiche ID Portrait**.*")
    with bar_col2:
        liste_ids_filtres = filtered_df["NO_ELEVE"].tolist()
        if liste_ids_filtres:
            quick_pick_id = st.selectbox(
                "Accès rapide Fiche Élève :",
                options=liste_ids_filtres,
                format_func=lambda x: f"{x} — {filtered_df[filtered_df['NO_ELEVE'] == x]['NOM_ECOLE'].iloc[0]}",
                key="quick_pick_fiche_id",
                label_visibility="collapsed",
            )
        else:
            quick_pick_id = None
    with bar_col3:
        if liste_ids_filtres:
            if st.button("🔍 Ouvrir la Fiche ID", use_container_width=True, key="btn_open_quick_fiche"):
                st.session_state.popup_student_id = quick_pick_id
                afficher_fiche_id_popup(quick_pick_id)

    # Accordéon de création manuelle d'une fiche élève
    with st.expander("➕ Saisie manuelle : Ajouter une nouvelle fiche élève", expanded=False):
        st.markdown("*Remplissez ce formulaire pour créer manuellement une nouvelle fiche élève anonymisée.*")
        existing_nums = []
        for sid in df_raw["NO_ELEVE"].astype(str):
            if sid.startswith("Élève-"):
                try:
                    existing_nums.append(int(sid.replace("Élève-", "")))
                except ValueError:
                    pass
        next_num = (max(existing_nums) + 1) if existing_nums else 1
        suggested_id = f"Élève-{next_num:03d}"

        c_add1, c_add2, c_add3 = st.columns(3)
        with c_add1:
            new_id = st.text_input("Identifiant élève :", value=suggested_id, help="Format recommandé : Élève-XXX", key="inp_new_id")
            ecole_keys = sorted(list(set(df_raw["CD_ECOLE"].unique())))
            new_ecole = st.selectbox("Établissement scolaire :", options=ecole_keys, format_func=lambda k: dm.format_school_display(k), key="inp_new_ecole")
        with c_add2:
            new_parcours = st.radio("Parcours :", options=["FMS", "FPT"], horizontal=True, key="inp_new_parcours")
            new_prof = st.selectbox("Enseignant responsable :", options=enseignants_list if enseignants_list else ["Enseignant-01"], key="inp_new_prof")
        with c_add3:
            default_cd = "196204" if new_parcours == "FMS" else "108234"
            new_course_code = st.text_input("Code du cours :", value=default_cd, key="inp_new_course_cd")
            default_titre = "Préparation à l'exercice d'un métier semi-spécialisé (stage)" if new_parcours == "FMS" else "Insertion professionnelle (stage)"
            new_course_title = st.text_input("Titre du cours :", value=default_titre, key="inp_new_course_titre")

        if st.button("➕ Enregistrer la nouvelle fiche", type="primary", use_container_width=True, key="btn_create_student_tab0"):
            if not new_id.strip():
                st.error("Veuillez saisir un identifiant valide.")
            else:
                ok_add, msg_add = dm.add_new_student(
                    student_id=new_id.strip(),
                    school_code=str(new_ecole).strip(),
                    parcours=new_parcours,
                    teacher_name=new_prof,
                    course_code=new_course_code.strip(),
                    course_title=new_course_title.strip(),
                    csv_path=csv_file_path,
                )
                if ok_add:
                    st.toast(msg_add, icon="✅")
                    st.session_state.save_status_msg = msg_add
                    st.session_state.download_ready_csv_bytes = dm.get_latest_csv_bytes(csv_file_path)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(msg_add)

    # Configuration des colonnes pour le st.data_editor
    display_columns = [
        "NO_ELEVE",
        "NOM_ECOLE",
        "PARCOURS",
        "ENSEIGNANT_STAGE",
        "COURS_STAGE",
        "Metier_FMS",
        "Secteur_RMS",
        "Date de départ en stage",
        "Carnet de stage?",
        "Évaluation mi-stage",
        "Jours d'absence",
        "Statut Carnet",
        "Alerte Évaluation",
        "Statut Absentéisme",
    ]

    df_for_editor = filtered_df[display_columns].copy()
    df_for_editor.insert(0, "🔍", False)

    column_config = {
        "🔍": st.column_config.CheckboxColumn(
            "🔍 Fiche",
            help="Cochez la case pour ouvrir la Fiche d'identification portrait de cet élève",
            default=False,
            width="small",
        ),
        "NO_ELEVE": st.column_config.TextColumn(
            "Élève (Anonymisé)",
            help="Identifiant anonymisé de l'élève (élève-*)",
            disabled=True,
            width="small",
        ),
        "NOM_ECOLE": st.column_config.TextColumn(
            "Établissement",
            help="École d'appartenance ou de stage",
            disabled=True,
            width="medium",
        ),
        "PARCOURS": st.column_config.TextColumn(
            "Parcours",
            help="FMS ou FPT",
            disabled=True,
            width="small",
        ),
        "ENSEIGNANT_STAGE": st.column_config.TextColumn(
            "Enseignant responsable",
            help="Enseignant responsable du stage ou de l'élève",
            disabled=True,
            width="medium",
        ),
        "COURS_STAGE": st.column_config.TextColumn(
            "Cours de Stage",
            help="Libellé du cours de stage lié",
            disabled=True,
            width="medium",
        ),
        "Metier_FMS": st.column_config.SelectboxColumn(
            "Métier semi-spécialisé (MEQ)",
            help="Sélectionnez le métier officiel MEQ",
            options=dm.get_rms_options(),
            required=False,
            disabled=False,
            width="large",
        ),
        "Secteur_RMS": st.column_config.TextColumn(
            "Secteur RMS",
            help="Secteur économique MEQ associé au métier",
            disabled=True,
            width="medium",
        ),
        "Date de départ en stage": st.column_config.DateColumn(
            "Date Départ Stage",
            help="Sélectionnez la date de départ effectif en stage",
            format="YYYY-MM-DD",
            disabled=False,
            width="medium",
        ),
        "Carnet de stage?": st.column_config.SelectboxColumn(
            "Carnet de stage ?",
            help="État du carnet de stage de l'élève",
            options=dm.OPTIONS_CARNET,
            required=True,
            disabled=False,
            width="medium",
        ),
        "Évaluation mi-stage": st.column_config.SelectboxColumn(
            "Éval. Mi-stage",
            help="État ou réalisation de l'évaluation mi-stage",
            options=dm.OPTIONS_MI_STAGE,
            required=True,
            disabled=False,
            width="medium",
        ),
        "Jours d'absence": st.column_config.NumberColumn(
            "Jours Absence",
            help="Nombre total de jours d'absence cumulés en stage",
            min_value=0,
            max_value=150,
            step=1,
            format="%d",
            disabled=False,
            width="small",
        ),
        "Statut Carnet": st.column_config.TextColumn(
            "Indicateur Carnet",
            help="Pastille visuelle du carnet",
            disabled=True,
            width="medium",
        ),
        "Alerte Évaluation": st.column_config.TextColumn(
            "Alerte Mi-Stage",
            help="Délai calculé selon la date de départ (seuil 12 sem. FMS / 20 sem. FPT)",
            disabled=True,
            width="large",
        ),
        "Statut Absentéisme": st.column_config.TextColumn(
            "Alerte Absentéisme",
            help="Taux d'absence calculé selon les jours prévus",
            disabled=True,
            width="medium",
        ),
    }

    # Le tableau interactif st.data_editor
    edited_data = st.data_editor(
        df_for_editor,
        column_config=column_config,
        disabled=[
            "NO_ELEVE",
            "NOM_ECOLE",
            "PARCOURS",
            "ENSEIGNANT_STAGE",
            "COURS_STAGE",
            "Secteur_RMS",
            "Statut Carnet",
            "Alerte Évaluation",
            "Statut Absentéisme",
        ],
        hide_index=True,
        use_container_width=True,
        key="main_student_editor",
    )

    # Détection si une case 🔍 a été cochée en colonne A
    if "🔍" in edited_data.columns:
        checked_rows = edited_data[edited_data["🔍"] == True]
        if len(checked_rows) > 0:
            target_id = str(checked_rows.iloc[0]["NO_ELEVE"])
            st.session_state.popup_student_id = target_id
            afficher_fiche_id_popup(target_id)

    with action_save:
        if st.button("💾 Enregistrer les modifications", type="primary", use_container_width=True):
            with st.spinner("Sauvegarde synchrone en mémoire virtuelle..."):
                success, msg = dm.save_student_data(edited_data, csv_file_path)
                if success:
                    st.session_state.save_status_msg = msg
                    st.session_state.download_ready_csv_bytes = dm.get_latest_csv_bytes(csv_file_path)
                    st.session_state.download_ready_filename = f"Listes_profs_élèves_FMS-FPT_26-27_MAJ_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    st.cache_data.clear()
                    st.toast(msg, icon="✅")
                    st.rerun()
                else:
                    st.error(f"Erreur d'enregistrement : {msg}")

    st.write("")

    # --- VOLET DÉTAIL / FICHE ÉLÈVE (DRILL-DOWN) ---
    st.markdown("### 🔍 Dossier Détaillé de l'Élève (Drill-Down)")

    liste_options_eleves = filtered_df["NO_ELEVE"].tolist()
    if not liste_options_eleves:
        st.info("Aucun élève ne correspond aux critères de filtre sélectionnés.")
    else:
        idx_default = 0
        if (
            st.session_state.selected_student_id
            and st.session_state.selected_student_id in liste_options_eleves
        ):
            idx_default = liste_options_eleves.index(st.session_state.selected_student_id)

        col_sel_eleve, col_sel_info = st.columns([3, 4])
        with col_sel_eleve:
            choix_id = st.selectbox(
                "Sélectionner un élève pour afficher sa charge globale et ses cours :",
                options=liste_options_eleves,
                index=idx_default,
                format_func=lambda x: f"{x} — {filtered_df[filtered_df['NO_ELEVE'] == x]['NOM_ECOLE'].iloc[0]} ({filtered_df[filtered_df['NO_ELEVE'] == x]['PARCOURS'].iloc[0]})",
            )
            st.session_state.selected_student_id = choix_id

        eleve_row = filtered_df[filtered_df["NO_ELEVE"] == choix_id].iloc[0]

        with st.container():
            st.markdown(
                f"""
                <div class="drilldown-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 12px; margin-bottom: 12px; flex-wrap: wrap;">
                        <div>
                            <h3 style="margin: 0; color: #005596;">Fiche de Suivi — {eleve_row['NO_ELEVE']}</h3>
                            <span style="font-size: 0.9rem; color: #475569;">
                                <strong>Établissement :</strong> {eleve_row['NOM_ECOLE']} &nbsp;|&nbsp; 
                                <strong>Parcours :</strong> <span style="background: #E0F2FE; color: #0369A1; padding: 2px 8px; border-radius: 4px; font-weight: 600;">{eleve_row['PARCOURS']}</span> &nbsp;|&nbsp;
                                <strong>Enseignant Stage :</strong> {eleve_row['ENSEIGNANT_STAGE']}
                            </span>
                        </div>
                        <div style="margin-top: 8px;">
                            <span style="margin-right: 12px;"><strong>Carnet :</strong> {eleve_row['Statut Carnet']}</span>
                            <span style="margin-right: 12px;"><strong>Mi-stage :</strong> {eleve_row['Alerte Évaluation']}</span>
                            <span><strong>Absentéisme :</strong> {eleve_row['Statut Absentéisme']}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Encadré Répertoire des Métiers Semi-Spécialisés (RMS) / FPT
            if eleve_row["PARCOURS"] == "FMS" or eleve_row.get("Metier_FMS") or "196204" in str(eleve_row.get("COURS_STAGE", "")):
                metier_nom = eleve_row["Metier_FMS"] if eleve_row.get("Metier_FMS") else "Aucun métier semi-spécialisé assigné pour le moment"
                code_fgj_txt = eleve_row["Code_FGJ"] if eleve_row.get("Code_FGJ") else "Non renseigné"
                secteur_txt = eleve_row["Secteur_RMS"] if eleve_row.get("Secteur_RMS") else "En attente d'assignation"
                st.markdown(
                    f'<div class="rms-card">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">'
                    f'<div><span class="rms-badge">RÉPERTOIRE DES MÉTIERS SEMI-SPÉCIALISÉS (MEQ)</span></div>'
                    f'<div style="font-size: 0.85rem; color: #0284C7; font-weight: 700;">Code ministériel FGJ : <span style="background: #E0F2FE; padding: 2px 8px; border-radius: 4px; font-family: monospace;">{code_fgj_txt}</span></div>'
                    f'</div>'
                    f'<div style="font-size: 1.12rem; font-weight: 700; color: #0F172A; margin-bottom: 4px;">🛠️ {metier_nom}</div>'
                    f'<div style="font-size: 0.88rem; color: #475569;"><strong>Secteur d\'activité économique :</strong> {secteur_txt}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                with st.expander("📋 Compétences spécifiques & Les 11 rôles de la classe-atelier / stage FMS", expanded=False):
                    st.markdown("*Chaque métier semi-spécialisé s'articule autour des 11 rôles et compétences clés en milieu de travail :*")
                    r_col1, r_col2 = st.columns(2)
                    for i, (r_num, r_title, r_desc) in enumerate(dm.ROLES_CLASSE_ATELIER_FMS):
                        target_col = r_col1 if i % 2 == 0 else r_col2
                        with target_col:
                            st.markdown(
                                f'<div style="background: white; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px 12px; margin-bottom: 8px;">'
                                f'<div style="font-weight: 700; font-size: 0.85rem; color: #005596;">{r_num} — {r_title}</div>'
                                f'<div style="font-size: 0.78rem; color: #64748B; margin-top: 2px;">{r_desc}</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
            else:
                st.markdown(
                    '<div style="background: #F8FAFC; border: 1px solid #CBD5E1; border-left: 5px solid #64748B; border-radius: 8px; padding: 12px 16px; margin: 12px 0;">'
                    '<div style="font-weight: 700; color: #334155;">🎯 Parcours Formation Préparatoire au Travail (FPT3)</div>'
                    '<div style="font-size: 0.85rem; color: #64748B; margin-top: 4px;">Les stages du parcours FPT développent des compétences d\'insertion socioprofessionnelle générales (polyvalence, autonomie, ponctualité) menant à un certificat général sans rattachement obligatoire à un métier semi-spécialisé unique.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

            # Grille complète des cours d'origine
            st.markdown("##### 📚 Grille complète des cours inscrits pour cet élève :")
            courses_list = eleve_row["COURS_DETAILS"]
            if courses_list:
                df_student_courses = pd.DataFrame(courses_list)
                df_student_courses = df_student_courses.rename(
                    columns={
                        "CD_COURS": "Code Cours",
                        "TITRE_COURS": "Titre Officiel du Cours",
                        "Description": "Description Fichier",
                        "FONCTION": "Fonction / Rôle",
                        "NOM_ENSEIGN": "Enseignant Responsable",
                        "NOM_ECOLE": "École Dispensatrice",
                    }
                )
                colonnes_ordre = [
                    "Code Cours",
                    "Description Fichier",
                    "Titre Officiel du Cours",
                    "Fonction / Rôle",
                    "Enseignant Responsable",
                    "École Dispensatrice",
                ]
                st.dataframe(
                    df_student_courses[colonnes_ordre],
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.info("Aucun détail de cours enregistré pour cet élève.")


with tabs[1]:
    st.markdown("### 👨‍🏫 Grille de Suivi par Enseignant (enseignant-*)")
    st.markdown(
        "Cette vue synthétise la charge d'encadrement, les effectifs d'élèves, l'avancement des carnets, les évaluations de stage et l'assiduité sous la responsabilité de chaque enseignant anonymisé (`Enseignant-01` à `Enseignant-38`)."
    )

    df_teachers = dm.get_teacher_summary(df_student_view)

    # Métriques clés enseignants
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1:
        st.metric("Total Enseignants Répertoriés", f"{len(df_teachers)}")
    with t_col2:
        profs_avec_stage = int((df_teachers["En Stage Actif"] > 0).sum())
        st.metric("Enseignants avec Stages Actifs", f"{profs_avec_stage} / {len(df_teachers)}")
    with t_col3:
        profs_retard = int((df_teachers["Éval. en Retard"] > 0).sum())
        st.metric("Enseignants avec Éval. en Retard", f"{profs_retard}", delta=f"-{profs_retard}" if profs_retard > 0 else "0", delta_color="inverse")
    with t_col4:
        profs_abs_crit = int((df_teachers["Abs. Critique (>15%)"] > 0).sum())
        st.metric("Enseignants avec Abs. Critique", f"{profs_abs_crit}", delta=f"-{profs_abs_crit}" if profs_abs_crit > 0 else "0", delta_color="inverse")

    st.write("")
    c_dl_t1, c_dl_t2, c_search_t = st.columns([1.5, 1.5, 3])
    with c_dl_t1:
        csv_t_bytes = df_teachers.to_csv(sep=";", index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="📥 Télécharger CSV Enseignants",
            data=csv_t_bytes,
            file_name=f"Grille_Synthese_Enseignants_{datetime.date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c_dl_t2:
        xlsx_t_bytes = dm.export_dataframe_to_excel(df_teachers)
        st.download_button(
            label="📥 Télécharger Excel Enseignants",
            data=xlsx_t_bytes,
            file_name=f"Grille_Synthese_Enseignants_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with c_search_t:
        search_prof = st.text_input("🔍 Filtrer les enseignants :", placeholder="Ex: Enseignant-04, Dalbé-Viau...", label_visibility="collapsed", key="search_prof_tab1")

    df_teachers_disp = df_teachers.copy()
    if search_prof.strip():
        sp = search_prof.strip().lower()
        df_teachers_disp = df_teachers_disp[
            df_teachers_disp["Enseignant"].str.lower().str.contains(sp)
            | df_teachers_disp["Établissement(s)"].str.lower().str.contains(sp)
        ]

    st.dataframe(
        df_teachers_disp,
        column_config={
            "Enseignant": st.column_config.TextColumn("Enseignant (enseignant-*)", width="medium"),
            "Établissement(s)": st.column_config.TextColumn("Établissement(s)", width="large"),
            "Total Élèves": st.column_config.NumberColumn("Total Élèves", format="%d", width="small"),
            "Élèves FMS": st.column_config.NumberColumn("FMS", format="%d", width="small"),
            "Élèves FPT": st.column_config.NumberColumn("FPT", format="%d", width="small"),
            "En Stage Actif": st.column_config.NumberColumn("En Stage", format="%d", width="small"),
            "Carnets Validés": st.column_config.NumberColumn("Carnets OK", format="%d", width="small"),
            "Carnets En Cours": st.column_config.NumberColumn("Carnets En Cours", format="%d", width="small"),
            "Éval. Réalisées": st.column_config.NumberColumn("Éval. OK", format="%d", width="small"),
            "Éval. en Retard": st.column_config.NumberColumn("Éval. Retard", format="%d", width="small"),
            "Abs. Critique (>15%)": st.column_config.NumberColumn("Abs. Critique", format="%d", width="small"),
            "Moy. Abs. (j)": st.column_config.NumberColumn("Moy. Abs. (j)", format="%.1f j", width="small"),
        },
        hide_index=True,
        use_container_width=True,
    )


with tabs[2]:
    st.markdown("### 📊 Répartition et Indicateurs PFAE (2026-2027)")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("##### 🏫 Répartition des élèves par établissement")
        ecole_counts = (
            df_student_view["NOM_ECOLE"]
            .value_counts()
            .reset_index()
            .rename(columns={"NOM_ECOLE": "Établissement", "count": "Nombre d'élèves"})
        )
        st.bar_chart(
            ecole_counts.set_index("Établissement"),
            color="#005596",
            use_container_width=True,
        )

    with chart_col2:
        st.markdown("##### 📖 Progression de distribution des carnets de stage")
        carnet_counts = (
            df_student_view["Carnet de stage?"]
            .value_counts()
            .reindex(dm.OPTIONS_CARNET, fill_value=0)
            .reset_index()
            .rename(columns={"Carnet de stage?": "Statut", "count": "Nombre"})
        )
        st.bar_chart(
            carnet_counts.set_index("Statut"),
            color="#0284C7",
            use_container_width=True,
        )

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.markdown("##### ⏱️ État des évaluations mi-stage (Feux de circulation)")
        mi_stage_summary = (
            df_student_view["STATUT_MI_CODE"]
            .map(
                {
                    "ATTENTE": "⚪ En attente de départ",
                    "FUTUR": "⚪ Départ à venir",
                    "REALISEE": "🟢 Réalisée",
                    "DANS_DELAIS": "🟢 Dans les délais",
                    "A_PLANIFIER": "🟡 À planifier sous peu",
                    "RETARD": "🔴 En retard",
                }
            )
            .value_counts()
            .reset_index()
            .rename(columns={"STATUT_MI_CODE": "État", "count": "Nombre"})
        )
        st.dataframe(
            mi_stage_summary,
            hide_index=True,
            use_container_width=True,
        )

    with chart_col4:
        st.markdown("##### ⚠️ Synthèse de l'assiduité en stage")
        abs_summary = (
            df_student_view["STATUT_ABS_CODE"]
            .map(
                {
                    "NORMAL": "🟢 Normal (< 8 %)",
                    "VIGILANCE": "🟡 Vigilance (8 à 15 %)",
                    "CRITIQUE": "🔴 Critique (> 15 %)",
                }
            )
            .value_counts()
            .reset_index()
            .rename(columns={"STATUT_ABS_CODE": "Niveau d'assiduité", "count": "Nombre"})
        )
        st.dataframe(
            abs_summary,
            hide_index=True,
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("##### 💼 Répartition des élèves FMS par secteur d'activité économique (RMS)")

    df_fms = df_student_view[df_student_view["PARCOURS"] == "FMS"]
    total_fms = len(df_fms)
    assigned_fms = int((df_fms["Metier_FMS"].astype(str).str.strip() != "").sum())
    pct_assigned = round((assigned_fms / total_fms * 100), 1) if total_fms > 0 else 0.0

    rms_col_left, rms_col_right = st.columns([1.3, 2.7])
    with rms_col_left:
        st.markdown(
            f"""
            <div class="kpi-card" style="border-left: 4px solid #0284C7; margin-bottom: 12px;">
                <div class="kpi-title">Élèves FMS avec Métier Assigné</div>
                <div class="kpi-value" style="color: #0284C7;">{assigned_fms} / {total_fms}</div>
                <div class="kpi-subtitle">{pct_assigned} % des effectifs FMS</div>
            </div>
            <div class="kpi-card" style="border-left: 4px solid #005596;">
                <div class="kpi-title">Répertoire MEQ (RMS)</div>
                <div class="kpi-value" style="font-size: 1.5rem; color: #005596;">64 Métiers</div>
                <div class="kpi-subtitle">Répartis sur 15 secteurs d'activité officiels</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with rms_col_right:
        fms_secteurs = (
            df_fms["Secteur_RMS"]
            .replace({"": "En attente d'assignation"})
            .value_counts()
            .reset_index()
        )
        fms_secteurs.columns = ["Secteur d'activité", "Nombre d'élèves"]
        st.bar_chart(
            fms_secteurs.set_index("Secteur d'activité"),
            color="#0284C7",
            horizontal=True,
            use_container_width=True,
        )


with tabs[3]:
    st.markdown("### 💾 Sauvegarde Locale & Persistance sur Portable (Loi 25)")
    st.markdown(
        """
        <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-left: 5px solid #16A34A; border-radius: 8px; padding: 16px 20px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <span style="font-size: 1.4rem;">💻</span>
                <span style="font-weight: 700; color: #166534; font-size: 1.05rem;">Persistance Locale Client-Side Active</span>
            </div>
            <div style="font-size: 0.88rem; color: #14532D; line-height: 1.5;">
                • <strong>Conformité stricte Loi 25 :</strong> Zéro transmission réseau, aucun serveur distant, exécution 100 % sécurisée dans votre navigateur.<br/>
                • <strong>Sauvegarde permanente sur ce portable :</strong> Vos modifications manuelles et fiches sont automatiquement conservées dans le stockage local (<code>localStorage</code>) du navigateur. Même si vous quittez la page ou redémarrez votre ordinateur, vos données restent intactes.<br/>
                • <strong>Téléchargement sur disque :</strong> Vous pouvez à tout instant télécharger une copie physique du fichier CSV maître ou Excel pour vos archives.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c_dl_tab3_csv, c_dl_tab3_xlsx, c_dl_tab3_tmpl = st.columns(3)
    with c_dl_tab3_csv:
        st.download_button(
            label="💾 Enregistrer le CSV sur mon portable",
            data=dm.get_latest_csv_bytes(csv_file_path),
            file_name=f"Listes_profs_élèves_FMS-FPT_26-27_Anonymise_{datetime.date.today().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
            help="Télécharger le fichier CSV maître complet et actualisé sur votre ordinateur portable",
        )
    with c_dl_tab3_xlsx:
        st.download_button(
            label="📊 Télécharger la synthèse Excel (.xlsx)",
            data=dm.export_dataframe_to_excel(df_student_view),
            file_name=f"Synthese_Stages_PFAE_Anonymise_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Télécharger la synthèse complète au format Excel",
        )
    with c_dl_tab3_tmpl:
        df_template = df_student_view[["NO_ELEVE", "NOM_ECOLE", "PARCOURS", "ENSEIGNANT_STAGE", "COURS_STAGE", "Metier_FMS", "Date de départ en stage", "Carnet de stage?", "Évaluation mi-stage", "Jours d'absence", "Commentaires_Stage"]].copy()
        tmpl_bytes = dm.export_dataframe_to_excel(df_template)
        st.download_button(
            label="📄 Télécharger grille vierge (Excel)",
            data=tmpl_bytes,
            file_name=f"Grille_Saisie_Manuelle_PFAE_Vierge_{datetime.date.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            help="Grille modèle pour impression ou saisie manuelle",
        )

    st.markdown("---")
    backup_folder = os.path.join(os.path.dirname(csv_file_path), "backups")
    if os.path.exists(backup_folder):
        backup_files = sorted(
            glob.glob(os.path.join(backup_folder, "*.bak")),
            key=os.path.getmtime,
            reverse=True,
        )
        if backup_files:
            st.markdown("##### 🗄️ Sauvegardes intermédiaires de la session courante")
            b_list = []
            for b in backup_files:
                st_info = os.stat(b)
                mtime_dt = datetime.datetime.fromtimestamp(st_info.st_mtime)
                size_kb = round(st_info.st_size / 1024.0, 1)
                b_list.append({
                    "Fichier de sauvegarde": os.path.basename(b),
                    "Date et Heure": mtime_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "Taille (Ko)": size_kb,
                })
            df_backups = pd.DataFrame(b_list)
            st.dataframe(df_backups, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 🔄 Réinitialisation aux données anonymisées par défaut")
    st.caption("Si vous souhaitez effacer vos modifications locales et repartir du jeu de données anonymisé d'origine :")
    confirm_reset = st.checkbox("Je confirme vouloir réinitialiser toutes les saisies locales aux valeurs d'origine.", key="chk_confirm_reset")
    if confirm_reset:
        if st.button("⚠️ Réinitialiser le fichier maître", type="secondary", key="btn_exec_reset"):
            try:
                import js
                if hasattr(js, "window") and hasattr(js.window, "pfaeClearLaptopStorage"):
                    js.window.pfaeClearLaptopStorage()
                elif hasattr(js, "localStorage"):
                    js.localStorage.removeItem("pfae_stages_saved_csv")
                    js.localStorage.removeItem("pfae_stages_last_save")
            except Exception:
                pass
            st.cache_data.clear()
            st.success("Données locales réinitialisées avec succès !")
            st.rerun()


# --- OUVERTURE DE LA FICHE ID POPUP (DIALOG) ---
if st.session_state.get("show_popup_dialog") and st.session_state.get("popup_student_id"):
    target_id = st.session_state.popup_student_id
    st.session_state.show_popup_dialog = False
    afficher_fiche_id_popup(target_id)
