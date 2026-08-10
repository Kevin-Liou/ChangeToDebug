"""主視窗。"""

import html
import os
from pathlib import Path

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QFrame, QGroupBox,
                             QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                             QProgressBar, QPushButton, QScrollArea, QSplitter,
                             QTabWidget, QTextEdit, QVBoxLayout, QWidget)

from ..appinfo import APP_NAME, APP_TITLE, APP_VERSION, LOG_FILE, app_dir, user_profile_dir
from ..core.profiles import detect_profile, load_profiles, yaml
from ..core.runner import RunRequest
from .pages import PAGE_CLASSES
from .theme import build_stylesheet, log_colors, palette
from .worker import RunWorker

#: 保留在記憶體中的訊息筆數（切換主題時用來重畫）
LOG_RECORD_LIMIT = 5000

LEVEL_ICON = {
    "debug": "·",
    "info": "•",
    "ok": "✔",
    "warn": "▲",
    "error": "✖",
    "step": "▶",
}


class MainWindow(QMainWindow):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.theme_name = settings.get("theme", "light")
        self.profiles = []
        self.detected_profile = None
        self.worker = None
        self.log_path = app_dir() / LOG_FILE
        self._chip_state = ("ok", "")
        self._log_records = []

        self.setWindowTitle(f"{APP_TITLE}  v{APP_VERSION}")
        self.setMinimumSize(980, 660)
        self.resize(1120, 880)

        self._build_ui()
        self._apply_theme(self.theme_name)
        self._load_settings()
        self.reload_profiles(quiet=True)

    # ================================================================ UI

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("Root")
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(12)

        outer.addWidget(self._build_header())

        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)

        top = QWidget()
        top.setObjectName("Canvas")
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(12)
        top_layout.addWidget(self._build_project_group())
        top_layout.addWidget(self._build_tabs(), 1)

        scroll = QScrollArea()
        scroll.setObjectName("MainScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(top)
        splitter.addWidget(scroll)
        splitter.addWidget(self._build_log_group())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([600, 260])
        outer.addWidget(splitter, 1)

        outer.addWidget(self._build_action_bar())

    def _build_header(self):
        frame = QFrame()
        frame.setObjectName("Header")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        text_box = QVBoxLayout()
        text_box.setSpacing(2)
        title = QLabel(APP_NAME)
        title.setObjectName("HeaderTitle")
        subtitle = QLabel("BIOS source 一鍵切換 Debug Mode｜FY 世代由 profile 設定檔決定")
        subtitle.setObjectName("HeaderSubtitle")
        text_box.addWidget(title)
        text_box.addWidget(subtitle)
        layout.addLayout(text_box)

        version = QLabel(f"v{APP_VERSION}")
        version.setObjectName("VersionChip")
        layout.addWidget(version)
        layout.addStretch(1)

        self.theme_btn = QPushButton("切換深色")
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)

        about_btn = QPushButton("關於")
        about_btn.clicked.connect(self._show_about)
        layout.addWidget(about_btn)
        return frame

    def _build_project_group(self):
        group = QGroupBox("1　專案根目錄與執行選項")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        row = QHBoxLayout()
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.setInsertPolicy(QComboBox.NoInsert)
        self.path_combo.lineEdit().setPlaceholderText("選擇 BIOS source 的根目錄（含 .gitman 的那一層）")
        self.path_combo.currentTextChanged.connect(self._on_path_changed)
        row.addWidget(self.path_combo, 1)

        browse_btn = QPushButton("瀏覽…")
        browse_btn.clicked.connect(self._browse_path)
        row.addWidget(browse_btn)
        layout.addLayout(row)

        status_row = QHBoxLayout()
        self.status_chip = QLabel("尚未選擇路徑")
        self.status_chip.setObjectName("StatusChip")
        status_row.addWidget(self.status_chip)

        status_row.addSpacing(10)
        status_row.addWidget(QLabel("專案世代："))
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(220)
        self.profile_combo.currentIndexChanged.connect(self._on_profile_selected)
        status_row.addWidget(self.profile_combo)

        reload_btn = QPushButton("重新載入設定檔")
        reload_btn.setToolTip("重新掃描 profiles 資料夾，新增 FY27.yaml 後按這裡即可")
        reload_btn.clicked.connect(lambda: self.reload_profiles(quiet=False))
        status_row.addWidget(reload_btn)

        open_btn = QPushButton("開啟設定檔資料夾")
        open_btn.clicked.connect(self._open_profile_dir)
        status_row.addWidget(open_btn)

        gen_btn = QPushButton("產生 Profile…")
        gen_btn.setToolTip("從 code change 套件的 ORG / MOD 自動產生新世代的設定檔")
        gen_btn.clicked.connect(self._open_profile_generator)
        status_row.addWidget(gen_btn)
        status_row.addStretch(1)
        layout.addLayout(status_row)

        self.profile_hint = QLabel("")
        self.profile_hint.setObjectName("Hint")
        self.profile_hint.setWordWrap(True)
        layout.addWidget(self.profile_hint)

        layout.addWidget(self._build_options_row())
        return group

    def _build_options_row(self):
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(22)

        label = QLabel("執行選項：")
        label.setObjectName("Muted")
        layout.addWidget(label)

        self.debug_flag_box = QCheckBox("啟用所有 Debug Flag")
        self.debug_flag_box.setToolTip("設定檔中 option_debug_flag: true 的選配項目才會被套用（log 量會大幅增加）")
        self.debug_flag_box.toggled.connect(self._on_debug_flag_toggled)

        self.backup_box = QCheckBox("備份原始檔案")
        self.backup_box.setToolTip("修改前先複製一份 xxx.bak.<時間戳> 在原檔旁邊")

        self.dry_run_box = QCheckBox("預覽模式（不實際修改）")
        self.dry_run_box.setToolTip("只比對並列出會被修改的檔案，不寫入任何內容")
        self.dry_run_box.toggled.connect(self._update_run_button)

        self.verify_box = QCheckBox("完成後自動驗證")
        self.verify_box.setToolTip("跑完後重新讀取被修改的檔案，確認內容真的變成預期的樣子"
                                   "（預覽模式不會驗證）")

        for box in (self.debug_flag_box, self.backup_box, self.dry_run_box, self.verify_box):
            layout.addWidget(box)
        layout.addStretch(1)
        return row

    def _build_tabs(self):
        group = QGroupBox("2　功能（可同時勾選多項，會依分頁順序執行）")
        layout = QVBoxLayout(group)
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(330)
        self.pages = []
        for page_cls in PAGE_CLASSES:
            page = page_cls()
            page.enabled_changed.connect(self._on_task_toggled)
            self.pages.append(page)
            self.tabs.addTab(page, page.task_title)
        layout.addWidget(self.tabs)
        return group

    def _build_log_group(self):
        group = QGroupBox("執行記錄")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        bar = QHBoxLayout()
        self.summary_label = QLabel("待命中")
        self.summary_label.setObjectName("Hint")
        bar.addWidget(self.summary_label, 1)

        clear_btn = QPushButton("清除")
        clear_btn.clicked.connect(self._clear_log)
        bar.addWidget(clear_btn)

        save_btn = QPushButton("另存記錄…")
        save_btn.clicked.connect(self._save_log)
        bar.addWidget(save_btn)

        open_log_btn = QPushButton("開啟 log 檔")
        open_log_btn.clicked.connect(self._open_log_file)
        bar.addWidget(open_log_btn)
        layout.addLayout(bar)

        self.log_view = QTextEdit()
        self.log_view.setObjectName("LogView")
        self.log_view.setReadOnly(True)
        self.log_view.document().setMaximumBlockCount(8000)
        layout.addWidget(self.log_view, 1)
        return group

    def _build_action_bar(self):
        bar = QWidget()
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)     # 進度數字改用旁邊的標籤，避免蓋在色塊上看不清
        layout.addWidget(self.progress, 1)

        self.progress_label = QLabel("待命中")
        self.progress_label.setObjectName("Hint")
        self.progress_label.setMinimumWidth(130)
        self.progress_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.progress_label)

        self.cancel_btn = QPushButton("停止")
        self.cancel_btn.setObjectName("Danger")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_run)
        layout.addWidget(self.cancel_btn)

        self.run_btn = QPushButton("開始執行")
        self.run_btn.setObjectName("Primary")
        self.run_btn.clicked.connect(self._start_run)
        layout.addWidget(self.run_btn)
        return bar

    # ================================================================ 主題

    def _apply_theme(self, name):
        self.theme_name = name
        self.setStyleSheet(build_stylesheet(name))
        self.theme_btn.setText("切換淺色" if name == "dark" else "切換深色")
        self._set_chip(*self._chip_state)

    def _toggle_theme(self):
        self._apply_theme("dark" if self.theme_name == "light" else "light")
        self._rerender_log()
        self.settings.set("theme", self.theme_name)
        self.settings.save()

    def _set_chip(self, kind, text):
        self._chip_state = (kind, text)
        colors = palette(self.theme_name)
        mapping = {
            "ok": (colors["ok"], "rgba(21,128,61,0.12)"),
            "warn": (colors["warn"], "rgba(180,83,9,0.12)"),
            "error": (colors["error"], "rgba(185,28,28,0.12)"),
            "idle": (colors["subtext"], colors["surface_alt"]),
        }
        fg, bg = mapping.get(kind, mapping["idle"])
        self.status_chip.setText(text)
        self.status_chip.setStyleSheet(
            f"QLabel#StatusChip {{ color: {fg}; background: {bg};"
            f" border-radius: 9px; padding: 3px 10px; font-weight: 600; }}")

    # ================================================================ 設定值

    def _load_settings(self):
        self.path_combo.blockSignals(True)
        self.path_combo.addItems(self.settings.get("recent_paths", []))
        self.path_combo.setCurrentText(
            self.settings.get("recent_paths", [""])[0] if self.settings.get("recent_paths") else "")
        self.path_combo.blockSignals(False)

        self.debug_flag_box.setChecked(bool(self.settings.get("enable_all_debug_flags")))
        self.backup_box.setChecked(bool(self.settings.get("backup", True)))
        self.dry_run_box.setChecked(bool(self.settings.get("dry_run")))
        self.verify_box.setChecked(bool(self.settings.get("verify_after_run", True)))

        enabled = set(self.settings.get("enabled_tasks", ["patchset"]))
        for page in self.pages:
            page.load_settings(self.settings)
            page.set_task_enabled(page.task_key in enabled)
        self._update_run_button()

    def _save_settings(self):
        self.settings.set("enable_all_debug_flags", self.debug_flag_box.isChecked())
        self.settings.set("backup", self.backup_box.isChecked())
        self.settings.set("dry_run", self.dry_run_box.isChecked())
        self.settings.set("verify_after_run", self.verify_box.isChecked())
        self.settings.set("theme", self.theme_name)
        self.settings.set("enabled_tasks",
                          [p.task_key for p in self.pages if p.is_task_enabled()])
        for page in self.pages:
            page.save_settings(self.settings)
        self.settings.save()

    # ================================================================ Profile

    def reload_profiles(self, quiet=True):
        self.profiles = load_profiles()

        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profile_combo.addItem("自動偵測", None)
        for profile in self.profiles:
            label = profile.title if profile.title == profile.key else f"{profile.key}｜{profile.title}"
            self.profile_combo.addItem(label, profile.key)
        self.profile_combo.blockSignals(False)

        if not self.profiles:
            self._append_log("error", "找不到任何 profile 設定檔，請確認 profiles 資料夾內有 FY25/FY26 等 YAML。")
        elif not quiet:
            names = "、".join(p.key for p in self.profiles)
            self._append_log("ok", f"已載入 {len(self.profiles)} 個世代設定：{names}")

        for profile in self.profiles:
            if profile.load_error:
                self._append_log("warn", f"{profile.key}：{profile.load_error}")

        self._detect_profile()

    def _detect_profile(self):
        base = self.path_combo.currentText().strip()
        if not base:
            self.detected_profile = None
            self._set_chip("idle", "尚未選擇路徑")
            self.profile_hint.setText("")
            self._sync_pages_profile()
            return

        if not os.path.isdir(base):
            self.detected_profile = None
            self._set_chip("error", "路徑不存在")
            self.profile_hint.setText("請確認輸入的資料夾是否存在。")
            self._sync_pages_profile()
            return

        self.detected_profile = detect_profile(base, self.profiles)
        if self.detected_profile is None:
            self._set_chip("warn", "無法辨識專案世代")
            hints = "；".join(f"{p.key} → {p.detect_hint()}" for p in self.profiles)
            self.profile_hint.setText(
                f"自動偵測失敗，可在右方手動指定世代。目前的偵測條件：{hints or '（無）'}")
        else:
            self._set_chip("ok", f"已偵測：{self.detected_profile.title}")
            self.profile_hint.setText(
                f"偵測依據：{self.detected_profile.detect_hint()}　"
                f"設定檔：{self.detected_profile.source_path}")
        self._sync_pages_profile()

    def current_profile(self):
        key = self.profile_combo.currentData()
        if key is None:
            return self.detected_profile
        for profile in self.profiles:
            if profile.key == key:
                return profile
        return None

    def _sync_pages_profile(self):
        profile = self.current_profile()
        for page in self.pages:
            page.on_profile_changed(profile)
            page.on_debug_flag_changed(self.debug_flag_box.isChecked())
        self._update_run_button()

    # ================================================================ 事件

    def _browse_path(self):
        start = self.path_combo.currentText().strip() or str(Path.home())
        path = QFileDialog.getExistingDirectory(self, "選擇 BIOS source 根目錄", start)
        if path:
            self.path_combo.setCurrentText(os.path.normpath(path))

    def _on_path_changed(self, _text):
        self._detect_profile()

    def _on_profile_selected(self, _index):
        profile = self.current_profile()
        if self.profile_combo.currentData() is not None and profile is not None:
            self._set_chip("ok", f"手動指定：{profile.title}")
            self.profile_hint.setText(f"設定檔：{profile.source_path}")
        elif self.profile_combo.currentData() is None:
            self._detect_profile()
            return
        self._sync_pages_profile()

    def _on_debug_flag_toggled(self, checked):
        for page in self.pages:
            page.on_debug_flag_changed(checked)

    def _on_task_toggled(self):
        self._update_run_button()

    def _update_run_button(self, *_):
        enabled = [p for p in self.pages if p.is_task_enabled()]
        self.run_btn.setEnabled(bool(enabled) and self.worker is None)
        if self.dry_run_box.isChecked():
            self.run_btn.setText("開始預覽")
        else:
            self.run_btn.setText("開始執行")

    def _open_profile_generator(self):
        from .profilegen_dialog import ProfileGenDialog
        dialog = ProfileGenDialog(self, stylesheet=build_stylesheet(self.theme_name))
        if dialog.exec_() == ProfileGenDialog.Accepted:
            self._append_log("ok", "已產生新的 profile，重新載入設定檔。")
            self.reload_profiles(quiet=False)

    def _open_profile_dir(self):
        target = user_profile_dir()
        try:
            target.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def _open_log_file(self):
        if not self.log_path.is_file():
            QMessageBox.information(self, APP_NAME, "目前還沒有 log 檔，執行一次後才會產生。")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.log_path)))

    def _save_log(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "另存執行記錄", str(app_dir() / "ChangeToDebug_report.txt"),
            "文字檔 (*.txt);;所有檔案 (*.*)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_view.toPlainText())
            QMessageBox.information(self, APP_NAME, f"已儲存到：\n{path}")
        except Exception as exc:
            QMessageBox.warning(self, APP_NAME, f"儲存失敗：{exc}")

    # ================================================================ 執行

    def _start_run(self):
        if self.worker is not None:
            return

        base = self.path_combo.currentText().strip()
        if not base or not os.path.isdir(base):
            QMessageBox.warning(self, APP_NAME, "請先選擇有效的專案根目錄。")
            return

        pages = [p for p in self.pages if p.is_task_enabled()]
        if not pages:
            QMessageBox.warning(self, APP_NAME, "請至少啟用一項功能。")
            return

        profile = self.current_profile()
        needs_profile = any(p.task_key == "patchset" for p in pages)
        if needs_profile:
            if yaml is None:
                QMessageBox.critical(self, APP_NAME,
                                     "未安裝 PyYAML，無法讀取設定檔。\n請執行：pip install pyyaml")
                return
            if profile is None:
                QMessageBox.warning(self, APP_NAME,
                                    "無法判斷專案世代，請在「專案世代」下拉選單手動指定。")
                return

        dry_run = self.dry_run_box.isChecked()
        backup = self.backup_box.isChecked()
        if dry_run:
            message = "目前為預覽模式，不會實際修改任何檔案。是否繼續？"
        else:
            message = ("這將會直接修改專案中的檔案，"
                       + ("並在原檔旁建立備份。" if backup else "且不會建立任何備份。")
                       + "\n是否繼續？")
        names = "、".join(p.task_title for p in pages)
        confirm = QMessageBox.question(
            self, "執行確認",
            f"專案：{base}\n世代：{profile.title if profile else '（不需要）'}\n"
            f"功能：{names}\n\n{message}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return

        options = {p.task_key: p.collect_options() for p in pages}
        request = RunRequest(
            base_path=base,
            profile=profile,
            task_keys=[p.task_key for p in pages],
            options=options,
            dry_run=dry_run,
            backup=backup,
            enable_all_debug_flags=self.debug_flag_box.isChecked(),
            verify_after_run=self.verify_box.isChecked(),
        )

        self.settings.push_recent_path(base)
        self._save_settings()
        self._refresh_recent_combo(base)

        self._clear_log()
        self.progress.setRange(0, 0)
        self.progress_label.setText("執行中…")
        self.summary_label.setText("執行中…")
        self.run_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

        self.worker = RunWorker(request, log_file=self.log_path)
        self.worker.logged.connect(self._append_log)
        self.worker.progressed.connect(self._on_progress)
        self.worker.finished_run.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self._on_thread_done)
        self.worker.start()

    def _refresh_recent_combo(self, current):
        self.path_combo.blockSignals(True)
        self.path_combo.clear()
        self.path_combo.addItems(self.settings.get("recent_paths", []))
        self.path_combo.setCurrentText(current)
        self.path_combo.blockSignals(False)

    def _cancel_run(self):
        if self.worker is not None:
            self.worker.cancel()
            self.cancel_btn.setEnabled(False)
            self.summary_label.setText("正在停止…（會在目前檔案處理完後結束）")

    def _on_progress(self, done, total):
        if total <= 0:
            return
        if self.progress.maximum() != total:
            self.progress.setRange(0, total)
        self.progress.setValue(done)
        self.progress_label.setText(f"{done} / {total}　({done * 100 // max(total, 1)}%)")

    def _on_finished(self, summary):
        stats = summary.overall
        verification = summary.verification
        parts = [
            f"共處理 {stats.total} 項",
            f"變更 {stats.changed}",
            f"已套用過 {stats.already}",
            f"略過 {stats.skipped}",
            f"失敗 {stats.failed}",
        ]
        if verification is not None and verification.total:
            parts.append(f"驗證通過 {verification.passed}/{verification.total}")
        text = "　|　".join(parts) + f"　|　耗時 {summary.elapsed:.1f} 秒"
        self.summary_label.setText(text)

        self._append_log("step", "執行結果")
        for key, task_stats in summary.stats_by_task.items():
            self._append_log(
                "info",
                f"{key}：處理 {task_stats.total}，變更 {task_stats.changed}，"
                f"已套用過 {task_stats.already}，略過 {task_stats.skipped}，失敗 {task_stats.failed}")
        if summary.backup_count:
            self._append_log("info",
                             f"已備份 {summary.backup_count} 個檔案（副檔名 .bak.{summary.run_stamp}）")

        failures = [r for r in stats.results if not r.ok]
        if failures:
            self._append_log("warn", f"以下 {len(failures)} 項需要人工確認：")
            for result in failures[:50]:
                self._append_log("warn", f"  [{result.status_text}] {result.label or result.file_path}")
            if len(failures) > 50:
                self._append_log("warn", f"  …另有 {len(failures) - 50} 項，詳見 log 檔")

        verify_failed = verification.failed if verification is not None else 0
        if verify_failed:
            self._append_log("error", f"以下 {verify_failed} 項驗證沒有通過（檔案內容與預期不符）：")
            for result in verification.failures[:50]:
                self._append_log("error",
                                 f"  {result.label or result.file_path}：{result.reason_text}")
            if verify_failed > 50:
                self._append_log("error", f"  …另有 {verify_failed - 50} 項，詳見 log 檔")

        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress_label.setText("完成")

        if summary.cancelled:
            self._append_log("warn", "執行已被使用者中止。")
            QMessageBox.information(self, APP_NAME, "已中止執行。\n\n" + text)
        elif verify_failed:
            self._append_log("error", "處理完成，但驗證發現實際內容與預期不符。")
            QMessageBox.critical(self, APP_NAME,
                                 f"驗證未通過：{verify_failed} 個項目的檔案內容與預期不符。\n\n"
                                 f"{text}\n\n請於下方執行記錄確認詳情。")
        elif stats.failed:
            self._append_log("warn", "處理完成，但有項目未成功。")
            QMessageBox.warning(self, APP_NAME,
                                f"處理完成，但有 {stats.failed} 項未成功。\n\n{text}\n\n"
                                "請於下方執行記錄確認詳情。")
        else:
            self._append_log("ok", "處理完成。")
            QMessageBox.information(self, APP_NAME, f"處理完成。\n\n{text}")

    def _on_failed(self, message):
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress_label.setText("發生錯誤")
        self.summary_label.setText("發生錯誤")
        QMessageBox.critical(self, APP_NAME, f"執行時發生錯誤：\n{message}")

    def _on_thread_done(self):
        self.worker = None
        self.cancel_btn.setEnabled(False)
        self._update_run_button()

    # ================================================================ Log

    def _log_html(self, level, message):
        colors = log_colors(self.theme_name)
        color = colors.get(level, colors["info"])
        icon = LEVEL_ICON.get(level, "•")
        escaped = html.escape(message)
        if "\n" in message:
            return f'<div style="color:{color}; white-space:pre-wrap;">{icon} {escaped}</div>'
        weight = "font-weight:700;" if level == "step" else ""
        return f'<div style="color:{color}; {weight}">{icon} {escaped}</div>'

    def _append_log(self, level, message):
        self._log_records.append((level, message))
        if len(self._log_records) > LOG_RECORD_LIMIT:
            del self._log_records[:len(self._log_records) - LOG_RECORD_LIMIT]

        self.log_view.append(self._log_html(level, message))
        scrollbar = self.log_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _clear_log(self):
        self._log_records = []
        self.log_view.clear()

    def _rerender_log(self):
        """切換主題後重畫既有訊息，避免舊顏色在新背景下看不清楚。"""
        if not self._log_records:
            return
        self.log_view.clear()
        self.log_view.setHtml("".join(self._log_html(lv, msg)
                                      for lv, msg in self._log_records))
        scrollbar = self.log_view.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    # ================================================================ 其他

    def _show_about(self):
        profiles = "\n".join(
            f"  • {p.key}｜{p.title}　({p.rule_count()} 條規則)" for p in self.profiles
        ) or "  （尚未載入任何設定檔）"
        QMessageBox.about(
            self, f"關於 {APP_NAME}",
            f"<b>{APP_NAME}</b> v{APP_VERSION}<br>"
            f"BIOS source 一鍵切換 Debug Mode<br><br>"
            f"<b>已載入的專案世代</b><pre>{html.escape(profiles)}</pre>"
            f"<b>新增下一個世代（例如 FY27）</b><br>"
            f"把 <code>FY27.yaml</code> 放進 <code>{html.escape(str(user_profile_dir()))}</code>，"
            f"再按「重新載入設定檔」即可，不需要改程式。<br><br>"
            f"log 檔：<code>{html.escape(str(self.log_path))}</code>")

    def closeEvent(self, event):
        if self.worker is not None:
            confirm = QMessageBox.question(
                self, APP_NAME, "仍在執行中，確定要關閉嗎？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm != QMessageBox.Yes:
                event.ignore()
                return
            self.worker.cancel()
            self.worker.wait(3000)
        self._save_settings()
        super().closeEvent(event)
