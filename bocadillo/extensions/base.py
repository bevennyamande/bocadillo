class BaseExtension:
    """Base class for Bocadillo extensions."""

    def init(self, app, **kwargs):
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

    def alias_property(self, app, property_name: str, has_setter=False):
        """Alias a property of the extension onto the app.

        Parameters
        ----------
        app : API
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

        setattr(type(app), property_name, property(get_value, set_value))
