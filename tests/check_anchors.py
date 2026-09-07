"""多錨點的完整流程：套用 -> 衝突 -> 解決 -> 新增錨點 -> 新舊樹都套得上；外加 manifest 對齊。

用 _common 的迷你 profile 與三棵假樹（old / new / newer），全程在暫存目錄。
"""
import shutil
from pathlib import Path

from _common import (ADDED, REL_C, REL_INF, Checker, load_mini, logger_pair, make_profile,
                     make_tree, quiet_logger, read, redirect_conflicts, rmtree, run_patchset,
                     sandbox, statuses)

from changetodebug.core import conflicts, reanchor
from changetodebug.core.basesnap import BaseRef
from changetodebug.core.conflicts import ConflictRecord
from changetodebug.core.patcher import (Anchor, PatchEngine, Rule, STATUS_ALREADY, STATUS_MERGED,
                                        STATUS_MODIFIED, STATUS_NOT_FOUND, STATUS_PREVIEW)

ck = Checker()
tmp = sandbox("ctd_anchor_")
redirect_conflicts(tmp)
quiet = quiet_logger()


def rule_of(profile, label):
    return next(r for r in profile.all_rules if r.label == label)


def engine_apply(profile, rule, path, reverse=False, dry=False):
    snap = profile.base_snapshot
    logs, lg = logger_pair()
    res = PatchEngine(lg, dry_run=dry, backup=False, diagnose=False).apply(
        str(path), rule, snap.base_for(rule.rule_id, str(path)), reverse=reverse,
        anchor_refs=[snap.anchor_base(a, str(path)) for a in rule.anchors])
    used = next((m for m in logs if "組錨點" in m), "")
    return res, used


try:
    # ================================================================ A. 模型
    ck.section("A. Rule.variants / anchors 解析")
    make_profile(tmp)
    prof = load_mini(tmp)
    ck("迷你 profile 載入", not prof.load_error and len(prof.all_rules) == 4, prof.load_error)
    ck("manifest 本來就對齊，無警告", prof.base_warnings == [], prof.base_warnings)
    r = Rule(old_code="A", new_code="B", anchors=[Anchor(old_code="A2", new_code="B2")])
    vs = r.variants()
    ck("variants = 規則本身 + 各錨點，且都沒有 anchors", len(vs) == 2 and not vs[1].anchors and vs[1].old_code == "A2")
    ck("沒有 anchors 的規則 variants 是自己", Rule(old_code="x").variants()[0].old_code == "x")

    # ================================================================ B. 引擎挑選（合成）
    ck.section("B. 引擎挑選錨點")
    w = tmp / "w"
    w.mkdir()
    HEAD_ = "[Defines]\n  X = 1\n\n[LibraryClasses]\n   HpGpioLib\n"
    TAIL = "\n[Guids]\n"
    base_A = HEAD_ + "   PcdLib\n" + TAIL
    base_B = HEAD_ + "   PcdLib\n   HpVpinSelectionLib\n" + TAIL
    OLD_A, NEW_A = "   HpGpioLib\n   PcdLib\n\n[Guids]\n", "   HpGpioLib\n   PcdLib\n   HpForceDebugLib\n\n[Guids]\n"
    OLD_B, NEW_B = "   PcdLib\n   HpVpinSelectionLib\n\n[Guids]\n", "   PcdLib\n   HpVpinSelectionLib\n   HpForceDebugLib\n\n[Guids]\n"
    rule = Rule(rule_id="mod:0", label="X.inf", sub_path="X.inf", old_code=OLD_A, new_code=NEW_A,
                anchors=[Anchor(old_code=OLD_B, new_code=NEW_B, note="newer")])
    (w / "bA").write_text(base_A, encoding="utf-8")
    (w / "bB").write_text(base_B, encoding="utf-8")
    refA, refB = BaseRef(str(w / "bA")), BaseRef(str(w / "bB"))

    def go(text, name, **kw):
        f = w / name
        f.write_text(text, encoding="utf-8")
        logs, lg = logger_pair()
        res = PatchEngine(lg, dry_run=kw.get("dry", False), backup=False, diagnose=False).apply(
            str(f), rule, refA, reverse=kw.get("reverse", False), anchor_refs=[refB])
        return res, f.read_text(encoding="utf-8"), logs

    res, out, logs = go(base_A, "old")
    ck("舊樹 -> 第 1 組精確命中", res.status == STATUS_MODIFIED and "HpForceDebugLib" in out and not any("第 2 組" in m for m in logs))
    res, out, logs = go(base_B, "new")
    ck("新樹 -> 第 2 組精確命中", res.status == STATUS_MODIFIED and out == base_B.replace(OLD_B, NEW_B) and any("使用第 2 組錨點" in m for m in logs))
    res, _, _ = go(out, "applied")
    ck("已套用 -> 已套用過", res.status == STATUS_ALREADY)
    res, out2, _ = go(out, "revert", reverse=True)
    ck("反向移除走第 2 組", res.status == STATUS_MODIFIED and out2 == base_B)
    neither = base_B.replace("  X = 1", "  X = 2").replace("   PcdLib\n   HpVpin", "   PcdLib\n   FooLib\n   HpVpin")
    res, out, logs = go(neither, "neither")
    ck("兩組都不中 -> 用最像的 base 三方合併", res.status == STATUS_MERGED and "HpForceDebugLib" in out and any("第 2 組錨點的 base" in m for m in logs))
    res, _, logs = go("hello\nworld\n", "none")
    ck("全部失敗 -> 找不到片段，只警告一次", res.status == STATUS_NOT_FOUND and sum("找不到指定片段" in m for m in logs) == 1)
    res, _, logs = go(base_B, "dry", dry=True)
    ck("預覽模式也挑第 2 組", res.status == STATUS_PREVIEW and any("第 2 組" in m for m in logs))

    # ================================================================ C. 完整流程
    ck.section("C. 舊樹全套上；新樹衝突並留下可用的產物")
    old = make_tree(tmp / "old", "old")
    s, _ = run_patchset(prof, old)
    ck("舊樹：全部 GOOD、無衝突", s.overall.failed == 0 and not s.conflicts, statuses(s))
    ck("舊樹：四條規則的新增內容都在", all(v in read(old / p) for p, v in (
        (REL_INF, ADDED["Foo.inf"]), (REL_C, ADDED["Foo.c"]), (REL_C, ADDED["Foo.c 修改 2"]))))

    new = make_tree(tmp / "new", "new")
    before_c = read(new / REL_C)
    s, logs = run_patchset(prof, new)
    st = statuses(s)
    ck("新樹：Foo.inf 與 Foo.c 兩檔衝突", st.get("合併衝突") == 3 and len(s.conflicts) == 2, st)
    ck("新樹：dsc 兩個專案照樣套上", st.get("已修改") == 2)
    ck("新樹：衝突檔原檔一個位元組沒動、沒有標記", read(new / REL_C) == before_c and "<<<<<<<" not in read(new / REL_INF))
    recs = {r.label: r for r in s.conflicts}
    rec_c = next(r for r in s.conflicts if r.target.endswith("Foo.c"))
    rec_inf = next(r for r in s.conflicts if r.target.endswith("Foo.inf"))
    ck("同檔兩條規則併成一筆 mod:1,mod:2", rec_c.rule_id == "mod:1,mod:2")
    ck("每筆的 .merged 已產生且帶標記", all(Path(r.merged).is_file() and "<<<<<<<" in Path(r.merged).read_text(encoding="utf-8") for r in s.conflicts))
    ck("index.yaml 寫出、latest_run 找得到", conflicts.latest_run(str(new)) is not None
       and len(conflicts.load_index(s.conflict_dir)) == 2)
    ck("衝突產物在暫存目錄", s.conflict_dir.startswith(str(tmp)))

    ck.section("D. 使用者解完 -> 寫回專案 -> 新增錨點")
    cur_inf, cur_c = read(rec_inf.current), read(rec_c.current)
    resolved_inf = cur_inf.replace("   HpVpinSelectionLib\n", "   HpVpinSelectionLib\n   HpForceDebugLib\n")
    resolved_c = cur_c.replace("#include <C.h>\n", "#include <C.h>\n#include <HpForceDebugLib.h>\n") \
                      .replace("  Status = Extra ();\n", "  Status = Extra ();\n  DEBUG ((DEBUG_INFO, \"[HpForceDebug] Foo\\n\"));\n")
    Path(rec_inf.merged).write_text(resolved_inf, encoding="utf-8", newline="\n")
    Path(rec_c.merged).write_text(resolved_c, encoding="utf-8", newline="\n")
    applied = conflicts.apply_all(s.conflicts, quiet)
    ck("兩檔都寫回", len(applied.applied) == 2 and read(new / REL_INF) == resolved_inf and read(new / REL_C) == resolved_c)

    bad = reanchor.plan(prof, rec_c, quiet, project_root=str(new))
    ck("複合 rule_id 不拆開 -> 明確拒絕", not bad.ok and "多條規則" in bad.error)
    plans = [reanchor.plan(prof, rec_inf, quiet, project_root=str(new)),
             reanchor.plan(prof, rec_c, quiet, project_root=str(new), rule_id="mod:1"),
             reanchor.plan(prof, rec_c, quiet, project_root=str(new), rule_id="mod:2")]
    ck("三個 plan 都成功", all(p.ok for p in plans), [p.error for p in plans])
    ck("同檔兩條各挑自己那段", "HpForceDebugLib.h" in plans[1].new_code and "[HpForceDebug] Foo" not in plans[1].new_code
       and "[HpForceDebug] Foo" in plans[2].new_code and "HpForceDebugLib.h" not in plans[2].new_code)
    ck("各 plan 標了「另有改動不屬於本規則」", all(any("不屬於本規則" in w for w in p.warnings) for p in plans[1:]))
    yaml_before = (Path(prof.package_dir) / "profile.yaml").read_text(encoding="utf-8")
    results = [reanchor.apply(prof, rec, p, quiet) for rec, p in zip((rec_inf, rec_c, rec_c), plans)]
    ck("三筆連續寫回都成功（不互相覆蓋）", all(ok for ok, _ in results), [m for _, m in results])

    prof2 = load_mini(tmp)
    ck("重新載入無錯誤", not prof2.load_error, prof2.load_error)
    ck("mod:0/1/2 各多一組錨點，pcd:0 沒有", [len(r.anchors) for r in prof2.all_rules] == [1, 1, 1, 0])
    ck("原本的 old_code / new_code 不變", all(a.old_code == b.old_code and a.new_code == b.new_code
                                            for a, b in zip(prof.all_rules, prof2.all_rules)))
    ck("錨點的 base 都寫在 base/_anchors/ 下", all((Path(prof2.package_dir) / "base" / r.anchors[0].base_file).is_file()
                                                 for r in prof2.all_rules if r.anchors))
    ck("主 base 與 manifest 沒動", prof2.base_warnings == [] and read(Path(prof2.package_dir) / "base" / REL_INF) == read(Path(prof.package_dir) / "base" / REL_INF))
    yaml_after = (Path(prof2.package_dir) / "profile.yaml").read_text(encoding="utf-8")
    ck("YAML 註解分隔線仍在、anchors 插在分隔線之前", yaml_after.count("# ------") == yaml_before.count("# ------")
       and yaml_after.index("anchors:") < yaml_after.index("# ------", yaml_after.index("anchors:")))
    again = reanchor.plan(prof2, rec_inf, quiet, project_root=str(new))
    ck("同樣的解法再寫回 -> 已有相同的錨點", not again.ok and "相同的錨點" in again.error)

    ck.section("E. 同一份 profile：新樹、舊樹、更新的樹都套得上")
    for variant, expect_used in (("new", "第 2 組"), ("old", None)):
        t = make_tree(tmp / f"again_{variant}", variant)
        s, logs = run_patchset(prof2, t)
        used = [m for m in logs if "第 2 組" in m]
        ck(f"{variant} 樹：全 GOOD 無衝突", s.overall.failed == 0 and not s.conflicts, statuses(s))
        ck(f"{variant} 樹：{'有' if expect_used else '沒有'}用到第 2 組", bool(used) == bool(expect_used))
    t = make_tree(tmp / "again_newer", "newer")
    res, used = engine_apply(prof2, rule_of(prof2, "Foo.inf"), t / REL_INF)
    ck("newer 樹：Foo.inf 用第 1 組的 base 三方合併", res.status == STATUS_MERGED and "HpForceDebugLib" in read(t / REL_INF), res.status_text)
    res, used = engine_apply(prof2, rule_of(prof2, "Foo.inf"), tmp / "again_new" / REL_INF)
    ck("已套用的新樹 -> 已套用過", res.status == STATUS_ALREADY)
    res, _ = engine_apply(prof2, rule_of(prof2, "Foo.inf"), tmp / "again_new" / REL_INF, reverse=True)
    ck("新樹反向移除 -> 回到新樹原貌", res.status == STATUS_MODIFIED and read(tmp / "again_new" / REL_INF) == read(new / REL_INF).replace("   HpForceDebugLib\n", ""))

    ck.section("F. 重新錨定的邊界")
    ws = tmp / "ws.merged"
    ws.write_text(cur_inf.replace("   PcdLib\n", "   PcdLib   \n"), encoding="utf-8")
    pw = reanchor.plan(prof2, ConflictRecord(target=rec_inf.target, label="Foo.inf", rule_id="mod:0",
                                             current=rec_inf.current, merged=str(ws)), quiet, project_root=str(new))
    ck("只差行尾空白 -> 拒絕並說明", not pw.ok and "空白" in pw.error, pw.error)

    ck.section("G. manifest 自我對齊")
    y = (Path(prof2.package_dir) / "profile.yaml").read_text(encoding="utf-8")
    start = y.index("  - sub_path: '" + REL_INF)
    nxt = y.index("# ------", start)
    (Path(prof2.package_dir) / "profile.yaml").write_text(y[:start] + y[nxt:], encoding="utf-8")
    prof3 = load_mini(tmp)
    ck("刪掉第一條後載入無錯誤", not prof3.load_error, prof3.load_error)
    ck("有對齊說明，含移除紀錄", prof3.base_warnings and any("移除" in n for n in prof3.base_warnings), prof3.base_warnings)
    r = rule_of(prof3, "Foo.c")
    b = prof3.base_snapshot.base_for(r.rule_id)
    ck("位移後 Foo.c（現在 mod:0）仍拿到自己的 base", r.rule_id == "mod:0" and b is not None and b.path.endswith("Foo.c"))
    ck("孤兒 base 抓得到", [p.name for p in prof3.base_snapshot.orphan_base_files()] == ["Foo.inf"])
finally:
    rmtree(tmp)

ck.finish("anchors")
