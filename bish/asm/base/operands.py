# https://github.com/tpn/winsdk-10/blob/master/Include/10.0.10240.0/um/d3d11TokenizedProgramFormat.hpp#L690
from __future__ import annotations

from . import tokens
from . import opcodes


def operand_for(opcode: opcodes.Opcode):
    if not opcode.name.startswith("DCL"):
        return Operand
    # TODO: table for all ~40 DCL_* opcodes
    # -- in d3d11TokenizedProgramFormat.hpp
    # -- L2143: DCL_FUNCTION_BODY
    # -- L2161: DCL_FUNCTION_TABLE
    # -- L2182: DCL_INTERFACE
    # TODO: move to `declarations` module?
    else:
        return Operand_DCL


class Operand(tokens.Token):
    ...

    @classmethod
    def from_token(cls, token: int) -> Operand:
        raise NotImplementedError()
        # [01:00] num_components {0:0, 1:1, 2:4, 3:n}  # N is "unused for now"
        # [11:02] component selection


class Operand_DCL(Operand):
    # DCL_* operand tokens have multiple formats
    ...

    @classmethod
    def from_token(cls, token: int) -> Operand_DCL:
        raise NotImplementedError()
