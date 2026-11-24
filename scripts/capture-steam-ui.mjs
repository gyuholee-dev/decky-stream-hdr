// Captures the real Steam gamepad UI styles from a running Steam client, for the browser preview.
//
// Steam's UI is not available outside Steam, and its CSS class names are hashed and change between
// Steam versions, so the preview reads them from the device instead of guessing. Read-only: it only
// evaluates scripts in Steam's pages that read class names and style rules, and fetches the fonts.
//
// 1. Open a tunnel to the device's Steam debugging port (leave it running in another terminal):
//      ssh -N -L 8080:localhost:8080 <user>@<device>
// 2. Open the Decky quick access menu on the device (optionally the plugin page you want to compare).
// 3. yarn capture
//
// Output goes to preview/steam-ui/, which is git-ignored: it contains Valve's CSS and fonts and is
// only for local use. Needs Node 22+ (global fetch and WebSocket).
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const outDir = path.join(root, "preview", "steam-ui");
const port = process.env.STEAM_DEBUG_PORT ?? "8080";
const base = `http://localhost:${port}`;

async function listPages() {
  try {
    return await (await fetch(`${base}/json`)).json();
  } catch {
    throw new Error(
      `Cannot reach Steam's debugging port at ${base}. Open the tunnel first:\n` +
        "  ssh -N -L 8080:localhost:8080 <user>@<device>",
    );
  }
}

async function evaluate(pages, titlePrefix, expression) {
  const page = pages.find((entry) => entry.title.startsWith(titlePrefix));
  if (!page) {
    throw new Error(`Steam page "${titlePrefix}" not found. Pages: ${pages.map((entry) => entry.title).join(", ")}`);
  }
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.onopen = resolve;
    socket.onerror = () => reject(new Error("Could not open the debugging connection."));
  });
  const reply = await new Promise((resolve) => {
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.id === 1) resolve(message);
    };
    socket.send(
      JSON.stringify({ id: 1, method: "Runtime.evaluate", params: { expression, returnByValue: true, awaitPromise: true } }),
    );
  });
  socket.close();
  if (reply.result?.exceptionDetails) throw new Error(JSON.stringify(reply.result.exceptionDetails));
  return reply.result?.result?.value;
}

const classMapsScript = `(() => {
  const dfl = window.DFL;
  if (!dfl) return JSON.stringify(null);
  const maps = {};
  for (const [name, value] of Object.entries(dfl)) {
    if (!/Classes$/.test(name) || !value || typeof value !== "object") continue;
    maps[name] = Object.fromEntries(Object.entries(value).filter(([, v]) => typeof v === "string"));
  }
  return JSON.stringify(maps);
})()`;

const stylesScript = `(() => {
  const out = [];
  for (const sheet of document.styleSheets) {
    try {
      out.push(Array.from(sheet.cssRules).map((rule) => rule.cssText).join("\\n"));
    } catch (error) {
      // cross-origin sheets cannot be read; skip them
    }
  }
  return out.join("\\n");
})()`;

const fontScript = (url) => `(async () => {
  const response = await fetch(${JSON.stringify(url)});
  const bytes = new Uint8Array(await response.arrayBuffer());
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(binary);
})()`;

const pages = await listPages();

const classMaps = JSON.parse(await evaluate(pages, "SharedJSContext", classMapsScript));
if (!classMaps) {
  throw new Error("Decky's UI library (DFL) is not available in Steam. Is Decky Loader running?");
}

let css = await evaluate(pages, "QuickAccess", stylesScript);

// Fonts are served by Steam itself; copy them next to the CSS so the preview text looks the same.
mkdirSync(path.join(outDir, "fonts"), { recursive: true });
const fontUrls = [...new Set([...css.matchAll(/url\("(\/custom_fonts\/[^"]+)"\)/g)].map((match) => match[1]))];
let fontCount = 0;
for (const url of fontUrls) {
  try {
    const encoded = await evaluate(pages, "QuickAccess", fontScript(url));
    const name = url.split("?").pop().replace(/[^A-Za-z0-9._-]/g, "_") + ".ttf";
    writeFileSync(path.join(outDir, "fonts", name), Buffer.from(encoded, "base64"));
    css = css.split(`url("${url}")`).join(`url("/fonts/${name}")`);
    fontCount += 1;
  } catch (error) {
    console.warn(`Skipped font ${url}: ${error.message}`);
  }
}

const version = await (await fetch(`${base}/json/version`)).json();
writeFileSync(path.join(outDir, "classes.json"), JSON.stringify(classMaps, null, 2));
writeFileSync(path.join(outDir, "steam.css"), css);
writeFileSync(
  path.join(outDir, "meta.json"),
  JSON.stringify({ capturedAt: new Date().toISOString(), browser: version.Browser, fonts: fontCount }, null, 2),
);

console.log(
  `Captured ${Object.keys(classMaps).length} class maps, ${(css.length / 1e6).toFixed(1)} MB of CSS and ${fontCount} fonts into preview/steam-ui/`,
);
