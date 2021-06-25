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


def test_success_if_ru_RU_locale(client):
    response = client.get("/success/", headers={"Accept-Language": "ru-RU"})
    assert response.status_code == 200
    assert response.text == "Успех"


def test_success_if_real_locale(client):
    response = client.get(
        "/success/", headers={"Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3"}
    )
    assert response.status_code == 200
    assert response.text == "Успех"


def test_success_if_no_exact_locale(client):
    response = client.get("/success/", headers={"Accept-Language": "ru-RU,en-US;q=0.5,en;q=0.3"})
    assert response.status_code == 200
    assert response.text == "Успех"


def test_success_if_extended_locale(client):
    response = client.get("/success/", headers={"Accept-Language": "uk-UA,en-US;q=0.5,en;q=0.3"})
    assert response.status_code == 200
    assert response.text == "Успіх"


def test_success_if_no_strict_extended_locale(client):
    response = client.get("/success/", headers={"Accept-Language": "uk,en-US;q=0.5,en;q=0.3"})
    assert response.status_code == 200
    assert response.text == "Успіх"


def test_success_if_only_prefix_locale(client):
    response = client.get("/success/", headers={"Accept-Language": "uk-FOO,en-US;q=0.5,en;q=0.3"})
    assert response.status_code == 200
    assert response.text == "Успіх"


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
