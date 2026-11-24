import { PanelSection, PanelSectionRow } from "@decky/ui";
import { definePlugin } from "@decky/api";
import { useEffect, useState } from "react";
import { FaTv } from "react-icons/fa";

import { ping } from "./api";
import { strings } from "./strings";

function Content() {
  const [connected, setConnected] = useState<boolean | undefined>();

  useEffect(() => {
    ping()
      .then((reply) => setConnected(reply === "pong"))
      .catch(() => setConnected(false));
  }, []);

  return (
    <PanelSection title={strings.sectionTitle}>
      <PanelSectionRow>
        <div>
          {connected === undefined
            ? strings.scaffoldNote
            : connected
              ? strings.backendOk
              : strings.backendError}
        </div>
      </PanelSectionRow>
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
