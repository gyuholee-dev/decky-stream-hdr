import { callable } from "@decky/api";

import type { ErrorInfo } from "./strings";

// The names of the options: see py_modules/streamhdr/options.json.
export type OptionName = "hdr_enabled" | "paper_white" | "contrast" | "gamma" | "saturation";

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
export const setOption = callable<[name: OptionName, value: number | boolean], Status>("set_option");
export const resetSettings = callable<[], Status>("reset_settings");
