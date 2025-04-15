from __future__ import annotations
import io
import struct
from typing import Dict, Tuple

from . import chunks
from .utils.binary import read_struct


class DXBC:
    checksum: bytes
    filesize: int
    chunks: Dict[str, Tuple[int, int]]
    # ^ {"id": (offset, length)}
    loading_errors: Dict[str, Exception]
    # ^ {"id": Error}

    def __init__(self):
        self.chunks = dict()
        self.loading_errors = dict()
        # defaults
        self.checksum = b""
        self.filesize = 0

    def __repr__(self) -> str:
        descriptor = f"{len(self.chunks)} chunks {self.filesize} bytes"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def as_bytes(self) -> bytes:
        """for extracting from .vcs"""
        header = [
            b"DXBC",
            self.checksum,
            struct.pack("3I", 1, self.filesize, len(self.chunks))]
        chunk_offsets, chunk_data = list(), list()
        # TODO: verify chunk offsets line up
        for name, (offset, length) in self.chunks.items():
            raw_chunk = getattr(self, f"RAW_{name}")
            assert isinstance(raw_chunk, bytes)
            assert len(raw_chunk) == length
            chunk_offsets.append(struct.pack("I", offset))
            chunk_data.extend([
                name.encode("ascii", "strict"),
                struct.pack("I", length),
                raw_chunk])
        return b"".join([
            *header,
            *chunk_offsets,
            *chunk_data])

    def save_as(self, filename: str):
        with open(filename, "wb") as out_file:
            out_file.write(self.as_bytes())

    @classmethod
    def from_bytes(cls, raw_data: bytes) -> DXBC:
        return cls.from_stream(io.BytesIO(raw_data))

    @classmethod
    def from_file(cls, filename: str) -> DXBC:
        with open(filename, "rb") as stream:
            return cls.from_stream(stream)

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> DXBC:
        out = cls()
        header = read_struct(stream, "4s16s3I")
        magic, checksum, one, filesize, num_chunks = header
        assert magic == b"DXBC"
        out.checksum = checksum
        assert one == 1
        out.filesize = filesize
        chunk_offsets = struct.unpack(f"{num_chunks}I", stream.read(num_chunks * 4))
        for offset in chunk_offsets:
            stream.seek(offset)
            assert stream.tell() == offset
            name, length = read_struct(stream, "4sI")
            name = name.decode("ascii", "strict")
            out.chunks[name] = (offset, length)
            assert length < filesize
            assert not any(
                offset < other_offset < offset + length
                for other_offset in chunk_offsets)
            raw_chunk = stream.read(length)
            assert len(raw_chunk) == length
            if name in chunks.parser:
                try:
                    parsed_chunk = chunks.parser[name].from_bytes(raw_chunk)
                    setattr(out, name, parsed_chunk)
                    setattr(out, f"RAW_{name}", raw_chunk)  # for debugging
                except Exception as exc:
                    out.loading_errors[name] = exc
                    setattr(out, name, raw_chunk)
            else:
                setattr(out, name, raw_chunk)
        # NOTE: we're closing the stream now, hope we got everything!
        return out
