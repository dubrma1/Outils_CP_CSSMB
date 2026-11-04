# 📚 Planificateur PFAE (FPT 1, 2, 3 & FMS) — Application Web Québécoise

Application web interactive de planification pédagogique pour les programmes de la **Formation axée sur l'emploi (PFAE)** au Québec :
- **FPT 1** (Formation préparatoire au travail - An 1 : Ateliers & Consolidation)
- **FPT 2** (Formation préparatoire au travail - An 2 : Stages 1 à 2 jours)
- **FPT 3** (Formation préparatoire au travail - An 3 : Stages intensifs 3 jours)
- **FMS** (Formation menant à l'exercice d'un métier semi-spécialisé - 1 an / Stage 375h)

L'application est **100 % côté client (Vanilla HTML5, CSS3, JavaScript ES6)**. Elle s'exécute instantanément, sans aucun serveur backend, **directement en local via `file:///`** ou en ligne sur **GitHub Pages** et **Azure Static Web Apps**.

---

## ⚜️ Style épuré aux couleurs du Québec
- **Palette officielle :** Bleu royal québécois (`#095797`), Bleu nuit profond (`#002855`), Bleu accent interactif (`#1472bf`), fond neutre haute lisibilité (`#f4f6f9`).
- **Fleur-de-lys stylisée** et design conforme aux normes graphiques gouvernementales du Québec et du CSSMB.
- **Mise en page optimisée pour l'impression (Ctrl+P / Cmd+P) :** Format paysage soigné pour les réunions multidisciplinaires, bilans d'étapes et plans de transition (TÉVA).

---

## 🎯 Fonctionnalités principales

1. **Parcours PFAE complets :**
   - Bascule fluide entre `FPT 1`, `FPT 2`, `FPT 3` et `FMS`.
   - Charge instantanément les disciplines, codes de cours ministériels, compétences ministérielles (C1, C2, C3) et pondérations officielles aux bulletins scolaires.

2. **Planification par matière en 3 colonnes (Modèle Dalbé-Viau) :**
   - Division claire par étapes de bulletins :
     - **Étape 1 :** 20 % (Automne)
     - **Étape 2 :** 20 % (Hiver)
     - **Étape 3 :** 60 % (Printemps / Bilan)
   - **Interactivité totale :**
     - 🖱️ **Glisser-déposer (Drag & Drop) :** Déplacez intuitivement les cartes d'une étape à l'autre.
     - ⬅️ / ➡️ : Déplacement instantané d'un thème entre colonnes d'étapes.
     - ⬆️ / ⬇️ : Réordonnancement de la position du thème au sein de sa colonne.
     - ✏️ : Boîte de dialogue pour modifier le titre, la description, les compétences ciblées, la durée en semaines, l'axe thématique, le projet / SAE et les ressources.
     - 🗑️ : Suppression sécurisée avec confirmation.
     - ➕ : Ajout immédiat de nouveaux thèmes personnalisés.

3. **Plus de 260 thèmes pré-configurés :**
   - Données issues des écoles de référence (Dalbé-Viau, Rose-Virginie-Pelletier, Lucien-Pagé, Baie-Saint-François).
   - Matières : Français, Mathématiques, PMT, SMT (ateliers), IP (stages), PEMS (FMS - 375h), APS, EST (Sciences), Univers social, Anglais langue seconde, ÉPS.

4. **Vue intégrée annuelle (Globale interdisciplinaire) :**
   - **Tableau synoptique croisé :** Matières × Étapes avec filtrage par étape.
   - **Recherche en direct :** Filtrage instantané par mot-clé (ex: *Budget*, *SIMDUT*, *CV*, *Recette*).
   - **Matrice croisée par axes thématiques ministériels :** Vue synthétique sur les 8 grands axes transversaux (*Santé & bien-être*, *Société & citoyenneté*, *Consommation*, *Autonomie financière*, *Transport*, *Identité*, *Monde du travail*, *Insertion professionnelle*).
   - Bouton d'export PDF / Impression intégrée.

5. **Sauvegarde, persistance et partage :**
   - ⚡ **Persistance automatique (`localStorage`) :** Toutes vos modifications sont conservées même après fermeture du navigateur.
   - 💾 **Exportation JSON :** Téléchargement d'une sauvegarde complète en un clic.
   - 📝 **Exportation Markdown (.md) :** Rapport récapitulatif textuel hiérarchisé prêt pour vos documents Word ou Google Docs.
   - 📥 **Téléversement / Reprise :** Glissez-déposez un fichier JSON pour restaurer votre planification sur n'importe quel ordinateur.
   - 🔄 **Réinitialisation :** Possibilité de rétablir les données d'origine à tout moment.

---

## 🚀 Déploiement sur GitHub Pages

L'application ne requiert aucun compilateur ni serveur backend :

1. Poussez le dépôt sur votre compte GitHub (ex: `https://github.com/votre-nom/planificateur-pfae`).
2. Dans GitHub, accédez à **Settings** > **Pages**.
3. Sous **Branch**, sélectionnez `main` (ou `master`) et le dossier `/ (root)`.
4. Cliquez sur **Save**.
5. Votre application est immédiatement accessible en ligne sur `https://votre-nom.github.io/planificateur-pfae/`.

---

## 💻 Exécution en local (Sans serveur)

- Double-cliquez directement sur `index.html` (ou ouvrez `file:///.../index.html` dans Chrome, Edge, Firefox ou Safari).
- **Aucune erreur CORS / fetch :** Les données curriculaires sont embarquées via `curriculum_data.js` et le mode hors-ligne fonctionne à 100 %.

---

## 📁 Structure du projet

```
Planificateur-PFAE/
│
├── index.html                  # Interface utilisateur principale HTML5
├── style.css                   # Feuille de style CSS3 (Style Québec épuré)
├── app.js                      # Moteur d'application interactif Vanilla JS
├── curriculum_data.js          # Base de données JavaScript (chargement sans blocage CORS)
├── curriculum_data.json        # Base de données JSON brute
├── generate_curriculum.py      # Script Python de compilation initial des données
├── enrich_curriculum.py        # Script Python d'enrichissement des données
└── README.md                   # Documentation du projet
```
