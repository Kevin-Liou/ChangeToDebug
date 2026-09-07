"""一鍵跑完 tests/ 底下所有 check_*.py，各自獨立行程，最後列總表。

    python tests/run_checks.py            全部
    python tests/run_checks.py anchors    只跑名字含 anchors 的
"""
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")      # Windows 主控台預設 cp1252，印中文會炸
except Exception:                                  # pragma: no cover
    pass

HERE = Path(__file__).resolve().parent
pattern = sys.argv[1] if len(sys.argv) > 1 else ""
scripts = sorted(p for p in HERE.glob("check_*.py") if pattern in p.stem)
if not scripts:
    print(f"找不到符合「{pattern}」的檢查")
    sys.exit(2)

env = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
results = []
for script in scripts:
    print(f"\n{'#' * 70}\n# {script.name}\n{'#' * 70}")
    started = time.time()
    code = subprocess.run([sys.executable, str(script)], cwd=str(HERE), env=env).returncode
    results.append((script.name, code, time.time() - started))

print(f"\n{'=' * 70}")
bad = 0
for name, code, took in results:
    print(f"  {'PASS' if code == 0 else 'FAIL'}  {name:28} {took:5.1f}s")
    bad += code != 0
print(f"{'=' * 70}\n{len(results) - bad}/{len(results)} 通過")
sys.exit(1 if bad else 0)
