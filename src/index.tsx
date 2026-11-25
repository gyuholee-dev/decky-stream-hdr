import { ButtonItem, ConfirmModal, Field, Navigation, PanelSection, PanelSectionRow, showModal } from "@decky/ui";
import { definePlugin, routerHook } from "@decky/api";
import { useEffect, useRef } from "react";

import { resetSettings, Status } from "./api";
import { TitleView } from "./header";
import { InfoIcon, StreamIcon } from "./icon";
import { infoRoute, InfoPage } from "./info-page";
import { KeepAll } from "./keep-all";
import { Notice, NoticeTone } from "./notice";
import { OptionSlider, OptionToggle } from "./option-fields";
import { useStatus } from "./status";
import { ErrorInfo, errorText, strings } from "./strings";

// Steam scrolls a focused row into view only until its top edge shows, which leaves the last rows half
// hidden behind the bottom bar. Keeping this much space clear below a focused row fixes that.
const SCROLL_PADDING = "16px";

// The "Plugin Info" row at the bottom of the panel: a small line of text with an icon that opens the
// info page (the repository link is on that page). It is a plain row, not a full-size button, and is
// only highlighted when it has focus.
function Footer({ onRequest }: { onRequest: (request: Promise<Status>) => void }) {
  const confirmReset = () =>
    showModal(
      <ConfirmModal
        strTitle={strings.resetTitle}
        strDescription={<KeepAll>{strings.resetDescription}</KeepAll>}
        strOKButtonText={strings.resetConfirmButton}
        strCancelButtonText={strings.cancelButton}
        onOK={() => onRequest(resetSettings())}
      />,
    );

  return (
    <>
      <PanelSectionRow>
        <Field
          focusable
          bottomSeparator="none"
          onActivate={() => Navigation.Navigate(infoRoute)}
          onClick={() => Navigation.Navigate(infoRoute)}
          description={
            <span style={{ display: "flex", justifyContent: "center", alignItems: "center", fontSize: "12px" }}>
              <span style={{ display: "inline-flex", marginRight: "5px" }}>
                <InfoIcon />
              </span>
              {strings.infoButton}
            </span>
          }
        />
      </PanelSectionRow>
      <PanelSectionRow>
        <ButtonItem layout="below" onClick={confirmReset}>
          {strings.resetButton}
        </ButtonItem>
      </PanelSectionRow>
    </>
  );
}

function Message({ text, tone }: { text: string; tone: NoticeTone }) {
  return (
    <PanelSection>
      <PanelSectionRow>
        <Notice tone={tone}>{text}</Notice>
      </PanelSectionRow>
    </PanelSection>
  );
}

function Panel() {
  const { status, failed, send, change } = useStatus();

  if (failed) return <Message tone="error" text={strings.statusUnavailable} />;
  if (!status) return <Message tone="info" text={strings.statusLoading} />;

  const field = { status, change };
  // Problems come first, right under the header, each in its own red box; while a stream runs a blue box says
  // why two of the options cannot be changed.
  const problems = [status.error, status.paper_white_error, status.look_error].filter((error): error is ErrorInfo => error !== null);

  return (
    <>
      <PanelSection>
        {problems.map((error, index) => (
          <PanelSectionRow key={index}>
            <Notice tone="error">{strings.errorPrefix + errorText(error)}</Notice>
          </PanelSectionRow>
        ))}
        {status.streaming && (
          <PanelSectionRow>
            <Notice tone="info">{strings.streamingNotice}</Notice>
          </PanelSectionRow>
        )}
        <OptionToggle {...field} label={strings.hdrToggleLabel} description={strings.hdrToggleDescription} />
        <OptionSlider {...field} name="paper_white" suffix=" nits" label={strings.paperWhiteLabel} description={strings.paperWhiteDescription} />
        <OptionSlider {...field} name="contrast" suffix="%" label={strings.contrastLabel} description={strings.contrastDescription} />
        <OptionSlider {...field} name="gamma" label={strings.gammaLabel} description={strings.gammaDescription} />
        <OptionSlider {...field} name="saturation" suffix="%" label={strings.saturationLabel} description={strings.saturationDescription} />
        <Footer onRequest={send} />
      </PanelSection>
    </>
  );
}

// Sets the scroll padding on the panel's scrolling container while the panel is shown.
function ScrollPadding() {
  const marker = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    let element: HTMLElement | null = marker.current?.parentElement ?? null;
    while (element && !/(auto|scroll)/.test(getComputedStyle(element).overflowY)) element = element.parentElement;
    if (!element) return;
    const scroller = element;
    const previous = scroller.style.scrollPaddingBottom;
    scroller.style.scrollPaddingBottom = SCROLL_PADDING;
    return () => {
      scroller.style.scrollPaddingBottom = previous;
    };
  }, []);
  // Steam leaves 24px under every panel section and draws a line under its last row. Here the panel ends 16px
  // under the last button instead: the row already has 10px of padding, and 6px more goes on the section.
  return (
    <>
      <style>
        {/* The section's own bottom margin, and the line Steam draws under its last row. */
        ".streamhdr-marker + * { margin-bottom: 0 !important; padding-bottom: 6px !important; } .streamhdr-marker + * > :last-child > :last-child::after { display: none !important; }"}
      </style>
      <span ref={marker} className="streamhdr-marker" style={{ display: "none" }} />
    </>
  );
}

function Content() {
  return (
    <>
      <ScrollPadding />
      <Panel />
    </>
  );
}

export default definePlugin(() => {
  routerHook.addRoute(infoRoute, () => <InfoPage />, { exact: true });

  return {
    name: strings.pluginName,
    titleView: <TitleView />,
    content: <Content />,
    icon: <StreamIcon />,
    onDismount() {
      routerHook.removeRoute(infoRoute);
    },
  };
});
