import { PanelSectionRow, SliderField, ToggleField } from "@decky/ui";
import options from "streamhdr-options";

import { setOption, Status } from "./api";
import { KeepAll } from "./keep-all";

// What a field needs from the panel: the current status and a way to show a change at once and send it on.
export interface FieldContext {
  status: Status;
  change: (patch: Partial<Status>, request: Promise<Status>) => void;
}

type SliderName = "paper_white" | "contrast" | "gamma" | "saturation";

interface Texts {
  label: string;
  description: string;
}

// The range, step, default and "frozen during a stream" of every option come from options.json, the same
// file the backend uses, so they cannot drift apart. Only the texts and the unit are decided here.
export function OptionToggle({ status, change, label, description }: FieldContext & Texts) {
  return (
    <PanelSectionRow>
      <ToggleField
        label={label}
        description={<KeepAll>{description}</KeepAll>}
        checked={status.hdr_enabled}
        disabled={options.hdr_enabled.frozenWhileStreaming && status.streaming}
        onChange={(enabled: boolean) => change({ hdr_enabled: enabled }, setOption("hdr_enabled", enabled))}
      />
    </PanelSectionRow>
  );
}

// The slider prints the value as a plain number (1.1, 1.15, 1). The unit text that follows the number is used to pad it to a
// fixed number of decimals, so that 1.10 and 1.00 are shown instead.
function paddingZeros(shown: number, decimals: number): string {
  const plain = String(shown);
  const padded = shown.toFixed(decimals);
  return padded.startsWith(plain) ? padded.slice(plain.length) : "";
}

export function OptionSlider({ name, suffix, status, change, label, description }: FieldContext & Texts & { name: SliderName; suffix?: string }) {
  const spec = options[name];
  const scale = spec.scale ?? 1; // gamma is stored in hundredths and shown as the plain number
  const shown = status[name] / scale;
  const decimals = Math.round(Math.log10(scale)); // gamma: 2 (1.00); the whole-number options: 0
  return (
    <PanelSectionRow>
      <SliderField
        label={label}
        description={<KeepAll>{description}</KeepAll>}
        value={shown}
        disabled={spec.frozenWhileStreaming && status.streaming}
        min={spec.min / scale}
        max={spec.max / scale}
        step={spec.step / scale}
        resetValue={spec.default / scale}
        showValue
        valueSuffix={decimals > 0 ? paddingZeros(shown, decimals) : suffix}
        onChange={(next: number) => {
          const stored = Math.round(next * scale);
          change({ [name]: stored }, setOption(name, stored));
        }}
      />
    </PanelSectionRow>
  );
}
