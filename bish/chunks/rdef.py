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
        print(f'({start}, {start + 60}): "{cls.__name__}",')
        num_const_buffers = read_struct(stream, "I")
        const_buffer_offset = read_struct(stream, "I")
        num_resource_bindings = read_struct(stream, "I")
        resource_binding_offset = read_struct(stream, "I")
        out.version = read_struct(stream, "2B")
        out.program_type = read_struct(stream, "h")
        out.flags = read_struct(stream, "I")
        creator_offset = read_struct(stream, "I")
        # struct sizes?
        unknown = (b"RD11", 60, 24, 32, 40, 36, 12, 0)
        assert read_struct(stream, "4s7I") == unknown
        # const buffers
        stream.seek(start + const_buffer_offset)
        for i in range(num_const_buffers):
            out.const_buffers.append(ConstBuffer.from_stream(stream))
        s = start + const_buffer_offset
        e = s + 24 * num_const_buffers
        print(f'({s}, {e}): "ConstBuffers",')
        # resource bindings
        stream.seek(start + resource_binding_offset)
        for i in range(num_resource_bindings):
            out.resource_bindings.append(ResourceBinding.from_stream(stream))
        s = start + resource_binding_offset
        e = s + 32 * num_resource_bindings
        print(f'({s}, {e}): "ResourceBindings",')
        # creator
        stream.seek(start + creator_offset)
        out.creator = read_str(stream)
        s = start + creator_offset
        e = s + len(out.creator) + 1
        print(f'({s}, {e}): "ResourceDefinition.creator",')
        # NOTE: stream.tell() should be at the end of the lump
        return out


class ConstBuffer:
    name: str
    variables: List[ShaderVariable]
    flags: int
    buffer_type: int  # TODO: enum
    unknown: int

    def __repr__(self) -> str:
        descriptor = f"{self.name} {len(self.variables)} variables"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_bytes(cls, raw_chunk: bytes) -> ConstBuffer:
        return cls.from_stream(io.BytesIO(raw_chunk))

    @classmethod
    def from_stream(cls, stream: io.BytesIO, version=(0, 5)) -> ConstBuffer:
        out = cls()
        start = stream.tell()
        name_offset = read_struct(stream, "I")
        variable_count = read_struct(stream, "I")
        variable_offset = read_struct(stream, "I")
        out.flags = read_struct(stream, "I")
        out.buffer_type = read_struct(stream, "I")
        out.unknown = read_struct(stream, "I")
        # name
        stream.seek(name_offset)
        out.name = read_str(stream)
        s = name_offset
        e = s + len(out.name) + 1
        print(f'({s}, {e}): "ConstBuffer.name",')
        # variables
        assert version[0] == 0
        if version[1] < 5:
            variable_class = ShaderVariable
        elif version[1] == 5:
            variable_class = ShaderVariable_v5
        else:
            v = f"v{version[0]}.{version[1]}"
            raise NotImplementedError(f"unknown ShaderVariable version: {v}")
        # variables
        stream.seek(variable_offset)
        out.variables = [
            variable_class.from_stream(stream)
            for i in range(variable_count)]
        s = variable_offset
        e = s + {(0, 5): 40}[version] * variable_count
        print(f'({s}, {e}): "ShaderVariables",')
        stream.seek(start + 24)
        return out


class ShaderType:
    var_class: VariableClass
    var_type: VariableType
    rows: int
    columns: int
    num_elements: int
    members: bytes  # List[ShaderType]

    def __repr__(self) -> str:
        descriptor = f"{self.var_class.name} {self.var_type.name}"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_stream(cls, stream) -> ShaderType:
        out = cls()
        start = stream.tell()
        print(f'({start}, {start + 16}): "{cls.__name__}",')
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
        print(f'({member_offset}, {member_offset + num_members}): "ShaderType.members",')
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
        print(f'({start}, {start + 20}): "{cls.__name__}",')
        out.parent_type_offset = read_struct(stream, "I")
        out.unknown = read_struct(stream, "3I")
        parent_name_offset = read_struct(stream, "I")
        # parent_name
        stream.seek(parent_name_offset)
        out.parent_name = read_str(stream)
        s = parent_name_offset
        e = s + len(out.parent_name) + 1
        print(f'({s}, {e}): "ShaderType_v5.parent_name",')
        stream.seek(start + 20)
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
        name_offset = read_struct(stream, "I")
        variable_offset = read_struct(stream, "I")
        variable_length = read_struct(stream, "I")
        out.flags = read_struct(stream, "I")
        out.type_offset = read_struct(stream, "I")  # ShaderType?
        out.default_variable_offset = read_struct(stream, "I")  # ???
        # name
        stream.seek(name_offset)
        out.name = read_str(stream)
        s = name_offset
        e = s + len(out.name) + 1
        print(f'({s}, {e}): "ShaderVariable.name",')
        # variable
        stream.seek(variable_offset)
        out.variable = stream.read(variable_length)
        stream.seek(start + 24)
        return out


class ShaderVariable_v5(ShaderVariable):
    texture: bytes
    sampler: bytes

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ShaderVariable:
        out = super(ShaderVariable_v5, cls).from_stream(stream)
        start = stream.tell()
        texture_offset = read_struct(stream, "i")
        texture_length = read_struct(stream, "I")
        sampler_offset = read_struct(stream, "i")
        sampler_length = read_struct(stream, "I")
        # texture
        if texture_offset != -1:
            stream.seek(texture_offset)
            out.texture = stream.read(texture_length)
            s = texture_offset
            e = s + texture_length
            print(f'({s}, {e}): "ShaderVariable_v5.texture",')
        else:
            assert texture_length == 0
            out.texture = b""
        # sampler
        if sampler_offset != -1:
            stream.seek(sampler_offset)
            out.sampler = stream.read(sampler_length)
            s = sampler_offset
            e = s + sampler_length
            print(f'({s}, {e}): "ShaderVariable_v5.sampler",')
        else:
            assert sampler_length == 0
            out.sampler = b""
        stream.seek(start + 16)
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
    def from_bytes(cls, raw_chunk: bytes) -> ResourceBinding:
        return cls.from_stream(io.BytesIO(raw_chunk))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ResourceBinding:
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
        # name
        stream.seek(name_offset)
        out.name = read_str(stream)
        print(f'({name_offset}, {name_offset + len(out.name) + 1}): "ResourceBinding.name",')
        stream.seek(start + 32)
        return out
