from __future__ import annotations
import io


class Statistics:
    num_instructions: int

    @classmethod
    def from_bytes(cls, raw_chunk: bytes) -> Statistics:
        assert len(raw_chunk) == 148
        return cls.from_stream(io.BytesIO(raw_chunk))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Statistics:
        out = cls()
        raise NotImplementedError()
        return out
