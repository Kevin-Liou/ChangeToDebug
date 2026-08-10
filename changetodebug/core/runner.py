"""把「選項 + task 清單」串成一次完整執行。GUI 與未來的 CLI 共用這一層。"""

from dataclasses import dataclass, field
from datetime import datetime

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


@dataclass
class RunSummary:
    stats_by_task: dict = field(default_factory=dict)
    overall: PatchStats = field(default_factory=PatchStats)
    cancelled: bool = False
    backup_count: int = 0
    run_stamp: str = ""
    elapsed: float = 0.0
    verification: object = None     # VerifySummary；None 表示這次沒有驗證


def execute(request, logger, cancel_check=None, progress_cb=None):
    """依序執行 request.task_keys 指定的功能，回傳彙總結果。"""
    started = datetime.now()
    run_stamp = started.strftime("%Y%m%d%H%M%S")
    engine = PatchEngine(logger,
                         dry_run=request.dry_run,
                         backup=request.backup,
                         run_stamp=run_stamp)

    ctx = RunContext(
        base_path=request.base_path,
        profile=request.profile,
        logger=logger,
        engine=engine,
        dry_run=request.dry_run,
        backup=request.backup,
        enable_all_debug_flags=request.enable_all_debug_flags,
        options=request.options,
        _cancel_check=cancel_check,
        _progress_cb=progress_cb,
    )

    summary = RunSummary(run_stamp=run_stamp)

    logger.info(f"專案根目錄：{request.base_path}")
    logger.info(f"模式：{'預覽 (Dry-Run)' if request.dry_run else '實際修改'}"
                f"　備份：{'開啟' if request.backup and not request.dry_run else '關閉'}")

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

    summary.backup_count = engine.backup_count
    summary.elapsed = (datetime.now() - started).total_seconds()
    return summary


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
