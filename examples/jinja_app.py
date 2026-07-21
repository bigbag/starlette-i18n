"""Jinja example that passes a request-local translator to every render."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.applications import Starlette
from starlette.responses import HTMLResponse

from starlette_i18n import LocaleMiddleware, TranslationCatalog

CATALOG = TranslationCatalog.load(Path(__file__).parent / "locales", "messages", "en")
TEMPLATES = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)
app = Starlette()
app.add_middleware(LocaleMiddleware, catalog=CATALOG)


async def homepage(request) -> HTMLResponse:
    template = TEMPLATES.get_template("index.html")
    return HTMLResponse(template.render(request=request, _=request.state.locale.translate))


app.add_route("/", homepage)
