from __future__ import annotations
import enum
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
        print(f"parsing {cls.__name__} @ {start}")
        num_const_buffers = read_struct(stream, "I")
        const_buffer_offset = read_struct(stream, "I")
        num_resource_bindings = read_struct(stream, "I")
        resource_binding_offset = read_struct(stream, "I")
        out.version = read_struct(stream, "2B")
        out.program_type = read_struct(stream, "h")
        out.flags = read_struct(stream, "I")
        creator_offset = read_struct(stream, "I")
        # TODO: bytes 28 -> 60
        # -- RD11 ???
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
    name: str
    variables: List[ShaderVariable]
    flags: int
    buffer_type: int  # TODO: enum
    unknown: int

    def __repr__(self) -> str:
        descriptor = f"{self.name}"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_bytes(cls, raw_chunk: bytes) -> ConstBuffer:
        return cls.from_stream(io.BytesIO(raw_chunk))

    @classmethod
    def from_stream(cls, stream: io.BytesIO, version=(0, 5)) -> ConstBuffer:
        out = cls()
        start = stream.tell()
        print(f"parsing {cls.__name__} @ {start} -> {start + 24}")
        name_offset = read_struct(stream, "I")
        variable_count = read_struct(stream, "I")
        variable_offset = read_struct(stream, "I")
        out.flags = read_struct(stream, "I")
        out.buffer_type = read_struct(stream, "I")
        out.unknown = read_struct(stream, "I")
        # name
        stream.seek(name_offset)
        out.name = read_str(stream)
        # variables
        assert version[0] == 0
        if version[1] < 5:
            variable_class = ShaderVariable
        elif version[1] == 5:
            variable_class = ShaderVariable_v5
        else:
            v = f"v{version[0]}.{version[1]}"
            raise NotImplementedError(f"unknown ShaderVariable version: {v}")
        stream.seek(variable_offset)
        out.variables = [
            variable_class.from_stream(stream)
            for i in range(variable_count)]
        # return to end of header
        stream.seek(start + 6 * 4)
        return out


class ShaderType:
    var_class: VariableClass
    var_type: VariableType
    rows: int
    columns: int
    num_elements: int
    members: bytes

    def __repr__(self) -> str:
        descriptor = f"{self.var_class.name} {self.var_type.name}"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_stream(cls, stream) -> ShaderType:
        out = cls()
        start = stream.tell()
        print(f"parsing {cls.__name__} @ {start} -> {start + 16}")
        out.var_class = VariableClass(read_struct(stream, "h"))
        out.var_type = VariableType(read_struct(stream, "H"))
        out.rows = read_struct(stream, "H")
        out.columns = read_struct(stream, "H")
        out.num_elements = read_struct(stream, "H")
        num_members = read_struct(stream, "H")
        member_offset = read_struct(stream, "I")
        # members
        stream.seek(member_offset)
        out.members = read_struct(stream, f"{num_members}B")  # guessing
        stream.seek(start + 16)
        return out


class ShaderType_v5(ShaderType):
    parent_type_offset: int
    unknown: Tuple[int, int, int]
    parent_name: str

    @classmethod
    def from_stream(cls, stream) -> ShaderType_v5:
        out = super(ShaderType_v5, cls).from_stream(stream)
        start = stream.tell()
        print(f"parsing {cls.__name__} @ {start} -> {start + 20}")
        out.parent_type_offset = read_struct(stream, "I")
        out.unknown = read_struct(stream, "3I")
        parent_name_offset = read_struct(stream, "I")
        # parent_name
        stream.seek(parent_name_offset)
        out.parent_name = read_str(stream)
        stream.seek(start + 4 * 5)
        return out


class VariableClass(enum.Enum):
    D3D_SCALAR = 0
    D3D_VECTOR = 1
    D3D_MATRIX_ROWS = 2
    D3D_MATRIX_COLUMNS = 3
    D3D_OBJECT = 4
    D3D_STRUCT = 5
    D3D_INTERFACE_CLASS = 6
    D3D_INTERFACE_POINTER = 7
    D3D10_SCALAR = 8
    D3D10_VECTOR = 9
    D3D10_MATRIX_ROWS = 10
    D3D10_MATRIX_COLUMNS = 11
    D3D10_OBJECT = 12
    D3D10_STRUCT = 13
    D3D11_INTERFACE_CLASS = 14
    D3D11_INTERFACE_POINTER = 15
    FORCE_DWORD = -1


class VariableType(enum.Enum):
    VOID = 0
    BOOL = 1
    INT = 2
    FLOAT = 3
    STRING = 4
    TEXTURE = 5
    TEXTURE_1D = 6
    TEXTURE_2D = 7
    TEXTURE_3D = 8
    TEXTURE_CUBE = 9
    SAMPLER = 10
    PIXEL_SHADER = 15
    VERTEX_SHADER = 16
    UINT = 19
    UINT8 = 20
    GEOMETRY_SHADER = 21
    RASTERISER = 22
    DEPTH_STENCIL = 23
    BLEND = 24
    BUFFER = 25
    CBUFFER = 26
    TBUFFER = 27
    TEXTURE_1D_ARRAY = 28
    TEXTURE_2D_ARRAY = 29
    RENDER_TARGET_VIEW = 30
    DEPTH_STENCIL_VIEW = 31
    TEXTURE_2D_MULTISAMPLED = 32
    TEXTURE_2D_MULTISAMPLED_ARRAY = 33
    TEXTURE_CUBE_ARRAY = 34
    # DX11
    HULL_SHADER = 35
    DOMAIN_SHADER = 36
    INTERFACE_POINTER = 37
    COMPUTE_SHADER = 38
    DOUBLE = 39
    READ_WRITE_TEXTURE_1D = 40
    READ_WRITE_TEXTURE_1D_ARRAY = 41
    READ_WRITE_TEXTURE_2D = 42
    READ_WRITE_TEXTURE_2D_ARRAY = 43
    READ_WRITE_TEXTURE_3D = 44
    READ_WRITE_BUFFER = 45
    BYTE_ADDRESS_BUFFER = 46
    READ_WRITE_BYTE_ADDRESS_BUFFER = 47
    STRUCTURED_BUFFER = 48
    READ_WRITE_STRUCTURED_BUFFER = 49
    APPEND_STRUCTURED_BUFFER = 50
    CONSUME_STRUCTURED_BUFFER = 51


class ShaderVariable:
    name: str
    variable: bytes
    flags: int
    # idk the lengths to read these, so I'm just gonna keep the offsets for now
    type_offset: int
    default_variable_offset: int

    def __repr__(self) -> str:
        descriptor = f"{self.name}"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ShaderVariable:
        out = cls()
        start = stream.tell()
        print(f"parsing {cls.__name__} @ {start} -> {start + 24}")
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
        stream.seek(start + 6 * 4)
        return out


class ShaderVariable_v5(ShaderVariable):
    texture: bytes
    sampler: bytes

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ShaderVariable:
        out = super(ShaderVariable_v5, cls).from_stream(stream)
        start = stream.tell()
        print(f"parsing {cls.__name__} @ {start} -> {start + 16}")
        texture_offset = read_struct(stream, "I")
        texture_length = read_struct(stream, "I")
        sampler_offset = read_struct(stream, "I")
        sampler_length = read_struct(stream, "I")
        # texture
        stream.seek(texture_offset)
        out.texture = stream.read(texture_length)
        # sampler
        stream.seek(sampler_offset)
        out.sampler = stream.read(sampler_length)
        stream.seek(start + 4 * 4)
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
        print(f"parsing {cls.__name__} @ {start} -> {start + 32}")
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
