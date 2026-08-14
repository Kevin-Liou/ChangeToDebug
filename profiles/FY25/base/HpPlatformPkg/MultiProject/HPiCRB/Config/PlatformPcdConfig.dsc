#//
#// (c) Copyright 2015 - 2024 HP Development Company, L.P.
#// This software and associated documentation (if any) is furnished under a license and may only be used or
#// copied in accordance with the terms of the license. Except as permitted by such license, no part of this
#// software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
#// form or by any means without the express written consent of HP Development Company.
#//
#// Platform configuration file.
#//

#
# TRUE is ENABLE. FALSE is DISABLE.
#
[Defines]

DEFINE HP_POST_CODE_TO_SERIAL_PORT_ENABLE = TRUE
!if $(FSP_DEBUG_IN_RELEASE_MODE) == TRUE
   DEFINE HP_POST_CODE_TO_SERIAL_PORT_ENABLE = TRUE
!endif
DEFINE DEBUG_IO_PORT_80_ENABLE = TRUE
DEFINE DEBUG_IO_PORT_24E_ENABLE = FALSE
DEFINE DEBUG_IO_PORT_80_WORD_ACCESS_ENABLE = FALSE
DEFINE SERIAL_DEBUG_IN_ACPI_ENABLE = FALSE
DEFINE HP_TCEQ_ERROR_HANDLING_SUPPORT = TRUE
DEFINE HP_CMOS_BUTTON_SUPPORT = TRUE
DEFINE HP_CLEAR_PASSWORD_JUMPER_SUPPORT = FALSE

[PcdsFeatureFlag]

#
# BIOS build switches configuration
#

   gMinPlatformPkgTokenSpaceGuid.PcdTpm2Enable|TRUE
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdVPEnable              |FALSE
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdSLEEnable             |FALSE

   ## PCD to determine if Audio needs initializing before Tceq error is triggered.

#
# BIOS build switches configuration
#

# ME

   # PCD for Feature Byte: vPro upsell on 600-class Desktop Platforms
   gHpIntelChipsetPkgTokenSpaceGuid.PcdFeatureBytevProUpsellSupport|FALSE

   # PCD for remove "Intel Management Engine (ME)" option in F10 and BCU.
   # TRUE: Remove Intel ME option in F10/BCU, FALSE: Keep Intel ME option in F10/BCU.
   gHpIntelChipsetPkgTokenSpaceGuid.PcdIntelMeOptionRemovalEnable|TRUE


   ## PCD to define if platform support I2C/I2S Audio Codec
   gHpIntelChipsetPkgTokenSpaceGuid.PcdAdspEnable|FALSE

   # PCD to enable Serial Debug in ACPI
!if $(HP_RTD3_ACPI_MEM_DEBUG_ENABLE) == TRUE
   gHpIntelChipsetPkgTokenSpaceGuid.PcdSerialDebugInAcpiEnable|TRUE
!else
   gHpIntelChipsetPkgTokenSpaceGuid.PcdSerialDebugInAcpiEnable|FALSE
!endif

   ## PCD to define if platform support Keyboard Power On feature. (Intel DT only)
   gHpIntelChipsetPkgTokenSpaceGuid.PcdKeyboardPowerOnSupport|TRUE

   # PCD for mailbox support.
   gNuvotonCommonTokenSpaceGuid.PcdNuvotonMailboxSupport|FALSE

   ## PCD to enable/disable placeholder for storage on SATA port and M.2 slot, TRUE: enable, FALSE: disable (default)
   gEfiHpStoragePkgTokenSpaceGuid.PcdHpStoragePlaceHolderSupport|FALSE

   # PCD for HP VTIO support, default not support
   gHpIntelChipsetPkgTokenSpaceGuid.PcdHpVtioSupport|FALSE

   # PCD to use forcing Intel VGA (IGD)'s MMIO resource below 4G Support
   gHpIntelChipsetPkgTokenSpaceGuid.PcdForceIntelIgdRunningMmio32Support|FALSE

   #
   # Enable/Disable System Guard TPM provisioning supporting to meet the requirement.
   # For Windows System Guard supported platform please set both of PcdSystemGuardTpmProvisionEnable and
   # PcdSystemGuard19H1TpmProvisionEnable PCD to TRUE!
   #
   gHpIntelChipsetPkgTokenSpaceGuid.PcdSystemGuardTpmProvisionEnable|TRUE
   gHpIntelChipsetPkgTokenSpaceGuid.PcdSystemGuard19H1TpmProvisionEnable|TRUE

   #
   # Intel NB Platform need to supporting TPM interrupt since Intel BIOS19 for all NB(mWS) 600 and above.
   # TPM interrupt was not a POR on 2020 DT platforms, disable it.
   #
   gHpIntelChipsetPkgTokenSpaceGuid.PcdTpmHwInterruptSupport|TRUE

   # PCD for PCH DMIC support
   gHpIntelChipsetPkgTokenSpaceGuid.PcdPchDmicSupport|TRUE
   !if gHpIntelChipsetPkgTokenSpaceGuid.PcdPchDmicSupport == TRUE
      gHpIntelChipsetPkgTokenSpaceGuid.PcdPchDmic1Support|TRUE
      gNhltFeaturePkgTokenSpaceGuid.PcdNhltFeatureEnable|TRUE
   !endif

   # PCD to determine if wake on touch panel is supported
   gEfiHpPlatformPkgTokenSpaceGuid.PcdWakeOnTouchPanelSupport|FALSE


   gHpIntelChipsetPkgTokenSpaceGuid.PcdIntelRvpSetupEnable|FALSE
   #
   # PCD override to determine if we want SATA CD-ROM Boot option in F10 Advanced setup menu.
   #
   gEfiHpCdRomBootPubIntPkgTokenSpaceGuid.gPcdCdRomBootSupport|TRUE

   # PCD to determine if platform supports Mixed DIMM Alert.
   gEfiHpPlatformPkgTokenSpaceGuid.PcdMixedDimmAlertSupport|TRUE

   gEfiHpPlatformPkgTokenSpaceGuid.gRposDockUSBWakeOnLanSupport|FALSE

[PcdsFixedAtBuild]

   gEfiHpSetupPubIntPkgTokenSpaceGuid.MaxDimmsPerCpu|0x10

   gPlatformModuleTokenSpaceGuid.PcdOpalPasswordEnable|FALSE  # HP override


  gBoardModuleTokenSpaceGuid.PcdAcpiDebugFeatureEnable|FALSE
  gBoardModuleTokenSpaceGuid.PcdS4Enable|TRUE

  gMeteorLakeBinPkgTokenSpaceGuid.PcdNhltBinEnable|FALSE                   #NhltIcl.bin
  gMebxFeaturePkgTokenSpaceGuid.PcdMebxFeatureEnable|TRUE             #Mebx.efi
  gCommonBinPkgTokenSpaceGuid.PcdRaidDriverEfiEnable|FALSE             #RaidDriver.efi
  gCommonBinPkgTokenSpaceGuid.PcdRsteDriverEfiEnable|FALSE             #SataDriverRste.efi
  gBoardModuleTokenSpaceGuid.PcdNvmeEnable|FALSE
  gBoardModuleTokenSpaceGuid.PcdIntelRaidEnable|FALSE
  gBoardModuleTokenSpaceGuid.PcdTerminalEnable|TRUE

  gEcFeaturePkgTokenSpaceGuid.PcdEcEnable|TRUE


  # Build scripts override the value of this PCD, update value in scripts for the change to take effect.
  gBoardModuleTokenSpaceGuid.PcdSetupEnable|TRUE
  gMeteorLakeBinPkgTokenSpaceGuid.PcdStartupAcmBinEnable|FALSE           #StartupAcm.bin

  gPlatformModuleTokenSpaceGuid.PcdPlatformCmosAccessSupport|FALSE
  gPlatformModuleTokenSpaceGuid.PcdEnableSecureErase|FALSE
  gPlatformModuleTokenSpaceGuid.PcdCapsuleEnable|FALSE
  gCapsuleFeaturePkgTokenSpaceGuid.PcdNvmeRecoveryEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdI2cTouchDriverEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdPiI2cStackEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdUsb3SerialStatusCodeEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdUserAuthenticationEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdPciHotplugEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdUsbTypeCEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdVirtualKeyboardEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdEbcEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdHddPasswordEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdNetworkEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdMouseEnable|TRUE
!if $(TARGET) == DEBUG
  gPlatformModuleTokenSpaceGuid.PcdSinitAcmBinEnable|FALSE      # Reduce DXE FV size.
!else
  gPlatformModuleTokenSpaceGuid.PcdSinitAcmBinEnable|TRUE
!endif
  gPlatformModuleTokenSpaceGuid.PcdScsiEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdJpgEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdUsbEnable|TRUE

  gPlatformModuleTokenSpaceGuid.PcdNetworkIp6Enable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdNetworkIscsiEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdNetworkVlanEnable|TRUE

  gPlatformModuleTokenSpaceGuid.PcdLzmaEnable|TRUE
  gPlatformModuleTokenSpaceGuid.PcdDxeCompressEnable|TRUE

  gPlatformModuleTokenSpaceGuid.PcdNat87393Present|FALSE
  gPlatformModuleTokenSpaceGuid.PcdNct677FPresent|FALSE

  gPlatformModuleTokenSpaceGuid.PcdMemoryTestEnable|FALSE
  gPlatformModuleTokenSpaceGuid.PcdTpmEnable|TRUE

  ## Indicate the Flash part size
  gEfiHpRegionDataPubIntPkgTokenSpaceGuid.PcdFlashPartSize|0x02000000


  #
  # FALSE - Platform does not support ME EC recovery. EX : Surestart lite platform
  # TRUE - Platform supports ME EC recovery. EX : 1000/800/600 series
  #
  gHpFirmwareFlashPubIntPkgTokenSpaceGuid.PcdMeEcRecoverySupport|TRUE


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

   #
   # Determine ACPI reserved memory under 4G
   #
!if $(TARGET) == DEBUG
   gPlatformModuleTokenSpaceGuid.PcdS3AcpiReservedMemorySize|0x3000000
!else
   gPlatformModuleTokenSpaceGuid.PcdS3AcpiReservedMemorySize|0x3000000
!endif

   #
   # PCD to determine Pch Series LP = 0x00 / H & S= 0x01
   #
   gHpIntelChipsetPkgTokenSpaceGuid.PcdPchSeries|1


!if ($(TARGET) == DEBUG) OR ($(HP_POST_CODE_TO_SERIAL_PORT_ENABLE) == TRUE)
   gHpIntelChipsetPkgTokenSpaceGuid.PcdStatusCodeUseSerialPortPlatform|TRUE
!endif

   # Specifies whether StatusCode is reported via PostCode
!if gPlatformModuleTokenSpaceGuid.PcdPostCodeStatusCodeEnable == TRUE
   gPostCodeDebugFeaturePkgTokenSpaceGuid.PcdStatusCodeUsePostCode|TRUE
!else
   gPostCodeDebugFeaturePkgTokenSpaceGuid.PcdStatusCodeUsePostCode|FALSE
!endif



   #    Used as GPO to control Fingerprinter Lock/Unlock.
   #    High means that Fingerprinter is unlock. Low means that Fingerprinter is lock.
   #    GPP_F9/FPR_LOCK# :  FPR_LOCK#   (If it is not support, please set it as 0xFF.)
   #
   gHpIntelChipsetPkgTokenSpaceGuid.FprLockGpioPin|0xFFFFFFFF            # not support
   gHpIntelChipsetPkgTokenSpaceGuid.FprLockGpioActive|0xFF         # not support




   gHpIntelChipsetPkgTokenSpaceGuid.PcdMipiFrontCameraPortId|0
   gHpIntelChipsetPkgTokenSpaceGuid.PcdMipiIRCameraPortId|0

   # Default disable VDM Message.
   gNuvotonCommonTokenSpaceGuid.PcdCCGxEventMask|0x01FFFF7F


   # The method to control legacy USB port charging
   # 0: The platform does not support legacy(Type-A) USB port charging
   # 1: The platform supports legacy USB port charging (Notebook). Charging function will be disabled when battery is lower then a user entered percentage
   # 2: The platform supports legacy USB port charging (Desktop)
   gHpExtUsbPortCfgPubIntPkgTokenSpaceGuid.PcdLegacyUsbChargingSupportType|2

   gEfiSioTokenSpaceGuid.PcdRposDockSupport|FALSE

   gEfiHpDmarTokenSpaceGuid.PcdDmarFeatureSupport|TRUE
   gEfiHpDmarTokenSpaceGuid.PcdHpDmarEnableAllDebugMSG|FALSE

   # PCD to define the default value of "Pre-boot DMA protection" option in setup menu.
   # 0: Disabled, 1: TBT Only, 2:Protect All, 3:Protect All with approved White list.
   gEfiHpDmarTokenSpaceGuid.PcdDmaProtectionScopeDefaultValue|2


   # This GUID is for Thunderbolt(TM) Capsule function.
   # DT800 is Tower system. So Thor PCD token need to set zero.
   gHpFirmwareFlashPubIntPkgTokenSpaceGuid.PcdViserraMRTD3FWGuid|{0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}

   # Platforms with eSPI(Intel) should set to 0x0F, all other platforms(AMD) should set to 0xB
   # BIT 0 & 1 are set in previous generations
   # BIT 2, indicates seamless firmware update is supported(Intel eSPI platforms)
   # BIT 3, indicates BIOS supports upgrades without BiosAdmin/BEAM authentications(all 2022 platforms)
   gHpFirmwareFlashPubIntPkgTokenSpaceGuid.PcdFURGenerationDefinition|0x1F

  #
  # FALSE - Platform does not support ME EC recovery. EX : Surestart lite platform
  # TRUE - Platform supports ME EC recovery. EX : 1000/800/600 series
  #
!if $(SURESTART_SUPPORT) != TRUE
  gHpFirmwareFlashPubIntPkgTokenSpaceGuid.PcdMeEcRecoverySupport|FALSE
!endif

#!if gPlatformModuleTokenSpaceGuid.PcdPerformanceEnable == TRUE
#   ## Control which FPDT record format will be used to store the performance entry.
#   # On TRUE, the string FPDT record will be used to store every performance entry.
#   # On FALSE, the different FPDT record will be used to store the different performance entries.
#   gEfiMdeModulePkgTokenSpaceGuid.PcdEdkiiFpdtStringRecordEnableOnly|TRUE
#!endif

   gEfiHpPlatformPkgTokenSpaceGuid.PrivacyPanelCableGpioPin     |0xFFFFFFFF       # not support
   gEfiHpPlatformPkgTokenSpaceGuid.PrivacyPanelCableGpioActive  |0xFF       # not support

   #
   # This is for USB3.2 gen2x2 support
   # Possible Paired combinations are: {0,1}, {2,3}, {4,5}, {6,7}, {8,9}
   # Example:
   # Case 1: No Usb3.2 gen2x2 support => {0xff}
   # Case 2: 1 Pair of USB3.2 Gen2x2 with Usb3 port0, 1 => {0, 1}
   # case 3: 2 pairs of USB3.2 gen2x2 with Usb3 port 0,1 and 4,5 => {0, 1, 4, 5}
   #
   gHpIntelChipsetPkgTokenSpaceGuid.PcdHpUsbGen2x2PortDefine|{6,7}

##PCDs for SGX Enable default setting: 0 - default SW control, 1 - DT800, 2 - DT600, 3 - DT400
   gHpIntelChipsetPkgTokenSpaceGuid.PcdSgxEnableDefaultSetting|0x1

   #Set power on from keyboard port number USB_P2 on connector J9, USB_P3 on connector J9
   gHpIntelChipsetPkgTokenSpaceGuid.PcdKeyboardPowerOnPort|{ 0x01, 0x02, 0xFF, 0xFF, 0xFF, 0xFF }


   #    Used as GPO to determine if SMBUS is used by Scaler or other Smbus slave device
   #    Low: Smbus is used by other Smbus slave device. High: Smbus is used by Scaler.
   #    GPP_B4 :  HPGP_ISP_CONTROL   (If it is not support, please set it as 0xFF.)
   #
   gHpIntelChipsetPkgTokenSpaceGuid.ScalerSmbusIspControlGpioInfo|{0xFF, 0xFF, 0xFF}   # unsupported

   # PCD to determine if platform supports USB Dual 3.2 Gen1 Flex I/O type-A ladder card
   gHpExtUsbPortCfgPubIntPkgTokenSpaceGuid.PcdDualUSBTypeALadderCardVidDid|0x30421B21 # VID 0x1B21/DID 0x3042
   gHpIntelChipsetPkgTokenSpaceGuid.PcdDtDualUSBTypeALadderCardPchPcieRpNum|5
   gHpExtUsbPortCfgPubIntPkgTokenSpaceGuid.PcdAllowUsbHIDWhenPortsDisabled|TRUE

[PcdsFixedAtBuild.IA32]
   gIntelSiliconPkgTokenSpaceGuid.PcdVTdPeiDmaBufferSize|0x02400000

[PcdsFixedAtBuild.X64]

  gEfiSioTokenSpaceGuid.PcdSioSecuritySupport|TRUE

[PcdsDynamicDefault]
   # The method to control external USB ports
   # 0: Do not support usb port enable/disable control
   # 1: each external usb ports has a option to control the enable/disable separately. (DEFAULT)
   # 2: There's only 1 option for all externa usb ports to enable/disable all those ports.
   gHpExtUsbPortCfgPubIntPkgTokenSpaceGuid.PcdExternalUsbPortControlMethod|1

   # The method to control external USB ports
   # 0: Do not support disable USB ports
   # 1: Disable USB port on EndOfDxe
   # 2: Disable USB port on PreReadyToBoot
   # 3: Disable USB port on ReadyToBoot
   gHpUsbPortConfigPubIntPkgTokenSpaceGuid.PcdHpUsbPortDisableTime|1
   #
   # Bridge definition that Storage device is byhind Bridge.
   # BIOS Recovery function need to enable storage device in PEI phase.
   # The C style structure is defined as below:<BR>
   #  typedef struct {<BR>
   #    UINT8  Bus;          /// Bus
   #    UINT8  Dev;          /// Device
   #    UINT8  Func;         /// Function
   #    UINT8  TempBus;      /// Assign Temporary Bus
   #  } BRIDGE_PFA;<BR>
   #
#   gHpIntelChipsetPkgTokenSpaceGuid.PcdBridgesListForNVMe|{0x00, 0x1B, 0x00, 0x0A, 0x00, 0x1B, 0x04, 0x0B, 0xFF, 0xFF, 0xFF, 0xFF}
   # Set 0xFF to allow scanning all PCIe bridges to initial NVME device
   gHpIntelChipsetPkgTokenSpaceGuid.PcdBridgesListForNVMe|{0xFF}

   #
   # To support TPM interrupt, given a initial PCD default data to UINT32(0) to prevent build error,
   # the actual PcdTpm2PossibleIrqNumBuf buffer data will be assigned in HpTpmInterruptGpioConfigPei.c
   #
   gEfiSecurityPkgTokenSpaceGuid.PcdTpm2PossibleIrqNumBuf|{0x00, 0x00, 0x00, 0x00}
   gEfiSecurityPkgTokenSpaceGuid.PcdTpm2SelfTestPolicy|0

   # PCD to determine ISH always exist or reference GPIO.
   # If FALSE, BIOS will refer to ALS GPIO detection (PcdAlsDetGpioPinGroup, PcdAlsDetGpioPin, PcdAlsDetGpioActive) to determine if need to enable ISH controller
   gHpIntelChipsetPkgTokenSpaceGuid.PcdIshAlwaysEnable|FALSE


[PcdsDynamicExDefault.common.DEFAULT]
   #
   # System BIOS firmware update GUID.
   # 69697ed0-c234-461d-a4ef-f701aede36f8
   gEfiHpFirmwareUpdatePubIntPkgTokenSpaceGuid.PcdSystemFirmwareGuid|{ 0xd0, 0x7e, 0x69, 0x69, 0x34, 0xc2, 0x1d, 0x46, 0xa4, 0xef, 0xf7, 0x01, 0xae, 0xde, 0x36, 0xf8}

   #
   # Combined firmware updated GUID
   # 9195e63c-4cf3-447d-a0c7-0ffd6203e634
   gEfiHpFirmwareUpdatePubIntPkgTokenSpaceGuid.PcdCombinedSystemFirmwareGuid|{0x3c, 0xe6, 0x95, 0x91, 0xf3, 0x4c, 0x7d, 0x44, 0xa0, 0xc7, 0x0f, 0xfd, 0x62, 0x03, 0xe6, 0x34}

[PcdsPatchableInModule.Common]
   # Change to remove EFI_D_INFO by default, can add on individual drivers for debug if desired
   gEfiMdePkgTokenSpaceGuid.PcdDebugPrintErrorLevel|0x80000046
