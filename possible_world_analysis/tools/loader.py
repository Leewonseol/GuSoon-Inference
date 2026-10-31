"""숫자로 시작하는 03_constraints.py를 모듈로 불러오는 공용 로더(보고서 생성기·테스트에서 사용)."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_constraints():
    name = "sigok_constraints"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "03_constraints.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
