from collections.abc import Callable
from pathlib import Path

import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse

from starlette_i18n import LocaleMiddleware, TranslationCatalog, gettext


@pytest.fixture(scope="session")
def catalog() -> TranslationCatalog:
    return TranslationCatalog.load(Path(__file__).parent / "locales", "messages", "en")


@pytest.fixture
def configured_catalog(catalog: TranslationCatalog) -> TranslationCatalog:
    async def downstream(scope, receive, send) -> None:
        return None

    LocaleMiddleware(downstream, catalog=catalog)
    return catalog


@pytest.fixture
def app_factory(catalog: TranslationCatalog) -> Callable[..., Starlette]:
    def create(**middleware_options: str | None) -> Starlette:
        app = Starlette()
        app.add_middleware(LocaleMiddleware, catalog=catalog, **middleware_options)

        async def homepage(request) -> PlainTextResponse:
            return PlainTextResponse(f"{request.state.locale.code}:{gettext('Success')}")

        app.add_route("/", homepage)
        return app

    return create
