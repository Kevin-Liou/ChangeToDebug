"""「盤點命中數」對話框：列出每條規則在實際 source 中會命中幾處，並可寫回 expect_count。"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAbstractItemView, QDialog, QHBoxLayout, QHeaderView,
                             QLabel, QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout)

from ..appinfo import APP_NAME
from ..core import reanchor

COL_RULE, COL_TARGET, COL_FILES, COL_STATUS, COL_NOW, COL_SUGGEST = range(6)


class AuditDialog(QDialog):
    """盤點結果與 expect_count 寫入。勾選欄只在有建議值時可勾。"""

    def __init__(self, profile, results, logger, parent=None, stylesheet=""):
        super().__init__(parent)
        self.setWindowTitle("命中數盤點")
        self.setMinimumSize(980, 560)
        if stylesheet:
            self.setStyleSheet(stylesheet)

        self.profile = profile
        self.results = results
        self.logger = logger
        self.written = False
        self._build_ui()
        self._fill()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(10)

        intro = QLabel(
            "old_code 只保證在「產生 profile 當下的那份 source」中唯一。上游後來新增相似區塊時，"
            "同一條規則可能命中多處，而工具是整檔取代所有出現處——會安靜地把好幾個地方一起改掉。\n"
            "勾選要寫入 expect_count 的規則：寫入後，命中數與宣告不符就會報錯且不寫入檔案。")
        intro.setObjectName("Hint")
        intro.setWordWrap(True)
        outer.addWidget(intro)

        self.summary = QLabel("")
        self.summary.setObjectName("Hint")
        outer.addWidget(self.summary)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["規則", "目標", "檔案數", "命中狀況", "目前", "建議寫入"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 全部 Interactive，使用者才能拖曳分隔線調整欄寬
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(60)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setWordWrap(False)
        outer.addWidget(self.table, 1)

        bar = QHBoxLayout()
        all_btn = QPushButton("全選可寫入")
        none_btn = QPushButton("全不選")
        all_btn.clicked.connect(lambda: self._set_all(True))
        none_btn.clicked.connect(lambda: self._set_all(False))
        bar.addWidget(all_btn)
        bar.addWidget(none_btn)
        bar.addStretch(1)

        self.write_btn = QPushButton("寫入 expect_count")
        self.write_btn.setObjectName("Primary")
        self.write_btn.clicked.connect(self._write)
        bar.addWidget(self.write_btn)

        close_btn = QPushButton("關閉")
        close_btn.clicked.connect(self.reject)
        bar.addWidget(close_btn)
        outer.addLayout(bar)

    def _fill(self):
        self.table.setRowCount(len(self.results))
        writable = flagged = 0

        for row, item in enumerate(self.results):
            rule_cell = QTableWidgetItem(item.rule_id)
            rule_cell.setData(Qt.UserRole, row)
            self.table.setItem(row, COL_RULE, rule_cell)

            target = QTableWidgetItem(item.target)
            target.setToolTip(item.label)
            self.table.setItem(row, COL_TARGET, target)

            self.table.setItem(row, COL_FILES, QTableWidgetItem(str(item.files)))

            status = QTableWidgetItem(item.status)
            if item.flagged:
                status.setToolTip("命中多處或各檔案不一致，請確認是否為預期行為")
                flagged += 1
            self.table.setItem(row, COL_STATUS, status)

            self.table.setItem(row, COL_NOW,
                               QTableWidgetItem(str(item.current) if item.current else "—"))

            suggestion = item.suggestion
            cell = QTableWidgetItem(str(suggestion) if suggestion else "—")
            cell.setFlags(cell.flags() | Qt.ItemIsUserCheckable)
            # 已經宣告過同樣的值就沒必要重寫
            can_write = bool(suggestion) and suggestion != item.current
            cell.setCheckState(Qt.Checked if can_write else Qt.Unchecked)
            if not can_write:
                cell.setFlags(cell.flags() & ~Qt.ItemIsUserCheckable & ~Qt.ItemIsEnabled)
            else:
                writable += 1
            self.table.setItem(row, COL_SUGGEST, cell)

        self.summary.setText(
            f"共 {len(self.results)} 條規則　|　可寫入 expect_count {writable} 條"
            f"　|　需要確認 {flagged} 條（命中多處或各檔案不一致）")
        self.write_btn.setEnabled(writable > 0)
        self._autosize()

    def showEvent(self, event):
        super().showEvent(event)
        self._autosize()    # 對話框顯示後才拿得到正確的可視寬度

    def _autosize(self):
        """給一組合理的初始寬度，之後由使用者自行拖曳。"""
        if not self.table.rowCount():
            return
        self.table.resizeColumnsToContents()
        for column, minimum in ((COL_RULE, 80), (COL_FILES, 70), (COL_STATUS, 220),
                                (COL_NOW, 70), (COL_SUGGEST, 90)):
            self.table.setColumnWidth(column,
                                      max(self.table.columnWidth(column) + 14, minimum))
        used = sum(self.table.columnWidth(c)
                   for c in (COL_RULE, COL_FILES, COL_STATUS, COL_NOW, COL_SUGGEST))
        self.table.setColumnWidth(COL_TARGET,
                                  max(self.table.viewport().width() - used - 8, 240))

    def _set_all(self, checked):
        state = Qt.Checked if checked else Qt.Unchecked
        for row in range(self.table.rowCount()):
            cell = self.table.item(row, COL_SUGGEST)
            if cell is not None and cell.flags() & Qt.ItemIsUserCheckable:
                cell.setCheckState(state)

    def _selected_updates(self):
        updates = []
        for row in range(self.table.rowCount()):
            cell = self.table.item(row, COL_SUGGEST)
            if cell is None or cell.checkState() != Qt.Checked:
                continue
            item = self.results[row]
            if item.suggestion:
                updates.append((item.section, item.index, "expect_count", item.suggestion))
        return updates

    def _write(self):
        updates = self._selected_updates()
        if not updates:
            QMessageBox.information(self, APP_NAME, "沒有勾選任何要寫入的規則。")
            return

        confirm = QMessageBox.question(
            self, APP_NAME,
            f"要把 {len(updates)} 條規則的 expect_count 寫進 {self.profile.title} 嗎？\n\n"
            "寫入後，命中數與宣告不符時該規則會報錯且不寫入檔案。\n"
            "會先備份 profile.yaml，改完立即讀回驗證，驗證不過就整個放棄。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if confirm != QMessageBox.Yes:
            return

        ok, message = reanchor.apply_fields(self.profile, updates, self.logger)
        if ok:
            self.written = True
            QMessageBox.information(self, APP_NAME,
                                    f"{message}\n\n舊版本已備份（profile.yaml.bak.<時間戳>）。")
            self.accept()
        else:
            QMessageBox.warning(self, APP_NAME, f"未寫入：{message}")
