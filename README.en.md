# StreamHDR

[한국어](README.md)

### About the Plugin

StreamHDR is a Decky plugin that adds HDR streaming to Steam Remote Play. If the latest SteamOS is installed on a device capable of HDR output, this plugin lets you set it up for HDR streaming in the BT.2020 color gamut.

### How Is This Possible?

SteamOS does not actually stream HDR. The badge marked HDR is only a display based on predefined HDR compatibility information, and the stream that the host encodes and sends is actually in the BT.709 SDR color gamut. In other words, an SDR stream is merely being rendered on an HDR display, and even that falls back to SDR rendering when there is no predefined compatibility value.

StreamHDR was developed to solve this problem. What this plugin does is simple. By wrapping Steam's streaming client (`streaming_client`), it changes the streaming request that Steam sends to the host into an HDR request, and it sets up the client so that the HDR stream is rendered at a normal brightness. That is all.

## Installation

[Decky Loader](https://decky.xyz/) must already be installed on the device that runs the stream.

### Quick Install

- To install quickly, open the Developer settings in Decky Loader, choose "Install Plugin from URL", and enter the address of the release file.

```text
https://github.com/gyuholee-dev/decky-stream-hdr/releases/download/v1.0.0/decky-stream-hdr-1.0.0.zip
```

### Install from a ZIP File

1. Download `decky-stream-hdr-1.0.0.zip` from [GitHub Releases](https://github.com/gyuholee-dev/decky-stream-hdr/releases).
2. In Decky's settings, turn on "Developer mode".
3. In Decky's Developer settings, choose "Install Plugin from ZIP File", select the downloaded file, and install it.

### After Installation

Once the installation is complete, open StreamHDR from the Decky menu, turn on HDR Streaming there, and then start Remote Play.

## Usage

1. Turn on HDR Streaming in the plugin menu, then start Remote Play. If a stream is already running, end it and start it again for the change to take effect.
2. Streaming Content Brightness sets the reference brightness of the HDR stream. To change it, end the stream first.
3. Contrast, Gamma and Saturation let you tune the HDR picture to your taste. You can change them freely, even while streaming.
4. All plugin settings apply to Remote Play only. The screen of games you install and run directly on the client device is not affected.

## HDR Streaming Requirements

- Host (the PC that runs the game): A PC powerful enough to run HDR games smoothly is required.
- Client (the device that runs the stream): SteamOS must be running in Game Mode on a device with a built-in or externally connected HDR display.
- Network: A high-bandwidth, low-latency connection is recommended. For a stationary device, a wired connection of 1GbE or faster is recommended; for a handheld device, turn off Wi-Fi power saving. If MLO (Multi-Link Operation) is turned on at the router, devices that do not support MLO (such as Wi-Fi 6E devices) can see higher latency and packet loss on 6 GHz, and gameplay may not run smoothly; turn MLO off or connect to 5 GHz Wi-Fi.
- When streaming HDR to a device with a built-in OLED display, such as the Lenovo Legion Go 2, SteamOS 3.10.1 or later, where a relaxed content luminance limit has been confirmed, is recommended.
- The PyroWave Video option, added to Steam in October 2026, is required. PyroWave is not subject to Steam's regular Bandwidth Limit and sends a very large amount of data (over 1 Gbps; up to 1.1 Gbps at 1080p with YUV 4:4:4 on and Quality Modifier 2, tested over 6 GHz Wi-Fi). If the frame rate drops or stuttering appears while streaming, turn off YUV 4:4:4 and set Quality Modifier to 1 or lower (about 620-730 Mbps at 1080p).

## Recommended Host Settings

- Host > Steam Settings > Remote Play > Advanced Host Options
- Enable Advanced Host Options: On
- Primary display while streaming: an HDR-capable display
- Streaming display HDR: Default, or Custom (Custom HDR Enabled: On)
- Use NVFBC capture on NVIDIA GPU: Off
- Enable hardware encoding: On
- Prioritize network traffic: On
- Windows Settings > System > Display > HDR: Use HDR On, SDR content brightness 50
- In-game HDR setting: maximum brightness 1000 nits

## Recommended Client Settings

- Client > Steam Settings > Remote Play > Advanced Client Options
- Enable Advanced Client Options: On
- Video: Beautiful
- Resolution Limit: Display resolution
- Framerate Limit: the client device's refresh rate
- HDR: On
- Hardware Decoding: On
- HEVC Video: On
- AV1 Video: Off
- PyroWave Video: On (YUV 4:4:4: Off, Automatic Bitrate: On, Quality Modifier: 1)
- Low Latency Networking: On
- Client > Steam Settings > Developer > HDR Compatibility Testing: On
- StreamHDR plugin: Streaming Content Brightness 200 nits (default)

## Known Issues

- This plugin automatically modifies Steam's system file `streaming_client`, and restores it, depending on conditions. If a serious error occurs, it can be hard for users to fix on their own, so please be careful.
- On the built-in display of a handheld device, clipping may occur in the HDR peak luminance range. SteamOS is presumed to limit the maximum luminance of HDR content on the built-in display to about 600 nits (with the brightness slider at its maximum), and pixels brighter than this are shown as white. If a very bright area, such as the sun in the sky of a game, looks burnt out to white, you can reduce the problem by lowering the host game's maximum brightness to 800 nits or less, or by lowering Streaming Content Brightness.
- If the host's "Streaming display HDR" option is set to "Match Client", the encoding falls back to SDR right after the stream starts. Always set the option to "Default" or "Custom".
- If the host's "Use NVFBC capture on NVIDIA GPU" option is on, the captured data is not encoded in the HDR color gamut. Always turn this option off.
- If a Steam update changes `streaming_client`, the plugin may stop working. If you can't update the plugin, disable or uninstall it and restart Steam to restore the original state.

---

# Development

## Development Environment

You need Node.js, yarn (1.x) and Python 3. Building the injected library also needs `make` and `gcc` on Linux.

## Test Environment

- Client device: Lenovo Legion Go 2 OLED
- Client OS: SteamOS 3.10.1, CachyOS (as of November 26-27, 2026: gamescope 3.17.0, kernel 7.3.5, mesa 26.3.1). Both run in Game Mode.
- Host: Windows 11, NVIDIA RTX 5090, LG 45GX950A, Samsung G80SD
- Network: 2.5GbE wired connection, 5 GHz Wi-Fi connection, 6 GHz Wi-Fi connection with MLO turned off
- On other devices and OS environments, the plugin may not work or may behave unstably.

## Design Principles

- **The only system file it modifies is `streaming_client`.** The original is always kept in the same folder as `streaming_client.real`, and the plugin puts it back when it is uninstalled or when Steam exits.
- **Installing and restoring are timed around Steam's file check.** Every time Steam starts, it checks the size of `streaming_client`; if it differs, Steam restores the file with an update and then restarts itself. If the plugin immediately puts the wrapper back, Steam repeats the same procedure over and over (the wrapper restore loop), and Game Mode may fail to boot. So when Steam exits, the plugin restores the original first, and installs the wrapper only after Steam has been running for a while.
- **It runs on events instead of polling.** File changes are detected with `inotify` and process exits with `pidfd`; there is no periodic timer check. Only while Steam is not running does it look again, at growing intervals.
- **Every feature is for streaming only.** The wrapper affects only `streaming_client`, and the color adjustment is applied when a stream starts and removed when it ends. Local games are not affected.
- **Option definitions live in one place.** Range, step, default and whether an option is locked during a stream are all in `py_modules/streamhdr/options.json`, which the frontend, the backend and the browser mockup all read.

## How It Works

1. **Wrapper installation:** `streaming_client` is kept as `streaming_client.real`, and a shell script (the wrapper) takes its place under the same name. The wrapper sets `LD_PRELOAD` only when the HDR Streaming flag (`enabled`) and `sdl_hdr_shim.so` exist, writes `start <pid>` to the `stream_event` file, and then `exec`s the original. The wrapper is installed regardless of the HDR Streaming setting; the flag file decides whether it is on.
2. **Requesting HDR:** When Steam on Linux asks SDL (on X11) whether the display supports HDR, it always gets "no", so it requests SDR from the host. The injected library (`backend/src/sdl_hdr_shim.c`) answers `true` to the `SDL.display.HDR_enabled` query, so Steam requests HDR.
3. **Streaming Content Brightness:** SDL's renderer on X11 assumes an SDR white level of 80 nits, which makes the stream look dark. Right before the renderer is created, the injected library sets the window property `SDL.window.SDR_white_level` to `Streaming Content Brightness ÷ 80`. The value is read from the `paper_white` file, so a change applies from the next connection.
4. **When it installs:** The wrapper is installed only while Steam is running. If the original was in place cleanly (it was the original when the plugin loaded, or the plugin restored it when Steam exited), it goes in 5 seconds after Steam starts; if the wrapper was left behind when Steam started (after a forced power-off, for example), it goes in after 30 seconds.
5. **Restoring when Steam exits:** As soon as the `steamrt64/steam` process ends, the original is restored.
6. **Detecting streams:** The plugin learns that a stream has started by reading `stream_event`, which the wrapper writes, and is notified when that process exits through `pidfd`. Starts and ends reach the panel as a `status` event and are used for the notice box and for locking options.
7. **Color adjustment:** Contrast, Gamma and Saturation are turned into a 17×17×17 3D LUT (`.cube`), which is set on gamescope's `GAMESCOPE_COLOR_LOOK_PQ` property with `xprop`. Each combination of settings gets its own `look_pq_s###_c###_g###_p###.cube` file and the others are cleaned up; when all three values are at their defaults, the property is removed. `xprop` is required (included by default on SteamOS); without it, Contrast, Gamma and Saturation can't be applied and an error box is shown. HDR streaming itself and Streaming Content Brightness don't use `xprop`.
8. **Preventing repeated restores:** If Steam restores the original 3 times within 10 minutes, the plugin stops reinstalling and shows an error box. It tries again when HDR Streaming is switched or the plugin is reloaded.

## Options

| Option | Default | Range | Notes |
|---|---|---|---|
| HDR Streaming | On | On / Off | Locked during a stream; applies from the next connection |
| Streaming Content Brightness | 200 nits | 80 - 480 nits, in steps of 10 nits | Locked during a stream; applies from the next connection |
| Contrast | 100% | 0 - 200%, in steps of 5 | Can be changed during a stream |
| Gamma | 1.00 | 0.50 - 2.00, in steps of 0.05 | Can be changed during a stream |
| Saturation | 100% | 0 - 200%, in steps of 5 | Can be changed during a stream |

Reset All Settings sets every option back to its default. During a stream, the options that are locked (HDR Streaming and Streaming Content Brightness) are left as they are.

## Brightness Calculation

These are results tested with a Windows host and SteamOS 3.10.1. The brightness of the stream is determined in the following order.

1. The host game sets the luminance of the HDR content (the game's maximum brightness setting, for example).
2. The host Windows SDR content brightness (slider value s) sets the stream's reference white to `80 + 4 × s` nits. With the slider at 50, that is 280 nits.
3. The client draws this reference white again as the Streaming Content Brightness. The content luminance is multiplied by `Streaming Content Brightness ÷ host reference white`, and this ratio is called the PW correction. With the host's SDR content brightness at 50 and Streaming Content Brightness at the default 200 nits, the PW correction is 200 nits ÷ 280 nits ≈ 0.71. Lowering the host's SDR content brightness raises the PW correction and makes the picture brighter; raising it makes the picture darker.
4. gamescope multiplies in the gain of the brightness slider and draws the result.

The game's maximum brightness and paper white only change the host's content; they do not change the PW correction.

### Rendering Limit

The rendering limit is a cap on the maximum luminance that HDR content can have, regardless of the luminance actually shown on the display. Content luminance above this value is all drawn as the same white, which causes clipping. The rendering limit is inversely proportional to the gain of the brightness slider, `about 1850 nits ÷ gain`, with a measurement error of about ±5%.

| Brightness slider | Gain | Rendering limit |
|---|---|---|
| 100 | 3.0 | about 617 nits |
| 88 | 2.395 | about 772 nits |
| 80 | 1.945 | about 951 nits |
| 76 | 1.753 | about 1055 nits |

Clipping occurs when the host content luminance multiplied by the PW correction exceeds the rendering limit. With the host's SDR content brightness at 50 and Streaming Content Brightness at 200 nits, a host game maximum brightness of 800 nits gives a content value of about 571 nits, so there is no clipping at slider 100; at 1000 nits it is about 714 nits, so clipping occurs.

## File Structure

```
plugin.json, package.json    Plugin info and build settings (package.json is the source of the version)
main.py                      Backend entry point (delegates to the modules)
py_modules/streamhdr/        Backend
  options.json               Single source of the option definitions
  options.py                 Reads the options and validates values
  controller.py              Ties settings, wrapper and gamescope together; handles state and option changes
  wrapper.py                 Installs, checks and restores the wrapper
  streaming_client.sh.tmpl   Wrapper script template
  events.py                  inotify and pidfd events (file changes; stream and Steam start/exit)
  look.py                    Builds the contrast, gamma and saturation LUT
  gamescope.py               Reads gamescope's environment; sets and removes the xprop property
  paperwhite.py              Streaming Content Brightness value file
  paths.py, settings.py, errors.py
src/                         Frontend (React, Decky UI)
  index.tsx                  Panel
  info-page.tsx              Plugin Info page
  status.ts                  Backend state and events
  locales/                   Texts (en.ts is the reference, ko.ts)
backend/                     Injected library source (src/sdl_hdr_shim.c) and build settings
preview/                     Browser mockup (uses mock_steam.css, which imitates the Steam UI)
scripts/                     package.sh (release zip), install-dev.sh (install on a device)
tests/                       Backend unit tests
```

The plugin creates these files on the device:

| Path | Contents |
|---|---|
| `~/.local/share/Steam/steamrt64/streaming_client` | The wrapper script (the original is `streaming_client.real`) |
| `~/.local/share/decky-stream-hdr/sdl_hdr_shim.so` | The injected library |
| `~/.local/share/decky-stream-hdr/enabled` | HDR Streaming flag (on if the file exists) |
| `~/.local/share/decky-stream-hdr/paper_white` | Streaming Content Brightness value |
| `~/.local/share/decky-stream-hdr/stream_event` | Stream start event written by the wrapper |
| `~/.local/share/decky-stream-hdr/luts/` | Color adjustment LUT files |
| `~/homebrew/settings/decky-stream-hdr/settings.json` | Option values |

## Development Commands

Install, check, test and build the frontend with these commands.

```bash
yarn install
yarn typecheck    # type check
yarn test         # backend unit tests (unittest)
yarn build        # build the frontend (dist/)
yarn serve        # browser mockup: http://localhost:5173/ (add ?lang=english to see English)
```

The mockup is an approximation of Decky and the Steam UI, so spacing and fonts are not exact. Check the final look on a device.

The injected library can only be built on Linux, so build the release zip on a Linux device.

```bash
make -C backend           # backend/out/sdl_hdr_shim.so
sh scripts/package.sh     # release/decky-stream-hdr-<version>.zip
```

During development, you can pull the repository on the device and build and install into Decky in one step. It asks for your `sudo` password.

```bash
git pull
sh scripts/install-dev.sh
```

## Translation

The texts are in `src/locales/en.ts` (the reference language) and `ko.ts`; the language is chosen from Steam's language setting, and anything a language lacks is shown in English. Steam option names in the English texts are written exactly as they appear in Steam's English interface. To add a language, create `src/locales/<language>.ts` and register it in `src/locales/index.ts`. The info page texts are kept identical to this README from the introduction at the top and from "Usage" through "Known Issues" (the installation instructions are not on the info page).

## Manual Recovery

If you can't remove the plugin, or the Steam update prompt keeps coming back and Game Mode won't boot, connect over SSH or a TTY and run the following in order.

```bash
sudo systemctl stop plugin_loader
mv -f ~/.local/share/Steam/steamrt64/streaming_client.real ~/.local/share/Steam/steamrt64/streaming_client
sudo rm -rf ~/homebrew/plugins/decky-stream-hdr ~/.local/share/decky-stream-hdr
sudo reboot
```

If the second command says there is no such file, the original has already been restored, so skip it.

## License

Licensed under [GPL-3.0](LICENSE). Notices for the third-party software this project uses are in [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES).
