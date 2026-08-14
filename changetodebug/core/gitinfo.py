"""唯讀的 git 版本查詢，用來判斷專案與 profile 產生基準相差多遠。

設計原則：
  * 全部是唯讀指令（rev-parse / cat-file / rev-list / merge-base），不會動到工作目錄。
  * 任何失敗都安靜降級成一段說明文字，不拋例外、不阻擋主流程——
    沒有 git、不是 repo、base commit 不在這個 clone 裡，都是正常情況。
  * 打包成 windowed exe 後 subprocess 會閃出 console 視窗，故一律帶 CREATE_NO_WINDOW。
"""

import os
import subprocess
from dataclasses import dataclass

#: 單一 git 指令的逾時秒數（都是本機操作，超過就是有問題）
GIT_TIMEOUT = 10

#: Windows 下避免閃出 console 視窗；其他平台沒有這個旗標
_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


@dataclass
class DriftInfo:
    """一個 repo 與 profile 產生基準之間的差距。"""

    repo: str = ""              # 顯示用名稱（相對於專案根目錄的子路徑）
    base_commit: str = ""       # profile 宣告的基準
    head_commit: str = ""
    base_known: bool = False    # base_commit 是否存在於這個 repo
    ahead: int = 0              # 只在 HEAD 側的 commit 數
    behind: int = 0             # 只在 base 側的 commit 數（> 0 代表分岔）
    merge_base: str = ""
    repo_root: str = ""         # 實際的 repo 根目錄
    nested: bool = False        # 查詢路徑本身不是 repo 根目錄（往上找到的）
    error: str = ""

    @property
    def diverged(self):
        return self.behind > 0

    @property
    def needs_attention(self):
        """GUI 用來決定要不要把狀態燈降成警告。"""
        return bool(self.error) or not self.base_known or self.diverged

    def summary(self):
        if self.error:
            return self.error
        if not self.base_known:
            return (f"profile 基準 {_short(self.base_commit)} 不存在於此 repo"
                    f"（可能是不同的 clone，或淺層複製）")
        if self.ahead == 0 and self.behind == 0:
            text = f"與 profile 基準 {_short(self.base_commit)} 完全一致"
        elif self.diverged:
            text = (f"與 profile 基準分岔：上游前進 {self.ahead}，基準側另有 {self.behind}"
                    f"（共同祖先 {_short(self.merge_base)}）")
        else:
            text = f"上游已前進 {self.ahead} 個 commit（基準 {_short(self.base_commit)}）"
        if self.nested:
            text += f"　※ 此路徑不是 repo 根目錄，實際查詢的是 {self.repo_root}"
        return text


def _short(commit):
    return (commit or "")[:8]


# ---------------------------------------------------------------- 指令包裝

def _git(repo_dir, *args):
    """執行一個唯讀 git 指令。失敗（含找不到 git、逾時、非零回傳）一律回 None。"""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_dir), *args],
            capture_output=True, timeout=GIT_TIMEOUT, creationflags=_NO_WINDOW)
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8", "replace").strip()


def repo_root(path):
    """回傳該路徑所屬的 git repo 根目錄；不是 repo 時回 None。"""
    return _git(path, "rev-parse", "--show-toplevel")


def is_git_repo(path):
    return repo_root(path) is not None


def _same_dir(a, b):
    try:
        return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))
    except Exception:
        return False


# ---------------------------------------------------------------- 主要查詢

def drift(repo_dir, base_commit, repo_label=""):
    """比較 repo_dir 的 HEAD 與 base_commit 的差距。

    base_commit 為空時回傳 None（代表這個 profile 沒有宣告基準，不需要檢查）。
    其餘情況一律回傳 DriftInfo，呼叫端只要印 summary() 即可。
    """
    if not base_commit:
        return None

    info = DriftInfo(repo=repo_label or str(repo_dir), base_commit=str(base_commit))

    root = repo_root(repo_dir)
    if root is None:
        info.error = "不是 git 工作目錄，無法檢查版本"
        return info
    info.repo_root = root
    info.nested = not _same_dir(root, repo_dir)

    info.head_commit = _git(repo_dir, "rev-parse", "HEAD") or ""

    # base commit 不在這個 clone 裡（不同來源 / 淺層複製）就到此為止
    if _git(repo_dir, "cat-file", "-e", f"{base_commit}^{{commit}}") is None:
        return info
    info.base_known = True

    # 三個點：base 與 HEAD 可能是分岔的，單向計數會誤導
    counts = _git(repo_dir, "rev-list", "--left-right", "--count",
                  f"{base_commit}...HEAD")
    if counts:
        parts = counts.split()
        if len(parts) >= 2:
            try:
                info.behind, info.ahead = int(parts[0]), int(parts[1])
            except ValueError:
                pass

    info.merge_base = _git(repo_dir, "merge-base", base_commit, "HEAD") or ""
    return info
