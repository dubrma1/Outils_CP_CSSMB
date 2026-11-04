/**
 * Application : Générateur & Studio de Grilles d'Observation des Métiers (PFAE)
 * Conforme aux normes graphiques du Gouvernement du Québec / CSSMB
 * Format d'évaluation officiel FMS / FPT
 */

// État global de l'application
let appState = {
  metierSelectionne: "aide-concierge",
  donnees: null,
  plateformeIA: "copilot",
  objectifIA: "depuis-metier",
  modeInteractif: false
};

// Initialisation au chargement du DOM
document.addEventListener("DOMContentLoaded", () => {
  chargerDonneesInitiales();
  initialiserNavigation();
  initialiserFormulaire();
  initialiserPromptIA();
  initialiserEditeur();
  mettreAJourRenduGrille();
  mettreAJourPrompt();
});

/**
 * Charge les données initiales (depuis localStorage ou modèle par défaut)
 */
function chargerDonneesInitiales() {
  const sauvegarde = localStorage.getItem("pfae_grille_courante");
  if (sauvegarde) {
    try {
      appState.donnees = JSON.parse(sauvegarde);
    } catch (e) {
      console.warn("Impossible de charger la sauvegarde locale :", e);
      appState.donnees = JSON.parse(JSON.stringify(METIERS_PFAE["aide-concierge"]));
    }
  } else {
    appState.donnees = JSON.parse(JSON.stringify(METIERS_PFAE["aide-concierge"]));
  }
}

/**
 * Sauvegarde automatique dans localStorage
 */
function sauvegarderEnLocal() {
  if (appState.donnees) {
    localStorage.setItem("pfae_grille_courante", JSON.stringify(appState.donnees));
  }
}

/**
 * Gestion de la navigation par onglets (Stepper)
 */
function initialiserNavigation() {
  const tabs = document.querySelectorAll(".step-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const cibleId = tab.getAttribute("data-target");
      basculerVolet(cibleId);
    });
  });

  // Boutons de navigation interne
  document.querySelectorAll("[data-nav-vers]").forEach(btn => {
    btn.addEventListener("click", () => {
      const cible = btn.getAttribute("data-nav-vers");
      basculerVolet(cible);
    });
  });
}

function basculerVolet(voletId) {
  // Masquer tous les volets
  document.querySelectorAll(".section-volet").forEach(sec => sec.classList.remove("actif"));
  document.querySelectorAll(".step-tab").forEach(tab => tab.classList.remove("actif"));

  // Activer le volet et l'onglet cible
  const voletCible = document.getElementById(voletId);
  const tabCible = document.querySelector(`.step-tab[data-target="${voletId}"]`);

  if (voletCible) voletCible.classList.add("actif");
  if (tabCible) tabCible.classList.add("actif");

  // Si on passe à l'aperçu ou l'édition, on s'assure que le rendu est à jour
  if (voletId === "volet-impression") {
    mettreAJourRenduGrille();
  } else if (voletId === "volet-edition") {
    remplirInterfaceEditeur();
  } else if (voletId === "volet-prompt") {
    mettreAJourPrompt();
  }

  window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * Initialise le formulaire de l'Étape 1 (Saisie & Sélection du métier)
 */
function initialiserFormulaire() {
  const selectModele = document.getElementById("select-modele-metier");
  const inputNom = document.getElementById("champ-metier-nom");
  const inputCode = document.getElementById("champ-metier-code");
  const inputSecteur = document.getElementById("champ-metier-secteur");
  const inputCentre = document.getElementById("champ-metier-centre");
  const selectEchelle = document.getElementById("select-echelle-type");
  const inputSousTitre = document.getElementById("champ-metier-soustitre");

  // Remplir les champs avec les données actuelles
  if (appState.donnees) {
    if (inputNom) inputNom.value = appState.donnees.nom || "";
    if (inputCode) inputCode.value = appState.donnees.code || "";
    if (inputSecteur) inputSecteur.value = appState.donnees.secteur || "";
    if (inputCentre) inputCentre.value = appState.donnees.centre || "";
    if (inputSousTitre) inputSousTitre.value = appState.donnees.sousTitre || "";
    if (selectEchelle) {
      if (appState.donnees.echelle && appState.donnees.echelle.includes("Non acquis")) {
        selectEchelle.value = "na-ea-a-m";
      } else {
        selectEchelle.value = "dev-prog-att-dep";
      }
    }
  }

  // Changement de modèle pré-rempli
  if (selectModele) {
    selectModele.addEventListener("change", () => {
      const choix = selectModele.value;
      if (choix && METIERS_PFAE[choix]) {
        appState.donnees = JSON.parse(JSON.stringify(METIERS_PFAE[choix]));
        appState.metierSelectionne = choix;
        synchroniserFormulaireDepuisDonnees();
        sauvegarderEnLocal();
        afficherToast(`Métier chargé : ${appState.donnees.nom}`);
      }
    });
  }

  // Écouteurs sur les champs texte pour mise à jour immédiate
  const ecouteursChamps = [
    { el: inputNom, cle: "nom" },
    { el: inputCode, cle: "code" },
    { el: inputSecteur, cle: "secteur" },
    { el: inputCentre, cle: "centre" },
    { el: inputSousTitre, cle: "sousTitre" }
  ];

  ecouteursChamps.forEach(item => {
    if (item.el) {
      item.el.addEventListener("input", () => {
        appState.donnees[item.cle] = item.el.value;
        sauvegarderEnLocal();
      });
    }
  });

  if (selectEchelle) {
    selectEchelle.addEventListener("change", () => {
      if (selectEchelle.value === "na-ea-a-m") {
        appState.donnees.echelle = "1 = Non acquis (NA) | 2 = En acquisition (EA) | 3 = Acquis (A) | 4 = Maîtrisé / Autonome (M)";
      } else {
        appState.donnees.echelle = "1 = À développer | 2 = En progression | 3 = Atteint | 4 = Dépasse les attentes";
      }
      sauvegarderEnLocal();
    });
  }

  // Bouton pour analyser une liste de tâches brutes collées
  const btnParser = document.getElementById("btn-analyser-taches-brutes");
  const zoneTachesBrutes = document.getElementById("zone-taches-brutes");

  if (btnParser && zoneTachesBrutes) {
    btnParser.addEventListener("click", () => {
      const texte = zoneTachesBrutes.value.trim();
      if (!texte) {
        afficherToast("Veuillez d'abord coller du texte de tâches.");
        return;
      }
      analyserTexteBrutEtCreerGrille(texte);
      zoneTachesBrutes.value = "";
    });
  }
}

function synchroniserFormulaireDepuisDonnees() {
  if (!appState.donnees) return;
  const inputNom = document.getElementById("champ-metier-nom");
  const inputCode = document.getElementById("champ-metier-code");
  const inputSecteur = document.getElementById("champ-metier-secteur");
  const inputCentre = document.getElementById("champ-metier-centre");
  const inputSousTitre = document.getElementById("champ-metier-soustitre");
  const selectEchelle = document.getElementById("select-echelle-type");

  if (inputNom) inputNom.value = appState.donnees.nom || "";
  if (inputCode) inputCode.value = appState.donnees.code || "";
  if (inputSecteur) inputSecteur.value = appState.donnees.secteur || "";
  if (inputCentre) inputCentre.value = appState.donnees.centre || "";
  if (inputSousTitre) inputSousTitre.value = appState.donnees.sousTitre || "";
  if (selectEchelle) {
    if (appState.donnees.echelle && appState.donnees.echelle.includes("Non acquis")) {
      selectEchelle.value = "na-ea-a-m";
    } else {
      selectEchelle.value = "dev-prog-att-dep";
    }
  }
}

/**
 * Initialise le Volet 2 : Prompts IA Optimisés (Copilot M365 & Gemini)
 */
function initialiserPromptIA() {
  const radiosPlateforme = document.querySelectorAll('input[name="plateforme-ia"]');
  const selectObjectif = document.getElementById("select-objectif-ia");
  const btnCopierPrompt = document.getElementById("btn-copier-prompt");
  const btnImporterReponseIA = document.getElementById("btn-importer-reponse-ia");
  const zoneReponseIA = document.getElementById("zone-reponse-ia");

  radiosPlateforme.forEach(r => {
    r.addEventListener("change", () => {
      appState.plateformeIA = r.value;
      mettreAJourPrompt();
    });
  });

  if (selectObjectif) {
    selectObjectif.addEventListener("change", () => {
      appState.objectifIA = selectObjectif.value;
      mettreAJourPrompt();
    });
  }

  if (btnCopierPrompt) {
    btnCopierPrompt.addEventListener("click", () => {
      const codeEl = document.getElementById("contenu-prompt-code");
      if (codeEl) {
        const texte = codeEl.innerText;
        navigator.clipboard.writeText(texte).then(() => {
          afficherToast("Prompt copié dans le presse-papiers !");
        }).catch(err => {
          console.error("Erreur de copie :", err);
          afficherToast("Sélectionnez le texte manuellement avec Ctrl+C");
        });
      }
    });
  }

  if (btnImporterReponseIA && zoneReponseIA) {
    btnImporterReponseIA.addEventListener("click", () => {
      const texte = zoneReponseIA.value.trim();
      if (!texte) {
        afficherToast("Veuillez d'abord coller la réponse générée par Copilot ou Gemini.");
        return;
      }
      importerReponseIA(texte);
      zoneReponseIA.value = "";
    });
  }
}

/**
 * Génère le prompt optimisé pour Copilot M365 / Gemini selon le métier et l'objectif
 */
function mettreAJourPrompt() {
  const codeEl = document.getElementById("contenu-prompt-code");
  if (!codeEl) return;

  const nomMetier = appState.donnees?.nom || "Aide-concierge";
  const codeMetier = appState.donnees?.code || "8332";
  const plateforme = appState.plateformeIA === "copilot" ? "Microsoft Copilot (M365 Éducation)" : "Google Gemini (Compte Institutionnel)";

  let prompt = "";

  if (appState.objectifIA === "depuis-metier") {
    prompt = `Tu agis en tant que conseiller pédagogique expert en formation professionnelle semi-spécialisée (FMS / FPT) au Québec (programme PFAE du Ministère de l'Éducation).

OBJECTIF :
Génère une grille d'observation et d'évaluation complète, réaliste et conforme aux exigences ministérielles pour le métier semi-spécialisé suivant :
- Nom du métier : ${nomMetier}
- Code officiel PFAE / FMS : ${codeMetier}

CONSIGNES PÉDAGOGIQUES OBLIGATOIRES :
1. Définis 2 à 4 compétences professionnelles clés propres à ce métier (ex: manipulation d'outils, exécution de tâches courantes, santé et sécurité, service à la clientèle).
2. Pour chaque compétence :
   - Indique le code de la compétence (ex: 501, 502, ou code PFAE à 6 chiffres) et son libellé officiel.
   - Liste entre 4 et 12 TÂCHES OBSERVABLES concrètes, formulées obligatoirement avec un VERBE D'ACTION À L'INFINITIF précis (ex: "Passer l'aspirateur sur les tapis", "Laver et assainir le plan de travail"). Évite les formulations floues ou passives.
   - Liste entre 4 et 6 CRITÈRES DE PERFORMANCE observables (ex: Respect des règles SST / SIMDUT, Respect des consignes de l'intervenant, Qualité et propreté du travail, Maniement sécuritaire des équipements).
3. Adapte le niveau de langage pour des apprenants en insertion professionnelle (vocabulaire technique juste mais accessible).

FORMAT DE RÉPONSE STRICT :
Fournis uniquement ta réponse au format JSON structuré suivant (encadré par \`\`\`json et \`\`\`), afin qu'il puisse être importé directement dans l'application :

\`\`\`json
{
  "nom": "${nomMetier}",
  "code": "${codeMetier}",
  "secteur": "Secteur d'activité professionnel",
  "centre": "Centre de services scolaire",
  "echelle": "1 = À développer | 2 = En progression | 3 = Atteint | 4 = Dépasse les attentes",
  "competences": [
    {
      "code": "501",
      "titre": "Titre clair de la première compétence",
      "complexite": "2",
      "taches": [
        "Première tâche observable à l'infinitif.",
        "Deuxième tâche observable à l'infinitif.",
        "Troisième tâche observable à l'infinitif."
      ],
      "criteres": [
        "Respect des règles de santé et sécurité au travail (SST).",
        "Respect des directives et des consignes reçues.",
        "Application rigoureuse de la technique de travail."
      ]
    }
  ]
}
\`\`\``;
  } else if (appState.objectifIA === "nettoyer-texte") {
    prompt = `Tu agis en tant qu'expert en adaptation pédagogique et analyse de tâches pour les parcours de formation axée sur l'emploi (FPT / FMS - PFAE Québec).

OBJECTIF :
Je vais te fournir ci-dessous une liste brute de tâches ou un extrait de plan de cours ministériel pour le métier "${nomMetier}".
Ta mission est de le nettoyer, le synthétiser et le restructurer en une grille d'observation officielle rigoureuse.

RÈGLES D'OPTIMISATION :
1. Chaque tâche doit être une action unitaire, observable sur un plateau de travail, commençant par un verbe d'action à l'infinitif.
2. Regroupe les tâches sous 2 à 4 compétences cohérentes.
3. Associe à chaque compétence 4 à 6 critères de performance concrets (SST, hygiène, conformité aux consignes, dextérité, propreté).
4. Rends la réponse obligatoirement sous forme de bloc JSON prêt à l'emploi :

\`\`\`json
{
  "nom": "${nomMetier}",
  "code": "${codeMetier}",
  "competences": [
    {
      "code": "501",
      "titre": "Titre de la compétence",
      "taches": ["Action 1...", "Action 2..."],
      "criteres": ["Critère 1...", "Critère 2..."]
    }
  ]
}
\`\`\`

[COLLEZ VOTRE TEXTE BRUT ICI]`;
  } else if (appState.objectifIA === "falc-specialise") {
    prompt = `Tu agis en tant que spécialiste en adaptation scolaire pour élèves ayant un trouble du spectre de l'autisme (TSA) ou un trouble développemental du langage (TDL) en formation à un métier semi-spécialisé (FMS / FPT).

OBJECTIF :
Pour le métier "${nomMetier}", formule des énoncés de tâches et de critères d'observation selon les normes du Facile à lire et à comprendre (FALC) :
1. Phrases courtes (1 seule idée par consigne, structure Verbe d'action à l'infinitif + Complément concret).
2. Zéro tournure passive, zéro métaphore, vocabulaire visuel direct.
3. Actions chronologiques faciles à séquencer et à auto-évaluer.

Rends ta réponse sous format JSON structuré :
\`\`\`json
{
  "nom": "${nomMetier}",
  "code": "${codeMetier}",
  "competences": [
    {
      "code": "101",
      "titre": "Libellé épuré de la compétence",
      "taches": ["Action simple 1", "Action simple 2", "Action simple 3"],
      "criteres": ["Règle de sécurité respectée", "Consigne suivie", "Poste propre et rangé"]
    }
  ]
}
\`\`\``;
  }

  codeEl.innerText = prompt;
}

/**
 * Analyse une réponse issue de Copilot / Gemini (JSON ou Markdown/texte)
 */
function importerReponseIA(texteBrut) {
  let donneesParsees = null;

  // 1. Essai d'extraction d'un bloc ```json ... ```
  const regexJsonBlock = /```(?:json)?\s*([\s\S]*?)\s*```/i;
  const matchJson = texteBrut.match(regexJsonBlock);

  if (matchJson && matchJson[1]) {
    try {
      donneesParsees = JSON.parse(matchJson[1]);
    } catch (e) {
      console.warn("Échec parsing bloc JSON, tentative globale...", e);
    }
  }

  // 2. Essai de parsing JSON global direct
  if (!donneesParsees) {
    try {
      const matchAccolades = texteBrut.match(/\{[\s\S]*\}/);
      if (matchAccolades) {
        donneesParsees = JSON.parse(matchAccolades[0]);
      }
    } catch (e) {
      console.warn("Échec parsing JSON brut", e);
    }
  }

  // 3. Si aucun JSON valide, on effectue un parsing textuel heuristique
  if (!donneesParsees) {
    donneesParsees = parserTexteStructure(texteBrut);
  }

  if (donneesParsees && donneesParsees.competences && donneesParsees.competences.length > 0) {
    if (!appState.donnees) {
      appState.donnees = {
        nom: "Métier semi-spécialisé",
        code: "8000",
        secteur: "",
        centre: "Centre de services scolaire Marguerite-Bourgeoys",
        sousTitre: "Outil de reconnaissance des compétences et de suivi de l’évolution professionnelle à partir du plan de formation fourni.",
        echelle: "1 = À développer | 2 = En progression | 3 = Atteint | 4 = Dépasse les attentes",
        competences: []
      };
    }
    // Fusion intelligente avec l'existant
    appState.donnees.nom = donneesParsees.nom || appState.donnees.nom;
    appState.donnees.code = donneesParsees.code || appState.donnees.code;
    if (donneesParsees.secteur) appState.donnees.secteur = donneesParsees.secteur;
    if (donneesParsees.centre) appState.donnees.centre = donneesParsees.centre;
    if (donneesParsees.echelle) appState.donnees.echelle = donneesParsees.echelle;

    appState.donnees.competences = donneesParsees.competences.map((c, idx) => ({
      id: c.id || `comp-${Date.now()}-${idx}`,
      code: c.code || `${501 + idx}`,
      titre: c.titre || `Compétence ${idx + 1}`,
      complexite: c.complexite || "2",
      taches: Array.isArray(c.taches) ? c.taches : ["Tâche à préciser"],
      criteres: Array.isArray(c.criteres) ? c.criteres : [
        "Respect des règles SST",
        "Respect des directives",
        "Ordre et propreté"
      ]
    }));

    sauvegarderEnLocal();
    synchroniserFormulaireDepuisDonnees();
    afficherToast("Grille importée avec succès depuis l'IA !");
    basculerVolet("volet-edition");
  } else {
    afficherToast("Impossible d'extraire des compétences valides. Vérifiez le format.");
  }
}

/**
 * Parseur heuristique pour texte brut avec sections / puces
 */
function parserTexteStructure(texte) {
  const lignes = texte.split("\n").map(l => l.trim()).filter(l => l.length > 0);
  const competences = [];
  let compActuelle = null;
  let sectionActuelle = "taches"; // 'taches' ou 'criteres'

  for (let ligne of lignes) {
    // Détection d'un titre de compétence (ex: # Compétence 501, ### Nettoyer..., Compétence 1 :)
    if (/^(?:#+\s*|comp[eé]tence\s*[:#\d]|\d+[\.\)]\s*comp)/i.test(ligne)) {
      if (compActuelle && compActuelle.taches.length > 0) {
        competences.push(compActuelle);
      }
      const codeMatch = ligne.match(/\b(\d{3,6})\b/);
      const code = codeMatch ? codeMatch[1] : `${501 + competences.length}`;
      const titreNettoye = ligne.replace(/^[#\*\s\d\.\:\-]+/g, "").replace(/^comp[eé]tence\s*#?\d*\s*[:\-]?\s*/i, "").trim();

      compActuelle = {
        code: code,
        titre: titreNettoye || `Compétence #${code}`,
        taches: [],
        criteres: []
      };
      sectionActuelle = "taches";
      continue;
    }

    // Basculement vers critères
    if (/crit[eè]res?(?:\s*de\s*performance)?/i.test(ligne)) {
      sectionActuelle = "criteres";
      continue;
    }

    // Basculement vers tâches
    if (/t[aâ]ches?(?:\s*observ[eé]es?)?/i.test(ligne)) {
      sectionActuelle = "taches";
      continue;
    }

    // Détection d'une ligne d'item (puce, tiret, numéro)
    if (/^[\-\*\•\d\.\)]\s+/.test(ligne)) {
      const contenuItem = ligne.replace(/^[\-\*\•\d\.\)\s]+/, "").trim();
      if (!contenuItem) continue;

      if (!compActuelle) {
        compActuelle = {
          code: "501",
          titre: "Compétence principale du métier",
          taches: [],
          criteres: []
        };
      }

      if (sectionActuelle === "criteres") {
        compActuelle.criteres.push(contenuItem);
      } else {
        compActuelle.taches.push(contenuItem);
      }
    }
  }

  if (compActuelle && compActuelle.taches.length > 0) {
    competences.push(compActuelle);
  }

  if (competences.length > 0) {
    return {
      nom: appState.donnees?.nom || "Métier semi-spécialisé",
      competences: competences
    };
  }

  return null;
}

/**
 * Analyse une liste de tâches brutes (ligne par ligne) et crée une compétence
 */
function analyserTexteBrutEtCreerGrille(texte) {
  const lignes = texte.split("\n")
    .map(l => l.trim().replace(/^[\-\*\•\d\.\)\s]+/, "").trim())
    .filter(l => l.length > 2);

  if (lignes.length === 0) {
    afficherToast("Aucune tâche détectée.");
    return;
  }

  const nouvelleComp = {
    id: `comp-${Date.now()}`,
    code: "501",
    titre: "Exécution des tâches du métier",
    complexite: "2",
    taches: lignes,
    criteres: [
      "Respect des règles de santé et de sécurité au travail (SST)",
      "Respect des consignes et directives de travail",
      "Application correcte des méthodes et techniques",
      "Utilisation appropriée du matériel et des équipements",
      "Ordre, propreté et rangement"
    ]
  };

  appState.donnees.competences = [nouvelleComp];
  sauvegarderEnLocal();
  afficherToast(`${lignes.length} tâches importées dans une nouvelle compétence !`);
  basculerVolet("volet-edition");
}

/**
 * Volet 3 : Éditeur interactif de compétences
 */
function initialiserEditeur() {
  const btnAjouterComp = document.getElementById("btn-ajouter-competence");
  if (btnAjouterComp) {
    btnAjouterComp.addEventListener("click", () => {
      const num = (appState.donnees.competences.length + 1);
      const nouvelleComp = {
        id: `comp-${Date.now()}`,
        code: `${500 + num}`,
        titre: `Nouvelle compétence #${num}`,
        complexite: "2",
        taches: [
          "Action observable 1...",
          "Action observable 2..."
        ],
        criteres: [
          "Respect des règles SST",
          "Respect des directives",
          "Ordre et propreté"
        ]
      };
      appState.donnees.competences.push(nouvelleComp);
      sauvegarderEnLocal();
      remplirInterfaceEditeur();
      afficherToast("Nouvelle compétence ajoutée.");
    });
  }
}

/**
 * Remplit l'interface de l'éditeur avec les cartes de compétences
 */
function remplirInterfaceEditeur() {
  const conteneur = document.getElementById("liste-competences-editeur");
  if (!conteneur) return;

  conteneur.innerHTML = "";

  if (!appState.donnees || !appState.donnees.competences || appState.donnees.competences.length === 0) {
    conteneur.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--qc-texte-discret);">
        <p>Aucune compétence définie pour le moment.</p>
        <button type="button" class="btn-secondaire" onclick="document.getElementById('btn-ajouter-competence').click();">
          + Ajouter une première compétence
        </button>
      </div>`;
    return;
  }

  appState.donnees.competences.forEach((comp, idxComp) => {
    const carte = document.createElement("div");
    carte.className = "carte-competence";
    carte.innerHTML = `
      <div class="carte-competence-header">
        <div class="carte-competence-titre">
          <span>Compétence #${idxComp + 1}</span>
          <input type="text" class="input-code-comp" value="${echapperHtml(comp.code || '')}" placeholder="Code (ex: 501)" style="width: 100px; padding: 0.3rem 0.5rem; font-weight: 700;">
          <input type="text" class="input-titre-comp" value="${echapperHtml(comp.titre || '')}" placeholder="Titre de la compétence" style="width: 380px; padding: 0.3rem 0.5rem; font-weight: 700;">
        </div>
        <div style="display: flex; gap: 0.4rem; align-items: center;">
          <button type="button" class="btn-danger-subtil btn-supprimer-comp" title="Supprimer cette compétence">
            Supprimer
          </button>
        </div>
      </div>
      <div class="carte-competence-corps">
        <!-- Section Tâches -->
        <div style="margin-bottom: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <strong style="color: var(--qc-bleu-fonce); font-size: 0.95rem;">
              Tâches et opérations observées (${comp.taches.length}) :
            </strong>
            <button type="button" class="btn-secondaire btn-petit btn-ajouter-tache">
              + Ajouter une tâche
            </button>
          </div>
          <div class="liste-items-editable liste-taches-container"></div>
        </div>

        <!-- Section Critères -->
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <strong style="color: var(--qc-bleu-fonce); font-size: 0.95rem;">
              Critères de performance à évaluer (${comp.criteres.length}) :
            </strong>
            <button type="button" class="btn-secondaire btn-petit btn-ajouter-critere">
              + Ajouter un critère
            </button>
          </div>
          <div class="liste-items-editable liste-criteres-container"></div>
        </div>
      </div>
    `;

    // Écouteurs sur le code et le titre
    const inputCode = carte.querySelector(".input-code-comp");
    const inputTitre = carte.querySelector(".input-titre-comp");
    inputCode.addEventListener("input", () => {
      comp.code = inputCode.value;
      sauvegarderEnLocal();
    });
    inputTitre.addEventListener("input", () => {
      comp.titre = inputTitre.value;
      sauvegarderEnLocal();
    });

    // Supprimer compétence
    const btnSuppr = carte.querySelector(".btn-supprimer-comp");
    btnSuppr.addEventListener("click", () => {
      if (confirm(`Voulez-vous vraiment supprimer la compétence "${comp.titre}" ?`)) {
        appState.donnees.competences.splice(idxComp, 1);
        sauvegarderEnLocal();
        remplirInterfaceEditeur();
        afficherToast("Compétence supprimée.");
      }
    });

    // Rendu des tâches
    const containerTaches = carte.querySelector(".liste-taches-container");
    rendreListeItems(containerTaches, comp.taches, (nouvelleListe) => {
      comp.taches = nouvelleListe;
      sauvegarderEnLocal();
    }, "Tâche à observer...");

    carte.querySelector(".btn-ajouter-tache").addEventListener("click", () => {
      comp.taches.push("");
      sauvegarderEnLocal();
      remplirInterfaceEditeur();
    });

    // Rendu des critères
    const containerCriteres = carte.querySelector(".liste-criteres-container");
    rendreListeItems(containerCriteres, comp.criteres, (nouvelleListe) => {
      comp.criteres = nouvelleListe;
      sauvegarderEnLocal();
    }, "Critère de performance...");

    carte.querySelector(".btn-ajouter-critere").addEventListener("click", () => {
      comp.criteres.push("");
      sauvegarderEnLocal();
      remplirInterfaceEditeur();
    });

    conteneur.appendChild(carte);
  });
}

function rendreListeItems(conteneur, liste, callbackMiseAJour, placeholder) {
  conteneur.innerHTML = "";
  liste.forEach((texte, index) => {
    const item = document.createElement("div");
    item.className = "item-editable";
    item.innerHTML = `
      <span class="item-num">${index + 1}.</span>
      <input type="text" value="${echapperHtml(texte)}" placeholder="${placeholder}">
      <button type="button" class="btn-danger-subtil" title="Supprimer cet élément" style="padding: 0.25rem 0.5rem;">✕</button>
    `;

    const input = item.querySelector("input");
    input.addEventListener("input", () => {
      liste[index] = input.value;
      callbackMiseAJour(liste);
    });

    item.querySelector("button").addEventListener("click", () => {
      liste.splice(index, 1);
      callbackMiseAJour(liste);
      remplirInterfaceEditeur();
    });

    conteneur.appendChild(item);
  });
}

/**
 * Volet 4 : Rendu Haute Fidélité conforme à exemple-grilles-concierge.pdf
 */
function mettreAJourRenduGrille() {
  const conteneurApercu = document.getElementById("zone-rendu-grille-document");
  if (!conteneurApercu) return;

  const donnees = appState.donnees;
  if (!donnees || !donnees.competences || donnees.competences.length === 0) {
    conteneurApercu.innerHTML = `
      <div style="text-align: center; padding: 3rem; background: #fff; border: 1px dashed #cbd5e1;">
        <p style="color: #64748b;">Aucune donnée de grille disponible. Veuillez saisir un métier ou charger un exemple.</p>
      </div>`;
    return;
  }

  let htmlTotal = "";

  donnees.competences.forEach((comp, idx) => {
    const estPremierePage = (idx === 0);

    htmlTotal += `
      <div class="page-grille-pdf" data-page-index="${idx}">
        <!-- En-tête officiel présent sur la première page (ou discret sur les suivantes) -->
        <div class="grille-entete-document">
          <div class="grille-titre-principal">Grille d’observation et d’évaluation</div>
          <div class="grille-metier-nom">${echapperHtml(donnees.nom || "Métier semi-spécialisé")}</div>
          <div class="grille-sous-titre-doc">${echapperHtml(donnees.sousTitre || "Outil de reconnaissance des compétences et de suivi de l’évolution professionnelle à partir du plan de formation fourni.")}</div>
        </div>

        <!-- Titre de la compétence et Échelle -->
        <div class="grille-competence-titre">
          COMPÉTENCE #${echapperHtml(comp.code || `${501 + idx}`)} - ${echapperHtml(comp.titre || "Titre de la compétence")}
        </div>
        <div class="grille-echelle-texte">
          Échelle: ${echapperHtml(donnees.echelle || "1 = À développer | 2 = En progression | 3 = Atteint | 4 = Dépasse les attentes")}
        </div>

        <!-- Tableau 1 : Tâches observées -->
        <table class="tableau-grille-norme tableau-taches">
          <thead>
            <tr>
              <th class="col-tache">Tâche observée</th>
              <th class="col-note col-centre">1</th>
              <th class="col-note col-centre">2</th>
              <th class="col-note col-centre">3</th>
              <th class="col-note col-centre">4</th>
              <th class="col-commentaires">Commentaires</th>
            </tr>
          </thead>
          <tbody>
            ${comp.taches.map(tache => `
              <tr>
                <td>${echapperHtml(tache)}</td>
                <td class="col-centre"><span class="case-note-val"></span></td>
                <td class="col-centre"><span class="case-note-val"></span></td>
                <td class="col-centre"><span class="case-note-val"></span></td>
                <td class="col-centre"><span class="case-note-val"></span></td>
                <td></td>
              </tr>
            `).join("")}
          </tbody>
        </table>

        <!-- Tableau 2 : Critères de performance -->
        <div class="grille-intertitre">Critères de performance à évaluer :</div>
        <table class="tableau-grille-norme tableau-criteres">
          <thead>
            <tr>
              <th class="col-critere">Critère</th>
              <th class="col-note col-centre">1</th>
              <th class="col-note col-centre">2</th>
              <th class="col-note col-centre">3</th>
              <th class="col-note col-centre">4</th>
            </tr>
          </thead>
          <tbody>
            ${comp.criteres.map(critere => `
              <tr>
                <td>${echapperHtml(critere)}</td>
                <td class="col-centre"><span class="case-note-val"></span></td>
                <td class="col-centre"><span class="case-note-val"></span></td>
                <td class="col-centre"><span class="case-note-val"></span></td>
                <td class="col-centre"><span class="case-note-val"></span></td>
              </tr>
            `).join("")}
          </tbody>
        </table>

        <!-- Bilan / plan d'évolution -->
        <div class="grille-ligne-bilan">
          <span>Bilan / plan d’évolution :</span>
          <div class="grille-ligne-bilan-trait"></div>
        </div>
      </div>
    `;
  });

  conteneurApercu.innerHTML = htmlTotal;
}

/**
 * Fonction d'impression de la grille
 */
function imprimerGrille() {
  // S'assurer que le rendu est à jour
  mettreAJourRenduGrille();
  window.print();
}

/**
 * Export Word (.doc XML formaté MSO)
 * S'ouvre directement et proprement dans Microsoft Word et LibreOffice avec les mêmes tableaux et polices Calibri
 */
function exporterEnWord() {
  const donnees = appState.donnees;
  if (!donnees) return;

  const nomFichier = `Grille_${(donnees.nom || "Metier").replace(/[\s\/\\]+/g, "_")}.doc`;

  let corpsHtml = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
      <meta charset='utf-8'>
      <title>Grille d'observation - ${echapperHtml(donnees.nom)}</title>
      <!--[if gte mso 9]>
      <xml>
        <w:WordDocument>
          <w:View>Print</w:View>
          <w:Zoom>100</w:Zoom>
          <w:DoNotOptimizeForBrowser/>
        </w:WordDocument>
      </xml>
      <![endif]-->
      <style>
        body {
          font-family: Calibri, sans-serif;
          font-size: 11pt;
          color: #000000;
          margin: 1in;
        }
        h1 {
          font-size: 16pt;
          text-align: center;
          margin: 0;
          color: #1f4e78;
        }
        h2 {
          font-size: 14pt;
          text-align: center;
          margin-top: 2pt;
          margin-bottom: 6pt;
          color: #000000;
        }
        .sous-titre {
          font-size: 9.5pt;
          font-style: italic;
          text-align: center;
          color: #555555;
          margin-bottom: 20pt;
        }
        .titre-comp {
          font-size: 12.5pt;
          font-weight: bold;
          color: #1f4e78;
          margin-top: 15pt;
          margin-bottom: 4pt;
        }
        .echelle {
          font-size: 9pt;
          font-style: italic;
          color: #333333;
          margin-bottom: 8pt;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 15pt;
        }
        th, td {
          border: 1px solid #000000;
          padding: 4pt 6pt;
          font-size: 9.5pt;
        }
        th {
          background-color: #f2f2f2;
          font-weight: bold;
        }
        .center {
          text-align: center;
        }
        .saut-page {
          page-break-after: always;
          mso-break-type: section-break;
        }
        .bilan-trait {
          margin-top: 15pt;
          font-size: 10pt;
        }
      </style>
    </head>
    <body>
  `;

  donnees.competences.forEach((comp, idx) => {
    corpsHtml += `
      <div>
        <h1>Grille d’observation et d’évaluation</h1>
        <h2>${echapperHtml(donnees.nom)}</h2>
        <div class="sous-titre">${echapperHtml(donnees.sousTitre)}</div>

        <div class="titre-comp">COMPÉTENCE #${echapperHtml(comp.code)} - ${echapperHtml(comp.titre)}</div>
        <div class="echelle">Échelle: ${echapperHtml(donnees.echelle)}</div>

        <table>
          <thead>
            <tr>
              <th style="width: 50%;">Tâche observée</th>
              <th style="width: 6%;" class="center">1</th>
              <th style="width: 6%;" class="center">2</th>
              <th style="width: 6%;" class="center">3</th>
              <th style="width: 6%;" class="center">4</th>
              <th style="width: 26%;">Commentaires</th>
            </tr>
          </thead>
          <tbody>
            ${comp.taches.map(t => `
              <tr>
                <td>${echapperHtml(t)}</td>
                <td class="center"></td>
                <td class="center"></td>
                <td class="center"></td>
                <td class="center"></td>
                <td></td>
              </tr>
            `).join("")}
          </tbody>
        </table>

        <div style="font-weight: bold; margin-top: 10pt; margin-bottom: 4pt;">Critères de performance à évaluer :</div>
        <table>
          <thead>
            <tr>
              <th style="width: 76%;">Critère</th>
              <th style="width: 6%;" class="center">1</th>
              <th style="width: 6%;" class="center">2</th>
              <th style="width: 6%;" class="center">3</th>
              <th style="width: 6%;" class="center">4</th>
            </tr>
          </thead>
          <tbody>
            ${comp.criteres.map(c => `
              <tr>
                <td>${echapperHtml(c)}</td>
                <td class="center"></td>
                <td class="center"></td>
                <td class="center"></td>
                <td class="center"></td>
              </tr>
            `).join("")}
          </tbody>
        </table>

        <div class="bilan-trait">
          <strong>Bilan / plan d’évolution :</strong> _________________________________________________________________________
        </div>
      </div>
      ${(idx < donnees.competences.length - 1) ? '<br class="saut-page" style="page-break-after:always;">' : ''}
    `;
  });

  corpsHtml += `
    </body>
    </html>
  `;

  const blob = new Blob(['\ufeff', corpsHtml], {
    type: "application/msword"
  });

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomFichier;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  afficherToast(`Fichier Word généré : ${nomFichier}`);
}

/**
 * Exporte la grille actuelle au format JSON
 */
function exporterEnJSON() {
  if (!appState.donnees) return;
  const jsonStr = JSON.stringify(appState.donnees, null, 2);
  const nomFichier = `grille_${(appState.donnees.nom || "metier").replace(/[\s\/\\]+/g, "_")}.json`;

  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomFichier;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  afficherToast(`Grille exportée en JSON : ${nomFichier}`);
}

/**
 * Charge un fichier JSON depuis l'ordinateur
 */
function declencherImportJSON() {
  const inputFichier = document.getElementById("input-fichier-json");
  if (inputFichier) inputFichier.click();
}

function gererFichierJSON(event) {
  const fichier = event.target.files[0];
  if (!fichier) return;

  const lecteur = new FileReader();
  lecteur.onload = (e) => {
    try {
      const contenu = JSON.parse(e.target.result);
      if (contenu && contenu.competences) {
        appState.donnees = contenu;
        sauvegarderEnLocal();
        synchroniserFormulaireDepuisDonnees();
        afficherToast(`Grille chargée : ${contenu.nom || fichier.name}`);
        basculerVolet("volet-impression");
      } else {
        afficherToast("Le fichier JSON ne contient pas de structure de grille valide.");
      }
    } catch (err) {
      console.error(err);
      afficherToast("Erreur lors de la lecture du fichier JSON.");
    }
  };
  lecteur.readAsText(fichier);
  event.target.value = "";
}

/**
 * Affiche une bulle de notification toast discrète
 */
function afficherToast(message) {
  let toast = document.getElementById("toast-alerte");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast-alerte";
    toast.className = "toast-alerte";
    document.body.appendChild(toast);
  }

  toast.innerText = message;
  toast.style.display = "block";

  if (window.toastTimeout) clearTimeout(window.toastTimeout);
  window.toastTimeout = setTimeout(() => {
    toast.style.display = "none";
  }, 3500);
}

/**
 * Échappe le HTML pour éviter les injections XSS
 */
function echapperHtml(str) {
  if (typeof str !== "string") return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
