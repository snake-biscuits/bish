# https://github.com/tpn/winsdk-10/blob/master/Include/10.0.10240.0/um/d3d11TokenizedProgramFormat.hpp
__all__ = [
    "D3D_10_0", "D3D_10_1", "D3D_11_0", "D3D_11_1", "WDDM_1_3",
    "Opcode", "opcode_for"]

import enum
from typing import Union


def opcode_for(value: int):
    all_opcodes = {
        opcode.value: opcode
        for opcode in [
            *D3D_10_0, *D3D_10_1,
            *D3D_11_0, *D3D_11_1,
            *WDDM_1_3]}
    if value in all_opcodes:
        return all_opcodes[value]
    else:
        raise RuntimeError(f"Invalid Opcode Value: 0x{value:02X}")


class D3D_10_0(enum.Enum):
    """D3D 10.0 Opcodes"""
    ADD = 0x00
    AND = 0x01
    BREAK = 0x02
    BREAK_C = 0x03
    CALL = 0x04
    CALL_C = 0x05
    CASE = 0x06
    CONTINUE = 0x07
    CONTINUE_C = 0x08
    CUT = 0x09
    DEFAULT = 0x0A
    DERIV_RTX = 0x0B
    DERIV_RTY = 0x0C
    DISCARD = 0x0D
    DIV = 0x0E
    DP_2 = 0x0F
    DP_3 = 0x10
    DP_4 = 0x11
    ELSE = 0x12
    EMIT = 0x13
    EMIT_THEN_CUT = 0x14
    END_IF = 0x15
    END_LOOP = 0x16
    END_SWITCH = 0x17
    EQ = 0x18
    EXP = 0x19
    FRC = 0x1A
    F_TO_I = 0x1B
    F_TO_U = 0x1C
    GE = 0x1D
    IADD = 0x1E
    IF = 0x1F
    IEQ = 0x20
    IGE = 0x21
    ILT = 0x22
    IMAD = 0x23
    IMAX = 0x24
    IMIN = 0x25
    IMUL = 0x26
    INE = 0x27
    INEG = 0x28
    ISHL = 0x29
    ISHR = 0x2A
    I_TO_F = 0x2B
    LABEL = 0x2C
    LD = 0x2D
    LD_MS = 0x2E
    LOG = 0x2F
    LOOP = 0x30
    LT = 0x31
    MAD = 0x32
    MIN = 0x33
    MAX = 0x34
    CUSTOM_DATA = 0x35  # custom_data.CustomDataBlock
    MOV = 0x36
    MOV_C = 0x37
    MUL = 0x38
    NE = 0x39
    NOP = 0x3A
    NOT = 0x3B
    OR = 0x3C
    RES_INFO = 0x3D
    RET = 0x3E
    RET_C = 0x3F
    ROUND_NE = 0x40
    ROUND_NI = 0x41
    ROUND_PI = 0x42
    ROUND_Z = 0x43
    RSQ = 0x44
    SAMPLE = 0x45
    SAMPLE_C = 0x46
    SAMPLE_C_LZ = 0x47
    SAMPLE_L = 0x48
    SAMPLE_D = 0x49
    SAMPLE_B = 0x4A
    SQRT = 0x4B
    SWITCH = 0x4C
    SIN_COS = 0x4D
    UDIV = 0x4E
    ULT = 0x4F
    UGE = 0x50
    UMUL = 0x51
    UMAD = 0x52
    UMAX = 0x53
    UMIN = 0x54
    USHR = 0x55  # Unsigned Shift Right?
    U_TO_F = 0x56
    XOR = 0x57
    DCL_RESOURCE = 0x58
    DCL_CONSTANT_BUFFER = 0x59
    DCL_SAMPLER = 0x5A
    DCL_INDEX_RANGE = 0x5B
    DCL_GS_OUTPUT_PRIMITIVE_TOPOLOGY = 0x5C
    DCL_GS_INPUT_PRIMITIVE = 0x5D
    DCL_MAX_OUTPUT_VERTEX_COUNT = 0x5E
    DCL_INPUT = 0x5F
    DCL_INPUT_SGV = 0x60
    DCL_INPUT_SIV = 0x61
    DCL_INPUT_PS = 0x62
    DCL_INPUT_PS_SGV = 0x63
    DCL_INPUT_PS_SIV = 0x64
    DCL_OUTPUT = 0x65
    DCL_OUTPUT_SGV = 0x66
    DCL_OUTPUT_SIV = 0x67
    DCL_TEMPS = 0x68
    DCL_INDEXABLE_TEMP = 0x69
    DCL_GLOBAL_FLAGS = 0x6A
    RESERVED = 0x6B


class D3D_10_1(enum.Enum):
    """D3D 10.1 Opcodes"""
    LOD = 0x6C
    GATHER_4 = 0x6D
    SAMPLE_POS = 0x6E
    SAMPLE_INFO = 0x6F
    RESERVED = 0x70


class D3D_11_0(enum.Enum):
    """D3D 11.0 Opcodes"""
    HS_DECLS = 0x71
    HS_CONTROL_POINT_PHASE = 0x72
    HS_FORK_PHASE = 0x73
    HS_JOIN_PHASE = 0x74
    EMIT_STREAM = 0x75
    CUT_STREAM = 0x76
    EMIT_THEN_CUT_STREAM = 0x77
    INTERFACE_CALL = 0x78
    BUF_INFO = 0x79
    DERIV_RTX_COARSE = 0x7A
    DERIV_RTX_FINE = 0x7B
    DERIV_RTY_COARSE = 0x7C
    DERIV_RTY_FINE = 0x7D
    GATHER_4_C = 0x7E
    GATHER_4_PO = 0x7F
    GATHER_4_PO_C = 0x80
    RCP = 0x81
    F32_TO_F16 = 0x82
    F16_TO_F32 = 0x83
    UADDC = 0x84
    USUBB = 0x85
    COUNTBITS = 0x86
    FIRSTBIT_HI = 0x87
    FIRSTBIT_LO = 0x88
    FIRSTBIT_SHI = 0x89
    UBFE = 0x8A
    IBFE = 0x8B
    BFI = 0x8C
    BFREV = 0x8D
    SWAPC = 0x8E
    DCL_STREAM = 0x8F
    DCL_FUNCTION_BODY = 0x90
    DCL_FUNCTION_TABLE = 0x91
    DCL_INTERFACE = 0x92
    DCL_INPUT_CONTROL_POINT_COUNT = 0x93
    DCL_OUTPUT_CONTROL_POINT_COUNT = 0x94
    DCL_TESS_DOMAIN = 0x95
    DCL_TESS_PARTITIONING = 0x96
    DCL_TESS_OUTPUT_PRIMITIVE = 0x97
    DCL_HS_MAX_TESSFACTOR = 0x98
    DCL_HS_FORK_PHASE_INSTANCE_COUNT = 0x99
    DCL_HS_JOIN_PHASE_INSTANCE_COUNT = 0x9A
    DCL_THREAD_GROUP = 0x9B
    DCL_UNORDERED_ACCESS_VIEW_TYPED = 0x9C
    DCL_UNORDERED_ACCESS_VIEW_RAW = 0x9D
    DCL_UNORDERED_ACCESS_VIEW_STRUCTURED = 0x9E
    DCL_THREAD_GROUP_SHARED_MEMORY_RAW = 0x9F
    DCL_THREAD_GROUP_SHARED_MEMORY_STRUCTURED = 0xA0
    DCL_RESOURCE_RAW = 0xA1
    DCL_RESOURCE_STRUCTURED = 0xA2
    LD_UAV_TYPED = 0xA3
    STORE_UAV_TYPED = 0xA4
    LD_RAW = 0xA5
    STORE_RAW = 0xA6
    LD_STRUCTURED = 0xA7
    STORE_STRUCTURED = 0xA8
    ATOMIC_AND = 0xA9
    ATOMIC_OR = 0xAA
    ATOMIC_XOR = 0xAB
    ATOMIC_CMP_STORE = 0xAC
    ATOMIC_IADD = 0xAD
    ATOMIC_IMAX = 0xAE
    ATOMIC_IMIN = 0xAF
    ATOMIC_UMAX = 0xB0
    ATOMIC_UMIN = 0xB1
    IMM_ATOMIC_ALLOC = 0xB2
    IMM_ATOMIC_CONSUME = 0xB3
    IMM_ATOMIC_IADD = 0xB4
    IMM_ATOMIC_AND = 0xB5
    IMM_ATOMIC_OR = 0xB6
    IMM_ATOMIC_XOR = 0xB7
    IMM_ATOMIC_EXCH = 0xB8
    IMM_ATOMIC_CMP_EXCH = 0xB9
    IMM_ATOMIC_IMAX = 0xBA
    IMM_ATOMIC_IMIN = 0xBB
    IMM_ATOMIC_UMAX = 0xBC
    IMM_ATOMIC_UMIN = 0xBD
    SYNC = 0xBE
    DADD = 0xBF
    DMAX = 0xC0
    DMIN = 0xC1
    DMUL = 0xC2
    DEQ = 0xC3
    DGE = 0xC4
    DLT = 0xC5
    DNE = 0xC6
    DMOV = 0xC7
    DMOVC = 0xC8
    DTOF = 0xC9
    FTOD = 0xCA
    EVAL_SNAPPED = 0xCB
    EVAL_SAMPLE_INDEX = 0xCC
    EVAL_CENTROID = 0xCD
    DCL_GS_INSTANCE_COUNT = 0xCE
    ABORT = 0xCF
    DEBUG_BREAK = 0xD0
    RESERVED = 0xD1


class D3D_11_1(enum.Enum):
    """D3D 11.1 Opcodes"""
    DDIV = 0xD2
    DFMA = 0xD3
    DRCP = 0xD4
    MSAD = 0xD5
    D_TO_I = 0xD6
    D_TO_U = 0xD7
    I_TO_D = 0xD8
    U_TO_D = 0xD9
    RESERVED = 0xDA


class WDDM_1_3(enum.Enum):
    """WDDM 1.3 Opcodes"""
    GATHER_4_FEEDBACK = 0xDB
    GATHER_4_C_FEEDBACK = 0xDC
    GATHER_4_PO_FEEDBACK = 0xDD
    GATHER_4_PO_C_FEEDBACK = 0xDE
    LD_FEEDBACK = 0xDF
    LD_MS_FEEDBACK = 0xE0
    LD_UAV_TYPED_FEEDBACK = 0xE1
    LD_RAW_FEEDBACK = 0xE2
    LD_STRUCTURED_FEEDBACK = 0xE3
    SAMPLE_L_FEEDBACK = 0xE4
    SAMPLE_C_LZ_FEEDBACK = 0xE5
    SAMPLE_CLAMP_FEEDBACK = 0xE6
    SAMPLE_B_CLAMP_FEEDBACK = 0xE7
    SAMPLE_D_CLAMP_FEEDBACK = 0xE8
    SAMPLE_C_CLAMP_FEEDBACK = 0xE9
    CHECK_ACCESS_FULLY_MAPPED = 0xEA
    RESERVED = 0xEB


Opcode = Union[D3D_10_0, D3D_10_1, D3D_11_0, D3D_11_1, WDDM_1_3]
