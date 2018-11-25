from typing import List

from starlette.middleware.trustedhost import TrustedHostMiddleware

from .base import MiddlewareExtension

ALL_HOSTS = '*'


class AllowedHosts(MiddlewareExtension):
    """Add support for allowed hosts checks.

    Parameters
    ----------
    allowed_hosts : list of str, optional
        A list of hosts which the server is allowed to run at.
        If the list contains '*', any host is allowed.
        Defaults to ['*'].
    """

    middleware = TrustedHostMiddleware

    def get_middleware_kwargs(self, allowed_hosts: List[str] = None, **kwargs):
        if allowed_hosts is None:
            allowed_hosts = [ALL_HOSTS]
        return {'allowed_hosts': allowed_hosts}
