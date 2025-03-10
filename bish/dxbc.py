from __future__ import annotations
import io
import struct
from typing import Dict, Tuple

from .utils.binary import read_struct


class DXBC:
    checksum: bytes
    filesize: int
    chunks: Dict[str, Tuple[int, int]]
    # ^ {"id": (offset, length)}

    def __repr__(self) -> str:
        descriptor = f"{len(self.chunks)} chunks {self.filesize} bytes"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

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
        out.chunks = dict()
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
            data = stream.read(length)
            assert len(data) == length
            # TODO: convert data from bytes
            setattr(out, name, data)
        # NOTE: we're closing the stream now, hope we got everything!
        return out
