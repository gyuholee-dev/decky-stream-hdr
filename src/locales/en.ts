// English texts. This is the reference language: every other language is checked against its keys,
// and any text a language does not provide falls back to the English one.
//
// Placeholders such as {detail} are replaced with values that cannot be translated, for example
// the output of a system tool.
export const en = {
  pluginName: "StreamHDR",
  hdrToggleLabel: "HDR streaming",
  hdrToggleDescription:
    "Makes Steam's streaming client request an HDR stream. Takes effect the next time you connect. " +
    "On the host PC, set Steam's streaming display HDR to Default (or Custom with HDR enabled), " +
    "never to Match client. Turn on Windows HDR and turn off NVFBC capture.",
  saturationLabel: "Saturation",
  saturationDescription:
    "Boosts the color saturation of the HDR stream. 100% leaves colors unchanged and 150% is recommended. " +
    "Applies only while you are streaming. Very high values can clip strongly colored areas.",
  statusLoading: "Loading...",
  statusUnavailable: "The plugin backend is not reachable.",
  errorPrefix: "Problem: ",
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
    env_no_display: "gamescope's environment file has no DISPLAY entry.",
    xprop_missing: "The xprop tool is not installed, so saturation cannot be applied.",
    xprop_timeout: "xprop timed out while talking to gamescope.",
    xprop_failed: "xprop failed: {detail}",
    lut_failed: "Could not create the color table: {detail}",
  } as Record<string, string>,
};

export type Strings = typeof en;
