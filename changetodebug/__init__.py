"""ChangeToDebug - BIOS source 一鍵切換 Debug Mode 工具。

套件結構：
    changetodebug.core   純邏輯層（不依賴 GUI，可單獨被 CLI / 測試使用）
    changetodebug.gui    PyQt5 介面層
"""

from .appinfo import APP_NAME, APP_TITLE, APP_VERSION

__all__ = ["APP_NAME", "APP_TITLE", "APP_VERSION"]
