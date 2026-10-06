# 00 · Preflight Report — `gusun_clean_restart_csv_pack/` 실측 보고

구현 전에 입력 pack을 전부 읽고 정리한 결과다. 이후 Stage 1–5는 이 보고서의 규칙을 따른다.

## 1. 파일별 행 수 (헤더 제외)

| 파일 | 행 | 역할 | DAG 입력 |
|---|---|---|---|
| 00_INPUT_MANIFEST.csv | 5 | 파일 역할·금지 규칙 | – |
| 01_confirmed_facts.csv | 50 (CF001–CF050) | 주 입력 | YES |
| 02_institutional_normative_features.csv | 20 (F001–F020) | 제도 compatibility layer | YES (평가만) |
| 03_environment_1793.csv | 4 (E001–E004) | 외생 context | YES (CONTEXT_SUPPORTS만) |
| 04_source_records.csv | 8 (SRC3_001–SRC3_008) | provenance | NO |
| 05_source_faithful_propositions_AUDIT_ONLY.csv | 156 (V3P0001–V3P0156) | 충실도 audit | NO |

## 2. 핵심 컬럼

- **01**: `fact_id`, `chronology`, `occurrence_lunar_text`, `record_lunar_date`, `confirmation_level`(13종; RECORDED_TESTIMONY 22건), `subject`, **`confirmed_statement`**(의미 단위), `underlying_claim_status`, `source_record_id`, `source_prop_ids`(파이프 구분), `notes`(동일성·열린 목록 경고 포함)
- **02**: `feature_id`, `feature_group`, `feature_name`, `operational_definition`, `model_role`(hard gate / affordance / review affordance), `valid_from–valid_to`
- **03**: `env_id`, `lunar_date`, `region_scope`, `attested_context`, `feature_name`, `model_role`, `notes`(“개인 감염 증명 아님”)
- **04**: `source_record_id`, `source_work`, `record_lunar_date`, `source_title`, `source_tier`, `case_role`
- **05**: `prop_id`, `reporting_actor`, `attestation_mode`, `subject/predicate/object_or_content`, `epistemic_scope`, `claim_topic`, `conflict_group`, `set_status`(OPEN_SET 등)

## 3. 파일 간 참조 관계

```
01.source_record_id ──► 04.source_record_id      (50/50 유효)
01.source_prop_ids  ──► 05.prop_id (N:M)         (73개 prop 참조, 83개 prop은 CF에 미반영)
05.source_record_id ──► 04.source_record_id
02, 03              ── FK 없음 (이 작업에서 node/edge에 평가 링크로만 연결)
```
- CF가 참조하지 않는 prop 83개(SRC3_006 40, SRC3_002 17, SRC3_001 13, SRC3_005 5 …)는 **DAG 노드로 올리지 않는다**. Audit 1에서 “confirmed set 밖의 사료 내용”으로 목록만 보고하고, Stage 4에서 latent 후보의 `audit_attestation`(사료 내 언급 존재 표시)으로만 인용한다. 그래도 후보 상태는 LATENT로 유지한다.
- SRC3_007(윤노동 파직)은 CF에서 참조하지 않는다. SRC3_008은 CF050만 참조한다.

## 4. 대략적인 시간축 (음력 1793)

| 시점 | 내용 (인식 수준) |
|---|---|
| 1/22 | E001 호서 전염병, E002 구휼 (환경) |
| 2월 초순 이전~이후 | 친숙·왕래 → 박거사 일 힐책 → 왕래 단절 (명업 진술) |
| 2/22 밤 | 도적 전언: 30여 명·횃불·지세대감 (명업이 전한 나복 발언, 중첩 진술) |
| 신고 이후 | 구순 소장 → 체포령 (명업 진술) |
| 2/28 밤 | 비장청 호출, 한재욱의 덕평 출동·변지돌/정원돌 체포 지시, 철편 4개 (이진욱 진술) |
| 2/29 | 변지돌은 이미 공주진에 잡혀감, 자미덕 체포 (이진욱) → 압송·신문·구류·회유·대질 (자미덕) |
| (날짜 없음) | 유제희의 현지 탐문, “풍각 김상제도 극히 수상” 기록 (유제희) |
| 3/4 | 병사의 풍각·흥덕 김생원 체포 지시 → 조계완의 구순 집 방문·서찰 → 김명신·김갑득 체포 |
| 4/10 | E003 호서·영남 전염병 지속 (환경) |
| 5/12 | 이형원 장계(구금 달포 이상, 장물 없음, 사망, 혹형), 정조 1차 판단(도난 없음 방향), 구순 의금부; E004 옥수 치료 정책 |
| 5/27 | 이조원 보고(도난 없음 방향) → 정조 비판·파직; 구순 의금부 반복 신문 |
| 5/28 | 홍대협 공주 안핵어사 차하 |
| 6/11 | 윤노동 별단(구금 중 병사, 혹형, 장물 없음) → 비변사 보류, 윤허 |
| 6/13 | 홍대협 복명(공초 전체 수록), 도난 일부 실재·좀도둑 수준, 질병 사망 / 정조 최종 판단(도난 실재, 부처 전염병 사망, 곤장·평문 없음, 직접 인과 불확실, 구순·이광섭 책임) / 처분 4건 |
| 6/16 | 이형원 유임 |

주의: SRC3_006 공초에 담긴 사건 시점은 **진술 내용 속 시점**이다. 진술 행위 자체는 홍대협 안핵(5/28–6/13) 중에 있었다. 두 시간을 따로 기록한다.

## 5. 제안 episode grouping (요약)

- 관계: [구순–김명신 관계 변화] CF001–003
- 도난: [2/22 도적 전언] CF004–005, [소장과 체포령] CF006
- 병영 2월: [2/28 출동 준비] CF007–010, [2/29 덕평 체포] CF011–012, [자미덕 압송·신문·구류] CF013–015, [한 비장의 석방 조건·대질 거짓 진술] CF016–017
- 탐문: [유제희 현지 탐문 기록] CF020
- 3/4: [병사 체포 지시 + 김생원 식별] CF021–022, [조계완의 구순 집 방문·서찰] CF024, [김명신·김갑득 체포] CF023
- 공초 반론: [한재욱 안핵 공초] CF018–019
- 5/12: [이형원 장계 보고] CF027–028, [이형원 지휘 책임 평가] CF025–026, [정조 1차 판단] CF030, [정조 의금부 명] CF031
- 5/27–28: [이조원 보고] CF032, [정조의 이조원 비판·파직] CF033, [의금부 반복 신문 명] CF034, [홍대협 차하] CF035
- 6/11: [윤노동 별단] CF029, [비변사 보류] CF036
- 6/13: [안핵 복명] CF037, [홍대협 도난 판단] CF038, [정조 도난 판단] CF039, [홍대협 사인 평가] CF040-①, [정조 사인·처우 판단] CF040-②+CF041, [직접 인과 불확실] CF042, [구순 책임] CF043, [이광섭 책임] CF044, [홍대협 지세 미확정] CF045-①, [정조 지세 날조 불인정] CF045-②, 처분 4건 CF046/047/048/049
- 6/16: [이형원 유임] CF050

CF040과 CF045는 **홍대협(official) ↔ 정조(royal)** 경계에서만 절(clause)로 나눈다. 판단 주체가 다르면 분리하라는 규칙 때문이고, 각 절은 원문 substring 그대로 보존한다.

## 6. 예상 node 수

- episode node 37개 (CF 50 → 37) + environment context node 4개 = 41개
- 제도 피쳐(F001–F020)는 node가 아니라 `node_feature_links.csv`의 평가 링크로만 붙인다.

## 7. Edge 생성 규칙

1. 모든 edge에 `basis`(SOURCE_DIRECT / TEMPORAL / PROCEDURAL / INFORMATION_FLOW / INSTITUTIONAL_COMPATIBILITY / ENVIRONMENTAL_CONTEXT)와 `status`(OBSERVED / DERIVED)를 붙인다.
2. `CAUSES`는 쓰지 않는다. 정조가 명시한 책임 귀속은 `RESPONSIBILITY_LINK`(판단 수준)로 표현한다.
3. 진술 내용끼리의 시간 순서는 `claim_level=TRUE`로 표시한다.
4. 명령과 실행은 분리한다. `ORDER_TO_ACTION`은 사료가 “분부에 따라” 같은 연결을 명시했거나, 같은 진술 흐름에서 실행이 확인될 때만 쓴다.
5. 판단 변화는 `REVIEW_OF`(후속 판단이 앞 판단·보고를 검토), `REVISES`(같은 주체의 판단 번복), `CONTRADICTS_AT_CLAIM_LEVEL`(주장끼리의 충돌)로 남긴다.
6. 미확정 동일성에 기대는 edge는 `condition` 컬럼에 identity id를 적는다. 동일성 자체는 확정하지 않는다.
7. INSTITUTIONAL_COMPATIBILITY나 ENVIRONMENTAL_CONTEXT 하나만으로는 사건 사이 edge를 만들지 않는다.

## 8. Institutional feature 적용 방식

- node/edge 단위로 `legal_available / jurisdictionally_possible / role_compatible / procedure_available / review_available / information_flow_compatible`를 COMPATIBLE · COMPATIBLE_WITH_CAVEAT · LOW · UNDETERMINED로 평가한다.
- `creates_event=NO`로 고정한다. 평가는 “제도상 가능했는가”이지 “그렇게 했을 확률”이 아니다.
- 예: 3/4 병사→장교 체포 지시는 F007·F008에 따라 role_compatible=COMPATIBLE. 구순(전 부사)→병사 서찰은 공식 지휘 경로가 아니므로 공식 명령으로서는 LOW이고, 사적 정보 흐름으로서는 UNDETERMINED.

## 9. Environment feature 적용 방식

- E001–E004는 context node로만 쓰고, `CONTEXT_SUPPORTS` edge는 **판단 node**(홍대협 질병 평가, 정조 전염병 판단, 윤노동 병사 보고)로만 연결한다.
- 김명신 개인의 감염·발병을 사건 node로 만들지 않는다. E004(5/12 정책)는 사망 이후 날짜이므로 사망에 영향을 준 것처럼 연결하지 않는다.

## 10. 예상 주요 gap

G01 소장 접수 기관 → 체포령 → 병영 출동 / G02 2/28 출동 명령의 상위 출처 / G03 유제희 탐문의 시점·파견자·보고 수신자 / G04 구순 발언·성명 → 3/4 병사 체포 지시까지의 정보 경로 (핵심) / G05 3/4 구순 서찰의 전달·내용 / G06 3/4 체포~사망 사이 구금 경과 / G07 5월 ‘도난 없음’ 판단이 형성된 경로 / G08 이조원 비판 → 홍대협 차하의 동기 / G09 처분문 ‘한가’의 처분 근거와 동일성 / G10 이형원 파직 → 3일 뒤 유임 / G11 변지돌 공주진 체포 경위

## 11. 예상 왜곡 위험

- “극히 수상하다” → “범인 지목”, “거짓으로 꾸며 말했다” → “거짓 지목”으로 강해지는 것
- “은밀히 사주한 일 없음” → “어떤 사주도 없음”으로 범위가 넓어지는 것
- “등”이 붙은 명단을 닫힌 목록으로 취급하는 것
- 병사=이광섭, 한 비장=한재욱, 한가=한재욱, 하급 보조자=한재욱, 풍각 김상제=김명신, 염탐 담당자=유제희를 확정하는 것
- 정조 판단(CF043)의 “구순이 성명을 적어 주었다”와 유제희 진술의 “구순이 말했고 유제희가 기록했다”를 하나로 합치는 것
- 중첩 진술(30여 명·횃불·지세대감)을 객관 사실로 올리는 것
- 5월 판단(도난 없음)을 최종 판단에 덮어써 지우는 것
- 전염병 환경을 김명신 개인 감염의 원인으로 연결하는 것
- 구순 → 김명신 사망을 직접 causal edge 하나로 합치는 것
- 철편(이진욱: 한재욱이 만들어 줌)과 철퇴(정조: 이광섭이 만들게 함)를 행위자까지 같은 것으로 합치는 것
