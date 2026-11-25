import { KeepAll } from "./keep-all";
import type { ReactNode } from "react";

export type NoticeTone = "error" | "info";

// A tinted box: red for a problem, blue for something the user should know.
const TONES: Record<NoticeTone, { background: string; color: string }> = {
  error: { background: "rgba(229, 72, 77, 0.16)", color: "#ffdadb" },
  info: { background: "rgba(26, 159, 255, 0.16)", color: "#d6ecff" },
};

export function Notice({ tone, children }: { tone: NoticeTone; children: ReactNode }) {
  const { background, color } = TONES[tone];
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      style={{
        boxSizing: "border-box",
        width: "100%",
        padding: "8px 10px",
        borderRadius: "4px",
        background,
        color,
        fontSize: "12px",
        lineHeight: 1.4,
      }}
    >
      <KeepAll>{children}</KeepAll>
    </div>
  );
}
