// English texts. This is the reference language: every other language is checked against its keys,
// and any text a language does not provide falls back to the English one.
//
// Placeholders such as {detail} are replaced with values that cannot be translated, for example
// the output of a system tool.
export const en = {
  pluginName: "StreamHDR",
  hdrToggleLabel: "HDR Streaming",
  hdrToggleDescription:
    "Makes Steam's streaming client request an HDR stream. Takes effect the next time you connect. " +
    "On the host PC, set Steam's streaming display HDR to Default (or Custom with HDR enabled), " +
    "never to Match client. Turn on Windows HDR and turn off NVFBC capture.",
  paperWhiteLabel: "Paper White",
  paperWhiteDescription:
    "Sets how bright reference (paper) white is in the stream, in nits. 200-230 is recommended. " +
    "Takes effect the next time you connect.",
  contrastLabel: "Contrast",
  contrastDescription:
    "Widens or narrows the difference between dark and bright areas around paper white. 100% leaves the picture unchanged. " +
    "Applies only while you are streaming.",
  gammaLabel: "Gamma",
  gammaDescription:
    "Changes the brightness of dark and middle tones while keeping highlights. 1 leaves the picture unchanged; " +
    "higher values are darker and lower values are brighter. Applies only while you are streaming.",
  saturationLabel: "Saturation",
  saturationDescription:
    "Boosts the color saturation of the HDR stream. 100% leaves colors unchanged and 150% is recommended. " +
    "Applies only while you are streaming. Very high values can clip strongly colored areas.",
  infoButton: "Plugin Info",
  githubButton: "GitHub",
  resetButton: "Reset All Settings",
  resetTitle: "Reset all settings",
  resetDescription:
    "Sets Paper White, Contrast, Gamma and Saturation back to their defaults, and turns HDR Streaming on. " +
    "While streaming, HDR Streaming and Paper White stay as they are.",
  resetConfirmButton: "Reset",
  cancelButton: "Cancel",
  // Texts of the info page that the "Plugin Info" button opens.
  info: {
    aboutHeading: "About",
    about:
      "StreamHDR lets Steam Remote Play deliver real HDR to this device. Steam's Linux streaming client " +
      "always asks the host for SDR, because SDL cannot detect HDR under X11. This plugin makes the client ask for HDR instead.",
    usageHeading: "Usage",
    usage: [
      "Turn on HDR Streaming, then connect to your host PC with Remote Play. The setting applies from the next connection.",
      "Use Saturation to make colors stronger while streaming. 100% leaves colors unchanged and 150% is recommended.",
      "Both options only affect Remote Play streaming. Local games are not changed.",
    ],
    hostHeading: "Host PC",
    host: [
      "In Steam's Remote Play settings, set Streaming display HDR to Default, or to Custom with HDR enabled. " +
        "Never use Match client: the host drops back to SDR after a few seconds.",
      "Turn on Windows HDR. Without it most games hide their HDR option.",
      "Turn off NVFBC capture. It produces washed-out colors.",
    ],
    detailsHeading: "Details",
    version: "Version",
    author: "Author",
    license: "License",
    repository: "Repository",
  },
  streamingNotice: "A game is being streamed. HDR Streaming and Paper White cannot be changed while streaming.",
  statusLoading: "Loading...",
  statusUnavailable: "The plugin backend is not reachable.",
  unknownError: "Something went wrong ({code}).",
  // Texts for the error codes sent by the backend (py_modules/streamhdr/errors.py).
  errors: {
    client_not_found: "Steam's streaming client was not found. Start Steam once and try again.",
    shim_missing: "The bundled injection library is missing from the plugin package.",
    original_missing:
      "The wrapper is installed but the original streaming client copy is missing. " +
      "Restart Steam to restore the original, then reload the plugin.",
    unknown_format: "Steam's streaming client has an unexpected format, so it was left untouched.",
    file_operation_failed: "File operation failed: {detail}",
    env_missing: "gamescope's environment file was not found. Is gamescope running?",
    xprop_missing: "The xprop tool is not installed, so saturation cannot be applied.",
    xprop_timeout: "xprop timed out while talking to gamescope.",
    xprop_failed: "xprop failed: {detail}",
    lut_failed: "Could not create the color table: {detail}",
  } as Record<string, string>,
};

export type Strings = typeof en;

// What a language file provides: anything left out is taken from English.
export type LocaleStrings = Partial<Omit<Strings, "errors" | "info">> & {
  errors?: Record<string, string>;
  info?: Partial<Strings["info"]>;
};
