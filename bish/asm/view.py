import struct
from typing import List

# from bish.asm.base import custom_data
from bish.asm.base import opcodes


# TODO: colour (highlighting)
# -- opcode byte
# -- instruction segments
def r2(fxc, limit=None, start=0):
    """radare 2 inspired assembly bytecode viewer"""
    assert "SHEX" in fxc.chunks
    # 0000 | version & shader type token
    # 0004 | chunk size
    offset = 8  # first instruction
    offset += sum(
        len(instruction) * 4
        for instruction in fxc.SHEX.instructions[:start])
    limit = start + limit if limit is not None else None
    for i, instruction in enumerate(fxc.SHEX.instructions[start:limit]):
        i = start + i
        num_tokens = len(instruction)
        bytes_length = num_tokens * 4

        raw_tokens = fxc.RAW_SHEX[offset:offset + bytes_length]
        tokens = struct.unpack(f"{num_tokens}I", raw_tokens)
        opcode = instruction.opcode.name
        # TODO: group tokens by instruction data instead

        # TODO: better extension & operand reprs
        token_groups = list()
        if not opcode.startswith("DCL_"):
            token_offset = 1
            for extension in instruction.extensions:
                sub_tokens = tokens[token_offset:token_offset+1]
                tail = f"  {extension.type.name} ..."
                token_groups.append((sub_tokens, tail))
                token_offset += 1
            if not all(isinstance(o, int) for o in instruction.operands):
                for operand in instruction.operands:
                    sub_tokens = tokens[token_offset:token_offset+len(operand)]
                    tail = f"  {operand}"
                    token_groups.append((sub_tokens, tail))
                    token_offset += len(operand)
            if len(tokens) > token_offset:
                token_groups.append((tokens[token_offset:], ""))

        if instruction.opcode == opcodes.D3D_10_0.CUSTOM_DATA:
            print_tokens(offset, tokens[:2], f"{i:4}", opcode)
            print_tokens(offset + 8, tokens[2:])
        # TODO: lines for extensions & opcodes
        elif len(token_groups) > 0:
            print_tokens(offset, tokens[:1], f"{i:4}", opcode)
            sub_offset = offset + 4
            for group, tail in token_groups:
                print_tokens(sub_offset, group, tail=tail)
                sub_offset += len(group) * 4
        else:  # basic print
            print_tokens(offset, tokens, f"{i:4}", opcode)

        offset += bytes_length


def line_for(offset: int, tokens: List[int], head=" "*4, tail="") -> str:
    tokens = [f"{token:08X}" for token in tokens]
    if len(tokens) < 5:
        tokens.extend([" " * 8] * (5 - len(tokens)))
    assert len(tokens) == 5
    hex_ = " ".join(tokens)
    return f"{head} | {offset:04X} | {hex_} | {tail}"


def print_tokens(offset: int, tokens: List[int], head=" "*4, tail=""):
    for i in range(0, len(tokens), 5):
        sub_tokens = tokens[i:i + 5]
        print(line_for(offset, sub_tokens, head, tail))
        offset += 16
        # clear head & tail after first line
        head = " " * 4
        tail = ""
