# Extensions

Bocadillo being progressive, there should be a way for users with various needs to use or not use certain features.

To this extent, Bocadillo provides an **extension mechanism**, which provides a way to (optionally) extend the behavior of the `API` object. In fact, some of Bocadillo's built-in features are implemented as extensions, e.g. templates, static files or CORS headers.

## What is an extension?

From a user's perspective, Bocadillo extensions  are components that **perform extra logic when an `API` object is created**.

In practice, this means that they hook into calls to `bocadillo.API()` to add routes, middleware or even entire methods to the resulting `API` object.

For example:

- The `CORS` extension registers a middleware via `api.add_middleware()` that manages and checks CORS headers.
- The `Templates` extension provides the `.template()` `.template_sync()` and `.template_string()` methods (see [Templates](../api-guides/templates.md)).

## Inspecting extensions

Bocadillo stores registered extensions in `API.extensions`.

Here, you can see the extensions registered by default:

```python
>>> from bocadillo import API
>>> API.extensions
[AllowedHosts(), Static(), CORS(), HSTS(), Templates()]
```

Please note that, as you may have guessed from `extensions` being a class attribute, **all API instances will receive the same extensions**.

::: tip
While the above is generally not a problem, you can create a subclass of `API` if necessary. It will have its own, independent set of extensions.
:::

## Using extensions

To make Bocadillo applications use an extension, pass an instance of it to `API.use()`.

For the sake of example, here's how you'd use the (already registered) templates extension:

```python
# my_api.py
from bocadillo import API
from bocadillo.extensions import Templates

API.use(Templates())
```

::: warning
Don't forget to instanciate the extension:  use `Templates()` instead of `Templates`.
:::

Please note that **extensions will initialise the API object in the order of calls to `api.use()`**.

## Writing extensions

If you are interested in writing your own Bocadillo extensions, please see our guide: [How to write extensions](../how-to/extensions.md).
