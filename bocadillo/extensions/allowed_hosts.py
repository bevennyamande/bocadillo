from typing import List

from starlette.middleware.trustedhost import TrustedHostMiddleware

from .base import BaseExtension


class AllowedHosts(BaseExtension):

    def init(self, api, allowed_hosts: List[str] = None, **kwargs):
        """

        Parameters
        ----------
        api : API
        allowed_hosts : list of str, optional
            A list of hosts which the server is allowed to run at.
            If the list contains '*', any host is allowed.
            Defaults to ['*'].
        """
        if allowed_hosts is None:
            allowed_hosts = ['*']
        api.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
