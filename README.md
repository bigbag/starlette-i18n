# starlette-i18n

Request-safe gettext localization and locale negotiation for Starlette applications.

## Requirements

- Python 3.11+ (CI validates Python 3.11, 3.12, 3.13, and 3.14)
- Starlette newer than 1.2.0 and below 2.0

## Install

```console
uv add starlette-i18n
pip install starlette-i18n
```

## Quick start

Compile gettext catalogs before starting the application, then load them once:

```python
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse

from starlette_i18n import LocaleMiddleware, TranslationCatalog, gettext

catalog = TranslationCatalog.load("locales", domain="messages", default_locale="en")
app = Starlette()
app.add_middleware(LocaleMiddleware, catalog=catalog)


async def homepage(request):
    return PlainTextResponse(gettext("Success"))


app.add_route("/", homepage)
```

The selected `Locale` is also available as `request.state.locale`. The public translation helpers are `gettext`, `ngettext`, `gettext_lazy`, and `get_locale`.

## Locale selection

`LocaleMiddleware` selects one catalog for each HTTP request in this order:

1. A valid configured locale cookie (`locale` by default).
2. The request's `Accept-Language` header.
3. The catalog's configured default locale.

Header values are parsed as a q-weighted priority list and resolved using RFC 4647 lookup. Exact complex tags work: a `zh-CN` request selects a `zh_CN` catalog directory, while `pt-BR` can fall back to a `pt` catalog. Invalid values and `q=0` entries are ignored. A wildcard falls back to the configured default when no explicit supported locale matches.

Responses include `Content-Language`. The middleware adds configured selection inputs (`Cookie` and `Accept-Language` by default) to `Vary` so shared caches do not serve the wrong representation.

Configure another cookie name, or disable cookies entirely:

```python
app.add_middleware(LocaleMiddleware, catalog=catalog, cookie_name="language")
app.add_middleware(LocaleMiddleware, catalog=catalog, cookie_name=None)
```

## ASGI and Jinja safety

The active locale is stored in a `ContextVar` and is reset after every request, including exceptions. Concurrent requests therefore cannot leak translations into one another.

Do not install gettext functions into a shared Jinja environment per request: Jinja's installation mutates global environment state. Pass a request-local callable instead:

```python
html = template.render(request=request, _=request.state.locale.translate)
```

Then use `{{ _("Success") }}` in the template. See `examples/jinja_app.py`.

## Examples

```console
uv run --with uvicorn examples/basic_usage.py
uv run --with 'uvicorn[standard]' uvicorn examples.uvicorn_runner:app --reload
uv run --with gunicorn --with uvicorn gunicorn -c examples/gunicorn_conf.py examples.gunicorn_runner:app
curl -H 'Accept-Language: ru' http://127.0.0.1:8000/
```

## Migrating from 2.x

3.0 is a breaking release. It requires Python 3.11+, moves the package to `src/`, uses `pyproject.toml` and `uv`, and replaces `LocaleDefaultMiddleware`, `LocaleFromCookieMiddleware`, `LocaleFromHeaderMiddleware`, and the old ordering-dependent `LocaleMiddleware` with the single `LocaleMiddleware` shown above. Load catalogs with `TranslationCatalog.load()` instead of `load_gettext_translations()`.

## Further documentation

- [Locale negotiation, cache behavior, and template safety](docs/locale-negotiation.md)
- [Runnable examples and catalog workflow](examples/README.md)

## Development

```console
uv sync --all-groups
make lint
make test
make build
```

## License

starlette-i18n is distributed under the Apache License 2.0. Report vulnerabilities through the [security policy](https://github.com/bigbag/starlette-i18n/security/policy).
