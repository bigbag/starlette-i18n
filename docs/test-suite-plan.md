# Public API Test Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the tests around the supported catalog, translation, and ASGI middleware contract, including main configuration and error-adjacent request cases.

**Architecture:** Use Starlette applications and `TestClient`/`httpx2.AsyncClient` to assert observable request and response behavior. Retain focused catalog tests and use a small shared `app_factory` fixture to express middleware configurations without testing private parsing helpers. Remove source-text assertions because they do not protect the published runtime contract.

**Tech Stack:** Python 3.11+, pytest, Starlette 1.3, httpx2, Babel gettext catalogs.

---

## File structure

- Create: `tests/conftest.py` — shared compiled catalog and configurable Starlette application fixtures.
- Modify: `tests/test_catalog.py` — public catalog loading, resolution, and startup failures.
- Modify: `tests/test_translation.py` — exported translation helper and lazy-proxy behavior.
- Modify: `tests/test_middleware.py` — request negotiation, headers, configuration, concurrency, failures, and non-HTTP ASGI behavior.
- Modify: `tests/test_examples.py` — example response smoke tests.
- Delete: `tests/test_locale.py` — private normalization and lookup tests.
- Delete: `tests/test_project_files.py` — brittle assertions on repository text rather than behavior.

### Task 1: Add shared public test fixtures

**Files:**
- Create: `tests/conftest.py`
- Modify: `tests/test_catalog.py`
- Modify: `tests/test_translation.py`
- Modify: `tests/test_middleware.py`

- [ ] **Step 1: Write the shared fixture module**

```python
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
```

- [ ] **Step 2: Update test signatures to use `catalog` instead of module-level catalog construction**

Replace `CATALOG = TranslationCatalog.load(...)` and its module-level `configure_default_locale(CATALOG.get())` call with the `configured_catalog` fixture in `tests/test_translation.py`. Replace the `LOCALES` module constant in `tests/test_catalog.py` with `Path(__file__).parent / "locales"` inside each test. Keep existing assertions unchanged in this step.

- [ ] **Step 3: Run focused collection**

Run: `uv run pytest --collect-only -q`

Expected: all existing tests collect without import-time catalog construction.

- [ ] **Step 4: Commit the fixture migration**

```bash
git add tests/conftest.py tests/test_catalog.py tests/test_translation.py tests/test_middleware.py
git commit -m "test: add shared locale fixtures"
```

### Task 2: Cover the catalog and exported translation contract

**Files:**
- Modify: `tests/test_catalog.py`
- Modify: `tests/test_translation.py`
- Modify: `tests/test_public_api.py`

- [ ] **Step 1: Replace private locale-unit tests with catalog behavior**

Delete `tests/test_locale.py`, which imports `normalize_locale` and `lookup_locale` directly. Add this public catalog-resolution test to `tests/test_catalog.py`:

```python
def test_catalog_resolves_complex_and_less_specific_locale_tags(catalog: TranslationCatalog) -> None:
    assert catalog.get("zh-CN").code == "zh-CN"
    assert catalog.get("ru-RU").code == "ru"
```

- [ ] **Step 2: Add a skipped-directory startup test**

Add `import shutil` and the following test to `tests/test_catalog.py`:

```python
def test_load_skips_invalid_and_uncompiled_catalog_directories(tmp_path: Path) -> None:
    source_locales = Path(__file__).parent / "locales"
    shutil.copytree(source_locales / "en", tmp_path / "en")
    (tmp_path / "invalid name" / "LC_MESSAGES").mkdir(parents=True)
    (tmp_path / "invalid name" / "LC_MESSAGES" / "messages.mo").touch()
    (tmp_path / "fr" / "LC_MESSAGES").mkdir(parents=True)
    (tmp_path / "fr" / "LC_MESSAGES" / "messages.po").touch()

    catalog = TranslationCatalog.load(tmp_path, domain="messages", default_locale="en")

    assert catalog.supported_locales == frozenset({"en"})
```

This verifies malformed and uncompiled directories never become selectable through the public loader.

- [ ] **Step 3: Add a failing lazy-translation test**

```python
def test_gettext_lazy_uses_the_locale_at_evaluation_time(catalog: TranslationCatalog) -> None:
    lazy_success = gettext_lazy("Success")
    token = set_locale(catalog.get("ru"))
    try:
        assert str(lazy_success) == "Успех"
    finally:
        reset_locale(token)
```

Run: `uv run pytest tests/test_translation.py::test_gettext_lazy_uses_the_locale_at_evaluation_time -q`

Expected: FAIL until `gettext_lazy` is imported into the test module.

- [ ] **Step 4: Import `gettext_lazy` and verify the focused tests pass**

```python
from starlette_i18n.translation import gettext, gettext_lazy, ngettext
```

Run: `uv run pytest tests/test_catalog.py tests/test_translation.py tests/test_public_api.py -q`

Expected: PASS.

- [ ] **Step 5: Commit catalog and helper coverage**

```bash
git add tests/test_catalog.py tests/test_translation.py tests/test_public_api.py
git rm tests/test_locale.py
git commit -m "test: cover catalog and translation contracts"
```

### Task 3: Add the HTTP negotiation and configuration matrix

**Files:**
- Modify: `tests/test_middleware.py`

- [ ] **Step 1: Add a parametrized public header-negotiation test**

```python
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
def test_accept_language_negotiation(app_factory, header: str, expected: str) -> None:
    response = TestClient(app_factory()).get("/", headers={"Accept-Language": header})
    assert response.text == expected
```

- [ ] **Step 2: Run the new negotiation test**

Run: `uv run pytest tests/test_middleware.py::test_accept_language_negotiation -q`

Expected: PASS.

- [ ] **Step 3: Add tests for no selectors, cookie precedence, and custom header configuration**

```python
def test_default_locale_is_used_without_selection_headers(app_factory) -> None:
    response = TestClient(app_factory()).get("/")
    assert response.text == "en:Success"
    assert response.headers["content-language"] == "en"


def test_disabling_cookie_selection_uses_accept_language(app_factory) -> None:
    client = TestClient(app_factory(cookie_name=None))
    client.cookies.set("locale", "ru")
    response = client.get("/", headers={"Accept-Language": "zh-CN"})
    assert response.text == "zh-CN:成功"
    assert response.headers["vary"] == "Accept-Language"


def test_custom_language_header_is_used_and_varied(app_factory) -> None:
    response = TestClient(app_factory(cookie_name=None, language_header="X-Locale")).get(
        "/", headers={"X-Locale": "ru", "Accept-Language": "zh-CN"}
    )
    assert response.text == "ru:Успех"
    assert response.headers["vary"] == "X-Locale"
```

- [ ] **Step 4: Add an invalid-cookie fallback test**

```python
def test_invalid_cookie_falls_back_to_accept_language(app_factory) -> None:
    client = TestClient(app_factory())
    client.cookies.set("locale", "not-a-locale")
    response = client.get("/", headers={"Accept-Language": "ru"})
    assert response.text == "ru:Успех"
```

- [ ] **Step 5: Run the middleware module**

Run: `uv run pytest tests/test_middleware.py -q`

Expected: PASS.

- [ ] **Step 6: Commit negotiation coverage**

```bash
git add tests/test_middleware.py
git commit -m "test: cover locale selection configurations"
```

### Task 4: Cover the remaining observable ASGI contract

**Files:**
- Modify: `tests/test_middleware.py`

- [ ] **Step 1: Add a response-header de-duplication test**

Create a route returning `headers={"Vary": "Origin, cookie, ACCEPT-LANGUAGE"}` and assert the response header is unchanged except that no duplicate `Cookie` or `Accept-Language` entry is added. The exact assertion is:

```python
assert response.headers["vary"] == "Origin, cookie, ACCEPT-LANGUAGE"
```

- [ ] **Step 2: Add a request-local lazy helper endpoint test**

Add an endpoint that returns `str(gettext_lazy("Success"))`, then make Russian and Chinese requests to it:

```python
assert TestClient(app).get("/lazy", headers={"Accept-Language": "ru"}).text == "Успех"
assert TestClient(app).get("/lazy", headers={"Accept-Language": "zh-CN"}).text == "成功"
```

- [ ] **Step 3: Add non-HTTP pass-through coverage**

```python
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
```

Run: `uv run pytest tests/test_middleware.py::test_non_http_scope_is_passed_through -q`

Expected: PASS.

- [ ] **Step 4: Keep and verify the existing error-reset and concurrent-request tests**

Run: `uv run pytest tests/test_middleware.py -q`

Expected: PASS, including the 500 error reset and two simultaneous locale assertions.

- [ ] **Step 5: Commit ASGI contract coverage**

```bash
git add tests/test_middleware.py
git commit -m "test: cover ASGI response and lifecycle behavior"
```

### Task 5: Keep executable examples and remove text-coupled checks

**Files:**
- Modify: `tests/test_examples.py`
- Delete: `tests/test_project_files.py`

- [ ] **Step 1: Add default and complex-tag example assertions**

```python
def test_runner_example_uses_default_locale_without_a_header() -> None:
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.text == "Success"


def test_jinja_example_negotiates_a_complex_locale() -> None:
    response = TestClient(jinja_app).get("/", headers={"Accept-Language": "ru-RU"})
    assert response.status_code == 200
    assert "Успех" in response.text
```

- [ ] **Step 2: Delete repository-text tests**

```bash
rm tests/test_project_files.py
```

- [ ] **Step 3: Run the example tests**

Run: `uv run pytest tests/test_examples.py -q`

Expected: PASS.

- [ ] **Step 4: Commit the behavior-only cleanup**

```bash
git add tests/test_examples.py
git rm tests/test_project_files.py
git commit -m "test: retain executable example coverage"
```

### Task 6: Verify the full public-contract suite

**Files:**
- Verify: `tests/`

- [ ] **Step 1: Format and lint tests**

Run: `uv run ruff format tests && uv run ruff format --check tests && uv run ruff check tests`

Expected: formatter and Ruff report no violations.

- [ ] **Step 2: Run the full suite with coverage as information**

Run: `make test`

Expected: all tests pass. Do not add coverage exclusions or a coverage threshold merely to change the percentage.

- [ ] **Step 3: Run all project verification**

Run: `make lint && make build && uvx twine check dist/* && git diff --check`

Expected: every command succeeds and the working tree has only intended test changes.

- [ ] **Step 4: Commit final formatting only if needed**

```bash
git status --short
git add tests
git commit -m "style: format public contract tests"
```

Skip the commit when `git status --short` is empty.
