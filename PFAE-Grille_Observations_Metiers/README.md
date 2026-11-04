# Grille d'Observation des Métiers Semi-Spécialisés (PFAE)

> **Outil pédagogique officiel pour les programmes de formation axée sur l'emploi (FMS / FPT)**  
> Conforme aux exigences du Ministère de l'Éducation du Québec (MEQ), aux recueils de métiers semi-spécialisés et au standard d'évaluation en milieu de stage.

[![100% Client-Side](https://img.shields.io/badge/Architecture-100%25%20Client--Side-095797.svg)](#)
[![Loi 25 Québec](https://img.shields.io/badge/Conformit%C3%A9-Loi%2025%20Qu%C3%A9bec-0f766e.svg)](#)
[![Sans dépendance](https://img.shields.io/badge/D%C3%A9pendances-Z%C3%A9ro-success.svg)](#)
[![GitHub Pages Ready](https://img.shields.io/badge/D%C3%A9ploiement-GitHub%20Pages-blue.svg)](#)

---

## 🎯 À quoi sert cette application ?

Cette application web monopage (*Single Page Application*) ultra-légère permet aux enseignants de FMS / FPT, aux techniciens en éducation spécialisée (TES), aux conseillers pédagogiques et aux superviseurs de stage de :

1. **Transformer les tâches d'un métier semi-spécialisé** en grilles d'observation et d'évaluation claires, aérées et structurées par compétence.
2. **Produire des documents d'évaluation haute fidélité** 100 % compatibles avec le modèle officiel ministériel (mise en page A4 / Lettre, 1 compétence par page, colonnes d'évaluation `1 | 2 | 3 | 4`, colonnes de commentaires et bilan d'évolution).
3. **Générer des prompts optimisés pour Microsoft Copilot et Google Gemini institutionnels** afin d'extraire, nettoyer et structurer instantanément les tâches du programme ministériel en respectant la stricte confidentialité scolaire.
4. **Imprimer directement ou exporter** en PDF vectoriel net et en document Microsoft Word (`.doc`) sans nécessiter d'installation de logiciel lourd ni de serveur.

---

## ✨ Points forts & Conception québécoise

* **Style épuré aux couleurs du Québec :** Palette officielle institutionnelle (`#002855`, `#095797`, `#f4f6f9`), typographie accessible et sans éléments superflus, assurant un rendu irréprochable au photocopieur d'école noir et blanc.
* **Format rigide identique au PDF exemple :** Chaque compétence dispose de son tableau de tâches (6 colonnes), de son tableau de critères de performance SST/qualité (5 colonnes) et de sa ligne de bilan/plan d'évolution.
* **100 % hors-ligne & Respect strict de la Loi 25 :** Aucun compte requis, aucune transmission de données sur des serveurs distants, aucun traqueur. Toutes les grilles sont traitées dans la mémoire de votre navigateur et peuvent être sauvegardées localement en JSON.
* **Légèreté absolue pour GitHub :** Aucun `node_modules`, aucun processus de build requis. Un simple `index.html`, un fichier CSS et deux fichiers JS.

---

## 🚀 Utilisation immédiate (sans installation)

### Méthode 1 : En local sur votre ordinateur
1. Téléchargez le dossier ou clonez le dépôt :
   ```bash
   git clone https://github.com/[votre-utilisateur]/PFAE-Grille_Observations_Metiers.git
   ```
2. Faites un simple **double-clic sur `index.html`**.
3. L'application s'ouvre instantanément dans votre navigateur habituel (Chrome, Edge, Firefox, Safari).

### Méthode 2 : Déploiement en 1 clic sur GitHub Pages
1. Déposez les fichiers sur votre dépôt GitHub.
2. Allez dans **Settings > Pages**.
3. Choisissez la branche `main` (ou `master`) et le dossier `/ (root)`.
4. Cliquez sur **Save**. Votre application est en ligne gratuitement et accessible sur n'importe quel ordinateur ou tablette en milieu de stage !

---

## 🧭 Parcours en 4 étapes simples

```
[1. Saisie & Métier] ➔ [2. Prompt Copilot/Gemini] ➔ [3. Édition & Ajustements] ➔ [4. Impression / Export]
```

### Étape 1 : Saisie & Métier
* Choisissez un métier pré-rempli (*Aide-concierge 8332, Aide-cuisinier 8312, Commis d'épicerie 8321, Préposé paysager 8342*) ou saisissez vos propres informations.
* Vous pouvez également coller une liste brute de tâches (ex: issue d'un PDF ministériel) : le module les découpe et les convertit automatiquement en compétence avec critères SST.

### Étape 2 : Prompts IA institutionnels (Copilot / Gemini)
* Sélectionnez votre plateforme : **Microsoft Copilot** (Microsoft 365 Éducation) ou **Google Gemini** (compte institutionnel CSS).
* Cliquez sur **« Copier le prompt dans le presse-papiers »**.
* Collez-le dans votre IA scolaire. Elle vous retournera les compétences et critères structurés.
* Collez la réponse de l'IA dans l'encadré et cliquez sur **« Importer la réponse dans la grille »**.

### Étape 3 : Édition de la grille
* Ajustez les libellés, réordonnez les compétences, ajoutez ou supprimez des tâches et des critères de performance observables en milieu de travail.
* Vos modifications sont automatiquement conservées dans votre navigateur (`localStorage`).

### Étape 4 : Visualisation & Impression
* **Impression / PDF (<kbd>Ctrl</kbd> + <kbd>P</kbd>) :** Rendu vectoriel parfait au format Lettre US ou A4 avec saut de page automatique par compétence.
* **Export Word (.doc) :** Fichier Word éditable prêt à être partagé ou intégré dans les dossiers d'élèves.
* **Sauvegarde JSON :** Exportez et réimportez vos grilles d'une année à l'autre ou partagez-les entre collègues de département.

---

## 📂 Structure du projet

```
PFAE-Grille_Observations_Metiers/
├── index.html                   # Interface web principale (monopage autonome)
├── css/
│   └── style-quebec.css         # Design System Québec & feuille d'impression rigide @media print
├── js/
│   ├── app.js                   # Moteur interactif, navigation, parseur IA, exports
│   └── data-metiers.js          # Référentiel de métiers semi-spécialisés (PFAE - MEQ)
├── exemple-grilles-concierge.pdf # Modèle PDF de référence
├── PFAE_Grille-metiers.py       # Script Python historique de génération Word (.docx)
├── MODE_EMPLOI.md               # Guide d'utilisation détaillé pour les enseignants
└── README.md                    # Présentation et documentation technique
```

---

## 🔒 Confidentialité & Conformité Loi 25

Conformément aux normes québécoises de protection des renseignements personnels dans le secteur de l'éducation :
- Aucune donnée nominative n'est envoyée à des tiers.
- Le traitement du texte s'effectue entièrement dans le moteur JavaScript local du navigateur.
- L'utilisation de Copilot ou Gemini se fait au choix de l'utilisateur dans son propre compte sécurisé fourni par son Centre de services scolaire.

---

*Projet conçu pour les équipes du Programme de formation de l'école québécoise (PFAE).*
