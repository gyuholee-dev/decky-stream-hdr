import { callable } from "@decky/api";

export interface WrapperStatus {
  client_found: boolean;
  wrapped: boolean;
  original_saved: boolean;
  shim_installed: boolean;
  enabled: boolean;
}

export interface Status {
  hdr_enabled: boolean;
  wrapper: WrapperStatus;
  error: string | null;
}

// Thin wrappers around backend methods defined in main.py.
export const getStatus = callable<[], Status>("get_status");
export const setHdrEnabled = callable<[enabled: boolean], Status>("set_hdr_enabled");
