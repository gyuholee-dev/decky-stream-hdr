// Browser preview of the plugin panel (yarn serve, or yarn start to open the browser too). Steam's own UI modules are not available
// outside Steam, so @decky/ui and @decky/api are replaced by small stand-ins under preview/mocks.
import path from "node:path";
import { fileURLToPath } from "node:url";

import HtmlWebpackPlugin from "html-webpack-plugin";

const root = path.dirname(fileURLToPath(import.meta.url));

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
      { test: /\.css$/, use: ["style-loader", "css-loader"] },
    ],
  },
  plugins: [new HtmlWebpackPlugin({ template: "./preview/index.html" })],
  devServer: { port: 5173, hot: true, open: false },
  performance: { hints: false },
};
