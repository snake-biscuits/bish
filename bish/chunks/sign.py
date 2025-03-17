from __future__ import annotations
import io
from typing import List

from ..utils.binary import read_str, read_struct


class Signature:
    """Input (ISGN) / Output (OSGN) Signature"""
    unique_key: int
    elements: List[Element]

    @classmethod
    def from_bytes(cls, raw_isgn: bytes) -> Signature:
        return cls.from_stream(io.BytesIO(raw_isgn))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Signature:
        out = cls()
        num_elements = read_struct(stream, "I")
        out.unique_key = read_struct(stream, "I")
        out.elements = [
            Element.from_stream(stream)
            for i in range(num_elements)]
        return out


class Element:
    name: str
    semantic_index: int
    semantic_value_type: int
    component_type: int
    register: int
    mask: int
    read_write_mask: int
    unknown: int

    def __repr__(self) -> str:
        descriptor = f"{self.name}"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Element:
        out = cls()
        start = stream.tell()
        name_offset = read_struct(stream, "I")
        out.semantic_index = read_struct(stream, "I")
        out.semantic_value_type = read_struct(stream, "I")
        out.component_type = read_struct(stream, "I")
        out.register = read_struct(stream, "I")
        out.mask = read_struct(stream, "B")
        out.read_write_mask = read_struct(stream, "B")
        out.unknown = read_struct(stream, "H")
        stream.seek(name_offset)
        out.name = read_str(stream)
        stream.seek(start + 24)
        return out
