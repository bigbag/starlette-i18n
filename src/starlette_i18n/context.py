"""Request-local locale context."""

from contextvars import ContextVar, Token

from .locale import Locale

_current_locale: ContextVar[Locale | None] = ContextVar("starlette_i18n_locale", default=None)
_default_locale: Locale | None = None


def configure_default_locale(locale: Locale) -> None:
    """Configure the fallback locale used outside an active request."""
    global _default_locale
    _default_locale = locale


def get_locale() -> Locale:
    """Return the active locale or configured default outside a request."""
    locale = _current_locale.get()
    if locale is not None:
        return locale
    if _default_locale is None:
        raise RuntimeError("a TranslationCatalog must be configured before translation")
    return _default_locale


def set_locale(locale: Locale) -> Token[Locale | None]:
    """Set the active locale and return the restoration token."""
    return _current_locale.set(locale)


def reset_locale(token: Token[Locale | None]) -> None:
    """Restore the locale that preceded :func:`set_locale`."""
    _current_locale.reset(token)
