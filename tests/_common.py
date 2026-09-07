"""tests 共用：路徑、檢查小工具、合成的迷你 profile 與假 BIOS 樹。

所有檢查都在暫存目錄裡跑。`redirect_conflicts()` 把衝突產物導到暫存目錄，
GUI 檢查用 `Settings(path=暫存檔)`，所以不會碰到工具目錄的設定、log 或衝突資料夾，
也不會碰到使用者真實的 BIOS 工作樹。
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:       # pragma: no cover
    pass

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from changetodebug.core.logbus import Logger                     # noqa: E402


# ---------------------------------------------------------------- 檢查小工具

class Checker:
    """print 一行 OK/*** 並累積失敗；finish() 依結果決定 exit code。"""

    def __init__(self):
        self.fail = []

    def __call__(self, tag, cond, detail=""):
        print(f"  {'OK ' if cond else '***'} {tag}{('  ' + str(detail)) if detail else ''}")
        if not cond:
            self.fail.append(tag)
        return cond

    def section(self, title):
        print(f"\n=== {title} ===")

    def finish(self, name):
        print()
        if self.fail:
            print(f"*** {name}：{len(self.fail)} 項未通過 ***")
            for f in self.fail:
                print("   -", f)
            sys.exit(1)
        print(f"{name}：全部通過")


def logger_pair():
    logs = []
    return logs, Logger(sink=lambda lv, m: logs.append(m), log_file=None, echo_stdout=False)


def quiet_logger():
    return Logger(sink=None, log_file=None, echo_stdout=False)


def sandbox(prefix="ctd_test_"):
    return Path(tempfile.mkdtemp(prefix=prefix))


def redirect_conflicts(tmp):
    """把 ChangeToDebug_conflicts 導到暫存目錄；回傳那個目錄。"""
    from changetodebug.core import conflicts
    box = Path(tmp) / "app"
    box.mkdir(parents=True, exist_ok=True)
    conflicts.app_dir = lambda: box
    return box


# ---------------------------------------------------------------- 迷你 profile

FOO_INF = """[Defines]
  BASE_NAME = Foo

[Packages]
  MdePkg/MdePkg.dec

[LibraryClasses]
   HpGpioLib
   PcdLib

[Guids]

[Pcd]
   gTok.PcdX
"""

FOO_C = """#include <A.h>
#include <B.h>

//---------------------------------

EFI_STATUS
Foo (
  VOID
  )
{
  EFI_STATUS Status;
  Status = Init ();
  return Status;
}

VOID
Bar (
  VOID
  )
{
}
"""

DSC = """[Defines]
  DEFINE DBG = FALSE
  DEFINE OTHER = 1
"""

REL_INF = "HpPlatformPkg/MultiProject/ZAAPkg/Library/Foo/Foo.inf"
REL_C = "HpPlatformPkg/MultiProject/ZAAPkg/Library/Foo/Foo.c"
REL_DSC_A = "HpPlatformPkg/MultiProject/ZAAPkg/ZAAPkgConfig.dsc"
REL_DSC_B = "HpPlatformPkg/MultiProject/ZBBPkg/ZBBPkgConfig.dsc"
DETECT_DIR = ".gitman/Intel/MiniPkg"

#: (區塊, 目標, label, old_code, new_code)。四條規則涵蓋 sub_path 型、同檔兩條、file_name 萬用字元。
RULES = [
    ("mod", REL_INF, "Foo.inf",
     "   HpGpioLib\n   PcdLib\n\n[Guids]\n",
     "   HpGpioLib\n   PcdLib\n   HpForceDebugLib\n\n[Guids]\n"),
    ("mod", REL_C, "Foo.c",
     "#include <A.h>\n#include <B.h>\n\n//---",
     "#include <A.h>\n#include <B.h>\n#include <HpForceDebugLib.h>\n\n//---"),
    ("mod", REL_C, "Foo.c 修改 2",
     "  Status = Init ();\n  return Status;\n",
     "  Status = Init ();\n  DEBUG ((DEBUG_INFO, \"[HpForceDebug] Foo\\n\"));\n  return Status;\n"),
    ("pcd", "Z*PkgConfig.dsc", "Z*PkgConfig.dsc",
     "  DEFINE DBG = FALSE\n",
     "  DEFINE DBG = TRUE\n"),
]

#: 每條規則「真正新增」的那一行，測試用來判斷有沒有套上
ADDED = {
    "Foo.inf": "HpForceDebugLib",
    "Foo.c": "#include <HpForceDebugLib.h>",
    "Foo.c 修改 2": "[HpForceDebug] Foo",
    "Z*PkgConfig.dsc": "DEFINE DBG = TRUE",
}


def profile_yaml():
    from changetodebug.core.reanchor import _emit_block
    lines = [
        "# 測試用迷你 profile（由 tests/_common.py 產生）",
        "profile:",
        "  key: MINI",
        "  display_name: MINI (test)",
        "  priority: 90",
        "  detect:",
        "    any:",
        f"      - dir: {DETECT_DIR}",
        "  pcd_scan_roots:",
        "    - HpPlatformPkg/MultiProject",
        "",
    ]
    for section, key in (("modifications", "sub_path"), ("platform_pcd_modifications", "file_name")):
        lines.append(f"{section}:")
        for kind, target, label, old, new in RULES:
            if (kind == "mod") != (section == "modifications"):
                continue
            lines.append("# ----------------------------------------------------------")
            lines.append(f"  - {key}: '{target}'")
            lines.append(f"    label: '{label}'")
            lines.append("    option_debug_flag: false")
            lines += _emit_block(old, "old_code", 4, "|2")
            lines += _emit_block(new, "new_code", 4, "|2")
        lines.append("")
    return "\n".join(lines) + "\n"


def make_profile(tmp):
    """在 tmp/profiles/MINI 建立目錄型 profile（profile.yaml + base/ + manifest）。回傳套件目錄。"""
    from changetodebug.core.basesnap import MANIFEST_NAME, dump_manifest, sha256_of
    pkg = Path(tmp) / "profiles" / "MINI"
    base = pkg / "base"
    for rel, text in ((REL_INF, FOO_INF), (REL_C, FOO_C), (REL_DSC_A, DSC)):
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
    (pkg / "profile.yaml").write_text(profile_yaml(), encoding="utf-8", newline="\n")
    entries = [
        {"rule_id": "mod:0", "label": "Foo.inf", "sub_path": REL_INF, "base_file": REL_INF,
         "source": "org", "sha256": sha256_of(base / REL_INF)},
        {"rule_id": "mod:1", "label": "Foo.c", "sub_path": REL_C, "base_file": REL_C,
         "source": "org", "sha256": sha256_of(base / REL_C)},
        {"rule_id": "mod:2", "label": "Foo.c 修改 2", "sub_path": REL_C, "base_file": REL_C,
         "source": "org", "sha256": sha256_of(base / REL_C)},
        {"rule_id": "pcd:0", "label": "Z*PkgConfig.dsc", "file_name": "Z*PkgConfig.dsc",
         "base_file": REL_DSC_A, "source": "org", "sha256": sha256_of(base / REL_DSC_A),
         "covers": [REL_DSC_A, REL_DSC_B], "representative": "ZAAPkg"},
    ]
    (pkg / MANIFEST_NAME).write_text(dump_manifest(entries, "deadbeef"), encoding="utf-8", newline="\n")
    return pkg


def load_mini(tmp):
    from changetodebug.core.profiles import load_profiles
    return [p for p in load_profiles([str(Path(tmp) / "profiles")]) if p.key == "MINI"][0]


# ---------------------------------------------------------------- 假 BIOS 樹

def make_tree(root, variant="old"):
    """建一棵假的 BIOS 樹。

    old    改動前的原樣（= base）
    new    上游改到規則要改的那幾段：Foo.inf 多了 HpVpinSelectionLib、Foo.c 多了 C.h 與
           Extra()，三條 sub_path 規則精確比對都會失敗且 3-way 會衝突；dsc 只在尾端加行，不衝突
    newer  上游改的是別處（HpGpioLib 改名、Packages 多一行），精確比對失敗但 3-way 合得起來
    """
    root = Path(root)
    inf, c, dsc = FOO_INF, FOO_C, DSC
    if variant == "new":
        inf = inf.replace("   PcdLib\n", "   PcdLib\n   HpVpinSelectionLib\n")
        c = c.replace("#include <B.h>\n", "#include <B.h>\n#include <C.h>\n")
        c = c.replace("  Status = Init ();\n", "  Status = Init ();\n  Status = Extra ();\n")
        dsc = dsc + "  DEFINE NEWUP = 2\n"
    elif variant == "newer":
        inf = inf.replace("   HpGpioLib\n", "   HpGpioLib2\n")
        inf = inf.replace("  MdePkg/MdePkg.dec\n", "  MdePkg/MdePkg.dec\n  FooPkg/FooPkg.dec\n")
    for rel, text in ((REL_INF, inf), (REL_C, c), (REL_DSC_A, dsc), (REL_DSC_B, dsc)):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
    (root / DETECT_DIR).mkdir(parents=True, exist_ok=True)
    return root


def run_patchset(profile, tree, **overrides):
    """對一棵樹實際跑一次 patchset（不備份、不驗證、關診斷）。回傳 (RunSummary, logs)。"""
    from changetodebug.core.runner import RunRequest, execute
    kwargs = dict(base_path=str(tree), profile=profile, task_keys=["patchset"],
                  options={"patchset": {}}, dry_run=False, backup=False,
                  enable_all_debug_flags=True, verify_after_run=False, diagnose=False)
    kwargs.update(overrides)
    logs, logger = logger_pair()
    return execute(RunRequest(**kwargs), logger), logs


def statuses(summary):
    from collections import Counter
    return dict(Counter(r.status_text for r in summary.overall.results))


def read(path):
    from changetodebug.core.patcher import normalize_newlines, read_text
    return normalize_newlines(read_text(path)[0])


def rmtree(path):
    shutil.rmtree(path, ignore_errors=True)
