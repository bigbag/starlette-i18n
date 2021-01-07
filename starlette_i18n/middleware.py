from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from . import constants, i18n


@dataclass
class LocaleMiddleware(BaseHTTPMiddleware):
    language_header: str = constants.LANGUAGE_HEADER
    default_code: str = constants.DEFAULT_LOCALE

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        locale_code = i18n._get_code_from_headers(
            headers=request.headers,
            language_header=self.language_header,
            default_code=self.default_code,
        )

        i18n.set_locale(code=locale_code)
        response = await call_next(request)
        return response
