# Mode d'emploi : Grille d'observation des métiers semi-spécialisés (PFAE)

> **Public cible :** Enseignants de FMS / FPT, conseillers pédagogiques, techniciens en éducation spécialisée (TES) et superviseurs de stages en milieu de travail.  
> **Confidentialité & Sécurité :** 100 % hors-ligne dans votre navigateur (aucun compte requis, aucune transmission de données sur le réseau, conformité stricte Loi 25 du Québec).

---

## 1. À quoi sert cette application ?

Cette application permet de générer des **grilles d'observation et d'évaluation des compétences** pour les élèves inscrits dans un parcours de formation à un métier semi-spécialisé (FMS / FPT - PFAE) :

* **Clarté pour le milieu de stage :** Les tâches sont formulées par des verbes d'action concrets observables directement en atelier ou en entreprise.
* **Format officiel rigide :** Reproduit fidèlement la mise en page du document ministériel de référence (ex: *Aide-concierge 8332*), avec une présentation aérée de 1 compétence par feuille.
* **Échelle d'évaluation normée :** `1 = À développer | 2 = En progression | 3 = Atteint | 4 = Dépasse les attentes` (ou variante `NA / EA / A / M`).
* **Intégration d'intelligence artificielle éthique :** Possibilité de copier un prompt d'ingénierie pédagogique optimisé dans **Microsoft Copilot (M365 Éducation)** ou **Google Gemini Institutionnel** pour transformer des textes ministériels denses en grilles prêtes à l'emploi.

---

## 2. Comment lancer l'application ?

Aucune installation complexe n'est requise :
1. Ouvrez le dossier `PFAE-Grille_Observations_Metiers`.
2. Faites un double-clic sur le fichier **`index.html`**.
3. L'application s'ouvre instantanément dans votre navigateur (Chrome, Edge, Firefox).

*(L'application peut également être hébergée sur GitHub Pages pour être accessible depuis n'importe quelle tablette ou téléphone lors des visites en stage).*

---

## 3. Guide pas-à-pas en 4 étapes simples

### Étape 1 : Choisir le métier ou saisir les tâches
1. **Exemple pré-rempli :** Si vous travaillez sur l'un des métiers courants, sélectionnez-le dans le menu déroulant :
   * *Aide-concierge (8332 / M332)* : conforme au PDF exemple avec 3 compétences (#501, #503, #833203).
   * *Aide-cuisinier (8312)*.
   * *Commis d'épicerie / Magasinier (8321)*.
   * *Préposé à l'entretien paysager (8342)*.
2. **Personnalisation :** Vous pouvez ajuster le titre du métier, le code de programme, le secteur professionnel et le nom de votre Centre de services scolaire.
3. **Coller des tâches brutes (optionnel) :** Si vous avez déjà une liste de tâches copiée d'un PDF ministériel ou d'un babillard, collez-la dans la boîte de texte et cliquez sur **« Analyser et intégrer les tâches brutes »**.
4. Cliquez sur **« Générer avec Copilot / Gemini (Étape 2) »** ou passez directement à l'étape 3.

---

### Étape 2 : Utiliser l'IA institutionnelle (Copilot ou Gemini)
1. Choisissez votre outil sécurisé : **Microsoft Copilot** ou **Google Gemini Institutionnel**.
2. Sélectionnez votre objectif :
   * *Créer la grille complète à partir du nom du métier* ;
   * *Nettoyer et structurer des notes brutes ministérielles* ;
   * *Formuler selon la norme FALC (Facile à lire et à comprendre pour élèves TSA / TDL)*.
3. Cliquez sur le bouton bleu **« Copier le prompt dans le presse-papiers »**.
4. Dans votre navigateur, ouvrez votre outil IA avec votre compte scolaire institutionnel.
5. Collez le prompt avec <kbd>Ctrl</kbd> + <kbd>V</kbd> et appuyez sur **Entrée**.
6. Une fois la réponse obtenue : copiez le texte de l'IA, revenez dans l'application, collez-le dans le champ inférieur et cliquez sur le bouton vert **« Importer la réponse dans la grille »**.
7. L'application extrait automatiquement les compétences, les tâches et les critères de performance !

---

### Étape 3 : Ajuster et personnaliser la grille
1. Vous visualisez chaque compétence sous forme de carte pliable.
2. **Modifier un texte :** Cliquez directement dans les champs de texte pour ajuster la formulation d'une tâche ou d'un critère.
3. **Ajouter ou retirer des éléments :** Utilisez les boutons **« + Ajouter une tâche »**, **« + Ajouter un critère »** ou **« ✕ »** pour adapter la grille aux spécificités de votre milieu de stage.
4. **Ajouter une nouvelle compétence :** Cliquez sur le bouton bleu **« + Ajouter une compétence »** en haut à droite.
5. Vos modifications sont automatiquement sauvegardées dans la mémoire locale de votre navigateur.

---

### Étape 4 : Visualiser, Imprimer et Exporter
1. Vous arrivez sur la planche finale haute fidélité.
2. **Impression / Sauvegarde en PDF :**
   * Cliquez sur **« Imprimer / Enregistrer en PDF »** ou appuyez sur <kbd>Ctrl</kbd> + <kbd>P</kbd>.
   * Le gabarit force un saut de page propre par compétence (`page-break-after`). Chaque compétence tient ainsi sur sa propre feuille avec ses tableaux et sa ligne de bilan.
   * Cochez l'option "Graphiques d'arrière-plan" dans les options d'impression pour un contraste optimal.
3. **Export Word (.doc) :**
   * Cliquez sur le bouton **« Exporter Word (.doc) »**.
   * Le fichier téléchargé s'ouvre directement dans Microsoft Word ou LibreOffice avec une mise en page soignée, des tableaux formatés en Calibri et des sauts de page automatiques.
4. **Sauvegarde JSON :**
   * Cliquez sur **« Sauvegarder JSON »** pour archiver votre grille dans un mini-fichier et pouvoir la réimporter l'année suivante via **« Ouvrir JSON »**.

---

## 4. Foire Aux Questions (FAQ)

### Mes élèves ou mes données de stage sont-ils envoyés sur internet ?
**Non, absolument jamais.** L'application fonctionne à 100 % dans votre navigateur web local. Aucune information, aucun nom d'élève et aucune grille ne sortent de votre poste. L'outil respecte intégralement la **Loi 25 du Québec** sur la protection des données personnelles.

### Puis-je modifier la grille directement dans Microsoft Word ?
Oui. Utilisez le bouton **« Exporter Word (.doc) »** situé à l'Étape 4. Vous obtiendrez un document Word structuré, avec les mêmes en-têtes et bordures que le script Python initial, prêt pour vos annotations personnalisées.

### Comment obtenir une compétence par page à l'impression ?
Le style CSS d'impression (`@media print`) est rigoureusement calibré pour le format **Lettre US** (norme scolaire au Québec) et le format **A4**. Assurez-vous que l'échelle d'impression est réglée à 100 % ou "Ajuster à la page" dans la boîte de dialogue d'impression du navigateur.

---

*Conforme aux exigences du Programme de formation de l'école québécoise (PFAE — FMS / FPT) et aux règles d'accessibilité universelle.*
