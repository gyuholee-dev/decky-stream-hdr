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
    "Turns on HDR for both encoding and rendering when streaming with Steam. For the recommended host and client settings, see Plugin Info.",
  paperWhiteLabel: "Streaming Content Brightness",
  paperWhiteDescription: "Sets the reference brightness of the streamed game screen.",
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
    aboutHeading: "About the Plugin",
    about:
      "StreamHDR is a Decky plugin that adds HDR streaming to Steam Remote Play. If the latest SteamOS is installed on a device capable of HDR output, this plugin lets you set it up for HDR streaming in the BT.2020 color gamut.",
    howHeading: "How Is This Possible?",
    how: [
      "SteamOS does not actually stream HDR. The badge marked HDR is only a display based on predefined HDR compatibility information, and the stream that the host encodes and sends is actually in the BT.709 SDR color gamut. In other words, an SDR stream is merely being rendered on an HDR display, and even that falls back to SDR rendering when there is no predefined compatibility value.",
      "StreamHDR was developed to solve this problem. What this plugin does is simple. By wrapping Steam's streaming client (streaming_client), it changes the streaming request that Steam sends to the host into an HDR request, and it sets up the client so that the HDR stream is rendered at a normal brightness. That is all.",
    ],
    usageHeading: "Usage",
    usage: [
      "Turn on HDR Streaming in the plugin menu, then start Remote Play. If a stream is already running, end it and start it again for the change to take effect.",
      "Streaming Content Brightness sets the reference brightness of the HDR stream. To change it, end the stream first.",
      "Contrast, Gamma and Saturation let you tune the HDR picture to your taste. You can change them freely, even while streaming.",
      "All plugin settings apply to Remote Play only. The screen of games you install and run directly on the client device is not affected.",
    ],
    requirementsHeading: "HDR Streaming Requirements",
    requirements: [
      "Host (the PC that runs the game): A PC powerful enough to run HDR games smoothly is required.",
      "Client (the device that runs the stream): SteamOS must be running in Game Mode on a device with a built-in or externally connected HDR display.",
      "Network: A high-bandwidth, low-latency connection is recommended. For a stationary device, a wired connection of 1GbE or faster is recommended; for a handheld device, turn off Wi-Fi power saving. If MLO (Multi-Link Operation) is turned on at the router, devices that do not support MLO (such as Wi-Fi 6E devices) can see higher latency and packet loss on 6 GHz, and gameplay may not run smoothly; turn MLO off or connect to 5 GHz Wi-Fi.",
      "When streaming HDR to a device with a built-in OLED display, such as the Lenovo Legion Go 2, SteamOS 3.10.1 or later, where a relaxed content luminance limit has been confirmed, is recommended.",
      "The PyroWave Video option, added to Steam in October 2026, is required. PyroWave is not subject to Steam's regular Bandwidth Limit and sends a very large amount of data (over 1 Gbps; up to 1.1 Gbps at 1080p with YUV 4:4:4 on and Quality Modifier 2, tested over 6 GHz Wi-Fi). If the frame rate drops or stuttering appears while streaming, turn off YUV 4:4:4 and set Quality Modifier to 1 or lower (about 620-730 Mbps at 1080p).",
    ],
    hostHeading: "Recommended Host Settings",
    host: [
      "Host > Steam Settings > Remote Play > Advanced Host Options",
      "Enable Advanced Host Options: On",
      "Primary display while streaming: an HDR-capable display",
      "Streaming display HDR: Default, or Custom (Custom HDR Enabled: On)",
      "Use NVFBC capture on NVIDIA GPU: Off",
      "Enable hardware encoding: On",
      "Prioritize network traffic: On",
      "Windows Settings > System > Display > HDR: Use HDR On, SDR content brightness 50",
      "In-game HDR setting: maximum brightness 1000 nits",
    ],
    clientHeading: "Recommended Client Settings",
    client: [
      "Client > Steam Settings > Remote Play > Advanced Client Options",
      "Enable Advanced Client Options: On",
      "Video: Beautiful",
      "Resolution Limit: Display resolution",
      "Framerate Limit: the client device's refresh rate",
      "HDR: On",
      "Hardware Decoding: On",
      "HEVC Video: On",
      "AV1 Video: Off",
      "PyroWave Video: On (YUV 4:4:4: Off, Automatic Bitrate: On, Quality Modifier: 1)",
      "Low Latency Networking: On",
      "Client > Steam Settings > Developer > HDR Compatibility Testing: On",
      "StreamHDR plugin: Streaming Content Brightness 200 nits (default)",
    ],
    knownIssuesHeading: "Known Issues",
    knownIssues: [
      "This plugin automatically modifies Steam's system file streaming_client, and restores it, depending on conditions. If a serious error occurs, it can be hard for users to fix on their own, so please be careful.",
      "On the built-in display of a handheld device, clipping may occur in the HDR peak luminance range. SteamOS is presumed to limit the maximum luminance of HDR content on the built-in display to about 600 nits (with the brightness slider at its maximum), and pixels brighter than this are shown as white. If a very bright area, such as the sun in the sky of a game, looks burnt out to white, you can reduce the problem by lowering the host game's maximum brightness to 800 nits or less, or by lowering Streaming Content Brightness.",
      "If the host's \"Streaming display HDR\" option is set to \"Match Client\", the encoding falls back to SDR right after the stream starts. Always set the option to \"Default\" or \"Custom\".",
      "If the host's \"Use NVFBC capture on NVIDIA GPU\" option is on, the captured data is not encoded in the HDR color gamut. Always turn this option off.",
      "If a Steam update changes streaming_client, the plugin may stop working. If you can't update the plugin, disable or uninstall it and restart Steam to restore the original state.",
    ],
    detailsHeading: "Details",
    version: "Version",
    author: "Author",
    license: "License",
    repository: "Repository",
  },
  streamingNotice: "Steam is currently streaming. HDR Streaming and Streaming Content Brightness can't be changed until the stream ends.",
  statusLoading: "Loading...",
  statusUnavailable: "Can't connect to the plugin. Please reload the plugin.",
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
