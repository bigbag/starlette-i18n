import pytest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from starlette_i18n import middleware, view

from . import messages


@pytest.fixture()
def rich_app(load_translations):
    def success(request):
        return PlainTextResponse(messages.SUCCESS, status_code=200)

    app_ = Starlette(
        middleware=[
            Middleware(middleware.LocaleDefaultMiddleware, default_code="en"),
            Middleware(
                middleware.LocaleAutodetectMiddleware,
                language_header="Accept-Language",
                default_code=None,
            ),
            Middleware(middleware.LocaleFromCookieMiddleware, language_cookie="Language"),
        ],
        routes=[
            Route("/success/", endpoint=success),
        ],
    )
    return app_


def test_success_en_locale(rich_app):
    sclient = TestClient(rich_app)
    response = sclient.get("/success/")
    assert response.status_code == 200
    assert response.text == "Success"


def test_set_ru_locale(rich_app):
    rich_app.add_route("/lang/", route=view.SetLocale(language_cookie="Language", redirect=False))
    sclient = TestClient(rich_app)
    response = sclient.get("/lang/?locale=ru")
    assert response.status_code == 201
    response = sclient.get("/success/")
    assert response.status_code == 200
    assert response.text == "Успех"


def test_set_ru_post_locale(rich_app):
    rich_app.add_route(
        "/lang/",
        route=view.SetLocale(language_cookie="Language", redirect=False),
        methods=["GET", "POST"],
    )
    sclient = TestClient(rich_app)
    response = sclient.post("/lang/", data={"locale": "ru"})
    assert response.status_code == 201
    response = sclient.get("/success/")
    assert response.status_code == 200
    assert response.text == "Успех"


def test_set_locale_wrong_method(rich_app):
    rich_app.add_route(
        "/lang/",
        route=view.SetLocale(language_cookie="Language", redirect=False),
        methods=["GET", "POST", "PUT"],
    )
    sclient = TestClient(rich_app)
    response = sclient.put("/lang/", data={"locale": "ru"})
    assert response.status_code == 400


def test_set_ru_explicit_redirect_locale(rich_app):
    rich_app.add_route("/lang/", route=view.SetLocale(language_cookie="Language", redirect=False))
    sclient = TestClient(rich_app)
    response = sclient.get("/lang/?locale=ru&redirect_to=/success/")
    assert response.status_code == 200
    assert response.text == "Успех"


def test_set_ru_redirect_to_referer_locale(rich_app):
    rich_app.add_route("/lang/", route=view.SetLocale(language_cookie="Language", redirect=True))
    sclient = TestClient(rich_app)
    response = sclient.get("/lang/?locale=ru", headers={"referer": "/success/"})
    assert response.status_code == 200
    assert response.text == "Успех"


def test_set_ru_redirect_to_root_locale(rich_app):
    rich_app.add_route("/lang/", route=view.SetLocale(language_cookie="Language", redirect=True))
    sclient = TestClient(rich_app)
    response = sclient.get("/lang/?locale=ru", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/"
