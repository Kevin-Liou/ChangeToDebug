"""ChangeToDebug 進入點（不帶主控台視窗）。

內容與 ChangeToDebug_Start.py 等價，差別只在副檔名。Windows 把 .py 交給
py.exe、.pyw 交給 pyw.exe，後者不會附帶一個黑色的主控台視窗，所以雙擊這個
檔案就不會多開一個視窗出來。要看主控台輸出時仍可改用 .py。

代價是沒有主控台就看不到 traceback。啟動失敗時改寫進 ChangeToDebug_error.txt
並跳一個訊息框，不會靜靜地什麼都沒發生。
"""

import sys
import traceback
from pathlib import Path

if __name__ == "__main__":
    try:
        from changetodebug.app import main
        sys.exit(main())
    except Exception:
        detail = traceback.format_exc()
        report = None
        try:
            report = Path(__file__).resolve().parent / "ChangeToDebug_error.txt"
            report.write_text(detail, encoding="utf-8")
        except Exception:
            report = None
        try:
            import ctypes
            message = "ChangeToDebug 啟動失敗：\n\n" + detail[-1500:]
            if report:
                message += f"\n\n完整訊息已寫入：\n{report}"
            ctypes.windll.user32.MessageBoxW(None, message, "ChangeToDebug", 0x10)
        except Exception:
            pass
        sys.exit(1)
