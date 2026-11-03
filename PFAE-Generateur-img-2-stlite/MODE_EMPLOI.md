# Mode d'emploi : Studio d'assemblage de séquences visuelles (TSA / TDL)

> **Public cible :** Enseignants de FPT / FMS, techniciens en éducation spécialisée (TES), conseillers pédagogiques et moniteurs d'atelier.  
> **Confidentialité & Sécurité :** 100 % hors-ligne dans votre navigateur (aucun compte requis, aucune transmission de données sur le réseau, conformité stricte Loi 25).

---

## 1. À quoi sert cette application ?

Ce studio permet de créer en quelques clics des **fiches de tâches professionnelles adaptées** pour les élèves de 15 ans et plus présentant :
* Un **trouble du spectre de l'autisme (TSA)** : prévisibilité, 1 seule action explicite par case, zéro bruit de fond, flèches directionnelles univoques, style non enfantin (mannequin ergonomique ISO/IKEA).
* Un **trouble développemental du langage (TDL)** : consignes épurées selon la norme FALC (Facile à lire et à comprendre), pas de phrases passives ni de subordonnées.
* Une haute tolérance aux **photocopieurs d'école en noir et blanc** (contraste maximal, zéro dégradé grisâtre qui bave).

---

## 2. Comment lancer l'application ?

Aucune installation complexe n'est requise :
1. Ouvrez le dossier `PFAE-Generateur-img-2`.
2. Faites un double-clic sur le fichier **`index.html`**.
3. Il s'ouvre instantanément dans votre navigateur préféré (Google Chrome, Microsoft Edge, Mozilla Firefox).

---

## 3. Guide pas-à-pas en 4 étapes simples

### Étape 1 : Saisir la tâche et valider le texte FALC

1. **Titre de la tâche :** Donnez un nom clair au poste de travail (ex. *« Nettoyer et ranger le poste d'atelier »*).
2. **Exemples de métiers (optionnel) :** Si vous êtes en panne d'inspiration, choisissez un exemple dans le menu déroulant (*Aide-boulanger, Aide-concierge, Atelier de menuiserie, Magasinier*). Les consignes et les équipements de protection (ÉPI) se remplissent tout seuls !
3. **Équipements de protection (ÉPI) :** Cochez les cases correspondant aux règles de sécurité de l'atelier (*Lunettes, Tablier, Gants, Bottes à cap d'acier, Casque antibruit, Masque*).
4. **Liste des consignes :** Collez vos étapes habituelles (1 par ligne).
5. **Cliquer sur « Valider et simplifier en FALC » :** L'outil nettoie automatiquement les phrases longues pour ne garder qu'**un verbe d'action à l'infinitif + un complément concret** (ex. : *« Mettre les lunettes de sécurité. »*).
6. Vous pouvez retoucher le texte directement dans le tableau si vous souhaitez ajuster un mot.
7. Cliquez sur le bouton vert **« Continuer vers la génération de prompts (Étape 2) »**.

---

### Étape 2 : Copier le prompt pour l'Intelligence Artificielle

1. Par défaut, le mode **« Matrice Grille 2×2 »** est sélectionné (les 4 actions sur une seule image).
2. Cliquez sur le bouton bleu **« Copier le prompt dans le presse-papiers »**.
3. Ouvrez votre outil habituel de génération d'image (ex. **Google Gemini** avec votre compte scolaire, ou **Microsoft Copilot**).
4. Dans le champ de discussion, faites un simple <kbd>Ctrl</kbd> + <kbd>V</kbd> (Coller) et appuyez sur **Entrée**.
5. L'IA génère une image technique en 4 cadrans, sur fond blanc pur, avec le mannequin neutre et **aucun texte à l'intérieur de l'image** (ce qui évite que l'IA n'invente des mots illisibles).

---

### Étape 3 : Récupérer l'image par un simple Ctrl+V

1. Dans Google Gemini ou Copilot, faites un **clic droit** sur l'image générée $\rightarrow$ choisissez **« Copier l'image »**.
2. Revenez sur l'onglet de votre Studio dans le navigateur.
3. Appuyez simplement sur les touches <kbd>Ctrl</kbd> + <kbd>V</kbd> de votre clavier (ou glissez l'image dans la zone bleue en pointillés).
4. **Le traitement automatique s'exécute en une fraction de seconde :**
   * **Découpage 2×2 automatique :** L'image est coupée en 4 cadrans distincts (Haut-Gauche = 1, Haut-Droite = 2, Bas-Gauche = 3, Bas-Droite = 4).
   * **Binarisation d'Otsu :** Tout pixel clair est forcé à blanc pur (#FFFFFF) et tout trait sombre est forcé à noir pur (#000000). Les gris sales disparaissent.
   * **Gomme magique des bordures (5 %) :** Les faux chiffres ou cadres imparfaits dans les coins de l'IA sont automatiquement gommés.
   * **Vectorisation SVG (Potrace) :** L'image devient un tracé vectoriel d'une netteté absolue, agrandissable à l'infini sans pixellisation.
5. Cliquez sur **« Visualiser et imprimer le gabarit A4 (Étape 4) »**.

> **Astuce pour essayer immédiatement :**  
> Si vous n'avez pas encore d'image sous la main, cliquez sur le bouton vert **« 🧪 Charger un exemple visuel simulé »** dans la zone de dépôt pour tester le découpage et la vectorisation immédiatement !

---

### Étape 4 : Imprimer la fiche ou l'affiche d'atelier

1. Vous arrivez sur la planche finale prête pour l'atelier.
2. Chaque cadran comprend :
   * La **pastille numérotée géante** (1, 2, 3, 4).
   * Les **pictogrammes officiels d'ÉPI**.
   * La **case carrée d'auto-évaluation $\square$** (l'élève coche au crayon ou au feutre effaçable une fois le geste accompli).
   * L'**illustration vectorielle épurée**.
   * La **consigne FALC** en gros caractères lisibles.
3. **Deux modes d'impression sont disponibles :**
   * **Mode Fiche de tâche (Grille 2×2 sur 1 page)** *(par défaut)* : Les 4 étapes tiennent parfaitement sur une seule feuille A4 ou Lettre US, idéale pour glisser sous une pochette plastique sur le chariot de travail.
   * **Mode Affiche atelier (1 étape par page)** : Cliquez sur le bouton *« Basculer en mode Affiche atelier »* pour imprimer chaque étape en très grand format, parfait pour afficher au mur juste devant une machine-outil (scie, four, presse, plonge).
4. Cliquez sur le bouton bleu **« Imprimer la fiche (A4 / Lettre) »** ou appuyez sur <kbd>Ctrl</kbd> + <kbd>P</kbd>.

---

## 4. Foire Aux Questions (FAQ)

### Mes traits noirs sont trop fins ou ont disparu après le collage, que faire ?
Déplacez légèrement le curseur **« Seuil de luminance »** (situé dans le Volet 3) vers la droite pour épaissir les traits, puis cliquez à nouveau sur l'image. Le bouton *« Calculer Otsu »* permet de revenir en mode automatique.

### Puis-je remplacer une seule étape sans tout refaire ?
Oui ! Cliquez sur le bouton *« Effacer »* situé sous la case que vous voulez modifier, puis collez la nouvelle vignette individuelle.

### Est-ce que mes élèves ou mes textes sont envoyés sur un serveur ?
**Absolument pas.** L'application fonctionne à 100 % dans la mémoire de votre propre ordinateur (JavaScript dans le navigateur). Aucune image, aucun texte et aucun cookie ne sortent de votre poste. L'outil respecte intégralement la **Loi 25 du Québec** sur la protection des données.

### Puis-je sauvegarder une image vectorielle pour l'intégrer dans un document Word ou LibreOffice ?
Oui ! Cliquez sur le bouton **« ⬇ Télécharger SVG »** situé sous n'importe quelle étape du Volet 3 pour enregistrer l'image vectorielle sur votre ordinateur.

---

*Conforme aux exigences du Programme de formation de l'école québécoise (PFAE — FPT / FMS) et aux normes d'accessibilité universelle.*

