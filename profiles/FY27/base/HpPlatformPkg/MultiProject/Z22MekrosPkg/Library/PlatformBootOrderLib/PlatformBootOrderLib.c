//
// (c) Copyright 2014 - 2026 HP Development Company, L.P.
// This software and associated documentation (if any) is furnished under a license and may only be used or
// copied in accordance with the terms of the license. Except as permitted by such license, no part of this
// software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
// form or by any means without the express written consent of HP Development Company.
//
// Module Name: PlatformBootOrderLib.c
//
//

// #define BOOTORDER_DEBUG
#ifdef  BOOTORDER_DEBUG
  #pragma optimize ("",off)
#define BOOTORDER_PRINT   DEBUG
#else
#define BOOTORDER_PRINT(Expression)
#endif

#define BOOTORDER_ERR_LVL     (EFI_D_INFO | EFI_D_ERROR)

#include <PiDxe.h>
#include <HpBase.h>
#include <HpDebugPrint.h>
#include <Library/CoreBootManagerLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/HiiLib.h>
#include <Library/BaseLib.h>
#include <Library/UefiLib.h>
#include <Library/DevicePathLib.h>
#include <Library/HpDevicePathLib.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Protocol/HpPlatformServicesProtocol.h>
#include <Library/HpCommonPlatformBootOrderLib.h>
#include <IntelCommonBootOrderForTwoChip.h>
#include <Library/HpStorageBootOrderLib.h>
#include <PlatformDefinitions.h>
#include <Library/PcdLib.h>
#include <HpGfxMiscSetup.h>
#include <Library/HpGetVariableLib.h>
#include <Library/PciSegmentLib.h>
#include <IndustryStandard/Pci.h>


// ---------------------------------------------------------------------------------------------------------------------
// Local Macro Definitions
// ---------------------------------------------------------------------------------------------------------------------
#define M2_SSD_ROOT_PORT_DEVICE     0x06
#define M2_SSD1_ROOT_PORT_NUMBER    5       // Link Capabilities Port Number (1 based)
#define M2_SSD2_ROOT_PORT_NUMBER    6
#define M2_SSD1_PEG_TABLE_INDEX     3       // IntelM2NvmePegDp[3] - NVME_ON_PEG_M2_SLOT (3, ...)
#define M2_SSD2_PEG_TABLE_INDEX     4       // IntelM2NvmePegDp[4] - NVME_ON_PEG_M2_SLOT (4, ...)
#define M2_SSD_NO_ROOT_PORT         0xFF    // Slot has no root port, keep the place holder entry only

#define R_PCIE_CFG_LCAP             0x4C    // Link Capabilities
#define N_PCIE_CFG_LCAP_PN          24      // Link Capabilities Port Number field

// ---------------------------------------------------------------------------------------------------------------------
// Local Structure Type Definitions
// ---------------------------------------------------------------------------------------------------------------------

// ---------------------------------------------------------------------------------------------------------------------
// Local Function Prototypes
// ---------------------------------------------------------------------------------------------------------------------

// ---------------------------------------------------------------------------------------------------------------------
// File Global Variables
// ---------------------------------------------------------------------------------------------------------------------
extern STAY_ALWAYS_BOOT_OPTION_INFO  StayAlwaysBootOptionInfo;

static LIST_ENTRY      *mUefiListHead = NULL;
static EFI_HII_HANDLE  mHiiHandle     = NULL;

// Boot option description name pointers to add the associated boot options in to HP UEFI boot order without any restrictions.
// For example - Windows To Go boot option.
CHAR16  *StayAlwaysBootDescriptions[] = { L"USB Entry for Windows To Go" };  // Array of string pointers. Usage => {L"USB Entry for Windows To Go", L"Some other String", L"Some extra String"};

STAY_ALWAYS_BOOT_OPTION_INFO  StayAlwaysBootOptionInfo =
{
  StayAlwaysBootDescriptions,
  NUM_ELEMENTS (StayAlwaysBootDescriptions),
};

// Unicode strings
// Note: SupportStringID is currently unused but kept for potential future use
static EFI_STRING_ID  SupportStringID[] __attribute__((unused)) =
{
  STRING_TOKEN (SATA0_STR),
  STRING_TOKEN (SATA1_STR),
  STRING_TOKEN (SATA2_STR),
  STRING_TOKEN (SATA3_STR),
  STRING_TOKEN (SATA4_STR),
  STRING_TOKEN (SATA5_STR),
  STRING_TOKEN (USB_STR),
  STRING_TOKEN (CDROM_STR),
  STRING_TOKEN (NETWORK_STR),
  STRING_TOKEN (M2_SSD_STR),
  STRING_TOKEN (M2_SSD1_STR),
  STRING_TOKEN (M2_SSD2_STR),
  STRING_TOKEN (M2_SSD3_STR),
  STRING_TOKEN (M2_SSD4_STR),
  STRING_TOKEN (EMMC_STR),
  STRING_TOKEN (PCIE_BY_1_1_STR),
  STRING_TOKEN (PCIE_BY_1_2_STR),
  STRING_TOKEN (PCIE_BY_1_3_STR),
  STRING_TOKEN (PCIE_BY_4_1_STR),
  STRING_TOKEN (PCIE_BY_4_2_STR),
  STRING_TOKEN (PCIE_BY_16_1_STR),
};

static HP_BOOT_ORDER_PLATFORM_INFO_NODE  mUsbInfoTemplate =
{
  { NULL, NULL },                               // link
  PLATFORM_BOOT_ORDER_GROUP_USB,
  BBS_INDEX_DONT_CARE,
  (EFI_DEVICE_PATH_PROTOCOL  *)&Usb1Dp,         // UEFI DP
  NULL,                                         // HII handle (is dynamic)
  STRING_TOKEN (USB_STR),
  USB_PRIORITY,
  REMOVABLE_MEDIA,
  BOOT_ORDER_INCLUDE,
  PERMANENT_ITEM,
  STR_USB_HDD,
  RELATIVE_SORTING1
};

//
// Projects can define different table here:
// Refer "HpStoragePkg\Include\BootOrderMacro.docx" for the detail
//
static HP_BOOT_ORDER_PLATFORM_INFO_NODE  DefaultUefiBootOrder[] =
{
  // HDD_ON_SATA_PORT(2, SATA2_STR, HDD_PRIORITY)                           // HDD: "SATA 2:" - Sata port 2
  // HDD_ON_SATA_PORT(3, SATA1_STR, HDD_PRIORITY+3)                         // HDD: "SATA 1:" - Sata port 3

  // HDD_AND_CD_ON_SATA_PORT(0, SATA0_STR, HDD_PRIORITY+2)                  // HDD/CDROM: "SATA 0:" - Sata port 0

  // NVME_AND_AHCI_ON_M2_SLOT(8, 1, M2_SSD2_STR, PCIESSD_PRIORITY+1)        // HDD: "M2 SSD 2:" - PCIE port 8 (1D 00)/Sata port 1

  // NVME_ON_M2_SLOT(12, M2_SSD_STR, PCIESSD_PRIORITY)                      // HDD: "M2 SSD:" - PCIE port 12 (1D 04)

  NVME_ON_PEG_M2_SLOT (3, M2_SSD1_STR, PCIESSD_PRIORITY)                 // HDD: "M.2 SSD 1:" - CPU PCIe root port 5 (Device 6)
  NVME_ON_PEG_M2_SLOT (4, M2_SSD2_STR, PCIESSD_PRIORITY + 1)             // HDD: "M.2 SSD 2:" - CPU PCIe root port 6 (Device 6)

  // STORAGE_ON_PCIE_SLOT(0, PCIE_BY_4_1_STR, PCIESSD_PRIORITY+3)           // HDD: "PCI Express x4 Slot 1:" - PCIE port 0 (1C 00)
  NETWORK_GBE_UEFI(NETWORK_STR, NETWORK_PRIORITY)                           // NETWORK IPV4/IPV6: "NETWORK BOOT:" External LAN (1F 06)
  // EMMC_CONTROLLER(EMMC_STR, EMMC_PRIORITY)                               // HP_AED: "HP_AED:" - PCIE EMMC (1A 00)
};

static HP_BOOT_ORDER_PLATFORM_INFO_NODE  UmaUefiBootOrder[] =
{
  // HDD_ON_SATA_PORT(2, SATA2_STR, HDD_PRIORITY)                           // HDD: "SATA 2:" - Sata port 2
  // HDD_ON_SATA_PORT(3, SATA1_STR, HDD_PRIORITY+3)                         // HDD: "SATA 1:" - Sata port 3

  // HDD_AND_CD_ON_SATA_PORT(0, SATA0_STR, HDD_PRIORITY+2)                  // HDD/CDROM: "SATA 0:" - Sata port 0

  // NVME_AND_AHCI_ON_M2_SLOT(8, 1, M2_SSD2_STR, PCIESSD_PRIORITY+1)        // HDD: "M2 SSD 2:" - PCIE port 8 (1D 00)/Sata port 1

  // NVME_ON_M2_SLOT(12, M2_SSD_STR, PCIESSD_PRIORITY)                      // HDD: "M2 SSD:" - PCIE port 12 (1D 04)

  NVME_ON_PEG_M2_SLOT (3, M2_SSD1_STR, PCIESSD_PRIORITY)                 // HDD: "M.2 SSD 1:" - CPU PCIe root port 5 (Device 6)
  NVME_ON_PEG_M2_SLOT (4, M2_SSD2_STR, PCIESSD_PRIORITY + 1)             // HDD: "M.2 SSD 2:" - CPU PCIe root port 6 (Device 6)

  // STORAGE_ON_PCIE_SLOT(0, PCIE_BY_4_1_STR, PCIESSD_PRIORITY+3)           // HDD: "PCI Express x4 Slot 1:" - PCIE port 0 (1C 00)
  NETWORK_GBE_UEFI(NETWORK_STR, NETWORK_PRIORITY)                           // NETWORK IPV4/IPV6: "NETWORK BOOT:" External LAN (1F 06)
  // EMMC_CONTROLLER(EMMC_STR, EMMC_PRIORITY)                               // HP_AED: "HP_AED:" - PCIE EMMC (1A 00)
};

// ********************************************************************************************************************
// Function:  InstallPlatformDefaultData
//
// Summary:
//   This function will install platform specific UEFI Boot order
//
//
// Parameters:
//   VOID
//
// Function Returns:  nothing (data is returned in protocol structure)
// ********************************************************************************************************************
STATIC
VOID
InstallPlatformDefaultData (
  )
{
  HP_BOOT_ORDER_PLATFORM_INFO_NODE  *PlatformUefiBootOrder      = NULL;
  UINTN                             PlatformUefiBootOrderCounts = 0;
  UINTN                             NodeIndex;
  EFI_STATUS                        Status;
  HP_GFX_MISC_VARIABLE              *HpGfxMiscVariable = NULL;
  UINTN                             VarSize            = 0u;

  BOOTORDER_PRINT ((BOOTORDER_ERR_LVL, "[InstallPlatformDefaultData] Entry \n"));

  if (mUefiListHead != NULL)
  {
    //
    // Projects can assign different table by PcdDGpuHwPresent and HybridGraphicsEnable here
    //
    Status = HpGetVariable2 (HP_GFX_MISC_VARIABLE_NAME, &gHpVariableGuid, (VOID **)&HpGfxMiscVariable, &VarSize);
    if ((Status == EFI_SUCCESS) && (HpGfxMiscVariable->HybridGraphicsEnable) && (PcdGetBool (PcdDGpuHwPresent)))
    {
      PlatformUefiBootOrderCounts = NUM_ELEMENTS (DefaultUefiBootOrder);
      PlatformUefiBootOrder       = AllocateCopyPool (PlatformUefiBootOrderCounts * sizeof (HP_BOOT_ORDER_PLATFORM_INFO_NODE), DefaultUefiBootOrder);
    }
    else
    {
      PlatformUefiBootOrderCounts = NUM_ELEMENTS (UmaUefiBootOrder);
      PlatformUefiBootOrder       = AllocateCopyPool (PlatformUefiBootOrderCounts * sizeof (HP_BOOT_ORDER_PLATFORM_INFO_NODE), UmaUefiBootOrder);
    }

    if (PlatformUefiBootOrder != NULL)
    {
      BOOTORDER_PRINT ((BOOTORDER_ERR_LVL, "[InstallPlatformDefaultData] Insert Platform Boot Order \n"));

      for (NodeIndex = 0; NodeIndex < PlatformUefiBootOrderCounts; NodeIndex++)
      {
        if ((PlatformUefiBootOrder[NodeIndex].PermanentItem != PERMANENT_ITEM) || FeaturePcdGet (PcdHpStoragePlaceHolderSupport))
        {
          PlatformUefiBootOrder[NodeIndex].HiiHandle = mHiiHandle;
          InsertTailList (mUefiListHead, &PlatformUefiBootOrder[NodeIndex].Link);
        }
      }
    }
  }

  BOOTORDER_PRINT ((BOOTORDER_ERR_LVL, "[InstallPlatformDefaultData] Exit \n"));
}

// ********************************************************************************************************************
// Function:  UpdateM2SsdRootPortFunction
//
// Summary:
//   Resolve the PCI function number that each M.2 SSD root port currently owns and write it in to the boot order
//   device paths. See the "Local Macro Definitions" block for why the function number is not fixed.
//
//   A slot whose root port is not present gets M2_SSD_NO_ROOT_PORT, so its device path can never match a detected
//   NVMe device and the slot keeps showing its place holder entry only.
//
//
// Parameters:
//   VOID
//
// Function Returns:  nothing (the device paths of the platform boot order table are updated)
// ********************************************************************************************************************
STATIC
VOID
UpdateM2SsdRootPortFunction (
  VOID
  )
{
  UINT64  RpBase;
  UINTN   RpFunction;
  UINTN   PortNumber;
  UINT8   Ssd1Function = M2_SSD_NO_ROOT_PORT;
  UINT8   Ssd2Function = M2_SSD_NO_ROOT_PORT;

  for (RpFunction = 0; RpFunction <= PCI_MAX_FUNC; RpFunction++)
  {
    RpBase = PCI_SEGMENT_LIB_ADDRESS (0, 0, M2_SSD_ROOT_PORT_DEVICE, RpFunction, 0);

    if (PciSegmentRead16 (RpBase + PCI_VENDOR_ID_OFFSET) == MAX_UINT16)
    {
      continue;
    }

    PortNumber = (PciSegmentRead32 (RpBase + R_PCIE_CFG_LCAP) >> N_PCIE_CFG_LCAP_PN) & MAX_UINT8;

    DEBUG ((BOOTORDER_ERR_LVL, "[UpdateM2SsdRootPortFunction] 0/%x/%x is physical root port %d \n", M2_SSD_ROOT_PORT_DEVICE, RpFunction, PortNumber));

    if (PortNumber == M2_SSD1_ROOT_PORT_NUMBER)
    {
      Ssd1Function = (UINT8)RpFunction;
    }
    else if (PortNumber == M2_SSD2_ROOT_PORT_NUMBER)
    {
      Ssd2Function = (UINT8)RpFunction;
    }
  }

  IntelM2NvmePegDp[M2_SSD1_PEG_TABLE_INDEX].PciDevice.Function = Ssd1Function;
  IntelM2NvmePegDp[M2_SSD2_PEG_TABLE_INDEX].PciDevice.Function = Ssd2Function;

  DEBUG ((BOOTORDER_ERR_LVL, "[UpdateM2SsdRootPortFunction] M.2 SSD 1 = 0/%x/%x, M.2 SSD 2 = 0/%x/%x \n", M2_SSD_ROOT_PORT_DEVICE, Ssd1Function, M2_SSD_ROOT_PORT_DEVICE, Ssd2Function));
}

// Update Platform Specific Data
EFI_STATUS
UpdatePlatformSpecificData (
  IN EFI_HII_HANDLE  HiiHandle,
  IN LIST_ENTRY      *UefiListHead
  )
{
  //
  // Reserved for Platform Specific Data
  //

  return EFI_SUCCESS;
}

VOID
UpdatePlatformTableNodes (
  IN EFI_EVENT  Event,
  IN VOID       *Context
  )
{
  EFI_STATUS                     Status             = EFI_SUCCESS;
  HP_PLATFORM_SERVICES_PROTOCOL  *HpPlatformService = NULL;
  LIST_ENTRY                     *LegacyListHead    = NULL;
  LIST_ENTRY                     *UefiListHead      = NULL;

  BOOTORDER_PRINT ((BOOTORDER_ERR_LVL, "[UpdatePlatformTableNodes] Entry\n"));

  Status = gBS->LocateProtocol (
                  &gHpPlatformServicesProtocolGuid,
                  NULL,
                  (VOID **)&HpPlatformService
                  );

  if (Status == EFI_SUCCESS)
  {
    UefiListHead = HpPlatformService->BootOrderTypeListHead[UefiBootOptions];
  }

  if (UefiListHead != NULL)
  {
    if (mHiiHandle != NULL)
    {
      // Resolve the current root port function number of each M.2 SSD slot before the NVMe devices are matched
      UpdateM2SsdRootPortFunction ();

      // Update NVME information
      UpdateNvmeInfo (mHiiHandle, LegacyListHead, UefiListHead);

      // Update Sata information
      UpdateSataInfo (mHiiHandle, LegacyListHead, UefiListHead);

      // Add USB nodes in to platform table.
      AddUsbDeviceNodes (&mUsbInfoTemplate, mHiiHandle, LegacyListHead, UefiListHead, PLATFORM_BOOT_ORDER_GROUP_USB);

      // Update Platform specific Data
      UpdatePlatformSpecificData (mHiiHandle, UefiListHead);

      // Add placeholder for USB LAN if support
      if (FeaturePcdGet (PcdUsbLanPlaceHolderSupport))
      {
        InsertExtlNetworkPlaceHolderEntries ();
      }

      InsertWifiNetworkEntries ();
    }
  }

  BOOTORDER_PRINT ((BOOTORDER_ERR_LVL, "[UpdatePlatformTableNodes] Exit\n"));
  gBS->CloseEvent (Event);
}

// ********************************************************************************************************************
// Function:  DxeInitLinkedListForBootOrder
//
// Summary:
//   This is an example implementation of the HpPlatformServicesProtocol.InitLinkedListForBootOrder() function.
//   This function will create the two platform boot order linked lists that provide platform information to the core
//   boot order logic. See HpPlatformServicesProtocol.h for details.
//
//
// Global Variables:  gHpPlatformServicesProtocolGuid, HpPlatformServicesLibStrings
//
// Parameters:
//    -----------------------------------------------------------------------------------------------------------------
//    Name:          OUT This
//    Description:   Ptr to the protocol which holds the linked list ptrs which this function will initialize.
//    Valid values:  This->BootOrderTypeListHead[UefiBootOptions]
//                   initialized.
//    -----------------------------------------------------------------------------------------------------------------
//
// Function Returns:  nothing (data is returned in protocol structure)
// ********************************************************************************************************************
VOID
EFIAPI
DxeInitLinkedListForBootOrder (
  IN HP_PLATFORM_SERVICES_PROTOCOL  *This
  )
{
  static BOOLEAN  InitializedLinkList = FALSE;
  EFI_STATUS      Status              = EFI_NOT_STARTED;

  BOOTORDER_PRINT ((BOOTORDER_ERR_LVL, "[DxeInitLinkedListForBootOrder] Entry\n"));

  if (!InitializedLinkList)
  {
    //
    // Publish HII data
    //
    mHiiHandle = HiiAddPackages (
                   &gHpPlatformServicesProtocolGuid,
                   NULL,
                   PlatformBootOrderLibStrings,
                   NULL
                   );
    ASSERT (mHiiHandle != NULL);

    mUefiListHead = AllocateZeroPool (sizeof (*mUefiListHead));

    // Do this here, even if the pointers are NULL - they must be initialized!!!
    This->BootOrderTypeListHead[UefiBootOptions] = mUefiListHead;
    This->StayAlwaysBootOptionInfo               = &StayAlwaysBootOptionInfo;

    if (mUefiListHead != NULL)
    {
      // Provided they are non-NULL, initialize these no matter what, for safety.
      InitializeListHead (mUefiListHead);

      if (mHiiHandle != NULL)
      {
        // Install platform specific UEFI Boot order
        InstallPlatformDefaultData ();

        // Call back event to dynamic update boot order data (NVME, USB, etc)
        Status = EfiNamedEventListen (
                   &gBdsAllDriversConnectedProtocolGuid,
                   TPL_CALLBACK,
                   UpdatePlatformTableNodes,
                   NULL,
                   NULL
                   );
      }
    }

    InitializedLinkList = TRUE;
  }

  BOOTORDER_PRINT ((BOOTORDER_ERR_LVL, "[DxeInitLinkedListForBootOrder] Exit\n"));
}

// This is here to satisfy the library link requirements for SMM, but there is no
// boot order function in SMM, so this is just a stub.
VOID
EFIAPI
SmmInitLinkedListForBootOrder (
  IN HP_PLATFORM_SERVICES_PROTOCOL  *This
  )
{
  BOOTORDER_PRINT ((BOOTORDER_ERR_LVL, "[SmmInitLinkedListForBootOrder]: Not Implimented.\n"));
}
