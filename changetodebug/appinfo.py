"""程式基本資訊與路徑解析（相容 PyInstaller 打包）。"""

import sys
from pathlib import Path

APP_NAME = "ChangeToDebug"
APP_TITLE = "ChangeToDebug - BIOS Debug Mode Patcher"
APP_VERSION = "3.0.0"

# 設定檔 / log 檔名
SETTINGS_FILE = "ChangeToDebug_settings.json"
LEGACY_SETTINGS_FILE = "last_path_config.json"   # 舊版 DebugMode_Modify.py 使用
LOG_FILE = "ChangeToDebug_log.txt"
PROFILE_DIR_NAME = "profiles"


def is_frozen() -> bool:
    """是否為 PyInstaller 打包後的執行檔。"""
    return bool(getattr(sys, "frozen", False))


def app_dir() -> Path:
    """程式所在目錄。打包後為 exe 所在目錄，開發時為專案根目錄。"""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def bundle_dir() -> Path:
    """PyInstaller 執行期解壓目錄；未打包時等同 app_dir()。"""
    meipass = getattr(sys, "_MEIPASS", None)
    return Path(meipass) if meipass else app_dir()


def profile_search_dirs() -> list:
    """profile YAML 搜尋順序（先出現者優先，重複的 profile key 以先者為準）。

    1. exe/專案旁的 profiles\\        ← 使用者自行新增 FY27 時放這裡
    2. 打包內附的 profiles\\
    3. exe/專案根目錄本身            ← 相容舊版把 yaml 放同層的用法
    4. Debug\\                        ← 相容既有 repo 目錄結構
    """
    candidates = [
        app_dir() / PROFILE_DIR_NAME,
        bundle_dir() / PROFILE_DIR_NAME,
        app_dir(),
        app_dir() / "Debug",
    ]
    seen = []
    for d in candidates:
        if d.is_dir() and not any(d.samefile(s) for s in seen):
            seen.append(d)
    return seen


def user_profile_dir() -> Path:
    """使用者新增 profile 的建議位置（「開啟設定檔資料夾」按鈕會開這裡）。"""
    return app_dir() / PROFILE_DIR_NAME
