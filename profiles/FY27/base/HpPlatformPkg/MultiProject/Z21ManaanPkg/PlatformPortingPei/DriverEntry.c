//
// (c) Copyright 2017 - 2026 HP Development Company, L.P.
// This software and associated documentation (if any) is furnished under a license and may only be used or
// copied in accordance with the terms of the license. Except as permitted by such license, no part of this
// software or documentation may be reproduced, stored in a retrieval system, or transmitted in any
// form or by any means without the express written consent of HP Development Company.
//
// File Name:  DriverEntry.c
//
// Abstract:
//
//   Platform PEI drivers.
//

#include "Meta.h"
#include <HpDebugPrint.h>

// ---------------------------------------------------------------------------------------------------------------------
// Local Macro Definitions
// ---------------------------------------------------------------------------------------------------------------------

//#define PLATFORM_PEI_ENTRY_DEBUG
#ifdef  PLATFORM_PEI_ENTRY_DEBUG
  #pragma optimize ("",off)
#define MOD_PRINT_LVL     (EFI_D_INFO|EFI_D_ERROR)
#else
#define MOD_PRINT_LVL     (0)
#endif

// ---------------------------------------------------------------------------------------------------------------------
// Local Structure Type Definitions
// ---------------------------------------------------------------------------------------------------------------------

// ---------------------------------------------------------------------------------------------------------------------
// Local Function Prototypes
// ---------------------------------------------------------------------------------------------------------------------

// ---------------------------------------------------------------------------------------------------------------------
// File Global Variables
// ---------------------------------------------------------------------------------------------------------------------

// *********************************************************************************************************************
// Function: PeiDriverEntry
//
// Summary: Platform PEI Driver.
//
// Global Variables:  None
//
// Parameters:
//    -----------------------------------------------------------------------------------------------------------------
//    Name:                   IN FileHandle
//    Description:            Standard parameter for PEI driver entry point
//    Valid values:           non-NULL
//    -----------------------------------------------------------------------------------------------------------------
//    Name:                   IN PeiServices
//    Description:            Standard parameter for PEI driver entry point
//    Valid values:           non-NULL
//    -----------------------------------------------------------------------------------------------------------------
//
// Function Returns:  EFI_STATUS
//    -----------------------------------------------------------------------------------------------------------------
//    EFI_SUCCESS             -  Driver/PPI loaded properly
//    Other values
//    -----------------------------------------------------------------------------------------------------------------
//
// *********************************************************************************************************************
EFI_STATUS
InstallPlatformPortingPeiReadyPpi (
  VOID
  )
{
  EFI_STATUS              Status;
  EFI_PEI_PPI_DESCRIPTOR  *PlatformPeiPortingReadyPpiDesc;

  PlatformPeiPortingReadyPpiDesc = (EFI_PEI_PPI_DESCRIPTOR *)AllocateZeroPool (sizeof (EFI_PEI_PPI_DESCRIPTOR));
  if (PlatformPeiPortingReadyPpiDesc == NULL)
  {
    DEBUG ((DEBUG_ERROR, "%a: Not enough memory for EFI_PEI_PPI_DESCRIPTOR.\n", __func__));
    return EFI_OUT_OF_RESOURCES;
  }

  PlatformPeiPortingReadyPpiDesc->Flags = EFI_PEI_PPI_DESCRIPTOR_PPI | EFI_PEI_PPI_DESCRIPTOR_TERMINATE_LIST;
  PlatformPeiPortingReadyPpiDesc->Guid  = &gHpPlatformPortingPeiReadyPpiGuid;
  PlatformPeiPortingReadyPpiDesc->Ppi   = NULL;

  //
  // Install Platform Pei Porting Ready PPI
  //
  Status = PeiServicesInstallPpi (PlatformPeiPortingReadyPpiDesc);
  if (EFI_ERROR (Status)) {
    DEBUG ((DEBUG_ERROR, "%a: Failed to install Platform Pei Porting Ready PPI - %r\n", __func__, Status));
  }
  return Status;
}

//*********************************************************************************************************************
// Function: PeiDriverEntry
//
// Summary: Platform PEI Driver.
//
// Global Variables:  None
//
// Parameters:
//    -----------------------------------------------------------------------------------------------------------------
//    Name:                   IN FileHandle
//    Description:            Standard parameter for PEI driver entry point
//    Valid values:           non-NULL
//    -----------------------------------------------------------------------------------------------------------------
//    Name:                   IN PeiServices
//    Description:            Standard parameter for PEI driver entry point
//    Valid values:           non-NULL
//    -----------------------------------------------------------------------------------------------------------------
//
// Function Returns:  EFI_STATUS
//    -----------------------------------------------------------------------------------------------------------------
//    EFI_SUCCESS             -  Driver/PPI loaded properly
//    Other values
//    -----------------------------------------------------------------------------------------------------------------
//
//*********************************************************************************************************************
EFI_STATUS
PeiDriverEntry (
   IN EFI_PEI_FILE_HANDLE       FileHandle,
   IN CONST EFI_PEI_SERVICES    **PeiServices
   )
{
  FUNCTION_STARTS (MOD_PRINT_LVL);

  EFI_STATUS  Status = EFI_NOT_STARTED;

  Status = PlatformIdPeiEntry (FileHandle, PeiServices);
  if (Status != EFI_SUCCESS)
  {
    ERR_TRACE_STATUS (Status);
  }

  // Install PPI, after platform porting PEI is ready.
  Status = InstallPlatformPortingPeiReadyPpi (); 

  FUNCTION_ENDS (MOD_PRINT_LVL);
  return EFI_SUCCESS;
}
