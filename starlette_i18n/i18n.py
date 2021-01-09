from __future__ import annotations

import typing as t

from babel.support import LazyProxy
from starlette.datastructures import Headers

from . import constants
from .context import ContextStorage
from .locale import Locale, gettext_translations


class LanguageCtx(ContextStorage):
    DEFAULT_VALUE = Locale.get(constants.DEFAULT_LOCALE)
    CONTEXT_KEY_NAME = "language"


_language_ctx = LanguageCtx()


def _make_lazy_gettext(lookup_func: t.Callable) -> t.Callable:
    def lazy_gettext(
        string: t.Union[LazyProxy, str],
        *args: t.Any,
        locale: t.Optional[str] = None,
        **kwargs: t.Any,
    ) -> t.Union[LazyProxy, str]:

        if isinstance(string, LazyProxy):
            return string

        if "enable_cache" not in kwargs:
            kwargs["enable_cache"] = False

        return LazyProxy(lookup_func, string, locale=locale, *args, **kwargs)

    return lazy_gettext


def _lookup_func(
    message: str,
    plural_message: t.Optional[str] = None,
    count: t.Optional[int] = None,
    **kwargs: t.Any,
):
    code = kwargs.pop("locale", None)
    locale = Locale.get(code) if code else _language_ctx.get()
    return locale.translate(message, plural_message, count, **kwargs)


gettext_lazy = _make_lazy_gettext(_lookup_func)


def _get_code_from_headers(headers: Headers, language_header: str, default_code: str) -> str:
    return str(headers.get(language_header, default_code))


def load_gettext_translations(directory: str, domain: str) -> None:
    gettext_translations.load_translations(directory, domain)


def set_locale(code: str) -> None:
    locale = Locale.get(code)
    _language_ctx.set(locale)


def get_locale() -> Locale:
    locale: Locale = _language_ctx.get()
    return locale


def get_locale_code() -> str:
    return str(get_locale())
