import { useStatus } from "./status";
import { strings } from "./strings";

// The panel's header: the plugin name and, while a stream is running, a badge on the right that says
// whether HDR is being requested ("HDR") or not ("SDR").
export function TitleView() {
  const { status } = useStatus();
  const streaming = status?.streaming ?? false;
  const hdrActive = status?.hdr_active ?? false;

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
