// Browser preview of the plugin panel (yarn serve, or yarn start to open the browser too). Steam's own UI modules are not available
// outside Steam, so @decky/ui and @decky/api are replaced by small stand-ins under preview/mocks.
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import HtmlWebpackPlugin from "html-webpack-plugin";
import webpack from "webpack";

const root = path.dirname(fileURLToPath(import.meta.url));
const pkg = JSON.parse(readFileSync(path.join(root, "package.json"), "utf-8"));

// Steam's real UI styles, captured from a device with `yarn capture`. Without a capture the preview
// falls back to a rough approximation.
const captured = path.join(root, "preview", "steam-ui");
const hasCapture = existsSync(path.join(captured, "classes.json")) && existsSync(path.join(captured, "steam.css"));
const steamUi = hasCapture ? captured : path.join(root, "preview", "steam-ui-fallback");
if (!hasCapture) {
  console.warn("[preview] No Steam UI capture found: using the approximate look. Run `yarn capture` for the real one.");
}

// Values from package.json that the plugin shows on its info page.
const pluginInfo = new webpack.DefinePlugin({
  __PLUGIN_VERSION__: JSON.stringify(pkg.version),
  __PLUGIN_AUTHOR__: JSON.stringify(pkg.author),
  __PLUGIN_LICENSE__: JSON.stringify(pkg.license),
  __REPO_URL__: JSON.stringify(pkg.repository.url.replace(/^git\+/, "").replace(/\.git$/, "")),
});

export default {
  mode: "development",
  target: "web",
  entry: "./preview/main.tsx",
  devtool: "eval-source-map",
  output: {
    path: path.join(root, "release", "preview"),
    clean: true,
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
    alias: {
      "@decky/ui": path.join(root, "preview", "mocks", "decky-ui.tsx"),
      "@decky/api": path.join(root, "preview", "mocks", "decky-api.ts"),
      "steam-ui-classes": path.join(steamUi, "classes.json"),
      "steam-ui.css": path.join(steamUi, "steam.css"),
    },
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        exclude: /node_modules/,
        loader: "ts-loader",
        options: { transpileOnly: true },
      },
      // Material icons are imported as raw SVG text.
      { test: /\.svg$/, type: "asset/source" },
      // url: false keeps Steam's own url(...) references (fonts) untouched; the dev server serves them.
      { test: /\.css$/, use: ["style-loader", { loader: "css-loader", options: { url: false } }] },
    ],
  },
  plugins: [new HtmlWebpackPlugin({ template: "./preview/index.html" }), pluginInfo],
  devServer: { port: 5173, hot: true, open: false, static: { directory: steamUi } },
  performance: { hints: false },
};
