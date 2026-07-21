# Locale negotiation

`LocaleMiddleware` selects exactly one `Locale` for each HTTP request. It is intended for UI text, API messages, and templates that need a request-local gettext catalog.

## Setup

Compile catalogs during your build or release process, then load them once during application startup:

```python
from starlette_i18n import LocaleMiddleware, TranslationCatalog

catalog = TranslationCatalog.load("locales", domain="messages", default_locale="en")
app.add_middleware(LocaleMiddleware, catalog=catalog)
```

A loaded catalog must contain the configured default locale. Missing catalog directories and defaults without a compiled `.mo` file raise an exception at startup rather than silently returning untranslated text.

## Resolution order

The middleware evaluates these sources in order:

1. The configured cookie, `locale` by default.
2. The configured language header, `Accept-Language` by default.
3. The catalog's default locale.

Set `cookie_name=None` to disable cookie selection. A custom language header is supported with `language_header="X-Locale"`.

## Accept-Language behavior

The header is parsed as a comma-separated list. Valid `q` values from `0` to `1` set priority; entries with `q=0` are excluded and ties retain request order. Invalid entries are ignored.

Each supported candidate uses RFC 4647 lookup: an exact match is preferred, then subtags are removed from the right. With `pt` and `en` catalogs, `pt-BR` resolves to `pt`. Exact complex locale directories also work: `zh_CN` normalizes to `zh-CN`, so a request for `zh-CN` selects it directly. A wildcard chooses the configured default only after explicit supported ranges have been considered.

## Request-local APIs

The selected value is placed in `request.state.locale` and in a `ContextVar` for the duration of the request:

```python
from starlette_i18n import get_locale, gettext, ngettext


async def endpoint(request):
    title = gettext("Success")
    items = ngettext("{count} item", "{count} items", 2, count=2)
    assert get_locale() is request.state.locale
```

The context is restored in a `finally` block, including when the endpoint raises. Helpers called outside a request use the default catalog configured by the middleware.

## Response headers and caches

Every HTTP response gets `Content-Language` with the selected normalized tag. The middleware adds its enabled inputs to `Vary`: by default, `Vary` includes `Cookie, Accept-Language`; existing `Vary` values are preserved. This prevents a shared cache from returning a representation selected for one locale to another request.

If an exception escapes the middleware and an outer error middleware creates the response, that outer middleware owns the error response headers. Put error handling inside `LocaleMiddleware` when error responses must also include `Content-Language`.

## Templates

Do not install gettext functions into a shared Jinja environment while serving a request. That mutates shared state and can mix locales under concurrent ASGI requests. Pass the request-local callable into rendering instead:

```python
return HTMLResponse(template.render(request=request, _=request.state.locale.translate))
```

Use `{{ _("Success") }}` in the template. See `examples/jinja_app.py`.
