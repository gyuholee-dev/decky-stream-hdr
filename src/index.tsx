import { PanelSection, PanelSectionRow, ToggleField } from "@decky/ui";
import { definePlugin } from "@decky/api";
import { useEffect, useState } from "react";
import { FaTv } from "react-icons/fa";

import { getStatus, setHdrEnabled, Status } from "./api";
import { strings } from "./strings";

function Content() {
  const [status, setStatus] = useState<Status | undefined>();
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    getStatus()
      .then(setStatus)
      .catch(() => setFailed(true));
  }, []);

  if (failed) {
    return (
      <PanelSection title={strings.sectionTitle}>
        <PanelSectionRow>
          <div>{strings.statusUnavailable}</div>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  if (!status) {
    return (
      <PanelSection title={strings.sectionTitle}>
        <PanelSectionRow>
          <div>{strings.statusLoading}</div>
        </PanelSectionRow>
      </PanelSection>
    );
  }

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
    </PanelSection>
  );
}

export default definePlugin(() => {
  return {
    name: strings.pluginName,
    titleView: <div>{strings.pluginName}</div>,
    content: <Content />,
    icon: <FaTv />,
    onDismount() {},
  };
});
