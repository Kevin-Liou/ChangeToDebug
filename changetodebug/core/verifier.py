"""完成後驗證：重新讀取被修改過的檔案，確認內容真的變成預期的樣子。

這一步刻意不信任修補當下的回報，而是重新開檔比對，可以抓到
「寫入被防毒/唯讀擋掉」「事後被其他工具還原」「規則本身寫錯」等情況。
"""

import re
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path

from .patcher import (STATUS_ALREADY, STATUS_COPIED, STATUS_MODIFIED,
                      normalize_newlines, read_text)

#: 只有這些狀態需要驗證（預覽 / 略過 / 失敗的本來就沒改到東西）
VERIFIABLE_STATUS = (STATUS_MODIFIED, STATUS_ALREADY, STATUS_COPIED)

SNIPPET_LIMIT = 56


@dataclass
class VerifyResult:
    file_path: str
    label: str = ""
    ok: bool = True
    reasons: list = field(default_factory=list)

    @property
    def reason_text(self):
        return "；".join(self.reasons)


@dataclass
class VerifySummary:
    results: list = field(default_factory=list)
    skipped: int = 0        # 沒有可驗證條件（例如 regex 規則被判定無法驗證）

    @property
    def total(self):
        return len(self.results)

    @property
    def passed(self):
        return sum(1 for r in self.results if r.ok)

    @property
    def failed(self):
        return sum(1 for r in self.results if not r.ok)

    @property
    def failures(self):
        return [r for r in self.results if not r.ok]


def _snippet(text):
    """取片段中第一行有意義的內容當作訊息，避免整段程式碼灌進 log。"""
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    if not lines:
        return "(空白內容)"
    # 跳過只有括號之類的行，找第一行看得出內容的
    meaningful = next((line for line in lines
                       if any(ch.isalnum() for ch in line) and len(line) > 2), lines[0])
    return meaningful[:SNIPPET_LIMIT] + ("…" if len(meaningful) > SNIPPET_LIMIT else "")


def verify(results, logger, cancel_check=None):
    """對 PatchResult 清單做事後驗證。同一個檔案只會重新讀取一次。"""
    summary = VerifySummary()

    targets = []
    for result in results:
        if result.status not in VERIFIABLE_STATUS:
            continue
        check = result.verify
        if check is None or check.is_empty():
            summary.skipped += 1
            continue
        targets.append(result)

    if not targets:
        logger.info("沒有需要驗證的項目。")
        return summary

    by_file = OrderedDict()
    for result in targets:
        by_file.setdefault(str(Path(result.file_path)), []).append(result)

    logger.info(f"重新讀取 {len(by_file)} 個檔案，驗證 {len(targets)} 個項目…")

    for file_path, items in by_file.items():
        if cancel_check and cancel_check():
            logger.warn("驗證被中止。")
            break

        try:
            content, _ = read_text(file_path)
        except Exception as exc:
            for item in items:
                summary.results.append(
                    VerifyResult(file_path, item.label, False, [f"無法重新讀取檔案：{exc}"]))
            logger.error(f"[驗證失敗] 無法讀取：{file_path} -> {exc}")
            continue

        norm = normalize_newlines(content)
        for item in items:
            summary.results.append(_check_one(file_path, item, norm, logger))

    return summary


def _check_one(file_path, item, norm, logger):
    check = item.verify
    reasons = []

    for expected in check.contains:
        if normalize_newlines(expected) not in norm:
            reasons.append(f"找不到預期內容：{_snippet(expected)}")

    for unwanted in check.absent:
        if normalize_newlines(unwanted) in norm:
            reasons.append(f"修改前的內容仍然存在：{_snippet(unwanted)}")

    for pattern in check.regex_absent:
        try:
            if re.search(pattern, norm, re.MULTILINE):
                reasons.append(f"仍符合修改前的樣式：{_snippet(pattern)}")
        except re.error as exc:
            reasons.append(f"regex 無法驗證：{exc}")

    if check.same_as:
        try:
            source_text, _ = read_text(check.same_as)
        except Exception as exc:
            reasons.append(f"無法讀取來源檔比對：{exc}")
        else:
            if normalize_newlines(source_text) != norm:
                reasons.append(f"內容與來源檔不符：{check.same_as}")

    result = VerifyResult(file_path, item.label, not reasons, reasons)
    if result.ok:
        logger.debug(f"[驗證通過] {file_path}  ({item.label})")
    else:
        logger.error(f"[驗證失敗] {file_path}  ({item.label})：{result.reason_text}")
    return result
