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
                             QHeaderView, QLabel, QLineEdit, QListWidget,
                             QListWidgetItem, QPlainTextEdit, QPushButton,
                             QRadioButton, QSpinBox, QSplitter, QTableWidget,
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

    def on_base_path_changed(self, base):
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
        # 三個欄位都設成 Interactive 才能用滑鼠拖曳分隔線調整寬度；
        # Stretch / ResizeToContents 由 Qt 全權控制，使用者拖不動。
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        # 最後一欄自動吸收剩餘寬度，右邊不會留下一片空白。
        # 前兩欄的邊界照樣可以拖，寬度仍由使用者決定。
        header.setStretchLastSection(True)
        header.setMinimumSectionSize(60)
        header.setSectionsMovable(True)         # 欄位順序也可以拖著換
        header.sectionResized.connect(self._on_section_resized)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setWordWrap(False)
        self.table.itemChanged.connect(self._refresh_summary)

        # 左邊選專案、右邊選規則。PCD 掃描型規則會套用到每個專案的同名檔，
        # 不選的話就是全部一起改——多專案共用一棵 source 時常常只想改其中一兩個。
        split = QSplitter(Qt.Horizontal)
        split.setChildrenCollapsible(False)

        project_panel = QWidget()
        project_box = QVBoxLayout(project_panel)
        project_box.setContentsMargins(0, 0, 0, 0)
        project_box.setSpacing(4)
        self.project_label = QLabel("套用專案")
        self.project_label.setObjectName("Hint")
        project_box.addWidget(self.project_label)

        self.project_list = QListWidget()
        self.project_list.setAlternatingRowColors(True)
        self.project_list.setMinimumWidth(120)
        self.project_list.setToolTip(
            "只有 PCD 掃描型規則（例如 Z*PkgConfig.dsc）會受此影響。\n"
            "以 sub_path 指定路徑的規則與新增檔案不分專案，一律套用。")
        self.project_list.itemChanged.connect(self._refresh_summary)
        project_box.addWidget(self.project_list, 1)

        project_btns = QHBoxLayout()
        project_btns.setSpacing(4)
        all_btn = QPushButton("全選")
        none_btn = QPushButton("全不選")
        all_btn.clicked.connect(lambda: self._set_all_projects(True))
        none_btn.clicked.connect(lambda: self._set_all_projects(False))
        project_btns.addWidget(all_btn)
        project_btns.addWidget(none_btn)
        project_box.addLayout(project_btns)

        split.addWidget(project_panel)
        split.addWidget(self.table)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setSizes([200, 720])
        # 拖動分隔器只會改變表格寬度，不會觸發本頁的 resizeEvent，要另外接
        split.splitterMoved.connect(lambda *_: self._autosize_columns())
        self.body_layout.addWidget(split, 1)

        self._profile = None
        self._base_path = ""
        self._debug_flag_enabled = False
        self._columns_sized = False     # 使用者是否已自行調整欄寬
        self._sizing = False            # 程式正在配寬（用來分辨不是使用者拖的）

    # ---- 內容 ----
    def on_profile_changed(self, profile):
        self._profile = profile
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        if profile is None:
            self.table.blockSignals(False)
            self.summary_label.setText("尚未偵測到專案世代，無法列出修改項目")
            self._reload_projects()
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
        self._autosize_columns()
        self._reload_projects()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 版面配置完成、真正拿得到寬度之後才算得出合理的初始欄寬
        self._autosize_columns()

    def _on_section_resized(self, index, *_):
        """使用者親手拖過欄寬之後就不再自動配寬，尊重他的設定。

        最後一欄是自動吸收剩餘寬度的，視窗一縮放它就會變寬變窄——那不是使用者調的，
        不能拿來當「使用者已接手」的判斷依據。
        """
        header = self.table.horizontalHeader()
        if self._sizing or header.visualIndex(index) == header.count() - 1:
            return
        self._columns_sized = True

    def _content_width(self, column, minimum):
        """取內容與標題兩者較寬的那個，再留一點邊。"""
        header = self.table.horizontalHeader().sectionSizeHint(column)
        return max(header, self.table.sizeHintForColumn(column), minimum) + 16

    def _autosize_columns(self):
        """配一組合理的初始寬度，直到使用者自己拖過為止。

        最後一欄由 stretchLastSection 自動吸收，所以只需要算前兩欄——
        並把該留給最後一欄的寬度先從「修改目標」扣掉，它才不會被撐得太寬。
        """
        if self._columns_sized or not self.table.rowCount():
            return
        viewport = self.table.viewport().width()
        if viewport < 200:
            return      # 版面還沒配置完，等下一次 resizeEvent 再算

        self._sizing = True
        try:
            kind = self._content_width(self.COL_KIND, 74)
            flag = self._content_width(self.COL_FLAG, 94)
            self.table.setColumnWidth(self.COL_KIND, kind)
            # 剩下的寬度給「修改目標」，它最長也最需要看清楚
            self.table.setColumnWidth(self.COL_TARGET,
                                      max(viewport - kind - flag - 4, 260))
        finally:
            self._sizing = False

    def on_base_path_changed(self, base):
        self._base_path = base or ""
        self._reload_projects()

    def _reload_projects(self):
        """依目前的專案路徑與世代重新列出可選專案，盡量保留使用者原本的勾選。"""
        from ..core.tasks.patchset import list_projects

        previous = {self.project_list.item(i).text(): self.project_list.item(i).checkState()
                    for i in range(self.project_list.count())}
        self.project_list.blockSignals(True)
        self.project_list.clear()

        names = []
        if self._profile is not None and self._base_path:
            try:
                names = list_projects(self._base_path, self._profile.pcd_scan_roots)
            except Exception:
                names = []

        for name in names:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(previous.get(name, Qt.Checked))
            self.project_list.addItem(item)

        self.project_list.blockSignals(False)
        self.project_list.setEnabled(bool(names))
        if names:
            self.project_label.setText(f"套用專案（{len(names)} 個）")
        elif self._base_path:
            self.project_label.setText("套用專案（掃描不到專案）")
        else:
            self.project_label.setText("套用專案（尚未選擇路徑）")
        self._refresh_summary()

    def _set_all_projects(self, checked):
        state = Qt.Checked if checked else Qt.Unchecked
        self.project_list.blockSignals(True)
        for row in range(self.project_list.count()):
            self.project_list.item(row).setCheckState(state)
        self.project_list.blockSignals(False)
        self._refresh_summary()

    def _checked_projects(self):
        """回傳勾選的專案名稱；清單是空的（掃不到專案）時回 None 代表不過濾。"""
        if self.project_list.count() == 0:
            return None
        return [self.project_list.item(i).text()
                for i in range(self.project_list.count())
                if self.project_list.item(i).checkState() == Qt.Checked]

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
        text = f"共 {len(rules)} 條規則，已勾選 {len(checked)} 條，本次將套用 {applied} 條 {note}"

        projects = self._checked_projects()
        if projects is not None:
            total = self.project_list.count()
            if len(projects) < total:
                text += f"　｜　專案 {len(projects)}/{total}"
                if not projects:
                    text += "（未選任何專案，PCD 掃描型規則不會套用）"
        self.summary_label.setText(text)

    def collect_options(self):
        return {
            "enabled_ids": self._checked_ids() if self.table.rowCount() else None,
            "projects": self._checked_projects(),
        }


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
