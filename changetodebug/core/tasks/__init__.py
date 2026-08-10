"""Task 註冊表。

新增功能時在此 register()，GUI 會自動依註冊順序建立分頁。
"""

from collections import OrderedDict

from .base import RunContext, Task
from .driver_debug import MODE_MEMORY, MODE_SINGLE, DriverDebugTask
from .outp_marker import OutpMarkerTask
from .patchset import PatchSetTask

TASK_REGISTRY = OrderedDict()


def register(task_cls):
    TASK_REGISTRY[task_cls.key] = task_cls
    return task_cls


def get_task(key):
    task_cls = TASK_REGISTRY.get(key)
    return task_cls() if task_cls else None


def all_tasks():
    """回傳所有已註冊 task 的實例（依註冊順序）。"""
    return [cls() for cls in TASK_REGISTRY.values()]


register(PatchSetTask)
register(DriverDebugTask)
register(OutpMarkerTask)

__all__ = [
    "RunContext", "Task", "TASK_REGISTRY", "register", "get_task", "all_tasks",
    "PatchSetTask", "DriverDebugTask", "OutpMarkerTask",
    "MODE_MEMORY", "MODE_SINGLE",
]
