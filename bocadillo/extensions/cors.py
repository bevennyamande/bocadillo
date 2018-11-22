from starlette.middleware.cors import CORSMiddleware

from .base import BaseExtension

DEFAULT_CORS_CONFIG = {
    'allow_origins': [],
    'allow_methods': ['GET'],
}


class CORS(BaseExtension):
    """Add support for CORS headers."""

    def init(self, api, enable_cors: bool = False, cors_config: dict = None,
             **kwargs):
        """Initialize an app with CORS headers configuration.

        Parameters
        ----------
        api : API
        enable_cors : bool, optional
            If True, Cross Origin Resource Sharing will be configured according
            to `cors_config`.
            Defaults to False.
        cors_config : dict, optional
            A dictionary of CORS configuration parameters.
            Defaults to `{'allow_origins': [], 'allow_methods': ['GET']}`.
            See also: https://www.starlette.io/middleware/#corsmiddleware
        """
        if not enable_cors:
            return
        cors_config = {**DEFAULT_CORS_CONFIG, **(cors_config or {})}
        api.add_middleware(CORSMiddleware, **cors_config)
