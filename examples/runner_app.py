"""Shared application used by the basic, Uvicorn, and Gunicorn examples."""

from pathlib import Path

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse

from starlette_i18n import LocaleMiddleware, TranslationCatalog, gettext

CATALOG = TranslationCatalog.load(Path(__file__).parent / "locales", "messages", "en")
app = Starlette()
app.add_middleware(LocaleMiddleware, catalog=CATALOG)


async def homepage(request) -> PlainTextResponse:
    return PlainTextResponse(gettext("Success"))


app.add_route("/", homepage)
