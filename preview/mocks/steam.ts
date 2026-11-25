// Small helpers shared by the mock components.
import { useState } from "react";

export const cx = (...names: Array<string | false | undefined>) => names.filter(Boolean).join(" ");

// Steam marks the focused element with a highlight; this mimics it. Steam shows it for gamepad and keyboard
// navigation, not when the mouse clicks, so only focus that the browser considers keyboard focus
// (:focus-visible) counts.
export function useFocus() {
  const [focused, setFocused] = useState(false);
  return {
    focused,
    bind: {
      onFocus: (event: { currentTarget: Element }) => setFocused(event.currentTarget.matches(":focus-visible")),
      onBlur: () => setFocused(false),
    },
  };
}
