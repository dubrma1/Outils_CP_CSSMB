/**
 * MetierList.js — Composant Web <metier-list>
 * Recherche instantanée, filtrage par secteur, filtres d'admission et focus Montréal.
 */
import { ICONS } from './Icons.js';
import './MetierCard.js';

export class MetierList extends HTMLElement {
  constructor() {
    super();
    this._metiers = [];
    this._searchTerm = '';
    this._selectedSecteur = 'ALL';
    this._selectedCondition = 'ALL';
    this._onlyMontreal = true; // Actif par défaut selon la demande utilisateur
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
      // 1. Filtre Montréal
      if (this._onlyMontreal && !m.top_montreal) {
        return false;
      }

      // 2. Filtre Secteur
      if (this._selectedSecteur !== 'ALL' && m.secteur_code !== this._selectedSecteur) {
        return false;
      }

      // 3. Filtre Conditions particulières
      if (this._selectedCondition === 'NO_PERMIT' && m.requires_license) {
        return false;
      }
      if (this._selectedCondition === 'UNDER_16' && m.requires_16plus) {
        return false;
      }
      if (this._selectedCondition === 'NO_RECORD_CHECK' && m.requires_background_check) {
        return false;
      }

      // 4. Recherche textuelle
      if (this._searchTerm.trim() !== '') {
        const q = this._searchTerm.toLowerCase().trim();
        const matchesName = m.nom.toLowerCase().includes(q);
        const matchesCodeFGJ = (m.code_fgj || '').toLowerCase().includes(q);
        const matchesCodeFGA = (m.code_fga || '').toLowerCase().includes(q);
        const matchesSecteur = (m.secteur || '').toLowerCase().includes(q);
        const matchesAppellations = (m.autres_appellations || '').toLowerCase().includes(q);
        const matchesChamp = (m.champ_application || '').toLowerCase().includes(q);

        if (!matchesName && !matchesCodeFGJ && !matchesCodeFGA && !matchesSecteur && !matchesAppellations && !matchesChamp) {
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
        <!-- Ligne 1 : Barre de recherche et Bascule Montréal -->
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

        <!-- Ligne 2 : Sélecteur de secteur et conditions d'admission -->
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

        <!-- Ligne 3 : Indicateur des résultats -->
        <div class="results-info-bar" role="status" aria-live="polite">
          <div>
            Affichage de <span class="results-count">${filteredCount}</span> sur ${totalCount} métiers
            ${this._onlyMontreal ? ' (Sélection prioritaire Montréal)' : ' (Tous les métiers urbains)'}
          </div>
          ${(this._searchTerm || this._selectedSecteur !== 'ALL' || this._selectedCondition !== 'ALL') ? `
            <div>
              <span class="badge-tag">Filtres appliqués</span>
            </div>
          ` : ''}
        </div>
      </section>

      <!-- Grille des métiers -->
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

    // Attacher les données aux sous-composants <metier-card>
    const cardEls = this.querySelectorAll('metier-card');
    cardEls.forEach((el) => {
      const id = el.getAttribute('data-id');
      const data = filtered.find((m) => m.id === id);
      if (data) {
        el.metier = data;
      }
    });

    this._bindEvents();
  }

  _escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  _bindEvents() {
    // 1. Recherche avec input immédiat
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

    // Effacer la recherche
    const clearBtn = this.querySelector('#clearSearchBtn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        this._searchTerm = '';
        this.render();
      });
    }

    // 2. Bascule Montréal
    const mtlBtn = this.querySelector('#toggleMtlBtn');
    if (mtlBtn) {
      mtlBtn.addEventListener('click', () => {
        this._onlyMontreal = !this._onlyMontreal;
        this.render();
      });
    }

    // 3. Sélecteur Secteur
    const secSelect = this.querySelector('#secteurSelect');
    if (secSelect) {
      secSelect.addEventListener('change', (e) => {
        this._selectedSecteur = e.target.value;
        this.render();
      });
    }

    // 4. Sélecteur Conditions
    const condSelect = this.querySelector('#conditionSelect');
    if (condSelect) {
      condSelect.addEventListener('change', (e) => {
        this._selectedCondition = e.target.value;
        this.render();
      });
    }

    // 5. Réinitialisation
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

customElements.define('metier-list', MetierList);
