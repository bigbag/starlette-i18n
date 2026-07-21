"""Pure ASGI locale negotiation middleware."""

from __future__ import annotations

from collections.abc import Iterable

from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .catalog import TranslationCatalog
from .context import configure_default_locale, reset_locale, set_locale
from .locale import Locale


def parse_accept_language(value: str) -> list[tuple[str, float, int]]:
    """Parse valid non-zero language ranges sorted by quality then request order."""
    parsed: list[tuple[str, float, int]] = []
    for position, member in enumerate(value.split(",")):
        parts = [part.strip() for part in member.split(";")]
        language_range = parts[0]
        quality = 1.0
        valid = bool(language_range)
        for parameter in parts[1:]:
            name, separator, raw_value = parameter.partition("=")
            if name.casefold() != "q":
                continue
            if not separator or not _is_quality_value(raw_value):
                valid = False
                break
            quality = float(raw_value)
        if valid and quality > 0.0:
            parsed.append((language_range, quality, position))
    return sorted(parsed, key=lambda item: (-item[1], item[2]))


def _is_quality_value(value: str) -> bool:
    integer, dot, fraction = value.strip().partition(".")
    if integer not in {"0", "1"} or (dot and (len(fraction) > 3 or not fraction.isdigit())):
        return False
    return integer == "0" or not fraction or set(fraction) == {"0"}


def _merge_vary(current: str | None, additions: Iterable[str]) -> str:
    values = (
        [] if current is None else [value.strip() for value in current.split(",") if value.strip()]
    )
    seen = {value.casefold() for value in values}
    for addition in additions:
        if addition.casefold() not in seen:
            values.append(addition)
            seen.add(addition.casefold())
    return ", ".join(values)


class LocaleMiddleware:
    """Select a locale per HTTP request and expose it safely to application code."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        catalog: TranslationCatalog,
        cookie_name: str | None = "locale",
        language_header: str = "Accept-Language",
    ) -> None:
        self.app = app
        self.catalog = catalog
        self.cookie_name = cookie_name
        self.language_header = language_header
        self._vary_headers = tuple(
            header
            for header in ("Cookie" if cookie_name is not None else None, language_header)
            if header
        )
        configure_default_locale(catalog.get())

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        locale = self._resolve_locale(request)
        request.state.locale = locale
        token = set_locale(locale)

        async def send_with_locale(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["content-language"] = locale.code
                headers["vary"] = _merge_vary(headers.get("vary"), self._vary_headers)
            await send(message)

        try:
            await self.app(scope, receive, send_with_locale)
        finally:
            reset_locale(token)

    def _resolve_locale(self, request: Request) -> Locale:
        if self.cookie_name is not None:
            cookie_value = request.cookies.get(self.cookie_name)
            if cookie_value is not None:
                selected = self.catalog.resolve(cookie_value)
                if selected is not None:
                    return self.catalog.get(selected)

        header_value = request.headers.get(self.language_header)
        if header_value is not None:
            wildcard = False
            for language_range, _, _ in parse_accept_language(header_value):
                if language_range == "*":
                    wildcard = True
                    continue
                selected = self.catalog.resolve(language_range)
                if selected is not None:
                    return self.catalog.get(selected)
            if wildcard:
                return self.catalog.get()

        return self.catalog.get()
