#
# (c) Copyright 2015 - 2026 HP Development Company, L.P.
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
  DEFINE PROJECT_ACPI_OEM_TABLE_ID = 0x20202020204C564E  # PcdAcpiDefaultOemTableId, "NVL     "

[PcdsFeatureFlag]

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

   # PCD to determine if platform support Front TYPE-C PD
   gEfiPortOptionsPubIntPkgTokenSpaceGuid.PcdFrontTypeCPdSupport|TRUE

[PcdsFixedAtBuild]
   gEfiHpPlatformPkgTokenSpaceGuid.PcdHpSeries|8            # DM800
   gEfiHpPlatformPkgTokenSpaceGuid.PcdHpProjectIndex|21     # Z_21

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

  gPlatformModuleTokenSpaceGuid.PcdMemoryTestEnable|FALSE

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

# FLEX2_ID0# ~ FLEX2_ID3#
   gHpDtPkgTokenSpaceGuid.FlexIO2OptDetID0Pin|0x001E000F           # GPIOV2_NVL_PCH_S_GPP_D_15
   gHpDtPkgTokenSpaceGuid.FlexIO2OptDetID1Pin|0x001E0010           # GPIOV2_NVL_PCH_S_GPP_D_16
   gHpDtPkgTokenSpaceGuid.FlexIO2OptDetID2Pin|0x001E0011           # GPIOV2_NVL_PCH_S_GPP_D_17
   gHpDtPkgTokenSpaceGuid.FlexIO2OptDetID3Pin|0x001E0012           # GPIOV2_NVL_PCH_S_GPP_D_18

   gHpDtPkgTokenSpaceGuid.OptCardFlexIoSmbSelGpioPin|0x001E0504    # HPGP_FLEXIO_SMB_SEL   GPIOV2_NVL_PCH_S_GPP_B_4
   gHpDtPkgTokenSpaceGuid.OptCardFlexIoSmbSelGpioPinActive|0

   # VPIN Selection Pins
   gHpDtPkgTokenSpaceGuid.VpinSelect1GpioPin|0x001C048C            # GPIOV2_NVL_PCH_S_GPP_E_12  HPGP_IMON_65W
   gHpDtPkgTokenSpaceGuid.VpinSelect2GpioPin|0x001C048D            # GPIOV2_NVL_PCH_S_GPP_E_13  HPGP_IMON_90W
   gHpDtPkgTokenSpaceGuid.VpinSelect3GpioPin|0x001C048F            # GPIOV2_NVL_PCH_S_GPP_E_15  HPGP_IMON_100W
   gHpDtPkgTokenSpaceGuid.VpinSelect4GpioPin|0x001C0490            # GPIOV2_NVL_PCH_S_GPP_E_16  HPGP_IMON_120W
   gHpDtPkgTokenSpaceGuid.VpinSelect5GpioPin|0x001C0491            # GPIOV2_NVL_PCH_S_GPP_E_17  HPGP_IMON_150W
   gHpDtPkgTokenSpaceGuid.VpinSelect6GpioPin|0x001C0492            # GPIOV2_NVL_PCH_S_GPP_E_18  HPGP_IMON_180W
   gHpDtPkgTokenSpaceGuid.VpinSelect7GpioPin|0x001C0493            # GPIOV2_NVL_PCH_S_GPP_E_19  HPGP_IMON_230W
   gHpDtPkgTokenSpaceGuid.VpinSelect8GpioPin|0x001C0494            # GPIOV2_NVL_PCH_S_GPP_E_20  HPGP_IMON_Reserved

[PcdsFixedAtBuild.IA32]
   gIntelSiliconPkgTokenSpaceGuid.PcdVTdPeiDmaBufferSize|0x02400000

[PcdsFixedAtBuild.X64]
   gEfiHpDetachablesPkgPubIntTokenSpaceGuid.PcdDualAccelSupport|FALSE

  ## This value is used to allow platform determine whether NVME controllers needs to be enumerated in fast boot
  ## regardless of device path entries in gPlatformConnectSequence(DT cannot list each PCI slot that user could plug-in a card)
  gEfiHpBootOrderPubIntPkgTokenSpaceGuid.PcdConnectNvmeOnFastBoot|TRUE

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





[PcdsDynamicExDefault.common.DEFAULT]
   gEfiHpTpmPubIntPkgTokenSpaceGuid.PcdTpmAllowDisable|L"TXT"

   # GPIO pin for Serial Port A support
   gEfiHpPlatformPkgTokenSpaceGuid.PcdSerialPortAGpio|{CODE({
      0,                            // ExpanderNo (0 = not expander)
      GPIOV2_NVL_PCH_S_GPP_C_21,    // GpioNo (GPIOV2_PAD_NONE = not supported)
      0                             // Active (0=low, 1=high)
   })}


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

