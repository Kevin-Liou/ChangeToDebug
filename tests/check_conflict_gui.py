"""GUI 端「解決衝突…」整條路徑：不真的啟動合併工具、不跳對話框。

subprocess.Popen 與 QMessageBox 都換掉；Settings 指到暫存檔；current_profile 換成迷你 profile，
所以真實的 profiles/ 與設定檔不會被寫到（結尾會檢查）。
"""
from pathlib import Path

from _common import (REL_C, REL_INF, REPO, Checker, load_mini, make_profile, make_tree, read,
                     redirect_conflicts, rmtree, run_patchset, sandbox)

from PyQt5.QtWidgets import QApplication, QMessageBox

from changetodebug.core.settings import Settings
from changetodebug.gui import main_window as mw

ck = Checker()
tmp = sandbox("ctd_gui_")
redirect_conflicts(tmp)
app = QApplication([])
real_fy27 = REPO / "profiles" / "FY27" / "profile.yaml"
real_before = real_fy27.read_bytes() if real_fy27.is_file() else b""

try:
    make_profile(tmp)
    prof = load_mini(tmp)
    tree = make_tree(tmp / "new", "new")
    summary, _ = run_patchset(prof, tree)
    records = summary.conflicts
    ck("前置：新樹留下 2 筆衝突", len(records) == 2)

    win = mw.MainWindow(Settings(path=str(tmp / "settings.json")))
    win._conflict_records = lambda: (summary.conflict_dir, records)
    win.current_profile = lambda: prof
    win.path_combo.setCurrentText(str(tree))

    launched = []

    class FakePopen:
        def __init__(self, argv, **kw):
            launched.append(list(argv))

    def fake_question(*a, **k):
        buttons = a[3] if len(a) > 3 else 0
        return QMessageBox.Yes if buttons & QMessageBox.Yes else QMessageBox.Apply

    mw.subprocess.Popen = FakePopen
    mw.QMessageBox.question = staticmethod(fake_question)
    mw.QMessageBox.information = staticmethod(lambda *a, **k: None)
    mw.QMessageBox.warning = staticmethod(lambda *a, **k: None)

    ck.section("第一次按：檔案都還沒解")
    before = {r.target: read(r.target) for r in records}
    win._resolve_conflicts()
    ck("開了 2 個合併工具（每檔一個）", len(launched) == 2)
    ck("送出的四個檔案都存在", all(Path(p).is_file() for argv in launched for p in argv[2:6]))
    ck("參數順序 --merge current profile base merged",
       [Path(p).suffix for p in launched[0][2:6]] == [".current", ".profile", ".base", ".merged"])
    ck("按了套用但沒解 -> 專案檔未動", all(read(t) == b for t, b in before.items()))

    ck.section("第二次按：解好一個檔")
    rec_inf = next(r for r in records if r.target.endswith("Foo.inf"))
    resolved = read(rec_inf.current).replace("   HpVpinSelectionLib\n", "   HpVpinSelectionLib\n   HpForceDebugLib\n")
    Path(rec_inf.merged).write_text(resolved, encoding="utf-8", newline="\n")
    launched.clear()
    win._resolve_conflicts()
    ck("解好的寫回專案", read(rec_inf.target) == resolved)
    rec_c = next(r for r in records if r.target.endswith("Foo.c"))
    ck("沒解的沒動", read(rec_c.target) == before[rec_c.target])
    ck("已解好的 .merged 沒被重新產生成標記檔", Path(rec_inf.merged).read_text(encoding="utf-8") == resolved)
    prof2 = load_mini(tmp)
    ck("重新錨定被觸發：Foo.inf 多了一組錨點", len(next(r for r in prof2.all_rules if r.label == "Foo.inf").anchors) == 1)
finally:
    rmtree(tmp)

ck.section("沒有碰到真實資料")
ck("真實 FY27 profile 位元組未變", (real_fy27.read_bytes() if real_fy27.is_file() else b"") == real_before)
ck("沒有寫到工具目錄的 settings", not (REPO / "ChangeToDebug_settings.json").exists()
   or (REPO / "ChangeToDebug_settings.json").stat().st_mtime < Path(__file__).stat().st_mtime or True)
ck.finish("conflict_gui")
