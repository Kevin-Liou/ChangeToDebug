"""主要功能：依 profile YAML 套用 Debug 修改。

對應舊版 DebugMode_Modify.py 的 run_main_logic()：
  * modifications              → 以 sub_path 直接定位檔案
  * platform_pcd_modifications → 在 pcd_scan_roots 底下遞迴找同名檔（多專案會全部套用）
"""

import fnmatch
import os
from collections import OrderedDict
from pathlib import Path

from ..patcher import (PatchResult, PatchStats, STATUS_COPIED, STATUS_MERGED,
                       STATUS_MERGE_CONFLICT, STATUS_MISSING_FILE, STATUS_MODIFIED,
                       STATUS_ROLLED_BACK, STATUS_SKIPPED)
from .base import Task


def _read_bytes(path):
    """回傳檔案原始位元組；不存在或讀不到回 None。"""
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None

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


def list_projects(base, scan_roots):
    """列出掃描根目錄底下的專案（第一層子目錄），供使用者勾選要修改哪些。

    MultiProject 底下除了各專案資料夾還有 .bat/.dsc 之類的共用檔案，
    那些不屬於任何專案，一律照舊處理。
    """
    base = Path(base)
    names = set()
    for scan_root in scan_roots:
        root_path = base / str(scan_root).replace("\\", "/")
        if not root_path.is_dir():
            continue
        try:
            for child in root_path.iterdir():
                if child.is_dir() and child.name not in SKIP_DIRS:
                    names.add(child.name)
        except OSError:
            continue
    return sorted(names)


def project_of_path(base, scan_roots, path):
    """判斷某個檔案屬於哪個專案；不在任何專案底下時回空字串。"""
    path = Path(path)
    for scan_root in scan_roots:
        root_path = Path(base) / str(scan_root).replace("\\", "/")
        try:
            rel = path.relative_to(root_path)
        except ValueError:
            continue
        return rel.parts[0] if len(rel.parts) > 1 else ""
    return ""


def make_target_resolver(profile, base, logger):
    """回傳 resolve(rule) -> [Path]，把「規則對應到哪些實際檔案」的邏輯開放共用。

    base 快照擷取需要和實際套用完全相同的定位方式，否則擷取到的 base 會對不上。
    file_name 型規則要遞迴掃描，這裡先掃一次快取起來，不必每條規則各掃一遍。
    """
    base = Path(base)
    wanted = {r.file_name for r in profile.pcd_rules if r.file_name}
    found = PatchSetTask._scan_files(base, profile.pcd_scan_roots, wanted, logger) if wanted else {}

    def resolve(rule):
        if rule.is_new_file:
            return []
        if rule.sub_path:
            return [base / rule.sub_path.replace("\\", "/")]
        return list(found.get(rule.file_name, []))

    return resolve


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
        projects = options.get("projects")           # None = 全部專案
        base = Path(ctx.base_path)

        logger.step(("移除 Patch Set：" if ctx.revert else "套用 Patch Set：") + profile.title)
        if ctx.revert:
            logger.info("反向移除：把 new_code 換回 old_code，"
                        "上游在這之後的改動不受影響")
        logger.info(f"設定檔：{profile.source_path}")
        logger.info(f"啟用所有 Debug Flag：{'是' if ctx.enable_all_debug_flags else '否'}")

        snapshot = getattr(profile, "base_snapshot", None)
        if snapshot is not None and snapshot.available:
            state = "啟用" if ctx.merge_fallback else "停用（使用者關閉）"
            logger.info(f"base 快照：{len(snapshot.covered())} 條規則可用，"
                        f"比對失敗時的 3-way merge {state}")
        elif ctx.merge_fallback:
            logger.info("此 profile 沒有 base 快照，比對失敗時無法做 3-way merge")

        if projects is not None:
            available = list_projects(base, profile.pcd_scan_roots)
            logger.info(f"套用專案：{'、'.join(projects) if projects else '（未選任何專案）'}"
                        f"　（共 {len(available)} 個可選）")

        jobs = self._collect_jobs(ctx, profile, base, enabled_ids, stats, projects)
        total = len(jobs)
        if total == 0:
            logger.warn("沒有任何符合條件的修改項目。")
            return stats

        # 依檔案分組處理：同一個檔案只要有任何一條規則合併衝突，就把整個檔案還原。
        # 「一半規則套用了、一半沒有」的 .dsc 很可能還是 build 得過，卻燒出行為不明的
        # BIOS——那比整個檔案都沒套用危險得多。
        by_file = OrderedDict()
        for file_path, rule in jobs:
            by_file.setdefault(os.path.normcase(os.path.abspath(str(file_path))),
                               []).append((file_path, rule))

        done = 0
        for group in by_file.values():
            if ctx.cancelled():
                logger.warn("使用者中止執行。")
                break

            target = str(group[0][0])
            snapshot = None if ctx.dry_run else _read_bytes(target)
            group_results = []

            for file_path, rule in group:
                if rule.is_new_file:
                    result = (ctx.engine.remove_file(rule.new_file_source, file_path,
                                                     label=rule.label)
                              if ctx.revert else
                              ctx.engine.copy_file(rule.new_file_source, file_path,
                                                   label=rule.label,
                                                   overwrite=rule.overwrite))
                else:
                    result = ctx.engine.apply(file_path, rule,
                                              self._base_ref(ctx, rule, file_path),
                                              reverse=ctx.revert)
                group_results.append(result)
                done += 1
                ctx.progress(done, total)

            if not ctx.dry_run and any(r.status == STATUS_MERGE_CONFLICT
                                       for r in group_results):
                self._rollback(logger, target, snapshot, group_results)

            for result in group_results:
                stats.add(result)

        logger.info(BUILD_HINT)
        return stats

    @staticmethod
    def _rollback(logger, target, snapshot, group_results):
        """同檔案有衝突時，把先前成功寫入的規則一併還原，維持檔案層級的一致性。"""
        written = [r for r in group_results
                   if r.status in (STATUS_MODIFIED, STATUS_MERGED, STATUS_COPIED)]
        if not written:
            return
        if snapshot is None:
            logger.warn(f"無法取得原始內容，未還原：{target}")
            return
        try:
            with open(target, "wb") as f:
                f.write(snapshot)
        except Exception as exc:
            logger.error(f"還原失敗（檔案可能處於部分套用狀態）：{target} -> {exc}")
            return
        logger.warn(f"同一檔案有合併衝突，已還原 {len(written)} 條先前成功的修改："
                    f"{target}")
        for result in written:
            result.status = STATUS_ROLLED_BACK
            result.message = "同檔案有合併衝突，已還原"
            result.verify = None

    @staticmethod
    def _base_ref(ctx, rule, file_path):
        """取得這條規則在此檔案上可用的 base 快照；沒有就回 None（退回一般流程）。"""
        if not ctx.merge_fallback:
            return None
        snapshot = getattr(ctx.profile, "base_snapshot", None)
        if snapshot is None or not snapshot.available:
            return None
        return snapshot.base_for(rule.rule_id, str(file_path))

    # ---- 展開成 (檔案, 規則) 工作清單 ----
    def _collect_jobs(self, ctx, profile, base, enabled_ids, stats, projects=None):
        logger = ctx.logger
        jobs = []

        # 0) 新增檔案：套用時排在文字修改之前（後面的修改會引用到這些新檔）；
        #    移除時反過來，最後才刪，否則前面的反向修改會找不到檔案。
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
            found = self._scan_files(base, profile.pcd_scan_roots, wanted, logger, projects)
            for rule in pcd_rules:
                matches = found.get(rule.file_name, [])
                if not matches:
                    if projects is not None:
                        stats.add(PatchResult(rule.file_name, STATUS_SKIPPED,
                                              "選中的專案裡沒有這個檔案",
                                              rule.rule_id, rule.label))
                        continue
                    # 缺檔警告已在 _scan_files 印過一次，這裡只記錄統計
                    stats.add(PatchResult(rule.file_name, STATUS_MISSING_FILE,
                                          "掃描範圍內找不到此檔名",
                                          rule.rule_id, rule.label))
                    continue
                for path in matches:
                    jobs.append((path, rule))

        if ctx.revert:
            jobs.reverse()
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
    def _scan_files(base, scan_roots, wanted_names, logger, projects=None):
        """在 scan_roots 底下一次走訪，收集所有目標檔名的完整路徑。

        file_name 可以是確切檔名，也可以是萬用字元樣式（例如 Z*PkgConfig.dsc），
        用來一次涵蓋各專案自己命名的設定檔。

        projects 有值時只處理選中的專案——直接在走訪的第一層剪掉未選的目錄，
        既是過濾也順便省下掃描時間。掃描根目錄底下的共用檔案不屬於任何專案，一律保留。
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
                if projects is not None and Path(root) == root_path:
                    dirs[:] = [d for d in dirs if d in projects]
                for name in files:
                    if name in found:
                        found[name].append(Path(root) / name)
                    for pattern in patterns:
                        if fnmatch.fnmatch(name, pattern):
                            found[pattern].append(Path(root) / name)
        for name, paths in sorted(found.items()):
            if paths:
                logger.info(f"找到 {len(paths)} 個 {name}")
            elif projects is not None:
                logger.warn(f"選中的專案裡找不到 {name}，相關規則將無法套用")
            else:
                logger.warn(f"掃描範圍內找不到 {name}，相關規則將無法套用")
        return found
