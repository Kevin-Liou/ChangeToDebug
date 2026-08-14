"""使用者設定保存（最近路徑、選項狀態、主題）。"""

import json
from pathlib import Path

from ..appinfo import LEGACY_SETTINGS_FILE, SETTINGS_FILE, app_dir

MAX_RECENT = 8

DEFAULTS = {
    "recent_paths": [],
    "theme": "light",
    "backup": True,
    "dry_run": False,
    "verify_after_run": True,
    "merge_fallback": True,
    # 解決合併衝突用的外部工具。VS Code 的用法為
    #   code --merge <目前內容> <profile 期望> <共同起點> <輸出>
    "merge_tool_command": "code",
    "enable_all_debug_flags": False,
    "driver_mode": "memory",
    "driver_names": "",
    "marker_start_hex": 0xA0,
    "marker_target": "CpuDeadLoop ();",
    "enabled_tasks": ["patchset"],
}


class Settings:
    def __init__(self, path=None):
        self.path = Path(path) if path else app_dir() / SETTINGS_FILE
        self.data = dict(DEFAULTS)
        self.load()

    # ---- 讀寫 ----
    def load(self):
        if self.path.is_file():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                if isinstance(saved, dict):
                    self.data.update(saved)
            except Exception:
                pass
        else:
            self._migrate_legacy()
        return self.data

    def _migrate_legacy(self):
        """沿用舊版 last_path_config.json 的最近路徑，讓使用者無痛升級。"""
        for legacy in (app_dir() / LEGACY_SETTINGS_FILE,
                       app_dir() / "Debug" / LEGACY_SETTINGS_FILE):
            if not legacy.is_file():
                continue
            try:
                with open(legacy, "r", encoding="utf-8") as f:
                    paths = json.load(f).get("recent_paths", [])
                if isinstance(paths, list):
                    self.data["recent_paths"] = [str(p) for p in paths][:MAX_RECENT]
                    return
            except Exception:
                continue

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    # ---- 便利存取 ----
    def get(self, key, default=None):
        return self.data.get(key, DEFAULTS.get(key, default))

    def set(self, key, value):
        self.data[key] = value

    def push_recent_path(self, path):
        path = str(path).strip()
        if not path:
            return
        recent = [p for p in self.data.get("recent_paths", []) if p != path]
        recent.insert(0, path)
        self.data["recent_paths"] = recent[:MAX_RECENT]
