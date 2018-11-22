from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from .base import BaseExtension


class HSTS(BaseExtension):

    def init(self, api, enable_hsts: bool = False, **kwargs):
        """Initialize an app with HSTS configuration.

        Parameters
        ----------
        api : API
        enable_hsts : bool, optional
            If True, enable HSTS (HTTP Strict Transport Security) and
            automatically redirect HTTP traffic to HTTPS.
            Defaults to False.
        """
        if enable_hsts:
            api.add_middleware(HTTPSRedirectMiddleware)
