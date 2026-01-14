from __future__ import annotations
import struct
from typing import Dict, Tuple

import breki
from breki.binary import read_struct
from breki.files.parsed import parse_first

from . import chunks


class FxcHeader(breki.Struct):
    __slots__ = [
        "magic", "checksum", "one", "filesize", "num_chunks"]
    _format = "4s16s3I"


class Fxc(breki.BinaryFile):
    exts = ["*.fxc"]
    code_page = breki.CodePage("ascii", "strict")
    # header
    header: FxcHeader
    # data
    chunks: Dict[str, Tuple[int, int]]
    # ^ {"id": (offset, length)}
    loading_errors: Dict[str, Exception]
    # ^ {"id": Error}

    def __init__(self, filepath: str, archive=None, code_page=None):
        super().__init__(filepath, archive, code_page)
        self.header = FxcHeader()
        self.chunks = dict()
        self.loading_errors = dict()

    @parse_first
    def __repr__(self) -> str:
        descriptor = f"{len(self.chunks)} chunks"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def as_bytes(self) -> bytes:
        chunk_offsets, chunk_data = list(), list()
        # TODO: verify chunk offsets line up
        for name, (offset, length) in self.chunks.items():
            raw_chunk = getattr(self, f"RAW_{name}")
            assert isinstance(raw_chunk, bytes)
            assert len(raw_chunk) == length
            chunk_offsets.append(struct.pack("I", offset))
            chunk_data.extend([
                self.code_page.encode(name),
                struct.pack("I", length),
                raw_chunk])
        return b"".join([
            *self.header.as_bytes(),
            *chunk_offsets,
            *chunk_data])

    def parse(self):
        if self.is_parsed:
            return
        self.is_parsed = True
        # header
        self.header = FxcHeader.from_stream(self.stream)
        assert self.header.magic == b"DXBC"
        assert self.header.one == 1
        assert self.header.filesize == self.size
        # chunks
        chunk_offsets = struct.unpack(
            f"{self.header.num_chunks}I",
            self.stream.read(self.header.num_chunks * 4))
        for offset in chunk_offsets:
            self.stream.seek(offset)
            assert self.stream.tell() == offset
            name, length = read_struct(self.stream, "4sI")
            name = self.code_page.decode(name)
            self.chunks[name] = (offset, length)
            assert offset + length < self.size
            assert not any(
                offset < other_offset < offset + length
                for other_offset in chunk_offsets)
            raw_chunk = self.stream.read(length)
            assert len(raw_chunk) == length
            setattr(self, f"RAW_{name}", raw_chunk)
            if name in chunks.parser:
                try:
                    parsed_chunk = chunks.parser[name].from_bytes(raw_chunk)
                    setattr(self, name, parsed_chunk)
                except Exception as exc:
                    self.loading_errors[name] = exc
        assert self.stream.tell() == self.size
