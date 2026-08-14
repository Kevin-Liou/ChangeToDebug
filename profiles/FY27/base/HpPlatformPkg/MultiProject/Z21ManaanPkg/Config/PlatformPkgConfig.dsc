#
# (c) Copyright 2026 HP Development Company, L.P.
# This software and associated documentation (if any) is furnished under a license and may only be used or
# copied in accordance with the terms of the license. Except as permitted by such license, no part of this
# software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
# form or by any means without the express written consent of HP Development Company.
#
# Platform configuration file.
#

[Defines]
#
# TRUE is ENABLE. FALSE is DISABLE.
#

!if $(INTEL_PLATFORM) == TRUE
  DEFINE ME_FW_RECOVERY_SUPPORT = TRUE
  DEFINE ME_ENABLE = TRUE
  DEFINE ME_DISABLE_SUPPORT = TRUE
!endif

  # TRUE: Build HP AcpiTables.inf, FALSE: Build Intel AcpiTables.inf
  DEFINE HP_ACPI_TABLES_ENABLE = TRUE

#
# HpPlatformPkg
#
  DEFINE DEBUG_BIOS_ENABLE = FALSE
  DEFINE DXE_COMPRESS_ENABLE = TRUE
  DEFINE FAT_ENABLE = TRUE
  DEFINE LFMA_ENABLE = FALSE                # Load module at fixed address feature
  DEFINE LZMA_ENABLE = TRUE

  DEFINE NETWORK_ENABLE = TRUE
  DEFINE NETWORK_IP6_ENABLE = TRUE
  DEFINE NETWORK_ISCSI_ENABLE = TRUE        # Set to TRUE for ENABLE_MD5_DEPRECATED_INTERFACES flag
  DEFINE NETWORK_VLAN_ENABLE = TRUE

  DEFINE PPM_ENABLE = TRUE
  DEFINE S4_ENABLE = TRUE

  DEFINE SECURE_BOOT_ENABLE = TRUE
  DEFINE SETUP_ENABLE = TRUE
  DEFINE SOURCE_DEBUG_USE_USB = FALSE
  DEFINE SSE2_ENABLE = FALSE

  DEFINE TPM_ENABLE = TRUE

  DEFINE GROUP_GPIO_SUPPORT = TRUE
  DEFINE VTX_ENABLE = TRUE
  DEFINE CDROM_BOOT_SUPPORT = FALSE

!if $(NETCLONE_SUPPORT) == FALSE
# Do Not modify here
   DEFINE HP_NET_CLONE_EFI_SUPPORT = FALSE
!else
# Modify to FALSE if Net Clone EFI support is not desired in a Net Clone BIOS
   DEFINE HP_NET_CLONE_EFI_SUPPORT = TRUE
!endif

!if $(NETCLONE_SUPPORT) == FALSE
# NETCLONE_SUPPORT is FALSE means that Stratus/Doppler support may be enabled on the platform.
!if $(TARGET) == DEBUG
  DEFINE CONNECTED_BIOS_ENABLED   = FALSE
!else
  DEFINE CONNECTED_BIOS_ENABLED   = TRUE
!endif
!else
# NETCLONE_SUPPORT is TRUE means that Stratus/Doppler not supported
  DEFINE CONNECTED_BIOS_ENABLED   = FALSE
!endif


#
# HP Core
#
!if ($(DCI_ENABLE) == TRUE) OR ($(TARGET) == DEBUG)
  DEFINE MULTIPLE_FIRMWARE_VOLUME_SUPPORT = FALSE
!else
  DEFINE MULTIPLE_FIRMWARE_VOLUME_SUPPORT = FALSE
!endif

  DEFINE FINGERPRINT_SUPPORT = FALSE

  DEFINE DUST_FILTER_SUPPORT = TRUE
  DEFINE RESTRICT_USB_DEVICES_SUPPORT = FALSE

  DEFINE P21_SUPPORT = TRUE
  DEFINE BEAM_SUPPORT = TRUE
  DEFINE HEP_SUPPORT = TRUE
  DEFINE NETWORK_OS_RECOVERY_SUPPORT = TRUE
  DEFINE DRIVELOCK_AUTO_UNLOCK_SUPPORT = TRUE
  DEFINE NVME_NAMESPACE_SUPPORT = TRUE

# The following flags: EMBEDDED_OS_RECOVERY_DEVICE_SUPPORT and ESSD_SHM_SUPPORT are mutually exclusive.
# They cannot both be set to TRUE at any given time.
# The EMBEDDED_OS_RECOVERY_DEVICE_SUPPORT flag supports the native eMMC option for OS recovery, ME recovery, and secure erase.
# The ESSD_SHM_SUPPORT flag supports the USB-bridged-eMMC option for OS recovery, ME recovery, and secure erase
# through the EC shared memory interface.

  DEFINE EMBEDDED_OS_RECOVERY_DEVICE_SUPPORT  = FALSE
  DEFINE ESSD_SHM_SUPPORT = FALSE

  DEFINE FLIP_SUPPORT = TRUE
  DEFINE MULTI_KEY_SUPPORT = TRUE
  DEFINE SYSTEM_BIOS_SFU_SUPPORT = FALSE


  DEFINE BIOS_AUDIT_LOG_SUPPORT = TRUE
  DEFINE ENHANCED_SMART_COVER_SUPPORT = TRUE
  DEFINE USE_SECURITY_BINARY_PKG = TRUE

  #DEFINE BUILD_HP_TEST_APPS = FALSE
  #DEFINE SCREENSHOTS_ENABLED = FALSE

!if $(P21_SUPPORT) == FALSE
  # If P21_SUPPORT is FALSE, all P21 sub-features should be disabled.
  DEFINE BEAM_SUPPORT = FALSE
  DEFINE HEP_SUPPORT = FALSE
  DEFINE NETWORK_OS_RECOVERY_SUPPORT = FALSE
  DEFINE EMBEDDED_OS_RECOVERY_DEVICE_SUPPORT  = FALSE
  DEFINE ESSD_SHM_SUPPORT = FALSE
!endif

!if $(MULTI_KEY_SUPPORT) == FALSE
  # FLIP_SUPPORT requires MULTI_KEY_SUPPORT to be functional
  DEFINE FLIP_SUPPORT = FALSE
!endif

!if $(TARGET) == DEBUG
  DEFINE PREBOOT_WIFI_SUPPORT   = FALSE
!else
  DEFINE PREBOOT_WIFI_SUPPORT   = TRUE
!endif

  DEFINE AUTOMATION_TEST_MODE = TRUE

  DEFINE HP_DEVICE_IDENTITY_SUPPORT = TRUE
#
# TPM2:Begin
#
    DEFINE TPM2_ENABLE = TRUE
#
# TPM2:End
#

#
# MdeModulePkg
#
  DEFINE UNICODE_COLLECTION_ENABLE = TRUE
  DEFINE USB_ENABLE = TRUE
  DEFINE USB_SERIAL_STATUS_CODE_ENABLE = TRUE
  DEFINE VARIABLE_INFO_ENABLE = FALSE

#
# Intel
#
  DEFINE WDT_DXE_ENABLE = TRUE

  #
  # VP: Override flags for Virtual Platform
  #
!if gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdVPEnable == TRUE
  DEFINE NETWORK_ENABLE = FALSE
  DEFINE NETWORK_IP6_ENABLE = FALSE
  DEFINE NETWORK_ISCSI_ENABLE = FALSE
  DEFINE NETWORK_VLAN_ENABLE = FALSE

  DEFINE PPM_ENABLE = FALSE
  DEFINE S4_ENABLE = FALSE
  DEFINE TPM_ENABLE = FALSE
!endif

  #
  # SLE: Override flags for Emulation
  #
!if gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdSLEEnable == TRUE
  DEFINE DXE_COMPRESS_ENABLE = FALSE
  DEFINE FAT_ENABLE = FALSE
  DEFINE LZMA_ENABLE = FALSE
  DEFINE ME_ENABLE = FALSE

  DEFINE NETWORK_ENABLE = FALSE
  DEFINE NETWORK_IP6_ENABLE = FALSE
  DEFINE NETWORK_ISCSI_ENABLE = FALSE
  DEFINE NETWORK_VLAN_ENABLE = FALSE

  DEFINE PPM_ENABLE = FALSE
  DEFINE S4_ENABLE = FALSE
  DEFINE SECURE_BOOT_ENABLE = FALSE

  DEFINE SETUP_ENABLE = FALSE
  DEFINE SMBIOS_ENABLE = FALSE
  DEFINE TPM_ENABLE = FALSE

  DEFINE UNICODE_COLLECTION_ENABLE = FALSE
  DEFINE USB_ENABLE = FALSE

  DEFINE WDT_DXE_ENABLE = FALSE
!endif

#
# Intermediate cod file generation
#
  DEFINE RELEASE_BUILD_DEBUG            = FALSE
  DEFINE EFI_GENERATE_INTERMEDIATE_FILE = FALSE

#
# HP-specific Miscellaneous defines
#
  ##  set to I2C or USB
  ##  or set to NONE if platform does not support Touch panel
  ##  Do NOT set to FALSE or warning message will pop up due to comaprison betweren boolean and string
  DEFINE HP_TOUCH_PANEL_INTERFACE  = NONE

  DEFINE AMP_SUPPORT = FALSE

!if $(VTX_ENABLE) == FALSE
  DEFINE AXB_SUPPORT = FALSE
!else
  DEFINE AXB_SUPPORT = TRUE
!endif

  DEFINE HP_WAKE_ON_LAN_SUPPORT   = TRUE

  DEFINE HP_VPM_SUPPORT = TRUE

  DEFINE HP_DTT_SUPPORT = gEfiHpThermalPubIntPkgTokenSpaceGuid.PcdDptfEnable

!if ($(HP_VPM_SUPPORT) == TRUE)
  DEFINE HP_SUPER_VPM_SUPPORT = TRUE
!endif

!if gEfiHpConDevPkgTokenSpaceGuid.PcdHPHBMAOOBWOLSupport == TRUE
  DEFINE HP_WAKE_ON_LAN_SUPPORT   = TRUE
!endif

  DEFINE CLEAR_PASSWORD_BY_RTC_REMOVAL_SUPPORT = TRUE

  DEFINE REPLACEABLE_PANEL_SUPPORT = FALSE
  DEFINE HP_THUNDERBOLT_OPTIONROM_SUPPORT = TRUE

#
# TARGET controls the compiler option to enable source level debug.
# DEBUG_BIOS_ENABLE flag enables DEBUG message and disable optimization.
#
# TARGET    DEBUG_BIOS_ENABLE    BiosImage
# DEBUG     TRUE                 Image supports easy source level debug, and have debug message.
# DEBUG     FALSE                Image supports source level debug, but no debug message.
# RELEASE   FALSE                Image without source level debug and debug message.
# RELEASE   TRUE                 Image without source level debug, but has debug message.
#

!if $(TARGET) == DEBUG
  # Disable this flag when to debug image without debug message.
  DEFINE DEBUG_BIOS_ENABLE = TRUE

  # Disable some feature to fix ROM size insufficient problem on debug build.
  !if $(SPI_ROM_SIZE) < 32
    DEFINE ME_ENABLE = FALSE
  !endif
!endif

#
# There are platform-specific features that depend on the presence of an E-SPI bus on the platform.
# At present, this depends on AMD vs. Intel platform, but it might not always be the case.
# So define a flag that is E-SPI specific, and key it to Intel platform variable for the moment.
#
!if $(INTEL_PLATFORM) == TRUE
  DEFINE HP_ESPI_BUS_SUPPORT = TRUE
!else
  DEFINE HP_ESPI_BUS_SUPPORT = FALSE
!endif

# Generate .cod file on RELEASE_BUILD_DEBUG which is used by XDP.
!if ($(RELEASE_BUILD_DEBUG) == TRUE)
  DEFINE EFI_GENERATE_INTERMEDIATE_FILE = TRUE
!endif


DEFINE NETWORK_ENABLE = gPlatformModuleTokenSpaceGuid.PcdNetworkEnable
DEFINE INTEL_FPDT_ENABLE = gMinPlatformPkgTokenSpaceGuid.PcdPerformanceEnable
