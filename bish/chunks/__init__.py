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
