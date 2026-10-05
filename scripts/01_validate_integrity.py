#!/usr/bin/env python3
"""GuSoon dataset integrity validation (stage 1: integrity checks only).

- Loads the 5 raw CSVs into an in-memory DuckDB (all columns as VARCHAR).
- Never modifies the raw CSVs (SHA-256 is recorded before and after the run).
- Never auto-fixes anything; every problem found is written as its own row.
- Does not access source_url, does not use external knowledge, and makes no
  historical interpretation of event content.

Outputs:
  output/01_integrity_report.csv
  output/02_table_row_counts.csv
  logs/validation.log
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

TABLES = {
    "events": "gusun_events_v1.csv",
    "event_relations": "gusun_event_relations_v1.csv",
    "attestations": "gusun_attestations_v1.csv",
    "event_families": "gusun_event_families_v1.csv",
    "source_records": "gusun_source_records_v1.csv",
}

PRIMARY_KEYS = {
    "events": "event_id",
    "event_relations": "relation_id",
    "attestations": "attestation_id",
    "event_families": "event_family_id",
    "source_records": "source_record_id",
}

# Core fields: identifiers / foreign keys / structural class -> ERROR when NULL or blank,
# descriptive core fields -> WARNING when NULL or blank.
CORE_FIELDS = {
    "events": {
        "ERROR": ["event_id", "case_id", "event_family_id", "semantic_class"],
        "WARNING": ["actor", "action", "target_or_content"],
    },
    "event_relations": {
        "ERROR": ["relation_id", "relation_layer", "from_event_id", "to_event_id", "relation_type"],
        "WARNING": ["confidence"],
    },
    "attestations": {
        "ERROR": ["attestation_id", "event_id", "source_record_id"],
        "WARNING": ["report_lunar_date", "speaker_or_reporting_actor", "attestation_mode", "proposition_ko"],
    },
    "event_families": {
        "ERROR": ["event_family_id", "semantic_class"],
        "WARNING": [],
    },
    "source_records": {
        "ERROR": ["source_record_id"],
        "WARNING": ["source_work", "record_date_lunar", "source_url"],
    },
}

REPORT_COLUMNS = [
    "check_id", "check_type", "table_name", "record_id",
    "severity", "problem", "details", "recommended_action",
]

log = logging.getLogger("validation")


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(LOG_DIR / "validation.log", mode="w", encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.setLevel(logging.INFO)
    log.addHandler(fh)
    log.addHandler(sh)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_counts(path):
    """Count physical lines and parsed data records independently of DuckDB."""
    raw = path.read_bytes()
    physical_lines = raw.count(b"\n") + (0 if raw.endswith(b"\n") or not raw else 1)
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        header = next(reader)
        rows = list(reader)
    return {
        "physical_lines": physical_lines,
        "header_columns": len(header),
        "data_rows": len(rows),
        "ragged_rows": sum(1 for r in rows if len(r) != len(header)),
        "has_bom": raw.startswith(b"\xef\xbb\xbf"),
    }


class Report:
    def __init__(self):
        self.rows = []
        self.counter = {}

    def add(self, check_type, table, record_id, severity, problem, details, action):
        assert severity in ("ERROR", "WARNING", "INFO")
        n = self.counter.get(check_type, 0) + 1
        self.counter[check_type] = n
        self.rows.append({
            "check_id": f"{check_type}-{n:03d}",
            "check_type": check_type,
            "table_name": table,
            "record_id": record_id,
            "severity": severity,
            "problem": problem,
            "details": details,
            "recommended_action": action,
        })

    def passed(self, check_type, table, details):
        self.add(check_type, table, "", "INFO", "NO_ISSUE_FOUND", details, "None")


def load_tables(con):
    for table, fname in TABLES.items():
        path = RAW_DIR / fname
        # all_varchar: no type inference, values are kept as text; empty -> NULL.
        con.execute(f"""
            CREATE TABLE {table} AS
            SELECT * FROM read_csv(
                '{path.as_posix()}',
                header = true, delim = ',', quote = '"', escape = '"',
                all_varchar = true, strict_mode = true, ignore_errors = false,
                null_padding = false
            )
        """)
        log.info("Loaded %s <- %s", table, path.relative_to(ROOT))


def q(con, sql):
    return con.execute(sql).fetchall()


def check_row_counts(con, rep, csv_info):
    ct = "ROW_COUNT_MATCH"
    rows = []
    for table, fname in TABLES.items():
        info = csv_info[table]
        db_rows = q(con, f"SELECT count(*) FROM {table}")[0][0]
        db_cols = len(con.execute(f"SELECT * FROM {table} LIMIT 0").description)
        match = db_rows == info["data_rows"] and db_cols == info["header_columns"]
        rows.append({
            "table_name": table,
            "source_file": f"data/raw/{fname}",
            "sha256": info["sha256"],
            "csv_physical_lines": info["physical_lines"],
            "csv_header_columns": info["header_columns"],
            "csv_data_rows": info["data_rows"],
            "csv_ragged_rows": info["ragged_rows"],
            "duckdb_rows": db_rows,
            "duckdb_columns": db_cols,
            "row_count_match": "TRUE" if match else "FALSE",
        })
        details = (f"csv_data_rows={info['data_rows']}, duckdb_rows={db_rows}, "
                   f"csv_header_columns={info['header_columns']}, duckdb_columns={db_cols}, "
                   f"csv_ragged_rows={info['ragged_rows']}")
        if match and info["ragged_rows"] == 0:
            rep.add(ct, table, "", "INFO", "ROW_COUNT_MATCHED", details, "None")
        else:
            rep.add(ct, table, "", "ERROR", "ROW_COUNT_MISMATCH", details,
                    "Inspect raw CSV for quoting/embedded newline/column-count problems before use")
        log.info("Row count %s: %s", table, details)
    return rows


def check_event_id_duplicates(con, rep):
    ct = "DUPLICATE_EVENT_ID"
    res = q(con, """
        SELECT event_id, count(*) AS n
        FROM events WHERE event_id IS NOT NULL
        GROUP BY event_id HAVING count(*) > 1 ORDER BY event_id
    """)
    for event_id, n in res:
        rep.add(ct, "events", event_id, "ERROR", "DUPLICATE_PRIMARY_KEY",
                f"event_id appears {n} times in events",
                "Decide manually which row is canonical; do not auto-merge")
    if not res:
        rep.passed(ct, "events", "All event_id values are unique")
    log.info("%s: %d duplicated event_id", ct, len(res))
    return len(res)


def check_events_without_attestation(con, rep):
    ct = "EVENT_WITHOUT_ATTESTATION"
    res = q(con, """
        SELECT e.event_id FROM events e
        WHERE e.event_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM attestations a WHERE a.event_id = e.event_id)
        ORDER BY e.event_id
    """)
    for (event_id,) in res:
        rep.add(ct, "events", event_id, "ERROR", "EVENT_HAS_NO_ATTESTATION",
                "No attestation row references this event_id; event has no source provenance",
                "Add the missing attestation or flag the event as unsupported; do not delete automatically")
    if not res:
        rep.passed(ct, "events", "Every event has at least one attestation")
    log.info("%s: %d events", ct, len(res))
    return len(res)


def check_dangling(con, rep, ct, child, fk_col, pk_col, parent, pk_label):
    res = q(con, f"""
        SELECT c.{PRIMARY_KEYS[child]}, c.{fk_col} FROM {child} c
        WHERE c.{fk_col} IS NOT NULL AND trim(c.{fk_col}) <> ''
          AND NOT EXISTS (SELECT 1 FROM {parent} p WHERE p.{pk_col} = c.{fk_col})
        ORDER BY 1
    """)
    for rid, fk in res:
        rep.add(ct, child, rid, "ERROR", "DANGLING_REFERENCE",
                f"{child}.{fk_col}='{fk}' not found in {parent}.{pk_col}",
                f"Correct the {pk_label} reference or add the missing {parent} row; do not auto-fix")
    if not res:
        rep.passed(ct, child, f"All {child}.{fk_col} values exist in {parent}.{pk_col}")
    log.info("%s (%s.%s -> %s.%s): %d dangling", ct, child, fk_col, parent, pk_col, len(res))
    return len(res)


def check_self_loops(con, rep):
    ct = "SELF_LOOP_RELATION"
    res = q(con, """
        SELECT relation_id, relation_layer, relation_type, from_event_id
        FROM event_relations
        WHERE from_event_id IS NOT NULL AND from_event_id = to_event_id
        ORDER BY relation_id
    """)
    for rid, layer, rtype, ev in res:
        rep.add(ct, "event_relations", rid, "ERROR", "SELF_LOOP",
                f"from_event_id = to_event_id = '{ev}' (layer={layer}, type={rtype})",
                "Review relation endpoints manually")
    if not res:
        rep.passed(ct, "event_relations", "No relation has from_event_id = to_event_id")
    log.info("%s: %d", ct, len(res))
    return len(res)


def check_exact_duplicates(con, rep):
    ct = "EXACT_DUPLICATE_ROW"
    total = 0
    for table in TABLES:
        cols = [d[0] for d in con.execute(f"SELECT * FROM {table} LIMIT 0").description]
        col_list = ", ".join(f'"{c}"' for c in cols)
        pk = PRIMARY_KEYS[table]
        res = q(con, f"""
            SELECT "{pk}", count(*) AS n FROM {table}
            GROUP BY {col_list} HAVING count(*) > 1
            ORDER BY 1
        """)
        for rid, n in res:
            rep.add(ct, table, rid, "ERROR", "EXACT_DUPLICATE_ROW",
                    f"Identical row (all {len(cols)} columns) appears {n} times",
                    "Confirm the duplicate is unintended and remove it in a new data version; do not edit raw CSV")
        if not res:
            rep.passed(ct, table, f"No fully identical rows across {len(cols)} columns")
        log.info("%s %s: %d duplicate groups", ct, table, len(res))
        total += len(res)
    return total


def check_core_nulls(con, rep):
    ct = "CORE_FIELD_NULL_OR_BLANK"
    total = 0
    for table, by_sev in CORE_FIELDS.items():
        found = 0
        for severity, fields in by_sev.items():
            for col in fields:
                # rn = 1-based CSV data row (insertion order is preserved on load)
                res = q(con, f"""
                    WITH t AS (SELECT row_number() OVER () AS rn, * FROM {table})
                    SELECT rn, "{PRIMARY_KEYS[table]}", "{col}" IS NULL AS is_null
                    FROM t WHERE "{col}" IS NULL OR trim("{col}") = ''
                    ORDER BY rn
                """)
                for rn, rid, is_null in res:
                    rep.add(ct, table, rid if rid else f"(data_row={rn})", severity,
                            "NULL_VALUE" if is_null else "BLANK_VALUE",
                            f"Core field '{col}' is {'NULL/empty' if is_null else 'whitespace-only'} "
                            f"(csv data row {rn})",
                            "Fill the field from the source in a new data version or document why it is empty")
                found += len(res)
        if not found:
            rep.passed(ct, table, "No NULL/blank values in core fields: "
                       + ", ".join(by_sev["ERROR"] + by_sev["WARNING"]))
        log.info("%s %s: %d", ct, table, found)
        total += found
    return total


def find_cycles(nodes, edges):
    """Tarjan SCC (iterative). Returns SCCs with >1 node, plus self-loop nodes."""
    adj = {n: [] for n in nodes}
    for a, b, _ in edges:
        adj[a].append(b)
    index, low, on_stack, stack, sccs = {}, {}, set(), [], []
    counter = [0]
    for start in sorted(nodes):
        if start in index:
            continue
        work = [(start, iter(adj[start]))]
        index[start] = low[start] = counter[0]
        counter[0] += 1
        stack.append(start)
        on_stack.add(start)
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter[0]
                    counter[0] += 1
                    stack.append(w)
                    on_stack.add(w)
                    work.append((w, iter(adj[w])))
                    advanced = True
                    break
                elif w in on_stack:
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                sccs.append(sorted(comp))
    return [c for c in sccs if len(c) > 1]


def check_temporal_cycles(con, rep):
    ct = "TEMPORAL_PROCEDURAL_CYCLE"
    edges = q(con, """
        SELECT from_event_id, to_event_id, relation_id FROM event_relations
        WHERE relation_layer = 'TEMPORAL_PROCEDURAL'
          AND from_event_id IS NOT NULL AND to_event_id IS NOT NULL
        ORDER BY relation_id
    """)
    nodes = {a for a, _, _ in edges} | {b for _, b, _ in edges}
    self_loops = [e for e in edges if e[0] == e[1]]
    sccs = find_cycles(nodes, edges)
    log.info("%s: graph nodes=%d edges=%d, non-trivial SCCs=%d, self-loops=%d",
             ct, len(nodes), len(edges), len(sccs), len(self_loops))
    for comp in sccs:
        cs = set(comp)
        rels = [r for a, b, r in edges if a in cs and b in cs]
        rep.add(ct, "event_relations", ";".join(rels), "ERROR", "DIRECTED_CYCLE",
                f"Strongly connected component of {len(comp)} events: {', '.join(comp)}; "
                f"relations inside: {', '.join(rels)}",
                "Review direction/type of the listed TEMPORAL_PROCEDURAL relations manually")
    for a, _, rid in self_loops:
        rep.add(ct, "event_relations", rid, "ERROR", "DIRECTED_CYCLE_SELF_LOOP",
                f"TEMPORAL_PROCEDURAL self-loop on {a} (length-1 cycle)",
                "Review relation endpoints manually")
    if not sccs and not self_loops:
        rep.passed(ct, "event_relations",
                   f"TEMPORAL_PROCEDURAL graph is acyclic (nodes={len(nodes)}, edges={len(edges)}); "
                   "all relation types treated as directed from_event_id -> to_event_id")
    return bool(sccs or self_loops), len(nodes), len(edges)


def write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(rows)


def main():
    setup_logging()
    log.info("=== GuSoon integrity validation start ===")
    log.info("DuckDB version: %s", duckdb.__version__)
    log.info("Scope: integrity checks only; no auto-fix; source_url not accessed; "
             "no external knowledge; no historical interpretation")

    csv_info = {}
    for table, fname in TABLES.items():
        path = RAW_DIR / fname
        info = csv_counts(path)
        info["sha256"] = sha256(path)
        csv_info[table] = info
        log.info("Raw %s sha256=%s bom=%s physical_lines=%d data_rows=%d",
                 fname, info["sha256"], info["has_bom"], info["physical_lines"], info["data_rows"])

    for table, cols in CORE_FIELDS.items():
        log.info("Core fields %s: ERROR=%s WARNING=%s", table, cols["ERROR"], cols["WARNING"])

    con = duckdb.connect(":memory:")
    con.execute("SET threads = 1")
    con.execute("SET preserve_insertion_order = true")
    load_tables(con)
    rep = Report()

    counts = check_row_counts(con, rep, csv_info)
    dup_event_id = check_event_id_duplicates(con, rep)
    no_att = check_events_without_attestation(con, rep)
    dangling = 0
    dangling += check_dangling(con, rep, "ATTESTATION_DANGLING_EVENT_ID",
                               "attestations", "event_id", "event_id", "events", "event_id")
    dangling += check_dangling(con, rep, "RELATION_DANGLING_EVENT_ID",
                               "event_relations", "from_event_id", "event_id", "events", "event_id")
    dangling += check_dangling(con, rep, "RELATION_DANGLING_EVENT_ID",
                               "event_relations", "to_event_id", "event_id", "events", "event_id")
    dangling += check_dangling(con, rep, "DANGLING_EVENT_FAMILY_ID",
                               "events", "event_family_id", "event_family_id", "event_families",
                               "event_family_id")
    dangling += check_dangling(con, rep, "DANGLING_SOURCE_RECORD_ID",
                               "attestations", "source_record_id", "source_record_id", "source_records",
                               "source_record_id")
    self_loops = check_self_loops(con, rep)
    exact_dups = check_exact_duplicates(con, rep)
    nulls = check_core_nulls(con, rep)
    has_cycle, n_nodes, n_edges = check_temporal_cycles(con, rep)

    write_csv(OUT_DIR / "01_integrity_report.csv", REPORT_COLUMNS, rep.rows)
    write_csv(OUT_DIR / "02_table_row_counts.csv", list(counts[0].keys()), counts)

    # Confirm the raw CSVs were not modified.
    for table, fname in TABLES.items():
        after = sha256(RAW_DIR / fname)
        status = "UNCHANGED" if after == csv_info[table]["sha256"] else "CHANGED"
        log.info("Raw %s sha256 after run: %s", fname, status)
        if status != "UNCHANGED":
            log.error("Raw file %s was modified during validation", fname)

    sev = {s: sum(1 for r in rep.rows if r["severity"] == s) for s in ("ERROR", "WARNING", "INFO")}
    log.info("=== Summary ===")
    for c in counts:
        log.info("rows %s: csv=%s duckdb=%s match=%s", c["table_name"], c["csv_data_rows"],
                 c["duckdb_rows"], c["row_count_match"])
    log.info("ERROR=%d WARNING=%d INFO=%d", sev["ERROR"], sev["WARNING"], sev["INFO"])
    log.info("TEMPORAL_PROCEDURAL cycle: %s (nodes=%d, edges=%d)",
             "YES" if has_cycle else "NO", n_nodes, n_edges)
    log.info("dangling references=%d", dangling)
    log.info("duplicates: event_id=%d, exact_duplicate_row_groups=%d", dup_event_id, exact_dups)
    log.info("events_without_attestation=%d, self_loops=%d, core_null_or_blank=%d",
             no_att, self_loops, nulls)
    log.info("=== GuSoon integrity validation end ===")


if __name__ == "__main__":
    main()
