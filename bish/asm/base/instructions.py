# https://github.com/tpn/winsdk-10/blob/master/Include/10.0.10240.0/um/d3d11TokenizedProgramFormat.hpp
from __future__ import annotations
import functools
import io
from typing import List, Union

from breki.binary import read_struct

from . import custom_data
from . import extensions
from . import opcodes
from . import operands
from . import tokens


class FullInstruction:
    opcode: opcodes.Opcode
    instruction: Instruction
    custom_data: Union[custom_data.CustomDataBlock, None]
    # ^ only used if opcode is D3D_10_0.CUSTOM_DATA
    extensions: List[extensions.Extension]
    operands: List[int]

    def __init__(self):
        instruction = Instruction()
        self.opcode = instruction.opcode
        self.instruction = instruction
        self.custom_data = None
        self.extensions = list()
        self.operands = list()

    def __repr__(self) -> str:
        details = [f"(0x{self.opcode.value:02X}) {self.opcode.name}"]
        if self.instruction.is_extended:
            details.append(f"{len(self.extensions)} extensions")
        if self.opcode != opcodes.D3D_10_0.CUSTOM_DATA:
            descriptor = f"{len(self.operands)} operands"
        else:  # mimic CustomDataBlock repr
            details.append(f"{len(self.custom_data.tokens) - 2} tokens")
        descriptor = " ".join(details)
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def __len__(self) -> int:
        if self.custom_data is None:
            return self.instruction.length
        else:
            return len(self.custom_data)

    # TODO: as_bytes(self) -> bytes:

    def as_tokens(self) -> List[int]:
        return [
            self.instruction.as_int(),
            *[
                extension.as_int()
                for extension in self.extensions],
            # *[
            #     operand.as_tokens()
            #     for operand in self.operands]]
            *self.operands]

    @classmethod
    def from_bytes(cls, raw_tokens: bytes) -> FullInstruction:
        out = cls.from_stream(io.BytesIO(raw_tokens))
        assert len(raw_tokens) == out.length
        return out

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> FullInstruction:
        out = cls()
        # instruction
        token = read_struct(stream, "I")
        out.instruction = Instruction.from_token(token)
        out.opcode = out.instruction.opcode
        if out.opcode == opcodes.D3D_10_0.CUSTOM_DATA:
            assert not out.instruction.is_extended
            stream.seek(-4, 1)  # go back 1 token
            out.custom_data = custom_data.CustomDataBlock.from_stream(stream)
            # TODO: confirm CustomDataBlock consumes full length
            return out
        # extensions
        prev_token = out.instruction
        while prev_token.is_extended:
            prev_token = extensions.Extension.from_stream(stream)
            out.extensions.append(prev_token)
        # operands
        num_operand_tokens = out.instruction.length - len(out.extensions) - 1
        operand_tokens = [
            read_struct(stream, "I")
            for i in range(num_operand_tokens)]
        # NOTE: DCL_* operands use a different format
        try:
            offset = 0
            while offset < num_operand_tokens:
                operand = operands.FullOperand.from_tokens(operand_tokens[offset:])
                offset += len(operand)
                out.operands.append(operand)
        except Exception:
            # NOTE: silencing errors like this is bad practice
            out.operands = operand_tokens
        return out


class Instruction(tokens.Token):
    opcode: opcodes.Opcode
    controls: int
    length: int  # in DWORDS / tokens / uint32s
    is_extended: bool

    def __init__(self, opcode=opcodes.D3D_10_0.NOP, controls=0, length=1, is_extended=False):
        self.opcode = opcode
        self.controls = controls
        self.length = length
        self.is_extended = is_extended

    def __repr__(self) -> str:
        args = ", ".join([
            f"{self.opcode.__class__.__name__}.{self.opcode.name}",
            f"controls={self.controls}",
            f"length={self.length}",
            f"is_extended={self.is_extended}"])
        return f"{self.__class__.__name__}({args})"

    def as_int(self) -> int:
        assert 0 <= self.controls <= 0x1FFF
        assert 0 <= self.length <= 0x7F
        return functools.reduce(
            lambda a, b: a | b, [
                self.opcode.value << 0,
                self.controls << 11,
                self.length << 24,
                int(self.is_extended) << 31])

    @classmethod
    def from_token(cls, token: int) -> Instruction:
        out = cls()
        out.opcode = opcodes.opcode_for(token & 0x000003FF)  # [10:00]
        out.controls = (token & 0x00FFF800) >> 11  # [32:11]
        out.length = (token & 0x7F000000) >> 24  # [30:24]
        out.is_extended = bool((token & 0x80000000) >> 31)  # [31]
        # NOTE: you should use custom_data.CustomDataBlock for CUSTOM_DATA
        # -- but you have to parse the opcode first to know it's custom data
        if out.opcode != opcodes.D3D_10_0.CUSTOM_DATA:
            opcode_str = f"{out.opcode.name} (0x{out.opcode.value:02X})"
            assert out.length >= 1, f"{opcode_str} has invalid instruction length"
        return out
