#
# (c) Copyright 2012 - 2025 HP Development Company, L.P.
# This software and associated documentation (if any) is furnished under a license and may only be used or
# copied in accordance with the terms of the license. Except as permitted by such license, no part of this
# software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
# form or by any means without the express written consent of HP Development Company.
#
# Module Name: HpPlatformPkg.dsc
#
# Abstract: Project Package Build Description file.
#

[Defines]
#[HP_ADD]+ Sync with BoardPkg.dsc
  #
  # Set platform specific package/folder name, same as passed from PREBUILD script.
  # PLATFORM_PACKAGE would be the same as PLATFORM_NAME as well as package build folder
  # DEFINE only takes effect at R9 DSC and FDF.
  #
  DEFINE      PLATFORM_PACKAGE                = MinPlatformPkg
  DEFINE      PLATFORM_FULL_PACKAGE           = PantherLakePlatSamplePkg
  DEFINE      PLATFORM_SI_PACKAGE             = OneSiliconPkg
  DEFINE      SILICON_PRODUCT_PATH            = OneSiliconPkg/Product/PantherLake
  DEFINE      PLATFORM_FSP_BIN_PACKAGE        = PantherLakeFspBinPkg
  DEFINE      PLATFORM_BOARD_PACKAGE          = PantherLakeBoardPkg
  DEFINE      PLATFORM_OPEN_BOARD_PACKAGE     = PantherLakeOpenBoardPkg
  DEFINE      PLATFORM_FEATURES_PATH          = $(PLATFORM_FULL_PACKAGE)/Features
  DEFINE      PLATFORM_BIN_PACKAGE            = PantherLakeBinPkg
  DEFINE      COMMON_BIN_PACKAGE              = CommonBinPkg
  DEFINE      PLATFORM_BSP_PATH               = PantherLakeBoardPkg/BoardSupport

#
# Define ESRT GUIDs for Firmware Management Protocol instances
#
  DEFINE FMP_CLIENT_PLATFORM_SYSTEM_TSN_MAC_ADDR  = 6FEE88FF-49ED-48F1-B77B-EAD15771ABE7 # gFmpDevicePlatformTsnMacAddrGuid
#
# Defines Boards paths
#
  DEFINE      BOARD_PTLUH_BOARDS             = $(PLATFORM_BOARD_PACKAGE)/PantherLakeBoards/PantherLakeMobileBoards
  DEFINE      PROJECT_PTLUH_BOARDS           = $(PLATFORM_BOARD_PACKAGE)/PantherLakeBoards/PantherLakeMobileBoards
  DEFINE      PROJECT_PTL_BOARDS_BSP         = $(PLATFORM_BOARD_PACKAGE)/BoardSupport/PantherLakeBoards/PantherLakeMobileBoards
#[HP_ADD]- Copy from BoardPkg.dsc

  #
  # For HP Project
  #
  DEFINE      ME_SKU                          = FULL
  DEFINE      HP_PLATFORM_PACKAGE             = HpPlatformPkg
  DEFINE      HP_PLATFORM_PACKAGE_DEC         = $(HP_PLATFORM_PACKAGE)/$(HP_PLATFORM_PACKAGE).dec
  DEFINE      HP_PLATFORM_TYPE                = $(HP_PLATFORM_TYPE)
  DEFINE      HP_PLATFORM_PROJECT_PATH        = HpPlatformPkg/MultiProject/$(HP_PROJECT_NAME)
  DEFINE      HP_CHIPSET_PACKAGE              = HpIntelChipsetPkg
  DEFINE      HP_MEDIA_READER_PATH            = $(PORT_OPTIONS_PUB_SRC_PKG)\FlashMediaReader\Realtek
  DEFINE      HP_TBT_PACKAGE                  = HpThunderboltPkg
  DEFINE      HP_DMAR_PACKAGE                 = HpDmarPkg
  DEFINE      HP_MODERN_STANDBY_PACKAGE       = HpModernStandbyPkg
  DEFINE      HP_EPSC_COMMON_PACKAGE          = HpEpscCommon
  DEFINE      HP_CORE                         = HpCore
  DEFINE      HP_CORE_PVT                     = $(HP_CORE)/HpCorePvt
  DEFINE      HP_CORE_PVT_BINS                = $(HP_CORE)/HpCorePvtBins
  DEFINE      HP_FEATURE                      = HpFeature
  DEFINE      HP_FEATURE_PVT                  = HpFeaturePvt
  DEFINE      HP_FEATURE_PVT_BINS             = HpFeaturePvtBins
!if $(HP_EPSC) == Virtual
  DEFINE      HP_EPSC_PACKAGE                 = HpVirtualEcPkg
  DEFINE      HP_EPSC_PACKAGE_DEF             = $(HP_EPSC_PACKAGE)/HpVirtualEcPkgDef.dsc
  DEFINE      HP_EPSC_PACKAGE_DSC             = $(HP_EPSC_PACKAGE)/HpVirtualEcPkg.dsc
  DEFINE      HP_EPSC_PACKAGE_PEIM_FDF        = $(HP_EPSC_PACKAGE)/HpVirtualEcPkgPeim.fdf
  DEFINE      HP_EPSC_PACKAGE_FDF             = $(HP_EPSC_PACKAGE)/HpVirtualEcPkgDxe.fdf
  DEFINE      HP_EPSC_PACKAGE_DEC             = $(HP_EPSC_PACKAGE)/HpVirtualEcPkg.dec
!endif
!if $(HP_EPSC) == Ec
  DEFINE      HP_EPSC_PACKAGE                 = HpNuvotonEcPkg
  DEFINE      HP_EPSC_PACKAGE_DEF             = $(HP_EPSC_PACKAGE)/HpNuvotonEcChipsetPkgDef.dsc
  DEFINE      HP_EPSC_PACKAGE_DSC             = $(HP_EPSC_PACKAGE)/HpNuvotonEcChipsetPkgInf.dsc
  DEFINE      HP_EPSC_PACKAGE_PEIM_FDF        = $(HP_EPSC_PACKAGE)/HpNuvotonEcChipsetPkgIA32.fdf
  DEFINE      HP_EPSC_PACKAGE_FDF             = $(HP_EPSC_PACKAGE)/HpNuvotonEcChipsetPkgX64.fdf
!endif
!if $(HP_EPSC) == Sio
  DEFINE      HP_EPSC_PACKAGE                 = HpNuvoton324Pkg
  DEFINE      HP_DESKTOP_PACKAGE              = $(HP_FEATURE)/HpPe/HpDtPkg
  DEFINE      HP_EPSC_PACKAGE_DEF             = $(HP_EPSC_PACKAGE)/HpNuvoton324PkgDef.dsc
  DEFINE      HP_EPSC_PACKAGE_DSC             = $(HP_EPSC_PACKAGE)/HpNuvoton324PkgInf.dsc
  DEFINE      HP_EPSC_PACKAGE_PEIM_FDF        = $(HP_EPSC_PACKAGE)/HpNuvoton324PkgIA32.fdf
  DEFINE      HP_EPSC_PACKAGE_FDF             = $(HP_EPSC_PACKAGE)/HpNuvoton324PkgX64.fdf
!endif

  DEFINE      HP_PROJECT_SOURCE_POSTFIX       = $(HP_SERIES)

  #
  # HP Core Define
  #
  !include $(HP_CORE)/HpCoreDef.dsc
  !include $(HP_CORE)/HpCorePvtDef.dsc
  !include $(HP_CORE_PVT_BINS)/HpCorePvtBinsDef.dsc

  #
  # HpFeature Define
  #
  !include $(HP_FEATURE)/HpFeatureDef.dsc
  !include $(HP_FEATURE)/HpFeaturePvtDef.dsc
  !include $(HP_FEATURE_PVT_BINS)/HpFeaturePvtBinsDef.dsc
  !include $(HP_CHIPSET_PACKAGE)/HpFeature/HpFeatureChipsetDef.dsc

  #
  # HP Epsc (Nuvoton) Define
  #
  !include $(HP_EPSC_PACKAGE_DEF)
  !include $(HP_EPSC_COMMON_PACKAGE)/HpNuvotonCommonPkgDef.dsc
  !include $(HP_PLATFORM_PACKAGE)/Include/$(HP_PLATFORM_TYPE)/HpDef.dsc.inc
#[HP_ADD]+ Sync with BoardPkg.dsc
  #
  # Silicon On/Off feature are defined here
  #
  !include $(SILICON_PRODUCT_PATH)/SiPkgPcdInit.dsc
  #
  # Platform On/Off features are defined here
  #
  !include $(COMMON_BIN_PACKAGE)/Include/Dsc/CommonBinPkgPcdInit.dsc
  !include $(PLATFORM_BIN_PACKAGE)/Include/Dsc/PantherLakeBinPkgPcdInit.dsc
  !include $(PLATFORM_BOARD_PACKAGE)/BoardPkgPcdInit.dsc
  !include $(PLATFORM_BOARD_PACKAGE)/BoardPkgPcdUpdate.dsc
  !include $(PLATFORM_BOARD_PACKAGE)/Include/Dsc/HiiStructurePcd.dsc
  !include $(BOARD_PTLUH_BOARDS)/BoardVpdPcdsInit/BoardVpdPcdInit.dsc
!if gI2cFeaturePkgTokenSpaceGuid.PcdI2cTouchCommonEnable == TRUE
  !include $(PLATFORM_BOARD_PACKAGE)/VpdI2cRpTable.dsc
!endif
!if gThcFeaturePkgTokenSpaceGuid.PcdThcMultipleVenFeatureSupport == TRUE
  !include $(PLATFORM_BOARD_PACKAGE)/VpdThcSlaveAddressTable.dsc
!endif
#[HP_ADD]+ Sync with BoardPkg.dsc

  #
  # HP Post Code
  #
  !include $(HP_FEATURE)/PostCodeForEDKII_00.dsc
  !include $(HP_CORE)/PostCodeForHpCore_01.dsc
  !include $(HP_EPSC_COMMON_PACKAGE)/PostCodeForNuvoton_02.dsc
!if $(HP_EPSC) == Ec OR $(HP_EPSC) == Sio
  !include $(HP_EPSC_PACKAGE)/PostCodeForNuvoton$(HP_EPSC)_02.dsc
!endif
!if $(HP_EPSC) == Sio
  !include $(HP_DT_USBTYPEC_PACKAGE)/PostCodeForDtUsbTypeC_02.dsc
!endif
  !include $(HP_FEATURE)/HpPe/HpDtPkg/PostCodeForDt_04.dsc
  !include $(HP_CHIPSET_PACKAGE)/PostCodeForIntelChipset_06.dsc
  !include $(HP_CHIPSET_PACKAGE)/PostCodeForIntelCommon_07.dsc
  !include $(HP_CHIPSET_PACKAGE)/PostCodeForIntelReferenceCode_08.dsc
  !include $(HP_CORE)/PostCodeForMiscCore_09.dsc
  !include $(HP_TBT_PACKAGE)/PostCodeForHpThunderBolt_0B.dsc
  !include $(HP_CON_DEV_PACKAGE_PUB_SRC_PKG)/PostCodeForConDev_0C.dsc
  !include $(HP_FEATURE)/PostCodeForHpFeature_0E.dsc
  !include PostCodeForPlatform_0F.dsc

  #
  # HpFeature Configuration
  #
  !include $(HP_FEATURE)/HpFeatureConfig.dsc
  !include $(HP_CHIPSET_PACKAGE)/HpFeature/HpFeatureChipsetConfig.dsc

  #
  # Import PCD feature switch default value
  #
  !include $(HP_TBT_PACKAGE)/HpTbtPcdDefault.dsc
  !include $(HP_CHIPSET_PACKAGE)/HpIntelChipsetPkgPcdDefault.dsc
!if $(HP_EPSC) == Ec
  !include $(HP_EPSC_PACKAGE)/HpNuvotonEcChipsetPkgPcdDefault.dsc
!endif


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
  SUPPORTED_ARCHITECTURES             = $(PEI_ARCHITECTURE)|X64
  BUILD_TARGETS                       = DEBUG|RELEASE
  SKUID_IDENTIFIER                    = $(PLATFORM_SKUID)
  DEFINE      FSP_ARCH                = X64
  FLASH_DEFINITION                    = $(HP_PLATFORM_PACKAGE)/$(HP_PLATFORM_PACKAGE).fdf

#[HP_ADD]+ Copy from BoardPkg.dsc
  VPD_TOOL_GUID                       = 8C3D856A-9BE6-468E-850A-24F7A8D38E08
  FIX_LOAD_TOP_MEMORY_ADDRESS         = 0x0
  DEFINE TOP_MEMORY_ADDRESS           = 0x0

  #
  # Default value for BoardPkg.fdf use
  #
  !if gPlatformModuleTokenSpaceGuid.PcdExtendedBiosRegionSupport == TRUE
    DEFINE BIOS_SIZE_OPTION = SIZE_170
  !else
    DEFINE BIOS_SIZE_OPTION = SIZE_140
  !endif

  PCD_DYNAMIC_AS_DYNAMICEX                  = TRUE

  #
  # Map Network Feature PCD to macro setting used in NetworkPkg/NetworkDefines.dsc.inc
  #
  !if gPlatformModuleTokenSpaceGuid.PcdNetworkEnable == TRUE
    DEFINE NETWORK_ENABLE                 = TRUE
  !else
    DEFINE NETWORK_ENABLE                 = FALSE
  !endif
  !if gPlatformModuleTokenSpaceGuid.PcdNetworkIp6Enable == TRUE
    DEFINE NETWORK_IP6_ENABLE             = TRUE
  !else
    DEFINE NETWORK_IP6_ENABLE             = FALSE
  !endif
  !if gPlatformModuleTokenSpaceGuid.PcdNetworkIscsiEnable == TRUE
    DEFINE NETWORK_ISCSI_ENABLE           = TRUE
  !else
    DEFINE NETWORK_ISCSI_ENABLE           = FALSE
  !endif
  !if gPlatformModuleTokenSpaceGuid.PcdNetworkVlanEnable == TRUE
    DEFINE NETWORK_VLAN_ENABLE            = TRUE
  !else
    DEFINE NETWORK_VLAN_ENABLE            = FALSE
  !endif
  DEFINE NETWORK_TLS_ENABLE               = TRUE
  DEFINE NETWORK_HTTP_BOOT_ENABLE         = FALSE
  DEFINE PLATFORMX64_ENABLE               = TRUE
#[HP_ADD]- Copy from BoardPkg.dsc

  !if gPlatformModuleTokenSpaceGuid.PcdNetworkEnable == TRUE
    !include NetworkPkg/HpNetwork.dsc.inc
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

  #
  # components
  #
  !include NetworkPkg/NetworkDefines.dsc.inc
  !include $(HP_EPSC_PACKAGE_DSC)
!if $(HP_EPSC) == Ec OR $(HP_EPSC) == Sio
  !include $(HP_EPSC_COMMON_PACKAGE)/HpNuvotonCommonPkgInf.dsc
  !include $(HP_EPSC_PACKAGE)/HpFeature/HpFeature$(HP_EPSC)ChipsetInf.dsc
!endif
  !include $(HP_PLATFORM_PACKAGE)/Include/$(HP_PLATFORM_TYPE)/HpLib.dsc.inc
  !include HpPlatformPkg/MultiProject/PlatformHookLibInf.dsc


################################################################################
#
# Library Class section - list of all Library Classes needed by this Platform.
#
################################################################################
[LibraryClasses.X64.PEI_CORE]
!if $(TARGET) == DEBUG
  DebugLib|$(PLATFORM_FULL_PACKAGE)/Library/BaseDebugLibAllDebugPort/BaseDebugLibAllDebugPort.inf
!endif


[LibraryClasses.common]
!if $(DESKTOP_PLATFORM) == TRUE
  ExpansionSlotLib|$(HP_PLATFORM_PACKAGE)/Library/ExpansionSlotLib/ExpansionSlotLib.inf
  !if $(HP_EPSC) == Sio
    HpFanConfigurationLib|$(HP_PLATFORM_PACKAGE)/Library/HpFanConfigurationLib/HpFanConfigurationLib.inf
  !endif
!endif

  PlatformHookLib|$(HP_PLATFORM_PACKAGE)/MultiProject/Y21Moomin/PlatformHookLib/SerialPortPlatformHookLib/SerialPortPlatformHookLib.inf
  # HP: The platform decides which SIO will implement the serial port PlatformHookLib library
  PlatformRequestLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformRequestLib/PlatformRequestLib.inf

  PcdExportLib|$(HP_PLATFORM_PACKAGE)/Library/BasePcdExportLib/BasePcdExportLib.inf
!if $(HP_EPSC) == Sio
  BaseHpPlatformServicesLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformServicesLib/BaseHpPlatformServicesSioLib.inf
!else
  BaseHpPlatformServicesLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformServicesLib/BaseHpPlatformServicesEcLib.inf
!endif

!if $(HP_SIO_PRIVACY_PANEL_SUPPORT) == TRUE
  HpPrivacyPanelLib|$(HP_PLATFORM_PACKAGE)/Library/HpPrivacyPanelLib/HpPrivacyPanelLib.inf
!endif

!if $(TARGET) == DEBUG
  DebugLib|MdePkg/Library/BaseDebugLibSerialPort/BaseDebugLibSerialPort.inf
  !if gPlatformModuleTokenSpaceGuid.PcdSerialPortEnable == TRUE
    SerialPortLib|$(PLATFORM_FULL_PACKAGE)/Library/BaseSerialPortLib/BaseSerialPortLib.inf
  !else
    #
    # HP Customized SerialPortLib due to RTSCallbackHandlePei->DebugPostCode() output POST thru SerialPortWrite () directly, only works for Serial COM port but Serial UART port.
    # And regular BaseDebugLibSerialPort will route debug message to legacy COM port 3F8/2F8 (which is only available for DT and CRB).
    # In order to route debug message to serial IO UART port (via MMIO), use HP implemented PchSerialIoUartPortLib for route debug message to serial IO UART (via MMIO)
    # 'for NB platform'
    #
    SerialPortLib|$(HP_PLATFORM_PACKAGE)/Library/PchSerialIoUartPortLib/PchSerialIoUartPortLib.inf
  !endif
!endif

  LzmaDecompressLib|MdeModulePkg/Library/LzmaCustomDecompressLib/LzmaCustomDecompressLib.inf
!if $(HP_I2C_MOUSE_SUPPORT) == TRUE
  HidI2cPlatformSupportLib|$(HP_PLATFORM_PACKAGE)/Library/DxeHidI2cPlatformSupportLib/DxeHidI2cPlatformSupportLib.inf
!endif

  PciHostBridgeLib|$(PLATFORM_PACKAGE)/Pci/Library/PciHostBridgeLibSimple/PciHostBridgeLibSimple.inf

[LibraryClasses.X64.DXE_SMM_DRIVER]
  SmmNvmeLib|MdeModulePkg/Library/SmmNvmeLib/SmmNvmeLib.inf
!if $(HP_VPM_SUPPORT) == TRUE
  HpSioVoltagePwrMonitorLib|$(HP_PLATFORM_PACKAGE)/Library/HpSioVoltagePwrMonitorLib/HpSioVoltagePwrMonitorLib.inf
!endif
!if $(HP_EPSC) == Sio
  SmmKBPowerOnLib|$(HP_PLATFORM_PACKAGE)/Library/SmmKBPowerOnLib/SmmKBPowerOnLib.inf
  HpVpinSelectionLib|$(HP_PLATFORM_PACKAGE)/Library/HpVpinSelectionLib/HpVpinSelectionLib.inf
!endif

[LibraryClasses.Common.SEC]
  DebugLib|MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf

[LibraryClasses.$(PEI_ARCHITECTURE).PEIM]
  #
  # PEI phase common
  #
!if $(CRB_BOOT_SUPPORT) == FALSE
  PlatformNuvotonInitPeiLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformNuvotonInitPeiLib/PlatformNuvotonInitPeiLib.inf
  HpNuvotonMiscCommonLib|$(HP_EPSC_COMMON_PACKAGE)/Library/HpNuvotonMiscCommonLib/HpNuvotonMisc$(HP_EPSC)CommonLibPei.inf
!endif
!if $(HP_EPSC) == Sio
!if $(HP_VPM_SUPPORT) == TRUE
  HpSioVoltagePwrMonitorLib|$(HP_PLATFORM_PACKAGE)/Library/HpSioVoltagePwrMonitorLib/HpSioVoltagePwrMonitorLib.inf
!endif
  HpVpinSelectionLib|$(HP_PLATFORM_PACKAGE)/Library/HpVpinSelectionLib/HpVpinSelectionLib.inf
  PlatformSioInitPeiLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformSioInitPeiLib/PlatformSioInitPeiLib.inf
!endif
  FirmwareBootMediaLib|IntelSiliconPkg/Library/PeiDxeSmmBootMediaLib/PeiFirmwareBootMediaLib.inf
  FirmwareBootMediaInfoLib|BoardModulePkg/Library/PeiFirmwareBootMediaInfoLib/PeiFirmwareBootMediaInfoLib.inf
!ifdef $(SOURCE_DEBUG_USE_USB3)
  DebugCommunicationLib|SourceLevelDebugPkg/Library/DebugCommunicationLibUsb3/DebugCommunicationLibUsb3Pei.inf
!endif

!if $(TARGET) == DEBUG
  SerialIoUartDebugPropertyLib|$(PLATFORM_FULL_PACKAGE)/Library/SerialIoUartDebugPropertyLib/PeiSerialIoUartDebugPropertyLib.inf
  DebugLib|MdeModulePkg/Library/PeiDebugLibDebugPpi/PeiDebugLibDebugPpi.inf
  DebugPrintErrorLevelLib|$(PLATFORM_FULL_PACKAGE)/Library/PeiDxeSmmDebugPrintErrorLevelLib/PeiDebugPrintErrorLevelLib.inf
  !if gPlatformModuleTokenSpaceGuid.PcdSerialPortEnable == TRUE
    SerialPortLib|$(PLATFORM_FULL_PACKAGE)/Library/BaseSerialPortLib/BaseSerialPortLib.inf
  !else
    #
    # HP Customized SerialPortLib due to RTSCallbackHandlePei->DebugPostCode() output POST thru SerialPortWrite () directly, only works for Serial COM port but Serial UART port.
    # And regular BaseDebugLibSerialPort will route debug message to legacy COM port 3F8/2F8 (which is only available for DT and CRB).
    # In order to route debug message to serial IO UART port (via MMIO), use HP implemented PchSerialIoUartPortLib for route debug message to serial IO UART (via MMIO)
    # 'for NB platform'
    #
    SerialPortLib|$(HP_PLATFORM_PACKAGE)/Library/PchSerialIoUartPortLib/PchSerialIoUartPortLib.inf
  !endif
!endif


[LibraryClasses.X64.DXE_CORE]
  SerialPortParameterLib|$(PLATFORM_FULL_PACKAGE)/Library/DxeCoreSerialPortParameterLib/DxeCoreSerialPortParameterLib.inf
  TraceHubHookLib|$(PLATFORM_SI_PACKAGE)/IpBlock/TraceHub/Library/TraceHubHookLib/DxeCoreTraceHubHookLib.inf

!if $(TARGET) == DEBUG
  SerialIoUartDebugPropertyLib|$(PLATFORM_FULL_PACKAGE)/Library/SerialIoUartDebugPropertyLib/DxeCoreSerialIoUartDebugPropertyLib.inf
  DebugLib|$(PLATFORM_FULL_PACKAGE)/Library/BaseDebugLibAllDebugPort/BaseDebugLibAllDebugPort.inf
  !if gPlatformModuleTokenSpaceGuid.PcdSerialPortEnable == TRUE
    SerialPortLib|$(PLATFORM_FULL_PACKAGE)/Library/BaseSerialPortLib/BaseSerialPortLib.inf
  !else
    #
    # HP Customized SerialPortLib due to RTSCallbackHandlePei->DebugPostCode() output POST thru SerialPortWrite () directly, only works for Serial COM port but Serial UART port.
    # And regular BaseDebugLibSerialPort will route debug message to legacy COM port 3F8/2F8 (which is only available for DT and CRB).
    # In order to route debug message to serial IO UART port (via MMIO), use HP implemented PchSerialIoUartPortLib for route debug message to serial IO UART (via MMIO)
    # 'for NB platform'
    #
    SerialPortLib|$(HP_PLATFORM_PACKAGE)/Library/PchSerialIoUartPortLib/PchSerialIoUartPortLib.inf
  !endif
!endif

[LibraryClasses.X64.DXE_DRIVER]
!if $(CRB_BOOT_SUPPORT) == FALSE
  HpPlatformSpecificHookLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformSpecificHookLibDxe/HpPlatformSpecificHookLibDxe.inf
  HpNuvotonMiscCommonLib|$(HP_EPSC_COMMON_PACKAGE)/Library/HpNuvotonMiscCommonLib/HpNuvotonMisc$(HP_EPSC)CommonLibDxe.inf
!if $(HP_EPSC) == Ec
  HpKbdLib|$(HP_EPSC_PACKAGE)/Library/HpKbdLib/HpKbdLib.inf
!endif
!endif
  HpPlatformGraphicsDxeLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformGraphicsConfiguration/PlatformGraphicsConfiguration.inf
!if $(HP_TOUCH_FW_CAPSULE_SUPPORT) == TRUE
  # For I2c touch panel FW update. Vendor's FMP vendor needs to know if the I2C communication is ready.
  HpI2CTouchIntStatusReadLib|$(HP_CHIPSET_PACKAGE)/Library/HpI2cTouchIntStatusReadLib/HpI2CTouchIntStatusReadLib.inf
!endif

[LibraryClasses.X64.DXE_SMM_DRIVER]
!if $(CRB_BOOT_SUPPORT) == FALSE
  HpNuvotonMiscCommonLib|$(HP_EPSC_COMMON_PACKAGE)/Library/HpNuvotonMiscCommonLib/HpNuvotonMisc$(HP_EPSC)CommonLibSmm.inf
!endif

[LibraryClasses.X64.DXE_DRIVER, LibraryClasses.X64.DXE_SMM_DRIVER]
!if $(TARGET) == DEBUG
  SerialIoUartDebugPropertyLib|$(PLATFORM_FULL_PACKAGE)/Library/SerialIoUartDebugPropertyLib/DxeSmmSerialIoUartDebugPropertyLib.inf
  !if gPlatformModuleTokenSpaceGuid.PcdSerialPortEnable == TRUE
    SerialPortLib|$(PLATFORM_FULL_PACKAGE)/Library/BaseSerialPortLib/BaseSerialPortLib.inf
  !else
    #
    # HP Customized SerialPortLib due to RTSCallbackHandlePei->DebugPostCode() output POST thru SerialPortWrite () directly, only works for Serial COM port but Serial UART port.
    # And regular BaseDebugLibSerialPort will route debug message to legacy COM port 3F8/2F8 (which is only available for DT and CRB).
    # In order to route debug message to serial IO UART port (via MMIO), use HP implemented PchSerialIoUartPortLib for route debug message to serial IO UART (via MMIO)
    # 'for NB platform'
    #
    SerialPortLib|$(HP_PLATFORM_PACKAGE)/Library/PchSerialIoUartPortLib/PchSerialIoUartPortLib.inf
  !endif
!endif

  HpPlatformServicesLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformServicesLib/HpPlatformServicesLib.inf

[LibraryClasses.X64.DXE_RUNTIME_DRIVER, LibraryClasses.X64.UEFI_APPLICATION, LibraryClasses.X64.UEFI_DRIVER]
!if $(TARGET) == DEBUG
  SerialIoUartDebugPropertyLib|$(PLATFORM_FULL_PACKAGE)/Library/SerialIoUartDebugPropertyLib/DxeSmmSerialIoUartDebugPropertyLib.inf
  !if gPlatformModuleTokenSpaceGuid.PcdSerialPortEnable == TRUE
    SerialPortLib|$(PLATFORM_FULL_PACKAGE)/Library/BaseSerialPortLib/BaseSerialPortLib.inf
  !else
    #
    # HP Customized SerialPortLib due to RTSCallbackHandlePei->DebugPostCode() output POST thru SerialPortWrite () directly, only works for Serial COM port but Serial UART port.
    # And regular BaseDebugLibSerialPort will route debug message to legacy COM port 3F8/2F8 (which is only available for DT and CRB).
    # In order to route debug message to serial IO UART port (via MMIO), use HP implemented PchSerialIoUartPortLib for route debug message to serial IO UART (via MMIO)
    # 'for NB platform'
    #
    SerialPortLib|$(HP_PLATFORM_PACKAGE)/Library/PchSerialIoUartPortLib/PchSerialIoUartPortLib.inf
  !endif
!endif

[LibraryClasses.X64.SMM_CORE]
!if $(TARGET) == DEBUG
  SerialIoUartDebugPropertyLib|$(PLATFORM_FULL_PACKAGE)/Library/SerialIoUartDebugPropertyLib/DxeSmmSerialIoUartDebugPropertyLib.inf
  DebugLib|$(PLATFORM_FULL_PACKAGE)/Library/BaseDebugLibAllDebugPort/BaseDebugLibAllDebugPort.inf
  !if gPlatformModuleTokenSpaceGuid.PcdSerialPortEnable == TRUE
    SerialPortLib|$(PLATFORM_FULL_PACKAGE)/Library/BaseSerialPortLib/BaseSerialPortLib.inf
  !else
    #
    # HP Customized SerialPortLib due to RTSCallbackHandlePei->DebugPostCode() output POST thru SerialPortWrite () directly, only works for Serial COM port but Serial UART port.
    # And regular BaseDebugLibSerialPort will route debug message to legacy COM port 3F8/2F8 (which is only available for DT and CRB).
    # In order to route debug message to serial IO UART port (via MMIO), use HP implemented PchSerialIoUartPortLib for route debug message to serial IO UART (via MMIO)
    # 'for NB platform'
    #
    SerialPortLib|$(HP_PLATFORM_PACKAGE)/Library/PchSerialIoUartPortLib/PchSerialIoUartPortLib.inf
  !endif
!endif


  ##
  ## Include LastLibOverride.dsc to overwrite Library in last build phase with PlatformPkg.dsc.
  ## [IMPORT] Don't change this file location in PlatformPkg.dsc.
  ##
  !include LastLibOverride.dsc


################################################################################
#
# Components section - list of all Components needed by this Platform.
#
################################################################################

[Components.$(PEI_ARCHITECTURE)]
  $(HP_PLATFORM_PACKAGE)/BiosUpdatePlatformPolicy/BiosUpdatePlatformPolicyPei.inf
  $(HP_PLATFORM_PACKAGE)/HpPlatformServices/Pei/HpPlatformPeiServices.inf
  $(HP_PLATFORM_PROJECT_PATH)/PlatformPortingPei/PlatformPortingPei.inf
  $(HP_PLATFORM_PACKAGE)/HpSecureStorageDevicePei/HpSecureStorageDevicePei.inf
  $(HP_PLATFORM_PACKAGE)/PlatformMud/Pei/PlatformMudPei.inf
!if $(HP_EPSC) == Ec
  $(HP_EPSC_PACKAGE)/ThermalInitPei/ThermalInitPei.inf
!endif
!if $(CRB_BOOT_SUPPORT) == FALSE
!if $(SURESTART_SUPPORT) == FALSE
  MdeModulePkg/Bus/Pci/XhciPei/XhciPei.inf
  MdeModulePkg/Bus/Usb/UsbBotPei/UsbBotPei.inf
  MdeModulePkg/Bus/Usb/UsbBusPei/UsbBusPei.inf
  MdeModulePkg/Bus/Ata/AhciPei/AhciPei.inf
  MdeModulePkg/Bus/Pci/NvmExpressPei/NvmExpressPei.inf
  FatPkg/FatPei/FatPei.inf
!endif
!endif
!if gSiPkgTokenSpaceGuid.PcdBootGuardEnable == TRUE
  !include $(HP_CHIPSET_PACKAGE)/Override/Edk2/SecurityPkg/SecurityPkgInf.dsc  # For Boot Guard ACM involve PCR 0 measurement.
!else
  !include SecurityPkg/SecurityPkgInf.dsc
!endif
  #
  # EC24 & FireBird F/W's Bootloader structure
  #
!if $(HP_EPSC) == Ec OR $(HP_EPSC) == Sio
  $(HP_EPSC_PACKAGE)/Hp$(HP_EPSC)FireBirdBootloader/Hp$(HP_EPSC)FireBirdBootloader.inf
!endif

  CryptoPkg/Driver/CryptoPei.inf {
    <LibraryClasses>
      BaseCryptLib|CryptoPkg/Library/BaseCryptLib/PeiCryptLib.inf
      TlsLib|CryptoPkg/Library/TlsLibNull/TlsLibNull.inf
    <PcdsFixedAtBuild>
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Rsa.Services.Pkcs1Verify   | TRUE
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Rsa.Services.New           | TRUE
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Rsa.Services.SetKey        | TRUE
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Rsa.Services.Free          | TRUE
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha1.Family                | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha256.Family              | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha384.Family              | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha512.Family              | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
   }

[Components.X64]
#
# Overwrite Lib SimpleFontsLib.inf for Basic System Diagnostics Japanese/Chinese(simple and Traditional)/Russian
#
  MdeModulePkg\Universal\HiiDatabaseDxe\HiiDatabaseDxe.inf {
    <LibraryClasses>
      NULL|$(HP_HII_PUB_SRC_PKG)/Library/SimpleFontsLib/SimpleFontsLib.inf
  }
  CryptoPkg/Driver/CryptoSmm.inf {
    <LibraryClasses>
      BaseCryptLib|CryptoPkg/Library/BaseCryptLib/SmmCryptLib.inf
      TlsLib|CryptoPkg/Library/TlsLibNull/TlsLibNull.inf
    <PcdsFixedAtBuild>
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.HmacSha256.Family | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Pkcs.Family       | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Dh.Family         | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Random.Family     | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Rsa.Family        | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha1.Family       | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha256.Family     | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha384.Family     | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha512.Family     | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.X509.Family       | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Tdes.Family       | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Hkdf.Family       | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Aes.Family        | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
   }
  CryptoPkg/Driver/CryptoDxe.inf {
    <LibraryClasses>
      BaseCryptLib|CryptoPkg/Library/BaseCryptLib/BaseCryptLib.inf
      TlsLib|CryptoPkg/Library/TlsLib/TlsLib.inf
      OpensslLib|CryptoPkg/Library/OpensslLib/OpensslLibFull.inf # It is for MSFT_CSR_SUPPORT
    <PcdsFixedAtBuild>
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.HmacSha256.Family | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Pkcs.Family       | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Dh.Family         | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Random.Family     | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Rsa.Family        | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha1.Family       | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha256.Family     | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha384.Family     | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Sha512.Family     | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.X509.Family       | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Tdes.Family       | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Hkdf.Family       | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Tls.Family        | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.TlsSet.Family     | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.TlsGet.Family     | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Ec.Family         | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
      gEfiCryptoPkgTokenSpaceGuid.PcdCryptoServiceFamilyEnable.Bn.Family         | PCD_CRYPTO_SERVICE_ENABLE_FAMILY
   }
!if $(TARGET) == DEBUG
  $(HP_CORE)/HpUserInterface/PubSrcPkg/HpJpeg/HpJpeg.inf {
    <LibraryClasses>
      DebugLib|MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf
  }
#  $(HP_CORE)/HpNetworkPkg/Applications/HpEdk2NetworkTransferWorker/HpEdk2NetworkTransferWorker.inf {
#    <LibraryClasses>
#      ShellLib|$(HP_CORE)/HpNetworkPkg/Library/UefiShellLibNull/UefiShellLibNull.inf
#!if ("MSFT" in $(FAMILY))
#      BsdSocketLib|$(STD_LIB_PUB_SRC_PKG)/BsdSocketLib/BsdSocketLib.inf
#!endif
#      DebugLib|MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf
#  }
!endif
  $(HP_PLATFORM_PROJECT_PATH)/PlatformPortingDxe/PlatformPortingDxe.inf
  $(HP_PLATFORM_PACKAGE)/HpPlatformFeaturesDxe/HpPlatformFeaturesDxe.inf
  $(HP_PLATFORM_PACKAGE)/HpPlatformServices/Dxe/HpPlatformDxeServices.inf
  $(HP_PLATFORM_PACKAGE)/HpPlatformServices/Smm/HpPlatformSmmServices.inf
  $(HP_PLATFORM_PACKAGE)/HpSecureStorageDeviceDxe/HpSecureStorageDeviceDxe.inf
  $(HP_PLATFORM_PACKAGE)/PciPlatform/Dxe/PciPlatform.inf
  $(HP_PLATFORM_PACKAGE)/PlatformMud/Dxe/PlatformMudDxe.inf
  $(HP_PLATFORM_PACKAGE)/PlatformMud/Smm/PlatformMudSmm.inf
!if $(HP_EPSC) == Ec
  $(HP_PLATFORM_PACKAGE)/Hotkey/Hotkey.inf
  $(HP_PLATFORM_PACKAGE)/PlatformPrivateWmi/PlatformPrivateWmi.inf
!endif
!if $(HP_EPSC) == Sio
  $(HP_PLATFORM_PACKAGE)/PlatformPrivateWmi/PlatformPrivateWmi_DM800.inf
!endif
  $(HP_PLATFORM_PACKAGE)/BiosUpdatePlatformPolicy/BiosUpdatePlatformPolicySmm.inf
!if gSiPkgTokenSpaceGuid.PcdAcpiEnable == TRUE
  $(HP_PLATFORM_PACKAGE)/HpAcpiPlatformDxe/HpAcpiPlatformDxe.inf {
    <LibraryClasses>
       PcdLib|MdePkg/Library/DxePcdLib/DxePcdLib.inf
  }
!if $(HP_ACPI_TABLES_ENABLE) == TRUE
!if $(DESKTOP_PLATFORM) == TRUE
  $(HP_PLATFORM_PROJECT_PATH)/AcpiTables/AcpiTables.inf
!else
  $(HP_PLATFORM_PACKAGE)/AcpiTables/AcpiTables.inf
!endif
!endif
!endif
  $(HP_PLATFORM_PROJECT_PATH)/PlatformPortingSmm/PlatformPortingSmm.inf
!if $(ENHANCED_SMART_COVER_SUPPORT) == TRUE
!if $(DESKTOP_PLATFORM) == FALSE
  $(HP_PLATFORM_PACKAGE)/SmartCover/NB/SmartCoverPortingDxe.inf
  $(HP_PLATFORM_PACKAGE)/SmartCover/NB/SmartCoverPortingSmm.inf
!else
  $(HP_PLATFORM_PACKAGE)/SmartCover/DT/SmartCoverPortingDxe.inf
  $(HP_PLATFORM_PACKAGE)/SmartCover/DT/SmartCoverPortingSmm.inf
  $(HP_PLATFORM_PACKAGE)/SmartCover/DT/SmartCoverSmbiosDxe.inf
!endif
!endif

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

  MdeModulePkg/Universal/RegularExpressionDxe/RegularExpressionDxe.inf {
    <LibraryClasses>
      DebugLib|MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf
  }
   MdeModulePkg/Universal/Disk/RamDiskDxe/RamDiskDxe.inf
!if gTseFeaturePkgTokenSpaceGuid.PcdTseFeatureEnable == TRUE
  TseFeaturePkg/TseNvmExpressDxe/NvmExpressSmm.inf
!else
  MdeModulePkg/Bus/Pci/NvmExpressDxe/NvmExpressSmm.inf
!endif

!if $(HP_EPSC) == Ec
  $(HP_EPSC_PACKAGE)/ThermalInitDxe/ThermalInitDxe.inf
!endif

!if $(HP_EPSC) == Ec OR $(HP_EPSC) == Sio
!if $(HP_WAKE_ON_LAN_SUPPORT) == TRUE
  $(HP_EPSC_PACKAGE)/HpCommonPorting/WOLPlatformPortingDxe/WOLPlatformPortingDxe.inf
  $(HP_EPSC_PACKAGE)/HpCommonPorting/WOLPlatformPortingSmm/WOLPlatformPortingSmm.inf
!endif
!endif

!if $(HP_EPSC) == Sio
  $(HP_DESKTOP_PACKAGE)/SetupMenu/SetupMenuSmm.inf {
      <LibraryClasses>
  NULL|$(HP_EPSC_PACKAGE)/S5MaxPowerSavingsSmm/S5MaxPowerSavingsSmmLib.inf
  }
!endif

  !include $(HP_PROJECT_PATH)/Config/CapsuleDriversBuild.dsc

  ##
  ## Include LastPcdOverride.dsc to overwrite PCD token setting in last build phase with PlatformPkg.dsc.
  ## [IMPORT] Don't change this file location in PlatformPkg.dsc.
  ##
  !include LastPcdOverride.dsc

  #
  # Build Options
  #
  !include BuildOptions.dsc

  # Erase functionality is not working with and without connecting to the internet. - Permanent fix
  # When the fast boot is enabled, the BIOS couldn't detect the NVME drive it wants to erase when the flip request comes in.
  # PcdConnectNvmeOnFastBoot is default to false and it needs to be override during the build time
  [PcdsFixedAtBuild.X64]
   gEfiHpBootOrderPubIntPkgTokenSpaceGuid.PcdConnectNvmeOnFastBoot|TRUE

[PcdsFixedAtBuild.common]
   # PCDs for Touch panel
   ##  1: USB
   ##  2: I2C
   !if $(HP_TOUCH_PANEL_INTERFACE) == USB
      gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdTouchPanelInterfaceType|1
      # driver guid for UsbTouchPanelDxe.inf
      gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdTouchPanelDriverFile|{ 0x64, 0x04, 0x3d, 0x97, 0xb5, 0xf1, 0x01, 0x4b, 0xb2, 0xd9, 0x15, 0x0D, 0x85, 0x75, 0x09, 0x62 }
   !elseif $(HP_TOUCH_PANEL_INTERFACE) == I2C
      gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdTouchPanelInterfaceType|2
      # driver guid for TouchPanelDriver.inf(I2C)
      gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdTouchPanelDriverFile|{ 0x0F, 0xF2, 0x5C, 0x5E, 0x3F, 0xB6, 0xe1, 0x11, 0x83, 0x5e, 0x38, 0x60, 0x77, 0xf1, 0x1e, 0x9d }
  !endif
[PcdsFixedAtBuild.X64]
  gEfiMdePkgTokenSpaceGuid.PcdUefiVariableDefaultPlatformLangCodes|"en-US;da-DA;nl-BE;fi-FI;fr-FR;de-DE;it-IT;ja-JA;no-NO;pt-PT;zh-CN;es-ES;sv-SV;zh-TW;ru-RU"