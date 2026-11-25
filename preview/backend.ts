// In-memory stand-in for the plugin backend, used only by the browser preview.
// It mirrors the replies of main.py so the panel can be styled without a device. The options
// (ranges, steps, defaults, what is frozen during a stream) come from the same file as the real backend.
import options from "streamhdr-options";

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

type OptionName = keyof typeof options;
const optionNames = Object.keys(options) as OptionName[];
const defaults = Object.fromEntries(optionNames.map((name) => [name, options[name].default])) as Pick<PreviewStatus, OptionName>;

const state: PreviewStatus = {
  ...defaults,
  hdr_active: false,
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


// What the real backend does with a request: put it on the grid and inside the range.
const snap = (name: OptionName, value: number | boolean) => {
  const spec = options[name];
  if (typeof spec.default === "boolean") return Boolean(value);
  const { min, max, step } = spec as { min: number; max: number; step: number };
  return Math.max(min, Math.min(max, Math.round((Number(value) - min) / step) * step + min));
};

// The wrapper follows the HDR toggle, like the real backend installs and removes things.
const followToggle = () => {
  const on = state.hdr_enabled;
  state.wrapper = {
    ...state.wrapper,
    wrapped: on || state.wrapper.wrapped,
    original_saved: on || state.wrapper.original_saved,
    shim_installed: on || state.wrapper.shim_installed,
    enabled: on,
  };
};

const frozen = (name: OptionName) => state.streaming && Boolean((options[name] as { frozenWhileStreaming?: boolean }).frozenWhileStreaming);

const handlers: Record<string, (...args: any[]) => PreviewStatus> = {
  get_status: () => ({ ...state, hdr_active: state.streaming && state.hdr_enabled, wrapper: { ...state.wrapper } }),
  set_option: (name: OptionName, value: number | boolean) => {
    if (optionNames.includes(name) && !frozen(name)) {
      Object.assign(state, { [name]: snap(name, value) });
      if (name === "hdr_enabled") followToggle();
    }
    return handlers.get_status();
  },
  reset_settings: () => {
    // Everything goes back to its default, except what is frozen during a stream.
    for (const name of optionNames) if (!frozen(name)) Object.assign(state, { [name]: defaults[name] });
    followToggle();
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
