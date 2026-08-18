//
// (c) Copyright 2012 - 2026 HP Development Company, L.P.
// This software and associated documentation (if any) is furnished under a license and may only be used or
// copied in accordance with the terms of the license. Except as permitted by such license, no part of this
// software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
// form or by any means without the express written consent of HP Development Company.
//



#include <Uefi.h>
#include <ExpansionSlotConfig.h>
#include <Library/ExpansionSlotLib.h>
#include <Library/PcdLib.h>
#include <Library/HpGpioLib.h>
#include <GpioV2Pad.h>
#include <Nvl/Pch/GpioV2PinsNvlPchS.h>
#include <PlatformDefinitions.h>
#include <HpPlatformId.h>

#define HPGP_GFX_ID0            GPIOV2_NVL_PCH_S_GPP_B_7
#define HPGP_GFX_ID1            GPIOV2_NVL_PCH_S_GPP_B_8
#define HPGP_GFX_ID2            GPIOV2_NVL_PCH_S_GPP_B_9

#define OPTION_CARD_NONE        0x00    // No option card
#define OPTION_CARD_BOPPER      0x02    // RTX5050 50W GN22-X2 8GB - dGPU
#define OPTION_CARD_BABBAGE     0x03    // 1x M.2 SSD Adapter      - M.2 SSD 3

//
// HpDtPortingExpansionSlotConfigDxe names the M.2 SSD slots by the order they appear in this table,
// so the first PCIE_M2_SSD_SLOT entry becomes "M.2 SSD 1", the second "M.2 SSD 2" and so on.
//
// ExpansionSlotConfig->ExpansionSlotEnabled[] is indexed by table position, so the optional M.2 SSD 3
// entry is appended after M.2 WLAN/BT. That keeps the index of every always present slot the same no
// matter whether the option card is installed.
//
static EXPANSION_SLOT_DEFINITION mSlotDefinition[MAX_SLOTS] =
{
//  SlotPos           SlotType
   {CPU_SLOT_EX(5),  PCIE_M2_SSD_SLOT},     // M.2 SSD 1     - CPU PCIe root port 5, Flex I/O lane B8~B11, J39
   {CPU_SLOT_EX(6),  PCIE_M2_SSD_SLOT},     // M.2 SSD 2     - CPU PCIe root port 6, Flex I/O lane B12~B15, J40
   {PCH_SLOT(4),     PCIE_M2_WLAN_BT_SLOT}, // M.2 WLAN/BT   - PCH PCIe root port 4 (00/1C/03), see PcdWlanPcieBridgeNum
};

//
// Manaan PG with the Babbage "1x M.2 SSD Adapter" option card installed on the PCIe x16 slot.
//
static EXPANSION_SLOT_DEFINITION mSlotDefinitionWithThirdSsd[MAX_SLOTS] =
{
//  SlotPos           SlotType
   {CPU_SLOT_EX(5),  PCIE_M2_SSD_SLOT},     // M.2 SSD 1     - CPU PCIe root port 5, Flex I/O lane B8~B11, J39
   {CPU_SLOT_EX(6),  PCIE_M2_SSD_SLOT},     // M.2 SSD 2     - CPU PCIe root port 6, Flex I/O lane B12~B15, J40
   {PCH_SLOT(4),     PCIE_M2_WLAN_BT_SLOT}, // M.2 WLAN/BT   - PCH PCIe root port 4 (00/1C/03), see PcdWlanPcieBridgeNum
   {CPU_SLOT_EX(3),  PCIE_M2_SSD_SLOT},     // M.2 SSD 3     - CPU PCIe root port 3, Flex I/O lane B0~B7, Babbage option card
};

/**
  @brief Report whether the Babbage "1x M.2 SSD Adapter" option card is installed.

  Only Manaan PG boards carry the PCIe x16 option card connector, Manaan P and Manaan M do not. The
  dGPU option cards use the same connector, so they are mutually exclusive with the third M.2 SSD.

  @retval TRUE    The option card providing M.2 SSD 3 is installed.
  @retval FALSE   No option card, or a dGPU option card, is installed.
**/
static
BOOLEAN
IsThirdSsdCardInstalled (
   VOID
   )
{
   UINT8  OptionCardId;

   if (PcdGet16 (PcdDtPcaId) != BOARD_ID_DM800_PG)
   {
      return FALSE;
   }

   OptionCardId = (UINT8)((HpGpioRead (HPGP_GFX_ID2) << 2) |
                          (HpGpioRead (HPGP_GFX_ID1) << 1) |
                          HpGpioRead (HPGP_GFX_ID0));

   return (BOOLEAN)(OptionCardId == OPTION_CARD_BABBAGE);
}

EXPANSION_SLOT_DEFINITION *
GetSlotDefinition(
   VOID
   )
{
   if (IsThirdSsdCardInstalled ())
   {
      return mSlotDefinitionWithThirdSsd;
   }

   return mSlotDefinition;
}

