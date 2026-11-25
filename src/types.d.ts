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

// The options shared with the backend: py_modules/streamhdr/options.json (see options.py for what the fields mean).
declare module "streamhdr-options" {
  export interface OptionSpec {
    min: number;
    max: number;
    step: number;
    default: number;
    neutral?: number;
    scale?: number;
    frozenWhileStreaming?: boolean;
  }
  export interface ToggleSpec {
    default: boolean;
    frozenWhileStreaming?: boolean;
  }
  const options: {
    hdr_enabled: ToggleSpec;
    paper_white: OptionSpec;
    contrast: OptionSpec;
    gamma: OptionSpec;
    saturation: OptionSpec;
  };
  export default options;
}
