/**
 * Explorateur PDA PFEQ & Constellation des méconceptions (style Synergie)
 * 100 % hors ligne (file://), zéro dépendance externe, Charte Québec, AbortController.
 */
(() => {
  'use strict';

  const DATA = window.PDA_EXPLORER_DATA;
  if (!DATA) return;

  const PAGE_SIZE = 20;
  const controller = new AbortController();
  const { signal } = controller;

  const UNIV_META = {
    'Univers matériel':      { cls: 'u-mat', color: '#d97706' },
    'Univers vivant':        { cls: 'u-viv', color: '#16a34a' },
    'Terre et espace':       { cls: 'u-ter', color: '#0284c7' },
    'Univers technologique': { cls: 'u-tec', color: '#9333ea' }
  };

  // Indexation rapide en mémoire
  const pdaById = new Map();
  const linksByPda = new Map();
  const linksByMc = new Map();

  for (const m of DATA.manifestations) {
    m._search = normalizeText([
      m.id, m.univ, m.sec, m.secs.join(' '), m.cat, m.concept,
      m.text, m.verb, m.bloom, m.tags.join(' '), m.bscs.join(' '),
      m.prog.map((p) => `${p.p} ${p.num} ${p.s}`).join(' ')
    ].join(' '));
    pdaById.set(m.id, m);
    linksByPda.set(m.id, []);
  }

  for (const lk of DATA.links) {
    if (!linksByPda.has(lk.pda)) linksByPda.set(lk.pda, []);
    linksByPda.get(lk.pda).push(lk);
    if (!linksByMc.has(lk.mc)) linksByMc.set(lk.mc, []);
    linksByMc.get(lk.mc).push(lk);

    // Enrichir l'index de recherche de la manifestation avec le code et texte des méconceptions liées
    const pda = pdaById.get(lk.pda);
    const mc = DATA.misconceptions[lk.mc];
    if (pda && mc) {
      pda._search += ' ' + normalizeText(`${mc.code} ${mc.text}`);
    }
  }

  // Manifestations triées par nombre de méconceptions (pour le sélecteur de nœud central)
  const linkedPdas = DATA.manifestations
    .filter((m) => m.mcCount > 0)
    .sort((a, b) => b.highPrevCount - a.highPrevCount || b.mcCount - a.mcCount || b.maxPrev - a.maxPrev);

  const state = {
    tab: 'explorer',
    // Filtres Explorateur
    q: '',
    prog: '',
    univ: '',
    sec: '',
    type: '',
    bloom: '',
    statut: '',
    mcMode: 'all',
    tag: '',
    sort: 'mc-desc',
    page: 1,
    filtered: [],
    openDrawers: new Set(),

    // État Constellation (Nœuds)
    graphMode: 'ego', // 'ego' | 'global'
    centerPdaId: linkedPdas[0] ? linkedPdas[0].id : DATA.manifestations[0].id,
    showNeighbors: true,
    graphLimit: 45,
    graphUniv: '',
    graphProg: '',
    graphLinkType: '',
    graphMinPrev: 0,
    selectedNodeId: null,
    hoveredNodeId: null,
    frozen: false,

    // État Matrice
    matrixProg: '',
    matrixUniv: ''
  };

  // ==================== ÉTAT PHYSIQUE DU GRAPHE (ZÉRO ALLOCATION EN BOUCLE) ====================
  const graph = {
    nodes: [],
    edges: [],
    nodeMap: new Map(),
    camX: 0,
    camY: 0,
    zoom: 1,
    width: 800,
    height: 600,
    dpr: 1,
    rafId: 0,
    alpha: 1,
    draggingNode: null,
    panning: false,
    panStartX: 0,
    panStartY: 0,
    camStartX: 0,
    camStartY: 0,
    pointerMoved: false
  };

  const els = {
    pdaSearch: document.getElementById('pdaSearch'),
    clearPdaSearch: document.getElementById('clearPdaSearch'),
    resetExplorerBtn: document.getElementById('resetExplorerBtn'),
    progChips: document.getElementById('progChips'),
    univSelect: document.getElementById('univSelect'),
    secSelect: document.getElementById('secSelect'),
    typeSelect: document.getElementById('typeSelect'),
    bloomSelect: document.getElementById('bloomSelect'),
    statutSelect: document.getElementById('statutSelect'),
    mcFilterSelect: document.getElementById('mcFilterSelect'),
    pdaSortSelect: document.getElementById('pdaSortSelect'),
    topTagsCloud: document.getElementById('topTagsCloud'),
    explorerKpis: document.getElementById('explorerKpis'),
    pdaList: document.getElementById('pdaList'),
    pdaPagination: document.getElementById('pdaPagination'),

    centerConceptSelect: document.getElementById('centerConceptSelect'),
    egoPickerWrap: document.getElementById('egoPickerWrap'),
    globalControlsWrap: document.getElementById('globalControlsWrap'),
    showNeighborsChk: document.getElementById('showNeighborsChk'),
    graphLimitSelect: document.getElementById('graphLimitSelect'),
    graphUnivSelect: document.getElementById('graphUnivSelect'),
    graphProgSelect: document.getElementById('graphProgSelect'),
    graphLinkTypeSelect: document.getElementById('graphLinkTypeSelect'),
    graphPrevSelect: document.getElementById('graphPrevSelect'),
    graphCanvas: document.getElementById('graphCanvas'),
    graphTooltip: document.getElementById('graphTooltip'),
    graphLegend: document.getElementById('graphLegend'),
    freezeBtn: document.getElementById('freezeBtn'),
    inspectorContent: document.getElementById('inspectorContent'),

    matrixProgSelect: document.getElementById('matrixProgSelect'),
    matrixUnivSelect: document.getElementById('matrixUnivSelect'),
    matrixStats: document.getElementById('matrixStats'),
    matrixTableWrap: document.getElementById('matrixTableWrap'),

    legendModal: document.getElementById('legendModal'),
    toast: document.getElementById('toast')
  };

  function normalizeText(str) {
    return (str || '').toString().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  }

  function escapeHtml(str) {
    return (str || '').toString()
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function formatPct(val) {
    if (val === null || val === undefined || Number.isNaN(val)) return '—';
    const s = Number.isInteger(val) ? String(val) : val.toFixed(1).replace('.', ',');
    return `${s}\u00a0%`;
  }

  function highlight(text, tokens) {
    if (!tokens.length) return escapeHtml(text);
    const norm = normalizeText(text);
    const map = [];
    for (let i = 0; i < text.length; i++) {
      const n = text[i].normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      for (let k = 0; k < n.length; k++) map.push(i);
    }
    const ranges = [];
    for (const tk of tokens) {
      if (tk.length < 2) continue;
      let pos = norm.indexOf(tk);
      while (pos !== -1) {
        const s = map[pos];
        const e = (map[pos + tk.length - 1] ?? text.length - 1) + 1;
        if (s !== undefined && e > s) ranges.push([s, e]);
        pos = norm.indexOf(tk, pos + tk.length);
      }
    }
    if (!ranges.length) return escapeHtml(text);
    ranges.sort((a, b) => a[0] - b[0]);
    const merged = [];
    for (const r of ranges) {
      if (!merged.length || r[0] > merged[merged.length - 1][1]) merged.push(r);
      else merged[merged.length - 1][1] = Math.max(merged[merged.length - 1][1], r[1]);
    }
    let out = '';
    let cur = 0;
    for (const [s, e] of merged) {
      out += escapeHtml(text.slice(cur, s)) + `<mark class="hl">${escapeHtml(text.slice(s, e))}</mark>`;
      cur = e;
    }
    return out + escapeHtml(text.slice(cur));
  }

  let toastTimer = null;
  function showToast(msg) {
    els.toast.textContent = msg;
    els.toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { els.toast.hidden = true; }, 2500);
  }

  async function copyText(txt) {
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(txt);
      } else {
        const ta = document.createElement('textarea');
        ta.value = txt;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        ta.remove();
      }
      showToast('Fiche POE copiée dans le presse-papiers !');
    } catch {
      showToast('Impossible de copier automatiquement.');
    }
  }

  // ==================== ONGLET 1 : EXPLORATEUR PDA ====================
  function initFilterControls() {
    // Pilules programmes
    els.progChips.innerHTML = `<button type="button" class="prog-chip is-active" data-action="set-prog" data-prog="">Tous</button>` +
      DATA.progOrder.map((p) => `<button type="button" class="prog-chip" data-action="set-prog" data-prog="${p}">${p}</button>`).join('');

    // Univers
    const univs = Object.keys(UNIV_META);
    els.univSelect.innerHTML = '<option value="">Tous les univers (4)</option>' +
      univs.map((u) => `<option value="${escapeHtml(u)}">${escapeHtml(u)}</option>`).join('');

    // Sélecteurs programmes pour Graphe & Matrice
    const progOpts = '<option value="">Tous les programmes</option>' +
      DATA.progOrder.map((p) => `<option value="${p}">${p}</option>`).join('');
    els.graphProgSelect.innerHTML = progOpts;
    els.matrixProgSelect.innerHTML = progOpts;

    // Sélecteur rapide Concept central (trié par densité de méconceptions)
    els.centerConceptSelect.innerHTML = linkedPdas.map((m) => {
      const label = `${m.concept} (${m.mcCount} méc.${m.highPrevCount ? ` · ${m.highPrevCount} ≥40%` : ''}) — ${m.text.slice(0, 56)}…`;
      return `<option value="${m.id}">${escapeHtml(label)}</option>`;
    }).join('');
    els.centerConceptSelect.value = state.centerPdaId;
  }

  function updateSectionOptions() {
    const secCounts = new Map();
    for (const m of DATA.manifestations) {
      if (state.univ && m.univ !== state.univ) continue;
      if (state.prog && !m.prog.some((p) => p.p === state.prog)) continue;
      for (const s of m.secs) {
        if (!s) continue;
        secCounts.set(s, (secCounts.get(s) || 0) + 1);
      }
    }
    const sorted = [...secCounts.entries()].sort((a, b) => a[0].localeCompare(b[0], 'fr'));
    if (state.sec && !secCounts.has(state.sec)) state.sec = '';
    els.secSelect.innerHTML = `<option value="">Toutes les sections (${sorted.length})</option>` +
      sorted.map(([s, c]) => `<option value="${escapeHtml(s)}"${state.sec === s ? ' selected' : ''}>${escapeHtml(s)} (${c})</option>`).join('');
  }

  function applyExplorerFilters() {
    const tokens = normalizeText(state.q).split(/\s+/).filter(Boolean);
    const list = DATA.manifestations.filter((m) => {
      if (state.univ && m.univ !== state.univ) return false;
      if (state.sec && !m.secs.includes(state.sec)) return false;
      if (state.type && m.type !== state.type) return false;
      if (state.bloom && m.bloom !== state.bloom) return false;
      if (state.tag && !m.tags.includes(state.tag)) return false;

      if (state.prog) {
        const hit = m.prog.find((p) => p.p === state.prog);
        if (!hit) return false;
        if (state.statut && hit.s !== state.statut) return false;
      } else if (state.statut) {
        if (!m.prog.some((p) => p.s === state.statut)) return false;
      }

      if (state.mcMode === 'linked' && m.mcCount === 0) return false;
      if (state.mcMode === 'high' && m.highPrevCount === 0) return false;
      if (state.mcMode === 'none' && m.mcCount > 0) return false;

      if (tokens.length) {
        for (const tk of tokens) {
          if (!m._search.includes(tk)) return false;
        }
      }
      return true;
    });

    list.sort((a, b) => {
      if (state.sort === 'mc-desc') return b.mcCount - a.mcCount || b.highPrevCount - a.highPrevCount || a.concept.localeCompare(b.concept, 'fr');
      if (state.sort === 'prev-desc') return b.maxPrev - a.maxPrev || b.mcCount - a.mcCount;
      if (state.sort === 'verb') return a.verb.localeCompare(b.verb, 'fr') || a.text.localeCompare(b.text, 'fr');
      return a.univ.localeCompare(b.univ, 'fr') || a.sec.localeCompare(b.sec, 'fr') || a.concept.localeCompare(b.concept, 'fr');
    });

    state.filtered = list;
    const totalPages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
    if (state.page > totalPages) state.page = 1;
  }

  function renderTopTags() {
    const counts = new Map();
    for (const m of state.filtered) {
      for (const t of m.tags) counts.set(t, (counts.get(t) || 0) + 1);
    }
    const top = [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 18);
    els.topTagsCloud.innerHTML = top.map(([t, c]) =>
      `<button type="button" class="tag-pill${state.tag === t ? ' is-active' : ''}" data-action="toggle-tag" data-tag="${escapeHtml(t)}">#${escapeHtml(t)} (${c})</button>`
    ).join('') || '<span class="pda-id-tag">Aucun tag</span>';
  }

  function renderExplorer() {
    updateSectionOptions();
    applyExplorerFilters();
    renderTopTags();

    const list = state.filtered;
    const tokens = normalizeText(state.q).split(/\s+/).filter(Boolean);
    const hasFilter = Boolean(state.q || state.prog || state.univ || state.sec || state.type || state.bloom || state.statut || state.mcMode !== 'all' || state.tag);
    els.resetExplorerBtn.hidden = !hasFilter;
    els.clearPdaSearch.hidden = !state.q;

    const linkedCnt = list.filter((m) => m.mcCount > 0).length;
    const highCnt = list.filter((m) => m.highPrevCount > 0).length;
    const totalLinks = list.reduce((s, m) => s + m.mcCount, 0);

    els.explorerKpis.innerHTML = `
      <div class="kpi-box"><div class="kpi-lbl">Manifestations PDA</div><div class="kpi-val">${list.length} / ${DATA.manifestations.length}</div></div>
      <div class="kpi-box kpi-box--success"><div class="kpi-lbl">Avec méconceptions</div><div class="kpi-val">${linkedCnt}</div></div>
      <div class="kpi-box kpi-box--danger"><div class="kpi-lbl">Fort risque POE (≥ 40 %)</div><div class="kpi-val">${highCnt}</div></div>
      <div class="kpi-box"><div class="kpi-lbl">Liens BSCS associés</div><div class="kpi-val">${totalLinks}</div></div>
    `;

    if (!list.length) {
      els.pdaList.innerHTML = `<div class="empty-box"><h3>Aucune manifestation PDA trouvée</h3><p>Essayez d'élargir vos filtres ou réinitialisez la recherche.</p></div>`;
      els.pdaPagination.innerHTML = '';
      return;
    }

    const start = (state.page - 1) * PAGE_SIZE;
    const pageItems = list.slice(start, start + PAGE_SIZE);

    els.pdaList.innerHTML = pageItems.map((m) => {
      const uCls = UNIV_META[m.univ]?.cls || 'u-mat';
      const drawerOpen = state.openDrawers.has(m.id);
      const pdaLinks = (linksByPda.get(m.id) || []).slice().sort((a, b) => {
        const pa = DATA.misconceptions[a.mc]?.maxP || 0;
        const pb = DATA.misconceptions[b.mc]?.maxP || 0;
        return pb - pa || b.conf - a.conf;
      });

      const meqStrip = m.prog.map((pe) => {
        let cls = 'meq-cell--reut';
        let sym = '■';
        if (pe.s.startsWith('Planifié')) { cls = 'meq-cell--plan'; sym = '→'; }
        else if (pe.s.startsWith('Maîtrisé')) { cls = 'meq-cell--mait'; sym = '★'; }
        const los = pe.sp.includes('◆') ? ' ◆' : '';
        return `<span class="meq-cell ${cls}" title="${escapeHtml(`${pe.p} · ${pe.s} · ${pe.sp} · ${pe.src}`)}">${escapeHtml(pe.p)} ${sym}${los}</span>`;
      }).join('');

      const drawerHtml = drawerOpen && pdaLinks.length ? `
        <div class="mc-drawer">
          ${pdaLinks.map((lk) => {
            const mc = DATA.misconceptions[lk.mc];
            if (!mc) return '';
            const rCls = lk.type === 'PREREQUIS' ? ' mc-row--prereq' : (lk.type === 'CONCEPT_VOISIN' ? ' mc-row--voisin' : '');
            return `<div class="mc-row${rCls}">
              <div class="mc-row-head">
                <div><span class="mc-code">${escapeHtml(mc.code)}</span> <strong>${escapeHtml(lk.type)}</strong> (${Math.round(lk.conf * 100)}\u00a0%)</div>
                <div><strong>${escapeHtml(mc.gb || 'Prévalence n.d.')}</strong></div>
              </div>
              <div>${highlight(mc.text, tokens)}</div>
              <p class="mc-justif">${escapeHtml(lk.j)}</p>
            </div>`;
          }).join('')}
        </div>` : '';

      return `<article class="pda-card">
        <div class="pda-card-top">
          <div class="pda-breadcrumb">
            <span class="u-badge ${uCls}">${escapeHtml(m.univ)}</span>
            <span class="crumb-txt">${highlight(m.sec, tokens)}</span>
            ${m.concept && m.concept !== m.sec ? `<span class="crumb-sep">›</span><span class="crumb-txt">${highlight(m.concept, tokens)}</span>` : ''}
            <span class="bloom-badge">${escapeHtml(m.verb)} · ${escapeHtml(m.bloom)}</span>
          </div>
          <span class="pda-id-tag">${escapeHtml(m.id)} · ${escapeHtml(m.type)}</span>
        </div>

        <p class="pda-statement">${highlight(m.text, tokens)}</p>

        <div class="meq-strip">${meqStrip}</div>

        <div class="pda-footer">
          <div class="pda-tags">
            ${m.tags.map((t) => `<button type="button" class="tag-pill${state.tag === t ? ' is-active' : ''}" data-action="toggle-tag" data-tag="${escapeHtml(t)}">#${escapeHtml(t)}</button>`).join('')}
          </div>
          <div class="pda-actions">
            ${m.mcCount > 0
              ? `<button type="button" class="mc-pill" data-action="toggle-drawer" data-id="${m.id}">
                  ${drawerOpen ? '▾' : '▸'} ${m.mcCount} méconception${m.mcCount > 1 ? 's' : ''}${m.highPrevCount ? ` (${m.highPrevCount} ≥ 40 %)` : ''}
                </button>
                <button type="button" class="btn-constellation" data-action="open-in-graph" data-id="${m.id}">
                  Constellation 🕸️
                </button>`
              : `<span class="mc-pill mc-pill--zero">0 méconception BSCS liée</span>`}
          </div>
        </div>
        ${drawerHtml}
      </article>`;
    }).join('');

    renderPagination(list.length);
  }

  function renderPagination(total) {
    const pages = Math.ceil(total / PAGE_SIZE);
    if (pages <= 1) { els.pdaPagination.innerHTML = ''; return; }
    const cur = state.page;
    const nums = new Set([1, pages]);
    for (let i = Math.max(2, cur - 2); i <= Math.min(pages - 1, cur + 2); i++) nums.add(i);
    const sorted = [...nums].sort((a, b) => a - b);
    let html = `<button type="button" class="page-btn" data-action="pda-page" data-page="${cur - 1}"${cur <= 1 ? ' disabled' : ''}>←</button>`;
    let prev = 0;
    for (const p of sorted) {
      if (prev && p - prev > 1) html += '<span style="padding:0 4px;color:var(--muted);">…</span>';
      html += `<button type="button" class="page-btn${p === cur ? ' is-current' : ''}" data-action="pda-page" data-page="${p}">${p}</button>`;
      prev = p;
    }
    html += `<button type="button" class="page-btn" data-action="pda-page" data-page="${cur + 1}"${cur >= pages ? ' disabled' : ''}>→</button>`;
    els.pdaPagination.innerHTML = html;
  }

  function exportFilteredPdaCsv() {
    const headers = ['id_manifestation', 'univers', 'section_programme', 'concept_prescrit', 'type_de_savoir', 'verbe_action', 'bloom_niveau', 'manifestation', 'programmes', 'nb_meconceptions_bscs', 'nb_fort_risque_40pct', 'tags_thematiques'];
    const esc = (v) => { const s = String(v ?? ''); return /[";\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
    const lines = [headers.join(';')];
    for (const m of state.filtered) {
      lines.push([
        m.id, m.univ, m.sec, m.concept, m.type, m.verb, m.bloom, m.text,
        m.prog.map((p) => `${p.p}:${p.s}`).join(' | '),
        m.mcCount, m.highPrevCount, m.tags.join('|')
      ].map(esc).join(';'));
    }
    const blob = new Blob(['\uFEFF' + lines.join('\r\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pda_selection_pfeq.csv';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast(`${state.filtered.length} manifestations exportées en CSV.`);
  }

  // ==================== ONGLET 2 : CONSTELLATION DE NŒUDS (STYLE SYNERGIE) ====================
  function getFilteredLinksForPda(pdaId) {
    const raw = linksByPda.get(pdaId) || [];
    return raw.filter((lk) => {
      if (state.graphLinkType && lk.type !== state.graphLinkType) return false;
      const mc = DATA.misconceptions[lk.mc];
      if (!mc) return false;
      if (state.graphMinPrev > 0 && mc.maxP < state.graphMinPrev) return false;
      return true;
    });
  }

  function buildGraphData() {
    graph.nodes = [];
    graph.edges = [];
    graph.nodeMap.clear();
    graph.alpha = 1.0;

    if (state.graphMode === 'ego') {
      const center = pdaById.get(state.centerPdaId) || linkedPdas[0];
      if (!center) return;
      state.centerPdaId = center.id;
      els.centerConceptSelect.value = center.id;

      // Nœud central (Concept PDA)
      const cNode = {
        id: center.id,
        kind: 'pda-center',
        label: center.concept,
        sub: center.sec,
        radius: 34,
        color: '#095797',
        stroke: '#38bdf8',
        x: 0, y: 0, vx: 0, vy: 0,
        pinned: true,
        data: center
      };
      graph.nodes.push(cNode);
      graph.nodeMap.set(cNode.id, cNode);

      const pLinks = getFilteredLinksForPda(center.id);
      const count = pLinks.length;
      const orbitR = Math.max(155, Math.min(260, 125 + count * 4.5));

      const neighborScores = new Map();

      pLinks.forEach((lk, idx) => {
        const mc = DATA.misconceptions[lk.mc];
        const angle = (2 * Math.PI * idx) / Math.max(1, count) - Math.PI / 2;
        const rNode = Math.max(11, Math.min(24, 9 + (mc.maxP || 15) * 0.24));
        const col = mc.maxP >= 40 ? '#dc2626' : (mc.maxP >= 25 ? '#d97706' : '#2563eb');
        const mNode = {
          id: mc.code,
          kind: 'mc',
          label: `${mc.code} (${mc.maxP ? Math.round(mc.maxP) + '%' : '?'})`,
          radius: rNode,
          color: col,
          stroke: '#ffffff',
          x: Math.cos(angle) * orbitR,
          y: Math.sin(angle) * orbitR,
          vx: 0, vy: 0,
          pinned: false,
          data: mc,
          linkMeta: lk
        };
        graph.nodes.push(mNode);
        graph.nodeMap.set(mNode.id, mNode);
        graph.edges.push({
          source: cNode,
          target: mNode,
          type: lk.type,
          conf: lk.conf,
          restLen: orbitR
        });

        // Trouver les concepts PDA voisins partageant cette méconception (synergie)
        if (state.showNeighbors) {
          for (const otherLk of (linksByMc.get(mc.code) || [])) {
            if (otherLk.pda === center.id) continue;
            const nbPda = pdaById.get(otherLk.pda);
            if (!nbPda) continue;
            if (state.graphUniv && nbPda.univ !== state.graphUniv) continue;
            if (state.graphProg && !nbPda.prog.some((p) => p.p === state.graphProg)) continue;
            if (!neighborScores.has(otherLk.pda)) neighborScores.set(otherLk.pda, []);
            neighborScores.get(otherLk.pda).push({ mc: mc.code, lk: otherLk });
          }
        }
      });

      // Ajouter les Top 10 concepts PDA en synergie sur l'orbite extérieure
      if (state.showNeighbors && neighborScores.size) {
        const topNb = [...neighborScores.entries()]
          .sort((a, b) => b[1].length - a[1].length)
          .slice(0, 10);
        const outerR = orbitR + 150;
        topNb.forEach(([nbId, shared], idx) => {
          const nb = pdaById.get(nbId);
          // Placer près du barycentre de ses méconceptions partagées
          let bx = 0; let by = 0;
          for (const s of shared) {
            const mn = graph.nodeMap.get(s.mc);
            if (mn) { bx += mn.x; by += mn.y; }
          }
          const ang = (bx || by) ? Math.atan2(by, bx) : (2 * Math.PI * idx) / topNb.length;
          const nNode = {
            id: nb.id,
            kind: 'pda-neighbor',
            label: nb.concept,
            sub: `${shared.length} lien(s) partagé(s)`,
            radius: Math.min(26, 15 + shared.length * 1.6),
            color: '#0d9488',
            stroke: '#ccfbf1',
            x: Math.cos(ang) * outerR,
            y: Math.sin(ang) * outerR,
            vx: 0, vy: 0,
            pinned: false,
            data: nb,
            sharedCount: shared.length
          };
          graph.nodes.push(nNode);
          graph.nodeMap.set(nNode.id, nNode);
          for (const s of shared) {
            const mn = graph.nodeMap.get(s.mc);
            if (mn) {
              graph.edges.push({
                source: mn,
                target: nNode,
                type: 'SYNERGIE',
                conf: s.lk.conf,
                restLen: 120
              });
            }
          }
        });
      }

      state.selectedNodeId = cNode.id;
    } else {
      // MODE CONSTELLATION GLOBALE (Concepts PDA pivots reliés par méconceptions partagées)
      const candidates = linkedPdas.filter((m) => {
        if (state.graphUniv && m.univ !== state.graphUniv) return false;
        if (state.graphProg && !m.prog.some((p) => p.p === state.graphProg)) return false;
        return getFilteredLinksForPda(m.id).length > 0;
      });
      const topPdas = candidates.slice(0, state.graphLimit);
      const idSet = new Set(topPdas.map((m) => m.id));

      // Regrouper l'angle initial par univers pour une lisibilité immédiate
      const univOrder = Object.keys(UNIV_META);
      topPdas.forEach((m, idx) => {
        const uIdx = Math.max(0, univOrder.indexOf(m.univ));
        const baseAng = (uIdx * Math.PI) / 2 + ((idx % 17) / 17) * (Math.PI / 2.2);
        const radDist = 110 + (idx % 5) * 58;
        const filteredLks = getFilteredLinksForPda(m.id);
        const r = Math.max(12, Math.min(32, 10 + Math.sqrt(filteredLks.length) * 4.2));
        const node = {
          id: m.id,
          kind: 'pda-global',
          label: m.concept,
          sub: `${filteredLks.length} méc.`,
          radius: r,
          color: UNIV_META[m.univ]?.color || '#1472BF',
          stroke: m.highPrevCount >= 3 ? '#dc2626' : '#ffffff',
          x: Math.cos(baseAng) * radDist,
          y: Math.sin(baseAng) * radDist,
          vx: 0, vy: 0,
          pinned: false,
          data: m,
          filteredMcCount: filteredLks.length
        };
        graph.nodes.push(node);
        graph.nodeMap.set(node.id, node);
      });

      // Créer les arêtes de synergie entre concepts partageant des méconceptions
      const pairCount = new Map();
      for (const m of topPdas) {
        for (const lk of getFilteredLinksForPda(m.id)) {
          for (const other of (linksByMc.get(lk.mc) || [])) {
            if (other.pda <= m.id || !idSet.has(other.pda)) continue;
            const k = `${m.id}|${other.pda}`;
            pairCount.set(k, (pairCount.get(k) || 0) + 1);
          }
        }
      }
      for (const [k, weight] of pairCount.entries()) {
        const [a, b] = k.split('|');
        const na = graph.nodeMap.get(a);
        const nb = graph.nodeMap.get(b);
        if (na && nb) {
          graph.edges.push({
            source: na,
            target: nb,
            type: 'SYNERGIE_GLOBAL',
            weight,
            restLen: Math.max(85, 170 - weight * 12)
          });
        }
      }

      state.selectedNodeId = graph.nodes[0] ? graph.nodes[0].id : null;
    }

    updateGraphLegend();
    fitGraphCamera();
    renderInspector();
    startPhysicsLoop();
  }

  function updateGraphLegend() {
    if (state.graphMode === 'ego') {
      els.graphLegend.innerHTML = `
        <div class="gleg-row"><span class="dot dot--center"></span> Concept PDA central</div>
        <div class="gleg-row"><span class="dot dot--mc-high"></span> Méconception ≥ 40 %</div>
        <div class="gleg-row"><span class="dot dot--mc-mid"></span> Méconception 25–39 %</div>
        <div class="gleg-row"><span class="dot dot--mc-low"></span> Méconception &lt; 25 %</div>
        <div class="gleg-row"><span class="dot dot--neighbor"></span> Concept PDA en synergie</div>
        <div class="gleg-sep"></div>
        <div class="gleg-row"><span class="line-sample line--direct"></span> Lien DIRECT</div>
        <div class="gleg-row"><span class="line-sample line--prereq"></span> Lien PRÉREQUIS</div>
        <div class="gleg-row"><span class="line-sample line--voisin"></span> Concept voisin</div>`;
    } else {
      els.graphLegend.innerHTML = `
        <div class="gleg-row"><span class="dot" style="background:#d97706"></span> Univers matériel (incl. CHI/PHY)</div>
        <div class="gleg-row"><span class="dot" style="background:#16a34a"></span> Univers vivant</div>
        <div class="gleg-row"><span class="dot" style="background:#0284c7"></span> Terre et espace</div>
        <div class="gleg-row"><span class="dot" style="background:#9333ea"></span> Univers technologique</div>
        <div class="gleg-sep"></div>
        <div class="gleg-row"><span class="dot" style="background:#fff;border:2.5px solid #dc2626"></span> Anneau rouge : ≥ 3 méc. ≥ 40 %</div>
        <div class="gleg-row" style="color:var(--muted)">Double-clic : placer au centre</div>`;
    }
  }

  function resizeCanvas() {
    const wrap = els.graphCanvas.parentElement;
    if (!wrap) return;
    const rect = wrap.getBoundingClientRect();
    if (rect.width < 10 || rect.height < 10) return;
    graph.dpr = Math.min(window.devicePixelRatio || 1, 2);
    graph.width = rect.width;
    graph.height = rect.height;
    els.graphCanvas.width = Math.round(rect.width * graph.dpr);
    els.graphCanvas.height = Math.round(rect.height * graph.dpr);
    drawGraph();
  }

  function fitGraphCamera() {
    if (!graph.nodes.length) {
      graph.camX = 0; graph.camY = 0; graph.zoom = 1;
      return;
    }
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const n of graph.nodes) {
      if (n.x - n.radius < minX) minX = n.x - n.radius;
      if (n.x + n.radius > maxX) maxX = n.x + n.radius;
      if (n.y - n.radius < minY) minY = n.y - n.radius;
      if (n.y + n.radius > maxY) maxY = n.y + n.radius;
    }
    const spanX = Math.max(220, maxX - minX + 120);
    const spanY = Math.max(220, maxY - minY + 120);
    graph.camX = (minX + maxX) / 2;
    graph.camY = (minY + maxY) / 2;
    graph.zoom = Math.max(0.35, Math.min(1.25, Math.min(graph.width / spanX, graph.height / spanY)));
  }

  function stepPhysics() {
    const nodes = graph.nodes;
    const edges = graph.edges;
    const nLen = nodes.length;
    if (!nLen) return;

    const repulse = state.graphMode === 'ego' ? 4800 : 6200;
    const damping = 0.82;
    const gravity = state.graphMode === 'ego' ? 0.008 : 0.015;

    // Répulsion entre paires + évitement de collision
    for (let i = 0; i < nLen; i++) {
      const a = nodes[i];
      for (let j = i + 1; j < nLen; j++) {
        const b = nodes[j];
        let dx = b.x - a.x;
        let dy = b.y - a.y;
        let d2 = dx * dx + dy * dy;
        if (d2 < 1) { dx = 0.5; dy = 0.5; d2 = 0.5; }
        const dist = Math.sqrt(d2);
        const minDist = a.radius + b.radius + 16;
        let force = repulse / d2;
        if (dist < minDist) force += (minDist - dist) * 0.45;
        const fx = (dx / dist) * force * graph.alpha;
        const fy = (dy / dist) * force * graph.alpha;
        if (!a.pinned && a !== graph.draggingNode) { a.vx -= fx; a.vy -= fy; }
        if (!b.pinned && b !== graph.draggingNode) { b.vx += fx; b.vy += fy; }
      }
    }

    // Ressorts sur les arêtes
    for (let i = 0; i < edges.length; i++) {
      const e = edges[i];
      const a = e.source;
      const b = e.target;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const k = e.type === 'SYNERGIE' ? 0.018 : (e.type === 'SYNERGIE_GLOBAL' ? 0.015 : 0.045);
      const disp = (dist - e.restLen) * k * graph.alpha;
      const fx = (dx / dist) * disp;
      const fy = (dy / dist) * disp;
      if (!a.pinned && a !== graph.draggingNode) { a.vx += fx; a.vy += fy; }
      if (!b.pinned && b !== graph.draggingNode) { b.vx -= fx; b.vy -= fy; }
    }

    // Gravité douce vers l'origine + intégration
    for (let i = 0; i < nLen; i++) {
      const n = nodes[i];
      if (n.pinned || n === graph.draggingNode) { n.vx = 0; n.vy = 0; continue; }
      n.vx = (n.vx - n.x * gravity * graph.alpha) * damping;
      n.vy = (n.vy - n.y * gravity * graph.alpha) * damping;
      n.x += Math.max(-18, Math.min(18, n.vx));
      n.y += Math.max(-18, Math.min(18, n.vy));
    }

    graph.alpha *= 0.985;
  }

  function drawGraph() {
    const ctx = els.graphCanvas.getContext('2d');
    if (!ctx) return;
    ctx.save();
    ctx.scale(graph.dpr, graph.dpr);
    ctx.clearRect(0, 0, graph.width, graph.height);

    // Transformation caméra
    ctx.translate(graph.width / 2, graph.height / 2);
    ctx.scale(graph.zoom, graph.zoom);
    ctx.translate(-graph.camX, -graph.camY);

    const activeId = state.hoveredNodeId || state.selectedNodeId;

    // 1. Arêtes
    for (let i = 0; i < graph.edges.length; i++) {
      const e = graph.edges[i];
      const isRel = !activeId || e.source.id === activeId || e.target.id === activeId;
      ctx.beginPath();
      ctx.moveTo(e.source.x, e.source.y);
      ctx.lineTo(e.target.x, e.target.y);

      if (e.type === 'DIRECT') {
        ctx.setLineDash([]);
        ctx.strokeStyle = isRel ? 'rgba(220, 38, 38, 0.72)' : 'rgba(148, 163, 184, 0.25)';
        ctx.lineWidth = isRel ? 2.4 : 1.2;
      } else if (e.type === 'PREREQUIS') {
        ctx.setLineDash([7, 5]);
        ctx.strokeStyle = isRel ? 'rgba(217, 119, 6, 0.78)' : 'rgba(148, 163, 184, 0.22)';
        ctx.lineWidth = isRel ? 2.0 : 1.0;
      } else if (e.type === 'CONCEPT_VOISIN') {
        ctx.setLineDash([3, 4]);
        ctx.strokeStyle = isRel ? 'rgba(100, 116, 139, 0.65)' : 'rgba(148, 163, 184, 0.2)';
        ctx.lineWidth = 1.6;
      } else if (e.type === 'SYNERGIE') {
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = isRel ? 'rgba(13, 148, 136, 0.55)' : 'rgba(148, 163, 184, 0.16)';
        ctx.lineWidth = 1.4;
      } else {
        ctx.setLineDash([]);
        ctx.strokeStyle = isRel ? 'rgba(20, 114, 191, 0.48)' : 'rgba(148, 163, 184, 0.14)';
        ctx.lineWidth = Math.min(5, 0.9 + (e.weight || 1) * 0.6);
      }
      ctx.stroke();
    }
    ctx.setLineDash([]);

    // 2. Nœuds
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    for (let i = 0; i < graph.nodes.length; i++) {
      const n = graph.nodes[i];
      const isSelected = n.id === state.selectedNodeId;
      const isHover = n.id === state.hoveredNodeId;

      // Halo pour nœud central ou sélectionné
      if (n.kind === 'pda-center' || isSelected || isHover) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + (isHover ? 8 : 6), 0, Math.PI * 2);
        ctx.fillStyle = n.kind === 'pda-center' ? 'rgba(20, 114, 191, 0.16)' : 'rgba(15, 23, 42, 0.12)';
        ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
      ctx.fillStyle = n.color;
      ctx.fill();

      ctx.lineWidth = (isSelected || isHover) ? 3.5 : (n.kind === 'pda-center' ? 3 : (n.stroke === '#dc2626' ? 2.8 : 1.8));
      ctx.strokeStyle = isSelected ? '#0f172a' : n.stroke;
      ctx.stroke();

      // Étiquettes lisibles
      if (n.kind === 'pda-center') {
        ctx.fillStyle = '#ffffff';
        ctx.font = '800 11px system-ui, sans-serif';
        const shortC = n.label.length > 18 ? n.label.slice(0, 16) + '…' : n.label;
        ctx.fillText(shortC, n.x, n.y - 4);
        ctx.font = '600 9.5px system-ui, sans-serif';
        ctx.fillStyle = '#dbeafe';
        ctx.fillText(`${n.data.mcCount} méc.`, n.x, n.y + 10);
      } else if (n.kind === 'mc') {
        ctx.fillStyle = '#0f172a';
        ctx.font = '700 10.5px system-ui, sans-serif';
        ctx.fillText(n.label, n.x, n.y + n.radius + 11);
      } else {
        // pda-neighbor ou pda-global
        const showLbl = graph.zoom >= 0.62 || n.radius >= 19 || isSelected || isHover;
        if (n.kind === 'pda-global' && n.radius >= 15) {
          ctx.fillStyle = '#ffffff';
          ctx.font = '800 10.5px system-ui, sans-serif';
          ctx.fillText(String(n.filteredMcCount), n.x, n.y);
        }
        if (showLbl) {
          const shortLbl = n.label.length > 26 ? n.label.slice(0, 24) + '…' : n.label;
          ctx.font = '700 10.5px system-ui, sans-serif';
          const tw = ctx.measureText(shortLbl).width;
          ctx.fillStyle = 'rgba(255, 255, 255, 0.86)';
          ctx.fillRect(n.x - tw / 2 - 4, n.y + n.radius + 3, tw + 8, 15);
          ctx.fillStyle = '#0f172a';
          ctx.fillText(shortLbl, n.x, n.y + n.radius + 10.5);
        }
      }
    }

    ctx.restore();
  }

  function startPhysicsLoop() {
    cancelAnimationFrame(graph.rafId);
    const tick = () => {
      if (state.tab !== 'graph') return;
      if (!state.frozen && (graph.alpha > 0.015 || graph.draggingNode)) {
        stepPhysics();
        drawGraph();
        graph.rafId = requestAnimationFrame(tick);
      } else {
        drawGraph();
      }
    };
    graph.rafId = requestAnimationFrame(tick);
  }

  function screenToWorld(clientX, clientY) {
    const rect = els.graphCanvas.getBoundingClientRect();
    const sx = clientX - rect.left;
    const sy = clientY - rect.top;
    return {
      x: (sx - graph.width / 2) / graph.zoom + graph.camX,
      y: (sy - graph.height / 2) / graph.zoom + graph.camY,
      sx, sy
    };
  }

  function hitTestNode(wx, wy) {
    for (let i = graph.nodes.length - 1; i >= 0; i--) {
      const n = graph.nodes[i];
      const dx = wx - n.x;
      const dy = wy - n.y;
      if (dx * dx + dy * dy <= (n.radius + 5) * (n.radius + 5)) return n;
    }
    return null;
  }

  function renderInspector() {
    const node = graph.nodeMap.get(state.selectedNodeId);
    if (!node) {
      els.inspectorContent.innerHTML = `<div class="empty-box"><p>Cliquez sur un nœud du graphe pour afficher sa fiche didactique.</p></div>`;
      return;
    }

    if (node.kind === 'mc') {
      const mc = node.data;
      const lk = node.linkMeta;
      const allPdaLinks = linksByMc.get(mc.code) || [];
      els.inspectorContent.innerHTML = `
        <div class="pda-breadcrumb">
          <span class="mc-code">${escapeHtml(mc.code)}</span>
          <span class="bloom-badge">${escapeHtml(mc.domain)}</span>
        </div>
        <h3 class="insp-title">${escapeHtml(mc.topic)}</h3>
        <div class="mc-row${lk?.type === 'PREREQUIS' ? ' mc-row--prereq' : (lk?.type === 'CONCEPT_VOISIN' ? ' mc-row--voisin' : '')}">
          <div class="mc-row-head">
            <strong>Conception erronée (élève)</strong>
            <span><strong>${escapeHtml(mc.gb || 'n.d.')}</strong></span>
          </div>
          <div>${escapeHtml(mc.text)}</div>
        </div>
        <div class="insp-section">
          <h4>Idée scientifique visée (BSCS)</h4>
          <p style="margin:0;font-size:0.84rem;">${escapeHtml(mc.sci)}</p>
        </div>
        ${lk ? `<div class="insp-section">
          <h4>Justification du lien (${escapeHtml(lk.type)} · ${Math.round(lk.conf * 100)}\u00a0%)</h4>
          <p style="margin:0;font-size:0.84rem;color:var(--muted);">${escapeHtml(lk.j)}</p>
        </div>` : ''}
        <div class="insp-section">
          <h4>Manifestations PDA touchées (${allPdaLinks.length})</h4>
          ${allPdaLinks.map((ol) => {
            const pm = pdaById.get(ol.pda);
            if (!pm) return '';
            return `<button type="button" class="insp-list-btn" data-action="focus-pda-node" data-id="${pm.id}">
              <strong>${escapeHtml(pm.concept)}</strong> <span style="color:var(--muted)">(${escapeHtml(ol.type)})</span><br>
              <span>${escapeHtml(pm.text.slice(0, 110))}${pm.text.length > 110 ? '…' : ''}</span>
            </button>`;
          }).join('')}
        </div>`;
      return;
    }

    // Nœud PDA (center, neighbor ou global)
    const m = node.data;
    const uCls = UNIV_META[m.univ]?.cls || 'u-mat';
    const pLinks = getFilteredLinksForPda(m.id).sort((a, b) => (DATA.misconceptions[b.mc]?.maxP || 0) - (DATA.misconceptions[a.mc]?.maxP || 0));

    els.inspectorContent.innerHTML = `
      <div class="pda-breadcrumb">
        <span class="u-badge ${uCls}">${escapeHtml(m.univ)}</span>
        <span class="bloom-badge">${escapeHtml(m.verb)} · ${escapeHtml(m.bloom)}</span>
        <span class="pda-id-tag">${escapeHtml(m.id)}</span>
      </div>
      <h3 class="insp-title">${escapeHtml(m.concept)}</h3>
      <p style="margin:0;font-size:0.9rem;font-weight:600;">${escapeHtml(m.text)}</p>

      <div class="meq-strip">
        ${m.prog.map((pe) => {
          let cls = 'meq-cell--reut', sym = '■';
          if (pe.s.startsWith('Planifié')) { cls = 'meq-cell--plan'; sym = '→'; }
          else if (pe.s.startsWith('Maîtrisé')) { cls = 'meq-cell--mait'; sym = '★'; }
          return `<span class="meq-cell ${cls}">${escapeHtml(pe.p)} ${sym}</span>`;
        }).join('')}
      </div>

      <div class="insp-actions">
        ${node.kind !== 'pda-center' ? `<button type="button" class="btn-primary-sm" data-action="focus-pda-node" data-id="${m.id}">Placer au centre du graphe</button>` : ''}
        <button type="button" class="btn-outline" style="padding:6px 10px;font-size:0.79rem;" data-action="copy-pda-poe" data-id="${m.id}">Copier fiche POE</button>
      </div>

      <div class="insp-section">
        <h4>Tags PFEQ &amp; Thèmes BSCS</h4>
        <div class="pda-tags">
          ${m.tags.map((t) => `<span class="tag-pill" style="cursor:default">#${escapeHtml(t)}</span>`).join('')}
        </div>
      </div>

      <div class="insp-section">
        <h4>Méconceptions BSCS liées (${pLinks.length})</h4>
        ${pLinks.length ? pLinks.map((lk) => {
          const mc = DATA.misconceptions[lk.mc];
          if (!mc) return '';
          return `<button type="button" class="insp-list-btn" data-action="select-graph-node" data-id="${mc.code}">
            <div style="display:flex;justify-content:space-between;margin-bottom:3px;font-size:0.74rem;">
              <span><span class="mc-code">${escapeHtml(mc.code)}</span> <strong>${escapeHtml(lk.type)}</strong></span>
              <strong style="color:${mc.maxP >= 40 ? 'var(--danger)' : 'var(--secondary)'}">${formatPct(mc.maxP || null)}</strong>
            </div>
            <div>${escapeHtml(mc.text.slice(0, 120))}${mc.text.length > 120 ? '…' : ''}</div>
          </button>`;
        }).join('') : '<p style="margin:0;font-size:0.82rem;color:var(--muted);">Aucune méconception pour les filtres courants.</p>'}
      </div>`;
  }

  function formatPdaPoe(m) {
    const pLinks = (linksByPda.get(m.id) || []).slice().sort((a, b) => (DATA.misconceptions[b.mc]?.maxP || 0) - (DATA.misconceptions[a.mc]?.maxP || 0)).slice(0, 6);
    return [
      `[${m.id}] ${m.univ} — ${m.sec} › ${m.concept}`,
      `Manifestation PDA (${m.bloom}) : ${m.text}`,
      `Progression MEQ : ${m.prog.map((p) => `${p.p} (${p.s})`).join(' | ')}`,
      `Obstacles épistémologiques / Méconceptions BSCS :`,
      ...pLinks.map((lk) => {
        const mc = DATA.misconceptions[lk.mc];
        return `  - [${mc.code} · ${mc.gb || 'n.d.'} · ${lk.type}] ${mc.text}`;
      })
    ].join('\n');
  }

  // ==================== ONGLET 3 : MATRICE DES NŒUDS CRITIQUES ====================
  function renderMatrix() {
    const rows = linkedPdas.filter((m) => {
      if (state.matrixUniv && m.univ !== state.matrixUniv) return false;
      if (state.matrixProg && !m.prog.some((p) => p.p === state.matrixProg)) return false;
      return true;
    }).sort((a, b) => b.highPrevCount - a.highPrevCount || b.mcCount - a.mcCount || b.maxPrev - a.maxPrev);

    const totalHigh = rows.reduce((s, m) => s + m.highPrevCount, 0);
    const totalMc = rows.reduce((s, m) => s + m.mcCount, 0);
    const maxCount = rows[0] ? Math.max(1, rows[0].mcCount) : 1;

    els.matrixStats.innerHTML = `
      <div class="kpi-box"><div class="kpi-lbl">Concepts PDA avec méconceptions</div><div class="kpi-val">${rows.length}</div></div>
      <div class="kpi-box kpi-box--danger"><div class="kpi-lbl">Liens critiques (≥ 40 %)</div><div class="kpi-val">${totalHigh}</div></div>
      <div class="kpi-box"><div class="kpi-lbl">Total des liens BSCS</div><div class="kpi-val">${totalMc}</div></div>
    `;

    els.matrixTableWrap.innerHTML = `
      <table class="matrix-table">
        <thead>
          <tr>
            <th>Univers / Section</th>
            <th>Concept &amp; Manifestation PDA</th>
            <th>Progression MEQ</th>
            <th>Méc. liées</th>
            <th>≥ 40 %</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${rows.slice(0, 80).map((m) => {
            const uCls = UNIV_META[m.univ]?.cls || 'u-mat';
            const pctW = Math.round((100 * m.mcCount) / maxCount);
            const progsShow = state.matrixProg ? m.prog.filter((p) => p.p === state.matrixProg) : m.prog.slice(0, 5);
            return `<tr>
              <td>
                <span class="u-badge ${uCls}">${escapeHtml(m.univ)}</span>
                <div style="font-size:0.78rem;color:var(--muted);margin-top:4px;font-weight:600;">${escapeHtml(m.sec)}</div>
              </td>
              <td>
                <div style="font-weight:700;color:var(--secondary);">${escapeHtml(m.concept)}</div>
                <div style="font-size:0.83rem;">${escapeHtml(m.text)}</div>
              </td>
              <td>
                <div class="meq-strip">
                  ${progsShow.map((pe) => {
                    const cls = pe.s.startsWith('Planifié') ? 'meq-cell--plan' : (pe.s.startsWith('Maîtrisé') ? 'meq-cell--mait' : 'meq-cell--reut');
                    const sym = pe.s.startsWith('Planifié') ? '→' : (pe.s.startsWith('Maîtrisé') ? '★' : '■');
                    return `<span class="meq-cell ${cls}">${escapeHtml(pe.p)} ${sym}</span>`;
                  }).join('')}
                  ${!state.matrixProg && m.prog.length > 5 ? `<span class="pda-id-tag">+${m.prog.length - 5}</span>` : ''}
                </div>
              </td>
              <td style="white-space:nowrap;font-variant-numeric:tabular-nums;">
                <span class="heat-bar"><span class="heat-fill" style="width:${pctW}%;background:${m.highPrevCount ? 'var(--danger)' : 'var(--primary)'}"></span></span>
                <strong>${m.mcCount}</strong>
              </td>
              <td style="font-weight:800;color:${m.highPrevCount ? 'var(--danger)' : 'var(--muted)'};font-variant-numeric:tabular-nums;">${m.highPrevCount}</td>
              <td>
                <button type="button" class="btn-constellation" data-action="open-in-graph" data-id="${m.id}">Constellation</button>
              </td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>`;
  }

  // ==================== GESTION DES ONGLETS & ÉVÉNEMENTS ====================
  function switchTab(tabName) {
    state.tab = tabName;
    document.querySelectorAll('[data-action="switch-tab"]').forEach((btn) => {
      const active = btn.dataset.tab === tabName;
      btn.classList.toggle('is-active', active);
      btn.setAttribute('aria-selected', String(active));
    });
    document.querySelectorAll('.tab-panel').forEach((panel) => {
      const active = panel.id === `tab-${tabName}`;
      panel.hidden = !active;
      panel.classList.toggle('is-active', active);
    });
    if (tabName === 'graph') {
      requestAnimationFrame(() => {
        resizeCanvas();
        if (!graph.nodes.length) buildGraphData();
        else { fitGraphCamera(); drawGraph(); }
      });
    } else if (tabName === 'matrix') {
      renderMatrix();
    }
  }

  function bindCanvasEvents() {
    const cvs = els.graphCanvas;

    cvs.addEventListener('pointerdown', (e) => {
      const pt = screenToWorld(e.clientX, e.clientY);
      const hit = hitTestNode(pt.x, pt.y);
      graph.pointerMoved = false;
      if (hit) {
        graph.draggingNode = hit;
        state.selectedNodeId = hit.id;
        graph.alpha = Math.max(graph.alpha, 0.35);
        renderInspector();
        startPhysicsLoop();
      } else {
        graph.panning = true;
        graph.panStartX = e.clientX;
        graph.panStartY = e.clientY;
        graph.camStartX = graph.camX;
        graph.camStartY = graph.camY;
      }
      cvs.setPointerCapture(e.pointerId);
    }, { signal });

    cvs.addEventListener('pointermove', (e) => {
      const pt = screenToWorld(e.clientX, e.clientY);
      if (graph.draggingNode) {
        graph.pointerMoved = true;
        graph.draggingNode.x = pt.x;
        graph.draggingNode.y = pt.y;
        graph.alpha = Math.max(graph.alpha, 0.25);
        drawGraph();
        return;
      }
      if (graph.panning) {
        graph.pointerMoved = true;
        graph.camX = graph.camStartX - (e.clientX - graph.panStartX) / graph.zoom;
        graph.camY = graph.camStartY - (e.clientY - graph.panStartY) / graph.zoom;
        drawGraph();
        return;
      }

      const hit = hitTestNode(pt.x, pt.y);
      const newHover = hit ? hit.id : null;
      if (newHover !== state.hoveredNodeId) {
        state.hoveredNodeId = newHover;
        cvs.style.cursor = hit ? 'pointer' : 'grab';
        drawGraph();
      }
      if (hit) {
        let html = '';
        if (hit.kind === 'mc') {
          html = `<strong>${escapeHtml(hit.data.code)}</strong> · ${formatPct(hit.data.maxP || null)}<br>${escapeHtml(hit.data.text.slice(0, 150))}${hit.data.text.length > 150 ? '…' : ''}`;
        } else {
          html = `<strong>${escapeHtml(hit.data.concept)}</strong> (${hit.data.mcCount} méc.)<br>${escapeHtml(hit.data.text.slice(0, 140))}${hit.data.text.length > 140 ? '…' : ''}`;
        }
        els.graphTooltip.innerHTML = html;
        els.graphTooltip.style.left = `${Math.min(graph.width - 320, Math.max(10, pt.sx + 14))}px`;
        els.graphTooltip.style.top = `${Math.min(graph.height - 95, Math.max(10, pt.sy + 14))}px`;
        els.graphTooltip.hidden = false;
      } else {
        els.graphTooltip.hidden = true;
      }
    }, { signal });

    const endDrag = () => {
      graph.draggingNode = null;
      graph.panning = false;
    };
    cvs.addEventListener('pointerup', endDrag, { signal });
    cvs.addEventListener('pointercancel', endDrag, { signal });

    cvs.addEventListener('dblclick', (e) => {
      const pt = screenToWorld(e.clientX, e.clientY);
      const hit = hitTestNode(pt.x, pt.y);
      if (hit && hit.kind !== 'mc') {
        state.graphMode = 'ego';
        state.centerPdaId = hit.id;
        syncGraphModeButtons();
        buildGraphData();
      }
    }, { signal });

    cvs.addEventListener('wheel', (e) => {
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.12 : 0.89;
      graph.zoom = Math.max(0.25, Math.min(2.6, graph.zoom * factor));
      drawGraph();
    }, { passive: false, signal });

    window.addEventListener('resize', () => {
      if (state.tab === 'graph') resizeCanvas();
    }, { signal });
  }

  function syncGraphModeButtons() {
    document.querySelectorAll('[data-action="set-graph-mode"]').forEach((btn) => {
      const act = btn.dataset.mode === state.graphMode;
      btn.classList.toggle('is-active', act);
      btn.setAttribute('aria-pressed', String(act));
    });
    els.egoPickerWrap.hidden = state.graphMode !== 'ego';
    els.globalControlsWrap.hidden = state.graphMode !== 'global';
  }

  function bindEvents() {
    let searchTimer = null;
    els.pdaSearch.addEventListener('input', (e) => {
      state.q = e.target.value;
      state.page = 1;
      clearTimeout(searchTimer);
      searchTimer = setTimeout(renderExplorer, 90);
    }, { signal });

    document.addEventListener('change', (e) => {
      const el = e.target;
      const flt = el.dataset?.filter;
      if (flt) {
        state[flt] = el.value;
        if (flt === 'univ') state.sec = '';
        state.page = 1;
        renderExplorer();
        return;
      }
      if (el === els.centerConceptSelect) { state.centerPdaId = el.value; buildGraphData(); }
      else if (el === els.showNeighborsChk) { state.showNeighbors = el.checked; buildGraphData(); }
      else if (el === els.graphLimitSelect) { state.graphLimit = Number(el.value) || 45; buildGraphData(); }
      else if (el === els.graphUnivSelect) { state.graphUniv = el.value; buildGraphData(); }
      else if (el === els.graphProgSelect) { state.graphProg = el.value; buildGraphData(); }
      else if (el === els.graphLinkTypeSelect) { state.graphLinkType = el.value; buildGraphData(); }
      else if (el === els.graphPrevSelect) { state.graphMinPrev = Number(el.value) || 0; buildGraphData(); }
      else if (el === els.matrixProgSelect) { state.matrixProg = el.value; renderMatrix(); }
      else if (el === els.matrixUnivSelect) { state.matrixUniv = el.value; renderMatrix(); }
    }, { signal });

    document.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-action]');
      if (!btn) return;
      const act = btn.dataset.action;

      switch (act) {
        case 'switch-tab':
          switchTab(btn.dataset.tab);
          break;
        case 'set-prog':
          state.prog = btn.dataset.prog || '';
          state.page = 1;
          els.progChips.querySelectorAll('.prog-chip').forEach((c) => c.classList.toggle('is-active', c.dataset.prog === state.prog));
          renderExplorer();
          break;
        case 'toggle-tag':
          state.tag = state.tag === btn.dataset.tag ? '' : btn.dataset.tag;
          state.page = 1;
          renderExplorer();
          break;
        case 'clear-search':
          state.q = '';
          els.pdaSearch.value = '';
          state.page = 1;
          renderExplorer();
          break;
        case 'reset-explorer':
          state.q = ''; state.prog = ''; state.univ = ''; state.sec = '';
          state.type = ''; state.bloom = ''; state.statut = ''; state.mcMode = 'all'; state.tag = ''; state.page = 1;
          els.pdaSearch.value = ''; els.univSelect.value = ''; els.secSelect.value = '';
          els.typeSelect.value = ''; els.bloomSelect.value = ''; els.statutSelect.value = ''; els.mcFilterSelect.value = 'all';
          els.progChips.querySelectorAll('.prog-chip').forEach((c) => c.classList.toggle('is-active', c.dataset.prog === ''));
          renderExplorer();
          break;
        case 'toggle-drawer': {
          const id = btn.dataset.id;
          if (state.openDrawers.has(id)) state.openDrawers.delete(id);
          else state.openDrawers.add(id);
          renderExplorer();
          break;
        }
        case 'pda-page': {
          const p = Number(btn.dataset.page);
          if (p >= 1) { state.page = p; renderExplorer(); window.scrollTo({ top: 0, behavior: 'smooth' }); }
          break;
        }
        case 'export-pda-csv':
          exportFilteredPdaCsv();
          break;
        case 'open-in-graph':
        case 'focus-pda-node':
          state.centerPdaId = btn.dataset.id;
          state.graphMode = 'ego';
          syncGraphModeButtons();
          if (state.tab !== 'graph') switchTab('graph');
          requestAnimationFrame(() => { resizeCanvas(); buildGraphData(); });
          break;
        case 'select-graph-node':
          if (graph.nodeMap.has(btn.dataset.id)) {
            state.selectedNodeId = btn.dataset.id;
            renderInspector();
            drawGraph();
          }
          break;
        case 'set-graph-mode':
          state.graphMode = btn.dataset.mode;
          syncGraphModeButtons();
          buildGraphData();
          break;
        case 'graph-zoom-in':
          graph.zoom = Math.min(2.6, graph.zoom * 1.2);
          drawGraph();
          break;
        case 'graph-zoom-out':
          graph.zoom = Math.max(0.25, graph.zoom * 0.82);
          drawGraph();
          break;
        case 'graph-fit':
          fitGraphCamera();
          drawGraph();
          break;
        case 'graph-freeze':
          state.frozen = !state.frozen;
          els.freezeBtn.classList.toggle('is-active', state.frozen);
          els.freezeBtn.textContent = state.frozen ? '▶' : '⏸';
          if (!state.frozen) { graph.alpha = 0.5; startPhysicsLoop(); }
          break;
        case 'graph-export-png': {
          const a = document.createElement('a');
          a.href = els.graphCanvas.toDataURL('image/png');
          a.download = `constellation_pda_${state.graphMode}.png`;
          a.click();
          showToast('Image PNG de la constellation téléchargée !');
          break;
        }
        case 'copy-pda-poe': {
          const m = pdaById.get(btn.dataset.id);
          if (m) copyText(formatPdaPoe(m));
          break;
        }
        case 'open-legend':
          els.legendModal.showModal();
          break;
        case 'close-legend':
          els.legendModal.close();
          break;
        default:
          break;
      }
    }, { signal });

    els.legendModal.addEventListener('click', (e) => {
      if (e.target === els.legendModal) els.legendModal.close();
    }, { signal });

    bindCanvasEvents();
  }

  function init() {
    initFilterControls();
    bindEvents();
    renderExplorer();
  }

  window.PDA_EXPLORER_APP = {
    dispose() { cancelAnimationFrame(graph.rafId); controller.abort(); },
    getState() { return state; }
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
