from .allowed_hosts import AllowedHostsExtension
from .base import BaseExtension
from .cors import CORSExtension
from .hsts import HSTSExtension
from .static import StaticExtension
from .templates import TemplatesExtension

builtin_extensions = [
    AllowedHostsExtension(),
    StaticExtension(),
    CORSExtension(),
    HSTSExtension(),
    TemplatesExtension(),
]
