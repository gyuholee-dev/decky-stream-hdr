import { callable } from "@decky/api";

import type { ErrorInfo } from "./strings";

export interface WrapperStatus {
  client_found: boolean;
  wrapped: boolean;
  original_saved: boolean;
  shim_installed: boolean;
  enabled: boolean;
}

export interface Status {
  hdr_enabled: boolean;
  hdr_active: boolean;
  saturation: number;
  paper_white: number;
  contrast: number;
  gamma: number; // hundredths: 100 means 1.00
  streaming: boolean;
  wrapper: WrapperStatus;
  error: ErrorInfo | null;
  look_error: ErrorInfo | null;
  paper_white_error: ErrorInfo | null;
}

// Thin wrappers around backend methods defined in main.py.
export const getStatus = callable<[], Status>("get_status");
export const setHdrEnabled = callable<[enabled: boolean], Status>("set_hdr_enabled");
export const setSaturation = callable<[percent: number], Status>("set_saturation");
export const setPaperWhite = callable<[nits: number], Status>("set_paper_white");
export const setContrast = callable<[percent: number], Status>("set_contrast");
export const setGamma = callable<[hundredths: number], Status>("set_gamma");
export const resetSettings = callable<[], Status>("reset_settings");
