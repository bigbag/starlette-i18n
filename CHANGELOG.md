# Changelog

## 3.0.0

- Require Python 3.11+ and validate 3.11–3.14 in CI.
- Move to PEP 621 metadata, Hatchling, uv, Ruff, strict mypy, and a `src/` layout.
- Replace legacy middleware classes with one pure-ASGI `LocaleMiddleware`.
- Add token-safe request-local locale context and response `Content-Language`/`Vary` headers.
- Use RFC 4647 lookup for q-weighted `Accept-Language` negotiation, fixing complex locale tags reported in [#16](https://github.com/bigbag/starlette-i18n/issues/16).
- Remove `LocaleDefaultMiddleware`, `LocaleFromCookieMiddleware`, `LocaleFromHeaderMiddleware`, `load_gettext_translations`, and the prior ordering-dependent API.

## 2.1.0

- Previous release history is available in the git history.
