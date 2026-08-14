"""比對失敗時的診斷：指出檔案中最相似的區塊，並列出差異。

規則失效通常有兩種原因，但「找不到指定片段」這一句話分不出來：
  * 上游只動了 old_code 順便帶進來的前後文（縮排、註解）→ 把 old_code 縮短就能修好
  * 上游真的改了要修改的那一行                          → 規則本身需要重寫

這裡用「錨點先行」找出最相似的區塊再輸出 unified diff，讓記錄直接回答是哪一種。

效能：逐一滑窗比對是 O(檔案行數 × 片段行數)，.dsc 動輒數千行會明顯卡住。
改成先用片段中最有辨識度的一行找出少數候選位置，只比對那幾個位置附近。
"""

import difflib

#: 相似度低於此值就不輸出 diff（寧可說「找不到近似區塊」也不要亂指）
MIN_RATIO = 0.5

#: 錨點命中太多次時只看前幾個，避免在大量重複內容的檔案裡空轉
MAX_CANDIDATES = 12

#: 最多嘗試幾個錨點。最有辨識度的那行可能正好就是被改掉的，需要能退而求其次
MAX_ANCHORS = 4

#: 錨點附近容許的行位移（上游在片段內插入或刪除幾行仍找得到）
ALIGN_SLACK = 3

#: 視窗長度的伸縮範圍。上游在片段中插入／刪除幾行時，等長的視窗會錯位，
#: diff 就會顯示成不相干的增刪；多試幾種長度才能對齊出真正被改的那幾行。
LENGTH_SLACK = 3

#: 輸出的 diff 行數上限
MAX_DIFF_LINES = 24


def _anchor_candidates(old_lines, limit=MAX_ANCHORS):
    """回傳依辨識度排序的錨點候選 [(內容, 在片段中的索引), ...]。

    跳過空行、註解行與純符號行——那些在檔案裡到處都是，當錨點會產生大量候選。
    取多個而不是只取一個：最有辨識度的那行有可能正好就是被上游改掉的那行，
    這時要能退而求其次用別的行定位。
    """
    scored = []
    for index, line in enumerate(old_lines):
        text = line.strip()
        if len(text) < 4 or text.startswith(("//", "#", "/*", "*", "*/")):
            continue
        score = len(text) + sum(1 for ch in text if ch.isalnum())
        scored.append((score, index, text))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [(text, index) for _, index, text in scored[:limit]]


def _stable_prefix(text):
    """取一行中比較不會變動的前半段：切在第一個 = | : 之前。

        'DEFINE PROJECT_DEBUG_LEVEL = 0x80080046  # ...' -> 'DEFINE PROJECT_DEBUG_LEVEL'

    各專案的設定檔常常只有等號右邊的值不同，整行比對會完全找不到，
    用前半段才定位得到對應的那一行。
    """
    cuts = [text.find(sep) for sep in ("=", "|", ":")]
    cuts = [pos for pos in cuts if pos > 3]
    if not cuts:
        return ""
    prefix = text[:min(cuts)].strip()
    return prefix if len(prefix) >= 4 else ""


def _line_hits(file_lines, needle):
    """先找整行相同，找不到再放寬成子字串。"""
    hits = [i for i, line in enumerate(file_lines) if line.strip() == needle]
    if hits:
        return hits
    return [i for i, line in enumerate(file_lines) if needle in line]


def locate(file_lines, old_lines):
    """在檔案中找出與 old_lines 最相似的區塊，回傳 (起始索引, 視窗長度, 相似度) 或 None。"""
    if not old_lines or not file_lines:
        return None

    span = len(old_lines)
    lengths = [n for n in range(span - LENGTH_SLACK, span + LENGTH_SLACK + 1) if n >= 1]

    for anchor, anchor_index in _anchor_candidates(old_lines):
        candidates = _line_hits(file_lines, anchor)
        if not candidates:
            # 整行找不到時，改用不含專案專屬數值的前半段再找一次
            prefix = _stable_prefix(anchor)
            if prefix:
                candidates = _line_hits(file_lines, prefix)
        if not candidates:
            continue

        best = None
        for pos in candidates[:MAX_CANDIDATES]:
            # 錨點在片段中的位置已知，直接對齊；再容許前後幾行的位移
            aligned = pos - anchor_index
            for start in range(aligned - ALIGN_SLACK, aligned + ALIGN_SLACK + 1):
                if start < 0 or start >= len(file_lines):
                    continue
                for length in lengths:
                    window = file_lines[start:start + length]
                    if not window:
                        continue
                    matcher = difflib.SequenceMatcher(None, old_lines, window,
                                                      autojunk=False)
                    # 兩層便宜的上界先剪枝，真正的 ratio() 才是貴的那個
                    if (matcher.real_quick_ratio() < MIN_RATIO
                            or matcher.quick_ratio() < MIN_RATIO):
                        continue
                    ratio = matcher.ratio()
                    # 同分時取長度最接近原片段的，再取位置最前的，讓輸出穩定
                    key = (ratio, -abs(length - span), -start)
                    if best is None or key > best[0]:
                        best = (key, start, length, ratio)

        if best is not None and best[3] >= MIN_RATIO:
            return best[1], best[2], best[3]

    return None


def _verdict(old_lines, window):
    """判斷差異的性質，讓使用者不必自己讀 diff 就知道該怎麼修。"""
    if len(old_lines) == len(window):
        if all(a.strip() == b.strip() for a, b in zip(old_lines, window)):
            return "差異只在空白／縮排"
        if all(" ".join(a.split()) == " ".join(b.split()) for a, b in zip(old_lines, window)):
            return "差異只在行內空白"
    return "內容有實質差異"


def explain(content, old_code):
    """回傳一段可直接寫進記錄的說明文字。content 與 old_code 都要先正規化過換行。"""
    old_lines = old_code.strip("\n").split("\n")
    file_lines = content.split("\n")

    found = locate(file_lines, old_lines)
    if found is None:
        return ("檔案中找不到近似區塊——可能是上游大幅改寫、"
                "此修改已用其他方式存在，或該片段本來就不屬於這個檔案。")

    start, length, ratio = found
    window = file_lines[start:start + length]
    diff = list(difflib.unified_diff(
        old_lines, window,
        fromfile="profile 的 old_code", tofile=f"實際檔案第 {start + 1} 行起",
        lineterm="", n=1))
    if len(diff) > MAX_DIFF_LINES:
        omitted = len(diff) - MAX_DIFF_LINES
        diff = diff[:MAX_DIFF_LINES] + [f"…（另有 {omitted} 行差異未列出）"]

    head = (f"最相似區塊在第 {start + 1} 行"
            f"（相似度 {ratio:.0%}，{_verdict(old_lines, window)}）")
    return "\n".join([head] + diff)
