from __future__ import annotations
import io
from typing import Dict

from .utils.binary import read_struct
from . import dxbc


# TODO: .vcssubfile (patches?)


class VCS:
    """Valve Compiled Shader (Titanfall 1 variant)"""
    # https://developer.valvesoftware.com/wiki/VCS
    num_combos: int
    num_dynamic_combos: int
    flags: int  # TODO: enum
    centroid_mask: int
    num_static_combos: int  # idk, can be larger than num_combos
    crc: int  # CRC32
    unknown_1: int
    unknown_2: int
    filesize: int
    unknown_3: int
    unknown_4: int
    shaders: Dict[int, dxbc.DXBC]
    # ^ {shader_id: shader}

    def __init__(self):
        self.shaders = dict()

    def __repr__(self):
        descriptor = f"{len(self.shaders)} shaders"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    # TODO: export shaders .fxc

    @classmethod
    def from_bytes(cls, raw_data: bytes) -> VCS:
        return cls.from_stream(io.BytesIO(raw_data))

    @classmethod
    def from_file(cls, filename: str) -> VCS:
        with open(filename, "rb") as stream:
            return cls.from_stream(stream)

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> VCS:
        out = cls()
        version = read_struct(stream, "I")
        assert version == 6, f"{version=}"
        out.num_combos = read_struct(stream, "i")
        out.num_dynamic_combos = read_struct(stream, "i")
        out.flags = read_struct(stream, "I")
        out.centroid_mask = read_struct(stream, "I")
        out.num_static_combos = read_struct(stream, "I")
        out.crc = read_struct(stream, "I")
        # reversed from: "fxc/tonemap_overlay_ps40.vcs" (12KB)
        # NOTE: number of unknowns probably varies from file to file
        unknown_1 = read_struct(stream, "I")  # 0x00
        assert unknown_1 == 0x00, f"{unknown_1=}"
        some_offset = read_struct(stream, "I")
        assert some_offset >= 0x30, f"{some_offset=}"
        if some_offset > 0x30:
            extras = some_offset - 0x30
            assert extras % 4 == 0
            out.unknown_2 = read_struct(stream, f"{extras // 4}I")
        print(f"0x{stream.tell():02X}")
        assert read_struct(stream, "i") == -1  # section terminator?
        out.filesize = read_struct(stream, "I")
        out.unknown_3 = read_struct(stream, "I")  # 0x00
        assert out.unknown_3 == 0x00, f"{out.unknown_3=}"
        out.unknown_4 = read_struct(stream, "I")  # 0x8C280080
        assert (out.unknown_4 & 0x80000000) != 0, f"{out.unknown_4=}"
        # attempt to parse shaders
        # {print(f"{k:<24} | {v}") for k, v in out.__dict__.items()}
        combos = f"{out.num_combos=}, {out.num_dynamic_combos=}"
        assert out.num_dynamic_combos == out.num_combos, combos
        assert out.flags == 0, f"{out.flags=}"
        assert out.centroid_mask == 0, f"{out.centroid_mask=}"
        for i in range(out.num_combos):
            shader_id, shader_length = read_struct(stream, "2I")
            assert shader_id == i, f"{shader_id=}, {i=}"
            raw_shader = stream.read(shader_length)
            assert len(raw_shader) == shader_length, "unexpected EOF"
            shader = dxbc.DXBC.from_bytes(raw_shader)
            out.shaders[shader_id] = shader
        # end of file
        terminator = read_struct(stream, "i")
        assert terminator == -1, f"{terminator=}"
        assert stream.tell() == out.filesize
        return out
