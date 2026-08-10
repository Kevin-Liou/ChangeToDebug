"""各功能的設定分頁。

每個 page 都實作同一組介面，主視窗不需要知道細節：
    task_key            對應的 Task.key
    is_task_enabled()   使用者是否勾選啟用
    collect_options()   回傳要傳給 Task 的 options dict
    load_settings()/save_settings()
    on_profile_changed(profile)
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QAbstractItemView, QCheckBox, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QPlainTextEdit,
                             QPushButton, QRadioButton, QSpinBox, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from ..core.tasks import MODE_MEMORY, MODE_SINGLE


class HexSpinBox(QSpinBox):
    """以 0xAA 形式顯示的 8-bit 數值輸入框。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0x00, 0xFF)
        self.setDisplayIntegerBase(16)
        self.setPrefix("0x")
        self.setMinimumWidth(96)

    def textFromValue(self, value):
        return f"{value:02X}"


class TaskPage(QWidget):
    """所有分頁的基底：最上方固定一個「啟用此功能」開關。"""

    enabled_changed = pyqtSignal()

    task_key = ""
    task_title = ""
    task_description = ""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(14, 12, 14, 12)
        self._outer.setSpacing(10)

        self.enable_box = QCheckBox(f"啟用「{self.task_title}」")
        self.enable_box.setObjectName("TaskToggle")
        self.enable_box.toggled.connect(self._on_toggle)
        self._outer.addWidget(self.enable_box)

        desc = QLabel(self.task_description)
        desc.setObjectName("Hint")
        desc.setWordWrap(True)
        self._outer.addWidget(desc)

        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 4, 0, 0)
        self.body_layout.setSpacing(8)
        self._outer.addWidget(self.body, 1)

        self.build_body()
        self.body.setEnabled(False)

    # ---- 子類別覆寫 ----
    def build_body(self):
        pass

    def collect_options(self):
        return {}

    def load_settings(self, settings):
        pass

    def save_settings(self, settings):
        pass

    def on_profile_changed(self, profile):
        pass

    def on_debug_flag_changed(self, enabled):
        pass

    # ---- 共用 ----
    def _on_toggle(self, checked):
        self.body.setEnabled(checked)
        self.enabled_changed.emit()

    def is_task_enabled(self):
        return self.enable_box.isChecked()

    def set_task_enabled(self, value):
        self.enable_box.setChecked(bool(value))


# ---------------------------------------------------------------- Patch Set

class PatchSetPage(TaskPage):
    task_key = "patchset"
    task_title = "Debug Patch Set"
    task_description = ("依偵測到的專案世代套用該世代的所有 Debug 修改。"
                        "下表列出設定檔中的每一條規則，可取消勾選不想套用的項目。")

    COL_TARGET = 0
    COL_KIND = 1
    COL_FLAG = 2

    def build_body(self):
        bar = QHBoxLayout()
        self.summary_label = QLabel("尚未載入設定檔")
        self.summary_label.setObjectName("Hint")
        bar.addWidget(self.summary_label, 1)

        self.select_all_btn = QPushButton("全選")
        self.select_none_btn = QPushButton("全不選")
        self.select_all_btn.clicked.connect(lambda: self._set_all(True))
        self.select_none_btn.clicked.connect(lambda: self._set_all(False))
        bar.addWidget(self.select_all_btn)
        bar.addWidget(self.select_none_btn)
        self.body_layout.addLayout(bar)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["修改目標", "來源區塊", "Debug Flag"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(self.COL_TARGET, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_KIND, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(self.COL_FLAG, QHeaderView.ResizeToContents)
        self.table.itemChanged.connect(self._refresh_summary)
        self.body_layout.addWidget(self.table, 1)

        self._profile = None
        self._debug_flag_enabled = False

    # ---- 內容 ----
    def on_profile_changed(self, profile):
        self._profile = profile
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        if profile is None:
            self.table.blockSignals(False)
            self.summary_label.setText("尚未偵測到專案世代，無法列出修改項目")
            return

        rules = profile.all_rules
        self.table.setRowCount(len(rules))
        for row, rule in enumerate(rules):
            target = QTableWidgetItem(rule.target_display)
            target.setFlags(target.flags() | Qt.ItemIsUserCheckable)
            target.setCheckState(Qt.Checked)
            target.setData(Qt.UserRole, rule.rule_id)
            tip = rule.note or rule.label
            if tip:
                target.setToolTip(tip)
            self.table.setItem(row, self.COL_TARGET, target)

            kind = {"platform_pcd_modifications": "PCD 掃描",
                    "new_files": "新增檔案"}.get(rule.source, "指定路徑")
            self.table.setItem(row, self.COL_KIND, QTableWidgetItem(kind))

            flag = "選配 (需勾選)" if rule.option_debug_flag else "必要"
            self.table.setItem(row, self.COL_FLAG, QTableWidgetItem(flag))

        self.table.blockSignals(False)
        self._refresh_summary()

    def on_debug_flag_changed(self, enabled):
        self._debug_flag_enabled = bool(enabled)
        self._refresh_summary()

    def _set_all(self, checked):
        state = Qt.Checked if checked else Qt.Unchecked
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, self.COL_TARGET)
            if item is not None:
                item.setCheckState(state)
        self.table.blockSignals(False)
        self._refresh_summary()

    def _checked_ids(self):
        ids = set()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, self.COL_TARGET)
            if item is not None and item.checkState() == Qt.Checked:
                ids.add(item.data(Qt.UserRole))
        return ids

    def _refresh_summary(self, *_):
        if self._profile is None:
            return
        checked = self._checked_ids()
        rules = {r.rule_id: r for r in self._profile.all_rules}
        applied = sum(1 for rid in checked
                      if self._debug_flag_enabled or not rules[rid].option_debug_flag)
        optional = sum(1 for r in rules.values() if r.option_debug_flag)
        note = "" if self._debug_flag_enabled else f"（其中 {optional} 條選配項目未啟用）"
        self.summary_label.setText(
            f"共 {len(rules)} 條規則，已勾選 {len(checked)} 條，本次將套用 {applied} 條 {note}")

    def collect_options(self):
        return {"enabled_ids": self._checked_ids() if self.table.rowCount() else None}


# ---------------------------------------------------------------- Driver Debug

class DriverDebugPage(TaskPage):
    task_key = "driver"
    task_title = "Driver Debug"
    task_description = ("輸入要開 Debug 的 .c 檔名（一行一個），會把該檔的 DEBUG_WARN / "
                        "DEBUG_INFO 全部改成 DEBUG_ERROR。")

    def build_body(self):
        mode_bar = QHBoxLayout()
        mode_bar.addWidget(QLabel("模式："))
        self.memory_radio = QRadioButton("Memory Debug")
        self.memory_radio.setToolTip("另外會開啟 PcdHpMemoryDebugEnable、改 DxeMemDebugAcpiArea.c，"
                                     "並在對應的 .inf 加入 MemDebugLib")
        self.single_radio = QRadioButton("Single Driver Debug")
        self.single_radio.setToolTip("只把指定 driver 的 DEBUG 訊息升級為 DEBUG_ERROR")
        self.memory_radio.setChecked(True)
        mode_bar.addWidget(self.memory_radio)
        mode_bar.addWidget(self.single_radio)
        mode_bar.addStretch(1)
        self.body_layout.addLayout(mode_bar)

        self.body_layout.addWidget(QLabel("Driver 檔名（一行一個，含副檔名）："))
        self.names_edit = QPlainTextEdit()
        self.names_edit.setPlaceholderText("PlatformDxe.c\nHpUsbPortCfgDxe.c")
        self.names_edit.setMinimumHeight(120)
        self.body_layout.addWidget(self.names_edit, 1)

    def collect_options(self):
        names = [line.strip() for line in self.names_edit.toPlainText().splitlines()]
        return {
            "mode": MODE_MEMORY if self.memory_radio.isChecked() else MODE_SINGLE,
            "names": [n for n in names if n],
        }

    def load_settings(self, settings):
        if settings.get("driver_mode") == MODE_SINGLE:
            self.single_radio.setChecked(True)
        else:
            self.memory_radio.setChecked(True)
        self.names_edit.setPlainText(settings.get("driver_names", ""))

    def save_settings(self, settings):
        settings.set("driver_mode",
                     MODE_MEMORY if self.memory_radio.isChecked() else MODE_SINGLE)
        settings.set("driver_names", self.names_edit.toPlainText())


# ---------------------------------------------------------------- POST Code Marker

class MarkerPage(TaskPage):
    task_key = "marker"
    task_title = "POST Code Marker"
    task_description = ("在指定字串前插入遞增的 _outp(0x80, XX) 打點，"
                        "沒有序列埠 log 時可用 POST Code 判斷卡在哪一行。已插入過的位置會自動略過。")

    def build_body(self):
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("目標字串："))
        self.target_edit = QLineEdit("CpuDeadLoop ();")
        row1.addWidget(self.target_edit, 1)
        self.body_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("起始 POST Code："))
        self.hex_spin = HexSpinBox()
        self.hex_spin.setValue(0xA0)
        row2.addWidget(self.hex_spin)
        row2.addSpacing(18)
        row2.addWidget(QLabel("掃描子目錄："))
        self.scan_edit = QLineEdit()
        self.scan_edit.setPlaceholderText("留空 = 掃描整個專案（相對於根目錄，例如 HpPlatformPkg）")
        row2.addWidget(self.scan_edit, 1)
        self.body_layout.addLayout(row2)

        warn = QLabel("※ 此功能會大量改動 .c 原始碼，建議搭配「備份原始檔案」或先用預覽模式確認範圍。")
        warn.setObjectName("Hint")
        warn.setWordWrap(True)
        self.body_layout.addWidget(warn)
        self.body_layout.addStretch(1)

    def collect_options(self):
        return {
            "target": self.target_edit.text().strip(),
            "start_hex": self.hex_spin.value(),
            "scan_root": self.scan_edit.text().strip(),
        }

    def load_settings(self, settings):
        self.target_edit.setText(settings.get("marker_target", "CpuDeadLoop ();"))
        self.hex_spin.setValue(int(settings.get("marker_start_hex", 0xA0)))

    def save_settings(self, settings):
        settings.set("marker_target", self.target_edit.text().strip())
        settings.set("marker_start_hex", self.hex_spin.value())


#: 註冊順序即分頁顯示順序
PAGE_CLASSES = [PatchSetPage, DriverDebugPage, MarkerPage]
