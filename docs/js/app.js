/* 구순–김명신 사건 Mechanism Super-DAG — Interactive Temporal DAG
 *
 * 이 스크립트는 data/bundle.js(= data/*.json)에 들어 있는 canonical 값을 그대로 보여 준다.
 * 상태·configuration·공존 판정·개입 결과·후보 등급을 다시 계산하거나 해석하지 않는다.
 * 배치는 Python이 미리 계산한 preset 좌표다(물리 시뮬레이션 없음, node 이동 불가).
 */
(function () {
  'use strict';

  var D = window.GUSUN_DATA;
  if (!D || !window.cytoscape) {
    document.getElementById('cy').textContent = '데이터 또는 라이브러리를 불러오지 못했습니다. docs/data/bundle.js와 docs/vendor/cytoscape/cytoscape.min.js를 확인하세요.';
    return;
  }
  var META = D.meta, SD = D.super_dag, W = D.worlds, IX = D.interactions, IV = D.interventions;
  var CAND = D.candidates, VIEWS = D.views, FACTS = D.facts;

  // ------------------------------------------------------------------ 기본 색인
  var nodeById = {}, edgeById = {};
  SD.nodes.forEach(function (n) { nodeById[n.id] = n; });
  SD.edges.forEach(function (e) { edgeById[e.id] = e; });
  var MECHS = W.mechanisms.slice();
  var BACKBONE = toSet(W.backbone);
  var STATUS_KEYS = ['OBSERVED', 'DERIVED', 'LATENT', 'CONTEXT', 'UNRESOLVED'];
  var COLORS = {
    OBSERVED: '#256abf', DERIVED: '#8ea0bd', LATENT: '#c4501f', CONTEXT: '#008300', UNRESOLVED: '#b83a6b',
    MECH: '#4a3aa7'
  };
  var SIZE = {
    OBSERVED_EVENT: [144, 56], MECHANISM: [204, 50], STRUCTURAL_VARIABLE: [188, 40], CANDIDATE_BRIDGE: [150, 52],
    INSTITUTIONAL_CONTEXT: [136, 38], ENV_CONTEXT: [180, 44], UNRESOLVED_ITEM: [214, 48]
  };
  var DEFAULT_STATE = function () {
    return { view: 'overview', world: 'ALL', hideOthers: false, status: toSet(STATUS_KEYS), mech: toSet(MECHS), iv: null, pair: ['M1', 'M2'] };
  };
  var state = DEFAULT_STATE();

  function toSet(a) { var s = {}; (a || []).forEach(function (x) { s[x] = true; }); return s; }
  function has(s, k) { return Object.prototype.hasOwnProperty.call(s, k) && s[k]; }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function splitIds(s) { return String(s || '').split('|').map(function (x) { return x.trim(); }).filter(Boolean); }
  function $(id) { return document.getElementById(id); }

  // ------------------------------------------------------------------ 머리글
  $('app-title').textContent = META.title;
  $('app-desc').textContent = META.description;
  document.title = '구순–김명신 Super-DAG';
  $('meta-strip').innerHTML =
    '<span>node <b>' + META.counts.nodes + '</b></span>' +
    '<span>edge <b>' + META.counts.edges + '</b></span>' +
    '<span>LATENT 후보 <b>' + META.counts.candidates + '</b></span>' +
    '<span>world <b>' + META.counts.worlds + '</b></span>' +
    '<span>frozen <code>' + esc(META.frozen_hash_prefix) + '</code></span>';
  $('foot-note').textContent = META.role_note + ' 좌표 규칙: ' + META.layout_rule;

  // ------------------------------------------------------------------ cytoscape 요소
  function nodeLabel(n) { return n.short_label; }
  var elements = [];
  SD.nodes.forEach(function (n) {
    var t = n.canonical.node_type, sz = SIZE[t] || [150, 48];
    elements.push({
      group: 'nodes',
      data: {
        id: n.id, label: nodeLabel(n), base: nodeLabel(n), ntype: t, sgroup: n.status_group, status: n.canonical.sd_status,
        mech: (t === 'MECHANISM' ? n.id : (t === 'CANDIDATE_BRIDGE' ? n.canonical.mechanism : '')),
        w: sz[0], h: sz[1], tw: sz[0] - 12, outcome: n.common_outcome ? 1 : 0, excluded: n.analysis_excluded ? 1 : 0
      },
      position: { x: n.layout.x, y: n.layout.y },
      classes: [t, n.common_outcome ? 'outcome' : '', n.analysis_excluded ? 'excluded' : ''].join(' ').trim()
    });
  });
  SD.edges.forEach(function (e) {
    var c = e.canonical;
    elements.push({
      group: 'edges',
      data: { id: e.id, source: c.src, target: c.dst, etype: c.edge_type, sgroup: e.status_group, origin: c.origin },
      classes: ['et-' + c.edge_type, 'eo-' + c.origin, 'es-' + e.status_group].join(' ')
    });
  });

  var DASH = { solid: 'solid', dashed: 'dashed', dotted: 'dotted' };
  var style = [
    { selector: 'node', style: {
      'label': 'data(label)', 'text-wrap': 'wrap', 'text-max-width': 'data(tw)', 'font-size': 11,
      'font-family': 'system-ui, -apple-system, "Segoe UI", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif',
      'text-valign': 'center', 'text-halign': 'center', 'width': 'data(w)', 'height': 'data(h)',
      'shape': 'round-rectangle', 'background-color': '#ffffff', 'border-width': 1.5, 'border-color': '#898781',
      'color': '#0b0b0b', 'min-zoomed-font-size': 4, 'transition-property': 'opacity', 'transition-duration': 120
    } },
    { selector: 'node.OBSERVED_EVENT', style: { 'background-color': '#eaf2fc', 'border-color': '#256abf', 'border-width': 2, 'border-style': 'solid' } },
    { selector: 'node.outcome', style: { 'border-style': 'double', 'border-width': 5, 'border-color': '#1c5cab' } },
    { selector: 'node.MECHANISM', style: { 'shape': 'hexagon', 'background-color': '#efedfa', 'border-color': '#4a3aa7', 'border-style': 'dashed', 'border-width': 2.5, 'font-weight': 700, 'font-size': 12 } },
    { selector: 'node.STRUCTURAL_VARIABLE', style: { 'shape': 'cut-rectangle', 'background-color': '#f6f4fd', 'border-color': '#4a3aa7', 'border-style': 'dashed', 'border-width': 1.5, 'font-size': 10.5 } },
    { selector: 'node.CANDIDATE_BRIDGE', style: { 'background-color': '#fdf1ea', 'border-color': '#c4501f', 'border-style': 'dashed', 'border-width': 1.8, 'font-size': 10.5 } },
    { selector: 'node.CANDIDATE_BRIDGE.excluded', style: { 'background-color': '#f5f4f1', 'border-style': 'dotted', 'color': '#52514e' } },
    { selector: 'node.INSTITUTIONAL_CONTEXT', style: { 'shape': 'rectangle', 'background-color': '#eef6ee', 'border-color': '#008300', 'border-style': 'dotted', 'border-width': 2, 'font-size': 10 } },
    { selector: 'node.ENV_CONTEXT', style: { 'shape': 'barrel', 'background-color': '#eef6ee', 'border-color': '#008300', 'border-style': 'dotted', 'border-width': 2.2, 'font-size': 10.5 } },
    { selector: 'node.UNRESOLVED_ITEM', style: { 'shape': 'octagon', 'background-color': '#fcf0f5', 'border-color': '#b83a6b', 'border-style': 'double', 'border-width': 4, 'font-size': 10.5 } },
    // 축소 시 ID만 크게
    { selector: 'node.far', style: { 'label': 'data(id)', 'font-size': 24, 'font-weight': 700, 'text-overflow-wrap': 'anywhere' } },
    { selector: 'node.far.STRUCTURAL_VARIABLE, node.far.UNRESOLVED_ITEM, node.far.INSTITUTIONAL_CONTEXT', style: { 'font-size': 15 } },
    { selector: 'edge', style: {
      'curve-style': 'bezier', 'width': 1.3, 'line-color': '#898781', 'target-arrow-color': '#898781', 'target-arrow-shape': 'triangle',
      'arrow-scale': 0.8, 'opacity': 0.8, 'font-size': 10, 'text-background-color': '#ffffff', 'text-background-opacity': 0.9,
      'text-background-padding': 2, 'text-rotation': 'autorotate', 'color': '#0b0b0b'
    } },
    { selector: 'edge.eo-SUPER_DAG', style: { 'opacity': 0.5, 'width': 1.1 } },
    { selector: 'edge.es-DERIVED', style: { 'width': 1.7 } },
    { selector: 'edge.es-OBSERVED', style: { 'width': 3.2 } }
  ];
  Object.keys(META.edge_styles).forEach(function (t) {
    var s = META.edge_styles[t];
    style.push({ selector: 'edge.et-' + t, style: { 'line-color': s.color, 'target-arrow-color': s.color, 'target-arrow-shape': s.arrow, 'line-style': DASH[s.line] || 'solid' } });
  });
  style = style.concat([
    { selector: '.dim', style: { 'opacity': 0.16 } },
    { selector: 'edge.dim', style: { 'opacity': 0.06 } },
    { selector: '.hidden', style: { 'display': 'none' } },
    { selector: 'node.hl', style: { 'underlay-color': '#eda100', 'underlay-opacity': 0.38, 'underlay-padding': 7, 'underlay-shape': 'round-rectangle' } },
    { selector: 'node.hl-rej', style: { 'underlay-color': '#d03b3b', 'underlay-opacity': 0.30, 'underlay-padding': 7, 'border-color': '#d03b3b', 'border-style': 'dashed' } },
    { selector: 'node.cfg-UNSPECIFIED', style: { 'background-color': '#f3f3f1', 'border-color': '#898781', 'border-style': 'dotted', 'color': '#52514e' } },
    { selector: 'node.cfg-PARTIAL', style: { 'border-style': 'dashed', 'border-width': 3 } },
    { selector: 'node.cfg-ON', style: { 'border-style': 'solid', 'border-width': 4 } },
    { selector: 'node.focus', style: { 'underlay-color': '#4a3aa7', 'underlay-opacity': 0.22, 'underlay-padding': 9 } },
    { selector: 'node.grpA', style: { 'underlay-color': '#008300', 'underlay-opacity': 0.28, 'underlay-padding': 8 } },
    { selector: 'node.grpB', style: { 'underlay-color': '#eb6834', 'underlay-opacity': 0.30, 'underlay-padding': 8 } },
    { selector: 'node.anchor', style: { 'underlay-color': '#52514e', 'underlay-opacity': 0.14, 'underlay-padding': 8 } },
    { selector: 'node.pair', style: { 'underlay-color': '#2a78d6', 'underlay-opacity': 0.30, 'underlay-padding': 9 } },
    { selector: 'node.iv-off', style: { 'background-color': '#e9e8e4', 'border-color': '#52514e', 'border-style': 'solid', 'border-width': 3, 'color': '#52514e' } },
    { selector: 'node.iv-removed', style: { 'opacity': 0.45, 'border-color': '#d03b3b', 'border-style': 'dashed', 'border-width': 3 } },
    { selector: 'node.iv-remaining', style: { 'underlay-color': '#0ca30c', 'underlay-opacity': 0.32, 'underlay-padding': 7 } },
    { selector: 'node.iv-PATH_BREAKS', style: { 'underlay-color': '#d03b3b', 'underlay-opacity': 0.35, 'underlay-padding': 9 } },
    { selector: 'node.iv-PATH_WEAKENS', style: { 'underlay-color': '#fab219', 'underlay-opacity': 0.5, 'underlay-padding': 9 } },
    { selector: 'node.iv-PATH_REMAINS', style: { 'underlay-color': '#0ca30c', 'underlay-opacity': 0.35, 'underlay-padding': 9 } },
    { selector: 'node.iv-UNKNOWN', style: { 'underlay-color': '#898781', 'underlay-opacity': 0.35, 'underlay-padding': 9 } },
    { selector: 'node.iv-target', style: { 'underlay-color': '#2a78d6', 'underlay-opacity': 0.30, 'underlay-padding': 9 } },
    { selector: 'edge.iv-path', style: { 'opacity': 1, 'width': 3, 'z-index': 9 } },
    { selector: 'node.search-hit', style: { 'underlay-color': '#2a78d6', 'underlay-opacity': 0.45, 'underlay-padding': 12 } },
    { selector: 'edge.hover, edge:selected', style: { 'label': 'data(etype)', 'opacity': 1, 'width': 3, 'z-index': 20 } },
    { selector: 'node:selected', style: { 'border-color': '#0b0b0b', 'border-width': 4, 'border-style': 'solid' } }
  ]);

  var cy = window.cytoscape({
    container: $('cy'), elements: elements, style: style, layout: { name: 'preset', fit: false },
    autoungrabify: true, autounselectify: false, boxSelectionEnabled: false, selectionType: 'single',
    minZoom: 0.06, maxZoom: 2.6, pixelRatio: 'auto'
  });

  // ------------------------------------------------------------------ 배경(시간 구간·lane)
  var SVGNS = 'http://www.w3.org/2000/svg';
  var overlay = $('overlay');
  var g = document.createElementNS(SVGNS, 'g');
  overlay.appendChild(g);
  var bb = (function () {
    var x0 = Infinity, x1 = -Infinity;
    SD.nodes.forEach(function (n) {
      var w = (SIZE[n.canonical.node_type] || [150])[0] / 2;
      x0 = Math.min(x0, n.layout.x - w); x1 = Math.max(x1, n.layout.x + w);
    });
    return { x0: x0 - 30, x1: x1 + 30 };
  })();
  var LABEL_W = 250;
  function svgEl(tag, attrs, text) {
    var el = document.createElementNS(SVGNS, tag);
    Object.keys(attrs).forEach(function (k) { el.setAttribute(k, attrs[k]); });
    if (text != null) el.textContent = text;
    return el;
  }
  (function drawOverlay() {
    var defs = svgEl('defs', {});
    var pat = svgEl('pattern', { id: 'hatch', width: 10, height: 10, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' });
    pat.appendChild(svgEl('line', { x1: 0, y1: 0, x2: 0, y2: 10, stroke: '#e1e0d9', 'stroke-width': 3 }));
    defs.appendChild(pat);
    g.appendChild(defs);
    var kindFill = { context: '#f2f7f1', latent: '#fbf6f2', unresolved: '#fbf2f6', observed: '#fcfcfb' };
    SD.lanes.forEach(function (l, i) {
      g.appendChild(svgEl('rect', { x: bb.x0 - LABEL_W, y: l.y0, width: bb.x1 - bb.x0 + LABEL_W, height: l.y1 - l.y0,
        fill: l.kind === 'observed' ? (i % 2 ? '#fcfcfb' : '#f8f8f5') : kindFill[l.kind] }));
      g.appendChild(svgEl('line', { x1: bb.x0 - LABEL_W, x2: bb.x1, y1: l.y1, y2: l.y1, stroke: '#e1e0d9', 'stroke-width': 1 }));
    });
    SD.bands.forEach(function (b, i) {
      g.appendChild(svgEl('rect', { x: b.x0, y: b.y0, width: b.x1 - b.x0, height: b.y1 - b.y0,
        fill: b.dated ? (i % 2 ? 'rgba(42,120,214,0.045)' : 'rgba(42,120,214,0.085)') : 'url(#hatch)', stroke: b.dated ? 'rgba(42,120,214,0.25)' : '#c3c2b7',
        'stroke-dasharray': b.dated ? '' : '6 4', rx: 6 }));
      g.appendChild(svgEl('text', { x: b.x0 + 10, y: b.y0 + 24, 'font-size': 20, 'font-weight': 700, fill: '#1c5cab' }, b.label));
      g.appendChild(svgEl('text', { x: b.x0 + 10, y: b.y0 + 44, 'font-size': 12.5, fill: '#52514e' }, b.sub));
    });
    var obsTop = Math.min.apply(null, SD.bands.map(function (b) { return b.y0; }));
    SD.ticks.forEach(function (t) {
      g.appendChild(svgEl('text', { x: t.x, y: obsTop + 64, 'font-size': 12, 'font-weight': 600, fill: '#52514e', 'text-anchor': 'middle' }, t.label));
    });
    // 시간 화살표
    var dated = SD.bands.filter(function (b) { return b.dated; });
    if (dated.length) {
      var ax0 = dated[0].x0, ax1 = dated[dated.length - 1].x1, ay = obsTop - 12;
      g.appendChild(svgEl('line', { x1: ax0, x2: ax1 - 6, y1: ay, y2: ay, stroke: '#898781', 'stroke-width': 2 }));
      g.appendChild(svgEl('path', { d: 'M' + ax1 + ' ' + ay + ' l-12 -6 l0 12 z', fill: '#898781' }));
      g.appendChild(svgEl('text', { x: ax0, y: ay - 8, 'font-size': 13, fill: '#52514e' }, '시간 → (관측 사건만 날짜 순서로 배치)'));
    }
    SD.lanes.forEach(function (l) {
      var y = (l.y0 + l.y1) / 2;
      g.appendChild(svgEl('text', { x: bb.x0 - LABEL_W + 12, y: y - 2, 'font-size': 15, 'font-weight': 700,
        fill: { observed: '#1c5cab', latent: '#8a3a12', context: '#0b5e0b', unresolved: '#8f2a52' }[l.kind] }, l.label));
      g.appendChild(svgEl('text', { x: bb.x0 - LABEL_W + 12, y: y + 16, 'font-size': 11, fill: '#6f6d68' }, l.sub));
    });
  })();
  function syncOverlay() {
    var p = cy.pan(), z = cy.zoom();
    g.setAttribute('transform', 'translate(' + p.x + ' ' + p.y + ') scale(' + z + ')');
    var far = z < 0.42;
    if (far !== syncOverlay.far) {
      syncOverlay.far = far;
      cy.batch(function () { cy.nodes().toggleClass('far', far); });
    }
  }
  cy.on('viewport', syncOverlay);

  function fitTo(eles, pad) {
    pad = pad == null ? 30 : pad;
    var box = (eles && eles.length ? eles : cy.elements()).boundingBox({ includeLabels: false });
    var x1 = box.x1 - LABEL_W, x2 = box.x2, y1 = box.y1 - 70, y2 = box.y2;
    var wv = cy.width(), hv = cy.height();
    var z = Math.min((wv - 2 * pad) / (x2 - x1), (hv - 2 * pad) / (y2 - y1));
    z = Math.max(cy.minZoom(), Math.min(1.4, z));
    cy.viewport({ zoom: z, pan: { x: (wv - z * (x1 + x2)) / 2, y: (hv - z * (y1 + y2)) / 2 } });
    syncOverlay();
  }

  // ------------------------------------------------------------------ 상태 적용(보이기·흐리기·강조)
  var CLASS_RESET = 'hidden dim hl hl-rej focus grpA grpB anchor pair iv-off iv-removed iv-remaining iv-PATH_BREAKS iv-PATH_WEAKENS iv-PATH_REMAINS iv-UNKNOWN iv-target iv-path cfg-ON cfg-PARTIAL cfg-UNSPECIFIED cfg-OFF';
  function ivRows() { return state.iv ? IV.rows.filter(function (r) { return r.canonical.mechanism === state.iv; }) : []; }

  function applyState() {
    var sel = W.selections[state.world];
    var view = VIEWS.views[state.view];
    var inView = toSet(view.nodes);
    var always = toSet(sel.always_visible);
    var dimW = toSet(sel.dim), hideW = toSet(sel.hideable), hlW = toSet(sel.highlight);
    var rows = ivRows();
    var ivPath = {};
    rows.forEach(function (r) { r.path_nodes.forEach(function (x) { ivPath[x] = true; }); });
    cy.batch(function () {
      cy.elements().removeClass(CLASS_RESET);
      cy.nodes().forEach(function (n) {
        var d = n.data(), id = d.id, hide = false, dim = false;
        if (!has(state.status, d.sgroup)) hide = true;
        if (d.mech && !has(state.mech, d.mech)) hide = true;
        if (!has(inView, id)) { if (d.sgroup === 'OBSERVED') dim = true; else if (!has(ivPath, id)) hide = true; }
        if (has(dimW, id)) { if (state.hideOthers && has(hideW, id)) hide = true; else dim = true; }
        // AUDIT5:BACKBONE_GUARD — OBSERVED backbone(관측 사건·공통 결말)은 어떤 선택·필터·view·개입에서도 숨기지 않는다
        if (BACKBONE[id] || has(always, id)) hide = false;
        if (hide) n.addClass('hidden');
        else if (dim) n.addClass('dim');
        if (has(hlW, id)) n.addClass(sel.rejected ? 'hl-rej' : 'hl');
        var label = d.base;
        if (d.ntype === 'MECHANISM' && state.world !== 'ALL') {
          var v = sel.mechanism_state[id];
          n.addClass('cfg-' + v);
          label = d.base + '\n[' + state.world + ': ' + W.config_display[v].label + ']';
        }
        if (state.iv && id === state.iv) label = d.base + '\ndo(' + id + '=OFF) · 설명 모델에서 제거';
        n.data('label', label);
      });
      (view.emphasis || []).forEach(function (id) { cy.getElementById(id).addClass('focus'); });
      if (view.groups) {
        view.groups.A.forEach(function (id) { cy.getElementById(id).addClass('grpA'); });
        view.groups.B.forEach(function (id) { cy.getElementById(id).addClass('grpB'); });
        view.groups.anchor.forEach(function (id) { cy.getElementById(id).addClass('anchor'); });
      }
      rows.forEach(function (r) {
        var c = r.canonical;
        cy.getElementById(c.mechanism).addClass('iv-off');
        splitIds(c.removed).forEach(function (id) { cy.getElementById(id).addClass('iv-removed'); });
        splitIds(c.remaining).forEach(function (id) { cy.getElementById(id).addClass('iv-remaining'); });
        cy.getElementById(c.variable).addClass('iv-' + c.result);
        splitIds(c.target).forEach(function (id) { cy.getElementById(id).addClass('iv-target'); });
      });
      cy.edges().forEach(function (e) {
        var d = e.data(), s = e.source(), t = e.target();
        var hide = s.hasClass('hidden') || t.hasClass('hidden') || (!has(state.status, d.sgroup) && d.sgroup !== 'OBSERVED');
        if (hide) { e.addClass('hidden'); return; }
        if (rows.length && ivPath[d.source] && ivPath[d.target]) e.addClass('iv-path');
        else if (s.hasClass('dim') || t.hasClass('dim') || (rows.length && d.origin === 'SUPER_DAG')) e.addClass('dim');
      });
      if (state.pairOn) { cy.getElementById(state.pair[0]).addClass('pair'); cy.getElementById(state.pair[1]).addClass('pair'); }
    });
    renderBanners();
    renderWorldButtons();
    renderTabs();
    renderWorldPanel();
    renderIvPanel();
  }

  // ------------------------------------------------------------------ 배너·탭
  function renderBanners() {
    var sel = W.selections[state.world];
    var b = $('banner-world');
    if (sel.rejected) { b.hidden = false; b.innerHTML = '<b>' + esc(state.world) + ' REJECTED</b> — ' + esc(sel.banner); }
    else { b.hidden = true; b.innerHTML = ''; }
    var iv = $('banner-iv');
    if (state.iv) {
      iv.hidden = false;
      iv.innerHTML = '<b>do(' + esc(state.iv) + '=OFF)</b> — ' + esc(IV.note) +
        ' 붉은 점선 = 사라지는 후보, 초록 = 남는 후보, 구조 변수 색 = 저장된 결과.';
    } else { iv.hidden = true; iv.innerHTML = ''; }
    var v = VIEWS.views[state.view];
    $('view-desc').innerHTML = '<b>' + esc(v.title) + '</b> · ' + esc(v.desc) +
      (v.cross_edges ? ' <span class="chip flag">A↔B 직접 edge ' + v.cross_edges.length + '개</span>' : '');
  }
  function renderTabs() {
    var nav = $('view-tabs');
    if (!nav.childElementCount) {
      VIEWS.order.forEach(function (id) {
        var b = document.createElement('button');
        b.type = 'button'; b.setAttribute('role', 'tab'); b.dataset.view = id; b.textContent = VIEWS.views[id].label;
        b.addEventListener('click', function () { setView(id); });
        nav.appendChild(b);
      });
    }
    Array.prototype.forEach.call(nav.children, function (b) { b.setAttribute('aria-selected', String(b.dataset.view === state.view)); });
  }
  function renderWorldButtons() {
    var box = $('world-buttons');
    if (!box.childElementCount) {
      ['ALL'].concat(W.order).forEach(function (wid) {
        var s = W.selections[wid];
        var b = document.createElement('button');
        b.type = 'button'; b.setAttribute('role', 'radio'); b.dataset.world = wid; b.textContent = s.label;
        if (s.rejected) { b.className = 'rejected'; b.title = '검토했지만 배제된 설명(REJECTED). 경쟁 설명이 아님'; }
        b.addEventListener('click', function () { setWorld(wid); });
        box.appendChild(b);
      });
    }
    Array.prototype.forEach.call(box.children, function (b) { b.setAttribute('aria-checked', String(b.dataset.world === state.world)); });
  }

  // ------------------------------------------------------------------ 필터 UI
  (function buildFilters() {
    var box = $('status-filters');
    var notes = {
      OBSERVED: '고정 backbone — 숨기지 않음', DERIVED: 'edge 상태(관측 node 사이 기록 근거 연결). edge에만 적용',
      LATENT: '메커니즘·구조 변수·후보 (LATENT_MECHANISM)', CONTEXT: '제도·환경 context (사건 아님)', UNRESOLVED: '확정하지 않은 항목'
    };
    STATUS_KEYS.forEach(function (k) {
      var lab = document.createElement('label');
      var locked = k === 'OBSERVED';
      lab.className = locked ? 'disabled' : '';
      lab.innerHTML = '<input type="checkbox" data-status="' + k + '" checked' + (locked ? ' disabled' : '') + '>' +
        '<span class="sw" style="background:' + COLORS[k] + '"></span><span>' + k + ' <span class="note">' + esc(notes[k]) + '</span></span>';
      lab.querySelector('input').addEventListener('change', function (ev) {
        if (ev.target.checked) state.status[k] = true; else delete state.status[k];
        applyState();
      });
      box.appendChild(lab);
    });
    var mb = $('mech-filters');
    MECHS.forEach(function (m) {
      var lab = document.createElement('label');
      lab.innerHTML = '<input type="checkbox" data-mech="' + m + '" checked><span class="sw" style="background:#efedfa;border:1.5px dashed #4a3aa7"></span>' +
        '<span><b>' + m + '</b> ' + esc(META.mechanism_display[m]) + '</span>';
      lab.querySelector('input').addEventListener('change', function (ev) {
        if (ev.target.checked) state.mech[m] = true; else delete state.mech[m];
        applyState();
      });
      mb.appendChild(lab);
    });
    $('hide-others').addEventListener('change', function (ev) { state.hideOthers = ev.target.checked; applyState(); });
  })();
  function syncFilterInputs() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-status]'), function (i) { i.checked = !!has(state.status, i.dataset.status); });
    Array.prototype.forEach.call(document.querySelectorAll('[data-mech]'), function (i) { i.checked = !!has(state.mech, i.dataset.mech); });
    $('hide-others').checked = state.hideOthers;
  }

  // ------------------------------------------------------------------ 범례
  (function buildLegend() {
    var nodesL = [
      ['OBSERVED 관측 사건', '#eaf2fc', '#256abf', '', 'rect'], ['공통 결말 (모든 world)', '#eaf2fc', '#1c5cab', '', 'double'],
      ['메커니즘 (LATENT)', '#efedfa', '#4a3aa7', '5 3', 'hex'], ['구조 변수 V_* (LATENT)', '#f6f4fd', '#4a3aa7', '5 3', 'cut'],
      ['LATENT 후보 bridge', '#fdf1ea', '#c4501f', '5 3', 'rect'], ['분석 제외 후보(대조·INCOMPATIBLE)', '#f5f4f1', '#c4501f', '1 3', 'rect'],
      ['제도 context', '#eef6ee', '#008300', '1 3', 'sq'], ['환경 context', '#eef6ee', '#008300', '1 3', 'barrel'],
      ['UNRESOLVED', '#fcf0f5', '#b83a6b', '', 'oct']
    ];
    var h = '<div class="grp">Node (색 + 모양 + 테두리)</div>';
    nodesL.forEach(function (r) {
      var shape;
      if (r[4] === 'hex') shape = '<polygon points="6,1 26,1 31,8 26,15 6,15 1,8" ';
      else if (r[4] === 'oct') shape = '<polygon points="7,1 25,1 31,6 31,10 25,15 7,15 1,10 1,6" ';
      else if (r[4] === 'cut') shape = '<polygon points="5,1 27,1 31,5 31,11 27,15 5,15 1,11 1,5" ';
      else if (r[4] === 'barrel') shape = '<rect x="1" y="1" width="30" height="14" rx="9" ry="7" ';
      else if (r[4] === 'sq') shape = '<rect x="1" y="1" width="30" height="14" ';
      else shape = '<rect x="1" y="1" width="30" height="14" rx="4" ';
      var extra = r[4] === 'double' ? '<rect x="4" y="4" width="24" height="8" rx="2" fill="none" stroke="' + r[2] + '" stroke-width="1.2"/>' : '';
      h += '<div class="row"><svg width="32" height="16">' + shape + 'fill="' + r[1] + '" stroke="' + r[2] + '" stroke-width="' + (r[4] === 'double' ? 1.2 : 1.8) + '" stroke-dasharray="' + r[3] + '"/>' + extra + '</svg>' + esc(r[0]) + '</div>';
    });
    h += '<div class="row muted">강조: <span style="background:rgba(237,161,0,.4);padding:0 4px;border-radius:3px">world 사용</span> <span style="background:rgba(208,59,59,.3);padding:0 4px;border-radius:3px">W6 배제</span></div>';
    $('legend-nodes').innerHTML = h;
    var groups = {};
    Object.keys(META.edge_styles).forEach(function (t) {
      var s = META.edge_styles[t];
      (groups[s.group] = groups[s.group] || []).push([t, s]);
    });
    var eh = '';
    Object.keys(groups).sort().forEach(function (gname) {
      eh += '<div class="grp">Edge — ' + esc(gname) + '</div>';
      groups[gname].forEach(function (p) {
        var s = p[1], da = s.line === 'dashed' ? '6 3' : (s.line === 'dotted' ? '1.5 3' : '');
        eh += '<div class="row" title="' + esc(s.ko) + '"><svg width="32" height="10"><line x1="1" y1="5" x2="25" y2="5" stroke="' + s.color + '" stroke-width="2" stroke-dasharray="' + da + '"/>' +
          '<path d="M31 5 l-6 -4 l0 8 z" fill="' + s.color + '"/></svg><span><code>' + esc(p[0]) + '</code> <span class="muted">' + esc(s.ko) + '</span></span></div>';
      });
    });
    eh += '<div class="row muted">선 굵기: OBSERVED edge 굵게, DERIVED edge 보통, 분석 edge 얇고 옅게</div>';
    $('legend-edges').innerHTML = eh;
  })();

  // ------------------------------------------------------------------ 상세 패널
  function kv(rows) {
    return '<table class="kv">' + rows.filter(function (r) { return r && r[1] !== undefined && r[1] !== null && r[1] !== ''; }).map(function (r) {
      return '<tr><th>' + esc(r[0]) + '</th><td>' + (r[2] ? r[1] : esc(r[1])) + '</td></tr>';
    }).join('') + '</table>';
  }
  function chip(cls, text) { return '<span class="chip ' + cls + '">' + esc(text) + '</span>'; }
  function nodeLink(id) {
    if (!nodeById[id]) return esc(id);
    return '<button type="button" class="linkish" data-goto="' + esc(id) + '">' + esc(id) + '</button>';
  }
  function edgeLink(id) { return '<button type="button" class="linkish" data-goto-edge="' + esc(id) + '">' + esc(id) + '</button>'; }
  function idsLinks(s) { return splitIds(s).map(nodeLink).join(', '); }
  function relatedMechHtml(n) {
    var rm = n.related_mechanisms || {};
    var ks = Object.keys(rm);
    if (!ks.length) return '<span class="muted">canonical edge로 연결된 mechanism 없음</span>';
    return ks.map(function (m) {
      return '<div>' + nodeLink(m) + ' ' + esc(META.mechanism_display[m] || '') + ' <span class="muted">via ' + rm[m].map(edgeLink).join(' → ') + '</span></div>';
    }).join('');
  }
  function incidentEdgesHtml(id) {
    var ins = [], outs = [];
    SD.edges.forEach(function (e) {
      if (e.canonical.dst === id) ins.push(e);
      if (e.canonical.src === id) outs.push(e);
    });
    function li(e, other) { return '<li>' + edgeLink(e.id) + ' <code>' + esc(e.canonical.edge_type) + '</code> ' + nodeLink(other) + ' ' + chip('st-' + e.status_group, e.canonical.sd_status) + '</li>'; }
    return '<h4>들어오는 edge (' + ins.length + ')</h4><ul class="plain">' + (ins.map(function (e) { return li(e, e.canonical.src); }).join('') || '<li class="muted">없음</li>') + '</ul>' +
      '<h4>나가는 edge (' + outs.length + ')</h4><ul class="plain">' + (outs.map(function (e) { return li(e, e.canonical.dst); }).join('') || '<li class="muted">없음</li>') + '</ul>';
  }
  function worldsOfNode(n) { return n.canonical.worlds; }

  function renderNodeDetail(id) {
    var n = nodeById[id];
    if (!n) return;
    var c = n.canonical, t = c.node_type, h = '';
    h += '<h3>' + esc(id) + ' · ' + esc(c.label) + '</h3>';
    h += '<p>' + chip('st-' + n.status_group, c.sd_status) + ' ' + chip('flag', c.node_type) +
      (c.worlds === 'ALL (공통)' ? ' ' + chip('flag flag-common', '모든 world 공통') : '') +
      (n.common_outcome ? ' ' + chip('flag flag-common', '공통 결말') : '') + '</p>';
    if (t === 'OBSERVED_EVENT') {
      var o = n.observed;
      h += kv([['node_id', id], ['label', c.label], ['status', c.sd_status + ' (frozen: ' + c.frozen_status + ')'],
        ['날짜(발생)', o.occurrence_text], ['t_min – t_max', (o.t_min || '?') + ' – ' + (o.t_max || '?') + (n.layout.dated ? '' : ' · 날짜 미기록(시간 축 밖)')],
        ['기록일', o.record_lunar_date], ['층(layer)', o.layer], ['branch lane', o.branch], ['인식 floor', o.epistemic_floor],
        ['진술/기록 주체', o.attesting_actor], ['worlds', worldsOfNode(n)]]);
      h += '<h4>사료 수준 요약 (episode summary)</h4><div class="quote">' + esc(o.summary) + '</div>';
      if (o.caution) h += '<p class="muted small">주의: ' + esc(o.caution) + '</p>';
      h += '<h4>Confirmed fact (' + splitIds(o.member_fact_ids).length + ')</h4><ul class="plain">';
      splitIds(o.member_fact_ids).forEach(function (f) {
        var cf = FACTS.confirmed_facts[f] || {};
        h += '<li><b>' + esc(f) + '</b> <span class="muted">' + esc(cf.confirmation_level || '') + '</span><br>' + esc(cf.confirmed_statement || '') + '</li>';
      });
      h += '</ul>';
      if (o.member_clauses) h += '<p class="small muted">사용한 절: ' + esc(o.member_clauses) + '</p>';
      h += '<h4>Source record</h4><ul class="plain">';
      splitIds(o.source_record_ids).forEach(function (s) {
        var r = FACTS.source_records[s] || {};
        h += '<li><b>' + esc(s) + '</b> ' + esc(r.source_work || '') + ' ' + esc(r.record_lunar_date || '') + '<br>' + esc(r.source_title || '') +
          (r.source_url ? ' <a href="' + esc(r.source_url) + '" target="_blank" rel="noopener">원문</a>' : '') + '</li>';
      });
      h += '</ul>';
      if (o.identity_links) h += '<p class="small">동일성 대장: ' + esc(o.identity_links) + '</p>';
      h += '<h4>관련 mechanism (canonical edge 경로)</h4>' + relatedMechHtml(n);
    } else if (t === 'CANDIDATE_BRIDGE') {
      var r = CAND.rows[id] || {}, gp = CAND.gaps[r.gap_id] || {};
      h = '<div class="callout latent">사료에 직접 적힌 사실이 아니라 빈칸을 설명하기 위한 가설</div>' + h;
      h += kv([['candidate ID', id], ['gap ID', r.gap_id + (gp.title ? ' · ' + gp.title : '')], ['bridge claim', r.latent_bridge_claim],
        ['source support', r.source_support], ['plausibility', r.plausibility_grade], ['institutional fit', r.institutional_fit],
        ['temporal fit', r.temporal_fit], ['assumption cost (n_assumptions)', r.n_assumptions], ['추가 가정', r.extra_assumptions],
        ['contradiction risk', r.contradiction_risk], ['final grade (overall)', r.overall], ['evidence grade', r.evidence_grade],
        ['bridge directly attested', r.bridge_directly_attested], ['bridge evidence', r.bridge_evidence], ['사용하는 world', worldsOfNode(n)],
        ['prune decision', r.prune_decision], ['identity conditions', r.identity_conditions], ['주 메커니즘', c.mechanism],
        ['관측 왼쪽', r.observed_left], ['관측 오른쪽', r.observed_right]]);
      h += '<h4>약점·충돌</h4>' + kv([['conflicts', r.conflicts || '-'], ['notes', r.notes], ['재감사 이유', r.reaudit_reason]]);
      h += '<h4>관련 mechanism</h4>' + relatedMechHtml(n);
    } else if (t === 'INSTITUTIONAL_CONTEXT' || t === 'ENV_CONTEXT') {
      var f = n.context_feature || {};
      h = '<div class="callout context">CONTEXT — 제약조건·호환성일 뿐, 사건 발생 자체를 증명하지 않음</div>' + h;
      if (t === 'INSTITUTIONAL_CONTEXT') {
        h += kv([['feature ID', f.feature_id], ['이름', f.feature_name], ['설명', c.detail]].concat(Object.keys(f).filter(function (k) {
          return ['feature_id', 'feature_name', 'operational_definition'].indexOf(k) < 0;
        }).map(function (k) { return [k, f[k]]; })));
      } else {
        var src = n.context_source || {};
        h += kv([['feature ID', f.env_id], ['설명', c.detail], ['context 기록일', src.record_lunar_date + ' (context 기록일 — 사건 날짜 lane에 두지 않음)']].concat(
          Object.keys(f).filter(function (k) { return k !== 'env_id'; }).map(function (k) { return [k, f[k]]; })));
      }
      h += '<h4>연결된 mechanism</h4>' + relatedMechHtml(n);
    } else if (t === 'MECHANISM') {
      var def = FACTS.definitions[id] || {};
      h += kv([['mechanism', id + ' · ' + META.mechanism_display[id]], ['canonical 이름', c.label], ['branch', c.branch], ['설명', c.detail]]);
      h += '<h4>정의 (mechanism_definitions.csv)</h4>' + kv(Object.keys(def).map(function (k) { return [k, def[k]]; }));
      h += '<h4>World configuration</h4><table class="tbl"><tr><th>world</th><th>값</th><th>근거</th></tr>' + W.order.map(function (wid) {
        var cf = W.configurations[wid], v = cf[id], rej = cf.role_type === 'REJECTED';
        return '<tr class="' + (rej ? 'rejected' : '') + '"><td>' + esc(wid) + (rej ? ' REJECTED' : '') + '</td><td>' + chip(W.config_display[v].css, v) + '</td><td>' + esc(cf[id + '_basis']) + '</td></tr>';
      }).join('') + '</table><p class="small muted">UNSPECIFIED ≠ OFF.</p>';
    } else if (t === 'STRUCTURAL_VARIABLE') {
      var rule = IX.rules.filter(function (r) { return r['var'] === id; })[0] || {};
      h += kv([['변수', id], ['연산', rule.op], ['규칙', rule.rule], ['설명', rule.desc], ['입력', rule.inputs], ['입력 후보', rule.input_candidates],
        ['gap', rule.gap], ['관측 대상', rule.target], ['제약', rule.constraint], ['branch', c.branch]]);
      h += '<p class="small muted">질적 구조 규칙이다. 역사적으로 그렇게 됐다는 단정이 아니다.</p>';
    } else if (t === 'UNRESOLVED_ITEM') {
      h += kv([['항목', id], ['내용', c.label], ['관측 영향', c.detail], ['worlds', c.worlds]]);
      h += '<div class="callout info">확정하지 않은 항목이다. 후보의 성립 조건(CONDITIONS)으로만 남고, Audit 4에서 UNRESOLVED(unresolved_item)로 기록된다.</div>';
    }
    h += incidentEdgesHtml(id);
    $('p-detail').innerHTML = h;
    showPane('detail');
  }

  function renderEdgeDetail(id) {
    var e = edgeById[id];
    if (!e) return;
    var c = e.canonical, s = META.edge_styles[c.edge_type] || {};
    var h = '<h3>edge ' + esc(id) + '</h3><p>' + chip('st-' + e.status_group, c.sd_status) + ' ' + chip('flag', c.origin) + '</p>';
    h += kv([['edge_id', id], ['src', nodeLink(c.src) + ' ' + esc((nodeById[c.src] || {}).short_label || ''), true],
      ['dst', nodeLink(c.dst) + ' ' + esc((nodeById[c.dst] || {}).short_label || ''), true], ['edge_type', c.edge_type + (s.ko ? ' · ' + s.ko : '')],
      ['sd_status', c.sd_status], ['origin', c.origin], ['note', c.note]]);
    if (e.frozen) {
      var f = e.frozen;
      h += '<h4>frozen observed edge 필드</h4>' + kv([['basis', f.basis], ['status', f.status], ['claim_level', f.claim_level], ['condition', f.condition],
        ['supporting', f.supporting], ['rationale', f.rationale], ['caution', f.caution], ['uncertainty_status', f.uncertainty_status], ['review_decision', f.review_decision]]);
    }
    $('p-detail').innerHTML = h;
    showPane('detail');
  }

  function defaultDetail() {
    $('p-detail').innerHTML = '<h3>상세</h3><p class="empty">그래프에서 node나 edge를 누르면 canonical 값이 여기에 나온다.</p>' +
      '<div class="callout info">OBSERVED = 확정 사실에서 만든 관측 사건(고정). LATENT = 사료가 알려주지 않는 중간 과정을 설명하는 가설·분석 변수. ' +
      'CONTEXT = 제도·환경 제약(사건 아님). UNRESOLVED = 확정하지 않은 항목.</div>' +
      kv([['frozen graph hash', META.frozen_hash], ['node', META.counts.nodes], ['edge', META.counts.edges],
        ['node status', Object.keys(META.counts.node_status).map(function (k) { return k + ' ' + META.counts.node_status[k]; }).join(' · ')],
        ['edge status', Object.keys(META.counts.edge_status).map(function (k) { return k + ' ' + META.counts.edge_status[k]; }).join(' · ')]]);
  }

  // ------------------------------------------------------------------ World 구성 패널
  function renderWorldPanel() {
    var h = '<h3>World configuration</h3>';
    h += '<div class="callout info"><b>UNSPECIFIED ≠ OFF</b> — UNSPECIFIED는 관련 후보가 없어 작동 여부를 말하지 않는다는 뜻이다. ' +
      (W.off_count === 0 ? '현재 어느 world에도 OFF 값은 없다.' : 'OFF 값 ' + W.off_count + '개.') + '</div>';
    if (state.world === 'ALL') {
      h += '<table class="tbl"><tr><th>world</th>' + MECHS.map(function (m) { return '<th>' + m + '</th>'; }).join('') + '</tr>';
      W.order.forEach(function (wid) {
        var cf = W.configurations[wid], rej = cf.role_type === 'REJECTED';
        h += '<tr class="' + (rej ? 'rejected' : '') + '"><td>' + esc(wid) + (rej ? ' REJECTED' : '') + '</td>' + MECHS.map(function (m) {
          return '<td>' + chip(W.config_display[cf[m]].css, cf[m] === 'UNSPECIFIED' ? 'UNSPEC.' : cf[m]) + '</td>';
        }).join('') + '</tr>';
      });
      h += '</table><p class="small muted">UNSPEC. = UNSPECIFIED. W6은 REJECTED(대조군)로 공존·개입 분석에서 제외된다.</p>';
    } else {
      var cf = W.configurations[state.world], nw = W.narratives[state.world] || {}, sel = W.selections[state.world];
      if (sel.rejected) h += '<div class="callout warn"><b>' + esc(state.world) + ' REJECTED</b> — ' + esc(sel.banner) + '</div>';
      h += kv([['world', state.world + (nw.name ? ' · ' + nw.name : '')], ['role_type', cf.role_type], ['latent bridges', cf.latent_bridges],
        ['질문', nw.story_question], ['최저 등급', nw.min_grade], ['가정 수', nw.n_assumptions], ['주요 약점', nw.main_weaknesses]]);
      h += '<table class="tbl"><tr><th>mechanism</th><th>값</th><th>근거</th></tr>' + MECHS.map(function (m) {
        return '<tr><td><b>' + m + '</b> ' + esc(META.mechanism_display[m]) + '</td><td>' + chip(W.config_display[cf[m]].css, cf[m]) + '</td><td>' + esc(cf[m + '_basis']) + '</td></tr>';
      }).join('') + '</table>';
      h += '<p class="small muted">값 뜻: ' + Object.keys(W.config_display).map(function (k) { return k + ' = ' + W.config_display[k].note; }).join(' / ') + '</p>';
    }
    h += '<h4>공통 OBSERVED 결말 (모든 world에서 표시)</h4><ul class="plain">' + Object.keys(W.common_outcome_nodes).map(function (k) {
      return '<li><b>' + esc(k) + '</b>: ' + W.common_outcome_nodes[k].map(nodeLink).join(', ') + '</li>';
    }).join('') + '</ul>';
    $('p-world').innerHTML = h;
  }

  // ------------------------------------------------------------------ 공존 패널
  var REL_TEXT = {
    SUBSTITUTE: '같은 관측 전이를 다른 방식으로 설명(대체)', EXCLUSIVE_ALTERNATIVE: '같은 전이를 서로 배타적으로 설명',
    COMPLEMENT: '한 world 안에서 서로 다른 전이를 함께 설명(보완)', INDEPENDENT: '다른 branch이거나 관측 고정이라 서로 설명하지 않음',
    NO_SHARED_TRANSITION: '공유하는 전이가 없음'
  };
  function findPair(a, b) {
    for (var i = 0; i < IX.pairs.length; i++) {
      var p = IX.pairs[i];
      if ((p.a === a && p.b === b) || (p.a === b && p.b === a)) return p;
    }
    return null;
  }
  function renderInterPanel() {
    var a = state.pair[0], b = state.pair[1];
    var opts = function (sel) { return MECHS.map(function (m) { return '<option value="' + m + '"' + (m === sel ? ' selected' : '') + '>' + m + ' ' + esc(META.mechanism_display[m]) + '</option>'; }).join(''); };
    var h = '<h3>메커니즘 공존</h3><p class="small muted">' + esc(IX.note) + '</p>';
    h += '<div class="pair-pick"><select id="pair-a" aria-label="mechanism A">' + opts(a) + '</select><span>×</span><select id="pair-b" aria-label="mechanism B">' + opts(b) + '</select></div>';
    // 행렬
    h += '<table class="matrix"><tr><th></th>' + MECHS.map(function (m) { return '<th>' + m + '</th>'; }).join('') + '</tr>';
    var abbr = { COMPATIBLE: 'C', PARTIALLY_COMPATIBLE: 'P', INCOMPATIBLE: 'X', UNKNOWN: '?' };
    var bg = { COMPATIBLE: '#e8f6e8', PARTIALLY_COMPATIBLE: '#fff1c8', INCOMPATIBLE: '#fbdada', UNKNOWN: '#efefec' };
    MECHS.forEach(function (r) {
      h += '<tr><th>' + r + '</th>' + MECHS.map(function (c) {
        if (r === c) return '<td class="diag"></td>';
        var p = findPair(r, c), co = p.canonical.coexistence, un = p.audit4.length ? '*' : '';
        var sel = (r === a && c === b) || (r === b && c === a);
        return '<td class="cell' + (sel ? ' sel' : '') + '" data-pa="' + r + '" data-pb="' + c + '" style="background:' + (bg[co] || '#fff') + '" title="' + r + '×' + c + ' ' + co + (un ? ' · Audit 4 UNRESOLVED' : '') + '">' + (abbr[co] || co) + un + '</td>';
      }).join('') + '</tr>';
    });
    h += '</table><p class="small muted">C = COMPATIBLE · P = PARTIALLY_COMPATIBLE · X = INCOMPATIBLE · ? = UNKNOWN · * = Audit 4 UNRESOLVED 있음</p>';
    if (a === b) {
      h += '<p class="empty">서로 다른 두 메커니즘을 고르세요.</p>';
    } else {
      var p = findPair(a, b), c = p.canonical;
      h += '<h4>' + esc(c['mechanism A']) + ' × ' + esc(c['mechanism B']) + '</h4>';
      h += '<p>' + chip('co-' + c.coexistence, c.coexistence) + '</p>';
      h += kv([['coexistence', c.coexistence], ['relation', splitIds(c.relation).map(function (r) { return '<code>' + esc(r) + '</code> ' + esc(REL_TEXT[r] || ''); }).join('<br>'), true],
        ['이유', c['이유']], ['충돌하는 candidate/edge', c['충돌하는 candidate/edge'] || '-'], ['같이 있을 때 설명되는 것', c['같이 있을 때 설명되는 것'] || '-'],
        ['함께 쓰는 world', c.cooccur_worlds || '없음'], ['canonical 이름', c.mechanism_a + ' × ' + c.mechanism_b]]);
      h += '<h4>Audit 4</h4>' + (p.audit4.length ? '<ul class="plain">' + p.audit4.map(function (f) {
        return '<li>' + chip('st-UNRESOLVED', f.severity) + ' <code>' + esc(f.check) + '</code> ' + esc(f.message) + '</li>';
      }).join('') + '</ul>' : '<p class="muted">이 쌍에 대한 Audit 4 UNRESOLVED 없음</p>');
      var shared = IX.rules.filter(function (r) { var ins = splitIds(r.inputs); return ins.indexOf(a) >= 0 && ins.indexOf(b) >= 0; });
      h += '<h4>두 메커니즘을 함께 입력으로 쓰는 구조 규칙</h4>' + (shared.length ? '<ul class="plain">' + shared.map(function (r) {
        return '<li><code>' + esc(r['var']) + '</code> <b>' + esc(r.op) + '</b> — ' + esc(r.rule) + '</li>';
      }).join('') + '</ul>' : '<p class="muted">없음</p>');
    }
    // 대체·배타·보완 요약(canonical 규칙·관계에서 그대로)
    h += '<h4>대체·배타·보완 (canonical 규칙과 relation 값)</h4><ul class="plain">';
    IX.rules.filter(function (r) { return (r.op === 'OR' || r.op === 'XOR') && splitIds(r.inputs).filter(function (x) { return MECHS.indexOf(x) >= 0; }).length >= 2; }).forEach(function (r) {
      var ins = splitIds(r.inputs);
      h += '<li><code>' + esc(r['var']) + '</code> = ' + esc(ins.join(r.op === 'OR' ? ' OR ' : ' XOR ')) + ' <span class="muted">(' + (r.op === 'OR' ? '대체' : '배타') + ')</span></li>';
    });
    var comp = IX.pairs.filter(function (p) { return p.canonical.relation === 'COMPLEMENT'; }).map(function (p) { return p.key; });
    h += '<li>보완(relation = COMPLEMENT): ' + esc(comp.join(', ') || '없음') + '</li>';
    var mixed = IX.pairs.filter(function (p) { return p.canonical.relation.indexOf('COMPLEMENT') >= 0 && p.canonical.relation !== 'COMPLEMENT'; });
    h += '<li>보완 + 대체/배타: ' + esc(mixed.map(function (p) { return p.key + ' (' + p.canonical.relation + ')'; }).join(', ') || '없음') + '</li></ul>';
    h += '<p class="small muted">공존 분석 제외 world: ' + esc(IX.excluded_worlds.join(', ')) + ' (REJECTED)</p>';
    $('p-inter').innerHTML = h;
    $('pair-a').addEventListener('change', function (ev) { setPair(ev.target.value, state.pair[1]); });
    $('pair-b').addEventListener('change', function (ev) { setPair(state.pair[0], ev.target.value); });
    Array.prototype.forEach.call(document.querySelectorAll('.matrix td.cell'), function (td) {
      td.addEventListener('click', function () { setPair(td.dataset.pa, td.dataset.pb); });
    });
  }
  function setPair(a, b) { state.pair = [a, b]; state.pairOn = true; renderInterPanel(); applyState(); }

  // ------------------------------------------------------------------ 개입 패널
  function renderIvPanel() {
    var h = '<h3>질적 개입 do(M = OFF)</h3><div class="callout info">' + esc(IV.note) + '</div>';
    h += '<div class="iv-buttons" role="group" aria-label="개입">' + MECHS.map(function (m) {
      return '<button type="button" data-iv="' + m + '" aria-pressed="' + String(state.iv === m) + '">do(' + m + '=OFF)</button>';
    }).join('') + '<button type="button" data-iv="" aria-pressed="false">개입 해제</button></div>';
    if (!state.iv) {
      h += '<p class="empty">메커니즘을 고르면 저장된 개입 결과(mechanism_interventions.csv)를 보여 주고, 그래프에서 영향받는 설명 경로를 강조한다.</p>';
      h += '<table class="tbl"><tr><th>intervention</th><th>결과 요약</th></tr>' + MECHS.map(function (m) {
        return '<tr><td>do(' + m + '=OFF)</td><td>' + IV.rows.filter(function (r) { return r.canonical.mechanism === m; }).map(function (r) {
          return '<code>' + esc(r.canonical.variable) + '</code> ' + chip('res-' + r.canonical.result, r.canonical.result);
        }).join('<br>') + '</td></tr>';
      }).join('') + '</table>';
    } else {
      var rows = ivRows();
      h += '<h4>do(' + esc(state.iv) + '=OFF) · ' + esc(META.mechanism_display[state.iv]) + '</h4>';
      h += '<div id="iv-table">' + rows.map(function (r) {
        var c = r.canonical;
        return '<div class="iv-row"><div class="iv-head"><code>' + esc(c.variable) + '</code> ' + chip('res-' + c.result, c.result) + '</div>' +
          kv([['관측 대상', idsLinks(c.target), true], ['사라지는 후보', idsLinks(c.removed) || '-', true], ['남는 후보', idsLinks(c.remaining) || '-', true],
            ['영향받는 world', c.affected_worlds], ['설명', c.note]]) + '</div>';
      }).join('') + '</div>';
      h += '<p class="small">관측 사건(OBSERVED)은 개입 중에도 그대로 남는다. 바뀌는 것은 그 앞의 설명 경로뿐이다.</p>';
    }
    $('p-iv').innerHTML = h;
    Array.prototype.forEach.call(document.querySelectorAll('[data-iv]'), function (b) {
      b.addEventListener('click', function () { setIntervention(b.dataset.iv || null); });
    });
  }

  // ------------------------------------------------------------------ 패널 탭
  function showPane(name) {
    Array.prototype.forEach.call(document.querySelectorAll('.ptabs button'), function (b) { b.classList.toggle('active', b.dataset.ptab === name); });
    Array.prototype.forEach.call(document.querySelectorAll('.pbody'), function (p) { p.hidden = p.dataset.pane !== name; });
  }
  Array.prototype.forEach.call(document.querySelectorAll('.ptabs button'), function (b) {
    b.addEventListener('click', function () { showPane(b.dataset.ptab); });
  });
  document.querySelector('.panel').addEventListener('click', function (ev) {
    var t = ev.target.closest('[data-goto]');
    if (t) { focusNode(t.dataset.goto); return; }
    var te = ev.target.closest('[data-goto-edge]');
    if (te) { focusEdge(te.dataset.gotoEdge); }
  });

  // ------------------------------------------------------------------ 검색
  var index = SD.nodes.map(function (n) {
    var c = n.canonical, parts = [n.id, c.label, n.short_label, c.detail, c.mechanism, c.node_type];
    if (n.observed) parts.push(n.observed.member_fact_ids, n.observed.summary, n.observed.title, n.observed.attesting_actor, n.observed.source_record_ids);
    var r = CAND.rows[n.id];
    if (r) parts.push(r.gap_id, r.latent_bridge_claim, r.bridge_evidence, r.supports, r.description);
    if (META.mechanism_display[n.id]) parts.push(META.mechanism_display[n.id]);
    return { id: n.id, text: parts.join(' \u0001 ').toLowerCase(), label: n.short_label };
  });
  function search(q) {
    q = String(q || '').trim().toLowerCase();
    if (!q) return [];
    var res = [];
    index.forEach(function (it) {
      var id = it.id.toLowerCase(), score = -1;
      if (id === q) score = 0; else if (id.indexOf(q) === 0) score = 1; else if (it.label.toLowerCase().indexOf(q) >= 0) score = 2;
      else if (it.text.indexOf(q) >= 0) score = 3;
      if (score >= 0) {
        var pos = it.text.indexOf(q), why = score === 3 ? it.text.substr(Math.max(0, pos - 20), 70).replace(/\u0001/g, '·') : '';
        res.push({ id: it.id, score: score, label: it.label, why: why });
      }
    });
    res.sort(function (x, y) { return x.score - y.score || (x.id < y.id ? -1 : 1); });
    return res.slice(0, 30);
  }
  var sInput = $('search'), sList = $('search-results'), sActive = 0, sRes = [];
  function renderResults() {
    if (!sRes.length) { sList.hidden = !sInput.value.trim(); sList.innerHTML = sInput.value.trim() ? '<li class="muted">결과 없음</li>' : ''; return; }
    sList.hidden = false;
    sList.innerHTML = sRes.map(function (r, i) {
      return '<li role="option" data-id="' + esc(r.id) + '" class="' + (i === sActive ? 'active' : '') + '"><b>' + esc(r.id) + '</b> ' + esc(r.label.replace(r.id + ' · ', '')) +
        (r.why ? '<span class="why">…' + esc(r.why) + '…</span>' : '') + '</li>';
    }).join('');
  }
  sInput.addEventListener('input', function () { sRes = search(sInput.value); sActive = 0; renderResults(); });
  sInput.addEventListener('keydown', function (ev) {
    if (ev.key === 'ArrowDown') { sActive = Math.min(sActive + 1, sRes.length - 1); renderResults(); ev.preventDefault(); }
    else if (ev.key === 'ArrowUp') { sActive = Math.max(sActive - 1, 0); renderResults(); ev.preventDefault(); }
    else if (ev.key === 'Enter') { if (sRes[sActive]) { focusNode(sRes[sActive].id); sList.hidden = true; } ev.preventDefault(); }
    else if (ev.key === 'Escape') { sList.hidden = true; }
  });
  sList.addEventListener('mousedown', function (ev) {
    var li = ev.target.closest('li[data-id]');
    if (li) { ev.preventDefault(); focusNode(li.dataset.id); sList.hidden = true; }
  });
  sInput.addEventListener('blur', function () { setTimeout(function () { sList.hidden = true; }, 150); });

  // ------------------------------------------------------------------ 상호작용
  function focusNode(id) {
    var n = cy.getElementById(id);
    if (!n || !n.length) return false;
    if (n.hasClass('hidden')) {
      // 필터 때문에 숨겨진 node는 보기·필터를 풀어서 보여 준다
      state.view = 'overview'; state.hideOthers = false;
      var d = n.data();
      state.status[d.sgroup] = true;
      if (d.mech) state.mech[d.mech] = true;
      syncFilterInputs();
      applyState();
    }
    cy.$(':selected').unselect();
    cy.nodes().removeClass('search-hit');
    n.select(); n.addClass('search-hit');
    cy.animate({ center: { eles: n }, zoom: Math.max(cy.zoom(), 0.85) }, { duration: 250 });
    renderNodeDetail(id);
    return true;
  }
  function focusEdge(id) {
    var e = cy.getElementById(id);
    if (!e || !e.length) return false;
    cy.$(':selected').unselect();
    e.select();
    cy.animate({ center: { eles: e }, zoom: Math.max(cy.zoom(), 0.6) }, { duration: 250 });
    renderEdgeDetail(id);
    return true;
  }
  cy.on('tap', 'node', function (ev) { cy.nodes().removeClass('search-hit'); renderNodeDetail(ev.target.id()); });
  cy.on('tap', 'edge', function (ev) { renderEdgeDetail(ev.target.id()); });
  var tip = $('tooltip');
  cy.on('mouseover', 'node', function (ev) {
    var n = nodeById[ev.target.id()], c = n.canonical, p = ev.renderedPosition;
    tip.innerHTML = '<b>' + esc(n.id) + '</b> ' + esc(c.label) + '<span class="t-sub">' + esc(c.sd_status) + ' · ' + esc(c.node_type) +
      (n.observed ? ' · ' + esc(n.observed.occurrence_text) : '') + '</span>';
    tip.style.left = Math.min(p.x + 14, cy.width() - 350) + 'px'; tip.style.top = (p.y + 14) + 'px'; tip.hidden = false;
  });
  cy.on('mouseout', 'node', function () { tip.hidden = true; });
  cy.on('mouseover', 'edge', function (ev) { ev.target.addClass('hover'); });
  cy.on('mouseout', 'edge', function (ev) { ev.target.removeClass('hover'); });
  cy.on('viewport', function () { tip.hidden = true; });

  function visibleOf(ids) {
    var c = cy.collection();
    ids.forEach(function (id) { var n = cy.getElementById(id); if (n.length && !n.hasClass('hidden')) c = c.union(n); });
    return c;
  }
  function setView(id) {
    state.view = id;
    applyState();
    var v = VIEWS.views[id];
    fitTo(id === 'overview' ? cy.nodes(':visible') : visibleOf(v.nodes));
  }
  function setWorld(wid) { state.world = wid; applyState(); }
  function setIntervention(m) {
    state.iv = m || null;
    applyState();
    showPane('iv');
    if (state.iv) fitTo(visibleOf(ivRows().reduce(function (a, r) { return a.concat(r.path_nodes); }, [])), 50);
  }
  function reset() {
    state = DEFAULT_STATE();
    syncFilterInputs();
    sInput.value = ''; sRes = []; renderResults(); sList.hidden = true;
    cy.$(':selected').unselect();
    cy.nodes().removeClass('search-hit');
    applyState();
    renderInterPanel();
    defaultDetail();
    showPane('detail');
    fitTo(cy.nodes());
  }
  $('reset').addEventListener('click', reset);
  $('zoom-in').addEventListener('click', function () { cy.zoom({ level: cy.zoom() * 1.25, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }); });
  $('zoom-out').addEventListener('click', function () { cy.zoom({ level: cy.zoom() / 1.25, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }); });
  $('zoom-fit').addEventListener('click', function () { fitTo(cy.nodes(':visible')); });
  window.addEventListener('resize', function () { cy.resize(); syncOverlay(); });

  // ------------------------------------------------------------------ 시작
  applyState();
  renderInterPanel();
  defaultDetail();
  fitTo(cy.nodes());

  // 테스트·디버깅용(읽기 전용 용도)
  window.__viz = {
    cy: cy, data: D, getState: function () { return JSON.parse(JSON.stringify(state)); },
    setView: setView, setWorld: setWorld, setIntervention: setIntervention, setPair: setPair,
    focusNode: focusNode, focusEdge: focusEdge, search: search, reset: reset
  };
})();
