# Déploiement sur SharePoint Institutionnel (.aspx)

Ce dossier **`PFAE-Generateur-img-2-stlite`** a été préparé pour un déploiement direct et sans serveur sur un SharePoint institutionnel (Centres de services scolaires, Cégeps, commissions scolaires).

---

## 🚀 Procédure de déploiement en 3 étapes

### 1. Téléverser sur SharePoint
* Ouvrez votre bibliothèque SharePoint (ex. *Documents partagés*, *Contenu du site* ou *Actifs du site*).
* Glissez-déposez le dossier complet **`PFAE-Generateur-img-2-stlite`** (ou uniquement le fichier **`index.html`**).

### 2. Renommer en `.aspx`
* Dans l'interface SharePoint, repérez le fichier principal **`index.html`**.
* Cliquez sur les 3 petits points (`...`) ou faites un clic droit > **Renommer**.
* Remplacez `index.html` par **`index.aspx`** et validez.

> **Pourquoi renommer en `.aspx` ?**  
> Par défaut, SharePoint force le téléchargement des fichiers `.html`. L'extension `.aspx` autorise SharePoint à afficher directement la page Web interactive dans l'onglet du navigateur sans nécessiter de serveur applicatif.

### 3. Utiliser et partager l'application
* Cliquez sur **`index.aspx`** : l'application s'ouvre instantanément.
* Copiez l'adresse URL dans la barre du navigateur pour la transmettre à vos collègues enseignants ou intervenants.

---

## 🔒 Confidentialité & Loi 25 (100 % Côté Client)
* **Aucun serveur requis :** Tout s'exécute dans le moteur JavaScript et WebAssembly du navigateur de l'utilisateur.
* **Zéro fuite de données :** Les images collées (Ctrl+V) et les textes saisis ne quittent jamais l'ordinateur de l'utilisateur.
* **Indépendance réseau :** Même si le pare-feu institutionnel bloque les CDN ou WebAssembly lourds, la page fonctionne immédiatement car tous les styles (CSS Québec), les algorithmes (Potrace) et les pictogrammes SVG sont intégrés dans le fichier principal.

---

## 📁 Contenu du dossier
* **`index.html`** *(Fichier principal à renommer en `index.aspx`)* : Version autonome complète (inlinée, 0 dépendance externe).
* **`index_stlite.html`** : Variante utilisant le lanceur `@stlite/mountable` (WebAssembly Pyodide) si requis par votre environnement technique.
* **`streamlit_app.py`** : Script Python compatible Streamlit / Stlite.
* **`MODE_EMPLOI.md`** : Guide complet d'utilisation pédagogique (TSA / TDL / FALC).
* **`css/`** et **`potrace.js`** : Fichiers sources modulaires conservés pour référence et maintenance.

