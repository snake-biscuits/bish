# https://github.com/r-ex/rsx/blob/main/src/core/shaderexp/multishader.h
import enum

import breki


class MswType(enum.Enum):
    SHADER = 0x00
    SHADER_SET = 0x01


class MswShaderType(enum.Enum):  # for SHADER
    PIXEL = 0x00
    VERTEX = 0x01
    GEOMETRY = 0x02
    HULL = 0x03
    DOMAIN = 0x04
    COMPUTE = 0x05
    # INVALID = 0xFF


# NOTE: kinda useless unless we exported shaders as MSW w/ GUID filenames
class MswShaderSetData(breki.Struct):  # for SHADER_SET
    pixel_shader_offset: int  # if non-zero, offset to embedded pixel shader
    vertex_shader_offset: int  # if non-zero, offset to embedded vertex shader
    __slots__ = [
        "pixel_shader_guid", "vertex_shader_guid",
        "num_pixel_shader_textures", "num_vertex_shader_textures",
        "num_samplers", "first_resource_bind_point", "num_resources",
        "pixel_shader_offset", "vertex_shader_offset"]
    _format = "2Q3H2B2I"


class Msw(breki.BinaryFile):
    """reSource MultiShaderWrapper"""
    exts = ["*.msw"]

    def parse(self):
        if self.is_parsed:
            return
        self.is_parsed = True
        magic, version, msw_type = breki.read_struct(self.stream, "3s2B")
        assert magic == b"MSW"
        assert version == 3
        self.msw_type = MswType(msw_type)
        if self.msw_type != MswType.SHADER_SET:
            # SHADER is more a little bit more complicated
            raise NotImplementedError()
        self.data = MswShaderSetData.from_stream(self.stream)
        # TODO: embedded shaders, if present
