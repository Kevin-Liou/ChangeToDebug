# ChangeToDebug

把 HP BIOS source 一鍵切換成 Debug mode 的整合工具（PyQt5 GUI）。

原本分散的兩套工具與一支腳本已整併為單一程式：

| 舊工具 | 現在的位置 |
| --- | --- |
| `Debug/DebugMode_Modify.py`（tkinter，FY25/FY26 YAML patch） | 分頁 **Debug Patch Set** |
| `ChangeToDebug_Controller.py`（PyQt5，Memory / Single Driver Debug） | 分頁 **Driver Debug** |
| `Debug/OutpMarkerGen.py`（`_outp(0x80, XX)` 打點） | 分頁 **POST Code Marker** |

三個功能共用同一套修補引擎、同一份執行記錄，可一次勾選多項依序執行。

---

## 快速開始

```bash
pip install -r requirements.txt
```

```bash
python ChangeToDebug_Start.py
```

1. 選擇 BIOS source 根目錄（含 `.gitman` 的那一層）
2. 工具會自動判斷 FY25 / FY26；判斷不出來時可在「專案世代」手動指定
3. 勾選要執行的功能與選項，按「開始執行」
4. 跑完後工具會自動重新讀檔驗證，摘要列會顯示「驗證通過 N/M」

建議第一次先勾「預覽模式」確認會動到哪些檔案，再實際執行。

---

## 三個功能

### Debug Patch Set

依偵測到的世代套用該世代 profile YAML 中的所有修改（CpuDeadLoop、DebugPrintErrorLevel、PostCode 導向序列埠、各子系統 DEBUG flag 等）。
表格會列出每一條規則，可取消勾選不想套用的項目。

`option_debug_flag` 的意義：

- `false`：必要修改，一定會套用
- `true`：選配修改（log 量大、可能影響時序），只有勾選「啟用所有 Debug Flag」時才套用

### Driver Debug

輸入 driver 的 `.c` 檔名（一行一個），把該檔的 `DEBUG_WARN` / `DEBUG_INFO` 全部改成 `DEBUG_ERROR`。

- **Memory Debug**：另外開啟 `PcdHpMemoryDebugEnable`、把 `DxeMemDebugAcpiArea.c` 的 `IsLegacySupported()` 換成 `0`，並在對應的 `.inf` 補上 `MemoryDebug.dec` 與 `MemDebugLib`
- **Single Driver Debug**：只做 DEBUG 訊息升級

### POST Code Marker

在指定字串（預設 `CpuDeadLoop ();`）前插入遞增的 `_outp(0x80, XX)` 打點，沒有序列埠 log 時可用 POST Code 判斷卡在哪一行。已插入過的位置會自動略過。

---

## 完成後自動驗證

勾選「完成後自動驗證」（預設開啟）時，所有功能跑完後會**重新讀取**每個被修改過的檔案，確認內容真的變成預期的樣子，而不是只相信當下的取代結果。可以抓到寫入被防毒／唯讀屬性擋掉、事後被其他工具還原、或規則本身寫錯等情況。

驗證條件依規則型態自動產生：

| 修改型態 | 驗證方式 |
| --- | --- |
| 一般字串取代 | `new_code` 必須出現；`old_code` 不應再出現（`new_code` 內含 `old_code` 時不檢查） |
| `regex: true` | 原本的 pattern 不應再命中（`new_code` 含 `\1` 回填，無法比對字面值） |
| `new_files` 新增的檔案 | 內容必須與來源檔完全相同 |
| Driver Debug | `DEBUG_WARN` / `DEBUG_INFO` 不應再出現 |
| Memory Debug 的 `.inf` | `MemoryDebug.dec` 與 `MemDebugLib` 必須出現 |
| POST Code Marker | 每個實際用到的 `_outp(0x80,0xXX)` 都必須出現 |

結果會顯示在摘要列（`驗證通過 N/M`）；有任何一項不符會在記錄中列出檔案與原因，並跳出紅色警示。同一個檔案只會重新讀取一次。預覽模式因為沒有實際寫入，會自動略過驗證。

---

## 新增下一個世代

**不需要改任何 Python 程式碼。** 兩種做法，建議用第一種。

### 做法 A：從 code change 的 ORG / MOD 自動產生（建議）

按主畫面的「**產生 Profile…**」，選擇 code change 套件資料夾（底下要有 `ORG\` 與 `MOD\`），填世代代號與偵測資料夾，按「產生並驗證」。

工具會：

1. 只在 `MOD\` 出現的檔案 → 自動列成 `new_files`
2. 兩邊都有的檔案 → 用 diff 取出每個修改片段，**自動往外擴前後文直到該片段在檔案中唯一**
3. `MultiProject\<專案>\` 底下各專案完全相同的修改 → 合併成一條 `file_name` 規則（檔名不同時自動推出 `Z*PkgConfig.dsc` 這種萬用字元）
4. 把產生的 YAML 讀回來逐條比對字串是否完整無誤
5. 複製一份 `ORG\` 實際套用一次，再與 `MOD\` 比對（忽略註解與空行），確認**功能等價**

結果與 YAML 都會顯示出來，可以直接在預覽框編輯後再存到 `profiles\`。

產生出來的規則 `option_debug_flag` 一律是 `false`（必要），哪些要改成選配由你決定。各專案只有註解不同時預設**不合併**，可以勾「忽略註解差異也合併」讓它統一採用第一個專案的版本（會列出被統一的專案）。

### 做法 B：手寫

1. 複製 `profiles\_TEMPLATE.yaml.example` 成 `profiles\FY28.yaml`
2. 改掉 `profile:` 區塊的 `key` / `display_name` / `detect`
3. 填入 `new_files` / `modifications` / `platform_pcd_modifications`
4. 回到工具按「重新載入設定檔」

自動偵測條件寫在 profile 自己身上：

```yaml
profile:
  key: FY27
  display_name: FY27 (Wildcat Lake)
  priority: 27
  detect:
    any:
      - dir: .gitman/Intel/WildcatLakeBoardPkg
```

`priority` 數字小者先比對。支援的判斷類型：`dir`、`file`、`exists`、`glob`。
`profiles\` 內以底線開頭或副檔名不是 `.yaml` / `.yml` 的檔案不會被載入。

profile 可以描述三種修改：

| 區塊 | 用途 |
| --- | --- |
| `new_files` | 把 code change 帶的**全新檔案**複製進專案。來源目錄由 `new_files_dir` 指定（可用絕對路徑指向 code change 套件，不必把 BIOS source 複製進工具 repo）。目標已存在且內容不同時預設**不覆蓋**，回報「已存在且不同」 |
| `modifications` | 以 `sub_path` 精準定位單一檔案做文字取代 |
| `platform_pcd_modifications` | 以 `file_name` 在 `pcd_scan_roots` 底下遞迴搜尋，每個同名檔都套用。`file_name` 支援萬用字元（`Z*PkgConfig.dsc`），用來涵蓋各專案自己命名的設定檔 |

執行順序固定為 `new_files` → `modifications` → `platform_pcd_modifications`。

「插入型」規則（`new_code` 完整包含 `old_code`，例如只是在原內容旁補幾行）是允許的：工具會先確認 `new_code` 是否已存在，已存在就回報「已套用過」，重跑不會重複插入。

profile 搜尋順序（先找到的同名 key 優先）：

1. exe / 專案旁的 `profiles\`
2. 打包進 exe 的 `profiles\`
3. exe / 專案根目錄
4. `Debug\`（相容舊版擺放位置）

也就是說：打包成 exe 後，只要在 exe 旁邊放一個 `profiles\FY27.yaml` 就能新增世代，不必重新 build。

---

## 專案結構

```
ChangeToDebug_Start.py        進入點
changetodebug/
  appinfo.py                  版本、路徑解析（相容 PyInstaller）
  app.py                      argparse + QApplication
  core/
    patcher.py                修補引擎（編碼偵測、換行保留、備份、dry-run）
    profiles.py               profile 載入與自動偵測
    profilegen.py             從 ORG/MOD 自動產生 profile
    verifier.py               完成後重新讀檔驗證
    runner.py                 把選項與 task 串成一次執行
    settings.py               最近路徑 / 選項 / 主題保存
    logbus.py                 統一訊息輸出
    tasks/                    功能實作（新增功能只要在此註冊）
      base.py  patchset.py  driver_debug.py  outp_marker.py
  gui/
    main_window.py  pages.py  theme.py  worker.py  profilegen_dialog.py
profiles/
  FY25.yaml  FY26.yaml  FY27.yaml  _TEMPLATE.yaml.example
```

### 已內建的世代

| Profile | 偵測依據 | 做什麼 |
| --- | --- | --- |
| FY25 (Meteor Lake) | `.gitman/Intel/MeteorLakeBoardPkg` | DEBUG build 上打開更多訊息 |
| FY26 (Panther Lake) | `.gitman/Intel/PantherLakeBoardPkg` | 同上 |
| FY27 (Nova Lake) | `.gitman/Intel/NovaLakeBoardPkg` | **RELEASE build 也輸出 BIOS 與 ACPI debug message**，含 6 個新增檔案 |

FY27 與前兩代性質不同，套用後還有兩件工具不會做的事：新增的 6 個檔案要 `git add`，第一次 build 前要 `touch HpPlatformPkg/AcpiTables/Dt/Dsdt/Dsdt.asl`（否則 build system 不會重編 ACPI table）。詳見 profile 檔開頭的說明與 code change 套件的 README。

新增一個「功能分頁」只要三步：`core/tasks/` 新增一個 `Task` 子類別 → 在 `core/tasks/__init__.py` `register()` → `gui/pages.py` 加一個 `TaskPage` 子類別並放進 `PAGE_CLASSES`。

---

## 其他

- 執行記錄同時顯示在視窗下方並寫入程式目錄的 `ChangeToDebug_log.txt`
- 勾選「備份原始檔案」時，同一次執行的備份共用一組時間戳：`原檔名.bak.<yyyymmddHHMMSS>`
- 設定（最近路徑、選項、主題）存在程式目錄的 `ChangeToDebug_settings.json`；會自動沿用舊版 `last_path_config.json` 的最近路徑
- test build 的 exe 可以在 GitHub Actions 裡找到

### 已移除的舊檔

以下檔案的功能都已併入新程式，已於整併時刪除（tracked 的部分仍可從 git 歷史取回）：

`ChangeToDebug_Controller.py`、`Ui_ChangeToDebug_*.py`、`ChangeToDebug_*.ui`、
`Debug/`（`DebugMode_Modify.py`、`OutpMarkerGen.py`、`modifications_FY2*.yaml`、舊 log 與設定）

`profiles\FY25.yaml` / `FY26.yaml` 的修改內容與原本 `Debug\modifications_FY25.yaml` / `FY26.yaml`
**位元組完全相同**，只是多了最上面的 `profile:` 區塊。
