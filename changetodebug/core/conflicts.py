"""合併衝突的產物與解決流程。

衝突發生時刻意**不動原檔**，而是把三方內容寫到工具自己的目錄：

    <工具目錄>/ChangeToDebug_conflicts/<專案資料夾名>/<執行時間戳>/
        HpPlatformPkg/HpPlatformPkg.dsc.base       共同起點（base 快照）
        HpPlatformPkg/HpPlatformPkg.dsc.profile    profile 期望的結果
        HpPlatformPkg/HpPlatformPkg.dsc.current    目前 source 的內容
        HpPlatformPkg/HpPlatformPkg.dsc.merged     使用者解完後存在這裡
        index.yaml                                 清單，供工具讀回

為什麼不像 git 那樣把衝突標記寫進原檔：
    BIOS source 被塞進 <<<<<<< 標記後不會 build 過，看似安全；但真正危險的是
    「大部分規則套用了、少數沒套用」的樹——它**很可能 build 得過**，然後燒出一個
    行為不明的 BIOS。所以這裡的策略是原檔完全不動，讓失敗訊號留在工具這一側。

為什麼不寫進 BIOS source 底下：
    那會在使用者的 git 工作目錄裡留下未追蹤檔案，每次 git status 都要看到。
    設定檔與 log 本來就寫在工具目錄，衝突產物放同一處也一致。
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from ..appinfo import app_dir
from .patcher import normalize_newlines, read_text, write_text

try:
    import yaml
except Exception:       # pragma: no cover
    yaml = None

CONFLICT_DIR_NAME = "ChangeToDebug_conflicts"
INDEX_NAME = "index.yaml"

SUFFIX_BASE = ".base"
SUFFIX_PROFILE = ".profile"
SUFFIX_CURRENT = ".current"
SUFFIX_MERGED = ".merged"


@dataclass
class ConflictRecord:
    target: str = ""            # 專案裡的實際檔案
    label: str = ""
    rule_id: str = ""
    count: int = 0              # 衝突段數
    base: str = ""
    profile: str = ""
    current: str = ""
    merged: str = ""
    encoding: str = "utf-8"
    newline: str = "\n"

    @property
    def resolved(self):
        """使用者是否已經產生 .merged 且內容有意義。"""
        return bool(self.merged) and os.path.isfile(self.merged) \
            and os.path.getsize(self.merged) > 0

    def as_dict(self):
        return {"target": self.target, "label": self.label, "rule_id": self.rule_id,
                "count": self.count, "base": self.base, "profile": self.profile,
                "current": self.current, "merged": self.merged,
                "encoding": self.encoding, "newline": "crlf" if self.newline == "\r\n" else "lf"}

    @classmethod
    def from_dict(cls, data):
        return cls(target=str(data.get("target", "")), label=str(data.get("label", "")),
                   rule_id=str(data.get("rule_id", "")), count=int(data.get("count", 0) or 0),
                   base=str(data.get("base", "")), profile=str(data.get("profile", "")),
                   current=str(data.get("current", "")), merged=str(data.get("merged", "")),
                   encoding=str(data.get("encoding", "utf-8")),
                   newline="\r\n" if str(data.get("newline", "lf")) == "crlf" else "\n")


def _project_slug(base_path):
    """由專案路徑取出一個可當資料夾名的識別字串。"""
    name = Path(str(base_path).rstrip("\\/")).name or "project"
    return re.sub(r"[^\w.-]", "_", name)


def project_dir(base_path):
    """某個專案的衝突根目錄。"""
    return app_dir() / CONFLICT_DIR_NAME / _project_slug(base_path)


def run_dir(base_path, run_stamp):
    return project_dir(base_path) / str(run_stamp)


def make_writer(base_path, run_stamp, logger):
    """回傳 write(target, base_text, ours_text, current_text, rule, count, ...) 供修補引擎呼叫。

    引擎不需要知道衝突產物長什麼樣，只要在衝突時把三方內容交出來。
    """
    root = run_dir(base_path, run_stamp)
    records = []

    def write(target, base_text, ours_text, current_text, rule, count,
              encoding="utf-8", newline="\n"):
        try:
            rel = Path(target).resolve().relative_to(Path(base_path).resolve())
        except ValueError:
            rel = Path(Path(target).name)
        out = root / rel
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            record = ConflictRecord(
                target=str(target), label=rule.label, rule_id=rule.rule_id, count=count,
                base=str(out) + SUFFIX_BASE, profile=str(out) + SUFFIX_PROFILE,
                current=str(out) + SUFFIX_CURRENT, merged=str(out) + SUFFIX_MERGED,
                encoding=encoding, newline=newline)
            for path, text in ((record.base, base_text), (record.profile, ours_text),
                               (record.current, current_text)):
                Path(path).write_text(text, encoding="utf-8", newline="\n")
        except Exception as exc:
            logger.warn(f"衝突產物寫出失敗（不影響其他項目）：{target} -> {exc}")
            return None
        records.append(record)
        return record

    write.root = root
    write.records = records
    return write


def refresh_current(records, logger):
    """執行結束後，把 .current 更新成檔案的最終狀態。

    .current 是在合併當下取的，此時同一個檔案的其他規則可能已經改過它；而衝突發生後
    整個檔案會被還原成執行前的樣子。以最終狀態為準，使用者在合併工具裡看到的才是
    他現在真正的檔案，重新錨定算出來的新 base 也才正確。
    """
    for record in records:
        try:
            text = normalize_newlines(read_text(record.target)[0])
        except Exception as exc:
            logger.debug(f"衝突產物的 current 無法更新：{record.target} -> {exc}")
            continue
        try:
            Path(record.current).write_text(text, encoding="utf-8", newline="\n")
        except Exception as exc:
            logger.debug(f"衝突產物的 current 寫出失敗：{record.current} -> {exc}")


def write_index(root, records, logger=None):
    """把清單寫成 index.yaml，讓「解決衝突」流程可以讀回。"""
    if not records:
        return None
    root = Path(root)
    try:
        root.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "conflicts": [r.as_dict() for r in records]}
        text = (yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)
                if yaml is not None else repr(payload))
        (root / INDEX_NAME).write_text(text, encoding="utf-8", newline="\n")
    except Exception as exc:
        if logger is not None:
            logger.warn(f"衝突清單寫出失敗：{exc}")
        return None
    return root / INDEX_NAME


def load_index(root):
    """讀回衝突清單；讀不到回空 list。"""
    path = Path(root) / INDEX_NAME
    if not path.is_file() or yaml is None:
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return []
    return [ConflictRecord.from_dict(item) for item in (data.get("conflicts") or [])
            if isinstance(item, dict)]


def latest_run(base_path):
    """找出這個專案最近一次留下衝突的執行目錄；沒有就回 None。"""
    root = project_dir(base_path)
    if not root.is_dir():
        return None
    runs = sorted((d for d in root.iterdir() if d.is_dir() and (d / INDEX_NAME).is_file()),
                  key=lambda d: d.name)
    return runs[-1] if runs else None


def apply_resolved(record, logger):
    """把使用者解好的 .merged 寫回專案檔案。

    回傳 (是否寫入, 說明)。刻意保守：內容為空、與現況相同、或仍留有衝突標記都不寫入。
    """
    if not record.resolved:
        return False, "尚未產生解決後的內容"

    try:
        merged = normalize_newlines(read_text(record.merged)[0])
    except Exception as exc:
        return False, f"讀取解決後的內容失敗：{exc}"

    if not merged.strip():
        return False, "解決後的內容是空的，未寫入"

    # 使用者若直接存下含衝突標記的檔案，寫進 BIOS source 會造成更難查的問題
    for marker in ("<<<<<<<", "=======", ">>>>>>>"):
        if marker in merged:
            return False, f"內容仍含衝突標記 {marker}，未寫入"

    try:
        current = normalize_newlines(read_text(record.target)[0])
    except Exception:
        current = None
    if current is not None and merged == current:
        return False, "與目前內容相同，不需要寫入"

    try:
        text = merged.replace("\n", "\r\n") if record.newline == "\r\n" else merged
        write_text(record.target, text, record.encoding)
    except Exception as exc:
        return False, f"寫入失敗：{exc}"

    logger.ok(f"已套用解決後的內容：{record.target}  ({record.label})")
    return True, "已寫入"


@dataclass
class ResolveSummary:
    applied: list = field(default_factory=list)
    skipped: list = field(default_factory=list)     # [(record, 原因)]

    @property
    def total(self):
        return len(self.applied) + len(self.skipped)


def apply_all(records, logger):
    summary = ResolveSummary()
    for record in records:
        ok, message = apply_resolved(record, logger)
        if ok:
            summary.applied.append(record)
        else:
            summary.skipped.append((record, message))
            logger.info(f"略過：{record.target}  ({record.label}) -> {message}")
    return summary
