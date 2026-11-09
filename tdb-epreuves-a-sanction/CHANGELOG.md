# Changelog - Refactorisation Learning Analytics Dashboards (LAD)

Toutes les modifications notables apportées au projet `tdb-ingenierie-pedagogique` sont documentées ici.

---

## [2.3.1] - Inversion des Couleurs de Fond & Révision des Titres de Navigation

### Inversion des Couleurs de Fond (Barre Latérale Bleu-Vert Pâle & Fenêtre Principale Blanche)
- **Barre latérale (`stSidebar`)** : Application de la couleur de fond bleu-vert pâle `--sidebar-bg: #e8f4f6` (conforme WCAG AAA avec contraste 14.2:1 sur texte ardoise `#0f172a`).
- **Fenêtre principale (`stApp`)** : Application du fond blanc pur `--bg: #ffffff` pour une lisibilité maximale des données, graphiques Plotly et tableaux interactifs.
- **Synchronisation tripartite** : Mise à jour harmonisée de `style-quebec.css`, `ui/theme.py` (`QUEBEC_CSS`), et du gabarit `index.html`.

### Révision de la Navigation et de la Page d'Atterrissage
- **Intitulés de la barre de navigation** : Cohérence stricte et ordonnée de la hiérarchie :
  1. `Accueil & Cadre Opérationnel` : Page d'atterrissage avec titre institutionnel *Tableau de Bord : Suivi des Matières à Sanction* et blocs d'orientation Macro, Méso, Micro et GPS.
  2. `1. Macro : Pilotage Systémique & Diplomation`
  3. `2. Méso : Équité & Modération des Notes`
  4. `3. Micro : Diagnostic des Épreuves & Classes`
  5. `4. Prescription : Triage GPS & Diplomation`
- **Correction des textes d'accueil** : Nettoyage du libellé pour le téléversement du Plan d'intervention (PI/EHDAA) et harmonisation de la formulation du palier Méso.
- **Empaquetage WebAssembly/Stlite** : Synchronisation complète de l'ensemble des modules Python et styles dans `index.html` pour exécution locale hors-ligne conforme Loi 25.

---

## [2.3.0] - Refactorisation Navigation, Architecture Hiérarchique & Questionnement Décisionnel

### Architecture de Navigation & Sidebar
- **Gradation logique et hiérarchique (Macro → Méso → Micro → Triage)** :
  1. `Accueil & Cadre Opérationnel` : Page d'atterrissage stratégique avec matrice de cohérence opérationnelle, bandeau Loi 25 et ingestion mémoire.
  2. `1. Macro : Pilotage Systémique & Diplomation` : Risque d'échec systémique, cibles PEVR, cumul des vulnérabilités (Venn 4e/5e), dépendance disciplinaire ($\Phi$ de Pearson), matrice 4 quadrants et bilan GPS.
  3. `2. Méso : Équité & Modération des Notes` : Risque de biais d'évaluation, 3 représentations NEB vs NMC (étalon ministériel, cohérence réseau OLS $\pm 1{,}5\sigma$, compression), audit systémique des surévaluations et matrice 4 quadrants.
  4. `3. Micro : Diagnostic des Épreuves & Classes` : Risque d'inégalité intra-muros et de rupture didactique, comparaison évaluations locales vs épreuves uniques, détection de la ségrégation interne (dispersion groupes réguliers $> 15\,\%$) et outliers d'écrasement.
  5. `4. Prescription : Triage GPS & Diplomation` : Triage prescriptif individualisé, suivi des candidats GPS (55-59 %, échecs multiples, risque de diplomation) avec filtres RETAC, école et matière.
- **Règle d'or respectée** : Zéro suppression de code ni de métriques/visualisations. Seuls les libellés, sous-titres, bandeaux d'intention et la hiérarchie ont été optimisés.

---

## [2.2.0] - Conformité Charte Gouvernement du Québec (style-quebec.css) & Élimination des Émojis

### Charte Graphique & Style Sobre
- **Normes Gouvernement du Québec (`style-quebec.css`)** :
  - Palette officielle intégrée : `--primary: #1472BF` (Bleu standard), `--secondary: #095797` (Bleu PIV foncé), `--accent: #f59e0b` (Ambre/Or), `--danger: #ef4444`, `--success: #10b981`, `--bg: #f1f5f9`, `--panel: #ffffff`, `--border: #cbd5e1`, `--text: #0f172a`, `--muted: #64748b`.
  - Typographie institutionnelle sobre : `system-ui, -apple-system, sans-serif`.
  - Création du fichier `style-quebec.css` à la racine et injection dynamique dans l'application Streamlit (`ui.theme.inject_quebec_theme()`).
- **Élimination intégrale des émojis** :
  - Suppression de tous les émojis dans l'ensemble des modules Python (`Tableau_de_bord.py`, pages 1 à 4, composants `ui/` et alertes `core/privacy.py`).
  - Suppression des émojis dans l'enveloppe `index.html` (remplacement du favicon et de l'icône de chargement par des tracés vectoriels SVG géométriques institutionnels, badges textuels sobres).
  - Remplacement des symboles dans les statuts et légendes graphiques par des étiquettes textuelles claires et des formes vectorielles discrètes (normes WCAG AA).

### Refactorisation Ergonomique & Docimologique - Modération (Page 3)
- **Harmonisation et standardisation stricte des axes** :
  - Axe X (abscisse, variable étalon) : `Moyenne de l'Épreuve Ministère (%)`.
  - Axe Y (ordonnée, variable évaluée) : `Moyenne de l'École (%)`.
  - Redressement docimologique du Graphique B ($Y_{\text{école}} = a \cdot X_{\text{ministère}} + b$, corridor $\pm 1{,}5\sigma$, résidu positif = indulgence critique au-dessus de la bande, résidu négatif = sévérité critique en dessous).
- **Structure en sections distinctes avec Boîtes d'aide à l'interprétation** :
  - Disposition côte-à-côte de chaque graphique avec son callout d'interprétation (`st.info`) sur deux lignes indépendantes.
  - Graphique A : *« A. Écart à l'Épreuve Ministérielle (Diagonale d'Équité y = x) »* avec questions métier et explication des phénomènes absolus (indulgence brute, sévérité brute, compression).
  - Graphique B : *« B. Comparaison à la Norme du Réseau (Tendance Globale & Groupes Atypiques) »* avec mention discrète de $R^2$ et explication docimologique des résiduels extrêmes.
  - Masquage par défaut des groupes conformes (`visible="legendonly"`), maintien du seuil de filtrage $N \ge 16$ élèves.

---

## [2.1.0] - Itération Bleu Québec & Alignement MACRO / MÉSO / MICRO

### ⚜️ Charte Graphique & Identité
- **Style Bleu Québec officiel** : Intégration du bleu fleurdelisé (`#0033A0`), fond doux (`#EDF2FC`), or québécois (`#C88A1A`) et icône fleurdelisée `⚜️`.
- **CSS Stlite** : Alignement des variables CSS de l'enveloppe HTML sur les couleurs québécoises.

### 🏛️ MACRO : Pilotage Stratégique & Équité (Page 1)
- **Détection universelle du niveau** : Extraction robuste du niveau du secondaire via `code_str[-3]` (4 pour 4e sec, 5 pour 5e sec).
- **Rapatriement des Profils d'Échecs de 4e sec.** : Diagramme de Venn 3 ensembles (Sciences, Maths, Histoire).
- **Matrice de corrélation des échecs** : Heatmap Plotly croisant les matières à sanction et validée par p-values d'un test $t$ pairé.
- **Ventilations enrichies** :
  - Volume d'échecs (1, 2, 3) par établissement (barres empilées).
  - Répartition par genre (M/F) avec support du fichier de correspondance.
  - Répartition par Plan d'intervention (PI / EHDAA).
- **Synthèse stratégique GPS de Diplomation** : Vue d'ensemble pour l'école d'été (candidats examen 55-59% vs cours 50-54% vs échecs multiples).

### 🔍 MÉSO : Modération & Calibrage Docimologique (Page 3)
- **Synthèse des 3 représentations NEB vs NMC** :
  - Dispersion brute autour de la droite d'équilibre $y=x$.
  - Modélisation OLS bivariée avec bandes de tolérance $\pm 1.5\sigma$ et détection des outliers résiduels.
  - Analyse de la compression de variance (Ratio $R < 0.6$) avec explication docimologique dédiée.
- **Nuance docimologique de la surperformance** : Documentation claire rappelant qu'une sous-évaluation annuelle génère un stress de performance excessif chez l'élève.
- **Seuils et ergonomie** : Slider de taille de groupe ajustable de 0 à 24 (valeur par défaut = 16 élèves).
- **Masquage par défaut des cercles "Normal"** : Activé via `visible="legendonly"` dans Plotly pour libérer l'attention sur les anomalies.
- **Comparaisons d'anomalies d'indulgence** :
  - Par discipline / matière (`CD_COURS`).
  - Par établissement (DGA).
  - Par typologie de groupe (Régulier 01-12, PEI 30-35, Concentration 50-55, EHDAA 80-85, Cas particuliers 90-99).
- **Matrice 4 quadrants rapatriée** : Positionnée ici avec le tableau de drill-down des groupes prioritaires à accompagner (Quadrant 1).

### 🔬 MICRO : Diagnostic des Épreuves & Ségrégation (Page 2)
- **Affichage unifié sans onglets** : Présentation directe et superposée de la réussite aux disciplines et aux épreuves uniques ministérielles avec IC Wilson 95%.
- **Détection de la ségrégation interne** : Analyse de la dispersion des taux de réussite entre classes régulières d'une même école, avec exclusion automatique des groupes EHDAA (80-85) et cas particuliers (90-99).
- **Outliers d'écrasement de la note école** : Tableau priorisé isolant les groupes dont le ratio d'écrasement dévie anormalement de la norme ($\pm 1.5\sigma$).
- **Filtres d'exclusion** : Curseur de taille de groupe (défaut 16) et case à cocher pour exclure les cours enrichis (058404/058402).

### 🛠️ Outil Autonome `predict_sexe.py`
- Création d'un script Python 100 % local et déterministe (sans appel réseau, conforme Loi 25) basé sur la banque des prénoms du Québec pour déduire le genre (M/F) et générer le fichier de correspondance `CD_PERMN, SEXE`.


## [2.0.0] - Refactorisation Complète LAD & Conformance

### 🏛️ Architecture & Refactoring Core
- **Création du package `core/`** :
  - `core/schema.py` : Unification de toutes les constantes métier (`SUBJECT_MAP`, `ECOLES_LIST`, `ECOLES_SECTEURS`, codes enrichis, codes épreuves). Élimination définitive des duplications entre `MATIERES_CIBLES_FULL`, `SANCTION_MATIERES_MAP` et les pages.
  - `core/metrics.py` : Fonctions mathématiques pures et testables (`wilson_interval`, `compute_success_rate`, `compute_cohen_d`, `compute_gini`, `compute_ols_regression`, `compute_quadrants`).
  - `core/privacy.py` : Module de conformité Loi 25 (suppression et masquage des cellules $< 5$ élèves, alertes $N < 15$, anonymisation des enseignants).
  - `core/state.py` : Source unique de vérité (SSOT) préservée dans `st.session_state` sans `.copy()` inutile, filtres partagés persistants.
  - `core/data_loader.py` : Ingestion robuste des CSV, sanitisation Arrow2 pour Stlite, downcasting mémoire optimisé.

### 🎨 Expérience Visuelle & Principes LAD (Package `ui/`)
- **Création du package `ui/`** :
  - `ui/theme.py` : Palette daltonien-safe (Okabe-Ito), contrastes conformes WCAG AA. L'état n'est jamais codé par la couleur seule (icônes + formes + couleurs).
  - `ui/kpi_cards.py` : Cartes KPI à feux tricolores, mention obligatoire de $N$, intervalle de confiance Wilson IC 95% et badge de volatilité si $N < 15$.
  - `ui/action_panel.py` : Composant `render_action_panel(question, constat_dynamique, pistes)` calculant le constat en temps réel sur les filtres actifs.
  - `ui/explainers.py` : Expanders d'explication pédagogique pour décharger la vue principale du jargon statistique ($d$ de Cohen, Gini, R/Q, OLS).
  - `ui/filters.py` : Filtres unifiés et synchronisés dans la barre latérale avec sliders what-if dynamiques.
  - `ui/charts.py` : Graphiques Plotly accessibles avec barres d'erreur Wilson et symboles redondants.

### 📑 Recomposition des Pages par Persona
- **Page 1 : `1_Pilotage_Strategique_Equite.py` (Direction)** :
  - Synthèse macro en 3 KPIs (Taux de réussite global, Écart moyen NEB-NMC, % de notes écrasées).
  - Nuage de points NEB vs NMC avec droite d'équilibre $y=x$.
  - Matrice 4 quadrants décisionnelle (Biais théorique $\times$ Sévérité pratique).
  - Drill-down interactif vers les groupes prioritaires à accompagner.
- **Page 2 : `2_Diagnostic_des_epreuves.py` (Conseillers pédagogiques)** :
  - Taux de réussite aux disciplines et aux épreuves uniques avec marges d'erreur IC 95%.
  - Diagramme de Venn natif Plotly des échecs multiples de 4e secondaire (Sciences, Maths, Histoire).
- **Page 3 : `3_Moderation.py` (Direction & Conseillers)** :
  - Positionnement NEB/NMC, audit des anomalies docimologiques et facteurs de modération R et Q.
  - Correction de la mention textuelle statique « plus de 16 élèves », désormais 100 % dynamique selon le curseur.
  - Valeur par défaut du slider portée à 5 élèves pour respect de la confidentialité.
- **Page 4 : `4_Triage_et_Prescription.py` (École d'été)** :
  - Tableau de triage priorisé des élèves en échec frontière (50-59%) et échecs multiples.
  - Moteur de prescription pédagogique automatisée (Examen de reprise vs Cours d'été vs Plan concerté).
- **Page 5 : `5_Avance_Labo.py` (Laboratoire de recherche)** :
  - Espace de recherche clairement balisé « Exploratoire ».
  - Calcul standardisé de l'Indice de Gini et de la Courbe de Lorenz.
  - Régression linéaire ordinaire (OLS) et détection des outliers résiduels ($\pm k\sigma$).
  - Histogramme et diagnostic de l'écrasement des notes par le MEQ.

### 🧹 Dette Technique Corrigée
- **Code mort** : Suppression de `4_Sandbox_Moyennes.py` (doublon strict de la page 3).
- **Incohérence d'étiquettes Mathématiques corrigée** : Dans l'ancien bac à sable, « Math (Résoudre) » était erronément mappé sur les codes de « Raisonner » (63420, 65420, 64420). Le référentiel `core/schema.py` attribue désormais l'épreuve unique ministérielle à « Raisonner » et les codes 63410, 65410, 64410 à « Résoudre » avec test unitaire dédié.
- **Formule de l'Indice de Gini corrigée** : Remplacement de la formule incomplète du bac à sable (qui retournait $0.33$ sur des notes identiques) par la formule officielle standardisée vérifiée par test unitaire ($G=0.0$ pour des notes identiques).
- **Mutation de state neutralisée** : Suppression des mutations directes (`df_global_cohort['...'] = ...`) au profit d'une sélection de colonnes propre sans altération du state.
- **Filtres globaux unifiés** : La sélection de filtres dans `Tableau_de_bord.py` est désormais partagée et respectée de manière consistante dans tous les modules.

### 📦 Intégration Client Stlite WebAssembly
- Régénération intégrale de `index.html` avec la nouvelle arborescence de fichiers dans `stliteConfig.files`.
- Aucune dépendance externe ajoutée (conforme au périmètre `["pandas", "numpy", "plotly", "scipy", "openpyxl"]`).
