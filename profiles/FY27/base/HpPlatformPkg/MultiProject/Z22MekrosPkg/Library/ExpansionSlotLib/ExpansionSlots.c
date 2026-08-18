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
#include <PlatformDefinitions.h>
#include <HpPlatformId.h>

static EXPANSION_SLOT_DEFINITION mSlotDefinition[MAX_SLOTS] =
{
//  SlotPos           SlotType
   {CPU_SLOT_EX(5),  PCIE_M2_SSD_SLOT},     // M.2 SSD 1     - CPU PCIe root port 5, Flex I/O lane B8~B11
   {CPU_SLOT_EX(6),  PCIE_M2_SSD_SLOT},     // M.2 SSD 2     - CPU PCIe root port 6, Flex I/O lane B12~B15
   {PCH_SLOT(4),     PCIE_M2_WLAN_BT_SLOT}, // M.2 WLAN/BT   - PCH PCIe root port 4 (00/1C/03), see PcdWlanPcieBridgeNum
};

EXPANSION_SLOT_DEFINITION *
GetSlotDefinition(
   VOID
   )
{
   return mSlotDefinition;
}

