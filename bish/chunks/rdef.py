from __future__ import annotations
import io


class ResourceDefinition:
    """constant buffers & resource bindings"""
    # TODO: creator: str  # compiler id / name / signature

    @classmethod
    def from_bytes(cls, raw_chunk: bytes) -> ResourceDefinition:
        return cls.from_stream(io.BytesIO(raw_chunk))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ResourceDefinition:
        out = cls()
        raise NotImplementedError()
        return out

