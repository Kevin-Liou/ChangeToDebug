"""POST Code Marker（整合自 OutpMarkerGen.py）。

在每一處目標字串（預設 CpuDeadLoop ();）前面插入遞增的 _outp(0x80, XX) 打點，
用來在沒有序列埠 log 的情況下靠 POST Code 判斷卡在哪一行。

相較舊版的改良：
  * 掃描根目錄改由 GUI 指定，不再寫死 g:\\Ptl5。
  * 支援 Dry-Run 與備份，且會偵測已插入過的打點避免重複插入。
  * 會列出每個檔案實際用掉的 hex 區間，方便對照 POST Code。
"""

import os
import re
from pathlib import Path

from ..patcher import (PatchResult, PatchStats, STATUS_ALREADY, STATUS_ERROR,
                       STATUS_MISSING_FILE, STATUS_MODIFIED, STATUS_PREVIEW,
                       VerifyCheck, read_text, write_text)
from .base import Task
from .patchset import SKIP_DIRS

DEFAULT_TARGET = "CpuDeadLoop ();"
DEFAULT_START_HEX = 0xA0
MAX_HEX = 0xFF
SOURCE_SUFFIXES = (".c",)


class OutpMarkerTask(Task):
    key = "marker"
    title = "POST Code Marker"
    description = "在指定字串前插入遞增的 _outp(0x80, XX) 打點，用 POST Code 追蹤停在哪一行"
    requires_profile = False

    def run(self, ctx):
        stats = PatchStats()
        logger = ctx.logger
        options = ctx.task_options(self.key)

        target = options.get("target") or DEFAULT_TARGET
        hex_value = int(options.get("start_hex", DEFAULT_START_HEX)) & 0xFF
        scan_sub = str(options.get("scan_root", "") or "").strip()

        base = Path(ctx.base_path)
        scan_root = base / scan_sub.replace("\\", "/") if scan_sub else base

        logger.step("POST Code Marker")
        if not scan_root.is_dir():
            logger.error(f"掃描目錄不存在：{scan_root}")
            stats.add(PatchResult(str(scan_root), STATUS_MISSING_FILE, "掃描目錄不存在"))
            return stats

        logger.info(f"掃描目錄：{scan_root}")
        logger.info(f"目標字串：{target}   起始 POST Code：0x{hex_value:02X}")

        pattern = re.compile(r"(^[ \t]*)" + re.escape(target), re.MULTILINE)
        candidates = self._collect_sources(ctx, scan_root)
        total = len(candidates)

        for index, file_path in enumerate(candidates, start=1):
            if ctx.cancelled():
                logger.warn("使用者中止執行。")
                break
            result, hex_value = self._process_file(ctx, file_path, pattern, target, hex_value)
            if result is not None:
                stats.add(result)
            ctx.progress(index, total)

        if stats.total == 0:
            logger.warn("沒有找到任何符合目標字串的檔案。")
        else:
            logger.info(f"下一個可用的 POST Code：0x{hex_value:02X}")
        return stats

    @staticmethod
    def _collect_sources(ctx, scan_root):
        files = []
        for root, dirs, names in os.walk(scan_root):
            if ctx.cancelled():
                break
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in names:
                if name.lower().endswith(SOURCE_SUFFIXES):
                    files.append(Path(root) / name)
        return files

    def _process_file(self, ctx, file_path, pattern, target, hex_value):
        try:
            content, encoding = read_text(file_path)
        except Exception as exc:
            return PatchResult(str(file_path), STATUS_ERROR, str(exc)), hex_value

        matches = list(pattern.finditer(content))
        if not matches:
            return None, hex_value

        pieces = []
        last_index = 0
        used = []
        skipped = 0

        for match in matches:
            indent = match.group(1)
            head = content[last_index:match.start()]

            # 已經插過打點就不再重複插入
            if _already_marked(content, match.start()):
                pieces.append(head)
                pieces.append(indent + target)
                last_index = match.end()
                skipped += 1
                continue

            pieces.append(head)
            pieces.append(_marker_code(hex_value, indent))
            pieces.append(indent + target)
            last_index = match.end()
            used.append(hex_value)
            hex_value = 0x00 if hex_value >= MAX_HEX else hex_value + 1

        pieces.append(content[last_index:])

        if not used:
            ctx.logger.info(f"已有打點，略過：{file_path}")
            return PatchResult(str(file_path), STATUS_ALREADY, f"已存在 {skipped} 處打點"), hex_value

        span = f"0x{used[0]:02X} ~ 0x{used[-1]:02X}" if len(used) > 1 else f"0x{used[0]:02X}"
        if ctx.dry_run:
            ctx.logger.info(f"[預覽] 將插入 {len(used)} 處打點（{span}）：{file_path}")
            return PatchResult(str(file_path), STATUS_PREVIEW,
                               f"可插入 {len(used)} 處（{span}）", count=len(used)), hex_value

        ctx.engine.backup_file(file_path)
        try:
            write_text(file_path, "".join(pieces), encoding)
        except Exception as exc:
            ctx.logger.error(f"寫入失敗：{file_path} -> {exc}")
            return PatchResult(str(file_path), STATUS_ERROR, str(exc)), hex_value

        ctx.logger.ok(f"插入 {len(used)} 處打點（{span}）：{file_path}")
        check = VerifyCheck(contains=[f"_outp(0x80,0x{v:02X})" for v in used])
        return PatchResult(str(file_path), STATUS_MODIFIED,
                           f"插入 {len(used)} 處（{span}）", count=len(used),
                           verify=check), hex_value


def _marker_code(hex_val, indent):
    return (
        f"{indent}{{UINTN x;\n"
        f"{indent}   for(x=0;x<100000;x++)\n"
        f"{indent}    _outp(0x80,0x{hex_val:02X}); }}\n"
    )


def _already_marked(content, match_start, lookback=200):
    """檢查目標字串前面是否已經有打點，避免重複插入。"""
    head = content[max(0, match_start - lookback):match_start]
    return "_outp(0x80," in head
