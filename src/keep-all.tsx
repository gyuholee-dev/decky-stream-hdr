import type { ReactNode } from "react";

// Korean and similar languages are broken between words, not inside them (Steam's own style would
// split a word at the end of a line). Very long unbreakable text such as a path still wraps.
export function KeepAll({ children }: { children: ReactNode }) {
  return <span style={{ wordBreak: "keep-all", overflowWrap: "anywhere" }}>{children}</span>;
}
