"""§17: 출처 ID·APA 필수 필드·URL 상태 vs 원문 검증 구분."""
import re

CATS = {"primary", "scholarship", "theory_institutional", "internal"}
URL_STATUS = {"OK", "AUTH_REQUIRED", "NOT_FOUND", "NETWORK_BLOCKED", "ERROR", "NO_URL", "NOT_CHECKED"}
TEXT_VER = {"ORIGINAL_VERIFIED", "INDIRECT_TRANSCRIPTION", "SECONDARY_SUMMARY", "BIBLIOGRAPHIC_ONLY", "NOT_VERIFIED", "URL_ONLY"}
REQUIRED = ["source_id", "category", "short", "apa", "title", "url", "event_date", "source_date", "missing_fields",
            "text_verification", "url_check"]


def test_required_fields_and_vocab(sources):
    for sid, s in sources.items():
        for k in REQUIRED:
            assert k in s, f"{sid}: APA/서지 필수 필드 누락 {k}"
        assert s["category"] in CATS
        assert s["text_verification"] in TEXT_VER
        assert s["url_check"]["status"] in URL_STATUS, sid
        assert "{title_link}" in s["apa"] or "{title}" in s["apa"], f"{sid}: APA에 제목 자리 없음"


def test_empty_url_has_reason(sources):
    for sid, s in sources.items():
        if not s["url"]:
            assert s.get("url_missing_reason"), f"{sid}: 원문 링크가 비었는데 이유가 없음"
            assert "URL" in s["missing_fields"], f"{sid}: URL 누락이 missing_fields에 표시되지 않음"


def test_unknown_dates_not_invented(sources):
    """편찬연도를 모르면 '확인 필요'로 두고 missing_fields에 적는다."""
    for sid, s in sources.items():
        if "확인 필요" in str(s["source_date"]) and s["category"] == "primary":
            assert any("편찬" in m for m in s["missing_fields"]), sid


def test_url_failure_not_treated_as_absence(sources):
    """URL이 열리지 않은 출처를 '원문 직접 확인'으로 표시하거나 삭제하지 않는다."""
    for sid, s in sources.items():
        st = s["url_check"]["status"]
        if s["category"] != "internal" and st != "OK":
            assert s["text_verification"] != "ORIGINAL_VERIFIED", f"{sid}: 접속 실패인데 원문 확인으로 표시"
        if st in ("NETWORK_BLOCKED", "ERROR", "NOT_FOUND"):
            assert s["title"] and s["apa"], f"{sid}: 접속 실패를 자료 부재로 처리"


def test_lunar_dates_marked(sources):
    for sid, s in sources.items():
        if s["category"] == "primary" and re.search(r"\(\d{4}년 음력", s["apa"]) is None and "(n.d.)" not in s["apa"] \
                and "편찬 시기 확인 필요)" not in s["apa"] and "(1789)" not in s["apa"] and "(18세기" not in s["apa"]:
            raise AssertionError(f"{sid}: 고문헌 날짜에 음력 표시가 없음")


def test_link_check_matches_sources(sources, results):
    lc = results["link_check"]["results"]
    assert set(lc) == set(sources), "link_check.json과 sources.yaml의 출처 ID가 다름"
    for sid, r in lc.items():
        assert r["status"] == sources[sid]["url_check"]["status"], sid


def test_no_wiki_sources(sources):
    for sid, s in sources.items():
        for u in [s["url"]] + s.get("alt_urls", []):
            assert not re.search(r"wikipedia|namu\.wiki|wiki", u or "", re.I), f"{sid}: 위키 계열 자료"
