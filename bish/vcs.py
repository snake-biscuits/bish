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


ShaderKey = Tuple[int, int, int]
# ^ (combo_id, unknown, shader_id)


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
    shaders: List[Tuple[ShaderKey, dxbc.DXBC]]
    # ^ [(combo_id, unknown, shader_id), shader)]

    def __init__(self):
        self.num_combos = 0  # len(self.shaders)
        self.num_dynamic_combos = 0
        self.flags = 0x00000000
        self.centroid_mask = 0x00000000
        self.crc = 0x00000000
        self.static_combos = list()
        self.filesize = 0
        self.duplicates = list()
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
        # parse shaders
        gap = out.static_combos[0][1] - stream.tell()
        assert gap == 0, f"gap between header and shaders of {gap} bytes"
        next_address = [
            address
            for combo_id, address in out.static_combos[1:]]
        next_address.append(out.filesize)
        for i, (combo_id, address) in enumerate(out.static_combos):
            stream.seek(address)
            unknown = read_struct(stream, "I")  # flags?
            while stream.tell() < next_address[i]:
                # header
                shader_id = read_struct(stream, "I")
                if shader_id >= 128:
                    unknown = shader_id
                    continue  # new block
                shader_length = read_struct(stream, "I")
                assert 0 <= shader_id <= 127, "invalid shader_id"
                # shader
                raw_shader = stream.read(shader_length)
                assert len(raw_shader) == shader_length, "unexpected EOF"
                assert raw_shader[:4] == b"DXBC", f"bad magic: {raw_shader[:4]}"
                shader = dxbc.DXBC.from_bytes(raw_shader)
                oversize = shader_length - shader.filesize
                assert oversize == 0, f"{oversize=}"
                shader_key = (combo_id, unknown, shader_id)
                out.shaders.append((shader_key, shader))
            assert unknown == 0xFFFFFFFF, "block of shaders terminated wrong"
            overshot = stream.tell() - next_address[i]
            assert overshot == 0, f"past end of block by {overshot} bytes"
        assert stream.tell() == out.filesize
        return out
