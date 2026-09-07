"""主題下拉、色票完整性、對比度、下拉／微調箭頭有沒有畫出來。"""
import json
from pathlib import Path

from _common import Checker, rmtree, sandbox

from PyQt5.QtWidgets import QApplication, QComboBox, QHBoxLayout, QSpinBox, QWidget
from PyQt5.QtGui import QColor

from changetodebug.core.settings import Settings
from changetodebug.gui import theme
from changetodebug.gui.main_window import MainWindow

ck = Checker()
tmp = sandbox("ctd_theme_")
app = QApplication([])


def lum(h):
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


try:
    ck.section("色票")
    keys = set(theme.THEMES["light"]) - {"label", "kind"}
    ck("至少 10 組主題", len(theme.THEMES) >= 10, len(theme.THEMES))
    ck("每組色票 key 齊全、kind 合法", all(keys <= set(v) and v["kind"] in ("light", "dark") for v in theme.THEMES.values()))
    low = [k for k, c in theme.THEMES.items()
           if ratio(c["text"], c["surface"]) < 4.5 or ratio(c["accent_text"], c["accent"]) < 3 or ratio(c["text"], c["log_bg"]) < 4.5]
    ck("text / accent_text / log 對比度足夠", low == [], low)

    ck.section("主視窗切換")
    sp = tmp / "s.json"
    win = MainWindow(Settings(path=str(sp)))
    combo = win.theme_combo
    labels = [combo.itemText(i) for i in range(combo.count()) if combo.itemData(i)]
    ck("下拉項目數 = 主題數", len(labels) == len(theme.THEMES))
    for i in range(combo.count()):
        key = combo.itemData(i)
        if not key or key == win.theme_name:
            continue
        combo.setCurrentIndex(i)
        if win.theme_name != key or theme.palette(key)["bg"] not in win.styleSheet() \
                or json.load(open(sp, encoding="utf-8"))["theme"] != key:
            ck(f"切換 {key}", False)
    ck("逐一切換：樣式表與設定檔同步", True)
    combo.setCurrentIndex(combo.findData("dracula"))
    win._set_chip("ok", "x")
    ck("狀態燈底色跟主題色", "rgba(80,250,123,0.15)" in win.status_chip.styleSheet())
    s2 = Settings(path=str(sp))
    s2.set("theme", "no_such")
    ck("未知主題退回 light", MainWindow(s2).theme_name == "light")
    win._on_theme_selected(next(i for i in range(combo.count()) if not combo.itemData(i)))
    ck("分隔線不觸發切換", win.theme_name == "dracula")

    ck.section("箭頭圖示（每個主題都要畫得出）")

    def arrow_pixels(w, sub, surface):
        img = w.grab().toImage()
        g = sub.geometry()
        ref = QColor(surface)
        n = 0
        for x in range(g.right() - 21, g.right() - 2):
            for y in range(g.top() + 4, g.bottom() - 3):
                px = img.pixelColor(x, y)
                if abs(px.red() - ref.red()) + abs(px.green() - ref.green()) + abs(px.blue() - ref.blue()) > 60:
                    n += 1
        return n

    missing = []
    for name, c in theme.THEMES.items():
        w = QWidget()
        w.setStyleSheet(theme.build_stylesheet(name))
        lay = QHBoxLayout(w)
        a = QComboBox(); a.setEditable(True); a.addItems(["x"]); a.setFixedWidth(200)
        s = QSpinBox(); s.setFixedWidth(90)
        lay.addWidget(a); lay.addWidget(s)
        w.resize(400, 48); w.show(); app.processEvents()
        if arrow_pixels(w, a, c["surface"]) == 0 or arrow_pixels(w, s, c["surface"]) == 0:
            missing.append(name)
        w.hide()
    ck("下拉與微調框在所有主題都有箭頭", missing == [], missing)
    orig = theme._arrow_image
    theme._ARROW_CACHE.clear()
    theme._arrow_image = lambda *a, **k: ""
    try:
        ck("產圖失敗時退回無箭頭樣式、不丟例外", "down-arrow" not in theme.build_stylesheet("light"))
    finally:
        theme._arrow_image = orig
        theme._ARROW_CACHE.clear()
finally:
    rmtree(tmp)

ck.finish("gui_theme")
