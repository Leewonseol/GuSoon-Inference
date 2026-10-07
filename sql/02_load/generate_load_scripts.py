"""Oracle load 스크립트 생성기 (sql/ 전용, 기존 파이프라인을 바꾸지 않는다).

하는 일
  1. DuckDB에만 있는 Python 산출물 3개를 CSV로 내보낸다(읽기 전용):
       sql/02_load/data/episode_members.csv   ← database/gusun_clean.duckdb : episode_members
       sql/02_load/data/py_audit_findings.csv ← database/gusun_clean.duckdb : audit_findings
       sql/02_load/data/dag_freeze.csv        ← output/clean/observed_dag_freeze.json
  2. canonical CSV 25개의 실제 header로 다음을 만든다.
       sql/02_load/00_staging_tables.sql            STG_* (모든 컬럼 VARCHAR2, 긴 서술만 CLOB)
       sql/02_load/01_external_tables_or_sqlldr.sql X_* external table + STG_* 적재 INSERT … SELECT
       sql/02_load/ctl/*.ctl                        SQL*Loader control file (external table 대안)
       sql/02_load/generated/stg_inserts.sql        서버 파일 접근이 없을 때 쓰는 INSERT script

실행: python3 sql/02_load/generate_load_scripts.py   (저장소 루트에서, duckdb 모듈 필요)
같은 입력이면 같은 출력(결정적)이다. canonical CSV·DuckDB는 읽기만 한다.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "gusun_clean_restart_csv_pack"
OUT = ROOT / "output" / "clean"
DB = ROOT / "database" / "gusun_clean.duckdb"
LOAD = ROOT / "sql" / "02_load"
DATA = LOAD / "data"

# (staging table, directory alias, 파일 경로(저장소 루트 기준))
SOURCES = [
    ("STG_INPUT_MANIFEST", "GUSUN_PACK_DIR", "gusun_clean_restart_csv_pack/00_INPUT_MANIFEST.csv"),
    ("STG_CONFIRMED_FACTS", "GUSUN_PACK_DIR", "gusun_clean_restart_csv_pack/01_confirmed_facts.csv"),
    ("STG_INSTITUTIONAL_FEATURES", "GUSUN_PACK_DIR", "gusun_clean_restart_csv_pack/02_institutional_normative_features.csv"),
    ("STG_ENVIRONMENT_1793", "GUSUN_PACK_DIR", "gusun_clean_restart_csv_pack/03_environment_1793.csv"),
    ("STG_SOURCE_RECORDS", "GUSUN_PACK_DIR", "gusun_clean_restart_csv_pack/04_source_records.csv"),
    ("STG_AUDIT_PROPOSITIONS", "GUSUN_PACK_DIR", "gusun_clean_restart_csv_pack/05_source_faithful_propositions_AUDIT_ONLY.csv"),
    ("STG_EPISODE_NODES", "GUSUN_OUT_DIR", "output/clean/episode_nodes.csv"),
    ("STG_OBSERVED_EDGES", "GUSUN_OUT_DIR", "output/clean/observed_edges.csv"),
    ("STG_NODE_FEATURE_LINKS", "GUSUN_OUT_DIR", "output/clean/node_feature_links.csv"),
    ("STG_IDENTITY_REGISTER", "GUSUN_OUT_DIR", "output/clean/identity_register.csv"),
    ("STG_GAPS", "GUSUN_OUT_DIR", "output/clean/gaps.csv"),
    ("STG_LATENT_CANDIDATES", "GUSUN_OUT_DIR", "output/clean/latent_candidates.csv"),
    ("STG_LATENT_ELEMENTS", "GUSUN_OUT_DIR", "output/clean/latent_elements.csv"),
    ("STG_NARRATIVE_WORLDS", "GUSUN_OUT_DIR", "output/clean/narrative_worlds.csv"),
    ("STG_WARN_DISPOSITIONS", "GUSUN_OUT_DIR", "output/clean/warn_dispositions.csv"),
    ("STG_SD_NODES", "GUSUN_OUT_DIR", "output/clean/mechanism_super_dag_nodes.csv"),
    ("STG_SD_EDGES", "GUSUN_OUT_DIR", "output/clean/mechanism_super_dag_edges.csv"),
    ("STG_MECHANISM_DEFINITIONS", "GUSUN_OUT_DIR", "output/clean/mechanism_definitions.csv"),
    ("STG_WORLD_MECH_CONFIGS", "GUSUN_OUT_DIR", "output/clean/world_mechanism_configurations.csv"),
    ("STG_MECH_INTERACTIONS", "GUSUN_OUT_DIR", "output/clean/mechanism_interaction_matrix.csv"),
    ("STG_MECH_INTERVENTIONS", "GUSUN_OUT_DIR", "output/clean/mechanism_interventions.csv"),
    ("STG_STRUCTURAL_RULES", "GUSUN_OUT_DIR", "output/clean/qualitative_structural_rules.csv"),
    ("STG_EPISODE_MEMBERS", "GUSUN_SQLDATA_DIR", "sql/02_load/data/episode_members.csv"),
    ("STG_PY_AUDIT_FINDINGS", "GUSUN_SQLDATA_DIR", "sql/02_load/data/py_audit_findings.csv"),
    ("STG_DAG_FREEZE", "GUSUN_SQLDATA_DIR", "sql/02_load/data/dag_freeze.csv"),
]

# CSV header → Oracle 컬럼명. Oracle 예약어(BETWEEN·DESC·AUDIT)·한글·공백 header만 바꾸고 나머지는 그대로 쓴다.
RENAME = {
    "between": "between_nodes", "desc": "rule_desc", "constraint": "constraint_text", "var": "var_id",
    "아주 쉬운 설명": "easy_description", "관련 candidate": "related_candidates",
    "관련 observed node": "related_observed_nodes", "필요한 institutional feature": "required_inst_features",
    "관련 environment feature": "related_env_features", "evidence status": "evidence_status", "비고": "remarks",
    "mechanism A": "mechanism_a_id", "mechanism B": "mechanism_b_id", "이유": "reason",
    "충돌하는 candidate/edge": "conflicting_items", "같이 있을 때 설명되는 것": "explained_together",
    "mechanism_a": "mechanism_a_name", "mechanism_b": "mechanism_b_name",
}
CLOB_COLS = {("STG_NARRATIVE_WORLDS", "narrative")}
CHUNK = 200  # SQL*Plus 한 줄 길이 제한을 피하려고 긴 literal을 '...' || '...'로 나눈다


def export_python_only_tables():
    """DuckDB·JSON에만 있는 Python 산출물을 CSV(CRLF, canonical CSV와 같은 형식)로 내보낸다."""
    import duckdb
    DATA.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB), read_only=True)
    rows = con.execute("SELECT episode_id, fact_id, clause FROM episode_members").fetchall()
    with open(DATA / "episode_members.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["episode_id", "member_seq", "fact_id", "clause"])
        seq = {}
        for ep, fid, clause in rows:  # DuckDB 삽입 순서 = build.py의 EPISODES·members 순서
            seq[ep] = seq.get(ep, 0) + 1
            w.writerow([ep, seq[ep], fid, clause or ""])
    rows = con.execute("SELECT audit, check_name, severity, target, message FROM audit_findings").fetchall()
    with open(DATA / "py_audit_findings.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["finding_seq", "audit_name", "check_name", "severity", "target", "message"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, *["" if v is None else v for v in r]])
    con.close()
    fz = json.loads((OUT / "observed_dag_freeze.json").read_text(encoding="utf-8"))
    with open(DATA / "dag_freeze.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        cols = ["name", "sha256", "structure_sha256", "topology_sha256", "n_nodes", "n_edges",
                "n_episode_nodes", "n_env_nodes", "latent_count"]
        w.writerow(["freeze_name"] + cols[1:])
        w.writerow([fz[c] for c in cols])


def header(path):
    with open(ROOT / path, encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f))


def rows(path):
    with open(ROOT / path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))[1:]


def oracle_cols(path):
    return [RENAME.get(h, h).upper() for h in header(path)]


BANNER = """-- =============================================================================
-- {title}
-- 이 파일은 sql/02_load/generate_load_scripts.py가 canonical CSV header로 생성했다. 손으로 고치지 말 것.
-- Oracle runtime에서 실행 검증되지 않았다(Oracle runtime unavailable) — sql/README.md §실행 상태 참고.
-- =============================================================================
"""


def gen_staging():
    out = [BANNER.format(title="STAGING 테이블 STG_* — CSV를 문자 그대로 받는 착지(landing) 영역")]
    out.append("""-- 원칙
--   * 모든 컬럼은 VARCHAR2(4000 BYTE)로 받는다(형 변환은 04_transform_to_canonical.sql에서 한다).
--   * 길이가 4000 byte에 가까운 서술(narrative_worlds.narrative)만 CLOB.
--   * CSV의 빈 문자열('')은 Oracle에서 NULL이 된다. Oracle은 ''와 NULL을 구분하지 않는다(SQLD 단골 함정).
--   * 제약조건은 걸지 않는다. 검증은 canonical 테이블의 제약과 03_load_validation.sql이 맡는다.
""")
    for stg, _, path in SOURCES:
        cols = oracle_cols(path)
        body = []
        for c in cols:
            typ = "CLOB" if (stg, c.lower()) in CLOB_COLS else "VARCHAR2(4000 BYTE)"
            body.append(f"    {c:<26} {typ}")
        out.append(f"-- 원본: {path}  ({len(rows(path))}행)\nCREATE TABLE {stg} (\n" + ",\n".join(body) + "\n);\n")
    (LOAD / "00_staging_tables.sql").write_text("\n".join(out), encoding="utf-8")


def gen_external():
    out = [BANNER.format(title="LOAD 방법 A — EXTERNAL TABLE(ORACLE_LOADER) → STG_* / 방법 B — SQL*Loader(ctl/)")]
    out.append("""-- 준비(DBA 권한, 한 번만). 경로는 Oracle 서버(또는 컨테이너) 안에서 보이는 경로로 바꾼다.
--   예: docker run -v $PWD:/repo ... gvenzl/oracle-free  → '/repo/...'
-- CREATE OR REPLACE DIRECTORY GUSUN_PACK_DIR    AS '/repo/gusun_clean_restart_csv_pack';
-- CREATE OR REPLACE DIRECTORY GUSUN_OUT_DIR     AS '/repo/output/clean';
-- CREATE OR REPLACE DIRECTORY GUSUN_SQLDATA_DIR AS '/repo/sql/02_load/data';
-- GRANT READ, WRITE ON DIRECTORY GUSUN_PACK_DIR    TO gusun;
-- GRANT READ, WRITE ON DIRECTORY GUSUN_OUT_DIR     TO gusun;
-- GRANT READ, WRITE ON DIRECTORY GUSUN_SQLDATA_DIR TO gusun;
--
-- CSV 형식(실측): UTF-8, 줄 끝 CRLF(0x0D0A), 첫 줄 header, pack 6개 파일은 BOM 포함(header 줄이라 SKIP 1로 건너뜀),
--                 필드 안 줄바꿈 없음, 필드 안 큰따옴표 없음 → 'FIELDS CSV WITH EMBEDDED'(12.2+) 없이도 읽힌다.
-- REJECT LIMIT 0: 한 줄이라도 못 읽으면 SELECT가 실패한다(조용한 누락 방지).
""")
    for stg, d, path in SOURCES:
        x = "X_" + stg[4:]
        cols = oracle_cols(path)
        fname = path.rsplit("/", 1)[1]
        coldef = ",\n".join(f"    {c:<26} VARCHAR2(4000 BYTE)" for c in cols)
        fields = ",\n".join(f"            {'\"' + c + '\"':<28} CHAR(4000)" for c in cols)   # 큰따옴표: 접근 파라미터 예약어(VALUE 등) 충돌 방지
        out.append(f"""-- {path}
CREATE TABLE {x} (
{coldef}
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY {d}
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY 0x'0D0A'
        CHARACTERSET AL32UTF8
        SKIP 1
        NOBADFILE NODISCARDFILE NOLOGFILE
        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        MISSING FIELD VALUES ARE NULL
        (
{fields}
        )
    )
    LOCATION ('{fname}')
)
REJECT LIMIT 0;
""")
    out.append("-- external table → staging (컬럼 순서가 같으므로 SELECT * 가능)")
    for stg, _, path in SOURCES:
        out.append(f"INSERT INTO {stg} SELECT * FROM X_{stg[4:]};")
    out.append("COMMIT;\n")
    out.append("""-- 방법 B: SQL*Loader (서버 DIRECTORY 권한이 없을 때). 저장소 루트에서 실행한다.
--   sqlldr userid=gusun/비밀번호@//localhost:1521/FREEPDB1 control=sql/02_load/ctl/stg_confirmed_facts.ctl
--   (ctl 파일 25개. 각 파일은 같은 STG_* 테이블에 APPEND한다.)
-- 방법 C: 순수 INSERT script — @sql/02_load/generated/stg_inserts.sql (파일 접근·sqlldr 없이 SQL*Plus/SQLcl만으로)
""")
    (LOAD / "01_external_tables_or_sqlldr.sql").write_text("\n".join(out), encoding="utf-8")


def gen_ctl():
    d = LOAD / "ctl"
    d.mkdir(parents=True, exist_ok=True)
    for stg, _, path in SOURCES:
        cols = oracle_cols(path)
        fields = ",\n".join(f"  {'\"' + c + '\"':<28} CHAR(4000)" for c in cols)
        (d / f"{stg.lower()}.ctl").write_text(f"""-- generate_load_scripts.py 생성. 저장소 루트에서 실행: sqlldr userid=... control=sql/02_load/ctl/{stg.lower()}.ctl
OPTIONS (SKIP=1, ERRORS=0)
LOAD DATA
CHARACTERSET AL32UTF8
INFILE '{path}' "STR X'0D0A'"
APPEND
INTO TABLE {stg}
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
{fields}
)
""", encoding="utf-8")


def lit(v, clob=False):
    if v == "":
        return "NULL"
    # 먼저 자르고 나서 작은따옴표를 이중화한다('' 가 두 조각으로 갈라지지 않게)
    parts = [v[i:i + CHUNK].replace("'", "''") for i in range(0, len(v), CHUNK)]
    wrap = (lambda p: f"TO_CLOB('{p}')") if clob else (lambda p: f"'{p}'")
    return ("\n        || ").join(wrap(p) for p in parts)


def gen_inserts():
    d = LOAD / "generated"
    d.mkdir(parents=True, exist_ok=True)
    out = [BANNER.format(title="LOAD 방법 C — STG_* INSERT script (서버 파일 접근 없이 실행)")]
    out.append("""SET DEFINE OFF
SET SQLBLANKLINES ON
-- 클라이언트 문자셋이 UTF-8이어야 한글이 깨지지 않는다(예: export NLS_LANG=AMERICAN_AMERICA.AL32UTF8).
-- 빈 CSV 값은 NULL로 넣는다(Oracle에서 ''는 NULL과 같다).
""")
    total = 0
    for stg, _, path in SOURCES:
        cols = oracle_cols(path)
        rs = rows(path)
        total += len(rs)
        out.append(f"-- {path} ({len(rs)}행)")
        for r in rs:
            vals = ",\n    ".join(lit(v, (stg, c.lower()) in CLOB_COLS) for c, v in zip(cols, r))
            out.append(f"INSERT INTO {stg} ({', '.join(cols)})\nVALUES (\n    {vals}\n);")
        out.append("")
    out.append(f"COMMIT;\n-- 합계 {total}행\n")
    (d / "stg_inserts.sql").write_text("\n".join(out), encoding="utf-8")


def main():
    export_python_only_tables()
    gen_staging()
    gen_external()
    gen_ctl()
    gen_inserts()
    for stg, _, path in SOURCES:
        print(f"{stg:<28} {len(rows(path)):>4}행  {path}")


if __name__ == "__main__":
    main()
