"""佈景主題：集中管理配色與 QSS，切換淺色/深色只需換一組色票。"""

PALETTES = {
    "light": {
        "bg": "#F1F4F9",
        "surface": "#FFFFFF",
        "surface_alt": "#F7F9FC",
        "border": "#D8E0EA",
        "text": "#1E2A38",
        "subtext": "#64748B",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "accent_text": "#FFFFFF",
        "danger": "#DC2626",
        "ok": "#15803D",
        "warn": "#B45309",
        "error": "#B91C1C",
        "step": "#2563EB",
        "log_bg": "#FFFFFF",
        "chip_bg": "#E8EFFB",
        "disabled": "#9AA6B5",
    },
    "dark": {
        "bg": "#151A21",
        "surface": "#1E252F",
        "surface_alt": "#232B36",
        "border": "#333D4B",
        "text": "#E4EAF2",
        "subtext": "#95A3B6",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "accent_text": "#FFFFFF",
        "danger": "#EF4444",
        "ok": "#4ADE80",
        "warn": "#FBBF24",
        "error": "#F87171",
        "step": "#60A5FA",
        "log_bg": "#12171E",
        "chip_bg": "#1E3050",
        "disabled": "#5A6673",
    },
}

FONT_FAMILY = '"Microsoft JhengHei UI", "Microsoft JhengHei", "Segoe UI", sans-serif'
MONO_FAMILY = '"Cascadia Mono", "Consolas", "Courier New", monospace'


def palette(name):
    return PALETTES.get(name, PALETTES["light"])


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
QHeaderView::section {{
    background: {c['surface_alt']};
    color: {c['subtext']};
    border: none;
    border-bottom: 1px solid {c['border']};
    padding: 6px 8px;
    font-weight: 600;
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
