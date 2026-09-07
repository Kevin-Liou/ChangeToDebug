# ChangeToDebug — 接手須知

給接手這個 repo 的人（或 AI）看的一頁。功能與用法在 [README.md](README.md)，這裡只寫**改程式時必須知道、README 不會講**的事。

## 先跑檢查

```bash
python tests/run_checks.py
```

全部在暫存目錄裡用合成的迷你 profile 與假 BIOS 樹跑，不碰真實資料，約 30 秒。
`check_live_env.py` 會額外對 `profiles/` 底下真實的 FY25/26/27 做載入檢查，並在
`G:\HpNvlPlat1` 存在時跑一次 FY27 的**預覽模式**（唯讀）；沒有那棵樹就自動跳過。

改了 `core/` 任何東西都要跑；改了 `gui/` 至少跑 `check_gui_theme.py` 與 `check_conflict_gui.py`。

## 不變量（破了就是 bug）

- **衝突時原檔一個位元組都不動**，也**絕不**把 `<<<<<<<` 寫進 BIOS source。三方內容寫到工具目錄的 `ChangeToDebug_conflicts/`，原檔保持乾淨。同一個檔案有任何一條規則衝突，該檔先前成功的規則要**整檔回滾**（`patchset._rollback`）。「大部分套上、少數沒套」的樹很可能 build 得過然後燒出行為不明的 BIOS，比 build 不過危險。
- **profile.yaml 只能定點文字置換，絕不 `yaml.dump`** 整份寫回——會把使用者的註解與排版全部吃掉。`reanchor.rewrite` / `set_field` / `append_anchor` 都是逐行找位置插入或替換，改完必須 `_verify()` 讀回比對「只有目標欄位變、其餘一字不動」，驗不過就整個放棄。
- **重新錨定是新增錨點，不是覆蓋。** 原本的 `old_code`/`new_code` 與主 base 一律保留，還沒跟上上游的樹才套得上。主 base 與 `base_manifest.yaml` 在重新錨定時完全不碰。
- `rule_id`（`mod:N` / `pcd:N` / `new:N`）是規則在 YAML 裡的**位置**。刪一條、後面全移。manifest 以它當 key，所以載入時 `BaseSnapshot.realign()` 依 `sub_path`/`label` 重新對應；衝突索引、`EXPECT_COUNT.md` 這類外部紀錄裡的 rule_id 在規則增刪後就不可信。
- 借用別的專案的 base（`BaseRef.approximate`）**不報衝突**，退回「找不到片段」。跨專案的檔案本來就不同，報成衝突只是噪音。
- `MIN_BASE_SIMILARITY = 0.5`：base 與現況不像就不 merge。3-way 合完還要確認 `added_lines()`（本規則實際新增的行）都在結果裡，否則寧可宣告失敗。
- `expect_count` 宣告了就必須剛好相符，多一處也不寫入。`old_code` 只保證在產生 profile 那份 source 中唯一。

## 脆弱點

- **YAML 區塊純量 `|2+`**（產生器預設）的尾端空行是值的一部分。在規則尾端插東西要插在整個規則範圍之後（含那些空行），且錨點內把單行純量放最後，否則讀回驗證會說 `new_code` 被動到。踩過一次。
- 合併工具存檔常砍行尾空格，`reanchor.plan` 會先濾掉純空白 hunk；多段改動時用 `added_lines` 挑屬於本規則的那段。同檔多規則的衝突紀錄 `rule_id` 是 `mod:7,mod:8`，要拆開逐條規劃。
- `_absorb()`：同檔第二條衝突規則併入第一筆紀錄，`.profile` 用三方合併疊加。
- QSS 一旦接管 `QComboBox::drop-down` / `QSpinBox` 按鈕，Qt 就不畫原生箭頭，而 CSS 邊框三角形在 Qt 是**長方形**。箭頭是執行時畫成 PNG 放系統暫存目錄（`theme._arrow_image`），產圖失敗就整段不輸出。
- `code` 在這台機器上是 Cursor 的 `.cmd`，Windows 的 `CreateProcess` 不套 PATHEXT，啟動前要 `shutil.which()`。`code --merge` 的四個檔案必須**都存在**。
- `pythonw.exe` 下 `sys.stdout` 是 `None`，`app._ensure_streams()` 先接上假串流；`.pyw` 進入點啟動失敗會寫 `ChangeToDebug_error.txt` 並跳訊息框。

## 環境

- Windows 11、Python 3.11、PyQt5 5.15。`core.autocrlf=true`，git 會一直警告 LF/CRLF，正常。
- 測試與任何離線腳本要 `QT_QPA_PLATFORM=offscreen`；主控台印中文要 `PYTHONIOENCODING=utf-8`（cp1252 會炸）。
- `G:\HpNvlPlat1~4`、`G:\Ptl*` 是使用者**活的** BIOS 工作樹。只能讀；要套用測試一律先複製到暫存目錄。不要在那些樹裡留檔案（`.bak.*` 會出現在它們的 `git status`）。
- 工具目錄下的 `ChangeToDebug_settings.json`、`ChangeToDebug_log.txt`、`ChangeToDebug_conflicts/`、`*.bak.20*` 都是執行期產物，已 gitignore。測試要用 `Settings(path=暫存檔)`，否則會寫回使用者的設定。

## Git 規矩

- 只 `git add` 任務相關路徑（`changetodebug/`、`profiles/`、`README.md`、`tests/`…），**不要 `git add .`**。
- 使用者要求才 commit / push；commit 訊息用中文寫「為什麼」，標題格式 `vX.Y.Z: short english summary`。
- 版本號在 `changetodebug/appinfo.py` 的 `APP_VERSION`；README 有「版本紀錄」一節要同步。

## 已知限制 / 待辦

- `file_name` 型規則（如 `DriverEntry.c`）會掃到樹裡全部同名檔，不相干的那些以「找不到片段」收場，數量可觀但無害。
- 重新錨定假設一條規則只改一段；同一條規則的解決結果散在兩段時會拒絕，要手動調整 profile。
- 錨點的 `covers` 只記錄解衝突時那一個檔案；`file_name` 型規則跨專案借用錨點 base 時標 approximate，走保守路徑。
- `profiles/EXPECT_COUNT.md` 是 v3.1.0 之前那份舊 FY27 的量測，規則編號已不對。`expect_count` 目前沒宣告在任何規則上。
- FY26 有 2 條 `old_code == new_code` 的死規則，使用者決定暫不處理。
- GUI 裡「清理備份…」「解決衝突…」「盤點命中數…」「擷取 base 快照…」只做過 offscreen 流程驗證，真人點擊由使用者驗。
- `profiles/FY27/base/_anchors/20260907121252/.../ExpansionSlots.c` 是規則刪除後留下的孤兒錨點 base，無人引用。
