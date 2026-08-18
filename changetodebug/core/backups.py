"""備份檔的盤點與清理。

修補引擎在寫入前會把原檔複製成 `原檔名.bak.<執行時間戳>`，同一次執行共用一個時間戳。
那是救命用的，但它們留在 BIOS source 裡不會自動消失——尤其「移除 Change」把修改還原
之後，樹上除了這些備份就沒有別的殘留了，卻仍然一堆未追蹤檔案掛在 git status 上。

這裡只負責找出來與刪掉，選哪些刪一律由使用者決定。刪除是不可逆的，因此：
  * 只認嚴格的 `.bak.` + 14 位數字，不會誤刪其他任何東西
  * 只刪一般檔案，遇到目錄或連結一律跳過
"""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

#: 掃描時直接跳過的目錄
SKIP_DIRS = {".git", "Build", "build", "__pycache__", ".vs", ".vscode"}

#: 嚴格比對修補引擎的命名：xxx.bak.20260818112353
BACKUP_RE = re.compile(r"\.bak\.(\d{14})$")


@dataclass
class BackupGroup:
    """同一次執行留下的備份。"""

    stamp: str = ""
    paths: list = field(default_factory=list)

    @property
    def count(self):
        return len(self.paths)

    @property
    def size(self):
        total = 0
        for path in self.paths:
            try:
                total += os.path.getsize(path)
            except OSError:
                pass
        return total

    @property
    def when(self):
        """把時間戳轉成可讀時間；格式不對就原樣回傳。"""
        try:
            return datetime.strptime(self.stamp, "%Y%m%d%H%M%S").strftime(
                "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return self.stamp


def scan(base_path, logger=None):
    """掃出專案底下所有備份檔，依執行時間戳分組（新的在前）。"""
    base = Path(base_path)
    if not base.is_dir():
        return []

    groups = {}
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            match = BACKUP_RE.search(name)
            if match:
                groups.setdefault(match.group(1), []).append(Path(root) / name)

    result = [BackupGroup(stamp, sorted(paths)) for stamp, paths in groups.items()]
    result.sort(key=lambda g: g.stamp, reverse=True)
    if logger is not None:
        logger.info(f"找到 {sum(g.count for g in result)} 個備份檔，"
                    f"來自 {len(result)} 次執行")
    return result


def remove(paths, logger):
    """刪除指定的備份檔。回傳 (刪除數, [(路徑, 原因), ...])。"""
    deleted, failed = 0, []
    for path in paths:
        path = Path(path)
        # 再確認一次檔名，避免呼叫端傳錯東西進來
        if not BACKUP_RE.search(path.name):
            failed.append((str(path), "檔名不是備份檔格式，未刪除"))
            continue
        if not path.is_file():
            failed.append((str(path), "不是一般檔案，未刪除"))
            continue
        try:
            path.unlink()
            deleted += 1
        except Exception as exc:
            failed.append((str(path), str(exc)))

    if deleted:
        logger.ok(f"已刪除 {deleted} 個備份檔")
    for path, reason in failed:
        logger.warn(f"未刪除：{path} -> {reason}")
    return deleted, failed


def human_size(size):
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.0f} KB"
    return f"{size / 1024 / 1024:.1f} MB"
