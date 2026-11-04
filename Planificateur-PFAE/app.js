/**
 * ==============================================================================
 * APPLICATION PLANIFICATEUR PFAE (FPT 1, 2, 3 & FMS)
 * Exécution 100% côté client (Vanilla ES6) — Zéro dépendance
 * Conforme PFEQ (Ministère de l'Éducation du Québec & CSSMB)
 * ==============================================================================
 */

(function () {
  'use strict';

  // Constantes de stockage local
  const STORAGE_KEY = 'pfae_planificateur_donnees_v1';
  const PARCOURS_STORAGE_KEY = 'pfae_selected_parcours';
  const MATIERE_STORAGE_KEY = 'pfae_selected_matiere';

  // État global de l'application
  const AppState = {
    curriculum: null,
    currentParcours: 'FPT1',
    currentMatiere: 'francais',
    currentView: 'matiere', // 'matiere' | 'globale' | 'gestion'
    searchQuery: '',
    stepFilter: 'all', // 'all' | 'etape1' | 'etape2' | 'etape3'
    isInfoExpanded: false,
    draggedData: null,
    modalContext: null
  };

  // Noms et libellés des étapes
  const ETAPES_CONFIG = [
    { key: 'etape1', title: 'Étape 1 (Automne)', weight: '20 %', classSuffix: '1' },
    { key: 'etape2', title: 'Étape 2 (Hiver)', weight: '20 %', classSuffix: '2' },
    { key: 'etape3', title: 'Étape 3 (Printemps / Bilan)', weight: '60 %', classSuffix: '3' }
  ];

  // ==========================================================================
  // INITIALISATION DES DONNÉES
  // ==========================================================================

  async function initData() {
    let loaded = null;

    // 1. Essai de chargement depuis le cache local du navigateur
    try {
      const cached = localStorage.getItem(STORAGE_KEY);
      if (cached) {
        loaded = JSON.parse(cached);
      }
    } catch (e) {
      console.warn("Impossible de lire localStorage:", e);
    }

    // 2. Si aucun cache, charger les données de référence (curriculum_data.js)
    if (!loaded && window.CURRICULUM_DEFAULT_DATA) {
      loaded = JSON.parse(JSON.stringify(window.CURRICULUM_DEFAULT_DATA));
    }

    // 3. Fallback en cas d'hébergement serveur direct sans script tag
    if (!loaded) {
      try {
        const response = await fetch('./curriculum_data.json');
        if (response.ok) {
          loaded = await response.json();
        }
      } catch (err) {
        console.warn("Fetch fallback échoué :", err);
      }
    }

    if (!loaded || !loaded.parcours) {
      showToast("Erreur critique : Données de programme introuvables.", "error");
      return;
    }

    AppState.curriculum = loaded;

    // Restaurer le parcours et la matière sélectionnés
    const savedP = localStorage.getItem(PARCOURS_STORAGE_KEY);
    if (savedP && AppState.curriculum.parcours[savedP]) {
      AppState.currentParcours = savedP;
    }

    ensureValidMatiere();
    updateStatusBadge();
    renderApp();
  }

  function ensureValidMatiere() {
    const pData = AppState.curriculum.parcours[AppState.currentParcours];
    if (!pData || !pData.matieres) return;

    const keys = Object.keys(pData.matieres);
    const savedM = localStorage.getItem(MATIERE_STORAGE_KEY);

    if (savedM && keys.includes(savedM)) {
      AppState.currentMatiere = savedM;
    } else if (!keys.includes(AppState.currentMatiere)) {
      AppState.currentMatiere = keys[0] || '';
    }
  }

  function saveCurriculumState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(AppState.curriculum));
      updateStatusBadge();
    } catch (e) {
      console.error("Erreur de sauvegarde locale:", e);
      showToast("Mémoire locale saturée ou inaccessible.", "error");
    }
  }

  function updateStatusBadge() {
    const badge = document.getElementById('statusBadge');
    if (!badge) return;

    const hasCustomData = localStorage.getItem(STORAGE_KEY) !== null;
    if (hasCustomData) {
      badge.className = 'header-status-badge dirty';
      badge.innerHTML = '<span class="dot"></span> Personnalisé (Enregistré localement)';
    } else {
      badge.className = 'header-status-badge';
      badge.innerHTML = '<span class="dot"></span> Données officielles de référence';
    }
  }

  // ==========================================================================
  // RENDU PRINCIPAL
  // ==========================================================================

  function renderApp() {
    renderHeader();
    renderParcoursSummary();

    const viewMatiere = document.getElementById('viewMatiere');
    const viewGlobale = document.getElementById('viewGlobale');
    const viewGestion = document.getElementById('viewGestion');

    // Gestion de la visibilité des vues
    if (viewMatiere) viewMatiere.style.display = AppState.currentView === 'matiere' ? 'block' : 'none';
    if (viewGlobale) viewGlobale.style.display = AppState.currentView === 'globale' ? 'block' : 'none';
    if (viewGestion) viewGestion.style.display = AppState.currentView === 'gestion' ? 'block' : 'none';

    // Rendu spécifique de la vue active
    if (AppState.currentView === 'matiere') {
      renderMatiereView();
    } else if (AppState.currentView === 'globale') {
      renderGlobaleView();
    } else if (AppState.currentView === 'gestion') {
      renderGestionView();
    }
  }

  function renderHeader() {
    const selector = document.getElementById('parcoursSelect');
    if (selector && selector.value !== AppState.currentParcours) {
      selector.value = AppState.currentParcours;
    }

    // Gestion de la classe active sur les onglets de vue
    document.querySelectorAll('.qc-tab-btn').forEach(btn => {
      const view = btn.getAttribute('data-view');
      if (view === AppState.currentView) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  function renderParcoursSummary() {
    const pData = AppState.curriculum.parcours[AppState.currentParcours];
    if (!pData) return;

    const titleEl = document.getElementById('summaryParcoursTitle');
    const descEl = document.getElementById('summaryParcoursDesc');
    const chipMatieres = document.getElementById('statCountMatieres');
    const chipThemes = document.getElementById('statCountThemes');

    if (titleEl) titleEl.textContent = pData.titre || AppState.currentParcours;
    if (descEl) descEl.textContent = pData.description || '';

    const matieresKeys = Object.keys(pData.matieres || {});
    let totalThemes = 0;
    matieresKeys.forEach(mKey => {
      const m = pData.matieres[mKey];
      if (m && m.etapes) {
        totalThemes += (m.etapes.etape1 || []).length;
        totalThemes += (m.etapes.etape2 || []).length;
        totalThemes += (m.etapes.etape3 || []).length;
      }
    });

    if (chipMatieres) chipMatieres.textContent = matieresKeys.length;
    if (chipThemes) chipThemes.textContent = totalThemes;
  }

  // ==========================================================================
  // VUE 1 : PLANIFICATION PAR MATIÈRE
  // ==========================================================================

  function renderMatiereView() {
    const pData = AppState.curriculum.parcours[AppState.currentParcours];
    if (!pData || !pData.matieres) return;

    renderMatierePills(pData.matieres);
    renderMatiereInfoCard(pData.matieres[AppState.currentMatiere]);
    renderEtapesBoard(pData.matieres[AppState.currentMatiere]);
  }

  function renderMatierePills(matieres) {
    const container = document.getElementById('matieresNavBar');
    if (!container) return;

    container.innerHTML = '';
    Object.keys(matieres).forEach(mKey => {
      const m = matieres[mKey];
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `matiere-pill-btn ${mKey === AppState.currentMatiere ? 'active' : ''}`;
      btn.innerHTML = `<span>${escapeHtml(m.nom)}</span> <span class="code">(${escapeHtml(m.code || '')})</span>`;
      btn.addEventListener('click', () => {
        AppState.currentMatiere = mKey;
        localStorage.setItem(MATIERE_STORAGE_KEY, mKey);
        renderMatiereView();
      });
      container.appendChild(btn);
    });
  }

  function renderMatiereInfoCard(mInfo) {
    const headerTitle = document.getElementById('matiereInfoTitle');
    const headerEl = document.getElementById('matiereInfoHeader');
    const bodyEl = document.getElementById('matiereInfoBody');

    if (!mInfo || !headerTitle || !bodyEl) return;

    headerTitle.innerHTML = `ℹ️ Références et compétences ministérielles : <strong>${escapeHtml(mInfo.nom)}</strong> <small>(${escapeHtml(mInfo.code || '')})</small>`;

    if (AppState.isInfoExpanded) {
      headerEl.classList.add('expanded');
      bodyEl.classList.add('expanded');
    } else {
      headerEl.classList.remove('expanded');
      bodyEl.classList.remove('expanded');
    }

    // Compétences
    const compGrid = document.getElementById('competencesGrid');
    if (compGrid) {
      compGrid.innerHTML = '';
      const comps = mInfo.competences || [];
      comps.forEach(c => {
        const box = document.createElement('div');
        box.className = 'competence-box';
        box.innerHTML = `
          <div class="competence-box-title">${escapeHtml(c.code)} - ${escapeHtml(c.titre)}</div>
          <div class="competence-box-desc">${escapeHtml(c.desc)}</div>
        `;
        compGrid.appendChild(box);
      });
    }

    // Modalités et pondérations
    const enseignantRef = document.getElementById('infoEnseignantRef');
    const pondEtape1 = document.getElementById('infoPondEtape1');
    const pondEtape2 = document.getElementById('infoPondEtape2');
    const pondEtape3 = document.getElementById('infoPondEtape3');
    const evalDesc = document.getElementById('infoEvaluationsDesc');

    if (enseignantRef) enseignantRef.textContent = mInfo.enseignant_ref || 'Planification officielle PFAE';
    if (pondEtape1) pondEtape1.textContent = (mInfo.ponderation && mInfo.ponderation.etape1) || '20 %';
    if (pondEtape2) pondEtape2.textContent = (mInfo.ponderation && mInfo.ponderation.etape2) || '20 %';
    if (pondEtape3) pondEtape3.textContent = (mInfo.ponderation && mInfo.ponderation.etape3) || '60 %';
    if (evalDesc) evalDesc.textContent = mInfo.evaluations_desc || '';
  }

  function renderEtapesBoard(mInfo) {
    if (!mInfo || !mInfo.etapes) return;

    ETAPES_CONFIG.forEach(cfg => {
      const colEl = document.getElementById(`col_${cfg.key}`);
      const countEl = document.getElementById(`count_${cfg.key}`);
      const listEl = document.getElementById(`list_${cfg.key}`);

      const themes = mInfo.etapes[cfg.key] || [];
      if (countEl) countEl.textContent = `${themes.length} thèmes`;

      if (listEl) {
        listEl.innerHTML = '';

        if (themes.length === 0) {
          listEl.innerHTML = `<div class="empty-etape-placeholder">Aucun thème planifié pour cette étape.<br>Cliquez sur <strong>+ Ajouter</strong> pour en insérer un.</div>`;
        } else {
          themes.forEach((theme, idx) => {
            const card = createThemeCard(theme, idx, cfg.key, themes.length);
            listEl.appendChild(card);
          });
        }
      }

      // Gestionnaires drag & drop sur la colonne
      if (colEl && !colEl.hasAttribute('data-drag-init')) {
        colEl.setAttribute('data-drag-init', 'true');
        colEl.addEventListener('dragover', (e) => {
          e.preventDefault();
          e.dataTransfer.dropEffect = 'move';
          colEl.classList.add('drag-over');
        });

        colEl.addEventListener('dragleave', () => {
          colEl.classList.remove('drag-over');
        });

        colEl.addEventListener('drop', (e) => {
          e.preventDefault();
          colEl.classList.remove('drag-over');
          if (!AppState.draggedData) return;

          const { fromStep, fromIndex } = AppState.draggedData;
          if (fromStep !== cfg.key) {
            moveThemeBetweenSteps(AppState.currentMatiere, fromStep, cfg.key, fromIndex);
          }
        });
      }
    });
  }

  function createThemeCard(theme, index, stepKey, totalInStep) {
    const card = document.createElement('div');
    card.className = 'theme-card';
    card.draggable = true;

    // Badges de compétences
    const comps = theme.competences || [];
    const compBadges = comps.map(c => {
      let tagClass = 'tag-c1';
      if (c.includes('2')) tagClass = 'tag-c2';
      if (c.includes('3')) tagClass = 'tag-c3';
      return `<span class="tag ${tagClass}">${escapeHtml(c)}</span>`;
    }).join('');

    const dureeTag = theme.duree_semaines ? `<span class="tag tag-duree">⏱️ ${escapeHtml(theme.duree_semaines)} sem.</span>` : '';
    const axeTag = theme.axe_thematique ? `<span class="tag tag-axe">${escapeHtml(theme.axe_thematique)}</span>` : '';
    const saeTag = theme.sae_projet ? `<span class="tag tag-sae">📁 ${escapeHtml(theme.sae_projet)}</span>` : '';
    const ressourceLine = theme.ressources ? `<div class="theme-card-ressources">📚 <em>${escapeHtml(theme.ressources)}</em></div>` : '';

    // Détermination des boutons disponibles
    const canMovePrev = stepKey === 'etape2' || stepKey === 'etape3';
    const targetPrev = stepKey === 'etape3' ? 'etape2' : (stepKey === 'etape2' ? 'etape1' : null);

    const canMoveNext = stepKey === 'etape1' || stepKey === 'etape2';
    const targetNext = stepKey === 'etape1' ? 'etape2' : (stepKey === 'etape2' ? 'etape3' : null);

    const canMoveUp = index > 0;
    const canMoveDown = index < totalInStep - 1;

    card.innerHTML = `
      <div class="theme-card-header">
        <div class="theme-card-title">${index + 1}. ${escapeHtml(theme.titre || 'Sans titre')}</div>
      </div>
      <div class="theme-card-desc">${escapeHtml(theme.description || '')}</div>
      <div class="theme-card-tags">
        ${compBadges}
        ${dureeTag}
        ${axeTag}
        ${saeTag}
      </div>
      ${ressourceLine}
      <div class="theme-card-toolbar">
        <div class="theme-btn-group">
          ${canMovePrev ? `<button type="button" class="btn-card-action" data-action="prev" title="Déplacer vers l'étape précédente">⬅️</button>` : ''}
          ${canMoveNext ? `<button type="button" class="btn-card-action" data-action="next" title="Déplacer vers l'étape suivante">➡️</button>` : ''}
        </div>
        <div class="theme-btn-group">
          ${canMoveUp ? `<button type="button" class="btn-card-action" data-action="up" title="Monter">⬆️</button>` : ''}
          ${canMoveDown ? `<button type="button" class="btn-card-action" data-action="down" title="Descendre">⬇️</button>` : ''}
        </div>
        <div class="theme-btn-group">
          <button type="button" class="btn-card-action" data-action="edit" title="Modifier le thème">✏️</button>
          <button type="button" class="btn-card-action danger" data-action="delete" title="Supprimer">🗑️</button>
        </div>
      </div>
    `;

    // Événements boutons de carte
    card.querySelectorAll('button[data-action]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const action = btn.getAttribute('data-action');
        if (action === 'prev' && targetPrev) {
          moveThemeBetweenSteps(AppState.currentMatiere, stepKey, targetPrev, index);
        } else if (action === 'next' && targetNext) {
          moveThemeBetweenSteps(AppState.currentMatiere, stepKey, targetNext, index);
        } else if (action === 'up') {
          reorderThemeInStep(AppState.currentMatiere, stepKey, index, -1);
        } else if (action === 'down') {
          reorderThemeInStep(AppState.currentMatiere, stepKey, index, 1);
        } else if (action === 'edit') {
          openThemeModal(true, AppState.currentMatiere, stepKey, index);
        } else if (action === 'delete') {
          confirmDeleteTheme(AppState.currentMatiere, stepKey, index);
        }
      });
    });

    // Événements Drag & Drop
    card.addEventListener('dragstart', (e) => {
      AppState.draggedData = { fromStep: stepKey, fromIndex: index, themeId: theme.id };
      card.classList.add('dragging');
      e.dataTransfer.setData('text/plain', theme.id || '');
      e.dataTransfer.effectAllowed = 'move';
    });

    card.addEventListener('dragend', () => {
      card.classList.remove('dragging');
      AppState.draggedData = null;
    });

    return card;
  }

  // ==========================================================================
  // LOGIQUE DE MANIPULATION DES THÈMES
  // ==========================================================================

  function moveThemeBetweenSteps(matiereKey, fromStep, toStep, index) {
    const etapes = AppState.curriculum.parcours[AppState.currentParcours].matieres[matiereKey].etapes;
    if (etapes[fromStep] && etapes[toStep] && etapes[fromStep][index]) {
      const [item] = etapes[fromStep].splice(index, 1);
      etapes[toStep].push(item);
      saveCurriculumState();
      renderApp();
      showToast(`Thème déplacé vers l'${toStep.replace('etape', 'étape ')}.`);
    }
  }

  function reorderThemeInStep(matiereKey, stepKey, index, delta) {
    const list = AppState.curriculum.parcours[AppState.currentParcours].matieres[matiereKey].etapes[stepKey];
    const newIdx = index + delta;
    if (newIdx >= 0 && newIdx < list.length) {
      const temp = list[index];
      list[index] = list[newIdx];
      list[newIdx] = temp;
      saveCurriculumState();
      renderApp();
    }
  }

  function confirmDeleteTheme(matiereKey, stepKey, index) {
    const list = AppState.curriculum.parcours[AppState.currentParcours].matieres[matiereKey].etapes[stepKey];
    const theme = list[index];
    if (!theme) return;

    if (window.confirm(`Supprimer définitivement le thème "${theme.titre || ''}" ?`)) {
      list.splice(index, 1);
      saveCurriculumState();
      renderApp();
      showToast("Thème supprimé avec succès.", "info");
    }
  }

  // ==========================================================================
  // MODAL D'AJOUT ET D'ÉDITION DE THÈME
  // ==========================================================================

  function openThemeModal(isEdit, matiereKey, stepKey, index = null) {
    AppState.modalContext = { isEdit, matiereKey, stepKey, index };

    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('themeForm');
    const inputTitre = document.getElementById('themeTitre');
    const inputDesc = document.getElementById('themeDesc');
    const inputDuree = document.getElementById('themeDuree');
    const inputAxe = document.getElementById('themeAxe');
    const inputSae = document.getElementById('themeSae');
    const inputRessources = document.getElementById('themeRessources');

    form.reset();

    const mInfo = AppState.curriculum.parcours[AppState.currentParcours].matieres[matiereKey];
    const stepLabel = stepKey === 'etape1' ? 'Étape 1' : (stepKey === 'etape2' ? 'Étape 2' : 'Étape 3');

    if (isEdit) {
      modalTitle.textContent = `Modifier le thème (${stepLabel})`;
      const theme = mInfo.etapes[stepKey][index];
      if (theme) {
        inputTitre.value = theme.titre || '';
        inputDesc.value = theme.description || '';
        inputDuree.value = theme.duree_semaines || 4;
        inputAxe.value = theme.axe_thematique || '';
        inputSae.value = theme.sae_projet || '';
        inputRessources.value = theme.ressources || '';

        const comps = theme.competences || [];
        document.querySelectorAll('input[name="themeComp"]').forEach(chk => {
          chk.checked = comps.includes(chk.value);
        });
      }
    } else {
      modalTitle.textContent = `Ajouter un thème d'apprentissage (${stepLabel})`;
      inputDuree.value = 4;
      document.querySelectorAll('input[name="themeComp"]').forEach((chk, i) => {
        chk.checked = i === 0; // Coche C1 par défaut
      });
    }

    const backdrop = document.getElementById('themeModalBackdrop');
    if (backdrop) backdrop.classList.add('active');
    inputTitre.focus();
  }

  function closeThemeModal() {
    const backdrop = document.getElementById('themeModalBackdrop');
    if (backdrop) backdrop.classList.remove('active');
    AppState.modalContext = null;
  }

  function handleThemeFormSubmit(e) {
    e.preventDefault();
    if (!AppState.modalContext) return;

    const { isEdit, matiereKey, stepKey, index } = AppState.modalContext;
    const inputTitre = document.getElementById('themeTitre');
    const inputDesc = document.getElementById('themeDesc');
    const inputDuree = document.getElementById('themeDuree');
    const inputAxe = document.getElementById('themeAxe');
    const inputSae = document.getElementById('themeSae');
    const inputRessources = document.getElementById('themeRessources');

    const titre = inputTitre.value.trim();
    if (!titre) {
      alert("Le titre du thème est obligatoire.");
      inputTitre.focus();
      return;
    }

    const selectedComps = [];
    document.querySelectorAll('input[name="themeComp"]:checked').forEach(chk => {
      selectedComps.push(chk.value);
    });

    const mEtapes = AppState.curriculum.parcours[AppState.currentParcours].matieres[matiereKey].etapes;

    if (isEdit && index !== null) {
      const theme = mEtapes[stepKey][index];
      if (theme) {
        theme.titre = titre;
        theme.description = inputDesc.value.trim();
        theme.competences = selectedComps;
        theme.duree_semaines = parseInt(inputDuree.value, 10) || 4;
        theme.axe_thematique = inputAxe.value.trim();
        theme.sae_projet = inputSae.value.trim();
        theme.ressources = inputRessources.value.trim();
      }
    } else {
      const newTheme = {
        id: `custom_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
        titre: titre,
        description: inputDesc.value.trim(),
        competences: selectedComps,
        duree_semaines: parseInt(inputDuree.value, 10) || 4,
        axe_thematique: inputAxe.value.trim(),
        sae_projet: inputSae.value.trim(),
        ressources: inputRessources.value.trim()
      };
      mEtapes[stepKey].push(newTheme);
    }

    saveCurriculumState();
    closeThemeModal();
    renderApp();
    showToast(isEdit ? "Thème modifié avec succès !" : "Nouveau thème ajouté avec succès !", "success");
  }

  // ==========================================================================
  // VUE 2 : VUE INTÉGRÉE ANNUELLE (GLOBALE)
  // ==========================================================================

  function renderGlobaleView() {
    renderSynoptiqueTable();
    renderAxesThematiquesMatrix();
  }

  function renderSynoptiqueTable() {
    const container = document.getElementById('synoptiqueTableWrapper');
    if (!container) return;

    const pData = AppState.curriculum.parcours[AppState.currentParcours];
    if (!pData || !pData.matieres) return;

    const query = AppState.searchQuery.toLowerCase().trim();
    const filter = AppState.stepFilter;

    // Colonnes à afficher selon le filtre
    let stepsToShow = ETAPES_CONFIG;
    if (filter !== 'all') {
      stepsToShow = ETAPES_CONFIG.filter(cfg => cfg.key === filter);
    }

    let html = `
      <table class="synoptique-table">
        <thead>
          <tr>
            <th class="col-discipline">Discipline ministérielle</th>
            ${stepsToShow.map(s => `<th>${escapeHtml(s.title)} (${escapeHtml(s.weight)})</th>`).join('')}
          </tr>
        </thead>
        <tbody>
    `;

    let totalMatches = 0;

    Object.keys(pData.matieres).forEach(mKey => {
      const m = pData.matieres[mKey];
      html += `<tr>`;
      html += `<td class="table-discipline-cell">${escapeHtml(m.nom)}<span class="code">${escapeHtml(m.code || '')}</span></td>`;

      stepsToShow.forEach(s => {
        const themes = m.etapes ? (m.etapes[s.key] || []) : [];
        const filteredThemes = themes.filter(t => {
          if (!query) return true;
          return (
            (t.titre && t.titre.toLowerCase().includes(query)) ||
            (t.description && t.description.toLowerCase().includes(query)) ||
            (t.sae_projet && t.sae_projet.toLowerCase().includes(query)) ||
            (t.axe_thematique && t.axe_thematique.toLowerCase().includes(query))
          );
        });

        totalMatches += filteredThemes.length;

        if (filteredThemes.length === 0) {
          html += `<td class="table-empty-cell">${query ? 'Aucun thème correspondant' : 'Aucun thème'}</td>`;
        } else {
          html += `<td><ul class="table-themes-list">`;
          filteredThemes.forEach(t => {
            const comps = (t.competences || []).join(', ');
            const saeText = t.sae_projet ? `<em>(${escapeHtml(t.sae_projet)})</em>` : '';
            html += `
              <li class="table-theme-item">
                <div class="table-theme-item-title">${escapeHtml(t.titre)} ${saeText} <span style="color: #b45309; font-size: 0.72rem;">[${escapeHtml(comps)}]</span></div>
                <div class="table-theme-item-desc">${escapeHtml(t.description || '')}</div>
              </li>
            `;
          });
          html += `</ul></td>`;
        }
      });

      html += `</tr>`;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;

    const countMatchesEl = document.getElementById('searchCountResult');
    if (countMatchesEl) {
      if (query) {
        countMatchesEl.textContent = `${totalMatches} thème(s) trouvé(s) pour "${escapeHtml(query)}"`;
      } else {
        countMatchesEl.textContent = '';
      }
    }
  }

  function renderAxesThematiquesMatrix() {
    const container = document.getElementById('axesAccordionList');
    if (!container) return;

    const pData = AppState.curriculum.parcours[AppState.currentParcours];
    const themesIntegres = AppState.curriculum.themes_integres || [];

    container.innerHTML = '';

    themesIntegres.forEach((axe, index) => {
      const itemEl = document.createElement('div');
      itemEl.className = 'axe-accordion-item';

      const axeName = axe.nom || '';
      const subThemes = axe.sous_themes || [];
      const axeKeyword = axeName.toLowerCase().split(' ')[0];

      // Recherche des projets correspondants dans les disciplines
      const matchingProjects = [];
      if (pData && pData.matieres) {
        Object.keys(pData.matieres).forEach(mKey => {
          const m = pData.matieres[mKey];
          if (m && m.etapes) {
            ['etape1', 'etape2', 'etape3'].forEach(sKey => {
              (m.etapes[sKey] || []).forEach(t => {
                const axeTh = (t.axe_thematique || '').toLowerCase();
                const titleTh = (t.titre || '').toLowerCase();
                const isMatch = axeTh.includes(axeKeyword) || subThemes.some(st => titleTh.includes(st.toLowerCase()));
                if (isMatch) {
                  matchingProjects.push({ matiere: m.nom, step: sKey, theme: t });
                }
              });
            });
          }
        });
      }

      const countBadge = matchingProjects.length > 0 ? `<span class="col-badge" style="background:#095797; color:white; padding: 2px 8px; border-radius:12px; font-size:0.75rem;">${matchingProjects.length} projet(s)</span>` : '';

      itemEl.innerHTML = `
        <div class="axe-accordion-header" data-index="${index}">
          <span>📁 Axe : <strong>${escapeHtml(axeName)}</strong></span>
          <div>${countBadge} <span class="arrow" style="margin-left: 8px;">▼</span></div>
        </div>
        <div class="axe-accordion-body" id="axeBody_${index}">
          <div class="axe-subthemes-tags">
            <strong style="font-size:0.8rem; color:var(--qc-texte-discret); margin-right:4px;">Sous-thèmes ministériels :</strong>
            ${subThemes.map(st => `<span class="tag tag-axe">${escapeHtml(st)}</span>`).join('')}
          </div>
          <div class="axe-projects-grid">
            ${matchingProjects.length === 0 ? '<p style="color:var(--qc-texte-discret); font-style:italic; font-size:0.85rem;">Aucun projet explicitement étiqueté pour cet axe dans ce parcours.</p>' : matchingProjects.map(p => `
              <div class="axe-project-tile">
                <span class="matiere-tag">${escapeHtml(p.matiere)} (${escapeHtml(p.step.replace('etape', 'Étape '))})</span>
                <div class="title">${escapeHtml(p.theme.titre)}</div>
                ${p.theme.sae_projet ? `<div style="font-size:0.78rem; color:#854d0e; font-style:italic;">📁 ${escapeHtml(p.theme.sae_projet)}</div>` : ''}
              </div>
            `).join('')}
          </div>
        </div>
      `;

      const header = itemEl.querySelector('.axe-accordion-header');
      const body = itemEl.querySelector('.axe-accordion-body');
      header.addEventListener('click', () => {
        const isOpen = body.classList.contains('open');
        body.classList.toggle('open', !isOpen);
        header.querySelector('.arrow').textContent = isOpen ? '▼' : '▲';
      });

      container.appendChild(itemEl);
    });
  }

  // ==========================================================================
  // VUE 3 : GESTION, SAUVEGARDE & TÉLÉVERSEMENT
  // ==========================================================================

  function renderGestionView() {
    const fileInput = document.getElementById('jsonFileInput');
    const dropZone = document.getElementById('jsonDropZone');

    if (dropZone && !dropZone.hasAttribute('data-init')) {
      dropZone.setAttribute('data-init', 'true');

      dropZone.addEventListener('click', () => {
        if (fileInput) fileInput.click();
      });

      dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-active');
      });

      dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-active');
      });

      dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-active');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          handleUploadedFile(e.dataTransfer.files[0]);
        }
      });
    }

    if (fileInput && !fileInput.hasAttribute('data-init')) {
      fileInput.setAttribute('data-init', 'true');
      fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
          handleUploadedFile(e.target.files[0]);
        }
      });
    }
  }

  function handleUploadedFile(file) {
    if (!file.name.endsWith('.json')) {
      alert("Veuillez sélectionner un fichier au format .json.");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const parsed = JSON.parse(e.target.result);
        if (!parsed.parcours) {
          throw new Error("Structure de fichier non reconnue (clé 'parcours' manquante).");
        }
        if (window.confirm("Restaurer cette planification ? Les modifications locales actuelles seront remplacées.")) {
          AppState.curriculum = parsed;
          saveCurriculumState();
          ensureValidMatiere();
          renderApp();
          showToast("Planification restaurée avec succès !", "success");
        }
      } catch (err) {
        alert("Erreur lors de la lecture du fichier JSON : " + err.message);
      }
    };
    reader.readAsText(file, 'utf-8');
  }

  function exportCurriculumJSON() {
    const dataStr = JSON.stringify(AppState.curriculum, null, 2);
    const dateStr = new Date().toISOString().slice(0, 10);
    const fileName = `planification_pfae_${AppState.currentParcours.toLowerCase()}_${dateStr}.json`;
    downloadFile(dataStr, fileName, 'application/json');
    showToast("Fichier JSON téléchargé.", "success");
  }

  function exportCurriculumMarkdown() {
    const pData = AppState.curriculum.parcours[AppState.currentParcours];
    if (!pData) return;

    const dateStr = new Date().toISOString().slice(0, 10);
    const lines = [
      `# Planification Annuelle PFAE — ${pData.titre || AppState.currentParcours}`,
      `*Généré le ${dateStr} depuis le Planificateur PFAE (Québec)*\n`,
      `**Description du programme :** ${pData.description || ''}\n`,
      `---\n`
    ];

    Object.keys(pData.matieres || {}).forEach(mKey => {
      const m = pData.matieres[mKey];
      lines.push(`## ${m.nom} (${m.code || ''})`);
      lines.push(`*Enseignant(e)s / Document de référence : ${m.enseignant_ref || 'Planification PFAE'}*\n`);

      ETAPES_CONFIG.forEach(s => {
        lines.push(`### ${s.title} — Pondération : ${s.weight}`);
        const themes = (m.etapes && m.etapes[s.key]) || [];
        if (themes.length === 0) {
          lines.push(`*(Aucun thème planifié)*\n`);
        } else {
          themes.forEach((t, idx) => {
            const comps = (t.competences || []).join(', ');
            lines.push(`- **${idx + 1}. ${t.titre}** [${comps}] (${t.duree_semaines || 4} sem.)`);
            if (t.description) lines.push(`  *Description :* ${t.description}`);
            if (t.sae_projet) lines.push(`  *SAE / Projet :* ${t.sae_projet}`);
            if (t.ressources) lines.push(`  *Ressources :* ${t.ressources}`);
          });
          lines.push(``);
        }
      });
      lines.push(`---\n`);
    });

    const fileName = `rapport_planif_${AppState.currentParcours.toLowerCase()}_${dateStr}.md`;
    downloadFile(lines.join('\n'), fileName, 'text/markdown');
    showToast("Rapport Markdown (.md) téléchargé.", "success");
  }

  function resetToDefaultCurriculum() {
    if (!window.CURRICULUM_DEFAULT_DATA) {
      alert("Données modèles de référence non disponibles.");
      return;
    }
    if (window.confirm("Êtes-vous sûr de vouloir écraser toutes vos modifications et restaurer les données officielles de référence ?")) {
      localStorage.removeItem(STORAGE_KEY);
      AppState.curriculum = JSON.parse(JSON.stringify(window.CURRICULUM_DEFAULT_DATA));
      ensureValidMatiere();
      saveCurriculumState();
      renderApp();
      showToast("Données officielles restaurées.", "info");
    }
  }

  // ==========================================================================
  // UTILITAIRES GÉNÉRAUX
  // ==========================================================================

  function downloadFile(content, fileName, mimeType) {
    const blob = new Blob([content], { type: `${mimeType};charset=utf-8;` });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(15px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // ==========================================================================
  // ÉCOUTEURS D'ÉVÉNEMENTS GLOBAUX
  // ==========================================================================

  function setupEventListeners() {
    // Changement de parcours
    const parcoursSelect = document.getElementById('parcoursSelect');
    if (parcoursSelect) {
      parcoursSelect.addEventListener('change', (e) => {
        AppState.currentParcours = e.target.value;
        localStorage.setItem(PARCOURS_STORAGE_KEY, AppState.currentParcours);
        ensureValidMatiere();
        renderApp();
      });
    }

    // Changement d'onglet de vue principale
    document.querySelectorAll('.qc-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const targetView = btn.getAttribute('data-view');
        if (targetView) {
          AppState.currentView = targetView;
          renderApp();
        }
      });
    });

    // Bascule du volet d'info de la matière
    const matiereInfoHeader = document.getElementById('matiereInfoHeader');
    if (matiereInfoHeader) {
      matiereInfoHeader.addEventListener('click', () => {
        AppState.isInfoExpanded = !AppState.isInfoExpanded;
        renderMatiereInfoCard(AppState.curriculum.parcours[AppState.currentParcours].matieres[AppState.currentMatiere]);
      });
    }

    // Boutons d'ajout de thème dans les colonnes d'étape
    ETAPES_CONFIG.forEach(cfg => {
      const btnAdd = document.getElementById(`btnAddTheme_${cfg.key}`);
      if (btnAdd) {
        btnAdd.addEventListener('click', () => {
          openThemeModal(false, AppState.currentMatiere, cfg.key);
        });
      }
    });

    // Modal formulaire
    const themeForm = document.getElementById('themeForm');
    if (themeForm) {
      themeForm.addEventListener('submit', handleThemeFormSubmit);
    }

    const btnCloseModal = document.getElementById('btnCloseModal');
    const btnCancelModal = document.getElementById('btnCancelModal');
    const modalBackdrop = document.getElementById('themeModalBackdrop');

    if (btnCloseModal) btnCloseModal.addEventListener('click', closeThemeModal);
    if (btnCancelModal) btnCancelModal.addEventListener('click', closeThemeModal);
    if (modalBackdrop) {
      modalBackdrop.addEventListener('click', (e) => {
        if (e.target === modalBackdrop) closeThemeModal();
      });
    }

    // Recherche en temps réel dans la vue synoptique
    const searchInput = document.getElementById('globalSearchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        AppState.searchQuery = e.target.value;
        renderSynoptiqueTable();
      });
    }

    // Filtre d'étape dans la vue synoptique
    const stepFilter = document.getElementById('globalStepFilter');
    if (stepFilter) {
      stepFilter.addEventListener('change', (e) => {
        AppState.stepFilter = e.target.value;
        renderSynoptiqueTable();
      });
    }

    // Boutons d'export et d'impression
    const btnExportJSON = document.getElementById('btnExportJSON');
    const btnExportMD = document.getElementById('btnExportMD');
    const btnResetDefaults = document.getElementById('btnResetDefaults');
    const btnPrintGlobale = document.getElementById('btnPrintGlobale');
    const btnNavPrint = document.getElementById('btnNavPrint');

    if (btnExportJSON) btnExportJSON.addEventListener('click', exportCurriculumJSON);
    if (btnExportMD) btnExportMD.addEventListener('click', exportCurriculumMarkdown);
    if (btnResetDefaults) btnResetDefaults.addEventListener('click', resetToDefaultCurriculum);
    if (btnPrintGlobale) btnPrintGlobale.addEventListener('click', () => window.print());
    if (btnNavPrint) btnNavPrint.addEventListener('click', () => window.print());

    // Fermeture du modal par touche Échap
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && AppState.modalContext) {
        closeThemeModal();
      }
    });
  }

  // Démarrage dès le chargement du DOM
  window.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    initData();
  });

})();
