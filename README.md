# decky-stream-hdr

StreamHDR is a [Decky Loader](https://decky.xyz) plugin that enables real HDR (BT.2020, PQ) for Steam Remote Play on Linux clients, such as a Legion Go 2 running CachyOS Handheld in gamescope game mode.

## The problem

On a Linux client, Steam's streaming client asks SDL3 whether the display has HDR enabled. Under X11 SDL always answers "no", so the client creates an sRGB renderer and the host streams SDR, even when the host has HDR on and the game supports it. The same device booted into Windows receives HDR normally.

## What the plugin does

- **HDR streaming** (toggle): preloads a tiny library into Steam's `streaming_client` that makes the single `SDL.display.HDR_enabled` query answer "yes". Everything else is forwarded to the real SDL. The host then captures and encodes an HDR stream.
- **Saturation** (slider, 0-200%, default 100%): HDR streams can look slightly less saturated than SDR. The slider sets a 3D LUT on gamescope's `GAMESCOPE_COLOR_LOOK_PQ` atom, but only while a stream is running. 100% means no change and 150% is a good starting point.

Both features apply to Remote Play streaming only. Local games are not touched.

## How it works

1. When HDR streaming is on, the plugin moves Steam's `streaming_client` to `streaming_client.real` and puts a small shell script in its place. The script sets `LD_PRELOAD` to the bundled library and runs the original.
2. Steam restores its original binary whenever it starts or updates. The plugin checks every 20 seconds and installs the wrapper again.
3. Turning HDR streaming off removes the flag file the script checks, so the stream request is no longer changed. Unloading or uninstalling the plugin puts the original binary back and removes the saturation LUT.

Plugin-owned files live under `~/.local/share/decky-stream-hdr/` so that the Steam runtime container can see them.

## Host PC settings

HDR only works when the host cooperates:

| Setting | Value |
| --- | --- |
| Steam Remote Play > Streaming display HDR | **Default**, or **Custom** with HDR enabled. Never **Match client**: the host drops HDR after a few seconds. |
| Windows HDR | On. With HDR off most games disable their HDR option. |
| NVFBC capture | Off. It produces limited-range 8-bit video and washed-out colors. |

On the client, turning on Steam's developer option "HDR compatibility test" makes the HDR badge follow the real state instead of Valve's per-game list.

## Requirements

- A Linux client running Steam in gamescope game mode with Decky Loader installed.
- gamescope HDR support on the display (for example `hdr.supported = true` in the display's gamescope script).
- `xprop` for the saturation slider.

## Install

On the Linux client, clone the repository, then build and install in one step. The script builds the frontend and the injection library, packages the plugin into `~/homebrew/plugins/decky-stream-hdr` and restarts Decky Loader. It needs git, node, yarn, gcc, make, python3 and sudo (on CachyOS: `sudo pacman -S git nodejs yarn gcc make python`).

```bash
git clone <repository url> ~/decky-stream-hdr
cd ~/decky-stream-hdr
sh scripts/install-dev.sh
```

To update later, run `git pull` and `sh scripts/install-dev.sh` again.

A release zip (`scripts/package.sh`) contains `dist/`, `main.py`, `plugin.json`, `package.json`, `py_modules/`, `LICENSE`, `README.md` and `bin/sdl_hdr_shim.so`. It can be extracted into `~/homebrew/plugins/` instead.

## Develop

Development happens on any machine; building and installing happens on the client. The panel can be previewed in a desktop browser, with the Steam and Decky UI components and the plugin backend replaced by stand-ins:

```bash
yarn install
yarn serve       # dev server; add the browser with `yarn start`
```

Then open http://localhost:5173/. The preview controls next to the panel switch the stand-in backend into other states (backend unreachable, a problem text, streaming). The stand-ins only approximate Steam's quick access menu, so check the final look on the device.

```bash
yarn test            # backend unit tests, only Python 3 is needed
yarn typecheck       # TypeScript type check
```

Build steps by hand (Linux): `yarn build`, `make -C backend`, then `scripts/package.sh`.

## Limitations

- The approach relies on the streaming client calling SDL3 dynamically. A Steam change that links SDL statically would stop it from working.
- Very high saturation values clip strongly colored areas to zero in one or more channels.
- The injection library has only been verified on a Legion Go 2 running CachyOS Handheld.

## License

MIT. The project is based on the Decky plugin template, whose BSD 3-Clause license is kept at the end of `LICENSE`.
