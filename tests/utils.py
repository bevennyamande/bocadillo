from bocadillo import API


class RouteBuilder:
    """Builder of simple testing routes."""

    def __init__(self, api: API = None):
        self._api = api

    @property
    def api(self):
        return self._api

    def function_based(self, pattern: str, *args, res: dict = None,
                       **kwargs):
        if res is None:
            res = {}

        @self._api.route(pattern, *args, **kwargs)
        def view(request, response):
            for key, value in res.items():
                setattr(response, key, value)

    def class_based(self, pattern: str, *args, **kwargs):
        @self._api.route(pattern, *args, **kwargs)
        class View:
            pass
