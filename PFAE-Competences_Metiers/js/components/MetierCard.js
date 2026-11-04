/**
 * MetierCard.js — Composant Web <metier-card>
 * Présentation sobre, épurée et accessible d'une fiche métier pour enseignants.
 */
import { ICONS } from './Icons.js';

export class MetierCard extends HTMLElement {
  constructor() {
    super();
    this._data = null;
  }

  set metier(data) {
    this._data = data;
    this.render();
  }

  connectedCallback() {
    if (this._data) {
      this.render();
    }
  }

  render() {
    if (!this._data) return;
    const m = this._data;

    // Badges de statut
    const isTopMtl = m.top_montreal;
    const reqPermis = m.requires_license;
    const req16 = m.requires_16plus;
    const reqAnt = m.requires_background_check;

    this.innerHTML = `
      <article class="metier-card" tabindex="0" role="region" aria-label="${m.nom}">
        <div class="card-top">
          <div class="card-tags">
            <span class="tag-secteur">Secteur ${m.secteur_code} — ${m.secteur}</span>
            ${isTopMtl ? `<span class="tag-montreal">Priorité Montréal</span>` : ''}
            ${reqPermis ? `<span class="tag-restriction">Permis classe 5</span>` : ''}
            ${req16 ? `<span class="tag-restriction">16 ans minimum</span>` : ''}
            ${reqAnt ? `<span class="tag-restriction">Vérification antécédents</span>` : ''}
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

    // Accessibilité clavier: Enter ou Espace sur la carte navigue
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

customElements.define('metier-card', MetierCard);
