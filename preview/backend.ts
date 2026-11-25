// In-memory stand-in for the plugin backend, used only by the browser preview.
// It mirrors the replies of main.py so the panel can be styled without a device.

export interface PreviewStatus {
  hdr_enabled: boolean;
  hdr_active: boolean;
  saturation: number;
  paper_white: number;
  contrast: number;
  gamma: number;
  streaming: boolean;
  wrapper: {
    client_found: boolean;
    wrapped: boolean;
    original_saved: boolean;
    shim_installed: boolean;
    enabled: boolean;
  };
  error: { code: string; detail: string | null } | null;
  look_error: { code: string; detail: string | null } | null;
  paper_white_error: { code: string; detail: string | null } | null;
}

export const knobs = {
  unreachable: false, // make every call fail, like a backend that did not load
  latencyMs: 150,
};

const state: PreviewStatus = {
  hdr_enabled: true,
  hdr_active: false,
  saturation: 100,
  paper_white: 230,
  contrast: 100,
  gamma: 100,
  streaming: false,
  wrapper: {
    client_found: true,
    wrapped: true,
    original_saved: true,
    shim_installed: true,
    enabled: true,
  },
  error: null,
  look_error: null,
  paper_white_error: null,
};

const listeners = new Set<(status: PreviewStatus) => void>();

// Like the real backend's "status" event: sent when something changes that the panel did not ask for.
export function subscribe(listener: (status: PreviewStatus) => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function patchState(patch: Partial<PreviewStatus>) {
  Object.assign(state, patch);
  const status = handlers.get_status();
  listeners.forEach((listener) => listener(status));
}


// The same grid as the real backend (see look.py and paperwhite.py).
const snap = (value: number, min: number, max: number, step: number) => Math.max(min, Math.min(max, Math.round(value / step) * step));

const handlers: Record<string, (...args: any[]) => PreviewStatus> = {
  get_status: () => ({ ...state, hdr_active: state.streaming && state.hdr_enabled, wrapper: { ...state.wrapper } }),
  set_hdr_enabled: (enabled: boolean) => {
    state.hdr_enabled = enabled;
    state.wrapper = {
      ...state.wrapper,
      wrapped: enabled || state.wrapper.wrapped,
      original_saved: enabled || state.wrapper.original_saved,
      shim_installed: enabled || state.wrapper.shim_installed,
      enabled,
    };
    return handlers.get_status();
  },
  reset_settings: () => {
    // While streaming, HDR streaming and Paper White stay as they are.
    Object.assign(state, { contrast: 100, gamma: 100, saturation: 100 });
    if (!state.streaming) {
      Object.assign(state, { paper_white: 230, hdr_enabled: true });
      state.wrapper = { ...state.wrapper, wrapped: true, original_saved: true, shim_installed: true, enabled: true };
    }
    return handlers.get_status();
  },
  set_paper_white: (nits: number) => {
    state.paper_white = snap(nits, 80, 480, 10);
    return handlers.get_status();
  },
  set_contrast: (percent: number) => {
    state.contrast = snap(percent, 0, 200, 5);
    return handlers.get_status();
  },
  set_gamma: (hundredths: number) => {
    state.gamma = snap(hundredths, 50, 200, 5);
    return handlers.get_status();
  },
  set_saturation: (percent: number) => {
    state.saturation = snap(percent, 0, 200, 5);
    return handlers.get_status();
  },
};

export async function call(name: string, args: any[]): Promise<PreviewStatus> {
  await new Promise((resolve) => setTimeout(resolve, knobs.latencyMs));
  if (knobs.unreachable) throw new Error("backend unreachable (preview knob)");
  const handler = handlers[name];
  if (!handler) throw new Error("unknown backend method: " + name);
  return handler(...args);
}
