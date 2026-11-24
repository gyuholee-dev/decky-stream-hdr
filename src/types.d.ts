declare module "*.svg" {
  const content: string;
  export default content;
}

declare module "*.png" {
  const content: string;
  export default content;
}

declare module "*.jpg" {
  const content: string;
  export default content;
}

// Filled in at build time from package.json (see the webpack configs).
declare const __PLUGIN_VERSION__: string;
declare const __PLUGIN_AUTHOR__: string;
declare const __PLUGIN_LICENSE__: string;
declare const __REPO_URL__: string;
