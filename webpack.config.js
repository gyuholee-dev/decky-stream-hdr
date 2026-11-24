// Production build of the plugin frontend: dist/index.js, an ES module with a default export.
// Decky Loader evaluates it inside Steam, where React and @decky/ui already exist as globals,
// so those are not bundled. The globals and the output format match what Decky expects.
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(fileURLToPath(import.meta.url));
const manifest = JSON.parse(readFileSync(path.join(root, "plugin.json"), "utf-8"));

export default {
  mode: "production",
  target: "web",
  entry: "./src/index.tsx",
  devtool: "source-map",
  experiments: { outputModule: true },
  output: {
    path: path.join(root, "dist"),
    filename: "index.js",
    clean: true,
    module: true,
    chunkFormat: "module",
    library: { type: "module" },
    // Lets Decky's dev tools map stack traces back to the plugin sources.
    devtoolModuleFilenameTemplate: (info) =>
      `decky://decky/plugin/${encodeURIComponent(manifest.name)}/${info.resourcePath.replace(/^\.\//, "")}`,
  },
  externalsType: "window",
  externals: {
    react: "SP_REACT",
    "react/jsx-runtime": "SP_JSX",
    "react-dom": "SP_REACTDOM",
    "@decky/ui": "DFL",
  },
  resolve: {
    extensions: [".tsx", ".ts", ".js"],
    // @decky/api reads the plugin name from this module.
    alias: { "@decky/manifest": path.join(root, "plugin.json") },
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
    ],
  },
  // Keep the output readable for debugging on the device.
  optimization: { minimize: false },
  performance: { hints: false },
};
