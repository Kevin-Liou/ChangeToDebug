#
# (c) Copyright 2012 - 2026 HP Development Company, L.P.
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
#[HP_ADD]+ Sync from BoardPkg.dsc
  #
  # Set platform specific package/folder name, same as passed from PREBUILD script.
  # PLATFORM_PACKAGE would be the same as PLATFORM_NAME as well as package build folder
  # DEFINE only takes effect at R9 DSC and FDF.
  #
  DEFINE PLATFORM_PACKAGE                = MinPlatformPkg
  DEFINE PLATFORM_FULL_PACKAGE           = NovaLakePlatSamplePkg
  DEFINE PLATFORM_SI_PACKAGE             = OneSiliconPkg
  DEFINE SILICON_PRODUCT_PATH            = OneSiliconPkg/Product/NovaLake
  DEFINE PLATFORM_FSP_BIN_PACKAGE        = NovaLakeFspBinPkg
  DEFINE PLATFORM_BOARD_PACKAGE          = NovaLakeBoardPkg
  DEFINE PLATFORM_OPEN_BOARD_PACKAGE     = NovaLakeOpenBoardPkg
  DEFINE PLATFORM_FEATURES_PATH          = $(PLATFORM_FULL_PACKAGE)/Features
  DEFINE PLATFORM_BIN_PACKAGE            = NovaLakeBinPkg
  DEFINE COMMON_BIN_PACKAGE              = CommonBinPkg
  DEFINE PLATFORM_BSP_PATH               = $(PLATFORM_BOARD_PACKAGE)/BoardSupport

!if gSiPkgTokenSpaceGuid.PcdNvlsSupport == TRUE
  DEFINE BOARD_NVL_BOARDS               = NovaLakeSBoards
!else
  DEFINE BOARD_NVL_BOARDS               = NovaLakePBoards
!endif
  DEFINE PROJECT_NVL_BOARDS             = NovaLakeBoardPkg/$(BOARD_NVL_BOARDS)
  DEFINE PROJECT_NVL_BOARDS_BSP         = $(PLATFORM_BSP_PATH)/$(BOARD_NVL_BOARDS)

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
  DEFINE NETWORK_HTTP_ENABLE            = FALSE

  DEFINE NETWORK_TLS_ENABLE             = FALSE
  DEFINE NETWORK_HTTP_BOOT_ENABLE       = FALSE
  DEFINE PLATFORMX64_ENABLE             = TRUE

  #*********************************************************************
  #* Board VPD related MACRO define Start                              *
  #*********************************************************************
  #
  # BoardType
  #
  DEFINE BOARD_TYPE_RVP       = 0x00   # Reference Validation Platform
  DEFINE BOARD_TYPE_RVPSTHI   = 0x01   # Boards with Special Test Hooks
  DEFINE BOARD_TYPE_RVPPPV    = 0x02   # Boards used for Processor Platform Validation
  DEFINE BOARD_TYPE_FFRD      = 0x03   # Form factor reference design Boards
  DEFINE BOARD_TYPE_RVPERB    = 0x04   # ERB Boards
  DEFINE BOARD_TYPE_RVPCPV    = 0x05   # Boards used for Chipset Platform Validation
  DEFINE BOARD_TYPE_SV        = 0x06   # Boards used for Silicon Validation
  DEFINE BOARD_TYPE_UPSERVER  = 0x07   # Server Boards
  DEFINE BOARD_TYPE_FFVS      = 0x08   # Form factor Validation system
  DEFINE BOARD_TYPE_TDV       = 0x09   # Technology Development Vehicle
  DEFINE BOARD_TYPE_MAX       = 0x0A  
  #
  # PlatformType
  #
  DEFINE TYPE_UNKNOWN = 0x0
  DEFINE TYPE_TRAD    = 0x1
  DEFINE TYPE_ULT_ULX = 0x2
  #
  # FlavorType
  #
  DEFINE FLAVOR_UNKNOWN            = 0x0
  DEFINE FLAVOR_MOBILE             = 0x1
  DEFINE FLAVOR_DESKTOP            = 0x2
  DEFINE FLAVOR_WORKSTATION        = 0x3
  DEFINE FLAVOR_UP_SERVER          = 0x4
  DEFINE FLAVOR_MOBILE_WORKSTATION = 0x5
  DEFINE FLAVOR_PLATFOR_MMAX       = 0x6  
  #
  # GPIO
  #
  DEFINE PIN_GPIO_ACTIVE_HIGH            = 1
  DEFINE PIN_GPIO_ACTIVE_LOW             = 0  
  #
  # Battery
  #
  DEFINE BOARD_REAL_BATTERY_SUPPORTED    = 1
  DEFINE BOARD_VIRTUAL_BATTERY_SUPPORTED = 2
  DEFINE BOARD_NO_BATTERY_SUPPORT        = 0  
#[HP_ADD]-

  #
  # For HP Project
  #
  DEFINE ME_SKU                          = FULL
  DEFINE HP_PLATFORM_PACKAGE             = HpPlatformPkg
  DEFINE HP_PLATFORM_PACKAGE_DEC         = $(HP_PLATFORM_PACKAGE)/$(HP_PLATFORM_PACKAGE).dec
  DEFINE HP_PLATFORM_TYPE                = $(HP_PLATFORM_TYPE)
  DEFINE HP_PROJECT_PACKAGE              = $(HP_PLATFORM_PACKAGE)/MultiProject/$(HP_PROJECT_NAME)Pkg
  DEFINE HP_CHIPSET_PACKAGE              = HpIntelChipsetPkg
  DEFINE HP_MEDIA_READER_PATH            = $(PORT_OPTIONS_PUB_SRC_PKG)/FlashMediaReader/Realtek
  DEFINE HP_TBT_PACKAGE                  = HpThunderboltPkg
  DEFINE HP_DMAR_PACKAGE                 = HpDmarPkg
  DEFINE HP_MODERN_STANDBY_PACKAGE       = HpModernStandbyPkg
  DEFINE HP_EPSC_COMMON_PACKAGE          = HpEpscCommon
  DEFINE HP_CORE                         = HpCore
  DEFINE HP_CORE_PVT                     = $(HP_CORE)/HpCorePvt
  DEFINE HP_CORE_PVT_BINS                = $(HP_CORE)/HpCorePvtBins
  DEFINE HP_FEATURE                      = HpFeature
  DEFINE HP_FEATURE_PVT                  = HpFeaturePvt
  DEFINE HP_FEATURE_PVT_BINS             = HpFeaturePvtBins
  DEFINE HP_CPU_FAMILY                   = $(HP_CPU_FAMILY)

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
  !include $(HP_PLATFORM_PACKAGE)/Include/$(HP_PLATFORM_TYPE)/HpEpscDef.dsc.inc
  
#[HP_ADD]+ Sync with BoardPkg.dsc
  #
  # Silicon On/Off feature are defined here
  #
  !include $(SILICON_PRODUCT_PATH)/SiPkgPcdInit.dsc

  #
  # Platform On/Off features are defined here
  #
  !include $(COMMON_BIN_PACKAGE)/Include/Dsc/CommonBinPkgPcdInit.dsc
  !include $(PLATFORM_BIN_PACKAGE)/Include/Dsc/NovaLakeBinPkgPcdInit.dsc
  !include $(PLATFORM_BOARD_PACKAGE)/BoardPkgPcdInit.dsc
  !include $(PLATFORM_BOARD_PACKAGE)/BoardPkgPcdUpdate.dsc
  !include $(PROJECT_NVL_BOARDS)/HiiPcdsInit/HiiStructurePcd.dsc
  !include $(PROJECT_NVL_BOARDS)/BoardVpdPcdsInit/BoardVpdPcdInit.dsc
#[HP_ADD]-

  #
  # HP Post Code
  #
  !include $(HP_FEATURE)/PostCodeForEDKII_00.dsc
  !include $(HP_CORE)/PostCodeForHpCore_01.dsc
  !include $(HP_EPSC_COMMON_PACKAGE)/PostCodeForNuvoton_02.dsc
  !include $(HP_PLATFORM_PACKAGE)/Include/$(HP_PLATFORM_TYPE)/HpEpscPostCode.dsc.inc
  !include $(HP_FEATURE)/HpPe/HpDtPkg/PostCodeForDt_04.dsc
  !include $(HP_CHIPSET_PACKAGE)/PostCodeForIntelChipset_06.dsc
  !include $(HP_CHIPSET_PACKAGE)/PostCodeForEdk2Platforms_07.dsc
  !include $(HP_CHIPSET_PACKAGE)/PostCodeForIntelReferenceCode_08.dsc
  !include $(HP_CHIPSET_PACKAGE)/Tools/BoardPkgFdfAutoGen/AutoGenOutput/PostCodeForIntelRcAutoGen.dsc
  !include $(HP_CORE)/PostCodeForMiscCore_09.dsc
  !include $(HP_TBT_PACKAGE)/PostCodeForHpThunderBolt_0B.dsc
  !include $(HP_CON_DEV_PACKAGE_PUB_SRC_PKG)/PostCodeForConDev_0C.dsc
  !include $(HP_FEATURE)/PostCodeForHpFeature_0E.dsc
  !include PostCodeForPlatform_0F.dsc

  #
  # HpFeature Configuration
  #
  !include HpPlatformPkg/MultiProject/HpFeaturePlatformPreConfig.dsc
  !include $(HP_FEATURE)/HpFeatureConfig.dsc
  !include $(HP_CHIPSET_PACKAGE)/HpFeature/HpFeatureChipsetConfig.dsc

  #
  # Import PCD feature switch default value
  #
  !include $(HP_TBT_PACKAGE)/HpTbtPcdDefault.dsc
  !include $(HP_CHIPSET_PACKAGE)/HpIntelChipsetPkgPcdDefault.dsc
  !include $(HP_PLATFORM_PACKAGE)/Include/$(HP_PLATFORM_TYPE)/HpEpscPcdDefault.dsc.inc

  !include $(HP_CHIPSET_PACKAGE)/HpIntelChipsetPkgOverrideIntelPcd.dsc

  #
  # Platform On/Off features are defined here
  #
  !include $(HP_PROJECT_PACKAGE)/$(HP_PROJECT_NAME)PkgConfig.dsc
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

  !if gPlatformModuleTokenSpaceGuid.PcdNetworkEnable == TRUE
    !include NetworkPkg/HpNetwork.dsc.inc
  !endif


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
  !include $(HP_PLATFORM_PACKAGE)/Include/$(HP_PLATFORM_TYPE)/HpEpsc.dsc.inc
  !include $(HP_PLATFORM_PACKAGE)/Include/$(HP_PLATFORM_TYPE)/HpEpscLib.dsc.inc
  !include $(HP_PROJECT_PACKAGE)/$(HP_PROJECT_NAME)Pkg.dsc

################################################################################
#
# Library Class section - list of all Library Classes needed by this Platform.
#
################################################################################
[LibraryClasses.X64.PEI_CORE]

[LibraryClasses.common]
  # HP: The platform decides which SIO will implement the serial port PlatformHookLib library
  PlatformRequestLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformRequestLib/PlatformRequestLib.inf

  PeiMemoryTelemetryLib|MemoryTelemetryFeaturePkg/Library/PeiMemoryTelemetryLib/PeiMemoryTelemetryLib.inf

  PcdExportLib|$(HP_PLATFORM_PACKAGE)/Library/BasePcdExportLib/BasePcdExportLib.inf
!if $(TARGET) == DEBUG
  DebugLib|$(PLATFORM_FULL_PACKAGE)/Library/BaseDebugLibAllDebugPort/BaseDebugLibAllDebugPort.inf
!endif
  LzmaDecompressLib|MdeModulePkg/Library/LzmaCustomDecompressLib/LzmaCustomDecompressLib.inf
!if $(HP_I2C_MOUSE_SUPPORT) == TRUE
  HidI2cPlatformSupportLib|$(HP_PLATFORM_PACKAGE)/Library/DxeHidI2cPlatformSupportLib/DxeHidI2cPlatformSupportLib.inf
!endif

[LibraryClasses.X64.DXE_SMM_DRIVER]
  SmmNvmeLib|MdeModulePkg/Library/SmmNvmeLib/SmmNvmeLib.inf


[LibraryClasses.Common.SEC]


[LibraryClasses.$(PEI_ARCHITECTURE).PEIM]
  #
  # PEI phase common
  FirmwareBootMediaLib|IntelSiliconPkg/Library/PeiDxeSmmBootMediaLib/PeiFirmwareBootMediaLib.inf
  FirmwareBootMediaInfoLib|BoardModulePkg/Library/PeiFirmwareBootMediaInfoLib/PeiFirmwareBootMediaInfoLib.inf
!ifdef $(SOURCE_DEBUG_USE_USB3)
  DebugCommunicationLib|SourceLevelDebugPkg/Library/DebugCommunicationLibUsb3/DebugCommunicationLibUsb3Pei.inf
!endif

[LibraryClasses.X64.DXE_CORE]

[LibraryClasses.X64.DXE_DRIVER]
  HpPlatformGraphicsDxeLib|$(HP_PLATFORM_PACKAGE)/Library/PlatformGraphicsConfiguration/PlatformGraphicsConfiguration.inf
!if $(HP_TOUCH_FW_CAPSULE_SUPPORT) == TRUE
  # For I2c touch panel FW update. Vendor's FMP vendor needs to know if the I2C communication is ready.
  HpI2CTouchIntStatusReadLib|$(HP_CHIPSET_PACKAGE)/Library/HpI2cTouchIntStatusReadLib/HpI2CTouchIntStatusReadLib.inf
!endif

[LibraryClasses.X64.DXE_SMM_DRIVER]

[LibraryClasses.X64.DXE_DRIVER, LibraryClasses.X64.DXE_SMM_DRIVER]
  HpPlatformServicesLib|$(HP_PLATFORM_PACKAGE)/Library/HpPlatformServicesLib/HpPlatformServicesLib.inf
  
[LibraryClasses.X64.DXE_RUNTIME_DRIVER, LibraryClasses.X64.UEFI_APPLICATION, LibraryClasses.X64.UEFI_DRIVER]

[LibraryClasses.X64.SMM_CORE]


################################################################################
#
# Components section - list of all Components needed by this Platform.
#
################################################################################

[Components.$(PEI_ARCHITECTURE)]
  $(HP_PLATFORM_PACKAGE)/BiosUpdatePlatformPolicy/BiosUpdatePlatformPolicyPei.inf
  $(HP_PLATFORM_PACKAGE)/HpPlatformServices/Pei/HpPlatformPeiServices.inf
  $(HP_PLATFORM_PACKAGE)/PlatformMud/Pei/PlatformMudPei.inf
  $(HP_PLATFORM_PACKAGE)/HpSecureStorageDevicePei/HpSecureStorageDevicePei.inf
!if $(HP_PLATFORM_TYPE) == Nb
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

  CryptoPkg/Driver/CryptoPeiMbedTls.inf {
    <LibraryClasses>
      MbedTlsLib|CryptoPkg/Library/MbedTlsLib/MbedTlsLib.inf
      BaseCryptLib|CryptoPkg/Library/BaseCryptLibMbedTls/PeiCryptLib.inf
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
    MdeModulePkg/Universal/HiiDatabaseDxe/HiiDatabaseDxe.inf {
    <LibraryClasses>
      NULL|$(HP_HII_PUB_SRC_PKG)/Library/SimpleFontsLib/SimpleFontsLib.inf
  }
  CryptoPkg/Driver/CryptoSmm.inf {
    <LibraryClasses>
      BaseCryptLib|CryptoPkg/Library/BaseCryptLib/SmmCryptLib.inf
      TlsLib|CryptoPkg/Library/TlsLibNull/TlsLibNull.inf
      OpensslLib|CryptoPkg/Library/OpensslLib/OpensslLib.inf
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
!endif
  $(HP_PLATFORM_PACKAGE)/HpPlatformFeaturesDxe/HpPlatformFeaturesDxe.inf
  $(HP_PLATFORM_PACKAGE)/PlatformMud/Dxe/PlatformMudDxe.inf
  $(HP_PLATFORM_PACKAGE)/PlatformMud/Smm/PlatformMudSmm.inf
  $(HP_PLATFORM_PACKAGE)/HpPlatformServices/Dxe/HpPlatformDxeServices.inf
  $(HP_PLATFORM_PACKAGE)/HpPlatformServices/Smm/HpPlatformSmmServices.inf
  $(HP_PLATFORM_PACKAGE)/HpSecureStorageDeviceDxe/HpSecureStorageDeviceDxe.inf
  $(HP_PLATFORM_PACKAGE)/PciPlatform/Dxe/PciPlatform.inf
!if $(HP_PLATFORM_TYPE) == Nb
  $(HP_PLATFORM_PACKAGE)/Hotkey/Hotkey.inf
  $(HP_PLATFORM_PACKAGE)/PlatformPrivateWmi/PlatformPrivateWmi.inf
!endif  
  $(HP_PLATFORM_PACKAGE)/BiosUpdatePlatformPolicy/BiosUpdatePlatformPolicySmm.inf
!if $(CRB_BOOT_SUPPORT) == FALSE
!if $(HP_PLATFORM_TYPE) == Dt
  $(HP_PLATFORM_PACKAGE)/HpDtPorting/HpDtPortingS5MaxPowerSavingsSmm/HpDtPortingS5MaxPowerSavingsSmm.inf
!endif
!endif
!if gSiPkgTokenSpaceGuid.PcdAcpiEnable == TRUE
  $(HP_PLATFORM_PACKAGE)/HpAcpiPlatformDxe/HpAcpiPlatformDxe.inf {
    <LibraryClasses>
       PcdLib|MdePkg/Library/DxePcdLib/DxePcdLib.inf
  }
!endif
 !include $(HP_PLATFORM_PACKAGE)/Include/$(HP_PLATFORM_TYPE)/SmartCover.dsc.inc

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
   MdeModulePkg/Bus/Pci/NvmExpressDxe/NvmExpressSmm.inf

!if $(HP_PLATFORM_TYPE) == Nb
  $(HP_EPSC_PACKAGE)/ThermalInitDxe/ThermalInitDxe.inf
!endif

!if $(HP_PLATFORM_TYPE) == Nb OR $(HP_PLATFORM_TYPE) == Dt
!if $(HP_WAKE_ON_LAN_SUPPORT) == TRUE
  $(HP_EPSC_PACKAGE)/HpCommonPorting/WOLPlatformPortingDxe/WOLPlatformPortingDxe.inf
  $(HP_EPSC_PACKAGE)/HpCommonPorting/WOLPlatformPortingSmm/WOLPlatformPortingSmm.inf
!endif
!endif
!if $(HP_ACPI_TABLES_ENABLE) == TRUE
  $(HP_PLATFORM_PACKAGE)/AcpiTables/$(HP_PLATFORM_TYPE)/AcpiTables.inf
  $(HP_PLATFORM_PACKAGE)/AcpiTables/$(HP_PLATFORM_TYPE)/PlatformSsdt/PlatformSsdt.inf
  $(HP_PLATFORM_PACKAGE)/AcpiTables/$(HP_PLATFORM_TYPE)/Graphics/IGpuSsdt.inf
!endif  

  #
  # Platform-specific capsule drivers and scoped library overrides.
  #
  !include $(HP_PROJECT_PATH)/Config/CapsuleDriversBuild.dsc

  #
  # Build Options
  #
  !include BuildOptions.dsc

[PcdsFeatureFlag]
  ## Indicates if the platform can support update capsule across a system reset.<BR><BR>
  #   TRUE  - Supports update capsule across a system reset.<BR>
  #   FALSE - Does not support update capsule across a system reset.<BR>
  # @Prompt Enable update capsule across a system reset.
  gEfiMdeModulePkgTokenSpaceGuid.PcdSupportUpdateCapsuleReset|TRUE

[PcdsDynamicDefault]
  ## Default OEM Table ID for ACPI table creation.
  # default set to "NVL     ", will be patched by AcpiPlatform per CPU family.
  # MultiProject builds override this via their Config/PlatformPcdConfig.dsc.
  gEfiMdeModulePkgTokenSpaceGuid.PcdAcpiDefaultOemTableId|0x20202020204C564E     # PcdAcpiDefaultOemTableId, "NVL     "

[PcdsDynamicHii.X64.DEFAULT]
  #
  # SIO1889900 - The "Executing Startup Delay" appears under the HP LOGO after applying factory defaults when MPM=Unlock.(cont.)
  #
  gEfiMdePkgTokenSpaceGuid.PcdPlatformBootTimeOut|L"Timeout"|gEfiGlobalVariableGuid|0x0|0 # Variable: L"Timeout"

[PcdsFixedAtBuild.X64]
  # Keep English default, but expose additional selectable UI languages.
  gEfiMdePkgTokenSpaceGuid.PcdUefiVariableDefaultPlatformLangCodes|"en-US;da-DA;nl-BE;fi-FI;fr-FR;de-DE;it-IT;ja-JA;no-NO;pt-PT;zh-CN;es-ES;sv-SV;zh-TW;ru-RU"

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
