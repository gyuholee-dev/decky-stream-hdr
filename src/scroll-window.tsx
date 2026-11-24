import { Focusable, GamepadButton, ModalPosition, ScrollPanelGroup, gamepadDialogClasses, scrollPanelClasses } from "@decky/ui";
import { useLayoutEffect, useRef, useState } from "react";
import type { ReactNode } from "react";

// A page that scrolls with the gamepad. When the content is taller than the window, the window can take
// focus: moving the stick or d-pad first focuses the scrollbar (its thumb lights up), and then the stick
// or d-pad scrolls it. Steam's own scroll panel does the scrolling; this component makes the content
// focusable, shows a thin scrollbar and fills the space between Steam's top bar and bottom legend.
//
// The mechanism is the one other Decky plugins use for their info pages; the code is written for this project.
const CONTAINER_CLASS = "modal-position-container";
const BAR_WIDTH = "4px";

// Steam hides scrollbars by default. The thumb is dim until the window has focus, then it lights up.
const css = `
.${CONTAINER_CLASS} .${gamepadDialogClasses.ModalPosition} { top: 0; bottom: 0; padding: 0; }
.${CONTAINER_CLASS} .${scrollPanelClasses.ScrollPanel}::-webkit-scrollbar { display: initial !important; width: ${BAR_WIDTH}; }
.${CONTAINER_CLASS} .${scrollPanelClasses.ScrollPanel}::-webkit-scrollbar-thumb { border: 0; }
.${CONTAINER_CLASS} .${scrollPanelClasses.ScrollPanel}.gpfocuswithin::-webkit-scrollbar-thumb { background-color: currentColor; }
`;

export function ScrollWindow({ children, onCancel }: { children: ReactNode; onCancel?: (event: CustomEvent) => void }) {
  const panelRef = useRef<HTMLElement>(null);
  const [overflowing, setOverflowing] = useState(false);

  // The content is only a focus target when there is something to scroll.
  useLayoutEffect(() => {
    const panel = panelRef.current;
    if (panel) setOverflowing(panel.scrollHeight > panel.clientHeight);
  }, [children]);

  const panel = (
    <ScrollPanelGroup {...({ ref: panelRef, focusable: false, style: { flex: 1, minHeight: 0 } } as object)}>
      <Focusable
        {...({ focusable: overflowing } as object)}
        noFocusRing
        onCancel={onCancel}
        actionDescriptionMap={overflowing ? { [GamepadButton.DIR_UP]: "Scroll Up", [GamepadButton.DIR_DOWN]: "Scroll Down" } : undefined}
      >
        {children}
      </Focusable>
    </ScrollPanelGroup>
  );

  return (
    // Steam publishes the heights of its top bar and bottom legend as variables.
    <div style={{ display: "flex", height: "-webkit-fill-available", margin: "var(--basicui-header-height, 40px) 0 var(--gamepadui-current-footer-height, 42px)" }}>
      <style>{css}</style>
      <div className={CONTAINER_CLASS} style={{ position: "relative", flex: 1 }}>
        {overflowing ? (
          <ModalPosition>{panel}</ModalPosition>
        ) : (
          <div className={`${gamepadDialogClasses.ModalPosition} ${gamepadDialogClasses.WithStandardPadding} Panel`}>{panel}</div>
        )}
      </div>
    </div>
  );
}
