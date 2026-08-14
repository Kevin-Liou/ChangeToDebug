#
# (c) Copyright 2015 - 2025 HP Development Company, L.P.
# This software and associated documentation (if any) is furnished under a license and may only be used or
# copied in accordance with the terms of the license. Except as permitted by such license, no part of this
# software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
# form or by any means without the express written consent of HP Development Company.
#
# Platform configuration file.
#

#
# TRUE is ENABLE. FALSE is DISABLE.
#

[Defines]
  DEFINE PROJECT_DEBUG_LEVEL = 0x80080046  # DEBUG_ERROR | DEBUG_EVENT | DEBUG_WARN | DEBUG_LOAD
  DEFINE DBG_SERIAL_PORT_BASE     = 0x3F8
  DEFINE SYSTEM_SIO_BASE_ADDRESS  = 0x260

  DEFINE PROJECT_SMBIOS_VERSION  = 0x0304  # SMBIOS 3.4
  DEFINE PROJECT_FAN_TABLE_COUNT = 6  # MULTI_FAN_TABLE_COUNTS
  DEFINE PROJECT_ACPI_OEM_TABLE_ID = 0x20202020204C544D  # PcdAcpiDefaultOemTableId, "MTL     "

[PcdsFeatureFlag]

   #
   # HpPlatformPkg, Edk2Platforms, HpCore
   #
   # PCD for Memory Speed Throttle Down support.
   #  BCR#195650 - Not support memory 2DPC 2400Mhz configs, they must throttle down to 2133 Mhz.
   #  For Vaughn and Affleck, BIOS need to check SODIMMs configuration to throttle down
   #  memory speed form 2400Mhz to 2133Mhz if 2DPC be detected.
   gEfiHpPlatformPkgTokenSpaceGuid.MemorySpeedThrottleDownSupport|FALSE

   ## Volume Down hotkey support PCD
   gEfiHpHotkeyPubIntPkgTokenSpaceGuid.PcdHotkeyVolumeDownSupport          |FALSE

   #
   # PCD override to determine if we want SATA CD-ROM Boot option in F10 Advanced setup menu.
   # [Platform Specific] This PCD value is updated to HpPlatformFeaturesProtocol and store into PlatformSupport variable.
   # Due to Armorhide support CD-ROM, the value in HpPlatformFeaturesProtocol will be overwrote directly. (see HpPlatformFeaturesDxe.c)
   #
!if $(CDROM_BOOT_SUPPORT) == TRUE
   gEfiHpCdRomBootPubIntPkgTokenSpaceGuid.gPcdCdRomBootSupport|TRUE
!else
   gEfiHpCdRomBootPubIntPkgTokenSpaceGuid.gPcdCdRomBootSupport|FALSE
!endif

    # PCD to enable Serial Debug in ACPI
!if $(HP_RTD3_ACPI_MEM_DEBUG_ENABLE) == TRUE
   gHpIntelChipsetPkgTokenSpaceGuid.PcdSerialDebugInAcpiEnable|TRUE
!else
   gHpIntelChipsetPkgTokenSpaceGuid.PcdSerialDebugInAcpiEnable|FALSE
!endif

   ## PCD to enable/disable placeholder for storage on SATA port and M.2 slot, TRUE: enable, FALSE: disable (default)
   gEfiHpStoragePkgTokenSpaceGuid.PcdHpStoragePlaceHolderSupport|FALSE

   gMinPlatformPkgTokenSpaceGuid.PcdTpm2Enable|FALSE


[PcdsFixedAtBuild]

   #
   # MeteorLakePlatSamplePkg
   #
  gPlatformModuleTokenSpaceGuid.PcdPciHotplugEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdEbcEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdHddPasswordEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdNetworkEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdMouseEnable|TRUE

  gPlatformModuleTokenSpaceGuid.PcdScsiEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdJpgEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdUsbEnable|TRUE

  gPlatformModuleTokenSpaceGuid.PcdNetworkIp6Enable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdNetworkIscsiEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdNetworkVlanEnable|TRUE

  gPlatformModuleTokenSpaceGuid.PcdLzmaEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdDxeCompressEnable|TRUE

  gPlatformModuleTokenSpaceGuid.PcdMemoryTestEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdTpmEnable|FALSE

   #
   # Determine ACPI reserved memory under 4G
   #
!if $(TARGET) == DEBUG
   gPlatformModuleTokenSpaceGuid.PcdS3AcpiReservedMemorySize|0x3000000
!else
   gPlatformModuleTokenSpaceGuid.PcdS3AcpiReservedMemorySize|0x3000000
!endif

   ## HpPlatformPkg

   #
   # I2C Touch Panel
   # TOUCH_PWR_EN
   #
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchPanelPowerGpio|0xFFFFFFFF     #GPP_F7
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchPanelPowerActive|1            #high active
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchPanelInterruptActive|1        #high active

   #Touch Panel LTR Setting
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchpanelLtrIdle|0xFFFF
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchpanelLtrSSactive|0xFFFF
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchpanelLtrFMactive|0xFFFF
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchpanelLtrFMPactive|0xFFFF

   gEfiHpPlatformPkgTokenSpaceGuid.PcdSioBaseAddress|$(SYSTEM_SIO_BASE_ADDRESS)

   ## Edk2

   gEfiMdeModulePkgTokenSpaceGuid.PcdSerialRegisterBase|$(DBG_SERIAL_PORT_BASE)

   ## Indicate the Flash part size
!if $(SPI_ROM_SIZE) == 32
   gEfiHpRegionDataPubIntPkgTokenSpaceGuid.PcdFlashPartSize|0x02000000
!else
   gEfiHpRegionDataPubIntPkgTokenSpaceGuid.PcdFlashPartSize|0x01000000
!endif

   #
   # Determine the memory size
   #
   gMinPlatformPkgTokenSpaceGuid.PcdPlatformEfiAcpiReclaimMemorySize|0x80
   gMinPlatformPkgTokenSpaceGuid.PcdPlatformEfiAcpiNvsMemorySize|0x200
   gMinPlatformPkgTokenSpaceGuid.PcdPlatformEfiReservedMemorySize|0x3100
   gMinPlatformPkgTokenSpaceGuid.PcdPlatformEfiRtDataMemorySize|0x2E4
   gMinPlatformPkgTokenSpaceGuid.PcdPlatformEfiRtCodeMemorySize|0x500
   gHpIntelChipsetPkgTokenSpaceGuid.PcdPlatformEfiBsCodeMemorySize|0x1800
   gHpIntelChipsetPkgTokenSpaceGuid.PcdPlatformEfiBsDataMemorySize|0xFF00

   # Specifies whether StatusCode is reported via PostCode
!if ($(TARGET) == DEBUG) OR ($(HP_POST_CODE_TO_SERIAL_PORT_ENABLE) == TRUE)
   gHpIntelChipsetPkgTokenSpaceGuid.PcdStatusCodeUseSerialPortPlatform|TRUE
!endif
!if gPlatformModuleTokenSpaceGuid.PcdPostCodeStatusCodeEnable == TRUE
   gPostCodeDebugFeaturePkgTokenSpaceGuid.PcdStatusCodeUsePostCode|TRUE
!else
   gPostCodeDebugFeaturePkgTokenSpaceGuid.PcdStatusCodeUsePostCode|FALSE
!endif

   ## PCD to enable HP PostCode Debug by serial port
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdHpPostCodeToSerialPortEnable|FALSE

   #
   # I2C Touch Panel
   # TOUCH_RST#
   #
   gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdI2CTouchResetGpio|0xFFFFFFFF  # unsupport
   gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdI2CTouchResetGpioActive|0     # low active
   # TOUCH_INT#
   gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdI2CTouchIntGpio|0xFFFFFFFF    # unsupport
   # WOT_EN#
   gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdI2CWakeOnTouchGpio|0xFFFFFFFF # unsupport
   gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdI2CWakeOnTouchGpioActive|0    # low active

   # PCDs for Touch pad GPP GPP_E0
   # I2C touch pad interrupt GPIO: Group E pin 0
   gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdI2CTouchPadIntGpio|0xFFFFFFFF # unsupport

   gEfiHpDmarTokenSpaceGuid.PcdDmarFeatureSupport|TRUE
   gEfiHpDmarTokenSpaceGuid.PcdDmarOptionDefaultValue|TRUE
   gEfiHpDmarTokenSpaceGuid.PcdHpDmarEnableAllDebugMSG|FALSE

   # PCD to enable/disable DCR280518 for enhanced pre-boot dma protection feature.
   gEfiHpDmarTokenSpaceGuid.PcdEnhancedPreBootDmarSupport|TRUE

   #
   # PcdsFixedAtBuild for HpStoragePkg
   #
   # Update StorageRtd3Support valuse to 0/1/2 in ADL.2347
   ## ADL - PCD to configure HP Storage RTD3 support. 0: D3 Disable, 1:RTD3 hot (default), 2: RTD3 cold
   gEfiHpStoragePkgTokenSpaceGuid.PcdStorageRtd3Support|1

   # Add ARK/Pelori USB Mouse into PcdUsbMsExceptionList for skip Absolute/Related mode byte
   gEfiMdeModulePkgTokenSpaceGuid.PcdUsbMsExceptionList|{CODE(
   {
   {0x1A86, 0xE129},
   })}

   # Use GPP_V1 as ACPRESENT GPIO pin and its active level is high.
   # ADP_PRES_OUT
   #
   gEfiHpPlatformPkgTokenSpaceGuid.PcdAcPresentGpio|0xFFFFFFFF # unsupport
   gEfiHpPlatformPkgTokenSpaceGuid.PcdAcPresentGpioActive|1 # High Active
   gEfiMdePkgTokenSpaceGuid.PcdDebugPropertyMask|0x0F

!if ($(NOTEBOOK_PLATFORM) == TRUE) AND ($(CRB_BOOT_SUPPORT) == FALSE)
   #
   # PcdSerialPortEnable enable use for output COM port via SerialPortWrite (), NB/mWS didn't have such legacy COM serial device.
   # For override HpIntel\HpIntelChipsetPkg\HpIntelChipsetPkgOverrideIntelPcd.dsc init PcdSerialPortEnable as TRUE.
   #
   gPlatformModuleTokenSpaceGuid.PcdSerialPortEnable|FALSE
!endif

[PcdsFixedAtBuild.IA32]
   gIntelSiliconPkgTokenSpaceGuid.PcdVTdPeiDmaBufferSize|0x02400000

[PcdsFixedAtBuild.X64]
   gEfiHpDetachablesPkgPubIntTokenSpaceGuid.PcdDualAccelSupport|FALSE

[PcdsDynamicDefault]

   ## Edk2
   #
   # To support TPM interrupt, given a initial PCD default data to UINT32(0) to prevent build error,
   # the actual PcdTpm2PossibleIrqNumBuf buffer data will be assigned in HpTpmInterruptGpioConfigPei.c
   #
   gEfiSecurityPkgTokenSpaceGuid.PcdTpm2PossibleIrqNumBuf|{0x00, 0x00, 0x00, 0x00}
   gEfiSecurityPkgTokenSpaceGuid.PcdTpm2SelfTestPolicy|0

   #
   # Note:
   #   ODM must refer to HW schema for the audio codec name !!!
   #   1. Realtek audio example: L"Realtek ALC221"
   #   2. Conexant audio example: L"Conexant CX7750"
   #


   gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdI2CTouchHidDescAddr|0x0001
   gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdI2cTouchPanelSpeed |400000       # 100, 400 or 1000 kbit
   gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdI2cClickPadSpeed   |400000       # 100, 400 or 1000 kbit

   gEfiHpBusSupportPubIntPkgTokenSpaceGuid.PcdSkipUsbOnFastBoot|TRUE

[PcdsDynamicExDefault.common.DEFAULT]
   gEfiHpTpmPubIntPkgTokenSpaceGuid.PcdTpmAllowDisable|L"TXT"

[PcdsPatchableInModule.common]

   gEfiMdePkgTokenSpaceGuid.PcdDebugPrintErrorLevel|$(PROJECT_DEBUG_LEVEL)
   gEfiMdeModulePkgTokenSpaceGuid.PcdSmbiosVersion|$(PROJECT_SMBIOS_VERSION)

   ## Default OEM Table ID for ACPI table creation, it is "EDK2    ".
   #  According to ACPI specification, this field is particularly useful when
   #  defining a definition block to distinguish definition block functions.
   #  The OEM assigns each dissimilar table a new OEM Table ID.
   #  This PCD is ignored for definition block.
   #
   # @Prompt Default OEM Table ID for ACPI table creation.
   # will be patched by AcpiPlatform per CPU family
   gEfiMdeModulePkgTokenSpaceGuid.PcdAcpiDefaultOemTableId|$(PROJECT_ACPI_OEM_TABLE_ID)

