# Changelog

## 2.0.0

- Rebase on [nordwestt/kokoro-wyoming](https://github.com/nordwestt/kokoro-wyoming),
  which now ships streaming synthesis, sentence boundary detection, a startup
  warmup, a synthesis cache and markdown stripping for LLM responses
- Use the Home Assistant Debian base image, with s6-overlay services and
  `bashio` discovery like the official Wyoming apps
- Add `speed` and `cache_size` options, and pick `voice` from a list
- Restart the app automatically if the Wyoming port stops responding
- Use the CPU build of onnxruntime, which works on both amd64 and aarch64
- Drop `build.yaml`, which Home Assistant has deprecated

## 1.0.0

- Initial release
