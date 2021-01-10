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


def test_success_if_empty_locale_gheader(client):
    response = client.get("/success/")
    assert response.status_code == 200
    assert response.text == "Success"
