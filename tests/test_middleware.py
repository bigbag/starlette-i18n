import pytest


def test_success_if_en_locale(client):
    response = client.get("/success/", headers={"Accept-Language": "en"})
    assert response.status_code == 200
    assert response.text == "Success"


def test_error_if_en_locale(client):
    response = client.get("/error/", headers={"Accept-Language": "en"})
    assert response.status_code == 500
    assert response.text == "Error"


def test_success_if_ru_locale(client):
    response = client.get("/success/", headers={"Accept-Language": "ru"})
    assert response.status_code == 200
    assert response.text == "Успех"


def test_error_if_ru_locale(client):
    response = client.get("/error/", headers={"Accept-Language": "ru"})
    assert response.status_code == 500
    assert response.text == "Ошибка"


def test_success_if_not_support_locale(client):
    response = client.get("/success/", headers={"Accept-Language": "es"})
    assert response.status_code == 200
    assert response.text == "Success"


@pytest.mark.parametrize(
    ("language", "success"),
    [("ru, fr;q=0.8", "Успех"), ("fr, it;q=0.7", "Success"), ("fr, en;q=0.8", "Success")],
)
def test_success_if_multiple_locales_in_header(client, language, success):
    response = client.get("/success/", headers={"Accept-Language": language})
    assert response.status_code == 200
    assert response.text == success


def test_success_if_empty_locale_header(client):
    response = client.get("/success/")
    assert response.status_code == 200
    assert response.text == "Success"
