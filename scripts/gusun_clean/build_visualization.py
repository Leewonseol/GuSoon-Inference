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

# edge type 표시 규칙. 세부 관계 유형 19종(edge_type)은 canonical 값 그대로 두고, 화면 선 모양은 아래 EDGE_DISPLAY의
# 3가지 표시 유형(display)으로만 그린다. ko = 원래 관계 의미(선택·hover·상세 패널에서 항상 보임). group = canonical origin 묶음.
# arrow = 화살촉. 방향성 흐름과 의미가 다른 CONTRADICTS_AT_CLAIM_LEVEL만 'tee'(상충)로 따로 그린다.
EDGE_STYLES = {
    "TEMPORAL_BEFORE": dict(display="record", arrow="triangle", group="관측 (frozen)", ko="시간 선후"),
    "PROCEDURAL_NEXT": dict(display="record", arrow="triangle", group="관측 (frozen)", ko="절차상 다음 단계"),
    "INFORMATION_FLOW": dict(display="record", arrow="triangle", group="관측 (frozen)", ko="정보 흐름(기록 근거)"),
    "ORDER_TO_ACTION": dict(display="record", arrow="triangle", group="관측 (frozen)", ko="명령 → 실행"),
    "REVIEW_OF": dict(display="record", arrow="triangle", group="관측 (frozen)", ko="검토·심리"),
    "REVISES": dict(display="record", arrow="triangle", group="관측 (frozen)", ko="판단 수정"),
    "RESPONSIBILITY_LINK": dict(display="record", arrow="triangle", group="관측 (frozen)", ko="책임 귀속(판단 node로만)"),
    "CONTRADICTS_AT_CLAIM_LEVEL": dict(display="record", arrow="tee", group="관측 (frozen)",
                                       ko="주장 수준 상충(흐름·인과가 아니라 두 기록의 주장이 서로 어긋남)"),
    "CONTEXT_SUPPORTS": dict(display="context", arrow="triangle", group="관측 (frozen)", ko="context가 판단을 뒷받침"),
    "CONSTRAINS": dict(display="context", arrow="triangle", group="Super-DAG 분석", ko="제도 context가 메커니즘을 제약"),
    "CONTEXT_COMPATIBLE": dict(display="context", arrow="triangle", group="Super-DAG 분석", ko="환경 호환성(개인 감염 아님)"),
    "INSTANTIATED_BY": dict(display="analysis", arrow="triangle", group="Super-DAG 분석", ko="메커니즘 → 후보(core/보조)"),
    "INSTANTIATED_BY_SECONDARY": dict(display="analysis", arrow="triangle", group="Super-DAG 분석", ko="메커니즘 → 후보(보조 메커니즘)"),
    "CONTRIBUTES_TO": dict(display="analysis", arrow="triangle", group="Super-DAG 분석", ko="후보 → 구조 변수(규칙 입력)"),
    "RULE_INPUT": dict(display="analysis", arrow="triangle", group="Super-DAG 분석", ko="구조 변수 → 구조 변수"),
    "EXPLAINS_TRANSITION_TO": dict(display="analysis", arrow="triangle", group="Super-DAG 분석", ko="구조 변수가 관측 전이를 설명"),
    "EXPLAINS_OBSERVED": dict(display="analysis", arrow="triangle", group="Super-DAG 분석", ko="관측 재검토 사건을 설명(사건은 그대로)"),
    "ANCHORED_TO": dict(display="analysis", arrow="triangle", group="Super-DAG 분석", ko="M5가 관측 backbone에 고정"),
    "CONDITIONS": dict(display="analysis", arrow="triangle", group="Super-DAG 분석", ko="미해결 항목이 후보의 성립 조건"),
}
# 화면 표시 유형 3종(선의 색상·형태). 관계 의미·증거 상태(OBSERVED/DERIVED…)는 바꾸지 않는 시각적 묶음이다.
# 증거 상태는 선 굵기로 따로 보인다(OBSERVED edge 굵게, DERIVED 보통, 분석·context edge 얇게).
EDGE_DISPLAY_ORDER = ["record", "analysis", "context"]
EDGE_DISPLAY = {
    "record": dict(label="기록·절차", color="#2b2a27", line="solid", width=2.6, opacity=0.9,
                   desc="사료 기록으로 이어진 시간·절차·검토·책임 연결(진한 실선)"),
    "analysis": dict(label="분석·추론", color="#6b55c9", line="dashed", width=1.6, opacity=0.85,
                     desc="메커니즘·구조 변수·후보 사이의 분석 연결(얇은 점선). 사료에 직접 적힌 연결이 아님"),
    "context": dict(label="맥락·제약", color="#4f9a4f", line="dotted", width=1.6, opacity=0.6,
                    desc="제도·환경 context의 뒷받침·제약·호환성(옅은 점선). 사건 발생을 증명하지 않음"),
}
# 기본 화면(간단히 보기) 규칙. 시각적 표시만 정하며 node·edge·분석 결과를 바꾸지 않는다.
# core_flow_types: OBSERVED 사건 사이에서 기본으로 보이는 시간·절차 흐름 관계(나머지 관계는 node를 선택하면 펼쳐짐).
# transitive_types: 수학적으로 추이적인 관계. 같은 유형만으로 된 다른 경로가 있으면 직접 edge는 기본 화면에서 숨길 수 있다.
#   REVIEW_OF·REVISES·INFORMATION_FLOW·RESPONSIBILITY_LINK 등은 추이적이라고 가정하지 않는다.
# merge_exclude_types: 같은 두 node 사이 여러 관계를 한 선으로 묶을 때 묶지 않고 따로 그리는 관계(의미가 방향성 흐름과 다름).
SIMPLE_VIEW = dict(
    levels=["simple", "records", "full"], default_level="simple", default_hops=1, max_hops=2,
    level_labels=dict(simple="간단히(핵심 흐름)", records="기록 관계 전체", full="전체(분석·맥락 포함)"),
    core_flow_types=["TEMPORAL_BEFORE", "PROCEDURAL_NEXT", "ORDER_TO_ACTION", "REVIEW_OF", "REVISES"],
    transitive_types=["TEMPORAL_BEFORE"],
    merge_exclude_types=["CONTRADICTS_AT_CLAIM_LEVEL"],
    note=("간단히 보기는 화면 표시만 줄인다. 접힌 LATENT·CONTEXT·UNRESOLVED node와 숨긴 edge는 삭제되지 않았고 "
          "world·공존·개입 결과와 상세 패널 계산에 그대로 들어 있다."),
)

# ---- 글자·node 크기(가독성 기준). 화면 좌표 단위(model px)이며 zoom 1.0에서 CSS px과 같다.
PT = 96 / 72                      # 1pt = 1.333px
READ_PX = round(11 * PT, 3)       # 11pt = 14.667px: 화면에 그려진 글자의 최소 크기
NODE_FONT = 16                    # node label 글자 크기(12pt). zoom ≥ READ_PX/NODE_FONT(0.917)이면 11pt 이상
EDGE_FONT = 16                    # edge label 글자 크기(선택·hover 때만 표시)
LINE_H = 1.6                      # node label·UI 공통 line-height
LINE_PX = NODE_FONT * LINE_H      # node label 한 줄 높이
INITIAL_ZOOM_MIN = 0.95           # 모든 View의 첫 화면 zoom 하한(16px × 0.95 = 15.2px ≥ 11pt)
INITIAL_ZOOM_MAX = 1.25
LANE_FONT, LANE_SUB_FONT, BAND_FONT, BAND_SUB_FONT, TICK_FONT = 17, 16, 22, 16, 17
# node 종류별 폭과 안쪽 여백(px). 글자 영역 폭 = 폭 - 2 × pad_x. 높이는 줄 수로 정한다.
NODE_BOX = {
    "OBSERVED_EVENT": dict(w=224, pad_x=14, pad_y=12),
    "CANDIDATE_BRIDGE": dict(w=224, pad_x=14, pad_y=12),
    "STRUCTURAL_VARIABLE": dict(w=300, pad_x=22, pad_y=12),
    "MECHANISM": dict(w=360, pad_x=90, pad_y=14),          # 육각형: 위·아래 모서리가 안쪽으로 w/4 들어옴 → 글자 폭 w/2
    "INSTITUTIONAL_CONTEXT": dict(w=224, pad_x=14, pad_y=12),
    "ENV_CONTEXT": dict(w=260, pad_x=24, pad_y=14),          # barrel: 좌우가 둥글게 들어옴
    "UNRESOLVED_ITEM": dict(w=300, pad_x=18, pad_y=14),
}
MECH_RESERVED_LINES = 2           # world 값·개입 표시 줄을 위한 메커니즘 lane 여유
COL_GAP = 64                      # 관측 column 사이 빈 공간(node 폭과 별개)
BAND_GAP = 80                    # 시간 구간 사이 추가 여백
ROW_GAP = 28                      # 같은 칸에 쌓인 node 사이 세로 여백
LANE_PAD = 16
GROUP_GAP = 120                   # 관측 lane 묶음과 분석 lane 묶음 사이
HEADER_H = 104                    # 시간 구간 제목·눈금 자리
H_GAP = 60                        # 분석 lane 안 node 사이 최소 가로 여백
LABEL_W = 190                     # 왼쪽 lane 이름 칸


# --------------------------------------------------------------------------- 글자 폭 추정·줄바꿈
_WIDE = set("→←↔·–—‘’“”…※○●◆□■△▲▽▼～〜")


def char_em(ch):
    """글자 폭(em) 보수적 추정. 실제 글꼴보다 넓게 잡아 node 밖으로 글자가 넘치지 않게 한다."""
    o = ord(ch)
    if ch == " ":
        return 0.36
    if 0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F or 0x4E00 <= o <= 0x9FFF or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF:
        return 1.0
    if ch in _WIDE or o >= 0x2000:
        return 1.0
    if ch.isupper():
        return 0.76
    if ch.isdigit():
        return 0.64
    if ch.islower():
        return 0.62
    if ch in "il.,:;!|'`":
        return 0.4
    return 0.66


def text_px(s, font=NODE_FONT):
    return sum(char_em(c) for c in s) * font


def wrap_text(text, max_px, font=NODE_FONT):
    """단어(공백) 단위로 줄을 나누고, 한 단어가 너무 길면 '_'·'·'·'→'·'/' 뒤나 글자 단위로 자른다. 글자를 버리지 않는다."""
    def pieces(word):
        out, cur = [], ""
        for ch in word:
            cur += ch
            if ch in "_·→/,)":
                out.append(cur)
                cur = ""
        if cur:
            out.append(cur)
        return out

    lines, cur = [], ""
    for word in text.split():
        cand = (cur + " " + word) if cur else word
        if text_px(cand, font) <= max_px:
            cur = cand
            continue
        if cur:
            lines.append(cur)
            cur = ""
        if text_px(word, font) <= max_px:
            cur = word
            continue
        for p in pieces(word):
            cand = cur + p
            if text_px(cand, font) <= max_px:
                cur = cand
                continue
            if cur:
                lines.append(cur)
                cur = ""
            for ch in p:                       # 그래도 길면 글자 단위
                if text_px(cur + ch, font) > max_px and cur:
                    lines.append(cur)
                    cur = ""
                cur += ch
    if cur:
        lines.append(cur)
    return lines


def node_text(n):
    """node label 원문: 첫 줄 ID, 다음 줄부터 canonical label 전체(자르지 않음). 메커니즘은 화면 이름."""
    nid, t = n["node_id"], n["node_type"]
    if t == "MECHANISM":
        return nid, MECH_DISPLAY.get(nid, n["label"])
    if t == "STRUCTURAL_VARIABLE" and n["label"] == nid:
        return nid, ""
    return nid, n["label"]


def node_box(n):
    """node 표시 글자(줄바꿈 포함)와 크기. 같은 입력이면 항상 같은 값."""
    spec = NODE_BOX[n["node_type"]]
    inner = spec["w"] - 2 * spec["pad_x"]
    head, body = node_text(n)
    lines = wrap_text(head, inner) + (wrap_text(body, inner) if body else [])
    h = round(len(lines) * LINE_PX + 2 * spec["pad_y"])
    return dict(lines=lines, label="\n".join(lines), w=spec["w"], h=h, text_w=inner, pad_x=spec["pad_x"],
                pad_y=spec["pad_y"], n_lines=len(lines),
                max_line_px=round(max(text_px(x) for x in lines), 1))


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


def _lane_lines(label, sub):
    return dict(label_lines=wrap_text(label, LABEL_W - 30, LANE_FONT), sub_lines=wrap_text(sub, LABEL_W - 30, LANE_SUB_FONT) if sub else [])


def layout_subset(canon, boxes, ids, above=frozenset(), names=None, focus=None):
    """canonical node 부분집합의 결정적 preset 좌표.

    - 관측 node: x = 시간 구간·정렬 기준일·같은 날짜 안 frozen edge 깊이 순서의 column, y = branch lane.
      같은 칸에 여럿이면 실제 높이만큼 아래로 쌓는다(겹침 없음).
    - 날짜 없는 분석 node: 관측 lane 아래(above에 든 node는 위)의 종류별 lane. x는 연결된 node 근처일 뿐 날짜가 아니다.
    - 부분집합 안의 node·edge만 보고 계산하므로 View마다 촘촘한 배치가 나온다. 같은 입력이면 같은 좌표.
    names: lane 이름 덮어쓰기(예: 질병·사망 View의 branch 표시).
    """
    ids = set(ids)
    names = names or {}
    eps = {r["node_id"]: r for r in canon["episodes"]}
    sdn = [n for n in canon["sd_nodes"] if n["node_id"] in ids]
    sde = [e for e in canon["sd_edges"] if e["src"] in ids and e["dst"] in ids]
    bx = lambda nid: boxes[nid]
    obs = [n["node_id"] for n in sdn if n["node_type"] == "OBSERVED_EVENT"]
    # ---- 관측 column
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
    pitch = NODE_BOX["OBSERVED_EVENT"]["w"] + COL_GAP
    colx, x, prev_band = {}, 0, None
    for c in cols:
        if prev_band is not None:
            x += pitch + (BAND_GAP if c[0] != prev_band else 0)
        colx[c] = x
        prev_band = c[0]
    lane_order = [b for b, _ in BRANCH_LANES] + sorted({eps[n]["branch"] for n in obs} - {b for b, _ in BRANCH_LANES})
    lane_label = dict(BRANCH_LANES)
    stack = defaultdict(list)
    for n in sorted(obs, key=lambda n: (colkey[n], n)):
        stack[(eps[n]["branch"], colkey[n])].append(n)
    pos = {n: colx[colkey[n]] for n in obs}
    mean = lambda xs: sum(xs) / len(xs) if xs else None
    fallback = mean(list(pos.values())) or 0
    out_e, in_e = defaultdict(list), defaultdict(list)
    for e in sde:
        out_e[e["src"]].append(e)
        in_e[e["dst"]].append(e)
    of_type = lambda t: [n["node_id"] for n in sdn if n["node_type"] == t]
    # ---- 분석 node x(anchor → 최소 간격으로 펼침)
    cand_rows = {c["candidate_id"]: c for c in canon["candidates"]}
    gap_rows = {g["gap_id"]: g for g in canon["gaps"]}
    dated_x = lambda nid: pos[nid] if nid in pos and info[nid]["key"] is not None else None
    by_gap = defaultdict(list)
    for c in of_type("CANDIDATE_BRIDGE"):
        by_gap[cand_rows[c]["gap_id"]].append(c)
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
        gap_anchor[g] = mean(xs) if xs else fallback
    gap_x = _spread(list(gap_anchor.items()), NODE_BOX["CANDIDATE_BRIDGE"]["w"] + H_GAP)
    ax = dict(pos)
    for g, cs in by_gap.items():
        for c in cs:
            ax[c] = gap_x[g]
    sv = of_type("STRUCTURAL_VARIABLE")
    sv_anchor = {}
    for v in sv:
        a = mean([pos[e["dst"]] for e in out_e[v] if e["edge_type"] in ("EXPLAINS_TRANSITION_TO", "EXPLAINS_OBSERVED") and e["dst"] in pos])
        if a is None:
            a = mean([ax[e["src"]] for e in in_e[v] if e["src"] in ax])
        sv_anchor[v] = a if a is not None else fallback
    sv_x = _spread(list(sv_anchor.items()), NODE_BOX["STRUCTURAL_VARIABLE"]["w"] + H_GAP)
    ax.update(sv_x)
    mech = of_type("MECHANISM")
    m_anchor = {}
    for m in mech:
        a = mean([ax[e["dst"]] for e in out_e[m] if e["edge_type"] in ("INSTANTIATED_BY", "ANCHORED_TO") and e["dst"] in ax])
        m_anchor[m] = a if a is not None else fallback
    m_x = _spread(list(m_anchor.items()), NODE_BOX["MECHANISM"]["w"] + H_GAP)
    ax.update(m_x)
    oe = {e["edge_id"]: e for e in canon["observed_edges"]}
    un = [n for n in sdn if n["node_type"] == "UNRESOLVED_ITEM"]
    u_anchor = {}
    for n in un:
        xs = [ax[e["dst"]] for e in out_e[n["node_id"]] if e["dst"] in ax]
        if not xs:
            for o in re.findall(r"OE\d{3}", n["detail"]):
                xs += [pos[x] for x in (oe[o]["src"], oe[o]["dst"]) if x in pos and dated_x(x) is not None]
        if not xs:
            xs = [pos[x] for x in re.findall(r"EP\d\d", n["detail"]) if x in pos]
        u_anchor[n["node_id"]] = mean(xs) if xs else fallback
    u_x = _spread(list(u_anchor.items()), NODE_BOX["UNRESOLVED_ITEM"]["w"] + H_GAP)
    ax.update(u_x)
    ctx = of_type("INSTITUTIONAL_CONTEXT")
    c_anchor, c_free = {}, []
    for c in ctx:
        xs = [ax[e["dst"]] for e in out_e[c] if e["dst"] in ax and e["dst"] not in pos]
        if xs:
            c_anchor[c] = mean(xs)
        else:
            c_free.append(c)
    ctx_pitch = NODE_BOX["INSTITUTIONAL_CONTEXT"]["w"] + H_GAP
    c_x = _spread(list(c_anchor.items()), ctx_pitch)
    right = max(c_x.values()) if c_x else fallback
    for i, c in enumerate(sorted(c_free)):
        c_x[c] = right + ctx_pitch * (i + 1)
    ax.update(c_x)
    env = of_type("ENV_CONTEXT")
    e_anchor = {}
    for n in env:
        xs = [ax[e["dst"]] for e in out_e[n] if e["dst"] in ax]
        e_anchor[n] = mean(xs) if xs else fallback
    e_x = _spread(list(e_anchor.items()), NODE_BOX["ENV_CONTEXT"]["w"] + H_GAP)
    ax.update(e_x)
    # ---- 세로 배치
    layout, lanes = {}, []
    y = 0

    def lane(lid, label, kind, sub, rows, reserve=0.0):
        """rows: [[nid, ...] per stack] — 같은 x 칸에 쌓을 node 목록들. 높이는 실제 node 높이로 계산."""
        nonlocal y
        if not any(rows):
            return
        heights = [sum(bx(n)["h"] for n in r) + ROW_GAP * (len(r) - 1) + reserve for r in rows if r]
        h = max(heights) + 2 * LANE_PAD
        lanes.append(dict(id=lid, label=names.get(lid, label), kind=kind, sub=sub, y0=round(y), y1=round(y + h),
                          **_lane_lines(names.get(lid, label), sub)))
        for r in rows:
            top = y + LANE_PAD + reserve / 2
            if len(r) == 1:                    # 한 줄 lane: 가운데 정렬
                top = y + h / 2 - bx(r[0])["h"] / 2
            for n in r:
                layout[n] = dict(x=round(ax[n]), y=round(top + bx(n)["h"] / 2), lane=lid)
                top += bx(n)["h"] + ROW_GAP
        y += h

    def analysis_lanes(sel, reverse=False):
        sel = set(sel)
        specs = [
            ("L_SVAR", "질적 구조 변수 V_*", "latent", "OR · AND · XOR · ANCHORED 규칙", [[v] for v in sv if v in sel], 0),
            ("L_CAND", "LATENT 후보 bridge", "latent", "gap별 가설 · 등급 그대로",
             [sorted(c for c in cs if c in sel) for g, cs in sorted(by_gap.items())], 0),
            ("L_UNRES", "UNRESOLVED", "unresolved", "확정하지 않은 동일성·범위·사유", [[u["node_id"]] for u in un if u["node_id"] in sel], 0),
            ("L_MECH", "메커니즘 (분석 변수)", "latent", "LATENT_MECHANISM · 역사적 사실 아님", [[m] for m in mech if m in sel],
             MECH_RESERVED_LINES * LINE_PX),
            ("L_CTX_INST", "제도 context (F001–F020)", "context", "제약조건 · 사건 아님", [[c] for c in ctx if c in sel], 0),
            ("L_CTX_ENV", "환경 context (E001–E004)", "context", "호환성 context · 개인 감염 확정 아님", [[n] for n in env if n in sel], 0),
        ]
        for i, (lid, label, kind, sub, rows, reserve) in enumerate(reversed(specs) if reverse else specs):
            lane(lid + ("_UP" if reverse else ""), label, kind, sub, rows, reserve)

    analysis = [n["node_id"] for n in sdn if n["node_type"] != "OBSERVED_EVENT"]
    up = [n for n in analysis if n in above]
    down = [n for n in analysis if n not in above]
    if up:
        analysis_lanes(up, reverse=True)
        y += GROUP_GAP
    y += HEADER_H
    obs_top = y
    for ln in lane_order:
        rows = [ns for (b, ck), ns in sorted(stack.items()) if b == ln]
        if rows:
            lane("L_OBS_" + ln, lane_label.get(ln, ln), "observed", ln, rows)
    obs_bottom = y
    if down:
        y += GROUP_GAP
        analysis_lanes(down)
    # ---- 시간 구간·눈금
    half = NODE_BOX["OBSERVED_EVENT"]["w"] / 2
    bands = []
    for bi, b in enumerate(BANDS):
        cx = [colx[c] for c in cols if c[0] == bi]
        if not cx:
            continue
        bands.append(dict(id=b["id"], label=b["label"], sub=b["sub"], dated=b["dated"],
                          x0=round(min(cx) - half - 24), x1=round(max(cx) + half + 24), y0=round(obs_top - HEADER_H + 10), y1=round(obs_bottom)))
    ticks, seen = [], set()
    for c in cols:
        if c[1] and (c[0], c[1]) not in seen:
            seen.add((c[0], c[1]))
            xs = [colx[d] for d in cols if d[0] == c[0] and d[1] == c[1]]
            ticks.append(dict(x=round((min(xs) + max(xs)) / 2), label=f"{c[1] // 100}/{c[1] % 100}", date_key=c[1]))
    extra = {n: dict(date_key=info[n]["key"], band=info[n]["band"], dated=info[n]["key"] is not None, column=cols.index(colkey[n]))
             for n in obs}
    xs0 = [layout[n]["x"] - bx(n)["w"] / 2 for n in layout]
    xs1 = [layout[n]["x"] + bx(n)["w"] / 2 for n in layout]
    extent = dict(x0=round(min(xs0 + [b["x0"] for b in bands]) - 30), x1=round(max(xs1 + [b["x1"] for b in bands]) + 30),
                  y0=0, y1=round(y))
    extent["label_x0"] = extent["x0"] - LABEL_W
    # 첫 화면 기준점: focus node(보통 View의 핵심 관측 node) 왼쪽 끝 앞에 lane 이름 칸만큼 여유를 둔 곳.
    # 핵심 node가 시간 축 앞쪽에 있으면 lane 이름 칸 왼쪽 끝과 같다.
    fx = [layout[n]["x"] - bx(n)["w"] / 2 for n in (focus or []) if n in layout]
    ax0 = extent["label_x0"] if not fx else max(extent["label_x0"], round(min(fx) - LABEL_W - 40))
    anchor = dict(x=ax0, y=round(obs_top - HEADER_H) if not up else 0)
    return dict(positions=layout, lanes=lanes, bands=bands, ticks=ticks, extra=extra, extent=extent, anchor=anchor,
                obs_top=round(obs_top), obs_bottom=round(obs_bottom))


def compute_layout(canon, boxes=None):
    """Overview(전체 canonical node) 배치. 반환 형식은 예전과 같다(+ extent·anchor)."""
    boxes = boxes or {n["node_id"]: node_box(n) for n in canon["sd_nodes"]}
    L = layout_subset(canon, boxes, [n["node_id"] for n in canon["sd_nodes"]])
    return L["positions"], L["lanes"], L["bands"], L["ticks"], L["extra"], L



# --------------------------------------------------------------------------- UI 데이터
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


# --------------------------------------------------------------------------- 관점별 View
# View는 '어떤 canonical node·edge를 이 화면에서 보여 줄 것인가'만 정한다. 새 node·edge·상태·해석을 만들지 않는다.
# 설명(desc)은 표시 범위만 말한다. 선택 규칙:
#   observed(핵심 관측) + context(직접 연결된 맥락 관측) + extra(명시한 분석·context node)
#   + gaps에 속한 LATENT 후보 전부
#   + 포함된 후보를 INSTANTIATED_BY(_SECONDARY)로 잇는 메커니즘
#   + 포함된 후보에 CONDITIONS를 거는 UNRESOLVED, 그리고 detail이 가리키는 관측 edge의 양끝이 모두 View 안에 있는 UNRESOLVED
# edge = 양끝 node가 모두 View 안에 있는 canonical edge 전부(자동 계산).
VIEW_SPECS = [
    dict(id="overview", key="A", label="A 전체 Overview", title="전체 Mechanism Super-DAG", policy="all",
         desc="모든 canonical node와 edge가 들어 있는 View입니다. 왼쪽 → 오른쪽이 시간(2월 → 3월 → 5월 → 6월 → 최종 판단·처분)이고, "
              "관측 lane 아래에 날짜 없는 분석 lane(구조 변수·후보·UNRESOLVED·메커니즘·context)이 있습니다. "
              "기본 표시 수준 '간단히'에서는 관측 사건과 핵심 흐름만 보이고 나머지는 접혀 있습니다('전체 보기'로 모두 표시)."),
    dict(id="timeline", key="B", label="B 시간순 사건", title="시간순 관측 사건", policy="subset", observed="ALL",
         desc="OBSERVED 사건 node(EP01–EP37)와 그 사이 canonical edge만 날짜 순서로 표시합니다. "
              "LATENT·CONTEXT·UNRESOLVED node는 이 View에서 숨깁니다('전체 주변 맥락 표시'로 함께 볼 수 있음)."),
    dict(id="suspect", key="C", label="C 구순→김명신 수사선상", title="구순 관련 정보 → 김명신 체포", policy="subset",
         observed=["EP01", "EP02", "EP03", "EP08", "EP09", "EP10", "EP11"], context=["EP07", "EP29"],
         gaps=["G03", "G04", "G05"], extra=["V_INFO_TO_COMMANDER"],
         desc="구순 관련 진술·정보가 김명신 체포(EP11)까지 연결되는 canonical node와 edge, "
              "그 사이 gap G03·G04·G05의 LATENT 후보와 관련 UNRESOLVED만 표시합니다."),
    dict(id="barracks", key="D", label="D 병영 지휘·체포", title="병영 지휘·체포", policy="subset",
         observed=["EP04", "EP05", "EP06", "EP09", "EP10", "EP11", "EP14", "EP30", "EP34", "EP35"], context=["EP03"],
         gaps=["G01", "G02", "G11"],
         extra=["V_COMPLAINT_TO_BARRACKS", "V_COMMAND_SOURCE", "V_ARREST_PATH", "V_INVESTIGATION_SCOPE",
                "CTX_F007", "CTX_F008", "CTX_F009", "U_ID06", "U_ID07", "U_ID08"],
         desc="병사·병영 비장·장교 일행의 출동·체포 지시·체포 기록(EP04–EP06, EP09–EP11)과 지휘 책임 기록(EP14, EP30, EP34, EP35), "
              "gap G01·G02·G11의 후보, 미확정 동일성 ID06–ID08을 표시합니다."),
    dict(id="jamideok", key="E", label="E 자미덕·진술·대질", title="자미덕·진술·대질", policy="subset",
         observed=["EP05", "EP06", "EP07", "EP12"], context=["EP04", "EP09", "EP23", "EP35"],
         gaps=["G09"], extra=["G04b", "G04d", "V_INFO_TO_COMMANDER", "V_INVESTIGATION_SCOPE"],
         desc="자미덕 관련 진술·대질 기록(EP05–EP07), 한재욱 공초(EP12), 두 진술 사이 주장 수준 상충 edge(OE007)와 "
              "진술 관련 후보(G04b·G04d·G09)·UNRESOLVED를 표시합니다."),
    dict(id="death", key="F", label="F 김명신 구금·사망", title="김명신 구금·사망: A 생물학적 경과 / B 절차·책임", policy="subset",
         observed=["EP11", "EP13", "EP21", "EP26", "EP27", "EP28", "EP29", "EP30"], context=["EP23"],
         gaps=["G06", "G12"],
         extra=["MB", "V_CUSTODY_COURSE", "ENV01", "ENV02", "ENV03", "ENV04", "V_ARREST_PATH", "V_INVESTIGATION_SCOPE", "V_RESPONSIBILITY"],
         desc="체포 뒤 구금·사망 관련 관측 기록, 전염병 환경 context, 사인 판단 branch A와 절차·책임 branch B를 위·아래로 나눠 표시합니다. "
              "두 branch를 직접 잇는 canonical edge는 없습니다."),
    dict(id="may_review", key="G", label="G 5월 재검토", title="5월 재검토", policy="subset",
         observed=["EP13", "EP14", "EP15", "EP16", "EP17", "EP18", "EP19", "EP20"],
         gaps=["G07", "G08", "G13"], extra=["V_INITIAL_JUDGMENT_BASIS", "V_REVIEW_CORRECTION"],
         desc="5월 재검토 기록(5/12 이형원 장계·1차 판단, 5/27 이조원 보고·비판, 5/28 안핵어사 차하)과 6월 재조사 이전 판단, "
              "gap G07·G08·G13의 후보를 표시합니다."),
    dict(id="hong_review", key="H", label="H 홍대협 재조사", title="홍대협 재조사", policy="subset",
         observed=["EP12", "EP20", "EP21", "EP22", "EP23", "EP24", "EP26", "EP31"],
         context=["EP02", "EP13", "EP15", "EP17", "EP18", "EP25", "EP27", "EP32"], extra=["V_REVIEW_CORRECTION", "M5"],
         desc="5/28 안핵어사 차하 이후 홍대협의 신문·복명과 6/13 홍대협 판단, 그 판단과 이전·이후 판단을 잇는 "
              "REVIEW_OF·REVISES·CONTRADICTS_AT_CLAIM_LEVEL edge를 표시합니다."),
    dict(id="final", key="I", label="I 정조 최종 판단·처분", title="정조 최종 판단·처분", policy="subset",
         observed=["EP25", "EP27", "EP28", "EP29", "EP30", "EP32", "EP33", "EP34", "EP35", "EP36", "EP37"],
         context=["EP14", "EP23", "EP24", "EP26", "EP31"], gaps=["G09", "G10"], extra=["V_RESPONSIBILITY", "V_SANCTION"],
         desc="6/13 정조의 판단(도난·사인·인과·책임·지세 호칭)과 처분, 6/16 이형원 유임, 직전 단계 기록과 "
              "gap G09·G10의 후보를 표시합니다."),
    dict(id="latent", key="J", label="J LATENT·World 비교", title="LATENT·World 비교", policy="dim", default_pane="world",
         desc="메커니즘·구조 변수·LATENT 후보·UNRESOLVED·context와 구조 변수가 설명 대상으로 가리키는 OBSERVED node를 표시합니다. "
              "나머지 OBSERVED node는 흐리게 남습니다. World·공존·개입 비교는 오른쪽 패널에서 합니다."),
]
VIEW_KEYS = {"id", "key", "label", "title", "desc", "policy", "nodes", "core", "context", "edges", "hidden_observed", "scope_rule",
             "layout", "initial", "default_pane", "groups", "cross_edges", "notice"}
VIEW_NOTICE = ("표시 범위만 줄인 화면입니다(시각적 필터). 숨긴 node는 삭제·부정된 것이 아니며 canonical graph에 그대로 있습니다. "
               "분석상 ON/OFF가 아닙니다.")


def build_views(canon, boxes, overview):
    import stage6_mechanisms as s6
    sdn, sde = canon["sd_nodes"], canon["sd_edges"]
    nmap = {n["node_id"]: n for n in sdn}
    ids = set(nmap)
    observed_all = sorted(n["node_id"] for n in sdn if n["node_type"] == "OBSERVED_EVENT")
    cand_rows = {c["candidate_id"]: c for c in canon["candidates"]}
    oe = {e["edge_id"]: e for e in canon["observed_edges"]}
    out, order = {}, []
    for spec in VIEW_SPECS:
        vid = spec["id"]
        order.append(vid)
        v = dict(id=vid, key=spec["key"], label=spec["label"], title=spec["title"], desc=spec["desc"], policy=spec["policy"],
                 default_pane=spec.get("default_pane", "detail"), notice="" if spec["policy"] == "all" else VIEW_NOTICE,
                 initial=dict(min_zoom=INITIAL_ZOOM_MIN, max_zoom=INITIAL_ZOOM_MAX, read_px=READ_PX))
        if spec["policy"] == "all":
            core, ctxn, rule = sorted(ids), [], "모든 canonical node"
        elif spec["policy"] == "dim":
            sd_targets = {e["dst"] for e in sde if e["origin"] == "SUPER_DAG" and nmap[e["dst"]]["node_type"] == "OBSERVED_EVENT"}
            core = sorted([n for n in ids if nmap[n]["node_type"] != "OBSERVED_EVENT"] + list(sd_targets))
            ctxn = []
            rule = "OBSERVED가 아닌 node 전부 + Super-DAG 분석 edge가 가리키는 OBSERVED node"
        else:
            obs = observed_all if spec.get("observed") == "ALL" else list(spec["observed"])
            ctxn = sorted(spec.get("context", []))
            gap_c = sorted(c for c, r in cand_rows.items() if r["gap_id"] in spec.get("gaps", []))
            extra = list(spec.get("extra", []))
            cands = set(gap_c) | {x for x in extra if nmap[x]["node_type"] == "CANDIDATE_BRIDGE"}
            mechs = {e["src"] for e in sde if e["edge_type"] in ("INSTANTIATED_BY", "INSTANTIATED_BY_SECONDARY") and e["dst"] in cands}
            base = set(obs) | set(ctxn) | set(extra) | cands | mechs
            unres = {e["src"] for e in sde if e["edge_type"] == "CONDITIONS" and e["dst"] in cands}
            for n in sdn:
                if n["node_type"] != "UNRESOLVED_ITEM" or not (spec.get("gaps") or extra):   # B(관측만)는 분석 node를 넣지 않음
                    continue
                refs = [(oe[o]["src"], oe[o]["dst"]) for o in re.findall(r"OE\d{3}", n["detail"]) if o in oe]
                refs += re.findall(r"(EP\d\d)→(EP\d\d)", n["detail"])
                if any(a in base and b in base for a, b in refs):
                    unres.add(n["node_id"])
            core = sorted((base | unres) - set(ctxn))
            parts = [f"핵심 관측: {', '.join(obs) if spec.get('observed') != 'ALL' else 'OBSERVED_EVENT 전부'}"]
            if ctxn:
                parts.append(f"맥락 관측: {', '.join(ctxn)}")
            if spec.get("gaps"):
                parts.append(f"gap {'·'.join(spec['gaps'])}의 LATENT 후보 전부")
            if extra:
                parts.append(f"명시 node: {', '.join(extra)}")
            if mechs:
                parts.append("포함 후보를 INSTANTIATED_BY로 잇는 메커니즘(" + ", ".join(sorted(mechs)) + ")")
            if unres:
                parts.append("포함 후보에 CONDITIONS를 걸거나 View 안 관측 edge를 가리키는 UNRESOLVED(" + ", ".join(sorted(unres)) + ")")
            rule = " · ".join(parts)
        nodes = sorted(set(core) | set(ctxn))
        assert set(nodes) <= ids, (vid, set(nodes) - ids)
        nset = set(nodes)
        v.update(nodes=nodes, core=sorted(core), context=ctxn, scope_rule=rule,
                 edges=sorted(e["edge_id"] for e in sde if e["src"] in nset and e["dst"] in nset),
                 hidden_observed=sorted(set(observed_all) - nset) if spec["policy"] == "subset" else [])
        if vid == "death":
            group_a = sorted(x for x in nodes if nmap[x]["branch"] == "A_BIOLOGICAL" or x in s6.BRANCH_A
                             or nmap[x]["node_type"] == "ENV_CONTEXT")
            group_b = sorted(x for x in nodes if x in s6.BRANCH_B)
            anchors = sorted(x for x in nodes if x not in group_a and x not in group_b)
            v["groups"] = dict(A=group_a, B=group_b, anchor=anchors)
            v["cross_edges"] = sorted(e["edge_id"] for e in sde if (e["src"] in group_a and e["dst"] in group_b)
                                      or (e["src"] in group_b and e["dst"] in group_a))
            above = {x for x in group_b if nmap[x]["node_type"] != "OBSERVED_EVENT"}
            names = {"L_SVAR_UP": "branch B · 절차·책임 구조 변수", "L_SVAR": "branch A · 생물학적 경과 구조 변수",
                     "L_CAND": "branch A · LATENT 후보 bridge", "L_MECH": "branch A · 메커니즘", "L_UNRES": "branch A · UNRESOLVED"}
        else:
            above, names = frozenset(), {}
        if spec["policy"] == "subset":
            focus = [x for x in core if nmap[x]["node_type"] == "OBSERVED_EVENT"] or core
            L = layout_subset(canon, boxes, nodes, above=above, names=names, focus=focus)
            v["layout"] = dict(positions={k: dict(x=p["x"], y=p["y"], lane=p["lane"]) for k, p in sorted(L["positions"].items())},
                               lanes=L["lanes"], bands=L["bands"], ticks=L["ticks"], extent=L["extent"], anchor=L["anchor"])
        elif spec["policy"] == "dim":
            first = min((l for l in overview["lanes"] if l["kind"] != "observed" and l["y0"] > overview["obs_top"]),
                        key=lambda l: l["y0"])
            pos = overview["positions"]
            fx = [pos[x]["x"] - boxes[x]["w"] / 2 for x in core if nmap[x]["node_type"] != "OBSERVED_EVENT"]
            v["layout"] = dict(anchor=dict(x=max(overview["extent"]["label_x0"], round(min(fx) - LABEL_W - 40)), y=first["y0"] - 40))
        out[vid] = v
    return dict(order=order, views=out, notice=VIEW_NOTICE,
                note="View는 canonical graph의 부분집합·강조일 뿐 새로운 분석 결과가 아니다. 상태·판정·World 구성은 바뀌지 않는다.")


def make_ui(canon, a4_findings=()):
    import stage5_worlds
    import stage6_mechanisms as s6
    sdn, sde = canon["sd_nodes"], canon["sd_edges"]
    eps = {r["node_id"]: r for r in canon["episodes"]}
    oedges = {r["edge_id"]: r for r in canon["observed_edges"]}
    cands = {r["candidate_id"]: r for r in canon["candidates"]}
    mech_ids = [n["node_id"] for n in sdn if n["node_type"] == "MECHANISM"]
    boxes = {n["node_id"]: node_box(n) for n in sdn}
    layout, lanes, bands, ticks, extra, full = compute_layout(canon, boxes)
    outcome = sorted({x for ids in stage5_worlds.COMMON_OUTCOME_NODES.values() for x in ids})
    env_ids = {r["env_id"]: r for r in canon["env"]}
    nodes = []
    for n in sdn:
        nid = n["node_id"]
        t = n["node_type"]
        head, body = node_text(n)
        short = f"{head} · {body}" if body else head   # 목록·검색용 한 줄 이름(자르지 않음)
        bxn = boxes[nid]
        display = dict(label=bxn["label"], lines=bxn["lines"], w=bxn["w"], h=bxn["h"], text_w=bxn["text_w"],
                       pad_x=bxn["pad_x"], pad_y=bxn["pad_y"], max_line_px=bxn["max_line_px"],
                       reserved_lines=MECH_RESERVED_LINES if t == "MECHANISM" else 0)
        item = dict(id=nid, canonical=dict(n), short_label=short, status_group=STATUS_GROUPS[n["sd_status"]],
                    layout=dict(layout[nid]), display=display, common_outcome=nid in outcome,
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
    super_dag = dict(nodes=nodes, edges=edges, lanes=lanes, bands=bands, ticks=ticks, extent=full["extent"],
                     anchor=full["anchor"], node_count=len(nodes), edge_count=len(edges))

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

    # ---- views (canonical node·edge의 부분집합과 표시 좌표만. 상태·판정·해석 필드는 없다)
    views = build_views(canon, boxes, full)

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
        edge_styles=EDGE_STYLES, edge_display=EDGE_DISPLAY, edge_display_order=EDGE_DISPLAY_ORDER,
        simple_view=SIMPLE_VIEW, config_display=CONFIG_DISPLAY,
        layout_rule=("x: 날짜가 있는 관측 node는 정렬 기준일(t_max, 없으면 t_min) 순서의 column에 놓는다. 같은 날짜 안에서는 frozen edge 깊이 순서. "
                     "y: 관측 node는 branch lane, 날짜 없는 node는 분석 lane. 날짜 없는 node의 x는 연결된 node 근처일 뿐 날짜를 뜻하지 않는다. "
                     "관점별 View는 그 View의 node만으로 같은 규칙을 다시 적용한 좌표를 쓴다."),
        typography=dict(read_px=READ_PX, read_pt=11, node_font_px=NODE_FONT, edge_font_px=EDGE_FONT, line_height=LINE_H,
                        read_zoom=round(READ_PX / NODE_FONT, 4), initial_zoom_min=INITIAL_ZOOM_MIN, initial_zoom_max=INITIAL_ZOOM_MAX,
                        far_id_font_px=30, lane_font_px=LANE_FONT, lane_sub_font_px=LANE_SUB_FONT, band_font_px=BAND_FONT,
                        band_sub_font_px=BAND_SUB_FONT, tick_font_px=TICK_FONT, label_w=LABEL_W, line_px=LINE_PX,
                        note="node label·UI 글자는 11pt(14.667px) 이상, line-height 1.6 이상. 첫 화면 zoom은 "
                             f"{INITIAL_ZOOM_MIN} 이상이라 node label이 {round(NODE_FONT * INITIAL_ZOOM_MIN, 1)}px로 그려진다."),
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


# index.html이 싣는 css·js 주소에 붙이는 ?v=<내용 해시>. GitHub Pages는 파일을 몇 분간 캐시하므로 버전이 없으면
# 새 index.html이 브라우저 캐시의 옛 app.js와 섞여 초기화가 중간에 멈출 수 있다(빈 그래프). 내용이 바뀌면 주소도 바뀐다.
ASSET_REF = re.compile(r'((?:src|href)=")((?:css|js|data|vendor)/[^"?]+)(?:\?v=[0-9a-f]*)?(")')


def asset_version(docs, rel):
    return hashlib.sha256((Path(docs) / rel).read_bytes()).hexdigest()[:12]


def stamped_index(docs=DOCS):
    """css·js 주소를 지금 파일 내용 해시로 맞춘 index.html 문자열(파일은 쓰지 않음)."""
    html = (Path(docs) / "index.html").read_text(encoding="utf-8")
    return ASSET_REF.sub(lambda m: f"{m.group(1)}{m.group(2)}?v={asset_version(docs, m.group(2))}{m.group(3)}", html)


def stamp_assets(docs=DOCS):
    """index.html의 css·js 주소를 지금 파일 내용 해시로 맞춘다. 바뀐 경우에만 다시 쓴다."""
    path = Path(docs) / "index.html"
    new = stamped_index(docs)
    if new != path.read_text(encoding="utf-8"):
        path.write_text(new, encoding="utf-8")
    return new


def build(docs=DOCS, out=OUT, pack=PACK, a4_findings=None):
    canon = load_canonical(out, pack)
    ui = make_ui(canon, a4_findings if a4_findings is not None else audit4_from_db())
    write_ui(docs, ui)
    stamp_assets(docs)
    return canon, read_ui(docs)


if __name__ == "__main__":
    canon, ui = build()
    print(f"[VIS] docs/data 작성: node {ui['meta']['counts']['nodes']} · edge {ui['meta']['counts']['edges']} · "
          f"frozen {ui['meta']['frozen_hash_prefix']}")
