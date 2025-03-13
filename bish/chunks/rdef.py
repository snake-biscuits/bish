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
        # NOTE: should be called from .from_bytes(dxbc.RDEF)
        # -- otherwise calls to stream.seek will wreak havoc
        out = cls()
        start = stream.tell()
        num_const_buffers = read_struct(stream, "I")
        const_buffer_offset = read_struct(stream, "I")
        num_resource_bindings = read_struct(stream, "I")
        resource_binding_offset = read_struct(stream, "I")
        out.version = read_struct(stream, "2B")
        out.program_type = read_struct(stream, "H")
        out.flags = read_struct(stream, "I")
        creator_offset = read_struct(stream, "I")
        # raise NotImplementedError()
        stream.seek(start + const_buffer_offset)
        for i in range(num_const_buffers):
            out.const_buffers.append(ConstBuffer.from_stream(stream))
        stream.seek(start + resource_binding_offset)
        for i in range(num_resource_bindings):
            out.resource_bindings.append(ResourceBinding.from_stream(stream))
        stream.seek(start + creator_offset)
        out.creator = read_str(stream)
        return out


class ConstBuffer:
    name: ...

    def __repr__(self) -> str:
        descriptor = ...
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_bytes(cls, raw_chunk: bytes) -> ResourceDefinition:
        return cls.from_stream(io.BytesIO(raw_chunk))

    @classmethod
    def from_stream(cls, stream: io.BytesIO, version=(0, 5)) -> ResourceDefinition:
        out = cls()
        start = stream.tell()
        ...
        # header
        # name
        # shader variables
        stream.seek(start + ...)
        return out


class ShaderType:
    ...


class ShaderType_v5:
    ...


class ShaderVariable:
    name: str
    variable: bytes
    flags: int
    # idk the lengths to read these, so I'm just gonna keep the offsets for now
    type_offset: int
    default_variable_offset: int

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ShaderVariable:
        out = cls()
        start = stream.tell()
        name_offset = read_struct(stream, "I")
        variable_offset = read_struct(stream, "I")
        variable_length = read_struct(stream, "I")
        out.flags = read_struct(stream, "I")
        out.type_offset = read_struct(stream, "I")  # ???
        out.default_variable_offset = read_struct(stream, "I")  # ???
        stream.seek(name_offset)
        out.name = read_str(stream)
        stream.seek(variable_offset)
        out.variable = stream.read(variable_length)
        out.seek(start + 6 * 4)
        return out


class ShaderVariable_v5(ShaderVariable):
    texture: bytes
    sampler: bytes

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ShaderVariable:
        out = super(cls).from_stream(stream)
        start = stream.tell()
        raise NotImplementedError()
        texture_offset = read_struct(stream, "I")
        texture_length = read_struct(stream, "I")
        sampler_offset = read_struct(stream, "I")
        sampler_length = read_struct(stream, "I")
        stream.seek(texture_offset)
        out.texture = stream.read(texture_length)
        stream.seek(sampler_offset)
        out.sampler = stream.read(sampler_length)
        out.seek(start + 4 * 4)
        return out


class ResourceBinding:
    name: str
    type: int  # TODO: enum
    return_type: int  # TODO: enum
    dimension: int  # needs enum?
    num_samples: int
    bind_point: int
    bind_count: int
    flags: int

    def __repr__(self) -> str:
        # TODO: include type & return_type enum names in descriptor
        descriptor = f"{self.name}"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_bytes(cls, raw_chunk: bytes) -> ResourceDefinition:
        return cls.from_stream(io.BytesIO(raw_chunk))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ResourceDefinition:
        out = cls()
        start = stream.tell()
        name_offset = read_struct(stream, "I")
        out.type = read_struct(stream, "I")
        out.return_type = read_struct(stream, "I")
        out.dimension = read_struct(stream, "I")
        out.num_samples = read_struct(stream, "I")
        out.bind_point = read_struct(stream, "I")
        out.bind_count = read_struct(stream, "I")
        out.flags = read_struct(stream, "I")
        stream.seek(name_offset)  # relative to chunk!
        out.name = read_str(stream)
        stream.seek(start + 8 * 4)
        return out
