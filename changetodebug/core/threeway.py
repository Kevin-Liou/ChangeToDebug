"""行導向的三方合併（diff3）。

用途：規則的 old_code 因為 codebase 更新而比對不到時，改用三份資料判斷該怎麼做。

    BASE    改動前的原始檔（base 快照）
    OURS    BASE 套用本規則後應有的樣子
    THEIRS  專案裡現在的內容

    上游動 A 區、我們動 B 區  -> 兩邊都保留，自動合併
    上游與我們動同一區        -> 衝突，交給人處理

沒有引入外部套件：這裡是標準的 diff3 同步區演算法，用 difflib 的匹配區塊實作，
約一百行。工具要打包成單一 exe，多一個相依就多一份出錯的可能。
"""

import difflib
from dataclasses import dataclass, field


@dataclass
class Conflict:
    """一段兩邊都改、且改法不同的區域。"""

    base: list = field(default_factory=list)
    ours: list = field(default_factory=list)
    theirs: list = field(default_factory=list)
    line: int = 0           # 在合併結果中的大約行號（1 起算）


@dataclass
class MergeResult:
    lines: list = field(default_factory=list)
    conflicts: list = field(default_factory=list)
    #: 依序記錄合併結果的組成：("text", [行...]) 或 ("conflict", Conflict)。
    #: lines 在衝突處只放了我方版本當佔位，看起來像一份乾淨的結果；要產生帶衝突
    #: 標記的檔案就必須知道衝突落在哪一段，所以走訪時一併記下來。
    blocks: list = field(default_factory=list)
    took_ours: int = 0          # 只有我方改動的區段數
    took_theirs: int = 0        # 只有上游改動的區段數
    same: int = 0               # 兩邊改法相同的區段數

    @property
    def ok(self):
        return not self.conflicts

    @property
    def text(self):
        return "\n".join(self.lines)

    @property
    def changed_regions(self):
        return self.took_ours + self.took_theirs + self.same + len(self.conflicts)


def _sync_regions(base, ours, theirs):
    """找出 base / ours / theirs 三方同時一致的區段。

    回傳 [(base_start, base_end, ours_start, ours_end, theirs_start, theirs_end), ...]，
    最後補一筆長度為零的哨兵，讓呼叫端能一併處理尾端的差異區。
    """
    ours_blocks = difflib.SequenceMatcher(None, base, ours, autojunk=False).get_matching_blocks()
    theirs_blocks = difflib.SequenceMatcher(None, base, theirs, autojunk=False).get_matching_blocks()

    regions = []
    i = j = 0
    while i < len(ours_blocks) and j < len(theirs_blocks):
        base_i, ours_i, len_i = ours_blocks[i]
        base_j, theirs_j, len_j = theirs_blocks[j]

        # 兩個匹配區在 base 上的交集，就是三方都一致的部分
        start = max(base_i, base_j)
        end = min(base_i + len_i, base_j + len_j)
        if start < end:
            regions.append((start, end,
                            ours_i + (start - base_i), ours_i + (end - base_i),
                            theirs_j + (start - base_j), theirs_j + (end - base_j)))

        # 前進在 base 上先結束的那一邊
        if base_i + len_i < base_j + len_j:
            i += 1
        else:
            j += 1

    regions.append((len(base), len(base), len(ours), len(ours), len(theirs), len(theirs)))
    return regions


def merge(base, ours, theirs):
    """三方合併三份「行清單」，回傳 MergeResult。"""
    result = MergeResult()
    base_pos = ours_pos = theirs_pos = 0

    def keep(lines):
        """把一段沒有爭議的內容同時記進 lines 與 blocks。"""
        if not lines:
            return
        result.lines.extend(lines)
        if result.blocks and result.blocks[-1][0] == "text":
            result.blocks[-1][1].extend(lines)
        else:
            result.blocks.append(("text", list(lines)))

    for base_start, base_end, ours_start, ours_end, theirs_start, theirs_end in \
            _sync_regions(base, ours, theirs):
        base_chunk = base[base_pos:base_start]
        ours_chunk = ours[ours_pos:ours_start]
        theirs_chunk = theirs[theirs_pos:theirs_start]

        if ours_chunk or theirs_chunk or base_chunk:
            if ours_chunk == theirs_chunk:
                # 兩邊做了相同的事（或都沒動）
                keep(ours_chunk)
                if ours_chunk != base_chunk:
                    result.same += 1
            elif ours_chunk == base_chunk:
                # 只有上游改
                keep(theirs_chunk)
                result.took_theirs += 1
            elif theirs_chunk == base_chunk:
                # 只有我們改
                keep(ours_chunk)
                result.took_ours += 1
            else:
                conflict = Conflict(list(base_chunk), list(ours_chunk),
                                    list(theirs_chunk), line=len(result.lines) + 1)
                result.conflicts.append(conflict)
                result.blocks.append(("conflict", conflict))
                # 佔位用我方版本；有衝突時上層不會寫入這個檔案
                result.lines.extend(ours_chunk)

        keep(base[base_start:base_end])
        base_pos, ours_pos, theirs_pos = base_end, ours_end, theirs_end

    return result


def merge_text(base_text, ours_text, theirs_text):
    """文字版入口。輸入須先正規化換行為 \\n。"""
    return merge(base_text.split("\n"), ours_text.split("\n"), theirs_text.split("\n"))


#: 衝突標記。與 git 的 diff3 格式一致，任何合併工具與純文字編輯器都認得。
MARK_LEFT = "<<<<<<<"
MARK_BASE = "|||||||"
MARK_MID = "======="
MARK_RIGHT = ">>>>>>>"

MARKERS = (MARK_LEFT, MARK_BASE, MARK_MID, MARK_RIGHT)


def render_conflicts(result, left_label="目前 source", right_label="profile 期望的修改",
                     base_label="共同起點 (base 快照)"):
    """把合併結果輸出成帶 diff3 衝突標記的文字。

    左右順序刻意對齊 git 與合併工具的左右欄：左邊是專案裡現在的內容，右邊是
    profile 想要的結果。注意本模組內部的 ours 是 profile、theirs 是目前 source，
    與 git 的命名相反，所以這裡是 theirs 在前、ours 在後。

    沒有 blocks（例如用舊版資料重建的 MergeResult）時退回 result.text，
    至少不會產生空檔案。
    """
    if not result.blocks:
        return result.text
    out = []
    for kind, payload in result.blocks:
        if kind == "text":
            out.extend(payload)
            continue
        out.append(f"{MARK_LEFT} {left_label}")
        out.extend(payload.theirs)
        out.append(f"{MARK_BASE} {base_label}")
        out.extend(payload.base)
        out.append(MARK_MID)
        out.extend(payload.ours)
        out.append(f"{MARK_RIGHT} {right_label}")
    return "\n".join(out)


def has_markers(text):
    """文字裡還留著未解決的衝突標記嗎。

    只認行首，而且必須同時出現 << 與 >> 兩端。BIOS source 裡常見的
    ========================= 分隔線會命中單獨的 =======，只看它會把一份
    已經解好的檔案誤判成還沒解完。
    """
    left = right = False
    for line in text.split("\n"):
        if line.startswith(MARK_LEFT):
            left = True
        elif line.startswith(MARK_RIGHT):
            right = True
        if left and right:
            return True
    return False


def added_lines(old_text, new_text):
    """new_code 相對 old_code 真正新增的那幾行（去掉空白行）。

    合併之後 old_code / new_code 裡的 context 很可能已經被上游改過，整段比對必然失敗。
    要確認「本規則的改動有沒有真的進去」，只能看它實際新增的內容。
    """
    old_lines = old_text.split("\n")
    new_lines = new_text.split("\n")
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    added = []
    for tag, _, _, start, end in matcher.get_opcodes():
        if tag in ("insert", "replace"):
            added.extend(new_lines[start:end])
    return [line for line in added if line.strip()]


def describe(conflict, limit=6):
    """把一段衝突整理成可讀的說明，供記錄與衝突報告使用。"""
    def block(title, lines):
        if not lines:
            return [f"  {title}：（無內容）"]
        shown = lines[:limit]
        out = [f"  {title}："] + [f"    {line}" for line in shown]
        if len(lines) > limit:
            out.append(f"    …另有 {len(lines) - limit} 行")
        return out

    parts = [f"衝突（合併結果第 {conflict.line} 行附近）"]
    parts += block("profile 期望", conflict.ours)
    parts += block("目前 source", conflict.theirs)
    parts += block("共同起點", conflict.base)
    return "\n".join(parts)
