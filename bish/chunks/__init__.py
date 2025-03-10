# http://timjones.io/blog/archive/2015/09/02/parsing-direct3d-shader-bytecode
__all__ = [
    "rdef", "shex", "stat",
    "ResourceDefinition", "Shader_v5", "Statistics"]


# from . import isgn
# from . import osgn
from . import rdef
# from . import shdr
from . import shex
from . import stat


# from .isgn import InputSignature
# from .osgn import OutputSignature
from .rdef import ResourceDefinition
# from .shdr import Shader_v4
from .shex import Shader_v5
from .stat import Statistics


parser = {
    # "ISGN": InputSignature,
    # "OSGN": OutputSignature,
    "RDEF": ResourceDefinition,
    # "SHDR": Shader_v4,
    "SHEX": Shader_v5,
    "STAT": Statistics}
