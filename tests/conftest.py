import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from starlette_i18n import LocaleMiddleware, load_gettext_translations

from . import constants, messages


@pytest.fixture()
def load_translations():
    load_gettext_translations(directory=constants.BABEL_LOCALES_PATH, domain=constants.BABEL_DOMAIN)


@pytest.fixture()
def app(load_translations):
    app_ = Starlette()
    app_.add_middleware(LocaleMiddleware, language_header="Accept-Language", default_code="en")

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
