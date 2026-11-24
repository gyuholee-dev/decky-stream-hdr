import { useEffect, useState } from "react";

import { getStatus } from "./api";
import { strings } from "./strings";

// Asks the backend now and then whether a stream is running and whether HDR is being requested.
function useStreamingState() {
  const [state, setState] = useState({ streaming: false, hdrActive: false });

  useEffect(() => {
    let alive = true;
    const poll = () =>
      getStatus()
        .then((status) => alive && setState({ streaming: status.streaming, hdrActive: status.hdr_active }))
        .catch(() => undefined);
    poll();
    const timer = setInterval(poll, 2000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);

  return state;
}

// The panel's header: the plugin name and, while a stream is running, a badge on the right that says
// whether HDR is being requested ("HDR") or not ("SDR").
export function TitleView() {
  const { streaming, hdrActive } = useStreamingState();

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
      <span>{strings.pluginName}</span>
      {streaming && (
        <span
          style={{
            padding: "2px 8px",
            borderRadius: "4px",
            fontSize: "12px",
            fontWeight: 700,
            letterSpacing: "0.5px",
            background: hdrActive ? "#1a9fff" : "rgba(255, 255, 255, 0.15)",
            color: hdrActive ? "#ffffff" : "#dcdedf",
          }}
        >
          {hdrActive ? "HDR" : "SDR"}
        </span>
      )}
    </div>
  );
}
