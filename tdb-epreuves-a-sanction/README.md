# Tableau de Bord - Ingénierie Pédagogique & Modération (LAD)

Application d'aide à la décision 100 % client (**Stlite / Pyodide / WebAssembly**) pour l'analyse des résultats ministériels réguliers, la compréhension des tables de modération des notes-écoles (**CHS040506R**) et le suivi des réussites scolaires (**CHAP060105**).

🔒 **Conformité stricte Loi 25 (Québec)** : Le traitement s'exécute intégralement dans la mémoire vive du navigateur. Aucune donnée nominative ou statistique ne transite sur un serveur distant.

---

## 🏛️ Architecture Modulaire

Le projet est structuré selon une séparation stricte entre logique statistique pure, composants visuels décisionnels et modules par persona :

```
├── Tableau_de_bord.py             # Accueil, téléversement et indexation mémoire
├── boot.py                         # Module de préchauffage (Warmup) Stlite/Pyodide
├── index.html                      # Enveloppe client autonome Stlite 0.80.5
├── core/                           # Logique métier pure et déterministe (zéro effet de bord)
│   ├── schema.py                   # Nomenclature unifiée (écoles, épreuves, matières, codes enrichis)
│   ├── metrics.py                  # Fonctions mathématiques pures (Wilson, Cohen d, Gini, OLS, Quadrants)
│   ├── privacy.py                  # Règles Loi 25 : suppression des cellules < 5, gestion opt-in
│   ├── state.py                    # Single Source of Truth (SSOT) et filtres persistants
│   └── data_loader.py              # Ingestion tolérante, downcasting mémoire et fusion vectorisée
├── ui/                             # Composants d'interface conformes aux principes LAD
│   ├── theme.py                    # Palette daltonien-safe (Okabe-Ito), contrastes WCAG AA
│   ├── kpi_cards.py                # Cartes KPI à feux tricolores (couleur + forme/icône, N, IC Wilson)
│   ├── action_panel.py             # Panneau décisionnel dynamique (Question -> Constat -> Pistes)
│   ├── explainers.py               # Expanders d'explication pédagogique des concepts statistiques
│   ├── filters.py                  # Barre latérale unifiée et filtres what-if
│   └── charts.py                   # Graphiques Plotly accessibles (nuages de points, Venn, barres avec IC)
├── pages/                          # Modules applicatifs orientés Persona / Décision
│   ├── 1_Pilotage_Strategique_Equite.py  # Direction (Macro : 3 KPIs, NEB/NMC, Quadrants, Drill-down)
│   ├── 2_Diagnostic_des_epreuves.py      # Conseillers pédagogiques (Méso : Épreuves, Venn 4e, IC)
│   ├── 3_Moderation.py                   # Direction & CP (Diagnostic : Nuage NEB/NMC, Facteurs R et Q)
│   ├── 4_Triage_et_Prescription.py       # École d'été (Micro : Triage 50-59%, Priorisation d'action)
│   └── 5_Avance_Labo.py                  # Laboratoire (Exploratoire : Gini, OLS résidus, Écrasement)
└── tests/                          # Suite de tests unitaires et de non-régression (pytest)
    ├── test_metrics.py
    ├── test_privacy.py
    ├── test_schema.py
    ├── test_ui.py
    └── test_non_regression.py
```

---

## 🎯 Principes LAD Appliqués (Learning Analytics Dashboards)

| Principe LAD | Implémentation dans la solution | Référence théorique |
| :--- | :--- | :--- |
| **P1. Du coup d'œil au détail** | Architecture à 4 niveaux : Synthèse (Macro) → Ventilations (Méso) → Diagnostic (Micro) → Données désensibilisées. | Voyer (2011), Dumaresq (2017) |
| **P2. Donnée → Insight → Action** | Composant unique `render_action_panel(question, constat_dynamique, pistes)` calculant le constat directement sur les filtres actifs. | Matcha et al. (2020) |
| **P3. Métaphores visuelles** | Feux tricolores avec seuils paramétrables, matrices 4 quadrants, nuages de points avec ligne d'équilibre $y=x$. | Few (2013) |
| **P4. Communication de l'incertitude** | Affichage systématique de $N$ sur chaque indicateur, intervalles de confiance Wilson (IC 95%), avertissement automatique si $N < 15$. | Verbert et al. (2014) |
| **P5. Interactivité guidée** | Filtres persistants unifiés dans la barre latérale (`core.state`), sliders « what-if » docimologiques. | Matcha et al. (2020) |
| **P6. Accessibilité inclusive** | Palette daltonien-safe (Okabe-Ito), contrastes WCAG AA. L'état n'est **jamais** codé par la couleur seule (icône + forme + couleur). | WCAG 2.1 AA |
| **P7. Charge cognitive minimale** | $\le 5$ éléments visuels au premier écran par page, pas de mur de texte, priorité à la lisibilité décisionnelle. | Sweller (1988), Few (2013) |
| **P8. Transparence et éthique** | Bloc « À propos de ces données », suppression systématique des cellules $< 5$ élèves (Loi 25), opt-in requis pour l'affichage enseignant. | Verbert et al. (2020) |

---

## 🗺️ Cartographie Page → Persona → Niveau Voyer → Question décisionnelle

| Page | Persona prioritaire | Niveau Voyer | Question décisionnelle directrice |
| :--- | :--- | :--- | :--- |
| **1. Pilotage Stratégique & Équité** | Directions d'école, Direction générale | Niveau 1 : Synthèse (Macro) | *Quel est l'état d'équité global de notre établissement et quels groupes doivent faire l'objet d'un accompagnement didactique prioritaire ?* |
| **2. Diagnostic des Épreuves** | Conseillers pédagogiques, Directions | Niveau 2 : Ventilations (Méso) | *Quelles compétences et épreuves spécifiques présentent des fragilités systémiques justifiant une intervention ciblée ?* |
| **3. Modération des Notes-Écoles** | Conseillers pédagogiques, Directions | Niveau 3 : Diagnostic (Micro) | *Où se situent les biais d'évaluation interne (indulgence / sévérité) par rapport au barème ministériel et aux facteurs R/Q ?* |
| **4. Triage & Prescription** | Coordonnateurs école d'été, Réussite | Niveau 4 : Prescription opérationnelle | *Quels élèves prioriser dans l'offre de cours et d'examens d'été pour maximiser les diplomations dès la session d'août ?* |
| **5. Laboratoire & Biais** | Analystes, Recherche docimologique | Niveau Exploratoire | *Quelles sont les dynamiques complexes d'inégalité (Gini/Lorenz) et les résidus de surperformance dans nos cohortes ?* |

---

## 🧪 Validation & Non-Régression

La suite de tests unitaires valide l'ensemble des modules :

```bash
# Lancement des tests automatisés
python3 -m pytest tests
```

### Critères validés :
1. ✅ **Exactitude mathématique** : Wilson exact, formule standard du coefficient de Gini, OLS bivarié et classification d'anomalies.
2. ✅ **Non-régression fonctionnelle** : Identité stricte des résultats avant et après refactorisation sur jeux de données synthétiques.
3. ✅ **Conformité Loi 25** : Masquage systématique des petites cellules ($N < 5$), mention explicite, et désensibilisation des enseignants.
4. ✅ **Zéro dépendance non autorisée** : Respect absolu du périmètre `["pandas", "numpy", "plotly", "scipy", "openpyxl"]`.

