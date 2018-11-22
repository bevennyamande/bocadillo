from .api import API
from .middleware import RoutingMiddleware
from .media import Media
from .extensions import builtin_extensions
from .extensions.staticfiles import static

for extension in builtin_extensions:
    API.extend(extension)

__version__ = '0.5.0'
