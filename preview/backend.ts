// In-memory stand-in for the plugin backend, used only by the browser preview.
// It mirrors the replies of main.py so the panel can be styled without a device.

export interface PreviewStatus {
  hdr_enabled: boolean;
  saturation: number;
  streaming: boolean;
  wrapper: {
    client_found: boolean;
    wrapped: boolean;
    original_saved: boolean;
    shim_installed: boolean;
    enabled: boolean;
  };
  error: string | null;
  saturation_error: string | null;
}

export const knobs = {
  unreachable: false, // make every call fail, like a backend that did not load
  latencyMs: 150,
};

const state: PreviewStatus = {
  hdr_enabled: false,
  saturation: 100,
  streaming: false,
  wrapper: {
    client_found: true,
    wrapped: false,
    original_saved: false,
    shim_installed: false,
    enabled: false,
  },
  error: null,
  saturation_error: null,
};

export function patchState(patch: Partial<PreviewStatus>) {
  Object.assign(state, patch);
}

const snapPercent = (value: number) => Math.max(0, Math.min(200, Math.round(value / 10) * 10));

const handlers: Record<string, (...args: any[]) => PreviewStatus> = {
  get_status: () => ({ ...state, wrapper: { ...state.wrapper } }),
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
  set_saturation: (percent: number) => {
    state.saturation = snapPercent(percent);
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
