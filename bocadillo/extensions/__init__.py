from .allowed_hosts import AllowedHosts
from .cors import CORS
from .hsts import HSTS
from .static import Static
from .templates import Templates

builtin_extensions = [
    AllowedHosts(),
    Static(),
    CORS(),
    HSTS(),
    Templates(),
]
