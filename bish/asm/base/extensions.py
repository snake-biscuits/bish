# https://github.com/tpn/winsdk-10/blob/master/Include/10.0.10240.0/um/d3d11TokenizedProgramFormat.hpp#L520
from __future__ import annotations
import enum
import functools
from typing import Union

from . import tokens


def controls_for(type_: Type, controls: int):
    if type_ == Type.EMPTY:
        return None
    return {
        Type.SAMPLE: SampleControls,
        Type.DIMENSION: DimensionControls,
        Type.RETURN: ReturnControls}[type_].from_controls(controls)


class Type(enum.Enum):
    EMPTY = 0x00
    SAMPLE = 0x01  # texel offsets
    DIMENSION = 0x02  # resource dimension
    RETURN = 0x03  # return types


class Extension(tokens.Token):
    type: Type
    controls: Union[None, SampleControls, DimensionControls, ReturnControls]
    is_extended: bool

    def __init__(self, type_=Type.EMPTY, controls=None, is_extended=False):
        self.type = type_
        self.controls = controls
        self.is_extended = is_extended

    def __repr__(self) -> str:
        args = ", ".join([
            f"type={self.type.__class__.__name__}.{self.type.name}",
            f"controls={self.controls!r}",
            f"is_extended={self.is_extended}"])
        return f"{self.__class__.__name__}({args})"

    def as_token(self) -> int:
        return functools.reduce(
            lambda a, b: a | b, [
                self.type.value << 0,
                self.controls.as_int() << 6,
                int(self.is_extended) << 31])

    @classmethod
    def from_token(cls, token: int) -> Extension:
        out = cls()
        out.type = Type(token & 0x0000003F)  # [05:00]
        controls = (token & 0x7FFFFFC0) >> 6  # [30:06]
        out.controls = controls_for(out.type, controls)
        out.is_extended = (token & 0x80000000) >> 31  # [31]
        return out


class SampleControls:
    """immediate offsets for UVW texel axes"""
    u_offset: int
    v_offset: int
    w_offset: int

    def __init__(self, u_offset=0, v_offset=0, w_offset=0):
        self.u_offset = u_offset
        self.v_offset = v_offset
        self.w_offset = w_offset

    def __repr__(self) -> str:
        args = ", ".join([
            f"{attr}={getattr(self, attr)}"
            for attr in ("u_offset", "v_offset", "w_offset")])
        return f"{self.__class__.__name__}({args})"

    def as_int(self) -> int:
        raise NotImplementedError()

    @classmethod
    def from_controls(cls, controls: int) -> SampleControls:
        out = cls()
        controls = controls << 6  # [30:06]
        assert controls & 0x000000E0 == 0  # [08:06]
        # TODO: handle 2's complement
        out.u_offset = controls & 0x00000F00 >> 0x08  # [12:09]
        out.v_offset = controls & 0x0000F000 >> 0x0C  # [16:13]
        out.w_offset = controls & 0x000F0000 >> 0x10  # [20:17]
        assert controls & 0x3FF00000 == 0  # [30:21]
        return out


class ResourceDimension(enum.Enum):
    # d3d11TokenizedProgramFormat.hpp#L2088
    UNKNOWN = 0x00
    BUFFER = 0x01
    TEXTURE_1D = 0x02
    TEXTURE_2D = 0x03
    TEXTURE_2D_MS = 0x04
    TEXTURE_3D = 0x05
    TEXTURE_CUBE = 0x06
    TEXTURE_1D_ARRAY = 0x07
    TEXTURE_2D_ARRAY = 0x08
    TEXTURE_2D_MS_ARRAY = 0x09
    TEXTURE_CUBE_ARRAY = 0x0A
    RAW_BUFFER = 0x0B
    STRUCTURED_BUFFER = 0x0C


class DimensionControls:
    dimension: ResourceDimension
    stride: int  # for STRUCTURED_BUFFER

    def __init__(self, dimension=ResourceDimension.UNKNOWN, stride=0):
        self.dimension = dimension
        self.stride = 0

    def __repr__(self) -> str:
        args = ", ".join([
            f"dimension={self.dimension.__class__.__name__}.{self.dimension.name}",
            f"stride={self.stride}"])
        return f"{self.__class__.__name__}({args})"

    def as_int(self) -> int:
        ...

    @classmethod
    def from_controls(cls, controls: int) -> SampleControls:
        out = cls()
        controls = controls << 6  # [30:06]
        out.dimension = ResourceDimension(controls & 0x000007C0 >> 0x06)  # [10:06]
        out.stride = controls & 0x007FF800 >> 0x0A  # [22:11]
        # if out.dimension != ResourceDimension.STRUCTURED_BUFFER:
        #     assert out.stride == 0
        assert controls & 0x7F800000 == 0  # [30:23]
        return out


class ReturnType(enum.Enum):
    # d3d11TokenizedProgramFormat.hpp#L2105
    U_NORM = 0x01
    S_NORM = 0x02
    S_INT = 0x03
    U_INT = 0x04
    FLOAT = 0x05
    MIXED = 0x06
    DOUBLE = 0x07
    CONTINUED = 0x08
    UNUSED = 0x09


class ReturnControls:
    x: ReturnType
    y: ReturnType
    z: ReturnType
    w: ReturnType

    def __init__(self, x=ReturnType.UNUSED, y=ReturnType.UNUSED, z=ReturnType.UNUSED, w=ReturnType.UNUSED):
        self.x = x
        self.y = y
        self.z = z
        self.w = w

    def __repr__(self) -> str:
        args = f"x={self.x}, y={self.y}, z={self.z}, w={self.w}"
        return f"{self.__class__.__name__}({args})"

    def as_int(self) -> int:
        return functools.reduce(
            lambda a, b: a | b, [
                self.x.value << 0x00,
                self.y.value << 0x04,
                self.z.value << 0x08,
                self.w.value << 0x0C])

    @classmethod
    def from_controls(cls, controls: int) -> SampleControls:
        out = cls()
        out.x = ReturnType(controls & 0x000F >> 0x00)
        out.y = ReturnType(controls & 0x00F0 >> 0x04)
        out.z = ReturnType(controls & 0x0F00 >> 0x08)
        out.w = ReturnType(controls & 0xF000 >> 0x0C)
        assert controls >> 16 == 0
        return out
