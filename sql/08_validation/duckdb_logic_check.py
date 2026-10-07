"""DuckDB 논리 에뮬레이션 — Oracle 실행이 아니다.

Oracle 서버가 없는 환경에서 sql/ 의 SQL '논리'(제약조건이 실제 데이터와 맞는지, 적재 변환·audit 질의가
기대한 행을 돌려주는지)를 최대한 확인하려고 만든 도구다. Oracle SQL을 텍스트 치환과 DuckDB 매크로로
DuckDB에서 돌린다. 다음은 확인하지 못한다(= Oracle에서 따로 확인해야 한다).
  * Oracle 고유 문법 자체의 수용 여부(파서·옵티마이저·권한·external table·SQL*Loader)
  * CONNECT BY 계층형 질의(DuckDB에 없음) → 06_graph·계층형 drill은 실행하지 않고 건너뛴다
  * UNPIVOT 다중 컬럼 문법 → world_mechanism_config는 같은 의미의 UNION ALL로 바꿔 넣는다
  * Oracle 정규식 엔진과 RE2의 미세한 차이, ''=NULL 의미 차이(적재 데이터는 빈 값을 NULL로 넣어 맞춤)
  * 가상 컬럼에 건 FK(DuckDB 미지원) → 같은 내용을 별도 질의로 검사

실행: python3 sql/08_validation/duckdb_logic_check.py [--verbose]   (저장소 루트, duckdb 모듈 필요)
결과 요약은 표준 출력으로 낸다. 기존 산출물·DB 파일은 읽지도 쓰지도 않는다(메모리 DB만 사용).
"""
import re
import sys
from pathlib import Path

import logging
import tempfile

import duckdb

logging.getLogger("sqlglot").setLevel(logging.ERROR)

ROOT = Path(__file__).resolve().parents[2]
SQL = ROOT / "sql"
VERBOSE = "--verbose" in sys.argv

MACROS = """
CREATE MACRO nvl(a, b) AS coalesce(a, b);
CREATE MACRO nvl2(a, b, c) AS CASE WHEN a IS NOT NULL THEN b ELSE c END;
CREATE MACRO to_number(x) AS CAST(x AS DOUBLE);
CREATE MACRO to_clob(x) AS x;
CREATE MACRO regexp_like(s, p) AS regexp_matches(s, p);
CREATE MACRO regexp_count(s, p) AS len(regexp_extract_all(s, p));
CREATE MACRO regexp_substr(s, p) AS CASE WHEN regexp_matches(s, p) THEN regexp_extract(s, p) END,  -- Oracle: 불일치 → NULL
                           (s, p, pos, occ) AS regexp_extract_all(substr(s, pos), p)[occ],
                           (s, p, pos, occ, mode, grp) AS nullif(regexp_extract_all(substr(s, pos), p, grp)[occ], '');
CREATE MACRO instr(s, sub) AS strpos(s, sub);
CREATE TABLE dual (dummy VARCHAR);
INSERT INTO dual VALUES ('X');
CREATE TABLE rowgen_10 AS SELECT range AS n FROM range(1, 11);
CREATE TABLE rowgen_20 AS SELECT range AS n FROM range(1, 21);
"""


def strip_comments(sql):
    out = []
    for line in sql.splitlines():
        # 문자열 안의 '--'는 없다고 가정(이 저장소의 SQL은 그렇게 작성했다)
        i = line.find("--")
        out.append(line if i < 0 else line[:i])
    return "\n".join(out)


def split_statements(sql):
    """세미콜론으로 문장을 나눈다(문자열 안의 ;는 고려)."""
    stmts, buf, q = [], [], False
    for ch in sql:
        if ch == "'":
            q = not q
        if ch == ";" and not q:
            s = "".join(buf).strip()
            if s:
                stmts.append(s)
            buf = []
        else:
            buf.append(ch)
    s = "".join(buf).strip()
    if s:
        stmts.append(s)
    return stmts


ROWGEN = re.compile(r"\(\s*SELECT\s+LEVEL\s+AS\s+n\s+FROM\s+dual\s+CONNECT\s+BY\s+LEVEL\s*<=\s*(\d+)\s*\)", re.I)
INSERT_ALL = re.compile(r"^\s*INSERT\s+ALL\s+(.*)\s+SELECT\s+\*\s+FROM\s+dual\s*$", re.I | re.S)
DDL = re.compile(r"^\s*(CREATE\s+(TABLE|INDEX|UNIQUE)|ALTER\s|COMMENT\s)", re.I)
ORACLE_ONLY = re.compile(r"\bPIVOT\b|\bUNPIVOT\b|\buser_constraints\b|\bTO_CHAR\s*\(|\bROWNUM\b|\bRATIO_TO_REPORT\b|\bLENGTHB\b|\bKEEP\s*\(|\bLNNVL\b|\bCYCLE\s+\w+\s+SET\b|\bv_dag_reachability\b", re.I)

# Oracle CONNECT BY로 쓴 cycle 검사(audit_2 A2-24)를 같은 의미의 DuckDB 재귀 CTE로 바꿔 끼운다
CYCLE_ORACLE = re.compile(r"SELECT\s+'acyclicity'.*$", re.S)
# 단순 경로만 따라간다(경로에 이미 있는 node로는 가지 않음, 출발 node로 돌아오는 것만 허용) → 유한.
# 출발 node로 돌아온 경로가 있으면 cycle이다. (Oracle의 행 수 의미와 같지는 않고 '0인가'만 같다)
WALK = """WITH RECURSIVE walk(start_node, node, path) AS (
            SELECT src, dst, '>' || src || '>' || dst || '>' FROM dag_edge
            UNION ALL
            SELECT w.start_node, e.dst, w.path || e.dst || '>'
              FROM walk w JOIN dag_edge e ON e.src = w.node
             WHERE w.node <> w.start_node
               AND (strpos(w.path, '>' || e.dst || '>') = 0 OR e.dst = w.start_node))"""
CYCLE_DUCKDB = """SELECT 'acyclicity', 'ERROR', 'graph', 'cycle: ' || MIN(start_node)
  FROM (""" + WALK + """
        SELECT start_node FROM walk WHERE node = start_node)
HAVING COUNT(*) > 0"""


# 불변식·기대값의 cycle 수 서브쿼리(Oracle CONNECT BY) → DuckDB 재귀 CTE
CYCLE_SUB_ORACLE = "(SELECT 1 FROM dag_edge WHERE CONNECT_BY_ISCYCLE = 1 CONNECT BY NOCYCLE PRIOR dst = src)"
CYCLE_SUB_DUCKDB = "(" + WALK + " SELECT 1 FROM walk WHERE node = start_node)"


def regex_translate(s):
    s = re.sub(r"\bVARCHAR2\s*\(\s*\d+\s*(?:CHAR|BYTE)?\s*\)", "VARCHAR", s, flags=re.I)
    s = re.sub(r"\bCHAR\s*\(\s*\d+\s*\)", "VARCHAR", s, flags=re.I)
    s = re.sub(r"\bNUMBER\s*\(\s*\d+\s*\)", "BIGINT", s, flags=re.I)
    s = re.sub(r"\bNUMBER\b", "DOUBLE", s, flags=re.I)
    s = re.sub(r"\bCLOB\b", "VARCHAR", s, flags=re.I)
    s = re.sub(r"TIMESTAMP\s*\(\s*6\s*\)", "TIMESTAMP", s, flags=re.I)
    s = re.sub(r"DEFAULT\s+TRUNC\s*\(\s*SYSDATE\s*\)", "DEFAULT current_date", s, flags=re.I)
    s = re.sub(r"DEFAULT\s+SYSTIMESTAMP", "DEFAULT current_timestamp", s, flags=re.I)
    return s


def glot_translate(s):
    """Oracle → DuckDB. '||'는 NULL을 빈 문자열로 보는 Oracle 의미에 맞춰 concat()으로 바꾼다."""
    import sqlglot
    from sqlglot import exp
    tree = sqlglot.parse_one(s, read="oracle")
    tree = tree.transform(lambda n: exp.Anonymous(this="concat", expressions=[n.left, n.right])
                          if isinstance(n, exp.DPipe) else n)
    return tree.sql(dialect="duckdb")


def translate(stmt):
    """하나의 Oracle 문장 → DuckDB 문장 목록."""
    m = INSERT_ALL.match(stmt)
    if m:  # INSERT ALL INTO t VALUES (...) ... → 여러 INSERT (DuckDB는 INSERT ALL이 없다)
        parts = [p.strip() for p in re.split(r"\bINTO\s+", m.group(1)) if p.strip()]
        return [regex_translate("INSERT INTO " + p) for p in parts]
    s = ROWGEN.sub(lambda m: f"(SELECT n FROM rowgen_{m.group(1)})", stmt)
    s = s.replace(CYCLE_SUB_ORACLE, CYCLE_SUB_DUCKDB)
    s = CYCLE_ORACLE.sub(CYCLE_DUCKDB, s) if "'acyclicity'" in s else s
    if DDL.match(s):
        return [regex_translate(s)]
    try:
        return [glot_translate(s)]
    except Exception:  # noqa: BLE001 — sqlglot이 못 읽으면 정규식 변환만
        return [regex_translate(s)]


class Emu:
    def __init__(self, with_fk=True):
        self.with_fk = with_fk  # 결함 주입용 사본은 FK 없이 만든다(DuckDB는 FK 부모 행 UPDATE를 막는다)
        # 메모리 DB. 임시 파일(.tmp)을 저장소 안에 만들지 않도록 시스템 임시 폴더를 쓴다
        self.con = duckdb.connect(config={"temp_directory": tempfile.gettempdir(), "max_temp_directory_size": "1GB"})
        self.con.execute(MACROS)
        self.tables = {}        # name → [column/inline-constraint defs]
        self.post_checks = []   # 가상 컬럼 FK (DuckDB 미지원) → 별도 검사
        self.failures = []

    def run(self, stmt, label=""):
        try:
            r = None
            for t in translate(stmt):
                r = self.con.execute(t).fetchall()
            return r
        except Exception as e:  # noqa: BLE001
            self.failures.append((label, str(e).splitlines()[0], stmt[:200]))
            return None

    # ---------------------------------------------------------------- schema
    def load_schema(self):
        tables = split_statements(strip_comments((SQL / "01_schema/01_tables.sql").read_text()))
        cons = split_statements(strip_comments((SQL / "01_schema/02_constraints.sql").read_text()))
        virtual = {}
        for t in tables:
            m = re.match(r"CREATE\s+TABLE\s+(\w+)\s*\((.*)\)\s*$", t, re.S | re.I)
            name, body = m.group(1).lower(), m.group(2)
            self.tables[name] = [body]
            virtual[name] = {v.lower() for v in re.findall(r"(\w+)\s+VARCHAR2\(\d+\)\s+GENERATED", body)}
        for c in cons:
            m = re.match(r"ALTER\s+TABLE\s+(\w+)\s+ADD\s+CONSTRAINT\s+(\w+)\s+(.*)$", c, re.S | re.I)
            tname, cname, rest = m.group(1).lower(), m.group(2), m.group(3).strip()
            fk = re.match(r"FOREIGN\s+KEY\s*\(([^)]*)\)\s*REFERENCES\s+(\w+)\s*\(([^)]*)\)", rest, re.I)
            if fk and not self.with_fk:
                continue
            if fk and {x.strip().lower() for x in fk.group(1).split(",")} & virtual[tname]:
                self.post_checks.append((cname, tname, fk.group(1), fk.group(2), fk.group(3)))
                continue
            self.tables[tname].append(f"CONSTRAINT {cname} {rest}")
        for name, parts in self.tables.items():
            self.run(f"CREATE TABLE {name} (" + ",\n".join(parts) + ")", f"create {name}")

    def check_virtual_fks(self):
        bad = []
        for cname, t, cols, parent, pcols in self.post_checks:
            q = (f"SELECT COUNT(*) FROM {t} c WHERE c.{cols} IS NOT NULL AND NOT EXISTS "
                 f"(SELECT 1 FROM {parent} p WHERE p.{pcols} = c.{cols})")
            r = self.run(q, cname)
            if r and r[0][0]:
                bad.append((cname, r[0][0]))
        return bad

    # ---------------------------------------------------------------- load
    def load_staging(self):
        for s in split_statements(strip_comments((SQL / "02_load/00_staging_tables.sql").read_text())):
            self.run(s, "staging ddl")
        text = (SQL / "02_load/generated/stg_inserts.sql").read_text()
        text = "\n".join(l for l in text.splitlines() if not re.match(r"\s*SET\s+(DEFINE|SQLBLANKLINES)", l, re.I))
        for s in split_statements(strip_comments(text)):
            if s.upper() != "COMMIT":
                self.run(s, "stg insert")

    def run_file(self, rel, skip_upto=None, stop_at=None, unpivot_fix=False):
        text = (ROOT / rel if rel.startswith("sql/") else SQL / rel).read_text()
        if stop_at:
            text = text.split(stop_at)[0]
        text = strip_comments(text)
        text = "\n".join(l for l in text.splitlines() if not re.match(r"\s*SET\s+(DEFINE|SQLBLANKLINES)", l, re.I))
        results = []
        for s in split_statements(text):
            if re.match(r"(COMMIT|SAVEPOINT|ROLLBACK)\b", s, re.I):
                continue
            if unpivot_fix and "UNPIVOT" in s.upper():
                s = UNPIVOT_EQUIV
            rest = ROWGEN.sub("", s).replace(CYCLE_SUB_ORACLE, "")
            rest = CYCLE_ORACLE.sub("", rest) if "'acyclicity'" in s else rest
            if re.search(r"\bCONNECT\s+BY\b|\bPRIOR\b|\bSTART\s+WITH\b", rest, re.I):
                results.append((s, "SKIPPED_CONNECT_BY", None))
                continue
            if ORACLE_ONLY.search(s):
                results.append((s, "SKIPPED_ORACLE_ONLY", None))
                continue
            r = self.run(s, rel)
            results.append((s, "OK" if r is not None else "FAILED", r))
        return results


UNPIVOT_EQUIV = " UNION ALL ".join(
    f"SELECT world_id, '{m}', {m}, {m}_basis FROM stg_world_mech_configs" for m in
    ["M1", "M2", "M3", "M4", "M5", "M6", "MB"])
UNPIVOT_EQUIV = "INSERT INTO world_mechanism_config (world_id, mechanism_id, config_value, config_basis) " + UNPIVOT_EQUIV


# 결함 주입(mutation) — Python regression.py처럼 '검사기가 결함을 실제로 잡는가'를 본다.
# 각 항목: (설명, DuckDB SQL 목록, 반드시 나와야 하는 (audit, check_name, severity))
MUTATIONS = [
    ("필수 관계 OE056(EP15 REVISES EP25) 삭제",
     ["DELETE FROM edge_basis_type WHERE edge_id = 'OE056'", "DELETE FROM edge_source_basis WHERE edge_id = 'OE056'",
      "DELETE FROM dag_edge WHERE edge_id = 'OE056'"],
     ("AUDIT2", "missing_relation", "ERROR")),
    ("구순 관계(EP01) → 김명신 구금·사망 보고(EP13) 직접 RESPONSIBILITY_LINK 추가",
     ["INSERT INTO dag_edge (edge_id, src, dst, edge_type, basis, status, claim_level, supporting, rationale) "
      "VALUES ('OE900', 'EP01', 'EP13', 'RESPONSIBILITY_LINK', 'SOURCE_DIRECT', 'DERIVED', 'False', 'CF001', 'x')",
      "INSERT INTO edge_basis_type VALUES ('OE900', 'SOURCE_DIRECT', 1)",
      "INSERT INTO edge_source_basis (edge_id, support_id, support_seq) VALUES ('OE900', 'CF001', 1)"],
     ("AUDIT2", "causal_inflation", "ERROR")),
    ("6/16 유임(EP37) → 관계 변화(EP01) TEMPORAL_BEFORE 추가 (시간 역전 + cycle)",
     ["INSERT INTO dag_edge (edge_id, src, dst, edge_type, basis, status, claim_level, supporting, rationale) "
      "VALUES ('OE901', 'EP37', 'EP01', 'TEMPORAL_BEFORE', 'TEMPORAL', 'DERIVED', 'False', 'CF001', 'x')",
      "INSERT INTO edge_basis_type VALUES ('OE901', 'TEMPORAL', 1)",
      "INSERT INTO edge_source_basis (edge_id, support_id, support_seq) VALUES ('OE901', 'CF001', 1)"],
     ("AUDIT2", "acyclicity", "ERROR")),
    ("위와 같은 결함 — 시간 역전 검사",
     ["INSERT INTO dag_edge (edge_id, src, dst, edge_type, basis, status, claim_level, supporting, rationale) "
      "VALUES ('OE901', 'EP37', 'EP01', 'TEMPORAL_BEFORE', 'TEMPORAL', 'DERIVED', 'False', 'CF001', 'x')",
      "INSERT INTO edge_basis_type VALUES ('OE901', 'TEMPORAL', 1)",
      "INSERT INTO edge_source_basis (edge_id, support_id, support_seq) VALUES ('OE901', 'CF001', 1)"],
     ("AUDIT2", "temporal_inversion", "ERROR")),
    ("OE010의 미확정 동일성 condition(ID08) 제거",
     ["DELETE FROM edge_identity_condition WHERE edge_id = 'OE010'"],
     ("AUDIT2", "identity_forcing", "ERROR")),
    ("근거 없는 DERIVED edge (OE001 근거 삭제)",
     ["DELETE FROM edge_source_basis WHERE edge_id = 'OE001'"],
     ("AUDIT2", "unsupported_edge", "ERROR")),
    ("후보 G01a를 final HIGH로 부풀림",
     ["UPDATE latent_candidate SET overall = 'HIGH' WHERE candidate_id = 'G01a'"],
     ("AUDIT3", "bridge_support_inflation", "ERROR")),
    ("EP01 summary에서 진술 표지 삭제('진술했' → '말했')",
     ["UPDATE dag_node SET summary = replace(summary, '진술했', '말했') WHERE node_id = 'EP01'"],
     ("AUDIT1", "testimony_to_fact", "ERROR")),
    ("EP29 caution에 책임 → 직접 사인 단정 문장 추가",
     ["UPDATE dag_node SET caution = '구순 때문에 김명신이 죽었다' WHERE node_id = 'EP29'"],
     ("AUDIT1", "responsibility_to_causation", "ERROR")),
    ("EP07 summary에서 원문 표면형 '한 비장'을 '한재욱'으로 치환",
     ["UPDATE dag_node SET summary = replace(summary, '한 비장', '한재욱') WHERE node_id = 'EP07'"],
     ("AUDIT1", "surface_form_substitution", "ERROR")),
    ("사용자가 열어 둔 gap G10을 W1이 G10a로 채움",
     ["INSERT INTO world_candidate VALUES ('W1', 'G10a', 'G10', 13)"],
     ("AUDIT3", "open_gap_filled", "ERROR")),
    ("W5 narrative에서 [L] 표지 삭제",
     ["UPDATE narrative_world SET narrative = replace(narrative, '[L]', '') WHERE world_id = 'W5'"],
     ("AUDIT3", "latent_as_observed", "ERROR")),
    ("W1의 M1 configuration을 UNSPECIFIED로 (M1 후보를 쓰는데)",
     ["UPDATE world_mechanism_config SET config_value = 'UNSPECIFIED' WHERE world_id = 'W1' AND mechanism_id = 'M1'"],
     ("AUDIT4", "config_value", "ERROR")),
    ("제도 피쳐(CTX_F001)가 관측 사건(EP04)을 직접 만드는 Super-DAG edge 추가",
     ["INSERT INTO sd_edge VALUES ('SD900', 'CTX_F001', 'EP04', 'CONSTRAINS', 'CONTEXT', 'SUPER_DAG', 'x')"],
     ("AUDIT4", "institution_to_event", "ERROR")),
    ("W6(REJECTED)을 개입 분석 대상 world에 넣음",
     ["UPDATE mechanism_intervention SET affected_worlds = affected_worlds || ', W6' WHERE mechanism_id = 'M1' AND variable = 'V_COMMAND_SOURCE'"],
     ("AUDIT4", "w6_reactivation", "ERROR")),
]


def run_mutations(emu):
    con = emu.con
    base = con.execute("SELECT COUNT(*) FROM v_sql_audit_all WHERE severity IN ('ERROR', 'WARN')").fetchone()[0]
    print(f"== 결함 주입 검사 (기준 상태 ERROR+WARN = {base})")
    ok = 0
    for desc, stmts, (aud, chk, sev) in MUTATIONS:
        con.execute("BEGIN TRANSACTION")
        try:
            for st in stmts:
                con.execute(st)
            hits = con.execute("SELECT COUNT(*) FROM v_sql_audit_all WHERE audit_name = ? AND check_name = ? AND severity = ?",
                               [aud, chk, sev]).fetchone()[0]
            inv = con.execute("SELECT COUNT(*) FROM v_invariant_check WHERE violations > 0").fetchone()[0] \
                if con.execute("SELECT COUNT(*) FROM duckdb_views() WHERE view_name = 'v_invariant_check'").fetchone()[0] else None
        except Exception as e:  # noqa: BLE001
            hits, inv = None, None
            print(f"   [ERROR] {desc}: {str(e).splitlines()[0]}")
        con.execute("ROLLBACK")
        mark = "DETECTED" if hits else "MISSED"
        ok += bool(hits)
        print(f"   [{mark}] {desc} → {aud} {chk} {sev} {hits}건" + (f" · 불변식 위반 {inv}개" if inv else ""))
    print(f"== 결함 주입 {ok}/{len(MUTATIONS)} 탐지")


def main():
    emu = Emu()
    emu.load_schema()
    emu.load_staging()
    emu.run_file("02_load/02_insert_examples.sql", stop_at="2부. SQLD DML")
    emu.run_file("02_load/04_transform_to_canonical.sql", unpivot_fix=True)
    print("== 가상 컬럼 FK 검사:", emu.check_virtual_fks() or "위반 0")
    res = emu.run_file("02_load/03_load_validation.sql")
    for s, st, r in res:
        if st == "OK" and r and "stg_rows" not in s:
            print("[load_validation] 문제 행:", r[:5])
    for s, st, r in res:
        if "stg_rows" in s and r:
            bad = [x for x in r if x[1] != x[2]]
            print("== STG↔canonical 행 수 불일치:", bad or "없음")
    for f in sys.argv[1:]:
        if f.endswith(".sql"):
            for s, st, r in emu.run_file(f):
                head = " ".join(s.split())[:90]
                print(f"[{st}] {head}\n    → {r if r is None or len(r) <= 8 else r[:8] + ['…']}")
    if "--mutations" in sys.argv:
        mut = Emu(with_fk=False)
        mut.load_schema()
        mut.load_staging()
        mut.run_file("02_load/02_insert_examples.sql", stop_at="2부. SQLD DML")
        mut.run_file("02_load/04_transform_to_canonical.sql", unpivot_fix=True)
        for f in sys.argv[1:]:
            if f.endswith(".sql"):
                mut.run_file(f)
        run_mutations(mut)
    if emu.failures:
        print(f"== 실패 {len(emu.failures)}건")
        for lab, err, st in emu.failures[:40]:
            print("  ", lab, "|", err, "|", " ".join(st.split())[:160])
    else:
        print("== 실패 0건")
    return emu


if __name__ == "__main__":
    main()
