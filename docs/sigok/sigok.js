/* 《시곡》 가능세계 분석 사이트. 데이터: sigok/data.js (possible_world_analysis/tools/build_site.py가 생성) */
(function () {
  'use strict';
  var D = window.SIGOK_DATA;
  if (!D) throw new Error('SIGOK_DATA 없음 (sigok/data.js)');

  // ───────── 공용 ─────────
  function $(s, r) { return (r || document).querySelector(s); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function by(arr, key) { var o = {}; arr.forEach(function (x) { o[x[key]] = x; }); return o; }
  var VAR = by(D.variables, 'id'), SRC = by(D.sources, 'source_id'), CLM = by(D.claims, 'claim_id');
  var BY = D.meta.base_year, LO = D.meta.domain[0], HI = D.meta.domain[1];
  function L(y, m, d) { return ((y - BY) * 12 + (m - 1)) * 30 + (d - 1); }
  function ymd(i) { var mi = Math.floor(i / 30), d = i - mi * 30, y = Math.floor(mi / 12), m = mi - y * 12; return [BY + y, m + 1, d + 1]; }
  function fmt(i) { if (i == null) return '—'; var a = ymd(i); return a[0] + '년 음력 ' + a[1] + '월 ' + a[2] + '일'; }
  function fmtBound(i, side) {
    if (side === 'lo' && i <= LO) return '사료상 하한 없음';
    if (side === 'hi' && i >= HI) return '사료상 상한 없음';
    return fmt(i);
  }
  var LAYER_VAR = { historical: '사료 변수', institutional: '제도', context: '비교·후대 맥락', theory: '이론', scenario: '극중 설정·가설' };
  var EXOG_LAYER = { creative: '극중 가정', hist: '사료 서술', inference: '사료로부터의 추론' };
  var EDGE_KO = { source: '사료에 나타난 관계', theory: '이론이 제안한 인과', film: '극중 추가 가정' };
  var CAT_KO = { primary: '1차 사료', scholarship: '학술연구', theory_institutional: '이론·제도·방법 해설', internal: '프로젝트 내부 자료 (증거 아님 — 추적용)' };

  function badgeResult(r) { return '<span class="badge ' + (r === 'SAT' ? 'b-sat' : 'b-unsat') + '">' + (r === 'SAT' ? '성립 SAT' : '불성립 UNSAT') + '</span>'; }
  function statusBadge(s) {
    var cls = /원문 확인|간접 확인/.test(s) ? 'b-ok' : (/극중/.test(s) ? 'b-film' : 'b-warn');
    return '<span class="badge ' + cls + '">' + esc(s) + '</span>';
  }
  function varLink(id) { return VAR[id] ? '<a href="#evidence/' + esc(id) + '">' + esc(id) + '</a>' : esc(id); }
  function srcLink(id) { return SRC[id] ? '<a href="#refs/' + esc(id) + '">' + esc(id) + '</a>' : esc(id); }
  function basisLink(b) {
    if (VAR[b]) return varLink(b);
    if (SRC[b]) return srcLink(b);
    if (CLM[b]) {
      var c = CLM[b], v = (c.related_variables || '').split(';')[0];
      return '<a href="#evidence/' + esc(v) + '" title="' + esc(c.claim) + '">' + esc(b) + '</a>';
    }
    return esc(b);
  }
  function cItem(id) {
    var c = D.constraints[id];
    if (!c) return '<code>' + esc(id) + '</code>';
    return '<code>' + esc(id) + '</code> <span class="badge b-layer">' + esc(D.layers[c.layer] || c.layer) + '</span> ' + esc(c.text) +
      (c.status ? ' <span class="fine">(' + esc(c.status) + ')</span>' : '') +
      '<div class="fine">근거: ' + c.basis.map(basisLink).join(', ') + '</div>';
  }
  function symLabel(k) {
    if (D.endo[k]) return D.endo[k].label;
    if (D.exog[k]) return D.exog[k].label;
    return k;
  }
  function symVar(k) { return (D.endo[k] || D.exog[k] || {}).var; }

  // ───────── 머리글 ─────────
  function header() {
    var c = D.meta.counts, blocked = D.meta.link_status.NETWORK_BLOCKED || 0;
    $('#stats').innerHTML = [
      [c.sources, '출처'], [c.claims, '주장'], [c.variables, '변수'], [c.constraints, '제약'],
      [c.feasible_worlds.toLocaleString('ko-KR'), '성립 인과구조'], [c.representatives, '대표 세계']
    ].map(function (x) { return '<li><b>' + x[0] + '</b>' + x[1] + '</li>'; }).join('');
    $('#access-note').textContent = blocked
      ? '링크 검사(' + D.meta.checked_at + '): 원문 DB 링크 ' + blocked + '건이 실행 환경의 네트워크 정책으로 차단되어, 한문 구절은 사용자 데이터셋 전사본으로만 확인했습니다(간접 확인). 차단은 자료 부재가 아닙니다.'
      : '링크 검사(' + D.meta.checked_at + ') 결과는 참고문헌 화면에서 확인하세요.';
    $('#repo-link').href = D.meta.repo;
  }

  // ───────── 개요 ─────────
  function renderOverview() {
    var M = D.modes, w = D.worlds;
    var nd = w.rows.filter(function (r) { return r.pareto; }).map(function (r) { return r.world; });
    var core = M.F_ON_H_SIM.mus[0];
    var html = '<div class="pane-head"><h2>개요</h2></div>';
    html += '<div class="card"><h3>핵심 결론</h3><ol>' +
      '<li>《심리록》(1780년 6월 성옥)만 채택해도, 《정조실록》 회고(1781년)만 채택해도 성립 ' + badgeResult(M.H_SIM.result) + ' ' + badgeResult(M.H_SIL.result) +
      '. 두 사료를 동시에 절대 사실로 고정하면 ' + badgeResult(M.H_BOTH.result) + ' — 상충 사료는 하위모형으로 분리했습니다.</li>' +
      '<li>극중 필수 순서(조상진 부임 &lt; 포폄 &lt; 윤씨 사망 &lt; 성옥)를 《심리록》 연대와 함께 고정하면 ' + badgeResult(M.F_ON_H_SIM.result) +
      '. 최소 충돌집합은 ' + core.length + '개 조건이며 그중 하나만 바꾸면 성립합니다: ' + core.map(function (c) { return '<code>' + esc(c) + '</code>'; }).join(' · ') + '. <a href="#time/F_ON_H_SIM">자세히</a></li>' +
      '<li>시놉시스 v4의 날짜(사망 1780년 4월 하순 → 조상진 6월 부임)는 새 극중 필수 순서와 충돌 ' + badgeResult(M.F_SYNOPSIS_V4.result) + '. 시놉시스는 수정하지 않았습니다.</li>' +
      '<li>MODE F(극중 필수·제도·인사 연표 유지)의 최소 사료 연대 수정: <b>' + D.f_adapt_mcs[0].length + '개</b> — ' + D.f_adapt_mcs[0].map(function (c) { return '<code>' + esc(c) + '</code>'; }).join(' ') +
      ' (실록 회고의 1781년 성옥을 채택). <a href="#time/F1">예시 해</a></li>' +
      '<li>시놉시스의 결말 압축까지 유지하면 앵커 <b>' + D.compressed.mcs[0].length + '개</b> 수정이 필요하고, 성옥이 두 사료 모두와 어긋납니다. <a href="#time/FC">예시 해</a></li>' +
      '<li>구별되는 성립 인과구조 ' + w.n.toLocaleString('ko-KR') + '개 중 대표 ' + w.rows.length + '개. 가중치 없는 파레토 비지배: <b>' + nd.join(', ') + '</b>. <a href="#worlds">비교</a></li>' +
      '</ol></div>';
    html += '<div class="card"><h3>모드별 판정</h3><div class="table-scroll"><table><thead><tr><th>모드</th><th>설명</th><th>결과</th></tr></thead><tbody>' +
      Object.keys(M).map(function (k) {
        return '<tr class="clickable" data-go="time/' + k + '"><td><code>' + k + '</code></td><td>' + esc(M[k].desc) + '</td><td>' + badgeResult(M[k].result) + '</td></tr>';
      }).join('') + '</tbody></table></div></div>';
    var lay = D.layers;
    html += '<div class="grid2"><div class="card"><h3>제약의 층위</h3><ul class="clist">' + Object.keys(lay).map(function (k) {
      return '<li><code>' + k + '</code> ' + esc(lay[k]) + (D.cost[k] ? '<div class="fine">완화 비용: ' + esc(D.cost[k]) + '</div>' : '') + '</li>';
    }).join('') + '<li><code>SCM</code> 구조방정식(이론·극중 가정에 의한 인과 연결) — 항상 강제, 개입 시 해당 식만 절단</li></ul></div>';
    html += '<div class="card"><h3>경제 시나리오 <span class="badge b-warn">가상 수치</span></h3><p class="fine">G<sub>가용</sub> = G<sub>보유</sub> − G<sub>양식</sub> − G<sub>종자</sub> − G<sub>기타의무</sub>. 단위는 가상 단위 u이며 역사적 관측치가 아닙니다.</p><div class="table-scroll"><table><thead><tr><th>시나리오</th><th class="num">가용</th><th class="num">추가 요구</th><th>요구 &gt; 가용</th></tr></thead><tbody>' +
      Object.keys(D.econ).map(function (k) {
        var e = D.econ[k];
        return '<tr><td>' + esc(k) + '<div class="fine">' + esc(e.label) + '</div></td><td class="num">' + e.G_available + 'u</td><td class="num">' + e.extra_demand + 'u</td><td>' + (e.u_extra_exceeds ? '예 (경제적 거절 사유 성립)' : '아니오') + '</td></tr>';
      }).join('') + '</tbody></table></div></div></div>';
    $('#pane-overview').innerHTML = html;
  }

  // ───────── 시간 충돌 ─────────
  var SHORT = { JSJ_ARRIVE: '조상진 부임', POPHYEOM: '권중립 포폄', DEATH: '윤씨 사망', BURIAL: '매장', ACCUSE: '고발', CHOGEOM: '초검',
    BOKGEOM: '복검', OKSA: '옥사 성립', REVIEW_ORDER: '재조사 명령', JSJ_REINVEST: '조상진 재조사', HYEONGJO_1781_8: '형조 심리',
    JOKJAENG: '조재정 격쟁', FINAL: '최종 판부', JSJ_END: '조상진 재임 종료' };
  var ROWS = ['JSJ_ARRIVE', 'POPHYEOM', 'DEATH', 'BURIAL', 'ACCUSE', 'CHOGEOM', 'BOKGEOM', 'OKSA', 'REVIEW_ORDER',
    'JSJ_REINVEST', 'HYEONGJO_1781_8', 'JOKJAENG', 'FINAL', 'JSJ_END'];
  var VIEWS = Object.keys(D.modes).map(function (k) { return { id: k, kind: 'mode', label: k }; })
    .concat(D.witnesses.map(function (w) { return { id: w.id, kind: 'wit', label: w.label }; }));
  var timeView = 'F_ON_H_SIM';

  function renderTimeChips() {
    $('#time-modes').innerHTML = VIEWS.map(function (v) {
      var extra = v.kind === 'mode' ? ' ' + badgeResult(D.modes[v.id].result).replace('성립 SAT', 'SAT').replace('불성립 UNSAT', 'UNSAT') : ' <span class="badge b-layer">예시 해</span>';
      return '<button type="button" class="chip" role="radio" data-view="' + v.id + '" aria-checked="' + (v.id === timeView) + '">' + esc(v.label) + extra + '</button>';
    }).join('');
  }

  function renderTime(view) {
    if (view) timeView = view;
    if (!VIEWS.some(function (v) { return v.id === timeView; })) timeView = 'F_ON_H_SIM';
    renderTimeChips();
    var mode = D.modes[timeView], wit = D.witnesses.filter(function (w) { return w.id === timeView; })[0];
    var desc = '', detail = '', windows = null, points = null, relaxed = [], active = null;
    if (mode) {
      active = mode.hard;
      desc = '<h3>' + esc(timeView) + ' ' + badgeResult(mode.result) + '</h3><p>' + esc(mode.desc) + '</p>';
      if (mode.result === 'SAT') {
        windows = mode.windows;
        detail = '<div class="card"><h3>가능 구간 (모형상 최소 ~ 최대)</h3><div class="table-scroll"><table><thead><tr><th>사건</th><th>최소</th><th>최대</th></tr></thead><tbody>' +
          Object.keys(windows).map(function (e) {
            return '<tr><td>' + esc(D.events[e].label) + ' <span class="fine">' + varLink(D.events[e].var) + '</span></td><td>' + fmtBound(windows[e][0], 'lo') + '</td><td>' + fmtBound(windows[e][1], 'hi') + '</td></tr>';
          }).join('') + '</tbody></table></div><p class="fine">‘하한/상한 없음’은 사료가 그 방향을 제약하지 않는다는 뜻입니다.</p></div>';
      } else {
        detail = mode.mus.map(function (m, i) {
          return '<div class="card mus"><h3>최소 충돌집합(MUS) ' + (i + 1) + '</h3><p class="fine">아래 조건을 모두 유지하면 해가 없고, 하나라도 빼면 이 충돌은 풀립니다.</p><ul class="clist">' +
            m.map(function (c) { return '<li>' + cItem(c) + '</li>'; }).join('') + '</ul></div>';
        }).join('') + '<div class="card"><h3>최소 수정안(MCS)</h3><p class="fine">한 줄만 완화하면 해가 생깁니다. 비용은 점수가 아니라 종류입니다.</p><ol class="mcs-list">' +
          mode.mcs.map(function (m) {
            var costs = {}; m.forEach(function (c) { var l = D.constraints[c].layer; if (D.cost[l]) costs[D.cost[l]] = 1; });
            return '<li>' + m.map(function (c) { return '<code>' + esc(c) + '</code>'; }).join(' + ') + '<div class="fine">' + esc(Object.keys(costs).join(' / ')) + '</div></li>';
          }).join('') + '</ol></div>';
      }
    } else if (wit) {
      relaxed = wit.relaxed;
      points = wit.events;
      desc = '<h3>' + esc(wit.label) + ' <span class="badge b-layer">예시 해 · 유일해 아님</span></h3>' +
        '<p>완화한 사료 연대 앵커: ' + (relaxed.length ? relaxed.map(function (c) { return '<code>' + esc(c) + '</code>'; }).join(' ') : '없음') + '</p>' +
        (wit.id === 'FC' ? '<p class="fine">강제한 시놉시스 선택: ' + D.compressed.forced.map(function (c) { return '<code>' + esc(c) + '</code>'; }).join(' ') + '</p>' : '') +
        '<p class="fine">보존하지 못한 시놉시스 선택: ' + (wit.dropped_prefs.length ? wit.dropped_prefs.map(function (c) { return '<code>' + esc(c) + '</code>'; }).join(' ') : '없음') + '</p>';
      detail = '<div class="card"><h3>완화한 앵커</h3><ul class="clist">' + relaxed.map(function (c) { return '<li>' + cItem(c) + '</li>'; }).join('') + '</ul></div>' +
        '<div class="card"><h3>예시 시점</h3><div class="table-scroll"><table><thead><tr><th>사건</th><th>예시 시점(음력 서수 근사)</th></tr></thead><tbody>' +
        ROWS.filter(function (e) { return points[e] != null; }).map(function (e) {
          return '<tr><td>' + esc(D.events[e].label) + '</td><td>' + fmt(points[e]) + '</td></tr>';
        }).join('') + '</tbody></table></div></div>';
    }
    $('#time-desc').innerHTML = desc;
    $('#time-detail').innerHTML = detail;
    $('#time-note').textContent = D.meta.index_note + '. 위쪽 띠는 사료 연대 앵커입니다(파랑: 적용, 흐림: 이 모드에서 미적용, 빨간 취소선: 이 해에서 완화).';
    drawTimeline(windows, points, relaxed, active);
  }

  function drawTimeline(windows, points, relaxed, active) {
    var svg = $('#timeline'), NS = 'http://www.w3.org/2000/svg';
    var x0 = L(1780, 1, 1), x1 = L(1783, 12, 30), left = 130, right = 20, W = 1100;
    var rows = ROWS.filter(function (e) { return (windows && windows[e]) || (points && points[e] != null); });
    var anchorH = D.anchors.length * 18 + 10, top = 30 + anchorH, rowH = 26, H = top + Math.max(rows.length, 1) * rowH + 16;
    function X(i) { return left + (Math.max(x0, Math.min(x1, i)) - x0) / (x1 - x0) * (W - left - right); }
    var out = [];
    out.push('<g class="grid">');
    for (var y = 1780; y <= 1783; y++) {
      for (var m = 1; m <= 12; m += 3) {
        var gx = X(L(y, m, 1));
        out.push('<line x1="' + gx + '" x2="' + gx + '" y1="22" y2="' + (H - 8) + '"' + (m === 1 ? ' stroke-width="1.5"' : ' stroke-dasharray="2 4"') + '/>');
        out.push('<text x="' + (gx + 3) + '" y="' + (m === 1 ? 16 : 30) + '"' + (m === 1 ? ' class="year"' : '') + '>' + (m === 1 ? y + '년' : m + '월') + '</text>');
      }
    }
    out.push('</g>');
    D.anchors.forEach(function (a, i) {
      var cls = 'anchor' + (relaxed.indexOf(a.id) >= 0 ? ' relaxed' : '');
      var on = !active || active.indexOf(a.id) >= 0 || relaxed.indexOf(a.id) >= 0;
      var ax = X(a.at[0]), aw = Math.max(5, X(a.at[1]) - ax), ay = 36 + i * 18;
      out.push('<g class="' + cls + '" opacity="' + (on ? 1 : .35) + '"><title>' + esc(a.id + ' — ' + a.label) + '</title><rect x="' + ax + '" y="' + ay + '" width="' + aw + '" height="12" rx="2"/>' +
        '<text x="' + Math.min(ax + aw + 4, W - 150) + '" y="' + (ay + 10) + '">' + esc(a.label) + '</text></g>');
    });
    rows.forEach(function (e, i) {
      var ry = top + i * rowH;
      out.push('<text class="rowlabel" x="8" y="' + (ry + 16) + '">' + esc(SHORT[e] || D.events[e].label) + '</text>');
      if (windows && windows[e]) {
        var a = windows[e][0], b = windows[e][1], xa = X(a), xb = X(b);
        out.push('<rect class="window" x="' + xa + '" y="' + (ry + 6) + '" width="' + Math.max(3, xb - xa) + '" height="12" rx="3"><title>' + esc(fmtBound(a, 'lo') + ' ~ ' + fmtBound(b, 'hi')) + '</title></rect>');
        if (a <= LO || a < x0) out.push('<text x="' + (left + 2) + '" y="' + (ry + 4) + '" class="fine">◀ 하한 없음</text>');
        if (b >= HI || b > x1) out.push('<text x="' + (W - right - 2) + '" y="' + (ry + 4) + '" text-anchor="end" class="fine">' + (b >= HI ? '상한 없음' : '1784년 이후까지') + ' ▶</text>');
      }
      if (points && points[e] != null) {
        out.push('<circle class="pt" cx="' + X(points[e]) + '" cy="' + (ry + 12) + '" r="6"><title>' + esc(fmt(points[e])) + '</title></circle>');
      }
    });
    if (!rows.length) out.push('<text x="' + left + '" y="' + (top + 18) + '">이 모드는 해가 없어 사건 구간을 그릴 수 없습니다. 아래 충돌집합을 보세요.</text>');
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.setAttribute('height', H);
    svg.innerHTML = out.join('');
    svg.setAttribute('xmlns', NS);
  }

  // ───────── 가능세계 ─────────
  var FLAG_KEYS = ['경제적 인과성', '희생양화(행위자 경로)', '행정적 인과성', '가족체계 설명력', '사법적 인과성', '수사 가능성'];
  var curWorld = null;
  function renderWorlds(sel) {
    var W = D.worlds;
    $('#worlds-intro').innerHTML = 'MODE F에서 핵심 인과 차원 ' + W.dims.length + '개로 구별되는 성립 구조 <b>' + W.n.toLocaleString('ko-KR') + '개</b> 중, 시놉시스에 가장 가까운 W01에서 출발해 최대 다양성으로 고른 대표 ' + W.rows.length + '개입니다. ' +
      '모든 세계에 공통으로 강제되는 극중 가정(세계별 가정 수에서 제외): ' + W.forced.map(function (k) { return '<code title="' + esc(symLabel(k)) + '">' + esc(symLabel(k)) + '</code>'; }).join(' · ') +
      '. 파레토 비지배는 ‘가정 수↓·연대 변경 수↓·각 설명 기준 충족↑’에서 다른 세계에 모두 뒤지지 않는다는 뜻이며 순위가 아닙니다.';
    var only = $('#pareto-only').checked;
    var rows = W.rows.filter(function (r) { return !only || r.pareto; });
    var head = '<thead><tr><th>세계</th>' + W.dims.map(function (d, i) { return '<th class="code" title="' + esc(d[1]) + '">D' + (i + 1) + '</th>'; }).join('') +
      FLAG_KEYS.map(function (f, i) { return '<th class="code" title="' + esc(f) + '">C' + (i + 1) + '</th>'; }).join('') + '<th class="num">고유 가정</th><th class="num">연대 수정</th><th>파레토</th></tr></thead>';
    var body = '<tbody>' + rows.map(function (r) {
      return '<tr class="clickable' + (r.world === sel ? ' selected' : '') + '" data-go="worlds/' + r.world + '"><td><b>' + r.world + '</b></td>' +
        W.dims.map(function (d) { return '<td class="dot ' + (r.proj[d[0]] ? 'on' : 'off') + '">' + (r.proj[d[0]] ? '●' : '○') + '</td>'; }).join('') +
        FLAG_KEYS.map(function (f) { return '<td class="dot ' + (r.flags[f] ? 'on' : 'off') + '">' + (r.flags[f] ? '●' : '○') + '</td>'; }).join('') +
        '<td class="num">' + r.n_assump + '</td><td class="num">' + r.n_dates + '</td><td>' + (r.pareto ? '<span class="badge b-ok">비지배</span>' : '') + '</td></tr>';
    }).join('') + '</tbody>';
    $('#world-matrix').innerHTML = head + body;
    $('#world-legend').innerHTML = '<li><b>인과 차원(D) — ● 참 / ○ 거짓</b></li>' + W.dims.map(function (d, i) { return '<li><code>D' + (i + 1) + '</code>' + esc(d[1]) + '</li>'; }).join('') +
      '<li><b>설명 기준(C) — ● 충족</b></li>' + FLAG_KEYS.map(function (f, i) { return '<li><code>C' + (i + 1) + '</code>' + esc(f) + '</li>'; }).join('');
    var r = W.rows.filter(function (x) { return x.world === sel; })[0];
    curWorld = r ? r.world : null;
    $('#world-detail').innerHTML = r ? worldCard(r) : '<p class="muted">행을 누르면 세계의 인과 경로와 필요한 가정이 나옵니다.</p>';
  }
  function worldCard(r) {
    return '<div class="card"><h3>' + r.world + ' ' + (r.pareto ? '<span class="badge b-ok">파레토 비지배</span>' : '') + '</h3><dl class="kv">' +
      '<dt>행정(권분·포폄·복검)</dt><dd>' + esc(r.admin) + '</dd>' +
      '<dt>살해 동기 경로</dt><dd>' + esc(r.murder) + '</dd>' +
      '<dt>무고 동기</dt><dd>' + esc(r.frame) + '</dd>' +
      '<dt>시간제약</dt><dd>극중 필수 순서 충족. 최소 사료 연대 수정 ' + r.n_dates + '개: ' + r.date_sets.map(function (s) { return s.map(function (c) { return '<code>' + esc(c) + '</code>'; }).join('+'); }).join(' 또는 ') + '</dd>' +
      '<dt>세계 고유 극중 가정 (' + r.assump.length + ')</dt><dd><ul class="clist">' + r.assump.map(function (k) {
        return '<li>' + varLink(symVar(k)) + ' ' + esc(symLabel(k)) + '</li>';
      }).join('') + '</ul></dd></dl>' +
      '<p><button type="button" class="btn" data-go="graph/' + r.world + '">인과 그래프에서 이 세계 보기</button></p>' +
      '<p class="fine">이 세계는 논리적으로 성립할 뿐이며 역사적 진실 가능성의 순위가 아닙니다.</p></div>';
  }

  // ───────── 반사실 ─────────
  function renderCF(qid) {
    var q = D.cf.filter(function (x) { return x.qid === qid; })[0] || D.cf[0];
    $('#cf-list').innerHTML = D.cf.map(function (x) {
      return '<li><button type="button" data-go="cf/' + x.qid + '" aria-current="' + (x.qid === q.qid) + '"><b>' + x.qid + '</b>' + esc(x.question) + '</button></li>';
    }).join('');
    var rows = Object.keys(q.intervened).map(function (o) {
      var ex = q.minimal_extra_assumptions[o], changed = q.baseline[o] !== q.intervened[o];
      var need = ex == null ? '해당 없음(불가능)' : (ex.necessary_beyond_baseline.length ? ex.necessary_beyond_baseline.map(function (k) { return varLink(symVar(k)) + ' ' + esc(symLabel(k)); }).join('<br>') : '없음');
      return '<tr><td>' + esc(symLabel(o)) + '<div class="fine"><code>' + esc(o) + '</code></div></td><td>' + esc(q.baseline[o]) + '</td><td' + (changed ? ' class="change"' : '') + '>' + esc(q.intervened[o]) + '</td><td>' + need + '</td></tr>';
    }).join('');
    $('#cf-detail').innerHTML = '<div class="card"><h3>' + q.qid + '. ' + esc(q.question) + '</h3><dl class="kv">' +
      '<dt>변경한 변수</dt><dd>' + Object.keys(q.changed).map(function (k) { return '<code>' + esc(k) + '</code> = ' + q.changed[k] + ' (' + esc(symLabel(k)) + ')'; }).join('<br>') + '</dd>' +
      '<dt>연산</dt><dd>' + esc(q.operation) + '</dd>' +
      '<dt>유지한 제약</dt><dd>' + q.kept_constraints.filter(function (c) { return !/^STR/.test(c); }).map(function (c) { return '<code>' + esc(c) + '</code>'; }).join(' ') + ' + 모형 구조(STR) 전부</dd>' +
      '<dt>풀어 둔 제약</dt><dd>' + (q.dropped_film_requirements.concat(q.dropped_historical_facts).map(function (c) { return '<code>' + esc(c) + '</code>'; }).join(' ') || '없음') + '<div class="fine">개입 변수의 후손이나 질문한 결과를 미리 고정하는 제약은 풀어야 결과를 물을 수 있습니다.</div></dd>' +
      '<dt>관찰 조건화</dt><dd>' + (q.conditioning_with_all_film_requirements_sat ? '성립' : '<b>불성립</b> (극중 필수 조건을 모두 유지하면 이 세계는 관찰될 수 없음)') + '</dd></dl>' +
      '<div class="table-scroll"><table><thead><tr><th>결과 변수</th><th>기준선</th><th>개입 후</th><th>결과를 위해 추가로 반드시 필요한 가정</th></tr></thead><tbody>' + rows + '</tbody></table></div>' +
      '<h4 style="margin-top:14px">모형상 결과</h4><p>' + esc(q.text) + '</p><h4>해석 한계</h4><p class="hint">' + esc(q.limit) + '</p></div>';
  }

  // ───────── 인과 그래프 ─────────
  var cy = null;
  function cssVar(n) { return getComputedStyle(document.documentElement).getPropertyValue(n).trim(); }
  function initGraph() {
    if (cy) return;
    if (typeof window.cytoscape !== 'function') {
      var e = $('#graph-error'); e.hidden = false; e.textContent = '그래프 라이브러리(cytoscape)를 불러오지 못했습니다.'; return;
    }
    var col = { endo: cssVar('--c-endo'), creative: cssVar('--c-creative'), hist: cssVar('--c-hist'), inference: cssVar('--c-inference') };
    var ecol = { source: cssVar('--c-source'), theory: cssVar('--c-theory'), film: cssVar('--c-film') };
    var els = D.graph.nodes.map(function (n) {
      return { group: 'nodes', data: { id: n.id, label: n.var + '\n' + n.label, kind: n.kind }, position: n.pos };
    }).concat(D.graph.edges.map(function (e, i) {
      return { group: 'edges', data: { id: 'e' + i, source: e.source, target: e.target, kind: e.kind } };
    }));
    cy = window.cytoscape({
      container: $('#cy'), elements: els, layout: { name: 'preset' }, wheelSensitivity: 0.2, minZoom: 0.15, maxZoom: 2.5,
      style: [
        { selector: 'node', style: { 'shape': 'round-rectangle', 'width': 190, 'height': 44, 'label': 'data(label)', 'text-wrap': 'wrap', 'text-max-width': 180,
          'font-size': 11, 'text-valign': 'center', 'color': cssVar('--ink'), 'background-color': cssVar('--surface'), 'border-width': 2, 'border-color': col.endo, 'font-family': cssVar('--font') } },
        { selector: 'node[kind = "creative"]', style: { 'border-color': col.creative, 'border-style': 'dashed', 'shape': 'round-tag' } },
        { selector: 'node[kind = "hist"]', style: { 'border-color': col.hist, 'shape': 'round-tag' } },
        { selector: 'node[kind = "inference"]', style: { 'border-color': col.inference, 'shape': 'round-tag' } },
        { selector: 'edge', style: { 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'arrow-scale': .8, 'width': 1.4, 'opacity': .75 } },
        { selector: 'edge[kind = "source"]', style: { 'line-color': ecol.source, 'target-arrow-color': ecol.source, 'width': 3 } },
        { selector: 'edge[kind = "theory"]', style: { 'line-color': ecol.theory, 'target-arrow-color': ecol.theory } },
        { selector: 'edge[kind = "film"]', style: { 'line-color': ecol.film, 'target-arrow-color': ecol.film, 'line-style': 'dashed' } },
        { selector: 'node.t', style: { 'background-color': cssVar('--warn-bg'), 'border-width': 3 } },
        { selector: 'node.f', style: { 'opacity': .35 } },
        { selector: 'node:selected', style: { 'border-color': cssVar('--accent'), 'border-width': 4 } },
        { selector: 'edge.hl', style: { 'opacity': 1, 'width': 3.5 } }
      ]
    });
    cy.on('tap', 'node', function (ev) { showNode(ev.target.id()); });
    $('#graph-legend').innerHTML =
      '<span><i style="border-color:' + ecol.source + ';border-top-width:3px"></i>' + EDGE_KO.source + '</span>' +
      '<span><i style="border-color:' + ecol.theory + '"></i>' + EDGE_KO.theory + '</span>' +
      '<span><i style="border-color:' + ecol.film + ';border-top-style:dashed"></i>' + EDGE_KO.film + '</span>' +
      '<span><span class="sw" style="border:2px solid ' + col.endo + '"></span>내생 변수(구조방정식)</span>' +
      '<span><span class="sw" style="border:2px solid ' + col.hist + '"></span>외생: 사료 서술</span>' +
      '<span><span class="sw" style="border:2px solid ' + col.inference + '"></span>외생: 사료로부터의 추론</span>' +
      '<span><span class="sw" style="border:2px dashed ' + col.creative + '"></span>외생: 극중 가정</span>' +
      '<span><span class="sw" style="background:' + cssVar('--warn-bg') + ';border:2px solid ' + col.endo + '"></span>선택한 세계에서 참</span>';
    $('#graph-world').innerHTML = '<option value="">세계 선택 안 함</option>' + D.worlds.rows.map(function (r) {
      return '<option value="' + r.world + '">' + r.world + (r.pareto ? ' (파레토 비지배)' : '') + '</option>';
    }).join('');
  }
  var graphFramed = false;
  function frameGraph() {
    // 전체를 맞추면 글자가 읽히지 않으므로, 읽을 수 있는 최소 배율을 지키고 왼쪽(원인 쪽)부터 보여 준다.
    cy.fit(undefined, 20);
    if (cy.zoom() < 0.55) {
      var bb = cy.elements().boundingBox();
      cy.zoom(0.55);
      cy.pan({ x: 20 - bb.x1 * 0.55, y: cy.height() / 2 - ((bb.y1 + bb.y2) / 2) * 0.55 });
    }
    graphFramed = true;
  }
  function applyWorld(w) {
    if (!cy) return;
    var r = D.worlds.rows.filter(function (x) { return x.world === w; })[0];
    $('#graph-world').value = r ? r.world : '';
    cy.nodes().removeClass('t f');
    if (!r) return;
    cy.nodes().forEach(function (n) { n.addClass(r.vals[n.id()] ? 't' : 'f'); });
  }
  function showNode(id) {
    var en = D.endo[id], ex = D.exog[id], v = VAR[(en || ex || {}).var];
    var w = $('#graph-world').value, r = D.worlds.rows.filter(function (x) { return x.world === w; })[0];
    cy.edges().removeClass('hl'); cy.$id(id).connectedEdges().addClass('hl');
    var html = '<h3>' + esc(symLabel(id)) + '</h3><p><code>' + esc(id) + '</code> · 변수 ' + varLink((en || ex).var) + '</p>';
    if (en) {
      html += '<p><span class="badge b-layer">내생 변수</span> 식의 근거: ' + esc(EDGE_KO[en.kind]) + '</p><p class="fine">부모: ' + en.parents.map(function (p) { return '<code>' + esc(p) + '</code>'; }).join(', ') + '</p>';
    } else {
      html += '<p><span class="badge b-layer">외생 변수</span> ' + esc(EXOG_LAYER[ex.layer] || ex.layer) + '</p>';
    }
    if (r) html += '<p>' + r.world + '에서: <b>' + (r.vals[id] ? '참' : '거짓') + '</b></p>';
    if (v) html += '<dl class="kv"><dt>정의</dt><dd>' + esc(v.definition) + '</dd><dt>층위</dt><dd>' + esc(LAYER_VAR[v.layer]) + '</dd><dt>검증 상태</dt><dd>' + statusBadge(v.evidence_status) + '</dd><dt>출처</dt><dd>' + (v.source_ids.map(srcLink).join(', ') || '없음') + '</dd></dl>';
    $('#graph-detail').innerHTML = html;
  }

  // ───────── 근거 추적 ─────────
  var evGroup = '', evLayer = '';
  function renderEvidenceFilters() {
    var groups = [['', '전체'], ['T', 'T 시간'], ['E', 'E 경제'], ['A', 'A 행정'], ['S', 'S 희생양화'], ['F', 'F 가족'], ['M', 'M 이가원'], ['J', 'J 검험·재조사']];
    $('#ev-groups').innerHTML = groups.map(function (g) { return '<button type="button" class="chip" data-evgroup="' + g[0] + '" aria-pressed="' + (evGroup === g[0]) + '">' + g[1] + '</button>'; }).join('');
    var layers = [['', '모든 층위']].concat(Object.keys(LAYER_VAR).map(function (k) { return [k, LAYER_VAR[k]]; }));
    $('#ev-layers').innerHTML = layers.map(function (g) { return '<button type="button" class="chip" data-evlayer="' + g[0] + '" aria-pressed="' + (evLayer === g[0]) + '">' + g[1] + '</button>'; }).join('');
  }
  function renderEvidence(sel) {
    renderEvidenceFilters();
    var q = ($('#ev-search').value || '').trim().toLowerCase();
    var vs = D.variables.filter(function (v) {
      if (evGroup && v.group !== evGroup) return false;
      if (evLayer && v.layer !== evLayer) return false;
      if (!q) return true;
      return (v.id + ' ' + v.name + ' ' + v.source_ids.join(' ') + ' ' + v.definition).toLowerCase().indexOf(q) >= 0;
    });
    $('#ev-table').innerHTML = '<thead><tr><th>ID</th><th>변수 또는 주장</th><th>층위</th><th>근거 유형</th><th>검증 상태</th></tr></thead><tbody>' +
      vs.map(function (v) {
        return '<tr class="clickable' + (v.id === sel ? ' selected' : '') + '" data-go="evidence/' + v.id + '"><td>' + v.id + '</td><td>' + esc(v.name) + '</td><td>' + esc(LAYER_VAR[v.layer]) + '</td><td>' + esc(v.basis_type) + (v.context_claim_ids.length ? '<div class="fine">비교·후대 맥락 포함</div>' : '') + '</td><td>' + statusBadge(v.evidence_status) + '</td></tr>';
      }).join('') + (vs.length ? '' : '<tr><td colspan="5" class="muted">조건에 맞는 변수가 없습니다.</td></tr>') + '</tbody>';
    var v = VAR[sel];
    $('#ev-detail').innerHTML = v ? varCard(v) : '<p class="muted">변수를 누르면 근거가 나옵니다.</p>';
  }
  function claimHtml(c) {
    return '<div class="claim"><p><code>' + esc(c.claim_id) + '</code> <span class="badge b-layer">' + esc(c.claim_type) + '</span> ' + statusBadge(c.verification_status) + '</p>' +
      '<p>' + esc(c.claim) + '</p>' +
      (c.original_text ? '<p><span class="orig">' + esc(c.original_text) + '</span></p>' + (c.translation ? '<p class="hint">' + esc(c.translation) + '</p>' : '') : '') +
      '<dl class="kv"><dt>출처</dt><dd>' + (c.source_id ? srcLink(c.source_id) : '없음') + ' · ' + esc(c.source_locator) + '</dd>' +
      '<dt>사건 날짜</dt><dd>' + esc(c.event_date) + '</dd><dt>편찬·작성</dt><dd>' + esc(c.source_date || '—') + '</dd>' +
      (c.url ? '<dt>원문 링크</dt><dd><a href="' + esc(c.url) + '" target="_blank" rel="noopener">' + esc(c.url) + '</a></dd>' : '') +
      (c.provenance_note ? '<dt>메모</dt><dd class="fine">' + esc(c.provenance_note) + '</dd>' : '') + '</dl></div>';
  }
  function varCard(v) {
    var cl = v.claim_ids.map(function (id) { return CLM[id]; }).filter(Boolean);
    var cx = v.context_claim_ids.map(function (id) { return CLM[id]; }).filter(Boolean);
    return '<div class="card"><h3>' + v.id + ' ' + esc(v.name) + '</h3><dl class="kv">' +
      '<dt>정의</dt><dd>' + esc(v.definition) + '</dd><dt>값</dt><dd>' + esc(v.domain) + '</dd>' +
      '<dt>층위</dt><dd>' + esc(LAYER_VAR[v.layer]) + '</dd><dt>근거 유형</dt><dd>' + esc(v.basis_type) + '</dd>' +
      '<dt>검증 상태</dt><dd>' + statusBadge(v.evidence_status) + '</dd>' +
      '<dt>출처</dt><dd>' + (v.source_ids.map(srcLink).join(', ') || '없음') + '</dd>' +
      (v.model_symbols.length ? '<dt>모형 기호</dt><dd>' + v.model_symbols.map(function (s) { return '<code>' + esc(s) + '</code>'; }).join(' ') + '</dd>' : '') +
      (v.note ? '<dt>주</dt><dd>' + esc(v.note) + '</dd>' : '') + '</dl>' +
      (v.layer === 'scenario' ? '<p class="notice">이 변수는 극중 설정·가설이며 역사적 사실이 아닙니다.</p>' : '') +
      '<h4>직접 근거 주장 (' + cl.length + ')</h4>' + (cl.map(claimHtml).join('') || '<p class="muted">없음</p>') +
      (cx.length ? '<h4 style="margin-top:14px">비교·후대 맥락 (' + cx.length + ') — 1780년 배천의 관측 근거로 쓰지 않음</h4>' + cx.map(claimHtml).join('') : '') + '</div>';
  }

  // ───────── 참고문헌 ─────────
  function apaHtml(s) {
    var link = s.url ? '<a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.title) + '</a>' : '<i>' + esc(s.title) + '</i>';
    var t = esc(s.apa).replace(/\*([^*]+)\*/g, '<i>$1</i>');
    return t.replace('{title_link}', link).replace('{title}', esc(s.title));
  }
  function renderRefs(sel) {
    var html = '';
    Object.keys(CAT_KO).forEach(function (cat) {
      html += '<h3>' + esc(CAT_KO[cat]) + '</h3>';
      D.sources.filter(function (s) { return s.category === cat; }).forEach(function (s) {
        var st = (s.url_check || {}).status || 'NOT_CHECKED';
        html += '<div class="ref" id="ref-' + esc(s.source_id) + '"><p class="apa"><b>[' + esc(s.source_id) + ']</b> ' + apaHtml(s) + '</p><div class="meta">' +
          '<span class="badge ' + (st === 'OK' ? 'b-ok' : 'b-warn') + '">' + esc(D.us_ko[st] || st) + '</span>' +
          '<span class="badge ' + (s.text_verification === 'ORIGINAL_VERIFIED' ? 'b-ok' : 'b-warn') + '">' + esc((D.tv_ko[s.text_verification] || s.text_verification).replace(/\*\*/g, '')) + '</span>' +
          '<span>사건 날짜: ' + esc(s.event_date) + '</span><span>편찬·작성: ' + esc(s.source_date) + '</span>' +
          (s.missing_fields && s.missing_fields.length ? '<span>확인 못 한 서지 요소: ' + esc(s.missing_fields.join(', ')) + '</span>' : '') +
          (!s.url ? '<span>링크 없음: ' + esc(s.url_missing_reason) + '</span>' : '') +
          (s.url_conflict ? '<span>링크 불일치: ' + esc(s.url_conflict) + '</span>' : '') +
          (s.local_copy ? '<span>로컬: ' + s.local_copy.split(';').map(function (p) { return '<code>' + esc(p.trim()) + '</code>'; }).join(' ') + '</span>' : '') +
          '</div></div>';
      });
    });
    $('#refs').innerHTML = html;
    if (sel) { var el = document.getElementById('ref-' + sel); if (el) { el.scrollIntoView({ block: 'center' }); el.style.background = 'var(--warn-bg)'; } }
  }

  // ───────── 라우팅 ─────────
  var TABS = ['overview', 'time', 'worlds', 'cf', 'graph', 'evidence', 'refs'];
  function route() {
    var h = decodeURIComponent(location.hash.replace(/^#/, '')), parts = h.split('/');
    var tab = TABS.indexOf(parts[0]) >= 0 ? parts[0] : 'overview', arg = parts[1] || '';
    Array.prototype.forEach.call(document.querySelectorAll('#tabs [data-tab]'), function (b) { b.setAttribute('aria-selected', b.dataset.tab === tab); });
    Array.prototype.forEach.call(document.querySelectorAll('.pane'), function (p) { p.hidden = p.dataset.pane !== tab; });
    if (tab === 'overview') renderOverview();
    if (tab === 'time') renderTime(arg || null);
    if (tab === 'worlds') renderWorlds(arg || curWorld);
    if (tab === 'cf') renderCF(arg || 'Q1');
    if (tab === 'graph') { initGraph(); if (cy) { cy.resize(); applyWorld(arg); if (!graphFramed) frameGraph(); } }
    if (tab === 'evidence') renderEvidence(arg);
    if (tab === 'refs') renderRefs(arg);
  }
  function go(path) { if (location.hash === '#' + path) route(); else location.hash = path; }

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-go],[data-tab],[data-view],[data-evgroup],[data-evlayer]');
    if (!t) return;
    if (t.dataset.go) { e.preventDefault(); go(t.dataset.go); }
    else if (t.dataset.tab) go(t.dataset.tab);
    else if (t.dataset.view) go('time/' + t.dataset.view);
    else if (t.dataset.evgroup != null) { evGroup = t.dataset.evgroup; renderEvidence(location.hash.split('/')[1]); }
    else if (t.dataset.evlayer != null) { evLayer = t.dataset.evlayer; renderEvidence(location.hash.split('/')[1]); }
  });
  $('#ev-search').addEventListener('input', function () { renderEvidence(location.hash.split('/')[1]); });
  $('#pareto-only').addEventListener('change', function () { renderWorlds(curWorld); });
  $('#graph-world').addEventListener('change', function (e) { go('graph' + (e.target.value ? '/' + e.target.value : '')); });
  $('#graph-fit').addEventListener('click', function () { if (cy) cy.fit(undefined, 20); });
  $('#graph-read').addEventListener('click', function () { if (cy) { graphFramed = false; frameGraph(); } });
  document.getElementById('tabs').addEventListener('keydown', function (e) {
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    var cur = TABS.indexOf((location.hash.replace('#', '').split('/')[0]) || 'overview');
    var nx = TABS[(cur + (e.key === 'ArrowRight' ? 1 : TABS.length - 1)) % TABS.length];
    go(nx); var b = document.querySelector('[data-tab="' + nx + '"]'); if (b) b.focus();
  });
  window.addEventListener('hashchange', route);

  header();
  route();
  window.__sigok = { ready: true, go: go, get cy() { return cy; } };
})();
