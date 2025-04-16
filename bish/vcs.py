# https://developer.valvesoftware.com/wiki/VCS
# https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/public/materialsystem/shader_vcs_version.h
# https://github.com/EM4Volts/vcs_repack/blob/main/vcspy.py
from __future__ import annotations
import io
from typing import List, Tuple

from .utils.binary import read_struct
# from .utils.binary import xxd
from . import dxbc


# TODO: .vcssubfile (patches?)


class VCS:
    """Valve Compiled Shader (Titanfall 1 variant)"""
    num_combos: int
    num_dynamic_combos: int
    flags: int  # TODO: enum
    centroid_mask: int
    crc: int  # CRC32
    static_combos: List[Tuple[int, int]]
    # ^ [(combo_id, offset)]
    filesize: int
    duplicates: List[Tuple[int, int]]
    # ^ [(combo_id, source_id)]
    unknown: int  # looks like a bit mask?
    shaders: List[dxbc.DXBC]

    def __init__(self):
        self.num_combos = 0  # len(self.shaders)
        self.num_dynamic_combos = 0
        self.flags = 0x00000000
        self.centroid_mask = 0x00000000
        self.crc = 0x00000000
        self.static_combos = list()
        self.filesize = 0
        self.duplicates = list()
        self.unknown = 0
        self.shaders = list()

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
        num_static_combos = read_struct(stream, "I")
        assert num_static_combos >= 1, f"{num_static_combos=}"
        out.crc = read_struct(stream, "I")
        out.static_combos = [
            read_struct(stream, "iI")  # (static_combo_id, offset)
            for i in range(num_static_combos - 1)]
        # last static combo is always (-1, filesize)
        terminator, out.filesize = read_struct(stream, "iI")
        assert terminator == -1, f"{terminator=}"
        num_duplicates = read_struct(stream, "I")
        out.duplicates = [
            read_struct(stream, "2I")  # (combo_id, source_id)
            for i in range(num_duplicates)]
        out.unknown = read_struct(stream, "I")
        # print("=== meta ===")
        # print(f"filesize={out.filesize}")
        # print(f"unknown=0x{out.unknown:08X}")
        # print(f"num_combos={out.num_combos}")
        # print(f"num_dynamic_combos={out.num_dynamic_combos}")
        # print(f"{num_static_combos=}")
        # print(f"{num_duplicates=}")
        # print("=== static combos ===")
        # {
        #     print(f"{id_:02d} @ 0x{offset:08X}")
        #     for id_, offset in out.static_combos}
        # print("=== duplicates ===")
        # {
        #     print(f"{combo_id=}, {source_id=}")
        #     for combo_id, source_id in out.duplicates}
        # print("=== shaders ===")
        # parse shaders
        # NOTE: have yet to find the true shader count
        i = 0
        while i < (num_static_combos - 1):
            shader_id, shader_length = read_struct(stream, "iI")
            if shader_id == -1:  # skip
                # NOTE: not recording shader_length
                # -- could be important metadata
                # print(f"skipping shader {i} (0x{shader_length:08X})")
                # xxd(stream, limit=0x20, row=0x10, start=stream.tell())
                # stream.seek(-0x20, 1)
                continue
            # print(f"{shader_id=}, {shader_length=}")
            raw_shader = stream.read(shader_length)
            assert len(raw_shader) == shader_length, "unexpected EOF"
            assert raw_shader[:4] == b"DXBC", f"bad magic: {raw_shader[:4]}"
            shader = dxbc.DXBC.from_bytes(raw_shader)
            oversize = shader_length - shader.filesize
            assert oversize == 0, f"{oversize=}"
            out.shaders.append(shader)
            i += 1
        # end of file
        tail_length = out.filesize - stream.tell()
        if tail_length > 4:
            # xxd(stream, row=0x10, start=stream.tell())
            raise RuntimeError(f"tail of {tail_length} bytes")
        else:
            terminator = read_struct(stream, "i")
            assert terminator == -1, f"{terminator=}"
        return out
