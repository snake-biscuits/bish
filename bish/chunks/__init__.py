# http://timjones.io/blog/archive/2015/09/02/parsing-direct3d-shader-bytecode
__all__ = [
    "rdef", "shex", "sign", "stat",
    "Signature", "ResourceDefinition", "Shader_v5", "Statistics"]


from . import rdef
from . import shex
from . import sign
from . import stat


from .rdef import ResourceDefinition
from .shex import Shader_v5
from .sign import Signature
from .stat import Statistics


parser = {
    "ISGN": Signature,
    "OSGN": Signature,
    "RDEF": ResourceDefinition,
    "SHEX": Shader_v5,
    "STAT": Statistics}
# ^ {chunk_id, parser_class}

unsupported_chunks = {
    "IFCE": "Interfaces",
    "ISG1": "In Signature w/ Stream & MinPrecision",
    "OSG1": "Out Signature w/ Stream & MinPrecision",
    "OSG5": "Out Signature (Shader Model 5)",
    "PCSG": "Patch Constant Signature Chunk",
    "SFIO": "???",
    "SHDR": "Shader (Shader Model 4)",
    "SPDB": "Debug",
    "XHSH": "???"}  # 8 bytes, appears in vertex shaders; hash?
# ^ {chunk_id, purpose}
