"""重新錨定：把解完衝突的結果寫回 profile，讓同一個衝突不會再出現一次。

沒有這一步，解衝突只修好了「這一次」——換一棵樹、或上游再前進，同樣的衝突要再解一遍。

原理很單純，三份資料在解衝突時本來就都在手上：

    新的 base      = 衝突當下專案裡的內容（.current）
    新的「改後」   = 使用者解出來的內容（.merged）
    新的規則       = 兩者的差異，往外擴前後文直到唯一（沿用產生器的邏輯）

危險之處在於這是**唯一會改寫既有 profile 的功能**，所以流程刻意設計成：
    1. 只做文字層級的定點置換，不用 YAML dump——那會毀掉檔案裡所有註解與排版
    2. 改完先讀回來，確認「目標規則變成預期的樣子」且「其他規則一個字都沒動」
    3. 驗證不過就整個放棄，原檔不動
    4. 真的要寫入前先備份
"""

import json
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .patcher import normalize_newlines, read_text
from .threeway import added_lines

try:
    import yaml
except Exception:       # pragma: no cover
    yaml = None

SECTION_OF = {"mod": "modifications", "pcd": "platform_pcd_modifications"}

#: 區塊純量的起始標記（|、|2、|-、|2-、|+ …）
_BLOCK_RE = re.compile(r"^(\s*)(old_code|new_code)\s*:\s*(\|[0-9]*[-+]?)\s*$")
_ITEM_RE = re.compile(r"^(\s*)-\s")
_TOPKEY_RE = re.compile(r"^[^\s#-]")


#: 錨點的 base 放在 base/ 底下這個子目錄，依時間戳分層，不會跟主 base 混在一起
ANCHOR_DIR_NAME = "_anchors"


@dataclass
class ReanchorPlan:
    """重新錨定 = 為規則新增一組錨點。原本的 old_code / new_code / base 一律保留，
    還沒跟上上游的那些樹才不會因為這次改寫而套不上。"""

    rule_id: str = ""
    label: str = ""
    section: str = ""
    index: int = -1
    old_code: str = ""          # 新錨點的 old_code
    new_code: str = ""          # 新錨點的 new_code
    base_text: str = ""         # 新錨點的 base 內容
    profile_path: str = ""
    base_file: str = ""         # 新錨點的 base 要存到 base/ 底下的哪裡（相對路徑）
    covers: list = field(default_factory=list)
    note: str = ""
    anchor: dict = field(default_factory=dict)   # 要寫進 YAML 的錨點內容
    yaml_text: str = ""         # 改寫後的完整 YAML
    warnings: list = field(default_factory=list)
    error: str = ""

    @property
    def ok(self):
        return not self.error and bool(self.yaml_text)


# ---------------------------------------------------------------- YAML 定點置換

def _section_range(lines, section):
    """找出某個區塊在行清單中的範圍 (start, end)；找不到回 None。"""
    start = None
    for index, line in enumerate(lines):
        if line.strip() == f"{section}:" or line.startswith(f"{section}:"):
            start = index + 1
            break
    if start is None:
        return None
    for index in range(start, len(lines)):
        line = lines[index]
        if line.strip() and _TOPKEY_RE.match(line):
            return start, index
    return start, len(lines)


def _item_ranges(lines, start, end):
    """把區塊內的清單項目切成 [(start, end), ...]。"""
    indent = None
    starts = []
    for index in range(start, end):
        match = _ITEM_RE.match(lines[index])
        if not match:
            continue
        if indent is None:
            indent = len(match.group(1))
        if len(match.group(1)) == indent:
            starts.append(index)
    ranges = []
    for position, item_start in enumerate(starts):
        item_end = starts[position + 1] if position + 1 < len(starts) else end
        ranges.append((item_start, item_end))
    return ranges


def _block_range(lines, item_start, item_end, key):
    """找出某個 key 的區塊純量範圍 (key 行, 內容結束行, key 縮排, 樣式)。"""
    for index in range(item_start, item_end):
        match = _BLOCK_RE.match(lines[index])
        if not match or match.group(2) != key:
            continue
        key_indent = len(match.group(1))
        body_end = index + 1
        while body_end < item_end:
            line = lines[body_end]
            if line.strip() and (len(line) - len(line.lstrip())) <= key_indent:
                break
            body_end += 1
        return index, body_end, key_indent, match.group(3)
    return None


def _emit_block(text, key, key_indent, style):
    """依原本的縮排與樣式重新產生一個區塊純量。

    沿用產生器的作法：一律用 |2 加上正確的 chomping，內容縮排為 key 縮排 + 2。
    """
    if not text.endswith("\n"):
        chomp, body = "-", text
    else:
        chomp = "+" if text.endswith("\n\n") else ""
        body = text[:-1]
    pad = " " * (key_indent + 2)
    out = [f"{' ' * key_indent}{key}: |2{chomp}"]
    for line in body.split("\n"):
        out.append(pad + line if line else "")
    return out


def set_field(yaml_text, updates):
    """為指定的規則設定一個純量欄位（沒有就新增，有就就地更新）。

    updates 形式為 [(section, index, key, value), ...]。同樣只做定點置換，
    不動檔案裡的任何註解與排版。回傳 (新的 YAML 文字, 錯誤訊息)。
    """
    lines = normalize_newlines(yaml_text).split("\n")

    # 由後往前處理，避免前面的插入影響後面的行號
    prepared = []
    for section, index, key, value in updates:
        span = _section_range(lines, section)
        if span is None:
            return "", f"找不到區塊 {section}"
        items = _item_ranges(lines, *span)
        if index >= len(items):
            return "", f"{section} 只有 {len(items)} 條規則，找不到第 {index + 1} 條"
        prepared.append((items[index], key, value))

    for (item_start, item_end), key, value in sorted(prepared, reverse=True):
        key_re = re.compile(rf"^(\s*){re.escape(key)}\s*:")
        replaced = False
        for line_no in range(item_start, item_end):
            match = key_re.match(lines[line_no])
            if match:
                lines[line_no] = f"{match.group(1)}{key}: {value}"
                replaced = True
                break
        if replaced:
            continue
        # 沒有這個欄位就插在項目第一行之後，縮排沿用下一行
        indent = " " * (len(lines[item_start]) - len(lines[item_start].lstrip()) + 2)
        if item_start + 1 < len(lines):
            following = lines[item_start + 1]
            if following.strip():
                indent = " " * (len(following) - len(following.lstrip()))
        lines.insert(item_start + 1, f"{indent}{key}: {value}")

    return "\n".join(lines), ""


_KEY_RE = re.compile(r"^(\s*)([A-Za-z_][\w-]*)\s*:")


def _scalar(value):
    """單行純量一律用雙引號寫出，路徑、冒號、中文都不會被 YAML 誤解。"""
    return json.dumps(str(value), ensure_ascii=False)


def append_anchor(yaml_text, section, index, anchor):
    """在第 index 條規則尾端加一組錨點，其餘一字不動。

    anchor 是 dict：note / base_file / covers / old_code / new_code。
    規則沒有 anchors 就新建整段；已有就接在清單最後。回傳 (新的 YAML, 錯誤訊息)。

    兩個細節都跟 YAML 的 keep chomping（|2+）有關——產生器寫出的 new_code 常以
    空行結尾，這種區塊的值包含它後面所有的空行：
      * 新內容一律插在規則範圍的最尾端，也就是那些空行之後；插在空行之前會把
        原本 new_code 的尾端換行切掉，讀回驗證就會說「new_code 被動到了」。
      * 錨點內把 old_code / new_code 放前面、note / base_file / covers 放後面，
        讓單行純量把區塊純量的尾端「關起來」，之後不管接幾個空行都不會被吃進值裡。
    """
    lines = normalize_newlines(yaml_text).split("\n")

    span = _section_range(lines, section)
    if span is None:
        return "", f"找不到區塊 {section}"
    items = _item_ranges(lines, *span)
    if index >= len(items):
        return "", f"{section} 只有 {len(items)} 條規則，找不到第 {index + 1} 條"
    item_start, item_end = items[index]

    found = _block_range(lines, item_start, item_end, "old_code")
    if found is None:
        return "", f"第 {index + 1} 條規則沒有區塊純量形式的 old_code"
    key_indent = found[2]

    anchors_line = None
    for line_no in range(item_start, item_end):
        match = _KEY_RE.match(lines[line_no])
        if match and match.group(2) == "anchors" and len(match.group(1)) == key_indent:
            anchors_line = line_no
            break

    block = []
    if anchors_line is None:
        # 規則範圍的尾端可能掛著給下一條規則看的分隔註解（縮排不深於 key 的 # 行），
        # 新內容要插在那些註解之前，否則看起來像黏在下一條上。註解前的空行屬於
        # 上一個 |2+ 區塊純量的值，留在原位不動。
        insert_at = item_end
        while insert_at > item_start + 1:
            line = lines[insert_at - 1]
            stripped = line.strip()
            if stripped.startswith("#") and (len(line) - len(line.lstrip())) <= key_indent:
                insert_at -= 1
                continue
            break
        block.append(f"{' ' * key_indent}anchors:")
    else:
        # anchors 清單到哪裡結束：下一個縮排不深於 key 的非空行（或規則結尾）
        insert_at = anchors_line + 1
        while insert_at < item_end:
            line = lines[insert_at]
            if line.strip() and (len(line) - len(line.lstrip())) <= key_indent:
                break
            insert_at += 1

    item_pad = " " * (key_indent + 2)
    key_pad = " " * (key_indent + 4)
    old_block = _emit_block(anchor.get("old_code", ""), "old_code", key_indent + 4, "|2")
    old_block[0] = f"{item_pad}- {old_block[0].lstrip()}"      # 第一個 key 跟 - 同一行
    block += old_block
    block += _emit_block(anchor.get("new_code", ""), "new_code", key_indent + 4, "|2")
    block.append(f"{key_pad}note: {_scalar(anchor.get('note', ''))}")
    if anchor.get("base_file"):
        block.append(f"{key_pad}base_file: {_scalar(anchor['base_file'])}")
    if anchor.get("covers"):
        block.append(f"{key_pad}covers:")
        for path in anchor["covers"]:
            block.append(f"{key_pad}  - {_scalar(path)}")
    # 與下一條規則之間留一個空行，保持原本的排版節奏；最後一個 key 是單行純量，
    # 這個空行不會被算進任何值
    if insert_at < len(lines) and lines[insert_at].strip():
        block.append("")

    lines[insert_at:insert_at] = block
    return "\n".join(lines), ""


def rewrite(yaml_text, section, index, old_code, new_code):
    """把第 index 條規則的 old_code / new_code 換掉，其餘一字不動。

    回傳 (新的 YAML 文字, 錯誤訊息)。
    """
    lines = normalize_newlines(yaml_text).split("\n")

    span = _section_range(lines, section)
    if span is None:
        return "", f"找不到區塊 {section}"
    items = _item_ranges(lines, *span)
    if index >= len(items):
        return "", f"{section} 只有 {len(items)} 條規則，找不到第 {index + 1} 條"

    item_start, item_end = items[index]
    # 由後往前置換，避免前面的置換影響後面的行號
    replacements = []
    for key, value in (("old_code", old_code), ("new_code", new_code)):
        found = _block_range(lines, item_start, item_end, key)
        if found is None:
            return "", f"第 {index + 1} 條規則沒有區塊純量形式的 {key}"
        key_line, body_end, key_indent, style = found
        replacements.append((key_line, body_end, _emit_block(value, key, key_indent, style)))

    for key_line, body_end, block in sorted(replacements, reverse=True):
        lines[key_line:body_end] = block
    return "\n".join(lines), ""


# ---------------------------------------------------------------- 規劃

def _relative_target(target, project_root):
    """目標檔相對於專案根目錄的路徑（正斜線）；算不出來就退回檔名。"""
    try:
        if project_root:
            return Path(target).resolve().relative_to(
                Path(project_root).resolve()).as_posix()
    except (ValueError, OSError):
        pass
    return Path(target).name


def _whitespace_only(org_lines, mod_lines, span):
    """這個 hunk 是否只有行尾空白不同（編輯器存檔時常順手砍掉尾端空格）。"""
    i1, i2, j1, j2 = span
    return ([l.rstrip() for l in org_lines[i1:i2]]
            == [l.rstrip() for l in mod_lines[j1:j2]])


def _hunk_has(mod_lines, span, wanted):
    """這個 hunk 的新內容是否包含 wanted 的每一行（比對時忽略行尾空白）。"""
    _, _, j1, j2 = span
    present = {l.rstrip() for l in mod_lines[j1:j2]}
    return all(w in present for w in wanted)


def plan(profile, record, logger, project_root="", rule_id=None):
    """依一筆已解決的衝突，規劃要新增的錨點與它的 base。不寫入任何檔案。

    project_root 是這次執行的專案根目錄，用來算目標檔的相對路徑（錨點的 covers
    與 base 存放位置都用它）。

    同一個檔案有多條規則衝突時，衝突紀錄只有一筆、rule_id 是 "mod:7,mod:8" 這種
    複合形式；呼叫端要拆開、每條規則各呼叫一次並傳入 rule_id。這裡會從解決後的
    內容裡挑出「含本規則新增行」的那一段當錨點，其他段落（別條規則的、或使用者
    順手改的）不納入。
    """
    from .profilegen import GenOptions, _hunk_spans, _make_snippet

    rule_id = (rule_id or record.rule_id or "").strip()
    result = ReanchorPlan(rule_id=rule_id, label=record.label,
                          profile_path=profile.source_path)

    if yaml is None:
        result.error = "未安裝 PyYAML，無法重新錨定"
        return result
    if "," in rule_id:
        result.error = "這筆衝突涵蓋多條規則，請逐條規劃（呼叫端要拆開 rule_id）"
        return result

    kind = rule_id.split(":")[0] if ":" in rule_id else ""
    if kind not in SECTION_OF:
        result.error = f"這條規則（{rule_id}）不支援重新錨定"
        return result
    result.section = SECTION_OF[kind]
    try:
        result.index = int(rule_id.split(":")[1])
    except (IndexError, ValueError):
        result.error = f"無法解析規則編號：{rule_id}"
        return result

    rule = next((r for r in profile.all_rules if r.rule_id == rule_id), None)
    if rule is not None and rule.label:
        result.label = rule.label

    try:
        current = normalize_newlines(read_text(record.current)[0])
        merged = normalize_newlines(read_text(record.merged)[0])
    except Exception as exc:
        result.error = f"讀取衝突產物失敗：{exc}"
        return result

    if current == merged:
        result.error = "解決後的內容與衝突當下相同，沒有可錨定的改動"
        return result

    options = GenOptions()
    org_lines = current.splitlines(keepends=True)
    mod_lines = merged.splitlines(keepends=True)
    spans = _hunk_spans(org_lines, mod_lines, options.context_lines)

    # 純空白的差異不是改動：合併工具或編輯器存檔時常把行尾空格砍掉，
    # 這種假差異會讓「一條規則只能有一段改動」的檢查誤判成分散的改動。
    kept = [s for s in spans if not _whitespace_only(org_lines, mod_lines, s)]
    if len(kept) != len(spans):
        result.warnings.append(f"忽略 {len(spans) - len(kept)} 處只有行尾空白差異的改動")
    spans = kept

    if not spans:
        result.error = "找不到差異（扣掉純空白差異後），無法重新錨定"
        return result
    if len(spans) > 1:
        # 多段改動：挑出含本規則新增行的那一段。其餘是別條規則的（同檔多規則共用
        # 一份解決結果）或使用者順手改的，都不屬於這條規則的錨點。
        wanted = ([l.rstrip() for l in added_lines(normalize_newlines(rule.old_code),
                                                    normalize_newlines(rule.new_code))]
                  if rule is not None else [])
        mine = [s for s in spans if wanted and _hunk_has(mod_lines, s, wanted)]
        if len(mine) == 1:
            result.warnings.append(
                f"解決後的內容另有 {len(spans) - 1} 處改動不屬於本規則，未納入錨點")
            spans = mine
        elif not mine:
            result.error = (f"解決後的內容有 {len(spans)} 處改動，但找不到含本規則新增行的那一段，"
                            "無法判斷哪一段屬於本規則，請手動調整 profile")
            return result
        else:
            result.error = (f"解決後的內容有 {len(mine)} 處都含本規則新增的行，"
                            "一條規則無法涵蓋，請手動調整 profile")
            return result

    snippet = _make_snippet(org_lines, mod_lines, spans[0], current, options)
    if snippet is None:
        result.error = (f"前後文擴到 {options.max_context_lines} 行仍無法讓片段唯一，"
                        "請手動調整 profile")
        return result

    result.old_code, result.new_code = snippet
    result.base_text = current

    # 已經有一組錨點的 old_code 跟這個一樣 → 這棵樹的樣子已經被記住了，不必再加
    if rule is not None:
        for variant in rule.variants():
            if normalize_newlines(variant.old_code) == result.old_code:
                result.error = "已有相同的錨點，不需要再新增"
                return result

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    rel = _relative_target(record.target, project_root)
    result.covers = [rel]
    tree = Path(str(project_root).rstrip("\\/")).name if project_root else ""
    result.note = f"{stamp[:8]} 於 {tree or '某棵樹'} 解決衝突後新增"
    if profile.package_dir:
        result.base_file = f"{ANCHOR_DIR_NAME}/{stamp}/{rel}"
    else:
        result.warnings.append("單檔型 profile 沒有 base 目錄，這組錨點不會帶 base，只能精確比對")
    result.anchor = {"note": result.note, "base_file": result.base_file,
                     "covers": result.covers,
                     "old_code": result.old_code, "new_code": result.new_code}

    # ---- 產生新的 YAML 並讀回驗證 ----
    try:
        original_yaml = Path(profile.source_path).read_text(encoding="utf-8")
    except Exception as exc:
        result.error = f"讀取 profile 失敗：{exc}"
        return result

    new_yaml, error = append_anchor(original_yaml, result.section, result.index, result.anchor)
    if error:
        result.error = error
        return result

    error = _verify(original_yaml, new_yaml, result)
    if error:
        result.error = error
        return result

    result.yaml_text = new_yaml
    logger.info(f"重新錨定規劃完成：{result.label}"
                f"（新增第 {len(rule.anchors) + 2 if rule else 2} 組錨點，"
                f"old_code {len(result.old_code.splitlines())} 行）")
    for warning in result.warnings:
        logger.info(f"  {result.label}：{warning}")
    return result


def _verify(original_yaml, new_yaml, result):
    """讀回改寫後的 YAML：目標規則只能剛好多出一組預期的錨點，其他一字不能動。"""
    try:
        before = yaml.safe_load(original_yaml) or {}
        after = yaml.safe_load(new_yaml) or {}
    except Exception as exc:
        return f"改寫後的 YAML 無法解析：{exc}"

    for section in ("modifications", "platform_pcd_modifications"):
        old_items = before.get(section) or []
        new_items = after.get(section) or []
        if len(old_items) != len(new_items):
            return f"{section} 的規則數改變了（{len(old_items)} -> {len(new_items)}）"
        for index, (old_item, new_item) in enumerate(zip(old_items, new_items)):
            target = section == result.section and index == result.index
            if target:
                before_anchors = old_item.get("anchors") or []
                after_anchors = new_item.get("anchors") or []
                if len(after_anchors) != len(before_anchors) + 1:
                    return "目標規則的錨點數不是剛好多一組"
                if after_anchors[:-1] != before_anchors:
                    return "目標規則原有的錨點被動到了"
                added = after_anchors[-1] if isinstance(after_anchors[-1], dict) else {}
                if normalize_newlines(added.get("old_code", "")) != result.old_code:
                    return "新錨點的 old_code 與預期不符"
                if normalize_newlines(added.get("new_code", "")) != result.new_code:
                    return "新錨點的 new_code 與預期不符"
                if str(added.get("base_file", "") or "") != result.base_file:
                    return "新錨點的 base_file 與預期不符"
                # 除了 anchors，其餘欄位（含原本的 old_code / new_code）不該變動
                keys = set(old_item) | set(new_item)
                for key in keys - {"anchors"}:
                    if old_item.get(key) != new_item.get(key):
                        return f"目標規則的 {key} 被動到了"
            elif old_item != new_item:
                return f"{section} 第 {index + 1} 條規則被動到了（不該改到它）"

    # profile 區塊與 new_files 也不能動
    for key in ("profile", "new_files"):
        if before.get(key) != after.get(key):
            return f"{key} 區塊被動到了"
    return ""


# ---------------------------------------------------------------- 寫入

def apply_fields(profile, updates, logger):
    """把一組純量欄位更新寫進 profile.yaml。

    updates 形式為 [(section, index, key, value), ...]。與規則改寫走同一套安全流程：
    改完先讀回驗證，確認只有指定的欄位變動，驗證不過就整個放棄。
    """
    if yaml is None:
        return False, "未安裝 PyYAML，無法寫入"
    if not updates:
        return False, "沒有要寫入的項目"

    path = Path(profile.source_path)
    try:
        original = path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"讀取 profile 失敗：{exc}"

    updated, error = set_field(original, updates)
    if error:
        return False, error

    try:
        before = yaml.safe_load(original) or {}
        after = yaml.safe_load(updated) or {}
    except Exception as exc:
        return False, f"改寫後的 YAML 無法解析：{exc}"

    wanted = {(section, index): (key, value) for section, index, key, value in updates}
    for section in ("modifications", "platform_pcd_modifications"):
        old_items = before.get(section) or []
        new_items = after.get(section) or []
        if len(old_items) != len(new_items):
            return False, f"{section} 的規則數改變了"
        for index, (old_item, new_item) in enumerate(zip(old_items, new_items)):
            target = wanted.get((section, index))
            if target is None:
                if old_item != new_item:
                    return False, f"{section} 第 {index + 1} 條規則被動到了（不該改到它）"
                continue
            key, value = target
            if str(new_item.get(key)) != str(value):
                return False, f"{section} 第 {index + 1} 條的 {key} 未正確寫入"
            for other in (set(old_item) | set(new_item)) - {key}:
                if old_item.get(other) != new_item.get(other):
                    return False, f"{section} 第 {index + 1} 條的 {other} 被動到了"

    for key in ("profile", "new_files"):
        if before.get(key) != after.get(key):
            return False, f"{key} 區塊被動到了"

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    try:
        shutil.copy2(path, f"{path}.bak.{stamp}")
    except Exception as exc:
        return False, f"備份失敗，未寫入：{exc}"
    try:
        path.write_text(updated, encoding="utf-8", newline="\n")
    except Exception as exc:
        return False, f"寫入失敗：{exc}"

    logger.ok(f"已更新 {len(updates)} 條規則的欄位：{path.name}")
    return True, f"已寫入 {len(updates)} 條"


def apply(profile, record, plan_result, logger):
    """把規劃寫入：備份 profile.yaml -> 寫入新 YAML -> 存下新錨點的 base。

    刻意不動主 base 與 manifest：原本那組錨點還在服務還沒跟上上游的樹。

    寫入前以檔案「現在」的內容重新插入一次，而不是直接寫 plan 時算好的 yaml_text：
    一次解決多個衝突時，所有 plan 都是對同一份原始 YAML 算的，若各自把自己那份
    寫出去，後寫的會把先寫的錨點蓋掉。
    """
    from .basesnap import BASE_DIR_NAME

    if not plan_result.ok:
        return False, plan_result.error or "沒有可寫入的內容"

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    profile_path = Path(profile.source_path)

    try:
        original = profile_path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"讀取 profile 失敗，未寫入：{exc}"
    new_yaml, error = append_anchor(original, plan_result.section, plan_result.index,
                                    plan_result.anchor)
    if not error:
        error = _verify(original, new_yaml, plan_result)
    if error:
        return False, f"寫入前重新驗證失敗，未寫入：{error}"

    try:
        shutil.copy2(profile_path, f"{profile_path}.bak.{stamp}")
    except Exception as exc:
        return False, f"備份 profile 失敗，未寫入：{exc}"

    try:
        profile_path.write_text(new_yaml, encoding="utf-8", newline="\n")
    except Exception as exc:
        return False, f"寫入 profile 失敗：{exc}"
    label = plan_result.label or record.label
    logger.ok(f"已新增錨點：{profile_path.name}　({label})")

    if not plan_result.base_file:
        return True, "已新增錨點（此 profile 沒有 base 目錄，這組錨點只做精確比對）"

    base_root = Path(profile.package_dir) / BASE_DIR_NAME
    target = base_root / plan_result.base_file
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(plan_result.base_text, encoding="utf-8", newline="\n")
    except Exception as exc:
        return True, f"錨點已新增，但它的 base 寫出失敗（這組錨點只能精確比對）：{exc}"

    logger.ok(f"已保存錨點的 base：{plan_result.base_file}")
    return True, "已新增錨點並保存對應的 base"
