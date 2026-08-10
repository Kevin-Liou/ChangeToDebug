"""程式進入點。"""

import argparse
import io
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from .appinfo import APP_NAME, APP_VERSION
from .core.settings import Settings
from .gui.main_window import MainWindow


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="ChangeToDebug",
        description="把 BIOS source 切換成 Debug mode 的整合工具")
    parser.add_argument("-v", "--version", action="version",
                        version=f"{APP_NAME} {APP_VERSION}")
    parser.add_argument("-p", "--path", help="啟動時預先帶入的專案根目錄")
    parser.add_argument("-d", "--debug", action="store_true", help="顯示詳細除錯訊息")
    return parser.parse_args(argv)


def _ensure_streams():
    """打包成 windowed exe 時 stdout/stderr 會是 None，先接上空裝置避免任何 print 直接崩潰。"""
    for name in ("stdout", "stderr"):
        if getattr(sys, name, None) is None:
            setattr(sys, name, io.StringIO())


def main(argv=None):
    _ensure_streams()
    args = parse_args(argv)

    # 高 DPI 螢幕下維持清晰（必須在建立 QApplication 前設定）
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    settings = Settings()
    window = MainWindow(settings)
    if args.path:
        window.path_combo.setCurrentText(args.path)
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
