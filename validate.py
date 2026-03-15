#!/usr/bin/env python3
"""Validates that the Kokoro Wyoming server is running and responding correctly."""
import asyncio
import sys

from wyoming.client import AsyncClient
from wyoming.info import Describe, Info
from wyoming.tts import Synthesize, SynthesizeVoice
from wyoming.audio import AudioStart, AudioChunk, AudioStop

URI = "tcp://127.0.0.1:10200"
TEST_TEXT = "Hello, this is a validation test."


async def validate():
    errors = []

    async with AsyncClient.from_uri(URI) as client:
        # --- Describe / Info ---
        await client.write_event(Describe().event())
        event = await client.read_event()
        if event is None:
            print("FAIL describe: no response")
            sys.exit(1)

        info = Info.from_event(event)
        if not info.tts:
            errors.append("no TTS programs in Info response")
        else:
            program = info.tts[0]
            print(f"OK   describe: {program.name} v{program.version}, {len(program.voices)} voices")

        # --- Synthesize ---
        voice = info.tts[0].voices[0].name if info.tts and info.tts[0].voices else "af_heart"
        await client.write_event(
            Synthesize(text=TEST_TEXT, voice=SynthesizeVoice(name=voice)).event()
        )

        got_start = False
        chunks = 0
        total_bytes = 0
        got_stop = False

        while True:
            event = await asyncio.wait_for(client.read_event(), timeout=30)
            if event is None:
                errors.append("connection closed before AudioStop")
                break
            if AudioStart.is_type(event.type):
                start = AudioStart.from_event(event)
                got_start = True
                print(f"OK   audio-start: rate={start.rate} width={start.width} channels={start.channels}")
            elif AudioChunk.is_type(event.type):
                chunk = AudioChunk.from_event(event)
                chunks += 1
                total_bytes += len(chunk.audio)
            elif AudioStop.is_type(event.type):
                got_stop = True
                break

        if not got_start:
            errors.append("never received AudioStart")
        if chunks == 0:
            errors.append("received no AudioChunk events")
        if not got_stop:
            errors.append("never received AudioStop")

        if got_stop:
            duration_ms = (total_bytes // 2) * 1000 // start.rate  # 16-bit mono
            print(f"OK   audio: {chunks} chunks, {total_bytes} bytes (~{duration_ms}ms)")

    if errors:
        for e in errors:
            print(f"FAIL {e}")
        sys.exit(1)

    print("PASS")


if __name__ == "__main__":
    asyncio.run(validate())
