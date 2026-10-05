# GuSoon-Inference

1793년(정조 17) 구순·김명신 사건 사료 데이터와 분석 파이프라인.

## v1 pipeline deprecated.

> **경고:** v1 결과물(events, attestations, event_relations, event_families,
> same-event 후보, partial DAG, UNKNOWN interface 후보, audit·repair 결과,
> source recheck queue, schema 제안)은 **역사적 근거로 사용하지 않는다.**
> v1 ID(`ATxxxx`, `ATTxxxx`, `RELxxxx`, `Fxxx`)는 v2에서 어떤 근거로도 쓰지 않으며,
> v1 row·relation·audit 판단을 v2 데이터에 복사하거나 덮어쓰지 않는다.
> v1 파일은 git 이력에만 남아 있다.

### 왜 v1을 폐기했는가

v1은 사료 진술을 처음부터 "event"로 묶은 뒤 attestation·relation을 붙이는 구조였다.
그 결과 증언·관찰사 보고·어사 주장·국왕 판정이 같은 수준의 사실처럼 섞였고,
audit에서 드러난 문제(사건/증언 분리 실패, 명단 provenance 불명확, relation 과잉 해석 등)는
파생 테이블을 고치는 것만으로는 해결되지 않았다.

### 왜 v2는 source-faithful proposition부터 시작하는가

v2의 기본 단위는 "어떤 사료가, 누가, 무엇을 말하거나 보고하거나 판단했다고 기록하는가"를
최소 명제로 보존한 proposition(`Pxxxx`)이다. proposition은 **실제 발생한 event 목록이 아니다.**
`TESTIMONY`, `OFFICIAL_REPORT`, `INSPECTOR_CLAIM`, `ROYAL_JUDGMENT` 등은
`attestation_mode`·`epistemic_scope`로 구분된 채 남으며, 자동으로 같은 수준의 사실로 취급하지 않는다.

## v2 기준 데이터 (`data/raw/`)

| 파일 | 역할 |
|---|---|
| `gusun_research_v2_source_records.csv` | 사료 단위 기록(`SRC2_xxx`): 서명, 기사 날짜, URL, 사료 등급 |
| `gusun_research_v2_source_faithful_propositions.csv` | **중심 테이블.** 사료별 최소 명제(`Pxxxx`) |
| `gusun_research_v2_person_membership.csv` | 인물별 명단 포함·대질·체포·구금·신문 여부와 근거 등급 |
| `gusun_research_v2_search_log.csv` | 검색어·검색 사이트·결과 상태 기록 (음성 결과 포함) |

원본 SHA-256: `data/raw/gusun_research_v2_SHA256SUMS.txt`.

## 현재 상태

- `scripts/v2_01_initial_validation.py`: 네 CSV를 `database/gusun_v2.duckdb`에 적재하고
  ID 중복·참조·행 수·핵심 필드·vocabulary·핵심 사례 존재 여부만 검사한다.
  결과는 `output/01~04_v2_*.csv`, `logs/v2_initial_validation.log`.
- **event reconstruction은 아직 시작하지 않았다.** event·attestation·relation·same-event
  후보·Episode·DAG·UNKNOWN interface·latent event·posterior 추론은 만들지 않았다.

```
pip install duckdb
python3 scripts/v2_01_initial_validation.py
```
