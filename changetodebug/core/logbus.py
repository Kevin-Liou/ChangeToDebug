"""統一的訊息輸出：同時送到 GUI（callback）、stdout 與 log 檔。"""

from datetime import datetime
from pathlib import Path


class LogLevel:
    DEBUG = "debug"
    INFO = "info"
    OK = "ok"
    WARN = "warn"
    ERROR = "error"
    STEP = "step"      # 區段標題


#: 寫進 log 檔時的前綴，方便事後用文字搜尋
_PREFIX = {
    LogLevel.DEBUG: "[除錯]",
    LogLevel.INFO: "[資訊]",
    LogLevel.OK: "[成功]",
    LogLevel.WARN: "[警告]",
    LogLevel.ERROR: "[錯誤]",
    LogLevel.STEP: "[步驟]",
}


class Logger:
    """可插拔 sink 的簡易 logger。

    sink 形式為 ``callable(level: str, message: str)``；GUI 會傳入一個
    透過 Qt signal 轉發到主執行緒的函式。
    """

    def __init__(self, sink=None, log_file=None, echo_stdout=True, verbose=False):
        self.sink = sink
        self.log_file = Path(log_file) if log_file else None
        self.echo_stdout = echo_stdout
        self.verbose = verbose

    # ---- 基本 ----
    def log(self, level, message):
        if level == LogLevel.DEBUG and not self.verbose:
            return
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{stamp}] {_PREFIX.get(level, '[資訊]')} {message}"

        if self.echo_stdout:
            try:
                print(line)
            except Exception:
                pass    # 打包成 windowed exe 時可能沒有 stdout

        if self.log_file is not None:
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except Exception:
                pass    # log 檔寫入失敗不應中斷主流程

        if self.sink is not None:
            self.sink(level, message)

    # ---- 語意化捷徑 ----
    def debug(self, msg):
        self.log(LogLevel.DEBUG, msg)

    def info(self, msg):
        self.log(LogLevel.INFO, msg)

    def ok(self, msg):
        self.log(LogLevel.OK, msg)

    def warn(self, msg):
        self.log(LogLevel.WARN, msg)

    def error(self, msg):
        self.log(LogLevel.ERROR, msg)

    def step(self, msg):
        self.log(LogLevel.STEP, msg)
