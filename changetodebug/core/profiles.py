"""Profile（專案世代設定）載入與自動偵測。

一個 profile = 一個 YAML 檔，描述某個世代（FY25 / FY26 / FY27 ...）需要哪些修改。
新增 FY27 不需要改任何 Python 程式碼，只要把 FY27.yaml 放進 profiles\\ 即可。

YAML 結構（所有欄位皆可省略，省略時使用預設值）::

    profile:
      key: FY27                       # 省略時取檔名
      display_name: FY27 (Wildcat Lake)
      description: 說明文字
      priority: 30                    # 數字小者先被比對
      detect:                         # 自動偵測條件
        any:                          # 任一命中即算符合
          - dir: .gitman/Intel/WildcatLakeBoardPkg
        all: []                       # 全部命中才算符合（可與 any 併用）
      pcd_scan_roots:                 # 需要遞迴掃描檔名的根目錄
        - HpPlatformPkg/MultiProject
      driver_debug:                   # Driver Debug 功能的專案相關設定
        search_roots: [...]
        memory_debug: {...}

    modifications:                    # 以 sub_path 精準定位的修改
      - sub_path: ...
        old_code: |
        new_code: |
        option_debug_flag: false
        regex: false
        label: 選填的顯示名稱

    platform_pcd_modifications:       # 以 file_name 遞迴搜尋的修改
      - file_name: PlatformPcdConfig.dsc
        old_code: |
        new_code: |
        option_debug_flag: false
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from ..appinfo import profile_search_dirs
from .patcher import Rule

try:
    import yaml
except Exception:       # pragma: no cover - 由 GUI 統一提示安裝
    yaml = None

#: 舊版 yaml 沒有 detect 區塊時使用的內建偵測條件
BUILTIN_DETECT = {
    "FY25": [{"dir": ".gitman/Intel/MeteorLakeBoardPkg"}],
    "FY26": [{"dir": ".gitman/Intel/PantherLakeBoardPkg"}],
}

DEFAULT_PCD_SCAN_ROOTS = ["HpPlatformPkg/MultiProject"]

DEFAULT_DRIVER_DEBUG = {
    "search_roots": [
        "HpPlatformPkg", "HpPe", "Edk2", "Edk2Platforms",
        "HpCore", "HpEpsc", "HpIntel", "Intel", ".gitman",
    ],
    "message_map": {
        "DEBUG_WARN": "DEBUG_ERROR",
        "DEBUG_INFO": "DEBUG_ERROR",
    },
    "memory_debug": {
        "pcd_scan_root": "HpPlatformPkg/MultiProject",
        "pcd_file": "PlatformPcdConfig.dsc",
        "pcd_pattern": r"(PcdHpMemoryDebugEnable\s*\|\s*)FALSE",
        "pcd_replacement": r"\1TRUE",
        "acpi_area_sub_path":
            "HpPe/HpCommonPkg/MemoryDebug/Dxe/DxeMemDebugAcpiArea/DxeMemDebugAcpiArea.c",
        "acpi_area_old": "IsLegacySupported()",
        "acpi_area_new": "0",
        "inf_package": "HpCommonPkg/MemoryDebug/MemoryDebug.dec",
        "inf_library": "MemDebugLib",
    },
}

_FILENAME_KEY_RE = re.compile(r"^(?:modifications[_-])?(.+)$", re.IGNORECASE)


def _deep_merge(base, override):
    """以 override 覆寫 base 的巢狀 dict（不修改原物件）。"""
    result = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


@dataclass
class Profile:
    key: str
    display_name: str = ""
    description: str = ""
    priority: int = 100
    detect_any: list = field(default_factory=list)
    detect_all: list = field(default_factory=list)
    pcd_scan_roots: list = field(default_factory=lambda: list(DEFAULT_PCD_SCAN_ROOTS))
    driver_debug: dict = field(default_factory=lambda: dict(DEFAULT_DRIVER_DEBUG))
    rules: list = field(default_factory=list)       # sub_path 型
    pcd_rules: list = field(default_factory=list)   # file_name 型
    new_file_rules: list = field(default_factory=list)  # 新增檔案型
    new_files_dir: str = ""
    source_path: str = ""
    load_error: str = ""

    @property
    def title(self):
        return self.display_name or self.key

    @property
    def all_rules(self):
        # 新增檔案排在最前面：後面的文字修改可能會引用到這些新檔
        return list(self.new_file_rules) + list(self.rules) + list(self.pcd_rules)

    def rule_count(self, enable_all_debug_flags=True):
        return sum(1 for r in self.all_rules
                   if enable_all_debug_flags or not r.option_debug_flag)

    # ---- 自動偵測 ----
    def matches(self, base_path):
        base = Path(base_path)
        if not base.is_dir():
            return False
        if not self.detect_any and not self.detect_all:
            return False
        if self.detect_all and not all(_check_condition(base, c) for c in self.detect_all):
            return False
        if self.detect_any:
            return any(_check_condition(base, c) for c in self.detect_any)
        return True

    def detect_hint(self):
        """給 GUI 顯示「這個 profile 靠什麼判斷」。"""
        parts = []
        for cond in list(self.detect_any) + list(self.detect_all):
            parts.extend(str(v) for v in cond.values())
        return "、".join(parts) if parts else "（未定義偵測條件）"


def _check_condition(base, cond):
    if not isinstance(cond, dict):
        return False
    for kind, value in cond.items():
        value = str(value).replace("\\", "/").strip("/")
        target = base / value
        if kind == "dir" and target.is_dir():
            return True
        if kind == "file" and target.is_file():
            return True
        if kind == "glob" and any(base.glob(value)):
            return True
        if kind == "exists" and target.exists():
            return True
    return False


# ---------------------------------------------------------------- 載入

def _key_from_filename(path):
    stem = Path(path).stem
    m = _FILENAME_KEY_RE.match(stem)
    return (m.group(1) if m else stem).strip()


def _build_rules(raw_list, source, key_prefix):
    rules = []
    for index, item in enumerate(raw_list or []):
        if not isinstance(item, dict):
            continue
        sub_path = str(item.get("sub_path", "") or "")
        file_name = str(item.get("file_name", "") or "")
        label = str(item.get("label", "") or "") or (sub_path or file_name)
        rules.append(Rule(
            rule_id=f"{key_prefix}:{index}",
            label=label,
            sub_path=sub_path,
            file_name=file_name,
            old_code=item.get("old_code", "") or "",
            new_code=item.get("new_code", "") or "",
            regex=bool(item.get("regex", False)),
            option_debug_flag=bool(item.get("option_debug_flag", False)),
            note=str(item.get("note", "") or ""),
            source=source,
        ))
    return rules


def _resolve_new_files_dir(raw, profile_path):
    """new_files_dir 可以是絕對路徑，或相對於 profile 檔所在目錄。"""
    if not raw:
        return ""
    candidate = Path(str(raw).replace("\\", "/"))
    if not candidate.is_absolute():
        candidate = Path(profile_path).parent / candidate
    return str(candidate)


def _build_new_file_rules(raw_list, base_dir):
    rules = []
    for index, item in enumerate(raw_list or []):
        if isinstance(item, str):
            item = {"path": item}
        if not isinstance(item, dict):
            continue
        target = str(item.get("target") or item.get("path") or "")
        source = str(item.get("source") or item.get("path") or target)
        if not target or not source:
            continue
        source_path = Path(source.replace("\\", "/"))
        if not source_path.is_absolute():
            if not base_dir:
                continue        # 沒有 new_files_dir 就無法定位相對來源
            source_path = Path(base_dir) / source_path
        rules.append(Rule(
            rule_id=f"new:{index}",
            label=str(item.get("label") or "") or target,
            sub_path=target,
            new_file_source=str(source_path),
            overwrite=bool(item.get("overwrite", False)),
            option_debug_flag=bool(item.get("option_debug_flag", False)),
            note=str(item.get("note", "") or ""),
            source="new_files",
        ))
    return rules


def load_profile_file(path):
    """讀取單一 profile YAML。解析失敗時回傳帶 load_error 的 Profile。"""
    path = Path(path)
    key = _key_from_filename(path)

    if yaml is None:
        return Profile(key=key, source_path=str(path),
                       load_error="未安裝 PyYAML，請執行 pip install pyyaml")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as exc:
        return Profile(key=key, source_path=str(path), load_error=f"YAML 解析失敗：{exc}")

    if not isinstance(data, dict):
        return Profile(key=key, source_path=str(path), load_error="YAML 根節點不是對應表")

    meta = data.get("profile") or {}
    if not isinstance(meta, dict):
        meta = {}

    key = str(meta.get("key") or key)
    detect = meta.get("detect") or {}
    detect_any = list(detect.get("any") or []) if isinstance(detect, dict) else []
    detect_all = list(detect.get("all") or []) if isinstance(detect, dict) else []
    if not detect_any and not detect_all:
        detect_any = list(BUILTIN_DETECT.get(key.upper(), []))

    new_files_dir = _resolve_new_files_dir(meta.get("new_files_dir"), path)

    profile = Profile(
        key=key,
        display_name=str(meta.get("display_name") or key),
        description=str(meta.get("description") or ""),
        priority=int(meta.get("priority", 100) or 100),
        detect_any=detect_any,
        detect_all=detect_all,
        pcd_scan_roots=[str(p) for p in (meta.get("pcd_scan_roots")
                                         or DEFAULT_PCD_SCAN_ROOTS)],
        driver_debug=_deep_merge(DEFAULT_DRIVER_DEBUG, meta.get("driver_debug") or {}),
        rules=_build_rules(data.get("modifications"), "modifications", "mod"),
        pcd_rules=_build_rules(data.get("platform_pcd_modifications"),
                               "platform_pcd_modifications", "pcd"),
        new_file_rules=_build_new_file_rules(data.get("new_files"), new_files_dir),
        new_files_dir=new_files_dir,
        source_path=str(path),
    )
    if not profile.all_rules:
        profile.load_error = "檔案中沒有任何 modifications / platform_pcd_modifications"
    return profile


def load_profiles(search_dirs=None):
    """掃描所有搜尋路徑載入 profile；同名 key 以先出現者為準。"""
    dirs = search_dirs if search_dirs is not None else profile_search_dirs()
    profiles = []
    seen_keys = set()

    for directory in dirs:
        directory = Path(directory)
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.y*ml")):
            # 底線開頭視為範本 / 停用；另外排除專案內其他用途的 yaml
            if path.name.startswith("_") or path.name.lower().startswith(("requirements", "settings")):
                continue
            profile = load_profile_file(path)
            upper = profile.key.upper()
            if upper in seen_keys:
                continue
            # 完全不是 profile 的 yaml（沒有規則也沒有 profile 區塊）就跳過
            if profile.load_error and not profile.all_rules and not profile.detect_any:
                continue
            seen_keys.add(upper)
            profiles.append(profile)

    profiles.sort(key=lambda p: (p.priority, p.key))
    return profiles


def detect_profile(base_path, profiles):
    """回傳第一個符合的 profile；沒有就回傳 None。"""
    if not base_path or not os.path.isdir(base_path):
        return None
    for profile in profiles:
        if profile.matches(base_path):
            return profile
    return None
