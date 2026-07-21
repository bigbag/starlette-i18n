import asyncio
from collections.abc import Callable

import httpx2 as httpx
import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from starlette_i18n import LocaleMiddleware, TranslationCatalog, gettext, gettext_lazy


@pytest.fixture
def app(app_factory: Callable[..., Starlette]) -> Starlette:
    application = app_factory()

    async def vary(request) -> PlainTextResponse:
        return PlainTextResponse("ok", headers={"Vary": "Origin"})

    async def vary_deduplicated(request) -> PlainTextResponse:
        return PlainTextResponse("ok", headers={"Vary": "Origin, cookie, ACCEPT-LANGUAGE"})

    async def lazy(request) -> PlainTextResponse:
        return PlainTextResponse(str(gettext_lazy("Success")))

    application.add_route("/vary", vary)
    application.add_route("/vary-deduplicated", vary_deduplicated)
    application.add_route("/lazy", lazy)
    return application


@pytest.fixture
def client(app: Starlette) -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("zh-CN,ru;q=0.5", "zh-CN:成功"),
        ("ru-RU", "ru:Успех"),
        ("ru;q=0.5,zh-CN;q=0.9", "zh-CN:成功"),
        ("ru;q=0,zh-CN;q=0.5", "zh-CN:成功"),
        ("en--US;q=bad,;q=1", "en:Success"),
        ("*,ru;q=0", "en:Success"),
    ],
)
def test_accept_language_negotiation(
    app_factory: Callable[..., Starlette], header: str, expected: str
) -> None:
    response = TestClient(app_factory()).get("/", headers={"Accept-Language": header})
    assert response.text == expected


def test_cookie_precedes_accept_language_and_sets_cache_vary(client: TestClient) -> None:
    client.cookies.set("locale", "ru")
    response = client.get("/", headers={"Accept-Language": "zh-CN"})
    assert response.text == "ru:Успех"
    assert response.headers["vary"] == "Cookie, Accept-Language"


def test_default_locale_is_used_without_selection_headers(
    app_factory: Callable[..., Starlette],
) -> None:
    response = TestClient(app_factory()).get("/")
    assert response.text == "en:Success"
    assert response.headers["content-language"] == "en"
    assert response.headers["vary"] == "Cookie, Accept-Language"


def test_disabling_cookie_selection_uses_accept_language(
    app_factory: Callable[..., Starlette],
) -> None:
    client = TestClient(app_factory(cookie_name=None))
    client.cookies.set("locale", "ru")
    response = client.get("/", headers={"Accept-Language": "zh-CN"})
    assert response.text == "zh-CN:成功"
    assert response.headers["vary"] == "Accept-Language"


def test_custom_language_header_is_used_and_varied(app_factory: Callable[..., Starlette]) -> None:
    response = TestClient(app_factory(cookie_name=None, language_header="X-Locale")).get(
        "/", headers={"X-Locale": "ru", "Accept-Language": "zh-CN"}
    )
    assert response.text == "ru:Успех"
    assert response.headers["vary"] == "X-Locale"


def test_invalid_cookie_falls_back_to_accept_language(
    app_factory: Callable[..., Starlette],
) -> None:
    client = TestClient(app_factory())
    client.cookies.set("locale", "not-a-locale")
    response = client.get("/", headers={"Accept-Language": "ru"})
    assert response.text == "ru:Успех"


def test_vary_header_is_merged(client: TestClient) -> None:
    response = client.get("/vary", headers={"Accept-Language": "ru"})
    assert response.headers["vary"] == "Origin, Cookie, Accept-Language"


def test_vary_header_is_not_duplicated_case_insensitively(client: TestClient) -> None:
    response = client.get("/vary-deduplicated")
    assert response.headers["vary"] == "Origin, cookie, ACCEPT-LANGUAGE"


def test_lazy_translation_is_request_local(client: TestClient) -> None:
    russian = client.get("/lazy", headers={"Accept-Language": "ru"})
    chinese = client.get("/lazy", headers={"Accept-Language": "zh-CN"})
    assert russian.text == "Успех"
    assert chinese.text == "成功"


def test_context_is_reset_after_an_error(catalog: TranslationCatalog) -> None:
    application = Starlette()
    application.add_middleware(LocaleMiddleware, catalog=catalog)

    async def boom(request):
        raise RuntimeError("boom")

    application.add_route("/", boom)
    response = TestClient(application, raise_server_exceptions=False).get(
        "/", headers={"Accept-Language": "ru"}
    )
    assert response.status_code == 500
    assert gettext("Success") == "Success"


@pytest.mark.anyio
async def test_non_http_scope_is_passed_through(catalog: TranslationCatalog) -> None:
    received_scopes: list[dict[str, object]] = []

    async def downstream(scope, receive, send) -> None:
        received_scopes.append(scope)

    async def receive() -> dict[str, object]:
        return {"type": "lifespan.startup"}

    async def send(message: dict[str, object]) -> None:
        return None

    middleware = LocaleMiddleware(downstream, catalog=catalog)
    scope: dict[str, object] = {"type": "lifespan", "asgi": {"version": "3.0"}}
    await middleware(scope, receive, send)
    assert received_scopes == [scope]


@pytest.mark.anyio
async def test_concurrent_requests_keep_locales_isolated(app: Starlette) -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        russian, chinese = await asyncio.gather(
            async_client.get("/", headers={"Accept-Language": "ru"}),
            async_client.get("/", headers={"Accept-Language": "zh-CN"}),
        )
    assert russian.text == "ru:Успех"
    assert chinese.text == "zh-CN:成功"
