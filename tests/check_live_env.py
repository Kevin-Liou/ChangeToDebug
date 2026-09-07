"""真實環境的煙霧測試：repo 內的 FY25/26/27 能載入；有 BIOS 樹時跑一次預覽（唯讀）。

只讀不寫。找不到 G:\\HpNvlPlat1 就跳過樹相關的部分，不算失敗。
"""
import os

from _common import REPO, Checker, quiet_logger, statuses

from changetodebug.core.profiles import load_profiles
from changetodebug.core.runner import RunRequest, execute

ck = Checker()
TREE = os.environ.get("CTD_TEST_TREE", r"G:\HpNvlPlat1")

ck.section("repo 內的 profile")
profiles = {p.key: p for p in load_profiles([str(REPO / "profiles")])}
for key in ("FY25", "FY26", "FY27"):
    p = profiles.get(key)
    ck(f"{key} 載入無錯誤", p is not None and not p.load_error, getattr(p, "load_error", "找不到"))
    if p is not None:
        ck(f"{key} manifest 與規則編號一致（無需重新對應）", p.base_warnings == [], p.base_warnings[:3])
        ck(f"{key} 沒有孤兒 base", p.base_snapshot is None or p.base_snapshot.orphan_base_files() == [])
fy27 = profiles.get("FY27")
if fy27:
    with_anchor = [r.label for r in fy27.all_rules if r.anchors]
    ck("FY27 帶有多錨點規則", bool(with_anchor), with_anchor)
    dead = fy27.dead_rules()
    ck("FY27 沒有死規則", not dead, [r.label for r in dead])

ck.section(f"預覽模式 @ {TREE}")
if fy27 and os.path.isdir(TREE):
    s = execute(RunRequest(base_path=TREE, profile=fy27, task_keys=["patchset"], options={"patchset": {}},
                           dry_run=True, backup=False, enable_all_debug_flags=True, verify_after_run=False),
                quiet_logger())
    st = statuses(s)
    print("   ", st)
    ck("展開項目數 > 0", s.overall.total > 0)
    ck("沒有「錯誤」狀態", st.get("錯誤", 0) == 0, st.get("錯誤"))
    ck("預覽模式沒留下衝突產物", not s.conflict_dir or not os.path.isdir(s.conflict_dir))
else:
    print(f"   （沒有 {TREE}，跳過。可用環境變數 CTD_TEST_TREE 指定另一棵樹）")

ck.finish("live_env")
