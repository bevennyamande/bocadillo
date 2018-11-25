from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from .base import MiddlewareExtension


class HSTS(MiddlewareExtension):
    """Extension for HSTS (HTTP Strict Transport Security).

    Parameters
    ----------
    enable_hsts : bool, optional
        If True, automatically redirect HTTP traffic to HTTPS.
        Defaults to False.
    """

    flag = 'enable_hsts'
    middleware = HTTPSRedirectMiddleware
