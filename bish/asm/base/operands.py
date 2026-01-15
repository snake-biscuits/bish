# https://github.com/tpn/winsdk-10/blob/master/Include/10.0.10240.0/um/d3d11TokenizedProgramFormat.hpp#L690
from __future__ import annotations
import enum
import io
from typing import List, Tuple, Union

from breki.binary import read_struct

from . import tokens
# from . import opcodes


# NOTE: we aren't going to validate operand types against opcodes
# -- would be pretty convoluted and isn't really helpful
# -- since we're just looking at compiled shaders which we know are valid


class FullOperand:
    type: Type
    selection_mode: Union[SelectionMode, None]
    mask: Union[Mask, None]
    swizzle: Union[List[Name], None]
    name: Union[Name, None]
    index_representations: List[IndexRepresentation]
    indices: List[Tuple[Union[int, None], Union[FullOperand, None]]]
    # ^ [(imm, rel)]

    def __init__(self):
        self.selection_mode = None
        self.mask = None
        self.swizzle = None
        self.name = None
        self.index_representations = list()
        self.indices = list()

    def __repr__(self) -> str:
        descriptor = f"{self.swizzle_str()} {len(self.indices)} indices"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def __str__(self) -> str:
        out = f"{register_name(self.type, self.indices)}"
        swizzle_str = self.swizzle_str()
        if swizzle_str is not None:
            out += swizzle_str.lower()
        return out

    def __len__(self) -> int:
        num_index_tokens = 0
        for i, index_repr in enumerate(self.index_representations):
            if index_repr.name.startswith("IMM32"):
                num_index_tokens += 1
            elif index_repr.name.startswith("IMM64"):
                num_index_tokens += 2
            if index_repr.name.endswith("REL"):
                num_index_tokens += len(self.indices[i][1])
        return 1 + num_index_tokens

    def swizzle_str(self) -> str:
        if self.selection_mode is None:
            return
        elif self.selection_mode == SelectionMode.MASK:
            swizzle = "".join([x.name for x in self.mask])
        elif self.selection_mode == SelectionMode.SWIZZLE:
            swizzle = "".join([x.name for x in self.swizzle])
        elif self.selection_mode == SelectionMode.SELECT_1:
            swizzle = self.name.name
        else:
            raise RuntimeError("Invalid Selection Mode")
        return f".{swizzle}"

    @classmethod
    def from_bytes(cls, raw_tokens: bytes) -> FullOperand:
        return cls.from_stream(io.BytesIO(raw_tokens))

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> FullOperand:
        out = cls()
        operand = Operand.from_stream(stream)
        out.type = operand.type
        out.selection_mode = operand.selection_mode
        out.mask = operand.mask
        out.swizzle = operand.swizzle
        out.name = operand.name
        out.index_representations = operand.index_representations
        assert not operand.is_extended, "Extended Operand Not Yet Implemented"
        for index_repr in out.index_representations:
            imm, rel = None, None
            if index_repr.name.startswith("IMM32"):
                imm = read_struct(stream, "I")
            elif index_repr.name.startswith("IMM64"):
                hi32, lo32 = read_struct(stream, "2I")
                imm = (hi32 << 32) | lo32
            if index_repr.name.endswith("REL"):
                rel = FullOperand.from_stream(stream)
                assert all("REL" not in ir.name for ir in rel.index_representations)
            out.indices.append((imm, rel))
        return out

    @classmethod
    def from_tokens(cls, tokens: List[int]) -> FullOperand:
        return cls.from_bytes(b"".join([
            token.to_bytes(4, "little")
            for token in tokens]))


class Operand(tokens.Token):
    type: Type
    selection_mode: Union[SelectionMode, None]
    mask: Union[Mask, None]
    swizzle: Union[List[Name], None]
    name: Union[Name, None]
    index_representations: List[IndexRepresentation]
    is_extended: bool

    def __init__(self):
        self.selection_mode = None
        self.mask = None
        self.swizzle = None
        self.name = None
        self.index_representations = list()

    def __repr__(self) -> str:
        descriptor = self.swizzle_str()
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def swizzle_str(self) -> str:
        if self.selection_mode is None:
            return
        elif self.selection_mode == SelectionMode.MASK:
            swizzle = "".join([x.name for x in self.mask])
        elif self.selection_mode == SelectionMode.SWIZZLE:
            swizzle = "".join([x.name for x in self.swizzle])
        elif self.selection_mode == SelectionMode.SELECT_1:
            swizzle = self.name.name
        else:
            raise RuntimeError("Invalid Selection Mode")
        return f".{swizzle}"

    @classmethod
    def from_token(cls, token: int) -> Operand:
        out = cls()
        out.type = Type((token & 0x000FF000) >> 12)  # [19:12]
        num_components = NumComponents((token & 0x00000003) >> 0)  # [01:00]
        if num_components == NumComponents.FOUR:
            out.selection_mode = SelectionMode((token & 0x0000000C) >> 2)  # [03:02]
            if out.selection_mode == SelectionMode.MASK:
                out.mask = Mask((token & 0x000000F0) >> 4)  # [07:04]
            elif out.selection_mode == SelectionMode.SWIZZLE:
                out.swizzle = [  # [11:04]
                    Name((token & 0x00000030) >> 0x04),
                    Name((token & 0x000000C0) >> 0x06),
                    Name((token & 0x00000300) >> 0x08),
                    Name((token & 0x00000C00) >> 0x0C)]
            elif out.selection_mode == SelectionMode.SELECT_1:
                out.name = Name((token & 0x00000300) >> 4)  # [05:04]
        index_dimension = (token & 0x00300000) >> 20  # [21:20]
        for i in range(index_dimension):
            shift = 22 + 3 * i
            mask = 0x03 << shift
            index_repr = IndexRepresentation((token & mask) >> shift)
            out.index_representations.append(index_repr)
        out.is_extended = bool(token >> 31)  # [31]
        # cleanup assertions
        # NOTE: breaking for DCL_TEMPS
        if num_components in (NumComponents.ZERO, NumComponents.ONE):
            assert (token & 0x00000FFC) >> 2 == 0
        assert num_components != NumComponents.N
        # TODO: assert IndexRepresentations for unused dimensions are 0
        return out


class Type(enum.Enum):
    """D3D10_SB_OPERAND_TYPE"""
    # DirectX 10.0
    # register files
    TEMP = 0x00
    INPUT = 0x01
    OUTPUT = 0x02
    INDEXABLE_TEMP = 0x03
    # immediates
    IMMEDIATE_32 = 0x04
    IMMEDIATE_64 = 0x05
    # references
    SAMPLER = 0x06
    RESOURCE = 0x07  # memory resource (e.g. texture)
    CONSTANT_BUFFER = 0x08
    IMMEDIATE_CONSTANT_BUFFER = 0x09
    # misc.
    LABEL = 0x0A  # for branching
    INPUT_PRIMITIVE_ID = 0x0B
    OUTPUT_DEPTH = 0x0C
    NULL = 0x0D  # discard results
    # DirectX 10.1
    RASTERIZER = 0x0E  # depth / stencil / render_target
    OUTPUT_COVERAGE_MASK = 0x0F  # PS out MSAA coverage mask (scalar)
    # DirectX 11
    STREAM = 0x10  # GS out
    FUNCTION_BODY = 0x11
    FUNCTION_TABLE = 0x12  # class methods
    INTERFACE = 0x13
    FUNCTION_INPUT = 0x14
    FUNCTION_OUPUT = 0x15
    # HS & DS phase inputs & outputs
    OUTPUT_CONTROL_POINT_ID = 0x16
    INPUT_FORK_INSTANCE_ID = 0x17
    INPUT_JOIN_INSTANCE_ID = 0x18
    INPUT_CONTROL_POINT = 0x19
    OUTPUT_CONTROL_POINT = 0x1A
    INPUT_PATCH_CONSTANT = 0x1B
    INPUT_DOMAIN_POINT = 0x1C
    # misc.
    THIS_POINTER = 0x1D
    UNORDERED_ACCESS_VIEW = 0x1E
    THREAD_GROUP_SHARED_MEMORY = 0x1F
    INPUT_THREAD_ID = 0x20
    INPUT_THREAD_GROUP_ID = 0x21
    INPUT_THREAD_ID_IN_GROUP = 0x22
    INPUT_COVERAGE_MASK = 0x23
    INPUT_THREAD_ID_IN_GROUP_FLATTENED = 0x24
    INPUT_GS_INSTANCE_ID = 0x25
    OUTPUT_DEPTH_GREATER_EQUAL = 0x26
    OUTPUT_DEPTH_LESS_EQUAL = 0x27
    CYCLE_COUNTER = 0x28


def register_name(type_: Type, indices) -> str:
    chars = {
        Type.CONSTANT_BUFFER: "cb",
        Type.INPUT: "v",  # vertex attribute (in a pixel shader)
        Type.RESOURCE: "t",  # texture (in a SAMPLE call)
        Type.SAMPLER: "s",  # texture sampler register
        Type.TEMP: "r",  # temp register
    }
    if len(indices) == 1:
        index = indices[0][0]  # IMM, not REL
        return f"{chars.get(type_, type_.name + ' ')}{index}"
    elif len(indices) == 2 and type_ == Type.CONSTANT_BUFFER:
        # assuming DCL_CONSTANT_BUFFER w/ immediateIndexed AccessPattern
        return f"cb{indices[0][0]}[{indices[1][0]}]"
    # TODO: IMMEDIATE_32 w/ no indices
    else:
        print(f"{type_.name}: {indices=}")
        raise RuntimeError()


class IndexRepresentation(enum.Enum):
    IMM32 = 0x00  # +1 token
    IMM64 = 0x01  # +2 tokens
    REL = 0x02  # +1 operand
    IMM32_PLUS_REL = 0x03  # +1 token, +1 operand
    IMM64_PLUS_REL = 0x04  # +2 tokens, +1 operand


class Mask(enum.IntFlag):
    X = 0x01  # R
    Y = 0x02  # G
    Z = 0x04  # B
    W = 0x08  # A


class Name(enum.Enum):
    X = 0x00  # R
    Y = 0x01  # G
    Z = 0x02  # B
    W = 0x03  # A


class NumComponents(enum.Enum):
    ZERO = 0
    ONE = 1
    FOUR = 2
    N = 3  # undefined & unused


class SelectionMode(enum.Enum):
    MASK = 0
    SWIZZLE = 1
    SELECT_1 = 2
