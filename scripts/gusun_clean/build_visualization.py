"""Interactive Temporal DAG — canonical 산출물 → docs/data/*.json (+ bundle.js).

목적: 이미 만들어진 Mechanism Super-DAG를 탐색용 웹 화면으로 보여 주기 위한 데이터만 만든다.
- 새 node·edge·사실·판단을 만들지 않는다. 상태·configuration·공존 판정·개입 결과·후보 등급은 canonical CSV 값을 그대로 옮긴다.
- 배치(x·y)는 결정적으로 계산한다(preset layout). 날짜가 있는 관측 node는 날짜 순서대로 왼쪽 → 오른쪽에 놓인다.
  날짜가 없는 node(메커니즘·구조 변수·후보·context·UNRESOLVED)는 별도 lane(행)에 두고, x는 연결된 관측 node 근처로만 정한다.
  context node에는 날짜 lane·날짜 표시를 주지 않는다(사건이 아니므로).
- 출력은 바이트 단위로 결정적이다(정렬된 key, 고정 순서, timestamp 없음).

실행: build.py가 Audit 4 뒤에 호출한다. 단독 실행도 가능하다:
    python3 scripts/gusun_clean/build_visualization.py
(단독 실행 시 Audit 4 결과는 database/gusun_clean.duckdb의 audit_findings에서 읽는다.)
"""
import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

ROOT = HERE.parents[1]
PACK = ROOT / "gusun_clean_restart_csv_pack"
OUT = ROOT / "output" / "clean"
DOCS = ROOT / "docs"
DATA_FILES = ["super_dag", "worlds", "interactions", "interventions", "candidates", "views", "facts", "meta"]

# canonical 입력 파일(생성 근거). meta.json에 sha256과 함께 적는다.
CANON_FILES = {
    "sd_nodes": ("out", "mechanism_super_dag_nodes.csv"),
    "sd_edges": ("out", "mechanism_super_dag_edges.csv"),
    "episodes": ("out", "episode_nodes.csv"),
    "observed_edges": ("out", "observed_edges.csv"),
    "candidates": ("out", "latent_candidates.csv"),
    "gaps": ("out", "gaps.csv"),
    "worlds": ("out", "narrative_worlds.csv"),
    "configs": ("out", "world_mechanism_configurations.csv"),
    "interactions": ("out", "mechanism_interaction_matrix.csv"),
    "interventions": ("out", "mechanism_interventions.csv"),
    "rules": ("out", "qualitative_structural_rules.csv"),
    "definitions": ("out", "mechanism_definitions.csv"),
    "freeze": ("out", "observed_dag_freeze.json"),
    "facts": ("pack", "01_confirmed_facts.csv"),
    "inst": ("pack", "02_institutional_normative_features.csv"),
    "env": ("pack", "03_environment_1793.csv"),
    "sources": ("pack", "04_source_records.csv"),
}

TITLE = "구순–김명신 사건 Mechanism Super-DAG"
DESCRIPTION = "확정된 사건은 고정하고, 사료가 알려주지 않는 중간 과정은 LATENT 메커니즘으로 비교한다."
ROLE_NOTE = ("Mermaid(output/clean/mechanism_super_dag.mmd)는 정적 문서 요약이고, 이 화면은 탐색용이다. "
             "두 산출물은 같은 canonical CSV에서 나온다.")

# 화면 표시용 이름(사용자 명세의 메커니즘 한국어 이름). canonical 이름(mechanism_name)은 그대로 함께 보여 준다.
MECH_DISPLAY = {"M1": "공식 정보 경로", "M2": "진술 증폭", "M3": "사적 통로", "M4": "분산 실무",
                "M5": "재검토·교정", "M6": "5월 초기 판단 근거", "MB": "구금·생물학적 경과"}

# 표시 상태 그룹: canonical sd_status → 필터 그룹. 이름만 줄인 1:1 대응이다(상태를 바꾸지 않음).
STATUS_GROUPS = {"OBSERVED": "OBSERVED", "DERIVED": "DERIVED", "LATENT_MECHANISM": "LATENT",
                 "CONTEXT": "CONTEXT", "UNRESOLVED": "UNRESOLVED"}

# world configuration 값의 표시. UNSPECIFIED는 OFF가 아니다.
CONFIG_DISPLAY = {
    "ON": dict(label="ON", css="cfg-on", note="그 메커니즘의 핵심 gap을 core 후보로 채움"),
    "PARTIAL": dict(label="PARTIAL", css="cfg-partial", note="보조 후보만 쓰거나 같은 world에 부정 후보가 함께 있음"),
    "UNSPECIFIED": dict(label="UNSPECIFIED", css="cfg-unspecified",
                        note="관련 후보가 없어 작동 여부를 말하지 않음. OFF가 아니다(UNSPECIFIED ≠ OFF)"),
    "OFF": dict(label="OFF", css="cfg-off", note="그 메커니즘을 부정하는 후보만 있음"),
}

# 관측 branch lane(위 → 아래). 책임 branch(B)와 생물학 branch(A)가 화면에서도 떨어지도록 배치한다.
BRANCH_LANES = [
    ("RELATION", "관계"), ("THEFT", "도난·소장"), ("SUSPECT_INFORMATION", "혐의 정보"),
    ("BARRACKS_OPERATION", "병영 작전·체포"), ("COMMAND_RESPONSIBILITY", "지휘 책임"), ("RESPONSIBILITY", "책임 판단"),
    ("DISPOSITION", "처분"), ("REINVESTIGATION", "재조사 명령"), ("REVIEW", "재검토"), ("THEFT_JUDGMENT", "도난 판단"),
    ("JISE", "지세 호칭"), ("CAUSATION_BOUNDARY", "인과 경계"), ("DETENTION_DEATH", "구금·사망 보고"),
    ("BIOLOGICAL", "사인 판단 (branch A)"),
]
ROYAL_LAYERS = {"ROYAL_JUDGMENT", "ROYAL_ORDER", "ROYAL_JUDGMENT_AND_ORDER"}
BANDS = [
    dict(id="UNDATED", label="날짜 미기록", sub="시간 축 밖 · 위치는 날짜를 뜻하지 않음", dated=False),
    dict(id="FEB", label="1793-02 (2월)", sub="관계 · 도난 · 병영 출동", dated=True),
    dict(id="MAR", label="1793-03 (3월)", sub="3/4 체포 지시 · 체포", dated=True),
    dict(id="MAY", label="1793-05 (5월)", sub="장계 · 1차 판단 · 재조사", dated=True),
    dict(id="JUN", label="1793-06 (6월)", sub="별단 · 안핵 신문·복명", dated=True),
    dict(id="FINAL", label="최종 판단·처분", sub="6/13 정조 판단 → 처분 → 6/16", dated=True),
]

# edge type 표시 규칙(범례). 색·선 모양·화살표를 함께 바꿔 색만으로 구분하지 않는다.
EDGE_STYLES = {
    "TEMPORAL_BEFORE": dict(color="#898781", line="solid", arrow="triangle", group="관측 (frozen)", ko="시간 선후"),
    "PROCEDURAL_NEXT": dict(color="#256abf", line="solid", arrow="triangle", group="관측 (frozen)", ko="절차상 다음 단계"),
    "INFORMATION_FLOW": dict(color="#1baf7a", line="dashed", arrow="triangle", group="관측 (frozen)", ko="정보 흐름(기록 근거)"),
    "ORDER_TO_ACTION": dict(color="#0b0b0b", line="solid", arrow="triangle-tee", group="관측 (frozen)", ko="명령 → 실행"),
    "REVIEW_OF": dict(color="#4a3aa7", line="solid", arrow="vee", group="관측 (frozen)", ko="검토·심리"),
    "REVISES": dict(color="#e34948", line="solid", arrow="triangle-backcurve", group="관측 (frozen)", ko="판단 수정"),
    "RESPONSIBILITY_LINK": dict(color="#c98500", line="dashed", arrow="diamond", group="관측 (frozen)", ko="책임 귀속(판단 node로만)"),
    "CONTEXT_SUPPORTS": dict(color="#008300", line="dotted", arrow="circle", group="관측 (frozen)", ko="context가 판단을 뒷받침"),
    "CONTRADICTS_AT_CLAIM_LEVEL": dict(color="#e34948", line="dashed", arrow="tee", group="관측 (frozen)", ko="주장 수준 상충"),
    "CONSTRAINS": dict(color="#008300", line="dotted", arrow="square", group="Super-DAG 분석", ko="제도 context가 메커니즘을 제약"),
    "CONTEXT_COMPATIBLE": dict(color="#008300", line="dotted", arrow="circle-triangle", group="Super-DAG 분석", ko="환경 호환성(개인 감염 아님)"),
    "INSTANTIATED_BY": dict(color="#4a3aa7", line="solid", arrow="triangle", group="Super-DAG 분석", ko="메커니즘 → 후보(core/보조)"),
    "INSTANTIATED_BY_SECONDARY": dict(color="#4a3aa7", line="dashed", arrow="triangle", group="Super-DAG 분석", ko="메커니즘 → 후보(보조 메커니즘)"),
    "CONTRIBUTES_TO": dict(color="#eb6834", line="solid", arrow="triangle", group="Super-DAG 분석", ko="후보 → 구조 변수(규칙 입력)"),
    "RULE_INPUT": dict(color="#4a3aa7", line="dashed", arrow="vee", group="Super-DAG 분석", ko="구조 변수 → 구조 변수"),
    "EXPLAINS_TRANSITION_TO": dict(color="#eb6834", line="dashed", arrow="triangle", group="Super-DAG 분석", ko="구조 변수가 관측 전이를 설명"),
    "EXPLAINS_OBSERVED": dict(color="#eb6834", line="dotted", arrow="triangle", group="Super-DAG 분석", ko="관측 재검토 사건을 설명(사건은 그대로)"),
    "ANCHORED_TO": dict(color="#4a3aa7", line="dotted", arrow="square", group="Super-DAG 분석", ko="M5가 관측 backbone에 고정"),
    "CONDITIONS": dict(color="#d55181", line="dashed", arrow="diamond", group="Super-DAG 분석", ko="미해결 항목이 후보의 성립 조건"),
}

COL_W = 158          # 관측 column 간격
BAND_GAP = 60        # 시간 구간 사이 여백
ROW_H = 64           # lane 안의 한 행 높이
LANE_PAD = 12
GROUP_GAP = 100


# --------------------------------------------------------------------------- 입력
def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def load_canonical(out=OUT, pack=PACK):
    """canonical 산출물을 읽는다. 값은 문자열 그대로 둔다."""
    canon, hashes = {}, {}
    for key, (where, name) in CANON_FILES.items():
        path = (out if where == "out" else pack) / name
        canon[key] = json.loads(path.read_text(encoding="utf-8")) if name.endswith(".json") else _read_csv(path)
        hashes[f"{'output/clean' if where == 'out' else 'gusun_clean_restart_csv_pack'}/{name}"] = _sha(path)
    canon["_hashes"] = hashes
    return canon


def audit4_from_db(db=ROOT / "database" / "gusun_clean.duckdb"):
    try:
        import duckdb
        con = duckdb.connect(str(db), read_only=True)
        rows = con.execute("SELECT check_name, severity, target, message FROM audit_findings WHERE audit='AUDIT4' "
                           "ORDER BY check_name, target, message").fetchall()
        con.close()
        return [dict(check=a, severity=b, target=c, message=d) for a, b, c, d in rows]
    except Exception:  # noqa: BLE001 — DB가 없으면 Audit 4 표시만 빠진다
        return []


# --------------------------------------------------------------------------- 배치
def _int(x):
    return int(x) if str(x).strip() else None


def date_key(ep):
    """관측 node의 정렬 기준일(MMDD): t_max가 있으면 t_max, 없으면 t_min. 둘 다 없으면 None(날짜 미기록)."""
    return _int(ep.get("t_max", "")) or _int(ep.get("t_min", ""))


def band_of(ep, k):
    if k is None:
        return "UNDATED"
    m = k // 100
    if m == 2:
        return "FEB"
    if m == 3:
        return "MAR"
    if m in (4, 5):
        return "MAY"
    if k >= 613 and ep["layer"] in ROYAL_LAYERS:
        return "FINAL"
    return "JUN"


def _spread(items, min_gap):
    """items: [(id, anchor)] → {id: x}. anchor 순서를 지키며 최소 간격을 두고, 전체를 anchor 평균 쪽으로 되돌린다."""
    items = sorted(items, key=lambda t: (t[1], t[0]))
    xs = []
    for i, (_, a) in enumerate(items):
        xs.append(a if i == 0 else max(a, xs[-1] + min_gap))
    # 오른쪽으로 밀린 만큼 전체를 평행 이동해 anchor 평균에 맞춘다(간격·순서는 유지)
    shift = (sum(xs) - sum(a for _, a in items)) / len(xs) if xs else 0
    return {iid: round(x - shift) for (iid, _), x in zip(items, xs)}


def compute_layout(canon):
    eps = {r["node_id"]: r for r in canon["episodes"]}
    sdn = canon["sd_nodes"]
    sde = canon["sd_edges"]
    ntype = {n["node_id"]: n["node_type"] for n in sdn}
    obs = [n["node_id"] for n in sdn if n["node_type"] == "OBSERVED_EVENT"]
    # ---- 관측 column: (band, date, sub-band, depth)
    info = {}
    for nid in obs:
        ep = eps[nid]
        k = date_key(ep)
        b = band_of(ep, k)
        sub = (0 if ep["layer"] == "ROYAL_JUDGMENT" else 1) if b == "FINAL" else 0
        info[nid] = dict(key=k, band=b, sub=sub)
    frozen = [e for e in sde if e["origin"] == "FROZEN"]
    group = lambda n: (info[n]["band"], info[n]["key"], info[n]["sub"])
    depth = {n: 0 for n in obs}
    for _ in range(len(obs)):           # 같은 (band, 날짜, sub) 안의 최장 경로 깊이
        changed = False
        for e in frozen:
            s, d = e["src"], e["dst"]
            if s in info and d in info and group(s) == group(d) and depth[d] < depth[s] + 1:
                depth[d] = depth[s] + 1
                changed = True
        if not changed:
            break
    border = [b["id"] for b in BANDS]
    colkey = {n: (border.index(info[n]["band"]), info[n]["key"] or 0, info[n]["sub"], depth[n]) for n in obs}
    cols = sorted(set(colkey.values()))
    colx, x, prev_band = {}, 0, None
    for c in cols:
        if prev_band is not None:
            x += COL_W + (BAND_GAP if c[0] != prev_band else 0)
        colx[c] = x
        prev_band = c[0]
    # ---- 관측 lane
    lane_order = [b for b, _ in BRANCH_LANES] + sorted({eps[n]["branch"] for n in obs} - {b for b, _ in BRANCH_LANES})
    lane_label = dict(BRANCH_LANES)
    stack = defaultdict(list)
    for n in sorted(obs, key=lambda n: (colkey[n], n)):
        stack[(eps[n]["branch"], colkey[n])].append(n)
    lane_rows = {ln: max([len(v) for (b, _), v in stack.items() if b == ln] or [0]) for ln in lane_order}
    pos, layout = {}, {}
    for n in obs:
        pos[n] = [colx[colkey[n]], None]
    # ---- 날짜 없는 lane: anchor 계산에 필요한 x부터
    cand_rows = {c["candidate_id"]: c for c in canon["candidates"]}
    gap_rows = {g["gap_id"]: g for g in canon["gaps"]}
    dated_x = lambda nid: pos[nid][0] if nid in pos and info[nid]["key"] is not None else None
    by_gap = defaultdict(list)
    for n in sdn:
        if n["node_type"] == "CANDIDATE_BRIDGE":
            by_gap[cand_rows[n["node_id"]]["gap_id"]].append(n["node_id"])
    gap_anchor = {}
    for g, cs in by_gap.items():
        xs = []
        for c in cs:
            for side in ("observed_left", "observed_right"):
                m = re.match(r"(EP\d\d)\b", cand_rows[c][side])
                if m and dated_x(m.group(1)) is not None:
                    xs.append(dated_x(m.group(1)))
        if not xs:
            xs = [dated_x(t) for t in gap_rows[g]["between"].split("|") if dated_x(t) is not None]
        gap_anchor[g] = sum(xs) / len(xs)
    gap_x = _spread(list(gap_anchor.items()), 168)
    for g, cs in by_gap.items():
        for i, c in enumerate(sorted(cs)):
            pos[c] = [gap_x[g], i]
    cand_lane_rows = max(len(v) for v in by_gap.values())
    out_edges = defaultdict(list)
    in_edges = defaultdict(list)
    for e in sde:
        out_edges[e["src"]].append(e)
        in_edges[e["dst"]].append(e)
    mean = lambda xs: sum(xs) / len(xs) if xs else None
    # 구조 변수: 설명하는 관측 node의 x
    sv = [n["node_id"] for n in sdn if n["node_type"] == "STRUCTURAL_VARIABLE"]
    sv_anchor = {v: mean([pos[e["dst"]][0] for e in out_edges[v]
                          if e["edge_type"] in ("EXPLAINS_TRANSITION_TO", "EXPLAINS_OBSERVED") and e["dst"] in pos]) for v in sv}
    for v in sv:
        if sv_anchor[v] is None:
            sv_anchor[v] = mean([pos[e["src"]][0] for e in in_edges[v] if e["src"] in pos]) or 0
    sv_x = _spread(list(sv_anchor.items()), 196)
    # 메커니즘: 자기 후보들의 x
    mech = [n["node_id"] for n in sdn if n["node_type"] == "MECHANISM"]
    m_anchor = {m: mean([pos[e["dst"]][0] for e in out_edges[m] if e["edge_type"] == "INSTANTIATED_BY" and e["dst"] in pos]) or 0
                for m in mech}
    m_x = _spread(list(m_anchor.items()), 230)
    # UNRESOLVED: 조건을 거는 후보, 없으면 detail에 적힌 관측 edge 끝점
    oe = {e["edge_id"]: e for e in canon["observed_edges"]}
    un = [n for n in sdn if n["node_type"] == "UNRESOLVED_ITEM"]
    u_anchor = {}
    for n in un:
        xs = [pos[e["dst"]][0] for e in out_edges[n["node_id"]] if e["dst"] in pos]
        if not xs:
            for o in re.findall(r"OE\d{3}", n["detail"]):
                xs += [pos[x][0] for x in (oe[o]["src"], oe[o]["dst"]) if x in pos and dated_x(x) is not None]
        if not xs:
            xs = [pos[x][0] for x in re.findall(r"EP\d\d", n["detail"]) if x in pos]
        u_anchor[n["node_id"]] = mean(xs) or 0
    u_x = _spread(list(u_anchor.items()), 230)
    # 제도 context: 제약하는 메커니즘·구조 변수의 x. 연결 없는 피쳐는 오른쪽 끝에 모아 둔다.
    ctx = [n["node_id"] for n in sdn if n["node_type"] == "INSTITUTIONAL_CONTEXT"]
    allx = {**{m: [m_x[m]] for m in mech}, **{v: [sv_x[v]] for v in sv}}
    c_anchor, c_free = {}, []
    for c in ctx:
        xs = [allx[e["dst"]][0] for e in out_edges[c] if e["dst"] in allx]
        if xs:
            c_anchor[c] = mean(xs)
        else:
            c_free.append(c)
    c_x = _spread(list(c_anchor.items()), 150)
    right = max(c_x.values()) if c_x else 0
    for i, c in enumerate(sorted(c_free)):
        c_x[c] = right + 150 * (i + 1)
    # 환경 context: 연결된 관측 판단 node·메커니즘의 x(날짜 위치에 두지 않음)
    env = [n["node_id"] for n in sdn if n["node_type"] == "ENV_CONTEXT"]
    e_anchor = {}
    for n in env:
        xs = [pos[e["dst"]][0] for e in out_edges[n] if e["dst"] in pos] + [m_x[e["dst"]] for e in out_edges[n] if e["dst"] in m_x]
        e_anchor[n] = mean(xs) or 0
    e_x = _spread(list(e_anchor.items()), 190)
    # ---- 세로 배치(위 → 아래): 제도 context · 메커니즘 · UNRESOLVED · 후보 · 구조 변수 · 관측 lane들 · 환경 context
    lanes, y = [], 0

    def lane(lid, label, kind, rows, ids_x, sub=""):
        nonlocal y
        h = rows * ROW_H + 2 * LANE_PAD
        lanes.append(dict(id=lid, label=label, kind=kind, sub=sub, y0=round(y), y1=round(y + h)))
        top = y + LANE_PAD + ROW_H / 2
        for nid, (xx, row) in ids_x.items():
            layout[nid] = dict(x=round(xx), y=round(top + row * ROW_H), lane=lid)
        y += h

    lane("L_CTX_INST", "제도 context (F001–F020)", "context", 1, {c: (c_x[c], 0) for c in ctx}, "제약조건 · 사건 아님")
    lane("L_MECH", "메커니즘 (분석 변수)", "latent", 1, {m: (m_x[m], 0) for m in mech}, "LATENT_MECHANISM · 역사적 사실 아님")
    lane("L_UNRES", "UNRESOLVED", "unresolved", 1, {u: (u_x[u], 0) for u in u_x}, "확정하지 않은 동일성·범위·사유")
    lane("L_CAND", "LATENT 후보 bridge", "latent", cand_lane_rows,
         {c: (pos[c][0], pos[c][1]) for g in by_gap for c in by_gap[g]}, "gap별 가설 · 등급 그대로")
    lane("L_SVAR", "질적 구조 변수 V_*", "latent", 1, {v: (sv_x[v], 0) for v in sv}, "OR · AND · XOR · ANCHORED 규칙")
    y += GROUP_GAP
    obs_top = y
    for ln in lane_order:
        rows = lane_rows[ln]
        if not rows:
            continue
        ids = {}
        for (b, ck), ns in stack.items():
            if b == ln:
                for i, n in enumerate(ns):
                    ids[n] = (pos[n][0], i)
        lane("L_OBS_" + ln, lane_label.get(ln, ln), "observed", rows, ids, ln)
    obs_bottom = y
    y += GROUP_GAP // 3
    lane("L_CTX_ENV", "환경 context (E001–E004)", "context", 1, {n: (e_x[n], 0) for n in env}, "호환성 context · 개인 감염 확정 아님")
    # ---- 시간 구간·눈금
    bands = []
    for bi, b in enumerate(BANDS):
        cx = [colx[c] for c in cols if c[0] == bi]
        if not cx:
            continue
        bands.append(dict(id=b["id"], label=b["label"], sub=b["sub"], dated=b["dated"],
                          x0=round(min(cx) - COL_W / 2 + 4), x1=round(max(cx) + COL_W / 2 - 4), y0=round(obs_top - 70), y1=round(obs_bottom)))
    ticks = []
    seen = {}
    for c in cols:
        if c[1] and (c[0], c[1]) not in seen:
            seen[(c[0], c[1])] = True
            xs = [colx[d] for d in cols if d[0] == c[0] and d[1] == c[1]]
            ticks.append(dict(x=round((min(xs) + max(xs)) / 2), label=f"{c[1] // 100}/{c[1] % 100}", date_key=c[1]))
    extra = {}
    for n in obs:
        extra[n] = dict(date_key=info[n]["key"], band=info[n]["band"], dated=info[n]["key"] is not None,
                        column=cols.index(colkey[n]))
    return layout, lanes, bands, ticks, extra


# --------------------------------------------------------------------------- UI 데이터
def _short(s, n):
    s = s.strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _graph_index(sde):
    out_e, in_e = defaultdict(list), defaultdict(list)
    for e in sde:
        out_e[e["src"]].append(e)
        in_e[e["dst"]].append(e)
    return out_e, in_e


def related_mechanisms(nid, sde, mech_ids):
    """canonical edge를 거꾸로 따라가 이 node에 닿는 메커니즘(분석 edge만). 경로도 함께 돌려준다."""
    _, in_e = _graph_index([e for e in sde if e["origin"] == "SUPER_DAG"])
    seen, frontier, paths = {nid}, [(nid, [])], {}
    while frontier:
        nxt = []
        for cur, path in frontier:
            for e in sorted(in_e[cur], key=lambda e: e["edge_id"]):
                s = e["src"]
                if s in seen:
                    continue
                seen.add(s)
                p = [e["edge_id"]] + path
                if s in mech_ids:
                    paths[s] = p
                else:
                    nxt.append((s, p))
        frontier = nxt
    return {m: paths[m] for m in sorted(paths)}


def make_ui(canon, a4_findings=()):
    import report_mech
    import stage5_worlds
    import stage6_mechanisms as s6
    sdn, sde = canon["sd_nodes"], canon["sd_edges"]
    eps = {r["node_id"]: r for r in canon["episodes"]}
    oedges = {r["edge_id"]: r for r in canon["observed_edges"]}
    cands = {r["candidate_id"]: r for r in canon["candidates"]}
    mech_ids = [n["node_id"] for n in sdn if n["node_type"] == "MECHANISM"]
    layout, lanes, bands, ticks, extra = compute_layout(canon)
    outcome = sorted({x for ids in stage5_worlds.COMMON_OUTCOME_NODES.values() for x in ids})
    env_ids = {r["env_id"]: r for r in canon["env"]}
    nodes = []
    for n in sdn:
        nid = n["node_id"]
        t = n["node_type"]
        if t == "OBSERVED_EVENT":
            short = f"{nid} · {_short(n['label'], 30)}"
        elif t == "MECHANISM":
            short = f"{nid} {MECH_DISPLAY.get(nid, '')}"
        elif t == "CANDIDATE_BRIDGE":
            short = f"{nid} · {_short(n['label'], 24)}"
        elif t == "INSTITUTIONAL_CONTEXT":
            short = _short(n["label"], 22)
        elif t == "ENV_CONTEXT":
            short = f"{eps[nid]['env_id']} · {_short(n['label'].split(' ', 1)[-1], 22)}"
        elif t == "UNRESOLVED_ITEM":
            short = _short(n["label"], 30)
        else:
            short = nid
        item = dict(id=nid, canonical=dict(n), short_label=short, status_group=STATUS_GROUPS[n["sd_status"]],
                    layout=dict(layout[nid]), common_outcome=nid in outcome,
                    analysis_excluded="분석 제외" in n["detail"])  # canonical detail 문구 그대로의 표시
        if t == "OBSERVED_EVENT":
            item["layout"].update(extra[nid])
            item["observed"] = dict(eps[nid])
            item["related_mechanisms"] = related_mechanisms(nid, sde, set(mech_ids))
        else:
            item["layout"].update(date_key=None, band=None, dated=False, column=None)
        if t == "ENV_CONTEXT":
            item["context_source"] = dict(eps[nid])          # frozen 환경 node(문구 그대로)
            item["context_feature"] = dict(env_ids[eps[nid]["env_id"]])
        if t == "INSTITUTIONAL_CONTEXT":
            item["context_feature"] = next(dict(r) for r in canon["inst"] if "CTX_" + r["feature_id"] == nid)
        if t in ("CANDIDATE_BRIDGE", "STRUCTURAL_VARIABLE", "UNRESOLVED_ITEM", "INSTITUTIONAL_CONTEXT", "ENV_CONTEXT"):
            item["related_mechanisms"] = related_mechanisms(nid, sde, set(mech_ids))
            if t in ("INSTITUTIONAL_CONTEXT", "ENV_CONTEXT"):
                item["related_mechanisms"] = {e["dst"]: [e["edge_id"]] for e in sde if e["src"] == nid and e["dst"] in mech_ids}
        nodes.append(item)
    edges = []
    for e in sde:
        item = dict(id=e["edge_id"], canonical=dict(e), status_group=STATUS_GROUPS[e["sd_status"]])
        if e["origin"] == "FROZEN":
            item["frozen"] = dict(oedges[e["edge_id"]])
        edges.append(item)
    super_dag = dict(nodes=nodes, edges=edges, lanes=lanes, bands=bands, ticks=ticks,
                     node_count=len(nodes), edge_count=len(edges))

    # ---- worlds
    configs = {r["world_id"]: r for r in canon["configs"]}
    narr = {r["world_id"]: r for r in canon["worlds"]}
    order = [r["world_id"] for r in canon["configs"]]
    backbone = sorted(n["node_id"] for n in sdn if n["sd_status"] == "OBSERVED")
    cand_nodes = sorted(n["node_id"] for n in sdn if n["node_type"] == "CANDIDATE_BRIDGE")
    selections = {"ALL": dict(id="ALL", label="ALL", rejected=False, banner="",
                              always_visible=backbone, highlight=[], mechanism_state={}, dim=[], hideable=[])}
    for wid in order:
        c = configs[wid]
        bridges = [b for b in c["latent_bridges"].split("|") if b]
        state = {m: c[m] for m in s6.ORDER}
        rejected = c["role_type"] == "REJECTED"
        others = [x for x in cand_nodes if x not in bridges]
        selections[wid] = dict(
            id=wid, label=wid + (" REJECTED" if rejected else ""), rejected=rejected, role_type=c["role_type"],
            banner=(f"{wid}는 검토했지만 배제된 설명(REJECTED)이다. 경쟁 설명(W1–W5)과 같은 자리에 두지 않으며, "
                    "공존·개입 분석에서도 제외된다. 아래 강조는 '배제된 가설이 무엇이었는지' 보여 주기 위한 것이다."
                    if rejected else ""),
            always_visible=backbone, highlight=sorted(bridges + [m for m in s6.ORDER if state[m] in ("ON", "PARTIAL")]),
            mechanism_state=state, dim=others, hideable=others)
    worlds = dict(order=order, selections=selections,
                  configurations={wid: dict(configs[wid]) for wid in order},
                  narratives={wid: dict(narr[wid]) for wid in order if wid in narr},
                  common_outcome_nodes={k: list(v) for k, v in stage5_worlds.COMMON_OUTCOME_NODES.items()},
                  backbone=backbone, mechanisms=list(s6.ORDER), config_display=CONFIG_DISPLAY,
                  off_count=sum(configs[w][m] == "OFF" for w in order for m in s6.ORDER),
                  rejected=[w for w in order if configs[w]["role_type"] == "REJECTED"])

    # ---- interactions
    a4 = defaultdict(list)
    for f in a4_findings:
        if "×" in f["target"]:
            a4[f["target"]].append(dict(check=f["check"], severity=f["severity"], message=f["message"]))
    pairs = []
    for r in canon["interactions"]:
        key = f"{r['mechanism A']}×{r['mechanism B']}"
        pairs.append(dict(key=key, a=r["mechanism A"], b=r["mechanism B"], canonical=dict(r),
                          audit4=sorted(a4.get(key, []), key=lambda x: (x["check"], x["message"]))))
    rules = [dict(r) for r in canon["rules"]]
    interactions = dict(pairs=pairs, rules=rules, excluded_worlds=worlds["rejected"],
                        note="공존 판정은 mechanism_interaction_matrix.csv 값을 그대로 보여 준다. 새 판정을 만들지 않는다. "
                             "W6(REJECTED)은 canonical 분석에서처럼 제외된다.")

    # ---- interventions
    rows = []
    for i, r in enumerate(canon["interventions"]):
        path = sorted({r["mechanism"], r["variable"], *[x for x in r["removed"].split("|") if x],
                       *[x for x in r["remaining"].split("|") if x], *[x for x in r["target"].split("|") if x]})
        rows.append(dict(index=i, canonical=dict(r), path_nodes=path))
    interventions = dict(rows=rows, mechanisms=list(s6.ORDER),
                         note="현재 설명 모델에서 해당 mechanism을 제거했을 때 설명 경로가 어떻게 변하는가. "
                              "역사적 사실을 지우지 않는다 — OBSERVED node는 개입 중에도 그대로 남는다.")

    # ---- candidates
    candidates = dict(rows={cid: dict(r) for cid, r in sorted(cands.items())},
                      gaps={g["gap_id"]: dict(g) for g in canon["gaps"]})

    # ---- views (canonical node의 부분집합만)
    ids = {n["node_id"] for n in sdn}
    inst_by = defaultdict(set)
    for e in sde:
        if e["edge_type"] in ("INSTANTIATED_BY", "INSTANTIATED_BY_SECONDARY"):
            inst_by[e["src"]].add(e["dst"])
    ctx_of = lambda ms: {e["src"] for e in sde if e["edge_type"] == "CONSTRAINS" and e["dst"] in ms}
    cond_of = lambda cs: {e["src"] for e in sde if e["edge_type"] == "CONDITIONS" and e["dst"] in cs}
    inv_c = set().union(*[inst_by[m] for m in ("M1", "M2", "M3", "M4")])
    v2 = set(report_mech.INVESTIGATION_PANEL) | inv_c | {"EP01", "EP02"} | cond_of(inv_c)
    rev_c = set().union(*[inst_by[m] for m in ("M5", "M6")])
    v3 = ({x for x in report_mech.REVIEW_PANEL if not x.startswith("ENV")} | rev_c | ctx_of({"M5"}) | cond_of(rev_c))
    group_a = sorted({n["node_id"] for n in sdn if n["branch"] == "A_BIOLOGICAL" or n["node_id"] in s6.BRANCH_A}
                     | {n["node_id"] for n in sdn if n["node_type"] == "ENV_CONTEXT"})
    group_b = sorted(x for x in s6.BRANCH_B if x in ids)
    nb = defaultdict(set)
    for e in sde:
        nb[e["src"]].add(e["dst"])
        nb[e["dst"]].add(e["src"])
    anchors = sorted({x for a in group_a for x in nb[a]
                      if x not in group_a and x not in group_b and next(n for n in sdn if n["node_id"] == x)["sd_status"] == "OBSERVED"})
    cross = sorted(e["edge_id"] for e in sde if (e["src"] in group_a and e["dst"] in group_b) or (e["src"] in group_b and e["dst"] in group_a))
    views = dict(order=["overview", "investigation", "review", "death"], views=dict(
        overview=dict(id="overview", label="1 Overview", title="전체 Mechanism Super-DAG",
                      desc="모든 canonical node·edge. 왼쪽 → 오른쪽이 시간(2월 → 3월 → 5월 → 6월 → 최종 판단·처분)이고, 위쪽 lane은 날짜가 없는 분석 층이다. 휠·＋ 버튼으로 확대하면 라벨이 보인다.",
                      nodes=sorted(ids), emphasis=[], path=""),
        investigation=dict(id="investigation", label="2 수사 확대", title="수사 확대 (M1–M4 중심)",
                           desc="정보 → 의심 → 병영 → 체포 → 구금. M1–M4와 그 후보, 3/4 체포 지시(EP09)로 가는 구조 변수.",
                           nodes=sorted(v2 & ids), emphasis=["M1", "M2", "M3", "M4"], path="정보 → 의심 → 병영 → 체포 → 구금"),
        review=dict(id="review", label="3 재검토·판단·처분", title="재검토·판단·처분 (M5 중심)",
                    desc="5/12 → 5/27 → 5/28 → 6/11 → 6/13 → 책임 판단 → 처분. 재검토 backbone은 OBSERVED이고 M5는 그것을 설명하는 분석 변수다.",
                    nodes=sorted(v3 & ids), emphasis=["M5"], path="5/12 → 5/27 → 5/28 → 6/11 → 6/13 → 책임 판단 → 처분"),
        death=dict(id="death", label="4 질병·사망 branch", title="질병·사망 branch: A 생물학적 경과 / B 절차·책임",
                   desc="A(MB → V_CUSTODY_COURSE, 환경 context, 사인 판단)와 B(M1–M4 → 체포 경로 → 책임 판단)를 분리해 보여 준다. "
                        "두 branch를 직접 잇는 edge는 canonical data에 없다.",
                   nodes=sorted(set(group_a) | set(group_b) | set(anchors)), emphasis=[], path="A ∥ B (직접 연결 없음)",
                   groups=dict(A=group_a, B=group_b, anchor=anchors), cross_edges=cross)))

    # ---- facts (확정 사실·출처: 원본 pack 그대로)
    facts = dict(confirmed_facts={r["fact_id"]: dict(r) for r in canon["facts"]},
                 source_records={r["source_record_id"]: dict(r) for r in canon["sources"]},
                 definitions={r["mechanism_id"]: dict(r) for r in canon["definitions"]})

    from collections import Counter
    meta = dict(
        title=TITLE, description=DESCRIPTION, role_note=ROLE_NOTE,
        frozen_hash=canon["freeze"]["sha256"], frozen_hash_prefix=canon["freeze"]["sha256"][:16],
        counts=dict(nodes=len(nodes), edges=len(edges),
                    node_status=dict(sorted(Counter(n["sd_status"] for n in sdn).items())),
                    edge_status=dict(sorted(Counter(e["sd_status"] for e in sde).items())),
                    node_type=dict(sorted(Counter(n["node_type"] for n in sdn).items())),
                    edge_type=dict(sorted(Counter(e["edge_type"] for e in sde).items())),
                    candidates=len(cands), worlds=len(order), interventions=len(rows), interaction_pairs=len(pairs)),
        generated_from=dict(sorted(canon["_hashes"].items())),
        generated_by="scripts/gusun_clean/build_visualization.py",
        status_groups=STATUS_GROUPS, mechanism_display=MECH_DISPLAY,
        mechanism_names={r["mechanism_id"]: r["mechanism_name"] for r in canon["definitions"]},
        edge_styles=EDGE_STYLES, config_display=CONFIG_DISPLAY,
        layout_rule=("x: 날짜가 있는 관측 node는 정렬 기준일(t_max, 없으면 t_min) 순서의 column에 놓는다. 같은 날짜 안에서는 frozen edge 깊이 순서. "
                     "y: 관측 node는 branch lane, 날짜 없는 node는 분석 lane. 날짜 없는 node의 x는 연결된 node 근처일 뿐 날짜를 뜻하지 않는다."),
    )
    return dict(super_dag=super_dag, worlds=worlds, interactions=interactions, interventions=interventions,
                candidates=candidates, views=views, facts=facts, meta=meta)


# --------------------------------------------------------------------------- 쓰기·읽기
def _dump(obj, indent=1):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=indent) + "\n"


def write_ui(docs, ui):
    d = Path(docs) / "data"
    d.mkdir(parents=True, exist_ok=True)
    for k in DATA_FILES:
        (d / f"{k}.json").write_text(_dump(ui[k]), encoding="utf-8")
    (d / "bundle.js").write_text(bundle_text(ui), encoding="utf-8")


def bundle_text(ui):
    return ("// 자동 생성: scripts/gusun_clean/build_visualization.py — 직접 고치지 말 것.\n"
            "// data/*.json과 같은 내용. file:// 로 열어도 동작하도록 script로도 싣는다.\n"
            "window.GUSUN_DATA = " + json.dumps({k: ui[k] for k in DATA_FILES}, ensure_ascii=False, sort_keys=True,
                                                separators=(",", ":")) + ";\n")


def read_ui(docs):
    d = Path(docs) / "data"
    ui = {k: json.loads((d / f"{k}.json").read_text(encoding="utf-8")) for k in DATA_FILES}
    ui["_bundle"] = (d / "bundle.js").read_text(encoding="utf-8")
    return ui


def build(docs=DOCS, out=OUT, pack=PACK, a4_findings=None):
    canon = load_canonical(out, pack)
    ui = make_ui(canon, a4_findings if a4_findings is not None else audit4_from_db())
    write_ui(docs, ui)
    return canon, read_ui(docs)


if __name__ == "__main__":
    canon, ui = build()
    print(f"[VIS] docs/data 작성: node {ui['meta']['counts']['nodes']} · edge {ui['meta']['counts']['edges']} · "
          f"frozen {ui['meta']['frozen_hash_prefix']}")
