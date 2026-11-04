/**
 * app.js — Application Mon Stage / Répertoire des Métiers Semi-Spécialisés
 * Conçu pour fonctionner universellement :
 *   - En direct via file:/// (double-clic explorateur Windows)
 *   - Sur serveur HTTP / HTTPS (GitHub Pages, Azure Static Web Apps)
 * Respect strict des règles du projet : pas de classes (réservées aux Web Components).
 */

(() => {
  'use strict';

  /* ==========================================================================
     1. PICTOGRAMMES VECTORIELS INLINE (Icons)
     ========================================================================== */
  const ICONS = {
    search: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
    arrowLeft: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>`,
    print: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>`,
    check: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
    refresh: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-1.19"></path></svg>`,
    alert: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
    close: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,
    bookOpen: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>`,
    clipboardList: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect><path d="M9 12h6"></path><path d="M9 16h6"></path></svg>`,
    trash: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`,
    undo: `<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>`,
    edit: `<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>`
  };

  /* ==========================================================================
     2. GESTION DU STOCKAGE LOCAL (storage)
     ========================================================================== */
  const STORAGE_PREFIX = 'fms_stage';

  function getStorageKey(metierId, keyType) {
    return `${STORAGE_PREFIX}:${metierId}:${keyType}`;
  }

  function getStoredJson(key, defaultValue) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return defaultValue;
      return JSON.parse(raw);
    } catch (err) {
      return defaultValue;
    }
  }

  function setStoredJson(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (err) {
      return false;
    }
  }

  function loadProgress(metierId) {
    if (!metierId) return [];
    const key = getStorageKey(String(metierId), 'tasks');
    const result = getStoredJson(key, []);
    return Array.isArray(result) ? result.map(String) : [];
  }

  function saveProgress(metierId, taskIds) {
    if (!metierId) return false;
    const key = getStorageKey(String(metierId), 'tasks');
    const validList = Array.isArray(taskIds) ? taskIds.map(String) : [];
    return setStoredJson(key, validList);
  }

  function toggleTask(metierId, taskId) {
    const current = loadProgress(metierId);
    const idStr = String(taskId);
    const exists = current.includes(idStr);
    const updated = exists ? current.filter((id) => id !== idStr) : [...current, idStr];
    saveProgress(metierId, updated);
    return updated;
  }

  function loadExclusions(metierId) {
    if (!metierId) return { comps: [], tasks: [], criteria: [] };
    const key = getStorageKey(String(metierId), 'exclusions');
    const res = getStoredJson(key, { comps: [], tasks: [], criteria: [] });
    return {
      comps: Array.isArray(res.comps) ? res.comps.map(String) : [],
      tasks: Array.isArray(res.tasks) ? res.tasks.map(String) : [],
      criteria: Array.isArray(res.criteria) ? res.criteria.map(String) : []
    };
  }

  function saveExclusions(metierId, exclusions) {
    if (!metierId) return false;
    const key = getStorageKey(String(metierId), 'exclusions');
    return setStoredJson(key, {
      comps: Array.isArray(exclusions.comps) ? exclusions.comps.map(String) : [],
      tasks: Array.isArray(exclusions.tasks) ? exclusions.tasks.map(String) : [],
      criteria: Array.isArray(exclusions.criteria) ? exclusions.criteria.map(String) : []
    });
  }

  function excludeItem(metierId, type, id) {
    const current = loadExclusions(metierId);
    const idStr = String(id);
    if (!current[type].includes(idStr)) {
      current[type].push(idStr);
      saveExclusions(metierId, current);
    }
    return current;
  }

  function restoreItem(metierId, type, id) {
    const current = loadExclusions(metierId);
    const idStr = String(id);
    current[type] = current[type].filter((item) => item !== idStr);
    saveExclusions(metierId, current);
    return current;
  }

  function resetExclusions(metierId) {
    if (!metierId) return false;
    const key = getStorageKey(String(metierId), 'exclusions');
    try {
      localStorage.removeItem(key);
      return true;
    } catch (err) {
      return false;
    }
  }

  function loadStageInfo(metierId) {
    if (!metierId) return { eleveNom: '', milieuStage: '', enseignantNom: '', dateDebut: '' };
    const key = getStorageKey(String(metierId), 'info');
    return getStoredJson(key, { eleveNom: '', milieuStage: '', enseignantNom: '', dateDebut: '' });
  }

  function saveStageInfo(metierId, info) {
    if (!metierId) return false;
    const key = getStorageKey(String(metierId), 'info');
    return setStoredJson(key, info);
  }

  function resetStageTracking(metierId) {
    if (!metierId) return false;
    const mid = String(metierId);
    try {
      localStorage.removeItem(getStorageKey(mid, 'tasks'));
      localStorage.removeItem(getStorageKey(mid, 'info'));
      return true;
    } catch (err) {
      return false;
    }
  }

  /* ==========================================================================
     3. COMPOSANTS WEB (Web Components)
     ========================================================================== */

  /**
   * <metier-card> — Vignette synthétique d'un métier
   */
  class MetierCard extends HTMLElement {
    constructor() {
      super();
      this._data = null;
    }

    set metier(data) {
      this._data = data;
      this.render();
    }

    connectedCallback() {
      if (this._data) this.render();
    }

    render() {
      if (!this._data) return;
      const m = this._data;

      this.innerHTML = `
        <article class="metier-card" tabindex="0" role="region" aria-label="${m.nom}">
          <div class="card-top">
            <div class="card-tags">
              <span class="tag-secteur">Secteur ${m.secteur_code} — ${m.secteur}</span>
              ${m.top_montreal ? `<span class="tag-montreal">Priorité Montréal</span>` : ''}
              ${m.requires_license ? `<span class="tag-restriction">Permis classe 5</span>` : ''}
              ${m.requires_16plus ? `<span class="tag-restriction">16 ans minimum</span>` : ''}
              ${m.requires_background_check ? `<span class="tag-restriction">Vérification antécédents</span>` : ''}
            </div>

            <h2 class="card-title">
              <a href="#/metier/${m.id}" class="card-action-link" aria-label="Consulter la fiche ${m.nom}">
                ${m.nom}
              </a>
            </h2>

            <div class="card-codes">
              <span class="card-code-item">FGJ: <strong>${m.code_fgj}</strong></span>
              ${m.code_fga ? `<span class="card-code-item">FGA: <strong>${m.code_fga}</strong></span>` : ''}
              ${m.autres_appellations ? `<span class="card-code-item">(${m.autres_appellations.split(';')[0]})</span>` : ''}
            </div>

            ${m.champ_application ? `
              <p class="card-desc">${m.champ_application}</p>
            ` : ''}
          </div>

          <div class="card-bottom">
            <div class="card-metrics">
              <span><strong class="card-metrics-val">${m.nb_competences}</strong> comp.</span>
              <span>•</span>
              <span><strong class="card-metrics-val">${m.nb_taches}</strong> tâches</span>
              <span>•</span>
              <span><strong class="card-metrics-val">${m.nb_criteres}</strong> critères</span>
            </div>

            <a href="#/metier/${m.id}" class="btn btn-secondary" aria-label="Voir la fiche complète de ${m.nom}">
              Consulter
            </a>
          </div>
        </article>
      `;

      const card = this.querySelector('.metier-card');
      if (card) {
        card.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' && e.target === card) {
            window.location.hash = `#/metier/${m.id}`;
          }
        });
      }
    }
  }

  if (!customElements.get('metier-card')) {
    customElements.define('metier-card', MetierCard);
  }

  /**
   * <metier-list> — Recherche, filtres et catalogue complet
   */
  class MetierList extends HTMLElement {
    constructor() {
      super();
      this._metiers = [];
      this._searchTerm = '';
      this._selectedSecteur = 'ALL';
      this._selectedCondition = 'ALL';
      this._onlyMontreal = true;
    }

    set metiers(list) {
      this._metiers = Array.isArray(list) ? list : [];
      this.render();
    }

    connectedCallback() {
      this.render();
    }

    getSecteurs() {
      const map = new Map();
      this._metiers.forEach((m) => {
        const code = m.secteur_code || '00';
        if (!map.has(code)) {
          map.set(code, { code, nom: m.secteur || `Secteur ${code}`, count: 0 });
        }
        map.get(code).count++;
      });
      return Array.from(map.values()).sort((a, b) => a.code.localeCompare(b.code));
    }

    getFilteredMetiers() {
      return this._metiers.filter((m) => {
        if (this._onlyMontreal && !m.top_montreal) return false;
        if (this._selectedSecteur !== 'ALL' && m.secteur_code !== this._selectedSecteur) return false;
        if (this._selectedCondition === 'NO_PERMIT' && m.requires_license) return false;
        if (this._selectedCondition === 'UNDER_16' && m.requires_16plus) return false;
        if (this._selectedCondition === 'NO_RECORD_CHECK' && m.requires_background_check) return false;

        if (this._searchTerm.trim() !== '') {
          const q = this._searchTerm.toLowerCase().trim();
          const matchesName = m.nom.toLowerCase().includes(q);
          const matchesCodeFGJ = (m.code_fgj || '').toLowerCase().includes(q);
          const matchesCodeFGA = (m.code_fga || '').toLowerCase().includes(q);
          const matchesSecteur = (m.secteur || '').toLowerCase().includes(q);
          const matchesApp = (m.autres_appellations || '').toLowerCase().includes(q);
          const matchesChamp = (m.champ_application || '').toLowerCase().includes(q);

          if (!matchesName && !matchesCodeFGJ && !matchesCodeFGA && !matchesSecteur && !matchesApp && !matchesChamp) {
            return false;
          }
        }
        return true;
      });
    }

    render() {
      const filtered = this.getFilteredMetiers();
      const secteurs = this.getSecteurs();
      const totalCount = this._metiers.length;
      const filteredCount = filtered.length;

      this.innerHTML = `
        <section class="filter-card" aria-label="Recherche et filtres de métiers">
          <div class="filter-row-primary">
            <div class="search-field">
              <span class="search-field-icon">${ICONS.search}</span>
              <input 
                type="search" 
                id="metierSearchInput" 
                class="search-field-input" 
                placeholder="Rechercher par titre, code (ex: 8118, M118), mot-clé (ex: épicerie, cuisine, coiffure)..."
                value="${this._escapeHtml(this._searchTerm)}"
                aria-label="Rechercher un métier semi-spécialisé"
              />
              ${this._searchTerm ? `
                <button type="button" id="clearSearchBtn" class="search-clear-btn" aria-label="Effacer la recherche">
                  ${ICONS.close}
                </button>
              ` : ''}
            </div>

            <div class="filter-toggles">
              <button 
                type="button" 
                id="toggleMtlBtn" 
                class="btn btn-toggle ${this._onlyMontreal ? 'active' : ''}" 
                aria-pressed="${this._onlyMontreal}"
                aria-label="Filtrer les métiers phares à Montréal"
              >
                ${this._onlyMontreal ? ICONS.check : ''}
                <span>Métiers phares Montréal</span>
              </button>
            </div>
          </div>

          <div class="filter-row-secondary">
            <div class="select-wrapper">
              <label for="secteurSelect" class="select-label">Secteur de formation</label>
              <select id="secteurSelect" class="select-input" aria-label="Filtrer par secteur de formation">
                <option value="ALL">Tous les secteurs (${totalCount} métiers)</option>
                ${secteurs.map((s) => `
                  <option value="${s.code}" ${this._selectedSecteur === s.code ? 'selected' : ''}>
                    ${s.code} — ${s.nom} (${s.count})
                  </option>
                `).join('')}
              </select>
            </div>

            <div class="select-wrapper">
              <label for="conditionSelect" class="select-label">Conditions particulières</label>
              <select id="conditionSelect" class="select-input" aria-label="Filtrer selon les conditions d'admission">
                <option value="ALL" ${this._selectedCondition === 'ALL' ? 'selected' : ''}>Toutes les conditions</option>
                <option value="NO_PERMIT" ${this._selectedCondition === 'NO_PERMIT' ? 'selected' : ''}>Sans permis de conduire requis</option>
                <option value="UNDER_16" ${this._selectedCondition === 'UNDER_16' ? 'selected' : ''}>Accessible aux moins de 16 ans</option>
                <option value="NO_RECORD_CHECK" ${this._selectedCondition === 'NO_RECORD_CHECK' ? 'selected' : ''}>Sans vérification d'antécédents</option>
              </select>
            </div>

            <div class="select-wrapper" style="justify-content: flex-end;">
              <span class="select-label">&nbsp;</span>
              <button type="button" id="resetFiltersBtn" class="btn btn-secondary" aria-label="Réinitialiser tous les filtres">
                Réinitialiser
              </button>
            </div>
          </div>

          <div class="results-info-bar" role="status" aria-live="polite">
            <div>
              Affichage de <span class="results-count">${filteredCount}</span> sur ${totalCount} métiers
              ${this._onlyMontreal ? ' (Sélection prioritaire Montréal)' : ' (Tous les métiers urbains)'}
            </div>
            ${(this._searchTerm || this._selectedSecteur !== 'ALL' || this._selectedCondition !== 'ALL') ? `
              <div><span class="badge-tag">Filtres appliqués</span></div>
            ` : ''}
          </div>
        </section>

        <section class="metiers-grid-section" aria-label="Liste des métiers semi-spécialisés">
          ${filteredCount > 0 ? `
            <div class="metiers-grid">
              ${filtered.map((m) => `<metier-card data-id="${m.id}"></metier-card>`).join('')}
            </div>
          ` : `
            <div class="empty-state-card" style="background-color: var(--qc-surface); border: 1px solid var(--qc-bordure); border-radius: var(--radius-lg); padding: 40px 20px; text-align: center;">
              <p style="font-size: 1.1rem; font-weight: 700; color: var(--qc-texte);">Aucun métier ne correspond à vos critères de recherche.</p>
              <p style="color: var(--qc-texte-discret); margin-top: 8px;">Essayez de modifier votre mot-clé ou désactivez le filtre Montréal pour élargir les résultats.</p>
              <button type="button" id="emptyResetBtn" class="btn btn-primary" style="margin-top: 16px;">
                Afficher tous les métiers
              </button>
            </div>
          `}
        </section>
      `;

      const cardEls = this.querySelectorAll('metier-card');
      cardEls.forEach((el) => {
        const id = el.getAttribute('data-id');
        const data = filtered.find((m) => m.id === id);
        if (data) el.metier = data;
      });

      this._bindEvents();
    }

    _escapeHtml(str) {
      if (!str) return '';
      return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    _bindEvents() {
      const searchInput = this.querySelector('#metierSearchInput');
      if (searchInput) {
        searchInput.addEventListener('input', (e) => {
          this._searchTerm = e.target.value;
          this.render();
          const newInp = this.querySelector('#metierSearchInput');
          if (newInp) {
            newInp.focus();
            newInp.setSelectionRange(this._searchTerm.length, this._searchTerm.length);
          }
        });
      }

      const clearBtn = this.querySelector('#clearSearchBtn');
      if (clearBtn) {
        clearBtn.addEventListener('click', () => {
          this._searchTerm = '';
          this.render();
        });
      }

      const mtlBtn = this.querySelector('#toggleMtlBtn');
      if (mtlBtn) {
        mtlBtn.addEventListener('click', () => {
          this._onlyMontreal = !this._onlyMontreal;
          this.render();
        });
      }

      const secSelect = this.querySelector('#secteurSelect');
      if (secSelect) {
        secSelect.addEventListener('change', (e) => {
          this._selectedSecteur = e.target.value;
          this.render();
        });
      }

      const condSelect = this.querySelector('#conditionSelect');
      if (condSelect) {
        condSelect.addEventListener('change', (e) => {
          this._selectedCondition = e.target.value;
          this.render();
        });
      }

      const resetBtn = this.querySelector('#resetFiltersBtn');
      if (resetBtn) {
        resetBtn.addEventListener('click', () => {
          this._searchTerm = '';
          this._selectedSecteur = 'ALL';
          this._selectedCondition = 'ALL';
          this._onlyMontreal = true;
          this.render();
        });
      }

      const emptyResetBtn = this.querySelector('#emptyResetBtn');
      if (emptyResetBtn) {
        emptyResetBtn.addEventListener('click', () => {
          this._searchTerm = '';
          this._selectedSecteur = 'ALL';
          this._selectedCondition = 'ALL';
          this._onlyMontreal = false;
          this.render();
        });
      }
    }
  }

  if (!customElements.get('metier-list')) {
    customElements.define('metier-list', MetierList);
  }

  /**
   * <metier-detail> — Fiche détaillée & Grille d'évaluation
   * Inclut désormais le mode d'adaptation / personnalisation pour l'enseignant.
   */
  class MetierDetail extends HTMLElement {
    constructor() {
      super();
      this._metier = null;
      this._activeTab = 'fiche';
      this._isCustomizing = false;
      this._showExcludedDrawer = false;
      this._completedTaskIds = [];
      this._exclusions = { comps: [], tasks: [], criteria: [] };
      this._stageInfo = { eleveNom: '', milieuStage: '', enseignantNom: '', dateDebut: '' };
    }

    set metier(data) {
      this._metier = data;
      if (data) {
        this._completedTaskIds = loadProgress(data.id);
        this._exclusions = loadExclusions(data.id);
        this._stageInfo = loadStageInfo(data.id);
      }
      this.render();
    }

    connectedCallback() {
      if (this._metier) this.render();
    }

    /**
     * Retourne les données filtrées sans les éléments exclus par l'enseignant
     */
    getActiveData() {
      if (!this._metier) return { competences: [], totalTasks: 0, completedTasks: 0, totalExcluded: 0 };

      const exComps = this._exclusions.comps;
      const exTasks = this._exclusions.tasks;
      const exCrit = this._exclusions.criteria;

      let totalTasks = 0;
      let totalExcluded = exComps.length + exTasks.length + exCrit.length;

      const activeComps = (this._metier.competences || [])
        .filter((comp) => !exComps.includes(String(comp.code)))
        .map((comp) => {
          const activeTasks = (comp.taches || []).filter((t) => {
            const taskIdStr = `${this._metier.id}::${t.ordre}`;
            return !exTasks.includes(taskIdStr);
          });

          const activeCrit = (comp.criteres || []).filter((c) => {
            const critIdStr = `${this._metier.id}::${comp.code}::${c.ordre}`;
            return !exCrit.includes(critIdStr);
          });

          totalTasks += activeTasks.length;

          return {
            ...comp,
            taches: activeTasks,
            criteres: activeCrit
          };
        });

      const completedTasks = this._completedTaskIds.filter((tid) => !exTasks.includes(tid)).length;
      const percent = totalTasks > 0 ? Math.min(100, Math.round((completedTasks / totalTasks) * 100)) : 0;

      return {
        competences: activeComps,
        totalTasks,
        completedTasks,
        percent,
        totalExcluded
      };
    }

    /**
     * Collecte la liste détaillée des éléments exclus pour affichage dans le volet de restauration
     */
    getExcludedItemsList() {
      if (!this._metier) return { comps: [], tasks: [], criteria: [] };
      const exComps = this._exclusions.comps;
      const exTasks = this._exclusions.tasks;
      const exCrit = this._exclusions.criteria;

      const res = { comps: [], tasks: [], criteria: [] };

      (this._metier.competences || []).forEach((c) => {
        const cCodeStr = String(c.code);
        if (exComps.includes(cCodeStr)) {
          res.comps.push({ id: cCodeStr, label: `Compétence ${c.code} — ${c.intitule}` });
        } else {
          // Si la compétence n'est pas exclue, vérifier ses tâches et critères
          (c.taches || []).forEach((t) => {
            const taskIdStr = `${this._metier.id}::${t.ordre}`;
            if (exTasks.includes(taskIdStr)) {
              res.tasks.push({ id: taskIdStr, label: `Tâche (Comp. ${c.code}) : ${t.texte}` });
            }
          });

          (c.criteres || []).forEach((cr) => {
            const critIdStr = `${this._metier.id}::${c.code}::${cr.ordre}`;
            if (exCrit.includes(critIdStr)) {
              res.criteria.push({ id: critIdStr, label: `Critère (Comp. ${c.code}) : ${cr.texte}` });
            }
          });
        }
      });

      return res;
    }

    render() {
      if (!this._metier) {
        this.innerHTML = `
          <div class="empty-state-card" style="background-color: var(--qc-surface); border: 1px solid var(--qc-bordure); border-radius: var(--radius-lg); padding: 40px; text-align: center;">
            <p style="font-size: 1.1rem; font-weight: 700;">Aucun métier sélectionné</p>
            <a href="#/" class="btn btn-primary" style="margin-top: 16px;">
              ${ICONS.arrowLeft} <span>Retour au répertoire</span>
            </a>
          </div>
        `;
        return;
      }

      const m = this._metier;
      const activeData = this.getActiveData();
      const excludedList = this.getExcludedItemsList();
      const isGrille = this._activeTab === 'grille';
      const isCustomizing = this._isCustomizing;
      const hasExclusions = activeData.totalExcluded > 0;

      this.innerHTML = `
        <div class="detail-view">
          <nav class="detail-nav-bar" aria-label="Navigation de la fiche">
            <a href="#/" class="btn-back" aria-label="Retourner à la liste des métiers">
              ${ICONS.arrowLeft} <span>Retour au répertoire des métiers</span>
            </a>

            <div class="header-badges">
              <span class="badge-tag montreal">Secteur ${m.secteur_code} — ${m.secteur}</span>
              ${m.top_montreal ? `<span class="tag-montreal">Priorité Montréal</span>` : ''}
              ${hasExclusions ? `<span class="tag-montreal" style="background-color: var(--qc-bleu-subtil); color: var(--qc-bleu-principal); border-color: var(--qc-bordure-accent);">Fiche personnalisée</span>` : ''}
            </div>
          </nav>

          <header class="detail-header-card">
            <div class="detail-header-tags">
              <span class="tag-secteur">Secteur ${m.secteur_code}</span>
              <span class="card-code-item">Code FGJ: <strong>${m.code_fgj}</strong></span>
              ${m.code_fga ? `<span class="card-code-item">Code FGA: <strong>${m.code_fga}</strong></span>` : ''}
              ${hasExclusions ? `<span class="badge-tag" style="background-color: var(--qc-succes-bg); color: var(--qc-succes); border-color: var(--qc-succes-bordure);">Adaptée au stage</span>` : ''}
            </div>

            <h1 class="detail-title">${m.nom}</h1>

            ${m.autres_appellations ? `
              <div class="detail-section-block">
                <span class="detail-section-title">Autres appellations reconnues dans le milieu du travail :</span>
                <p class="detail-section-text">${m.autres_appellations}</p>
              </div>
            ` : ''}

            ${m.champ_application ? `
              <div class="detail-section-block">
                <span class="detail-section-title">Champ d'application et milieu de stage :</span>
                <p class="detail-section-text">${m.champ_application}</p>
              </div>
            ` : ''}

            ${m.conditions_admission ? `
              <div class="conditions-alert-box" role="alert">
                <div class="conditions-alert-icon">${ICONS.alert}</div>
                <div class="conditions-alert-content">
                  <strong>Conditions particulières d'admission au stage :</strong>
                  <p style="margin-top: 4px;">${m.conditions_admission}</p>
                </div>
              </div>
            ` : ''}
          </header>

          <!-- Bandeau d'état de personnalisation -->
          ${hasExclusions ? `
            <section class="custom-banner" aria-label="État de personnalisation de la fiche">
              <div class="custom-banner-text">
                <span>Fiche adaptée : <strong>${activeData.totalExcluded} élément(s) retiré(s)</strong> pour ce milieu de stage.</span>
              </div>
              <div class="custom-banner-actions">
                <button type="button" id="toggleExcludedDrawerBtn" class="btn btn-secondary" style="min-height: 36px; padding: 4px 12px; font-size: 0.8rem;">
                  ${this._showExcludedDrawer ? 'Masquer la liste' : 'Gérer / Restaurer les éléments'}
                </button>
                <button type="button" id="resetExclusionsBtn" class="btn btn-danger" style="min-height: 36px; padding: 4px 12px; font-size: 0.8rem;">
                  ${ICONS.undo} <span>Rétablir le programme officiel</span>
                </button>
              </div>
            </section>
          ` : ''}

          <!-- Volet déroulant des éléments exclus -->
          ${(this._showExcludedDrawer && hasExclusions) ? `
            <section class="excluded-drawer" aria-label="Liste des éléments exclus du plan de formation">
              <div class="excluded-drawer-header">
                <span>Éléments retirés du plan de stage (${activeData.totalExcluded})</span>
                <button type="button" id="closeDrawerBtn" class="btn-exclude-item" aria-label="Fermer le volet">${ICONS.close}</button>
              </div>
              <div class="excluded-list">
                ${excludedList.comps.map((c) => `
                  <div class="excluded-item-row">
                    <span>${c.label}</span>
                    <button type="button" class="btn-restore" data-type="comps" data-id="${c.id}">${ICONS.undo} <span>Restaurer</span></button>
                  </div>
                `).join('')}
                ${excludedList.tasks.map((t) => `
                  <div class="excluded-item-row">
                    <span>${t.label}</span>
                    <button type="button" class="btn-restore" data-type="tasks" data-id="${t.id}">${ICONS.undo} <span>Restaurer</span></button>
                  </div>
                `).join('')}
                ${excludedList.criteria.map((cr) => `
                  <div class="excluded-item-row">
                    <span>${cr.label}</span>
                    <button type="button" class="btn-restore" data-type="criteria" data-id="${cr.id}">${ICONS.undo} <span>Restaurer</span></button>
                  </div>
                `).join('')}
              </div>
            </section>
          ` : ''}

          <!-- Barre d'outils Enseignant : Choix du mode et Actions -->
          <section class="teacher-toolbar" aria-label="Actions de l'enseignant">
            <div class="toolbar-tabs" role="tablist">
              <button 
                type="button" 
                id="tabFicheBtn" 
                class="tab-btn ${!isGrille ? 'active' : ''}" 
                role="tab" 
                aria-selected="${!isGrille}"
                aria-label="Mode Fiche pédagogique"
              >
                ${ICONS.bookOpen} <span>Fiche pédagogique</span>
              </button>
              <button 
                type="button" 
                id="tabGrilleBtn" 
                class="tab-btn ${isGrille ? 'active' : ''}" 
                role="tab" 
                aria-selected="${isGrille}"
                aria-label="Mode Grille de suivi de stage"
              >
                ${ICONS.clipboardList} <span>Grille de suivi de stage</span>
              </button>
            </div>

            <div class="toolbar-actions">
              <!-- Bascule du mode Personnalisation / Retrait d'éléments -->
              <button 
                type="button" 
                id="toggleCustomizeBtn" 
                class="btn ${isCustomizing ? 'btn-primary' : 'btn-secondary'}" 
                aria-pressed="${isCustomizing}"
                aria-label="Activer ou désactiver le mode d'adaptation de la fiche"
                title="Supprimer des compétences, tâches ou critères inapplicables au milieu de stage"
              >
                ${ICONS.edit} <span>${isCustomizing ? 'Terminer l’adaptation' : 'Adapter la fiche (Retraits)'}</span>
              </button>

              <button type="button" id="printBtn" class="btn btn-secondary" aria-label="Imprimer la fiche de stage ou sauvegarder en PDF">
                ${ICONS.print} <span>Imprimer la fiche</span>
              </button>
              ${isGrille ? `
                <button type="button" id="openResetModalBtn" class="btn btn-danger" aria-label="Réinitialiser les tâches cochées pour ce stage">
                  ${ICONS.refresh} <span>Réinitialiser suivi</span>
                </button>
              ` : ''}
            </div>
          </section>

          ${isCustomizing ? `
            <div style="background-color: var(--qc-surface); border: 1px solid var(--qc-bleu-principal); border-radius: var(--radius-md); padding: 10px 16px; font-size: 0.88rem; color: var(--qc-texte-secondaire); display: flex; align-items: center; justify-content: space-between;">
              <span><strong>Mode adaptation actif :</strong> Cliquez sur le bouton de suppression à côté d'une compétence, d'une tâche ou d'un critère pour le retirer du plan de stage de l'élève.</span>
              <button type="button" id="finishCustomizeBtn" class="btn btn-primary" style="min-height: 36px; padding: 4px 12px; font-size: 0.8rem;">
                Terminer
              </button>
            </div>
          ` : ''}

          ${isGrille ? `
            <section class="stage-info-card" style="background-color: var(--qc-surface); border: 1px solid var(--qc-bordure); border-radius: var(--radius-lg); padding: 18px 20px; box-shadow: var(--shadow-sm);">
              <h2 style="font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--qc-texte-secondaire); margin-bottom: 12px;">
                Identification du stage de l'élève
              </h2>
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px;">
                <div class="select-wrapper">
                  <label for="eleveNomInput" class="select-label">Nom de l'élève</label>
                  <input type="text" id="eleveNomInput" class="select-input" value="${this._escapeHtml(this._stageInfo.eleveNom)}" placeholder="Prénom et nom de l'élève" />
                </div>
                <div class="select-wrapper">
                  <label for="milieuStageInput" class="select-label">Entreprise / Milieu de stage</label>
                  <input type="text" id="milieuStageInput" class="select-input" value="${this._escapeHtml(this._stageInfo.milieuStage)}" placeholder="Nom de l'entreprise" />
                </div>
                <div class="select-wrapper">
                  <label for="enseignantNomInput" class="select-label">Enseignant(e) superviseur(e)</label>
                  <input type="text" id="enseignantNomInput" class="select-input" value="${this._escapeHtml(this._stageInfo.enseignantNom)}" placeholder="Nom de l'enseignant" />
                </div>
              </div>
            </section>

            <section class="progress-status-bar" aria-label="Progression des tâches acquises">
              <div class="progress-text">
                Progression : <strong>${activeData.completedTasks}</strong> sur <strong>${activeData.totalTasks}</strong> tâches actives acquises (${activeData.percent}%)
                ${hasExclusions ? ` <span style="font-size: 0.8rem; color: var(--qc-texte-discret); font-weight: normal;">(sur plan personnalisé)</span>` : ''}
              </div>
              <div class="progress-bar-track" aria-hidden="true">
                <div class="progress-bar-fill" style="width: ${activeData.percent}%;"></div>
              </div>
            </section>
          ` : ''}

          <main class="competences-container" aria-label="Compétences ministérielles du métier">
            ${activeData.competences.map((comp) => {
              const isOpt = comp.optionnelle;
              const isSpec = comp.type === 'specifique';

              return `
                <article class="comp-card" id="comp-${comp.code}" aria-label="Compétence ${comp.code} : ${comp.intitule}">
                  <header class="comp-header">
                    <div class="comp-header-main">
                      <span class="comp-code-badge">${comp.code}</span>
                      <h2 class="comp-title">${comp.intitule}</h2>
                    </div>

                    <div class="comp-badges">
                      <span class="badge-comp-type ${comp.type}">
                        ${isSpec ? 'Compétence spécifique' : 'Compétence récurrente'}
                      </span>
                      ${isOpt ? `<span class="badge-comp-opt">Optionnelle</span>` : ''}
                      ${comp.complexite ? `<span class="badge-complexity">Complexité ${comp.complexite}</span>` : ''}
                      ${isCustomizing ? `
                        <button type="button" class="btn-exclude-comp" data-comp-code="${comp.code}" title="Retirer cette compétence du plan de stage" aria-label="Retirer la compétence ${comp.code}">
                          ${ICONS.trash} <span>Retirer compétence</span>
                        </button>
                      ` : ''}
                    </div>
                  </header>

                  <div class="comp-body">
                    <!-- Colonne 1 : Tâches -->
                    <div class="comp-tasks-column">
                      <div class="comp-subcol-title">
                        <span>Tâches du métier (${(comp.taches || []).length})</span>
                        ${isGrille ? `<span style="font-size: 0.75rem; text-transform: none; color: var(--qc-texte-discret);">Cocher si acquise</span>` : ''}
                      </div>

                      <div class="task-items-list" role="list">
                        ${(comp.taches || []).map((t) => {
                          const taskIdStr = `${m.id}::${t.ordre}`;
                          const isCompleted = this._completedTaskIds.includes(taskIdStr);

                          return `
                            <div class="task-item ${isCompleted ? 'completed' : ''}" role="listitem">
                              ${isGrille ? `
                                <label class="task-checkbox-label">
                                  <input 
                                    type="checkbox" 
                                    class="task-checkbox" 
                                    data-task-id="${taskIdStr}"
                                    ${isCompleted ? 'checked' : ''}
                                    aria-label="${t.texte}"
                                  />
                                  <span class="task-text">
                                    <strong>${t.ordre_comp || t.ordre}.</strong> ${t.texte}
                                    ${t.optionnelle ? `<span class="task-opt-tag">(optionnelle)</span>` : ''}
                                  </span>
                                </label>
                              ` : `
                                <div style="display: flex; gap: 10px; align-items: flex-start; padding: 4px 0; width: 100%;">
                                  <span style="font-size: 0.82rem; font-weight: 700; color: var(--qc-texte-discret); min-width: 22px;">
                                    ${t.ordre_comp || t.ordre}.
                                  </span>
                                  <span class="task-text" style="flex: 1;">
                                    ${t.texte}
                                    ${t.optionnelle ? `<span class="task-opt-tag">(optionnelle)</span>` : ''}
                                  </span>
                                </div>
                              `}
                              ${isCustomizing ? `
                                <button type="button" class="btn-exclude-item btn-exclude-task" data-task-id="${taskIdStr}" aria-label="Retirer cette tâche" title="Retirer cette tâche du plan de stage">
                                  ${ICONS.trash}
                                </button>
                              ` : ''}
                            </div>
                          `;
                        }).join('')}
                      </div>
                    </div>

                    <!-- Colonne 2 : Critères d'évaluation -->
                    <div class="comp-criteria-column">
                      <div class="comp-subcol-title">
                        <span>Critères d'évaluation officiels (${(comp.criteres || []).length})</span>
                      </div>

                      ${(comp.criteres || []).length > 0 ? `
                        <div class="criteria-items-list" role="list">
                          ${comp.criteres.map((c) => {
                            const critIdStr = `${m.id}::${comp.code}::${c.ordre}`;

                            return `
                              <div class="criterion-item" role="listitem">
                                <span class="criterion-num">${c.ordre}.</span>
                                <span class="criterion-text" style="flex: 1;">${c.texte}</span>
                                ${isCustomizing ? `
                                  <button type="button" class="btn-exclude-item btn-exclude-crit" data-criterion-id="${critIdStr}" aria-label="Retirer ce critère" title="Retirer ce critère d'évaluation">
                                    ${ICONS.trash}
                                  </button>
                                ` : ''}
                              </div>
                            `;
                          }).join('')}
                        </div>
                      ` : `
                        <p style="font-size: 0.85rem; color: var(--qc-texte-discret); font-style: italic;">
                          Critères intégrés aux critères généraux du programme.
                        </p>
                      `}
                    </div>
                  </div>
                </article>
              `;
            }).join('')}
          </main>

          <div class="print-signatures-block" aria-hidden="true">
            <h3 style="font-size: 11pt; font-weight: bold; margin-bottom: 4px;">ATTESTATION ET VALIDATION DU STAGE</h3>
            ${hasExclusions ? `
              <p style="font-size: 8.5pt; font-style: italic; margin-bottom: 6px; color: #333;">
                Fiche de stage adaptée au milieu de travail par l'enseignant (${activeData.totalTasks} tâches et compétences retenues).
              </p>
            ` : ''}
            <p style="font-size: 9pt; margin-bottom: 20px;">
              Les signataires certifient que les tâches cochées ont été observées et évaluées en milieu de stage selon les exigences du Répertoire ministériel des métiers semi-spécialisés.
            </p>
            <div class="signatures-grid">
              <div class="sig-col">
                <p style="margin-bottom: 45px; font-weight: bold;">Signature de l'élève :</p>
                <div class="sig-line">Date et signature</div>
              </div>
              <div class="sig-col">
                <p style="margin-bottom: 45px; font-weight: bold;">Superviseur en entreprise :</p>
                <div class="sig-line">Date et signature</div>
              </div>
              <div class="sig-col">
                <p style="margin-bottom: 45px; font-weight: bold;">Enseignant(e) PFAE / FMS :</p>
                <div class="sig-line">Date et signature</div>
              </div>
            </div>
          </div>
        </div>
      `;

      this._bindEvents();
    }

    _escapeHtml(str) {
      if (!str) return '';
      return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    _bindEvents() {
      // 1. Onglets
      const tabFicheBtn = this.querySelector('#tabFicheBtn');
      const tabGrilleBtn = this.querySelector('#tabGrilleBtn');

      if (tabFicheBtn) {
        tabFicheBtn.addEventListener('click', () => {
          this._activeTab = 'fiche';
          this.render();
        });
      }

      if (tabGrilleBtn) {
        tabGrilleBtn.addEventListener('click', () => {
          this._activeTab = 'grille';
          this.render();
        });
      }

      // 2. Bascule du mode adaptation / personnalisation
      const toggleCustomizeBtn = this.querySelector('#toggleCustomizeBtn');
      if (toggleCustomizeBtn) {
        toggleCustomizeBtn.addEventListener('click', () => {
          this._isCustomizing = !this._isCustomizing;
          this.render();
        });
      }

      const finishCustomizeBtn = this.querySelector('#finishCustomizeBtn');
      if (finishCustomizeBtn) {
        finishCustomizeBtn.addEventListener('click', () => {
          this._isCustomizing = false;
          this.render();
        });
      }

      // 3. Bascule du volet des éléments exclus
      const toggleDrawerBtn = this.querySelector('#toggleExcludedDrawerBtn');
      if (toggleDrawerBtn) {
        toggleDrawerBtn.addEventListener('click', () => {
          this._showExcludedDrawer = !this._showExcludedDrawer;
          this.render();
        });
      }

      const closeDrawerBtn = this.querySelector('#closeDrawerBtn');
      if (closeDrawerBtn) {
        closeDrawerBtn.addEventListener('click', () => {
          this._showExcludedDrawer = false;
          this.render();
        });
      }

      // 4. Rétablissement complet du programme officiel
      const resetExclusionsBtn = this.querySelector('#resetExclusionsBtn');
      if (resetExclusionsBtn) {
        resetExclusionsBtn.addEventListener('click', () => {
          if (confirm('Voulez-vous rétablir toutes les compétences, tâches et critères officiels du programme ?')) {
            resetExclusions(this._metier.id);
            this._exclusions = { comps: [], tasks: [], criteria: [] };
            this._showExcludedDrawer = false;
            this.render();
          }
        });
      }

      // 5. Boutons de suppression de compétence
      const compExcludeBtns = this.querySelectorAll('.btn-exclude-comp');
      compExcludeBtns.forEach((btn) => {
        btn.addEventListener('click', (e) => {
          const compCode = e.currentTarget.getAttribute('data-comp-code');
          this._exclusions = excludeItem(this._metier.id, 'comps', compCode);
          this.render();
        });
      });

      // 6. Boutons de suppression de tâche
      const taskExcludeBtns = this.querySelectorAll('.btn-exclude-task');
      taskExcludeBtns.forEach((btn) => {
        btn.addEventListener('click', (e) => {
          const taskId = e.currentTarget.getAttribute('data-task-id');
          this._exclusions = excludeItem(this._metier.id, 'tasks', taskId);
          this.render();
        });
      });

      // 7. Boutons de suppression de critère
      const critExcludeBtns = this.querySelectorAll('.btn-exclude-crit');
      critExcludeBtns.forEach((btn) => {
        btn.addEventListener('click', (e) => {
          const critId = e.currentTarget.getAttribute('data-criterion-id');
          this._exclusions = excludeItem(this._metier.id, 'criteria', critId);
          this.render();
        });
      });

      // 8. Boutons de restauration unitaire
      const restoreBtns = this.querySelectorAll('.btn-restore');
      restoreBtns.forEach((btn) => {
        btn.addEventListener('click', (e) => {
          const type = e.currentTarget.getAttribute('data-type');
          const id = e.currentTarget.getAttribute('data-id');
          this._exclusions = restoreItem(this._metier.id, type, id);
          this.render();
        });
      });

      // 9. Impression
      const printBtn = this.querySelector('#printBtn');
      if (printBtn) {
        printBtn.addEventListener('click', () => {
          window.print();
        });
      }

      // 10. Réinitialisation du suivi des tâches cochées
      const openResetBtn = this.querySelector('#openResetModalBtn');
      if (openResetBtn) {
        openResetBtn.addEventListener('click', () => {
          this.dispatchEvent(new CustomEvent('request-reset', {
            bubbles: true,
            detail: { metierId: this._metier.id }
          }));
        });
      }

      // 11. Cocher / décocher les tâches
      const checkboxes = this.querySelectorAll('.task-checkbox');
      checkboxes.forEach((cb) => {
        cb.addEventListener('change', (e) => {
          const taskId = e.target.getAttribute('data-task-id');
          this._completedTaskIds = toggleTask(this._metier.id, taskId);

          const parentItem = e.target.closest('.task-item');
          if (parentItem) {
            if (e.target.checked) {
              parentItem.classList.add('completed');
            } else {
              parentItem.classList.remove('completed');
            }
          }

          const activeData = this.getActiveData();
          const progressText = this.querySelector('.progress-text');
          const progressBar = this.querySelector('.progress-bar-fill');
          if (progressText) {
            progressText.innerHTML = `Progression : <strong>${activeData.completedTasks}</strong> sur <strong>${activeData.totalTasks}</strong> tâches actives acquises (${activeData.percent}%)`;
          }
          if (progressBar) {
            progressBar.style.width = `${activeData.percent}%`;
          }
        });
      });

      // 12. Champs d'information élève / stage
      const eleveInput = this.querySelector('#eleveNomInput');
      const stageInput = this.querySelector('#milieuStageInput');
      const ensInput = this.querySelector('#enseignantNomInput');

      const updateStageInfo = () => {
        this._stageInfo = {
          eleveNom: eleveInput ? eleveInput.value.trim() : '',
          milieuStage: stageInput ? stageInput.value.trim() : '',
          enseignantNom: ensInput ? ensInput.value.trim() : ''
        };
        saveStageInfo(this._metier.id, this._stageInfo);
      };

      if (eleveInput) eleveInput.addEventListener('input', updateStageInfo);
      if (stageInput) stageInput.addEventListener('input', updateStageInfo);
      if (ensInput) ensInput.addEventListener('input', updateStageInfo);
    }
  }

  if (!customElements.get('metier-detail')) {
    customElements.define('metier-detail', MetierDetail);
  }

  /* ==========================================================================
     4. ORCHESTRATEUR PRINCIPAL ET ROUTEUR (Router & App State)
     ========================================================================== */
  const state = {
    metiers: [],
    metiersMap: new Map(),
    currentRoute: { name: 'list', metierId: null },
    pendingResetMetierId: null,
    isLoading: true
  };

  function populateMap(list) {
    state.metiersMap.clear();
    list.forEach((m) => {
      state.metiersMap.set(String(m.id), m);
    });
  }

  async function loadData() {
    if (Array.isArray(window.METIERS_DATA) && window.METIERS_DATA.length > 0) {
      state.metiers = window.METIERS_DATA;
      populateMap(state.metiers);
      state.isLoading = false;
      return;
    }

    const paths = ['./data/metiers_data.json', './metiers_data.json'];
    for (const path of paths) {
      try {
        const res = await fetch(path);
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            state.metiers = data;
            populateMap(data);
            state.isLoading = false;
            return;
          }
        }
      } catch (err) {
        // En file:///, fetch échoue silencieusement
      }
    }

    throw new Error('Impossible de charger les données des métiers semi-spécialisés.');
  }

  function parseHash() {
    const hash = window.location.hash || '#/';
    if (hash.startsWith('#/metier/')) {
      const id = hash.replace('#/metier/', '').split('/')[0].trim();
      if (id) {
        return { name: 'detail', metierId: id };
      }
    }
    return { name: 'list', metierId: null };
  }

  function renderRoute() {
    const appContainer = document.getElementById('appContent');
    if (!appContainer) return;

    const route = parseHash();
    state.currentRoute = route;

    if (route.name === 'detail') {
      const metier = state.metiersMap.get(route.metierId);
      if (!metier) {
        window.location.hash = '#/';
        return;
      }

      appContainer.innerHTML = `<metier-detail></metier-detail>`;
      const detailEl = appContainer.querySelector('metier-detail');
      if (detailEl) {
        detailEl.metier = metier;
      }
      document.title = `${metier.nom} — Fiche Stage FMS`;
      window.scrollTo({ top: 0, behavior: 'auto' });
    } else {
      appContainer.innerHTML = `<metier-list></metier-list>`;
      const listEl = appContainer.querySelector('metier-list');
      if (listEl) {
        listEl.metiers = state.metiers;
      }
      document.title = 'Répertoire des Métiers Semi-Spécialisés — Accompagnement Enseignants';
    }
  }

  function setupResetModal() {
    const dialog = document.getElementById('resetConfirmModal');
    const cancelBtn = document.getElementById('cancelResetBtn');
    const confirmBtn = document.getElementById('confirmResetBtn');

    if (!dialog || !cancelBtn || !confirmBtn) return;

    document.addEventListener('request-reset', (e) => {
      state.pendingResetMetierId = e.detail.metierId;
      if (typeof dialog.showModal === 'function') {
        dialog.showModal();
        cancelBtn.focus();
      } else {
        if (confirm('Voulez-vous réinitialiser le suivi de stage pour ce métier ?')) {
          resetStageTracking(state.pendingResetMetierId);
          const detailEl = document.querySelector('metier-detail');
          if (detailEl) detailEl.metier = state.metiersMap.get(state.pendingResetMetierId);
        }
      }
    });

    cancelBtn.addEventListener('click', () => {
      state.pendingResetMetierId = null;
      dialog.close();
    });

    confirmBtn.addEventListener('click', () => {
      if (state.pendingResetMetierId) {
        resetStageTracking(state.pendingResetMetierId);
        dialog.close();

        const detailEl = document.querySelector('metier-detail');
        if (detailEl && state.currentRoute.metierId === state.pendingResetMetierId) {
          detailEl.metier = state.metiersMap.get(state.pendingResetMetierId);
        }
        state.pendingResetMetierId = null;
      }
    });

    dialog.addEventListener('click', (e) => {
      const rect = dialog.getBoundingClientRect();
      const isInDialog = (
        rect.top <= e.clientY &&
        e.clientY <= rect.top + rect.height &&
        rect.left <= e.clientX &&
        e.clientX <= rect.left + rect.width
      );
      if (!isInDialog) dialog.close();
    });
  }

  function setupKeyboardNavigation() {
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && state.currentRoute.name === 'detail') {
        const dialog = document.getElementById('resetConfirmModal');
        if (dialog && dialog.open) return;
        window.location.hash = '#/';
      }
    });
  }

  async function init() {
    const loadingEl = document.getElementById('appLoading');

    try {
      await loadData();
      if (loadingEl) {
        loadingEl.style.display = 'none';
      }
      setupResetModal();
      setupKeyboardNavigation();

      window.addEventListener('hashchange', renderRoute);
      window.addEventListener('popstate', renderRoute);
      renderRoute();
    } catch (err) {
      console.error('Erreur au chargement de l’application :', err);
      if (loadingEl) {
        loadingEl.innerHTML = `
          <div style="padding: 24px; text-align: center; color: var(--qc-danger);">
            <p style="font-weight: 700; font-size: 1.1rem;">Erreur de chargement des données</p>
            <p style="margin-top: 8px; color: var(--qc-texte-discret);">Veuillez vérifier vos fichiers ou recharger la page.</p>
          </div>
        `;
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
