"""Context-backed gettext helpers."""

from __future__ import annotations

from typing import Any

from babel.support import LazyProxy

from .context import get_locale


def gettext(message: str, **kwargs: Any) -> str:
    """Translate ``message`` using the active request locale."""
    return get_locale().translate(message, **kwargs)


def ngettext(message: str, plural_message: str, number: int, **kwargs: Any) -> str:
    """Translate a plural message using the active request locale."""
    return get_locale().translate(message, plural_message, number, **kwargs)


def gettext_lazy(message: str, **kwargs: Any) -> LazyProxy:
    """Return a lazily evaluated translation without cross-request caching."""
    return LazyProxy(gettext, message, enable_cache=False, **kwargs)
