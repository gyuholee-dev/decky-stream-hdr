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
  saturation: number;
  streaming: boolean;
  wrapper: WrapperStatus;
  error: ErrorInfo | null;
  saturation_error: ErrorInfo | null;
}

// Thin wrappers around backend methods defined in main.py.
export const getStatus = callable<[], Status>("get_status");
export const setHdrEnabled = callable<[enabled: boolean], Status>("set_hdr_enabled");
export const setSaturation = callable<[percent: number], Status>("set_saturation");
