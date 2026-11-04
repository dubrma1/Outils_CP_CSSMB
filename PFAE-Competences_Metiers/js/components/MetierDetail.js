/**
 * MetierDetail.js — Composant Web <metier-detail>
 * Fiche métier complète et grille d'évaluation de stage pour les enseignants.
 * Conforme WCAG AA, responsive, mode impression officiel, sans framework.
 */
import { ICONS } from './Icons.js';
import { 
  loadProgress, 
  toggleTask, 
  loadStageInfo, 
  saveStageInfo,
  loadSelectedCompetencies,
  toggleCompetencySelection
} from '../storage.js';

export class MetierDetail extends HTMLElement {
  constructor() {
    super();
    this._metier = null;
    this._activeTab = 'fiche'; // 'fiche' (consultation) ou 'grille' (suivi interactif)
    this._completedTaskIds = [];
    this._stageInfo = { eleveNom: '', milieuStage: '', enseignantNom: '', dateDebut: '' };
    this._selectedComps = null;
  }

  set metier(data) {
    this._metier = data;
    if (data) {
      this._completedTaskIds = loadProgress(data.id);
      this._stageInfo = loadStageInfo(data.id);
      this._selectedComps = loadSelectedCompetencies(data.id);
    }
    this.render();
  }

  connectedCallback() {
    if (this._metier) {
      this.render();
    }
  }

  /**
   * Calcule le total des tâches actives et des tâches acquises
   */
  getTaskMetrics() {
    if (!this._metier || !this._metier.competences) return { total: 0, completed: 0, percent: 0 };
    
    let total = 0;
    this._metier.competences.forEach((comp) => {
      // Si un filtrage des compétences au plan existe, vérifier si active
      if (this._selectedComps && !this._selectedComps.includes(String(comp.code))) {
        return;
      }
      total += (comp.taches || []).length;
    });

    const completed = this._completedTaskIds.length;
    const percent = total > 0 ? Math.min(100, Math.round((completed / total) * 100)) : 0;
    return { total, completed, percent };
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
    const metrics = this.getTaskMetrics();
    const isGrille = this._activeTab === 'grille';

    this.innerHTML = `
      <div class="detail-view">
        <!-- Barre de navigation supérieure -->
        <nav class="detail-nav-bar" aria-label="Navigation de la fiche">
          <a href="#/" class="btn-back" aria-label="Retourner à la liste des métiers">
            ${ICONS.arrowLeft} <span>Retour au répertoire des métiers</span>
          </a>

          <div class="header-badges">
            <span class="badge-tag montreal">Secteur ${m.secteur_code} — ${m.secteur}</span>
            ${m.top_montreal ? `<span class="tag-montreal">Priorité Montréal</span>` : ''}
          </div>
        </nav>

        <!-- En-tête officiel du métier -->
        <header class="detail-header-card">
          <div class="detail-header-tags">
            <span class="tag-secteur">Secteur ${m.secteur_code}</span>
            <span class="card-code-item">Code FGJ: <strong>${m.code_fgj}</strong></span>
            ${m.code_fga ? `<span class="card-code-item">Code FGA: <strong>${m.code_fga}</strong></span>` : ''}
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

          <!-- Conditions d'admission au stage (Alerte réglementaire) -->
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
            <button type="button" id="printBtn" class="btn btn-secondary" aria-label="Imprimer la fiche de stage ou sauvegarder en PDF">
              ${ICONS.print} <span>Imprimer la fiche</span>
            </button>
            ${isGrille ? `
              <button type="button" id="openResetModalBtn" class="btn btn-danger" aria-label="Réinitialiser les tâches cochées pour ce stage">
                ${ICONS.refresh} <span>Réinitialiser</span>
              </button>
            ` : ''}
          </div>
        </section>

        <!-- Formulaire de stage et progression (Visible en mode Grille) -->
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

          <!-- Barre de progression des tâches -->
          <section class="progress-status-bar" aria-label="Progression des tâches acquises">
            <div class="progress-text">
              Progression : <strong>${metrics.completed}</strong> sur <strong>${metrics.total}</strong> tâches acquises (${metrics.percent}%)
            </div>
            <div class="progress-bar-track" aria-hidden="true">
              <div class="progress-bar-fill" style="width: ${metrics.percent}%;"></div>
            </div>
          </section>
        ` : ''}

        <!-- Liste des Compétences du métier -->
        <main class="competences-container" aria-label="Compétences ministérielles du métier">
          ${(m.competences || []).map((comp) => {
            const isOpt = comp.optionnelle;
            const isSpec = comp.type === 'specifique';
            const compCodeStr = String(comp.code);
            const isCompIncluded = !this._selectedComps || this._selectedComps.includes(compCodeStr);

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
                  </div>
                </header>

                <div class="comp-body">
                  <!-- Colonne 1 : Tâches associées -->
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
                              <div style="display: flex; gap: 10px; align-items: flex-start; padding: 4px 0;">
                                <span style="font-size: 0.82rem; font-weight: 700; color: var(--qc-texte-discret); min-width: 22px;">
                                  ${t.ordre_comp || t.ordre}.
                                </span>
                                <span class="task-text">
                                  ${t.texte}
                                  ${t.optionnelle ? `<span class="task-opt-tag">(optionnelle)</span>` : ''}
                                </span>
                              </div>
                            `}
                          </div>
                        `;
                      }).join('')}
                    </div>
                  </div>

                  <!-- Colonne 2 : Critères d'évaluation de la performance -->
                  <div class="comp-criteria-column">
                    <div class="comp-subcol-title">
                      <span>Critères d'évaluation officiels (${(comp.criteres || []).length})</span>
                    </div>

                    ${(comp.criteres || []).length > 0 ? `
                      <div class="criteria-items-list" role="list">
                        ${comp.criteres.map((c) => `
                          <div class="criterion-item" role="listitem">
                            <span class="criterion-num">${c.ordre}.</span>
                            <span class="criterion-text">${c.texte}</span>
                          </div>
                        `).join('')}
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

        <!-- Bloc officiel de signature d'évaluation pour l'impression -->
        <div class="print-signatures-block" aria-hidden="true">
          <h3 style="font-size: 11pt; font-weight: bold; margin-bottom: 6px;">ATTESTATION ET VALIDATION DU STAGE</h3>
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
    // 1. Bascule d'onglets (Fiche vs Grille)
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

    // 2. Impression
    const printBtn = this.querySelector('#printBtn');
    if (printBtn) {
      printBtn.addEventListener('click', () => {
        window.print();
      });
    }

    // 3. Réinitialisation avec dialogue modal
    const openResetBtn = this.querySelector('#openResetModalBtn');
    if (openResetBtn) {
      openResetBtn.addEventListener('click', () => {
        const dialog = document.getElementById('resetConfirmModal');
        if (dialog && typeof dialog.showModal === 'function') {
          // Déclencher un événement personnalisé vers l'application principale
          this.dispatchEvent(new CustomEvent('request-reset', {
            bubbles: true,
            detail: { metierId: this._metier.id }
          }));
        }
      });
    }

    // 4. Cases à cocher des tâches (Mode Grille)
    const checkboxes = this.querySelectorAll('.task-checkbox');
    checkboxes.forEach((cb) => {
      cb.addEventListener('change', (e) => {
        const taskId = e.target.getAttribute('data-task-id');
        this._completedTaskIds = toggleTask(this._metier.id, taskId);
        
        // Mise à jour visuelle immédiate de l'élément sans re-render complet pour la fluidité
        const parentItem = e.target.closest('.task-item');
        if (parentItem) {
          if (e.target.checked) {
            parentItem.classList.add('completed');
          } else {
            parentItem.classList.remove('completed');
          }
        }

        // Mettre à jour la barre de progression
        const metrics = this.getTaskMetrics();
        const progressText = this.querySelector('.progress-text');
        const progressBar = this.querySelector('.progress-bar-fill');
        if (progressText) {
          progressText.innerHTML = `Progression : <strong>${metrics.completed}</strong> sur <strong>${metrics.total}</strong> tâches acquises (${metrics.percent}%)`;
        }
        if (progressBar) {
          progressBar.style.width = `${metrics.percent}%`;
        }
      });
    });

    // 5. Champs d'information élève / stage (sauvegarde automatique en local)
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

customElements.define('metier-detail', MetierDetail);
