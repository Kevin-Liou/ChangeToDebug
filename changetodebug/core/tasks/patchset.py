"""主要功能：依 profile YAML 套用 Debug 修改。

對應舊版 DebugMode_Modify.py 的 run_main_logic()：
  * modifications              → 以 sub_path 直接定位檔案
  * platform_pcd_modifications → 在 pcd_scan_roots 底下遞迴找同名檔（多專案會全部套用）
"""

import fnmatch
import os
from pathlib import Path

from ..patcher import PatchResult, PatchStats, STATUS_MISSING_FILE, STATUS_SKIPPED
from .base import Task

#: 掃描時直接跳過的目錄，避免在 Build / .git 裡浪費時間
SKIP_DIRS = {".git", "build", "Build", "__pycache__", ".vs", ".vscode"}

BUILD_HINT = """請於需要 Debug 的 Driver 後加入以下內容：

  $(HP_PLATFORM_PACKAGE)/PlatformDxe/PlatformDxe.inf {
    <PcdsPatchableInModule>
      gEfiMdePkgTokenSpaceGuid.PcdDebugPrintErrorLevel|0x80080046
    <PcdsFixedAtBuild>
      gEfiMdePkgTokenSpaceGuid.PcdDebugPropertyMask|0x2F
    <LibraryClasses>
      DebugLib|MdePkg/Library/BaseDebugLibSerialPort/BaseDebugLibSerialPort.inf
    <BuildOptions>
      MSFT:*_*_*_CC_FLAGS    = /UMDEPKG_NDEBUG
  }"""


class PatchSetTask(Task):
    key = "patchset"
    title = "Debug Patch Set"
    description = "依 FY 世代設定檔套用所有 Debug 修改（CpuDeadLoop、ErrorLevel、PostCode 等）"
    requires_profile = True

    def run(self, ctx):
        stats = PatchStats()
        profile = ctx.profile
        logger = ctx.logger

        if profile is None:
            logger.error("未指定專案世代（profile），無法套用 Patch Set。")
            return stats

        options = ctx.task_options(self.key)
        enabled_ids = options.get("enabled_ids")     # None = 全部
        base = Path(ctx.base_path)

        logger.step(f"套用 Patch Set：{profile.title}")
        logger.info(f"設定檔：{profile.source_path}")
        logger.info(f"啟用所有 Debug Flag：{'是' if ctx.enable_all_debug_flags else '否'}")

        jobs = self._collect_jobs(ctx, profile, base, enabled_ids, stats)
        total = len(jobs)
        if total == 0:
            logger.warn("沒有任何符合條件的修改項目。")
            return stats

        for index, (file_path, rule) in enumerate(jobs, start=1):
            if ctx.cancelled():
                logger.warn("使用者中止執行。")
                break
            if rule.is_new_file:
                stats.add(ctx.engine.copy_file(rule.new_file_source, file_path,
                                               label=rule.label, overwrite=rule.overwrite))
            else:
                stats.add(ctx.engine.apply(file_path, rule))
            ctx.progress(index, total)

        logger.info(BUILD_HINT)
        return stats

    # ---- 展開成 (檔案, 規則) 工作清單 ----
    def _collect_jobs(self, ctx, profile, base, enabled_ids, stats):
        logger = ctx.logger
        jobs = []

        # 0) 新增檔案：一定排在文字修改之前（後面的修改會引用到這些新檔）
        for rule in profile.new_file_rules:
            if not self._is_enabled(ctx, rule, enabled_ids, stats):
                continue
            jobs.append((base / rule.sub_path.replace("\\", "/"), rule))
        if profile.new_file_rules:
            logger.info(f"新增檔案來源：{profile.new_files_dir or '(未設定)'}")

        # 1) sub_path 型：一條規則對一個檔案
        for rule in profile.rules:
            if not self._is_enabled(ctx, rule, enabled_ids, stats):
                continue
            jobs.append((base / rule.sub_path.replace("\\", "/"), rule))

        # 2) file_name 型：需要先掃描目錄
        pcd_rules = [r for r in profile.pcd_rules
                     if self._is_enabled(ctx, r, enabled_ids, stats)]
        if pcd_rules:
            wanted = {r.file_name for r in pcd_rules if r.file_name}
            found = self._scan_files(base, profile.pcd_scan_roots, wanted, logger)
            for rule in pcd_rules:
                matches = found.get(rule.file_name, [])
                if not matches:
                    # 缺檔警告已在 _scan_files 印過一次，這裡只記錄統計
                    stats.add(PatchResult(rule.file_name, STATUS_MISSING_FILE,
                                          "掃描範圍內找不到此檔名",
                                          rule.rule_id, rule.label))
                    continue
                for path in matches:
                    jobs.append((path, rule))
        return jobs

    def _is_enabled(self, ctx, rule, enabled_ids, stats):
        if enabled_ids is not None and rule.rule_id not in enabled_ids:
            stats.add(PatchResult(rule.target_display, STATUS_SKIPPED,
                                  "使用者取消勾選", rule.rule_id, rule.label))
            return False
        if rule.option_debug_flag and not ctx.enable_all_debug_flags:
            stats.add(PatchResult(rule.target_display, STATUS_SKIPPED,
                                  "option_debug_flag 未啟用", rule.rule_id, rule.label))
            return False
        return True

    @staticmethod
    def _scan_files(base, scan_roots, wanted_names, logger):
        """在 scan_roots 底下一次走訪，收集所有目標檔名的完整路徑。

        file_name 可以是確切檔名，也可以是萬用字元樣式（例如 Z*PkgConfig.dsc），
        用來一次涵蓋各專案自己命名的設定檔。
        """
        found = {name: [] for name in wanted_names}
        patterns = [n for n in wanted_names if any(ch in n for ch in "*?[")]
        for scan_root in scan_roots:
            root_path = base / str(scan_root).replace("\\", "/")
            if not root_path.is_dir():
                logger.warn(f"掃描根目錄不存在，略過：{root_path}")
                continue
            logger.info(f"掃描目錄：{root_path}")
            for root, dirs, files in os.walk(root_path):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
                for name in files:
                    if name in found:
                        found[name].append(Path(root) / name)
                    for pattern in patterns:
                        if fnmatch.fnmatch(name, pattern):
                            found[pattern].append(Path(root) / name)
        for name, paths in sorted(found.items()):
            if paths:
                logger.info(f"找到 {len(paths)} 個 {name}")
            else:
                logger.warn(f"掃描範圍內找不到 {name}，相關規則將無法套用")
        return found
