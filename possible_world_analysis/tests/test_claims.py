"""주장 레지스트리: 출처 연결·주장 유형·후대 자료 소급 금지."""
import re

TYPES = {"직접 사실", "학술적 해석", "추론", "극중 창작"}
STATUS = {"원문 확인", "간접 확인", "미확인", "사료 간 충돌"}
FIELDS = ["claim_id", "claim", "source_id", "source_locator", "original_text", "translation", "claim_type",
          "verification_status", "event_date", "source_date", "url", "related_variables"]


def test_fields_and_vocab(claims):
    ids = set()
    for c in claims:
        for f in FIELDS:
            assert f in c
        assert c["claim_id"] not in ids
        ids.add(c["claim_id"])
        assert c["claim_type"] in TYPES, c["claim_id"]
        assert c["verification_status"] in STATUS, c["claim_id"]


def test_source_ids_exist(claims, sources):
    for c in claims:
        if c["source_id"]:
            assert c["source_id"] in sources, f"{c['claim_id']}: 없는 출처 {c['source_id']}"


def test_direct_historical_claims_have_source(claims, sources):
    for c in claims:
        if c["claim_type"] == "직접 사실" and c["verification_status"] in ("원문 확인", "간접 확인", "사료 간 충돌"):
            assert c["source_id"], f"{c['claim_id']}: 역사적 직접 주장에 근거 ID 없음"
            assert sources[c["source_id"]]["category"] != "internal" or c["claim_id"].startswith("CL-OFF"), c["claim_id"]


def test_empty_url_explained(claims):
    for c in claims:
        if not c["url"]:
            assert "URL 비어 있음" in c["provenance_note"] or c["source_id"] in ("GYDJ_POPHYEOM",), c["claim_id"]


def test_original_and_translation_separate(claims):
    for c in claims:
        if c["original_text"] and re.search(r"[一-鿿]", c["original_text"]):
            assert c["translation"] and c["translation"] != c["original_text"], c["claim_id"]
            assert not re.search(r"[一-鿿]{3,}", c["translation"].split("[")[0]), f"{c['claim_id']}: 번역란에 원문이 섞임"


def test_original_verified_only_for_film_text(claims, sources):
    """이번 실행에서 원문 DB를 못 열었으므로 '원문 확인'은 시놉시스 텍스트(극중 창작)에만 허용."""
    for c in claims:
        if c["verification_status"] == "원문 확인":
            assert c["claim_type"] == "극중 창작" and c["source_id"] == "SIGOK_PDF", c["claim_id"]


def test_film_claims_not_labeled_fact(claims):
    for c in claims:
        if c["claim_id"].startswith("CL-FILM"):
            assert c["claim_type"] == "극중 창작", c["claim_id"]


def test_event_date_and_source_date_distinct_fields(claims):
    for c in claims:
        if c["claim_type"] == "직접 사실" and c["source_id"] in ("SIM", "SIL1783", "CHUG"):
            assert c["source_date"] == "확인 필요", f"{c['claim_id']}: 편찬 시기를 사건 날짜로 채움"
