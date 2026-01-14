# https://developer.valvesoftware.com/wiki/VCS
# https://github.com/ValveSoftware/source-sdk-2013/blob/master/src/public/materialsystem/shader_vcs_version.h
# https://github.com/EM4Volts/vcs_repack/blob/main/vcspy.py
from __future__ import annotations
from typing import Dict, List, Tuple

import breki
from breki.files.parsed import parse_first
from breki.binary import read_struct


# TODO: .vcssubfile (patches?)


class VcsHeader(breki.Struct):
    version: int  # always 6
    __slots__ = [
        "version", "num_combos", "num_dynamic_combos",
        "flags", "centroid_mask", "num_static_combos",
        "crc"]
    _format = "I2i4I"


class Vcs(breki.BinaryFile, breki.archives.base.Archive):
    """Valve Compiled Shader (Titanfall 1 variant)"""
    exts = ["*.vcs"]
    header: VcsHeader
    static_combos: List[Tuple[int, int]]
    # ^ [(combo_id, offset)]
    duplicates: List[Tuple[int, int]]
    # ^ [(combo_id, source_id)]
    entries: Dict[str, Tuple[int, int]]
    # ^ {"combo_id.unknown.shader_id": (offset, length)}

    def __init__(self, filepath: str, archive=None, code_page=None):
        super().__init__(filepath, archive, code_page)
        self.header = VcsHeader()
        self.static_combos = list()
        self.duplicates = list()
        self.entries = dict()

    @parse_first
    def namelist(self) -> List[str]:
        return sorted(self.entries.keys())

    @parse_first
    def read(self, filepath: str) -> bytes:
        assert filepath in self.entries
        offset, length = self.entries[filepath]
        self.stream.seek(offset)
        return self.stream.read(length)

    def parse(self):
        if self.is_parsed:
            return
        self.is_parsed = True
        self.header = VcsHeader.from_stream(self.stream)
        assert self.header.version == 6
        assert self.header.num_static_combos >= 1
        self.static_combos = [
            read_struct(self.stream, "iI")  # (static_combo_id, offset)
            for i in range(self.header.num_static_combos)]
        assert self.static_combos[-1] == (-1, self.size)
        self.static_combos.pop(-1)
        num_duplicates = read_struct(self.stream, "I")
        self.duplicates = [
            read_struct(self.stream, "2I")  # (combo_id, source_id)
            for i in range(num_duplicates)]
        # assert we got everything before headers
        gap = self.static_combos[0][1] - self.stream.tell()
        assert gap == 0, f"gap between header and shaders of {gap} bytes"
        # build entries table
        next_address = [
            address
            for combo_id, address in self.static_combos[1:]]
        next_address.append(self.size)
        for i, (combo_id, address) in enumerate(self.static_combos):
            self.stream.seek(address)
            unknown = read_struct(self.stream, "I")  # flags?
            while self.stream.tell() < next_address[i]:
                # header
                shader_id = read_struct(self.stream, "I")
                if shader_id >= 128:
                    unknown = shader_id
                    continue  # new block
                assert 0 <= shader_id <= 127, "invalid shader_id"
                filename = f"{combo_id:08X}/{unknown:08X}.{shader_id:08X}.fxc"
                length = read_struct(self.stream, "I")
                offset = self.stream.tell()
                assert offset + length < self.size, "hit EOF early"
                assert filename not in self.entries, f"duplicate: {filename}"
                self.entries[filename] = (offset, length)
                self.stream.seek(length, 1)
                # NOTE: no longer verifying length
                # -- could confirm shader is DXBC & get internal filesize
            assert unknown == 0xFFFFFFFF, "shader block terminator missing"
            overshot = self.stream.tell() - next_address[i]
            assert overshot == 0, f"past end of block by {overshot} bytes"
        assert self.stream.tell() == self.size
