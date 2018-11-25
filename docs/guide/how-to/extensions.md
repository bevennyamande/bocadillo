# How to write a Bocadillo extension

This guide explains how you can implement and use your own Bocadillo extensions. For an overview of Bocadillo extensions, see our [Extensions](../topics/extensions.md) topic guide.

## The extension interface

As far as Bocadillo is concerned, an extension is any Python class that exposes a `.init(api, **kwargs)` method. It is however recommended to subclass `BaseExtension` which provides behavior common to all extensions.

So an extension may look something like this:

```python
# my_extensions.py
from bocadillo.extensions import BaseExtension

class Colors(BaseExtension):

    def init(self, api, **kwargs):
        # TODO: init api with colorful features
        print('initialising api with Colors')
```

In practice, the `.init()` methods of registered extensions will be called at the very end of building an `API` object (i.e. at the end of its `__init__()` method).

## What can I do in `.init()`?

Within the `.init()` method, the extension is allowed to **mutate the `api` object to register extra functionality**. (So basically, you can do anything you want.)
 
Here are examples of what an extension might do:

- Register middleware classes using `api.add_middleware()` (also see [Middleware extensions](#middleware-extensions)).
- Add routes using `@api.route()`.
- Dynamically add methods, attributes or properties to the `api` object (this is how `Templates` is implemented).
- etc.

For example, let's make `Colors` register a new route on the API:

```python
# my_extensions.py
from bocadillo.extensions import BaseExtension

class Colors(BaseExtension):

    def init(self, api, **kwargs):
        @api.route('/colors')
        async def colors(req, res):
            res.media = ['black', 'white']
```

::: tip NOTE
If your extension needs to store some attributes (for example the `api` object), it is better practice to first initialise them in the extension's `__init__()` method.
:::

## Using keyword arguments

All keyword arguments given to the `API` object will be passed to the extension. The extension can use these to perform initialisation logic or derive values:

```python
# my_extensions.py
from typing import List
from bocadillo.extensions import BaseExtension

class Colors(BaseExtension):

    def init(self, api, colors: List[str] = None, **kwargs):
        """Init an app with colorful extensions."""
        if colors is None:
            colors = []

        @api.route('/colors')
        async def colors(req, res):
            res.media = colors

# myapi.py
from bocadillo import API
from my_extensions import Colors

API.use(Colors())
# Here, `colors` will be passed to the `Colors` extension.
api = bocadillo.API(colors=['red', 'green', 'blue'])
```

## Dynamically adding attributes, methods or properties

## Middleware extensions

Bocadillo provides a specific `MiddlewareExtension` base class for extensions that add middleware to an `API` object. This is actually how the `CORS`, `HSTS` and `AllowedHosts` extensions are implemented.

### Basic usage

The basic usage of this base class is to set which `middleware` should be registered, e.g.:

```python
# my_extensions.py
from bocadillo.extensions import MiddlewareExtension
from my_middleware import PeopleMiddleware

class PeopleExtension(MiddlewareExtension):

    middleware = PeopleMiddleware
```

### Enabling the middleware based on a flag

If the extension should be enabled/disabled based on a flag (i.e. a boolean keyword argument) passed to `API`, you should set its name on the extension:

```python
# my_extensions.py
class PeopleExtension(MiddlewareExtension):

    middleware = PeopleMiddleware
    flag = 'enable_people'

# my_api.py
from bocadillo import API
from my_extensions import PeopleExtension

API.use(PeopleExtension())
api = API(enable_people=True)  # False by default
```

By default, no flag is used, i.e. the middleware will always be registered.

### Passing extra kwargs to the middleware constructor

If your middleware class needs extra keyword arguments to be built, you can override `.get_middleware_kwargs()`. It will receive the same `kwargs` as those passed to the `.init()` method.

For example, the following will result in calling `PersonMiddleware(number=10)`.

```python
# my_extensions.py
class PeopleExtension(MiddlewareExtension):

    middleware = PeopleMiddleware

    def get_middleware_kwargs(self, number: int = 10, **kwargs) -> dict:
        return {'number': number}
```
