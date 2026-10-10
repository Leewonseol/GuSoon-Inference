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
  // 간단히 보기(meta.simple_view): 화면 표시만 줄인다. node·edge·world·개입·공존 데이터는 그대로다.
  var SV = META.simple_view, EDISP = META.edge_display, EORDER = META.edge_display_order;
  var CORE_FLOW = toSet(SV.core_flow_types), TRANSITIVE = toSet(SV.transitive_types), NO_MERGE = toSet(SV.merge_exclude_types);
  function catOf(t) { return (META.edge_styles[t] || {}).display || 'record'; }
  function relText(t) { var s = META.edge_styles[t] || {}; return t + (s.ko ? ' · ' + s.ko : ''); }
  var DEFAULT_STATE = function () {
    return { view: 'overview', world: 'ALL', hideOthers: false, showContext: false, status: toSet(STATUS_KEYS), mech: toSet(MECHS), iv: null, pair: ['M1', 'M2'],
      level: SV.default_level, hops: SV.default_hops, sel: null, focusMech: null };
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
      data: { id: e.id, source: c.src, target: c.dst, etype: c.edge_type, sgroup: e.status_group, origin: c.origin, cat: catOf(c.edge_type), elabel: relText(c.edge_type) },
      classes: ['et-' + c.edge_type, 'eo-' + c.origin, 'es-' + e.status_group, 'cat-' + catOf(c.edge_type)].join(' ')
    });
  });

  // ------------------------------------------------------------------ 표시 전용 계산(원본 edge는 그대로 두고 화면에서만 묶거나 접는다)
  // 같은 두 node·같은 방향·같은 표시 유형·같은 증거 상태인 관계 여럿 → 화면에서는 선 하나(MG~…). 원본 edge는 cy에 그대로 있고 눌러서 모두 볼 수 있다.
  // 방향이 다르거나 증거 상태가 다르거나 merge_exclude_types(주장 수준 상충)이면 따로 그린다.
  function mergeGroups(edges) {
    var g = {};
    edges.forEach(function (e) {
      var c = e.canonical;
      if (NO_MERGE[c.edge_type]) return;
      var k = [c.src, c.dst, catOf(c.edge_type), e.status_group].join('\u0001');
      (g[k] = g[k] || []).push(e.id);
    });
    return Object.keys(g).filter(function (k) { return g[k].length > 1; }).sort().map(function (k) {
      var p = k.split('\u0001');
      return { id: 'MG~' + g[k].slice().sort().join('~'), src: p[0], dst: p[1], cat: p[2], sgroup: p[3], members: g[k].slice().sort() };
    });
  }
  // 추이적 관계(meta.simple_view.transitive_types, 지금은 TEMPORAL_BEFORE만)에서 같은 유형만으로 된 길이 2 이상 경로가 따로 있는 직접 edge.
  // REVIEW_OF·REVISES·INFORMATION_FLOW·RESPONSIBILITY_LINK 등은 추이적이라고 가정하지 않는다.
  function transitiveRedundant(edges) {
    var out = {}, byType = {};
    edges.forEach(function (e) { var t = e.canonical.edge_type; if (TRANSITIVE[t]) (byType[t] = byType[t] || []).push(e); });
    Object.keys(byType).forEach(function (t) {
      var succ = {};
      byType[t].forEach(function (e) { (succ[e.canonical.src] = succ[e.canonical.src] || []).push(e.canonical.dst); });
      byType[t].forEach(function (e) {
        var s = e.canonical.src, d = e.canonical.dst, seen = {}, stack = (succ[s] || []).filter(function (x) { return x !== d; });
        while (stack.length) {
          var x = stack.pop();
          if (x === d) { out[e.id] = true; break; }
          if (seen[x] || x === s) continue;
          seen[x] = true;
          (succ[x] || []).forEach(function (y) { stack.push(y); });
        }
      });
    });
    return out;
  }
  var MERGED = mergeGroups(SD.edges), MERGE_OF = {}, REDUNDANT = transitiveRedundant(SD.edges);
  MERGED.forEach(function (m) {
    m.members.forEach(function (id) { MERGE_OF[id] = m.id; });
    elements.push({
      group: 'edges',
      data: { id: m.id, source: m.src, target: m.dst, etype: 'MERGED', sgroup: m.sgroup, origin: 'DISPLAY', cat: m.cat, members: m.members,
        mlabel: '관계 ' + m.members.length + '개', elabel: '관계 ' + m.members.length + '개: ' + m.members.map(function (id) { return edgeById[id].canonical.edge_type; }).join(' · ') },
      classes: ['merged', 'cat-' + m.cat, 'es-' + m.sgroup].join(' ')
    });
  });
  // 원본 인접 목록(펼치기 계산용, 표시 전용 묶음 edge는 넣지 않음)
  var ADJ = {};
  SD.edges.forEach(function (e) {
    (ADJ[e.canonical.src] = ADJ[e.canonical.src] || []).push(e);
    (ADJ[e.canonical.dst] = ADJ[e.canonical.dst] || []).push(e);
  });
  function isObs(id) { return nodeById[id] && nodeById[id].canonical.node_type === 'OBSERVED_EVENT'; }
  // 선택 node에서 k-hop 안의 node와 그 사이를 지나간 원본 edge(방향 무시)
  function hopBall(id, k) {
    var nodes = {}, edges = {}, ring = [id], d;
    nodes[id] = 0;
    for (d = 1; d <= k; d++) {
      var next = [];
      ring.forEach(function (u) {
        (ADJ[u] || []).forEach(function (e) {
          var v = e.canonical.src === u ? e.canonical.dst : e.canonical.src;
          edges[e.id] = true;
          if (!(v in nodes)) { nodes[v] = d; next.push(v); }
        });
      });
      ring = next;
    }
    return { nodes: nodes, edges: edges };
  }
  // 메커니즘 펼치기 범위: 메커니즘 → 후보(INSTANTIATED_BY·_SECONDARY) → 구조 변수(CONTRIBUTES_TO, ANCHORED_TO) → 설명 대상 관측 사건,
  // 그리고 이 묶음에 걸린 context(CONSTRAINS·CONTEXT_COMPATIBLE)·UNRESOLVED(CONDITIONS). 원본 edge를 따라가기만 한다.
  var MECH_SCOPE = {};
  MECHS.forEach(function (m) {
    var core = {}, nodes = {}, edges = {};
    core[m] = true;
    SD.edges.forEach(function (e) {
      var c = e.canonical;
      if (c.src === m && (c.edge_type === 'INSTANTIATED_BY' || c.edge_type === 'INSTANTIATED_BY_SECONDARY' || c.edge_type === 'ANCHORED_TO')) core[c.dst] = true;
    });
    SD.edges.forEach(function (e) {
      var c = e.canonical;
      if (c.edge_type === 'CONTRIBUTES_TO' && core[c.src]) core[c.dst] = true;
    });
    SD.edges.forEach(function (e) {
      var c = e.canonical, st = nodeById[c.src].canonical.sd_status;
      if (c.origin !== 'SUPER_DAG') return;
      if ((core[c.src] && core[c.dst]) || (core[c.src] && isObs(c.dst)) || (core[c.dst] && (st === 'CONTEXT' || st === 'UNRESOLVED'))) {
        edges[e.id] = true; nodes[c.src] = true; nodes[c.dst] = true;
      }
    });
    Object.keys(core).forEach(function (x) { nodes[x] = true; });
    MECH_SCOPE[m] = { nodes: nodes, edges: edges };
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
    { selector: 'edge.arc', style: { 'curve-style': 'unbundled-bezier', 'control-point-distances': 'data(cpd)', 'control-point-weights': 0.5 } }
  ];
  // 표시 유형 3종(기록·절차 진한 실선 / 분석·추론 얇은 점선 / 맥락·제약 옅은 점선). 세부 관계 19종은 선택·hover·상세 패널에서 보인다.
  EORDER.forEach(function (k) {
    var s = EDISP[k];
    style.push({ selector: 'edge.cat-' + k, style: { 'line-color': s.color, 'target-arrow-color': s.color, 'line-style': DASH[s.line] || 'solid',
      'width': s.width, 'opacity': s.opacity } });
  });
  // 증거 상태는 관계 유형과 따로: 기록·절차 선의 굵기(OBSERVED 굵게, DERIVED 보통)
  style.push({ selector: 'edge.cat-record.es-OBSERVED', style: { 'width': 4.2 } });
  Object.keys(META.edge_styles).forEach(function (t) {
    var s = META.edge_styles[t];
    if (s.arrow && s.arrow !== 'triangle') style.push({ selector: 'edge.et-' + t, style: { 'target-arrow-shape': s.arrow, 'arrow-scale': 1.5 } });
  });
  style = style.concat([
    { selector: 'edge.merged', style: { 'label': 'data(mlabel)', 'width': 4, 'font-weight': 700 } },
    { selector: 'edge.merged-member', style: { 'display': 'none' } },
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
    { selector: 'node.mfocus', style: { 'underlay-color': '#6b55c9', 'underlay-opacity': 0.28, 'underlay-padding': 10 } },
    { selector: 'edge.mfocus', style: { 'opacity': 1, 'width': 3, 'z-index': 20 } },
    { selector: 'edge.faded', style: { 'opacity': 0.08 } },
    // 선택 node의 직접 관계는 원래 관계 이름(유형 · 의미)을 선 위에 보여 준다. 선 모양(표시 유형)은 그대로 둔다.
    { selector: 'edge.sel-in, edge.sel-out', style: { 'opacity': 1, 'width': 5, 'z-index': 30, 'label': 'data(elabel)' } },
    { selector: 'edge.sel-2', style: { 'opacity': 0.9, 'width': 3, 'z-index': 25 } },
    { selector: 'node.sel-nbr', style: { 'underlay-color': '#2a78d6', 'underlay-opacity': 0.18, 'underlay-padding': 8 } },
    { selector: 'node.sel-nbr2', style: { 'underlay-color': '#2a78d6', 'underlay-opacity': 0.09, 'underlay-padding': 6 } },
    { selector: 'node.search-hit', style: { 'underlay-color': '#2a78d6', 'underlay-opacity': 0.45, 'underlay-padding': 14 } },
    { selector: 'edge.hover, edge:selected', style: { 'label': 'data(elabel)', 'opacity': 1, 'width': 5, 'z-index': 40 } },
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
  // 간단히 보기에서는 접힌 분석 lane 아래쪽을 빼고 지금 보이는 node까지만 지도 범위로 쓴다(좌표는 그대로)
  function liveExtent() {
    var ex = activeLayout().extent;
    if (!isCollapseMode()) return ex;
    var vis = cy.nodes().filter(function (n) { return !n.hasClass('hidden'); });
    if (!vis.length) return ex;
    var bb = vis.boundingBox({ includeLabels: false });
    return { x0: ex.x0, x1: ex.x1, label_x0: ex.label_x0, y0: ex.y0, y1: Math.min(ex.y1, Math.max(bb.y2 + 60, ex.y0 + 200)) };
  }
  function fitAll() {
    // 전체 보기(지도): 글자가 11pt보다 작아질 수 있다. node는 ID만 표시된다.
    var ex = liveExtent(), sz = graphSize(), pad = 20;
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
  var CLASS_RESET = 'hidden collapsed dim hl hl-rej grpA grpB pair iv-off iv-removed iv-remaining iv-PATH_BREAKS iv-PATH_WEAKENS iv-PATH_REMAINS iv-UNKNOWN iv-target iv-path cfg-ON cfg-PARTIAL cfg-UNSPECIFIED cfg-OFF mfocus merged-member reduced';
  function ivRows() { return state.iv ? IV.rows.filter(function (r) { return r.canonical.mechanism === state.iv; }) : []; }
  // 간단히 보기는 전체 Overview(A)에만 쓴다. 관점별 View(B–J)는 이미 고른 범위라 그 범위를 그대로 펼쳐 보여 준다.
  function isCollapseMode() { return VIEWS.views[state.view].policy === 'all' && state.level !== 'full'; }
  // 접힌 화면에서 펼칠 node·edge: 선택 node의 k-hop, 메커니즘 펼치기, 고른 world가 쓰는 후보·메커니즘, 개입 경로, 공존 쌍
  function revealSets(rows) {
    var nodes = {}, edges = {};
    function addN(x) { nodes[x] = true; }
    if (state.sel && nodeById[state.sel]) {
      var b = hopBall(state.sel, state.hops);
      Object.keys(b.nodes).forEach(addN);
      Object.keys(b.edges).forEach(function (x) { edges[x] = true; });
    }
    if (state.focusMech && MECH_SCOPE[state.focusMech]) {
      Object.keys(MECH_SCOPE[state.focusMech].nodes).forEach(addN);
      Object.keys(MECH_SCOPE[state.focusMech].edges).forEach(function (x) { edges[x] = true; });
    }
    var hl = W.selections[state.world].highlight;
    hl.forEach(addN);
    var hlS = toSet(hl), ivS = {};
    rows.forEach(function (r) { r.path_nodes.forEach(function (x) { addN(x); ivS[x] = true; }); });
    if (state.pairOn) state.pair.forEach(addN);
    SD.edges.forEach(function (e) {
      var s = e.canonical.src, t = e.canonical.dst;
      if ((hlS[s] && (hlS[t] || isObs(t))) || (hlS[t] && isObs(s)) || (ivS[s] && ivS[t])) edges[e.id] = true;
    });
    return { nodes: nodes, edges: edges };
  }
  // 접힌 화면에서 기본으로 보이는 관측 사건 사이 관계: simple = 핵심 시간·절차 흐름(추이적으로 중복된 edge 제외), records = 관측 사건 사이 관계 전부
  function baseEdgeShown(e) {
    var c = e.canonical;
    if (!isObs(c.src) || !isObs(c.dst)) return false;
    if (state.level === 'records') return true;
    return !!CORE_FLOW[c.edge_type] && !REDUNDANT[e.id];
  }
  var lastCounts = null;

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
    var collapse = isCollapseMode(), reveal = collapse ? revealSets(rows) : null;
    var mscope = state.focusMech ? MECH_SCOPE[state.focusMech] : null;
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
        // 메커니즘 펼치기: 전체 표시에서는 그 메커니즘 범위 밖 분석 node를 흐리게만 한다(삭제·계산 제외 아님)
        if (mscope && !collapse && !has(mscope.nodes, id) && !BACKBONE[id]) dim = true;
        // AUDIT5:SIMPLE_COLLAPSE — 간단히 보기: 펼치지 않은 LATENT·CONTEXT·UNRESOLVED node는 화면에서만 접는다(collapsed). 계산·world·개입 데이터는 그대로이며 바로 아래 BACKBONE_GUARD가 OBSERVED를 되살린다.
        var collapsed = collapse && !has(reveal.nodes, id);
        if (collapsed) hide = true;
        // AUDIT5:BACKBONE_GUARD — 필터·world 선택·개입·간단히 보기는 OBSERVED backbone(관측 사건·공통 결말)을 숨기지 못한다
        if (BACKBONE[id] || has(always, id)) { hide = false; collapsed = false; }
        // AUDIT5:VIEW_SCOPE — View 범위 밖 node는 subset View에서만 숨긴다. 숨긴 OBSERVED 수는 #banner-view에 항상 표시된다.
        if (outside) hide = true;
        if (hide) n.addClass('hidden');
        else if (dim) n.addClass('dim');
        if (collapsed && !outside) n.addClass('collapsed');
        if (mscope && has(mscope.nodes, id) && !hide && !BACKBONE[id]) n.addClass('mfocus');
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
      var nEdge = 0, nCollapsedEdge = 0;
      cy.edges().forEach(function (e) {
        var d = e.data(), s = e.source(), t = e.target();
        if (d.members) return;                       // 표시 전용 묶음 edge는 아래에서 구성원 상태로 정한다
        var hide = s.hasClass('hidden') || t.hasClass('hidden') || (!has(state.status, d.sgroup) && d.sgroup !== 'OBSERVED');
        if (hide) {
          e.addClass('hidden');
          if (s.hasClass('collapsed') || t.hasClass('collapsed')) { e.addClass('collapsed'); nCollapsedEdge++; }
          return;
        }
        // 간단히 보기: 기본 흐름 edge와 펼친 관계만 보이고 나머지는 화면에서만 접는다(원본 edge·분석은 그대로)
        if (collapse && !has(reveal.edges, d.id) && !baseEdgeShown(edgeById[d.id])) {
          e.addClass('hidden'); e.addClass('collapsed'); nCollapsedEdge++;
          if (REDUNDANT[d.id]) e.addClass('reduced');
          return;
        }
        if (rows.length && ivPath[d.source] && ivPath[d.target]) e.addClass('iv-path');
        else if (s.hasClass('dim') || t.hasClass('dim') || (rows.length && d.origin === 'SUPER_DAG')) e.addClass('dim');
        else if (mscope && !collapse && d.origin === 'SUPER_DAG' && !has(mscope.edges, d.id)) e.addClass('dim');
        if (mscope && has(mscope.edges, d.id)) e.addClass('mfocus');
      });
      // 같은 node 쌍 묶음: 구성원 중 하나라도 보이면 묶음 선 하나로 그리고, 구성원 선은 화면에서만 감춘다(원본 edge는 그대로).
      MERGED.forEach(function (m) {
        var me = cy.getElementById(m.id), vis = m.members.map(function (x) { return cy.getElementById(x); }).filter(function (x) { return !x.hasClass('hidden'); });
        if (!vis.length) { me.addClass('hidden'); return; }
        vis.forEach(function (x) { x.addClass('merged-member'); });
        if (vis.every(function (x) { return x.hasClass('dim'); })) me.addClass('dim');
        if (vis.some(function (x) { return x.hasClass('iv-path'); })) me.addClass('iv-path');
        if (vis.some(function (x) { return x.hasClass('mfocus'); })) me.addClass('mfocus');
      });
      cy.edges().forEach(function (e) { if (!e.hasClass('hidden') && !e.hasClass('merged-member')) nEdge++; });
      lastCounts = { nodes: cy.nodes().filter(function (n) { return !n.hasClass('hidden'); }).length, edges: nEdge,
        collapsedNodes: cy.nodes('.collapsed').length, collapsedEdges: nCollapsedEdge, reduced: cy.edges('.reduced').length };
      if (state.pairOn) { cy.getElementById(state.pair[0]).addClass('pair'); cy.getElementById(state.pair[1]).addClass('pair'); }
    });
    applySelection();
    renderBanners();
    renderSimplifyControls();
    renderWorldButtons();
    renderTabs();
    renderWorldPanel();
    renderIvPanel();
    scheduleMinimap();
  }

  // 선택한 node의 들어오는·나가는 edge 강조, 관련 없는 edge 흐림
  // 2-hop이면 이웃의 이웃과 그 관계도 옅게 강조한다(원본 edge 기준, 묶음 선은 구성원을 따라감).
  function applySelection() {
    cy.batch(function () {
      cy.elements().removeClass('sel-in sel-out sel-2 sel-nbr sel-nbr2 faded');
      var n = cy.$('node:selected');
      if (!n.length) return;
      n.incomers('edge').addClass('sel-in');
      n.outgoers('edge').addClass('sel-out');
      n.neighborhood('node').addClass('sel-nbr');
      var keep = n.connectedEdges();
      if (state.hops > 1) {
        var b = hopBall(n.id(), state.hops);
        Object.keys(b.edges).forEach(function (id) {
          var e = cy.getElementById(MERGE_OF[id] || id);
          if (!e.hasClass('sel-in') && !e.hasClass('sel-out')) e.addClass('sel-2');
          keep = keep.union(e);
        });
        Object.keys(b.nodes).forEach(function (id) { if (b.nodes[id] > 1) cy.getElementById(id).addClass('sel-nbr2'); });
      }
      cy.edges().difference(keep).addClass('faded');
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
    } else if (isCollapseMode()) {
      // AUDIT5:SIMPLE_NOTICE — 접힌 node·관계가 사라진 것으로 읽히지 않도록 개수와 '화면에서만 접음' 안내를 항상 보여 준다
      var k = lastCounts || {}, selTxt = '';
      if (state.sel && nodeById[state.sel]) {
        var ball = hopBall(state.sel, state.hops);
        selTxt = ' <span class="sel-note">선택 <b>' + esc(state.sel) + '</b>: ' + state.hops + '-hop 관련 node ' + (Object.keys(ball.nodes).length - 1) +
          '개·관계 ' + Object.keys(ball.edges).length + '개 펼침 <button type="button" class="btn btn-sm" id="show-revealed">펼친 범위 보기</button></span>';
      }
      vb.hidden = false;
      vb.innerHTML = '<b>' + esc(SV.level_labels[state.level]) + '</b> · 보이는 node <b id="simple-node-count">' + k.nodes + '</b>개(관측 사건 ' + W.backbone.length +
        '개 모두 포함) · 관계 <b id="simple-edge-count">' + k.edges + '</b>개 — 접힌 node ' + k.collapsedNodes + '개·관계 ' + k.collapsedEdges + '개' +
        (k.reduced ? '(시간 선후 중복 ' + k.reduced + '개 포함)' : '') +
        ' <span class="notice-text">삭제가 아니라 화면에서만 접은 것(world·공존·개입 결과와 상세 패널에 그대로 포함). node를 누르면 관련 관계가 펼쳐집니다.</span>' + selTxt +
        ' <button type="button" class="btn btn-sm" id="level-toggle" data-to="full">전체 보기</button>';
      $('level-toggle').addEventListener('click', function () { setLevel('full'); });
      if ($('show-revealed')) $('show-revealed').addEventListener('click', showRevealed);
    } else {
      vb.hidden = false;
      vb.innerHTML = '<b>전체 보기</b> · 모든 node ' + META.counts.nodes + '개와 관계 ' + META.counts.edges + '개(분석·맥락 포함)를 표시합니다. ' +
        '<button type="button" class="btn btn-sm" id="level-toggle" data-to="simple">간단히 보기</button>';
      $('level-toggle').addEventListener('click', function () { setLevel('simple'); });
    }
  }
  // ------------------------------------------------------------------ 화면 단순화 조작(표시 수준·선택 확장·메커니즘 펼치기)
  function renderSimplifyControls() {
    var lb = $('level-buttons'), hb = $('hop-buttons'), mf = $('mech-focus');
    if (!lb.childElementCount) {
      SV.levels.forEach(function (lv) {
        var b = document.createElement('button');
        b.type = 'button'; b.setAttribute('role', 'radio'); b.dataset.level = lv; b.textContent = SV.level_labels[lv];
        b.addEventListener('click', function () { setLevel(lv); });
        lb.appendChild(b);
      });
      for (var h = 1; h <= SV.max_hops; h++) (function (h) {
        var b = document.createElement('button');
        b.type = 'button'; b.setAttribute('role', 'radio'); b.dataset.hops = h; b.textContent = h + '-hop';
        b.title = h === 1 ? '선택한 node와 직접 연결된 관계' : '이웃의 이웃까지';
        b.addEventListener('click', function () { setHops(h); });
        hb.appendChild(b);
      })(h);
      MECHS.forEach(function (m) {
        var b = document.createElement('button');
        b.type = 'button'; b.dataset.focusMech = m; b.innerHTML = '<b>' + m + '</b> ' + esc(META.mechanism_display[m]);
        b.addEventListener('click', function () { setFocusMech(state.focusMech === m ? null : m); });
        mf.appendChild(b);
      });
    }
    Array.prototype.forEach.call(lb.children, function (b) { b.setAttribute('aria-checked', String(b.dataset.level === state.level)); });
    Array.prototype.forEach.call(hb.children, function (b) { b.setAttribute('aria-checked', String(+b.dataset.hops === state.hops)); });
    Array.prototype.forEach.call(mf.children, function (b) { b.setAttribute('aria-pressed', String(b.dataset.focusMech === state.focusMech)); });
    $('level-scope-note').textContent = VIEWS.views[state.view].policy === 'all' ? '' :
      '지금 View(' + VIEWS.views[state.view].label + ')는 이미 고른 범위라 그 범위를 그대로 표시합니다. 표시 수준은 A 전체 Overview에 적용됩니다.';
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
  function edgeSwatch(k, extraArrow) {
    var s = EDISP[k], da = s.line === 'dashed' ? '6 3' : (s.line === 'dotted' ? '1.5 3' : '');
    var head = extraArrow === 'tee' ? '<line x1="33" y1="1" x2="33" y2="11" stroke="' + s.color + '" stroke-width="2.4"/>' : '<path d="M35 6 l-7 -5 l0 10 z" fill="' + s.color + '"/>';
    return '<svg width="36" height="12" aria-hidden="true" style="opacity:' + Math.max(0.55, s.opacity) + '"><line x1="1" y1="6" x2="28" y2="6" stroke="' + s.color +
      '" stroke-width="' + Math.max(1.6, s.width) + '" stroke-dasharray="' + da + '"/>' + head + '</svg>';
  }
  function nodeSwatch(r) {
    var shape;
    if (r[4] === 'hex') shape = '<polygon points="8,1 28,1 35,9 28,17 8,17 1,9" ';
    else if (r[4] === 'cut') shape = '<polygon points="5,1 31,1 35,5 35,13 31,17 5,17 1,13 1,5" ';
    else if (r[4] === 'barrel') shape = '<rect x="1" y="1" width="34" height="16" rx="10" ry="8" ';
    else if (r[4] === 'sq') shape = '<rect x="1" y="1" width="34" height="16" ';
    else shape = '<rect x="1" y="1" width="34" height="16" rx="4" ';
    var extra = r[4] === 'double' ? '<rect x="4" y="4" width="28" height="10" rx="2" fill="none" stroke="' + r[2] + '" stroke-width="1.4"/>' : '';
    return '<svg width="36" height="18" aria-hidden="true">' + shape + 'fill="' + r[1] + '" stroke="' + r[2] + '" stroke-width="' + (r[4] === 'double' ? 1.4 : 2) + '" stroke-dasharray="' + r[3] + '"/>' + extra + '</svg>';
  }
  // 기본 범례: node 4종·edge 3종. 기존 세부 범례(node 9종·관계 19종·선 굵기·이중 테두리)는 '상세 범례 보기'에 그대로 있다.
  (function buildSimpleLegend() {
    var nodesS = [['관측 사건', '#eaf2fc', '#256abf', '', 'rect', 'OBSERVED · 항상 표시'], ['추론·가설', '#fdf1ea', '#c4501f', '5 3', 'rect', 'LATENT 메커니즘·구조 변수·후보 · 기본은 접힘'],
      ['제도·환경', '#eef6ee', '#008300', '1 3', 'sq', 'CONTEXT · 사건 아님'], ['미확정 항목', '#fcf0f5', '#b83a6b', '', 'double', 'UNRESOLVED · 이중 테두리']];
    $('legend-nodes').innerHTML = '<div class="grp">Node</div>' + nodesS.map(function (r) {
      return '<div class="row">' + nodeSwatch(r) + '<span>' + esc(r[0]) + ' <span class="muted">' + esc(r[5]) + '</span></span></div>';
    }).join('');
    $('legend-edges').innerHTML = '<div class="grp">Edge</div>' + EORDER.map(function (k) {
      return '<div class="row" data-legend-cat="' + k + '">' + edgeSwatch(k) + '<span>' + esc(EDISP[k].label) + '</span></div>';
    }).join('');
  })();
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
      h += '<div class="row">' + nodeSwatch(r) + '<span>' + esc(r[0]) + '</span></div>';
    });
    h += '<div class="row muted">강조: <span style="background:rgba(237,161,0,.4);padding:0 4px;border-radius:3px">world 사용</span> <span style="background:rgba(208,59,59,.3);padding:0 4px;border-radius:3px">W6 배제</span> ' +
      '<span style="background:rgba(107,85,201,.3);padding:0 4px;border-radius:3px">메커니즘 펼치기</span></div>';
    $('legend-detail-nodes').innerHTML = h;
    // 관계 19종을 표시 유형 3종 아래에 원래 이름·의미 그대로 나열한다
    var eh = '';
    EORDER.forEach(function (k) {
      eh += '<div class="grp">Edge — ' + esc(EDISP[k].label) + ' <span class="muted">(' + esc(EDISP[k].desc) + ')</span></div>';
      Object.keys(META.edge_styles).filter(function (t) { return META.edge_styles[t].display === k; }).forEach(function (t) {
        var s = META.edge_styles[t];
        eh += '<div class="row" data-legend-type="' + esc(t) + '" title="' + esc(s.ko) + '">' + edgeSwatch(k, s.arrow) + '<span><code>' + esc(t) + '</code> <span class="muted">' + esc(s.ko) + '</span></span></div>';
      });
    });
    eh += '<div class="row muted">선 굵기 = 증거 상태: 기록·절차 선 중 OBSERVED edge는 굵게, DERIVED edge는 보통. 관계 유형과 증거 상태는 따로 표시됩니다(상세 패널의 status).</div>' +
      '<div class="row muted">주장 수준 상충(CONTRADICTS_AT_CLAIM_LEVEL)은 흐름이 아니므로 끝을 ⊣ 모양으로 그리고 다른 관계와 묶지 않습니다.</div>' +
      '<div class="row muted">‘관계 N개’ 선 = 같은 두 node·같은 방향·같은 표시 유형·같은 증거 상태인 관계 묶음. 누르면 원래 관계가 모두 나옵니다.</div>' +
      '<div class="row muted">관계 이름(유형 · 의미)은 마우스를 올리거나 node·edge를 선택하면 선 위에 보입니다.</div>';
    $('legend-detail-edges').innerHTML = eh;
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
  // 이 node와 분석 edge(SUPER_DAG)로 이어진 LATENT 후보: 메커니즘이면 그 메커니즘이 INSTANTIATED_BY로 잇는 후보,
  // 그 밖에는 분석 edge를 거꾸로 따라가며 만나는 후보(메커니즘에서 멈춤). 등급은 canonical 값 그대로.
  function relatedCandidatesHtml(n) {
    var found = {}, via = {};
    if (n.canonical.node_type === 'MECHANISM') {
      SD.edges.forEach(function (e) {
        var c = e.canonical;
        if (c.src === n.id && (c.edge_type === 'INSTANTIATED_BY' || c.edge_type === 'INSTANTIATED_BY_SECONDARY')) { found[c.dst] = true; via[c.dst] = c.edge_type; }
      });
    } else {
      var seen = {}, frontier = [n.id];
      seen[n.id] = true;
      while (frontier.length) {
        var next = [];
        frontier.forEach(function (u) {
          SD.edges.forEach(function (e) {
            var c = e.canonical;
            if (c.origin !== 'SUPER_DAG' || c.dst !== u || seen[c.src]) return;
            seen[c.src] = true;
            var t = nodeById[c.src].canonical.node_type;
            if (t === 'CANDIDATE_BRIDGE') { found[c.src] = true; via[c.src] = c.edge_type + ' → ' + u; }
            else if (t === 'STRUCTURAL_VARIABLE') next.push(c.src);
          });
        });
        frontier = next;
      }
      if (n.canonical.node_type === 'CANDIDATE_BRIDGE') delete found[n.id];
    }
    var ids = Object.keys(found).sort();
    if (!ids.length) return '<p class="muted">분석 edge로 이어진 LATENT 후보 없음</p>';
    return '<ul class="plain">' + ids.map(function (c) {
      var r = CAND.rows[c] || {};
      return '<li>' + nodeLink(c) + ' <span class="muted">' + esc(nodeById[c].canonical.mechanism || '') + ' · overall ' + esc(r.overall || '-') + ' · via ' + esc(via[c]) + '</span></li>';
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
      return '<li>' + edgeLink(e.id) + ' <code>' + esc(e.canonical.edge_type) + '</code> <span class="muted">' + esc(s.ko || '') + ' · ' + esc((EDISP[s.display] || {}).label || '') + '</span> ' +
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
    h += '<h4>관련 LATENT 후보</h4>' + relatedCandidatesHtml(n);
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
      '<p class="chips">' + chip('st-' + e.status_group, c.sd_status) + ' ' + chip('flag', c.origin) + ' ' + chip('flag', '화면 표시: ' + ((EDISP[s.display] || {}).label || '')) + '</p></div>';
    if (c.edge_type === 'CONTRADICTS_AT_CLAIM_LEVEL') {
      h += '<div class="callout warn">원래 관계: <b>CONTRADICTS_AT_CLAIM_LEVEL</b> — ' + esc(s.ko) + '. 시간 흐름이나 원인 방향을 뜻하지 않으며, 화면의 기록·절차 선 모양은 표시 묶음일 뿐입니다.</div>';
    }
    if (MERGE_OF[id]) h += '<p class="muted">화면에서는 같은 두 node 사이 관계와 함께 선 하나(' + esc(MERGE_OF[id]) + ')로 묶여 그려집니다. 원본 edge는 그대로입니다.</p>';
    h += kv([['edge ID', id], ['type', c.edge_type + (s.ko ? ' · ' + s.ko : '')], ['화면 표시 유형', (EDISP[s.display] || {}).label + ' — ' + ((EDISP[s.display] || {}).desc || '')],
      ['status', c.sd_status], ['origin', c.origin],
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

  // 표시 전용 묶음 선: 원래 관계를 하나도 빼지 않고 모두 보여 준다(각 항목을 누르면 그 edge 상세)
  function renderMergedDetail(mid) {
    var me = cy.getElementById(mid);
    if (!me.length) return;
    var d = me.data(), members = d.members.map(function (x) { return edgeById[x]; });
    var h = '<div class="card-head"><div class="nid">관계 ' + members.length + '개</div><div class="ntitle">' + nodeLink(d.source) + ' → ' + nodeLink(d.target) + '</div>' +
      '<p class="chips">' + chip('flag', '화면 표시: ' + EDISP[d.cat].label) + ' ' + chip('st-' + d.sgroup, d.sgroup) + '</p></div>';
    h += '<div class="callout info">같은 두 node·같은 방향·같은 표시 유형·같은 증거 상태인 관계를 화면에서만 선 하나로 묶었습니다. 원본 edge ' + members.length + '개는 그대로이며 아래에 모두 있습니다.</div>';
    h += '<h4>원래 관계 (' + members.length + ')</h4><ul class="plain" id="merged-members">' + members.map(function (e) {
      return '<li>' + edgeLink(e.id) + ' <code>' + esc(e.canonical.edge_type) + '</code> <span class="muted">' + esc((META.edge_styles[e.canonical.edge_type] || {}).ko || '') + '</span> ' +
        chip('st-' + e.status_group, e.canonical.sd_status) + ' <span class="muted">' + esc(e.canonical.origin) + '</span></li>';
    }).join('') + '</ul>';
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
      '<p class="muted">' + esc(SV.note) + '</p>' +
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
    state.sel = id;                         // 간단히 보기에서는 이 node와 관련 관계를 펼친다
    if (isCollapseMode() && !n.hasClass('hidden')) applyState();
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
    // 묶음 선의 구성원이면 화면에서는 묶음 선을 고르고, 상세는 요청한 원래 관계를 보여 준다
    var shown = MERGE_OF[id] && e.hasClass('merged-member') ? cy.getElementById(MERGE_OF[id]) : e;
    cy.$(':selected').unselect();
    shown.select();
    applySelection();
    centerOn(shown, Math.min(1.8, Math.max(cy.zoom(), READ_ZOOM + 0.05)));
    if (e.data('members')) renderMergedDetail(id); else renderEdgeDetail(id);
    return true;
  }
  cy.on('tap', 'node', function (ev) {
    cy.nodes().removeClass('search-hit');
    var id = ev.target.id();
    renderNodeDetail(id);
    state.sel = id;
    setTimeout(applyState, 0);
  });
  cy.on('tap', 'edge', function (ev) {
    var d = ev.target.data();
    if (d.members) renderMergedDetail(d.id); else renderEdgeDetail(d.id);
    setTimeout(applySelection, 0);
  });
  cy.on('tap', function (ev) {
    if (ev.target !== cy) return;
    var had = state.sel;
    state.sel = null;
    setTimeout(had ? applyState : applySelection, 0);
  });
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
    var ex = liveExtent(), W0 = mm.width, H0 = mm.height;
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
  // AUDIT5:EMPTY_VIEW_GUARD — 보이는 node가 하나도 없으면 빈 흰 화면으로 두지 않는다: 알리고 Overview로 1회 복구.
  // node는 있는데 첫 화면 창과 하나도 겹치지 않으면 핵심 node 하나를 읽기 배율로 가운데에 둔다(전체 맞춤 아님).
  var emptyRecovered = false;
  function showVizNotice(html, kind) {
    var box = $('viz-error');
    if (!box) return;
    box.className = 'viz-error' + (kind === 'notice' ? ' notice' : '');
    box.innerHTML = html;
    box.hidden = false;
  }
  function guardEmptyView() {
    var shown = cy.nodes().filter(function (n) { return n.style('display') !== 'none'; });
    if (!shown.length) {
      if (state.view !== 'overview' && !emptyRecovered) {
        emptyRecovered = true;
        setView('overview');
        showVizNotice('<b>현재 View에서 표시할 그래프를 찾지 못했습니다.</b><span>Overview로 복구합니다. (눌러서 닫기)</span>', 'notice');
      } else {
        showVizNotice('<b>시각화 초기화 오류</b><span>표시할 node가 없습니다. ‘초기화’ 버튼이나 새로 고침으로 다시 시도하세요.</span>');
      }
      return false;
    }
    var sz = graphSize();
    var inView = shown.filter(function (n) {
      var b = n.renderedBoundingBox({ includeLabels: false });
      return b.x2 > 0 && b.y2 > 0 && b.x1 < sz.w && b.y1 < sz.h;
    });
    if (!inView.length) {
      var focus = visibleOf(focusIds(VIEWS.views[state.view]));
      centerOn(focus.length ? focus[0] : shown[0], Math.max(READ_ZOOM, cy.zoom()));
    }
    return true;
  }
  function setView(id) {
    state.view = id;
    state.showContext = false;            // View마다 그 View의 표시 범위에서 시작
    state.sel = null;

    cy.$(':selected').unselect();
    cy.nodes().removeClass('search-hit');
    applyPositions();
    applyState();
    initialViewport();
    if ($('viz-error')) $('viz-error').hidden = true;
    guardEmptyView();
    showPane(VIEWS.views[state.view].default_pane || 'detail');
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
  // 보이는 node 묶음을 읽을 수 있는 배율로 화면 가운데에 둔다(다 들어오지 않으면 가운데 기준)
  function frameNodes(vis) {
    if (!vis.length) return;
    var bb = vis.boundingBox({ includeLabels: false }), sz = graphSize();
    var z = Math.max(READ_ZOOM + 0.05, Math.min(1.2, Math.min((sz.w - 60) / (bb.w || 1), (sz.h - 60) / (bb.h || 1))));
    cy.viewport({ zoom: z, pan: { x: sz.w / 2 - z * (bb.x1 + bb.x2) / 2, y: sz.h / 2 - z * (bb.y1 + bb.y2) / 2 } });
    syncOverlay();
  }
  function setIntervention(m) {
    state.iv = m || null;
    applyState();
    showPane('iv');
    if (state.iv) frameNodes(visibleOf(ivRows().reduce(function (a, r) { return a.concat(r.path_nodes); }, [])));
  }
  // 표시 수준(간단히·관측 사건 사이 관계 전체·전체). 화면 표시만 바뀐다.
  function setLevel(lv) {
    if (SV.levels.indexOf(lv) < 0) return;
    state.level = lv;
    applyState();
  }
  function setHops(h) { state.hops = Math.max(1, Math.min(SV.max_hops, +h || 1)); applyState(); }
  // 메커니즘 펼치기: 그 메커니즘의 후보·구조 변수·관련 context·UNRESOLVED와 분석 관계만 펼치고 강조한다(나머지는 삭제·계산 제외 아님)
  function setFocusMech(m) {
    state.focusMech = m && MECH_SCOPE[m] ? m : null;
    applyState();
    if (state.focusMech) {
      var mn = cy.getElementById(state.focusMech);
      if (!mn.hasClass('hidden')) centerOn(mn, Math.max(READ_ZOOM + 0.05, Math.min(1.2, cy.zoom())));
      renderNodeDetail(state.focusMech);
    }
  }
  function showRevealed() {
    if (!state.sel) return;
    frameNodes(visibleOf(Object.keys(hopBall(state.sel, state.hops).nodes)));
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
  guardEmptyView();
  if ($('viz-error')) $('viz-error').addEventListener('click', function () { if (this.classList.contains('notice')) this.hidden = true; });

  // 테스트·디버깅용(읽기 전용 용도)
  window.__viz = {
    cy: cy, data: D, getState: function () { return JSON.parse(JSON.stringify(state)); },
    setView: setView, setWorld: setWorld, setIntervention: setIntervention, setPair: setPair, setShowContext: setShowContext,
    focusNode: focusNode, focusEdge: focusEdge, search: search, reset: reset, fitAll: fitAll, initialViewport: initialViewport,
    setLevel: setLevel, setHops: setHops, setFocusMech: setFocusMech, counts: function () { return JSON.parse(JSON.stringify(lastCounts)); },
    // 표시 전용 계산(검증용). 입력 데이터를 바꾸지 않는다.
    display: { mergeGroups: mergeGroups, transitiveRedundant: transitiveRedundant, hopBall: hopBall, mechScope: MECH_SCOPE, merged: MERGED, redundant: REDUNDANT }
  };
})();
