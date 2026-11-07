# Wyoming Kokoro TTS

Runs the [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) text-to-speech
model locally and exposes it to Home Assistant over the
[Wyoming protocol](https://github.com/rhasspy/wyoming).

## Setup

1. Install and start the app. The first install builds the image and
   downloads the Kokoro model (~350 MB), so it can take a while.
2. Home Assistant discovers the app automatically. Go to
   **Settings → Devices & services**, find **Wyoming Protocol** under
   **Discovered** and select **Add**.
3. Go to **Settings → Voice assistants**, edit your assistant and set
   **Text-to-speech** to **Kokoro**.

If the app isn't discovered, add the **Wyoming Protocol** integration
manually with the hostname shown on the app's **Info** tab and port `10200`.

## Configuration

| Option | Default | Description |
| --- | --- | --- |
| `voice` | `af_heart` | Voice used when Home Assistant doesn't request one |
| `speed` | `1.0` | Speaking rate, from `0.5` to `2.0` |
| `cache_size` | `128` | Sentences kept in memory for instant replay, `0` disables |
| `debug` | `false` | Verbose logging |

Each voice can also be picked per assistant in Home Assistant, which overrides
the default above.

## Voices

Voice names start with a language letter and a gender letter (`f`/`m`). See
the [Kokoro voice list](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)
for samples and quality grades.

| Prefix | Language |
| --- | --- |
| `a` | English (US) |
| `b` | English (UK) |
| `e` | Spanish |
| `f` | French |
| `h` | Hindi |
| `i` | Italian |
| `j` | Japanese |
| `p` | Portuguese (Brazil) |
| `z` | Chinese |

The server currently phonemizes every voice as English (US for `a` voices,
UK for the rest), so the non-English voices work best with English text.

## Streaming

With Home Assistant 2025.7 or later, responses from an LLM-backed assistant
are streamed: each sentence is spoken as soon as it's generated, instead of
after the whole reply is ready.
