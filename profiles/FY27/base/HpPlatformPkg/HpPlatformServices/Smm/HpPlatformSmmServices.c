//
// (c) Copyright 2012 - 2025 HP Development Company, L.P.
// This software and associated documentation (if any) is furnished under a license and may only be used or
// copied in accordance with the terms of the license. Except as permitted by such license, no part of this
// software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
// form or by any means without the express written consent of HP Development Company.
//
// Module Name: HpPlatformSmmServices.c
//
// Abstract: Installing platformservice protocol in SMM.
//

#include <PiSmm.h>

#include <Library/UefiBootServicesTableLib.h>
#include <Library/UefiDriverEntryPoint.h>
#include <Library/DebugLib.h>
#include <Library/SmmServicesTableLib.h>
#include <Library/HpUefiBootManagerLib.h>
#include <Library/CoreBootManagerLib.h>
#include <Protocol/HpPlatformServicesProtocol.h>
#include <Library/BaseMemoryLib.h>
#include <Library/HpPlatformServicesLib.h>
#include <Library/BaseHpPlatformServicesLib.h>
#include <Library/PlatformBootOrderLib.h>

HP_PLATFORM_SERVICES_PROTOCOL  SmmHpPlatformService;

EFI_STATUS
EFIAPI
HpPlatformSmmEntry (
  IN      EFI_HANDLE        ImageHandle,
  IN      EFI_SYSTEM_TABLE  *SystemTable
  )
{
  EFI_STATUS  Status;
  EFI_HANDLE  mHandle = NULL;

  ZeroMem (&SmmHpPlatformService, sizeof (SmmHpPlatformService));

  SmmHpPlatformService.RefreshAllBootOption           = RefreshAllBootOption;
  SmmHpPlatformService.UpdateConsoleVariable          = UpdateConsoleVariable;
  SmmHpPlatformService.PlatformUpdateBootMode         = PlatformUpdateBootMode;
  SmmHpPlatformService.PlatformBdsBoot                = PlatformBdsBoot;
  SmmHpPlatformService.PlatformRegisterHotKey         = PlatformRegisterHotKey;
  SmmHpPlatformService.PlatformConsoleReady           = PlatformConsoleReady;
  SmmHpPlatformService.InstallAdditionalOpRom         = InstallAdditionalOpRom;
  SmmHpPlatformService.InstallAdditionalExternalOpRom = InstallAdditionalExternalOpRom;
  SmmHpPlatformService.TriggerHpSetupExternal         = TriggerHpSetupExternal;
  SmmHpPlatformService.DisplayExternalSetupInfo       = DisplayExternalSetupInfo;
  SmmHpPlatformService.BlockUnblockForceRestart       = BlockUnblockForceRestart;
  SmmHpPlatformService.InitLinkedListForBootOrder     = SmmInitLinkedListForBootOrder;
  SmmHpPlatformService.AfterConnectRootBridgeHook     = HpAfterConnectRootBridgeHook;
  SmmHpPlatformService.OptionROMPlatformLaunchCheck   = NULL;

  Status = gSmst->SmmInstallProtocolInterface (
                    &mHandle,
                    &gHpPlatformServicesProtocolGuid,
                    EFI_NATIVE_INTERFACE,
                    &SmmHpPlatformService
                    );
  DEBUG ((EFI_D_ERROR, "[HpPlatformSmmEntry]: Status after installation - %r\n", Status));
  ASSERT_EFI_ERROR (Status);

  return Status;
}
