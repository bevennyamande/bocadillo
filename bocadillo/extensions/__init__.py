from .allowed_hosts import AllowedHosts
from .base import *
from .cors import CORS
from .hsts import HSTS
from .staticfiles import Static
from .templates import Templates

builtin_extensions = [AllowedHosts(), Static(), CORS(), HSTS(), Templates()]
