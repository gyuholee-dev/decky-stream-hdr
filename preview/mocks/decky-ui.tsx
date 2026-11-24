// Stand-ins for the @decky/ui components used by the panel, drawn to look roughly like
// Steam's quick access menu. Spacing and fonts are approximations; check the real look on a device.
import type { ReactNode } from "react";

export function PanelSection({ title, children }: { title?: string; children?: ReactNode }) {
  return (
    <section className="ps">
      {title && <div className="ps-title">{title}</div>}
      {children}
    </section>
  );
}

export function PanelSectionRow({ children }: { children?: ReactNode }) {
  return <div className="psr">{children}</div>;
}

interface ToggleFieldProps {
  label?: ReactNode;
  description?: ReactNode;
  checked: boolean;
  disabled?: boolean;
  onChange?(checked: boolean): void;
}

export function ToggleField({ label, description, checked, disabled, onChange }: ToggleFieldProps) {
  return (
    <div className="field">
      <div className="field-row">
        <div className="field-label">{label}</div>
        <button
          type="button"
          role="switch"
          aria-checked={checked}
          disabled={disabled}
          className={"toggle" + (checked ? " on" : "")}
          onClick={() => onChange?.(!checked)}
        >
          <span className="knob" />
        </button>
      </div>
      {description && <div className="field-desc">{description}</div>}
    </div>
  );
}

interface SliderFieldProps {
  label?: ReactNode;
  description?: ReactNode;
  value: number;
  min?: number;
  max?: number;
  step?: number;
  showValue?: boolean;
  valueSuffix?: string;
  resetValue?: number;
  disabled?: boolean;
  onChange?(value: number): void;
}

export function SliderField({
  label,
  description,
  value,
  min = 0,
  max = 100,
  step = 1,
  showValue,
  valueSuffix = "",
  resetValue,
  disabled,
  onChange,
}: SliderFieldProps) {
  return (
    <div className="field">
      <div className="field-row">
        <div className="field-label">{label}</div>
        {showValue && (
          <div className="slider-value">
            {value}
            {valueSuffix}
          </div>
        )}
      </div>
      <input
        className="slider"
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange?.(Number(event.target.value))}
      />
      {resetValue !== undefined && (
        <button type="button" className="slider-reset" onClick={() => onChange?.(resetValue)}>
          Reset to {resetValue}
          {valueSuffix}
        </button>
      )}
      {description && <div className="field-desc">{description}</div>}
    </div>
  );
}
