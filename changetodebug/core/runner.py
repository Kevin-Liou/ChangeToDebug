"""把「選項 + task 清單」串成一次完整執行。GUI 與未來的 CLI 共用這一層。"""

from dataclasses import dataclass, field
from datetime import datetime

from .conflicts import (make_writer as make_conflict_writer, refresh_current,
                        write_index)
from .patcher import PatchEngine, PatchStats
from .tasks import RunContext, get_task
from .verifier import VerifySummary, verify


@dataclass
class RunRequest:
    base_path: str
    profile: object = None
    task_keys: list = field(default_factory=list)
    options: dict = field(default_factory=dict)
    dry_run: bool = False
    backup: bool = True
    enable_all_debug_flags: bool = False
    verify_after_run: bool = True
    diagnose: bool = True           # 比對失敗時輸出「最相似區塊」的差異
    merge_fallback: bool = True     # 比對失敗時用 base 快照做 3-way merge
    revert: bool = False            # True = 反向移除已套用的修改


@dataclass
class RunSummary:
    stats_by_task: dict = field(default_factory=dict)
    overall: PatchStats = field(default_factory=PatchStats)
    cancelled: bool = False
    backup_count: int = 0
    run_stamp: str = ""
    elapsed: float = 0.0
    verification: object = None     # VerifySummary；None 表示這次沒有驗證
    conflict_dir: str = ""          # 有合併衝突時，三方內容的保存位置
    conflicts: list = field(default_factory=list)   # [ConflictRecord]


def execute(request, logger, cancel_check=None, progress_cb=None):
    """依序執行 request.task_keys 指定的功能，回傳彙總結果。"""
    started = datetime.now()
    run_stamp = started.strftime("%Y%m%d%H%M%S")
    conflict_writer = None
    if not request.dry_run:
        conflict_writer = make_conflict_writer(request.base_path, run_stamp, logger)

    engine = PatchEngine(logger,
                         dry_run=request.dry_run,
                         backup=request.backup,
                         run_stamp=run_stamp,
                         diagnose=request.diagnose,
                         conflict_sink=conflict_writer)

    ctx = RunContext(
        base_path=request.base_path,
        profile=request.profile,
        logger=logger,
        engine=engine,
        dry_run=request.dry_run,
        backup=request.backup,
        enable_all_debug_flags=request.enable_all_debug_flags,
        merge_fallback=request.merge_fallback,
        revert=request.revert,
        options=request.options,
        _cancel_check=cancel_check,
        _progress_cb=progress_cb,
    )

    summary = RunSummary(run_stamp=run_stamp)

    logger.info(f"專案根目錄：{request.base_path}")
    if request.revert:
        logger.warn("本次為「移除 Change」——會把已套用的修改反向還原")
    logger.info(f"模式：{'預覽 (Dry-Run)' if request.dry_run else '實際修改'}"
                f"　備份：{'開啟' if request.backup and not request.dry_run else '關閉'}")
    _log_drift(request, logger)

    for key in request.task_keys:
        if cancel_check and cancel_check():
            summary.cancelled = True
            break
        task = get_task(key)
        if task is None:
            logger.warn(f"未知的功能代號：{key}")
            continue
        if task.requires_profile and request.profile is None:
            logger.error(f"「{task.title}」需要先偵測到專案世代，已略過。")
            continue
        stats = task.run(ctx)
        summary.stats_by_task[key] = stats
        summary.overall.merge(stats)

    if cancel_check and cancel_check():
        summary.cancelled = True

    # ---- 完成後重新讀檔驗證 ----
    if request.verify_after_run:
        logger.step("驗證修改結果")
        if request.dry_run:
            logger.info("預覽模式沒有實際寫入，略過驗證。")
            summary.verification = VerifySummary()
        else:
            summary.verification = verify(summary.overall.results, logger, cancel_check)
            _log_verify(summary.verification, logger)

    # ---- 合併衝突的三方內容留檔，供「解決衝突」流程讀回 ----
    if conflict_writer is not None and conflict_writer.records:
        # 衝突檔案在 task 層被還原過，以還原後的最終狀態為準
        refresh_current(conflict_writer.records, logger)
        summary.conflicts = list(conflict_writer.records)
        summary.conflict_dir = str(conflict_writer.root)
        write_index(conflict_writer.root, summary.conflicts, logger)
        logger.warn(f"有 {len(summary.conflicts)} 個檔案需要人工解決衝突，"
                    f"三方內容已保存在：{summary.conflict_dir}")

    summary.backup_count = engine.backup_count
    summary.elapsed = (datetime.now() - started).total_seconds()
    return summary


def _log_drift(request, logger):
    """把 profile 的版本基準差距寫進執行記錄。純資訊，不影響是否繼續執行。"""
    if request.profile is None:
        return
    try:
        infos = request.profile.check_drift(request.base_path)
    except Exception as exc:        # 版本檢查絕不能擋住主流程
        logger.debug(f"版本基準檢查失敗（略過）：{exc}")
        return
    for info in infos:
        text = f"版本基準｜{info.repo}：{info.summary()}"
        if info.needs_attention:
            logger.warn(text)
        else:
            logger.info(text)


def _log_verify(verification, logger):
    if verification.total == 0:
        return
    text = (f"驗證完成：{verification.passed} 項通過"
            f"，{verification.failed} 項失敗")
    if verification.skipped:
        text += f"，{verification.skipped} 項無法驗證"
    if verification.failed:
        logger.error(text)
    else:
        logger.ok(text)
