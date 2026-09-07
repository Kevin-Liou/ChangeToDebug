"""主視窗。"""

import html
import os
import shutil
import subprocess
from pathlib import Path

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QFileDialog,
                             QFrame, QGroupBox, QHBoxLayout, QLabel, QMainWindow,
                             QMessageBox, QProgressBar, QPushButton, QScrollArea,
                             QSplitter, QTabWidget, QTextEdit, QVBoxLayout, QWidget)

from ..appinfo import APP_NAME, APP_TITLE, APP_VERSION, LOG_FILE, app_dir, user_profile_dir
from ..core.basesnap import extract_for_profile, write_package
from ..core.logbus import Logger
from ..core.profiles import detect_profile, load_profiles, yaml
from ..core.runner import RunRequest
from .pages import PAGE_CLASSES
from .theme import build_stylesheet, list_themes, log_colors, palette, with_alpha
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
        self._drift_cache = {}
        self._conflict_dir = ""

        self.setWindowTitle(f"{APP_TITLE}  v{APP_VERSION}")
        self.setMinimumSize(980, 660)
        self.resize(*self._default_size())

        self._build_ui()
        self._apply_theme(self.theme_name)
        self._load_settings()
        self.reload_profiles(quiet=True)

    @staticmethod
    def _default_size():
        """依螢幕可用區域決定預設視窗大小。

        原本寫死 1120x880，在一般螢幕上規則表格只看得到兩三列、執行記錄只剩幾行，
        載入時的警告很容易一開始就被捲出畫面。改成依螢幕比例決定，並設上下限：
        小螢幕不會超出可用區域，大螢幕也不會只開一小塊。
        """
        screen = QApplication.primaryScreen()
        if screen is None:
            return 1400, 1000
        area = screen.availableGeometry()
        width = max(1120, min(1600, int(area.width() * 0.80)))
        height = max(800, min(1100, int(area.height() * 0.90)))
        # 小螢幕上下限可能反而超出可用區域，最後再夾一次
        return min(width, area.width()), min(height, area.height())

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
        splitter.setSizes([620, 400])
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

        # 主題下拉：淺色一組、深色一組，中間以分隔線隔開。userData 存主題 key。
        self.theme_combo = QComboBox()
        self.theme_combo.setToolTip("佈景主題")
        self.theme_combo.setMinimumWidth(150)
        themes = list_themes()
        for kind in ("light", "dark"):
            if kind == "dark" and self.theme_combo.count():
                self.theme_combo.insertSeparator(self.theme_combo.count())
            for key, label, k in themes:
                if k == kind:
                    self.theme_combo.addItem(label, key)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_selected)
        layout.addWidget(self.theme_combo)

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

        audit_btn = QPushButton("盤點命中數…")
        audit_btn.setToolTip("算出每條規則在這棵 source 中會命中幾處，\n"
                             "並可把結果寫成 expect_count 守門，避免安靜地多改幾處")
        audit_btn.clicked.connect(self._open_audit)
        status_row.addWidget(audit_btn)

        base_btn = QPushButton("擷取 base 快照…")
        base_btn.setToolTip("從目前這棵「尚未套用」的 source tree 取出各規則的原始檔，\n"
                            "存成目錄型 profile 的 base\\，供日後比對失敗時做 3-way merge")
        base_btn.clicked.connect(self._extract_base)
        status_row.addWidget(base_btn)
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

        self.merge_box = QCheckBox("比對失敗時嘗試合併")
        self.merge_box.setToolTip(
            "codebase 更新導致 old_code 比對不到時，用 profile 的 base 快照做 3-way merge：\n"
            "上游改的若不是本規則要動的地方，就自動合併；改到同一段則報衝突並跳過該檔。\n"
            "只有帶 base 快照的目錄型 profile 才有作用。")

        for box in (self.debug_flag_box, self.backup_box, self.dry_run_box,
                    self.verify_box, self.merge_box):
            layout.addWidget(box)
        layout.addStretch(1)
        return row

    def _build_tabs(self):
        group = QGroupBox("2　功能（可同時勾選多項，會依分頁順序執行）")
        layout = QVBoxLayout(group)
        self.tabs = QTabWidget()
        self.tabs.setMinimumHeight(380)
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

        self.backup_btn = QPushButton("清理備份…")
        self.backup_btn.setToolTip("列出各次執行留下的 .bak.<時間戳> 備份，挑選要刪除的")
        self.backup_btn.clicked.connect(self._open_backups)
        bar.addWidget(self.backup_btn)

        self.resolve_btn = QPushButton("解決衝突…")
        self.resolve_btn.setToolTip("用合併工具處理上次執行留下的合併衝突")
        self.resolve_btn.clicked.connect(self._resolve_conflicts)
        bar.addWidget(self.resolve_btn)
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

        self.revert_btn = QPushButton("移除 Change…")
        self.revert_btn.setToolTip(
            "把這個世代已套用的修改反向移除（new_code 換回 old_code）。\n"
            "只移除本 profile 帶來的改動，上游在這之後的改動不受影響。")
        self.revert_btn.clicked.connect(self._start_revert)
        layout.addWidget(self.revert_btn)

        self.run_btn = QPushButton("開始執行")
        self.run_btn.setObjectName("Primary")
        self.run_btn.clicked.connect(self._start_run)
        layout.addWidget(self.run_btn)
        return bar

    # ================================================================ 主題

    def _apply_theme(self, name):
        # 設定檔可能存著已不存在的主題名，palette() 會退回預設；這裡也同步把
        # 名稱正規化，下拉選單才找得到對應項目
        if self.theme_combo.findData(name) < 0:
            name = "light"
        self.theme_name = name
        self.setStyleSheet(build_stylesheet(name))
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentIndex(self.theme_combo.findData(name))
        self.theme_combo.blockSignals(False)
        self._set_chip(*self._chip_state)

    def _on_theme_selected(self, index):
        key = self.theme_combo.itemData(index)
        if not key or key == self.theme_name:
            return
        self._apply_theme(key)
        self._rerender_log()
        self.settings.set("theme", self.theme_name)
        self.settings.save()

    def _set_chip(self, kind, text):
        self._chip_state = (kind, text)
        colors = palette(self.theme_name)
        mapping = {
            "ok": (colors["ok"], with_alpha(colors["ok"], 0.15)),
            "warn": (colors["warn"], with_alpha(colors["warn"], 0.15)),
            "error": (colors["error"], with_alpha(colors["error"], 0.15)),
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
        self.merge_box.setChecked(bool(self.settings.get("merge_fallback", True)))

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
        self.settings.set("merge_fallback", self.merge_box.isChecked())
        self.settings.set("theme", self.theme_name)
        self.settings.set("enabled_tasks",
                          [p.task_key for p in self.pages if p.is_task_enabled()])
        for page in self.pages:
            page.save_settings(self.settings)
        self.settings.save()

    # ================================================================ Profile

    def reload_profiles(self, quiet=True):
        collisions = []
        self.profiles = load_profiles(collisions=collisions)
        self._drift_cache.clear()

        # 同名 key 會被安靜地略過，不講的話使用者會以為自己放的設定檔沒作用是別的原因
        for item in collisions:
            self._append_log("warn",
                             f"設定檔的世代代號「{item['key']}」重複，已略過："
                             f"{item['ignored']}\n"
                             f"　實際使用的是：{item['used']}\n"
                             f"　要同時使用請改掉其中一個的 key，或在檔名前加底線停用。")
        # 兩個 profile 的偵測條件一樣時，自動偵測只會選 priority 小的那個，
        # 另一個等於形同虛設——使用者卻不會知道自己用到的是哪一份。
        by_detect = {}
        for profile in self.profiles:
            signature = profile.detect_signature()
            if signature:
                by_detect.setdefault(signature, []).append(profile)
        for group in by_detect.values():
            if len(group) < 2:
                continue
            group = sorted(group, key=lambda p: (p.priority, p.key))
            winner = group[0]
            others = "、".join(f"{p.key}(priority {p.priority})" for p in group[1:])
            self._append_log(
                "warn",
                f"以下世代的偵測條件完全相同：{'、'.join(p.key for p in group)}\n"
                f"　偵測依據：{winner.detect_hint()}\n"
                f"　自動偵測只會選 priority 最小的 {winner.key}（priority "
                f"{winner.priority}），{others} 需要手動指定才會用到。\n"
                "　要改變優先順序請調整 profile 的 priority，數字小者先比對。")

        # new_files_dir 常常指向外部的 code change 套件，套件被改名或搬走就整批失效
        for profile in self.profiles:
            source = profile.new_files_dir
            if profile.new_file_rules and source and not os.path.isdir(source):
                self._append_log(
                    "warn",
                    f"{profile.key} 的新增檔案來源目錄不存在，"
                    f"{len(profile.new_file_rules)} 條新增檔案規則無法套用：\n"
                    f"　{source}")

        for profile in self.profiles:
            notes = getattr(profile, "base_warnings", None) or []
            if notes:
                shown = "\n".join(f"　• {n}" for n in notes[:8])
                if len(notes) > 8:
                    shown += f"\n　…另有 {len(notes) - 8} 條"
                self._append_log(
                    "warn",
                    f"{profile.key} 的 base manifest 與規則編號不一致（規則被刪除或搬動過），"
                    "已依 sub_path / label 重新對應。建議重新「擷取 base 快照」讓檔案也對齊：\n"
                    + shown)

        for profile in self.profiles:
            dead = profile.dead_rules()
            if dead:
                self._append_log(
                    "warn",
                    f"{profile.key} 有 {len(dead)} 條規則的 old_code 與 new_code 完全相同，"
                    "套用了也不會有任何改變：\n"
                    + "\n".join(f"　• {r.rule_id}　{r.target_display}" for r in dead))

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
            note, attention = self._drift_note(self.detected_profile, base)
            self._set_chip("warn" if attention else "ok",
                           f"已偵測：{self.detected_profile.title}"
                           + ("（版本已偏離）" if attention else ""))
            hint = (f"偵測依據：{self.detected_profile.detect_hint()}　"
                    f"設定檔：{self.detected_profile.source_path}")
            self.profile_hint.setText(hint + ("\n" + note if note else ""))
        self._sync_pages_profile()

    def _drift_note(self, profile, base):
        """回傳 (版本基準提示, 是否需要注意)。profile 沒宣告基準時回傳 ("", False)。

        路徑輸入框每打一個字就會觸發偵測，故以 (路徑, profile) 為鍵快取結果，
        避免重複啟動 git 子行程。
        """
        if profile is None or not base:
            return "", False
        cache_key = (os.path.normcase(os.path.abspath(base)), profile.key, profile.source_path)
        if cache_key not in self._drift_cache:
            try:
                infos = profile.check_drift(base)
            except Exception:       # 版本檢查失敗不該影響介面
                infos = []
            self._drift_cache[cache_key] = infos
        infos = self._drift_cache[cache_key]
        if not infos:
            return "", False
        text = "　".join(f"{i.repo}：{i.summary()}" for i in infos)
        return "版本基準　" + text, any(i.needs_attention for i in infos)

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
        base = self.path_combo.currentText().strip()
        for page in self.pages:
            page.on_base_path_changed(base)
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
            note, attention = self._drift_note(profile, self.path_combo.currentText().strip())
            self._set_chip("warn" if attention else "ok",
                           f"手動指定：{profile.title}" + ("（版本已偏離）" if attention else ""))
            self.profile_hint.setText(
                f"設定檔：{profile.source_path}" + ("\n" + note if note else ""))
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
        if hasattr(self, "revert_btn"):
            self.revert_btn.setEnabled(self.worker is None)
            self.revert_btn.setText("預覽移除" if self.dry_run_box.isChecked()
                                    else "移除 Change…")
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

    def _open_audit(self):
        """盤點每條規則在目前這棵 source 中的命中數。純唯讀。"""
        from ..core.audit import audit
        from .audit_dialog import AuditDialog

        base = self.path_combo.currentText().strip()
        profile = self.current_profile()
        if not base or not os.path.isdir(base):
            QMessageBox.warning(self, APP_NAME, "請先選擇有效的專案根目錄。")
            return
        if profile is None:
            QMessageBox.warning(self, APP_NAME, "請先在「專案世代」選擇要盤點的世代。")
            return

        self._append_log("step", f"盤點命中數：{profile.title}")
        logger = Logger(sink=self._append_log, log_file=self.log_path, echo_stdout=False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            results = audit(profile, base, logger)
        except Exception as exc:
            self._append_log("error", f"盤點失敗：{exc}")
            QMessageBox.critical(self, APP_NAME, f"盤點失敗：\n{exc}")
            return
        finally:
            QApplication.restoreOverrideCursor()

        dialog = AuditDialog(profile, results, logger, self,
                             stylesheet=build_stylesheet(self.theme_name))
        dialog.exec_()
        if dialog.written:
            self.reload_profiles(quiet=False)

    def _extract_base(self):
        """從目前的 source tree 擷取 base 快照，存成目錄型 profile。"""
        base = self.path_combo.currentText().strip()
        profile = self.current_profile()
        if not base or not os.path.isdir(base):
            QMessageBox.warning(self, APP_NAME, "請先選擇有效的專案根目錄。")
            return
        if profile is None:
            QMessageBox.warning(self, APP_NAME,
                                "請先在「專案世代」選擇要擷取 base 的世代。")
            return

        target = user_profile_dir() / profile.key
        confirm = QMessageBox.question(
            self, APP_NAME,
            f"要從這棵 source tree 擷取「{profile.title}」的 base 快照嗎？\n\n"
            f"來源：{base}\n"
            f"輸出：{target}\n\n"
            "只會複製「尚未套用此 profile」的檔案當作 base，不會修改來源。\n"
            "來源樹若已經套用過這個世代的修改，該規則會被記為缺 base。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return
        if target.exists():
            confirm = QMessageBox.question(
                self, APP_NAME, f"{target} 已存在，要覆蓋嗎？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm != QMessageBox.Yes:
                return

        self._append_log("step", f"擷取 base 快照：{profile.title}")
        logger = Logger(sink=self._append_log, log_file=self.log_path, echo_stdout=False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            base_files, entries, stats = extract_for_profile(profile, base, logger)
            yaml_text = Path(profile.source_path).read_text(encoding="utf-8")
            copied = write_package(target, yaml_text, base_files, entries,
                                   base_commit=profile.base_commits.get("", ""))
        except Exception as exc:
            QApplication.restoreOverrideCursor()
            self._append_log("error", f"擷取失敗：{exc}")
            QMessageBox.critical(self, APP_NAME, f"擷取 base 失敗：\n{exc}")
            return
        finally:
            QApplication.restoreOverrideCursor()

        self._append_log("ok", f"已寫出 {target}（base 檔案 {copied} 個）")
        QMessageBox.information(
            self, APP_NAME,
            f"已擷取 base 快照：\n{target}\n\n"
            f"可取得 base 的規則　{stats['covered']} 條\n"
            f"缺 base 的規則　　　{stats['missing']} 條\n"
            f"複製的原始檔　　　　{copied} 個\n\n"
            "缺 base 的規則已記在 base_manifest.yaml，日後有乾淨的樹可再補。")
        self.reload_profiles(quiet=False)

    # ---------------------------------------------------------------- 衝突

    def _conflict_records(self):
        """取得待解決的衝突：優先用本次執行的結果，否則從專案裡找最近一次。"""
        from ..core.conflicts import latest_run, load_index
        if self._conflict_dir:
            records = load_index(self._conflict_dir)
            if records:
                return self._conflict_dir, records
        base = self.path_combo.currentText().strip()
        if base and os.path.isdir(base):
            run = latest_run(base)
            if run is not None:
                return str(run), load_index(run)
        return "", []

    def _open_conflict_dir(self):
        directory, records = self._conflict_records()
        if not directory:
            QMessageBox.information(self, APP_NAME, "目前沒有待解決的衝突。")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(directory))

    def _resolve_conflicts(self):
        """用外部合併工具解決衝突，解完後讀回並寫入專案。"""
        from ..core.conflicts import apply_all, build_all_merged

        directory, records = self._conflict_records()
        if not records:
            QMessageBox.information(self, APP_NAME, "目前沒有待解決的衝突。")
            return

        logger = Logger(sink=self._append_log, log_file=self.log_path, echo_stdout=False)

        # 同一個檔案可能有多條規則各留一筆紀錄（舊版本的產物就是這樣），而它們指向
        # 同一組檔案。不去重的話會把同一個檔案開兩次，套用時第二次也只會得到
        # 「與目前內容相同」。
        records = list({r.merged: r for r in records}.values())

        # .merged 必須先存在合併工具才打得開——`code --merge` 的第四個參數是輸出檔，
        # 檔案不存在時只會顯示「無法開啟編輯器，因為找不到檔案」。這裡順便讓舊的
        # 衝突資料夾也能用：缺什麼就補什麼，已經解好的（非空）不動。
        missing = build_all_merged(records, logger, overwrite=False)
        if missing:
            usable = [r for r in records if all(r is not bad for bad, _ in missing)]
            if not usable:
                self._append_log("error", "無法產生待解決的檔案，衝突資料可能已損壞或被刪除。")
                QMessageBox.warning(
                    self, APP_NAME,
                    "無法產生待解決的檔案。\n\n"
                    f"{missing[0][1]}\n\n"
                    f"請確認這個資料夾還在：\n{directory}")
                return
            self._append_log("warn", f"有 {len(missing)} 個檔案無法產生待解決內容，已略過。")
            records = usable

        command = self.settings.get("merge_tool_command", "code")
        # VS Code / Cursor 的 code 是 .cmd 批次檔，而 Windows 的 CreateProcess 不會套用
        # PATHEXT——直接用裸名會得到 WinError 2。which() 解析出含副檔名的完整路徑就啟動
        # 得起來；解析不到時沿用原字串，讓設定成絕對路徑的情況仍然可用。
        resolved = shutil.which(command) or command
        launched, failed = [], []
        for record in records:
            try:
                subprocess.Popen(
                    [resolved, "--merge", record.current, record.profile,
                     record.base, record.merged],
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                launched.append(record)
            except Exception as exc:
                failed.append((record, str(exc)))

        if failed and not launched:
            self._append_log("error", f"無法啟動合併工具「{command}」：{failed[0][1]}")
            QMessageBox.warning(
                self, APP_NAME,
                f"無法啟動合併工具「{command}」。\n\n"
                f"{failed[0][1]}\n\n"
                "可在設定檔 ChangeToDebug_settings.json 的 merge_tool_command 指定路徑，\n"
                "或直接用任何文字編輯器開啟下列資料夾中的 .merged 檔案，\n"
                "檔案裡已經標好 <<<<<<< / ======= / >>>>>>> 三段，改完存檔即可：\n"
                f"{directory}")
            QDesktopServices.openUrl(QUrl.fromLocalFile(directory))
            return

        # 部分失敗時原本什麼都不說，使用者會以為全部都開好了
        for record, why in failed:
            self._append_log("warn", f"這個檔案的合併工具沒開起來：{record.target} -> {why}")

        self._append_log("step", f"已開啟 {len(launched)} 個檔案的合併工具")
        note = ""
        if failed:
            note = (f"\n另有 {len(failed)} 個檔案沒開起來，"
                    "可以直接在資料夾裡編輯它們的 .merged。\n")
        confirm = QMessageBox.question(
            self, APP_NAME,
            f"已在「{command}」開啟 {len(launched)} 個衝突檔案。\n"
            f"{note}\n"
            "檔案裡已經標好衝突的三段（目前 source / base / profile 期望），\n"
            "請解決後**存檔**，全部完成再按「套用」，\n"
            "工具會把結果寫回專案並重新驗證。\n\n"
            "尚未解決、或內容仍留著衝突標記的檔案會自動略過。",
            QMessageBox.Apply | QMessageBox.Cancel, QMessageBox.Apply)
        if confirm != QMessageBox.Apply:
            self._append_log("info", "已取消套用，衝突內容仍保留在資料夾中。")
            return

        result = apply_all(records, logger)

        lines = [f"已套用 {len(result.applied)} 個檔案"]
        if result.skipped:
            lines.append(f"略過 {len(result.skipped)} 個：")
            lines += [f"  {Path(r.target).name}：{why}" for r, why in result.skipped[:10]]
        QMessageBox.information(self, APP_NAME, "\n".join(lines))
        if result.applied:
            self._append_log("ok", f"衝突解決完成，已寫入 {len(result.applied)} 個檔案。"
                                   "建議重新執行一次以確認所有規則都已套用。")
            self._offer_reanchor(result.applied, logger)

    def _offer_reanchor(self, records, logger):
        """解完衝突後，詢問是否把結果寫回 profile，讓同一個衝突不再出現。"""
        from ..core import reanchor

        profile = self.current_profile()
        if profile is None:
            return

        plans, blocked = [], []
        rule_ids = {r.rule_id for r in profile.all_rules}
        project_root = self.path_combo.currentText().strip()
        for record in records:
            # 同一個檔案有多條規則衝突時只有一筆紀錄，rule_id 是 "mod:7,mod:8"；
            # 每條規則各規劃一組錨點，各自從解決後的內容裡挑自己那一段
            for rule_id in [x.strip() for x in record.rule_id.split(",") if x.strip()]:
                if rule_id not in rule_ids:
                    self._append_log("info", f"略過已不存在的規則 {rule_id}（{record.label}）")
                    continue
                result = reanchor.plan(profile, record, logger, project_root=project_root,
                                       rule_id=rule_id)
                (plans if result.ok else blocked).append((record, result))

        if not plans:
            if blocked:
                self._append_log("info", "沒有可自動重新錨定的規則：")
                for record, result in blocked:
                    self._append_log("info", f"  {record.label}：{result.error}")
            return

        lines = [f"已解決 {len(records)} 個衝突。要把結果寫回 profile 嗎？", "",
                 "不寫回的話，換一棵樹或上游再前進時，同樣的衝突要再解一次。", "",
                 f"將為 {profile.title} 的以下規則各新增一組錨點",
                 "（原有的錨點與 base 保留，還沒跟上上游的樹仍然套得上）："]
        lines += [f"　• {result.label or record.label}" for record, result in plans[:10]]
        if len(plans) > 10:
            lines.append(f"　…另有 {len(plans) - 10} 條")
        if blocked:
            lines += ["", f"以下 {len(blocked)} 條無法自動處理，需手動調整："]
            lines += [f"　• {result.label or record.label}：{result.error}"
                      for record, result in blocked[:5]]
        lines += ["", "會先備份 profile.yaml，改完後立即讀回驗證，驗證不過就整個放棄。"]

        confirm = QMessageBox.question(self, APP_NAME, "\n".join(lines),
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if confirm != QMessageBox.Yes:
            self._append_log("info", "未寫回 profile，規則維持原樣。")
            return

        self._append_log("step", "重新錨定 profile")
        done, failed = 0, []
        for record, result in plans:
            ok, message = reanchor.apply(profile, record, result, logger)
            if ok:
                done += 1
            else:
                failed.append((record, message))
                self._append_log("error", f"{result.label or record.label}：{message}")

        QMessageBox.information(
            self, APP_NAME,
            f"已為 {done} 條規則新增錨點" + (f"，{len(failed)} 條失敗" if failed else "") +
            "\n\nprofile.yaml 的舊版本已備份在同一個資料夾（.bak.<時間戳>），\n"
            "新錨點的 base 存在 base\\_anchors\\ 底下。")
        self.reload_profiles(quiet=False)

    def _open_backups(self, preselect=""):
        """列出專案裡的備份檔並讓使用者挑選刪除。"""
        from ..core.backups import scan
        from .backup_dialog import BackupDialog

        base = self.path_combo.currentText().strip()
        if not base or not os.path.isdir(base):
            QMessageBox.warning(self, APP_NAME, "請先選擇有效的專案根目錄。")
            return

        logger = Logger(sink=self._append_log, log_file=self.log_path,
                        echo_stdout=False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            groups = scan(base, logger)
        finally:
            QApplication.restoreOverrideCursor()

        if not groups:
            QMessageBox.information(self, APP_NAME, "這個專案底下沒有備份檔。")
            return

        dialog = BackupDialog(groups, logger, self,
                              stylesheet=build_stylesheet(self.theme_name),
                              preselect=preselect if isinstance(preselect, str) else "")
        dialog.exec_()

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
            merge_fallback=self.merge_box.isChecked(),
        )
        self._launch(request, base)

    def _start_revert(self):
        """把這個世代已套用的修改反向移除。"""
        if self.worker is not None:
            return

        base = self.path_combo.currentText().strip()
        if not base or not os.path.isdir(base):
            QMessageBox.warning(self, APP_NAME, "請先選擇有效的專案根目錄。")
            return
        profile = self.current_profile()
        if profile is None:
            QMessageBox.warning(self, APP_NAME,
                                "請先在「專案世代」選擇要移除哪個世代的修改。")
            return

        page = next((p for p in self.pages if p.task_key == "patchset"), None)
        options = {"patchset": page.collect_options() if page else {}}
        dry_run = self.dry_run_box.isChecked()
        backup = self.backup_box.isChecked()

        regex_rules = sum(1 for r in profile.all_rules if r.regex)
        detail = [f"專案：{base}", f"世代：{profile.title}", ""]
        if dry_run:
            detail.append("目前為預覽模式，只會列出可移除的項目，不會實際修改。")
        else:
            detail.append("這會把此世代已套用的修改**反向還原**，"
                          + ("並在原檔旁建立備份。" if backup else "且不會建立任何備份。"))
        detail += [
            "",
            "移除方式是把 new_code 換回 old_code，只動本 profile 帶來的改動；",
            "上游在這之後的改動不受影響。new_files 帶進來的檔案若內容未被改過會一併刪除。",
        ]
        if regex_rules:
            detail.append(f"\n※ 其中 {regex_rules} 條 regex 規則無法反向推導，會被略過。")
        detail.append("\n※ Driver Debug 與 POST Code Marker 的改動不在此功能範圍內。")
        detail.append("\n確定要繼續嗎？")

        confirm = QMessageBox.question(self, "移除 Change 確認", "\n".join(detail),
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return

        request = RunRequest(
            base_path=base,
            profile=profile,
            task_keys=["patchset"],
            options=options,
            dry_run=dry_run,
            backup=backup,
            enable_all_debug_flags=True,    # 移除時一律涵蓋選配項目，才不會留下殘留
            verify_after_run=self.verify_box.isChecked(),
            merge_fallback=self.merge_box.isChecked(),
            revert=True,
        )
        self._launch(request, base)

    def _launch(self, request, base):
        """把一個 RunRequest 交給背景執行緒，並切換介面狀態。"""
        self._last_was_revert = bool(getattr(request, "revert", False))
        self.settings.push_recent_path(base)
        self._save_settings()
        self._refresh_recent_combo(base)

        self._clear_log()
        self.progress.setRange(0, 0)
        self.progress_label.setText("執行中…")
        self.summary_label.setText("執行中…")
        self.run_btn.setEnabled(False)
        self.revert_btn.setEnabled(False)
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
        if stats.merged:
            parts.insert(2, f"其中合併 {stats.merged}")
        if stats.conflicted:
            parts.append(f"合併衝突 {stats.conflicted}")
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

        if summary.conflicts:
            self._conflict_dir = summary.conflict_dir
            self._append_log("error",
                             f"以下 {len(summary.conflicts)} 個檔案需要人工解決衝突：")
            for record in summary.conflicts[:50]:
                self._append_log("error", f"  {record.target}　({record.label})")
            self._append_log("info", f"三方內容已保存在：{summary.conflict_dir}")

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
        elif summary.conflicts:
            self._append_log("error", "處理完成，但有檔案需要人工解決合併衝突。")
            box = QMessageBox(QMessageBox.Warning, APP_NAME,
                              f"有 {len(summary.conflicts)} 個檔案發生合併衝突，"
                              "這些檔案未被修改。\n\n"
                              f"{text}\n\n"
                              "可以用合併工具逐一處理，或先看衝突內容再決定。",
                              parent=self)
            resolve_btn = box.addButton("解決衝突…", QMessageBox.AcceptRole)
            open_btn = box.addButton("開啟衝突資料夾", QMessageBox.ActionRole)
            box.addButton("稍後處理", QMessageBox.RejectRole)
            box.exec_()
            if box.clickedButton() is resolve_btn:
                self._resolve_conflicts()
            elif box.clickedButton() is open_btn:
                self._open_conflict_dir()
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
        # 不論這次結果落在哪個分支都要問——移除通常都會伴隨一些「找不到片段」，
        # 只在「完全沒有失敗」時才問的話，實務上等於永遠不會出現。
        self._offer_backup_cleanup(summary)

    def _offer_backup_cleanup(self, summary):
        """「移除 Change」跑完後，主動問要不要清掉備份檔。

        移除的用意就是讓樹回到乾淨狀態，但還原本身也是寫入、也會產生備份，
        不清的話 .bak 只會越積越多，而且全部掛在 BIOS repo 的 git status 上。
        """
        if not getattr(self, "_last_was_revert", False):
            return
        if not summary.backup_count:
            return

        box = QMessageBox(
            QMessageBox.Information, APP_NAME,
            f"移除完成，但這次還原又建立了 {summary.backup_count} 個備份檔"
            f"（.bak.{summary.run_stamp}）。\n\n"
            "修改已經還原，這些備份留在 BIOS source 裡會一直出現在 git status。\n"
            "要現在清理嗎？（對話框會列出所有次數的備份，可一併選取）",
            parent=self)
        clean_btn = box.addButton("清理備份…", QMessageBox.AcceptRole)
        box.addButton("先留著", QMessageBox.RejectRole)
        box.exec_()
        if box.clickedButton() is clean_btn:
            self._open_backups(preselect=summary.run_stamp)

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
