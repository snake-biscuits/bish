from __future__ import annotations
import enum
import io
from typing import List, Tuple

from .. import asm
from ..utils.binary import read_struct


class ShaderType(enum.Enum):
    # DirectX 10
    Pixel = 0x00
    Vertex = 0x01
    Geometry = 0x02
    # DirectX 11
    Hull = 0x03
    Domain = 0x04
    Compute = 0x05
    Reserved = 0xFFF0


class Shader_v5:
    """DirectX 11 (Shader Model 5) Shader"""
    type: ShaderType
    version: Tuple[int, int]
    instructions: List[asm.Instruction]

    def __init__(self):
        self.type = ShaderType(0x00)
        self.version = (5, 0)
        self.instructions = list()

    def __repr__(self) -> str:
        descriptor = f"v{self.version[0]}.{self.version[1]} ({self.type.name})"
        descriptor = f"{descriptor} {len(self.instructions)} instructions"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_bytes(cls, raw_chunk: bytes) -> Shader_v5:
        return cls.from_stream(io.BytesIO(raw_chunk))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Shader_v5:
        out = cls()
        version = read_struct(stream, "I")
        type_ = (version & 0xFFFF0000) >> 16
        major = (version & 0x000000F0) >> 4
        minor = (version & 0x0000000F) >> 0
        out.type = ShaderType(type_)
        out.version = (major, minor)
        length = read_struct(stream, "I")
        assert length >= 2, f"invalid length: {length}"
        out.instructions = list()
        tokens_read = 2
        while (tokens_read < length):
            try:
                instruction = asm.Instruction.from_stream(stream)
            except Exception as exc:
                print(f"! {tokens_read=}")
                raise exc
            tokens_read += len(instruction)
            out.instructions.append(instruction)
        assert tokens_read == length, f"overshot by {tokens_read - length} tokens"
        return out
