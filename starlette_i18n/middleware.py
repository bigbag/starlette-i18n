import logging
import typing as t
from dataclasses import dataclass, field

from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from . import constants, helpers, i18n

logger = logging.getLogger(__name__)


@dataclass
class BaseLocaleMiddleware(BaseHTTPMiddleware):
    app: ASGIApp
    default_code: t.Optional[str] = None
    dispatch_func: DispatchFunction = field(init=False)

    def __post_init__(self):
        self.dispatch_func = self.dispatch


@dataclass
class LocaleDefaultMiddleware(BaseLocaleMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger.debug("LocaleDefaultMiddleware::dispatch")

        if self.default_code:
            logger.debug(f"LocaleDefaultMiddleware: set locale to: {self.default_code}")
            i18n.set_locale(code=self.default_code)

        response = await call_next(request)
        return response


@dataclass
class LocaleFromCookieMiddleware(BaseLocaleMiddleware):
    language_cookie: str = constants.LANGUAGE_COOKIE

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger.debug("LocaleFromCookieMiddleware::dispatch")

        cookie_locale = helpers.CookieLocale(name=self.language_cookie, request=request)
        locale_code = cookie_locale.code or self.default_code

        if locale_code:
            logger.debug(f"LocaleFromCookieMiddleware: set locale to: {locale_code}")
            i18n.set_locale(code=locale_code)

        response = await call_next(request)
        return response


@dataclass
class LocaleFromHeaderMiddleware(BaseLocaleMiddleware):
    language_header: str = constants.LANGUAGE_HEADER

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger.debug("LocaleFromHeaderMiddleware::dispatch")

        header_locale = helpers.HeaderLocale(name=self.language_header, request=request)
        locale_code = header_locale.code or self.default_code

        if locale_code:
            logger.debug(f"LocaleFromHeaderMiddleware: set locale to: {locale_code}")
            i18n.set_locale(code=locale_code)

        response = await call_next(request)
        return response


# Backward compatibility
@dataclass
class LocaleMiddleware(LocaleFromHeaderMiddleware):
    default_code: str = constants.DEFAULT_LOCALE
