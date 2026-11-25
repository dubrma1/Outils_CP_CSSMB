/**
 * Catalogue interactif des conceptions erronées en sciences (BSCS / AAAS — PFEQ)
 * 100 % hors ligne (file://), bilingue FR (Québec) / EN, import/export CSV.
 */
(() => {
  'use strict';

  const PAGE_SIZE = 24;

  const DOMAIN_META = {
    'Earth Science': { cls: 'earth', fr: 'Terre et espace', en: 'Earth Science' },
    'Life Science': { cls: 'life', fr: 'Univers vivant', en: 'Life Science' },
    'Physical Science': { cls: 'phys', fr: 'Univers matériel', en: 'Physical Science' },
    'Nature of Science': { cls: 'nos', fr: 'Nature des sciences', en: 'Nature of Science' }
  };

  const UI_STRINGS = {
    fr: {
      appTitle: 'Catalogue des conceptions erronées en sciences',
      appSubtitle: 'Base AAAS Project 2061 / BSCS adaptée aux écoles du Québec (PFEQ)',
      searchPlaceholder: 'Rechercher une conception, une idée scientifique, un thème ou un code (ex. tectonique, cellules, PTM011, masse, énergie)...',
      allDomains: 'Tous les univers',
      allTopics: 'Tous les thèmes',
      allSubtopics: 'Toutes les idées scientifiques',
      filterTopic: 'Thème',
      filterSubtopic: 'Idée scientifique / Sous-thème',
      filterPrevalence: 'Prévalence minimale',
      filterGradeBasis: 'Niveau de référence',
      filterItems: 'Items d\'évaluation liés',
      filterSort: 'Trier par',
      exportCsv: 'Exporter CSV',
      importCsv: 'Importer CSV',
      viewCards: 'Cartes',
      viewTable: 'Tableau',
      misconceptionLabel: 'Conception erronée (élève)',
      scientificLabel: 'Idée scientifique visée (PFEQ)',
      g68Label: '6e année – 2e sec.',
      g912Label: '3e – 5e sec. / Cégep',
      detailsBtn: 'Détails',
      copyBtn: 'Copier POE',
      copiedMsg: 'Fiche copiée dans le presse-papiers !',
      noResultsTitle: 'Aucune conception ne correspond à vos critères',
      noResultsHint: 'Essayez un mot-clé plus général ou réinitialisez les filtres.',
      statTotal: 'Conceptions affichées',
      statAvg68: 'Prévalence moy. (6e–2e sec.)',
      statAvg912: 'Prévalence moy. (3e–5e sec.)',
      statHigh: 'Très fréquentes (≥ 40 %)',
      itemsUnit: 'item(s) lié(s)',
      resetFilters: 'Réinitialiser les filtres',
      noPrevalence: 'Données de prévalence non disponibles'
    },
    en: {
      appTitle: 'Science Misconceptions Catalog',
      appSubtitle: 'AAAS Project 2061 / BSCS Science Assessment Database',
      searchPlaceholder: 'Search a misconception, scientific idea, topic, or code (e.g. photosynthesis, plate tectonics, PTM011)...',
      allDomains: 'All domains',
      allTopics: 'All topics',
      allSubtopics: 'All scientific ideas',
      filterTopic: 'Topic',
      filterSubtopic: 'Scientific Idea / Subtopic',
      filterPrevalence: 'Minimum prevalence',
      filterGradeBasis: 'Grade band basis',
      filterItems: 'Linked assessment items',
      filterSort: 'Sort by',
      exportCsv: 'Export CSV',
      importCsv: 'Import CSV',
      viewCards: 'Cards',
      viewTable: 'Table',
      misconceptionLabel: 'Student Misconception',
      scientificLabel: 'Target Scientific Idea',
      g68Label: 'Grades 6–8',
      g912Label: 'Grades 9–12',
      detailsBtn: 'Details',
      copyBtn: 'Copy POE',
      copiedMsg: 'Copied to clipboard!',
      noResultsTitle: 'No misconceptions match your criteria',
      noResultsHint: 'Try broader keywords or reset active filters.',
      statTotal: 'Matching misconceptions',
      statAvg68: 'Avg. prevalence (Grades 6–8)',
      statAvg912: 'Avg. prevalence (Grades 9–12)',
      statHigh: 'High prevalence (≥ 40%)',
      itemsUnit: 'linked item(s)',
      resetFilters: 'Reset filters',
      noPrevalence: 'Prevalence data unavailable'
    }
  };

  /** @type {AbortController} */
  const controller = new AbortController();
  const { signal } = controller;

  const state = {
    records: [],
    filtered: [],
    lang: 'fr', // 'fr' | 'bi' | 'en'
    view: 'cards', // 'cards' | 'table'
    query: '',
    domain: '',
    topic: '',
    subtopic: '',
    minPrevalence: 0,
    gradeBasis: 'max', // 'max' | 'g68' | 'g912'
    itemsOnly: 'all', // 'all' | 'with' | 'without'
    sort: 'code',
    page: 1,
    activeDetailCode: null,
    sourceLabel: 'Catalogue intégré (FR/EN)'
  };

  const els = {
    searchInput: document.getElementById('searchInput'),
    clearSearchBtn: document.getElementById('clearSearchBtn'),
    domainPills: document.getElementById('domainPills'),
    topicFilter: document.getElementById('topicFilter'),
    subtopicFilter: document.getElementById('subtopicFilter'),
    prevalenceFilter: document.getElementById('prevalenceFilter'),
    gradeBasisFilter: document.getElementById('gradeBasisFilter'),
    itemsFilter: document.getElementById('itemsFilter'),
    sortFilter: document.getElementById('sortFilter'),
    resultCount: document.getElementById('resultCount'),
    sourceBadge: document.getElementById('sourceBadge'),
    resetFiltersBtn: document.getElementById('resetFiltersBtn'),
    statsStrip: document.getElementById('statsStrip'),
    resultsContainer: document.getElementById('resultsContainer'),
    paginationBar: document.getElementById('paginationBar'),
    detailModal: document.getElementById('detailModal'),
    detailCodeBadge: document.getElementById('detailCodeBadge'),
    detailDomainBadge: document.getElementById('detailDomainBadge'),
    detailTitle: document.getElementById('detailTitle'),
    detailBody: document.getElementById('detailBody'),
    detailSourceLink: document.getElementById('detailSourceLink'),
    infoModal: document.getElementById('infoModal'),
    csvFileInput: document.getElementById('csvFileInput'),
    toast: document.getElementById('toast')
  };

  /** Normalise une chaîne pour une recherche insensible aux accents et à la casse. */
  function normalizeText(str) {
    return (str || '')
      .toString()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();
  }

  function escapeHtml(str) {
    return (str || '')
      .toString()
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /** Extrait les pourcentages Grades 6-8 et Grades 9-12 d'une chaîne grade_bands (FR ou EN). */
  function parsePrevalence(raw) {
    const s = (raw || '').toString();
    let g68 = null;
    let g912 = null;

    const m68 = s.match(/(?:Grades?\s*6\s*[-–]\s*8|6e\s*ann[eé]e\s*[-–]\s*2e\s*sec\.?)\s*:\s*(\d+(?:[.,]\d+)?)\s*%/i);
    if (m68) g68 = parseFloat(m68[1].replace(',', '.'));

    const m912 = s.match(/(?:Grades?\s*9\s*[-–]\s*12|3e\s*[-–]\s*5e\s*sec\.?(?:\s*\/\s*C[eé]gep)?)\s*:\s*(\d+(?:[.,]\d+)?)\s*%/i);
    if (m912) g912 = parseFloat(m912[1].replace(',', '.'));

    return { g68, g912 };
  }

  /** Déduit la clé de domaine canonique (EN) depuis un domaine FR ou EN. */
  function canonicalDomain(val) {
    const n = normalizeText(val).trim();
    if (n.includes('earth') || n.includes('terre')) return 'Earth Science';
    if (n.includes('life') || n.includes('vivant')) return 'Life Science';
    if (n.includes('physical') || n.includes('materiel')) return 'Physical Science';
    if (n.includes('nature')) return 'Nature of Science';
    return val || 'Nature of Science';
  }

  /** Prépare l'index de recherche d'un enregistrement bilingue ou importé. */
  function hydrateRecord(raw) {
    const domKey = canonicalDomain(raw.domain_en || raw.domain);
    const prev = {
      g68: typeof raw.g68 === 'number' ? raw.g68 : parsePrevalence(raw.grade_bands_en || raw.grade_bands).g68,
      g912: typeof raw.g912 === 'number' ? raw.g912 : parsePrevalence(raw.grade_bands_en || raw.grade_bands).g912
    };

    const rec = {
      code: (raw.code || raw.misconception_code || '').trim(),
      domainKey: domKey,
      domainFr: raw.domain_fr || (DOMAIN_META[domKey] ? DOMAIN_META[domKey].fr : raw.domain),
      domainEn: raw.domain_en || (DOMAIN_META[domKey] ? DOMAIN_META[domKey].en : raw.domain),
      topicFr: raw.topic_fr || raw.topic || '',
      topicEn: raw.topic_en || raw.topic || '',
      subtopicFr: raw.subtopic_fr || raw.subtopic || '',
      subtopicEn: raw.subtopic_en || raw.subtopic || '',
      misconceptionFr: raw.misconception_fr || raw.misconception_text || '',
      misconceptionEn: raw.misconception_en || raw.misconception_text || '',
      scientificFr: raw.scientific_fr || raw.scientific_idea || '',
      scientificEn: raw.scientific_en || raw.scientific_idea || '',
      gradeBandsFr: raw.grade_bands_fr || raw.grade_bands || '',
      gradeBandsEn: raw.grade_bands_en || raw.grade_bands || '',
      g68: prev.g68,
      g912: prev.g912,
      linkedCount: Number.parseInt(raw.linked_items_count ?? raw.linkedCount ?? 0, 10) || 0,
      linkedIds: (raw.linked_item_ids ?? raw.linkedIds ?? '').toString().trim(),
      sourceUrl: (raw.source_url ?? raw.sourceUrl ?? '').toString().trim()
    };

    rec._search = normalizeText([
      rec.code,
      rec.domainFr, rec.domainEn,
      rec.topicFr, rec.topicEn,
      rec.subtopicFr, rec.subtopicEn,
      rec.misconceptionFr, rec.misconceptionEn,
      rec.scientificFr, rec.scientificEn,
      rec.linkedIds
    ].join(' '));

    return rec;
  }

  function getT() {
    return state.lang === 'en' ? UI_STRINGS.en : UI_STRINGS.fr;
  }

  function getDomainLabel(rec) {
    return state.lang === 'en' ? rec.domainEn : rec.domainFr;
  }

  function getTopicLabel(rec) {
    return state.lang === 'en' ? rec.topicEn : rec.topicFr;
  }

  function getSubtopicLabel(rec) {
    return state.lang === 'en' ? rec.subtopicEn : rec.subtopicFr;
  }

  function getPrevalenceValue(rec, basis) {
    if (basis === 'g68') return rec.g68;
    if (basis === 'g912') return rec.g912;
    if (rec.g68 === null && rec.g912 === null) return null;
    if (rec.g68 === null) return rec.g912;
    if (rec.g912 === null) return rec.g68;
    return Math.max(rec.g68, rec.g912);
  }

  function formatPct(val) {
    if (val === null || Number.isNaN(val)) return '—';
    const str = Number.isInteger(val) ? String(val) : val.toFixed(1);
    return state.lang === 'en' ? `${str}%` : `${str.replace('.', ',')}\u00a0%`;
  }

  /** Surligne les termes recherchés (insensible aux accents) dans un texte HTML-échappé. */
  function highlightText(text, queryTokens) {
    const safe = escapeHtml(text);
    if (!queryTokens.length) return safe;

    // Recherche simple sur les occurrences normalisées
    const normSrc = normalizeText(text);
    const marks = [];
    for (const token of queryTokens) {
      if (token.length < 2) continue;
      let idx = normSrc.indexOf(token);
      while (idx !== -1) {
        marks.push([idx, idx + token.length]);
        idx = normSrc.indexOf(token, idx + token.length);
      }
    }
    if (!marks.length) return safe;

    // Fusion des intervalles qui se chevauchent (attention aux caractères combinés: on reconstruit sur texte brut)
    // Pour éviter tout décalage NFD sur les caractères accentués, on mappe chaque index NFD sans diacritiques vers l'index original.
    const indexMap = [];
    for (let i = 0; i < text.length; i++) {
      const normChar = text[i].normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      for (let k = 0; k < normChar.length; k++) {
        indexMap.push(i);
      }
    }
    const origRanges = marks
      .map(([s, e]) => [indexMap[s], (indexMap[e - 1] ?? text.length - 1) + 1])
      .filter(([s, e]) => s !== undefined && e > s)
      .sort((a, b) => a[0] - b[0]);

    const merged = [];
    for (const r of origRanges) {
      if (!merged.length || r[0] > merged[merged.length - 1][1]) {
        merged.push(r);
      } else {
        merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], r[1]);
      }
    }

    let out = '';
    let cursor = 0;
    for (const [s, e] of merged) {
      out += escapeHtml(text.slice(cursor, s));
      out += `<mark class="hl">${escapeHtml(text.slice(s, e))}</mark>`;
      cursor = e;
    }
    out += escapeHtml(text.slice(cursor));
    return out;
  }

  function getQueryTokens() {
    return normalizeText(state.query)
      .split(/\s+/)
      .filter(Boolean);
  }

  /** Applique tous les filtres et le tri. */
  function applyFilters() {
    const tokens = getQueryTokens();
    const minPrev = state.minPrevalence;
    const basis = state.gradeBasis;

    const filtered = state.records.filter((rec) => {
      if (state.domain && rec.domainKey !== state.domain) return false;
      if (state.topic && rec.topicEn !== state.topic) return false;
      if (state.subtopic && rec.subtopicEn !== state.subtopic) return false;

      if (state.itemsOnly === 'with' && rec.linkedCount <= 0) return false;
      if (state.itemsOnly === 'without' && rec.linkedCount > 0) return false;

      if (minPrev > 0) {
        const pv = getPrevalenceValue(rec, basis);
        if (pv === null || pv < minPrev) return false;
      }

      if (tokens.length) {
        for (const t of tokens) {
          if (!rec._search.includes(t)) return false;
        }
      }
      return true;
    });

    filtered.sort((a, b) => {
      if (state.sort === 'prev-desc') {
        const va = getPrevalenceValue(a, basis) ?? -1;
        const vb = getPrevalenceValue(b, basis) ?? -1;
        return vb - va || a.code.localeCompare(b.code);
      }
      if (state.sort === 'prev-asc') {
        const va = getPrevalenceValue(a, basis) ?? 999;
        const vb = getPrevalenceValue(b, basis) ?? 999;
        return va - vb || a.code.localeCompare(b.code);
      }
      if (state.sort === 'items-desc') {
        return b.linkedCount - a.linkedCount || a.code.localeCompare(b.code);
      }
      if (state.sort === 'topic') {
        return getTopicLabel(a).localeCompare(getTopicLabel(b), 'fr') || a.code.localeCompare(b.code);
      }
      return a.code.localeCompare(b.code);
    });

    state.filtered = filtered;
    const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    if (state.page > totalPages) state.page = 1;
  }

  /** Met à jour les menus déroulants Thème et Sous-thème en cascade. */
  function renderFilterOptions() {
    const t = getT();

    // Thèmes disponibles pour le domaine sélectionné
    const topicMap = new Map();
    for (const rec of state.records) {
      if (state.domain && rec.domainKey !== state.domain) continue;
      if (!topicMap.has(rec.topicEn)) {
        topicMap.set(rec.topicEn, { en: rec.topicEn, label: getTopicLabel(rec), count: 0 });
      }
      topicMap.get(rec.topicEn).count++;
    }

    const sortedTopics = [...topicMap.values()].sort((a, b) => a.label.localeCompare(b.label, 'fr'));
    if (state.topic && !topicMap.has(state.topic)) state.topic = '';

    els.topicFilter.innerHTML = `<option value="">${escapeHtml(t.allTopics)} (${sortedTopics.length})</option>` +
      sortedTopics.map((item) =>
        `<option value="${escapeHtml(item.en)}"${state.topic === item.en ? ' selected' : ''}>${escapeHtml(item.label)} (${item.count})</option>`
      ).join('');

    // Sous-thèmes disponibles pour domaine + thème
    const subMap = new Map();
    for (const rec of state.records) {
      if (state.domain && rec.domainKey !== state.domain) continue;
      if (state.topic && rec.topicEn !== state.topic) continue;
      if (!subMap.has(rec.subtopicEn)) {
        subMap.set(rec.subtopicEn, { en: rec.subtopicEn, label: getSubtopicLabel(rec), count: 0 });
      }
      subMap.get(rec.subtopicEn).count++;
    }

    const sortedSubs = [...subMap.values()].sort((a, b) => a.label.localeCompare(b.label, 'fr'));
    if (state.subtopic && !subMap.has(state.subtopic)) state.subtopic = '';

    els.subtopicFilter.innerHTML = `<option value="">${escapeHtml(t.allSubtopics)} (${sortedSubs.length})</option>` +
      sortedSubs.map((item) => {
        const shortLabel = item.label.length > 96 ? `${item.label.slice(0, 93)}…` : item.label;
        return `<option value="${escapeHtml(item.en)}"${state.subtopic === item.en ? ' selected' : ''}>${escapeHtml(shortLabel)} (${item.count})</option>`;
      }).join('');
  }

  function renderDomainPills() {
    const t = getT();
    const counts = { '': state.records.length };
    for (const key of Object.keys(DOMAIN_META)) counts[key] = 0;
    for (const rec of state.records) {
      counts[rec.domainKey] = (counts[rec.domainKey] || 0) + 1;
    }

    const order = ['', 'Earth Science', 'Life Science', 'Physical Science', 'Nature of Science'];
    els.domainPills.innerHTML = order
      .filter((k) => k === '' || counts[k] > 0)
      .map((key) => {
        const label = key === ''
          ? t.allDomains
          : (state.lang === 'en' ? DOMAIN_META[key].en : DOMAIN_META[key].fr);
        const active = state.domain === key;
        return `<button type="button" class="domain-pill${active ? ' is-active' : ''}" data-action="set-domain" data-domain="${escapeHtml(key)}" aria-pressed="${active}">
          <span>${escapeHtml(label)}</span>
          <span class="pill-count">${counts[key]}</span>
        </button>`;
      }).join('');
  }

  function renderStats() {
    const t = getT();
    const list = state.filtered;
    const valid68 = list.map((r) => r.g68).filter((v) => v !== null);
    const valid912 = list.map((r) => r.g912).filter((v) => v !== null);
    const avg68 = valid68.length ? valid68.reduce((a, b) => a + b, 0) / valid68.length : null;
    const avg912 = valid912.length ? valid912.reduce((a, b) => a + b, 0) / valid912.length : null;
    const highCount = list.filter((r) => (getPrevalenceValue(r, state.gradeBasis) ?? 0) >= 40).length;

    els.statsStrip.innerHTML = `
      <div class="stat-card">
        <div class="stat-label">${escapeHtml(t.statTotal)}</div>
        <div class="stat-value">${list.length} / ${state.records.length}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">${escapeHtml(t.statAvg68)}</div>
        <div class="stat-value">${formatPct(avg68)}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">${escapeHtml(t.statAvg912)}</div>
        <div class="stat-value">${formatPct(avg912)}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">${escapeHtml(t.statHigh)}</div>
        <div class="stat-value">${highCount}</div>
      </div>
    `;
  }

  function prevBarClass(val) {
    if (val >= 40) return ' prev-fill--high';
    if (val >= 25) return ' prev-fill--mid';
    return '';
  }

  function renderPrevalenceBars(rec) {
    const t = getT();
    if (rec.g68 === null && rec.g912 === null) {
      const fallback = state.lang === 'en' ? rec.gradeBandsEn : rec.gradeBandsFr;
      return `<div class="prev-label">${escapeHtml(fallback || t.noPrevalence)}</div>`;
    }

    const parts = [];
    if (rec.g68 !== null) {
      parts.push(`
        <div class="prev-item">
          <div class="prev-header">
            <span class="prev-label">${escapeHtml(t.g68Label)}</span>
            <span class="prev-pct">${formatPct(rec.g68)}</span>
          </div>
          <div class="prev-track"><div class="prev-fill${prevBarClass(rec.g68)}" style="width:${Math.min(100, rec.g68)}%"></div></div>
        </div>`);
    }
    if (rec.g912 !== null) {
      parts.push(`
        <div class="prev-item">
          <div class="prev-header">
            <span class="prev-label">${escapeHtml(t.g912Label)}</span>
            <span class="prev-pct">${formatPct(rec.g912)}</span>
          </div>
          <div class="prev-track"><div class="prev-fill${prevBarClass(rec.g912)}" style="width:${Math.min(100, rec.g912)}%"></div></div>
        </div>`);
    }
    return `<div class="prevalence-list">${parts.join('')}</div>`;
  }

  function renderResults() {
    const t = getT();
    const tokens = getQueryTokens();
    const total = state.filtered.length;

    const hasActiveFilter = Boolean(
      state.query.trim() || state.domain || state.topic || state.subtopic ||
      state.minPrevalence > 0 || state.itemsOnly !== 'all'
    );
    els.resetFiltersBtn.hidden = !hasActiveFilter;
    els.clearSearchBtn.hidden = !state.query;

    els.resultCount.textContent = state.lang === 'en'
      ? `${total} misconception${total > 1 ? 's' : ''} found`
      : `${total} conception${total > 1 ? 's' : ''} trouvée${total > 1 ? 's' : ''}`;
    els.sourceBadge.textContent = state.sourceLabel;

    if (!total) {
      els.resultsContainer.innerHTML = `
        <div class="empty-state">
          <h3>${escapeHtml(t.noResultsTitle)}</h3>
          <p>${escapeHtml(t.noResultsHint)}</p>
          <button type="button" class="btn-secondary" data-action="reset-filters">${escapeHtml(t.resetFilters)}</button>
        </div>`;
      els.paginationBar.innerHTML = '';
      return;
    }

    const start = (state.page - 1) * PAGE_SIZE;
    const pageItems = state.filtered.slice(start, start + PAGE_SIZE);

    if (state.view === 'table') {
      els.resultsContainer.innerHTML = `
        <div class="table-wrap">
          <table class="catalog-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>${state.lang === 'en' ? 'Domain / Topic' : 'Univers / Thème'}</th>
                <th>${escapeHtml(t.misconceptionLabel)}</th>
                <th>${escapeHtml(t.scientificLabel)}</th>
                <th>${escapeHtml(t.g68Label)}</th>
                <th>${escapeHtml(t.g912Label)}</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${pageItems.map((rec) => {
                const domCls = DOMAIN_META[rec.domainKey]?.cls || 'nos';
                const miscMain = state.lang === 'en' ? rec.misconceptionEn : rec.misconceptionFr;
                const sciMain = state.lang === 'en' ? rec.scientificEn : rec.scientificFr;
                const sciPreview = sciMain.length > 180 ? `${sciMain.slice(0, 177)}…` : sciMain;
                return `<tr>
                  <td><span class="code-badge">${highlightText(rec.code, tokens)}</span></td>
                  <td>
                    <span class="domain-badge domain-badge--${domCls}">${escapeHtml(getDomainLabel(rec))}</span>
                    <div style="margin-top:5px;font-weight:600;color:var(--secondary);font-size:0.82rem;">${highlightText(getTopicLabel(rec), tokens)}</div>
                  </td>
                  <td>
                    <div>${highlightText(miscMain, tokens)}</div>
                    ${state.lang === 'bi' ? `<div class="block-text-en">${highlightText(rec.misconceptionEn, tokens)}</div>` : ''}
                  </td>
                  <td>
                    <div>${highlightText(sciPreview, tokens)}</div>
                    ${state.lang === 'bi' ? `<div class="block-text-en">${highlightText(rec.scientificEn.slice(0, 180), tokens)}</div>` : ''}
                  </td>
                  <td class="num-cell">${formatPct(rec.g68)}</td>
                  <td class="num-cell">${formatPct(rec.g912)}</td>
                  <td style="white-space:nowrap;">
                    <button type="button" class="btn-card btn-card--primary" data-action="open-detail" data-code="${escapeHtml(rec.code)}">${escapeHtml(t.detailsBtn)}</button>
                  </td>
                </tr>`;
              }).join('')}
            </tbody>
          </table>
        </div>`;
    } else {
      els.resultsContainer.innerHTML = `<div class="cards-grid">${pageItems.map((rec) => {
        const domCls = DOMAIN_META[rec.domainKey]?.cls || 'nos';
        const miscMain = state.lang === 'en' ? rec.misconceptionEn : rec.misconceptionFr;
        const sciMain = state.lang === 'en' ? rec.scientificEn : rec.scientificFr;
        const sciShort = sciMain.length > 260 ? `${sciMain.slice(0, 257)}…` : sciMain;

        return `<article class="misconception-card">
          <div class="card-head">
            <div class="card-badges">
              <span class="code-badge">${highlightText(rec.code, tokens)}</span>
              <span class="domain-badge domain-badge--${domCls}">${escapeHtml(getDomainLabel(rec))}</span>
            </div>
            <span class="items-badge">${rec.linkedCount} ${escapeHtml(t.itemsUnit)}</span>
          </div>

          <h3 class="card-topic">${highlightText(getTopicLabel(rec), tokens)}</h3>

          <div class="block-misconception">
            <span class="block-label">${escapeHtml(t.misconceptionLabel)}</span>
            <p class="block-text">${highlightText(miscMain, tokens)}</p>
            ${state.lang === 'bi' ? `<p class="block-text-en">${highlightText(rec.misconceptionEn, tokens)}</p>` : ''}
          </div>

          <div class="block-scientific">
            <span class="block-label">${escapeHtml(t.scientificLabel)}</span>
            <p class="block-text">${highlightText(sciShort, tokens)}</p>
            ${state.lang === 'bi' ? `<p class="block-text-en">${highlightText(rec.scientificEn.length > 260 ? rec.scientificEn.slice(0, 257) + '…' : rec.scientificEn, tokens)}</p>` : ''}
          </div>

          ${renderPrevalenceBars(rec)}

          <div class="card-foot">
            <span class="citation-tag">${rec.linkedIds ? `Items : ${escapeHtml(rec.linkedIds.split(';').slice(0, 3).join(', '))}${rec.linkedIds.split(';').length > 3 ? '…' : ''}` : ''}</span>
            <div class="card-actions">
              <button type="button" class="btn-card" data-action="copy-card" data-code="${escapeHtml(rec.code)}">${escapeHtml(t.copyBtn)}</button>
              <button type="button" class="btn-card btn-card--primary" data-action="open-detail" data-code="${escapeHtml(rec.code)}">${escapeHtml(t.detailsBtn)}</button>
            </div>
          </div>
        </article>`;
      }).join('')}</div>`;
    }

    renderPagination(total);
  }

  function renderPagination(total) {
    const totalPages = Math.ceil(total / PAGE_SIZE);
    if (totalPages <= 1) {
      els.paginationBar.innerHTML = '';
      return;
    }

    const pages = [];
    const cur = state.page;
    const addPage = (p) => { if (!pages.includes(p)) pages.push(p); };
    addPage(1);
    for (let p = Math.max(2, cur - 2); p <= Math.min(totalPages - 1, cur + 2); p++) addPage(p);
    addPage(totalPages);

    let html = `<button type="button" class="page-btn" data-action="goto-page" data-page="${cur - 1}"${cur <= 1 ? ' disabled' : ''}>←</button>`;
    let prev = 0;
    for (const p of pages) {
      if (prev && p - prev > 1) html += '<span class="page-ellipsis">…</span>';
      html += `<button type="button" class="page-btn${p === cur ? ' is-current' : ''}" data-action="goto-page" data-page="${p}" aria-current="${p === cur ? 'page' : 'false'}">${p}</button>`;
      prev = p;
    }
    html += `<button type="button" class="page-btn" data-action="goto-page" data-page="${cur + 1}"${cur >= totalPages ? ' disabled' : ''}>→</button>`;
    els.paginationBar.innerHTML = html;
  }

  function syncUiText() {
    const t = getT();
    document.documentElement.lang = state.lang === 'en' ? 'en' : 'fr';
    els.searchInput.placeholder = t.searchPlaceholder;
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const key = el.getAttribute('data-i18n');
      if (t[key]) el.textContent = t[key];
    });
    document.querySelectorAll('[data-action="set-lang"]').forEach((btn) => {
      const active = btn.dataset.lang === state.lang;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', String(active));
    });
    document.querySelectorAll('[data-action="set-view"]').forEach((btn) => {
      const active = btn.dataset.view === state.view;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-pressed', String(active));
    });
  }

  function renderAll() {
    syncUiText();
    renderDomainPills();
    renderFilterOptions();
    applyFilters();
    renderStats();
    renderResults();
  }

  function openDetail(code) {
    const rec = state.records.find((r) => r.code === code);
    if (!rec) return;
    state.activeDetailCode = code;

    const domCls = DOMAIN_META[rec.domainKey]?.cls || 'nos';
    els.detailCodeBadge.textContent = rec.code;
    els.detailDomainBadge.className = `domain-badge domain-badge--${domCls}`;
    els.detailDomainBadge.textContent = `${rec.domainFr} · ${rec.domainEn}`;
    els.detailTitle.textContent = `${rec.topicFr} (${rec.topicEn})`;

    els.detailBody.innerHTML = `
      <div class="block-misconception">
        <span class="block-label">Conception erronée (FR — Québec / PFEQ)</span>
        <p class="block-text">${escapeHtml(rec.misconceptionFr)}</p>
        <p class="block-text-en"><strong>EN (BSCS / AAAS) :</strong> ${escapeHtml(rec.misconceptionEn)}</p>
      </div>

      <div class="block-scientific">
        <span class="block-label">Idée scientifique visée (FR — PFEQ)</span>
        <p class="block-text">${escapeHtml(rec.scientificFr)}</p>
        <p class="block-text-en"><strong>EN (BSCS / AAAS) :</strong> ${escapeHtml(rec.scientificEn)}</p>
      </div>

      <div>
        <h3 class="detail-section-title">Prévalence mesurée auprès des élèves</h3>
        ${renderPrevalenceBars(rec)}
      </div>

      <div class="detail-meta-grid">
        <div class="detail-meta-item">
          <strong>Sous-thème (FR)</strong>
          <span>${escapeHtml(rec.subtopicFr)}</span>
        </div>
        <div class="detail-meta-item">
          <strong>Items d'évaluation liés (${rec.linkedCount})</strong>
          <span>${escapeHtml(rec.linkedIds ? rec.linkedIds.replace(/;/g, ', ') : 'Aucun item recensé')}</span>
        </div>
      </div>
    `;

    if (rec.sourceUrl) {
      els.detailSourceLink.href = rec.sourceUrl;
      els.detailSourceLink.hidden = false;
    } else {
      els.detailSourceLink.hidden = true;
    }

    els.detailModal.showModal();
  }

  function formatPoeSnippet(rec) {
    return [
      `[${rec.code}] ${rec.domainFr} — ${rec.topicFr}`,
      `Conception erronée (élève) : ${rec.misconceptionFr}`,
      `Idée scientifique visée : ${rec.scientificFr}`,
      `Prévalence : 6e–2e sec. = ${formatPct(rec.g68)} | 3e–5e sec. = ${formatPct(rec.g912)}`,
      rec.sourceUrl ? `Source : ${rec.sourceUrl}` : ''
    ].filter(Boolean).join('\n');
  }

  async function copyToClipboard(text) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
      }
      showToast(getT().copiedMsg);
    } catch {
      showToast('Impossible de copier automatiquement.');
    }
  }

  let toastTimer = null;
  function showToast(msg) {
    els.toast.textContent = msg;
    els.toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { els.toast.hidden = true; }, 2600);
  }

  /** Parseur RFC 4180 autonome pour importer un fichier CSV local. */
  function parseCsvText(text) {
    const clean = text.replace(/^\uFEFF/, '');
    const rows = [];
    let row = [];
    let field = '';
    let inQuotes = false;

    for (let i = 0; i < clean.length; i++) {
      const ch = clean[i];
      if (inQuotes) {
        if (ch === '"') {
          if (clean[i + 1] === '"') {
            field += '"';
            i++;
          } else {
            inQuotes = false;
          }
        } else {
          field += ch;
        }
      } else if (ch === '"') {
        inQuotes = true;
      } else if (ch === ',') {
        row.push(field);
        field = '';
      } else if (ch === '\r') {
        if (clean[i + 1] === '\n') i++;
        row.push(field);
        rows.push(row);
        row = [];
        field = '';
      } else if (ch === '\n') {
        row.push(field);
        rows.push(row);
        row = [];
        field = '';
      } else {
        field += ch;
      }
    }
    if (field.length || row.length) {
      row.push(field);
      rows.push(row);
    }
    if (rows.length < 2) return [];
    const headers = rows[0].map((h) => h.trim());
    return rows.slice(1)
      .filter((r) => r.some((cell) => cell.trim() !== ''))
      .map((r) => {
        const obj = {};
        headers.forEach((h, idx) => { obj[h] = r[idx] ?? ''; });
        return obj;
      });
  }

  function csvEscape(val) {
    const s = (val ?? '').toString();
    if (/[",\r\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
    return s;
  }

  function exportFilteredCsv() {
    const useEn = state.lang === 'en';
    const headers = [
      'misconception_code', 'domain', 'topic', 'subtopic',
      'misconception_text', 'scientific_idea', 'grade_bands',
      'linked_items_count', 'linked_item_ids', 'source_url'
    ];

    const lines = [headers.join(',')];
    for (const r of state.filtered) {
      const vals = [
        r.code,
        useEn ? r.domainEn : r.domainFr,
        useEn ? r.topicEn : r.topicFr,
        useEn ? r.subtopicEn : r.subtopicFr,
        useEn ? r.misconceptionEn : r.misconceptionFr,
        useEn ? r.scientificEn : r.scientificFr,
        useEn ? r.gradeBandsEn : r.gradeBandsFr,
        r.linkedCount,
        r.linkedIds,
        r.sourceUrl
      ];
      lines.push(vals.map(csvEscape).join(','));
    }

    const blob = new Blob(['\uFEFF' + lines.join('\r\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = useEn ? 'bscs_selection_en.csv' : 'bscs_selection_fr_qc.csv';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast(`${state.filtered.length} lignes exportées en CSV.`);
  }

  function handleCsvUpload(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const parsed = parseCsvText(String(reader.result || ''));
      if (!parsed.length || !parsed[0].misconception_code) {
        showToast('Fichier CSV invalide (colonne misconception_code manquante).');
        return;
      }
      state.records = parsed.map(hydrateRecord);
      state.domain = '';
      state.topic = '';
      state.subtopic = '';
      state.page = 1;
      state.sourceLabel = `CSV importé : ${file.name} (${state.records.length})`;
      renderAll();
      showToast(`${state.records.length} conceptions chargées depuis ${file.name}.`);
    };
    reader.readAsText(file, 'UTF-8');
  }

  function bindEvents() {
    let searchDebounce = null;
    els.searchInput.addEventListener('input', (e) => {
      state.query = e.target.value;
      state.page = 1;
      clearTimeout(searchDebounce);
      searchDebounce = setTimeout(() => {
        applyFilters();
        renderStats();
        renderResults();
      }, 90);
    }, { signal });

    document.addEventListener('change', (e) => {
      const target = e.target;
      if (target === els.csvFileInput) {
        handleCsvUpload(target.files[0]);
        target.value = '';
        return;
      }
      const param = target.dataset?.param;
      if (!param) return;
      if (param === 'topic') {
        state.topic = target.value;
        state.subtopic = '';
        state.page = 1;
        renderFilterOptions();
      } else if (param === 'subtopic') {
        state.subtopic = target.value;
        state.page = 1;
      } else if (param === 'minPrevalence') {
        state.minPrevalence = Number(target.value) || 0;
        state.page = 1;
      } else if (param === 'gradeBasis') {
        state.gradeBasis = target.value;
        state.page = 1;
      } else if (param === 'itemsOnly') {
        state.itemsOnly = target.value;
        state.page = 1;
      } else if (param === 'sort') {
        state.sort = target.value;
        state.page = 1;
      }
      applyFilters();
      renderStats();
      renderResults();
    }, { signal });

    document.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-action]');
      if (!btn) return;
      const action = btn.dataset.action;

      switch (action) {
        case 'set-lang':
          state.lang = btn.dataset.lang;
          renderAll();
          break;
        case 'set-view':
          state.view = btn.dataset.view;
          syncUiText();
          renderResults();
          break;
        case 'set-domain':
          state.domain = btn.dataset.domain || '';
          state.topic = '';
          state.subtopic = '';
          state.page = 1;
          renderDomainPills();
          renderFilterOptions();
          applyFilters();
          renderStats();
          renderResults();
          break;
        case 'clear-search':
          state.query = '';
          els.searchInput.value = '';
          state.page = 1;
          applyFilters();
          renderStats();
          renderResults();
          els.searchInput.focus();
          break;
        case 'reset-filters':
          state.query = '';
          state.domain = '';
          state.topic = '';
          state.subtopic = '';
          state.minPrevalence = 0;
          state.itemsOnly = 'all';
          state.page = 1;
          els.searchInput.value = '';
          els.prevalenceFilter.value = '0';
          els.itemsFilter.value = 'all';
          renderAll();
          break;
        case 'goto-page': {
          const p = Number(btn.dataset.page);
          if (p >= 1) {
            state.page = p;
            renderResults();
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }
          break;
        }
        case 'open-detail':
          openDetail(btn.dataset.code);
          break;
        case 'close-detail':
          els.detailModal.close();
          break;
        case 'copy-card': {
          const rec = state.records.find((r) => r.code === btn.dataset.code);
          if (rec) copyToClipboard(formatPoeSnippet(rec));
          break;
        }
        case 'copy-poe': {
          const rec = state.records.find((r) => r.code === state.activeDetailCode);
          if (rec) copyToClipboard(formatPoeSnippet(rec));
          break;
        }
        case 'export-csv':
          exportFilteredCsv();
          break;
        case 'open-info':
          els.infoModal.showModal();
          break;
        case 'close-info':
          els.infoModal.close();
          break;
        default:
          break;
      }
    }, { signal });

    // Fermer les modales en cliquant sur l'arrière-plan
    [els.detailModal, els.infoModal].forEach((dlg) => {
      dlg.addEventListener('click', (e) => {
        if (e.target === dlg) dlg.close();
      }, { signal });
    });
  }

  function init() {
    bindEvents();
    const bundle = window.BSCS_CATALOG;
    if (bundle && Array.isArray(bundle.records) && bundle.records.length) {
      state.records = bundle.records.map(hydrateRecord);
      state.sourceLabel = `Catalogue intégré FR/EN (${state.records.length})`;
      renderAll();
    } else {
      // Secours si ouvert via serveur HTTP sans data.js
      fetch('bscs_misconceptions_db_fr.csv')
        .then((res) => {
          if (!res.ok) throw new Error('CSV FR introuvable');
          return res.text();
        })
        .then((txt) => {
          state.records = parseCsvText(txt).map(hydrateRecord);
          state.sourceLabel = `bscs_misconceptions_db_fr.csv (${state.records.length})`;
          renderAll();
        })
        .catch(() => {
          els.resultsContainer.innerHTML = `
            <div class="empty-state">
              <h3>Aucune donnée chargée</h3>
              <p>Importez <code>bscs_misconceptions_db_fr.csv</code> à l'aide du bouton <strong>Importer CSV</strong> ci-dessus.</p>
            </div>`;
        });
    }
  }

  window.BSCS_APP = {
    dispose() { controller.abort(); },
    getState() { return state; }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
