# expect_count 盤點記錄

`old_code` 只保證在「產生 profile 當下的那份 source」中唯一。上游後來新增相似區塊時，
同一條規則可能命中多處，而修補引擎是**整檔取代所有出現處**——它會安靜地把好幾個地方
一起改掉，執行記錄只寫一句「已修改 N 處」。比對失敗至少會叫，這個不會。

`expect_count` 就是擋這件事的守門欄位：宣告後，命中數與宣告不符時該規則會**報錯且不寫入**。
這份文件記錄各規則在實際 source tree 中量到的命中數，供日後決定要不要寫進 profile。

> 工具裡的「**盤點命中數…**」按鈕可以隨時重新量測，並直接把結果寫回 profile。
> 這份文件是量測記錄，**尚未寫入任何 profile**。

- 量測日期：2026-08-15
- 工具版本：v3.0.0
- 量測方式：唯讀，只統計 `old_code` 在各目標檔中的出現次數

### 表格怎麼看

| 格子內容 | 意思 |
| --- | --- |
| `12 檔 × 1` | 找到 12 個目標檔，**每個檔各命中 1 處** |
| `1 檔 × 6` | 找到 1 個目標檔，該檔內命中 **6 處**——套用時會一次改 6 個地方 |
| `0（N 檔皆已套用或不符）` | 找得到檔案但 `old_code` 沒命中，通常代表**那棵樹已經套用過**此修改 |
| `—` | 該樹中找不到目標檔 |
| `regex` | regex 規則不適用 `expect_count` |

建議值只在**所有量測到的樹都得到同一個數字**時才給；跨樹不一致就不建議宣告。

## 量測用的 source tree

| Profile | Source tree | HEAD |
| --- | --- | --- |
| FY27 | `G:\HpNvlPlat1` | `a0156acc` |
| FY27 | `G:\HpNvlPlat2` | `8f2d73ed` |
| FY27 | `G:\HpNvlPlat3` | `c6d849e7` |
| FY26 | `G:\Ptl` | `e0aab086` |
| FY25 | `G:\Code\HpCode\HpArlSDt_main` | `0c138251` |

## FY27 (Nova Lake)

| 規則 | 區塊 | 目標 | HpNvlPlat1 | HpNvlPlat2 | HpNvlPlat3 | 建議值 |
| --- | --- | --- | --- | --- | --- | --- |
| `mod:0` | mod | `HpPlatformPkg/HpPlatformPkg.dec` | 0（1 檔皆已套用或不符） | 0（1 檔皆已套用或不符） | 0（1 檔皆已套用或不符） | — |
| `mod:1` | mod | `HpPlatformPkg/HpPlatformPkg.dsc` | 0（1 檔皆已套用或不符） | 0（1 檔皆已套用或不符） | 0（1 檔皆已套用或不符） | — |
| `mod:2` | mod | `HpPlatformPkg/AcpiTables/Dt/PlatformSsdt/PlatformSsdt.asl` | 0（1 檔皆已套用或不符） | 0（1 檔皆已套用或不符） | 0（1 檔皆已套用或不符） | — |
| `mod:3` | mod | `HpPlatformPkg/HpPlatformServices/Smm/HpPlatformSmmServices.inf` | 0（1 檔皆已套用或不符） | 1 檔 × 1 | 0（1 檔皆已套用或不符） | **1** |
| `mod:4` | mod | `HpPlatformPkg/HpPlatformServices/Smm/HpPlatformSmmServices.c` | 0（1 檔皆已套用或不符） | 1 檔 × 1 | 0（1 檔皆已套用或不符） | **1** |
| `mod:5` | mod | `HpPlatformPkg/HpPlatformServices/Smm/HpPlatformSmmServices.c` | 0（1 檔皆已套用或不符） | 1 檔 × 1 | 0（1 檔皆已套用或不符） | **1** |
| `pcd:0` | pcd | `Z*PkgConfig.dsc` | 0（11 檔皆已套用或不符） | 9 檔 × 1 | 0（11 檔皆已套用或不符） | **1** |
| `pcd:1` | pcd | `PlatformPkgConfig.dsc` | 0（12 檔皆已套用或不符） | 10 檔 × 1 | 0（12 檔皆已套用或不符） | **1** |
| `pcd:2` | pcd | `PlatformPcdConfig.dsc` | 0（12 檔皆已套用或不符） | 8 檔 × 1 | 0（12 檔皆已套用或不符） | **1** |
| `pcd:3` | pcd | `PlatformPcdConfig.dsc` | 0（12 檔皆已套用或不符） | 8 檔 × 1 | 0（12 檔皆已套用或不符） | **1** |
| `pcd:4` | pcd | `PlatformPcdConfig.dsc` | 12 檔 × 1 | 12 檔 × 1 | 12 檔 × 1 | **1** |
| `pcd:5` | pcd | `HpFeatureMiscConfig.dsc` | 12 檔 × 1 | 12 檔 × 1 | 12 檔 × 1 | **1** |
| `pcd:6` | pcd | `PlatformPortingPei.inf` | 0（11 檔皆已套用或不符） | 5 檔 × 1 | 3 檔 × 1 | **1** |
| `pcd:7` | pcd | `DriverEntry.c` | 11 檔 × 1 | 11 檔 × 1 | 11 檔 × 1 | **1** |
| `pcd:8` | pcd | `DriverEntry.c` | 0（28 檔皆已套用或不符） | 11 檔 × 1 | 9 檔 × 1 | **1** |
| `pcd:9` | pcd | `PlatformBootOrderLib.inf` | 0（12 檔皆已套用或不符） | 2 檔 × 1 | 0（12 檔皆已套用或不符） | **1** |
| `pcd:10` | pcd | `PlatformBootOrderLib.c` | 0（12 檔皆已套用或不符） | 6 檔 × 1 | 5 檔 × 1 | **1** |
| `pcd:11` | pcd | `PlatformBootOrderLib.c` | 0（12 檔皆已套用或不符） | 12 檔 × 1 | 10 檔 × 1 | **1** |

可安心宣告 **15** 條（共 18 條）。三棵樹的 HEAD 各不相同，量到的數字仍然一致——這是 `expect_count` 值得信任的依據。

## FY26 (Panther Lake) （目前未使用）

| 規則 | 區塊 | 目標 | Ptl | 建議值 |
| --- | --- | --- | --- | --- |
| `mod:0` | mod | `.gitman/Edk2/MdePkg/Library/BaseLib/CpuDeadLoop.c` | 1 檔 × 1 | **1** |
| `mod:1` | mod | `.gitman/HpCoreMirror/Edk2/MdePkg/Library/BaseLib/CpuDeadLoop.c` | 1 檔 × 1 | **1** |
| `mod:2` | mod | `.gitman/HpCoreMirror/HpTools/fixup.py` | 0（1 檔皆已套用或不符） | — |
| `mod:3` | mod | `.gitman/HpCoreMirror/HpTools/fixup.py` | 0（1 檔皆已套用或不符） | — |
| `mod:4` | mod | `.gitman/Intel/ClientOneSiliconPkg/IpBlock/P2sb/LibraryPrivate/PeiDxeSmmP2SbSidebandAccessLib/PeiDxeSmmP2SbSidebandAccessLib.c` | — | — |
| `mod:5` | mod | `HpPlatformPkg/BuildOptions.dsc` | 1 檔 × 1 | **1** |
| `mod:6` | mod | `HpPlatformPkg/BuildOptions.dsc` | 1 檔 × 1 | **1** |
| `mod:7` | mod | `HpPlatformPkg/HpPlatformPkg.dsc` | 0（1 檔皆已套用或不符） | — |
| `mod:8` | mod | `HpPlatformPkg/HpPlatformPkg.dsc` | 0（1 檔皆已套用或不符） | — |
| `mod:9` | mod | `HpPlatformPkg/HpPlatformPkg.dsc` | 0（1 檔皆已套用或不符） | — |
| `mod:10` | mod | `HpPlatformPkg/HpPlatformPkg.dsc` | 1 檔 × 6 | **6** ⚠ |
| `mod:11` | mod | `HpPlatformPkg/HpPlatformPkg.dsc` | 1 檔 × 1 | **1** |
| `mod:12` | mod | `HpPlatformPkg/18M_FlashMap.fdf` | — | — |
| `pcd:0` | pcd | `PlatformPcdConfig.dsc` | 1 檔 × 1 | **1** |
| `pcd:1` | pcd | `PlatformPcdConfig.dsc` | 5 檔 × 1 | 死規則（`old_code` == `new_code`），宣告無意義 |
| `pcd:2` | pcd | `PlatformPcdConfig.dsc` | 1 檔 × 1 | **1** |
| `pcd:3` | pcd | `PlatformPcdConfig.dsc` | 5 檔 × 1 | **1** |
| `pcd:4` | pcd | `PlatformPcdConfig.dsc` | 1 檔 × 1 | **1** |
| `pcd:5` | pcd | `HpFeatureMiscConfig.dsc` | 5 檔 × 1 | 死規則（`old_code` == `new_code`），宣告無意義 |
| `pcd:6` | pcd | `HpConnectionDeviceConfig.dsc` | 1 檔 × 1 | **1** |
| `pcd:7` | pcd | `18M_FlashMap.fdf` | 1 檔 × 1 | **1** |
| `pcd:8` | pcd | `18M_FlashMap.fdf` | 1 檔 × 1 | **1** |

可安心宣告 **13** 條（共 22 條）。

## FY25 (Meteor Lake) （目前未使用）

| 規則 | 區塊 | 目標 | HpArlSDt_main | 建議值 |
| --- | --- | --- | --- | --- |
| `mod:0` | mod | `.gitman/Edk2/MdePkg/Library/BaseLib/CpuDeadLoop.c` | 1 檔 × 1 | **1** |
| `mod:1` | mod | `.gitman/HpCoreMirror/Edk2/MdePkg/Library/BaseLib/CpuDeadLoop.c` | 1 檔 × 1 | **1** |
| `mod:2` | mod | `.gitman/HpCoreMirror/HpUnitTestPkg/Edk2/MdePkg/Library/BaseLib/CpuDeadLoop.c` | — | — |
| `mod:3` | mod | `.gitman/HpIntel/HpIntelChipsetPkg/HpRcPolicyWmiSmm/HpRcPolicyWmiSmm.c` | — | — |
| `mod:4` | mod | `.gitman/HpCoreMirror/HpTools/fixup.py` | 0（1 檔皆已套用或不符） | — |
| `mod:5` | mod | `.gitman/HpCoreMirror/HpTools/fixup.py` | 1 檔 × 1 | **1** |
| `mod:6` | mod | `.gitman/Intel/ClientOneSiliconPkg/IpBlock/P2sb/LibraryPrivate/PeiDxeSmmP2SbSidebandAccessLib/PeiDxeSmmP2SbSidebandAccessLib.c` | 1 檔 × 1 | **1** |
| `mod:7` | mod | `.gitman/HpFeature/HpFeature/HpConnectionDevicePkg/PubSrcPkg/HpWireless/DT/WirelessDevsDxe/WirelessDevsDxe.c` | 0（1 檔皆已套用或不符） | — |
| `mod:8` | mod | `HpPlatformPkg/BuildOptions.dsc` | 1 檔 × 1 | **1** |
| `mod:9` | mod | `HpPlatformPkg/PlatformPkg.dsc` | 1 檔 × 1 | **1** |
| `mod:10` | mod | `.gitman/HpFeature/HpFeature/HpFeatureErrorHandling/PubSrcPkg/RtsCallbackHandler/PostCode/PostCode.c` | 0（1 檔皆已套用或不符） | — |
| `pcd:0` | pcd | `PlatformPcdConfig.dsc` | 0（7 檔皆已套用或不符） | — |
| `pcd:1` | pcd | `PlatformPcdConfig.dsc` | 7 檔 × 1 | **1** |
| `pcd:2` | pcd | `HpFeatureMiscConfig.dsc` | 7 檔 × 1 | **1** |
| `pcd:3` | pcd | `HpConnectionDeviceConfig.dsc` | 7 檔 × 1 | **1** |
| `pcd:4` | pcd | `ChipsetPcdConfig.dsc` | 7 檔 × 1 | **1** |
| `pcd:5` | pcd | `PlatformPcdConfig.dsc` | 7 檔 × 1 | **1** |

可安心宣告 **11** 條（共 17 條）。

## 需要人工判斷的項目

以下規則在單一檔案內命中**超過一處**。可能是刻意的（例如同一個 PCD 在多個
`[LibraryClasses.*]` 區段都要改），也可能是上游新增了相似區塊而誤中——
**寫入前請先確認**：

- **FY26 `mod:10`**　`HpPlatformPkg/HpPlatformPkg.dsc`　命中 **6** 處

## 要寫進 profile 的話

兩種方式，效果相同：

1. **工具**：選好專案路徑與世代 → 按「盤點命中數…」→ 勾選要寫入的規則 → 「寫入 expect_count」。
   會先備份 `profile.yaml`，改完立即讀回驗證，驗證不過就整個放棄。
2. **手改**：在該規則底下加一行，例如

```yaml
  - file_name: 'PlatformPcdConfig.dsc'
    label: '...'
    expect_count: 1
    old_code: |2
      ...
```

未宣告 `expect_count` 的規則維持原本行為（不檢查命中數）。
