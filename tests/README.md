# tests

```bash
python tests/run_checks.py             # 全部，約 30 秒
python tests/run_checks.py anchors     # 只跑名字含 anchors 的
```

沒有 pytest 相依，每支 `check_*.py` 都是獨立腳本，exit code 非零即失敗。

| 檔案 | 檢查什麼 |
| --- | --- |
| `check_threeway.py` | diff3 合併分類、衝突標記輸出與偵測、`added_lines` |
| `check_conflicts.py` | 衝突產物寫出、同檔多規則併筆、`.merged` 產生、寫回專案的五道把關 |
| `check_anchors.py` | **主流程**：迷你 profile 套舊樹 → 套新樹衝突 → 解決 → 新增錨點 → 新舊樹都套得上；manifest 對齊 |
| `check_conflict_gui.py` | 主視窗「解決衝突…」按下去的整條路徑（Popen 與對話框都換成假的） |
| `check_gui_theme.py` | 主題色票、對比度、切換、下拉與微調框的箭頭 |
| `check_live_env.py` | repo 內真實 FY25/26/27 能載入；有 `G:\HpNvlPlat1` 時跑一次預覽（唯讀），沒有就跳過 |

## 夾具

`_common.py` 產生一個**合成的迷你 profile**（4 條規則：sub_path 型兩個檔、同檔兩條、`Z*PkgConfig.dsc` 萬用字元）與三棵假 BIOS 樹：

- `old`：改動前原樣（= base），全部規則精確命中
- `new`：上游改到規則要改的那幾段，三條 sub_path 規則衝突（其中兩條同檔，會併成一筆 `mod:1,mod:2`）
- `newer`：上游改的是別處，精確比對失敗但 3-way 合得起來

全部在暫存目錄裡，衝突產物用 `redirect_conflicts()` 導開，GUI 用 `Settings(path=暫存檔)`。**不會**碰工具目錄的設定 / log / `ChangeToDebug_conflicts/`，也不會碰 `profiles/` 底下的真實 profile 或使用者的 BIOS 樹（`check_conflict_gui.py` 結尾會用位元組比對確認）。

## 新增檢查

複製一支 `check_*.py`，用 `Checker` 做斷言、`finish()` 收尾；需要 profile 就 `make_profile(tmp)` + `load_mini(tmp)`，需要樹就 `make_tree(tmp/"x", "new")`。`run_checks.py` 會自動撿起來。
