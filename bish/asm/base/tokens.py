from __future__ import annotations
import io


class Token:
    """baseclass for DWORD tokens"""

    def as_int(self) -> int:
        raise NotImplementedError()

    @classmethod
    def from_bytes(cls, raw_token: bytes) -> Token:
        assert len(raw_token) == 4
        int_ = int.from_bytes(raw_token, "little")
        return cls.from_token(int_)

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> Token:
        raw_token = stream.read(4)
        return cls.from_bytes(raw_token)

    @classmethod
    def from_token(cls, token: int) -> Token:
        raise NotImplementedError()
