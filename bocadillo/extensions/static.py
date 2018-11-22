from typing import Optional

from ..static import static
from .base import BaseExtension


class Static(BaseExtension):

    def init(self,
             api,
             static_dir: Optional[str] = 'static',
             static_root: Optional[str] = 'static',
             **kwargs):
        """Initialize an app with static files configuration.

        Parameters
        ----------
        api : API
        static_dir: str, optional
            The name of the directory containing static files, relative to
            the application entry point.
            Defaults to 'static'.
        static_root : str, optional
            The path prefix for static assets.
            Defaults to 'static'.
        """
        if static_dir is None:
            return

        if static_root is None:
            static_root = static_dir
        api.mount(static_root, static(static_dir))
