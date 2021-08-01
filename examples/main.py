from jinja2 import Environment, FileSystemLoader
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import HTMLResponse
from starlette.routing import Route

from starlette_i18n import (
    LocaleDefaultMiddleware,
    LocaleFromCookieMiddleware,
    LocaleFromHeaderMiddleware,
    get_locale,
    load_gettext_translations,
)

BABEL_DOMAIN = "messages"
BABEL_LOCALES_PATH = "locales"


def get_jinja_environment() -> Environment:
    env = Environment(
        autoescape=True,
        loader=FileSystemLoader("templates"),
        extensions=["jinja2.ext.i18n"],
    )
    env.install_gettext_translations(get_locale().translations)  # type: ignore
    return env


async def mainpage(request):
    env = get_jinja_environment()
    html_template = env.get_template("index.html")
    return HTMLResponse(html_template.render(account="test"))


def init_app():
    load_gettext_translations(directory=BABEL_LOCALES_PATH, domain=BABEL_DOMAIN)

    return Starlette(
        middleware=[
            Middleware(LocaleFromHeaderMiddleware, language_header="Accept-Language"),
            Middleware(LocaleFromCookieMiddleware, language_cookie="Language"),
            Middleware(LocaleDefaultMiddleware, default_code="en"),
        ],
        routes=[
            Route("/", mainpage),
        ],
    )


app = init_app()
