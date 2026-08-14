#
# (c) Copyright 2023 - 2024 HP Development Company, L.P.
# This software and associated documentation (if any) is furnished under a license and may only be used or
# copied in accordance with the terms of the license. Except as permitted by such license, no part of this
# software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
# form or by any means without the express written consent of HP Development Company.
#
# File Name: HpFeatureMiscPlatformConfig.dsc
#
# Note: Platform developer can refer to path below to override the default feature flags in here
#
#   HpFeatureMisc: HpFeature\HpFeatureMisc\PubIntPkg\HpFeatureMiscPubIntPkgConfig.dsc
#

[Defines]

#
# Determine if BIOS image can boot on CRB. (Default is disabled)
#  (Default definition is in HpCore, but Build Option is in HpFeatureMisc)
#
DEFINE CRB_BOOT_SUPPORT = TRUE

#
# Intel Platform selection (Default is disabled)
#  Note: Default definition and Build Option are in HpCore
#
DEFINE INTEL_PLATFORM = TRUE

#
# AMD Platform selection. (Default is disabled)
#  Note: Default definition and Build Option are in HpCore
#
DEFINE AMD_PLATFORM = FALSE

#
# Enable ACPI Support. (Default is disabled)
#  Note: Default definition is in HpCore, but Build Option is in HpFeatureMisc
#
DEFINE ACPI_ENABLE = TRUE

#
# Enable S3 Support. (Default is disabled)
#  Note: Default definition is in HpCore, but Build Option is in HpFeatureMisc
#
DEFINE S3_ENABLE = FALSE

#
# Indicate HP Notebook platform (Default is disabled)
#
DEFINE NOTEBOOK_PLATFORM = FALSE

#
# Indicate HP Desktop (DT, DM, AIO) platform. (Default is disabled)
#
DEFINE DESKTOP_PLATFORM = TRUE

#
# Preboot LINUX OS detection via scanning disk partition type (Default is disabled)
#
DEFINE PREBOOT_LINUX_OS_DETECTION = FALSE   # For HP Hybrid Graphics on mWS only

#
# Feature flag to support ACPI HPPT table to report boot performance data. (Default is disabled)
#
DEFINE HP_BOOT_PERFORMANCE_TABLE_SUPPORT = FALSE   #FALSE

#
# HP Post Code Dump (Default is disabled)
# This function is to show up the current POST codes via Public WMI in MPM.
#
DEFINE HP_POST_CODE_DUMP_SUPPORT = FALSE

#
# HP BIOS Protection Sign Simulation (Default is disabled)
# This function is to simulate BIOS protection sign flow via Public WMI in MPM.
#
DEFINE HP_BIOS_PROTECTION_SIGN_SIMULATION_SUPPORT = TRUE

#
# SSID override vai Public WMI interface (Default is disabled)
# This function is to set a new SSID in BCU. Platform code can read it and overwrite SSID.
#
DEFINE OVERWRITE_SSID_IN_WMI_SUPPORT = FALSE

#
# Determine if platform want to disable H.264 and/or H.265 (HEVC). (Default is disabled)
#
DEFINE HW_CODEC_DISABLE_SUPPORT = TRUE

#
# Determine if platform support PCM Carbon. Default is supported.
#
DEFINE CARBON_SUPPORT = FALSE

[PcdsFeatureFlag]
   #
   # Virtual Platform feature support
   #
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdVPEnable            |FALSE

   #
   # Override flags for Emulation
   #
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdSLEEnable           |FALSE

#[HP_MOD]+ Keep these 2 PCDs temporarily due to *.py still use it
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdIntelPlatform       |$(INTEL_PLATFORM)
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdAmdPlatform         |$(AMD_PLATFORM)
#[HP_MOD]-


[PcdsFixedAtBuild]
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdTempBusNum          |0x90       # Follow default PcdSiliconInitTempPciBusMax

   ## PCD to enable HP PostCode Debug by serial port
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdHpPostCodeToSerialPortEnable | FALSE
!if $(FSP_DEBUG_IN_RELEASE_MODE) == TRUE
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdHpPostCodeToSerialPortEnable|TRUE
!endif