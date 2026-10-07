/* 구순–김명신 사건 Mechanism Super-DAG — Interactive Temporal DAG
 *
 * 이 스크립트는 data/bundle.js(= data/*.json)에 들어 있는 canonical 값을 그대로 보여 준다.
 * 상태·configuration·공존 판정·개입 결과·후보 등급을 다시 계산하거나 해석하지 않는다.
 * 배치는 Python이 미리 계산한 preset 좌표다(물리 시뮬레이션 없음, node 이동 불가).
 * 관점별 View(B–I)는 canonical node·edge의 부분집합을 그 View 전용 좌표로 보여 줄 뿐이다(시각적 필터).
 * 가독성 원칙: 첫 화면의 node label은 11pt 이상으로 그려진다(READABILITY > FIT ALL NODES).
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
  var TY = META.typography;
  var READ_ZOOM = TY.read_zoom;            // 이 배율 이상이면 node label이 11pt 이상

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
  var DEFAULT_STATE = function () {
    return { view: 'overview', world: 'ALL', hideOthers: false, showContext: false, status: toSet(STATUS_KEYS), mech: toSet(MECHS), iv: null, pair: ['M1', 'M2'] };
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
  function viewsOfNode(id) { return VIEWS.order.filter(function (v) { return VIEWS.views[v].nodes.indexOf(id) >= 0; }); }

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

  // ------------------------------------------------------------------ cytoscape 요소
  var elements = [];
  SD.nodes.forEach(function (n) {
    var t = n.canonical.node_type, d = n.display;
    elements.push({
      group: 'nodes',
      data: {
        id: n.id, label: d.label, base: d.label, ntype: t, sgroup: n.status_group, status: n.canonical.sd_status,
        mech: (t === 'MECHANISM' ? n.id : (t === 'CANDIDATE_BRIDGE' ? n.canonical.mechanism : '')),
        w: d.w, h: d.h, h0: d.h, tw: d.w, outcome: n.common_outcome ? 1 : 0, excluded: n.analysis_excluded ? 1 : 0
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
  var FONT = 'system-ui, -apple-system, "Segoe UI", "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", sans-serif';
  var style = [
    { selector: 'node', style: {
      'label': 'data(label)', 'text-wrap': 'wrap', 'text-max-width': 'data(tw)', 'font-size': TY.node_font_px, 'line-height': TY.line_height,
      'font-family': FONT, 'text-valign': 'center', 'text-halign': 'center', 'text-justification': 'center',
      'width': 'data(w)', 'height': 'data(h)', 'shape': 'round-rectangle', 'background-color': '#ffffff', 'border-width': 1.5,
      'border-color': '#898781', 'color': '#0b0b0b', 'min-zoomed-font-size': 0
    } },
    { selector: 'node.OBSERVED_EVENT', style: { 'background-color': '#eaf2fc', 'border-color': '#256abf', 'border-width': 2.5, 'border-style': 'solid' } },
    { selector: 'node.outcome', style: { 'border-style': 'double', 'border-width': 6, 'border-color': '#1c5cab' } },
    { selector: 'node.MECHANISM', style: { 'shape': 'hexagon', 'background-color': '#efedfa', 'border-color': '#4a3aa7', 'border-style': 'dashed', 'border-width': 3, 'font-weight': 700 } },
    { selector: 'node.STRUCTURAL_VARIABLE', style: { 'shape': 'cut-rectangle', 'background-color': '#f6f4fd', 'border-color': '#4a3aa7', 'border-style': 'dashed', 'border-width': 2 } },
    { selector: 'node.CANDIDATE_BRIDGE', style: { 'background-color': '#fdf1ea', 'border-color': '#c4501f', 'border-style': 'dashed', 'border-width': 2.2 } },
    { selector: 'node.CANDIDATE_BRIDGE.excluded', style: { 'background-color': '#f5f4f1', 'border-style': 'dotted', 'color': '#3f3e3b' } },
    { selector: 'node.INSTITUTIONAL_CONTEXT', style: { 'shape': 'rectangle', 'background-color': '#eef6ee', 'border-color': '#008300', 'border-style': 'dotted', 'border-width': 2.5 } },
    { selector: 'node.ENV_CONTEXT', style: { 'shape': 'barrel', 'background-color': '#eef6ee', 'border-color': '#008300', 'border-style': 'dotted', 'border-width': 2.5 } },
    { selector: 'node.UNRESOLVED_ITEM', style: { 'shape': 'round-rectangle', 'background-color': '#fcf0f5', 'border-color': '#b83a6b', 'border-style': 'double', 'border-width': 6 } },
    // 축소(지도) 모드: 글자가 11pt보다 작아지는 배율에서는 ID만 크게
    { selector: 'node.far', style: { 'label': 'data(id)', 'font-size': TY.far_id_font_px, 'font-weight': 700, 'text-overflow-wrap': 'anywhere' } },
    { selector: 'edge', style: {
      'curve-style': 'bezier', 'width': 2, 'line-color': '#898781', 'target-arrow-color': '#898781', 'target-arrow-shape': 'triangle',
      'arrow-scale': 1.1, 'opacity': 0.85, 'font-size': TY.edge_font_px, 'line-height': TY.line_height, 'font-family': FONT,
      'text-background-color': '#ffffff', 'text-background-opacity': 0.95, 'text-background-padding': 3, 'text-background-shape': 'roundrectangle',
      'text-border-color': '#c3c2b7', 'text-border-width': 1, 'text-border-opacity': 1,
      'text-rotation': 'autorotate', 'color': '#0b0b0b', 'min-zoomed-font-size': 0
    } },
    // 다른 node 밑을 지나가는 edge는 결정적으로 고른 곡선으로 돌려 그린다(routeEdges)
    { selector: 'edge.arc', style: { 'curve-style': 'unbundled-bezier', 'control-point-distances': 'data(cpd)', 'control-point-weights': 0.5 } },
    { selector: 'edge.eo-SUPER_DAG', style: { 'opacity': 0.6, 'width': 1.6 } },
    { selector: 'edge.es-DERIVED', style: { 'width': 2.4 } },
    { selector: 'edge.es-OBSERVED', style: { 'width': 4.2 } }
  ];
  Object.keys(META.edge_styles).forEach(function (t) {
    var s = META.edge_styles[t];
    style.push({ selector: 'edge.et-' + t, style: { 'line-color': s.color, 'target-arrow-color': s.color, 'target-arrow-shape': s.arrow, 'line-style': DASH[s.line] || 'solid' } });
  });
  style = style.concat([
    { selector: '.dim', style: { 'opacity': 0.2 } },
    { selector: 'edge.dim', style: { 'opacity': 0.07 } },
    { selector: '.hidden', style: { 'display': 'none' } },
    { selector: 'node.hl', style: { 'underlay-color': '#eda100', 'underlay-opacity': 0.38, 'underlay-padding': 9, 'underlay-shape': 'round-rectangle' } },
    { selector: 'node.hl-rej', style: { 'underlay-color': '#d03b3b', 'underlay-opacity': 0.30, 'underlay-padding': 9, 'border-color': '#d03b3b', 'border-style': 'dashed' } },
    { selector: 'node.cfg-UNSPECIFIED', style: { 'background-color': '#f3f3f1', 'border-color': '#898781', 'border-style': 'dotted', 'color': '#3f3e3b' } },
    { selector: 'node.cfg-PARTIAL', style: { 'border-style': 'dashed', 'border-width': 4 } },
    { selector: 'node.cfg-ON', style: { 'border-style': 'solid', 'border-width': 5 } },
    { selector: 'node.grpA', style: { 'underlay-color': '#008300', 'underlay-opacity': 0.24, 'underlay-padding': 10 } },
    { selector: 'node.grpB', style: { 'underlay-color': '#eb6834', 'underlay-opacity': 0.26, 'underlay-padding': 10 } },
    { selector: 'node.pair', style: { 'underlay-color': '#2a78d6', 'underlay-opacity': 0.30, 'underlay-padding': 11 } },
    { selector: 'node.iv-off', style: { 'background-color': '#e9e8e4', 'border-color': '#52514e', 'border-style': 'solid', 'border-width': 4, 'color': '#3f3e3b' } },
    { selector: 'node.iv-removed', style: { 'opacity': 0.5, 'border-color': '#d03b3b', 'border-style': 'dashed', 'border-width': 4 } },
    { selector: 'node.iv-remaining', style: { 'underlay-color': '#0ca30c', 'underlay-opacity': 0.32, 'underlay-padding': 9 } },
    { selector: 'node.iv-PATH_BREAKS', style: { 'underlay-color': '#d03b3b', 'underlay-opacity': 0.35, 'underlay-padding': 11 } },
    { selector: 'node.iv-PATH_WEAKENS', style: { 'underlay-color': '#fab219', 'underlay-opacity': 0.5, 'underlay-padding': 11 } },
    { selector: 'node.iv-PATH_REMAINS', style: { 'underlay-color': '#0ca30c', 'underlay-opacity': 0.35, 'underlay-padding': 11 } },
    { selector: 'node.iv-UNKNOWN', style: { 'underlay-color': '#898781', 'underlay-opacity': 0.35, 'underlay-padding': 11 } },
    { selector: 'node.iv-target', style: { 'underlay-color': '#2a78d6', 'underlay-opacity': 0.30, 'underlay-padding': 11 } },
    { selector: 'edge.iv-path', style: { 'opacity': 1, 'width': 4, 'z-index': 9 } },
    // 선택한 node의 들어오는/나가는 edge 강조, 나머지 edge 흐림
    { selector: 'edge.faded', style: { 'opacity': 0.08 } },
    { selector: 'edge.sel-in, edge.sel-out', style: { 'opacity': 1, 'width': 5, 'z-index': 30, 'label': 'data(etype)' } },
    { selector: 'edge.sel-in', style: { 'line-style': 'solid' } },
    { selector: 'node.sel-nbr', style: { 'underlay-color': '#2a78d6', 'underlay-opacity': 0.18, 'underlay-padding': 8 } },
    { selector: 'node.search-hit', style: { 'underlay-color': '#2a78d6', 'underlay-opacity': 0.45, 'underlay-padding': 14 } },
    { selector: 'edge.hover, edge:selected', style: { 'label': 'data(etype)', 'opacity': 1, 'width': 5, 'z-index': 40 } },
    { selector: 'node:selected', style: { 'border-color': '#0b0b0b', 'border-width': 5, 'border-style': 'solid' } }
  ]);

  var cy = window.cytoscape({
    container: $('cy'), elements: elements, style: style, layout: { name: 'preset', fit: false },
    autoungrabify: true, autounselectify: false, boxSelectionEnabled: false, selectionType: 'single',
    minZoom: 0.05, maxZoom: 3, pixelRatio: 'auto', wheelSensitivity: 0.4
  });

  // ------------------------------------------------------------------ 활성 배치(View 좌표 또는 Overview 좌표)
  function isSubsetMode() { var v = VIEWS.views[state.view]; return v.policy === 'subset' && !state.showContext; }
  function activeLayout() {
    // subset View(B–I)는 그 View 전용 좌표, 나머지(Overview·J·전체 맥락 표시)는 Overview 좌표
    if (isSubsetMode()) return VIEWS.views[state.view].layout;
    return { lanes: SD.lanes, bands: SD.bands, ticks: SD.ticks, extent: SD.extent, anchor: SD.anchor, positions: null };
  }
  function applyPositions() {
    var L = activeLayout();
    cy.batch(function () {
      cy.nodes().forEach(function (n) {
        var p = L.positions && L.positions[n.id()], o = nodeById[n.id()].layout;
        n.position(p ? { x: p.x, y: p.y } : { x: o.x, y: o.y });
      });
    });
    routeEdges(L);
    drawOverlay(L);
    buildPins(L);
  }

  // edge 경로: 직선이 다른 node 상자를 지나가면, 그 상자를 피하는 가장 작은 곡률을 정해진 순서로 찾는다(같은 좌표 → 같은 경로).
  var ARC_TRIES = [70, -70, 130, -130, 200, -200, 290, -290, 400, -400, 540, -540];
  function routeEdges(L) {
    var inScope = function (id) { return !L.positions || !!L.positions[id]; };
    var boxes = [];
    cy.nodes().forEach(function (n) {
      if (!inScope(n.id())) return;
      var p = n.position(), d = n.data(), hh = d.h0 / 2 + (d.ntype === 'MECHANISM' ? TY.line_px : 0);
      boxes.push({ id: n.id(), x1: p.x - d.w / 2 - 10, x2: p.x + d.w / 2 + 10, y1: p.y - hh - 10, y2: p.y + hh + 10 });
    });
    function hits(P0, P1, C, sid, tid) {
      var n = 0;
      for (var k = 2; k <= 30; k++) {
        var t = k / 32, a = (1 - t) * (1 - t), b = 2 * t * (1 - t), c = t * t;
        var x = a * P0.x + b * C.x + c * P1.x, y = a * P0.y + b * C.y + c * P1.y;
        for (var i = 0; i < boxes.length; i++) {
          var q = boxes[i];
          if (q.id !== sid && q.id !== tid && x > q.x1 && x < q.x2 && y > q.y1 && y < q.y2) { n++; break; }
        }
      }
      return n;
    }
    cy.batch(function () {
      cy.edges().forEach(function (e) {
        var s = e.source(), t = e.target();
        e.removeClass('arc');
        if (!inScope(s.id()) || !inScope(t.id())) return;
        var P0 = s.position(), P1 = t.position(), dx = P1.x - P0.x, dy = P1.y - P0.y, len = Math.sqrt(dx * dx + dy * dy) || 1;
        var M = { x: (P0.x + P1.x) / 2, y: (P0.y + P1.y) / 2 }, nx = -dy / len, ny = dx / len;
        if (!hits(P0, P1, M, s.id(), t.id())) return;
        var best = null, bestN = Infinity;
        for (var i = 0; i < ARC_TRIES.length; i++) {
          var d = ARC_TRIES[i], C = { x: M.x + nx * d, y: M.y + ny * d }, h = hits(P0, P1, C, s.id(), t.id());
          if (h < bestN) { best = d; bestN = h; }
          if (!h) break;
        }
        e.data('cpd', best);
        e.addClass('arc');
      });
    });
  }

  // ------------------------------------------------------------------ 배경(시간 구간·lane)
  var SVGNS = 'http://www.w3.org/2000/svg';
  var overlay = $('overlay');
  var g = document.createElementNS(SVGNS, 'g');
  overlay.appendChild(g);
  function svgEl(tag, attrs, text) {
    var el = document.createElementNS(SVGNS, tag);
    Object.keys(attrs).forEach(function (k) { el.setAttribute(k, attrs[k]); });
    if (text != null) el.textContent = text;
    return el;
  }
  function svgLines(x, y, lines, size, attrs) {
    var t = svgEl('text', Object.assign({ x: x, y: y, 'font-size': size }, attrs || {}));
    lines.forEach(function (ln, i) {
      var ts = svgEl('tspan', { x: x, dy: i === 0 ? 0 : size * TY.line_height }, ln);
      t.appendChild(ts);
    });
    return t;
  }
  function drawOverlay(L) {
    while (g.firstChild) g.removeChild(g.firstChild);
    var defs = svgEl('defs', {});
    var pat = svgEl('pattern', { id: 'hatch', width: 12, height: 12, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' });
    pat.appendChild(svgEl('line', { x1: 0, y1: 0, x2: 0, y2: 12, stroke: '#e1e0d9', 'stroke-width': 4 }));
    defs.appendChild(pat);
    g.appendChild(defs);
    var ex = L.extent, x0 = ex.label_x0, x1 = ex.x1;
    var kindFill = { context: '#f2f7f1', latent: '#fbf6f2', unresolved: '#fbf2f6', observed: '#fcfcfb' };
    L.lanes.forEach(function (l, i) {
      g.appendChild(svgEl('rect', { x: x0, y: l.y0, width: x1 - x0, height: l.y1 - l.y0,
        fill: l.kind === 'observed' ? (i % 2 ? '#fcfcfb' : '#f6f6f2') : kindFill[l.kind] }));
      g.appendChild(svgEl('line', { x1: x0, x2: x1, y1: l.y1, y2: l.y1, stroke: '#d6d5cd', 'stroke-width': 1.5 }));
    });
    L.bands.forEach(function (b, i) {
      g.appendChild(svgEl('rect', { x: b.x0, y: b.y0, width: b.x1 - b.x0, height: b.y1 - b.y0,
        fill: b.dated ? (i % 2 ? 'rgba(42,120,214,0.045)' : 'rgba(42,120,214,0.085)') : 'url(#hatch)', stroke: b.dated ? 'rgba(42,120,214,0.3)' : '#c3c2b7',
        'stroke-dasharray': b.dated ? '' : '8 5', rx: 8 }));
      var bt = svgEl('g', { 'class': 'band-title', 'data-x0': b.x0, 'data-x1': b.x1 });
      bt.appendChild(svgEl('text', { x: b.x0 + 14, y: b.y0 + 30, 'font-size': TY.band_font_px, 'font-weight': 700, fill: '#1c5cab' }, b.label));
      bt.appendChild(svgEl('text', { x: b.x0 + 14, y: b.y0 + 30 + TY.band_sub_font_px * TY.line_height, 'font-size': TY.band_sub_font_px, fill: '#3f3e3b' }, b.sub));
      g.appendChild(bt);
    });
    var obsTop = L.bands.length ? Math.min.apply(null, L.bands.map(function (b) { return b.y0; })) : 0;
    L.ticks.forEach(function (t) {
      g.appendChild(svgEl('text', { x: t.x, y: obsTop + 84, 'font-size': TY.tick_font_px, 'font-weight': 700, fill: '#3f3e3b', 'text-anchor': 'middle' }, t.label));
    });
    L.lanes.forEach(function (l) {
      var lines = l.label_lines || [l.label], subs = l.sub_lines || [];
      var hTot = (lines.length * TY.lane_font_px + subs.length * TY.lane_sub_font_px) * TY.line_height;
      var y = (l.y0 + l.y1) / 2 - hTot / 2 + TY.lane_font_px;
      g.appendChild(svgLines(x0 + 14, y, lines, TY.lane_font_px, { 'font-weight': 700,
        fill: { observed: '#1c5cab', latent: '#8a3a12', context: '#0b5e0b', unresolved: '#8f2a52' }[l.kind] }));
      if (subs.length) g.appendChild(svgLines(x0 + 14, y + lines.length * TY.lane_font_px * TY.line_height, subs, TY.lane_sub_font_px, { fill: '#3f3e3b' }));
    });
  }
  // 고정 lane 이름·시간 구간 이름: 원래 이름 칸이 화면 밖으로 나가면 그래프 가장자리에 붙여 보여 준다(HTML, 11pt 이상).
  var lanePins = $('lane-pins'), bandPins = $('band-pins'), pinLayout = null;
  function buildPins(L) {
    pinLayout = L;
    lanePins.innerHTML = L.lanes.map(function (l, i) {
      return '<div class="pin pin-' + l.kind + '" data-i="' + i + '">' + esc(l.label) + '</div>';
    }).join('');
    bandPins.innerHTML = L.bands.map(function (b, i) {
      return '<div class="bpin' + (b.dated ? '' : ' undated') + '" data-i="' + i + '">' + esc(b.label) + '</div>';
    }).join('');
  }
  function pinWidth() { var w = lanePins.hidden ? 0 : lanePins.offsetWidth; return w || (window.innerWidth <= 760 ? 116 : 150); }
  function syncPins() {
    if (!pinLayout) return;
    var L = pinLayout, p = cy.pan(), z = cy.zoom(), W0 = cy.width(), H0 = cy.height();
    var far = z < READ_ZOOM;
    var showLane = !far && z * (L.extent.label_x0 + TY.label_w * 0.6) + p.x < 0;
    var hdrY = L.bands.length ? z * (Math.min.apply(null, L.bands.map(function (b) { return b.y0; })) + 60) + p.y : 1;
    var showBand = !far && hdrY < 0;
    var top0 = showBand ? 32 : 0, left0 = showLane ? (lanePins.offsetWidth || 150) : 0;
    lanePins.hidden = !showLane;
    if (showLane) {
      Array.prototype.forEach.call(lanePins.children, function (el) {
        var l = L.lanes[+el.dataset.i], y0 = Math.max(z * l.y0 + p.y, top0), y1 = Math.min(z * l.y1 + p.y, H0);
        var vis = y1 - y0 > 28;
        el.style.display = vis ? '' : 'none';
        if (vis) { el.style.top = y0 + 'px'; el.style.height = (y1 - y0) + 'px'; }
      });
    }
    bandPins.hidden = !showBand;
    if (showBand) {
      Array.prototype.forEach.call(bandPins.children, function (el) {
        var b = L.bands[+el.dataset.i], x0 = Math.max(z * b.x0 + p.x, left0), x1 = Math.min(z * b.x1 + p.x, W0);
        var vis = x1 - x0 > 90;
        el.style.display = vis ? '' : 'none';
        if (vis) { el.style.left = x0 + 'px'; el.style.width = (x1 - x0) + 'px'; }
      });
    }
  }
  var zoomInfo = $('zoom-info');
  function syncOverlay() {
    var p = cy.pan(), z = cy.zoom();
    g.setAttribute('transform', 'translate(' + p.x + ' ' + p.y + ') scale(' + z + ')');
    var far = z < READ_ZOOM;
    if (far !== syncOverlay.far) {
      syncOverlay.far = far;
      cy.batch(function () { cy.nodes().toggleClass('far', far); });
      zoomInfo.classList.toggle('far', far);
    }
    var px = Math.round(TY.node_font_px * z * 10) / 10;
    zoomInfo.textContent = '배율 ' + Math.round(z * 100) + '% · ' + (far ? '축소 지도: 글자가 11pt보다 작아 ID만 표시' : 'node 글자 ' + px + 'px');
    syncPins();
    // 시간 구간 제목이 화면 왼쪽 밖으로 잘리면 그 구간 안에서 보이는 쪽으로 옮긴다
    var left = (-p.x + (lanePins.hidden ? 0 : pinWidth())) / z;
    Array.prototype.forEach.call(g.querySelectorAll('g.band-title'), function (bt) {
      var x0 = +bt.getAttribute('data-x0'), x1 = +bt.getAttribute('data-x1');
      var dx = Math.max(0, Math.min(left - x0, x1 - x0 - 320));
      bt.setAttribute('transform', 'translate(' + dx + ' 0)');
    });
    scheduleMinimap();
  }
  cy.on('viewport', syncOverlay);

  // ------------------------------------------------------------------ 첫 화면·맞춤
  function graphSize() { cy.resize(); return { w: cy.width(), h: cy.height() }; }
  function initialViewport() {
    // 읽을 수 있는 배율(≥ min_zoom)을 먼저 정하고, 다 들어오지 않으면 왼쪽 위(시간 시작)부터 보여 준다.
    var v = VIEWS.views[state.view], init = v.initial, pad = 24, sz = graphSize();
    var box, anchor;
    if (v.policy === 'subset' && state.showContext) {
      var bb = visibleOf(v.nodes).boundingBox({ includeLabels: false });
      box = { x1: bb.x1 - TY.label_w * 0.2, y1: bb.y1 - 40, x2: bb.x2 + 40, y2: bb.y2 + 40 };
      anchor = { x: box.x1, y: box.y1 };
    } else {
      var L = activeLayout(), ex = L.extent;
      box = { x1: ex.label_x0, y1: ex.y0, x2: ex.x1, y2: ex.y1 };
      anchor = (v.layout && v.layout.anchor) || L.anchor;
    }
    var bw = box.x2 - box.x1, bh = box.y2 - box.y1;
    var zFit = Math.min((sz.w - 2 * pad) / bw, (sz.h - 2 * pad) / bh);
    var z = Math.max(init.min_zoom, Math.min(init.max_zoom, zFit));
    var fitsX = bw * z <= sz.w - 2 * pad, fitsY = bh * z <= sz.h - 2 * pad;
    if (!(fitsX && fitsY) && !(v.policy === 'subset' && state.showContext)) anchor = densestAnchor(v, anchor, box, z, sz, pad);
    var px = fitsX ? (sz.w - z * (box.x1 + box.x2)) / 2 : pad - z * anchor.x;
    var py = fitsY ? (sz.h - z * (box.y1 + box.y2)) / 2 : pad - z * anchor.y;
    cy.viewport({ zoom: z, pan: { x: px, y: py } });
    syncOverlay();
  }
  // 첫 화면 창: 이 View의 핵심 node가 가장 많이 온전히 들어오는 위치(같으면 기본 기준점 → 시간상 앞쪽). 같은 화면 크기면 항상 같은 결과.
  function focusIds(v) {
    var obs = v.core.filter(function (id) { return nodeById[id].canonical.node_type === 'OBSERVED_EVENT'; });
    if (v.policy === 'dim') return v.core.filter(function (id) { return nodeById[id].canonical.node_type !== 'OBSERVED_EVENT'; });
    return obs.length ? obs : v.core;
  }
  function densestAnchor(v, anchor0, box, z, sz, pad) {
    var Wm = (sz.w - 2 * pad) / z, Hm = (sz.h - 2 * pad) / z, padL = (pinWidth() + 20) / z, padT = 48 / z;
    var rects = focusIds(v).map(function (id) {
      var n = cy.getElementById(id), p = n.position(), d = n.data();
      return { x1: p.x - d.w / 2, x2: p.x + d.w / 2, y1: p.y - d.h / 2, y2: p.y + d.h / 2 };
    });
    function clamp(a) {
      return { x: Math.max(box.x1, Math.min(a.x, box.x2 - Wm)), y: Math.max(box.y1, Math.min(a.y, box.y2 - Hm)) };
    }
    function count(a) {
      return rects.filter(function (r) { return r.x1 >= a.x + (a.x > box.x1 + 1 ? padL : 0) && r.x2 <= a.x + Wm && r.y1 >= a.y + (a.y > box.y1 + 1 ? padT : 0) && r.y2 <= a.y + Hm; }).length;
    }
    var best = clamp(anchor0), bestN = count(best);
    if (bestN >= Math.min(2, rects.length)) return best;     // 시간상 앞쪽 기준점에 핵심 node가 충분하면 그대로
    rects.slice().sort(function (a, b) { return a.x1 - b.x1 || a.y1 - b.y1; }).forEach(function (r) {
      [{ x: r.x1 - padL - 10, y: r.y1 - padT - 10 }, { x: r.x1 - padL - 10, y: anchor0.y }].forEach(function (c) {
        var a = clamp(c), n = count(a);
        if (n > bestN) { best = a; bestN = n; }
      });
    });
    return best;
  }
  function fitAll() {
    // 전체 보기(지도): 글자가 11pt보다 작아질 수 있다. node는 ID만 표시된다.
    var ex = activeLayout().extent, sz = graphSize(), pad = 20;
    var z = Math.min((sz.w - 2 * pad) / (ex.x1 - ex.label_x0), (sz.h - 2 * pad) / (ex.y1 - ex.y0));
    z = Math.max(cy.minZoom(), Math.min(1.2, z));
    cy.viewport({ zoom: z, pan: { x: (sz.w - z * (ex.label_x0 + ex.x1)) / 2, y: (sz.h - z * (ex.y0 + ex.y1)) / 2 } });
    syncOverlay();
  }
  function readableZoom() {
    var sz = graphSize(), z = Math.max(1, cy.zoom() < READ_ZOOM ? 1 : cy.zoom());
    cy.zoom({ level: z, renderedPosition: { x: sz.w / 2, y: sz.h / 2 } });
  }

  // ------------------------------------------------------------------ 상태 적용(보이기·흐리기·강조)
  var CLASS_RESET = 'hidden dim hl hl-rej grpA grpB pair iv-off iv-removed iv-remaining iv-PATH_BREAKS iv-PATH_WEAKENS iv-PATH_REMAINS iv-UNKNOWN iv-target iv-path cfg-ON cfg-PARTIAL cfg-UNSPECIFIED cfg-OFF';
  function ivRows() { return state.iv ? IV.rows.filter(function (r) { return r.canonical.mechanism === state.iv; }) : []; }

  function applyState() {
    var sel = W.selections[state.world];
    var view = VIEWS.views[state.view];
    var subset = isSubsetMode();
    var inView = toSet(view.nodes);
    var always = toSet(sel.always_visible);
    var dimW = toSet(sel.dim), hideW = toSet(sel.hideable), hlW = toSet(sel.highlight);
    var rows = ivRows();
    var ivPath = {};
    rows.forEach(function (r) { r.path_nodes.forEach(function (x) { ivPath[x] = true; }); });
    cy.batch(function () {
      cy.elements().removeClass(CLASS_RESET);
      cy.nodes().forEach(function (n) {
        var d = n.data(), id = d.id, hide = false, dim = false, outside = false;
        // 1) View 범위(시각적 필터). subset View는 범위 밖을 숨기고, Overview·J·'전체 주변 맥락 표시'는 흐리게만 한다.
        if (!has(inView, id)) { if (subset) outside = true; else if (!has(ivPath, id)) dim = true; }
        // 2) 표시 필터·world 선택(분석상 ON/OFF 아님)
        if (!has(state.status, d.sgroup)) hide = true;
        if (d.mech && !has(state.mech, d.mech)) hide = true;
        if (has(dimW, id)) { if (state.hideOthers && has(hideW, id)) hide = true; else dim = true; }
        // AUDIT5:BACKBONE_GUARD — 필터·world 선택·개입은 OBSERVED backbone(관측 사건·공통 결말)을 숨기지 못한다
        if (BACKBONE[id] || has(always, id)) hide = false;
        // AUDIT5:VIEW_SCOPE — View 범위 밖 node는 subset View에서만 숨긴다. 숨긴 OBSERVED 수는 #banner-view에 항상 표시된다.
        if (outside) hide = true;
        if (hide) n.addClass('hidden');
        else if (dim) n.addClass('dim');
        if (has(hlW, id)) n.addClass(sel.rejected ? 'hl-rej' : 'hl');
        var label = d.base, extra = 0;
        if (d.ntype === 'MECHANISM' && state.world !== 'ALL') {
          var v = sel.mechanism_state[id];
          n.addClass('cfg-' + v);
          label += '\n' + state.world + ': ' + W.config_display[v].label; extra += 1;
        }
        if (state.iv && id === state.iv) { label += '\ndo(' + id + '=OFF)'; extra += 1; }
        n.data('label', label);
        n.data('h', d.h0 + extra * TY.line_px);
      });
      if (view.groups) {
        view.groups.A.forEach(function (id) { cy.getElementById(id).addClass('grpA'); });
        view.groups.B.forEach(function (id) { cy.getElementById(id).addClass('grpB'); });
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
    applySelection();
    renderBanners();
    renderWorldButtons();
    renderTabs();
    renderWorldPanel();
    renderIvPanel();
    scheduleMinimap();
  }

  // 선택한 node의 들어오는·나가는 edge 강조, 관련 없는 edge 흐림
  function applySelection() {
    cy.batch(function () {
      cy.elements().removeClass('sel-in sel-out sel-nbr faded');
      var n = cy.$('node:selected');
      if (!n.length) return;
      n.incomers('edge').addClass('sel-in');
      n.outgoers('edge').addClass('sel-out');
      n.neighborhood('node').addClass('sel-nbr');
      cy.edges().difference(n.connectedEdges()).addClass('faded');
    });
  }

  // ------------------------------------------------------------------ 배너·탭
  function renderBanners() {
    var sel = W.selections[state.world];
    var b = $('banner-world');
    if (sel.rejected) { b.hidden = false; b.innerHTML = '<b>' + esc(state.world) + ' REJECTED</b> — ' + esc(sel.banner); }
    else { b.hidden = true; b.innerHTML = ''; }
    var iv = $('banner-iv');
    if (state.iv) {
      var outside = [];
      if (isSubsetMode()) {
        var inView = toSet(VIEWS.views[state.view].nodes);
        ivRows().forEach(function (r) { r.path_nodes.forEach(function (x) { if (!inView[x] && outside.indexOf(x) < 0) outside.push(x); }); });
      }
      iv.hidden = false;
      iv.innerHTML = '<b>do(' + esc(state.iv) + '=OFF)</b> — ' + esc(IV.note) +
        ' 붉은 점선 = 사라지는 후보, 초록 = 남는 후보, 구조 변수 색 = 저장된 결과.' +
        (outside.length ? ' <span class="small">이 View 밖 경로 node ' + outside.length + '개(' + esc(outside.join(', ')) + ')는 ‘전체 주변 맥락 표시’에서 보입니다.</span>' : '');
    } else { iv.hidden = true; iv.innerHTML = ''; }
    var v = VIEWS.views[state.view];
    $('view-desc').innerHTML = '<b>' + esc(v.title) + '</b> · ' + esc(v.desc) +
      (v.cross_edges ? ' <span class="chip flag">A↔B 직접 edge ' + v.cross_edges.length + '개</span>' : '') +
      ' <details class="scope" id="view-scope"><summary>표시 node ' + v.nodes.length + '개 · edge ' + v.edges.length + '개 — 선택 규칙 보기</summary>' +
      esc(v.scope_rule) + '</details>';
    // AUDIT5:VIEW_HIDDEN_NOTICE — 숨긴 OBSERVED가 사라진 것으로 읽히지 않도록 개수·ID를 항상 보여 준다
    var vb = $('banner-view');
    var toggle = '<label class="check context-toggle"><input type="checkbox" id="show-context"' + (state.showContext ? ' checked' : '') +
      '> 전체 주변 맥락 표시</label>';
    if (v.policy === 'subset') {
      var nHiddenOther = META.counts.nodes - v.nodes.length - v.hidden_observed.length;
      vb.hidden = false;
      vb.title = v.notice;
      vb.innerHTML = '<b>시각적 필터</b> · ' +
        (state.showContext
          ? '전체 node를 Overview 좌표로 함께 표시 중 — 이 View 밖 node는 흐리게. '
          : '이 화면에서 숨긴 OBSERVED node <b id="hidden-observed-count">' + v.hidden_observed.length + '</b>개' +
            (v.hidden_observed.length ? ' <details><summary>ID</summary> ' + esc(v.hidden_observed.join(', ')) + '</details>' : '') +
            ' · 그 밖의 node ' + nHiddenOther + '개 — ') +
        '<span class="notice-text">삭제·부정이 아니라 표시 범위만 줄인 것(분석상 ON/OFF 아님).</span> ' + toggle;
      $('show-context').addEventListener('change', function (ev) { setShowContext(ev.target.checked); });
    } else if (v.policy === 'dim') {
      vb.hidden = false;
      vb.innerHTML = '<b>시각적 강조</b> · 이 View 밖 OBSERVED node는 숨기지 않고 흐리게 남깁니다. 분석상 ON/OFF가 아닙니다.';
    } else { vb.hidden = true; vb.innerHTML = ''; }
  }
  function renderTabs() {
    var nav = $('view-tabs');
    if (!nav.childElementCount) {
      VIEWS.order.forEach(function (id) {
        var b = document.createElement('button');
        b.type = 'button'; b.setAttribute('role', 'tab'); b.dataset.view = id; b.textContent = VIEWS.views[id].label;
        b.title = VIEWS.views[id].desc;
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
      OBSERVED: '고정 backbone — 필터로 숨기지 않음', DERIVED: 'edge 상태(관측 node 사이 기록 근거 연결). edge에만 적용',
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
      ['UNRESOLVED (이중 테두리)', '#fcf0f5', '#b83a6b', '', 'double']
    ];
    var h = '<div class="grp">Node (색 + 모양 + 테두리)</div>';
    nodesL.forEach(function (r) {
      var shape;
      if (r[4] === 'hex') shape = '<polygon points="8,1 28,1 35,9 28,17 8,17 1,9" ';
      else if (r[4] === 'cut') shape = '<polygon points="5,1 31,1 35,5 35,13 31,17 5,17 1,13 1,5" ';
      else if (r[4] === 'barrel') shape = '<rect x="1" y="1" width="34" height="16" rx="10" ry="8" ';
      else if (r[4] === 'sq') shape = '<rect x="1" y="1" width="34" height="16" ';
      else shape = '<rect x="1" y="1" width="34" height="16" rx="4" ';
      var extra = r[4] === 'double' ? '<rect x="4" y="4" width="28" height="10" rx="2" fill="none" stroke="' + r[2] + '" stroke-width="1.4"/>' : '';
      h += '<div class="row"><svg width="36" height="18" aria-hidden="true">' + shape + 'fill="' + r[1] + '" stroke="' + r[2] + '" stroke-width="' + (r[4] === 'double' ? 1.4 : 2) + '" stroke-dasharray="' + r[3] + '"/>' + extra + '</svg><span>' + esc(r[0]) + '</span></div>';
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
        eh += '<div class="row" title="' + esc(s.ko) + '"><svg width="36" height="12" aria-hidden="true"><line x1="1" y1="6" x2="28" y2="6" stroke="' + s.color + '" stroke-width="2.4" stroke-dasharray="' + da + '"/>' +
          '<path d="M35 6 l-7 -5 l0 10 z" fill="' + s.color + '"/></svg><span><code>' + esc(p[0]) + '</code> <span class="muted">' + esc(s.ko) + '</span></span></div>';
      });
    });
    eh += '<div class="row muted">선 굵기: OBSERVED edge 굵게, DERIVED edge 보통, 분석 edge 얇고 옅게. edge 이름은 마우스를 올리거나 node·edge를 선택하면 보입니다.</div>';
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
    if (!ks.length) return '<p class="muted">canonical edge로 연결된 mechanism 없음</p>';
    return '<ul class="plain">' + ks.map(function (m) {
      return '<li>' + nodeLink(m) + ' ' + esc(META.mechanism_display[m] || '') + ' <span class="muted">via ' + rm[m].map(edgeLink).join(' → ') + '</span></li>';
    }).join('') + '</ul>';
  }
  function incidentEdgesHtml(id) {
    var ins = [], outs = [];
    SD.edges.forEach(function (e) {
      if (e.canonical.dst === id) ins.push(e);
      if (e.canonical.src === id) outs.push(e);
    });
    function li(e, other) {
      var s = META.edge_styles[e.canonical.edge_type] || {};
      return '<li>' + edgeLink(e.id) + ' <code>' + esc(e.canonical.edge_type) + '</code> <span class="muted">' + esc(s.ko || '') + '</span> ' +
        nodeLink(other) + ' ' + esc((nodeById[other] || {}).short_label ? nodeById[other].short_label.replace(other + ' · ', '') : '') + ' ' + chip('st-' + e.status_group, e.canonical.sd_status) + '</li>';
    }
    return '<h4>관련 edge — 들어오는 edge (' + ins.length + ')</h4><ul class="plain">' + (ins.map(function (e) { return li(e, e.canonical.src); }).join('') || '<li class="muted">없음</li>') + '</ul>' +
      '<h4>관련 edge — 나가는 edge (' + outs.length + ')</h4><ul class="plain">' + (outs.map(function (e) { return li(e, e.canonical.dst); }).join('') || '<li class="muted">없음</li>') + '</ul>';
  }
  function worldsHtml(n) {
    var c = n.canonical;
    if (c.node_type === 'MECHANISM') return '<p>world별 값은 위 World configuration 표.</p>';
    var used = W.order.filter(function (wid) { return splitIds(W.configurations[wid].latent_bridges).indexOf(n.id) >= 0; });
    var rows = [['canonical worlds 값', c.worlds]];
    if (c.node_type === 'CANDIDATE_BRIDGE') rows.push(['latent_bridges에 이 후보를 쓰는 world', used.length ? used.join(', ') : '없음']);
    if (n.common_outcome) rows.push(['공통 결말', '모든 world에 공통인 OBSERVED 결말']);
    return kv(rows);
  }
  function unresolvedHtml(id) {
    var items = [];
    SD.edges.forEach(function (e) {
      var c = e.canonical;
      if (c.edge_type === 'CONDITIONS' && c.dst === id) items.push('<li>' + nodeLink(c.src) + ' ' + esc(nodeById[c.src].canonical.label) + ' <span class="muted">(CONDITIONS ' + edgeLink(e.id) + ')</span></li>');
      if (e.frozen && (c.src === id || c.dst === id) && (e.frozen.condition || e.frozen.uncertainty_status)) {
        items.push('<li>' + edgeLink(e.id) + ' ' + esc([e.frozen.condition ? 'condition: ' + e.frozen.condition : '', e.frozen.uncertainty_status ? 'uncertainty: ' + e.frozen.uncertainty_status : ''].filter(Boolean).join(' · ')) + '</li>');
      }
    });
    var inc = SD.edges.filter(function (e) { return e.canonical.src === id || e.canonical.dst === id; }).map(function (e) { return e.id; });
    SD.nodes.forEach(function (u) {
      if (u.canonical.node_type !== 'UNRESOLVED_ITEM' || u.id === id) return;
      var refs = (u.canonical.detail.match(/OE\d{3}/g) || []).filter(function (o) { return inc.indexOf(o) >= 0; });
      if (refs.length) items.push('<li>' + nodeLink(u.id) + ' ' + esc(u.canonical.label) + ' <span class="muted">(가리키는 edge ' + esc(refs.join(', ')) + ')</span></li>');
    });
    return items.length ? '<ul class="plain">' + items.join('') + '</ul>' : '<p class="muted">canonical data에 연결된 UNRESOLVED 의존 없음</p>';
  }
  function viewsHtml(id) {
    return '<p>' + viewsOfNode(id).map(function (v) { return '<button type="button" class="linkish" data-view-go="' + v + '">' + esc(VIEWS.views[v].label) + '</button>'; }).join(' · ') +
      '</p><p class="small muted">View는 표시 범위일 뿐이며 node의 상태를 바꾸지 않습니다.</p>';
  }
  function headCard(n, dateText) {
    var c = n.canonical;
    return '<div class="card-head"><div class="nid">' + esc(n.id) + '</div><div class="ntitle">' + esc(c.label) + '</div>' +
      '<p class="chips">' + chip('st-' + n.status_group, c.sd_status) + ' ' + chip('flag', c.node_type) +
      (c.worlds === 'ALL (공통)' ? ' ' + chip('flag flag-common', '모든 world 공통') : '') +
      (n.common_outcome ? ' ' + chip('flag flag-common', '공통 결말') : '') + '</p>' +
      (dateText ? '<p class="ndate">날짜: ' + esc(dateText) + '</p>' : '') + '</div>';
  }

  function renderNodeDetail(id) {
    var n = nodeById[id];
    if (!n) return;
    var c = n.canonical, t = c.node_type, h = '';
    if (t === 'OBSERVED_EVENT') {
      var o = n.observed;
      h += headCard(n, (o.occurrence_text || '') + ' (t_min ' + (o.t_min || '?') + ' – t_max ' + (o.t_max || '?') + ')' + (n.layout.dated ? '' : ' · 날짜 미기록(시간 축 밖)'));
      h += '<h4>canonical summary (episode summary, 사료 수준)</h4><div class="quote">' + esc(o.summary) + '</div>';
      if (o.caution) h += '<p class="muted">주의: ' + esc(o.caution) + '</p>';
      h += kv([['node_id', id], ['status', c.sd_status + ' (frozen: ' + c.frozen_status + ')'], ['기록일', o.record_lunar_date],
        ['층(layer)', o.layer], ['branch lane', o.branch], ['인식 floor', o.epistemic_floor], ['진술/기록 주체', o.attesting_actor]]);
      h += '<h4>Source fact ID — Confirmed fact (' + splitIds(o.member_fact_ids).length + ')</h4><ul class="plain">';
      splitIds(o.member_fact_ids).forEach(function (f) {
        var cf = FACTS.confirmed_facts[f] || {};
        h += '<li><b>' + esc(f) + '</b> <span class="muted">' + esc(cf.confirmation_level || '') + '</span><br>' + esc(cf.confirmed_statement || '') + '</li>';
      });
      h += '</ul>';
      if (o.member_clauses) h += '<p class="muted">사용한 절: ' + esc(o.member_clauses) + '</p>';
      h += '<h4>Source record</h4><ul class="plain">';
      splitIds(o.source_record_ids).forEach(function (s) {
        var r = FACTS.source_records[s] || {};
        h += '<li><b>' + esc(s) + '</b> ' + esc(r.source_work || '') + ' ' + esc(r.record_lunar_date || '') + '<br>' + esc(r.source_title || '') +
          (r.source_url ? ' <a href="' + esc(r.source_url) + '" target="_blank" rel="noopener">원문</a>' : '') + '</li>';
      });
      h += '</ul>';
      if (o.identity_links) h += '<p>동일성 대장: ' + esc(o.identity_links) + '</p>';
    } else if (t === 'CANDIDATE_BRIDGE') {
      var r = CAND.rows[id] || {}, gp = CAND.gaps[r.gap_id] || {};
      h += '<div class="callout latent">사료에 직접 적힌 사실이 아니라 빈칸을 설명하기 위한 가설</div>' + headCard(n, '');
      h += '<h4>canonical summary (bridge claim)</h4><div class="quote">' + esc(r.latent_bridge_claim) + '</div>';
      h += kv([['candidate ID', id], ['gap ID', r.gap_id + (gp.title ? ' · ' + gp.title : '')],
        ['source support', r.source_support], ['plausibility', r.plausibility_grade], ['institutional fit', r.institutional_fit],
        ['temporal fit', r.temporal_fit], ['assumption cost (n_assumptions)', r.n_assumptions], ['추가 가정', r.extra_assumptions],
        ['contradiction risk', r.contradiction_risk], ['final grade (overall)', r.overall], ['evidence grade', r.evidence_grade],
        ['bridge directly attested', r.bridge_directly_attested], ['bridge evidence', r.bridge_evidence],
        ['prune decision', r.prune_decision], ['identity conditions', r.identity_conditions], ['주 메커니즘', c.mechanism],
        ['관측 왼쪽', r.observed_left], ['관측 오른쪽', r.observed_right], ['source fact (support_basis)', r.support_basis]]);
      h += '<h4>약점·충돌</h4>' + kv([['conflicts', r.conflicts || '-'], ['notes', r.notes], ['재감사 이유', r.reaudit_reason]]);
    } else if (t === 'INSTITUTIONAL_CONTEXT' || t === 'ENV_CONTEXT') {
      var f = n.context_feature || {};
      h += '<div class="callout context">CONTEXT — 제약조건·호환성일 뿐, 사건 발생 자체를 증명하지 않음</div>' + headCard(n, '');
      h += '<h4>canonical summary</h4><div class="quote">' + esc(c.detail) + '</div>';
      if (t === 'INSTITUTIONAL_CONTEXT') {
        h += kv([['feature ID', f.feature_id], ['이름', f.feature_name]].concat(Object.keys(f).filter(function (k) {
          return ['feature_id', 'feature_name'].indexOf(k) < 0;
        }).map(function (k) { return [k, f[k]]; })));
      } else {
        var src = n.context_source || {};
        h += kv([['feature ID', f.env_id], ['context 기록일', src.record_lunar_date + ' (context 기록일 — 사건 날짜 lane에 두지 않음)'],
          ['source fact', src.member_fact_ids], ['source record', src.source_record_ids]].concat(
          Object.keys(f).filter(function (k) { return k !== 'env_id'; }).map(function (k) { return [k, f[k]]; })));
      }
    } else if (t === 'MECHANISM') {
      var def = FACTS.definitions[id] || {};
      h += '<div class="callout latent">LATENT 분석 변수 — 사료에 직접 적힌 사실이 아니라 빈칸을 설명하기 위한 가설 구조</div>' + headCard(n, '');
      h += '<h4>canonical summary</h4><div class="quote">' + esc(c.detail) + '</div>';
      h += kv([['mechanism', id + ' · ' + META.mechanism_display[id]], ['canonical 이름', c.label], ['branch', c.branch]]);
      h += '<h4>정의 (mechanism_definitions.csv)</h4>' + kv(Object.keys(def).map(function (k) { return [k, def[k]]; }));
      h += '<h4>World configuration</h4><table class="tbl"><tr><th>world</th><th>값</th><th>근거</th></tr>' + W.order.map(function (wid) {
        var cf = W.configurations[wid], v = cf[id], rej = cf.role_type === 'REJECTED';
        return '<tr class="' + (rej ? 'rejected' : '') + '"><td>' + esc(wid) + (rej ? ' REJECTED' : '') + '</td><td>' + chip(W.config_display[v].css, v) + '</td><td>' + esc(cf[id + '_basis']) + '</td></tr>';
      }).join('') + '</table><p class="muted">UNSPECIFIED ≠ OFF.</p>';
    } else if (t === 'STRUCTURAL_VARIABLE') {
      var rule = IX.rules.filter(function (r) { return r['var'] === id; })[0] || {};
      h += '<div class="callout latent">LATENT 구조 변수 — 사료에 직접 적힌 사실이 아니라 빈칸을 설명하기 위한 가설 규칙</div>' + headCard(n, '');
      h += '<h4>canonical summary</h4><div class="quote">' + esc(c.detail) + '</div>';
      h += kv([['변수', id], ['연산', rule.op], ['규칙', rule.rule], ['설명', rule.desc], ['입력', rule.inputs], ['입력 후보', rule.input_candidates],
        ['gap', rule.gap], ['관측 대상', rule.target], ['제약', rule.constraint], ['branch', c.branch]]);
      h += '<p class="muted">질적 구조 규칙이다. 역사적으로 그렇게 됐다는 단정이 아니다.</p>';
    } else if (t === 'UNRESOLVED_ITEM') {
      h += headCard(n, '');
      h += kv([['항목', id], ['내용', c.label], ['관측 영향', c.detail], ['worlds', c.worlds]]);
      h += '<div class="callout info">확정하지 않은 항목이다. 후보의 성립 조건(CONDITIONS)으로만 남고, Audit 4에서 UNRESOLVED(unresolved_item)로 기록된다.</div>';
    }
    h += incidentEdgesHtml(id);
    h += '<h4>관련 Mechanism (canonical edge 경로)</h4>' + relatedMechHtml(n);
    h += '<h4>관련 World</h4>' + worldsHtml(n);
    h += '<h4>UNRESOLVED 의존</h4>' + unresolvedHtml(id);
    h += '<h4>이 node가 들어 있는 View</h4>' + viewsHtml(id);
    $('p-detail').innerHTML = h;
    showPane('detail');
  }

  function renderEdgeDetail(id) {
    var e = edgeById[id];
    if (!e) return;
    var c = e.canonical, s = META.edge_styles[c.edge_type] || {}, f = e.frozen || {};
    var h = '<div class="card-head"><div class="nid">edge ' + esc(id) + '</div><div class="ntitle">' + esc(c.edge_type) + (s.ko ? ' · ' + esc(s.ko) : '') + '</div>' +
      '<p class="chips">' + chip('st-' + e.status_group, c.sd_status) + ' ' + chip('flag', c.origin) + '</p></div>';
    h += kv([['edge ID', id], ['type', c.edge_type + (s.ko ? ' · ' + s.ko : '')], ['status', c.sd_status], ['origin', c.origin],
      ['src', nodeLink(c.src) + ' ' + esc((nodeById[c.src] || {}).short_label || ''), true],
      ['dst', nodeLink(c.dst) + ' ' + esc((nodeById[c.dst] || {}).short_label || ''), true],
      ['source basis', e.frozen ? [f.basis, f.supporting].filter(Boolean).join(' · ') : (c.note || '분석 edge(Super-DAG) — 근거는 node 상세의 canonical 값')],
      ['caution', e.frozen ? (f.caution || '-') : (c.sd_status === 'LATENT_MECHANISM' ? 'LATENT 분석 edge — 사료에 직접 적힌 연결이 아님' : (c.sd_status === 'CONTEXT' ? 'CONTEXT edge — 사건 발생 자체를 증명하지 않음' : '-'))],
      ['note', c.note]]);
    if (e.frozen) {
      h += '<h4>frozen observed edge 필드</h4>' + kv([['basis', f.basis], ['status', f.status], ['claim_level', f.claim_level], ['condition', f.condition],
        ['supporting', f.supporting], ['rationale', f.rationale], ['caution', f.caution], ['uncertainty_status', f.uncertainty_status], ['review_decision', f.review_decision]]);
    }
    $('p-detail').innerHTML = h;
    showPane('detail');
  }

  function defaultDetail() {
    $('p-detail').innerHTML = '<h3>상세</h3><p class="empty">그래프에서 node나 edge를 누르면 canonical 값이 여기에 나옵니다.</p>' +
      '<div class="callout info">OBSERVED = 확정 사실에서 만든 관측 사건(고정). LATENT = 사료가 알려주지 않는 중간 과정을 설명하는 가설·분석 변수. ' +
      'CONTEXT = 제도·환경 제약(사건 아님). UNRESOLVED = 확정하지 않은 항목.</div>' +
      kv([['frozen graph hash', META.frozen_hash], ['node', META.counts.nodes], ['edge', META.counts.edges],
        ['node status', Object.keys(META.counts.node_status).map(function (k) { return k + ' ' + META.counts.node_status[k]; }).join(' · ')],
        ['edge status', Object.keys(META.counts.edge_status).map(function (k) { return k + ' ' + META.counts.edge_status[k]; }).join(' · ')]]) +
      '<p class="muted">' + esc(VIEWS.note) + '</p>' +
      '<h4>화면 규칙</h4><p class="muted">' + esc(META.role_note) + ' 좌표 규칙: ' + esc(META.layout_rule) + '</p>' +
      '<p class="muted">' + esc(TY.note) + '</p>';
  }

  // ------------------------------------------------------------------ World 구성 패널
  function renderWorldPanel() {
    var h = '<h3>World configuration</h3>';
    h += '<div class="callout info"><b>UNSPECIFIED ≠ OFF</b> — UNSPECIFIED는 관련 후보가 없어 작동 여부를 말하지 않는다는 뜻이다. ' +
      (W.off_count === 0 ? '현재 어느 world에도 OFF 값은 없다.' : 'OFF 값 ' + W.off_count + '개.') + '</div>';
    if (state.world === 'ALL') {
      h += '<div class="tbl-scroll"><table class="tbl"><tr><th>world</th>' + MECHS.map(function (m) { return '<th>' + m + '</th>'; }).join('') + '</tr>';
      W.order.forEach(function (wid) {
        var cf = W.configurations[wid], rej = cf.role_type === 'REJECTED';
        h += '<tr class="' + (rej ? 'rejected' : '') + '"><td>' + esc(wid) + (rej ? ' REJECTED' : '') + '</td>' + MECHS.map(function (m) {
          return '<td>' + chip(W.config_display[cf[m]].css, cf[m] === 'UNSPECIFIED' ? 'UNSPEC.' : cf[m]) + '</td>';
        }).join('') + '</tr>';
      });
      h += '</table></div><p class="muted">UNSPEC. = UNSPECIFIED. W6은 REJECTED(대조군)로 공존·개입 분석에서 제외된다.</p>';
    } else {
      var cf = W.configurations[state.world], nw = W.narratives[state.world] || {}, sel = W.selections[state.world];
      if (sel.rejected) h += '<div class="callout warn"><b>' + esc(state.world) + ' REJECTED</b> — ' + esc(sel.banner) + '</div>';
      h += kv([['world', state.world + (nw.name ? ' · ' + nw.name : '')], ['role_type', cf.role_type], ['latent bridges', cf.latent_bridges],
        ['질문', nw.story_question], ['최저 등급', nw.min_grade], ['가정 수', nw.n_assumptions], ['주요 약점', nw.main_weaknesses]]);
      h += '<table class="tbl"><tr><th>mechanism</th><th>값</th><th>근거</th></tr>' + MECHS.map(function (m) {
        return '<tr><td><b>' + m + '</b> ' + esc(META.mechanism_display[m]) + '</td><td>' + chip(W.config_display[cf[m]].css, cf[m]) + '</td><td>' + esc(cf[m + '_basis']) + '</td></tr>';
      }).join('') + '</table>';
      h += '<p class="muted">값 뜻: ' + Object.keys(W.config_display).map(function (k) { return k + ' = ' + W.config_display[k].note; }).join(' / ') + '</p>';
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
    var h = '<h3>메커니즘 공존</h3><p class="muted">' + esc(IX.note) + '</p>';
    h += '<div class="pair-pick"><select id="pair-a" aria-label="mechanism A">' + opts(a) + '</select><span>×</span><select id="pair-b" aria-label="mechanism B">' + opts(b) + '</select></div>';
    h += '<div class="tbl-scroll"><table class="matrix"><tr><th></th>' + MECHS.map(function (m) { return '<th>' + m + '</th>'; }).join('') + '</tr>';
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
    h += '</table></div><p class="muted">C = COMPATIBLE · P = PARTIALLY_COMPATIBLE · X = INCOMPATIBLE · ? = UNKNOWN · * = Audit 4 UNRESOLVED 있음</p>';
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
    h += '<h4>대체·배타·보완 (canonical 규칙과 relation 값)</h4><ul class="plain">';
    IX.rules.filter(function (r) { return (r.op === 'OR' || r.op === 'XOR') && splitIds(r.inputs).filter(function (x) { return MECHS.indexOf(x) >= 0; }).length >= 2; }).forEach(function (r) {
      var ins = splitIds(r.inputs);
      h += '<li><code>' + esc(r['var']) + '</code> = ' + esc(ins.join(r.op === 'OR' ? ' OR ' : ' XOR ')) + ' <span class="muted">(' + (r.op === 'OR' ? '대체' : '배타') + ')</span></li>';
    });
    var comp = IX.pairs.filter(function (p) { return p.canonical.relation === 'COMPLEMENT'; }).map(function (p) { return p.key; });
    h += '<li>보완(relation = COMPLEMENT): ' + esc(comp.join(', ') || '없음') + '</li>';
    var mixed = IX.pairs.filter(function (p) { return p.canonical.relation.indexOf('COMPLEMENT') >= 0 && p.canonical.relation !== 'COMPLEMENT'; });
    h += '<li>보완 + 대체/배타: ' + esc(mixed.map(function (p) { return p.key + ' (' + p.canonical.relation + ')'; }).join(', ') || '없음') + '</li></ul>';
    h += '<p class="muted">공존 분석 제외 world: ' + esc(IX.excluded_worlds.join(', ')) + ' (REJECTED)</p>';
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
      h += '<p>관측 사건(OBSERVED)은 개입 중에도 그대로 남는다. 바뀌는 것은 그 앞의 설명 경로뿐이다.</p>';
    }
    $('p-iv').innerHTML = h;
    Array.prototype.forEach.call(document.querySelectorAll('[data-iv]'), function (b) {
      b.addEventListener('click', function () { setIntervention(b.dataset.iv || null); });
    });
  }

  // ------------------------------------------------------------------ 패널 탭
  function showPane(name) {
    Array.prototype.forEach.call(document.querySelectorAll('.ptabs button'), function (b) {
      b.classList.toggle('active', b.dataset.ptab === name); b.setAttribute('aria-selected', String(b.dataset.ptab === name));
    });
    Array.prototype.forEach.call(document.querySelectorAll('.pbody'), function (p) { p.hidden = p.dataset.pane !== name; });
  }
  Array.prototype.forEach.call(document.querySelectorAll('.ptabs button'), function (b) {
    b.addEventListener('click', function () { showPane(b.dataset.ptab); });
  });
  document.querySelector('.panel').addEventListener('click', function (ev) {
    var t = ev.target.closest('[data-goto]');
    if (t) { focusNode(t.dataset.goto); return; }
    var te = ev.target.closest('[data-goto-edge]');
    if (te) { focusEdge(te.dataset.gotoEdge); return; }
    var tv = ev.target.closest('[data-view-go]');
    if (tv) { var sel = cy.$('node:selected').map(function (n) { return n.id(); })[0]; setView(tv.dataset.viewGo); if (sel) focusNode(sel); }
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
        var pos = it.text.indexOf(q), why = score === 3 ? it.text.substr(Math.max(0, pos - 24), 80).replace(/\u0001/g, '·') : '';
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
  var FOCUS_ZOOM = 1.15;                    // 검색·링크로 이동할 때 배율(node 글자 18.4px)
  function centerOn(ele, zoom) {
    var sz = graphSize(), p = ele.isNode() ? ele.position() : ele.midpoint();
    cy.viewport({ zoom: zoom, pan: { x: sz.w / 2 - zoom * p.x, y: sz.h / 2 - zoom * p.y } });
    syncOverlay();
  }
  function focusNode(id) {
    var n = cy.getElementById(id);
    if (!n || !n.length) return false;
    if (n.hasClass('hidden')) {
      // 지금 View 범위 밖이거나 필터로 숨겨진 node: View를 Overview로 바꾸고 그 node를 가리는 필터를 푼다
      var view = VIEWS.views[state.view];
      if (view.nodes.indexOf(id) < 0 && view.policy === 'subset' && !state.showContext) { state.view = 'overview'; state.showContext = false; applyPositions(); }
      state.hideOthers = false;
      var d = n.data();
      state.status[d.sgroup] = true;
      if (d.mech) state.mech[d.mech] = true;
      syncFilterInputs();
      applyState();
    }
    cy.$(':selected').unselect();
    cy.nodes().removeClass('search-hit');
    n.select(); n.addClass('search-hit');
    applySelection();
    centerOn(n, Math.min(1.8, Math.max(cy.zoom(), FOCUS_ZOOM)));
    renderNodeDetail(id);
    return true;
  }
  function focusEdge(id) {
    var e = cy.getElementById(id);
    if (!e || !e.length) return false;
    if (e.hasClass('hidden')) { focusNode(e.data('source')); }
    cy.$(':selected').unselect();
    e.select();
    applySelection();
    centerOn(e, Math.min(1.8, Math.max(cy.zoom(), READ_ZOOM + 0.05)));
    renderEdgeDetail(id);
    return true;
  }
  cy.on('tap', 'node', function (ev) { cy.nodes().removeClass('search-hit'); renderNodeDetail(ev.target.id()); setTimeout(applySelection, 0); });
  cy.on('tap', 'edge', function (ev) { renderEdgeDetail(ev.target.id()); setTimeout(applySelection, 0); });
  cy.on('tap', function (ev) { if (ev.target === cy) setTimeout(applySelection, 0); });
  var tip = $('tooltip');
  cy.on('mouseover', 'node', function (ev) {
    var n = nodeById[ev.target.id()], c = n.canonical, p = ev.renderedPosition;
    tip.innerHTML = '<b>' + esc(n.id) + '</b> ' + esc(c.label) + '<span class="t-sub">' + esc(c.sd_status) + ' · ' + esc(c.node_type) +
      (n.observed ? ' · ' + esc(n.observed.occurrence_text) : '') + '</span>';
    tip.style.left = Math.max(4, Math.min(p.x + 14, cy.width() - 360)) + 'px'; tip.style.top = (p.y + 14) + 'px'; tip.hidden = false;
  });
  cy.on('mouseout', 'node', function () { tip.hidden = true; });
  cy.on('mouseover', 'edge', function (ev) { ev.target.addClass('hover'); });
  cy.on('mouseout', 'edge', function (ev) { ev.target.removeClass('hover'); });
  cy.on('viewport', function () { tip.hidden = true; });

  // 휠 = 스크롤(상하, Shift는 좌우), Ctrl/⌘ + 휠·핀치 = 확대/축소. 글자 크기를 유지한 채 탐색하도록.
  $('graph-wrap').addEventListener('wheel', function (ev) {
    if (ev.ctrlKey || ev.metaKey) return;            // cytoscape 기본 확대/축소
    ev.preventDefault(); ev.stopPropagation();
    var k = ev.deltaMode === 1 ? 32 : (ev.deltaMode === 2 ? cy.height() : 1);
    var dx = (ev.shiftKey && !ev.deltaX ? ev.deltaY : ev.deltaX) * k, dy = (ev.shiftKey && !ev.deltaX ? 0 : ev.deltaY) * k;
    cy.panBy({ x: -dx, y: -dy });
  }, { capture: true, passive: false });
  // 키보드: 그래프에 포커스가 있을 때 화살표로 이동, +/- 확대·축소
  $('graph-wrap').addEventListener('keydown', function (ev) {
    var step = 120, m = { ArrowLeft: [step, 0], ArrowRight: [-step, 0], ArrowUp: [0, step], ArrowDown: [0, -step] }[ev.key];
    if (m) { cy.panBy({ x: m[0], y: m[1] }); ev.preventDefault(); }
    else if (ev.key === '+' || ev.key === '=') { $('zoom-in').click(); ev.preventDefault(); }
    else if (ev.key === '-') { $('zoom-out').click(); ev.preventDefault(); }
  });

  // ------------------------------------------------------------------ 미니맵(전체 위치 안내 · 글자 없음)
  var mm = $('minimap'), mctx = mm.getContext('2d'), mmPending = false;
  var MM_FILL = { OBSERVED: '#256abf', LATENT: '#c4501f', CONTEXT: '#008300', UNRESOLVED: '#b83a6b', DERIVED: '#8ea0bd' };
  function scheduleMinimap() { if (!mmPending) { mmPending = true; requestAnimationFrame(drawMinimap); } }
  function mmTransform() {
    var ex = activeLayout().extent, W0 = mm.width, H0 = mm.height;
    var s = Math.min(W0 / (ex.x1 - ex.label_x0), H0 / (ex.y1 - ex.y0));
    return { s: s, ox: (W0 - s * (ex.x1 - ex.label_x0)) / 2 - s * ex.label_x0, oy: (H0 - s * (ex.y1 - ex.y0)) / 2 - s * ex.y0 };
  }
  function drawMinimap() {
    mmPending = false;
    if (!mm.offsetWidth) return;
    var dpr = window.devicePixelRatio || 1;
    if (mm.width !== Math.round(mm.offsetWidth * dpr)) { mm.width = Math.round(mm.offsetWidth * dpr); mm.height = Math.round(mm.offsetHeight * dpr); }
    var T = mmTransform();
    mctx.clearRect(0, 0, mm.width, mm.height);
    mctx.fillStyle = 'rgba(252,252,251,0.94)'; mctx.fillRect(0, 0, mm.width, mm.height);
    cy.nodes().forEach(function (n) {
      if (n.hasClass('hidden')) return;
      var p = n.position(), d = n.data();
      mctx.globalAlpha = n.hasClass('dim') ? 0.25 : 0.9;
      mctx.fillStyle = MM_FILL[d.sgroup] || '#898781';
      mctx.fillRect(T.ox + T.s * (p.x - d.w / 2), T.oy + T.s * (p.y - d.h / 2), Math.max(1.5, T.s * d.w), Math.max(1.5, T.s * d.h));
    });
    mctx.globalAlpha = 1;
    var z = cy.zoom(), pan = cy.pan(), sz = graphSize();
    var vx0 = -pan.x / z, vy0 = -pan.y / z;
    mctx.strokeStyle = '#0b0b0b'; mctx.lineWidth = 2 * dpr;
    mctx.strokeRect(T.ox + T.s * vx0, T.oy + T.s * vy0, T.s * sz.w / z, T.s * sz.h / z);
  }
  function minimapGo(ev) {
    var r = mm.getBoundingClientRect(), dpr = mm.width / r.width, T = mmTransform();
    var mx = ((ev.clientX - r.left) * dpr - T.ox) / T.s, my = ((ev.clientY - r.top) * dpr - T.oy) / T.s;
    var z = cy.zoom(), sz = graphSize();
    cy.pan({ x: sz.w / 2 - z * mx, y: sz.h / 2 - z * my });
  }
  var mmDrag = false;
  mm.addEventListener('pointerdown', function (ev) { mmDrag = true; mm.setPointerCapture(ev.pointerId); minimapGo(ev); ev.preventDefault(); });
  mm.addEventListener('pointermove', function (ev) { if (mmDrag) minimapGo(ev); });
  mm.addEventListener('pointerup', function () { mmDrag = false; });

  // ------------------------------------------------------------------ View·world·개입 전환
  function visibleOf(ids) {
    var c = cy.collection();
    ids.forEach(function (id) { var n = cy.getElementById(id); if (n.length && !n.hasClass('hidden')) c = c.union(n); });
    return c;
  }
  function setView(id) {
    state.view = id;
    state.showContext = false;            // View마다 그 View의 표시 범위에서 시작

    cy.$(':selected').unselect();
    cy.nodes().removeClass('search-hit');
    applyPositions();
    applyState();
    initialViewport();
    showPane(VIEWS.views[id].default_pane || 'detail');
  }
  function setShowContext(on) {
    var keep = cy.$('node:selected').map(function (n) { return n.id(); })[0];
    state.showContext = !!on;
    applyPositions();
    applyState();
    initialViewport();
    if (keep) focusNode(keep);
  }
  function setWorld(wid) { state.world = wid; applyState(); }
  function setIntervention(m) {
    state.iv = m || null;
    applyState();
    showPane('iv');
    if (state.iv) {
      var ids = ivRows().reduce(function (a, r) { return a.concat(r.path_nodes); }, []);
      var vis = visibleOf(ids);
      if (vis.length) {
        var bb = vis.boundingBox({ includeLabels: false }), sz = graphSize();
        var z = Math.max(READ_ZOOM + 0.05, Math.min(1.2, Math.min((sz.w - 60) / (bb.w || 1), (sz.h - 60) / (bb.h || 1))));
        cy.viewport({ zoom: z, pan: { x: sz.w / 2 - z * (bb.x1 + bb.x2) / 2, y: sz.h / 2 - z * (bb.y1 + bb.y2) / 2 } });
        syncOverlay();
      }
    }
  }
  function reset() {
    state = DEFAULT_STATE();
    syncFilterInputs();
    sInput.value = ''; sRes = []; renderResults(); sList.hidden = true;
    cy.$(':selected').unselect();
    cy.nodes().removeClass('search-hit');
    applyPositions();
    applyState();
    renderInterPanel();
    defaultDetail();
    showPane('detail');
    initialViewport();
  }
  $('reset').addEventListener('click', reset);
  $('zoom-in').addEventListener('click', function () { cy.zoom({ level: cy.zoom() * 1.2, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }); });
  $('zoom-out').addEventListener('click', function () { cy.zoom({ level: cy.zoom() / 1.2, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } }); });
  $('zoom-fit').addEventListener('click', fitAll);
  $('zoom-read').addEventListener('click', readableZoom);
  $('zoom-home').addEventListener('click', initialViewport);
  $('toggle-sidebar').addEventListener('click', function () {
    var app = document.querySelector('.app'), on = !app.classList.contains('side-collapsed');
    app.classList.toggle('side-collapsed', on);
    this.setAttribute('aria-expanded', String(!on));
    this.textContent = on ? '필터 펼치기' : '필터 접기';
    setTimeout(function () { cy.resize(); syncOverlay(); }, 0);
  });
  $('toggle-minimap').addEventListener('click', function () {
    var on = this.getAttribute('aria-pressed') !== 'true';
    this.setAttribute('aria-pressed', String(on));
    mm.hidden = !on;
    scheduleMinimap();
  });
  window.addEventListener('resize', function () { cy.resize(); syncOverlay(); });
  // 배너 높이가 바뀌어 그래프 영역 크기가 달라지면 cytoscape에도 알린다
  if (window.ResizeObserver) new ResizeObserver(function () { cy.resize(); syncOverlay(); }).observe($('cy'));

  // ------------------------------------------------------------------ 시작
  if (cy.width() < 600) { $('toggle-minimap').setAttribute('aria-pressed', 'false'); mm.hidden = true; }   // 좁은 화면: 미니맵 기본 숨김
  applyPositions();
  applyState();
  renderInterPanel();
  defaultDetail();
  initialViewport();

  // 테스트·디버깅용(읽기 전용 용도)
  window.__viz = {
    cy: cy, data: D, getState: function () { return JSON.parse(JSON.stringify(state)); },
    setView: setView, setWorld: setWorld, setIntervention: setIntervention, setPair: setPair, setShowContext: setShowContext,
    focusNode: focusNode, focusEdge: focusEdge, search: search, reset: reset, fitAll: fitAll, initialViewport: initialViewport
  };
})();
