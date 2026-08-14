"""Driver Debug 功能（整合自舊版 ChangeToDebug_Controller.py）。

兩種模式：
  * memory        Memory Debug：開 PcdHpMemoryDebugEnable、改 DxeMemDebugAcpiArea.c、
                  指定 driver 的 DEBUG 訊息升級為 DEBUG_ERROR，並在對應 .inf 加入 MemDebugLib。
  * single        Single Driver Debug：只把指定 driver 的 DEBUG 訊息升級為 DEBUG_ERROR。

相較舊版的改良：
  * 不再以 os.getcwd() 為根目錄，改用 GUI 選擇的專案路徑（工具不必放進 code 裡）。
  * 一次走訪即可比對全部 driver 名稱（舊版是「每個名稱 × 每個根目錄」重複掃描）。
  * 支援 Dry-Run / 備份 / 編碼偵測，與 Patch Set 共用同一套引擎與 log。
"""

import os
from pathlib import Path

from ..patcher import (PatchResult, PatchStats, Rule, STATUS_ALREADY,
                       STATUS_MISSING_FILE, STATUS_NOT_FOUND, VerifyCheck,
                       read_text)
from .base import Task
from .patchset import SKIP_DIRS

MODE_MEMORY = "memory"
MODE_SINGLE = "single"

MODE_TEXT = {
    MODE_MEMORY: "Memory Debug",
    MODE_SINGLE: "Single Driver Debug",
}


class DriverDebugTask(Task):
    key = "driver"
    title = "Driver Debug"
    description = "指定 driver 檔名，將其 DEBUG 訊息升級為 DEBUG_ERROR（可選 Memory Debug 模式）"
    requires_profile = False

    def run(self, ctx):
        stats = PatchStats()
        logger = ctx.logger
        options = ctx.task_options(self.key)

        mode = options.get("mode", MODE_MEMORY)
        names = [n.strip() for n in options.get("names", []) if n and n.strip()]
        base = Path(ctx.base_path)

        logger.step(f"Driver Debug：{MODE_TEXT.get(mode, mode)}")

        if not names:
            logger.warn("沒有輸入任何 driver 檔名，略過此功能。")
            return stats

        cfg = self._config(ctx)
        mem_cfg = cfg.get("memory_debug", {})

        # ---- Memory Debug 的前置設定 ----
        if mode == MODE_MEMORY:
            stats.merge(self._enable_memory_pcd(ctx, base, mem_cfg))
            if ctx.cancelled():
                return stats
            stats.merge(self._patch_acpi_area(ctx, base, mem_cfg))
            if ctx.cancelled():
                return stats

        # ---- 尋找並修改 driver ----
        found = self._find_drivers(ctx, base, cfg.get("search_roots", []), names)
        message_map = cfg.get("message_map", {})
        pairs = list(message_map.items())

        for name in names:
            paths = found.get(self._norm(name), [])
            if not paths:
                logger.warn(f"找不到 driver：{name}")
                stats.add(PatchResult(name, STATUS_NOT_FOUND, "在搜尋範圍內找不到此檔案",
                                      label=name))

        targets = [(name, p) for name in names for p in found.get(self._norm(name), [])]
        total = len(targets)
        for index, (name, path) in enumerate(targets, start=1):
            if ctx.cancelled():
                logger.warn("使用者中止執行。")
                break
            logger.info(f"找到 driver：{path}")
            stats.add(ctx.engine.replace_pairs(path, pairs, label=name))

            if mode == MODE_MEMORY:
                inf_path = self._find_inf(ctx, path.parent, name)
                if inf_path:
                    stats.add(self._patch_inf(ctx, inf_path, mem_cfg, name))
                else:
                    # Memory Debug 一定要有對應的 .inf 才能加 MemDebugLib，計入失敗
                    logger.warn(f"找不到 {name} 對應的 .inf，MemDebugLib 未加入")
                    stats.add(PatchResult(str(path.parent), STATUS_NOT_FOUND,
                                          "找不到對應的 .inf", label=name))
            ctx.progress(index, total)

        return stats

    # ---------------------------------------------------------------- 設定

    def _config(self, ctx):
        from ..profiles import DEFAULT_DRIVER_DEBUG
        if ctx.profile is not None and getattr(ctx.profile, "driver_debug", None):
            return ctx.profile.driver_debug
        return dict(DEFAULT_DRIVER_DEBUG)

    @staticmethod
    def _norm(name):
        return name.strip().lower()

    # ---------------------------------------------------------------- Memory Debug

    def _enable_memory_pcd(self, ctx, base, mem_cfg):
        """開啟 PcdHpMemoryDebugEnable（以 regex 比對，不受空白數量影響）。"""
        stats = PatchStats()
        scan_root = base / str(mem_cfg.get("pcd_scan_root", "")).replace("\\", "/")
        file_name = mem_cfg.get("pcd_file", "PlatformPcdConfig.dsc")

        if not scan_root.is_dir():
            ctx.logger.warn(f"Memory Debug PCD 掃描目錄不存在：{scan_root}")
            stats.add(PatchResult(str(scan_root), STATUS_MISSING_FILE, "掃描目錄不存在",
                                  label="PcdHpMemoryDebugEnable"))
            return stats

        rule = Rule(
            rule_id="driver:memory_pcd",
            label="PcdHpMemoryDebugEnable = TRUE",
            file_name=file_name,
            old_code=mem_cfg.get("pcd_pattern", ""),
            new_code=mem_cfg.get("pcd_replacement", ""),
            regex=True,
            regex_applied_check=mem_cfg.get("pcd_applied_check", ""),
        )

        hit = False
        for root, dirs, files in os.walk(scan_root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                if name == file_name:
                    hit = True
                    stats.add(ctx.engine.apply(Path(root) / name, rule))
        if not hit:
            ctx.logger.warn(f"掃描不到 {file_name}")
            stats.add(PatchResult(file_name, STATUS_MISSING_FILE, "掃描範圍內找不到此檔名",
                                  label=rule.label))
        return stats

    def _patch_acpi_area(self, ctx, base, mem_cfg):
        """將 DxeMemDebugAcpiArea.c 中的 IsLegacySupported() 換成 0。"""
        stats = PatchStats()
        sub_path = str(mem_cfg.get("acpi_area_sub_path", "")).replace("\\", "/")
        if not sub_path:
            return stats
        rule = Rule(
            rule_id="driver:acpi_area",
            label="IsLegacySupported() -> 0",
            sub_path=sub_path,
            old_code=mem_cfg.get("acpi_area_old", "IsLegacySupported()"),
            new_code=mem_cfg.get("acpi_area_new", "0"),
        )
        stats.add(ctx.engine.apply(base / sub_path, rule))
        return stats

    # ---------------------------------------------------------------- 搜尋

    def _find_drivers(self, ctx, base, search_roots, names):
        """一次走訪所有搜尋根目錄，回傳 {小寫檔名: [路徑, ...]}。"""
        wanted = {self._norm(n) for n in names}
        found = {n: [] for n in wanted}

        roots = []
        for item in search_roots:
            path = base / str(item).replace("\\", "/")
            if path.is_dir():
                roots.append(path)
            else:
                ctx.logger.debug(f"搜尋根目錄不存在，略過：{path}")

        if not roots:
            ctx.logger.warn("所有搜尋根目錄都不存在，改為掃描整個專案根目錄。")
            roots = [base]

        for root_path in roots:
            ctx.logger.info(f"搜尋目錄：{root_path}")
            for root, dirs, files in os.walk(root_path):
                if ctx.cancelled():
                    return found
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for name in files:
                    key = name.lower()
                    if key in found:
                        found[key].append(Path(root) / name)
        return found

    def _find_inf(self, ctx, search_dir, driver_name):
        """在 driver 所在目錄往下找出引用該 driver 的 .inf。"""
        token = driver_name.split("_")[0] if "_" in driver_name else driver_name
        for root, dirs, files in os.walk(search_dir):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                if not name.lower().endswith(".inf"):
                    continue
                path = Path(root) / name
                try:
                    content, _ = read_text(path)
                except Exception:
                    continue
                if token in content:
                    ctx.logger.info(f"找到對應 inf：{path}")
                    return path
        return None

    # ---------------------------------------------------------------- inf

    def _patch_inf(self, ctx, inf_path, mem_cfg, label):
        """在 .inf 的 [Packages] / [LibraryClasses] 補上 Memory Debug 需要的項目。"""
        package = mem_cfg.get("inf_package", "HpCommonPkg/MemoryDebug/MemoryDebug.dec")
        library = mem_cfg.get("inf_library", "MemDebugLib")

        try:
            content, encoding = read_text(inf_path)
        except Exception as exc:
            ctx.logger.error(f"讀取 inf 失敗：{inf_path} -> {exc}")
            return PatchResult(str(inf_path), STATUS_MISSING_FILE, str(exc), label=label)

        lines = content.splitlines(keepends=True)
        stripped = [line.strip() for line in lines]
        check = VerifyCheck(contains=[package, library])

        if package in stripped or library in stripped:
            ctx.logger.info(f"inf 已為 Memory Debug 設定，略過：{inf_path}")
            return PatchResult(str(inf_path), STATUS_ALREADY, "inf 已包含 MemDebugLib",
                               label=label, verify=check)

        changed = False

        # [Packages]：插在區段第一行後面，沿用下一行的縮排
        for i, text in enumerate(stripped):
            if text == "[Packages]":
                indent = _indent_of(lines[i + 1]) if i + 1 < len(lines) else "  "
                lines.insert(i + 1, f"{indent}{package}\n")
                changed = True
                break

        # [LibraryClasses]：插在區段結尾（遇到空行或下一個區段）
        stripped = [line.strip() for line in lines]
        for i, text in enumerate(stripped):
            if text == "[LibraryClasses]":
                indent = _indent_of(lines[i + 1]) if i + 1 < len(lines) else "  "
                j = i + 1
                while j < len(lines) and stripped[j] != "" and not stripped[j].startswith("["):
                    j += 1
                lines.insert(j, f"{indent}{library}\n")
                changed = True
                break

        if not changed:
            ctx.logger.warn(f"inf 中找不到 [Packages] / [LibraryClasses]：{inf_path}")
            return PatchResult(str(inf_path), STATUS_NOT_FOUND,
                               "找不到 [Packages] / [LibraryClasses]", label=label)

        return ctx.engine.write_lines(inf_path, lines, encoding, label=label, verify=check)


def _indent_of(line):
    """取出該行開頭的空白（含 tab）。"""
    count = 0
    while count < len(line) and line[count] in " \t":
        count += 1
    return line[:count] or "  "
