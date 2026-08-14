#
# (c) Copyright 2012 - 2025 HP Development Company, L.P.
# This software and associated documentation (if any) is furnished under a license and may only be used or
# copied in accordance with the terms of the license. Except as permitted by such license, no part of this
# software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
# form or by any means without the express written consent of HP Development Company.
#

[Defines]
#[HP_ADD]+ Sync with BoardPkg.dsc
  #
  # Set platform specific package/folder name, same as passed from PREBUILD script.
  # PLATFORM_PACKAGE would be the same as PLATFORM_NAME as well as package build folder
  # DEFINE only takes effect at R9 DSC and FDF.
  #
  DEFINE      PLATFORM_PACKAGE                = MinPlatformPkg
  DEFINE      PLATFORM_FULL_PACKAGE           = MeteorLakePlatSamplePkg
  DEFINE      PLATFORM_SI_PACKAGE             = ClientOneSiliconPkg
  DEFINE      C1S_PRODUCT_PATH                = ClientOneSiliconPkg/Product/MeteorLake
  DEFINE      PLATFORM_FSP_BIN_PACKAGE        = MeteorLakeFspBinPkg
  DEFINE      PLATFORM_BOARD_PACKAGE          = MeteorLakeBoardPkg
  DEFINE      PLATFORM_OPEN_BOARD_PACKAGE     = MeteorLakeOpenBoardPkg
  DEFINE      PLATFORM_FEATURES_PATH          = $(PLATFORM_FULL_PACKAGE)/Features
  DEFINE      PLATFORM_BIN_PACKAGE            = MeteorLakeBinPkg
  DEFINE      COMMON_BIN_PACKAGE              = CommonBinPkg

  #
  # Define ESRT GUIDs for Firmware Management Protocol instances
  #
  DEFINE FMP_CLIENT_PLATFORM_SYSTEM_TSN_MAC_ADDR  = 6FEE88FF-49ED-48F1-B77B-EAD15771ABE7 # gFmpDevicePlatformTsnMacAddrGuid
  #
  # Defines Boards paths
  #
  DEFINE      BOARD_MTL_BOARDS              = $(PLATFORM_BOARD_PACKAGE)/MeteorLakeBoards
  DEFINE      PROJECT_MTL_BOARDS            = $(PLATFORM_BOARD_PACKAGE)/MeteorLakeBoards
#[HP_ADD]- Copy from BoardPkg.dsc

  #
  # For HP Project
  #
  DEFINE      ME_SKU                          = FULL
  DEFINE      HP_PLATFORM_PACKAGE             = HpPlatformPkg
  DEFINE      HP_PLATFORM_PROJECT_PATH        = HpPlatformPkg/MultiProject/$(HP_PROJECT_NAME)
  DEFINE      HP_DESKTOP_PACKAGE              = HpDtPkg
  DEFINE      HP_CHIPSET_PACKAGE              = HpIntelChipsetPkg
  DEFINE      HP_TBT_PACKAGE                  = HpThunderboltPkg
  DEFINE      HP_DMAR_PACKAGE                 = HpDmarPkg
  DEFINE      HP_MODERN_STANDBY_PACKAGE       = HpModernStandbyPkg
  DEFINE      HP_EPSC                         = Sio
  DEFINE      HP_EPSC_PACKAGE                 = HpNuvoton324Pkg
  DEFINE      HP_EPSC_COMMON_PACKAGE          = HpEpscCommon
  DEFINE      HP_DT_USBTYPEC_PACKAGE          = HpDtUsbTypeCPkg
  DEFINE      HP_CORE                         = HpCore
  DEFINE      HP_CORE_PVT                     = $(HP_CORE)/HpCorePvt
  DEFINE      HP_CORE_PVT_BINS                = $(HP_CORE)/HpCorePvtBins
  DEFINE      HP_FEATURE                      = HpFeature
  DEFINE      HP_FEATURE_PVT                  = HpFeaturePvt
  DEFINE      HP_FEATURE_PVT_BINS             = HpFeaturePvtBins

  DEFINE      HP_PROJECT_SOURCE_POSTFIX       = $(HP_SERIES)


  #
  # HP Core Define
  #
  !include $(HP_CORE)/HpCoreDef.dsc
  !include $(HP_CORE)/HpCorePvtDef.dsc
  !include $(HP_CORE_PVT_BINS)/HpCorePvtBinsDef.dsc
#[HP_FEATURE]+
  !include $(HP_FEATURE)/HpFeatureDef.dsc
  !include $(HP_FEATURE)/HpFeaturePvtDef.dsc
  !include $(HP_FEATURE_PVT_BINS)/HpFeaturePvtBinsDef.dsc
  !include $(HP_CHIPSET_PACKAGE)/HpFeature/HpFeatureChipsetDef.dsc
#[HP_FEATURE]-

  #
  #  HP Nuvoton Define
  #
  !include $(HP_EPSC_COMMON_PACKAGE)/HpNuvotonCommonPkgDef.dsc
  !include $(HP_EPSC_PACKAGE)/$(HP_EPSC_PACKAGE)Def.dsc

#[HP_ADD]+ Sync with BoardPkg.dsc
  #
  # Silicon On/Off feature are defined here
  #
  !include $(C1S_PRODUCT_PATH)/SiPkgPcdInit.dsc
  !include $(PLATFORM_BOARD_PACKAGE)/BoardPkgPcdInit.dsc
  !include $(PLATFORM_BOARD_PACKAGE)/BoardPkgPcdUpdate.dsc
  !include $(BOARD_MTL_BOARDS)/BoardVpdPcdsInit/BoardVpdPcdInit.dsc
#[HP_ADD]+ Sync with BoardPkg.dsc

  #
  # HP Post Code
  #
  !include $(HP_FEATURE)/PostCodeForEDKII_00.dsc
  !include $(HP_CORE)/PostCodeForHpCore_01.dsc
  !include $(HP_EPSC_COMMON_PACKAGE)/PostCodeForEpscCommon_02.dsc
  !include $(HP_EPSC_PACKAGE)/PostCodeForNuvotonSio_02.dsc
  !include $(HP_DT_USBTYPEC_PACKAGE)/PostCodeForDtUsbTypeC_02.dsc
  !include $(HP_DESKTOP_PACKAGE)/PostCodeForDt_04.dsc
  !include $(HP_CHIPSET_PACKAGE)/PostCodeForIntelChipset_06.dsc
  !include $(HP_CHIPSET_PACKAGE)/../PostCodeForIntelCommon_07.dsc
  !include $(HP_CHIPSET_PACKAGE)/PostCodeForIntelReferenceCode_08.dsc
  !include $(HP_CORE)/PostCodeForMiscCore_09.dsc
  !include $(HP_TBT_PACKAGE)/PostCodeForHpThunderBolt_0B.dsc
  !include $(HP_CON_DEV_PACKAGE_PUB_SRC_PKG)/PostCodeForConDev_0C.dsc
  !include $(HP_FEATURE)/PostCodeForHpFeature_0E.dsc
  !include PostCodeForPlatform_0F.dsc

#[HP_FEATURE]+
  !include $(HP_FEATURE)/HpFeatureConfig.dsc
  !include $(HP_CHIPSET_PACKAGE)/HpFeature/HpFeatureChipsetConfig.dsc
#[HP_FEATURE]-

  #
  # Import PCD feature switch default value
  #
  !include $(HP_TBT_PACKAGE)/HpTbtPcdDefault.dsc
  !include $(HP_CHIPSET_PACKAGE)/HpIntelChipsetPkgPcdDefault.dsc



  #
  # Platform On/Off features are defined here
  #
  !include HpPlatformPkg/MultiProject/PlatformConfig.dsc
  !include $(HP_CORE)/HpCoreConfig.dsc

  #
  # Import Intel Chipset Common Definitions
  #
  !include $(HP_CHIPSET_PACKAGE)/$(HP_CHIPSET_PACKAGE)Def.dsc
#[HP_MOD]+ Copy from BoardPkg.dsc
################################################################################
#
# Defines Section - statements that will be processed to create a Makefile.
#
################################################################################
[Defines]
  PLATFORM_NAME                       = HpPlatformPkg
  PLATFORM_GUID                       = 465B0A0B-7AC1-443b-8F67-7B8DEC145F90
  PLATFORM_VERSION                    = 0.1
  DSC_SPECIFICATION                   = 0x00010005


  OUTPUT_DIRECTORY                    = Build/$(HP_PLATFORM_PACKAGE)
  SUPPORTED_ARCHITECTURES             = IA32|X64
  BUILD_TARGETS                       = DEBUG|RELEASE
  SKUID_IDENTIFIER                    = $(PLATFORM_SKUID)
  FLASH_DEFINITION                    = $(HP_PLATFORM_PACKAGE)/PlatformPkg.fdf
  VPD_TOOL_GUID                       = 8C3D856A-9BE6-468E-850A-24F7A8D38E08


!if $(DEBUG_BIOS_ENABLE) == TRUE
  DEFINE DEBUG_MESSAGE_ENABLE     = TRUE
  DEFINE OPTIMIZE_COMPILER_ENABLE = TRUE
!else
  DEFINE DEBUG_MESSAGE_ENABLE     = FALSE
  DEFINE OPTIMIZE_COMPILER_ENABLE = TRUE
  # MDEPKG_NDEBUG is introduced for the intention
  # of size reduction when compiler optimization is disabled. If MDEPKG_NDEBUG is
  # defined, then debug and assert related macros wrapped by it are the NULL implementations.
  DEFINE DEBUG_BUILD_OPTIONS = -D MDEPKG_NDEBUG -D NDEBUG
!endif
  DEFINE PLATFORMX64_ENABLE               = TRUE
!if gPlatformModuleTokenSpaceGuid.PcdNetworkEnable == TRUE
  !include NetworkPkg/HpNetwork.dsc.inc
!endif

!if $(LFMA_ENABLE) == TRUE
  FIX_LOAD_TOP_MEMORY_ADDRESS         = 0xFFFFFFFFFFFFFFFF
  DEFINE   TOP_MEMORY_ADDRESS         = 0xFFFFFFFFFFFFFFFF
!else
  FIX_LOAD_TOP_MEMORY_ADDRESS         = 0x0
  DEFINE   TOP_MEMORY_ADDRESS         = 0x0
!endif

!if gSiPkgTokenSpaceGuid.PcdStatusCodeUseTraceHub == TRUE
  DEFINE     TRACEHUB     = TraceHub
!else
  DEFINE     TRACEHUB     =
!endif

###################################################################################################
#
# Add package-specific "definition" DSCs here.
#
# The files included here are used to
#   1.  define the macros associated with the DSC's parent package
#   2.  override the values of macros previously defined by more sharable packages
#   3.  override the default value of PCDs specified by a DEC or an INF file
#
# To ensure overrides are performed in the proper order, the DSCs must be listed in order of
# decreasing commonality (i.e. list the most common package's DSCs first).
#
###################################################################################################
  #
  # Network definitions
  #
  DEFINE NETWORK_TLS_ENABLE             = FALSE
  DEFINE NETWORK_HTTP_BOOT_ENABLE       = FALSE

  !include $(HP_CHIPSET_PACKAGE)/HpIntelChipsetPkgOverrideIntelPcd.dsc

  #
  # HpCore
  #
  !include $(HP_CORE)/HpCoreInf.dsc

  #
  # HpFeature
  #
  !include $(HP_FEATURE)/HpFeatureInf.dsc
  !include $(HP_CHIPSET_PACKAGE)/HpFeature/HpFeatureChipsetInf.dsc 

  #
  # Intel RC/HpChipset
  #
  !include $(PLATFORM_BOARD_PACKAGE)/BoardPkg.dsc
  !include $(HP_CHIPSET_PACKAGE)/HpIntelChipsetPkg.dsc
  !include $(HP_MODERN_STANDBY_PACKAGE)/HpModernStandbyPkg.dsc
  !include $(HP_DMAR_PACKAGE)/HpDmarPkg.dsc
  !include $(HP_TBT_PACKAGE)/HpThunderboltPkgInf.dsc
  !include HpDtUsbTypeCPkg/HpDtUsbTypeCPkgDef.dsc

  #
  # components
  #
  !include NetworkPkg/NetworkDefines.dsc.inc
  !include HpDtPkg/HpDtPkg.dsc
!if $(CRB_BOOT_SUPPORT) == TRUE
  !include HpVirtualEcPkg/HpVirtualEcPkg.dsc
!else
  !include $(HP_SIO_PACKAGE)/HpNuvoton324PkgInf.dsc
  !include $(HP_NUVOTON_COMMON_PACKAGE)/HpNuvotonCommonPkgInf.dsc
  !include $(HP_SIO_PACKAGE)/HpFeature/HpFeatureSioChipsetInf.dsc
  !include $(HP_DT_USBTYPEC_PACKAGE)/HpDtUsbTypeCPkgInf.dsc
!endif
   !include HpPlatformPkg/MultiProject/PlatformHookLibInf.dsc


################################################################################
#
# Library Class section - list of all Library Classes needed by this Platform.
#
################################################################################
[LibraryClasses.common]
# HP: The platform decides which SIO will implement the serial port PlatformHookLib library
  PlatformHookLib|$(HP_PLATFORM_PACKAGE)/Library/SerialPortPlatformHookLib/SerialPortPlatformHookLib.inf
  PlatformRequestLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformRequestLib/PlatformRequestLib.inf

  PcdExportLib|$(HP_PLATFORM_PACKAGE)/Library/BasePcdExportLib/BasePcdExportLib.inf

  S3BootScriptTable|$(HP_PLATFORM_PACKAGE)/Library/S3BootScriptTable/S3BootScriptTable.inf

!if gEfiSioTokenSpaceGuid.PcdDGpuVpmSupport == TRUE
  HpDgpuVpmPortingLib|$(HP_PLATFORM_PACKAGE)/Library/HpDgpuVpmPortingLib/HpDgpuVpmPortingLib.inf
!endif
  HidI2cPlatformSupportLib|$(HP_HUMAN_INTERFACE_DEVICES_PUB_SRC_PKG)/Library/DxeHidI2cPlatformSupportLibNull/DxeHidI2cPlatformSupportLibNull.inf


[LibraryClasses.Common.PEIM]
  #
  # PEI phase common
  #
  PeiKBPowerOnLib|$(HP_PLATFORM_PACKAGE)/Library/HpKBPowerOnLib/Pei/PeiKBPowerOnLib.inf
  HpPlatformInfoHobHookLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformInfoHobHookLib/HpPlatformInfoHobHookLib.inf
  HpThermalPlatformHookPeiLib|$(HP_PLATFORM_PACKAGE)/Library/HpThermalPlatformHookLibPei/HpThermalPlatformHookLibPei.inf
  # HP Platform RC Policy Override PEI Hook Library
  # Purpose: Allow platform to customize RC policy.
  HpVerbTableLib|$(HP_PLATFORM_PACKAGE)/Library/HpVerbTableLib/HpVerbTableLib.inf
  PlatformNuvotonInitPeiLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformNuvotonInitPeiLib/PlatformNuvotonInitPeiLib.inf

!if $(CRB_BOOT_SUPPORT) == FALSE
  HpPlatformRcPolicyOverrideHookLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformRcPolicyOverrideHookLibPei/HpPlatformRcPolicyOverrideHookLibPei.inf
  HpPlatformServicesLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformServicesLibPei/HpPlatformServicesLibPei.inf
  HpNuvotonMiscCommonLib|$(HP_EPSC_COMMON_PACKAGE)\Library\HpNuvotonMiscCommonLib\HpNuvotonMisc$(HP_EPSC)CommonLibPei.inf
!endif


!if $(HP_VPM_SUPPORT) == TRUE
  HpSioVoltagePwrMonitorLib|$(HP_PLATFORM_PACKAGE)/Library/HpSioVoltagePwrMonitorLib/HpSioVoltagePwrMonitorLib.inf
!endif
  HpVpinSelectionLib|$(HP_PLATFORM_PACKAGE)/Library/HpVpinSelectionLib/HpVpinSelectionLib.inf

  PeiHpMultiBoardInitPreMemLib|$(HP_PLATFORM_PACKAGE)/Library/HpBoardInitLib/Pei/PeiMultiBoardInitPreMemLib.inf
  PeiHpMultiBoardInitPostMemLib|$(HP_PLATFORM_PACKAGE)/Library/HpBoardInitLib/Pei/PeiMultiBoardInitPostMemLib.inf

  FirmwareBootMediaLib|IntelSiliconPkg/Library/PeiDxeSmmBootMediaLib/PeiFirmwareBootMediaLib.inf
  FirmwareBootMediaInfoLib|BoardModulePkg/Library/PeiFirmwareBootMediaInfoLib/PeiFirmwareBootMediaInfoLib.inf

!ifdef $(SOURCE_DEBUG_USE_USB3)
  DebugCommunicationLib|SourceLevelDebugPkg/Library/DebugCommunicationLibUsb3/DebugCommunicationLibUsb3Pei.inf
!endif

  PlatformSioInitPeiLib|$(HP_PLATFORM_PACKAGE)\Library\PlatformSioInitPeiLib\PlatformSioInitPeiLib.inf

[LibraryClasses.Common.SEC]


[LibraryClasses.Common.DXE_DRIVER]
  PlatformBootManagerLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformBootManagerLib/PlatformBootManagerLib.inf
  HpThermalPlatformHookDxeLib|$(HP_PLATFORM_PACKAGE)/Library/HpThermalPlatformHookLibDxe/HpThermalPlatformHookLibDxe.inf
!if $(CRB_BOOT_SUPPORT) == FALSE
  HpPlatformSpecificHookLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformSpecificHookLibDxe/HpPlatformSpecificHookLibDxe.inf
  HpNuvotonMiscCommonLib|$(HP_EPSC_COMMON_PACKAGE)/Library/HpNuvotonMiscCommonLib/HpNuvotonMisc$(HP_EPSC)CommonLibDxe.inf
  HpPlatformRcPolicyOverrideHookLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformRcPolicyOverrideHookLibDxe/HpPlatformRcPolicyOverrideHookLibDxe.inf
!endif
  HpPlatformInfoDxeLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformInfoDxeLib/HpPlatformInfoDxeLib.inf
  HpPlatformGraphicsDxeLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformGraphicsConfiguration/PlatformGraphicsConfiguration.inf

[LibraryClasses.Common.DXE_DRIVER, LibraryClasses.Common.DXE_SMM_DRIVER]
!if $(CRB_BOOT_SUPPORT) == FALSE
  HpPlatformServicesLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformServicesLib/HpPlatformServicesLib.inf
!endif

[LibraryClasses.common.DXE_SMM_DRIVER, LibraryClasses.common.DXE_DRIVER]
!if $(HP_SERIES) == AIO800 || $(HP_SERIES) == AIO400
   ExternalUsbPortDxeLib|$(HP_PLATFORM_PACKAGE)/Library/ExternalUsbPortLib/ExternalUsbPortDxeLib.inf
!endif

[LibraryClasses.common.DXE_SMM_DRIVER]
  SmmNvmeLib|MdeModulePkg/Library/SmmNvmeLib/SmmNvmeLib.inf
  SmmKBPowerOnLib|$(HP_PLATFORM_PACKAGE)\Library\SmmKBPowerOnLib\SmmKBPowerOnLib.inf
  HpThermalPlatformHookSmmLib|$(HP_PLATFORM_PACKAGE)/Library/HpThermalPlatformHookLibSmm/HpThermalPlatformHookLibSmm.inf
!if $(HP_VPM_SUPPORT) == TRUE
  HpSioVoltagePwrMonitorLib|$(HP_PLATFORM_PACKAGE)/Library/HpSioVoltagePwrMonitorLib/HpSioVoltagePwrMonitorLib.inf
!endif
  HpVpinSelectionLib|$(HP_PLATFORM_PACKAGE)/Library/HpVpinSelectionLib/HpVpinSelectionLib.inf
!if $(CRB_BOOT_SUPPORT) == FALSE
  HpPlatformSpecificHookLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformSpecificHookLibSmm/HpPlatformSpecificHookLibSmm.inf
  HpNuvotonMiscCommonLib|$(HP_EPSC_COMMON_PACKAGE)\Library\HpNuvotonMiscCommonLib\HpNuvotonMisc$(HP_EPSC)CommonLibSmm.inf
!endif

[Components.$(PEI_ARCHITECTURE)]
   $(HP_CHIPSET_PACKAGE)/FIT/FitTableGenerate.inf
   $(HP_CHIPSET_PACKAGE)/FIT/FitTableInfo.inf

!if $(HP_SERIES) == AIO800 || $(HP_SERIES) == AIO400
  $(HP_PLATFORM_PACKAGE)/AioUsbPortControlPei/AioUsbPortControlPei.inf
!endif

!if gSiPkgTokenSpaceGuid.PcdSourceDebugEnable == TRUE
   SourceLevelDebugPkg/DebugAgentPei/DebugAgentPei.inf {
      <LibraryClasses>
         DebugAgentLib|SourceLevelDebugPkg/Library/DebugAgent/SecPeiDebugAgentLib.inf
   }
!endif
!if $(SURESTART_SUPPORT) == FALSE
   MdeModulePkg/Bus/Pci/XhciPei/XhciPei.inf
   MdeModulePkg/Bus/Usb/UsbBotPei/UsbBotPei.inf
   MdeModulePkg/Bus/Usb/UsbBusPei/UsbBusPei.inf
   MdeModulePkg/Bus/Ata/AhciPei/AhciPei.inf
   MdeModulePkg/Bus/Pci/NvmExpressPei/NvmExpressPei.inf
   FatPkg/FatPei/FatPei.inf
!endif
   $(HP_CHIPSET_PACKAGE)/FlashInfo/Pei/FlashInfoPei.inf
   $(HP_PLATFORM_PACKAGE)/BiosUpdatePlatformPolicy/BiosUpdatePlatformPolicyPei.inf

   $(HP_PLATFORM_PACKAGE)/HpPlatformServices/Pei/HpPlatformPeiServices.inf

   $(HP_PLATFORM_PACKAGE)/PlatformPei/PlatformPei.inf {
      <LibraryClasses>
         ResetSystemLib|$(PLATFORM_SI_PACKAGE)/Pch/Library/BaseResetSystemLib/BaseResetSystemLib.inf
   }
!if gEfiHpPlatformPkgTokenSpaceGuid.gRposDockUSBWakeOnLanSupport == TRUE
   $(HP_PLATFORM_PACKAGE)/RposDockUsbLanWakeSource/RposDockUsbLanWakeSourcePei.inf
!endif

#!if gSiPkgTokenSpaceGuid.PcdBootGuardEnable == TRUE
  !include $(HP_CHIPSET_PACKAGE)/Override/Edk2/SecurityPkg/SecurityPkgInf.dsc  # For Boot Guard ACM involve PCR 0 measurement.
#!else
#  !include SecurityPkg/SecurityPkgInf.dsc
#!endif

   #
   # SIO15 & FireBird F/W's Bootloader structure
   #
   $(HP_SIO_PACKAGE)/HpSioFireBirdBootloader/HpSioFireBirdBootloader.inf
   $(HP_PLATFORM_PACKAGE)\HpSecureStorageDevicePei\HpSecureStorageDevicePei.inf

   BoardModulePkg/FirmwareBootMediaInfo\FirmwareBootMediaInfoPei.inf

[LibraryClasses.common]
#
#  ScalarControlGpioLib
#
!if $(HP_SCALAR_FW_CAPSULE_SUPPORT) == TRUE
  ScalarControlGpioLib|$(HP_PLATFORM_PACKAGE)/Library/HpScalarControlGpioLib/ScalarControlGpioLib.inf
!endif

   ExpansionSlotLib|$(HP_PLATFORM_PACKAGE)/Library/ExpansionSlotLib/ExpansionSlotLib.inf

!if gEfiSioTokenSpaceGuid.PcdCustomFanConfigLibSupport == TRUE
  HpFanConfigurationLib|$(HP_PLATFORM_PACKAGE)/Library/HpFanConfigurationLib/HpFanConfigurationLib.inf
!endif

!if gNuvotonCommonTokenSpaceGuid.PcdNuvotonCommonPlatformHookLibSupport == TRUE
   # DM specific
   HpNuvotonCommonPlatformHookLib|HpPlatformPkg/Library/HpNuvotonCommonPlatformHookLib/HpNuvotonCommonPlatformHookLib.inf
!endif

   HpPlatformTypeCHookLib|HpPlatformPkg/Library/HpPlatformTypeCHookLib/HpPlatformTypeCHookLib.inf

!if $(HP_SIO_PRIVACY_PANEL_SUPPORT) == TRUE
   HpPrivacyPanelLib|$(HP_PLATFORM_PACKAGE)/Library/HpPrivacyPanelLib/HpPrivacyPanelLib.inf
!endif

!if $(HP_SCALAR_PRIVACY_PANEL_SUPPORT) == TRUE
   HpScalarPrivacyPanelLib|$(HP_PLATFORM_PACKAGE)/Library/HpScalarPrivacyPanelLib/HpScalarPrivacyPanelLib.inf
!endif

!if $(HP_SERIES) == AIO800 || $(HP_SERIES) == AIO400
  HpUsbcFirmwareFlashPlatformHookLib|$(HP_PLATFORM_PACKAGE)/Library/HpUsbcFirmwareFlashPlatformHookLib/HpUsbcFirmwareFlashPlatformHookLib.inf
!endif

[LibraryClasses.X64]
#
#  ScalarControlGpioLib
#
!if $(HP_SCALAR_FW_CAPSULE_SUPPORT) == TRUE
    ScalarControlGpioLib|$(HP_PLATFORM_PACKAGE)/Library/HpScalarControlGpioLib/ScalarControlGpioLib.inf
!endif

[Components.X64]
!if $(TARGET) == DEBUG
  $(HP_CORE)/HpUserInterface/PubSrcPkg/HpJpeg/HpJpeg.inf {
    <LibraryClasses>
      DebugLib|MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf
  }
!endif
  $(HP_PLATFORM_PACKAGE)/HpPlatformFeaturesDxe/HpPlatformFeaturesDxe.inf
  $(HP_PLATFORM_PACKAGE)/PlatformDxe/PlatformDxe.inf
  $(HP_PLATFORM_PACKAGE)/PlatformSmm/PlatformSmm.inf
  $(HP_PLATFORM_PACKAGE)/HpPlatformServices/Dxe/HpPlatformDxeServices.inf
  $(HP_PLATFORM_PACKAGE)/HpPlatformServices/Smm/HpPlatformSmmServices.inf
  $(HP_PLATFORM_PACKAGE)/HpRuntimeBiosUpdateCheck/HpRuntimeBiosUpdateCheckDxe.inf
  $(HP_PLATFORM_PACKAGE)/HpRuntimeBiosUpdateCheck/HpRuntimeBiosUpdateCheckSmm.inf

  $(HP_PLATFORM_PACKAGE)/HpSecureStorageDeviceDxe/HpSecureStorageDeviceDxe.inf

!if $(HP_TOUCH_PANEL_INTERFACE) == USB
   $(HP_HUMAN_INTERFACE_DEVICES_PUB_SRC_PKG)/UsbTouchPanel/UsbTouchPanelDxe.inf
!endif

!if $(ENHANCED_SMART_COVER_SUPPORT) == TRUE
  $(HP_PLATFORM_PACKAGE)/SmartCover/SmartCoverPortingDxe.inf
  $(HP_PLATFORM_PACKAGE)/SmartCover/SmartCoverPortingSmm.inf
  $(HP_PLATFORM_PACKAGE)/SmartCover/SmartCoverSmbiosDxe.inf
!endif

!if gPlatformModuleTokenSpaceGuid.PcdNetworkEnable == TRUE
   !include NetworkPkg/NetworkComponents.dsc.inc

   !if $(PREBOOT_WIFI_SUPPORT) == TRUE
      NetworkPkg/WifiConnectionManagerDxe/WifiConnectionManagerDxe.inf {
         <LibraryClasses>
            BaseCryptLib|$(HP_CRYPTO_PUB_SRC_PKG)/Library/HpSecurityLib/HpSecurityDxeLib.inf
            PcdLib|MdePkg/Library/DxePcdLib/DxePcdLib.inf
      }
      HpPlatformPkg/WiFiSupport/WiFiSupport.inf
   !endif
!endif

  $(HP_PLATFORM_PACKAGE)/PciPlatform/Dxe/PciPlatform.inf

!if gSiPkgTokenSpaceGuid.PcdAcpiEnable == TRUE
  $(HP_PLATFORM_PACKAGE)/HpAcpiPlatformDxe/HpAcpiPlatformDxe.inf {
    <LibraryClasses>
       PcdLib|MdePkg/Library/DxePcdLib/DxePcdLib.inf
  }
!if $(HP_ACPI_TABLES_ENABLE) == TRUE
  $(HP_PLATFORM_PACKAGE)/AcpiTables/AcpiTables.inf {
    <BuildOptions>
      *_*_IA32_ASLPP_FLAGS   = /D ASL_BUILD
      *_*_X64_ASLPP_FLAGS    = /D ASL_BUILD
  }
!endif
!endif

  $(HP_CHIPSET_PACKAGE)/Binary/Microcode/MicrocodeUpdatesDt.inf
!if gPlatformModuleTokenSpaceGuid.PcdNetworkEnable == TRUE
  !include NetworkPkg/NetworkComponents.dsc.inc
  !if $(PREBOOT_WIFI_SUPPORT) == TRUE
    NetworkPkg/WifiConnectionManagerDxe/WifiConnectionManagerDxe.inf {
      <LibraryClasses>
        PcdLib|MdePkg/Library/DxePcdLib/DxePcdLib.inf
    }

    $(HP_PLATFORM_PACKAGE)/WiFiSupport/WiFiSupport.inf
  !endif
!endif
  $(HP_PLATFORM_PACKAGE)/BiosUpdatePlatformPolicy/BiosUpdatePlatformPolicySmm.inf

  MdeModulePkg/Universal/RegularExpressionDxe/RegularExpressionDxe.inf {
    <LibraryClasses>
      DebugLib|MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf
  }
   MdeModulePkg/Universal/Disk/RamDiskDxe/RamDiskDxe.inf
!if $(NVME_ENABLE) == TRUE
   MdeModulePkg/Bus/Pci/NvmExpressDxe/NvmExpressSmm.inf
!endif

!if gEfiHpPlatformPkgTokenSpaceGuid.gRposDockUSBWakeOnLanSupport == TRUE
   $(HP_PLATFORM_PACKAGE)/RposDockUsbLanWakeSource/RposDockUsbLanWakeSourceDxe.inf
!endif

   $(HP_DESKTOP_PACKAGE)/SetupMenu/SetupMenuDxe.inf {
      <LibraryClasses>
         NULL|$(PORT_OPTIONS_PUB_SRC_PKG)/Library/StorageDevCfgDxeLib/StorageDevCfgDxeLib.inf
!if gEfiSioTokenSpaceGuid.PcdWirelessChargerSupport == TRUE
         NULL|$(HP_SIO_PACKAGE)/Library/HpWirelessChargerLib/HpWirelessChargerDxeLib.inf
!endif
!if $(HP_RPOS_PLATFORM) == TRUE
         NULL|$(HP_SIO_PACKAGE)/Library/PoweredSerialPortDxeLib/PoweredSerialPortDxeLib.inf
!endif
   }

   $(HP_DESKTOP_PACKAGE)/SetupMenu/SetupMenuSmm.inf {
      <LibraryClasses>
!if $(S5_MAX_POWER_SAVING_SUPPORT) == TRUE
   NULL|$(HP_SIO_PACKAGE)/S5MaxPowerSavingsSmm/S5MaxPowerSavingsSmmLib.inf
!endif

!if gEfiSioTokenSpaceGuid.PcdWirelessChargerSupport == TRUE
   NULL|$(HP_SIO_PACKAGE)/WirelessCharger/WirelessChargerSmmLib.inf
!endif

!if gHpDtPkgTokenSpaceGuid.PcdAlwaysPowerStandPortsSupport == TRUE
         NULL|$(HP_DESKTOP_PACKAGE)/AlwaysPowerStandPorts/AlwaysPowerStandPortsSmmLib.inf
!endif

   }
!if $(HP_SERIES) == AIO800
  !if gEfiHpTbtPkgTokenSpaceGuid.PcdHpThunderboltSupport == TRUE
    $(HP_PLATFORM_PACKAGE)/GrSmm/HpGrSmm.inf
  !endif
!endif
   ##
   ## Include CapsuleDriversBuild.dsc to trigger customize Capsule drivers build process.
   ##
   !include $(HP_PROJECT_PATH)/Config/CapsuleDriversBuild.dsc

   ##
   ## Include LastPcdOverride.dsc to overwrite PCD token setting in last build phase with PlatformPkg.dsc.
   ## [IMPORT] Don't change this file location in PlatformPkg.dsc.
   ##
   !include LastPcdOverride.dsc
   !include LastLibOverride.dsc

   #
   # Build Options
   #
   !include BuildOptions.dsc

[PcdsDynamicExDefault]
