# Wyoming Kokoro TTS for Home Assistant

A Home Assistant app that runs [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M)
as a local text-to-speech engine over the [Wyoming protocol](https://github.com/rhasspy/wyoming).
No cloud required.

[![Add repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fchrishoage%2Fkokoro-wyoming)

## Features

- 54 voices across English (US and UK), Spanish, French, Hindi, Italian,
  Japanese, Portuguese and Chinese
- Streaming synthesis: LLM responses are spoken sentence by sentence as they're
  generated
- Wyoming discovery, so Home Assistant finds the app automatically
- Runs on amd64 and aarch64

## Installation

1. Select the button above, or open the app store under **Settings → Apps**,
   open the **⋮** menu → **Repositories** and add
   `https://github.com/chrishoage/kokoro-wyoming`.
2. Find **Wyoming Kokoro TTS** in the store and select **Install**.
3. Start the app, then follow [the app's documentation](kokoro_wyoming/DOCS.md)
   to connect it to your voice assistant.

## Repository layout

- `kokoro_wyoming/` is the Home Assistant app. Its Dockerfile fetches the
  server (`src/main.py`) from upstream at the commit pinned by
  `KOKORO_WYOMING_REF`.
- Apart from this README, `repository.yaml`, `validate.py` and the app build
  workflow, everything else is [nordwestt/kokoro-wyoming](https://github.com/nordwestt/kokoro-wyoming),
  kept unmodified so this fork rebases cleanly. Its Docker images and compose
  files still work for running the server outside Home Assistant.

To update the server, bump `KOKORO_WYOMING_REF` in `kokoro_wyoming/Dockerfile`
and the app `version` in `kokoro_wyoming/config.yaml`.

### Testing locally

```sh
docker build -t kokoro-wyoming-app kokoro_wyoming
docker run --rm -p 10200:10200 --entrypoint python3 kokoro-wyoming-app \
  /usr/src/kokoro_wyoming/main.py --uri tcp://0.0.0.0:10200 \
  --model /usr/share/kokoro/kokoro-v1.0.onnx --voices /usr/share/kokoro/voices-v1.0.bin
python3 validate.py
```

## Acknowledgements

- [nordwestt/kokoro-wyoming](https://github.com/nordwestt/kokoro-wyoming) and
  its contributors, including [relvacode](https://github.com/relvacode/kokoro-wyoming),
  for the Wyoming server
- [araa47/wyoming_pocket_tts](https://github.com/araa47/wyoming_pocket_tts) and
  the official [Piper app](https://github.com/home-assistant/addons/tree/master/piper)
  for the app packaging
- [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) and
  [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)
