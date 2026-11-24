import { Focusable, ModalPosition, ScrollPanelGroup, gamepadDialogClasses, scrollPanelClasses } from "@decky/ui";
import { useLayoutEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

// A page that scrolls with the gamepad. When the content is taller than the window, the window can take
// focus: moving the stick or d-pad first focuses the scrollbar (its thumb lights up), and then the stick
// or d-pad scrolls it. Steam's own scroll panel does the actual scrolling; this component makes it
// focusable, shows a thin scrollbar and keeps the page between Steam's top bar and bottom legend.
//
// The idea follows how other Decky plugins build their info pages; the code is written for this project.
const ROOT_CLASS = "streamhdr-scroll-window";
const BAR_WIDTH = "4px";

// Steam hides scrollbars by default. The thumb is dim until the window has focus, then it lights up.
const style = () => `
.${ROOT_CLASS} .${scrollPanelClasses.ScrollPanel}::-webkit-scrollbar { display: initial !important; width: ${BAR_WIDTH}; }
.${ROOT_CLASS} .${scrollPanelClasses.ScrollPanel}::-webkit-scrollbar-thumb { border: 0; background-color: rgba(255, 255, 255, 0.25); border-radius: 2px; }
.${ROOT_CLASS} .${scrollPanelClasses.ScrollPanel}.gpfocuswithin::-webkit-scrollbar-thumb { background-color: currentColor; }
`;

export function ScrollWindow({ children, onCancel }: { children: ReactNode; onCancel?: (event: CustomEvent) => void }) {
  const root = useRef<HTMLDivElement>(null);
  const [overflowing, setOverflowing] = useState(false);

  // The window is only a focus target when there is something to scroll.
  useLayoutEffect(() => {
    const measure = () => {
      const panel = root.current?.querySelector<HTMLElement>(`.${scrollPanelClasses.ScrollPanel}`);
      if (panel) setOverflowing(panel.scrollHeight > panel.clientHeight);
    };
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, [children]);

  const scrollPanel = (
    <Focusable noFocusRing {...({ focusable: overflowing } as object)} onCancel={onCancel} style={{ height: "100%" }}>
      {/* Steam's scroll group handles the gamepad scrolling; the group itself must not take focus. */}
      <ScrollPanelGroup {...({ focusable: false } as object)}>{children}</ScrollPanelGroup>
    </Focusable>
  );

  return (
    <div
      ref={root}
      className={ROOT_CLASS}
      style={{
        position: "relative",
        // Steam publishes the heights of its top bar and bottom legend as variables.
        margin: "var(--basicui-header-height, 40px) 0 var(--gamepadui-current-footer-height, 42px)",
        height: "calc(100% - var(--basicui-header-height, 40px) - var(--gamepadui-current-footer-height, 42px))",
      }}
    >
      <style>{style()}</style>
      {overflowing ? (
        <ModalPosition>{scrollPanel}</ModalPosition>
      ) : (
        <div className={`${gamepadDialogClasses.ModalPosition} ${gamepadDialogClasses.WithStandardPadding} Panel`}>{scrollPanel}</div>
      )}
    </div>
  );
}
