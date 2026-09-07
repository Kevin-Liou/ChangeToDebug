"""文字修補引擎：負責讀檔、比對、備份、寫回。

相較舊版 DebugMode_Modify.py 的改良：
  * 會分辨「找不到片段」與「已經改過了」，後者不再被誤報為失敗。
  * 支援多重編碼偵測（utf-8 / utf-8-sig / cp950 / latin-1）並以原編碼寫回。
  * 保留原檔換行風格 (LF/CRLF)，並回報實際取代次數。
  * 支援 regex 規則，old_code == new_code 會被標記為 noop 而非「成功」。
  * 同一次執行共用一個備份時間戳，方便整批還原。
"""

import dataclasses
import difflib
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
STATUS_MERGED = "merged"              # old_code 比對不到，改用 base 做 3-way merge 成功
STATUS_MERGE_CONFLICT = "merge_conflict"   # 3-way merge 有衝突，未寫入，需人工處理
STATUS_ROLLED_BACK = "rolled_back"    # 同一檔案有衝突，這條先前成功的修改已被還原

#: 視為「這條規則沒問題」的狀態
GOOD_STATUS = {STATUS_MODIFIED, STATUS_PREVIEW, STATUS_ALREADY, STATUS_NOOP,
               STATUS_COPIED, STATUS_MERGED}

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
    STATUS_MERGED: "已合併",
    STATUS_MERGE_CONFLICT: "合併衝突",
    STATUS_ROLLED_BACK: "已還原",
}

_ENCODINGS = ("utf-8", "utf-8-sig", "cp950", "latin-1")

#: base 與目前檔案的相似度低於此值就不做 3-way merge——
#: 這種 base 不可能是這個檔案的祖先，合併結果沒有意義
MIN_BASE_SIMILARITY = 0.5


@dataclass
class Anchor:
    """規則的另一組錨點：同一個修改在另一個上游版本上的 old_code / new_code。

    上游改到規則要改的那一段、使用者在合併工具裡解決衝突之後，工具會把解好的結果
    以「新增一組錨點」寫回 profile，而不是覆蓋原本的 old_code——覆蓋會讓還沒跟上
    上游的那些樹套不上。套用時逐組嘗試，哪一組比對得到就用哪一組。
    """

    old_code: str = ""
    new_code: str = ""
    base_file: str = ""                 # 相對於 profile 套件 base/ 目錄；空字串代表沒有 base
    covers: list = field(default_factory=list)   # 這份 base 取自哪個檔案（相對專案根目錄）
    note: str = ""


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
    regex_applied_check: str = ""       # regex 規則專用：套用後應該命中的樣式（用來辨識「已套用過」）
    expect_count: int = 0               # > 0 時，命中數必須剛好這麼多，否則報錯不寫入
    option_debug_flag: bool = False     # True = 只有勾選「啟用所有 Debug Flag」才套用
    note: str = ""
    source: str = "modifications"       # modifications / platform_pcd_modifications / new_files
    new_file_source: str = ""           # 有值代表這是「新增檔案」規則，值為來源檔絕對路徑
    overwrite: bool = False             # 新增檔案時，目標已存在且內容不同是否覆蓋
    anchors: list = field(default_factory=list)   # 額外的錨點（Anchor），規則本身是第一組

    @property
    def is_new_file(self):
        return bool(self.new_file_source)

    @property
    def target_display(self):
        return self.sub_path or self.file_name or "(未指定)"

    def variants(self):
        """依序回傳每一組錨點對應的「單錨點規則」：規則本身在前，再依 anchors 順序。

        回傳的每一個都是沒有 anchors 的 Rule，方便沿用單錨點的套用流程。
        """
        if not self.anchors:
            return [self]
        primary = dataclasses.replace(self, anchors=[])
        out = [primary]
        for anchor in self.anchors:
            out.append(dataclasses.replace(primary, old_code=anchor.old_code,
                                           new_code=anchor.new_code))
        return out


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
        return self.count_of(STATUS_MODIFIED, STATUS_PREVIEW, STATUS_COPIED, STATUS_MERGED)

    @property
    def already(self):
        return self.count_of(STATUS_ALREADY)

    @property
    def merged(self):
        return self.count_of(STATUS_MERGED)

    @property
    def conflicted(self):
        return self.count_of(STATUS_MERGE_CONFLICT)

    @property
    def rolled_back(self):
        return self.count_of(STATUS_ROLLED_BACK)

    @property
    def failed(self):
        return self.count_of(STATUS_NOT_FOUND, STATUS_MISSING_FILE, STATUS_ERROR,
                             STATUS_CONFLICT, STATUS_MERGE_CONFLICT, STATUS_ROLLED_BACK)

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

    def __init__(self, logger, dry_run=False, backup=True, run_stamp=None, diagnose=True,
                 conflict_sink=None):
        self.logger = logger
        self.dry_run = dry_run
        self.backup = backup
        self.run_stamp = run_stamp or datetime.now().strftime("%Y%m%d%H%M%S")
        self.diagnose = diagnose        # 比對失敗時是否輸出「最相似區塊」的差異
        self.conflict_sink = conflict_sink   # 合併衝突時把三方內容交出去保存
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
    def apply(self, file_path, rule, base_ref=None, reverse=False, anchor_refs=()):
        """套用一條規則；有多組錨點時自動挑能用的那一組。

        anchor_refs 與 rule.anchors 對齊，是每組額外錨點各自的 base（沒有就放 None）。

        挑選順序：
          1. 逐組做精確比對（含「已套用過」的判斷），第一組命中的就用——絕大多數
             情況在這裡就結束，成本與單錨點相同。
          2. 全部比對不到，才依各組 base 與現況的相似度由高到低嘗試 3-way merge。
             最像的 base 才是這個檔案真正的祖先，用它合出來的結果（或衝突）才有意義；
             一旦某組給出結果（合併成功或衝突）就停，不再拿更不像的 base 硬合。
          3. 全部都不行，用第一組走一次正常流程，讓它輸出「找不到片段」與診斷。
        """
        variants = rule.variants()
        if len(variants) == 1:
            return self._apply_single(file_path, rule, base_ref, reverse)

        label = rule.label or rule.target_display
        path = str(file_path)
        if rule.is_new_file or not os.path.isfile(path):
            return self._apply_single(path, variants[0], base_ref, reverse)
        try:
            norm = normalize_newlines(read_text(path)[0])
        except Exception:
            return self._apply_single(path, variants[0], base_ref, reverse)

        # 1) 精確比對
        for index, variant in enumerate(variants):
            if _variant_hits(norm, variant, reverse):
                if index:
                    note = rule.anchors[index - 1].note
                    self.logger.info(f"使用第 {index + 1} 組錨點"
                                     f"{'（' + note + '）' if note else ''}：{label}")
                return self._apply_single(path, variant, None, reverse)

        # 2) 3-way merge，base 最像現況的先
        refs = [base_ref] + list(anchor_refs)
        refs += [None] * (len(variants) - len(refs))
        ranked = []
        for index, (variant, ref) in enumerate(zip(variants, refs)):
            if ref is None:
                continue
            base_text = ref.read()
            if base_text is None:
                continue
            similarity = difflib.SequenceMatcher(
                None, base_text.split("\n"), norm.split("\n")).quick_ratio()
            ranked.append((similarity, index, variant, ref))
        for similarity, index, variant, ref in sorted(ranked, key=lambda r: (-r[0], r[1])):
            result = self._apply_single(path, variant, ref, reverse, quiet_not_found=True)
            if result.status != STATUS_NOT_FOUND:
                if index:
                    self.logger.info(f"以第 {index + 1} 組錨點的 base 做三方合併：{label}")
                return result

        # 3) 全部失敗
        return self._apply_single(path, variants[0], None, reverse)

    def _apply_single(self, file_path, rule, base_ref=None, reverse=False,
                      quiet_not_found=False):
        """套用一條單錨點規則。

        base_ref 有值時（profile 帶了 base 快照），exact 比對失敗會改用 3-way merge：
        以 base 為共同起點，判斷上游改的是不是我們要改的地方。

        reverse=True 代表反向移除：把 new_code 換回 old_code。刻意用「反向套用」而不是
        「還原成 base」——後者會把上游在這之後的改動一併抹掉，那不是精準移除。
        """
        file_path = str(file_path)
        forward_rule = rule

        if reverse:
            if rule.regex:
                # regex 的 new_code 可能含 \1 回填，無法反推原文
                self.logger.warn(f"regex 規則無法反向移除，已略過：{rule.label}")
                return PatchResult(file_path, STATUS_SKIPPED, "regex 規則無法反向移除",
                                   rule.rule_id, rule.label or rule.target_display)
            rule = dataclasses.replace(rule, old_code=rule.new_code,
                                       new_code=rule.old_code)
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
            # regex 規則的 new_code 可能含 \1 之類的回填，無法直接比對字面值，
            # 因此另外用 regex_applied_check 判斷是否已經套用過（否則重跑會誤報失敗）。
            if rule.regex and rule.regex_applied_check and _matches(rule.regex_applied_check, norm):
                self.logger.info(f"已套用過，略過：{file_path}  ({label})")
                return PatchResult(file_path, STATUS_ALREADY, "內容已是修改後的樣子",
                                   rule.rule_id, label, verify=check)
            # exact 比對不到時，若有 base 快照就改用 3-way merge
            if base_ref is not None:
                merged = self._merge_with_base(file_path, rule, norm, base_ref, label,
                                               newline_style, encoding, check,
                                               forward_rule, reverse)
                if merged is not None:
                    return merged

            # 多錨點逐組嘗試時，中間那幾組比對不到是預期中的事，不要每組都叫一次
            if not quiet_not_found:
                self.logger.warn(f"找不到指定片段：{file_path}  ({label})")
                if self.diagnose and not rule.regex:
                    from .diagnose import explain
                    self.logger.warn(explain(norm, old))
            return PatchResult(file_path, STATUS_NOT_FOUND, "找不到指定片段",
                               rule.rule_id, label)

        # 守門：規則宣告了預期命中數就必須剛好相符。
        # old_code 只保證在「產生 profile 當下的那份 source」中唯一，上游新增相似區塊後
        # 可能變成命中多處——那會安靜地多改幾個地方，比對失敗至少還會叫。
        if rule.expect_count and count != rule.expect_count:
            self.logger.error(f"命中 {count} 處，與規則宣告的 {rule.expect_count} 處不符，"
                              f"未寫入：{file_path}  ({label})")
            return PatchResult(file_path, STATUS_ERROR,
                               f"命中 {count} 處，預期 {rule.expect_count} 處",
                               rule.rule_id, label, count)

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

    # ---- 3-way merge（exact 比對失敗後的退路） ----
    def _merge_with_base(self, file_path, rule, current, base_ref, label,
                         newline_style, encoding, check, forward_rule=None,
                         reverse=False):
        """以 base 快照為共同起點做三方合併。

        回傳 PatchResult；判斷不適用時回傳 None，讓呼叫端沿用原本的「找不到片段」。

        反向移除時把三方對調：以「base 套用規則後」當共同起點、「base 原樣」當我方，
        合併結果就是「現況扣掉本規則的改動」，上游後來的改動不受影響。
        """
        from .threeway import added_lines, describe, merge_text

        base_text = base_ref.read()
        if base_text is None:
            self.logger.debug(f"base 快照讀取失敗，改用一般流程：{file_path}")
            return None

        # base 是「改動前」的狀態，正向規則理論上一定套得上；
        # 套不上代表這份 base 對不上這條規則，不能拿來 merge。
        applied, count = _apply_rule_to_text(base_text, forward_rule or rule)
        if count == 0 or applied == base_text:
            self.logger.debug(f"規則在 base 上無法套用，不做 merge：{label}")
            return None

        if reverse:
            base_text, ours_text = applied, base_text
        else:
            ours_text = applied

        source = "借用其他專案的 base" if base_ref.approximate else "base"
        if base_ref.approximate:
            note = f"（{source}"
            if base_ref.representative:
                note += f"：{base_ref.representative}"
            note += "）"
        else:
            note = ""

        # base 必須真的像是這個檔案的祖先，否則合併出來的東西沒有意義。
        # quick_ratio 是相似度的上界且只需線性時間，用來擋掉明顯不相干的 base 剛好。
        if difflib.SequenceMatcher(
                None, base_text.split("\n"), current.split("\n")
        ).quick_ratio() < MIN_BASE_SIMILARITY:
            self.logger.debug(f"base 與現況差異過大，不做 merge：{file_path}")
            return None

        result = merge_text(base_text, ours_text, current)

        # 借用其他專案的 base 時，衝突多半只代表「這兩個專案的檔案本來就不同」，
        # 而不是「上游改到了我們要改的地方」，報成衝突只會製造噪音並蓋掉真正的診斷。
        # 這種情況退回原本的流程，由「找不到片段」加診斷訊息說明差異。
        if result.conflicts and base_ref.approximate:
            self.logger.info(
                f"借用的 base 合併後有衝突（非本專案的 base），退回一般流程："
                f"{file_path}  ({label})")
            return None

        if result.conflicts:
            self.logger.error(
                f"合併衝突，未寫入：{file_path}  ({label}){note}　"
                f"上游與本規則改到同一段（{len(result.conflicts)} 處）")
            for conflict in result.conflicts[:3]:
                self.logger.warn(describe(conflict))
            if len(result.conflicts) > 3:
                self.logger.warn(f"（另有 {len(result.conflicts) - 3} 處衝突）")

            # 把三方內容留下來，讓使用者可以用合併工具處理
            if self.conflict_sink is not None and not self.dry_run:
                record = self.conflict_sink(file_path, base_text, ours_text, current,
                                            rule, len(result.conflicts),
                                            encoding=encoding, newline=newline_style)
                if record is not None:
                    self.logger.info(f"衝突內容已保存：{Path(record.base).parent}")
            return PatchResult(file_path, STATUS_MERGE_CONFLICT,
                               f"合併衝突 {len(result.conflicts)} 處，需人工處理",
                               rule.rule_id, label)

        merged = result.text

        # 守門：合併結果一定要真的含有本規則新增的內容，否則寧可宣告失敗。
        # 這裡不能比對整段 new_code——merge 的前提就是 context 已經被上游改過，
        # 整段一定對不上；只有「本規則實際新增的那幾行」才是有效的後置條件。
        # 這條檢查擋得住 base 對不上而 merge 產出一份看似成功卻沒改到東西的結果。
        added = added_lines(normalize_newlines(rule.old_code),
                            normalize_newlines(rule.new_code))
        if added:
            missing = [line for line in added if line not in merged]
            if missing:
                self.logger.warn(f"合併結果不含本規則新增的內容，放棄合併："
                                 f"{file_path}  ({label})")
                return None
        if merged == current:
            self.logger.debug(f"合併結果與現況相同，不視為修改：{file_path}")
            return None

        # 事後驗證同樣不能比對整段 new_code，改成確認新增的行都在
        merge_check = VerifyCheck(contains=list(added)) if added else None

        if self.dry_run:
            self.logger.info(
                f"[預覽] 可用 3-way merge 套用：{file_path}  ({label}){note}　"
                f"（採用上游 {result.took_theirs} 段、本規則 {result.took_ours} 段）")
            return PatchResult(file_path, STATUS_PREVIEW, f"可合併{note}",
                               rule.rule_id, label, 1)

        self.backup_file(file_path)
        try:
            write_text(file_path, restore_newlines(merged, newline_style), encoding)
        except Exception as exc:
            self.logger.error(f"寫入失敗：{file_path} -> {exc}")
            return PatchResult(file_path, STATUS_ERROR, str(exc), rule.rule_id, label)

        self.logger.ok(
            f"已用 3-way merge 套用：{file_path}  ({label}){note}　"
            f"（採用上游 {result.took_theirs} 段、本規則 {result.took_ours} 段）")
        return PatchResult(file_path, STATUS_MERGED, f"已合併{note}",
                           rule.rule_id, label, 1, verify=merge_check)

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

    # ---- 移除先前複製進來的新增檔案（new_files 的反向） ----
    def remove_file(self, source, target, label=""):
        """刪除 profile 帶進來的檔案。

        只刪「確定是我們放的」——內容與來源檔不同代表有人改過，寧可留著讓人自己判斷。
        """
        source, target = Path(source), Path(target)
        label = label or str(target)

        if not target.is_file():
            self.logger.info(f"檔案不存在，無須移除：{target}")
            return PatchResult(str(target), STATUS_ALREADY, "檔案不存在，無須移除",
                               label=label)

        if source.is_file() and not _same_text(source, target):
            self.logger.warn(f"檔案內容與來源不同，未移除：{target}")
            return PatchResult(str(target), STATUS_CONFLICT,
                               "內容與來源不同，可能被改過，未移除", label=label)

        if self.dry_run:
            self.logger.info(f"[預覽] 將移除檔案：{target}")
            return PatchResult(str(target), STATUS_PREVIEW, "可移除", label=label, count=1)

        self.backup_file(target)
        try:
            target.unlink()
        except Exception as exc:
            self.logger.error(f"移除失敗：{target} -> {exc}")
            return PatchResult(str(target), STATUS_ERROR, str(exc), label=label)

        self.logger.ok(f"已移除檔案：{target}")
        return PatchResult(str(target), STATUS_MODIFIED, "已移除", label=label, count=1)

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


def _apply_rule_to_text(text, rule):
    """把一條規則套用在文字上，回傳 (結果, 取代次數)。套不上時回傳原文與 0。"""
    old = normalize_newlines(rule.old_code)
    new = normalize_newlines(rule.new_code)
    if not old:
        return text, 0
    try:
        if rule.regex:
            return re.compile(old, re.MULTILINE).subn(new, text)
    except re.error:
        return text, 0
    count = text.count(old)
    return (text.replace(old, new) if count else text), count


def _variant_hits(norm, rule, reverse):
    """這組錨點在文字裡比對得到嗎（含已經是套用後的樣子）。只做便宜的探測，不套用。"""
    old = normalize_newlines(rule.new_code if reverse else rule.old_code)
    new = normalize_newlines(rule.old_code if reverse else rule.new_code)
    if not old:
        return False
    if rule.regex:
        return _matches(old, norm) or (bool(rule.regex_applied_check)
                                       and _matches(rule.regex_applied_check, norm))
    return old in norm or (bool(new) and new in norm)


def _matches(pattern, text):
    """安全地判斷 regex 是否命中；規則寫壞時當作沒命中，不讓它中斷主流程。"""
    try:
        return re.search(pattern, text, re.MULTILINE) is not None
    except re.error:
        return False


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
