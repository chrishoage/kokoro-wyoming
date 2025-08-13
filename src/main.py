#!/usr/bin/env python3
import argparse
import asyncio
import logging
import signal
from functools import partial
from typing import Optional

import kokoro_onnx.config
from wyoming.error import Error
from wyoming.server import AsyncEventHandler
from kokoro_onnx import Kokoro
from kokoro_onnx.log import log
import numpy as np

from wyoming.info import (
    Attribution,
    TtsProgram,
    TtsVoice,
    TtsVoiceSpeaker,
    Describe,
    Info,
)
from wyoming.server import AsyncServer
from wyoming.tts import (
    Synthesize,
    SynthesizeChunk,
    SynthesizeStart,
    SynthesizeStop,
    SynthesizeStopped,
)
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
import re

_LOGGER = log.getChild(__name__)
VERSION = "0.1"


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences using punctuation boundaries.

    Args:
        text: Input text to split

    Returns:
        List of sentences

    Example:
        >>> text = "Hello world! How are you? I'm doing great."
        >>> split_into_sentences(text)
        ['Hello world!', 'How are you?', "I'm doing great."]
    """
    # First normalize whitespace and clean the text
    text = " ".join(text.strip().split())

    # Split on sentence boundaries
    pattern = r"(?<=[.!?])\s+"
    sentences = re.split(pattern, text)

    # Filter out empty strings and strip whitespace
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences


def get_model_voices(model: Kokoro) -> list[TtsVoice]:

    return [
        TtsVoice(
            name=voice_id,
            description=voice_id,
            attribution=Attribution(name="", url=""),
            installed=True,
            version=None,
            languages=[
                (
                    "en"
                    if voice_id.startswith("a")
                    else (
                        "it"
                        if voice_id.startswith("i")
                        else (
                            "jp"
                            if voice_id.startswith("j")
                            else (
                                "cn"
                                if voice_id.startswith("z")
                                else (
                                    "es"
                                    if voice_id.startswith("e")
                                    else (
                                        "fr"
                                        if voice_id.startswith("f")
                                        else "hi" if voice_id.startswith("h") else "en"
                                    )
                                )
                            )
                        )
                    )
                )
            ],
            speakers=[TtsVoiceSpeaker(name=voice_id.split("_")[1])],
        )
        for voice_id in model.voices.keys()
    ]


class KokoroEventHandler(AsyncEventHandler):
    def __init__(self, wyoming_info: Info, kokoro_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.kokoro = kokoro_instance
        self.args = args
        self.wyoming_info_event = wyoming_info.event()
        self.is_streaming = False
        self._synthesize = None

    async def handle_event(self, event: Event) -> bool:
        """Handle Wyoming protocol events."""

        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent description info")
            return True

        elif Synthesize.is_type(event.type):
            if self.is_streaming:
                # This event is sent for backwards compatibility reasons during streaming,
                # but should be treated as a noop in that mode.
                _LOGGER.debug("Ignoring Synthesize event while in streaming mode.")
                return True
            else:
                # If we're not already streaming, this is a one-shot request and we should actually synthesize.
                try:
                    synthesize = Synthesize.from_event(event)
                    return await self._handle_synthesize(synthesize)
                except Exception as err:
                    await self.write_event(
                        Error(text=str(err), code=err.__class__.__name__).event()
                    )
                    raise err
        elif SynthesizeStart.is_type(event.type):
            _LOGGER.debug("Starting streaming synthesis.")
            self.is_streaming = True
            stream_start = SynthesizeStart.from_event(event)
            self._synthesize = Synthesize(text="", voice=stream_start.voice)
            _LOGGER.debug("Text stream started: voice=%s", stream_start.voice)
            return True
        elif SynthesizeChunk.is_type(event.type):
            assert self._synthesize is not None
            assert self.is_streaming
            _LOGGER.debug("Synthesizing stream chunk.")
            stream_chunk = SynthesizeChunk.from_event(event)
            self._synthesize.text = stream_chunk.text
            await self._handle_synthesize(self._synthesize)
            return True
        elif SynthesizeStop.is_type(event.type):
            _LOGGER.debug("Stopping streaming synthesis.")
            await self.write_event(SynthesizeStopped().event())
            self._synthesize = None
            self.is_streaming = False
            return True

        else:
            _LOGGER.warning("Unexpected event: %s", event)
            return True

    """Handle text to speech synthesis request."""

    async def _handle_synthesize(self, synthesize: Synthesize) -> Optional[bool]:
        try:
            # Get voice settings
            voice_name = "af_heart"  # default voice
            if synthesize.voice:
                voice_name = synthesize.voice.name

            sentences = split_into_sentences(synthesize.text)

            i = 0
            t_bytes = 0
            for sentence in sentences:

                # Create audio stream
                stream = self.kokoro.create_stream(
                    sentence,
                    voice=voice_name,
                    speed=1.0,
                    lang="en-us" if voice_name.startswith("a") else "en-gb",
                )

                if i == 0:
                    # Send audio start
                    await self.write_event(
                        AudioStart(
                            rate=kokoro_onnx.config.SAMPLE_RATE,
                            width=2,
                            channels=1,
                        ).event()
                    )
                    i += 1

                # Process each chunk from the stream
                async for audio, sample_rate in stream:
                    # Convert float32 to int16
                    audio_int16 = (audio * 32767).astype(np.int16)
                    audio_bytes = audio_int16.tobytes()

                    t_bytes += len(audio_bytes)

                    # Send audio chunk
                    await self.write_event(
                        AudioChunk(
                            audio=audio_bytes,
                            rate=kokoro_onnx.config.SAMPLE_RATE,
                            width=2,
                            channels=1,
                        ).event()
                    )

            # Send audio stop
            await self.write_event(AudioStop().event())

            _LOGGER.debug("Synthesized %d bytes from %s", t_bytes, repr(synthesize))

            return True

        except Exception as e:
            _LOGGER.exception("Error synthesizing: %s", e)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="Host to listen on")
    parser.add_argument("--port", type=int, default=10200, help="Port to listen on")
    parser.add_argument(
        "--uri", default="tcp://0.0.0.0:10210", help="unix:// or tcp://"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    if args.debug:
        log.setLevel(level=logging.DEBUG)

    kokoro_instance = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    wyoming_voices = get_model_voices(kokoro_instance)

    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="Kokoro",
                description="A fast, local, kokoro-based tts engine",
                attribution=Attribution(
                    name="Kokoro TTS",
                    url="https://huggingface.co/hexgrad/Kokoro-82M",
                ),
                installed=True,
                voices=sorted(wyoming_voices, key=lambda v: v.name),
                version="1.5.0",
                supports_synthesize_streaming=True,
            )
        ]
    )

    _LOGGER.info("Kokoro Onyx server starting on %s", args.uri)
    server = AsyncServer.from_uri(args.uri)

    # Handle OS signals
    loop = asyncio.get_event_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, lambda: asyncio.create_task(server.stop()))

    # Start server with kokoro instance
    await server.run(partial(KokoroEventHandler, wyoming_info, kokoro_instance))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
