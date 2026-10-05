#!/usr/bin/env python3
"""GuSoon v2 initial validation (source-faithful data only).

- Loads the 4 v2 CSVs into database/gusun_v2.duckdb (all columns as VARCHAR).
- Never modifies the raw CSVs (SHA-256 is recorded before and after the run).
- Never auto-fixes anything and never merges vocabularies.
- Builds no events, attestations, relations, episodes, DAGs or inferences.
- Uses nothing from the deprecated v1 pipeline.

Outputs:
  output/01_v2_integrity_report.csv
  output/02_v2_row_counts.csv
  output/03_v2_vocabularies.csv
  output/04_v2_sanity_checks.csv
  logs/v2_initial_validation.log
  database/gusun_v2.duckdb
  data/raw/gusun_research_v2_SHA256SUMS.txt
"""

import csv
import hashlib
import logging
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
DB_PATH = ROOT / "database" / "gusun_v2.duckdb"
SHA_PATH = RAW_DIR / "gusun_research_v2_SHA256SUMS.txt"

TABLES = {
    "source_records": "gusun_research_v2_source_records.csv",
    "source_faithful_propositions": "gusun_research_v2_source_faithful_propositions.csv",
    "person_membership": "gusun_research_v2_person_membership.csv",
    "search_log": "gusun_research_v2_search_log.csv",
}

PRIMARY_KEYS = {
    "source_records": "source_record_id",
    "source_faithful_propositions": "prop_id",
    "search_log": "search_id",
}

CORE_PROP_FIELDS = ["prop_id", "source_record_id", "proposition_type", "subject", "predicate"]

VOCAB_FIELDS = [
    "attestation_mode",
    "proposition_type",
    "epistemic_scope",
    "occurrence_precision",
    "place_status",
    "set_status",
    "directness",
]

# Fields that carry extracted content. `notes` is excluded on purpose: it is
# the extractor's commentary, not a proposition about the source.
DATA_FIELDS = ["subject", "predicate", "object_or_content", "named_entities"]

log = logging.getLogger("v2_validation")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv_rows(path):
    # utf-8-sig: the v2 CSVs start with a UTF-8 BOM, which DuckDB also strips.
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = [r for r in reader if r]
    return header, rows


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def blank(v):
    return v is None or str(v).strip() == ""


def main():
    OUT_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    DB_PATH.parent.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_DIR / "v2_initial_validation.log", mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    paths = {t: RAW_DIR / fn for t, fn in TABLES.items()}
    missing = [str(p) for p in paths.values() if not p.exists()]
    if missing:
        log.error("Missing v2 CSV(s); stopping: %s", missing)
        sys.exit(1)

    sha_before = {t: sha256(p) for t, p in paths.items()}
    for t, h in sha_before.items():
        log.info("SHA-256 before %s: %s", TABLES[t], h)

    if DB_PATH.exists():
        DB_PATH.unlink()
    con = duckdb.connect(str(DB_PATH))

    findings = []  # check_id, check_group, severity, table, field, row_key, value, message

    def add(check_id, group, severity, table, field, row_key, value, message):
        findings.append([check_id, group, severity, table, field, row_key, value, message])

    # ---- load + C. row counts ----
    count_rows = []
    csv_data = {}
    for t, p in paths.items():
        header, rows = read_csv_rows(p)
        csv_data[t] = (header, rows)
        if p.read_bytes()[:3] == b"\xef\xbb\xbf":
            add("C0", "ROW_COUNT", "INFO", t, "", "", "UTF-8 BOM",
                "File starts with a UTF-8 BOM (stripped on read; file not modified)")
        bad_width = [i + 2 for i, r in enumerate(rows) if len(r) != len(header)]
        for line in bad_width:
            add("C2", "ROW_COUNT", "ERROR", t, "", f"line {line}", "",
                "Row width differs from header width")
        con.execute(
            f"CREATE TABLE {t} AS SELECT * FROM read_csv(?, header=true, all_varchar=true, "
            f"quote='\"', escape='\"', delim=',')",
            [str(p)],
        )
        db_rows = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        db_cols = [c[0] for c in con.execute(f"DESCRIBE {t}").fetchall()]
        match = db_rows == len(rows) and db_cols == header
        count_rows.append([t, TABLES[t], len(rows), db_rows, len(header), len(db_cols),
                           "MATCH" if match else "MISMATCH", sha_before[t]])
        if db_rows != len(rows):
            add("C1", "ROW_COUNT", "ERROR", t, "", "", f"csv={len(rows)} db={db_rows}",
                "CSV row count differs from DuckDB row count")
        if db_cols != header:
            add("C3", "ROW_COUNT", "ERROR", t, "", "", "", "DuckDB columns differ from CSV header")
        log.info("Loaded %s: csv_rows=%d duckdb_rows=%d cols=%d", t, len(rows), db_rows, len(header))

    # ---- A. PK / ID ----
    for t, pk in PRIMARY_KEYS.items():
        dups = con.execute(
            f"SELECT {pk}, count(*) FROM {t} GROUP BY {pk} HAVING count(*) > 1 ORDER BY 1"
        ).fetchall()
        for key, n in dups:
            add("A1", "PK_ID", "ERROR", t, pk, key, str(n), "Duplicate primary key")
        nulls = con.execute(f"SELECT count(*) FROM {t} WHERE {pk} IS NULL OR trim({pk}) = ''").fetchone()[0]
        if nulls:
            add("A2", "PK_ID", "ERROR", t, pk, "", str(nulls), "Empty primary key")
        if not dups and not nulls:
            add("A1", "PK_ID", "PASS", t, pk, "", "", "No duplicate or empty primary key")

    # ---- B. references ----
    src_ids = {r[0] for r in con.execute("SELECT source_record_id FROM source_records").fetchall()}

    dangling = con.execute(
        "SELECT p.prop_id, p.source_record_id FROM source_faithful_propositions p "
        "LEFT JOIN source_records s USING (source_record_id) "
        "WHERE s.source_record_id IS NULL ORDER BY p.prop_id"
    ).fetchall()
    for pid, sid in dangling:
        add("B1", "REFERENCE", "ERROR", "source_faithful_propositions", "source_record_id", pid, sid,
            "source_record_id not found in source_records")
    if not dangling:
        add("B1", "REFERENCE", "PASS", "source_faithful_propositions", "source_record_id", "", "",
            "All proposition source_record_id values exist in source_records")

    b2_bad = 0
    for sid_row, ids, status in con.execute(
        "SELECT search_id, relevant_source_record_ids, result_status FROM search_log ORDER BY search_id"
    ).fetchall():
        if blank(ids):
            add("B2", "REFERENCE", "INFO", "search_log", "relevant_source_record_ids", sid_row, status,
                "No relevant_source_record_ids (empty list, not a dangling reference)")
            continue
        for part in ids.split("|"):
            part_s = part.strip()
            if part_s != part or part_s not in src_ids:
                b2_bad += 1
                add("B2", "REFERENCE", "ERROR", "search_log", "relevant_source_record_ids", sid_row, part,
                    "Listed source id not found in source_records (exact match)")
    if not b2_bad:
        add("B2", "REFERENCE", "PASS", "search_log", "relevant_source_record_ids", "", "",
            "All listed relevant_source_record_ids exist in source_records")

    # ---- D. empty core fields ----
    for field in CORE_PROP_FIELDS:
        empty = con.execute(
            f"SELECT prop_id FROM source_faithful_propositions "
            f"WHERE {field} IS NULL OR trim({field}) = '' ORDER BY prop_id"
        ).fetchall()
        for (pid,) in empty:
            add("D1", "CORE_FIELD", "ERROR", "source_faithful_propositions", field, pid or "", "",
                "Empty core field")
        if not empty:
            add("D1", "CORE_FIELD", "PASS", "source_faithful_propositions", field, "", "",
                "No empty values")

    # ---- E. controlled vocabularies (report only, no merging) ----
    vocab_rows = []
    for field in VOCAB_FIELDS:
        for value, n in con.execute(
            f"SELECT {field}, count(*) FROM source_faithful_propositions GROUP BY 1 ORDER BY 1 NULLS FIRST"
        ).fetchall():
            vocab_rows.append(["source_faithful_propositions", field,
                               "<EMPTY>" if value is None else value, n])
        n_distinct = sum(1 for r in vocab_rows if r[1] == field)
        add("E1", "VOCABULARY", "INFO", "source_faithful_propositions", field, "", str(n_distinct),
            "Distinct values listed in 03_v2_vocabularies.csv (not modified)")

    # ---- 7. sanity checks (presence only; no relations created) ----
    cur = con.execute("SELECT * FROM source_faithful_propositions ORDER BY prop_id")
    cols = [d[0] for d in cur.description]
    props = [{c: ("" if v is None else v) for c, v in zip(cols, row)} for row in cur.fetchall()]

    def text(r):
        return " ".join(r[f] for f in DATA_FIELDS)

    def ids(rs):
        return "|".join(r["prop_id"] for r in rs)

    def set_status(rs):
        return "set_status=" + "|".join(sorted({r["set_status"] for r in rs})) if rs else ""

    sanity = []

    big_list = ["정원돌", "이집거", "김갑득", "김성손", "김흥득"]
    m1 = [r for r in props if r["reporting_actor"] == "자미덕" and "큰 도적" in r["predicate"]
          and all(n in text(r) for n in big_list)]
    sanity.append(["S1", "자미덕 진술: 정원돌·이집거·김갑득·김성손·김흥득 등을 큰 도적이라고 말하도록 요구받음",
                   "FOUND" if m1 else "NOT_FOUND", ids(m1), set_status(m1)])

    m2 = [r for r in props if r["claim_topic"] == "CONFRONTATION"
          and "자미덕" in r["named_entities"] and "이집거" in r["named_entities"]]
    sanity.append(["S2", "자미덕과 이집거의 대질", "FOUND" if m2 else "NOT_FOUND", ids(m2), ""])

    m3 = [r for r in props if r["reporting_actor"] == "자미덕"
          and all(w in r["predicate"] for w in ("대질", "거짓", "한 비장"))]
    sanity.append(["S3", "자미덕: 대질 때 한 비장의 지휘로 거짓으로 꾸며 말함",
                   "FOUND" if m3 else "NOT_FOUND", ids(m3), ""])

    m4 = [r for r in props if r["reporting_actor"] == "한재욱"
          and "사주" in r["predicate"] and "없" in r["predicate"]]
    sanity.append(["S4", "한재욱의 사주 부인", "FOUND" if m4 else "NOT_FOUND", ids(m4), ""])

    yu_list = ["변지돌", "변재돌", "정원돌", "김명신", "김성손", "김흥득", "김흥길"]
    m5 = [r for r in props if r["reporting_actor"] == "한재욱" and r["subject"] == "유제희"
          and all(n in r["predicate"] for n in yu_list)]
    sanity.append(["S5", "한재욱 진술 속 유제희 명단: 변지돌·변재돌·정원돌·김명신·김성손·김흥득·김흥길 등",
                   "FOUND" if m5 else "NOT_FOUND", ids(m5), set_status(m5)])

    kim = [r for r in props if "김명신" in r["named_entities"] or r["subject"] == "김명신"]
    occ = [r for r in kim if r["claim_topic"] == "DEATH_OCCURRENCE"]
    cause = [r for r in kim if r["claim_topic"] == "DEATH_CAUSE"]
    cause_words = ["병", "질병", "전염병", "형벌", "곤장", "원통"]
    occ_with_cause = [r for r in occ if any(w in r["predicate"] for w in cause_words)]
    s6_note = f"DEATH_OCCURRENCE={ids(occ)}; DEATH_CAUSE={ids(cause)}"
    if occ_with_cause:
        s6_note += ("; note: occurrence proposition(s) " + ids(occ_with_cause)
                    + " also carry cause wording in predicate (not modified)")
    sanity.append(["S6", "김명신 사망 발생과 사망 원인 판단이 별개 proposition으로 존재",
                   "FOUND" if occ and cause else "NOT_FOUND", ids(occ + cause), s6_note])

    helper = [r for r in props if "하급 보조자" in text(r)]
    helper_han = [r for r in helper if "한재욱" in text(r) or "한가" in text(r)]
    membership_hit = [r for r in csv_data["person_membership"][1] if any("하급 보조자" in c for c in r)]
    s7_ok = not helper_han and not membership_hit
    sanity.append(["S7", "병영의 하급 보조자 = 한재욱 동일시가 사실로 들어가 있지 않음",
                   "NOT_PRESENT (OK)" if s7_ok else "PRESENT", ids(helper_han),
                   f"'하급 보조자' propositions={ids(helper)}; none link it to 한재욱 in "
                   f"{'/'.join(DATA_FIELDS)}; person_membership rows mentioning it={len(membership_hit)}"
                   if s7_ok else "identification found in data fields"])

    for s in sanity:
        log.info("Sanity %s: %s -> %s [%s]", s[0], s[1], s[2], s[3])

    con.close()

    # ---- raw files unchanged ----
    for t, p in paths.items():
        after = sha256(p)
        log.info("SHA-256 after  %s: %s", TABLES[t], after)
        if after != sha_before[t]:
            add("Z1", "RAW_UNCHANGED", "ERROR", t, "", "", "", "Raw CSV changed during validation")
    with open(SHA_PATH, "w", encoding="utf-8") as f:
        for t in TABLES:
            f.write(f"{sha_before[t]}  {TABLES[t]}\n")

    # ---- write outputs ----
    write_csv(OUT_DIR / "01_v2_integrity_report.csv",
              ["check_id", "check_group", "severity", "table", "field", "row_key", "value", "message"],
              findings)
    write_csv(OUT_DIR / "02_v2_row_counts.csv",
              ["table", "csv_file", "csv_rows", "duckdb_rows", "csv_columns", "duckdb_columns",
               "status", "sha256"],
              count_rows)
    write_csv(OUT_DIR / "03_v2_vocabularies.csv", ["table", "field", "value", "row_count"], vocab_rows)
    write_csv(OUT_DIR / "04_v2_sanity_checks.csv",
              ["check_id", "description", "result", "prop_ids", "detail"], sanity)

    sev = {}
    for r in findings:
        sev[r[2]] = sev.get(r[2], 0) + 1
    n_dup = sum(1 for r in findings if r[0] == "A1" and r[2] == "ERROR")
    n_dangling = sum(1 for r in findings if r[0] in ("B1", "B2") and r[2] == "ERROR")
    log.info("Summary: ERROR=%d WARNING=%d INFO=%d PASS=%d duplicate_ids=%d dangling_refs=%d",
             sev.get("ERROR", 0), sev.get("WARNING", 0), sev.get("INFO", 0), sev.get("PASS", 0),
             n_dup, n_dangling)
    log.info("Database: %s", DB_PATH)


if __name__ == "__main__":
    main()
