from starlette.testclient import TestClient

from examples.jinja_app import app as jinja_app
from examples.runner_app import app


def test_runner_example_negotiates_russian() -> None:
    response = TestClient(app).get("/", headers={"Accept-Language": "ru"})
    assert response.status_code == 200
    assert response.text == "Успех"


def test_runner_example_uses_default_locale_without_a_header() -> None:
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert response.text == "Success"


def test_jinja_example_negotiates_a_complex_locale() -> None:
    response = TestClient(jinja_app).get("/", headers={"Accept-Language": "ru-RU"})
    assert response.status_code == 200
    assert "Успех" in response.text
