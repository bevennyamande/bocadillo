"""Base extension classes and mixins."""


class BaseExtension:
    """Base class for Bocadillo extensions."""

    def init(self, api, **kwargs):
        pass

    def alias_methods(self, api, *method_names: str):
        """Alias methods of the extension onto the app.

        Parameters
        ----------
        api : API
        method_names : str
        """
        for method_name in method_names:
            setattr(api, method_name, getattr(self, method_name))

    def alias_property(self, api, property_name: str, has_setter=False):
        """Alias a property of the extension onto the app.

        Parameters
        ----------
        api : API
        property_name : str
        has_setter : bool, optional
            Whether the aliased property has a setter.
            Defaults to False.
        """
        this = self

        def get_value(self):
            nonlocal this
            return getattr(this, property_name)

        if has_setter:

            def set_value(self, value):
                nonlocal this
                setattr(this, property_name, value)

        else:
            set_value = None

        setattr(type(api), property_name, property(get_value, set_value))


class UseOnFlagExtensionMixin:
    """Mixin for extensions enabled by the value of a bool keyword argument.

    Class Attributes
    ----------------
        flag : str, optional
        The name of the keyword argument that will be checked to decide
        whether the middleware should be added.
        Defauts to None (always add the middleware).
    """

    flag: str = None

    def should_use(self, **kwargs) -> bool:
        """Return whether the extension should be used."""
        if self.flag is None:
            return True
        return kwargs.get(self.flag)


class MiddlewareExtension(UseOnFlagExtensionMixin, BaseExtension):
    """Base class for extensions that add middleware to the API object."""

    middleware = None

    def get_middleware_kwargs(self, **kwargs) -> dict:
        """Return keyword arguments to pass to the middleware constructor."""
        return {}

    def init(self, api, **kwargs) -> None:
        if not self.should_use(**kwargs):
            return
        middleware_kwargs = self.get_middleware_kwargs(**kwargs)
        api.add_middleware(self.middleware, **middleware_kwargs)
