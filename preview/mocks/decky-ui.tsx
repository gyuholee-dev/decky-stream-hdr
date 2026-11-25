// Stand-ins for the @decky/ui components used by the panel, for the browser preview only.
//
// They imitate how Steam's components look and behave, in preview/mock_steam.css, with class names of their
// own (starting with "mk-"). The markup keeps the shape of Steam's: a section holds rows, a row holds a
// field with a left column (label, description) and an optional right column, and every field draws its
// separator line with ::after. The panel's own CSS relies on that shape.
import { forwardRef, cloneElement, useRef } from "react";
import type { CSSProperties, KeyboardEvent, ReactElement, ReactNode } from "react";
import { createRoot } from "react-dom/client";

import { router } from "../router";

import { cx, useFocus } from "./steam";

// --- sections ---------------------------------------------------------------------------------

export function PanelSection({ title, children }: { title?: string; children?: ReactNode }) {
  return (
    <div className="mk-section">
      {title && <div className="mk-section-title">{title}</div>}
      {children}
    </div>
  );
}

export function PanelSectionRow({ children }: { children?: ReactNode }) {
  return <div className="mk-row">{children}</div>;
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

  return (
    <div className={cx("mk-field", "mk-highlight", focused && "mk-focused")}>
      <div className="mk-left">
        <div className="mk-label-row">
          <div className="mk-label">{label}</div>
        </div>
        {description && <div className="mk-desc">{description}</div>}
      </div>
      <div className="mk-right">
        <div className="mk-toggle-holder">
          <div
            role="checkbox"
            aria-checked={checked}
            tabIndex={0}
            className={cx("mk-toggle", checked && "mk-on", disabled && "mk-disabled", focused && "mk-focused")}
            onClick={toggle}
            onKeyDown={onKeyDown}
            {...bind}
          >
            <div className="mk-toggle-rail" />
            <div className="mk-toggle-knob" />
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

interface SliderHitProps {
  label?: string;
  value: number;
  min: number;
  max: number;
  step: number;
  disabled?: boolean;
  onChange?(value: number): void;
  bind: ReturnType<typeof useFocus>["bind"];
}

// Rounds to the slider grid and keeps floating point noise (0.1 + 0.2) out of the value.
function snapToGrid(raw: number, min: number, max: number, step: number) {
  const snapped = Math.round((raw - min) / step) * step + min;
  return Number(Math.max(min, Math.min(max, snapped)).toFixed(6));
}

function SliderHit({ label, value, min, max, step, disabled, onChange, bind }: SliderHitProps) {
  const ref = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);
  const lastSent = useRef(value);
  lastSent.current = value;

  const send = (next: number) => {
    if (next === lastSent.current) return;
    lastSent.current = next;
    onChange?.(next);
  };
  const fromPointer = (clientX: number) => {
    const rect = ref.current?.getBoundingClientRect();
    if (!rect || rect.width <= 0) return;
    // The drawn handle's center travels between half a handle width from each end of the track.
    const handle = ref.current?.parentElement?.querySelector(".mk-slider-handle")?.getBoundingClientRect().width ?? 0;
    const travel = rect.width - handle;
    if (travel <= 0) return;
    const fraction = (clientX - rect.left - handle / 2) / travel;
    send(snapToGrid(min + fraction * (max - min), min, max, step));
  };
  const onKeyDown = (event: KeyboardEvent) => {
    if (disabled) return;
    const keys: Record<string, number> = { ArrowLeft: value - step, ArrowDown: value - step, ArrowRight: value + step, ArrowUp: value + step, Home: min, End: max };
    if (!(event.key in keys)) return;
    event.preventDefault();
    send(snapToGrid(keys[event.key], min, max, step));
  };

  return (
    <div
      ref={ref}
      className="preview-slider-input"
      role="slider"
      tabIndex={disabled ? -1 : 0}
      aria-label={label}
      aria-valuenow={value}
      aria-valuemin={min}
      aria-valuemax={max}
      aria-disabled={disabled || undefined}
      onPointerDown={(event) => {
        if (disabled) return;
        dragging.current = true;
        event.currentTarget.setPointerCapture(event.pointerId);
        event.currentTarget.focus();
        fromPointer(event.clientX);
      }}
      onPointerMove={(event) => {
        if (dragging.current) fromPointer(event.clientX);
      }}
      onPointerUp={(event) => {
        dragging.current = false;
        event.currentTarget.releasePointerCapture(event.pointerId);
      }}
      onPointerCancel={() => {
        dragging.current = false;
      }}
      onKeyDown={onKeyDown}
      {...bind}
    />
  );
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
  disabled,
  onChange,
}: SliderFieldProps) {
  const { focused, bind } = useFocus();
  const normalized = max > min ? (value - min) / (max - min) : 0;

  return (
    <div className={cx("mk-field", "mk-highlight", focused && "mk-focused")}>
      <div className="mk-left">
        <div className="mk-label-row">
          <div className="mk-label">{label}</div>
          {showValue && (
            <div className="mk-value">
              {value}
              {valueSuffix}
            </div>
          )}
        </div>
        <div className={cx("mk-slider", disabled && "mk-disabled")} style={{ "--n": normalized } as CSSProperties}>
          <div className="mk-slider-control">
            <div className="mk-slider-track" />
            <div className="mk-slider-handle" />
          </div>
          <SliderHit
            label={typeof label === "string" ? label : undefined}
            value={value}
            min={min}
            max={max}
            step={step}
            disabled={disabled}
            onChange={onChange}
            bind={bind}
          />
        </div>
        {description && <div className="mk-desc">{description}</div>}
      </div>
    </div>
  );
}

// --- buttons and fields -----------------------------------------------------------------------

interface ButtonItemProps {
  children?: ReactNode;
  description?: ReactNode;
  disabled?: boolean;
  layout?: "below" | "inline";
  onClick?(event: MouseEvent | React.MouseEvent): void;
}

export function ButtonItem({ children, description, disabled, onClick }: ButtonItemProps) {
  const { focused, bind } = useFocus();
  return (
    <div className={cx("mk-field", "mk-highlight", focused && "mk-focused")}>
      <div className="mk-left">
        <button type="button" className={cx("mk-button", focused && "mk-focused")} disabled={disabled} onClick={onClick} {...bind}>
          {children}
        </button>
        {description && <div className="mk-desc">{description}</div>}
      </div>
    </div>
  );
}

// A plain focus container; the preview does not model gamepad navigation.
export function Focusable({ children, style, onCancel }: { children?: ReactNode; style?: CSSProperties; onCancel?(): void; noFocusRing?: boolean }) {
  return (
    <div
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
  const activate = (event: unknown) => (onClick ?? onActivate)?.(event);

  return (
    <div
      className={cx(
        "mk-field",
        "mk-highlight",
        bottomSeparator === "none" && "mk-no-separator",
        focusable && "mk-clickable",
        focused && "mk-focused",
      )}
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
      <div className="mk-left">
        {label && (
          <div className="mk-label-row">
            <div className="mk-label">{label}</div>
          </div>
        )}
        {children}
        {description && <div className="mk-desc">{description}</div>}
      </div>
    </div>
  );
}

// A push button as used inside pages (Steam's DialogButton).
export function DialogButton({ children, style, onClick }: { children?: ReactNode; style?: CSSProperties; onClick?(event: unknown): void }) {
  const { focused, bind } = useFocus();
  return (
    <button type="button" className={cx("mk-button", focused && "mk-focused")} style={style} onClick={onClick} {...bind}>
      {children}
    </button>
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


// --- scroll window pieces ------------------------------------------------------------------------

// Class names the panel's own CSS refers to (Steam's scroll panel and dialog positioning).
export const scrollPanelClasses = { ScrollPanel: "mk-scroll-panel" };
export const gamepadDialogClasses = { ModalPosition: "mk-modal-position", WithStandardPadding: "mk-standard-padding" };

// Steam's ModalPosition fills the space it is given, which is what makes its scroll panel scroll.
export function ModalPosition({ children }: { children?: ReactNode }) {
  return <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column" }}>{children}</div>;
}

// Steam's scroll group: here simply a scrolling box.
export const ScrollPanelGroup = forwardRef<HTMLDivElement, { children?: ReactNode; style?: CSSProperties }>(function ScrollPanelGroup({ children, style }, ref) {
  return (
    <div ref={ref} className={scrollPanelClasses.ScrollPanel} style={{ flex: 1, minHeight: 0, overflowY: "auto", ...style }}>
      {children}
    </div>
  );
});

// Button ids used for the footer hints of the scroll window; the preview shows no footer.
export const GamepadButton = { DIR_UP: 1, DIR_DOWN: 2 };

// --- modal dialog ---------------------------------------------------------------------------------

interface ConfirmModalMockProps {
  strTitle?: ReactNode;
  strDescription?: ReactNode;
  strOKButtonText?: ReactNode;
  strCancelButtonText?: ReactNode;
  onOK?: () => void;
  closeModal?: () => void;
}

export function ConfirmModal({ strTitle, strDescription, strOKButtonText, strCancelButtonText, onOK, closeModal }: ConfirmModalMockProps) {
  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
      <div style={{ background: "#23262e", color: "#fff", padding: "24px", width: "420px", maxWidth: "90vw", borderRadius: "4px", fontSize: "14px" }}>
        <div style={{ fontSize: "18px", marginBottom: "12px" }}>{strTitle}</div>
        <div style={{ marginBottom: "20px", lineHeight: 1.4 }}>{strDescription}</div>
        <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
          <button onClick={() => closeModal?.()}>{strCancelButtonText ?? "Cancel"}</button>
          <button
            onClick={() => {
              onOK?.();
              closeModal?.();
            }}
          >
            {strOKButtonText}
          </button>
        </div>
      </div>
    </div>
  );
}

// Renders the modal into its own root, like Steam does, and hands it a function that closes it.
export const showModal = (modal: ReactElement) => {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  const close = () => {
    root.unmount();
    host.remove();
  };
  root.render(cloneElement(modal as ReactElement<{ closeModal?: () => void }>, { closeModal: close }));
  return { Close: close };
};
