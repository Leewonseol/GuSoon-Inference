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
    ("identity_forcing", "미확정 동일성(ID05) 강제: '풍각 김상제'를 김명신으로 치환(EP08)",
     lambda: _episode_case("EP08", "유제희는 현지 탐문 중 구순이 김명신도 극히 수상하다고 말했고, 자신이 그 말을 원돌 등의 이름과 함께 "
                                   "기록해 올렸다고 진술했다.", "identity_forcing")),
    ("stale_identity_condition", "사용자 확정 동일성(ID01)이 edge condition에 남아 있음(OE081)", lambda: _stale_edge_case()),
    ("resolved_identity_conflict", "확정 동일성(ID02)을 불성립으로 전제한 후보(G09b)가 INCOMPATIBLE이 아님", lambda: _negation_case()),
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


def run():
    results = []
    for rule, desc, fn in CASES:
        ok, detail = fn()
        results.append(dict(rule=rule, case=desc, caught=ok, detail=detail))
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
