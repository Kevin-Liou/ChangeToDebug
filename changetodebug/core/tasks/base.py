"""Task 抽象層。

要新增功能（例如未來的「Coverage 打點」）只要：
  1. 繼承 Task 實作 run()
  2. 在 changetodebug/core/tasks/__init__.py 呼叫 register()
  3. GUI 會自動長出對應的分頁（若需要專屬選項再加一個 page widget）
"""

from dataclasses import dataclass, field

from ..patcher import PatchStats


@dataclass
class RunContext:
    """一次執行所需的全部資訊。"""

    base_path: str
    profile: object = None
    logger: object = None
    engine: object = None
    dry_run: bool = False
    backup: bool = True
    enable_all_debug_flags: bool = False
    merge_fallback: bool = True      # 比對失敗時是否用 base 快照做 3-way merge
    revert: bool = False             # True = 反向移除已套用的修改
    options: dict = field(default_factory=dict)      # 各 task 的專屬選項，key 為 task.key
    _cancel_check: object = None
    _progress_cb: object = None

    def task_options(self, key):
        return self.options.get(key, {}) or {}

    def cancelled(self):
        return bool(self._cancel_check and self._cancel_check())

    def progress(self, done, total):
        if self._progress_cb:
            self._progress_cb(done, total)


class Task:
    """所有功能的基底類別。"""

    key = ""
    title = ""
    description = ""
    requires_profile = False        # 是否一定要先偵測到 profile 才能跑

    def run(self, ctx):             # pragma: no cover - 由子類別實作
        raise NotImplementedError

    # ---- 共用小工具 ----
    @staticmethod
    def empty_stats():
        return PatchStats()
