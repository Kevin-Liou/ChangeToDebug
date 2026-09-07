"""base 快照：保存「修改之前的完整檔案」，供日後做 3-way merge。

為什麼需要：
    現在的規則只記得 old_code / new_code 兩個片段，比對不到就只能宣告失敗。
    3-way merge 需要第三份資料——改動前的**完整檔案**（BASE）。有了它才分得出
    「上游動的是我順便帶進來的前後文」與「上游動的正是我要改的那一行」。

base 從哪裡來（依可靠度排序）：
    org        code change 套件的 ORG 資料夾，這就是 base 的定義
    extracted  從一棵尚未套用此 change 的 source tree 反向擷取（可自動驗證）
    git        從 git 取未修改的版本

刻意支援「部分存在」：
    不是每條規則都找得到 base（例如手上沒有對應世代的乾淨樹）。manifest 逐條記錄，
    缺的標明原因；有 base 的走 merge，沒有的退回現行的字串比對。
"""

import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from .patcher import normalize_newlines, read_text

try:
    import yaml
except Exception:       # pragma: no cover - 由 GUI 統一提示安裝
    yaml = None

MANIFEST_NAME = "base_manifest.yaml"
BASE_DIR_NAME = "base"
MANIFEST_VERSION = 1

#: base 的來源，會寫進 manifest 供日後判斷可信度
SOURCE_ORG = "org"
SOURCE_EXTRACTED = "extracted"
SOURCE_GIT = "git"


@dataclass
class BaseRef:
    """一條規則對應的 base 檔案。"""

    path: str = ""
    source: str = ""
    approximate: bool = False   # pcd 規則跨專案時，base 取自另一個專案的同名檔
    representative: str = ""    # 該 base 來自哪個專案

    def read(self):
        """回傳正規化換行後的內容；讀不到回 None。"""
        try:
            return normalize_newlines(read_text(self.path)[0])
        except Exception:
            return None


@dataclass
class BaseSnapshot:
    """一個 profile 的 base 快照（base/ 目錄 + manifest）。"""

    root: str = ""                                  # base/ 目錄
    base_commit: str = ""
    entries: dict = field(default_factory=dict)     # rule_id -> manifest 項目
    load_error: str = ""

    @property
    def available(self):
        return bool(self.root) and os.path.isdir(self.root) and bool(self.entries)

    def covered(self):
        """有 base 可用的 rule_id 集合。"""
        return {rid for rid, item in self.entries.items() if item.get("base_file")}

    def missing(self):
        """沒有 base 的 rule_id -> 原因。"""
        return {rid: item.get("reason", "未記錄原因")
                for rid, item in self.entries.items() if not item.get("base_file")}

    def realign(self, rules):
        """讓 manifest 的項目跟上 profile 現在的規則編號。

        manifest 以 rule_id（mod:N）當 key，而 N 是規則在 YAML 裡的位置——使用者刪掉
        或搬動一條規則，後面所有規則的編號都會改變，manifest 就會把 base 配給錯的規則，
        而 3-way merge 拿錯的 base 去合，結果只會是垃圾。項目裡另外記了 sub_path /
        file_name / label，這裡用它們認人，重新對回正確的 rule_id。

        回傳說明訊息清單；空清單代表本來就對。只改記憶體中的對應，不寫檔。
        """
        if not self.entries:
            return []

        def identity(sub_path, file_name, label):
            return (str(sub_path or "").replace("\\", "/"), str(file_name or ""),
                    str(label or ""))

        def matches(entry, rule):
            # 有記路徑就要路徑相同；label 一律要相同
            if entry.get("sub_path") and identity(entry.get("sub_path"), "", "")[0] \
                    != identity(rule.sub_path, "", "")[0]:
                return False
            if entry.get("file_name") and str(entry.get("file_name")) != rule.file_name:
                return False
            return str(entry.get("label") or "") == str(rule.label or "")

        notes, new_entries, claimed = [], {}, set()
        for rule in rules:
            entry = self.entries.get(rule.rule_id)
            if entry is not None and matches(entry, rule):
                new_entries[rule.rule_id] = entry
                claimed.add(id(entry))
                continue
            found = next((e for e in self.entries.values()
                          if id(e) not in claimed and matches(e, rule)), None)
            if found is None:
                if entry is not None:
                    notes.append(f"{rule.rule_id}（{rule.label}）在 manifest 裡對到的是"
                                 f"「{entry.get('label')}」，且找不到它自己的紀錄，視為沒有 base")
                continue
            old_id = found.get("rule_id", "?")
            found["rule_id"] = rule.rule_id
            new_entries[rule.rule_id] = found
            claimed.add(id(found))
            notes.append(f"{old_id} -> {rule.rule_id}　{rule.label}")

        dropped = [e for e in self.entries.values() if id(e) not in claimed]
        for entry in dropped:
            notes.append(f"移除已不存在的規則的紀錄：{entry.get('rule_id')}　{entry.get('label')}")

        self.entries = new_entries
        return notes

    def orphan_base_files(self):
        """base/ 底下沒有任何 manifest 項目引用的檔案（realign 移除項目後可能出現）。"""
        root = Path(self.root)
        if not root.is_dir():
            return []
        referenced = set()
        for entry in self.entries.values():
            if entry.get("base_file"):
                referenced.add((root / str(entry["base_file"]).replace("\\", "/")).resolve())
        orphans = []
        for path in root.rglob("*"):
            if not path.is_file() or ".bak." in path.name:
                continue
            if "_anchors" in path.relative_to(root).parts:
                continue        # 錨點的 base 由 profile.yaml 引用，不在 manifest 裡
            if path.resolve() not in referenced:
                orphans.append(path)
        return orphans

    def base_for(self, rule_id, target_path=""):
        """取得某條規則的 base 檔案；沒有就回 None。

        pcd 規則會展開到多個專案，但 base 只存了一份代表副本。若目標檔案不是
        代表副本本身，回傳的 BaseRef 會標記 approximate，讓上層知道這份 base
        是借用別的專案的，衝突時要據實告知而不是當成確定答案。
        """
        item = self.entries.get(rule_id)
        if not item or not item.get("base_file"):
            return None
        path = Path(self.root) / str(item["base_file"]).replace("\\", "/")
        if not path.is_file():
            return None

        approximate = False
        covers = item.get("covers") or []
        if covers and target_path:
            target = str(target_path).replace("\\", "/")
            approximate = not any(target.endswith(str(c).replace("\\", "/")) for c in covers)
        return BaseRef(str(path), item.get("source", ""), approximate,
                       item.get("representative", ""))

    def anchor_base(self, anchor, target_path=""):
        """取得某組額外錨點的 base；錨點沒帶 base 或檔案不在就回 None。

        錨點的 base 是在某一個特定檔案上解決衝突時存下來的，covers 記錄那個檔案。
        目標不是那個檔案時標記 approximate，讓上層知道這份 base 是借來的。
        """
        if not anchor.base_file or not self.root:
            return None
        path = Path(self.root) / str(anchor.base_file).replace("\\", "/")
        if not path.is_file():
            return None
        approximate = False
        if anchor.covers and target_path:
            target = str(target_path).replace("\\", "/")
            approximate = not any(target.endswith(str(c).replace("\\", "/"))
                                  for c in anchor.covers)
        return BaseRef(str(path), "anchor", approximate, "")


# ---------------------------------------------------------------- manifest 讀寫

def sha256_of(path):
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                digest.update(chunk)
    except Exception:
        return ""
    return digest.hexdigest()


def load_snapshot(package_dir):
    """從 profile 套件目錄讀出 base 快照。沒有 manifest 時回傳空的 BaseSnapshot。"""
    package_dir = Path(package_dir)
    snapshot = BaseSnapshot(root=str(package_dir / BASE_DIR_NAME))

    manifest_path = package_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        return snapshot
    if yaml is None:
        snapshot.load_error = "未安裝 PyYAML，無法讀取 base manifest"
        return snapshot

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as exc:
        snapshot.load_error = f"base manifest 解析失敗：{exc}"
        return snapshot

    if not isinstance(data, dict):
        snapshot.load_error = "base manifest 根節點不是對應表"
        return snapshot

    snapshot.base_commit = str(data.get("base_commit", "") or "")
    for item in data.get("entries") or []:
        if isinstance(item, dict) and item.get("rule_id"):
            snapshot.entries[str(item["rule_id"])] = item
    return snapshot


def dump_manifest(entries, base_commit=""):
    """把 manifest 序列化成 YAML 文字（欄位順序固定，方便 diff）。"""
    if yaml is None:
        return ""
    payload = {"version": MANIFEST_VERSION}
    if base_commit:
        payload["base_commit"] = base_commit
    payload["entries"] = entries
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False,
                          default_flow_style=False)


def write_package(package_dir, profile_yaml, base_files, entries, base_commit=""):
    """寫出一個 profile 套件目錄：profile.yaml + base/ + base_manifest.yaml。

    base_files 形式為 {base 內的相對路徑: 來源檔絕對路徑}。
    回傳實際複製的檔案數。
    """
    import shutil

    package_dir = Path(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "profile.yaml").write_text(profile_yaml, encoding="utf-8", newline="\n")

    base_root = package_dir / BASE_DIR_NAME
    base_root.mkdir(parents=True, exist_ok=True)

    copied = 0
    for rel, source in sorted(base_files.items()):
        target = base_root / rel.replace("\\", "/")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied += 1

    (package_dir / MANIFEST_NAME).write_text(
        dump_manifest(entries, base_commit), encoding="utf-8", newline="\n")
    return copied


# ---------------------------------------------------------------- 從 source tree 擷取

def _is_pre_modification(text, rule):
    """判斷這份內容是否處於「尚未套用此規則」的狀態，也就是可以當 base。

    順序很重要：插入型規則的 new_code 完整包含 old_code，套用後兩者都在，
    所以必須先排除「已套用」再確認「找得到 old_code」。
    """
    old = normalize_newlines(rule.old_code or "")
    new = normalize_newlines(rule.new_code or "")
    if not old:
        return False

    if rule.regex:
        applied = rule.regex_applied_check
        if applied:
            try:
                if re.search(applied, text, re.MULTILINE):
                    return False        # 已套用
            except re.error:
                pass
        try:
            return re.search(old, text, re.MULTILINE) is not None
        except re.error:
            return False

    if new and new in text:
        return False                    # 已套用
    return old in text


def extract(profile, base_path, resolve_targets, logger=None):
    """從一棵 source tree 反向擷取 base。

    resolve_targets(rule) 須回傳該規則對應的實際檔案路徑清單（由呼叫端提供，
    因為 file_name 型規則的掃描邏輯屬於 patchset task）。

    回傳 (base_files, entries, stats)：
        base_files  {base 內相對路徑: 來源絕對路徑}
        entries     manifest 的 entries 清單（含找不到 base 的規則與原因）
        stats       {'covered': n, 'missing': n, 'files': n}
    """
    base_root = Path(base_path)
    base_files = {}
    entries = []
    covered = missing = 0

    for rule in profile.all_rules:
        entry = {"rule_id": rule.rule_id, "label": rule.label}
        if rule.sub_path:
            entry["sub_path"] = rule.sub_path
        if rule.file_name:
            entry["file_name"] = rule.file_name

        if rule.is_new_file:
            # 新增檔案沒有「改動前的版本」，本來就不需要 base
            entry.update(base_file="", reason="新增檔案，不需要 base")
            entries.append(entry)
            continue

        matched = []
        for path in resolve_targets(rule):
            path = Path(path)
            if not path.is_file():
                continue
            try:
                text = normalize_newlines(read_text(path)[0])
            except Exception:
                continue
            if _is_pre_modification(text, rule):
                matched.append(path)

        if not matched:
            entry.update(base_file="",
                         reason="此樹中找不到處於改動前狀態的檔案（可能已套用、"
                                "內容不同，或檔案不存在）")
            entries.append(entry)
            missing += 1
            continue

        representative = matched[0]
        try:
            rel = representative.relative_to(base_root).as_posix()
        except ValueError:
            rel = representative.name
        base_files[rel] = str(representative)

        entry.update(base_file=rel, source=SOURCE_EXTRACTED,
                     sha256=sha256_of(representative))
        if len(matched) > 1:
            entry["covers"] = [_rel_or_name(p, base_root) for p in matched]
            entry["representative"] = project_of(rel)
        entries.append(entry)
        covered += 1

    if logger is not None:
        logger.info(f"可取得 base 的規則 {covered} 條，缺 {missing} 條，"
                    f"需快照 {len(base_files)} 個檔案")

    return base_files, entries, {"covered": covered, "missing": missing,
                                 "files": len(base_files)}


def extract_for_profile(profile, base_path, logger):
    """便利入口：自動組出與實際套用相同的檔案定位方式，再擷取 base。"""
    from .tasks.patchset import make_target_resolver

    resolver = make_target_resolver(profile, base_path, logger)
    return extract(profile, base_path, resolver, logger)


def _rel_or_name(path, root):
    try:
        return Path(path).relative_to(root).as_posix()
    except ValueError:
        return Path(path).name


def project_of(rel):
    """從 MultiProject/<專案>/... 取出專案名稱，用來說明 base 借自哪個專案。"""
    parts = str(rel).replace("\\", "/").split("/")
    if "MultiProject" in parts:
        index = parts.index("MultiProject")
        if index + 1 < len(parts):
            return parts[index + 1]
    return ""
