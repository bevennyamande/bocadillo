from starlette.middleware.cors import CORSMiddleware

from .base import MiddlewareExtension

DEFAULT_CORS_CONFIG = {'allow_origins': [], 'allow_methods': ['GET']}


class CORS(MiddlewareExtension):
    """Add support for CORS headers.

    Parameters
    ----------
    enable_cors : bool, optional
        If True, Cross Origin Resource Sharing will be configured according
        to `cors_config`.
        Defaults to False.
    cors_config : dict, optional
        A dictionary of CORS configuration parameters.
        Defaults to `{'allow_origins': [], 'allow_methods': ['GET']}`.
        See also: https://www.starlette.io/middleware/#corsmiddleware
    """

    flag = 'enable_cors'
    middleware = CORSMiddleware

    def get_middleware_kwargs(self, cors_config: dict = None, **kwargs):
        return {**DEFAULT_CORS_CONFIG, **(cors_config or {})}
