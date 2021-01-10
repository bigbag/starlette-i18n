import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from starlette_i18n import LocaleMiddleware, load_gettext_translations

from . import messages

BABEL_DOMAIN = "messages"
BABEL_LOCALES_PATH = "tests/locales"


@pytest.fixture()
def app():
    app_ = Starlette()
    app_.add_middleware(LocaleMiddleware, language_header="Accept-Language", default_code="en")
    load_gettext_translations(directory=BABEL_LOCALES_PATH, domain=BABEL_DOMAIN)

    @app_.route("/success/")
    def success(request):
        return PlainTextResponse(messages.SUCCESS, status_code=200)

    @app_.route("/error/")
    def error(request):
        return PlainTextResponse(messages.ERROR, status_code=500)

    return app_


@pytest.fixture
def client(app):
    return TestClient(app)
