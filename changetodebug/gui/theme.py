"""佈景主題：集中管理配色與 QSS，切換主題只需換一組色票。

THEMES 依顯示順序排列；每組色票有 label（下拉選單顯示）、kind（light/dark，
下拉選單分組用）與一套固定的色票 key。"light" / "dark" 兩個 key 是舊版就有的
內建主題，設定檔可能仍存著這兩個值，不能改名。

其餘色票取自最多人用的編輯器配色（GitHub、One Dark、Dracula、Nord、Solarized、
Gruvbox、Catppuccin、Tokyo Night、Monokai、Rosé Pine），色碼皆為各主題官方定義；
"chip_bg" 等原主題沒有的角色色，則從同一色系中挑相近的一格。
"""


def _theme(label, kind, **colors):
    colors["label"] = label
    colors["kind"] = kind
    return colors


THEMES = {
    # ---- 內建 ----
    "light": _theme(
        "預設淺色", "light",
        bg="#F1F4F9", surface="#FFFFFF", surface_alt="#F7F9FC", border="#D8E0EA",
        text="#1E2A38", subtext="#64748B",
        accent="#2563EB", accent_hover="#1D4ED8", accent_text="#FFFFFF",
        danger="#DC2626", ok="#15803D", warn="#B45309", error="#B91C1C", step="#2563EB",
        log_bg="#FFFFFF", chip_bg="#E8EFFB", disabled="#9AA6B5",
    ),
    "dark": _theme(
        "預設深色", "dark",
        bg="#151A21", surface="#1E252F", surface_alt="#232B36", border="#333D4B",
        text="#E4EAF2", subtext="#95A3B6",
        accent="#3B82F6", accent_hover="#2563EB", accent_text="#FFFFFF",
        danger="#EF4444", ok="#4ADE80", warn="#FBBF24", error="#F87171", step="#60A5FA",
        log_bg="#12171E", chip_bg="#1E3050", disabled="#5A6673",
    ),
    # ---- 淺色 ----
    "github_light": _theme(
        "GitHub Light", "light",
        bg="#F6F8FA", surface="#FFFFFF", surface_alt="#F6F8FA", border="#D0D7DE",
        text="#1F2328", subtext="#656D76",
        accent="#0969DA", accent_hover="#0550AE", accent_text="#FFFFFF",
        danger="#CF222E", ok="#1A7F37", warn="#9A6700", error="#CF222E", step="#8250DF",
        log_bg="#FFFFFF", chip_bg="#DDF4FF", disabled="#8C959F",
    ),
    "solarized_light": _theme(
        "Solarized Light", "light",
        bg="#EEE8D5", surface="#FDF6E3", surface_alt="#F5EFDC", border="#D3CBB7",
        text="#073642", subtext="#657B83",
        accent="#268BD2", accent_hover="#2075C7", accent_text="#FDF6E3",
        danger="#DC322F", ok="#859900", warn="#B58900", error="#DC322F", step="#6C71C4",
        log_bg="#FDF6E3", chip_bg="#DCE7EE", disabled="#93A1A1",
    ),
    "gruvbox_light": _theme(
        "Gruvbox Light", "light",
        bg="#F2E5BC", surface="#FBF1C7", surface_alt="#EBDBB2", border="#D5C4A1",
        text="#3C3836", subtext="#7C6F64",
        accent="#076678", accent_hover="#427B58", accent_text="#FBF1C7",
        danger="#9D0006", ok="#79740E", warn="#B57614", error="#9D0006", step="#8F3F71",
        log_bg="#FBF1C7", chip_bg="#E2E0C2", disabled="#A89984",
    ),
    "catppuccin_latte": _theme(
        "Catppuccin Latte", "light",
        bg="#E6E9EF", surface="#EFF1F5", surface_alt="#E6E9EF", border="#CCD0DA",
        text="#4C4F69", subtext="#6C6F85",
        accent="#1E66F5", accent_hover="#7287FD", accent_text="#EFF1F5",
        danger="#D20F39", ok="#40A02B", warn="#A86A0A", error="#D20F39", step="#8839EF",  # warn 非官方色：官方 yellow 對比僅 2.3
        log_bg="#EFF1F5", chip_bg="#DCE0E8", disabled="#9CA0B0",
    ),
    # ---- 深色 ----
    "github_dark": _theme(
        "GitHub Dark", "dark",
        bg="#0D1117", surface="#161B22", surface_alt="#1C2128", border="#30363D",
        text="#E6EDF3", subtext="#8B949E",
        accent="#2F81F7", accent_hover="#58A6FF", accent_text="#FFFFFF",
        danger="#F85149", ok="#3FB950", warn="#D29922", error="#F85149", step="#A371F7",
        log_bg="#0D1117", chip_bg="#1B3A5C", disabled="#484F58",
    ),
    "one_dark": _theme(
        "One Dark Pro", "dark",
        bg="#21252B", surface="#282C34", surface_alt="#2C313A", border="#3E4451",
        text="#ABB2BF", subtext="#7F848E",
        accent="#61AFEF", accent_hover="#528BFF", accent_text="#282C34",
        danger="#E06C75", ok="#98C379", warn="#E5C07B", error="#E06C75", step="#C678DD",
        log_bg="#1E2227", chip_bg="#3A4B60", disabled="#4B5263",
    ),
    "dracula": _theme(
        "Dracula", "dark",
        bg="#21222C", surface="#282A36", surface_alt="#343746", border="#44475A",
        text="#F8F8F2", subtext="#8B93B5",
        accent="#BD93F9", accent_hover="#FF79C6", accent_text="#282A36",
        danger="#FF5555", ok="#50FA7B", warn="#F1FA8C", error="#FF5555", step="#8BE9FD",
        log_bg="#1E1F29", chip_bg="#44475A", disabled="#6272A4",
    ),
    "nord": _theme(
        "Nord", "dark",
        bg="#2E3440", surface="#3B4252", surface_alt="#434C5E", border="#4C566A",
        text="#ECEFF4", subtext="#A3AFC2",
        accent="#88C0D0", accent_hover="#81A1C1", accent_text="#2E3440",
        danger="#BF616A", ok="#A3BE8C", warn="#EBCB8B", error="#D98A92", step="#81A1C1",  # error 非官方色：nord11 對比僅 2.5
        log_bg="#272C36", chip_bg="#434C5E", disabled="#616E88",
    ),
    "solarized_dark": _theme(
        "Solarized Dark", "dark",
        bg="#002B36", surface="#073642", surface_alt="#0B3D49", border="#1B4B58",
        text="#EEE8D5", subtext="#93A1A1",
        accent="#268BD2", accent_hover="#2AA198", accent_text="#FDF6E3",
        danger="#DC322F", ok="#859900", warn="#B58900", error="#EF6B69", step="#6C71C4",  # error 非官方色：官方紅對比僅 2.8
        log_bg="#00252E", chip_bg="#0F4A5B", disabled="#586E75",
    ),
    "gruvbox_dark": _theme(
        "Gruvbox Dark", "dark",
        bg="#1D2021", surface="#282828", surface_alt="#32302F", border="#504945",
        text="#EBDBB2", subtext="#A89984",
        accent="#83A598", accent_hover="#8EC07C", accent_text="#1D2021",
        danger="#FB4934", ok="#B8BB26", warn="#FABD2F", error="#FB4934", step="#D3869B",
        log_bg="#1D2021", chip_bg="#3C3836", disabled="#665C54",
    ),
    "catppuccin_mocha": _theme(
        "Catppuccin Mocha", "dark",
        bg="#181825", surface="#1E1E2E", surface_alt="#313244", border="#45475A",
        text="#CDD6F4", subtext="#A6ADC8",
        accent="#89B4FA", accent_hover="#B4BEFE", accent_text="#1E1E2E",
        danger="#F38BA8", ok="#A6E3A1", warn="#F9E2AF", error="#F38BA8", step="#CBA6F7",
        log_bg="#11111B", chip_bg="#313244", disabled="#6C7086",
    ),
    "tokyo_night": _theme(
        "Tokyo Night", "dark",
        bg="#16161E", surface="#1A1B26", surface_alt="#24283B", border="#3B4261",
        text="#C0CAF5", subtext="#7982B4",
        accent="#7AA2F7", accent_hover="#7DCFFF", accent_text="#1A1B26",
        danger="#F7768E", ok="#9ECE6A", warn="#E0AF68", error="#F7768E", step="#BB9AF7",
        log_bg="#16161E", chip_bg="#292E42", disabled="#414868",
    ),
    "monokai": _theme(
        "Monokai", "dark",
        bg="#1E1F1C", surface="#272822", surface_alt="#3E3D32", border="#49483E",
        text="#F8F8F2", subtext="#908F7E",
        accent="#66D9EF", accent_hover="#A6E22E", accent_text="#272822",
        danger="#F92672", ok="#A6E22E", warn="#E6DB74", error="#F92672", step="#AE81FF",
        log_bg="#1E1F1C", chip_bg="#3E3D32", disabled="#75715E",
    ),
    "rose_pine": _theme(
        "Rosé Pine", "dark",
        bg="#191724", surface="#1F1D2E", surface_alt="#26233A", border="#403D52",
        text="#E0DEF4", subtext="#908CAA",
        accent="#C4A7E7", accent_hover="#EBBCBA", accent_text="#191724",
        danger="#EB6F92", ok="#9CCFD8", warn="#F6C177", error="#EB6F92", step="#EBBCBA",
        log_bg="#191724", chip_bg="#403D52", disabled="#6E6A86",
    ),
}

# 舊名稱，保留給仍 import PALETTES 的程式
PALETTES = THEMES

DEFAULT_THEME = "light"

FONT_FAMILY = '"Microsoft JhengHei UI", "Microsoft JhengHei", "Segoe UI", sans-serif'
MONO_FAMILY = '"Cascadia Mono", "Consolas", "Courier New", monospace'


def palette(name):
    """取得色票；設定檔存了不存在的主題名（例如日後移除）時退回預設淺色。"""
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def list_themes():
    """(key, label, kind) 依顯示順序，供下拉選單填入。"""
    return [(k, v["label"], v["kind"]) for k, v in THEMES.items()]


def with_alpha(hex_color, alpha):
    """'#RRGGBB' -> 'rgba(r,g,b,a)'。狀態燈的底色用主題自己的狀態色淡化而來，
    不再寫死某一組淺色主題的 rgba。"""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def build_stylesheet(name):
    c = palette(name)
    return f"""
* {{
    font-family: {FONT_FAMILY};
    font-size: 13px;
}}
QWidget#Root, QWidget#Canvas, QMainWindow, QDialog {{
    background: {c['bg']};
    color: {c['text']};
}}
QScrollArea#MainScroll {{
    background: transparent;
    border: none;
}}
QSplitter {{
    background: {c['bg']};
}}
QWidget {{
    color: {c['text']};
}}

/* ---- 頁首 ---- */
QFrame#Header {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 10px;
}}
QLabel#HeaderTitle {{
    font-size: 19px;
    font-weight: 700;
    color: {c['text']};
}}
QLabel#HeaderSubtitle {{
    color: {c['subtext']};
    font-size: 12px;
}}
QLabel#VersionChip {{
    background: {c['chip_bg']};
    color: {c['accent']};
    border-radius: 9px;
    padding: 2px 10px;
    font-weight: 600;
}}

/* ---- 區塊卡片 ---- */
QGroupBox {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px 12px 12px 12px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: {c['accent']};
}}

QLabel#Hint, QLabel#Muted {{
    color: {c['subtext']};
    font-size: 12px;
}}
QLabel#StatusChip {{
    border-radius: 9px;
    padding: 3px 10px;
    font-weight: 600;
    background: {c['chip_bg']};
    color: {c['accent']};
}}

/* ---- 輸入元件 ---- */
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QTextEdit {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 5px 8px;
    selection-background-color: {c['accent']};
    selection-color: {c['accent_text']};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QPlainTextEdit:focus, QTextEdit:focus {{
    border: 1px solid {c['accent']};
}}
QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QPlainTextEdit:disabled {{
    color: {c['disabled']};
    background: {c['surface_alt']};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    selection-background-color: {c['accent']};
    selection-color: {c['accent_text']};
    outline: none;
}}

/* ---- 按鈕 ---- */
QPushButton {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 6px 14px;
    color: {c['text']};
}}
QPushButton:hover {{
    border-color: {c['accent']};
    color: {c['accent']};
}}
QPushButton:pressed {{
    background: {c['surface_alt']};
}}
QPushButton:disabled {{
    color: {c['disabled']};
    border-color: {c['border']};
}}
QPushButton#Primary {{
    background: {c['accent']};
    border: 1px solid {c['accent']};
    color: {c['accent_text']};
    font-weight: 700;
    padding: 9px 26px;
    font-size: 14px;
}}
QPushButton#Primary:hover {{
    background: {c['accent_hover']};
    border-color: {c['accent_hover']};
    color: {c['accent_text']};
}}
QPushButton#Primary:disabled {{
    background: {c['disabled']};
    border-color: {c['disabled']};
    color: {c['surface']};
}}
QPushButton#Danger {{
    color: {c['danger']};
    border-color: {c['danger']};
    font-weight: 600;
    padding: 9px 18px;
}}
QPushButton#Danger:disabled {{
    color: {c['disabled']};
    border-color: {c['border']};
}}

/* ---- 勾選 / 單選 ---- */
QCheckBox, QRadioButton {{
    spacing: 7px;
    padding: 2px;
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {c['border']};
    background: {c['surface']};
}}
QCheckBox::indicator {{ border-radius: 4px; }}
QRadioButton::indicator {{ border-radius: 8px; }}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background: {c['accent']};
    border-color: {c['accent']};
}}
QCheckBox#TaskToggle {{
    font-weight: 700;
    color: {c['accent']};
}}

/* ---- 分頁 ---- */
QTabWidget::pane {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 10px;
    top: -1px;
}}
QTabBar::tab {{
    background: transparent;
    color: {c['subtext']};
    border: 1px solid transparent;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 7px 16px;
    margin-right: 4px;
}}
QTabBar::tab:selected {{
    background: {c['surface']};
    color: {c['accent']};
    border: 1px solid {c['border']};
    border-bottom-color: {c['surface']};
    font-weight: 700;
}}
QTabBar::tab:hover:!selected {{
    color: {c['accent']};
}}

/* ---- 表格 ---- */
QTableWidget {{
    background: {c['surface']};
    alternate-background-color: {c['surface_alt']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    gridline-color: {c['border']};
    selection-background-color: {c['chip_bg']};
    selection-color: {c['text']};
}}
/* 欄位縮短後，最後一欄右邊會露出 header 容器本身；
   只設 ::section 的話那塊空白會落回 Qt 預設白底，深色主題下非常刺眼。 */
QHeaderView {{
    background: {c['surface_alt']};
    border: none;
}}
QTableCornerButton::section {{
    background: {c['surface_alt']};
    border: none;
    border-bottom: 1px solid {c['border']};
}}
QHeaderView::section {{
    background: {c['surface_alt']};
    color: {c['subtext']};
    border: none;
    border-bottom: 1px solid {c['border']};
    padding: 6px 8px;
    font-weight: 600;
}}
/* 欄位之間畫一條分隔線，讓「可以拖曳調整寬度」看得出來 */
QHeaderView::section:horizontal {{
    border-right: 1px solid {c['border']};
}}
QHeaderView::section:horizontal:hover {{
    background: {c['chip_bg']};
    color: {c['text']};
}}

/* ---- 清單（專案勾選等） ---- */
QListWidget {{
    background: {c['surface']};
    alternate-background-color: {c['surface_alt']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    color: {c['text']};
    padding: 2px;
    outline: none;
}}
QListWidget::item {{
    padding: 3px 4px;
    border-radius: 4px;
    color: {c['text']};
}}
QListWidget::item:hover {{
    background: {c['surface_alt']};
}}
QListWidget::item:selected {{
    background: {c['chip_bg']};
    color: {c['text']};
}}
QListWidget:disabled {{
    background: {c['surface_alt']};
    color: {c['disabled']};
}}
QListWidget::item:disabled {{
    color: {c['disabled']};
}}

/* ---- 進度條 ---- */
QProgressBar {{
    background: {c['surface_alt']};
    border: 1px solid {c['border']};
    border-radius: 7px;
    height: 12px;
}}
QProgressBar::chunk {{
    background: {c['accent']};
    border-radius: 6px;
}}

/* ---- Log ---- */
QTextEdit#LogView {{
    background: {c['log_bg']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    font-family: {MONO_FAMILY};
    font-size: 12px;
}}

/* ---- 捲軸 ---- */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {c['border']};
    border-radius: 5px;
    min-height: 26px;
}}
QScrollBar::handle:vertical:hover {{ background: {c['subtext']}; }}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {c['border']};
    border-radius: 5px;
    min-width: 26px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

QSplitter::handle {{
    background: transparent;
    height: 8px;
}}
QMenuBar, QMenu {{
    background: {c['surface']};
    color: {c['text']};
}}
QMenu::item:selected {{
    background: {c['accent']};
    color: {c['accent_text']};
}}
"""


def log_colors(name):
    c = palette(name)
    return {
        "debug": c["subtext"],
        "info": c["text"],
        "ok": c["ok"],
        "warn": c["warn"],
        "error": c["error"],
        "step": c["step"],
    }
