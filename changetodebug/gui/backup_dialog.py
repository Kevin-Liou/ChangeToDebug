"""「清理備份」對話框：列出各次執行留下的備份，讓使用者挑選要刪除的。

刪除不可逆，所以預設一項都不勾，且會再問一次。
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAbstractItemView, QDialog, QHBoxLayout, QHeaderView,
                             QLabel, QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout)

from ..appinfo import APP_NAME
from ..core.backups import human_size, remove

COL_STAMP, COL_WHEN, COL_COUNT, COL_SIZE = range(4)


class BackupDialog(QDialog):
    def __init__(self, groups, logger, parent=None, stylesheet="", preselect=""):
        super().__init__(parent)
        self.setWindowTitle("清理備份")
        self.setMinimumSize(620, 400)
        if stylesheet:
            self.setStyleSheet(stylesheet)

        self.groups = groups
        self.logger = logger
        self.deleted = 0
        self._build_ui()
        self._fill(preselect)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(10)

        intro = QLabel(
            "修補前會把原檔複製成 `原檔名.bak.<執行時間戳>`，同一次執行共用一個時間戳。\n"
            "這些備份不會自動消失——「移除 Change」把修改還原之後，樹上剩下的就只有它們，\n"
            "卻仍然掛在 git status 上。確認不需要之後可以在這裡刪掉。")
        intro.setObjectName("Hint")
        intro.setWordWrap(True)
        outer.addWidget(intro)

        self.summary = QLabel("")
        self.summary.setObjectName("Hint")
        outer.addWidget(self.summary)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["執行時間戳", "時間", "檔案數", "大小"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        self.table.itemChanged.connect(lambda *_: self._refresh())
        outer.addWidget(self.table, 1)

        bar = QHBoxLayout()
        all_btn = QPushButton("全選")
        none_btn = QPushButton("全不選")
        all_btn.clicked.connect(lambda: self._set_all(True))
        none_btn.clicked.connect(lambda: self._set_all(False))
        bar.addWidget(all_btn)
        bar.addWidget(none_btn)
        bar.addStretch(1)

        self.delete_btn = QPushButton("刪除勾選的備份")
        self.delete_btn.setObjectName("Danger")
        self.delete_btn.clicked.connect(self._delete)
        bar.addWidget(self.delete_btn)

        close_btn = QPushButton("關閉")
        close_btn.clicked.connect(self.reject)
        bar.addWidget(close_btn)
        outer.addLayout(bar)

    def _fill(self, preselect):
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.groups))
        for row, group in enumerate(self.groups):
            stamp = QTableWidgetItem(group.stamp)
            stamp.setFlags(stamp.flags() | Qt.ItemIsUserCheckable)
            stamp.setCheckState(Qt.Checked if group.stamp == preselect else Qt.Unchecked)
            self.table.setItem(row, COL_STAMP, stamp)
            self.table.setItem(row, COL_WHEN, QTableWidgetItem(group.when))
            self.table.setItem(row, COL_COUNT, QTableWidgetItem(str(group.count)))
            self.table.setItem(row, COL_SIZE, QTableWidgetItem(human_size(group.size)))
        self.table.blockSignals(False)
        self.table.resizeColumnsToContents()
        self._refresh()

    def _checked(self):
        out = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, COL_STAMP)
            if item is not None and item.checkState() == Qt.Checked:
                out.append(self.groups[row])
        return out

    def _set_all(self, checked):
        state = Qt.Checked if checked else Qt.Unchecked
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            self.table.item(row, COL_STAMP).setCheckState(state)
        self.table.blockSignals(False)
        self._refresh()

    def _refresh(self):
        chosen = self._checked()
        total = sum(g.count for g in self.groups)
        size = sum(g.size for g in self.groups)
        picked = sum(g.count for g in chosen)
        picked_size = sum(g.size for g in chosen)
        self.summary.setText(
            f"共 {len(self.groups)} 次執行、{total} 個備份檔（{human_size(size)}）"
            f"　|　已勾選 {len(chosen)} 次、{picked} 個檔案（{human_size(picked_size)}）")
        self.delete_btn.setEnabled(bool(chosen))

    def _delete(self):
        chosen = self._checked()
        if not chosen:
            return
        paths = [p for g in chosen for p in g.paths]
        stamps = "\n".join(f"　• {g.stamp}（{g.when}）　{g.count} 個檔案"
                           for g in chosen)
        confirm = QMessageBox.question(
            self, APP_NAME,
            f"確定要刪除以下 {len(chosen)} 次執行的備份嗎？\n\n{stamps}\n\n"
            f"合計 {len(paths)} 個檔案。**刪除後無法復原**，\n"
            "請先確認這些修改已經驗證過、或已經提交進版本控制。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return

        deleted, failed = remove(paths, self.logger)
        self.deleted += deleted
        message = f"已刪除 {deleted} 個備份檔。"
        if failed:
            message += f"\n\n{len(failed)} 個未刪除：\n" + "\n".join(
                f"　• {p}：{why}" for p, why in failed[:8])
        QMessageBox.information(self, APP_NAME, message)

        self.groups = [g for g in self.groups if g not in chosen or failed]
        if not self.groups:
            self.accept()
        else:
            self._fill("")
