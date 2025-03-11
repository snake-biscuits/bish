from __future__ import annotations
import enum
import io
from typing import List

from . import opcodes
from ...utils.binary import read_struct


class Type(enum.Enum):
    COMMENT = 0x00
    DEBUG_INFO = 0x01
    OPAQUE = 0x02
    DCL_IMMEDIATE_CONSTANT_BUFFER = 0x03
    SHADER_MESSAGE = 0x04
    SHADER_CLIP_PLANE_CONSTANT_MAPPINGS = 0x05  # for DirectX 9


class CustomDataBlock:
    type: Type
    tokens: List[int]

    def __repr__(self) -> str:
        descriptor = f"{self.type.name} {len(self.tokens) - 2} tokens"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def __len__(self) -> int:
        return len(self.tokens)

    def as_bytes(self) -> bytes:
        return b"".join(
            token.to_bytes(4, "little")
            for token in self.tokens)

    @classmethod
    def from_bytes(cls, raw_block: bytes) -> CustomDataBlock:
        return cls.from_stream(io.BytesIO(raw_block))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> CustomDataBlock:
        out = cls()
        token = read_struct(stream, "I")
        opcode = opcodes.opcode_for(token & 0x000003FF)  # [10:00]
        assert opcode == opcodes.D3D_10_0.CUSTOM_DATA
        out.type = Type(token >> 11)  # [32:11]
        num_tokens = read_struct(stream, "I")
        assert num_tokens >= 2, "invalid custom data length"
        # TODO: parse the rest of the block
        out.tokens = [token, num_tokens, *read_struct(stream, f"{num_tokens - 2}I")]
        return out
