// All user-facing text lives here so that other languages can be added later.
export const strings = {
  pluginName: "StreamHDR",
  sectionTitle: "Remote Play HDR",
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
};
