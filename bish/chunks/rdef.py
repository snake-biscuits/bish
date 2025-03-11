from __future__ import annotations
import io
from typing import Any, List, Tuple

from ..utils.binary import read_str, read_struct


class ResourceDefinition:
    """constant buffers & resource bindings"""
    version: Tuple[int]  # (major, minor)
    program_type: int  # TODO: enum.Enum
    flags: int  # TODO: enum.IntFlags
    const_buffers: List[Any]
    resource_bindings: List[Any]
    creator: str  # compiler name & version etc.

    def __init__(self):
        self.const_buffers = list()
        self.resource_bindings = list()

    def __repr__(self) -> str:
        descriptor = f"v{self.version[0]}.{self.version[1]}"
        # TODO: program_type.name
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_bytes(cls, raw_chunk: bytes) -> ResourceDefinition:
        return cls.from_stream(io.BytesIO(raw_chunk))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ResourceDefinition:
        out = cls()
        start = stream.tell()
        num_const_buffers = read_struct(stream, "I")
        const_buffer_offset = read_struct(stream, "I")
        num_resource_bindings = read_struct(stream, "I")
        resource_binding_offset = read_struct(stream, "I")
        out.version, out.program_type = read_struct(stream, "2BH")
        out.flags = read_struct(stream, "I")
        creator_offset = read_struct(stream, "I")
        raise NotImplementedError()
        # TODO: classes for each buffer + version variants
        stream.seek(start + const_buffer_offset)
        for i in range(num_const_buffers):
            ...  # ConstBufferClass.from_stream(stream)
        stream.seek(start + resource_binding_offset)
        for i in range(num_resource_bindings):
            ...  # ResourceBindingClass.from_stream(stream)
        stream.seek(start + creator_offset)
        out.creator = read_str(stream)
        return out


class ConstBuffer:
    ...


class ResourceBinding:
    ...
