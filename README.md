# Wyoming Kokoro TTS

A Home Assistant add-on that runs [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) as a local text-to-speech engine via the [Wyoming protocol](https://github.com/rhasspy/wyoming). Fast, high-quality, 100% on-device — no cloud required.

[![Add to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fchrishoage%2Fkokoro-wyoming)

## Features

- **54 voices** across English (US & UK), French, Italian, Japanese, Chinese, Spanish, and Hindi
- **Streaming synthesis** for low-latency voice responses
- **Sentence boundary detection** for natural-sounding output from streamed text
- **Wyoming auto-discovery** — Home Assistant finds it automatically
- **Local** — no internet connection needed after installation

## Installation

### Home Assistant Add-on Repository

1. **Add this repository to Home Assistant:**
   - Go to **Settings → Add-ons → Add-on Store**
   - Click the **⋮** menu (top right) → **Repositories**
   - Add: `https://github.com/chrishoage/kokoro-wyoming`
   - Click **Add** → **Close**

   Or click the button at the top of this page.

2. **Install the add-on:**
   - Refresh the page (or click **Check for updates**)
   - Find **"Wyoming Kokoro TTS"** in the add-on store
   - Click **Install**

   > **Note**: First install downloads the Kokoro model files (~350MB). This may take a few minutes depending on your connection.

3. **Configure the add-on** (optional):
   - Go to the **Configuration** tab
   - Set `voice` to your preferred default voice (default: `af_heart`)
   - Enable `debug` for verbose logging if needed
   - Click **Save**

4. **Start the add-on:**
   - Go to the **Info** tab
   - Click **Start**
   - Enable **Start on boot** if desired

5. **Connect to Home Assistant (Auto-Discovery):**

   The add-on registers itself via Wyoming discovery automatically:
   - Go to **Settings → Devices & Services**
   - Look for the **"Discovered"** section — you should see **Wyoming Kokoro TTS**
   - Click **Configure** to add it

   **If not auto-discovered** (manual setup):
   - Click **Add Integration** → search for **Wyoming Protocol**
   - Enter the hostname shown in the add-on's **Info** tab and port `10200`

6. **Set as your TTS provider:**
   - Go to **Settings → Voice Assistants**
   - Edit your assistant (or create one)
   - Set **Text-to-speech** to **Wyoming Kokoro TTS**

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `voice` | `af_heart` | Default voice for synthesis |
| `debug` | `false` | Enable verbose debug logging |

## Voices

Available voices follow the naming convention `{language_prefix}_{name}`. A full list is in the [Kokoro VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md).

| Prefix | Language |
|--------|----------|
| `a` | English (US) |
| `b` | English (UK) |
| `e` | Spanish |
| `f` | French |
| `h` | Hindi |
| `i` | Italian |
| `j` | Japanese |
| `z` | Chinese |

## Acknowledgements

This add-on is a fork of the excellent work done by:

- [relvacode/kokoro-wyoming](https://github.com/relvacode/kokoro-wyoming)
- [nordwestt/kokoro-wyoming](https://github.com/nordwestt/kokoro-wyoming)

The add-on packaging and Home Assistant integration structure was heavily inspired by [araa47/wyoming_pocket_tts](https://github.com/araa47/wyoming_pocket_tts).

The underlying TTS engine is [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) running the [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) model.
