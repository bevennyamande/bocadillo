import os
from collections import Coroutine
from contextlib import contextmanager
from typing import List

from jinja2 import FileSystemLoader, Template, Environment, select_autoescape

from .base import BaseExtension


def get_templates_environment(template_dirs: List[str]):
    return Environment(
        loader=FileSystemLoader(template_dirs),
        autoescape=select_autoescape(['html', 'xml']),
        enable_async=True,
    )


class Templates(BaseExtension):
    def __init__(self):
        self.api = None
        self.environment = None

    def init(self, api, templates_dir: str = 'templates', **kwargs):
        """Initialize an app with templates.

        Parameters
        ----------
        api : API
        templates_dir : str, optional
            The name of the directory containing templates, relative to
            the application entry point.
            Defaults to 'templates'.
        """
        self.api = api
        self.environment = get_templates_environment(
            [os.path.abspath(templates_dir)]
        )
        self.environment.globals.update(self._get_template_globals())

        self.alias_methods(api, 'template', 'template_string', 'template_sync')
        self.alias_property(api, 'templates_dir', has_setter=True)

    def _get_template_globals(self) -> dict:
        return {'url_for': self.api.url_for}

    @property
    def templates_dir(self) -> str:
        loader: FileSystemLoader = self.environment.loader
        return loader.searchpath[0]

    @templates_dir.setter
    def templates_dir(self, templates_dir: str):
        loader: FileSystemLoader = self.environment.loader
        loader.searchpath = [os.path.abspath(templates_dir)]

    def _get_template(self, name: str) -> Template:
        return self.environment.get_template(name)

    @contextmanager
    def _prevent_async_template_rendering(self):
        """If enabled, temporarily disable async template rendering.

        Notes
        -----
        Hot fix for a bug with Jinja2's async environment, which always
        renders asynchronously even under `render()`.
        Example error:
        `RuntimeError: There is no current event loop in thread [...]`
        """
        if not self.environment.is_async:
            yield
            return

        self.environment.is_async = False
        try:
            yield
        finally:
            self.environment.is_async = True

    @staticmethod
    def _prepare_context(context: dict = None, **kwargs):
        if context is None:
            context = {}
        context.update(kwargs)
        return context

    async def template(
        self, name_: str, context: dict = None, **kwargs
    ) -> Coroutine:
        """Render a template asynchronously.

        Can only be used within `async`  functions.

        Parameters
        ----------
        name_ : str
            Name of the template, located inside `templates_dir`.
            Trailing underscore to avoid collisions with a potential
            context variable named 'name'.
        context : dict
            Context variables to inject in the template.
        """
        context = self._prepare_context(context, **kwargs)
        return await self._get_template(name_).render_async(context)

    def template_sync(self, name_: str, context: dict = None, **kwargs) -> str:
        """Render a template synchronously.

        See Also
        --------
        .template()
        """
        context = self._prepare_context(context, **kwargs)
        with self._prevent_async_template_rendering():
            return self._get_template(name_).render(context)

    def template_string(
        self, source: str, context: dict = None, **kwargs
    ) -> str:
        """Render a template from a string (synchronous)."""
        context = self._prepare_context(context, **kwargs)
        with self._prevent_async_template_rendering():
            template = self.environment.from_string(source=source)
            return template.render(context)
