#
# (c) Copyright 2026 HP Development Company, L.P.
# This software and associated documentation (if any) is furnished under a license and may only be used or
# copied in accordance with the terms of the license. Except as permitted by such license, no part of this
# software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
# form or by any means without the express written consent of HP Development Company.
#
# File Name: Z22MekrosPkgConfig.dsc
#

[Defines]
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpFeatureMiscConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/BootOptionsConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/SystemOptionsConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/BuiltInDeviceOptionsConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/PortOptionsConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/PowerManagementOptionsConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpUsbPortConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpFeatureErrorHandlingConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpHumanInterfaceDevicesConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpRtd3AcpiPlatformConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpDiagnosticConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpThermalConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpTelemetryConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpFirmwareFlashConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpPlatformAutoTestConfig.dsc

   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/HpGfxMiscConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/NvidiaGraphicsConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/AmdGraphicsConfig.dsc

   # For Notebook platform
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/HpLidSwitchingConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/HpBrightnessConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/DreamColorPanelConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpBatteryConfig.dsc

   # For Notebook (Panel Tcon) and AIO (Scaler) platform
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/InstantOnLogoConfig.dsc

   # For Intel NB RTD3
!if $(INTEL_PLATFORM) == TRUE
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/IntelHybridGraphicsConfig.dsc
!endif

   # For AMD NB RTD3
!if $(AMD_PLATFORM) == TRUE
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/AmdPowerXpressConfig.dsc
!endif

   # For Desktop platform
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/AddonGfxPolicyConfig.dsc

   # For AIO platform
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpGfx/AioGfxPolicyConfig.dsc

   # For Intel CSME related expending features below.
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpCsme/HpRefurbishCounterConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpCsme/HpMePolicyConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpCsme/HpAmtPolicyConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpAudioConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/HpFeature/HpConnectionDeviceConfig.dsc

   #
   # Platform On/Off features are defined here
   #
   !include $(HP_PROJECT_PACKAGE)/Config/PlatformPkgConfig.dsc
   
   #
   # DSC files include for different boards
   #
   !include $(HP_PROJECT_PACKAGE)/Config/PlatformPcdConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/ChipsetPcdConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/EpscPcdConfig.dsc
   !include $(HP_PROJECT_PACKAGE)/Config/TbtPcdConfig.dsc

