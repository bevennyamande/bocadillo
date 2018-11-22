"""The Bocadillo API class."""
import inspect
import os
from http import HTTPStatus
from typing import Optional, Tuple, Type, List, Dict, Any, Union

from asgiref.wsgi import WsgiToAsgi
from starlette.testclient import TestClient
from uvicorn.main import run, get_logger
from uvicorn.reloaders.statreload import StatReload

from .checks import check_route
from .constants import ALL_HTTP_METHODS
from .error_handlers import ErrorHandler, handle_http_error
from .exceptions import HTTPError
from .extensions.base import BaseExtension
from .hooks import HookFunction
from .media import Media
from .middleware import CommonMiddleware, RoutingMiddleware
from .redirection import Redirection
from .request import Request
from .response import Response
from .route import Route
from .app_types import ASGIApp, WSGIApp, ASGIAppInstance


class API:
    """Bocadillo API.

    Parameters
    ----------
    media_type : str, optional
        Determines how values given to `res._media` are serialized.
        Can be one of the supported _media types.
        Defaults to 'application/json'.
    """

    _error_handlers: List[Tuple[Type[Exception], ErrorHandler]]
    extensions = []

    def __init__(self, media_type: Optional[str] = Media.JSON, **kwargs):
        self._routes: Dict[str, Route] = {}
        self._named_routes: Dict[str, Route] = {}

        self._error_handlers = []
        self.add_error_handler(HTTPError, handle_http_error)

        self._extra_apps: Dict[str, Any] = {}

        self.client = self._build_client()

        self._media = Media(media_type=media_type)

        # Middleware
        self._routing_middleware = RoutingMiddleware(self)
        self._common_middleware = CommonMiddleware(self._routing_middleware)

        self._init_extensions(**kwargs)

    @classmethod
    def extend(cls, *extensions: BaseExtension):
        """Register a new extension."""
        cls.extensions += extensions

    def _init_extensions(self, **kwargs):
        for extension in type(self).extensions:
            extension.init(self, **kwargs)

    def _build_client(self) -> TestClient:
        return TestClient(self)

    def mount(self, prefix: str, app: Union[ASGIApp, WSGIApp]):
        """Mount another WSGI or ASGI app at the given prefix."""
        if not prefix.startswith('/'):
            prefix = '/' + prefix
        self._extra_apps[prefix] = app

    @property
    def media_type(self) -> str:
        return self._media.type

    @media_type.setter
    def media_type(self, media_type: str):
        self._media.type = media_type

    @property
    def media_handlers(self) -> dict:
        return self._media.handlers

    @media_handlers.setter
    def media_handlers(self, media_handlers: dict):
        self._media.handlers = media_handlers

    def add_error_handler(self, exception_cls: Type[Exception],
                          handler: ErrorHandler):
        """Register a new error handler.

        Parameters
        ----------
        exception_cls : Exception class
            The type of exception that should be handled.
        handler : (request, response, exception) -> None
            The actual error handler, which is called when an instance of
            `exception_cls` is caught.
        """
        self._error_handlers.insert(0, (exception_cls, handler))

    def error_handler(self, exception_cls: Type[Exception]):
        """Register a new error handler (decorator syntax).

        Example
        -------
        >>> import bocadillo
        >>> api = bocadillo.API()
        >>> @api.error_handler(KeyError)
        ... def on_key_error(req, resp, exc):
        ...     pass  # perhaps set resp.content and resp.status_code
        """

        def wrapper(handler):
            self.add_error_handler(exception_cls, handler)
            return handler

        return wrapper

    def _find_handlers(self, exception):
        return (
            handler for err_type, handler in self._error_handlers
            if isinstance(exception, err_type)
        )

    def _handle_exception(self, request, response, exception) -> None:
        """Handle an exception raised during dispatch.

        At most one handler is called for the exception: the first one
        to support it.

        If no handler was registered for the exception, it is raised.
        """
        for handler in self._find_handlers(exception):
            handler(request, response, exception)
            break
        else:
            raise exception from None

    def route(self, pattern: str, *, methods: List[str] = None,
              name: str = None):
        """Register a new route.

        Parameters
        ----------
        pattern : str
            A route pattern given as an f-string expression.
        methods : list of str, optional
            HTTP methods supported by this route.
            Defaults to all HTTP methods.
            Ignored for class-based views.
        name : str, optional
            A name for this route, which must be unique.

        Example
        -------
        >>> import bocadillo
        >>> api = bocadillo.API()
        >>> @api.route('/greet/{person}')
        ... def greet(req, resp, person: str):
        ...     pass
        """
        if methods is None:
            methods = ALL_HTTP_METHODS

        methods = [method.upper() for method in methods]

        def wrapper(view):
            if inspect.isclass(view):
                view = view()
            check_route(pattern, view, methods)
            route = Route(
                pattern=pattern,
                view=view,
                methods=methods,
                name=name,
            )

            self._routes[pattern] = route
            if name is not None:
                self._named_routes[name] = route

            return route

        return wrapper

    @staticmethod
    def before(hook_function: HookFunction, *args, **kwargs):
        """Register a before hook on a route.

        Note: @api.before() must be above @api.route().
        """
        return Route.before_hook(hook_function, *args, **kwargs)

    @staticmethod
    def after(hook_function: HookFunction, *args, **kwargs):
        """Register an after hook on a route.

        Note: @api.after() must be above @api.route().
        """
        return Route.after_hook(hook_function, *args, **kwargs)

    def _find_matching_route(self, path: str) -> Tuple[Optional[str], dict]:
        """Find a route matching the given path."""
        for pattern, route in self._routes.items():
            kwargs = route.match(path)
            if kwargs is not None:
                return pattern, kwargs
        return None, {}

    def _get_route_or_404(self, name: str):
        try:
            return self._named_routes[name]
        except KeyError as e:
            raise HTTPError(HTTPStatus.NOT_FOUND.value) from e

    def url_for(self, name: str, **kwargs) -> str:
        """Return the URL path for a route.

        Parameters
        ----------
        name : str
            Name of the route.
        kwargs :
            Route parameters.

        Raises
        ------
        HTTPError(404) :
            If no route exists for the given `name`.
        """
        route = self._get_route_or_404(name)
        return route.url(**kwargs)

    def redirect(self, *,
                 name: str = None,
                 url: str = None,
                 permanent: bool = False,
                 **kwargs):
        """Redirect to another route.

        Parameters
        ----------
        name : str, optional
            Name of the route to redirect to.
        url : str, optional (unless name not given)
            URL of the route to redirect to.
        permanent : bool, optional
            If False (the default), returns a temporary redirection (302).
            If True, returns a permanent redirection (301).
        kwargs :
            Route parameters.
        """
        if name is not None:
            url = self.url_for(name=name, **kwargs)
        else:
            assert url is not None, 'url is expected if no route name is given'
        raise Redirection(url=url, permanent=permanent)

    def run(self,
            host: str = None,
            port: int = None,
            debug: bool = False,
            log_level: str = 'info'):
        """Serve the application using uvicorn.

        Parameters
        ----------
        host : str, optional
            The host to bind to.
            Defaults to '127.0.0.1' (localhost). If not given and `PORT` is set,
            '0.0.0.0' will be used to serve to all known hosts.
        port : int, optional
            The port to bind to.
            Defaults to 8000 or (if set) the value of the `PORT` environment
            variable.
        debug : bool, optional
            Whether to serve the application in debug mode. Defaults to `False`.
        log_level : str, optional
            A logging level for the debug logger. Must be compatible with
            logging levels from the `logging` module.

        See Also
        --------
        https://www.uvicorn.org/settings/
        """
        if 'PORT' in os.environ:
            port = int(os.environ['PORT'])
            if host is None:
                host = '0.0.0.0'

        if host is None:
            host = '127.0.0.1'

        if port is None:
            port = 8000

        if debug:
            reloader = StatReload(get_logger(log_level))
            reloader.run(run, {
                'app': self,
                'host': host,
                'port': port,
                'log_level': log_level,
                'debug': debug,
            })
        else:
            run(self, host=host, port=port)

    async def dispatch(self, request: Request) -> Response:
        """Dispatch a request and return a response."""
        response = Response(request, media=self._media)

        try:
            pattern, kwargs = self._find_matching_route(request.url.path)
            route = self._routes.get(pattern)
            if route is None:
                raise HTTPError(status=404)
            else:
                try:
                    await route(request, response, **kwargs)
                except Redirection as redirection:
                    response = redirection.response
        except Exception as e:
            self._handle_exception(request, response, e)

        return response

    def _is_routing_middleware(self, middleware_cls) -> bool:
        return hasattr(middleware_cls, 'dispatch')

    def add_middleware(self, middleware_cls, **kwargs):
        if self._is_routing_middleware(middleware_cls):
            self._routing_middleware.add(middleware_cls, **kwargs)
        else:
            self._common_middleware.add(middleware_cls, **kwargs)

    def _find_app(self, scope: dict) -> ASGIAppInstance:
        """Return an ASGI app depending on the scope's path."""
        path: str = scope['path']

        # Return a sub-mounted extra app, if found
        for prefix, app in self._extra_apps.items():
            if not path.startswith(prefix):
                continue
            # Remove prefix from path so that the request is made according
            # to the mounted app's point of view.
            scope['path'] = path[len(prefix):]
            try:
                return app(scope)
            except TypeError:
                app = WsgiToAsgi(app)
                return app(scope)

        return self._common_middleware(scope)

    def __call__(self, scope: dict) -> ASGIAppInstance:
        return self._find_app(scope)
