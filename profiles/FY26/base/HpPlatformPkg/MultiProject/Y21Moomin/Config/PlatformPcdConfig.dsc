#
# (c) Copyright 2015 - 2025 HP Development Company, L.P.
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
    #DEFINE PROJECT_DEBUG_LEVEL = 0x80080046  # DEBUG_ERROR | DEBUG_EVENT | DEBUG_WARN | DEBUG_LOAD
   DEFINE PROJECT_DEBUG_LEVEL = 0x80080006  # DEBUG_ERROR | DEBUG_EVENT | DEBUG_WARN | DEBUG_LOAD
   DEFINE DBG_SERIAL_PORT_BASE     = 0x3F8
   DEFINE SYSTEM_SIO_BASE_ADDRESS  = 0x260

   DEFINE PROJECT_SMBIOS_VERSION  = 0x0308  # SMBIOS 3.8
   DEFINE PROJECT_FAN_TABLE_COUNT = 6  # MULTI_FAN_TABLE_COUNTS
   DEFINE PROJECT_ACPI_OEM_TABLE_ID = 0x20202020204C5450  # PcdAcpiDefaultOemTableId, "PTL     "

   DEFINE HP_POST_CODE_TO_SERIAL_PORT_ENABLE = TRUE
!if $(FSP_DEBUG_IN_RELEASE_MODE) == TRUE
   DEFINE HP_POST_CODE_TO_SERIAL_PORT_ENABLE = TRUE
!endif

[PcdsDynamicHii.common.DEFAULT.STANDARD]
!if gCnvFeaturePkgTokenSpaceGuid.PcdCnvIntegratedSupport == 0x1
   gStructPcdTokenSpaceGuid.PcdCnvSetup.CnviBtInterface|0x2
!endif

   gStructPcdTokenSpaceGuid.PcdCpuSetup.EnableVsysCritical|0x2                                        # Vsys/Psys Critical                2;
   gStructPcdTokenSpaceGuid.PcdCpuSetup.VsysFullScale|0x5dc0                                          # Vsys/Psys Full Scale              24000;   // unit is 1mV
   gStructPcdTokenSpaceGuid.PcdCpuSetup.VsysCriticalThreshold|0x4268                                  # Vsys/Psys Critical Threshold      17000;   // unit is 1mV
   gStructPcdTokenSpaceGuid.PcdCpuSetup.PsysFullScale|0x35B60                                         # Vsys/Psys Full Scale              220000;  // unit is 1mV
   gStructPcdTokenSpaceGuid.PcdCpuSetup.PsysCriticalThreshold|0x27100                                 # Vsys/Psys Critical Threshold      160000;  // unit is 1mV
   gStructPcdTokenSpaceGuid.PcdCpuSetup.VsysAssertionDeglitchMantissa|0x1                             # Assertion Deglitch Mantissa       0x1;
   gStructPcdTokenSpaceGuid.PcdCpuSetup.VsysDeassertionDeglitchMantissa|0xd                           # De assertion Deglitch Mantissa    0xD;
   gStructPcdTokenSpaceGuid.PcdCpuSetup.VsysDeassertionDeglitchExponent|0x2                           # De assertion Deglitch Exponent    0x2;
   
   # Audio Speakers Enablement
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioHdaLinkEnable|0x0     # HDA Link
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioDmicLinkEnable[0]|0x0 # DMIC #0
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioDmicLinkEnable[1]|0x0 # DMIC #1
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioSndwLinkEnable[0]|0x0 # SNDW #0
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioSndwLinkEnable[1]|0x0 # SNDW #1
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioSndwLinkEnable[2]|0x0 # SNDW #2
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioSndwLinkEnable[3]|0x0 # SNDW #3
   gStructPcdTokenSpaceGuid.PcdSndwDevTopologyConfigurationVariable.SndwDevTopologyConfigurationNumber|0x0
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdaMicPrivacyHwModeDmic|0x0                                # DMIC
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdaMicPrivacyHwModeSoundWire0|0x0                          # SNDW #0
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdaMicPrivacyHwModeSoundWire1|0x0                          # SNDW #1
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdaMicPrivacyHwModeSoundWire2|0x0                          # SNDW #2
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdaMicPrivacyHwModeSoundWire3|0x0                          # SNDW #3
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdaMicPrivacyHwModeSoundWire4|0x0                          # SNDW #4
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdaMicPrivacyMode|0x0                                      # Microphone Privacy Mode
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioFeature[0]|0x1                                      # WoV (Wake on Voice)
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioFeature[1]|0x1                                      # Bluetooth Sideband
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioFeature[2]|0x0                                      # Codec based VAD
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioFeature[5]|0x1                                      # BT Intel HFP
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioFeature[6]|0x1                                      # BT Intel A2DP
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioFeature[9]|0x1                                      # BT Intel Low Energy
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioFeature[10]|0x1                                     # ACX/SDCA
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioFeature[11]|0x1                                     # ACX/SDCA speaker aggregation
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioSndwMultilaneEnable[0]|0x0                          # SNDW #2 Multilane
   gStructPcdTokenSpaceGuid.PcdPchSetup.PchHdAudioSndwMultilaneEnable[1]|0x2                          # SNDW #3 Multilane
   gStructPcdTokenSpaceGuid.PcdNhltEndpointsTableConfigurationVariable.NhltDmicMonoEnabled|0x0        # Dmic Mono
   gStructPcdTokenSpaceGuid.PcdNhltEndpointsTableConfigurationVariable.NhltDmicStereoEnabled|0x0      # Dmic Stereo
   gStructPcdTokenSpaceGuid.PcdNhltEndpointsTableConfigurationVariable.NhltDmicQuadEnabled|0x0        # Dmic Quad

   gStructPcdTokenSpaceGuid.PcdSetup.LchSupport|0x0                                                   # LCH Support
   gStructPcdTokenSpaceGuid.PcdPchSetup.ThcAssignment[0]|0x0                                          # THC Port Configuration
   gStructPcdTokenSpaceGuid.PcdPchSetup.ThcAssignment[1]|0x0                                          # THC Port Configuration
   gStructPcdTokenSpaceGuid.PcdPchSetup.ThcHidI2cDeviceAddress[0]|0x0                                 # HIDI2C Device address
   gStructPcdTokenSpaceGuid.PcdPchSetup.ThcWakeOnTouch[0]|0x0

# Mipi Camera Config
!if gMipiCamFeaturePkgTokenSpaceGuid.PcdMipiCamFeatureEnable == TRUE
   # ControlLogic 1 ~ 5 and Link 1 ~ 5  Disable
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic1|0x0
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic2|0x0                                # Control Logic 2
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic3|0x0                                # Control Logic 3
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic4|0x0                                # Control Logic 4
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic5|0x0                                # Control Logic 5
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link1|0x0
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link2|0x0                                        # Camera2
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link3|0x0                                        # Camera3
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link4|0x0                                        # Camera4
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link5|0x0                                        # Camera5

   # ControlLogic 0 : Discrete control on front Camera
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0|0x1                                # Control Logic 1
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_Type|0x5                           # Control Logic Type
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_CrdVersion|0x20                    # CRD Version
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_InputClock|0x0                     # Input Clock
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_PchClockSource|0x0                 # PCH Clock Source
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_Pld|0x29                           # PMIC Flash Panel
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioPinsEnabled|0x3                # Number of GPIO Pins

   # PLED_EN # READY: GPP_C15
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioGroupPadNumber[0]|0xF          # Group Pad Number
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioGroupNumber[0]|0x1             # Group Number
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioComNumber[0]|0x0               # Com number
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioFunction[0]|0x13                # Function
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioActiveValue[0]|0x1             # Active Value
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioInitialValue[0]|0x0            # Initial Value

   # PLED_EN # HDMI_DETECT: GPP_C5
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioGroupPadNumber[1]|0x5          # Group Pad Number
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioGroupNumber[1]|0x1             # Group Number
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioComNumber[1]|0x0               # Com number
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioFunction[1]|0x14                # Function
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioActiveValue[1]|0x1             # Active Value
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioInitialValue[1]|0x0            # Initial Value

   # Power Enable # RESET: GPP_E10
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioGroupPadNumber[2]|0xA          # Group Pad Number
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioGroupNumber[2]|0x1             # Group Number
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioComNumber[2]|0x1               # Com number
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioFunction[2]|0x0               # Function
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioActiveValue[2]|0x1             # Active Value
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_ControlLogic0_GpioInitialValue[2]|0x0            # Initial Value


   # MipiCam_Link 0 : Front Camera
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0|0x1                                        # Camera1
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_ControlLogic|0x0                # GPIO control
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_I2cChannel|0x2                             # I2C Channel
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_LaneUsed|0x2                    # LaneUsed
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_LinkUsed|0x0                    # MIPI port
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_CameraPhysicalLocation|0x69                # Camera position
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_I2cDevicesEnabled|0x1                      # Number of I2C Components
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_I2cDeviceType[0]|0x0                       # Device Type                      # Device Type
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_I2cAddress[0]|0x4F                         # I2C Address                         # I2C Address
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_CrdVersion|0x20                 # CRD Version
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_EepromType|0x0                 # EEPROM Type
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_VcmType|0x0                     # VCM Type
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_PhyConfiguration|0x1            # PhyConfiguration
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_Mclk|0x124f800                  # MCLK
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_FlashSupport|0x2                # Flash Support
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_PrivacyLed|0x0                  # Privacy LED
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_Degree|0x0                      # Rotation
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_PmicPosition|0x0                # PMIC Position
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_DriverData_VoltageRail|0x0                 # Voltage Rail
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_FlashDriverSelection|0x0                   # Flash Driver Selection
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_SensorModel|0x18                            # Sensor Model
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_ModuleName|L"CJFKE26"                      # Camera module name
   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Link0_UserHid|L"INTC1124"                        # Custom HID
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.Audio_Link1_UserHid|L"INTC1125"

   # Flash1 specific
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_I2cChannel|0x3                            # I2C Channel
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_I2cAddress|0x63                           # I2C Address
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_Model|0x0                                 # Flash Model
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_Mode|0x3                                  # Flash Mode
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_GpioActiveValue|0x0                       # Active Value
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_GpioComNumber|0x0                         # Com number
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_GpioGroupNumber|0x0                       # Group Number
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_GpioGroupPadNumber|0x0                    # Group Pad Number
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_GpioInitialValue|0x0                      # Initial Value
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_GpioSupport|0x0                           # Flash Trigger Gpio Support
#   gStructPcdTokenSpaceGuid.PcdMipiCamConfig.MipiCam_Flash1_ModuleName|L"Lm3643"                      # Camera module name

!endif



[PcdsFeatureFlag]

   #
   # HpPlatformPkg, Edk2Platforms, HpCore
   #
   # PCD for Memory Speed Throttle Down support.
   #  BCR#195650 - Not support memory 2DPC 2400Mhz configs, they must throttle down to 2133 Mhz.
   #  For Vaughn and Affleck, BIOS need to check SODIMMs configuration to throttle down
   #  memory speed form 2400Mhz to 2133Mhz if 2DPC be detected.
   gEfiHpPlatformPkgTokenSpaceGuid.MemorySpeedThrottleDownSupport|FALSE

   ## Volume Down hotkey support PCD
   gEfiHpHotkeyPubIntPkgTokenSpaceGuid.PcdHotkeyVolumeDownSupport          |FALSE

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

   # PCD to determine if platform supports Mixed DIMM Alert.
   gEfiHpPlatformPkgTokenSpaceGuid.PcdMixedDimmAlertSupport|TRUE

   gEfiHpPlatformPkgTokenSpaceGuid.TiPdRedriverWorkaroundSupport|TRUE

[PcdsFixedAtBuild]

   #
   # MeteorLakePlatSamplePkg
   #
   gPlatformModuleTokenSpaceGuid.PcdUserAuthenticationEnable|FALSE
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

   gPlatformModuleTokenSpaceGuid.PcdLzmaEnable|TRUE
   gPlatformModuleTokenSpaceGuid.PcdDxeCompressEnable|TRUE

   gPlatformModuleTokenSpaceGuid.PcdMemoryTestEnable|FALSE
   gPlatformModuleTokenSpaceGuid.PcdTpmEnable|TRUE
   #TODO: Disable for DB0
   gPlatformModuleTokenSpaceGuid.PcdOpalPasswordEnable|FALSE
   gCnvFeaturePkgTokenSpaceGuid.PcdCnvAcpiTables|FALSE
   gCnvFeaturePkgTokenSpaceGuid.PcdCnvFeatureEnable|TRUE
   #
   # Determine ACPI reserved memory under 4G
   #
!if $(TARGET) == DEBUG
   gPlatformModuleTokenSpaceGuid.PcdS3AcpiReservedMemorySize|0x3000000
!else
   gPlatformModuleTokenSpaceGuid.PcdS3AcpiReservedMemorySize|0x3000000
!endif

!if $(TARGET) == DEBUG
   gPlatformModuleTokenSpaceGuid.PcdSinitAcmBinEnable|FALSE      # Reduce DXE FV size.
!else
   gPlatformModuleTokenSpaceGuid.PcdSinitAcmBinEnable|TRUE
!endif

   ## HpPlatformPkg

   #
   # I2C Touch Panel
   # TOUCH_PWR_EN
   #
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchPanelPowerGpio|0xFFFFFFFF     #No Connection
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchPanelPowerActive|1            #high active
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchPanelInterruptActive|1        #high active

   #Touch Panel LTR Setting
   gEfiHpPlatformPkgTokenSpaceGuid.PcdTouchpanelLtrIdle|0x0001
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

   ## PCD to enable HP PostCode Debug by serial port
   gEfiHpFeatureMiscPubIntPkgTokenSpaceGuid.PcdHpPostCodeToSerialPortEnable|FALSE

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

   # PCDs for Touch pad GPP GPP_B20
   # I2C touch pad interrupt GPIO: Group B pin 20
   gHpHumanInterfaceDevicesPubIntPkgTokenSpaceGuid.PcdI2CTouchPadIntGpio|0xFFFFFFFF # unsupport

   gEfiHpDmarTokenSpaceGuid.PcdDmarFeatureSupport|TRUE
   gEfiHpDmarTokenSpaceGuid.PcdDmarOptionDefaultValue|TRUE
   gEfiHpDmarTokenSpaceGuid.PcdHpDmarEnableAllDebugMSG|FALSE

   # PCD to enable/disable DCR280518 for enhanced pre-boot dma protection feature.
   gEfiHpDmarTokenSpaceGuid.PcdEnhancedPreBootDmarSupport|TRUE

   #
   # PcdsFixedAtBuild for HpStoragePkg
   #
   # Update StorageRtd3Support valuse to 0/1/2 in ADL.2347
   ## ADL - PCD to configure HP Storage RTD3 support. 0: D3 Disable, 1:RTD3 hot (default), 2: RTD3 cold
   gEfiHpStoragePkgTokenSpaceGuid.PcdStorageRtd3Support|1

   # Add ARK/Pelori USB Mouse into PcdUsbMsExceptionList for skip Absolute/Related mode byte
   gEfiMdeModulePkgTokenSpaceGuid.PcdUsbMsExceptionList|{CODE(
   {
   {0x1A86, 0xE129},
   })}

   # Use GPP_V1 as ACPRESENT GPIO pin and its active level is high.
   # ADP_PRES_OUT
   #
   gEfiHpPlatformPkgTokenSpaceGuid.PcdAcPresentGpio|0x001A0001 # GPP_V1
   gEfiHpPlatformPkgTokenSpaceGuid.PcdAcPresentGpioActive|1 # High Active
   gEfiMdePkgTokenSpaceGuid.PcdDebugPropertyMask|0x0F

   #Set power on from keyboard port number USB_P2 on connector J9, USB_P3 on connector J9
   gHpIntelChipsetPkgTokenSpaceGuid.PcdKeyboardPowerOnPort|{ 0x05, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF }

!if ($(NOTEBOOK_PLATFORM) == TRUE) AND ($(CRB_BOOT_SUPPORT) == FALSE)
   #
   # PcdSerialPortEnable enable use for output COM port via SerialPortWrite (), NB/mWS didn't have such legacy COM serial device.
   # For override HpIntel\HpIntelChipsetPkg\HpIntelChipsetPkgOverrideIntelPcd.dsc init PcdSerialPortEnable as TRUE.
   #
   gPlatformModuleTokenSpaceGuid.PcdSerialPortEnable|FALSE
!endif

   #
   # PCD for Serial PortA Present GPIO Pin
   # Set PCD 0xFFFFFFFF for not support Serial PortA Present GPIO Pin
   #
   gEfiHpPlatformPkgTokenSpaceGuid.PcdSerialPortAPresentGpioPin|0x001A1098
   gEfiHpPlatformPkgTokenSpaceGuid.PcdSerialPortAPresentGpioActive|0

[PcdsFixedAtBuild.IA32]
   gIntelSiliconPkgTokenSpaceGuid.PcdVTdPeiDmaBufferSize|0x02400000

[PcdsFixedAtBuild.X64]
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

   gEfiHpBusSupportPubIntPkgTokenSpaceGuid.PcdSkipUsbOnFastBoot|FALSE

   gNhltFeaturePkgTokenSpaceGuid.NhltI2sLontiumI2s0     |FALSE
   gNhltFeaturePkgTokenSpaceGuid.NhltI2sLontiumI2s1     |FALSE
   gNhltFeaturePkgTokenSpaceGuid.NhltI2sLontiumI2s2     |FALSE
   gNhltFeaturePkgTokenSpaceGuid.NhltDmicStereoVpEnabled|TRUE
   gNhltFeaturePkgTokenSpaceGuid.NhltBluetoothEnabled|0x2

[PcdsDynamicExDefault.common.DEFAULT]
   gEfiHpTpmPubIntPkgTokenSpaceGuid.PcdTpmAllowDisable|L"TXT"

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

[PcdsDynamicExVpd.common.SkuIdPtlUHDdr5Rvp4]
   gBoardModuleTokenSpaceGuid.VpdPcdBoardGpioTable| * |{CODE({
   // {GpioPad                 , {PadMode             , HostOwn             , Direction       , OutputState       , InterruptConfig               , ResetConfig         , TerminationConfig, LockConfig                 , LockTx       }}
//   {GPIOV2_PTL_PCD_XXGPP_A_0,  {}}, // ESPI_IO0
//   {GPIOV2_PTL_PCD_XXGPP_A_1,  {}}, // ESPI_IO1
//   {GPIOV2_PTL_PCD_XXGPP_A_2,  {}}, // ESPI_IO2
//   {GPIOV2_PTL_PCD_XXGPP_A_3,  {}}, // ESPI_IO3
//   {GPIOV2_PTL_PCD_XXGPP_A_4,  {}}, // ESPI_CS0
//   {GPIOV2_PTL_PCD_XXGPP_A_5,  {}}, // ESPI_CLK
//   {GPIOV2_PTL_PCD_XXGPP_A_6,  {}}, // ESPI_RESET
//   {GPIOV2_PTL_PCD_XXGPP_A_7,  {}}, // NC
//   {GPIOV2_PTL_PCD_XXGPP_A_8,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_A_9,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_A_10, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_A_14, {}}, // NC
//   {GPIOV2_PTL_PCD_XXGPP_A_15, {}}, // GPP_A15
   {GPIOV2_PTL_PCD_XXGPP_A_11, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                    GpioV2ResetHost,      GpioV2TermNone                  }}, // HPGP_WLAN_PLDR_RST
   {GPIOV2_PTL_PCD_XXGPP_A_12, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirInInv,  GpioV2StateDefault, GpioV2IntEdge|GpioV2IntSci,      GpioV2ResetHostDeep,  GpioV2TermDefault               }}, // HPGP_WLAN_WAKE
   {GPIOV2_PTL_PCD_XXGPP_A_13, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                    GpioV2ResetHost,      GpioV2TermNone                  }}, // HPGP_FLEXIO_SMB_SEL
   {GPIOV2_PTL_PCD_XXGPP_A_16, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                    GpioV2ResetHost,      GpioV2TermNone                  }}, // HPGP_BT_DISABLE
   {GPIOV2_PTL_PCD_XXGPP_A_17, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                    GpioV2ResetHost,      GpioV2TermNone                  }}, // HPGP_WLAN_DISABLE

//   {GPIOV2_PTL_PCD_XXGPP_B_0,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SML4_CLK NOTE: USE USBC_SML* FOR COMMUNICATING WITH USB-C* PD CONTROLLER
//   {GPIOV2_PTL_PCD_XXGPP_B_1,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SML4_DAT NOTE: USE USBC_SML* FOR COMMUNICATING WITH USB-C* PD CONTROLLER
//   {GPIOV2_PTL_PCD_XXGPP_B_2,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_B_3,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_B_12, {}}, // SLP_S0
//   {GPIOV2_PTL_PCD_XXGPP_B_13, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // PLTRST
//   {GPIOV2_PTL_PCD_XXGPP_B_15, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // CPU_USB_OC3
//   {GPIOV2_PTL_PCD_XXGPP_B_17, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_B_18, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_B_19, {GPIO_UNUSED}},
   {GPIOV2_PTL_PCD_XXGPP_B_4,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,       GpioV2TermNone                  }}, // HPGP_Chipset_strapping
   {GPIOV2_PTL_PCD_XXGPP_B_5,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,       GpioV2TermNone                  }}, // HPGP_GFX_ID0
   {GPIOV2_PTL_PCD_XXGPP_B_6,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,       GpioV2TermNone                  }}, // HPGP_GFX_ID1
   {GPIOV2_PTL_PCD_XXGPP_B_7,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,       GpioV2TermNone                  }}, // HPGP_GFX_ID2
   {GPIOV2_PTL_PCD_XXGPP_B_8,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,       GpioV2TermNone                  }}, // GC6_FB_EN
   {GPIOV2_PTL_PCD_XXGPP_B_9,  {GpioV2PadModeNative2, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,       GpioV2TermDefault               }}, // FLEX1_DP_HPD_Q
   {GPIOV2_PTL_PCD_XXGPP_B_10, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHostDeep,   GpioV2TermNone                  }}, // HPGP_PCIE_SSD2_EN
   {GPIOV2_PTL_PCD_XXGPP_B_11, {GpioV2PadModeNative2, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,       GpioV2TermDefault               }}, // DP2_HPD_Q
   {GPIOV2_PTL_PCD_XXGPP_B_14, {GpioV2PadModeNative2, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,       GpioV2TermDefault               }}, // HDMI_HPD_CON
   {GPIOV2_PTL_PCD_XXGPP_B_16, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHostDeep,   GpioV2TermNone                  }}, // HPGP_PCIE_SSD1_EN
   {GPIOV2_PTL_PCD_XXGPP_B_20, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHost,       GpioV2TermNone                  }}, // HPGP_FLEX1_RST
   {GPIOV2_PTL_PCD_XXGPP_B_21, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateLow,     GpioV2IntDis,                   GpioV2ResetHostDeep,   GpioV2TermNone                  }}, // HPGP_TBT_FRC_PWR
   {GPIOV2_PTL_PCD_XXGPP_B_22, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirInInv,  GpioV2StateDefault, GpioV2IntBothEdge|GpioV2IntSci, GpioV2ResetHostDeep,   GpioV2TermNone,    GpioV2Unlock }}, // DGPU_INT
   {GPIOV2_PTL_PCD_XXGPP_B_23, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,       GpioV2TermNone                  }}, // HPGP_Chipset_strapping
   {GPIOV2_PTL_PCD_XXGPP_B_24, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirInInv,  GpioV2StateDefault, GpioV2IntEdge|GpioV2IntSci,     GpioV2ResetHostDeep,   GpioV2TermDefault               }}, // HPGP_FLEX1_WAKE
   {GPIOV2_PTL_PCD_XXGPP_B_25, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirInInv,  GpioV2StateDefault, GpioV2IntEdge|GpioV2IntSci,     GpioV2ResetHostDeep,   GpioV2TermDefault               }}, // HPGP_FLEX2_WAKE

//   {GPIOV2_PTL_PCD_XXGPP_C_0,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SMB_CLK_RESUME
//   {GPIOV2_PTL_PCD_XXGPP_C_1,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SMB_DAT_RESUME
//   {GPIOV2_PTL_PCD_XXGPP_C_3,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SML0_CLK
//   {GPIOV2_PTL_PCD_XXGPP_C_4,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SML0_DAT
//   {GPIOV2_PTL_PCD_XXGPP_C_5,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,       GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,  GpioV2TermNone               }}, // HPGP_CSI_HDMI_DET
//   {GPIOV2_PTL_PCD_XXGPP_C_10, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // PCIE_CLKREQ_SSD
//   {GPIOV2_PTL_PCD_XXGPP_C_11, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // PCIE_CLKREQ_FLEX
//   {GPIOV2_PTL_PCD_XXGPP_C_12, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // PCIE_CLKREQ_LAN
//   {GPIOV2_PTL_PCD_XXGPP_C_14, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // PCIE_CLKREQ_MIPI
//   {GPIOV2_PTL_PCD_XXGPP_C_15, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,       GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,  GpioV2TermNone               }}, // HPGP_CSI_INT
//   {GPIOV2_PTL_PCD_XXGPP_C_16, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // DPP0_CLK_TBT_LSX0_TXD
//   {GPIOV2_PTL_PCD_XXGPP_C_17, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // DPP0_DATA_TBT_LSX0_RXD
//   {GPIOV2_PTL_PCD_XXGPP_C_18, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // TBT_LSX1_TXD
//   {GPIOV2_PTL_PCD_XXGPP_C_19, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // TBT_LSX1_RXD
//   {GPIOV2_PTL_PCD_XXGPP_C_20, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // DDP2_SCL
//   {GPIOV2_PTL_PCD_XXGPP_C_21, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // DDP2_SDA
//   {GPIOV2_PTL_PCD_XXGPP_C_22, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // DDP3_SCL
//   {GPIOV2_PTL_PCD_XXGPP_C_23, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // DDP3_SDA
   {GPIOV2_PTL_PCD_XXGPP_C_2,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,       GpioV2TermNone                  }}, // SMB_ALT
   {GPIOV2_PTL_PCD_XXGPP_C_6,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_C_7,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_C_8,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_C_9,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,       GpioV2TermDefault               }}, // GFX_PEG_CLKREQ
   {GPIOV2_PTL_PCD_XXGPP_C_13, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,       GpioV2TermDefault               }}, // PCIE_CLKREQ_WLAN

//   {GPIOV2_PTL_PCD_XXGPP_D_0,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_D_2,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_D_4,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_D_9,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_D_10, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // HDA_BCLK
//   {GPIOV2_PTL_PCD_XXGPP_D_11, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // HDA_SYNC
//   {GPIOV2_PTL_PCD_XXGPP_D_12, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // HDA_SDOUT
//   {GPIOV2_PTL_PCD_XXGPP_D_13, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // HDA_SDIN
//   {GPIOV2_PTL_PCD_XXGPP_D_18, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // PCIE_CLKREQ_SSD2
//   {GPIOV2_PTL_PCD_XXGPP_D_21, {GPIO_UNUSED}},
   {GPIOV2_PTL_PCD_XXGPP_D_1,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_D_3,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_NMI
   {GPIOV2_PTL_PCD_XXGPP_D_5,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // FLEX2_ID1
   {GPIOV2_PTL_PCD_XXGPP_D_6,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // FLEX2_ID0
   {GPIOV2_PTL_PCD_XXGPP_D_7,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // FLEX2_ID3
   {GPIOV2_PTL_PCD_XXGPP_D_8,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // FLEX2_ID2
   {GPIOV2_PTL_PCD_XXGPP_D_14, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_COINBATT_DET
   {GPIOV2_PTL_PCD_XXGPP_D_15, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntLevel | GpioV2IntApic, GpioV2ResetHostDeep,    GpioV2TermNone,GpioV2Unlock,GpioV2Unlock }}, // SPI_TPM_PIRQ_1V8
   {GPIOV2_PTL_PCD_XXGPP_D_16, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,        GpioV2TermDefault              }}, // HDA_RST
   {GPIOV2_PTL_PCD_XXGPP_D_17, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_D_19, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHostDeep,    GpioV2TermNone                 }}, // HPGP_PCIE_SSD2_RST
   {GPIOV2_PTL_PCD_XXGPP_D_20, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }},  // HPGP_GFX_RST
   {GPIOV2_PTL_PCD_XXGPP_D_22, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_D_23, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_MIPI_DET
   {GPIOV2_PTL_PCD_XXGPP_D_24, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_REAR_SERIAL_DET
   {GPIOV2_PTL_PCD_XXGPP_D_25, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_POWER_CUT

//   {GPIOV2_PTL_PCD_XXGPP_E_0,  {}}, // NC
//   {GPIOV2_PTL_PCD_XXGPP_E_2,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_E_4,  {}}, // NC
//   {GPIOV2_PTL_PCD_XXGPP_E_5,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_E_9,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                              }}, // CPU_USB_OC0
//   {GPIOV2_PTL_PCD_XXGPP_E_10, {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirOut,  GpioV2StateHigh,    GpioV2IntDis,     GpioV2ResetHost, GpioV2TermNone                                 }}, // HPGP_CSI_RST
//   {GPIOV2_PTL_PCD_XXGPP_E_21, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                              }}, // PMCALERT
//   {GPIOV2_PTL_PCD_XXGPP_E_22, {GPIO_UNUSED}},
   {GPIOV2_PTL_PCD_XXGPP_E_1,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,        GpioV2TermNone                 }}, // DGPU_EVENT
   {GPIOV2_PTL_PCD_XXGPP_E_3,  {GpioV2PadModeGpio,    GpioV2HostOwnAcpi,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHostDeep,    GpioV2TermNone                 }}, // HPGP_PCIE_SSD1_RST
   {GPIOV2_PTL_PCD_XXGPP_E_6,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // GPP_E06 (HPGP_Chipset_strapping)
   {GPIOV2_PTL_PCD_XXGPP_E_7,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,        GpioV2TermDefault              }}, // DDPA_SCL
   {GPIOV2_PTL_PCD_XXGPP_E_8,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,        GpioV2TermDefault              }}, // DDPA_SDA
   {GPIOV2_PTL_PCD_XXGPP_E_11, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateLow,     GpioV2IntDis,                   GpioV2ResetResume,      GpioV2TermNone                 }}, // HPGP_IMON_65W
   {GPIOV2_PTL_PCD_XXGPP_E_12, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateLow,     GpioV2IntDis,                   GpioV2ResetResume,      GpioV2TermNone                 }}, // HPGP_IMON_90W
   {GPIOV2_PTL_PCD_XXGPP_E_13, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateLow,     GpioV2IntDis,                   GpioV2ResetResume,      GpioV2TermNone                 }}, // HPGP_IMON_100W
   {GPIOV2_PTL_PCD_XXGPP_E_14, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateLow,     GpioV2IntDis,                   GpioV2ResetResume,      GpioV2TermNone                 }}, // HPGP_IMON_120W
   {GPIOV2_PTL_PCD_XXGPP_E_15, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateLow,     GpioV2IntDis,                   GpioV2ResetResume,      GpioV2TermNone                 }}, // HPGP_IMON_150W
   {GPIOV2_PTL_PCD_XXGPP_E_16, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateLow,     GpioV2IntDis,                   GpioV2ResetResume,      GpioV2TermNone                 }}, // HPGP_IMON_180W
   {GPIOV2_PTL_PCD_XXGPP_E_17, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateLow,     GpioV2IntDis,                   GpioV2ResetResume,      GpioV2TermNone                 }}, // HPGP_IMON_Reserved
   {GPIOV2_PTL_PCD_XXGPP_E_18, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateLow,     GpioV2IntDis,                   GpioV2ResetResume,      GpioV2TermNone                 }}, // HPGP_IMON_230W
   {GPIOV2_PTL_PCD_XXGPP_E_19, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_GFX_SEL (DISABLE)
   {GPIOV2_PTL_PCD_XXGPP_E_20, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,        GpioV2TermNone                 }}, // DGPU_PWROK

//   {GPIOV2_PTL_PCD_XXGPP_F_0,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // CNV_BRI_DT
//   {GPIOV2_PTL_PCD_XXGPP_F_1,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // CNV_RGI_RSP
//   {GPIOV2_PTL_PCD_XXGPP_F_2,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // CNV_RGI_DT
//   {GPIOV2_PTL_PCD_XXGPP_F_3,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // CNV_BRI_RSP
//   {GPIOV2_PTL_PCD_XXGPP_F_4,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // CNV_RF_RESET
//   {GPIOV2_PTL_PCD_XXGPP_F_5,  {GpioV2PadModeNative3, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // MODEN_CLKREQ
//   {GPIOV2_PTL_PCD_XXGPP_F_6,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_F_7,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_F_8,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_F_9,  {GPIO_UNUSED}}, // SX_EXIT_HOLDOFF
//   {GPIOV2_PTL_PCD_XXGPP_F_12, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_F_13, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_F_16, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_F_17, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_F_18, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_F_21, {GPIO_UNUSED}}, // NC
//   {GPIOV2_PTL_PCD_XXGPP_F_22, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_F_23, {GPIO_UNUSED}},
   {GPIOV2_PTL_PCD_XXGPP_F_10, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_GFX_PWEREN
   {GPIOV2_PTL_PCD_XXGPP_F_11, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_SPKR_DET
   {GPIOV2_PTL_PCD_XXGPP_F_14, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_LEGACYIO_DET
   {GPIOV2_PTL_PCD_XXGPP_F_15, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_THEM_DET
   {GPIOV2_PTL_PCD_XXGPP_F_19, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_F_20, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_CSI_WAKE_CPU

//   {GPIOV2_PTL_PCD_XXGPP_H_3,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_4,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // I2C2_DAT
//   {GPIOV2_PTL_PCD_XXGPP_H_5,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // I2C2_CLK
//   {GPIOV2_PTL_PCD_XXGPP_H_6,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_7,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_8,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_9,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_10, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_11, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_12, {GPIO_UNUSED}}, // NC
//   {GPIOV2_PTL_PCD_XXGPP_H_13, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_14, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_15, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_16, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_17, {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_H_18, {GPIO_UNUSED}}, // NC
//   {GPIOV2_PTL_PCD_XXGPP_H_20, {GPIO_UNUSED}},
   {GPIOV2_PTL_PCD_XXGPP_H_0,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_Chipset_strapping
   {GPIOV2_PTL_PCD_XXGPP_H_1,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_Chipset_strapping
   {GPIOV2_PTL_PCD_XXGPP_H_2,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirIn,     GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_Chipset_strapping
   {GPIOV2_PTL_PCD_XXGPP_H_17, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_H_19, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirOut,    GpioV2StateHigh,    GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // HPGP_QG_USB_EN
   {GPIOV2_PTL_PCD_XXGPP_H_21, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_H_22, {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE

// P26 MIPI
   {GPIOV2_PTL_PCD_XXGPP_S_0,  {GpioV2PadModeNative6, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,        GpioV2TermDefault              }}, // I2S1_TXD
   {GPIOV2_PTL_PCD_XXGPP_S_1,  {GpioV2PadModeNative6, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,        GpioV2TermDefault              }}, // I2S1_RXD
   {GPIOV2_PTL_PCD_XXGPP_S_2,  {GpioV2PadModeNative6, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,        GpioV2TermDefault              }}, // I2S1_SCLK
   {GPIOV2_PTL_PCD_XXGPP_S_3,  {GpioV2PadModeNative6, GpioV2HostOwnDefault, GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDefault,               GpioV2ResetHost,        GpioV2TermDefault              }}, // I2S1_SFRM
   {GPIOV2_PTL_PCD_XXGPP_S_4,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_S_5,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_S_6,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE
   {GPIOV2_PTL_PCD_XXGPP_S_7,  {GpioV2PadModeGpio,    GpioV2HostOwnGpio,    GpioV2DirNone,   GpioV2StateDefault, GpioV2IntDis,                   GpioV2ResetHost,        GpioV2TermNone                 }}, // DISABLE

//   {GPIOV2_PTL_PCD_XXGPP_V_0,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // BATLOW
//   {GPIOV2_PTL_PCD_XXGPP_V_1,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // ACPRESENT
//   {GPIOV2_PTL_PCD_XXGPP_V_2,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // LAN_WAKE
//   {GPIOV2_PTL_PCD_XXGPP_V_3,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SIO_PWBTN_OUT
//   {GPIOV2_PTL_PCD_XXGPP_V_4,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SLP_S3
//   {GPIOV2_PTL_PCD_XXGPP_V_5,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SLP_S4
//   {GPIOV2_PTL_PCD_XXGPP_V_6,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SLP_A
//   {GPIOV2_PTL_PCD_XXGPP_V_7,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SUSCLK_SIO
//   {GPIOV2_PTL_PCD_XXGPP_V_8,  {GPIO_UNUSED}},
//   {GPIOV2_PTL_PCD_XXGPP_V_9,  {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SLP_S5
//   {GPIOV2_PTL_PCD_XXGPP_V_10, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // LAN_DISABLE
//   {GPIOV2_PTL_PCD_XXGPP_V_11, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // SLP_LAN
//   {GPIOV2_PTL_PCD_XXGPP_V_12, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // PCIE_WAKE
//   {GPIOV2_PTL_PCD_XXGPP_V_13, {GPIO_UNUSED}}, // NC
//   {GPIOV2_PTL_PCD_XXGPP_V_14, {GPIO_UNUSED}}, // NC
//   {GPIOV2_PTL_PCD_XXGPP_V_15, {GPIO_UNUSED}}, // NC
//   {GPIOV2_PTL_PCD_XXGPP_V_16, {GpioV2PadModeNative1, GpioV2HostOwnDefault, GpioV2DirNone, GpioV2StateDefault, GpioV2IntDefault, GpioV2ResetHost, GpioV2TermDefault                               }}, // VCCST_EN
//   {GPIOV2_PTL_PCD_XXGPP_V_17, {GPIO_UNUSED}}, // NC
  {0x0}  // terminator
   })}

   gBoardModuleTokenSpaceGuid.VpdPcdBoardGpioTablePreMem|*|{CODE({
    //
    // TCSS
    //
    {GPIOV2_PTL_PCD_XXGPP_D_1,  {GpioV2PadModeGpio, GpioV2HostOwnAcpi, GpioV2DirOut,  GpioV2StateHigh,   GpioV2IntDis,  GpioV2ResetHostDeep,  GpioV2TermDefault}}, // MOD_TCSS1_TYP_A_VBUS_EN
    {GPIOV2_PTL_PCD_XXGPP_F_11, {GpioV2PadModeGpio, GpioV2HostOwnAcpi, GpioV2DirOut,  GpioV2StateHigh,   GpioV2IntDis,  GpioV2ResetHostDeep,  GpioV2TermDefault}}, // MOD_TCSS2_TYP_A_VBUS_EN
    //
    // GFX_ID0_2
    //
    {GPIOV2_PTL_PCD_XXGPP_B_5,  {GpioV2PadModeGpio, GpioV2HostOwnGpio, GpioV2DirIn,   GpioV2StateDefault, GpioV2IntDis, GpioV2ResetHost,  GpioV2TermNone}},  // HPGP_GFX_ID0
    {GPIOV2_PTL_PCD_XXGPP_B_6,  {GpioV2PadModeGpio, GpioV2HostOwnGpio, GpioV2DirIn,   GpioV2StateDefault, GpioV2IntDis, GpioV2ResetHost,  GpioV2TermNone}},  // HPGP_GFX_ID1
    {GPIOV2_PTL_PCD_XXGPP_B_7,  {GpioV2PadModeGpio, GpioV2HostOwnGpio, GpioV2DirIn,   GpioV2StateDefault, GpioV2IntDis, GpioV2ResetHost,  GpioV2TermNone}},  // HPGP_GFX_ID2
    {0x0}  // terminator
   })}