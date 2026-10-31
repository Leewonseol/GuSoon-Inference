# source_extracts — 입력자료 스냅숏 (읽기 전용)

이 폴더의 파일은 **분석 입력의 출처를 고정하기 위한 사본**이다. 내용은 수정하지 않았고, 원본은 아래 위치에 있다.

| 파일 | 원본 | 취득 경로 | 비고 |
|---|---|---|---|
| `sigok_pdf_pages/p01–p12.txt` | `../source_local/시곡_인물소개_이득준_출생정보_검증_최종.pdf` (사용자 업로드, Google Drive `1hooBf4HYl7ma8Hmyj1BIWThTcKZzCT6w`와 동일 크기·동일 링크 16개) | `pdftotext` 페이지별 추출 | 페이지 번호는 PDF 물리 페이지 |
| `drive_CORE_EVENTS.csv` | Google Drive `1JgnSa9omaxrgCm1f9ksC1FVLMKeKhopE` | Drive 커넥터 텍스트 읽기 | 사용자 이전 연구 데이터셋. 한문 구절은 **사용자가 전사한 것**이며 이번 실행에서 원문 DB와 대조하지 못함 |
| `drive_CORE_CASE_CLAIMS.csv` | Google Drive `1MCDpRsh8Pws6HmQu87hugXamsXl03Z4-` | 위와 같음 | 위와 같음 |
| `drive_SOURCES.csv` | Google Drive `1wYt_jcC3KNOZZHGzb4PdjIHANozJjDqU` | 위와 같음 | 위와 같음 |
| `drive_other_documents.md` | Drive의 C안 고증보고서·3대 연구과제 계획서·3사례 비교 보고서 | Drive 커넥터 | 인용 위치와 요지만 기록(전문 복제 아님) |

Drive 커넥터는 Markdown 이스케이프(`\_`, `\&`)를 붙여 반환하므로 CSV 저장 시 이를 제거했다. 그 외 문자열은 그대로다.
