"""
core/stream_parser.py
Streaming Token Chunk Parser for Nemotron Chain-of-Thought (CoT)
================================================================
Extracts internal reasoning tokens (<thought>...</thought> or [THINKING])
in real time and pipes them separately into the AG-UI live thought feed
without buffering or blocking user-facing markdown rendering.
"""

from typing import Iterator, Tuple


class NemotronStreamParser:
    """
    Real-time state machine separating reasoning thoughts from public response.
    Yields tuples of (channel: str, chunk: str) where channel is 'thought' or 'content'.
    """

    def __init__(self):
        self.in_thought = False
        self.buffer = ""

    def parse_stream(self, token_generator: Iterator[str]) -> Iterator[Tuple[str, str]]:
        for chunk in token_generator:
            self.buffer += chunk

            # Check if entering thought mode
            if not self.in_thought and "<thought>" in self.buffer:
                before, after = self.buffer.split("<thought>", 1)
                if before:
                    yield ("content", before)
                self.in_thought = True
                self.buffer = after

            # Check if exiting thought mode
            if self.in_thought and "</thought>" in self.buffer:
                thought_text, after = self.buffer.split("</thought>", 1)
                if thought_text:
                    yield ("thought", thought_text)
                self.in_thought = False
                self.buffer = after
                continue

            # Check for alternative [THINKING] tags
            if not self.in_thought and "[THINKING]" in self.buffer:
                before, after = self.buffer.split("[THINKING]", 1)
                if before:
                    yield ("content", before)
                self.in_thought = True
                self.buffer = after

            if self.in_thought and "[/THINKING]" in self.buffer:
                thought_text, after = self.buffer.split("[/THINKING]", 1)
                if thought_text:
                    yield ("thought", thought_text)
                self.in_thought = False
                self.buffer = after
                continue

            # Flush current chunk according to state
            if self.in_thought:
                # Keep small buffer in case closing tag is cut across chunks
                if len(self.buffer) > 10:
                    flushable = self.buffer[:-10]
                    self.buffer = self.buffer[-10:]
                    yield ("thought", flushable)
            else:
                if len(self.buffer) > 10:
                    flushable = self.buffer[:-10]
                    self.buffer = self.buffer[-10:]
                    yield ("content", flushable)

        # Flush any remaining buffer
        if self.buffer:
            channel = "thought" if self.in_thought else "content"
            yield (channel, self.buffer)
            self.buffer = ""
