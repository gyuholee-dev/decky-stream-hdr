import { useState, useSyncExternalStore } from "react";
import { createRoot } from "react-dom/client";

import plugin from "../src/index";
import { strings } from "../src/strings";
import { knobs, patchState } from "./backend";
import { router } from "./router";
import "./setup";
import "steam-ui.css";
import "./preview.css";
import { cx, real } from "./mocks/steam";

const errorCodes = Object.keys(strings.errors);

// The preview renders the same `content` element the plugin hands to Decky.
function Preview() {
  // Changing a knob remounts the panel so that it fetches the new state, like reopening it.
  const [remountKey, setRemountKey] = useState(0);
  const [unreachable, setUnreachable] = useState(knobs.unreachable);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState("");
  const [saturationError, setSaturationError] = useState("");
  const [latency, setLatency] = useState(knobs.latencyMs);

  const remount = () => setRemountKey((key) => key + 1);
  const routePath = useSyncExternalStore(router.subscribe, router.currentPath);
  const RoutePage = useSyncExternalStore(router.subscribe, router.currentComponent);

  return (
    <div className="page">
      <div className={cx("qam", real && "real", real && "BasicUI")}>
        <div className="qam-title">{plugin.titleView}</div>
        <div key={remountKey}>{plugin.content}</div>
      </div>

      {RoutePage && (
        <div className="page-window">
          <div className="page-window-bar">
            <button type="button" onClick={router.back}>
              Back
            </button>
            <span>{routePath}</span>
          </div>
          <div className="page-window-body">
            <RoutePage />
          </div>
        </div>
      )}

      <aside className="dev">
        <div className="note">
          Icon in the Decky plugin list: <span className="qam-icon">{plugin.icon}</span>
        </div>
        <h2>Preview controls</h2>
        <p className="note">
          These controls only exist in the browser preview. They change what the stand-in backend
          replies, so every panel state can be styled without a device.
        </p>
        <label>
          <input
            type="checkbox"
            checked={unreachable}
            onChange={(event) => {
              knobs.unreachable = event.target.checked;
              setUnreachable(event.target.checked);
              remount();
            }}
          />
          Backend unreachable
        </label>
        <label>
          <input
            type="checkbox"
            checked={streaming}
            onChange={(event) => {
              // Like a real stream starting: the panel is not reopened, it hears about it as an event.
              patchState({ streaming: event.target.checked });
              setStreaming(event.target.checked);
            }}
          />
          Streaming now
        </label>
        <label>
          HDR problem
          <select
            value={error}
            onChange={(event) => {
              patchState({ error: event.target.value ? { code: event.target.value, detail: "sample detail" } : null });
              setError(event.target.value);
              remount();
            }}
          >
            <option value="">none</option>
            {errorCodes.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>
        </label>
        <label>
          Color adjustment problem
          <select
            value={saturationError}
            onChange={(event) => {
              patchState({ look_error: event.target.value ? { code: event.target.value, detail: "sample detail" } : null });
              setSaturationError(event.target.value);
              remount();
            }}
          >
            <option value="">none</option>
            {errorCodes.map((code) => (
              <option key={code} value={code}>
                {code}
              </option>
            ))}
          </select>
        </label>
        <p className="note">Add ?lang=koreana to the address to try another language.</p>
        <label>
          Backend latency: {latency} ms
          <input
            type="range"
            min={0}
            max={2000}
            step={50}
            value={latency}
            onChange={(event) => {
              knobs.latencyMs = Number(event.target.value);
              setLatency(Number(event.target.value));
            }}
          />
        </label>
        <button type="button" onClick={remount}>
          Reopen panel
        </button>
      </aside>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<Preview />);
