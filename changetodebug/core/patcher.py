"""文字修補引擎：負責讀檔、比對、備份、寫回。

相較舊版 DebugMode_Modify.py 的改良：
  * 會分辨「找不到片段」與「已經改過了」，後者不再被誤報為失敗。
  * 支援多重編碼偵測（utf-8 / utf-8-sig / cp950 / latin-1）並以原編碼寫回。
  * 保留原檔換行風格 (LF/CRLF)，並回報實際取代次數。
  * 支援 regex 規則，old_code == new_code 會被標記為 noop 而非「成功」。
  * 同一次執行共用一個備份時間戳，方便整批還原。
"""

import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# ---- 修補結果狀態 ----
STATUS_MODIFIED = "modified"          # 實際寫入成功
STATUS_PREVIEW = "preview"            # Dry-Run，比對成功但未寫入
STATUS_ALREADY = "already"            # 已是修改後的樣子
STATUS_NOT_FOUND = "not_found"        # 檔案在，但找不到指定片段
STATUS_MISSING_FILE = "missing_file"  # 檔案不存在
STATUS_NOOP = "noop"                  # 規則本身 old == new，改了也沒差
STATUS_ERROR = "error"                # 讀寫或規則錯誤
STATUS_SKIPPED = "skipped"            # 被選項過濾掉（例如 option_debug_flag）
STATUS_COPIED = "copied"              # 新增檔案已複製
STATUS_CONFLICT = "conflict"          # 目標檔已存在且內容不同，未覆蓋

#: 視為「這條規則沒問題」的狀態
GOOD_STATUS = {STATUS_MODIFIED, STATUS_PREVIEW, STATUS_ALREADY, STATUS_NOOP, STATUS_COPIED}

STATUS_TEXT = {
    STATUS_MODIFIED: "已修改",
    STATUS_PREVIEW: "預覽通過",
    STATUS_ALREADY: "已套用過",
    STATUS_NOT_FOUND: "找不到片段",
    STATUS_MISSING_FILE: "檔案不存在",
    STATUS_NOOP: "規則無變化",
    STATUS_ERROR: "錯誤",
    STATUS_SKIPPED: "略過",
    STATUS_COPIED: "已新增",
    STATUS_CONFLICT: "已存在且不同",
}

_ENCODINGS = ("utf-8", "utf-8-sig", "cp950", "latin-1")


@dataclass
class Rule:
    """一條修補規則。對應 profile YAML 中 modifications / platform_pcd_modifications 的一筆。"""

    rule_id: str = ""
    label: str = ""                     # 顯示用名稱
    sub_path: str = ""                  # 相對於專案根目錄的路徑（精準定位用）
    file_name: str = ""                 # 只給檔名時代表要掃描目錄尋找同名檔（可用 * ? 萬用字元）
    old_code: str = ""
    new_code: str = ""
    regex: bool = False
    option_debug_flag: bool = False     # True = 只有勾選「啟用所有 Debug Flag」才套用
    note: str = ""
    source: str = "modifications"       # modifications / platform_pcd_modifications / new_files
    new_file_source: str = ""           # 有值代表這是「新增檔案」規則，值為來源檔絕對路徑
    overwrite: bool = False             # 新增檔案時，目標已存在且內容不同是否覆蓋

    @property
    def is_new_file(self):
        return bool(self.new_file_source)

    @property
    def target_display(self):
        return self.sub_path or self.file_name or "(未指定)"


@dataclass
class VerifyCheck:
    """修改完成後要重新確認的條件（由 verifier.py 重新讀檔驗證）。"""

    contains: list = field(default_factory=list)      # 這些字串必須出現在檔案裡
    absent: list = field(default_factory=list)        # 這些字串不應該再出現
    regex_absent: list = field(default_factory=list)  # 這些 regex 不應該再命中
    same_as: str = ""                                 # 內容必須與這個來源檔相同（新增檔案用）

    def is_empty(self):
        return not (self.contains or self.absent or self.regex_absent or self.same_as)


@dataclass
class PatchResult:
    file_path: str
    status: str
    message: str = ""
    rule_id: str = ""
    label: str = ""
    count: int = 0
    verify: object = None       # VerifyCheck；None 表示這筆不需要（或無法）驗證

    @property
    def ok(self):
        return self.status in GOOD_STATUS

    @property
    def status_text(self):
        return STATUS_TEXT.get(self.status, self.status)


@dataclass
class PatchStats:
    """一批修補的統計。"""

    results: list = field(default_factory=list)

    def add(self, result):
        self.results.append(result)
        return result

    def count_of(self, *statuses):
        return sum(1 for r in self.results if r.status in statuses)

    @property
    def total(self):
        return len(self.results)

    @property
    def changed(self):
        return self.count_of(STATUS_MODIFIED, STATUS_PREVIEW, STATUS_COPIED)

    @property
    def already(self):
        return self.count_of(STATUS_ALREADY)

    @property
    def failed(self):
        return self.count_of(STATUS_NOT_FOUND, STATUS_MISSING_FILE, STATUS_ERROR,
                             STATUS_CONFLICT)

    @property
    def skipped(self):
        return self.count_of(STATUS_SKIPPED, STATUS_NOOP)

    def merge(self, other):
        self.results.extend(other.results)
        return self


# ---------------------------------------------------------------- 換行 / 編碼

def normalize_newlines(text):
    """統一換行為 \\n，避免 CRLF/LF 差異造成比對失敗。"""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def detect_newline_style(text):
    return "\r\n" if "\r\n" in text else "\n"


def restore_newlines(text, style):
    return text.replace("\n", "\r\n") if style == "\r\n" else text


def read_text(file_path):
    """回傳 (content, encoding)。依序嘗試常見編碼，最後以 latin-1 保底。"""
    raw = Path(file_path).read_bytes()
    for enc in _ENCODINGS:
        try:
            return raw.decode(enc), enc
        except (UnicodeDecodeError, LookupError):
            continue
    # latin-1 理論上不會失敗，這行只是防禦
    return raw.decode("utf-8", errors="surrogatepass"), "utf-8"


def write_text(file_path, content, encoding):
    with open(file_path, "w", encoding=encoding, newline="", errors="surrogatepass") as f:
        f.write(content)


# ---------------------------------------------------------------- 引擎

class PatchEngine:
    """實際執行修補。dry_run / backup 等選項在建構時決定。"""

    def __init__(self, logger, dry_run=False, backup=True, run_stamp=None):
        self.logger = logger
        self.dry_run = dry_run
        self.backup = backup
        self.run_stamp = run_stamp or datetime.now().strftime("%Y%m%d%H%M%S")
        self._backed_up = set()

    # ---- 備份 ----
    def backup_file(self, file_path):
        if not self.backup or self.dry_run:
            return None
        key = os.path.normcase(os.path.abspath(file_path))
        if key in self._backed_up:
            return None     # 同一次執行內同檔只備份一次，保留最原始內容
        backup_path = f"{file_path}.bak.{self.run_stamp}"
        try:
            shutil.copy2(file_path, backup_path)
            self._backed_up.add(key)
            self.logger.debug(f"已備份：{backup_path}")
            return backup_path
        except Exception as exc:
            self.logger.warn(f"備份失敗（仍會繼續修改）：{file_path} -> {exc}")
            return None

    @property
    def backup_count(self):
        return len(self._backed_up)

    # ---- 單一規則 ----
    def apply(self, file_path, rule):
        file_path = str(file_path)
        label = rule.label or rule.target_display

        if not rule.old_code:
            return PatchResult(file_path, STATUS_ERROR, "規則缺少 old_code",
                               rule.rule_id, label)

        if not rule.regex and rule.old_code == rule.new_code:
            self.logger.warn(f"規則無變化（old_code 與 new_code 相同）：{label}")
            return PatchResult(file_path, STATUS_NOOP, "old_code 與 new_code 相同",
                               rule.rule_id, label)

        if not os.path.isfile(file_path):
            self.logger.warn(f"檔案不存在：{file_path}")
            return PatchResult(file_path, STATUS_MISSING_FILE, "檔案不存在",
                               rule.rule_id, label)

        try:
            content, encoding = read_text(file_path)
        except Exception as exc:
            self.logger.error(f"讀取失敗：{file_path} -> {exc}")
            return PatchResult(file_path, STATUS_ERROR, str(exc), rule.rule_id, label)

        newline_style = detect_newline_style(content)
        norm = normalize_newlines(content)
        old = normalize_newlines(rule.old_code)
        new = normalize_newlines(rule.new_code)

        try:
            if rule.regex:
                pattern = re.compile(old, re.MULTILINE)
                replaced, count = pattern.subn(new, norm)
            else:
                count = norm.count(old)
                replaced = norm.replace(old, new) if count else norm
        except re.error as exc:
            self.logger.error(f"regex 規則錯誤：{label} -> {exc}")
            return PatchResult(file_path, STATUS_ERROR, f"regex 錯誤：{exc}",
                               rule.rule_id, label)

        check = _build_check(old, new, rule.regex)

        # 「插入型」規則（new_code 本身包含 old_code）套用後 old_code 仍然存在，
        # 若不先判斷是否已套用過，重跑就會重複插入一次。
        if new and not rule.regex and old in new and new in norm:
            self.logger.info(f"已套用過，略過：{file_path}  ({label})")
            return PatchResult(file_path, STATUS_ALREADY, "內容已是修改後的樣子",
                               rule.rule_id, label, verify=check)

        if count == 0:
            # 找不到 old_code 時，先確認是不是已經被改成 new_code 了
            if new and not rule.regex and new in norm:
                self.logger.info(f"已套用過，略過：{file_path}  ({label})")
                return PatchResult(file_path, STATUS_ALREADY, "內容已是修改後的樣子",
                                   rule.rule_id, label, verify=check)
            self.logger.warn(f"找不到指定片段：{file_path}  ({label})")
            return PatchResult(file_path, STATUS_NOT_FOUND, "找不到指定片段",
                               rule.rule_id, label)

        if self.dry_run:
            self.logger.info(f"[預覽] 將修改 {count} 處：{file_path}  ({label})")
            return PatchResult(file_path, STATUS_PREVIEW, f"可修改 {count} 處",
                               rule.rule_id, label, count)

        self.backup_file(file_path)
        try:
            write_text(file_path, restore_newlines(replaced, newline_style), encoding)
        except Exception as exc:
            self.logger.error(f"寫入失敗：{file_path} -> {exc}")
            return PatchResult(file_path, STATUS_ERROR, str(exc), rule.rule_id, label)

        self.logger.ok(f"已修改 {count} 處：{file_path}  ({label})")
        return PatchResult(file_path, STATUS_MODIFIED, f"已修改 {count} 處",
                           rule.rule_id, label, count, verify=check)

    # ---- 新增檔案（profile 的 new_files） ----
    def copy_file(self, source, target, label="", overwrite=False):
        """把 profile 帶的檔案複製到專案裡。已存在且內容相同視為已套用過。"""
        source, target = Path(source), Path(target)
        label = label or str(target)

        if not source.is_file():
            self.logger.error(f"新增檔案的來源不存在：{source}")
            return PatchResult(str(target), STATUS_ERROR, f"來源檔不存在：{source}", label=label)

        check = VerifyCheck(same_as=str(source))

        if target.is_file():
            if _same_text(source, target):
                self.logger.info(f"檔案已存在且內容相同，略過：{target}")
                return PatchResult(str(target), STATUS_ALREADY, "已存在且內容相同",
                                   label=label, verify=check)
            if not overwrite:
                self.logger.warn(f"檔案已存在但內容不同，未覆蓋：{target}")
                return PatchResult(str(target), STATUS_CONFLICT,
                                   "已存在但內容不同（需 overwrite: true 才會覆蓋）", label=label)

        if self.dry_run:
            action = "覆蓋" if target.is_file() else "新增"
            self.logger.info(f"[預覽] 將{action}檔案：{target}")
            return PatchResult(str(target), STATUS_PREVIEW, f"可{action}", label=label, count=1)

        try:
            if target.is_file():
                self.backup_file(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        except Exception as exc:
            self.logger.error(f"複製失敗：{target} -> {exc}")
            return PatchResult(str(target), STATUS_ERROR, str(exc), label=label)

        self.logger.ok(f"已新增檔案：{target}")
        return PatchResult(str(target), STATUS_COPIED, "已新增", label=label, count=1,
                           verify=check)

    # ---- 直接對整個檔案做字串取代（給 Driver Debug 用） ----
    @staticmethod
    def _pairs_check(pairs):
        return VerifyCheck(absent=[old for old, new in pairs if old and old not in new])

    def replace_pairs(self, file_path, pairs, label=""):
        """pairs 為 [(old, new), ...]，全部套用在同一個檔案上。"""
        file_path = str(file_path)
        if not os.path.isfile(file_path):
            return PatchResult(file_path, STATUS_MISSING_FILE, "檔案不存在", label=label)

        try:
            content, encoding = read_text(file_path)
        except Exception as exc:
            self.logger.error(f"讀取失敗：{file_path} -> {exc}")
            return PatchResult(file_path, STATUS_ERROR, str(exc), label=label)

        total = 0
        updated = content
        for old, new in pairs:
            if not old:
                continue
            hit = updated.count(old)
            if hit:
                updated = updated.replace(old, new)
                total += hit

        check = self._pairs_check(pairs)

        if total == 0:
            return PatchResult(file_path, STATUS_ALREADY, "沒有需要取代的字串",
                               label=label, verify=check)

        if self.dry_run:
            self.logger.info(f"[預覽] 將取代 {total} 處：{file_path}")
            return PatchResult(file_path, STATUS_PREVIEW, f"可取代 {total} 處", label=label, count=total)

        self.backup_file(file_path)
        try:
            write_text(file_path, updated, encoding)
        except Exception as exc:
            self.logger.error(f"寫入失敗：{file_path} -> {exc}")
            return PatchResult(file_path, STATUS_ERROR, str(exc), label=label)

        self.logger.ok(f"已取代 {total} 處：{file_path}")
        return PatchResult(file_path, STATUS_MODIFIED, f"已取代 {total} 處",
                           label=label, count=total, verify=check)

    # ---- 寫回整份內容（給行編輯型的 inf 修改用） ----
    def write_lines(self, file_path, lines, encoding, label="", verify=None):
        if self.dry_run:
            self.logger.info(f"[預覽] 將更新：{file_path}")
            return PatchResult(file_path, STATUS_PREVIEW, "可更新", label=label, count=1)
        self.backup_file(file_path)
        try:
            with open(file_path, "w", encoding=encoding, newline="", errors="surrogatepass") as f:
                f.writelines(lines)
        except Exception as exc:
            self.logger.error(f"寫入失敗：{file_path} -> {exc}")
            return PatchResult(file_path, STATUS_ERROR, str(exc), label=label)
        self.logger.ok(f"已更新：{file_path}")
        return PatchResult(file_path, STATUS_MODIFIED, "已更新", label=label, count=1,
                           verify=verify)


def _same_text(path_a, path_b):
    """比對兩個檔案的文字內容（忽略換行風格差異）。"""
    try:
        text_a, _ = read_text(path_a)
        text_b, _ = read_text(path_b)
    except Exception:
        return False
    return normalize_newlines(text_a) == normalize_newlines(text_b)


def _build_check(old, new, is_regex):
    """依規則型態決定「改完之後應該長什麼樣」。"""
    if is_regex:
        # regex 的 new_code 可能含有 \1 之類的回填，無法直接比對字面值，
        # 只能確認原本的 pattern 已經不再命中。
        return VerifyCheck(regex_absent=[old])
    check = VerifyCheck()
    if new:
        check.contains.append(new)
    # new_code 內含 old_code 時（例如只是在原內容旁補行），舊字串本來就還會在
    if old and old not in new:
        check.absent.append(old)
    return check
