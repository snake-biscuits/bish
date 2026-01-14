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
        token_length = len(instruction)
        length = token_length * 4
        # raw instruction bytes
        raw = fxc.RAW_SHEX[offset:offset+length]
        hex_ = raw.hex().upper()
        padding = (4 - token_length % 4) % 4  # in tokens
        hex_ = hex_ + " " * 8 * padding
        hex_ = " ".join(
            hex_[i:i + 8]
            for i in range(0, len(hex_), 8))
        # opcode
        opcode = instruction.opcode.name
        # TODO: operands & other tokens

        # TODO: split CUSTOM_DATA to better represent mat4x4
        # TODO: split lines contextually, for each instruction subsection
        if token_length <= 4:
            print(f"{i:4} | {offset:04X} | {hex_} | {opcode} ...")
        else:  # multi-line
            for j in range((token_length + 3) // 4):
                sub_hex_ = hex_[j*36:(j+1)*36-1]
                sub_offset = offset + j * 16
                i_s = f"{i:4}" if j == 0 else " " * 4
                tail = f"{opcode} ..." if j == 0 else ""
                print(f"{i_s} | {sub_offset:04X} | {sub_hex_} | {tail}")

        offset += length
