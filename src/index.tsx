import { Field, Navigation, PanelSection, PanelSectionRow, SliderField, ToggleField } from "@decky/ui";
import { definePlugin, routerHook } from "@decky/api";
import { ReactNode, useEffect, useState } from "react";

import { getStatus, setContrast, setGamma, setHdrEnabled, setPaperWhite, setSaturation, Status } from "./api";
import { TitleView } from "./header";
import { InfoIcon, StreamIcon } from "./icon";
import { infoRoute, InfoPage } from "./info-page";
import { errorText, strings } from "./strings";

const PAPER_WHITE_MIN = 80;
const PAPER_WHITE_MAX = 480;
const PAPER_WHITE_STEP = 10;
const PAPER_WHITE_DEFAULT = 200;

const CONTRAST_MIN = 0;
const CONTRAST_MAX = 200;
const CONTRAST_STEP = 5;
const CONTRAST_DEFAULT = 100;

// Gamma is stored in hundredths (100 means 1.00); the slider shows the plain number.
const GAMMA_MIN = 50;
const GAMMA_MAX = 200;
const GAMMA_STEP = 10;
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
function Footer() {
  return (
    <PanelSection>
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
    </PanelSection>
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

function Content() {
  const [status, setStatus] = useState<Status | undefined>();
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    getStatus()
      .then(setStatus)
      .catch(() => setFailed(true));
  }, []);

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
            onChange={(enabled: boolean) => {
              setHdrEnabled(enabled)
                .then(setStatus)
                .catch(() => setFailed(true));
            }}
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
            min={PAPER_WHITE_MIN}
            max={PAPER_WHITE_MAX}
            step={PAPER_WHITE_STEP}
            resetValue={PAPER_WHITE_DEFAULT}
            showValue
            valueSuffix=" nits"
            onChange={(nits: number) => {
              setStatus({ ...status, paper_white: nits });
              setPaperWhite(nits)
                .then(setStatus)
                .catch(() => setFailed(true));
            }}
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
            onChange={(percent: number) => {
              setStatus({ ...status, contrast: percent });
              setContrast(percent)
                .then(setStatus)
                .catch(() => setFailed(true));
            }}
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
              setStatus({ ...status, gamma: hundredths });
              setGamma(hundredths)
                .then(setStatus)
                .catch(() => setFailed(true));
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
            onChange={(percent: number) => {
              // Show the new value at once; the backend reply replaces it with the stored one.
              setStatus({ ...status, saturation: percent });
              setSaturation(percent)
                .then(setStatus)
                .catch(() => setFailed(true));
            }}
          />
        </PanelSectionRow>
        {status.look_error && (
          <PanelSectionRow>
            <KeepAll>{strings.errorPrefix + errorText(status.look_error)}</KeepAll>
          </PanelSectionRow>
        )}
      </PanelSection>
      <Footer />
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
