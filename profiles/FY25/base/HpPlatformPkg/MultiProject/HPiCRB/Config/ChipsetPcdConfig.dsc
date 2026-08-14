#
# (c) Copyright 2015 - 2024 HP Development Company, L.P.
# This software and associated documentation (if any) is furnished under a license and may only be used or
# copied in accordance with the terms of the license. Except as permitted by such license, no part of this
# software or documentation may be reproduced, stored in a retrieval system, or transmitted in any form or
# by any means without the express written consent of HP Development Company.
#
# File Name: ChipsetPcdConfig.dsc
#
# Abstract: N/A
#
[Defines]
  DEFINE PLATFORM_SKUID   = SkuIdMtlSUDimm2DEvcrbFab2|SkuIdMtlSUDimm2DEvcrb

   #
   # Provide a white list to control DGR IO port access policy (DENY or ALLOW) in SMM mode after EndOfDxe event. (Default is disabled)
   # NOTE: Intel RC already provide default WhiteListedIo[] IO Port white list in SmmIoMsrAccess.h
   #       SMM code only allow access those IO ports which containedin white list after SMM LOCK (i.e. end of DXE),
   #       otherwise CPU EXCEPTION will occured cause system hard hang due to DGR detected invalid IO Port access in SMM mode.
   #
   DEFINE INTEL_DGR_IO_PORT_ALLOW_ACCESS_IN_SMN_AFTER_END_OF_DXE_SUPPORT = TRUE

   #
   # Provide a white list to control DGR IO port access policy (DENY or ALLOW) in SMM mode after EndOfDxe event. (Default is disabled)
   # NOTE: Intel RC already provide default WhiteListedMsr[] MSR index white list in SmmIoMsrAccess.h
   #       SMM code only allow access those MSR registers which contained in white list after SMM LOCK (i.e. end of DXE),
   #       otherwise CPU EXCEPTION will occured cause system hard hang due to DGR detected invalid MSR register access in SMM mode.
   #
   DEFINE INTEL_DGR_MSR_ALLOW_ACCESS_IN_SMN_AFTER_END_OF_DXE_SUPPORT = TRUE


[PcdsFeatureFlag]

   # PCD to enable above 4GB MMIO resource support
   gHpIntelChipsetPkgTokenSpaceGuid.PcdIntelAbove4GBMMIOSupport|TRUE

   # PCD for Intel VMD support, default not support
   gHpIntelChipsetPkgTokenSpaceGuid.PcdIntelVmdSupport|TRUE

   # PCD for PCIE Wake support for Deep Sx, update to support deep sleep wake
   gHpIntelChipsetPkgTokenSpaceGuid.PcdPcieWakeFromDeepSxSupport|TRUE

   # PCD to define if platform support I2C/I2S Audio Codec
   gHpIntelChipsetPkgTokenSpaceGuid.PcdAdspEnable|FALSE

   # PCD to enable Modern Standby
   gHpModernStandbyPkgTokenSpaceGuid.PcdHpModernStandbySupport|FALSE
   
[PcdsFixedAtBuild]
   gSiPkgTokenSpaceGuid.PcdAcpiEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdSmbiosEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdS3Enable|TRUE
   gSiPkgTokenSpaceGuid.PcdSiCatalogDebugEnable|FALSE
   gSiPkgTokenSpaceGuid.PcdStatusCodeUseTraceHub|FALSE
   gSiPkgTokenSpaceGuid.PcdSourceDebugEnable|FALSE
   gSiPkgTokenSpaceGuid.PcdBiosGuardEnable|FALSE
   gMeteorLakeBinPkgTokenSpaceGuid.PcdBiosGuardBinEnable|FALSE          #BiosGuardModule.bin
   gSiPkgTokenSpaceGuid.PcdHgEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdBootGuardEnable|FALSE
   gSiPkgTokenSpaceGuid.PcdTxtEnable|FALSE
   gSiPkgTokenSpaceGuid.PcdEmbeddedEnable|0x0
   gSiPkgTokenSpaceGuid.PcdAmtEnable|FALSE
   gSiPkgTokenSpaceGuid.PcdAtaEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdOverclockEnable|FALSE
   gIntelFsp2WrapperTokenSpaceGuid.PcdFspModeSelection|FALSE
   gSiPkgTokenSpaceGuid.PcdOcWdtEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdSerialIoUartEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdIpuEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdIgdEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdPeiDisplayEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdVtdEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdCpuPowerOnConfigEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdGnaEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdPttEnable|FALSE
   gSiPkgTokenSpaceGuid.PcdSmmVariableEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdThcEnable|FALSE
   gSiPkgTokenSpaceGuid.PcdOptimizeCompilerEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdPpmEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdPsmiEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdSerialIoUartDebugEnable|FALSE
   gSiPkgTokenSpaceGuid.PcdPpamEnable|TRUE
   gSiPkgTokenSpaceGuid.PcdTraceHubCatalogEnable|FALSE
   gSiPkgTokenSpaceGuid.PcdAcpiDebugEnableFlag|FALSE
   gMeteorLakeBinPkgTokenSpaceGuid.PcdIntelGopBinEnable|TRUE
   gBoardModuleTokenSpaceGuid.PcdFspPeiGopDisable|TRUE
   
   # PCD to determine Pch Series LP = 0x00 / H & S= 0x01
   gHpIntelChipsetPkgTokenSpaceGuid.PcdPchSeries|0

   # set TRUE to enable/disable USBr depends on F10 option
   gHpIntelChipsetPkgTokenSpaceGuid.PcdAMTUsbPortControl      |TRUE

   #/**
   #  The number of milliseconds reference code will wait for link to exit Detect state for enabled ports
   #  before assuming there is no device and potentially disabling the port.
   #  It's assumed that the link will exit detect state before root port initialization (sufficient time
   #  elapsed since PLTRST de-assertion) therefore default timeout is zero. However this might be useful
   #  if device power-up seqence is controlled by BIOS or a specific device requires more time to detect.
   #  In case of non-common clock enabled the default timout is 15ms.
   #  <b>Default: 0</b>
   #
   #  Intel PCH check for device presence (The Presence Detect Changed bit in SLot Control/Status register) with timeout.
   #  For Hybrid Graphics system, we encounter dGPU loss issue if it is connected to PCH.
   #  We have to increase timeout from 0ms to 15ms to make sure that dGPU is present. Otherwise, the root port of dGPU will be disabled.
   #
   #  Therefore, platform engineer must to configure this timeout value from 0ms to 15ms if platform supports Hybrid Graphics feature.
   #  If platform doesn't support Hybrid Graphics feature, but it has similar PCIe device loss problem,
   #  platform engineer can customize this timeout value by themselves.
   #
   #**/
   gHpIntelChipsetPkgTokenSpaceGuid.PcdPciePresenceDetectTimeoutMs|0

!if ($(TARGET) == DEBUG)
   gSiPkgTokenSpaceGuid.PcdSerialIoUartDebugEnable|1
   gSiPkgTokenSpaceGuid.PcdSerialIoUartNumber     |2
   gSiPkgTokenSpaceGuid.PcdSerialIoUartMode       |2
   #
   # Tell which debug port is used by Publisting DBGP table and DBG2 table
   # 0: UART0
   # 1: UART1
   # 2: UART2
   # 3: Legacy Uart
   # 0xFF: Don't Publish
   gHpIntelChipsetPkgTokenSpaceGuid.PcdOsDebugPort|gSiPkgTokenSpaceGuid.PcdSerialIoUartNumber
!endif

!if gHpIntelChipsetPkgTokenSpaceGuid.PcdIntelVmdSupport == TRUE
   gHpIntelChipsetPkgTokenSpaceGuid.PcdFixedIntelVmdSupport|TRUE
   gSiPkgTokenSpaceGuid.PcdVmdEnable|TRUE
!else
   gHpIntelChipsetPkgTokenSpaceGuid.PcdFixedIntelVmdSupport|FALSE
   gSiPkgTokenSpaceGuid.PcdVmdEnable|FALSE
!endif

   ## PCD to define if platform supports GpioGroupToGpe Override. Override by GPIO_CNL_H_GROUP_GPP_E, GPIO_CNL_H_GROUP_GPP_G, GPIO_CNL_H_GROUP_GPP_K
   ## TBT will override PcdOverrideGpioGroupToGpeDw2 for TBT 1-tier pin if TBT supported platform.
#   gPlatformModuleTokenSpaceGuid.PcdOverrideGpioGroupToGpeDw0|0x0304
#   gPlatformModuleTokenSpaceGuid.PcdOverrideGpioGroupToGpeDw1|0x0306
#   gPlatformModuleTokenSpaceGuid.PcdOverrideGpioGroupToGpeDw2|0x030A

!if $(ME_SKU) == Full OR $(ME_SKU) == FULL
   gHpIntelChipsetPkgTokenSpaceGuid.PcdMeSku|1
!else
   gHpIntelChipsetPkgTokenSpaceGuid.PcdMeSku|2
!endif
   gHpIntelChipsetPkgTokenSpaceGuid.PcdFspDebug|TRUE
   !if gHpIntelChipsetPkgTokenSpaceGuid.PcdFspDebug == TRUE
      gSiPkgTokenSpaceGuid.PcdSerialDebugLevel|0x04
   !else
      gSiPkgTokenSpaceGuid.PcdSerialDebugLevel|0x02
   !endif
  #
  # Modern Standby Feature
  #
!if gHpModernStandbyPkgTokenSpaceGuid.PcdHpModernStandbySupport == TRUE
   gHpModernStandbyPkgTokenSpaceGuid.PcdHpModernStandbyShowF10Option        |FALSE # debug purposal
   gHpModernStandbyPkgTokenSpaceGuid.PcdHpModernStandbyBCUSupport           |FALSE # debug purposal
   gHpModernStandbyPkgTokenSpaceGuid.PcdHpModernStandbySupportDefault       |TRUE
   gHpModernStandbyPkgTokenSpaceGuid.PcdHpModernStandbyEcIoTrapEnable       |FALSE
   gHpModernStandbyPkgTokenSpaceGuid.PcdHpModernStandbyEclowPowerExitGPIO   |0x0202000E  # Modern Standby EC IO trap, EC low power exit GPIO, Default:GPP_C14
   gHpModernStandbyPkgTokenSpaceGuid.PcdHpModernStandbyEcExtSmiGPIO         |0x02040010  # Modern Standby EC IO trap, EC EXT_SMI#, Default:GPP_E16
   gHpModernStandbyPkgTokenSpaceGuid.PcdHpModernStandbyLpitResidencyCounter |3            # Modern Standby LPIT residence counter: bit0: Package C10 counter, bit1: SLP_S0# counter, bit2: PS_ON# counter
!endif

   # Overwrite dGPU PCIe ClkReq (SCLK) setting by platform.
   gHpIntelChipsetPkgTokenSpaceGuid.PcdHpdGPUClkReqNumber|3

   gHpIntelChipsetPkgTokenSpaceGuid.PcdCirrusDampSupport|0
   
[PcdsFixedAtBuild.common]


[PcdsDynamicDefault]
  # BoardIdArlSBGASodimm2DAep
#  gBoardModuleTokenSpaceGuid.PcdBoardId|0x22

#
# Start of Platform PCD configuration -
#
[PcdsFeatureFlag]
      # PCD for Decode LPC Generic IO
   gHpIntelChipsetPkgTokenSpaceGuid.PcdLpcGenericIoDecodeSupport|FALSE
