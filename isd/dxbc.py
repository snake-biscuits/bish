from __future__ import annotations
import io
import struct
from typing import Dict, Union


class DXBC:
    checksum: bytes
    filesize: int
    chunks: Dict[str, Union[bytes, Any]]
    # ^ {"RDEF": RDEF(...), "SHEX": b"..."}

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
        header = struct.unpack("4s16s3I", stream.read(32))
        magic, checksum, one, filesize, num_chunks = header
        assert magic == b"DXBC"
        out.checksum = checksum
        assert one == 1
        out.filesize = filesize
        chunk_offsets = struct.unpack(f"{num_chunks}I", stream.read(num_chunks * 4))
        out.chunks = dict()
        for offset in chunk_offsets:
            stream.seek(offset)
            chunk_id, chunk_size = struct.unpack("4sI", stream.read(8))
            chunk_id = chunk_id.decode("ascii", "strict")
            assert chunk_size < filesize
            assert not any(
                offset < other_offset < offset + chunk_size
                for other_offset in chunk_offsets)
            chunk_data = stream.read(chunk_size)
            # TODO: convert data from bytes
            out.chunks[chunk_id] = chunk_data
        return out
