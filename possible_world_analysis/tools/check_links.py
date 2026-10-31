#!/usr/bin/env python3
"""실행 시점 링크 검사기.

상태 분류(접근 실패를 '자료 부재'로 오해하지 않기 위한 구분):
  OK              2xx/3xx 응답
  AUTH_REQUIRED   대상 사이트가 401/403 응답(로그인·구독 필요 가능성)
  NOT_FOUND       대상 사이트가 404/410 응답(링크 오류 가능성; 자료 부재를 뜻하지 않음)
  NETWORK_BLOCKED 이 실행 환경의 프록시/방화벽이 연결 자체를 거부(사이트 응답 없음)
  ERROR           DNS 실패·시간 초과·TLS 오류 등 기타
  NO_URL          sources.yaml에 URL 없음(url_missing_reason 참고)

URL_OK는 '원문 검증'이 아니다. 본문 검증 수준은 sources.yaml의 text_verification이 따로 관리한다.

사용법:
  python tools/check_links.py            # 검사 후 results/link_check.json 기록
  python tools/check_links.py --write    # 위 + sources.yaml의 url_check 줄 갱신(주석 보존)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import socket
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources.yaml"
OUT = ROOT / "results" / "link_check.json"

BLOCK_MARKERS = ("tunnel connection failed", "403 forbidden", "proxy", "connect_rejected")


def classify(url: str, timeout: float = 15.0) -> tuple[str, str]:
    if not url:
        return "NO_URL", ""
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "sigok-link-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
            return "OK", f"HTTP {r.status}"
    except urllib.error.HTTPError as e:  # 대상 서버가 응답함
        if e.code in (401, 403):
            return "AUTH_REQUIRED", f"HTTP {e.code}"
        if e.code in (404, 410):
            return "NOT_FOUND", f"HTTP {e.code}"
        return "ERROR", f"HTTP {e.code}"
    except urllib.error.URLError as e:  # 서버 응답 이전 실패
        msg = str(e.reason).lower()
        if any(m in msg for m in BLOCK_MARKERS):
            return "NETWORK_BLOCKED", str(e.reason)
        return "ERROR", str(e.reason)
    except (socket.timeout, TimeoutError):
        return "ERROR", "timeout"
    except Exception as e:  # noqa: BLE001
        msg = str(e).lower()
        if any(m in msg for m in BLOCK_MARKERS):
            return "NETWORK_BLOCKED", str(e)
        return "ERROR", f"{type(e).__name__}: {e}"


def run(write: bool) -> dict:
    data = yaml.safe_load(SOURCES.read_text(encoding="utf-8"))
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = {}
    for s in data["sources"]:
        status, detail = classify(s.get("url", ""))
        results[s["source_id"]] = {"url": s.get("url", ""), "status": status, "detail": detail, "checked_at": now}
        print(f"{s['source_id']:16s} {status:16s} {detail[:70]}")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"checked_at": now, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    if write:
        lines = SOURCES.read_text(encoding="utf-8").splitlines(keepends=True)
        cur = None
        for i, ln in enumerate(lines):
            m = re.match(r"^- source_id:\s*(\S+)", ln)
            if m:
                cur = m.group(1)
            if cur and re.match(r"^\s+url_check:\s*\{", ln):
                r = results[cur]
                indent = re.match(r"^(\s*)", ln).group(1)
                lines[i] = f"{indent}url_check: {{status: {r['status']}, checked_at: '{r['checked_at']}'}}\n"
        SOURCES.write_text("".join(lines), encoding="utf-8")
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    res = run(args.write)
    counts: dict[str, int] = {}
    for v in res.values():
        counts[v["status"]] = counts.get(v["status"], 0) + 1
    print(json.dumps(counts, ensure_ascii=False))
    sys.exit(0)
