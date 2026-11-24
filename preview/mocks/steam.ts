// Access to Steam's real class names (captured from a device with `yarn capture`).
// Without a capture every lookup is empty and the components fall back to the approximate look.
import { useState } from "react";

import classes from "steam-ui-classes";

type ClassMaps = Record<string, Record<string, string>>;
const maps = classes as ClassMaps;

export const real = Object.keys(maps).length > 0;

const lookup = (map: string) => (key: string) => maps[map]?.[key] ?? "";
export const dialog = lookup("gamepadDialogClasses");
export const slider = lookup("gamepadSliderClasses");
export const controls = lookup("quickAccessControlsClasses");
export const menu = lookup("quickAccessMenuClasses");

export const cx = (...names: Array<string | false | undefined>) => names.filter(Boolean).join(" ");

// Steam marks the focused element with gpfocus / gpfocuswithin; this mimics it for mouse and keyboard focus.
export function useFocus() {
  const [focused, setFocused] = useState(false);
  return { focused, bind: { onFocus: () => setFocused(true), onBlur: () => setFocused(false) } };
}
