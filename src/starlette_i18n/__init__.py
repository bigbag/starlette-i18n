"""Request-safe localization for Starlette."""

from .catalog import TranslationCatalog
from .context import get_locale
from .locale import Locale
from .middleware import LocaleMiddleware
from .translation import gettext, gettext_lazy, ngettext

__version__ = "3.0.0"

__all__ = [
    "Locale",
    "LocaleMiddleware",
    "TranslationCatalog",
    "get_locale",
    "gettext",
    "gettext_lazy",
    "ngettext",
]
