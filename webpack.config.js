// Production build of the plugin frontend: dist/index.js, an ES module with a default export.
// Decky Loader evaluates it inside Steam, where React and @decky/ui already exist as globals,
// so those are not bundled. The globals and the output format match what Decky expects.
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import webpack from "webpack";

const root = path.dirname(fileURLToPath(import.meta.url));
const manifest = JSON.parse(readFileSync(path.join(root, "plugin.json"), "utf-8"));
const pkg = JSON.parse(readFileSync(path.join(root, "package.json"), "utf-8"));

// Values from package.json that the plugin shows on its info page.
const pluginInfo = new webpack.DefinePlugin({
  __PLUGIN_VERSION__: JSON.stringify(pkg.version),
  __PLUGIN_AUTHOR__: JSON.stringify(pkg.author),
  __PLUGIN_LICENSE__: JSON.stringify(pkg.license),
  __REPO_URL__: JSON.stringify(pkg.repository.url.replace(/^git\+/, "").replace(/\.git$/, "")),
});

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
    alias: {
      "@decky/manifest": path.join(root, "plugin.json"),
      // The options (ranges, steps, defaults) are shared with the backend.
      "streamhdr-options": path.join(root, "py_modules", "streamhdr", "options.json"),
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
    ],
  },
  plugins: [pluginInfo],
  // Keep the output readable for debugging on the device.
  optimization: { minimize: false },
  performance: { hints: false },
};
