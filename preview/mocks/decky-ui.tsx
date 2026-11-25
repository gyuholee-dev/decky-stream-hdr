// Stand-ins for the @decky/ui components used by the panel.
//
// With a capture of the real Steam UI (`yarn capture`) they render the same markup and class names
// as Steam's own components, so the real Steam CSS styles them. Without a capture they fall back to a
// rough look made by preview/preview.css (class names starting with "approx-").
import { createContext, forwardRef, useContext, useEffect, useRef } from "react";
import type { CSSProperties, KeyboardEvent, ReactNode } from "react";

import { router } from "../router";

import { controls, cx, dialog, real, scrollClass, slider, useFocus } from "./steam";

// --- sections ---------------------------------------------------------------------------------

export function PanelSection({ title, children }: { title?: string; children?: ReactNode }) {
  if (!real) {
    return (
      <section className="approx-section">
        {title && <div className="approx-section-title">{title}</div>}
        {children}
      </section>
    );
  }
  return (
    <div className={controls("PanelSection")}>
      {title && (
        <div className={controls("PanelSectionTitle")}>
          <div className={controls("Text")}>{title}</div>
        </div>
      )}
      {children}
    </div>
  );
}

// Steam adds "qam-focusable-item" to rows that hold a button; its CSS also hides field labels there.
const RowContext = createContext<(() => void) | null>(null);

export function PanelSectionRow({ children }: { children?: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  if (!real) return <div className="approx-row">{children}</div>;
  const markFocusable = () => ref.current?.classList.add("qam-focusable-item");
  return (
    <RowContext.Provider value={markFocusable}>
      <div ref={ref} className={controls("PanelSectionRow")}>
        {children}
      </div>
    </RowContext.Provider>
  );
}

// --- toggle -----------------------------------------------------------------------------------

interface ToggleFieldProps {
  label?: ReactNode;
  description?: ReactNode;
  checked: boolean;
  disabled?: boolean;
  onChange?(checked: boolean): void;
}

export function ToggleField({ label, description, checked, disabled, onChange }: ToggleFieldProps) {
  const { focused, bind } = useFocus();
  const toggle = () => !disabled && onChange?.(!checked);
  const onKeyDown = (event: KeyboardEvent) => {
    if (event.key === " " || event.key === "Enter") {
      event.preventDefault();
      toggle();
    }
  };

  if (!real) {
    return (
      <div className="approx-field">
        <div className="approx-field-row">
          <div className="approx-label">{label}</div>
          <button type="button" role="switch" aria-checked={checked} disabled={disabled} className={cx("approx-toggle", checked && "on")} onClick={toggle}>
            <span className="approx-knob" />
          </button>
        </div>
        {description && <div className="approx-desc">{description}</div>}
      </div>
    );
  }

  return (
    <div
      className={cx(
        dialog("Field"),
        dialog("Classic"),
        dialog("VerticalAlignCenter"),
        dialog("WithBottomSeparatorStandard"),
        dialog("ExtraPaddingOnChildrenBelow"),
        dialog("StandardPadding"),
        dialog("HighlightOnFocus"),
        "Panel",
        "Focusable",
        focused && "gpfocuswithin",
      )}
    >
      <div className={dialog("FieldLeftColumn")}>
        <div className={dialog("FieldLabelRow")}>
          <div className={dialog("FieldLabel")}>{label}</div>
        </div>
        {description && <div className={dialog("FieldDescription")}>{description}</div>}
      </div>
      <div className={dialog("FieldRightColumn")}>
        <div className={dialog("FieldChildrenWithIcon")}>
          <div className={dialog("FieldChildrenInner")}>
            <div
              role="checkbox"
              aria-checked={checked}
              tabIndex={0}
              className={cx(dialog("Toggle"), checked && dialog("On"), disabled && dialog("Disabled"), "Focusable", focused && "gpfocus")}
              onClick={toggle}
              onKeyDown={onKeyDown}
              {...bind}
            >
              <div className={dialog("ToggleRail")} />
              <div className={dialog("ToggleSwitch")} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// --- slider -----------------------------------------------------------------------------------

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
  const { focused, bind } = useFocus();
  const normalized = max > min ? (value - min) / (max - min) : 0;
  const normalizedDefault = resetValue !== undefined && max > min ? (resetValue - min) / (max - min) : normalized;

  // A transparent range input on top makes the drawn slider usable with the mouse and the keyboard.
  const input = (
    <input
      className="preview-slider-input"
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      disabled={disabled}
      aria-label={typeof label === "string" ? label : undefined}
      onChange={(event) => onChange?.(Number(event.target.value))}
      {...bind}
    />
  );

  if (!real) {
    return (
      <div className="approx-field">
        <div className="approx-field-row">
          <div className="approx-label">{label}</div>
          {showValue && (
            <div className="approx-value">
              {value}
              {valueSuffix}
            </div>
          )}
        </div>
        <input className="approx-slider" type="range" min={min} max={max} step={step} value={value} disabled={disabled} onChange={(event) => onChange?.(Number(event.target.value))} />
        {description && <div className="approx-desc">{description}</div>}
      </div>
    );
  }

  const sliderVars: Record<string, string | number> = {
    position: "relative",
    "--normalized-slider-value": normalized,
    "--normalized-slider-origin": 0,
    "--slider-extra-notch-padding": "0px",
  };
  if (resetValue !== undefined) sliderVars["--normalized-slider-default-value"] = normalizedDefault;

  // Same markup as Steam's slider field (captured from a device).
  return (
    <div
      className={cx(
        dialog("Field"),
        dialog("Classic"),
        dialog("WithChildrenBelow"),
        dialog("VerticalAlignCenter"),
        dialog("WithBottomSeparatorStandard"),
        dialog("ChildrenWidthFixed"),
        dialog("ExtraPaddingOnChildrenBelow"),
        dialog("StandardPadding"),
        dialog("HighlightOnFocus"),
        "Panel",
        "Focusable",
        focused && "gpfocuswithin",
      )}
      style={{ "--indent-level": 0 } as React.CSSProperties}
    >
      <div className={dialog("FieldLeftColumn")}>
        <div className={dialog("FieldLabelRow")}>
          <div className={dialog("FieldLabel")}>{label}</div>
          {showValue && (
            <div className={dialog("FieldLabelValue")}>
              {value}
              {valueSuffix}
            </div>
          )}
        </div>
        <div className={dialog("FieldChildrenWithIcon")}>
          <div className={dialog("FieldChildrenInner")}>
            <div className={cx(slider("SliderControlPanelGroup"), "SliderControlPanelGroup", "Panel", "Focusable", focused && "gpfocus gpfocuswithin")}>
              <div
                role="slider"
                aria-valuenow={value}
                aria-valuemin={min}
                aria-valuemax={max}
                className={cx(slider("SliderControlAndNotches"), resetValue !== undefined && slider("WithDefaultValue"), disabled && slider("Disabled"), "Focusable")}
                style={sliderVars as React.CSSProperties}
              >
                <div className={cx(slider("SliderControl"), "SliderControl")}>
                  <div className={cx(slider("SliderTrack"), "SliderTrack")} />
                  <div className={cx(slider("SliderHandleContainer"), "SliderHandleContainer")}>
                    <div className={cx(slider("SliderHandle"), "SliderHandle")} />
                  </div>
                </div>
                {input}
              </div>
            </div>
          </div>
        </div>
        {description && <div className={dialog("FieldDescription")}>{description}</div>}
      </div>
    </div>
  );
}

// --- buttons, navigation and dialog pieces --------------------------------------------------------

interface ButtonItemProps {
  children?: ReactNode;
  description?: ReactNode;
  disabled?: boolean;
  layout?: "below" | "inline";
  onClick?(event: MouseEvent | React.MouseEvent): void;
}

export function ButtonItem({ children, description, disabled, onClick }: ButtonItemProps) {
  const { focused, bind } = useFocus();
  const markFocusable = useContext(RowContext);
  useEffect(() => markFocusable?.(), [markFocusable]);

  if (!real) {
    return (
      <div className="approx-field">
        <button type="button" className="approx-button" disabled={disabled} onClick={onClick}>
          {children}
        </button>
        {description && <div className="approx-desc">{description}</div>}
      </div>
    );
  }

  return (
    <div
      className={cx(
        dialog("Field"),
        dialog("Classic"),
        dialog("VerticalAlignCenter"),
        dialog("WithBottomSeparatorStandard"),
        dialog("WithChildrenBelow"),
        dialog("ExtraPaddingOnChildrenBelow"),
        dialog("StandardPadding"),
        dialog("HighlightOnFocus"),
        "Panel",
        "Focusable",
        focused && "gpfocuswithin",
      )}
      style={{ "--indent-level": 0 } as CSSProperties}
    >
      <div className={dialog("FieldLeftColumn")}>
        <div className={dialog("FieldChildrenWithIcon")}>
          <div className={dialog("FieldChildrenInner")}>
            <button
              type="button"
              role="button"
              disabled={disabled}
              className={cx("DialogButton", "_DialogLayout", "Secondary", dialog("Button"), "Focusable", focused && "gpfocus")}
              onClick={onClick}
              {...bind}
            >
              {children}
            </button>
          </div>
        </div>
        {description && <div className={dialog("FieldDescription")}>{description}</div>}
      </div>
    </div>
  );
}

// A plain focus container; the preview does not model gamepad navigation.
export function Focusable({ children, style, onCancel }: { children?: ReactNode; style?: CSSProperties; onCancel?(): void; noFocusRing?: boolean }) {
  return (
    <div
      className="Panel Focusable"
      style={style}
      tabIndex={-1}
      onKeyDown={(event) => {
        if (event.key === "Escape") onCancel?.();
      }}
    >
      {children}
    </div>
  );
}

export const Navigation = {
  Navigate: (path: string) => router.navigate(path),
  NavigateBack: () => router.back(),
  NavigateToExternalWeb: (url: string) => {
    console.info("[preview] would open in Steam's browser:", url);
    window.open(url, "_blank", "noopener");
  },
  CloseSideMenus: () => undefined,
};

export const DialogBody = ({ children }: { children?: ReactNode }) => <div className="preview-dialog-body">{children}</div>;
export const DialogControlsSection = ({ children }: { children?: ReactNode }) => <div className="preview-dialog-section">{children}</div>;
export const DialogControlsSectionHeader = ({ children }: { children?: ReactNode }) => <div className="preview-dialog-header">{children}</div>;
export const DialogBodyText = ({ children }: { children?: ReactNode }) => <div className="preview-dialog-text">{children}</div>;

interface FieldProps {
  label?: ReactNode;
  description?: ReactNode;
  children?: ReactNode;
  bottomSeparator?: "standard" | "thick" | "none";
  focusable?: boolean;
  onActivate?(event: unknown): void;
  onClick?(event: unknown): void;
}

// A generic row: an optional label and description, optionally focusable and clickable.
export function Field({ label, description, children, bottomSeparator = "standard", focusable, onActivate, onClick }: FieldProps) {
  const { focused, bind } = useFocus();
  const markFocusable = useContext(RowContext);
  useEffect(() => {
    if (focusable) markFocusable?.();
  }, [focusable, markFocusable]);
  const activate = (event: unknown) => (onClick ?? onActivate)?.(event);

  if (!real) {
    return (
      <div className="approx-field" role={focusable ? "button" : undefined} tabIndex={focusable ? 0 : undefined} onClick={activate}>
        {label && <div className="approx-label">{label}</div>}
        {children}
        {description && <div className="approx-desc">{description}</div>}
      </div>
    );
  }

  return (
    <div
      className={cx(
        dialog("Field"),
        dialog("Classic"),
        dialog("VerticalAlignCenter"),
        bottomSeparator === "standard" && dialog("WithBottomSeparatorStandard"),
        dialog("ExtraPaddingOnChildrenBelow"),
        dialog("StandardPadding"),
        focusable && dialog("Clickable"),
        dialog("HighlightOnFocus"),
        "Panel",
        "Focusable",
        focused && "gpfocuswithin",
      )}
      style={{ "--indent-level": 0 } as CSSProperties}
      role={focusable ? "button" : undefined}
      tabIndex={focusable ? 0 : undefined}
      onClick={activate}
      onKeyDown={(event) => {
        if (focusable && (event.key === "Enter" || event.key === " ")) {
          event.preventDefault();
          activate(event);
        }
      }}
      {...bind}
    >
      <div className={dialog("FieldLeftColumn")}>
        {label && (
          <div className={dialog("FieldLabelRow")}>
            <div className={dialog("FieldLabel")}>{label}</div>
          </div>
        )}
        {children}
        {description && <div className={dialog("FieldDescription")}>{description}</div>}
      </div>
    </div>
  );
}

// A small push button as used inside pages (Steam's DialogButton).
export function DialogButton({ children, style, onClick }: { children?: ReactNode; style?: CSSProperties; onClick?(event: unknown): void }) {
  const { focused, bind } = useFocus();
  if (!real) {
    return (
      <button type="button" className="approx-button" style={{ ...style, width: style?.width ?? "100%" }} onClick={onClick}>
        {children}
      </button>
    );
  }
  return (
    <button
      type="button"
      role="button"
      className={cx("DialogButton", "_DialogLayout", "Secondary", dialog("Button"), "Focusable", focused && "gpfocus")}
      style={style}
      onClick={onClick}
      {...bind}
    >
      {children}
    </button>
  );
}

// --- scroll window pieces ------------------------------------------------------------------------

// Class names of Steam's scroll panel and dialog positioning (approximations without a capture).
export const scrollPanelClasses = { ScrollPanel: real ? scrollClass("ScrollPanel") : "approx-scroll-panel" };
export const gamepadDialogClasses = { ModalPosition: dialog("ModalPosition"), WithStandardPadding: dialog("WithStandardPadding") };

export function ModalPosition({ children }: { children?: ReactNode }) {
  return <div className="modal-position-container">{children}</div>;
}

// Steam's scroll group: here simply a scrolling box.
export const ScrollPanelGroup = forwardRef<HTMLDivElement, { children?: ReactNode; style?: CSSProperties }>(function ScrollPanelGroup({ children, style }, ref) {
  return (
    <div ref={ref} className={scrollPanelClasses.ScrollPanel} style={{ height: "100%", overflowY: "auto", ...style }}>
      {children}
    </div>
  );
});

// Button ids used for the footer hints of the scroll window; the preview shows no footer.
export const GamepadButton = { DIR_UP: 1, DIR_DOWN: 2 };
