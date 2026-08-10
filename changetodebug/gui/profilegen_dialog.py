"""「從 ORG / MOD 產生 Profile」對話框。"""

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QFileDialog,
                             QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QMessageBox, QPlainTextEdit,
                             QPushButton, QSpinBox, QSplitter, QVBoxLayout,
                             QWidget)

from ..appinfo import APP_NAME, user_profile_dir
from ..core.logbus import Logger
from ..core.profilegen import GenOptions, generate, roundtrip_check, suggest_options


class ProfileGenDialog(QDialog):
    """把一份 code change 的 ORG/MOD 轉成 profile YAML。"""

    def __init__(self, parent=None, stylesheet=""):
        super().__init__(parent)
        self.setWindowTitle("從 ORG / MOD 產生 Profile")
        self.setMinimumSize(1000, 800)
        if stylesheet:
            self.setStyleSheet(stylesheet)

        self.result_text = ""
        self._build_ui()

    # ---------------------------------------------------------------- UI

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(12)

        intro = QLabel(
            "選擇 code change 套件（底下要有 ORG\\ 與 MOD\\ 兩個資料夾）。"
            "工具會自動比對出所有修改片段、把各專案相同的修改合併成一條規則，"
            "並實際套用一次驗證結果與 MOD 是否相符。")
        intro.setObjectName("Hint")
        intro.setWordWrap(True)
        outer.addWidget(intro)

        outer.addWidget(self._build_source_group())
        outer.addWidget(self._build_meta_group())

        bar = QHBoxLayout()
        self.generate_btn = QPushButton("產生並驗證")
        self.generate_btn.setObjectName("Primary")
        self.generate_btn.clicked.connect(self._generate)
        bar.addWidget(self.generate_btn)
        bar.addStretch(1)
        outer.addLayout(bar)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        msg_box = QGroupBox("產生結果")
        msg_layout = QVBoxLayout(msg_box)
        self.message_view = QPlainTextEdit()
        self.message_view.setReadOnly(True)
        self.message_view.setMinimumHeight(260)
        msg_layout.addWidget(self.message_view)
        splitter.addWidget(msg_box)

        yaml_box = QGroupBox("YAML 預覽（可直接編輯後再儲存）")
        yaml_layout = QVBoxLayout(yaml_box)
        self.yaml_view = QPlainTextEdit()
        self.yaml_view.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.yaml_view.setMinimumHeight(260)
        yaml_layout.addWidget(self.yaml_view)
        splitter.addWidget(yaml_box)
        splitter.setSizes([380, 620])
        outer.addWidget(splitter, 1)

        foot = QHBoxLayout()
        foot.addStretch(1)
        self.save_as_btn = QPushButton("另存新檔…")
        self.save_as_btn.clicked.connect(self._save_as)
        self.save_btn = QPushButton("儲存到 profiles\\")
        self.save_btn.setObjectName("Primary")
        self.save_btn.clicked.connect(self._save_to_profiles)
        close_btn = QPushButton("關閉")
        close_btn.clicked.connect(self.reject)
        for btn in (self.save_as_btn, self.save_btn, close_btn):
            foot.addWidget(btn)
        outer.addLayout(foot)

        self._set_saveable(False)

    def _build_source_group(self):
        group = QGroupBox("1　來源")
        grid = QGridLayout(group)
        grid.setColumnStretch(1, 1)

        grid.addWidget(QLabel("Code change 套件："), 0, 0)
        self.package_edit = QLineEdit()
        self.package_edit.setPlaceholderText("底下要有 ORG\\ 與 MOD\\ 的資料夾")
        self.package_edit.textChanged.connect(self._on_package_changed)
        grid.addWidget(self.package_edit, 0, 1)
        browse = QPushButton("瀏覽…")
        browse.clicked.connect(self._browse_package)
        grid.addWidget(browse, 0, 2)

        grid.addWidget(QLabel("ORG 資料夾："), 1, 0)
        self.org_edit = QLineEdit()
        grid.addWidget(self.org_edit, 1, 1, 1, 2)

        grid.addWidget(QLabel("MOD 資料夾："), 2, 0)
        self.mod_edit = QLineEdit()
        grid.addWidget(self.mod_edit, 2, 1, 1, 2)
        return group

    def _build_meta_group(self):
        group = QGroupBox("2　Profile 設定")
        grid = QGridLayout(group)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(4, 1)

        grid.addWidget(QLabel("世代代號："), 0, 0)
        self.key_edit = QLineEdit()
        self.key_edit.setPlaceholderText("FY28")
        grid.addWidget(self.key_edit, 0, 1)
        grid.addWidget(QLabel("顯示名稱："), 0, 3)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("FY28 (Xxx Lake)")
        grid.addWidget(self.name_edit, 0, 4)
        grid.addWidget(QLabel("優先序："), 0, 5)
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(0, 999)
        self.priority_spin.setValue(100)
        grid.addWidget(self.priority_spin, 0, 6)

        grid.addWidget(QLabel("偵測資料夾："), 1, 0)
        self.detect_edit = QLineEdit()
        self.detect_edit.setPlaceholderText(".gitman/Intel/XxxLakeBoardPkg（多個用分號隔開）")
        grid.addWidget(self.detect_edit, 1, 1, 1, 6)

        grid.addWidget(QLabel("PCD 掃描根目錄："), 2, 0)
        self.scan_edit = QLineEdit("HpPlatformPkg/MultiProject")
        grid.addWidget(self.scan_edit, 2, 1, 1, 6)

        grid.addWidget(QLabel("new_files 來源："), 3, 0)
        self.newfiles_edit = QLineEdit()
        self.newfiles_edit.setPlaceholderText("留空 = 直接指向上面的 MOD 資料夾（建議）")
        grid.addWidget(self.newfiles_edit, 3, 1, 1, 6)

        row = QHBoxLayout()
        row.addWidget(QLabel("前後文行數："))
        self.ctx_spin = QSpinBox()
        self.ctx_spin.setRange(1, 20)
        self.ctx_spin.setValue(3)
        self.ctx_spin.setToolTip("每個修改片段前後保留幾行原始內容。\n"
                                 "太少會比對不唯一，太多則容易被上游的無關改動影響。")
        row.addWidget(self.ctx_spin)
        row.addSpacing(20)

        self.merge_box = QCheckBox("合併多專案相同的修改")
        self.merge_box.setChecked(True)
        self.merge_box.setToolTip("MultiProject 底下各專案若有完全相同的修改，"
                                  "合併成一條 file_name 規則（檔名不同時自動推出萬用字元）")
        row.addWidget(self.merge_box)

        self.ignore_comment_box = QCheckBox("忽略註解差異也合併")
        self.ignore_comment_box.setToolTip(
            "各專案只有註解不同時也合併，統一採用第一個專案的版本。\n"
            "會在產生結果中列出哪些專案被統一。")
        row.addWidget(self.ignore_comment_box)

        self.roundtrip_box = QCheckBox("產生後實際套用一次驗證")
        self.roundtrip_box.setChecked(True)
        self.roundtrip_box.setToolTip("複製一份 ORG 套用產生的 profile，再與 MOD 比對（忽略註解與空行）")
        row.addWidget(self.roundtrip_box)
        row.addStretch(1)

        holder = QWidget()
        holder.setLayout(row)
        grid.addWidget(holder, 4, 0, 1, 7)
        return group

    # ---------------------------------------------------------------- 事件

    def _browse_package(self):
        start = self.package_edit.text().strip() or str(Path.home())
        path = QFileDialog.getExistingDirectory(self, "選擇 code change 套件資料夾", start)
        if path:
            self.package_edit.setText(path)

    def _on_package_changed(self, text):
        text = text.strip()
        if not text:
            return
        org, mod, key = suggest_options(text)
        if org:
            self.org_edit.setText(org)
        if mod:
            self.mod_edit.setText(mod)
        if key and not self.key_edit.text().strip():
            self.key_edit.setText(key)

    def _set_saveable(self, value):
        self.save_btn.setEnabled(value)
        self.save_as_btn.setEnabled(value)

    def _options(self):
        detect = [d.strip() for d in self.detect_edit.text().replace(",", ";").split(";")]
        scans = [s.strip() for s in self.scan_edit.text().replace(",", ";").split(";")]
        return GenOptions(
            org_dir=self.org_edit.text().strip(),
            mod_dir=self.mod_edit.text().strip(),
            key=self.key_edit.text().strip(),
            display_name=self.name_edit.text().strip(),
            priority=self.priority_spin.value(),
            detect_dirs=[d for d in detect if d],
            pcd_scan_roots=[s for s in scans if s],
            context_lines=self.ctx_spin.value(),
            merge_projects=self.merge_box.isChecked(),
            merge_ignore_comments=self.ignore_comment_box.isChecked(),
            new_files_dir=self.newfiles_edit.text().strip(),
        )

    def _generate(self):
        options = self._options()
        lines = []
        logger = Logger(sink=lambda level, msg: lines.append(f"{_ICON.get(level, '•')} {msg}"),
                        echo_stdout=False)

        self.message_view.setPlainText("產生中…")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            result = generate(options, logger)
            report = None
            if result.ok and self.roundtrip_box.isChecked():
                lines.append("")
                lines.append("▶ 實際套用驗證")
                report = roundtrip_check(result.yaml_text, options,
                                         Logger(echo_stdout=False))
        finally:
            QApplication.restoreOverrideCursor()

        self._render(result, report, lines)

    def _render(self, result, report, log_lines):
        out = []
        if result.errors:
            out.append("=== 產生失敗 ===")
            out += [f"✖ {e}" for e in result.errors]
        else:
            stats = result.stats
            out.append("=== 產生完成 ===")
            out.append(f"新增檔案　　　　{stats.get('new_files', 0)} 個")
            out.append(f"指定路徑規則　　{stats.get('sub_rules', 0)} 條")
            out.append(f"PCD 掃描規則　　{stats.get('pcd_rules', 0)} 條")
            out.append(f"無變化的檔案　　{stats.get('unchanged', 0)} 個")

        if report is not None:
            out.append("")
            out.append("=== 實際套用驗證 ===")
            if report.get("error"):
                out.append(f"✖ {report['error']}")
            else:
                out.append(f"套用成功　{report['applied']} 項，失敗 {report['failed']} 項")
                out.append(f"內容驗證　通過 {report['verified']}，失敗 {report['verify_failed']}")
                out.append(f"與 MOD 比對　{report['compared']} 個檔案"
                           f"，不符 {len(report['mismatch'])} 個")
                for rel in report["mismatch"][:20]:
                    out.append(f"    ✖ {rel}")
                if not report["mismatch"] and not report["failed"]:
                    out.append("✔ 產生的 profile 套用後與 MOD 功能等價")

        if result.warnings:
            out.append("")
            out.append(f"=== 需要注意（{len(result.warnings)}）===")
            out += [f"▲ {w}" for w in result.warnings]

        if log_lines:
            out.append("")
            out.append("=== 過程 ===")
            out += log_lines

        self.message_view.setPlainText("\n".join(out))
        self.yaml_view.setPlainText(result.yaml_text)
        self._set_saveable(result.ok)
        self.result_text = result.yaml_text

    # ---------------------------------------------------------------- 儲存

    def _current_yaml(self):
        return self.yaml_view.toPlainText()

    def _write(self, path):
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(self._current_yaml(), encoding="utf-8", newline="\n")
            return True
        except Exception as exc:
            QMessageBox.warning(self, APP_NAME, f"儲存失敗：{exc}")
            return False

    def _save_to_profiles(self):
        key = self.key_edit.text().strip() or "NEW"
        target = user_profile_dir() / f"{key}.yaml"
        if target.exists():
            confirm = QMessageBox.question(
                self, APP_NAME, f"{target.name} 已存在，要覆蓋嗎？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm != QMessageBox.Yes:
                return
        if self._write(target):
            QMessageBox.information(self, APP_NAME, f"已儲存：\n{target}")
            self.accept()

    def _save_as(self):
        key = self.key_edit.text().strip() or "NEW"
        path, _ = QFileDialog.getSaveFileName(
            self, "另存 profile", str(user_profile_dir() / f"{key}.yaml"),
            "YAML (*.yaml);;所有檔案 (*.*)")
        if path and self._write(path):
            QMessageBox.information(self, APP_NAME, f"已儲存：\n{path}")


_ICON = {"debug": "·", "info": "•", "ok": "✔", "warn": "▲", "error": "✖", "step": "▶"}
