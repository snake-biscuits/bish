__all__ = [
    "base",
    "Instruction", "Opcode", "opcode_for"]


from . import base

from .base.instructions import FullInstruction as Instruction
from .base.opcodes import Opcode, opcode_for
