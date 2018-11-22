from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from .base import BaseExtension


class HSTS(BaseExtension):

    def init(self, app, enable_hsts: bool = False, **kwargs):
        """Initialize an app with HSTS configuration.

        Parameters
        ----------
        app : API
        enable_hsts : bool, optional
            If True, enable HSTS (HTTP Strict Transport Security) and
            automatically redirect HTTP traffic to HTTPS.
            Defaults to False.
        """
        if enable_hsts:
            app.add_middleware(HTTPSRedirectMiddleware)
