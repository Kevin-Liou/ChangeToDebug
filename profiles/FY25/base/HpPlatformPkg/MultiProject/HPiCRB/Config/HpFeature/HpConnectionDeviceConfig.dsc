#
# Platform Connection Device configuration file.
#
# (c) Copyright 2018 HP Development Company, L.P.
# This software and associated documentation (if any) is furnished under a license and may only be used or
# copied in accordance with the terms of the license. Except as permitted by such license, no part of this
# software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
# form or by any means without the express written consent of HP Development Company.
#

################################################################################
#
# Connection Device build switches configuration
#
################################################################################
[PcdsFeatureFlag]
   gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessDesktopPlatform   |TRUE
   gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessNotebookPlatform  |FALSE

   ## PCD to enable all of Connection Device debug message.
   gEfiHpConDevPkgTokenSpaceGuid.PcdConDevEnableAllDebugMSG   |FALSE

##############################################################################
#                   Common Wireless function
##############################################################################
   ## PCD to enable Wireless device FCC ID support, 2016 platform wouldn't support FCC ID.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessFCCIDSupport      |FALSE

   ## PCD for Wake on Bluetooth supported, drop on 2018 platform. Set to disable.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWoBluetoothSupport        |FALSE

##############################################################################
#                   Specific Wireless function
##############################################################################
   ## PCD to enable Wake on wlan support / LanWLan switching, Turn on if your system is AiO or DM or NB.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWoWLANSupport             |TRUE
   gEfiHpConDevPkgTokenSpaceGuid.PcdLanWlanAutoSwitchingSupport|TRUE

   # Follow Intel Dynamic Peak Gain matrix. Intel #559910, PPAG Mode Revision. 
   # Bit0: PPAG enable/disable in EU. Bit1: PPAG enable/disable in China. Bit31-2: Reserved
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpDynamicAntennaGainSupport |0x03

#!if (gHpModernStandbyPkgTokenSpaceGuid.PcdHpModernStandbySupport == TRUE)
   gEfiHpConDevPkgTokenSpaceGuid.PcdWoWLANSupport             |FALSE
#!endif

!if (gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessNotebookPlatform == TRUE)
   ## PCD to determine if system need to support ElectronicLabel, please need to enable this PCD and extend the e-label region size to 200KB.
   gHpElectronicLabelPkgTokenSpaceGuid.PcdElectronicLabelSupport       |TRUE

   ## PCD to enable Host Base MAC address, because function require pre-boot support, please also enable USB LAN boot.(If need.)
   gEfiHpConDevPkgTokenSpaceGuid.PcdHPHBMASupport             |TRUE

   gEfiHpConDevPkgTokenSpaceGuid.PcdHPHBMAOOBWOLSupport          |FALSE

   ## PCD to enable USB LAN dongle support
   gEfiHpConDevPkgTokenSpaceGuid.PcdUsbLanSupport                |TRUE  ## confirm with HP BIOS PM Luke Connery should enable it

   ## PCD for Realtek USB 8153 Legacy boot supported. (UEFI boot default enable on NB) Enable this PCD if platform have no on board NIC or Special request(VA).
   gEfiHpConDevPkgTokenSpaceGuid.PcdRTLUSBLanLegacyBootSupport|FALSE

   ## PCD to show "Lock wireless button" option in F10. Some platform didn't support hardware wireless button and internal keyboard, that should block the wireless btn support.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWirelessButtonSupport     |TRUE

   ## PCD to set to FALSE if your project didn't support WWAN device. (ALL OF SKU)
   gEfiHpConDevPkgTokenSpaceGuid.PcdWWANModuleSupport         |TRUE
   ## PCD to enable Pcie Wwan card support
   gEfiHpConDevPkgTokenSpaceGuid.PcdPcieWwanSupport           |TRUE
   ## PCD to enable UART interface GPS support
   gEfiHpConDevPkgTokenSpaceGuid.PcdUARTGpsSupport            |FALSE

   # Wifi SAR customization default table from Comm. team, default set to disable, enable by request. Please override use below PCD.
   gEfiHpConDevPkgTokenSpaceGuid.PcdWRDSWifiSAREnable         |TRUE

   # Realtek Wifi Static SAR Supported. Default Disable, enable by request.
   gEfiHpConDevPkgTokenSpaceGuid.PcdRTLStaticWifiSAREnable    |TRUE

   ## Wifi Dynamic SAR customization default table from Comm. team, default set to disable, enable by request. Please override use below PCD.
   ## Some platform use same BIOS on Supported/Unsupported Dyn BIOS SAR platform.
#   gEfiHpConDevPkgTokenSpaceGuid.PcdWifiDynamicSAREnable      |FALSE  #default enable. This is dynamic PCD, update it depend on platform.

   # Target NB 800 as the lead platform and for those platforms prior to 800 will be supported at OOC.
   gEfiHpConDevPkgTokenSpaceGuid.PcdLanWwanAutoSwitchingSupport|TRUE

   # Target on NB 800 and beyond platform. Didn't support on Non-MS + WOBT enable platform (DT and NB 400 not supported)
   gEfiHpConDevPkgTokenSpaceGuid.PcdBTErrorRecoveryEnable     |TRUE

!else
   ## PCD to determine if system need to support ElectronicLabel, please need to enable this PCD and extend the e-label region size to 200KB.
   gHpElectronicLabelPkgTokenSpaceGuid.PcdElectronicLabelSupport       |FALSE

   ## PCD to enable Host Base MAC address, because function require pre-boot support, please also enable USB LAN boot.(If need.)
   gEfiHpConDevPkgTokenSpaceGuid.PcdHPHBMASupport             |FALSE

   gEfiHpConDevPkgTokenSpaceGuid.PcdHPHBMAOOBWOLSupport       |FALSE

   ## PCD to enable USB LAN dongle support
   gEfiHpConDevPkgTokenSpaceGuid.PcdUsbLanSupport                |FALSE

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

   # Target NB 800 as the lead platform and for those platforms prior to 800 will be supported at OOC.
   gEfiHpConDevPkgTokenSpaceGuid.PcdLanWwanAutoSwitchingSupport|FALSE

   # Target on NB 800 and beyond platform. Didn't support on Non-MS + WOBT enable platform (DT and NB 400 not supported)
   gEfiHpConDevPkgTokenSpaceGuid.PcdBTErrorRecoveryEnable     |TRUE

   # Supported on Ultron
   gEfiHpConDevPkgTokenSpaceGuid.PcdHpIoTSupport |FALSE

!endif

################################################################################
#
# Connection Device Feature Parameter configuration
#
################################################################################
[PcdsFixedAtBuild]
  # For WLAN Card
#  gEfiHpConDevPkgTokenSpaceGuid.PcdWlanPcieBridgeDevNum|28
#  gEfiHpConDevPkgTokenSpaceGuid.PcdWlanPcieBridgeFunNum|3
  gEfiHpConDevPkgTokenSpaceGuid.PcdWlanPcieBridgeNum|4

  # Wlan Device GPIO handle
#  gEfiHpConDevPkgTokenSpaceGuid.PcdWLANTransmitOffGpioPin|17
#  gEfiHpConDevPkgTokenSpaceGuid.PcdWLANTransmitOffGpioPinGroup|3
#  gEfiHpConDevPkgTokenSpaceGuid.PcdWLANTransmitOffGpioActive|1

  gEfiHpConDevPkgTokenSpaceGuid.PcdCnviEnableGpioPin|0x080B0008 # GPIO_VER6_SOC_S_DRIVER_GPP_C8

  gEfiHpConDevPkgTokenSpaceGuid.PcdBluetoothGpioPin|0x08050003    # GPP_B3
  gEfiHpConDevPkgTokenSpaceGuid.PcdBluetoothGpioActive|1             # High Active

  # Wifi Dynamic SAR customization default table from Comm. team, default set to disable, enable by request. Please override use below PCD.
  gEfiHpConDevPkgTokenSpaceGuid.PcdEWRDWifiDynamicSAR        |FALSE
################################################################################
#
# Connection Device Dynamic default setting
#
################################################################################
[PcdsDynamicDefault]
  # Intel Wifi 6E Function 3 : Ultra High Band Support
  gEfiHpConDevPkgTokenSpaceGuid.PcdHpWifi6EUhb|1

################################################################################
#
# Connection Device Platform Definition
#
################################################################################
[Defines]


################################################################################
#
# Connection Device Platform specific setting
#
################################################################################
[PcdsFixedAtBuild]

  ## PCD for Indonesia New Band support, due to the schedule impact 400/600 G8 should disabled. 800G8 follow on should enable if DCR apply.
  gEfiHpConDevPkgTokenSpaceGuid.PcdHpIndonesiaNewBandSupport |TRUE

[PcdsFixedAtBuild.common]


[BuildOptions]
!if $(INTEL_PLATFORM) == TRUE
      DEFINE WLAN_PCIE_RP_PATH                       = /D WLAN_PCIE_RP_PATH="\_SB.PC00.RP05"
      DEFINE WLAN_PCIE_DEV_PATH                      = /D WLAN_PCIE_DEV_PATH="\_SB.PC00.RP05.PXSX"
!endif

  !if ($(AMD_PLATFORM) == TRUE)
     DEFINE WLAN_PCIE_RP_PATH                       = /D WLAN_PCIE_RP_PATH="\_SB.PC00.GPP2"
     DEFINE WLAN_PCIE_DEV_PATH                      = /D WLAN_PCIE_DEV_PATH="\_SB.PC00.GPP2.NCRD"
  !endif

!if gEfiHpConDevPkgTokenSpaceGuid.PcdLanWlanAutoSwitchingSupport == TRUE
   DEFINE DSC_LAN_WLAN_AUTO_SWITCHING_SUPPORT = /DLAN_WLAN_AUTO_SWITCHING_SUPPORT=1
!else
   DEFINE DSC_LAN_WLAN_AUTO_SWITCHING_SUPPORT =
!endif

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

  DEFINE CONDEV_ACPI_PATH = $(WLAN_PCIE_RP_PATH) $(WLAN_PCIE_DEV_PATH) $(DSC_LAN_WLAN_AUTO_SWITCHING_SUPPORT) $(DSC_LAN_WLAN_WWAN_AUTO_SWITCHING) $(DSC_HP_HBMA_OOB_WAKE_ON_LAN_SUPPORT) $(DSC_CONDEV_DEBUG_OPTION) $(BT_ERROR_RECOVERY)

