import { PanelSection, PanelSectionRow, SliderField, ToggleField } from "@decky/ui";
import { definePlugin } from "@decky/api";
import { useEffect, useState } from "react";

import { getStatus, setHdrEnabled, setSaturation, Status } from "./api";
import { StreamIcon } from "./icon";
import { strings } from "./strings";

const SATURATION_MIN = 0;
const SATURATION_MAX = 200;
const SATURATION_STEP = 10;
const SATURATION_DEFAULT = 100;

function Message({ text }: { text: string }) {
  return (
    <PanelSection title={strings.sectionTitle}>
      <PanelSectionRow>
        <div>{text}</div>
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
    <PanelSection title={strings.sectionTitle}>
      <PanelSectionRow>
        <ToggleField
          label={strings.hdrToggleLabel}
          description={strings.hdrToggleDescription}
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
          <div>{strings.errorPrefix + status.error}</div>
        </PanelSectionRow>
      )}
      <PanelSectionRow>
        <SliderField
          label={strings.saturationLabel}
          description={strings.saturationDescription}
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
      {status.saturation_error && (
        <PanelSectionRow>
          <div>{strings.errorPrefix + status.saturation_error}</div>
        </PanelSectionRow>
      )}
    </PanelSection>
  );
}

export default definePlugin(() => {
  return {
    name: strings.pluginName,
    titleView: <div>{strings.pluginName}</div>,
    content: <Content />,
    icon: <StreamIcon />,
    onDismount() {},
  };
});
