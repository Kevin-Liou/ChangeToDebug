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

import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .patcher import normalize_newlines, read_text

try:
    import yaml
except Exception:       # pragma: no cover
    yaml = None

SECTION_OF = {"mod": "modifications", "pcd": "platform_pcd_modifications"}

#: 區塊純量的起始標記（|、|2、|-、|2-、|+ …）
_BLOCK_RE = re.compile(r"^(\s*)(old_code|new_code)\s*:\s*(\|[0-9]*[-+]?)\s*$")
_ITEM_RE = re.compile(r"^(\s*)-\s")
_TOPKEY_RE = re.compile(r"^[^\s#-]")


@dataclass
class ReanchorPlan:
    rule_id: str = ""
    label: str = ""
    section: str = ""
    index: int = -1
    old_code: str = ""          # 新的 old_code
    new_code: str = ""          # 新的 new_code
    base_text: str = ""         # 新的 base 內容
    profile_path: str = ""
    base_file: str = ""         # base/ 底下要覆寫的檔案
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

def plan(profile, record, logger):
    """依一筆已解決的衝突，算出重新錨定後的規則與 base。不寫入任何檔案。"""
    from .profilegen import GenOptions, _hunk_spans, _make_snippet

    result = ReanchorPlan(rule_id=record.rule_id, label=record.label,
                          profile_path=profile.source_path)

    if yaml is None:
        result.error = "未安裝 PyYAML，無法重新錨定"
        return result

    kind = record.rule_id.split(":")[0] if ":" in record.rule_id else ""
    if kind not in SECTION_OF:
        result.error = f"這條規則（{record.rule_id}）不支援重新錨定"
        return result
    result.section = SECTION_OF[kind]
    try:
        result.index = int(record.rule_id.split(":")[1])
    except (IndexError, ValueError):
        result.error = f"無法解析規則編號：{record.rule_id}"
        return result

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

    if not spans:
        result.error = "找不到差異，無法重新錨定"
        return result
    if len(spans) > 1:
        result.error = (f"解決後的內容有 {len(spans)} 處分散的改動，"
                        "一條規則無法涵蓋，請手動調整 profile")
        return result

    snippet = _make_snippet(org_lines, mod_lines, spans[0], current, options)
    if snippet is None:
        result.error = (f"前後文擴到 {options.max_context_lines} 行仍無法讓片段唯一，"
                        "請手動調整 profile")
        return result

    result.old_code, result.new_code = snippet
    result.base_text = current

    # ---- 產生新的 YAML 並讀回驗證 ----
    try:
        original_yaml = Path(profile.source_path).read_text(encoding="utf-8")
    except Exception as exc:
        result.error = f"讀取 profile 失敗：{exc}"
        return result

    new_yaml, error = rewrite(original_yaml, result.section, result.index,
                              result.old_code, result.new_code)
    if error:
        result.error = error
        return result

    error = _verify(original_yaml, new_yaml, result)
    if error:
        result.error = error
        return result

    result.yaml_text = new_yaml
    logger.info(f"重新錨定規劃完成：{record.label}"
                f"（新的 old_code {len(result.old_code.splitlines())} 行）")
    return result


def _verify(original_yaml, new_yaml, result):
    """讀回改寫後的 YAML：目標規則須變成預期的樣子，其他規則一字不能動。"""
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
                if normalize_newlines(new_item.get("old_code", "")) != result.old_code:
                    return "目標規則的 old_code 與預期不符"
                if normalize_newlines(new_item.get("new_code", "")) != result.new_code:
                    return "目標規則的 new_code 與預期不符"
                # 除了兩個程式碼欄位，其餘欄位不該變動
                keys = set(old_item) | set(new_item)
                for key in keys - {"old_code", "new_code"}:
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
    """把規劃寫入：備份 -> 覆寫 profile.yaml -> 更新 base 快照與 manifest。"""
    from .basesnap import MANIFEST_NAME, dump_manifest, load_snapshot, sha256_of

    if not plan_result.ok:
        return False, plan_result.error or "沒有可寫入的內容"

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    profile_path = Path(profile.source_path)

    try:
        shutil.copy2(profile_path, f"{profile_path}.bak.{stamp}")
    except Exception as exc:
        return False, f"備份 profile 失敗，未寫入：{exc}"

    try:
        profile_path.write_text(plan_result.yaml_text, encoding="utf-8", newline="\n")
    except Exception as exc:
        return False, f"寫入 profile 失敗：{exc}"
    logger.ok(f"已更新規則：{profile_path.name}　({record.label})")

    # ---- 更新 base 快照 ----
    snapshot = profile.base_snapshot
    if snapshot is None or not snapshot.available:
        return True, "規則已更新（此 profile 沒有 base 快照，略過 base 更新）"

    entry = snapshot.entries.get(record.rule_id)
    if not entry or not entry.get("base_file"):
        return True, "規則已更新（這條規則沒有 base，略過 base 更新）"

    base_path = Path(snapshot.root) / str(entry["base_file"]).replace("\\", "/")
    try:
        base_path.parent.mkdir(parents=True, exist_ok=True)
        if base_path.is_file():
            shutil.copy2(base_path, f"{base_path}.bak.{stamp}")
        base_path.write_text(plan_result.base_text, encoding="utf-8", newline="\n")
        entry["sha256"] = sha256_of(base_path)
        entry["source"] = "reanchored"
    except Exception as exc:
        return True, f"規則已更新，但 base 快照更新失敗：{exc}"

    # ---- 寫回 manifest ----
    try:
        package = Path(profile.package_dir)
        entries = [snapshot.entries[key] for key in snapshot.entries]
        (package / MANIFEST_NAME).write_text(
            dump_manifest(entries, snapshot.base_commit), encoding="utf-8", newline="\n")
    except Exception as exc:
        return True, f"規則與 base 已更新，但 manifest 寫回失敗：{exc}"

    logger.ok(f"已更新 base 快照：{base_path.name}")
    return True, "規則與 base 快照都已更新"
