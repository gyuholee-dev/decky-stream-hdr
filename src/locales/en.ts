// English texts. This is the reference language: every other language is checked against its keys,
// and any text a language does not provide falls back to the English one.
//
// Names of Steam's own options (for example "Use NVFBC capture on NVIDIA GPU") are written exactly as Steam's
// English interface shows them.
//
// Placeholders such as {detail} are replaced with values that cannot be translated, for example
// the output of a system tool.
export const en = {
  pluginName: "StreamHDR",
  hdrToggleLabel: "HDR Streaming",
  hdrToggleDescription:
    "Applies HDR to both encoding and rendering when you stream with Steam. See Plugin Info for the host and client settings.",
  paperWhiteLabel: "Paper White",
  paperWhiteDescription:
    "Sets the reference brightness used when rendering HDR. If your display peaks at 1000 nits, 230 nits is recommended.",
  contrastLabel: "Contrast",
  contrastDescription: "Adjusts the contrast of the HDR output. The default is recommended for OLED displays.",
  gammaLabel: "Gamma",
  gammaDescription: "Adjusts the gamma of the HDR output. For OLED displays, 0.85-1.00 is recommended.",
  saturationLabel: "Saturation",
  saturationDescription: "Adjusts the color saturation of the HDR output. For OLED displays, 125-135% is recommended.",
  infoButton: "Plugin Info",
  githubButton: "GitHub",
  resetButton: "Reset All Settings",
  resetTitle: "Reset All Settings",
  resetDescription: "Reset all settings to their defaults?",
  resetConfirmButton: "Reset",
  cancelButton: "Cancel",
  // Texts of the info page that the "Plugin Info" button opens.
  info: {
    aboutHeading: "About",
    about:
      "StreamHDR is a Decky plugin that brings BT.2020 PQ HDR streaming to Steam Remote Play. " +
      "On SteamOS, its derivatives and other Linux devices running Steam in Game Mode, as long as the device can handle HDR streaming, " +
      "the plugin steps into Steam's streaming process: it changes the HDR encoding request sent to the host and enables HDR rendering output on the client.",
    usageHeading: "Usage",
    usage: [
      "Turn on HDR Streaming in the plugin menu, then start Remote Play. If a stream is already running, end it and start it again for the change to take effect.",
      "Paper White sets the reference brightness of the HDR stream. To change it, end the stream first.",
      "Contrast, Gamma and Saturation let you tune the HDR picture to your taste. You can change them freely, even while streaming.",
      "All plugin settings apply to Remote Play only. Games running directly on this device are not affected.",
    ],
    requirementsHeading: "Requirements",
    requirements: [
      "Host PC (the PC that runs the game): An HDR-capable game and monitor, and a PC powerful enough to run HDR games smoothly on its own. " +
        "Tested with Windows 11, an RTX 50 series GPU and a Samsung OLED monitor.",
      "Client (this device): A device with a built-in or externally connected HDR display, running SteamOS in Game Mode. " +
        "Tested with the Lenovo Legion Go 2 OLED running CachyOS Handheld.",
      "Network: A high-bandwidth, low-latency connection is recommended. Tested over 2.5GbE wired and 5 GHz Wi-Fi.",
      "The PyroWave Video option, added to Steam in October 2026, is required. (Be sure to turn off Use NVFBC capture on NVIDIA GPU.)",
    ],
    hostHeading: "Host Settings",
    host: [
      "Host PC > Steam Settings > Remote Play > Advanced Host Options",
      "Enable Advanced Host Options: On",
      "Primary display while streaming: an HDR-capable display",
      "Streaming display HDR: Default, or Custom with Custom HDR Enabled turned on",
      "Use NVFBC capture on NVIDIA GPU: Off",
      "Enable hardware encoding: On",
      "Prioritize network traffic: On",
    ],
    clientHeading: "Client Settings",
    client: [
      "This device > Steam Settings > Remote Play > Advanced Client Options",
      "Enable Advanced Client Options: On",
      "Video: Beautiful",
      "Bandwidth Limit: Unlimited",
      "Resolution Limit: Display resolution",
      "Framerate Limit: this device's refresh rate",
      "HDR: On",
      "Hardware Decoding: On",
      "HEVC Video: On",
      "AV1 Video: Off",
      "PyroWave Video: On (Quality Modifier 1 or higher)",
      "Low Latency Networking: On",
      "This device > Steam Settings > Developer > HDR Compatibility Testing: On",
    ],
    detailsHeading: "Details",
    version: "Version",
    author: "Author",
    license: "License",
    repository: "Repository",
  },
  streamingNotice: "Steam is streaming. HDR Streaming and Paper White can't be changed while a stream is running.",
  statusLoading: "Loading...",
  statusUnavailable: "Can't reach the plugin. Please reload the plugin.",
  unknownError: "An unknown error occurred. Error code: {code}",
  // Texts for the error codes sent by the backend (py_modules/streamhdr/errors.py).
  errors: {
    client_not_found: "Couldn't find streaming_client. Make sure Steam is installed in its default location.",
    shim_missing: "The plugin files are damaged or missing. Please reinstall the plugin.",
    original_missing: "Couldn't find streaming_client.real. Restart Steam, then reload the plugin.",
    unknown_format: "streaming_client doesn't have the expected format, so the plugin can't work correctly.",
    file_operation_failed: "File operation failed: {detail}",
    env_missing: "Couldn't find gamescope information. Make sure Steam is running in Game Mode.",
    xprop_missing: "xprop is not installed, so HDR output settings can't be applied.",
    xprop_timeout: "Applying the HDR output settings timed out.",
    xprop_failed: "Couldn't apply the HDR output settings: {detail}",
    wrapper_unstable: "Steam keeps restoring its streaming client, so automatic installation was stopped. Switch HDR Streaming off and on, or reload the plugin.",
    lut_failed: "Couldn't create the LUT file: {detail}",
  } as Record<string, string>,
};

export type Strings = typeof en;

// What a language file provides: anything left out is taken from English.
export type LocaleStrings = Partial<Omit<Strings, "errors" | "info">> & {
  errors?: Record<string, string>;
  info?: Partial<Strings["info"]>;
};
