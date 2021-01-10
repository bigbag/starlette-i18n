from dataclasses import dataclass, field

from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from . import constants, i18n


@dataclass
class LocaleMiddleware(BaseHTTPMiddleware):
    app: ASGIApp
    language_header: str = constants.LANGUAGE_HEADER
    default_code: str = constants.DEFAULT_LOCALE
    dispatch_func: DispatchFunction = field(init=False)

    def __post_init__(self):
        self.dispatch_func = self.dispatch

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        locale_code = i18n._get_code_from_headers(
            headers=request.headers,
            language_header=self.language_header,
            default_code=self.default_code,
        )

        i18n.set_locale(code=locale_code)
        response = await call_next(request)
        return response
