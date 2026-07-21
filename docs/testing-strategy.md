# Test strategy

## Goal

The test suite protects the public behavior of `starlette-i18n` 3.x. It tests catalogs, exported helpers, and the ASGI middleware as application consumers use them; it does not assert private parsing or matching implementation details.

## Coverage areas

### Catalog and public API

- Discover normalized locale directories and select configured defaults.
- Fall back to the default locale for unsupported values.
- Fail fast for a missing catalog directory or missing compiled default catalog.
- Exercise exported `gettext`, `ngettext`, `gettext_lazy`, and locale context behavior.

### HTTP negotiation

- Select defaults, exact complex tags, and less-specific language fallbacks.
- Honor q-value ordering, ignore zero-quality and malformed entries, and use wildcard fallback.
- Prefer a valid locale cookie over the header.
- Verify custom and disabled selector configuration through middleware construction and requests.

### Request and response contract

- Expose the selected `Locale` through `request.state.locale` and translation helpers.
- Set `Content-Language` and merge/de-duplicate `Vary` values.
- Restore locale context when handlers fail.
- Keep simultaneous requests isolated.
- Pass non-HTTP ASGI scopes through without locale mutation.

### Examples

Smoke-test the basic response and Jinja request-local translation example.

## Boundaries

Tests must use `TranslationCatalog`, `LocaleMiddleware`, request/response data, and public helpers. Private functions may change without requiring test rewrites as long as the public contract remains stable. Coverage percentage is informational; meaningful behavioral cases take priority over line or branch targets.
