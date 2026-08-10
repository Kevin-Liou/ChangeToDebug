"""從 code change 套件的 ORG / MOD 兩個資料夾自動產生 profile YAML。

做法：
  1. 只在 MOD 出現的檔案     -> new_files 項目
  2. 兩邊都有的檔案          -> 用 difflib 取出差異片段，往外擴前後文直到
                               old_code 在該檔中「剛好出現一次」為止
  3. MultiProject/<專案>/ 底下、且各專案改法完全相同的片段
                             -> 合併成一條 file_name 規則（檔名不同時自動推出萬用字元）
  4. 產生完立刻把 YAML 讀回來，逐條比對字串是否與原始片段一致（防止縮排/跳脫出錯）

產生的規則 option_debug_flag 一律是 false（必要）；哪些要改成選配由人決定。
"""

import difflib
import os
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except Exception:       # pragma: no cover
    yaml = None

from .patcher import normalize_newlines, read_text

#: 依副檔名判斷註解符號（合併時「忽略註解差異」用）
COMMENT_MARKS = {
    ".c": ("//",), ".h": ("//",), ".asl": ("//",), ".aslc": ("//",),
    ".dsc": ("#",), ".dec": ("#",), ".inf": ("#",), ".fdf": ("#",),
    ".py": ("#",), ".yaml": ("#",), ".yml": ("#",),
}

SKIP_NAMES = {".git", "__pycache__", ".vs", ".vscode", "Build", "build"}

#: 產生器不處理的檔案（純文件、版本控制殘留）
IGNORE_SUFFIXES = ()


@dataclass
class GenOptions:
    org_dir: str = ""
    mod_dir: str = ""
    key: str = ""
    display_name: str = ""
    description: str = ""
    priority: int = 100
    detect_dirs: list = field(default_factory=list)
    pcd_scan_roots: list = field(default_factory=lambda: ["HpPlatformPkg/MultiProject"])
    multi_project_dir: str = "MultiProject"
    context_lines: int = 3
    max_context_lines: int = 15
    merge_projects: bool = True
    merge_ignore_comments: bool = False
    new_files_dir: str = ""          # 空 = 用 mod_dir 的絕對路徑
    header_note: str = ""


@dataclass
class GenRule:
    kind: str               # 'sub' | 'pcd' | 'new'
    target: str             # sub_path / file_name / 新增檔案的相對路徑
    label: str
    old_code: str = ""
    new_code: str = ""
    note: str = ""
    org_files: list = field(default_factory=list)   # 這條規則對應的 ORG 相對路徑


@dataclass
class GenResult:
    yaml_text: str = ""
    rules: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def ok(self):
        return not self.errors and bool(self.yaml_text)


# ---------------------------------------------------------------- 小工具

def _walk_rel(root):
    """收集 root 底下所有檔案的相對路徑（統一用 /）。"""
    root = Path(root)
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_NAMES]
        for name in filenames:
            rel = Path(dirpath, name).relative_to(root).as_posix()
            out.append(rel)
    return sorted(out)


def _text(path):
    content, _ = read_text(path)
    return normalize_newlines(content)


def _strip_comments(text, rel):
    marks = COMMENT_MARKS.get(Path(rel).suffix.lower(), ("#",))
    out = []
    for line in text.split("\n"):
        s = line.strip()
        if not s or any(s.startswith(m) for m in marks):
            continue
        out.append(" ".join(s.split()))
    return "\n".join(out)


def _split_project(rel, multi_dir):
    """回傳 (專案名, 專案內相對路徑)；不在 MultiProject 底下則回傳 (None, rel)。"""
    parts = rel.split("/")
    if multi_dir in parts:
        i = parts.index(multi_dir)
        if i + 2 <= len(parts) - 1:
            return parts[i + 1], "/".join(parts[i + 2:])
    return None, rel


def _glob_for(names):
    """由多個檔名推出萬用字元樣式，例如 Z21ManaanPkgConfig.dsc / Z22MekrosPkgConfig.dsc -> Z*PkgConfig.dsc"""
    names = sorted(set(names))
    if len(names) == 1:
        return names[0]
    prefix = os.path.commonprefix(names)
    suffix = os.path.commonprefix([n[::-1] for n in names])[::-1]
    if len(prefix) + len(suffix) >= max(len(n) for n in names):
        # 前後綴重疊，無法安全推導
        return None
    if not prefix and not suffix:
        return None
    return f"{prefix}*{suffix}"


# ---------------------------------------------------------------- 差異切片

def _hunk_spans(org_lines, mod_lines, ctx):
    """把 difflib 的非相等區塊合併成幾個大片段（相隔太近的併在一起）。"""
    matcher = difflib.SequenceMatcher(None, org_lines, mod_lines, autojunk=False)
    ops = [op for op in matcher.get_opcodes() if op[0] != "equal"]
    if not ops:
        return []
    groups = [[ops[0]]]
    for op in ops[1:]:
        if op[1] - groups[-1][-1][2] <= 2 * ctx:
            groups[-1].append(op)
        else:
            groups.append([op])
    return [(g[0][1], g[-1][2], g[0][3], g[-1][4]) for g in groups]


def _make_snippet(org_lines, mod_lines, span, org_text, options):
    """往外擴前後文，直到 old_code 在整份 ORG 中唯一。回傳 (old, new) 或 None。"""
    i1, i2, j1, j2 = span
    for ctx in range(options.context_lines, options.max_context_lines + 1):
        start = max(0, i1 - ctx)
        end = min(len(org_lines), i2 + ctx)
        old = "".join(org_lines[start:end])
        new = ("".join(org_lines[start:i1])
               + "".join(mod_lines[j1:j2])
               + "".join(org_lines[i2:end]))
        if start > 0:                       # 從行首開始比對，避免對到半行
            old, new = "\n" + old, "\n" + new
        if org_text.count(old) == 1:
            return old, new
    return None


# ---------------------------------------------------------------- 主流程

def generate(options, logger):
    result = GenResult()
    if yaml is None:
        result.errors.append("未安裝 PyYAML，無法產生 profile")
        return result

    org_root, mod_root = Path(options.org_dir), Path(options.mod_dir)
    if not org_root.is_dir():
        result.errors.append(f"ORG 資料夾不存在：{org_root}")
    if not mod_root.is_dir():
        result.errors.append(f"MOD 資料夾不存在：{mod_root}")
    if not options.key.strip():
        result.errors.append("請填寫世代代號（例如 FY28）")
    if result.errors:
        return result

    org_files, mod_files = set(_walk_rel(org_root)), set(_walk_rel(mod_root))
    logger.step(f"比對 ORG({len(org_files)} 檔) 與 MOD({len(mod_files)} 檔)")

    # ---- 只有 ORG 有的檔案：工具無法刪檔 ----
    for rel in sorted(org_files - mod_files):
        result.warnings.append(f"只存在於 ORG，工具無法處理刪除：{rel}")

    # ---- 只有 MOD 有的檔案：new_files ----
    new_files = sorted(mod_files - org_files)
    for rel in new_files:
        result.rules.append(GenRule("new", rel, rel))
        logger.info(f"新增檔案：{rel}")

    # ---- 兩邊都有：取差異 ----
    raw = []        # (project, rest, rel, old, new)
    unchanged = 0
    for rel in sorted(org_files & mod_files):
        org_text = _text(org_root / rel)
        mod_text = _text(mod_root / rel)
        if org_text == mod_text:
            unchanged += 1
            continue
        org_lines = org_text.splitlines(keepends=True)
        mod_lines = mod_text.splitlines(keepends=True)
        spans = _hunk_spans(org_lines, mod_lines, options.context_lines)
        for index, span in enumerate(spans):
            snippet = _make_snippet(org_lines, mod_lines, span, org_text, options)
            if snippet is None:
                result.warnings.append(
                    f"無法讓片段唯一（前後文已擴到 {options.max_context_lines} 行）："
                    f"{rel} 第 {span[0] + 1} 行附近，請手動處理")
                continue
            project, rest = _split_project(rel, options.multi_project_dir)
            raw.append(dict(project=project, rest=rest, rel=rel,
                            old=snippet[0], new=snippet[1], order=index))

    logger.info(f"取得 {len(raw)} 個差異片段（{unchanged} 個檔案無變化）")

    # ---- 多專案合併 ----
    merged, singles = _merge_projects(raw, options, result, logger)

    for item in merged:
        result.rules.append(GenRule(
            "pcd", item["file_name"], item["label"],
            item["old"], item["new"],
            note=item.get("note", ""), org_files=item["org_files"]))
    for item in singles:
        result.rules.append(GenRule(
            "sub", item["rel"], _label_for(item["rel"], item["order"]),
            item["old"], item["new"], org_files=[item["rel"]]))

    # ---- 產生 YAML 並讀回驗證 ----
    result.yaml_text = _emit_yaml(options, result.rules, mod_root)
    _verify_yaml(result, logger)

    result.stats = {
        "new_files": len(new_files),
        "sub_rules": sum(1 for r in result.rules if r.kind == "sub"),
        "pcd_rules": sum(1 for r in result.rules if r.kind == "pcd"),
        "unchanged": unchanged,
    }
    return result


def _label_for(rel, order):
    name = Path(rel).name
    return f"{name} 修改 {order + 1}" if order else name


def _merge_projects(raw, options, result, logger):
    """把各專案相同的修改片段合併成一條 file_name 規則。"""
    project_items = [r for r in raw if r["project"]]
    others = [r for r in raw if not r["project"]]

    if not options.merge_projects:
        return [], raw

    def sig(item):
        if options.merge_ignore_comments:
            return (Path(item["rest"]).name.lower(),
                    _strip_comments(item["old"], item["rel"]),
                    _strip_comments(item["new"], item["rel"]))
        return (Path(item["rest"]).name.lower(), item["old"], item["new"])

    groups = {}
    for item in project_items:
        groups.setdefault(sig(item), []).append(item)

    merged, singles = [], list(others)
    for _, items in groups.items():
        projects = {i["project"] for i in items}
        if len(projects) < 2:
            singles.extend(items)
            continue

        names = [Path(i["rel"]).name for i in items]
        file_name = _glob_for(names)
        if file_name is None:
            result.warnings.append(
                f"各專案檔名差異過大，無法合併：{sorted(set(names))}")
            singles.extend(items)
            continue

        first = items[0]
        note = ""
        if options.merge_ignore_comments:
            variants = {i["new"] for i in items}
            if len(variants) > 1:
                note = f"各專案原本的註解略有不同，已統一採用 {first['project']} 的版本"
                result.warnings.append(
                    f"{file_name}：{sorted(projects)} 的內容僅註解不同，已合併（採用 "
                    f"{first['project']}）")
        merged.append(dict(file_name=file_name,
                           label=f"{Path(first['rest']).name}"
                                 f"{' 修改 %d' % (first['order'] + 1) if first['order'] else ''}",
                           old=first["old"], new=first["new"], note=note,
                           org_files=[i["rel"] for i in items]))
        logger.info(f"合併 {len(projects)} 個專案的相同修改 -> file_name: {file_name}")

    return merged, singles


# ---------------------------------------------------------------- YAML 產生

def _quote(text):
    return "'" + str(text).replace("'", "''") + "'"


def _block(text, indent=6):
    """literal block scalar；父節點縮排 4，故使用 |2，內容縮排 6。

    chomping：
      -  結尾沒有換行
      '' 結尾剛好一個換行（clip）
      +  結尾有兩個以上換行（keep）
    三種情況都要先去掉一個結尾換行，因為輸出時各行是用 \\n 串起來的。
    """
    if not text.endswith("\n"):
        chomp, body = "-", text
    else:
        chomp = "+" if text.endswith("\n\n") else ""
        body = text[:-1]
    pad = " " * indent
    lines = [f"|2{chomp}"]
    for line in body.split("\n"):
        lines.append(pad + line if line else "")
    return "\n".join(lines)


def _emit_rule(rule):
    key = "sub_path" if rule.kind == "sub" else "file_name"
    out = [f"  - {key}: {_quote(rule.target)}",
           f"    label: {_quote(rule.label)}",
           "    option_debug_flag: false"]
    if rule.note:
        out.append(f"    note: {_quote(rule.note)}")
    out.append("    old_code: " + _block(rule.old_code))
    out.append("    new_code: " + _block(rule.new_code))
    return "\n".join(out)


def _emit_yaml(options, rules, mod_root):
    key = options.key.strip()
    display = options.display_name.strip() or key
    new_files_dir = (options.new_files_dir.strip()
                     or str(Path(mod_root).resolve()).replace("\\", "/"))

    head = [
        "# " + "=" * 58,
        f"# {display} 專案世代設定",
        "#",
        "# 由 ChangeToDebug 的「產生 Profile」功能從 ORG / MOD 自動產生。",
        f"#   ORG：{options.org_dir}",
        f"#   MOD：{options.mod_dir}",
        "#",
        "# 產生出來的規則 option_debug_flag 一律是 false（必要）。",
        "# 請自行把「選配 / 只在深入偵錯時才需要」的項目改成 true。",
    ]
    if options.header_note:
        head += ["#"] + ["# " + line for line in options.header_note.splitlines()]
    head += ["# " + "=" * 58, ""]

    head += [
        "profile:",
        f"  key: {key}",
        f"  display_name: {_quote(display)}",
    ]
    if options.description.strip():
        head.append(f"  description: {_quote(options.description.strip())}")
    head.append(f"  priority: {int(options.priority)}")

    if options.detect_dirs:
        head += ["", "  detect:", "    any:"]
        head += [f"      - dir: {_quote(d)}" for d in options.detect_dirs if d.strip()]

    if options.pcd_scan_roots:
        head += ["", "  pcd_scan_roots:"]
        head += [f"    - {_quote(p)}" for p in options.pcd_scan_roots if p.strip()]

    new_rules = [r for r in rules if r.kind == "new"]
    if new_rules:
        head += ["", "  # 新增檔案的來源目錄（可改成相對於本 YAML 的路徑）",
                 f"  new_files_dir: {_quote(new_files_dir)}"]

    parts = ["\n".join(head), ""]

    if new_rules:
        parts.append("new_files:")
        for r in new_rules:
            parts.append(f"  - path: {_quote(r.target)}")
        parts.append("")

    # 規則之間用註解行分隔，不能用空行：old_code/new_code 結尾若有空行，
    # block scalar 的 keep chomping 會把分隔用的空行也算進內容裡。
    sep = "# " + "-" * 58

    for section, kind in (("modifications", "sub"),
                          ("platform_pcd_modifications", "pcd")):
        section_rules = [r for r in rules if r.kind == kind]
        if not section_rules:
            parts.append(f"{section}: []")
            parts.append("")
            continue
        parts.append(f"{section}:")
        for r in section_rules:
            parts.append(_emit_rule(r))
            parts.append(sep)
        parts.append("")

    return "\n".join(parts)


def _verify_yaml(result, logger):
    """把產生的 YAML 讀回來，確認每條規則的字串與原始片段完全相同。"""
    try:
        data = yaml.safe_load(result.yaml_text) or {}
    except Exception as exc:
        result.errors.append(f"產生的 YAML 無法解析：{exc}")
        return

    loaded = []
    for section in ("modifications", "platform_pcd_modifications"):
        for item in data.get(section) or []:
            loaded.append((item.get("old_code", ""), item.get("new_code", "")))

    # 比對順序必須跟 _emit_yaml 一致：先 modifications(sub) 再 platform_pcd_modifications(pcd)
    expected = ([(r.old_code, r.new_code) for r in result.rules if r.kind == "sub"]
                + [(r.old_code, r.new_code) for r in result.rules if r.kind == "pcd"])
    if len(loaded) != len(expected):
        result.errors.append(f"規則數不符：預期 {len(expected)}，讀回 {len(loaded)}")
        return

    for index, ((lo, ln), (eo, en)) in enumerate(zip(loaded, expected)):
        if normalize_newlines(lo) != eo or normalize_newlines(ln) != en:
            result.errors.append(f"第 {index + 1} 條規則的內容在 YAML 往返後不一致")
            return

    logger.ok(f"YAML 往返驗證通過（{len(loaded)} 條規則）")


# ---------------------------------------------------------------- 實測套用

def roundtrip_check(yaml_text, options, logger):
    """把 ORG 複製一份、套用產生的 profile，再與 MOD 比對（忽略註解與空行）。"""
    from .profiles import load_profile_file
    from .runner import RunRequest, execute

    report = {"applied": 0, "failed": 0, "verified": 0, "verify_failed": 0,
              "compared": 0, "mismatch": [], "error": ""}
    tmp = Path(tempfile.mkdtemp(prefix="ctdgen_"))
    try:
        workspace = tmp / "ws"
        shutil.copytree(options.org_dir, workspace)
        profile_path = tmp / f"{options.key.strip()}.yaml"
        profile_path.write_text(yaml_text, encoding="utf-8", newline="\n")

        profile = load_profile_file(profile_path)
        if profile.load_error:
            report["error"] = profile.load_error
            return report

        summary = execute(RunRequest(base_path=str(workspace), profile=profile,
                                     task_keys=["patchset"], options={"patchset": {}},
                                     dry_run=False, backup=False,
                                     enable_all_debug_flags=True,
                                     verify_after_run=True),
                          logger)
        report["applied"] = summary.overall.changed
        report["failed"] = summary.overall.failed
        if summary.verification is not None:
            report["verified"] = summary.verification.passed
            report["verify_failed"] = summary.verification.failed

        mod_root = Path(options.mod_dir)
        for rel in _walk_rel(workspace):
            mod_file = mod_root / rel
            if not mod_file.is_file():
                continue
            got = _strip_comments(_text(workspace / rel), rel)
            want = _strip_comments(_text(mod_file), rel)
            report["compared"] += 1
            if got != want:
                report["mismatch"].append(rel)
    except Exception as exc:
        report["error"] = str(exc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return report


def suggest_options(package_dir):
    """由套件目錄推測 ORG / MOD 位置與世代代號。"""
    package = Path(package_dir)
    org = package / "ORG"
    mod = package / "MOD"
    key = ""
    match = re.search(r"(FY\d{2})", package.name, re.IGNORECASE)
    if match:
        key = match.group(1).upper()
    return (str(org) if org.is_dir() else "",
            str(mod) if mod.is_dir() else "",
            key)
