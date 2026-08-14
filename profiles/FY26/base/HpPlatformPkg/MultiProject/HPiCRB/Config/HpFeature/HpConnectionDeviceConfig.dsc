#
# (c) Copyright 2018 - 2025 HP Development Company, L.P.
# This software and associated documentation (if any) is furnished under a license and may only be used or
# copied in accordance with the terms of the license. Except as permitted by such license, no part of this
# software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
# form or by any means without the express written consent of HP Development Company.
#
# Platform Connection Device configuration file.
#

################################################################################
#
# Connection Device build switches configuration
#
################################################################################
[PcdsFeatureFlag]
   gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessDesktopPlatform   |FALSE
   gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessNotebookPlatform  |TRUE

   ## PCD to enable all of Connection Device debug message.
   gEfiHpConDevPkgTokenSpaceGuid.PcdConDevEnableAllDebugMSG   |FALSE

##############################################################################
#                   Common Wireless function
##############################################################################
   ## PCD to enable Wireless device FCC ID support, 2016 platform wouldn't support FCC ID.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessFCCIDSupport      |FALSE

   ## PCD for Wake on Bluetooth supported, drop on 2018 platform. Set to disable.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWoBluetoothSupport        |FALSE  ##800 G7/X360 :set to false to align 800 G6, it should be S3 system only, will double confirm

   gEfiHpConDevPkgTokenSpaceGuid.PcdBluetoothAudioOffloadSupport|FALSE
   gEfiHpConDevPkgTokenSpaceGuid.PcdBluetoothLeAudioSupport|FALSE

##############################################################################
#                   Specific Wireless function
##############################################################################
!if (gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessNotebookPlatform == TRUE)
   ## PCD to determine if system need to support ElectronicLabel, please need to enable this PCD and extend the e-label region size to 200KB.
   gHpElectronicLabelPkgTokenSpaceGuid.PcdElectronicLabelSupport       |FALSE

   ## PCD to enable Host Base MAC address, because function require pre-boot support, please also enable USB LAN boot.(If need.)
   gEfiHpConDevPkgTokenSpaceGuid.PcdHPHBMASupport             |FALSE

   gEfiHpConDevPkgTokenSpaceGuid.PcdHPHBMAOOBWOLSupport       |FALSE

   ## PCD to enable USB LAN dongle support
   gEfiHpConDevPkgTokenSpaceGuid.PcdUsbLanSupport                |FALSE  ## confirm with HP BIOS PM Luke Connery should enable it

   ## PCD to determine if placeholder support for USB LAN, TRUE: enable, FALSE: disable (default)
   gEfiHpConDevPkgTokenSpaceGuid.PcdUsbLanPlaceHolderSupport     |TRUE

   ## PCD for Realtek USB 8153 Legacy boot supported. (UEFI boot default enable on NB) Enable this PCD if platform have no on board NIC or Special request(VA).
   gEfiHpConDevPkgTokenSpaceGuid.PcdRTLUSBLanLegacyBootSupport|FALSE

   ## PCD to show "Lock wireless button" option in F10. Some platform didn't support hardware wireless button and internal keyboard, that should block the wireless btn support.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessButtonSupport     |FALSE

   ## PCD to set to FALSE if your project didn't support WWAN device. (ALL OF SKU)
   gEfiHpConDevPkgTokenSpaceGuid.PcdWWANModuleSupport         |FALSE
   ## PCD to enable Pcie Wwan card support
   gEfiHpConDevPkgTokenSpaceGuid.PcdPcieWwanSupport           |FALSE
   ## PCD to enable UART interface GPS support
   gEfiHpConDevPkgTokenSpaceGuid.PcdUARTGpsSupport            |FALSE

   # Wifi SAR customization default table from Comm. team, default set to disable, enable by request. Please override use below PCD.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWRDSWifiSAREnable         |TRUE

   # Realtek Wifi Static SAR Supported. Default Disable, enable by request.
   gEfiHpConDevPkgTokenSpaceGuid.PcdRTLStaticWifiSAREnable    |FALSE

   # PCD for platform override Realtek Wifi DSM function 3 and 6
   gEfiHpConDevPkgTokenSpaceGuid.PcdRTLWifiDsmFun3            |0x00  #00 - Do not disable 6GHz band; 01 - Disable 6GHz band; 02 - Reserved
   gEfiHpConDevPkgTokenSpaceGuid.PcdRTLWifiDsmFun6            |0x01  #00 - FCC 5.9GHz Disabled; 01 - FCC 5.9GHz Enabled

#   gEfiHpConDevPkgTokenSpaceGuid.PcdWifiDynamicSAREnable      |FALSE  #default enable. This is dynamic PCD, update it depend on platform.

   ## PCD to enable Wake on wlan support
   gEfiHpConDevPkgTokenSpaceGuid.PcdWoWLANSupport             |FALSE

   gEfiHpConDevPkgTokenSpaceGuid.PcdLanWlanAutoSwitchingSupport|TRUE

   # Target NB 800 as the lead platform and for those platforms prior to 800 will be supported at OOC.
   gEfiHpConDevPkgTokenSpaceGuid.PcdLanWwanAutoSwitchingSupport|TRUE

   # Target on NB 800 and beyond platform. Didn't support on Non-MS + WOBT enable platform (DT and NB 400 not supported)
   gEfiHpConDevPkgTokenSpaceGuid.PcdBTErrorRecoveryEnable     |FALSE

   # Target 2020 1000s OOC, platform need to implementation WwanTable.c added into supported list.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWwan5GModuleSupport       |FALSE

   # Follow Intel Dynamic Peak Gain matrix. Intel #559910, PPAG Mode Revision.
   # Bit0: PPAG enable/disable in EU. Bit1: PPAG enable/disable in China. Bit31-2: Reserved
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpDynamicAntennaGainSupport      |0x00

   gEfiHpConDevPkgTokenSpaceGuid.PcdInTileModuleSupport       |FALSE

   # DCR to drop on 800.
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpTile10Support|FALSE

   # Supported on Warg
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpIoTSupport |FALSE

   # BT PPAG Support, default disable
   gEfiHpConDevPkgTokenSpaceGuid.PcdBluetoothPpagSupport|FALSE

   # BT SAR Table Support, default disable
   gEfiHpConDevPkgTokenSpaceGuid.PcdBluetoothSarSupport|FALSE

   ## PCD to control Insta Dock feature support, default disable
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpInstaDockSupport|FALSE

!else
   ## PCD to determine if system need to support ElectronicLabel, please need to enable this PCD and extend the e-label region size to 200KB.
   gHpElectronicLabelPkgTokenSpaceGuid.PcdElectronicLabelSupport       |FALSE

   ## PCD to enable Host Base MAC address, because function require pre-boot support, please also enable USB LAN boot.(If need.)
   gEfiHpConDevPkgTokenSpaceGuid.PcdHPHBMASupport             |FALSE

   gEfiHpConDevPkgTokenSpaceGuid.PcdHPHBMAOOBWOLSupport       |FALSE

   ## PCD to enable USB LAN dongle support
   gEfiHpConDevPkgTokenSpaceGuid.PcdUsbLanSupport                |FALSE  ## confirm with HP BIOS PM Luke Connery should enable it

   ## PCD to determine if placeholder support for USB LAN, TRUE: enable, FALSE: disable (default)
   gEfiHpConDevPkgTokenSpaceGuid.PcdUsbLanPlaceHolderSupport     |FALSE

   ## PCD for Realtek USB 8153 Legacy boot supported. (UEFI boot default enable on NB) Enable this PCD if platform have no on board NIC or Special request(VA).
   gEfiHpConDevPkgTokenSpaceGuid.PcdRTLUSBLanLegacyBootSupport|FALSE

   ## PCD to show "Lock wireless button" option in F10. Some platform didn't support hardware wireless button and internal keyboard, that should block the wireless btn support.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessButtonSupport     |FALSE

   ## PCD to set to FALSE if your project didn't support WWAN device. (ALL OF SKU)
   gEfiHpConDevPkgTokenSpaceGuid.PcdWWANModuleSupport         |FALSE
   ## PCD to enable Pcie Wwan card support
   gEfiHpConDevPkgTokenSpaceGuid.PcdPcieWwanSupport           |FALSE
   ## PCD to enable UART interface GPS support
   gEfiHpConDevPkgTokenSpaceGuid.PcdUARTGpsSupport            |FALSE

   # Wifi SAR customization default table from Comm. team, default set to disable, enable by request. Please override use below PCD.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWRDSWifiSAREnable         |FALSE

   # Realtek Wifi Static SAR Supported.
   gEfiHpConDevPkgTokenSpaceGuid.PcdRTLStaticWifiSAREnable    |FALSE
   # PCD for platform override Realtek Wifi DSM function 3 and 6
   gEfiHpConDevPkgTokenSpaceGuid.PcdRTLWifiDsmFun3            |0x01  #00 - Do not disable 6GHz band; 01 - Disable 6GHz band; 02 - Reserved
   gEfiHpConDevPkgTokenSpaceGuid.PcdRTLWifiDsmFun6            |0x00  #00 - FCC 5.9GHz Disabled; 01 - FCC 5.9GHz Enabled

   ## PCD to enable Wake on wlan support, Turn on if your system is AiO or DM.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWoWLANSupport             |FALSE
   ## PCD to enable Lan/Wlan switching support, Turn on if your system is AiO or DM.
   gEfiHpConDevPkgTokenSpaceGuid.PcdLanWlanAutoSwitchingSupport|FALSE

   # Target NB 800 as the lead platform and for those platforms prior to 800 will be supported at OOC.
   gEfiHpConDevPkgTokenSpaceGuid.PcdLanWwanAutoSwitchingSupport|FALSE

   # Target on NB 800 and beyond platform. Didn't support on Non-MS + WOBT enable platform (DT and NB 400 not supported)
   gEfiHpConDevPkgTokenSpaceGuid.PcdBTErrorRecoveryEnable     |FALSE

   gEfiHpConDevPkgTokenSpaceGuid.PcdWwan5GModuleSupport       |TRUE

   gEfiHpConDevPkgTokenSpaceGuid.PcdInTileModuleSupport       |FALSE

   gEfiHpConDevPkgTokenSpaceGuid.PcdHpTile10Support           |FALSE

   gEfiHpConDevPkgTokenSpaceGuid.PcdHpIoTSupport               |FALSE

   ## PCD to control Insta Dock feature support, default disable
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpInstaDockSupport|FALSE
!endif

################################################################################
#
# Connection Device Feature Parameter configuration
#
################################################################################
[PcdsFixedAtBuild]
!if (gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessNotebookPlatform == TRUE)
   ## Wifi Dynamic SAR customization default table from Comm. team, default set to disable, enable by request. Please override use below PCD.
   ## Some platform use same BIOS on Supported/Unsupported Dyn BIOS SAR platform.
   ## If your BIOS need to support/not support Dynamic SAR at the same time, please enable PcdEWRDWifiDynamicSAR(Root flag) and enable/disable PcdWifiDynamicSAREnable depend on platform designed.
    gEfiHpConDevPkgTokenSpaceGuid.PcdEWRDWifiDynamicSAR        |FALSE
!else
   # Wifi Dynamic SAR customization default table from Comm. team, default set to disable, enable by request. Please override use below PCD.
   gEfiHpConDevPkgTokenSpaceGuid.PcdEWRDWifiDynamicSAR        |FALSE
!endif
  gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessDevPowerControlNum|3

  # For WLAN Card
  gEfiHpConDevPkgTokenSpaceGuid.PcdWlanPcieBridgeDevNum|0xFF
  gEfiHpConDevPkgTokenSpaceGuid.PcdWlanPcieBridgeFunNum|0xFF
  # PCIE Root Port for WLAN(0-Based)
  gEfiHpConDevPkgTokenSpaceGuid.PcdWlanPcieBridgeNum|0xFF

  # For WWAN Card
  gEfiHpConDevPkgTokenSpaceGuid.PcdWwanPcieBridgeDevNum|0xFF
  gEfiHpConDevPkgTokenSpaceGuid.PcdWwanPcieBridgeFunNum|0xFF
  # PCIE Root Port for WWAN(0-Based)
  gEfiHpConDevPkgTokenSpaceGuid.PcdWwanPcieBridgeNum|0xFF

  # for NIC
  gEfiHpConDevPkgTokenSpaceGuid.PcdGbNicBusNum|0xFF    #[Intel GbE controller]
  gEfiHpConDevPkgTokenSpaceGuid.PcdGbNicDevNum|0xFF    #[Intel GbE controller]
  gEfiHpConDevPkgTokenSpaceGuid.PcdGbNicFunNum|0xFF    #[Intel GbE controller]
  gEfiHpConDevPkgTokenSpaceGuid.PcdGbNicBridgeNum|0xFF #Implement the correct NIC bridge Num#.

#
# PCD to determine GPIO definition.
#
  # Wlan Device GPIO handle, fill out 0xFF if platform not support.
  # WLAN_TRANSMIT_OFF#
  gEfiHpConDevPkgTokenSpaceGuid.PcdWLANTransmitOffGpioPin|0xFFFFFFFF # unsupport
  gEfiHpConDevPkgTokenSpaceGuid.PcdWLANTransmitOffGpioActive|1       # High Active

  # Bluetooth Device GPIO handle, fill out 0xFF if platform not support.
  # BT_OFF
  gEfiHpConDevPkgTokenSpaceGuid.PcdBluetoothGpioPin|0xFFFFFFFF       # unsupport
  gEfiHpConDevPkgTokenSpaceGuid.PcdBluetoothGpioActive|0             # Low Active

  # Wlan LED Device GPIO handle, fill out 0xFF if platform not support.
  gEfiHpConDevPkgTokenSpaceGuid.PcdWlanSWRfKillLEDGpioPin|0xFFFFFFFF       # NA

  # Wwan Device GPIO handle, fill out 0xFF if platform not support.
  # WWAN_TRANSMIT_OFF#
  gEfiHpConDevPkgTokenSpaceGuid.PcdWWANTransmitOffGpioPin|0xFFFFFFFF # unsupport
  gEfiHpConDevPkgTokenSpaceGuid.PcdWWANTransmitOffGpioActive|1       # High Active

  # Gps Device GPIO handle, fill out 0xFF if platform not support.
  gEfiHpConDevPkgTokenSpaceGuid.PcdGPSTransmitOffGpioPin|0xFFFFFFFF  # unsupport
  gEfiHpConDevPkgTokenSpaceGuid.PcdGPSTransmitOffGpioActive|1        # High Active

  #For LAN/WLAN switching, fill out 0xFF if platform not support.
  gEfiHpConDevPkgTokenSpaceGuid.PcdLanLinkGpioPin|0xFFFFFFFF               # NA

  # For RFID IoT detection, please implement below PCD even platform didnt support IoT
  gEfiHpConDevPkgTokenSpaceGuid.PcdWWANConfig0GpioPin|0xFFFFFFFF # unsupport
  gEfiHpConDevPkgTokenSpaceGuid.PcdWWANConfig2GpioPin|0xFFFFFFFF # unsupport
  gEfiHpConDevPkgTokenSpaceGuid.PcdWWANConfig3GpioPin|0xFFFFFFFF # unsupport
  #For Pcie Wwan support, fill out 0xFF if platform not support.
  !if (gEfiHpConDevPkgTokenSpaceGuid.PcdPcieWwanSupport == TRUE)
     # BB_RST pin:
     gEfiHpConDevPkgTokenSpaceGuid.PcdPcieWwanBBResetGpioPin     |0xFFFFFFFF # unsupport

     # PERST pin:
     gEfiHpConDevPkgTokenSpaceGuid.PcdPcieWwanPEResetGpioPin     |0xFFFFFFFF # unsupport

     # Wake control pin
     gEfiHpConDevPkgTokenSpaceGuid.PcdPcieWwanWakeGpioPin        |0xFFFFFFFF # unsupport

     # 0-base definition. Please set to 0xFF if not support.
     # After CNL please fill out the request number as acually number, KBL-R fill out the mask offset.
     gEfiHpConDevPkgTokenSpaceGuid.PcdPcieWwanClockRequestNum    |0xFFFF
  !endif

   # NFC_DET#:
   gEfiHpConDevPkgTokenSpaceGuid.PcdNfcDetectGpioPin           |0xFFFFFFFF # unsupport

   # RFID, please set to 0xFF if platform not supported.
   gEfiHpConDevPkgTokenSpaceGuid.PcdRFIDBeepSoundEnableGpioPin      |0xFFFFFFFF
   # NFC_DWL_REQ / AUDIO_FEEDBACK_BEEP: GPP_F13
   # Please implement below PCD even platform didnt support RFID, and GPIO table have to init to RFID setting.
   gEfiHpConDevPkgTokenSpaceGuid.PcdNfcDwlReqGpioPin           |0xFFFFFFFF # unsupport

   # NFC_INT / RFID_CARD_READ: GPP_F11
   # Please implement below PCD even platform didnt support RFID, and GPIO table have to init to RFID setting.
   gEfiHpConDevPkgTokenSpaceGuid.PcdNfcIntGpioPin              |0xFFFFFFFF # unsupport

   # NFC_RST# / LOW_POWER_MODE
   # Please implement below PCD even platform didnt support RFID, and GPIO table have to init to RFID setting.
   gEfiHpConDevPkgTokenSpaceGuid.PcdRFIDLowPowerModeGpioPin     |0xFFFFFFFF # unsupport

   # RFID_WAKE_CODEC
   # Please implement below PCD even platform didnt support RFID, and GPIO table have to init to RFID setting.
   gEfiHpConDevPkgTokenSpaceGuid.PcdRFIDCodecWakeGpioPin        |0xFFFFFFFF # unsupport



################################################################################
#
# Connection Device Platform Definition
#
################################################################################
[Defines]

#
# Intel CNV UEFI Variables support. (Default is disabled), this FLAG works with PcdHpCnvLegacyAcpiTables
#   TRUE  : It will initial CNV UEFI Variables (PCD in PcdsDynamicExDefault) and biuld HpIntelCnvUefiLib for platform override.
#
DEFINE INTEL_CNV_UEFI_VARIABLES_SUPPORT = FALSE

################################################################################
#
# Connection Device Platform specific setting
#
################################################################################
[PcdsFixedAtBuild]

   ## PCD for Time Average SAR support, due to the schedule impact 400/600 G8 should disabled. 800G8 follow on should enable if DCR apply.
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpTimeAverageSARSupport|FALSE
!if (gEfiHpConDevPkgTokenSpaceGuid.PcdWRDSWifiSAREnable == FALSE) AND (gEfiHpConDevPkgTokenSpaceGuid.PcdEWRDWifiDynamicSAR == FALSE)
   ## If no SAR solution, should not enable Time average SAR solution.
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpTimeAverageSARSupport|FALSE
!endif

   ## PCD for Indonesia New Band support, due to the schedule impact 400/600 G8 should disabled. 800G8 follow on should enable if DCR apply.
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpIndonesiaNewBandSupport|FALSE

   ##
   ## Refer the struct in HpPe\HpConnectionDevicePkg\HpConnectionDevicePkg.dec
   ## For multi platform, platform override value (base on platform ID, override in HpPlatformPkg\PlatformDxe\HpBiosWifiSarOverrideDxe\HpBiosWifiSarOverrideDxe.inf) Platform need to implement to detect function.
   ## For multi platform, each pcd will be defined by gEfiHpPlatformPkgTokenSpaceGuid.XXX in HpPlatformPkg.dec

   ## Wifi SAR value definition (Static and Dynamic).
   ##
   # Static Wifi SAR Support.
   # Comm team BIOS SAR matrix, Computron need to enable Geo SAR and Static BIOS SAR.
   # Intel Static Wifi SAR
   #   Overrided by HpPlatformPkg\PlatformDxe\HpBiosWifiSarOverrideDxe\HpBiosWifiSarOverrideDxe_NB800.c

   ##
   ## Wifi Non FCC type BIOS SAR value definition. (GEO BIOS SAR)
   ## **IMPORTANT** Set to all 0x00 if platform not support.
   # Intel GEO SAR
   #   Overrided by HpPlatformPkg\PlatformDxe\HpBiosWifiSarOverrideDxe\HpBiosWifiSarOverrideDxe_NB800.c

   # Dynamic Wifi SAR Support.
   #   Overrided by HpPlatformPkg\PlatformDxe\HpBiosWifiSarOverrideDxe\HpBiosWifiSarOverrideDxe_NB800.c

   # Dynamic Wifi SAR Support.
   gEfiHpConDevPkgTokenSpaceGuid.PcdEWRDWifiDynamicSARSets    |0x03       # Dynamic WiFi SAR Number of Optional added SAR table sets to be used //0- No additional table sets, 1~3 - Optional additional table sets

   # Dynamic Wifi SAR device mode definition. BIT15-BIT8 means ANT A SAR table set(Fill out the number of sets), BIT7-BIT0 means ANT B SAR table set(Fill out the number of sets).
   # If device mode not support platform set to zero.
#   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeLidCloseOnTable |0x33
#   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeClamShellOnTable|0x22
#   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeFlatOnTable     |0x33
#   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeTentOnTable     |0x33
#   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeStandOnTable    |0x22
#   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeTabletOnTable   |0x33
#   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeBookOnTable     |0x22
#   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeDefault  |0x33
   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeLidClose         |0x33
   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeClamShell        |0x22
   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeFlat             |0x33
   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeTent             |0x33
   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeStand            |0x22
   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeTablet           |0x33
   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeDefault          |0x33
   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeMedia            |0x22
   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModePresentation     |0x22
   gEfiHpConDevPkgTokenSpaceGuid.PcdDynamicSARDevModeUnknow           |0x33

   # Warg/Warg 13 x360 don't Support RTK WLAN.
   # Realtek Wifi Static SAR support.
   # gEfiHpConDevPkgTokenSpaceGuid.PcdRTLStaticWifiSARTableSet_1|{0x11,0x08,0x08,0x08,0x08,0x11,0x08,0x08,0x08,0x08}
   # gEfiHpConDevPkgTokenSpaceGuid.PcdRTLStaticWifiSARTableSet_2|{0x11,0x08,0x08,0x08,0x08,0x11,0x08,0x08,0x08,0x08}
   # Realtek Wifi GEO SAR
   # gEfiHpConDevPkgTokenSpaceGuid.PcdRTLDynamicWifiGEOSAR_1|{0x11,0x00,0x00,0x00,0x00,0x08,0x00,0x00,0x00,0x00}
   # gEfiHpConDevPkgTokenSpaceGuid.PcdRTLDynamicWifiGEOSAR_2|{0x0A,0x00,0x00,0x00,0x00,0x12,0x0A,0x0A,0x0A,0x0A}
   # gEfiHpConDevPkgTokenSpaceGuid.PcdRTLDynamicWifiGEOSAR_3|{0x0A,0x00,0x00,0x00,0x00,0x12,0x0A,0x0A,0x0A,0x0A}

   # Follow Intel Dynamic Peak Gain matrix.
   # Default dynamic antenna peak Gain
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpDynamicAntennaGain|{0x18,0x28,0x28,0x28,0x28,0x18,0x28,0x28,0x28,0x28,0x28,0x28,0x18,0x28,0x28,0x28,0x28,0x18,0x28,0x28,0x28,0x28}

   ## PCD to include HP Intel/Realtek/QualComm/MediaTek ACPI SSDT code.
   gEfiHpConDevPkgTokenSpaceGuid.PcdIntelWifiSupport           |TRUE
   gEfiHpConDevPkgTokenSpaceGuid.PcdRtkWifiSupport             |FALSE
   gEfiHpConDevPkgTokenSpaceGuid.PcdQcWifiSupport              |FALSE
   gEfiHpConDevPkgTokenSpaceGuid.PcdMtkWifiSupport             |FALSE

   ##
   ## PCD to include ACPI SSDT code for WLAN/BT feature.
   ##   TRUE  : WLAN/BT feature will follow ACPI Method + some UEFI Variables (ex: BTPPAG, DSBR, must enable INTEL_CNV_UEFI_VARIABLES_SUPPORT) to Configure
   ##   FALSE : WLAN/BT feature will follow UEFI Variables (PCD in PcdsDynamicExDefault) -> ACPI Method priority to Configure
   ##
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpCnvLegacyAcpiTables      |TRUE

   ## PCD to report default value of GLAI (CNV Guid Lock Status ACPI Indicator)
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpCnvGuidLockStatus        |1

   ## PCD for the version of Intel CNV UEFI Variables
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpCnvUefiVarVersion        |2

[PcdsFixedAtBuild.common]

[PcdsDynamicDefault]
  # DSM Wi-Fi 6E UHB(6GHz) Function 3 bits description
  # bit 0       Force disable all countries that are not defined in the following bits
  # bit 1       USA
  # bit 2       Rest of the World
  # bit 3       EU countries
  # bit 4       South Korea
  # bit 5       Brazil
  # bit 6       Chile
  # bit 7       Japan
  # bit 8       Canada
  # bit 9       Morocco
  # bit 10      Mongolia
  # bit 11      Malaysia
  # bit 12      Saudi Arabia
  # bit 13      Mexico
  # bit 14      Nigeria
  # bit 15      Thailand
  # bit 16      Singapore
  # bit 17      Taiwan
  # bit 18      South Africa
  # bit 31-19   Reserved; should be set to zeros
gEfiHpConDevPkgTokenSpaceGuid.PcdHpWifi6EUhb |0x003F

[PcdsDynamicExDefault]
   #
   # DSBR (Drive Strength BRI Rsp) for Fillmore Peak 2 (BE201)
   # 0xF1 indicates the platform is not compatible with the 10 Ohm, and the resistor on board is 33 Ohm.
   # 0xB1 indicates the platform is compatible with the 10 Ohm (Default value when this variable does not exist)
   #
   #gEfiHpConDevPkgTokenSpaceGuid.PcdUefiDriveStrengthBriRsp     |0x000000F1

[BuildOptions]
     DEFINE WLAN_PCIE_RP_PATH                       = /D WLAN_PCIE_RP_PATH="\_SB.PC00.RP07"
     DEFINE WLAN_PCIE_DEV_PATH                      = /D WLAN_PCIE_DEV_PATH="\_SB.PC00.RP07.PXSX"
     DEFINE BT_USB_PORT_PATH                        = /D BT_USB_PORT_PATH="\_SB.PC00.XHCI.RHUB.HS10"
     DEFINE BT_DEVICE_PATH                          = /D BT_DEVICE_PATH="\_SB.PC00.XHCI.RHUB.HS10"

  !if (gEfiHpConDevPkgTokenSpaceGuid.PcdLanWwanAutoSwitchingSupport == TRUE)
     DEFINE DSC_LAN_WLAN_WWAN_AUTO_SWITCHING            = /D LAN_WLAN_WWAN_AUTO_SWITCHING=1
  !else
     DEFINE DSC_LAN_WLAN_WWAN_AUTO_SWITCHING            =
  !endif

  !if (gEfiHpConDevPkgTokenSpaceGuid.PcdHPHBMAOOBWOLSupport == TRUE)
     DEFINE DSC_HP_HBMA_OOB_WAKE_ON_LAN_SUPPORT = /DHP_HBMA_OOB_WAKE_ON_LAN_SUPPORT=1
  !else
     DEFINE DSC_HP_HBMA_OOB_WAKE_ON_LAN_SUPPORT =
  !endif

  !if (gEfiHpConDevPkgTokenSpaceGuid.PcdPcieWwanSupport == TRUE)
     DEFINE WWAN_ROOT_PORT                        = /D WWAN_ROOT_PORT="RP08" #DB1
  !else
     DEFINE WWAN_ROOT_PORT                       =
  !endif

  !if (gEfiHpConDevPkgTokenSpaceGuid.PcdConDevEnableAllDebugMSG == TRUE)
     DEFINE DSC_CONDEV_DEBUG_OPTION = /DCONDEV_ENABLE_ALL_DBG_MSG=1
  !else
     DEFINE DSC_CONDEV_DEBUG_OPTION =
  !endif

  !if (gEfiHpConDevPkgTokenSpaceGuid.PcdBTErrorRecoveryEnable == TRUE)
     DEFINE BT_ERROR_RECOVERY = /DBT_ERROR_RECOVERY=1
  !else
     DEFINE BT_ERROR_RECOVERY =
  !endif

  !if (gEfiHpConDevPkgTokenSpaceGuid.PcdInTileModuleSupport == TRUE)
     DEFINE HP_INTILE_SUPPORT = /DHP_INTILE_SUPPORT=1
  !else
     DEFINE HP_INTILE_SUPPORT =
  !endif

  !if $(INTEL_CNV_UEFI_VARIABLES_SUPPORT) == TRUE
     DEFINE DSC_INTEL_CNV_UEFI_VARIABLES_SUPPORT = -DINTEL_CNV_UEFI_VARIABLES_SUPPORT=1
  !else
     DEFINE DSC_INTEL_CNV_UEFI_VARIABLES_SUPPORT = -DINTEL_CNV_UEFI_VARIABLES_SUPPORT=0
  !endif

  #Cnvi Wifi/BT F10 dependency. Due to Cnvi WLAN could not turn off alone. Once user disable WLAN will pop up a warning and turn off BT automatic.
  #Once user want to Enable BT and wlan in disabled status that will alert a warning to notice user.(Cnvi only) Enable from 800 G7.
  DEFINE CNVIWLAN_F10_DEP = /DCNVIWLAN_F10_DEP=1

  DEFINE CONDEV_ACPI_PATH = $(WLAN_PCIE_RP_PATH) $(WLAN_PCIE_DEV_PATH) $(BT_USB_PORT_PATH) $(BT_DEVICE_PATH) $(DSC_LAN_WLAN_WWAN_AUTO_SWITCHING) $(DSC_HP_HBMA_OOB_WAKE_ON_LAN_SUPPORT) $(WWAN_ROOT_PORT) $(DSC_CONDEV_DEBUG_OPTION) $(CNVIWLAN_F10_DEP) $(BT_ERROR_RECOVERY) $(HP_INTILE_SUPPORT) $(DSC_INTEL_CNV_UEFI_VARIABLES_SUPPORT)
