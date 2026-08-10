"""背景執行緒：讓長時間的檔案掃描不會卡住介面，並即時把 log 送回主視窗。"""

from PyQt5.QtCore import QThread, pyqtSignal

from ..core.logbus import Logger
from ..core.runner import execute


class RunWorker(QThread):
    logged = pyqtSignal(str, str)        # (level, message)
    progressed = pyqtSignal(int, int)    # (done, total)
    finished_run = pyqtSignal(object)    # RunSummary
    failed = pyqtSignal(str)

    def __init__(self, request, log_file=None, verbose=False, parent=None):
        super().__init__(parent)
        self.request = request
        self.log_file = log_file
        self.verbose = verbose
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def is_cancelled(self):
        return self._cancelled

    def run(self):
        logger = Logger(sink=self.logged.emit, log_file=self.log_file,
                        echo_stdout=True, verbose=self.verbose)
        try:
            summary = execute(self.request, logger,
                              cancel_check=self.is_cancelled,
                              progress_cb=self.progressed.emit)
        except Exception as exc:            # 保護：任何未預期例外都不該讓 GUI 靜默失敗
            import traceback
            logger.error(f"執行時發生未預期錯誤：{exc}")
            logger.error(traceback.format_exc())
            self.failed.emit(str(exc))
            return
        self.finished_run.emit(summary)
