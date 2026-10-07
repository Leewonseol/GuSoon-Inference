"""STAGE 6 — Qualitative SCM / Boolean-style Mechanism Super-DAG.

목적: W1–W5를 따로 떨어진 세계로만 보지 않고, 하나의 상위 DAG 안에서 '메커니즘 변수의 조합(configuration)'으로 표현한다.
질문: 어떤 메커니즘이 단독 또는 함께 작동하면 관측된 사건 흐름을 설명할 수 있는가?

고정 원칙
- frozen observed graph(OBSERVED·DERIVED)는 그대로 복사만 한다. 수정하지 않는다.
- 메커니즘은 역사적 사실이 아니라 분석 변수다(status=LATENT_MECHANISM).
- 기존 LATENT 후보를 메커니즘으로 묶을 뿐, 새 후보·새 사건을 만들지 않는다. 후보 등급도 바꾸지 않는다.
- 제도 피쳐(F)는 메커니즘의 가능성을 제약하는 CONTEXT다. 환경 피쳐(E)는 질병·사망 설명의 호환성 CONTEXT다.
  둘 다 사건을 직접 만들지 않는다.
- 통계적 SEM 계수, 확률, practice prior를 쓰지 않는다. 값은 ON/OFF/PARTIAL/UNSPECIFIED와 질적 규칙뿐이다.
- 사망 branch A(생물학적 경과, MB)와 branch B(절차·책임, M1–M4)를 연결하지 않는다.
"""

# ---------------------------------------------------------------------------- 메커니즘 정의
MECHANISMS = {
    "M1": dict(name="M1_OFFICIAL_INFORMATION_ROUTE", short="공식경로",
               easy="구순 쪽 소장·정보가 진영·병영 비장·병사로 이어지는 공식 보고·지휘 경로를 따라 이동하는 구조",
               key_gap="G04", branch="B_PROCEDURAL",
               features="F005|F006|F007|F008|F009|F010|F020", envs="",
               note="공식 경로가 제도상 가능하다는 것(F007·F008)은 경로가 실제로 쓰였다는 근거가 아니다."),
    "M2": dict(name="M2_TESTIMONY_AMPLIFICATION", short="진술증폭",
               easy="자미덕 등의 진술·대질·번복이 수사 범위나 판단 자료를 키우거나 바꾸는 구조",
               key_gap="G04", branch="B_PROCEDURAL",
               features="F002|F004|F009|F020", envs="",
               note="회유 행위 자체의 합법성은 LOW(F002, EP07 feature link)다. 진술이 보고 경로를 탄다는 정보 흐름만 MEDIUM이다."),
    "M3": dict(name="M3_PRIVATE_INFLUENCE_CHANNEL", short="사적통로",
               easy="구순과 병영 지휘관 사이의 비공식·사적 통로(서신·접촉)를 통해 정보나 영향이 전달되는 구조",
               key_gap="G04", branch="B_PROCEDURAL",
               features="F007|F020", envs="",
               note="구순(전 부사)에게는 병영 지휘권이 없다(F007 role LOW). 그래서 M3는 '명령'이 아니라 '정보·영향 제공'으로만 쓸 수 있다(G04e INCOMPATIBLE)."),
    "M4": dict(name="M4_DISTRIBUTED_INSTITUTIONAL_ACTION", short="분산행동",
               easy="하나의 중앙 지휘가 아니라 비장·아전·진(鎭) 등 여러 기관·실무자의 판단이 따로 쌓이는 구조",
               key_gap="G02", branch="B_PROCEDURAL",
               features="F006|F008|F009|F010", envs="",
               note="F006(관찰사 감독)·F009(비장 막료)는 분산 실무의 여지를 주지만, 그 자체가 분산 행동의 근거는 아니다."),
    "M5": dict(name="M5_REVIEW_AND_CORRECTION", short="재검토교정",
               easy="초기 판단을 암행어사·안핵어사·비변사·국왕 심리가 따로 다시 검토하고 고치는 구조",
               key_gap="G08", branch="REVIEW",
               features="F006|F011|F012|F013|F014|F017|F018|F020", envs="",
               note="재검토 과정 자체(5/12 → 5/27 → 5/28 → 6/11 → 6/13 → 처분)는 OBSERVED backbone이다. M5는 그 backbone을 설명하는 분석 변수이고, "
                    "LATENT 후보(G08·G09·G10·G13)는 동기·근거·실행 같은 내부 세부만 다룬다. 관측 사건을 LATENT로 바꾸지 않는다.",
               observed_anchor=["EP15", "EP16", "EP17", "EP18", "EP19", "EP20", "EP21", "EP22", "EP23", "EP24", "EP25",
                                "EP26", "EP27", "EP28", "EP29", "EP30", "EP31", "EP32", "EP33", "EP34", "EP35", "EP36", "EP37"]),
    "M6": dict(name="M6_INITIAL_JUDGMENT_BASIS", short="초기판단근거",
               easy="5월 단계의 '도난 없음 방향' 판단이 어떤 자료·추론에서 형성되었는지에 관한 구조",
               key_gap="G07", branch="REVIEW",
               features="F006|F020", envs="",
               note="G07 계열이 반복되는 패턴이라 추가했다. 5월 판단 자체(EP15)는 OBSERVED이고, 그 근거만 LATENT다."),
    "MB": dict(name="MB_CUSTODY_BIOLOGICAL_COURSE", short="구금·질병경과",
               easy="체포 뒤 구금 중 발병·사망 경과에 관한 구조(사망 branch A: 생물학적 사인)",
               key_gap="G06", branch="A_BIOLOGICAL",
               features="F002|F003|F004|F015|F016", envs="E001|E002|E003|E004",
               note="환경 피쳐는 질병·사망 설명의 호환성만 제약한다. 김명신 개인의 감염을 확정하지 않는다. 책임 branch(M1–M4)와 연결하지 않는다."),
}
ORDER = ["M1", "M2", "M3", "M4", "M5", "M6", "MB"]
OBSERVED_ANCHORED = {"M5"}

# ---------------------------------------------------------------------------- 후보 → 메커니즘 매핑
# (primary, secondary, core, negates)
#  core: 그 메커니즘의 중심 주장인가(아니면 주변·보조 주장인가)
#  negates: 이 후보의 주장이 부정하는 메커니즘(같은 gap에서 다른 메커니즘을 배제)
CAND_MAP = {
    "G01a": ("M1", "", True, ""), "G01b": ("M1", "", True, ""), "G01c": ("M1", "", True, ""),
    "G02a": ("M1", "", True, ""), "G02b": ("M4", "", True, "M1"), "G02c": ("M4", "", True, ""),
    "G03a": ("M1", "", True, ""), "G03b": ("M1", "", True, ""), "G03c": ("M4", "", True, ""),
    "G04a": ("M1", "", True, ""), "G04b": ("M2", "", True, ""), "G04c": ("M3", "", True, ""),
    "G04d": ("M2", "", True, ""), "G04e": ("M3", "", True, ""),
    "G05a": ("M3", "", False, ""), "G05b": ("M3", "", False, "M3"),
    "G06a": ("MB", "", True, ""), "G06b": ("MB", "", True, ""), "G06c": ("MB", "", True, ""),
    "G07a": ("M6", "", True, ""), "G07b": ("M2", "M6", False, ""), "G07c": ("M2", "M6", False, ""),
    "G07d": ("M6", "", True, ""),
    "G08a": ("M5", "", True, ""), "G08b": ("M5", "", True, ""),
    "G09a": ("M5", "", False, ""), "G09b": ("M5", "", False, ""), "G09c": ("M5", "", False, ""),
    "G10a": ("M5", "", False, ""), "G10b": ("M5", "", False, ""), "G10c": ("M5", "", False, ""),
    "G11a": ("M4", "", False, ""), "G11b": ("M1", "", False, ""), "G11c": ("M4", "", False, ""),
    "G12a": ("MB", "", False, ""), "G12b": ("MB", "", False, ""),
    "G13a": ("M5", "", False, ""), "G13b": ("M5", "", False, "M5"),
}
MAPPING_NOTES = {
    "G02b": "'상위 명령 없이' 출동을 지시했다는 주장이라 M1의 지휘 부분(G02a)을 부정한다.",
    "G05b": "서찰이 사건과 무관했다는 주장이라 M3이 그 지점에서 작동하지 않았다고 본다.",
    "G13b": "의금부 신문이 진행되지 않았다는 주장이라 M5 내부 세부(실행)를 부정한다. 재검토 backbone 자체는 OBSERVED라 영향이 없다.",
    "G01b": "소장의 병영 직접 접수는 공식 제출 경로라 M1로 분류했다. W3에서는 사적 통로(M3)와 함께 쓰인다.",
    "G07b": "회동 조사 응답자 진술의 채택. 진술이 판단 자료를 바꾸는 구조라 M2가 주이고 M6이 보조다.",
    "G07c": "진술 번복이 5월 자료에 들어감. M2가 주이고 M6이 보조다.",
}

# ---------------------------------------------------------------------------- 질적 구조 변수
# 각 변수는 관측 전이 하나(또는 latent 세부)를 설명하는 분석 변수다. inputs의 OR/AND는 질적 규칙이다.
STRUCT_VARS = [
    dict(var="V_COMPLAINT_TO_BARRACKS", gap="G01", target="EP04", op="OR",
         desc="소장·체포령(EP03)이 2/28 병영 출동(EP04)으로 이어지는 경로", inputs=["M1"],
         rule="V_COMPLAINT_TO_BARRACKS = M1_OFFICIAL_INFORMATION_ROUTE",
         constraint="F005·F006·F010(접수·이첩 경로의 제도 가능성)"),
    dict(var="V_COMMAND_SOURCE", gap="G02", target="EP04", op="XOR",
         desc="2/28 출동 지시의 상위 출처", inputs=["M1", "M4"],
         rule="V_COMMAND_SOURCE = M1_OFFICIAL_INFORMATION_ROUTE(G02a: 병사 지시) XOR M4_DISTRIBUTED_INSTITUTIONAL_ACTION(G02b: 비장 자체 판단)",
         constraint="F007·F008·F009(병사 → 비장·장교 지휘의 제도 가능성)"),
    dict(var="V_INFO_TO_COMMANDER", gap="G03|G04", target="EP09", op="OR",
         desc="구순 쪽 정보·진술이 3/4 병사의 체포 지시(EP09)에 닿는 경로", inputs=["M1", "M2", "M3", "M4"],
         rule="V_INFO_TO_COMMANDER = M1 OR M2 OR M3 OR M4  (각각 G04a·G03a·G03b / G04b·G04d / G04c / G03c)",
         constraint="F007·F020(구순은 명령 불가, 정보 제공만) · F008(보고 경로)"),
    dict(var="V_ARREST_PATH", gap="", target="EP11", op="AND",
         desc="체포 지시(EP09, OBSERVED) → 체포 실행(EP11, OBSERVED)", inputs=["V_INFO_TO_COMMANDER", "INSTITUTIONALLY_COMPATIBLE"],
         rule="V_ARREST_PATH = V_INFO_TO_COMMANDER AND INSTITUTIONALLY_COMPATIBLE(F007·F008: 병사 → 장교 명령)",
         constraint="F007·F008"),
    dict(var="V_INVESTIGATION_SCOPE", gap="G04|G11", target="EP11", op="OR",
         desc="수사 범위가 여러 혐의자로 넓어지는 구조(김갑득 동시 체포, 공주진 선행 체포 등)", inputs=["M2", "M4"],
         rule="V_INVESTIGATION_SCOPE = M2_TESTIMONY_AMPLIFICATION OR M4_DISTRIBUTED_INSTITUTIONAL_ACTION",
         constraint="F010(도적 수색 관할) · F002(진술 획득 방식의 규범)"),
    dict(var="V_INITIAL_JUDGMENT_BASIS", gap="G07", target="EP15", op="OR",
         desc="5/12 '도난 없음 방향' 판단(EP15, OBSERVED)의 근거 형성", inputs=["M6", "M2"],
         rule="V_INITIAL_JUDGMENT_BASIS = M6_INITIAL_JUDGMENT_BASIS OR M2_TESTIMONY_AMPLIFICATION(보조: G07b·G07c)",
         constraint="F006·F020(장계 → 국왕 판단)"),
    dict(var="V_REVIEW_CORRECTION", gap="G08|G13", target="EP25", op="ANCHORED",
         desc="5/12 판단 → 5/27 → 5/28 → 6/11 → 6/13 → 처분으로 이어진 독립 재검토·판단 수정(OBSERVED backbone)",
         inputs=["M5"],
         rule="V_REVIEW_CORRECTION = M5_REVIEW_AND_CORRECTION  (관측 backbone: EP15 →REVISES→ EP25 등. world마다 달라지지 않음)",
         constraint="F012·F013·F014·F017·F018"),
    dict(var="V_RESPONSIBILITY", gap="G09", target="EP29|EP30", op="AND",
         desc="정조의 책임 귀속(EP29·EP30, OBSERVED)", inputs=["V_REVIEW_CORRECTION", "V_ARREST_PATH"],
         rule="V_RESPONSIBILITY = V_REVIEW_CORRECTION AND V_ARREST_PATH  (책임 판단은 절차 branch B에만 의존, 사인과 무관)",
         constraint="F018"),
    dict(var="V_SANCTION", gap="G10", target="EP33|EP34|EP35|EP36|EP37", op="ANCHORED",
         desc="처분(OBSERVED, 모든 world 공통)", inputs=["V_RESPONSIBILITY"],
         rule="V_SANCTION = V_RESPONSIBILITY  (처분은 관측 사실. G10 사유는 OPEN_UNRESOLVED)",
         constraint="F001·F006·F018"),
    dict(var="V_CUSTODY_COURSE", gap="G06|G12", target="EP13", op="OR",
         desc="구금 중 발병·사망 경과(사망 branch A). 책임 branch와 연결하지 않음", inputs=["MB"],
         rule="V_CUSTODY_COURSE = MB_CUSTODY_BIOLOGICAL_COURSE  (환경 E001–E004는 호환성 context. 개인 감염 확정 아님)",
         constraint="F002·F003·F004·F015·F016 / E001–E004(context)"),
]

LEVEL = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "NONE": 0}
# 메커니즘이 '작동하지 않았다'고 주장하는 null 변형 후보. 구조 변수의 입력이 되지 않는다.
NULL_VARIANTS = {"G05b", "G11c", "G13b"}


def usable(c):
    """분석에 쓰는 후보: INCOMPATIBLE·대조용(contradiction HIGH)·null 변형 제외."""
    return c["overall"] != "INCOMPATIBLE" and c["contradiction_risk"] != "HIGH" and c["candidate_id"] not in NULL_VARIANTS


def world_config(w, cand):
    """world bridge 구성에서 메커니즘 값을 계산한다(손으로 넣지 않음).
    ON: 그 메커니즘의 핵심 gap(key_gap)을 core 후보로 채우고 부정 후보가 없음
    PARTIAL: 후보를 쓰지만 핵심 gap이 아니거나 보조 후보뿐이거나, 같은 world 안에 부정 후보가 함께 있음
    OFF: 그 메커니즘을 부정하는 후보만 있음
    UNSPECIFIED: 관련 후보가 없음(OFF가 아니다 — 작동했는지 말하지 않음)
    M5는 OBSERVED backbone에 고정되어 모든 world에서 ON이다."""
    bs = [cand[b] for b in w["latent_bridges"]]
    cfg, why = {}, {}
    for m in ORDER:
        if m in OBSERVED_ANCHORED:
            used = [c["candidate_id"] for c in bs if CAND_MAP[c["candidate_id"]][0] == m]
            cfg[m], why[m] = "ON", "관측 재검토 backbone(EP15–EP37)에 고정" + (f"; 내부 세부 {', '.join(used)}" if used else "")
            continue
        core = [c["candidate_id"] for c in bs if CAND_MAP[c["candidate_id"]][0] == m and CAND_MAP[c["candidate_id"]][2]]
        aux = [c["candidate_id"] for c in bs if (CAND_MAP[c["candidate_id"]][0] == m and not CAND_MAP[c["candidate_id"]][2])
               or CAND_MAP[c["candidate_id"]][1] == m]
        neg = [c["candidate_id"] for c in bs if CAND_MAP[c["candidate_id"]][3] == m]
        key = MECHANISMS[m]["key_gap"]
        core_key = [x for x in core if cand[x]["gap_id"] == key]
        if core_key and not neg:
            v = "ON"
        elif core or aux:
            v = "PARTIAL"
        elif neg:
            v = "OFF"
        else:
            v = "UNSPECIFIED"
        cfg[m] = v
        parts = []
        if core:
            parts.append("core " + ", ".join(core))
        if aux:
            parts.append("보조 " + ", ".join(aux))
        if neg:
            parts.append("부정 " + ", ".join(neg))
        why[m] = "; ".join(parts) or "관련 후보 없음"
    return cfg, why


def cooccur(cfg, a, b):
    """함께 작동하는 world: 한쪽은 ON, 다른 쪽은 ON 또는 PARTIAL. 둘 다 PARTIAL(보조 후보뿐)이면 세지 않는다."""
    act = ("ON", "PARTIAL")
    return cfg[a] in act and cfg[b] in act and "ON" in (cfg[a], cfg[b])


def interaction(a, b, cands, configs, conflict_pairs):
    """두 메커니즘의 공존 가능성. 후보·충돌 쌍·부정 관계·observed 고정만 근거로 쓴다(그럴 법함은 근거가 아님)."""
    if a in OBSERVED_ANCHORED or b in OBSERVED_ANCHORED:
        return ("COMPATIBLE", "M5는 관측 재검토 backbone에 고정되어 있어 다른 메커니즘과 함께 존재한다. 다른 메커니즘은 재검토 이전의 경로를 설명한다.",
                "", "초기 판단의 형성과 그 독립 재검토·수정이 한 흐름으로 설명된다", ["INDEPENDENT"])
    if "MB" in (a, b):
        return ("COMPATIBLE", "MB는 사망 branch A(생물학적 경과)다. 절차·책임 메커니즘과 연결되지 않으므로 함께 있어도 충돌하지 않는다.",
                "", "책임 경로와 사인 경로가 따로 설명된다(서로를 설명하지 않음)", ["INDEPENDENT"])
    cmap = {c["candidate_id"]: c for c in cands if usable(c)}
    A = [x for x in cmap if CAND_MAP[x][0] == a]
    B = [x for x in cmap if CAND_MAP[x][0] == b]
    conflicts = [f"{x}×{y}" for x, y, _ in conflict_pairs if (x in A and y in B) or (x in B and y in A)]
    neg = [f"{x}(→{CAND_MAP[x][3]} 부정)" for x in A + B if CAND_MAP[x][3] in (a, b) and CAND_MAP[x][0] != CAND_MAP[x][3]]
    same_gap = sorted({cmap[x]["gap_id"] for x in A} & {cmap[y]["gap_id"] for y in B})
    cooc = [w for w, cfg in configs.items() if cooccur(cfg, a, b)]
    rel = []
    if same_gap:
        rel.append("EXCLUSIVE_ALTERNATIVE" if neg else "SUBSTITUTE")
    if cooc:
        rel.append("COMPLEMENT")
    if not rel:
        rel.append("NO_SHARED_TRANSITION")
    bad = conflicts + neg
    if bad and cooc:
        status = "PARTIALLY_COMPATIBLE"
        reason = (f"일부 후보 쌍이 충돌하지만({'; '.join(bad)}), 다른 후보로는 {', '.join(cooc)}에서 함께 쓰인다.")
    elif bad:
        status = "PARTIALLY_COMPATIBLE"
        reason = f"충돌하는 후보 쌍({'; '.join(bad)})이 있으나 다른 후보 조합은 충돌하지 않는다."
    elif cooc:
        status = "COMPATIBLE"
        reason = f"충돌하는 후보·edge가 없고, {', '.join(cooc)}에서 함께 쓰인다."
    else:
        status = "COMPATIBLE"
        reason = "충돌하는 후보 쌍·부정 관계·제도 제약이 없다. 다만 어느 world도 둘을 함께 쓰지 않아, 함께 작동했는지는 사료로 결정되지 않는다(UNRESOLVED)."
    if same_gap:
        reason += f" 같은 전이({', '.join(same_gap)})를 서로 다른 방식으로 설명하는 후보가 있다."
    explains = {
        ("M1", "M2"): "공식 보고 경로로 들어온 정보에 대질 진술이 더해져 3/4 지시의 근거가 되는 경우(어느 world도 두 입력을 함께 쓰지 않음)",
        ("M1", "M3"): "공식 지휘·이관(G01·G02) 위에 사적 통로가 겹쳐 병사의 판단에 영향을 주는 경우(W3)",
        ("M1", "M4"): "소장 이관은 공식 경로로, 출동 지시는 비장의 자체 판단으로 이루어지는 경우(W2·W4). 병사 지시(G02a)와 비장 자체 판단(G02b)은 함께 쓸 수 없다",
        ("M2", "M3"): "진술 증폭과 사적 통로가 각각 3/4 지시의 입력이 되는 경우(어느 world도 함께 쓰지 않음)",
        ("M2", "M4"): "분산된 실무 안에서 대질 진술이 수사 범위를 넓히는 경우(W2·W4)",
        ("M3", "M4"): "분산된 실무와 사적 통로가 동시에 있는 경우(어느 world도 함께 쓰지 않음)",
        ("M2", "M6"): "5월 판단의 근거가 장물 부재 추론과 진술 자료(회동 응답·번복)로 함께 형성되는 경우",
        ("M1", "M6"): "공식 경로로 진행된 수사의 결과(장물 부재)가 5월 판단의 근거가 되는 경우(W1·W3·W5)",
        ("M3", "M6"): "사적 통로와 5월 판단 근거 형성은 서로 다른 단계를 설명한다(W3)",
        ("M4", "M6"): "분산 실무와 5월 판단 근거 형성은 서로 다른 단계를 설명한다(W4)",
    }.get((a, b), "")
    return status, reason, "; ".join(bad), explains, rel


def interventions(cands, configs):
    """질적 개입 do(M=OFF). 확률·효과크기 없이 경로가 남는지만 본다.
    Super-DAG 수준: 같은 구조 변수를 채우는 다른 메커니즘 후보가 남는가, 남은 후보의 bridge 근거가 제거된 쪽보다 약한가.
    World 수준: 그 world 안에서 해당 전이를 채우던 bridge가 사라지는가."""
    cmap = {c["candidate_id"]: c for c in cands if usable(c)}
    out = []
    targets = [v for v in STRUCT_VARS if v["op"] in ("OR", "XOR", "ANCHORED") and set(v["inputs"]) & set(ORDER)]
    for m in ORDER:
        for v in targets:
            if m not in v["inputs"]:
                continue
            gaps = set(v["gap"].split("|")) if v["gap"] else set()
            ins = [x for x in cmap if cmap[x]["gap_id"] in gaps and (CAND_MAP[x][0] in v["inputs"] or CAND_MAP[x][1] in v["inputs"])]
            removed = [x for x in ins if CAND_MAP[x][0] == m or (CAND_MAP[x][1] == m and CAND_MAP[x][0] not in v["inputs"])]
            remain = [x for x in ins if x not in removed]
            best = lambda xs: max((LEVEL[cmap[x]["source_support"]] for x in xs), default=-1)
            if m in OBSERVED_ANCHORED:
                res = "PATH_BREAKS"
                note = ("재검토 경로는 관측 backbone(EP15 →REVISES→ EP25, EP23 → 판단·처분)이다. M5를 끄면 관측된 판단 수정·처분 경로를 설명할 수 없다. "
                        "관측 사실과 양립하지 않으므로 M5는 사실상 OFF로 둘 수 없다.")
            elif not remain:
                res = "PATH_BREAKS"
                note = (f"이 전이를 채우는 후보가 {m}뿐이다({', '.join(removed) or '-'}). 관측 사건({v['target']}) 자체는 그대로지만, "
                        "그 앞의 설명 경로는 비게 된다(W5처럼 UNSPECIFIED).")
            elif best(remain) < best(removed):
                res = "PATH_WEAKENS"
                note = (f"다른 메커니즘 후보({', '.join(remain)})로 경로는 남지만, 남은 bridge 근거가 더 약하다 "
                        f"(제거 {max(cmap[x]['source_support'] for x in removed)} → 남은 최고 "
                        f"{[k for k, l in LEVEL.items() if l == best(remain)][0]}).")
            else:
                res = "PATH_REMAINS"
                note = f"다른 메커니즘 후보({', '.join(remain)})가 같은 전이를 채울 수 있고, bridge 근거도 같거나 더 강하다."
            if v["var"] == "V_COMMAND_SOURCE" and remain and not res == "PATH_BREAKS":
                note += " (XOR: G02a와 G02b는 서로 배타적이라 남은 쪽이 단독으로 설명한다.)"
            world_effect = {}
            for w, cfg in configs.items():
                if cfg[m] in ("ON", "PARTIAL") and m not in OBSERVED_ANCHORED:
                    world_effect[w] = "그 world의 해당 bridge가 사라짐"
            out.append(dict(mechanism=m, variable=v["var"], target=v["target"], result=res, note=note,
                            removed="|".join(removed), remaining="|".join(remain),
                            affected_worlds=", ".join(f"{w}" for w in world_effect) or "-"))
    return out


# ---------------------------------------------------------------------------- Super-DAG 조립
UNRESOLVED_ITEMS = [
    dict(uid="U_ID06", label="ID06 병영의 염탐 담당자 = 유제희?", affects=["G04a"], affects_observed="OE071(condition ID06)"),
    dict(uid="U_ID07", label="ID07 철편 네 개 = 철퇴 네 개?", affects=["G02a"], affects_observed="OE080(condition ID07)"),
    dict(uid="U_ID08", label="ID08 3/4 장교 일행에 조계완 포함?", affects=[], affects_observed="OE010(condition ID08)"),
    dict(uid="U_OE007", label="OE007 자미덕 '지휘' 주장 ↔ 한재욱 '은밀한 사주' 부인 (PARTIAL_CONFLICT)", affects=["G04b", "G09a"],
         affects_observed="OE007"),
    dict(uid="U_OE062", label="OE062 5월 '조사' = 정조 '평범한 신문'? (UNRESOLVED_SCOPE)", affects=["G06a", "G06b"],
         affects_observed="OE062"),
    dict(uid="U_G10", label="G10 이형원 파직 → 유임 이유 (OPEN_UNRESOLVED)", affects=["G10a", "G10b", "G10c"], affects_observed="EP36→EP37"),
]
BRANCH_B = {"M1", "M2", "M3", "M4", "V_INFO_TO_COMMANDER", "V_ARREST_PATH", "V_RESPONSIBILITY", "V_COMMAND_SOURCE",
            "V_COMPLAINT_TO_BARRACKS", "V_INVESTIGATION_SCOPE", "EP29", "EP30"}
BRANCH_A = {"MB", "V_CUSTODY_COURSE", "EP26", "EP27"}


def build(nodes, edges, cands, worlds, inst_rows, env_rows, frozen_hash):
    cand = {c["candidate_id"]: c for c in cands}
    comp = [w for w in worlds if w["role_type"] == "COMPETING_EXPLANATION"]
    configs, whys = {}, {}
    for w in worlds:
        configs[w["world_id"]], whys[w["world_id"]] = world_config(w, cand)
    # ----- nodes
    sdn = []
    for n in nodes:
        env = n["layer"] == "ENVIRONMENT"
        sdn.append(dict(node_id=n["node_id"], sd_status="CONTEXT" if env else "OBSERVED",
                        node_type="ENV_CONTEXT" if env else "OBSERVED_EVENT", label=n["title"], frozen_status=n["node_status"],
                        branch=("A_BIOLOGICAL" if n["node_id"] in {"EP26", "EP27"} else ""), mechanism="", worlds="ALL (공통)",
                        detail=n["summary"]))
    for r in inst_rows:
        sdn.append(dict(node_id="CTX_" + r["feature_id"], sd_status="CONTEXT", node_type="INSTITUTIONAL_CONTEXT",
                        label=f"{r['feature_id']} {r['feature_name']}", frozen_status="", branch="", mechanism="",
                        worlds="ALL (제약조건)", detail=r["operational_definition"]))
    for m in ORDER:
        d = MECHANISMS[m]
        sdn.append(dict(node_id=m, sd_status="LATENT_MECHANISM", node_type="MECHANISM", label=d["name"], frozen_status="",
                        branch=d["branch"], mechanism=m, worlds="config별", detail=d["easy"]))
    for v in STRUCT_VARS:
        sdn.append(dict(node_id=v["var"], sd_status="LATENT_MECHANISM", node_type="STRUCTURAL_VARIABLE", label=v["var"],
                        frozen_status="", branch=("A_BIOLOGICAL" if v["var"] == "V_CUSTODY_COURSE" else
                                                  "REVIEW" if v["op"] == "ANCHORED" else "B_PROCEDURAL"),
                        mechanism="", worlds="config별", detail=v["rule"]))
    for c in cands:
        used = [w["world_id"] for w in worlds if c["candidate_id"] in w["latent_bridges"]]
        p, sec, core, neg = CAND_MAP[c["candidate_id"]]
        sdn.append(dict(node_id=c["candidate_id"], sd_status="LATENT_MECHANISM", node_type="CANDIDATE_BRIDGE",
                        label=c["label"], frozen_status="", branch=MECHANISMS[p]["branch"], mechanism=p,
                        worlds=", ".join(used) or "(world 미사용)",
                        detail=f"[LATENT] {c['latent_bridge_claim']} · evidence {c['source_support']} · final {c['overall']}"
                               + ("" if usable(c) else " · 분석 제외(INCOMPATIBLE 또는 대조용)")))
    for u in UNRESOLVED_ITEMS:
        sdn.append(dict(node_id=u["uid"], sd_status="UNRESOLVED", node_type="UNRESOLVED_ITEM", label=u["label"], frozen_status="",
                        branch="", mechanism="", worlds="ALL (확정하지 않음)", detail=u["affects_observed"]))
    # ----- edges
    sde = []
    for e in edges:
        sde.append(dict(edge_id=e["edge_id"], src=e["src"], dst=e["dst"], edge_type=e["edge_type"], sd_status=e["status"],
                        origin="FROZEN", note=e["rationale"]))
    k = 0

    def add(src, dst, etype, status, note):
        nonlocal k
        k += 1
        sde.append(dict(edge_id=f"SD{k:03d}", src=src, dst=dst, edge_type=etype, sd_status=status, origin="SUPER_DAG", note=note))
    for m in ORDER:
        for f in MECHANISMS[m]["features"].split("|"):
            add("CTX_" + f, m, "CONSTRAINS", "CONTEXT", "제도상 가능성·관할·역할 적합성만 제약한다(사건 생성 아님)")
        for e in filter(None, MECHANISMS[m]["envs"].split("|")):
            envnode = {"E001": "ENV01", "E002": "ENV02", "E003": "ENV03", "E004": "ENV04"}[e]
            add(envnode, m, "CONTEXT_COMPATIBLE", "CONTEXT", "질병·사망 설명의 환경적 호환성만(개인 감염 확정 아님)")
    for f in ("F007", "F008"):
        add("CTX_" + f, "V_ARREST_PATH", "CONSTRAINS", "CONTEXT", "병사 → 장교 체포 명령의 제도 적합성(INSTITUTIONALLY_COMPATIBLE)")
    for c in cands:
        p, sec, core, neg = CAND_MAP[c["candidate_id"]]
        add(p, c["candidate_id"], "INSTANTIATED_BY", "LATENT_MECHANISM", "core" if core else "보조")
        if sec:
            add(sec, c["candidate_id"], "INSTANTIATED_BY_SECONDARY", "LATENT_MECHANISM", "보조 메커니즘")
        if not usable(c):
            continue
        for v in STRUCT_VARS:
            gaps = set(v["gap"].split("|")) if v["gap"] else set()
            if c["gap_id"] in gaps and (p in v["inputs"] or sec in v["inputs"]):
                add(c["candidate_id"], v["var"], "CONTRIBUTES_TO", "LATENT_MECHANISM", "질적 규칙 입력")
    add("M5", "V_REVIEW_CORRECTION", "ANCHORED_TO", "LATENT_MECHANISM", "M5는 관측 재검토 backbone에 고정")
    for t in ("EP18", "EP20", "EP22", "EP23", "EP25"):
        add("V_REVIEW_CORRECTION", t, "EXPLAINS_OBSERVED", "LATENT_MECHANISM", "관측 재검토 사건을 설명(사건 자체는 OBSERVED 그대로)")
    for v in STRUCT_VARS:
        if v["var"] in ("V_REVIEW_CORRECTION",):
            continue
        for t in v["target"].split("|"):
            add(v["var"], t, "EXPLAINS_TRANSITION_TO", "LATENT_MECHANISM", v["desc"])
    for a, b in [("V_INFO_TO_COMMANDER", "V_ARREST_PATH"), ("V_ARREST_PATH", "V_RESPONSIBILITY"),
                 ("V_REVIEW_CORRECTION", "V_RESPONSIBILITY"), ("V_RESPONSIBILITY", "V_SANCTION"),
                 ("V_COMPLAINT_TO_BARRACKS", "V_COMMAND_SOURCE"), ("V_COMMAND_SOURCE", "V_INFO_TO_COMMANDER")]:
        add(a, b, "RULE_INPUT", "LATENT_MECHANISM", "질적 구조 규칙의 입력")
    for u in UNRESOLVED_ITEMS:
        for x in u["affects"]:
            add(u["uid"], x, "CONDITIONS", "UNRESOLVED", "확정하지 않은 동일성·범위·사유. 이 후보의 성립 조건으로만 남는다")
    # ----- interactions (경쟁 설명 world만 사용, W6 제외)
    comp_cfg = {w["world_id"]: configs[w["world_id"]] for w in comp}
    from stage5_worlds import CONFLICT_PAIRS
    inter = []
    for i, a in enumerate(ORDER):
        for b in ORDER[i + 1:]:
            st, reason, bad, expl, rel = interaction(a, b, cands, comp_cfg, CONFLICT_PAIRS)
            inter.append(dict(mechanism_a=MECHANISMS[a]["name"], mechanism_b=MECHANISMS[b]["name"], a=a, b=b, coexistence=st,
                              reason=reason, conflicting=bad, explains_together=expl, relation="|".join(rel),
                              cooccur_worlds=", ".join(w for w, cfg in comp_cfg.items() if cooccur(cfg, a, b))))
    lv = {"COMPATIBLE": 3, "PARTIALLY_COMPATIBLE": 2, "UNKNOWN": 1, "INCOMPATIBLE": 0}
    pair = {(x["a"], x["b"]): x for x in inter}
    tri = []
    for combo, why in [(("M1", "M2", "M4"), "W2·W4처럼 공식 이관 + 진술 증폭 + 분산 실무가 함께 있는 구조"),
                       (("M1", "M2", "M3"), "정보가 3/4 지시에 닿는 세 경로(공식·진술·사적)를 모두 입력으로 두는 구조(어느 world도 쓰지 않음)"),
                       (("M1", "M3", "M5"), "W3처럼 공식 지휘 + 사적 통로 위에 관측 재검토가 이어지는 구조"),
                       (("M2", "M4", "M6"), "W4처럼 분산 실무와 진술 자료가 5월 판단 근거 형성까지 이어지는 구조")]:
        ps = [pair.get((x, y)) or pair.get((y, x)) for x, y in [(combo[0], combo[1]), (combo[0], combo[2]), (combo[1], combo[2])]]
        worst = min(ps, key=lambda p: lv[p["coexistence"]])["coexistence"]
        cooc = [w for w, cfg in comp_cfg.items() if all(cfg[m] in ("ON", "PARTIAL") for m in combo)]
        tri.append(dict(combo=" × ".join(combo), coexistence=worst, why=why, cooccur_worlds=", ".join(cooc) or "없음",
                        conflicts="; ".join(p["conflicting"] for p in ps if p["conflicting"]) or "-"))
    inv = interventions(cands, comp_cfg)
    return dict(nodes=sdn, edges=sde, configs=configs, whys=whys, interactions=inter, triples=tri, interventions=inv,
                frozen_hash=frozen_hash)
