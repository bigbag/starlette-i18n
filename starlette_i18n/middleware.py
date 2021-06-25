import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from . import constants, i18n
from .locale import gettext_translations

logger = logging.getLogger(__name__)


# See RFC 7231, section 5.3.5: Accept-Language
accept_language_re = re.compile(
    r"""
    (?P<code>[A-Za-z]{1,8}(?:-[A-Za-z0-9]{1,8})*|\*)   # "en", "en-au", "x-y-z", "es-419", "*"
    (?:\s*;\s*q=(?P<q>0(?:\.\d{,3})?|1(?:\.0{,3})?))?  # Optional "q=1.00", "q=0.8"
""",
    re.VERBOSE,
)


@dataclass
class LocaleDefaultMiddleware(BaseHTTPMiddleware):
    """Middleware sticks locale to the default_code"""

    app: ASGIApp
    default_code: str = constants.DEFAULT_LOCALE
    dispatch_func: DispatchFunction = field(init=False)

    def __post_init__(self):
        self.dispatch_func = self.dispatch

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger.debug("LocaleDefaultMiddleware::dispatch")
        if self.default_code:
            logger.debug("LocaleDefaultMiddleware: set locale to: %s", self.default_code)
            i18n.set_locale(code=self.default_code)
        response = await call_next(request)
        return response


@dataclass
class LocaleAutodetectMiddleware(BaseHTTPMiddleware):
    """
    Middleware autodetects locale from the language header (`Accept-Language` by default).

    Sticks locale to the default code if the `default_code` is not empty. Set the
    `default_code` to empty string or None explicitly to avoid defaulting
    if necessary (in the middleware stack f.e.).
    """

    app: ASGIApp
    language_header: str = constants.LANGUAGE_HEADER
    default_code: str = constants.DEFAULT_LOCALE
    dispatch_func: DispatchFunction = field(init=False)

    def __post_init__(self):
        self.dispatch_func = self.dispatch

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger.debug("LocaleAutodetectMiddleware::dispatch")
        locale_code = self._get_code_from_headers(request=request)
        if not locale_code:
            if self.default_code:
                locale_code = self.default_code
        if locale_code:
            logger.debug("LocaleAutodetectMiddleware: set locale to: %s", locale_code)
            i18n.set_locale(code=locale_code)
        response = await call_next(request)
        return response

    def _get_code_from_headers(self, request: Request) -> Optional[str]:
        headers = request.headers
        locale_string = str(headers.get(self.language_header, ""))
        if not locale_string:
            return None
        locale_list = sorted(
            [
                (m["code"], float(m["q"]) if m["q"] else 1)
                for m in [accept_language_re.match(s.strip()) for s in locale_string.split(",")]
                if m
            ],
            key=lambda l: -l[1],
        )
        supported = gettext_translations.supported_locales
        appropriate = []
        for locale in locale_list:
            locale_requested = locale[0].lower().replace("-", "_")
            for s in supported:
                supported_locale = s.lower()
                locale_prefix = locale_requested
                while locale_prefix:
                    if supported_locale == locale_prefix:
                        appropriate.append((s, locale[1]))
                    else:
                        supported_prefix = supported_locale
                        while supported_prefix:
                            if supported_prefix == locale_prefix:
                                appropriate.append((s, locale[1]))
                            supported_prefix = "_".join(supported_prefix.split("_")[:-1])
                    locale_prefix = "_".join(locale_prefix.split("_")[:-1])
        if not appropriate:
            return None
        return sorted(appropriate, key=lambda l: -l[1])[0][0]


@dataclass
class LocaleFromCookieMiddleware(BaseHTTPMiddleware):
    """
    Middleware processes language cookie (Language) to determine and setup locale.

    It tries to get the language cookie value and sets locale to the value got,
    if the value corresponds to one of the installed languages.
    """

    app: ASGIApp
    language_cookie: str = constants.LANGUAGE_COOKIE
    dispatch_func: DispatchFunction = field(init=False)

    def __post_init__(self):
        self.dispatch_func = self.dispatch

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger.debug("LocaleFromCookieMiddleware::dispatch")
        locale_code = self._get_code_from_cookie(request=request)
        if locale_code:
            logger.debug("LocaleFromCookieMiddleware: set locale to: %s", locale_code)
            i18n.set_locale(code=locale_code)
        response = await call_next(request)
        return response

    def _get_code_from_cookie(self, request: Request) -> Optional[str]:
        supported = gettext_translations.supported_locales
        locale_code = request.cookies.get(self.language_cookie)
        if locale_code in supported:
            return locale_code
        return None


# Backward compatibility
LocaleMiddleware = LocaleAutodetectMiddleware
