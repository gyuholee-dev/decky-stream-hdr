import { ButtonItem, ConfirmModal, Field, Navigation, PanelSection, PanelSectionRow, SliderField, ToggleField, showModal } from "@decky/ui";
import { definePlugin, routerHook } from "@decky/api";
import { ReactNode, useEffect, useRef } from "react";

import { resetSettings, setContrast, setGamma, setHdrEnabled, setPaperWhite, setSaturation, Status } from "./api";
import { TitleView } from "./header";
import { InfoIcon, StreamIcon } from "./icon";
import { infoRoute, InfoPage } from "./info-page";
import { useStatus } from "./status";
import { errorText, strings } from "./strings";

// Steam scrolls a focused row into view only until its top edge shows, which leaves the last rows half
// hidden behind the bottom bar. Keeping this much space clear below a focused row fixes that.
const SCROLL_PADDING = "16px";

const PAPER_WHITE_MIN = 80;
const PAPER_WHITE_MAX = 480;
const PAPER_WHITE_STEP = 10;
const PAPER_WHITE_DEFAULT = 230;

const CONTRAST_MIN = 0;
const CONTRAST_MAX = 200;
const CONTRAST_STEP = 5;
const CONTRAST_DEFAULT = 100;

// Gamma is stored in hundredths (100 means 1.00); the slider shows the plain number.
const GAMMA_MIN = 50;
const GAMMA_MAX = 200;
const GAMMA_STEP = 5;
const GAMMA_DEFAULT = 100;

const SATURATION_MIN = 0;
const SATURATION_MAX = 200;
const SATURATION_STEP = 5;
const SATURATION_DEFAULT = 100;

// Korean and similar languages are broken between words, not inside them (Steam's own style would
// split a word at the end of a line). Very long unbreakable text such as a path still wraps.
function KeepAll({ children }: { children: ReactNode }) {
  return <span style={{ wordBreak: "keep-all", overflowWrap: "anywhere" }}>{children}</span>;
}

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
            <span style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "10px", fontSize: "12px" }}>
              {strings.infoButton}
              <InfoIcon />
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

function Message({ text }: { text: string }) {
  return (
    <PanelSection>
      <PanelSectionRow>
        <KeepAll>{text}</KeepAll>
      </PanelSectionRow>
    </PanelSection>
  );
}

function Panel() {
  const { status, failed, send, change } = useStatus();

  if (failed) return <Message text={strings.statusUnavailable} />;
  if (!status) return <Message text={strings.statusLoading} />;

  return (
    <>
      <PanelSection>
        <PanelSectionRow>
          <ToggleField
            label={strings.hdrToggleLabel}
            description={<KeepAll>{strings.hdrToggleDescription}</KeepAll>}
            checked={status.hdr_enabled}
            disabled={status.streaming}
            onChange={(enabled: boolean) => change({ hdr_enabled: enabled }, setHdrEnabled(enabled))}
          />
        </PanelSectionRow>
        {status.error && (
          <PanelSectionRow>
            <KeepAll>{strings.errorPrefix + errorText(status.error)}</KeepAll>
          </PanelSectionRow>
        )}
        <PanelSectionRow>
          <SliderField
            label={strings.paperWhiteLabel}
            description={<KeepAll>{strings.paperWhiteDescription}</KeepAll>}
            value={status.paper_white}
            disabled={status.streaming}
            min={PAPER_WHITE_MIN}
            max={PAPER_WHITE_MAX}
            step={PAPER_WHITE_STEP}
            resetValue={PAPER_WHITE_DEFAULT}
            showValue
            valueSuffix=" nits"
            onChange={(nits: number) => change({ paper_white: nits }, setPaperWhite(nits))}
          />
        </PanelSectionRow>
        {status.paper_white_error && (
          <PanelSectionRow>
            <KeepAll>{strings.errorPrefix + errorText(status.paper_white_error)}</KeepAll>
          </PanelSectionRow>
        )}
        <PanelSectionRow>
          <SliderField
            label={strings.contrastLabel}
            description={<KeepAll>{strings.contrastDescription}</KeepAll>}
            value={status.contrast}
            min={CONTRAST_MIN}
            max={CONTRAST_MAX}
            step={CONTRAST_STEP}
            resetValue={CONTRAST_DEFAULT}
            showValue
            valueSuffix="%"
            onChange={(percent: number) => change({ contrast: percent }, setContrast(percent))}
          />
        </PanelSectionRow>
        <PanelSectionRow>
          <SliderField
            label={strings.gammaLabel}
            description={<KeepAll>{strings.gammaDescription}</KeepAll>}
            value={status.gamma / 100}
            min={GAMMA_MIN / 100}
            max={GAMMA_MAX / 100}
            step={GAMMA_STEP / 100}
            resetValue={GAMMA_DEFAULT / 100}
            showValue
            onChange={(gamma: number) => {
              const hundredths = Math.round(gamma * 100);
              change({ gamma: hundredths }, setGamma(hundredths));
            }}
          />
        </PanelSectionRow>
        <PanelSectionRow>
          <SliderField
            label={strings.saturationLabel}
            description={<KeepAll>{strings.saturationDescription}</KeepAll>}
            value={status.saturation}
            min={SATURATION_MIN}
            max={SATURATION_MAX}
            step={SATURATION_STEP}
            resetValue={SATURATION_DEFAULT}
            showValue
            valueSuffix="%"
            onChange={(percent: number) => change({ saturation: percent }, setSaturation(percent))}
          />
        </PanelSectionRow>
        {status.look_error && (
          <PanelSectionRow>
            <KeepAll>{strings.errorPrefix + errorText(status.look_error)}</KeepAll>
          </PanelSectionRow>
        )}
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
