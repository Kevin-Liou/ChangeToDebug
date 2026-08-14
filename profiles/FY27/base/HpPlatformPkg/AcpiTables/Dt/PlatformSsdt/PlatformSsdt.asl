//
// (c) Copyright 2025 - 2026 HP Development Company, L.P.
// This software and associated documentation (if any) is furnished under a license and may only be used or
// copied in accordance with the terms of the license. Except as permitted by such license, no part of this
// software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
// form or by any means without the express written consent of HP Development Company.
//
// File Name: PlatformSsdt.asl
//
// Abstract: Sync with Intel\NovaLakeBoardPkg\Acpi\AcpiTables\PlatformSsdt\PlatformSsdt.asl
//
/** @file
  ACPI Platform SSDT table for TBD

  @copyright
  INTEL CONFIDENTIAL
  Copyright (C) 2025 Intel Corporation.

  This software and the related documents are Intel copyrighted materials,
  and your use of them is governed by the express license under which they
  were provided to you ("License"). Unless the License provides otherwise,
  you may not use, modify, copy, publish, distribute, disclose or transmit
  this software or the related documents without Intel's prior written
  permission.

  This software and the related documents are provided as is, with no
  express or implied warranties, other than those that are expressly stated
  in the License.

  @par Specification Reference:
**/

#include "PlatformBoardId.h"
#include <Library/PchInfoDefs.h>
//[HP_MOD]+ add only
#include <CoreLongNameMapAsl.h>
#include <HpGfxMiscLongNameMapAsl.h>
#include <GfxAcpiDebugPrint.h>
#include <HpFeatureMiscLongNameMapAsl.h>
#include <GfxAcpiDef.h>
#include <ConDevLongNameMapAsl.h>
#include <ConDevAcpiDef.h>
#include <HpIntelChipsetLongNameMapAsl.h>
#include <NvidiaGraphicsLongNameMapAsl.h>
#include <PlatLongNameMapAsl.h>
#include <DsdtDef.h>
#include "HpSioLongNameMapAsl.h"
#include <HpPrivateWmiSureStartSymbols.h>
#include "HpPrivateWmiEventIds.h"
#include <AcpiAsl.h>
#include "HpSioSharedAslDef.h"          // HP: various common code including SioAcpiAreaData ASL memory  

//[HP_MOD]-
#define LCH_ENABLED       0x01
#define LCH_LINK_NUMBER   0x00
#define LCH_FLASH_NUMBER  0x00
//[HP_MOD]+
//#define LCH_INTERFACE_USB 0x01
//#define LCH_LINK_NUMBER   0x01
//[HP_MOD]-
#define VGPIO_PIN3        0x03

DefinitionBlock (
  "PlatformSsdt.aml",
  "SSDT",
  0x02,
  "INTEL ",
  "PlatSsdt",
  0x1000
  )
{
  External (\ADBG, MethodObj)

//[HP_MOD]+ add only
  External (AcquireWmiResource, MethodObj)
  External (ReleaseWmiResource, MethodObj)
  External (\_SB.GGIV, MethodObj)
  External (\_SB.PC00.GFX0, DeviceObj)
  External (\_SB.OutDbgW, MethodObj)
  External (\_SB.SWSMI, MethodObj)
  External (\_SB.IntelChipsetWAKControl, MethodObj)
  External (OSYS)
  External (\DisplayCap, FieldUnitObj)
  External (\DisplayExt, FieldUnitObj)
  External (DGS_Next, FieldUnitObj)
  External (DCS_Attach, FieldUnitObj)
  External (GenerateSwSmi, MethodObj)
  External (MscExitSwSmiNum, FieldUnitObj)
  External (MscEntrySwSmiNum, FieldUnitObj)
  External (\_SB.WMIV.GeneratePrivateWmiEvent, MethodObj)
  External (\_SB.WMIB.InvalidatePublicWmiCache, MethodObj)
  External (HpGenerateSwSmi, MethodObj)
  External (FanConfiguration1, FieldUnitObj)
  External (FanConfiguration2, FieldUnitObj)
  External (FanConfiguration3, FieldUnitObj)
  External (FanConfiguration4, FieldUnitObj)
  External (SerialPortPresent, FieldUnitObj)
  External (ParallelPortPresent, FieldUnitObj)
  External (EAX, FieldUnitObj)
  External (EBX, FieldUnitObj)
  External (ECX, FieldUnitObj)
  External (EDX, FieldUnitObj)
  External (FanStallEvent, FieldUnitObj)
  External (ThermalEvent, FieldUnitObj)
  External (HoodSensorEvent, FieldUnitObj)
  External (SMBAlertEvent, FieldUnitObj)
  External (ComAnBSwap, FieldUnitObj)
  External (LockResource, FieldUnitObj)
  External (ComAIrq, FieldUnitObj)
  External (ComBIrq, FieldUnitObj)
  External (ComCIrq, FieldUnitObj)
  External (ComDIrq, FieldUnitObj)
  External (UsbCDockFanStallEvent, FieldUnitObj)
  External (UsbCDockThermalEvent, FieldUnitObj)
  External (ComAIo, FieldUnitObj)
  External (ComBIo, FieldUnitObj)
  External (ComCIo, FieldUnitObj)
  External (ComDIo, FieldUnitObj)
  External (SioWmiEventNotified, FieldUnitObj)
  External (Sio1DeviceFlag, FieldUnitObj)
  External (Sio2DeviceFlag, FieldUnitObj)
  External (_PBS, MethodObj)
  External (HPSF, FieldUnitObj)
//[HP_MOD]-

  #define INT_LEVEL_TRIG  0
  #define INT_ACTIVE_LOW  0

  #define CONVERTIBLE_BUTTON   6
//[HP_MOD]+
  #define EC_RUNBit         0x46   // for Sio runtime events

//[HP_MOD]-
  Include ("PlatformSsdtExternal.asl")

  ADBG ("[PlatformSSDT][AcpiTableEntry]")
  
//[HP_MOD]+
//  ADBG ("Include Ipf.asl")
//  Include ("Ipf.asl")
//[HP_MOD]-

  ADBG ("Include LpcB.asl")
  Include ("LpcB.asl")

//[HP_MOD]+
//  ADBG ("Include Video.asl")
//  Include ("Video.asl")
  // Note: Due to Intel IGD device (B0, D2, F0) and PEG (B0, D1, F0) device define on HostBus.ASL
  // If occurs 0xA5 ACPI BIOS ERROR maybe need check this device define in Platform (DSDT table) or not.
  Include ("IGPU.asl")               // Intel IGD device (B0, D2, F0)
#if INTEL_HYBRID_GRAPHICS_SUPPORT
  Include ("DGPU.asl")           // Intel PEG (B0, D1, F0) or PCH's PCIe and its AMD/NVidia dGPU common code
#endif
//[HP_MOD]-

  ADBG ("Include Gpe.asl")
  Include ("Gpe.asl")

  If (LEqual (LCHS,1)) {
    Include ("Lch.asl")
  }

  If (LEqual (PCHA, 0)) {
    Include ("Pld.asl")
  }

  Include ("HdaCodecsDevices.asl")
  Include ("HdaDspModules.asl")
  
  Include ("HidPlatformEventDev.asl")

  Include ("Platform.asl")

  Include ("SataRtd3Puis.asl")
  Include ("LinkDevices.asl")
  Include ("UsbBuffers.asl")


  ADBG ("[PlatformSSDT][AcpiTableExit]")

}