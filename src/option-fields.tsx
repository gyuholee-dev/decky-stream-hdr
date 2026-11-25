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

export function OptionSlider({ name, suffix, status, change, label, description }: FieldContext & Texts & { name: SliderName; suffix?: string }) {
  const spec = options[name];
  const scale = spec.scale ?? 1; // gamma is stored in hundredths and shown as the plain number
  return (
    <PanelSectionRow>
      <SliderField
        label={label}
        description={<KeepAll>{description}</KeepAll>}
        value={status[name] / scale}
        disabled={spec.frozenWhileStreaming && status.streaming}
        min={spec.min / scale}
        max={spec.max / scale}
        step={spec.step / scale}
        resetValue={spec.default / scale}
        showValue
        valueSuffix={suffix}
        onChange={(shown: number) => {
          const stored = Math.round(shown * scale);
          change({ [name]: stored }, setOption(name, stored));
        }}
      />
    </PanelSectionRow>
  );
}
