__all__ = [
    "base",
    "Instruction", "Opcode", "Operand", "OperandType"]


from . import base
# TODO: instruction subclasses spread over multiple files

from .base import Instruction, Opcode, Operand, OperandType
