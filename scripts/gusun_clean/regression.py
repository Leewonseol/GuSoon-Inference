"""Regression validation — 수동 검토에서 고친 오류가 다시 나타나면 검사기가 반드시 잡는지 확인한다.

build.py가 Audit 1 전에 run_or_exit()를 호출한다. 각 케이스는 과거에 실제로 있었던 결함(또는 금지 규칙의 대표 예)을
검사기에 넣고, 기대한 check가 ERROR로 나오는지 본다. 하나라도 놓치면 파이프라인을 멈춘다.
"""
import copy
import sys

import audits
from stage1_episodes import EPISODES

CF_STUB = None


def _load_cf():
    import csv
    from pathlib import Path
    root = Path(__file__).resolve().parents[2] / "gusun_clean_restart_csv_pack"
    rd = lambda n: [dict(r) for r in csv.DictReader(open(root / n, encoding="utf-8-sig"))]
    return rd("01_confirmed_facts.csv"), rd("05_source_faithful_propositions_AUDIT_ONLY.csv"), rd("04_source_records.csv")


def _episode_case(eid, new_summary, expect):
    eps = copy.deepcopy(EPISODES)
    for e in eps:
        if e["episode_id"] == eid:
            e["summary"] = new_summary
    cf, props, src = _load_cf()
    found, _ = audits.audit1(eps, cf, props, src)
    hit = {f["check"] for f in found if f["severity"] == "ERROR" and f["target"] == eid}
    return expect in hit, sorted(hit)


# (rule, 설명, 함수)
CASES = [
    ("epistemic_marker_deletion", "A1-W1 원안 EP01: 진술 3건을 '명업의 진술에 따르면' 하나로 합침",
     lambda: _episode_case("EP01", "명업의 진술에 따르면, 김명신은 본래 구순과 친숙하여 날마다 왕래했으나, 박거사 일로 구순에게 "
                                   "편지를 보내 힐책했고, 그 뒤 구순과 김명신의 왕래가 끊겼다.", "epistemic_marker_deletion")),
    ("testimony_to_fact", "A1-E1 원안 EP07: '자미덕의 진술에 따르면 … 거짓으로 꾸며 말했다'",
     lambda: _episode_case("EP07", "자미덕의 진술에 따르면, 한 비장이 정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적이라고 말하면 "
                                   "자신과 남편을 다음 날 석방하겠다고 말했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 "
                                   "거짓으로 꾸며 말했다.", "testimony_to_fact")),
    ("actor_substitution", "A1-W2 원안 EP04: '자신'을 '이진욱'으로 치환",
     lambda: _episode_case("EP04", "이진욱은 2월 28일 밤 병영에서 이진욱을 비장청으로 불렀다고 진술했고, 한재욱이 이진욱과 조계완 등에게 "
                                   "덕평으로 가도록 지시했다고 진술했으며, 한재욱이 변지돌과 정원돌을 잡아오라고 지시했다고 진술했고, "
                                   "한재욱이 철편 네 개를 만들어 주었다고 진술했다.", "actor_substitution")),
    ("actor_substitution", "진술자 바꿔치기: EP12의 한재욱 공초를 자미덕 진술로",
     lambda: _episode_case("EP12", "자미덕은 한재욱이 자신을 방으로 불러 남은 밥을 주었고 은밀히 사주한 일은 없다고 진술했고, "
                                   "구순과 평생 모르는 사이라고 진술했다.", "actor_substitution")),
    ("semantic_weakening", "'은밀히' 삭제: 어떤 사주도 없었다",
     lambda: _episode_case("EP12", "한재욱은 자미덕을 방으로 불러 남은 밥을 준 사실은 인정했지만 자미덕을 사주한 일은 전혀 없다고 진술했고, "
                                   "구순과 평생 모르는 사이라고 진술했다.", "semantic_weakening")),
    ("surface_form_substitution", "확정 동일성(ID01)이라도 episode summary에서 '병사'를 이광섭으로 바꾸면 안 됨(EP09)",
     lambda: _episode_case("EP09", "이진욱은 3월 4일 이광섭이 풍각 김생원과 흥덕 김생원을 잡아오라고 지시했다고 진술했다. "
                                   "해당 기사에서 풍각 김생원은 김명신, 흥덕 김생원은 김갑득으로 식별된다.", "surface_form_substitution")),
    ("surface_form_substitution", "확정 동일성(ID02)이라도 episode summary에서 '한 비장'을 한재욱으로 바꾸면 안 됨(EP07)",
     lambda: _episode_case("EP07", "자미덕은 한재욱이 정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적이라고 말하면 자신과 남편을 다음 날 "
                                   "석방하겠다고 말했다고 진술했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 "
                                   "말했다고 진술했다.", "surface_form_substitution")),
    ("surface_form_substitution", "확정 동일성(ID05)이라도 episode summary에서 '풍각 김상제'를 김명신으로 바꾸면 안 됨(EP08)",
     lambda: _episode_case("EP08", "유제희는 현지 탐문 중 구순이 김명신도 극히 수상하다고 말했고, 자신이 그 말을 원돌 등의 이름과 함께 "
                                   "기록해 올렸다고 진술했다.", "surface_form_substitution")),
    ("identity_forcing", "미확정 동일성(ID06) 강제: '병영의 염탐 담당자'를 유제희로 치환(EP29)",
     lambda: _episode_case("EP29", "정조는 구순이 김명신에게 사적인 감정을 품고 갈등을 일으켰고, 유제희에게 김명신의 성명을 적어 주었으며, "
                                   "그 과정이 김명신이 횡액을 입고 원통하게 죽는 결과로 이어졌다고 책임을 연결해 판단했다.", "identity_forcing")),
    ("stale_identity_condition", "사용자 확정 동일성(ID01)이 edge condition에 남아 있음(OE081)", lambda: _stale_edge_case()),
    ("resolved_identity_conflict", "확정 동일성(ID02)을 불성립으로 전제한 후보(G09b)가 INCOMPATIBLE이 아님", lambda: _negation_case()),
    ("open_gap_filled", "사용자가 열어 두기로 한 G10을 world가 채움", lambda: _open_gap_case()),
    ("bridge_support_inflation", "재감사 이전 G08a: 동기 bridge 근거 없음(NO)인데 source_support=HIGH",
     lambda: _bridge_case("G08a", dict(source_support="HIGH", bridge_evidence="V3P0028"), "bridge_support_inflation")),
    ("temporal_inflation", "시간 인접·endpoint 내용만으로 동기 bridge를 MEDIUM 이상으로 평가(G08a)",
     lambda: _bridge_case("G08a", dict(source_support="MEDIUM", bridge_evidence="V3P0028"), "temporal_inflation")),
    ("institutional_inflation", "제도 가능성만으로 source_support=MEDIUM(G01c)",
     lambda: _bridge_case("G01c", dict(source_support="MEDIUM", bridge_evidence="F005"), "institutional_inflation")),
    ("endpoint_leakage", "endpoint 구성 fact(CF033·CF035)를 bridge 근거로 인용(G08a)",
     lambda: _bridge_case("G08a", dict(bridge_evidence="CF033|CF035"), "endpoint_leakage")),
    ("bridge_support_inflation", "재감사 이전 값 전체(source_consistency_v1)를 다시 넣으면 검사가 잡는지",
     lambda: _old_values_case()),
    ("outcome_world_dependency", "확정 처분(구순 정배)을 특정 world의 결과로 서술", lambda: _outcome_case()),
    ("closed_set", "'등' 삭제(EP07)",
     lambda: _episode_case("EP07", "자미덕은 한 비장이 정원돌·이집거·김갑득·김성손·김흥득을 큰 도적이라고 말하면 자신과 남편을 다음 날 "
                                   "석방하겠다고 말했다고 진술했고, 자미덕은 이집거와 대질했으며, 그때 한 비장의 지휘에 따라 거짓으로 꾸며 "
                                   "말했다고 진술했다.", "closed_set")),
    ("semantic_strengthening", "'극히 수상하다' → 범인 지목(EP08)",
     lambda: _episode_case("EP08", "유제희는 현지 탐문 중 구순이 풍각 김상제를 범인으로 지목했고, 자신이 그 말을 원돌 등의 이름과 함께 "
                                   "기록해 올렸다고 진술했다.", "semantic_strengthening")),
    ("responsibility_to_causation", "책임 판단을 직접 사인으로(EP29)",
     lambda: _episode_case("EP29", "정조는 구순이 김명신에게 사적인 감정을 품고 갈등을 일으켰고, 병영의 염탐 담당자에게 김명신의 성명을 "
                                   "적어 주었으며, 그 과정이 김명신이 횡액을 입고 원통하게 죽는 결과로 이어졌다고 책임을 연결해 판단했다. "
                                   "즉 김명신은 구순 때문에 죽었다.", "responsibility_to_causation")),
    ("environment_to_individual_fact", "환경을 개인 사인으로(EP27)",
     lambda: _episode_case("EP27", "정조는 김명신 부처가 전염병에 걸려 죽은 것으로 판단했고, 김명신이 곤장을 맞지 않았고 평범한 신문도 "
                                   "받지 않았다고 판단했다. 호서 전염병 창궐 때문에 김명신이 감염되었다.", "environment_to_individual_fact")),
    ("occurrence_record_confusion", "기록일(6/13)을 진술 내용의 발생 시점으로 사용(EP06)",
     lambda: _occ_case()),
    ("latent_as_observed", "A3-W1 원안 G08a: 관측 node 사이 직접 latent edge",
     lambda: _latent_case()),
    ("open_set_closure", "world 서술에서 열린 명단의 '등' 삭제",
     lambda: ("open_set_closure" in {"open_set_closure" for _ in audits.open_set_closures("정원돌·이집거·김갑득을 지목")}, [])),
    ("environment_to_individual_fact", "후보·world 서술: 환경 → 개인 감염 단정",
     lambda: (bool(audits.text_regressions("호서 전염병 때문에 김명신이 옥중에서 감염되었다")), [])),
]

# Audit 4: mechanism Super-DAG
A4_CASES = [
    ("context_to_fact", "context(F013 암행어사 제도)에서 새 관측 사건 node를 만듦",
     lambda: _sd_case(_mut_new_fact, "context_to_fact")),
    ("environment_to_personal_fact", "환경(ENV03 전염병)을 김명신 구금 경과 후보(G06a)에 직접 연결",
     lambda: _sd_case(_mut_env_personal, "environment_to_personal_fact")),
    ("institution_to_event", "제도 가능성(F007 병사 지휘권)이 3/4 체포 지시(EP09)를 직접 만듦",
     lambda: _sd_case(_mut_inst_event, "institution_to_event")),
    ("world_merge", "상충 후보 G03b를 W2(G04b 사용)에 섞음",
     lambda: _sd_case(_mut_world_merge, "world_merge")),
    ("w6_reactivation", "REJECTED W6을 경쟁 설명으로 되살리고 공존 분석에 넣음",
     lambda: _sd_case(_mut_w6, "w6_reactivation")),
    ("responsibility_to_biological", "책임 구조 변수(V_RESPONSIBILITY) → 사인 판단(EP27) 직접 edge",
     lambda: _sd_case(_mut_resp_bio, "responsibility_to_biological")),
    ("off_mechanism_alive", "W1에서 M1=OFF로 바꿨는데 M1 후보(G01a·G02a·G03a·G04a)가 그대로 살아 있음",
     lambda: _sd_case(_mut_off_alive, "off_mechanism_alive")),
    ("unspecified_as_off", "W5의 M3(관련 후보 없음, UNSPECIFIED)를 OFF로 표기",
     lambda: _sd_case(_mut_unspec_off, "unspecified_as_off")),
    ("world_latent_promoted", "W1 전용 후보 G04a를 모든 world 공통 사실로 표시",
     lambda: _sd_case(_mut_promote, "world_latent_promoted")),
    ("outcome_world_dependency", "확정 처분(EP33 구순 정배)을 W1에만 속한 결과로 표시",
     lambda: _sd_case(_mut_outcome, "outcome_world_dependency")),
]
CASES = CASES + A4_CASES

# Audit 5: interactive visualization 데이터(docs/data). 화면 데이터 사본 하나만 바꿔 넣는다.
A5_CASES = [
    ("ui_node_not_canonical", "화면 데이터에 canonical에 없는 관측 사건 node(EP_NEW)를 추가",
     lambda: _ui_case(_ui_new_node, "ui_node_not_canonical")),
    ("ui_edge_not_canonical", "화면 데이터에 canonical에 없는 edge(CTX_F007 → EP09)를 추가",
     lambda: _ui_case(_ui_new_edge, "ui_edge_not_canonical")),
    ("status_changed", "LATENT 후보 G04a를 화면에서 OBSERVED로 표시",
     lambda: _ui_case(_ui_status, "status_changed")),
    ("w6_not_rejected", "W6을 화면에서 경쟁 설명(COMPETING_EXPLANATION)으로 표시하고 REJECTED 배너를 뺌",
     lambda: _ui_case(_ui_w6, "w6_not_rejected")),
    ("outcome_dropped", "W3 선택 시 공통 결말 EP33(구순 신지도 정배)을 숨김 대상으로 둠",
     lambda: _ui_case(_ui_outcome, "outcome_dropped")),
    ("unspecified_as_off", "W5의 M3(UNSPECIFIED)를 화면에서 OFF로 표시",
     lambda: _ui_case(_ui_unspec, "unspecified_as_off")),
    ("context_as_event", "환경 context ENV03을 4/10 날짜 구간에 사건처럼 배치",
     lambda: _ui_case(_ui_context_event, "context_as_event")),
    ("environment_to_individual", "환경 ENV03 → 김명신 구금 경과 후보 G06a edge를 화면에 추가",
     lambda: _ui_case(_ui_env_personal, "environment_to_individual")),
    ("responsibility_to_biological", "책임 V_RESPONSIBILITY → 사인 판단 EP27 직접 edge를 화면에 추가",
     lambda: _ui_case(_ui_resp_bio, "responsibility_to_biological")),
    ("temporal_order", "3/4 체포 지시(EP09)와 6/13 최종 도난 판단(EP25)의 x 위치를 맞바꿈",
     lambda: _ui_case(_ui_temporal, "temporal_order")),
    ("candidate_grade_changed", "화면에서 후보 G01a의 final grade를 MEDIUM → HIGH로 표시",
     lambda: _ui_case(_ui_grade, "candidate_grade_changed")),
    ("intervention_changed", "화면에서 do(M1=OFF)·V_COMPLAINT_TO_BARRACKS 결과를 PATH_BREAKS → PATH_REMAINS로 표시",
     lambda: _ui_case(_ui_iv, "intervention_changed")),
]
CASES = CASES + A5_CASES


def _occ_case():
    eps = copy.deepcopy(EPISODES)
    for e in eps:
        if e["episode_id"] == "EP06":
            e["t_min"], e["t_max"] = 613, 613
    cf, props, src = _load_cf()
    found, _ = audits.audit1(eps, cf, props, src)
    hit = {f["check"] for f in found if f["severity"] == "ERROR" and f["target"] == "EP06"}
    return "occurrence_record_confusion" in hit, sorted(hit)


def _latent_case():
    import stage4_latent
    gaps, cands = stage4_latent.build([], [])
    cands = copy.deepcopy(cands)
    for c in cands:
        if c["candidate_id"] == "G08a":
            c["latent_nodes"] = []
            c["latent_edges"] = [dict(src="EP18", dst="EP20", edge_type="PROCEDURAL_NEXT", status="LATENT")]
    nodes = [dict(node_id=f"EP{i:02d}", node_status="OBSERVED", layer="X") for i in range(1, 38)]
    nodes += [dict(node_id=f"ENV0{i}", node_status="OBSERVED", layer="ENVIRONMENT") for i in range(1, 5)]
    found = audits.audit3(nodes, [], "h", "h", gaps, cands, [])
    hit = {f["check"] for f in found if f["severity"] == "ERROR" and f["target"] == "G08a"}
    return "latent_as_observed" in hit, sorted(hit)


def _stale_edge_case():
    import build
    cf = build.read_csv("01_confirmed_facts.csv")
    env = build.read_csv("03_environment_1793.csv")
    nodes, edges, links = build.stage2(build.stage1(cf), env)
    for e in edges:
        if e["edge_id"] == "OE081":
            e["condition"] = "ID01"
    found = audits.audit2(nodes, edges, EPISODES, links, env, build.EDGE_TYPES, build.BASES)
    hit = {f["check"] for f in found if f["severity"] == "ERROR" and f["target"] == "OE081"}
    return "stale_identity_condition" in hit, sorted(hit)


def _negation_case():
    import stage4_latent
    gaps, cands = stage4_latent.build([], [])
    cands = copy.deepcopy(cands)
    for c in cands:
        if c["candidate_id"] == "G09b":
            c["overall"] = "LOW"
    nodes = [dict(node_id=f"EP{i:02d}", node_status="OBSERVED", layer="X") for i in range(1, 38)]
    found = audits.audit3(nodes, [], "h", "h", gaps, cands, [])
    hit = {f["check"] for f in found if f["severity"] == "ERROR" and f["target"] == "G09b"}
    return "resolved_identity_conflict" in hit, sorted(hit)


def _open_gap_case():
    import build
    import stage4_latent
    import stage5_worlds
    cf = build.read_csv("01_confirmed_facts.csv")
    env = build.read_csv("03_environment_1793.csv")
    nodes, edges, _ = build.stage2(build.stage1(cf), env)
    gaps, cands = stage4_latent.build(nodes, edges)
    worlds = copy.deepcopy(stage5_worlds.build(nodes, edges, gaps, cands))
    w5 = next(w for w in worlds if w["world_id"] == "W5")
    w5["latent_bridges"] = w5["latent_bridges"] + ["G10a"]
    found = audits.audit3(nodes, edges, "h", "h", gaps, cands, [], worlds)
    hit = {f["check"] for f in found if f["severity"] == "ERROR" and f["target"] == "W5"}
    return "open_gap_filled" in hit, sorted(hit)


def _reaudit_inputs():
    import build
    import stage4_latent
    cf = build.read_csv("01_confirmed_facts.csv")
    env = build.read_csv("03_environment_1793.csv")
    nodes, edges, _ = build.stage2(build.stage1(cf), env)
    gaps, cands = stage4_latent.build(nodes, edges)
    return nodes, copy.deepcopy(cands)


def _bridge_case(cid, overrides, expect):
    nodes, cands = _reaudit_inputs()
    c = next(x for x in cands if x["candidate_id"] == cid)
    c.update(overrides)
    hit = {f["check"] for f in audits.bridge_support_checks(c, nodes) if f["severity"] == "ERROR"}
    return expect in hit, sorted(hit)


def _old_values_case():
    """재감사 이전 HIGH 후보(G01a·G06a·G07a·G08a 등)의 옛 source 값을 그대로 넣었을 때 ERROR가 나는 후보를 센다."""
    nodes, cands = _reaudit_inputs()
    flagged = []
    for c in cands:
        if c["source_consistency_v1"] == "HIGH":
            c["source_support"] = "HIGH"
            if any(f["severity"] == "ERROR" for f in audits.bridge_support_checks(c, nodes)):
                flagged.append(c["candidate_id"])
    return {"G07a", "G08a"} <= set(flagged), flagged


def _outcome_case():
    import build
    import stage4_latent
    import stage5_worlds
    cf = build.read_csv("01_confirmed_facts.csv")
    env = build.read_csv("03_environment_1793.csv")
    nodes, edges, _ = build.stage2(build.stage1(cf), env)
    gaps, cands = stage4_latent.build(nodes, edges)
    worlds = copy.deepcopy(stage5_worlds.build(nodes, edges, gaps, cands))
    w5 = next(w for w in worlds if w["world_id"] == "W5")
    w5["story_implication"] += " W5에서는 구순이 정배되지 않을 수도 있다."
    hit = {f["check"] for f in audits.outcome_dependency_checks(worlds, cands, nodes) if f["severity"] == "ERROR"}
    return "outcome_world_dependency" in hit, sorted(hit)


_SD_INPUTS = {}


def _sd_inputs():
    if not _SD_INPUTS:
        import build
        import stage4_latent
        import stage5_worlds
        import stage6_mechanisms
        cf = build.read_csv("01_confirmed_facts.csv")
        env = build.read_csv("03_environment_1793.csv")
        inst = build.read_csv("02_institutional_normative_features.csv")
        nodes, edges, _ = build.stage2(build.stage1(cf), env)
        gaps, cands = stage4_latent.build(nodes, edges)
        worlds = stage5_worlds.build(nodes, edges, gaps, cands)
        frozen = build.graph_hash(nodes, edges)
        sd = stage6_mechanisms.build(nodes, edges, cands, worlds, inst, env, frozen)
        _SD_INPUTS.update(nodes=nodes, edges=edges, cands=cands, worlds=worlds, frozen=frozen, sd=sd, hash=build.graph_hash)
    return _SD_INPUTS


def _sd_case(mutate, expect):
    """깨끗한 Super-DAG에서 ERROR가 없음을 먼저 확인하고, 사본 하나만 바꿔 기대한 check가 ERROR로 나오는지 본다."""
    x = _sd_inputs()
    clean = audits.audit4(x["sd"], x["nodes"], x["edges"], x["frozen"], x["hash"], x["worlds"], x["cands"])
    if any(f["severity"] == "ERROR" for f in clean):
        return False, ["clean baseline already has ERROR"]
    sd, worlds = copy.deepcopy(x["sd"]), copy.deepcopy(x["worlds"])
    mutate(sd, worlds)
    found = audits.audit4(sd, x["nodes"], x["edges"], x["frozen"], x["hash"], worlds, x["cands"])
    hit = {f["check"] for f in found if f["severity"] == "ERROR"}
    return expect in hit, sorted(hit)


def _sd_edge(sd, src, dst, etype, status):
    sd["edges"].append(dict(edge_id="SD_REG", src=src, dst=dst, edge_type=etype, sd_status=status, origin="SUPER_DAG", note=""))


def _mut_new_fact(sd, worlds):
    sd["nodes"].append(dict(node_id="EP_NEW", sd_status="OBSERVED", node_type="OBSERVED_EVENT",
                            label="4월 암행어사 공주 재조사", frozen_status="", branch="", mechanism="", worlds="ALL (공통)", detail=""))
    _sd_edge(sd, "CTX_F013", "EP_NEW", "CONSTRAINS", "CONTEXT")


def _mut_env_personal(sd, worlds):
    _sd_edge(sd, "ENV03", "G06a", "CONTEXT_COMPATIBLE", "CONTEXT")


def _mut_inst_event(sd, worlds):
    _sd_edge(sd, "CTX_F007", "EP09", "CONSTRAINS", "CONTEXT")


def _mut_world_merge(sd, worlds):
    w2 = next(w for w in worlds if w["world_id"] == "W2")
    w2["latent_bridges"] = w2["latent_bridges"] + ["G03b"]


def _mut_w6(sd, worlds):
    w6 = next(w for w in worlds if w["world_id"] == "W6")
    w6["role_type"] = "COMPETING_EXPLANATION"
    sd["interactions"][0]["cooccur_worlds"] += ", W6"


def _mut_resp_bio(sd, worlds):
    _sd_edge(sd, "V_RESPONSIBILITY", "EP27", "EXPLAINS_TRANSITION_TO", "LATENT_MECHANISM")


def _mut_off_alive(sd, worlds):
    sd["configs"]["W1"]["M1"] = "OFF"


def _mut_unspec_off(sd, worlds):
    sd["configs"]["W5"]["M3"] = "OFF"


def _mut_promote(sd, worlds):
    n = next(n for n in sd["nodes"] if n["node_id"] == "G04a")
    n["worlds"] = "ALL (공통)"


def _mut_outcome(sd, worlds):
    n = next(n for n in sd["nodes"] if n["node_id"] == "EP33")
    n["worlds"] = "W1"


_UI_INPUTS = {}


def _ui_inputs():
    """화면 데이터를 canonical 산출물(output/clean, 원본 pack)에서 메모리로 만든다(docs/data 파일은 건드리지 않음)."""
    if not _UI_INPUTS:
        import build_visualization as bv
        canon = bv.load_canonical()
        _UI_INPUTS.update(canon=canon, ui=bv.make_ui(canon, []))
    return _UI_INPUTS


def _ui_case(mutate, expect):
    x = _ui_inputs()
    frozen = x["canon"]["freeze"]["sha256"]
    clean = audits.audit5(x["ui"], x["canon"], frozen)
    if any(f["severity"] == "ERROR" for f in clean):
        return False, ["clean baseline already has ERROR"]
    ui = copy.deepcopy(x["ui"])
    mutate(ui)
    hit = {f["check"] for f in audits.audit5(ui, x["canon"], frozen) if f["severity"] == "ERROR"}
    return expect in hit, sorted(hit)


def _ui_node(ui, nid):
    return next(n for n in ui["super_dag"]["nodes"] if n["id"] == nid)


def _ui_add_edge(ui, src, dst, etype, status, group):
    ui["super_dag"]["edges"].append(dict(id="SD_REG", status_group=group, canonical=dict(
        edge_id="SD_REG", src=src, dst=dst, edge_type=etype, sd_status=status, origin="SUPER_DAG", note="")))


def _ui_new_node(ui):
    n = copy.deepcopy(_ui_node(ui, "EP09"))
    n["id"] = n["canonical"]["node_id"] = "EP_NEW"
    n["canonical"]["label"] = "4월 암행어사 공주 재조사"
    ui["super_dag"]["nodes"].append(n)


def _ui_new_edge(ui):
    _ui_add_edge(ui, "CTX_F007", "EP09", "CONSTRAINS", "CONTEXT", "CONTEXT")


def _ui_status(ui):
    n = _ui_node(ui, "G04a")
    n["canonical"]["sd_status"], n["status_group"] = "OBSERVED", "OBSERVED"


def _ui_w6(ui):
    w = ui["worlds"]
    w["configurations"]["W6"]["role_type"] = "COMPETING_EXPLANATION"
    w["selections"]["W6"].update(rejected=False, banner="")
    w["rejected"] = []


def _ui_outcome(ui):
    s = ui["worlds"]["selections"]["W3"]
    s["always_visible"] = [x for x in s["always_visible"] if x != "EP33"]
    s["hideable"] = s["hideable"] + ["EP33"]


def _ui_unspec(ui):
    ui["worlds"]["configurations"]["W5"]["M3"] = "OFF"
    ui["worlds"]["selections"]["W5"]["mechanism_state"]["M3"] = "OFF"


def _ui_context_event(ui):
    n = _ui_node(ui, "ENV03")
    n["layout"].update(dated=True, date_key=410, band="MAY")


def _ui_env_personal(ui):
    _ui_add_edge(ui, "ENV03", "G06a", "CONTEXT_COMPATIBLE", "CONTEXT", "CONTEXT")


def _ui_resp_bio(ui):
    _ui_add_edge(ui, "V_RESPONSIBILITY", "EP27", "EXPLAINS_TRANSITION_TO", "LATENT_MECHANISM", "LATENT")


def _ui_temporal(ui):
    a, b = _ui_node(ui, "EP09"), _ui_node(ui, "EP25")
    a["layout"]["x"], b["layout"]["x"] = b["layout"]["x"], a["layout"]["x"]


def _ui_grade(ui):
    ui["candidates"]["rows"]["G01a"]["overall"] = "HIGH"


def _ui_iv(ui):
    r = next(r for r in ui["interventions"]["rows"]
             if r["canonical"]["mechanism"] == "M1" and r["canonical"]["variable"] == "V_COMPLAINT_TO_BARRACKS")
    r["canonical"]["result"] = "PATH_REMAINS"


def run():
    results = []
    for rule, desc, fn in CASES:
        ok, detail = fn()
        audit = ("AUDIT4" if any(desc == c[1] for c in A4_CASES) else
                 "AUDIT5" if any(desc == c[1] for c in A5_CASES) else "AUDIT1-3")
        results.append(dict(rule=rule, case=desc, caught=ok, detail=detail, audit=audit))
    return results


def run_or_exit():
    res = run()
    miss = [r for r in res if not r["caught"]]
    print(f"[REGRESSION] {len(res) - len(miss)}/{len(res)} 케이스 탐지")
    if miss:
        for r in miss:
            print("   MISSED", r["rule"], r["case"], r["detail"])
        sys.exit(1)
    return res
