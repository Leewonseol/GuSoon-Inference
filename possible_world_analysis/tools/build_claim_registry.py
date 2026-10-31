#!/usr/bin/env python3
"""01_claim_registry.csv 생성기. 주장 데이터는 이 파일에만 있고 CSV는 산출물이다.

번역 열의 한문 직역은 작성자(분석 시스템)의 직역이며 국사편찬위원회 국역본과 대조하지 않았다.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["claim_id", "claim", "source_id", "source_locator", "original_text", "translation",
          "claim_type", "verification_status", "event_date", "source_date", "url",
          "related_variables", "evidence_role", "provenance_note"]

SIM_URL = "https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_420_0020_0120_0040"
SIL_URL = "https://sillok.history.go.kr/id/kva_10706003_004"
CHUG_URL = "https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_200r_0020_0020_0050_0080_0080"
PDF = "SIGOK_PDF"
TR = "작성자 직역(국역본 미대조)"
DS = "사용자 Drive 데이터셋(CORE_EVENTS/CORE_CASE_CLAIMS) 전사 구절. 원문 DB 대조 실패(네트워크 차단)"

C = []
def add(**kw):
    row = {k: "" for k in FIELDS}
    row.update(kw)
    C.append(row)

# ── 《심리록》 ──
add(claim_id="CL-SIM-01", claim="《심리록》은 조재항 옥사가 경자년(1780) 음력 6월에 성립했다고 기록한다.",
    source_id="SIM", source_locator="〈백천 조재항옥〉 기사 첫머리(정확한 행 미확인)", original_text="庚子六月成獄",
    translation=f"경자년 6월에 옥사가 성립하였다. [{TR}]", claim_type="직접 사실", verification_status="사료 간 충돌",
    event_date="1780 L6", source_date="확인 필요", url=SIM_URL, related_variables="T16",
    evidence_role="direct", provenance_note=DS + "; CL-SIL-01과 충돌")
add(claim_id="CL-SIM-02", claim="옥사의 혐의 내용은 조재항이 '밥 한 사발' 때문에 아내 윤씨를 때리고 찼다는 것이다(고발·옥안상의 혐의이며 사실 인정 아님).",
    source_id="SIM", source_locator="〈백천 조재항옥〉 혐의 서술부", original_text="因一盂飯 毆踢其妻尹女",
    translation=f"밥 한 사발로 인하여 그 아내 윤녀를 때리고 찼다(는 것). [{TR}]", claim_type="직접 사실",
    verification_status="간접 확인", event_date="1780 L6 이전(혐의 대상 행위 시점 미상)", source_date="확인 필요",
    url=SIM_URL, related_variables="J3;M14;F1;F2", evidence_role="direct", provenance_note=DS)
add(claim_id="CL-SIM-03", claim="《심리록》은 신축년(1781) 8월에 형조 심리·판부가 있었다고 기록한다.",
    source_id="SIM", source_locator="〈백천 조재항옥〉 신축 8월 조", original_text="辛丑八月",
    translation=f"신축년 8월. [{TR}]", claim_type="직접 사실", verification_status="간접 확인",
    event_date="1781 L8", source_date="확인 필요", url=SIM_URL, related_variables="T18;J8",
    evidence_role="direct", provenance_note=DS + "; 판부 내용 전문 미확보")
add(claim_id="CL-SIM-04", claim="조재항의 아우 조재정이 격쟁하였다(《심리록》 임인년 7월 조).",
    source_id="SIM", source_locator="〈백천 조재항옥〉 임인(1782) 7월 조", original_text="載恒弟載鼎擊錚",
    translation=f"재항의 아우 재정이 격쟁하였다. [{TR}]", claim_type="직접 사실", verification_status="간접 확인",
    event_date="1782 L7", source_date="확인 필요", url=SIM_URL, related_variables="T19;J13",
    evidence_role="direct", provenance_note=DS + "; 날짜는 데이터셋의 월 단위 표기")
add(claim_id="CL-SIM-05", claim="1782년 7월 형조 검토 뒤 이가원을 감영 옥에 가두라는 판부가 내려졌다(명령이며 집행 기록 아님).",
    source_id="SIM", source_locator="〈백천 조재항옥〉 임인(1782) 7월 판부", original_text="使之牢囚營獄",
    translation=f"그로 하여금 영옥(감영 옥)에 단단히 가두게 하라. [{TR}]", claim_type="직접 사실",
    verification_status="간접 확인", event_date="1782 L7", source_date="확인 필요", url=SIM_URL,
    related_variables="M14;J15", evidence_role="direct", provenance_note=DS)
add(claim_id="CL-SIM-06", claim="윤씨는 사망 5일 만에 매장되었고, 약 40일 뒤 고발과 (굴검) 검험이 이루어졌다.",
    source_id="SIM", source_locator="원문 위치 미확보 — 시곡 PDF p.11 [S09] '시놉시스 연결' 설명에만 근거",
    original_text="", translation="", claim_type="직접 사실", verification_status="간접 확인",
    event_date="1780 L6 이전(심리록 연대 채택 시)", source_date="확인 필요", url=SIM_URL,
    related_variables="T9;T13;T14", evidence_role="direct",
    provenance_note="원문 구절 미확보. 시곡 PDF p.11: '매장 5일, 약 40일 뒤 고발·검험'. 원문의 일수 표현(예: 五日·四十日)은 확인 필요")
add(claim_id="CL-SIM-07", claim="초검관은 배천군수 권중립, 복검관은 연안부사 이우배였다.",
    source_id="SIM", source_locator="원문 위치 미확보 — 시곡 PDF p.3 인물소개·p.9 장면별 대응표에 근거",
    original_text="", translation="", claim_type="직접 사실", verification_status="간접 확인",
    event_date="초검·복검 시점(미상)", source_date="확인 필요", url=SIM_URL, related_variables="T1;T14;T15;J1;J2",
    evidence_role="direct",
    provenance_note="PDF는 초검·복검 사실을 S09·S13·S14로 '확인'이라 판정하나 검관 성명의 원문 구절은 제시하지 않음")

# ── 《정조실록》 1783-06-03 ──
for cid, claim, ot, tr, ed, vars_, vs, note in [
    ("CL-SIL-01", "1783년 판부는 사건을 신축년(1781)의 일로 언급한다(무엇을 가리키는지—사망·성옥·심리—는 문맥 미확인).",
     "事在辛丑", "일은 신축년에 있었다.", "1781(회고)", "T16;T8", "사료 간 충돌", "CL-SIM-01과 충돌. 지시 대상 해석 필요"),
    ("CL-SIL-02", "정조는 신축년 봄 심리 때 재조사를 지시했다고 회고한다.",
     "辛丑春審理時", "신축년 봄 심리할 때.", "1781 L1–L3(봄)", "T18;J8", "간접 확인", "시곡 PDF는 재조사 명령을 1780 L12로 적음(p.7–8) → 극중 설정 또는 별도 근거 확인 필요"),
    ("CL-SIL-03", "정조는 이가원이 몰래 마을 여인에게 (노래) 가사를 가르쳤다고 판단했다.",
     "暗敎村女", "몰래 마을 여인에게 가르쳐.", "윤씨 사망 이후(정확 시점 미상)", "M11;T11", "간접 확인", "정조의 판단(판부 속 사실인정)"),
    ("CL-SIL-04", "농요는 밭이나 길에서 사람들이 듣도록 의도되었다고 판단되었다.",
     "或在乎田 或行于路", "혹은 밭에서, 혹은 길에서.", "윤씨 사망 이후", "M11;M13", "간접 확인", "장소 유형일 뿐 실제 위치 아님"),
    ("CL-SIL-05", "여러 공초가 서로 어긋나고 피 묻은 옷의 행방이 확인되지 않았다고 판단되었다.",
     "諸招互相枝梧 血衣則便沒下落", "여러 공초가 서로 어긋나고, 피 묻은 옷은 끝내 행방이 없다.", "1783 L6 이전 심리 과정", "J4;M12;J3", "간접 확인", "피 묻은 옷이 누구의 주장 속 물증인지는 원문 심층 확인 필요"),
    ("CL-SIL-06", "정조는 도신(조상진)이 재조사 명을 받고도 한 번도 몸소 조사하지 않고 수령에게 맡겼다고 비판했다.",
     "不曾一番躬按 付之守宰", "한 번도 몸소 조사하지 않고 수령에게 맡겼다.", "1781 봄 이후 재조사 기간", "J9;J10;A13", "간접 확인", "정조의 평가. 고의적 은폐를 말하지 않음"),
    ("CL-SIL-07", "정조는 조재항을 타이른 뒤 방면하라고 명했다(명령; 석방 집행일 미상).",
     "詳細曉諭後 放送", "자세히 타일러 깨우친 뒤 풀어 보내라.", "1783 L6 3", "T20;J14;T17", "간접 확인", ""),
    ("CL-SIL-08", "이가원은 사형을 감하여 극변에 종신 정배하라는 명을 받았다.",
     "極邊限己身減死定配", "사형을 감하여 극변에 자기 몸이 다할 때까지 정배하라.", "1783 L6 3", "T20;M14", "간접 확인", "유배지·집행 미확인"),
    ("CL-SIL-09", "정조는 해당 도신 조상진을 파직하라고 명했다.",
     "該道臣趙尙鎭罷職", "해당 도신 조상진을 파직하라.", "1783 L6 3", "T20;J9;A15", "간접 확인", "판부 6일 전(1783 L5 9) 조상진은 대사성 제수 기록(CL-SIL-14) → 파직 대상 직위 확인 필요"),
    ("CL-SIL-10", "기타 관련인은 본영에서 경중에 따라 처벌하라고 명했다.",
     "從輕重決罪", "경중에 따라 죄를 처결하라.", "1783 L6 3", "S10;J15", "간접 확인", "윤씨 살해범 처벌을 뜻하지 않음"),
]:
    add(claim_id=cid, claim=claim, source_id="SIL1783", source_locator="정조 7년 6월 3일 4번째 기사", original_text=ot,
        translation=f"{tr} [{TR}]", claim_type="직접 사실", verification_status=vs, event_date=ed,
        source_date="확인 필요", url=SIL_URL, related_variables=vars_, evidence_role="direct", provenance_note=DS + ("; " + note if note else ""))
add(claim_id="CL-SIL-11", claim="이 사건은 3년 동안 네 차례의 조사를 거쳤다.", source_id="SIL1783",
    source_locator="정조 7년 6월 3일 4번째 기사(국역 요지)", original_text="", translation="'3년 동안에 네 차례의 조사' (사용자 3사례 보고서의 국역 인용)",
    claim_type="직접 사실", verification_status="간접 확인", event_date="1780/1781–1783", source_date="확인 필요", url=SIL_URL,
    related_variables="J8;J9;T18", evidence_role="direct", provenance_note="원문 구절 미확보. source_extracts/drive_other_documents.md#D3")
add(claim_id="CL-SIL-12", claim="이가원은 조재항의 먼 인척이다.", source_id="SIL1783", source_locator="정조 7년 6월 3일 4번째 기사(국역 요지)",
    original_text="", translation="'조재항의 먼 인척 이가원' (사용자 3사례 보고서)", claim_type="직접 사실", verification_status="사료 간 충돌",
    event_date="해당 없음(관계)", source_date="확인 필요", url=SIL_URL, related_variables="M2",
    evidence_role="direct", provenance_note="시곡 PDF p.12는 '원사료는 이가원의 … 윤씨 친족관계를 다룬다'고 적어 친족관계의 기준 인물이 문서마다 다름. 원문 확인 필요")
add(claim_id="CL-SIL-13", claim="이가원은 사람들을 사주하고, 뒤늦게 시신을 파내 검험하도록 하여 살인 옥안을 성립시키는 데 관여했다.",
    source_id="SIL1783", source_locator="정조 7년 6월 3일 4번째 기사(국역 요지)", original_text="", translation="(사용자 3사례 보고서의 국역 요지)",
    claim_type="직접 사실", verification_status="간접 확인", event_date="윤씨 사망 후 약 40일 무렵", source_date="확인 필요",
    url=SIL_URL, related_variables="M9;M10;T13;T14;J1", evidence_role="direct", provenance_note="정조의 판단에 서술된 사실인정")

# ── 《추관지》 ──
for cid, claim, vars_, ed in [
    ("CL-CHUG-01", "윤씨는 사망 5일 만에 매장되었다.", "T9", "사망+5일"),
    ("CL-CHUG-02", "이가원이 조재항에게 금품을 요구했다.", "M7;T10;M8", "사망 이후(정확 시점 미상)"),
    ("CL-CHUG-03", "이가원이 병든 조환을 선동(사주)했다.", "M9;T12;F6;F10;F12", "사망 이후"),
    ("CL-CHUG-04", "농요가 조작되었고 고발이 지연되었다.", "M11;T13", "사망 이후"),
]:
    add(claim_id=cid, claim=claim, source_id="CHUG", source_locator="권2 상복부·윤상·살처, 중보 조재항 옥안(원문 위치 미확보) — 시곡 PDF p.11 [S14] 설명",
        original_text="", translation="", claim_type="직접 사실", verification_status="간접 확인", event_date=ed,
        source_date="확인 필요", url=CHUG_URL, related_variables=vars_, evidence_role="direct",
        provenance_note="원문 구절 미확보; 시곡 PDF p.11 요약에만 근거. 《추관지》 URL 표기 3종 불일치")
add(claim_id="CL-CHUG-05", claim="조재항은 넉넉하게 살았다(경제적 여유가 있었다).", source_id="CHUG",
    source_locator="원문 위치 미확보 — C안 고증보고서 표1", original_text="", translation="", claim_type="직접 사실",
    verification_status="간접 확인", event_date="사건 당시", source_date="확인 필요", url=CHUG_URL, related_variables="E4",
    evidence_role="direct", provenance_note="C안 보고서: '조재항이 넉넉하게 살았다는 기록만 확인'. 계층(서민지주/토호)·토지량은 기록 없음")

# ── 인사 연표 ──
add(claim_id="CL-OFF-01", claim="조상진은 1781년 음력 9월 29일 무렵 황해감사로서 도내 농황 분등 장계를 올렸다(그 시점 재임).",
    source_id="BIB1781", source_locator="정조 5년 9월 29일 기사", original_text="", translation="",
    claim_type="직접 사실", verification_status="간접 확인", event_date="1781 L9 29", source_date="확인 필요",
    url="https://db.history.go.kr/item/compareViewer.do?levelId=bb_163r_001_03_0590", related_variables="T2;J9",
    evidence_role="direct", provenance_note="시곡 PDF p.10 [S05] 설명에만 근거")
add(claim_id="CL-OFF-02", claim="1782년 음력 4월 23일 황해감사는 이경양이었다(월봉 1등 처분).", source_id="SIL178204",
    source_locator="정조 6년 4월 23일 기사", original_text="監司李敬養 越俸一等", translation=f"감사 이경양을 월봉 1등에 처하라. [{TR}]",
    claim_type="직접 사실", verification_status="간접 확인", event_date="1782 L4 23", source_date="확인 필요",
    url="https://sillok.history.go.kr/id/kva_10604023_001", related_variables="T3;T2", evidence_role="direct",
    provenance_note=DS + "; 이경양의 부임일은 미확인")
add(claim_id="CL-OFF-03", claim="조상진은 1783년 음력 5월 9일 성균관 대사성에 제수되었다.", source_id="SIL1783M",
    source_locator="정조 7년 5월 9일 기사", original_text="", translation="", claim_type="직접 사실", verification_status="간접 확인",
    event_date="1783 L5 9", source_date="확인 필요", url="https://sillok.history.go.kr/id/kva_10705009_002",
    related_variables="T2;J9", evidence_role="direct", provenance_note="시곡 PDF p.11 [S12] 설명에만 근거")
add(claim_id="CL-OFF-04", claim="조상진은 1780년 여름(극중 표기: 음력 6월) 황해감사로 부임했다.", source_id="SIGOK_PDF",
    source_locator="PDF p.6 제3막 9문단('같은 해 음력 6월 부임한 황해도관찰사 조상진'); 사용자 지시문 '1780년 여름'",
    original_text="같은 해 음력 6월 부임한 황해도관찰사 조상진은 두 보고를 받아든다.", translation="(국문)",
    claim_type="직접 사실", verification_status="미확인", event_date="1780 L4–L6(여름) / 극중 L6", source_date="2026",
    url="", related_variables="T2;T4;T5;T6", evidence_role="direct",
    provenance_note="URL 비어 있음: 부임 기사(승정원일기·실록)를 이번 실행에서 확보하지 못함. 시놉시스 서술과 지시문 진술뿐이므로 '미확인'")
add(claim_id="CL-OFF-05", claim="이득준은 1780년 음력 3월 평산부사에 임명되었다.", source_id="SJW1780",
    source_locator="PDF p.3 고증 유의('사료에 근거'); 계획서가 지목한 승정원일기 1780.3.14 기사(내용 미확인)",
    original_text="", translation="", claim_type="직접 사실", verification_status="미확인", event_date="1780 L3",
    source_date="확인 필요", url="https://sjw.history.go.kr/id/SJW-G04030140-02600", related_variables="J11",
    evidence_role="direct", provenance_note="해당 URL이 이득준 기사인지 확인 못함. 1780 L12 재임 여부 미확정(PDF p.3)")
add(claim_id="CL-OFF-06", claim="심낙수는 1780년 훈련도감 안핵어사로 조사 업무를 맡았다.", source_id="SIGOK_PDF",
    source_locator="PDF p.2 인물소개·p.3 고증 유의", original_text="1780년 훈련도감 안핵어사로 조사 업무를 맡았다.",
    translation="(국문)", claim_type="직접 사실", verification_status="미확인", event_date="1780", source_date="2026",
    url="", related_variables="J12", evidence_role="direct", provenance_note="URL 비어 있음: PDF가 근거 사료를 명시하지 않음")
add(claim_id="CL-INST-01", claim="정기 포폄(수령 근무평가)은 관찰사가 매년 음력 6월·12월에 시행한다.", source_id="GYDJ_POPHYEOM",
    source_locator="《경국대전》 이전 포폄조(조문 원문 미확보)", original_text="", translation="", claim_type="학술적 해석",
    verification_status="미확인", event_date="해당 없음(제도)", source_date="확인 필요", url="", related_variables="T5;T6;A7",
    evidence_role="institutional", provenance_note="URL 비어 있음: 조문 링크 미확보(네트워크 차단). 사용자 지시문의 '일반적으로' 진술. 특별 포폄·수시 장계 포상의 가능성은 별도")

# ── 경제·제도 맥락 ──
add(claim_id="CL-ECON-01", claim="1780년 정월 정조는 지난해(1779) 수확이 회복되었다고 평가했다(전국 수준).", source_id="SIL1780J",
    source_locator="정조 4년 1월 1일 권농윤음", original_text="", translation="", claim_type="직접 사실", verification_status="간접 확인",
    event_date="1780 L1 1", source_date="확인 필요", url="https://sillok.history.go.kr/id/kva_10401001_002",
    related_variables="E1", evidence_role="direct", provenance_note="C안 보고서 요지. 배천 개별 작황 아님")
add(claim_id="CL-ECON-02", claim="1782년 음력 6월 배천군수 김안묵의 향곡 3분의 1 가분 요청이 불허되었다.", source_id="BIB178206",
    source_locator="정조 6년 6월 14일 기사", original_text="白川餉穀 限三分一加分", translation=f"배천의 향곡을 3분의 1 한도로 가분함. [{TR}]",
    claim_type="직접 사실", verification_status="간접 확인", event_date="1782 L6 14", source_date="확인 필요",
    url="https://db.history.go.kr/item/compareViewer.do?levelId=bb_164_001_06_0220", related_variables="E14;E13",
    evidence_role="later_context", provenance_note=DS + "; 加分≠勸分. 1780년 관측치로 소급 금지")
add(claim_id="CL-ECON-03", claim="1782년 음력 7월 식량 부족·영농 중단 우려로 배천 향곡 가분이 특별 허가되었다.", source_id="BIB178207",
    source_locator="정조 6년 7월 4일 기사", original_text="依狀請特爲許施可也", translation=f"장계의 청에 따라 특별히 허락하여 시행함이 옳다. [{TR}]",
    claim_type="직접 사실", verification_status="간접 확인", event_date="1782 L7 4", source_date="확인 필요",
    url="https://db.history.go.kr/common/compareViewer.do?levelId=bb_165_001_01_0070&type=joseon", related_variables="E14;E13;E1",
    evidence_role="later_context", provenance_note=DS + "; 1780년 관측치로 소급 금지")
add(claim_id="CL-ECON-04", claim="1782년 4월 정조는 황해감사의 농황 보고가 늘 '비는 흡족, 작황은 양호'라고만 한다고 질책했다.",
    source_id="SIL178204", source_locator="정조 6년 4월 23일 기사", original_text="雨澤則每每言周洽 農形則在在稱登熟",
    translation=f"비는 매번 두루 흡족하다 말하고, 농사 형편은 곳곳이 잘 익었다고 일컫는다. [{TR}]", claim_type="직접 사실",
    verification_status="간접 확인", event_date="1782 L4 23", source_date="확인 필요", url="https://sillok.history.go.kr/id/kva_10604023_001",
    related_variables="A8", evidence_role="comparative", provenance_note=DS + "; 감영 보고의 정확성 문제에 대한 후대 비교 사례. 1780년 조상진 보고에 대한 증거 아님")
add(claim_id="CL-ECON-05", claim="1789년 《호구총수》의 백천은 16면 4,994호 12,891구였다.", source_id="HOGU",
    source_locator="황해도 백천 조", original_text="", translation="", claim_type="직접 사실", verification_status="간접 확인",
    event_date="1789", source_date="1789(확인 필요)", url="https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_590_0050_0160",
    related_variables="E15", evidence_role="later_context", provenance_note="1780년 인구로 복사 금지")
add(claim_id="CL-ECON-06", claim="1793년 연안·배천은 넓은 들판과 부족한 관개로 적은 강우에도 농사가 취약하다고 언급되었다.",
    source_id="SIL1793", source_locator="정조 17년 9월 16일 윤음", original_text="", translation="", claim_type="직접 사실",
    verification_status="간접 확인", event_date="1793 L9 16", source_date="확인 필요", url="https://sillok.history.go.kr/id/kva_11709016_003",
    related_variables="E1", evidence_role="later_context", provenance_note="C안 보고서 요지. 구조적 취약성의 후대 설명")
add(claim_id="CL-ECON-07", claim="18세기 초 농가 토지 소유는 상위 약 6%가 약 44%를 차지하는 불평등을 보였다는 추계가 있다.",
    source_id="NIKH_NH36", source_locator="신편 한국사 36, 1) 민중세계의 각성", original_text="", translation="",
    claim_type="학술적 해석", verification_status="간접 확인", event_date="18세기 초", source_date="확인 필요",
    url="https://contents.history.go.kr/mobile/nh/view.do?levelId=nh_036_0030_0010_0010", related_variables="E2;E3",
    evidence_role="scholarship", provenance_note="C안 보고서 요지. 배천 실측치 아님")
add(claim_id="CL-LEE-01", claim="조선 후기 권분 부담은 상층 양반지주·토호지주보다 부농·서민지주(요호부민)에게 상대적으로 무겁게 작용했다(회피 능력 차이).",
    source_id="LEE2009", source_locator="쪽수 미확인", original_text="", translation="", claim_type="학술적 해석",
    verification_status="미확인", event_date="조선 후기(일반)", source_date="2009",
    url="https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE10953875", related_variables="E5;E6;E7;E3",
    evidence_role="scholarship", provenance_note="논문 본문·초록 모두 미열람. 사용자 지시문의 요약을 '검증 대상 주장'으로 등록한 것")
add(claim_id="CL-LEE-02", claim="권분은 원칙상 권유이며, 과도한 압박·강제징수는 당대에도 폐단으로 비판되었다.",
    source_id="LEE2009", source_locator="쪽수 미확인(C안 보고서 5절 인용)", original_text="", translation="", claim_type="학술적 해석",
    verification_status="미확인", event_date="조선 후기(일반)", source_date="2009",
    url="https://www.dbpia.co.kr/journal/articleDetail?nodeId=NODE10953875", related_variables="A1;A2", evidence_role="scholarship",
    provenance_note="C안 보고서의 인용 요지. 논문 원문 미열람")
for cid, sid, url, claim, ed, vars_, role in [
    ("CL-CMP-01", "BIB1727", "https://db.history.go.kr/item/compareViewer.do?levelId=bb_082_001_06_0310", "1727년 옥천에서 권분 대상 부민을 감금하여 곡식을 강제로 거둔 사례가 논의되었다.", "1727 L12 14", "A2;A3", "comparative"),
    ("CL-CMP-02", "BIB1731", "https://db.history.go.kr/common/compareViewer.do?levelId=bb_090r_001_06_0190&type=joseon", "1731년 송징계는 권분을 빙자한 부민 곡물 강취와 향리의 폐단을 비판했다.", "1731 L12 9", "A2;M4", "comparative"),
    ("CL-CMP-03", "BIB1741", "https://db.history.go.kr/common/compareViewer.do?levelId=bb_109_001_05_0430&type=joseon", "1741년 북도에서 부민 권분의 곡물 수량별 논상 기준이 정해졌다.", "1741 L11 21", "A1;E6", "comparative"),
    ("CL-CMP-04", "SIL1783A", "https://sillok.history.go.kr/id/kva_10701018_004", "1783년 정월 정조는 부민의 진휼을 권장하되 수령의 권분 강요를 경계했다.", "1783 L1 18", "A1;A2", "later_context"),
    ("CL-CMP-05", "SIL1783O", "https://sillok.history.go.kr/id/kva_10710029_003", "1783년 10월 어사 사목은 권분을 빙자한 강제징수를 감찰하도록 했다.", "1783 L10 29", "A2;A9", "later_context"),
    ("CL-CMP-06", "YJSIL1742", "https://sillok.history.go.kr/id/wua_11801006_001", "1742년 옥천 살인 옥사에 이천보를 안핵어사로 파견한 선례가 있다.", "1742 L1 6", "J12", "comparative"),
    ("CL-CMP-07", "TGJS", "https://db.history.go.kr/joseon/item/level.do?allViewYn=Y&levelId=jlawb_120_0020_0290", "1783년 사계정식은 황해도의 별도 사관 지정 관행과 이후 관찰사 직접 조사 원칙을 보여준다.", "1783 L7 8", "J9;J11", "later_context"),
    ("CL-CMP-08", "DMYJ_MOSAL", "https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_170_0190_0010_0010", "《대명률직해》 모살인 조는 주모자·실행 가담자·미가담 공모자의 형벌을 구분한다.", "해당 없음", "S9;S10;J15", "institutional"),
    ("CL-CMP-09", "DMYJ_MUGO", "https://db.history.go.kr/joseon/item/level.do?levelId=jlawb_170_0220_0010_0050", "《대명률직해》 무고 조는 반좌 원칙과 사형 혐의 무고의 처벌을 규정한다.", "해당 없음", "M14", "institutional"),
]:
    add(claim_id=cid, claim=claim, source_id=sid, source_locator="해당 기사/조문(시곡 PDF 부록·C안 보고서 요지)", original_text="", translation="",
        claim_type="직접 사실", verification_status="간접 확인", event_date=ed, source_date="확인 필요", url=url,
        related_variables=vars_, evidence_role=role, provenance_note="원문 미대조. 1780년 배천에서 동일한 일이 있었다는 증거 아님")
for cid, claim, vars_ in [
    ("CL-REQ-01", "1782년 서명선이 관봉(官封)·강제 대부를 비판했다.", "A3;A4"),
    ("CL-REQ-02", "1782~1783년 권분에 대한 수직(授職) 포상이 시행되었다.", "A6"),
    ("CL-REQ-03", "1787년 권분·진휼 관련 관리 비위가 문제되었다.", "A14"),
]:
    add(claim_id=cid, claim=claim, source_id="", source_locator="출처 미특정(사용자 지시문 언급)", original_text="", translation="",
        claim_type="직접 사실", verification_status="미확인", event_date=claim[:4], source_date="", url="",
        related_variables=vars_, evidence_role="comparative",
        provenance_note="URL 비어 있음: 근거 기사를 이번 실행에서 특정·확보하지 못함. 확보 전까지 비교 사례로도 사용하지 않음")

# ── 이론 ──
add(claim_id="CL-THY-01", claim="공동체의 위기에서 적대가 모방적으로 수렴하여 한 사람에게 집중되고, 그 폭력이 집단적 정당성을 얻는다(희생양 메커니즘).",
    source_id="GIRARD1986", source_locator="단행본 전반(쪽수 미특정)", original_text="", translation="", claim_type="학술적 해석",
    verification_status="미확인", event_date="해당 없음", source_date="1982/1986", url="", related_variables="S6;S7;S8",
    evidence_role="theory", provenance_note="URL 비어 있음: 단행본. 해석틀이며 윤씨 사건의 증거 아님")
add(claim_id="CL-THY-02", claim="출연을 막는 사람을 제거하면 곡식을 얻는다는 목적 달성형 폭력은 그 자체로 희생양 메커니즘과 같지 않다.",
    source_id="LEEJW2015", source_locator="C안 보고서 7절 인용", original_text="", translation="", claim_type="학술적 해석",
    verification_status="간접 확인", event_date="해당 없음", source_date="2015", url="https://doi.org/10.33156/philos.2015.40..010",
    related_variables="S7;S9", evidence_role="theory", provenance_note="C안 보고서 인용 요지. 논문 원문 미열람")
add(claim_id="CL-THY-03", claim="사람들은 죄책감을 줄이거나 통제감을 회복하려는 동기로 책임을 희생양에게 전가할 수 있다(실험사회심리학).",
    source_id="ROTHSCHILD2012", source_locator="논문 전반", original_text="", translation="", claim_type="학술적 해석",
    verification_status="미확인", event_date="해당 없음", source_date="2012", url="https://doi.org/10.1037/a0027413",
    related_variables="S2;S6", evidence_role="theory", provenance_note="서지만 확인(작성자 지식). 현대 실험 결과이며 조선 사례 증거 아님")
add(claim_id="CL-THY-04", claim="부정적 경제 충격은 소수자 박해를 촉발할 수 있으나 그 관계는 지역의 경제적 상호의존 등 조건에 따라 달라진다.",
    source_id="JEDWAB2019", source_locator="논문 전반", original_text="", translation="", claim_type="학술적 해석",
    verification_status="미확인", event_date="해당 없음", source_date="2019", url="https://doi.org/10.1007/s10887-019-09167-1",
    related_variables="S7;E13", evidence_role="theory", provenance_note="서지만 확인(작성자 지식). 역사적 박해 비교 틀")
add(claim_id="CL-THY-05", claim="불안이 높아진 2인 관계는 제3자를 끌어들여 삼각관계를 형성하며, 정보·정서가 그 경로로 왜곡될 수 있다(보웬 가족체계이론).",
    source_id="BOWEN1978", source_locator="단행본 전반", original_text="", translation="", claim_type="학술적 해석",
    verification_status="미확인", event_date="해당 없음", source_date="1978", url="", related_variables="F11;F3;F5",
    evidence_role="theory", provenance_note="URL 비어 있음: 단행본. 조환의 실제 동기를 입증하지 않음")
add(claim_id="CL-THY-06", claim="식량 안보는 가용성과 접근성을 구분해야 하며, 총공급이 있어도 가구별 접근 격차로 굶주림이 생길 수 있다.",
    source_id="FAO2008", source_locator="기본개념 안내서", original_text="", translation="", claim_type="학술적 해석",
    verification_status="간접 확인", event_date="해당 없음", source_date="2008",
    url="https://www.fao.org/agrifood-economics/publications/detail/en/c/122386/", related_variables="E2;E13",
    evidence_role="theory", provenance_note="현대 분석개념. C안 보고서 인용")

# ── 극중 설정(시곡 PDF 원문에서 확인 = 창작임을 확인) ──
P = "https://drive.google.com/file/d/1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w/view"
for cid, loc, ot, claim, ed, vars_ in [
    ("CL-FILM-01", "p.4 제1막 1문단", "군수 권중립은 부유한 가호에 곡식을 내도록 권한다.", "1780년 봄 배천에서 권중립이 권분을 시행한다.", "극중 1780 봄", "A1;A5;T1"),
    ("CL-FILM-02", "p.3 인물소개 이가원", "배천 관아의 호방 · 무고의 기획자", "이가원은 배천 관아의 호방이다.", "극중", "M3;M4"),
    ("CL-FILM-03", "p.5 제2막 4문단", "1780년 음력 4월 하순.", "윤씨는 1780년 음력 4월 하순 귀갓길에 주민들에게 살해된다.", "극중 1780 L4 하순", "T8;S9;S11;J6"),
    ("CL-FILM-04", "p.5 제2막 5문단", "주민들은 시신을 들어 … 조재항 집 가까이에 옮겨 놓고 흩어진다.", "살해 후 시신이 조재항 집 근처로 옮겨진다.", "극중", "S12;J6"),
    ("CL-FILM-05", "p.6 제3막 8문단", "윤씨가 죽은 지 약 사십 일이 지난 음력 6월, 고발을 받은 권중립은 매장된 시신을 꺼내 검험한다.", "초검은 1780년 음력 6월에 이루어진다.", "극중 1780 L6", "T14;T13"),
    ("CL-FILM-06", "p.6 제3막 9문단", "같은 해 음력 6월 부임한 황해도관찰사 조상진은 두 보고를 받아든다.", "조상진은 윤씨 사망 이후(1780 L6)에 부임해 초·복검 보고를 받는다.", "극중 1780 L6", "T2;T4"),
    ("CL-FILM-07", "p.7 제4막 10문단", "1780년 음력 12월. 정조는 … 조상진에게 다른 조사관을 정해 여러 방면으로 조사하라고 명한다.", "재조사 명령은 1780년 음력 12월이다.", "극중 1780 L12", "T18;J8"),
    ("CL-FILM-08", "p.7 제4막 10문단", "사관이 … 새로운 진술을 올리자 조상진은 이를 본 보고에서 덜어내고", "조상진은 이득준의 새 진술을 보고에서 고의로 누락한다.", "극중", "J10;A13;A14"),
    ("CL-FILM-09", "p.7 제4막 10문단", "정조는 … 암행어사를 비밀리에 파견한다.", "정조가 암행어사(심낙수)를 비밀 파견한다.", "극중", "J12"),
    ("CL-FILM-10", "p.7 제4막 12문단", "1781년 봄. 조재정은 … 격쟁으로 호소한다.", "조재정 격쟁을 1781년 봄으로 압축한다(실제 1782 L7).", "극중 1781 봄", "T19;J13"),
    ("CL-FILM-11", "p.8 제5막 14문단", "황해감사 조상진은 재조사 보고를 조작한 혐의로 현직에서 파직되어", "조상진은 현직 황해감사로서 파직된다.", "극중 1781 상반기", "T20;J9;T2"),
    ("CL-FILM-12", "p.8 사료와 각색 구분", "본 작품은 모든 결말을 조상진·권중립 재임 중인 1781년 상반기로 앞당긴다.", "모든 결말을 1781년 상반기로 압축한다.", "극중 1781 상반기", "T19;T20;T17"),
    ("CL-FILM-13", "p.3 인물소개 조환", "병든 윤씨의 친족 · 고발에 동원된 사람", "조환은 윤씨의 친족(사용자 지시문: 외숙부)이며 직접 목격하지 못했다.", "극중", "F3;F6;M9"),
    ("CL-FILM-14", "p.4 제1막 3문단", "권중립은 숫자가 잘 정리된 장계를 보며 만족하지만, 거절한 가호들이 떠안은 부담과 협박의 경위는 그 기록에서 빠진다.", "권중립의 구휼 보고는 강압·부담을 누락한다.", "극중 1780 봄", "A8;A14;A5"),
]:
    add(claim_id=cid, claim=claim, source_id="SIGOK_PDF", source_locator=loc, original_text=ot, translation="(국문 원문)",
        claim_type="극중 창작", verification_status="원문 확인", event_date=ed, source_date="2026-10-30", url=P,
        related_variables=vars_, evidence_role="film", provenance_note="시놉시스 원문에서 '창작 설정임'을 확인. 역사적 사실 아님")
add(claim_id="CL-FILM-REQ-01", claim="극중 필수 제약: 조상진 부임 < 권중립 포폄 < 윤씨 사망 < 옥사 성립, 포폄 평가자는 현직 감사 조상진.",
    source_id="", source_locator="사용자 지시문(2026-10-31) §4", original_text="", translation="", claim_type="극중 창작",
    verification_status="미확인", event_date="극중", source_date="2026-10-31", url="", related_variables="T2;T5;T6;T7;T8;T16;A7",
    evidence_role="film", provenance_note="URL 비어 있음: 사용자 지시 사항(문서 아님). 시놉시스 v4의 연대(사망 L4 하순 → 조상진 L6 부임)와 상충")
add(claim_id="CL-FILM-REQ-02", claim="조상진이 권중립에게 상고(긍정적 포폄)를 부여했다.", source_id="", source_locator="사용자 지시문 §6; 포폄계본 미확보",
    original_text="", translation="", claim_type="극중 창작", verification_status="미확인", event_date="극중", source_date="2026-10-31",
    url="", related_variables="A7;T7", evidence_role="film", provenance_note="URL 비어 있음: 실제 포폄계본·등급 미확보")
add(claim_id="CL-FILM-REQ-03", claim="조재항은 최상층 토호가 아니라 권분 요구를 회피하기 어려운 서민지주·요호부민이다.",
    source_id="", source_locator="사용자 지시문 §5", original_text="", translation="", claim_type="극중 창작", verification_status="미확인",
    event_date="극중", source_date="2026-10-31", url="", related_variables="E5;E3", evidence_role="film",
    provenance_note="URL 비어 있음: 사료는 '넉넉하게 살았다'(CL-CHUG-05)까지만. 계층 규정은 창작")

# 추론(모형이 도출한 주장) — 03_constraints.py 결과와 일치하는지 테스트가 확인
add(claim_id="CL-INF-01", claim="《심리록》 경자 6월 성옥, 1780년 여름 조상진 부임, 6·12월 정기 포폄, 사망→고발 약 40일, 고발≤초검<복검≤성옥을 모두 고정하면 극중 필수 순서(부임<포폄<사망<성옥)는 성립하지 않는다.",
    source_id="", source_locator="03_constraints.py → results/csp_results.json (MODE F_on_H_SIM)", original_text="", translation="",
    claim_type="추론", verification_status="미확인", event_date="해당 없음", source_date="2026-10-31", url="",
    related_variables="T2;T5;T8;T13;T16", evidence_role="inference",
    provenance_note="URL 비어 있음: 모형 계산 결과. 전제(특히 부임 시기·포폄 시기·40일)가 미확인/간접 확인이므로 결론도 전제에 종속")

def main():
    out = ROOT / "01_claim_registry.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in C:
            w.writerow(r)
    print(f"wrote {len(C)} claims -> {out.name}")

if __name__ == "__main__":
    main()
