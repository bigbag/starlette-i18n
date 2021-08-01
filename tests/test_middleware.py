class TestLocaleFromHeader:
    def test_success_if_default_locale(self, client):
        response = client.get("/locale/", headers={"Accept-Language": "en"})
        assert response.status_code == 200
        assert response.text == "en"

    def test_success_if_custom_locale(self, client):
        response = client.get("/locale/", headers={"Accept-Language": "ru"})
        assert response.status_code == 200
        assert response.text == "ru"

    def test_success_if_not_support_locale(self, client):
        response = client.get("/locale/", headers={"Accept-Language": "es"})
        assert response.status_code == 200
        assert response.text == "en"

    def test_success_if_empty_locale(self, client):
        response = client.get("/locale/")
        assert response.status_code == 200
        assert response.text == "en"

    def test_with_full_header(self, client):
        response = client.get("/locale/", headers={"Accept-Language": "es-BR,es;q=0.5,ru;q=0.4"})
        assert response.status_code == 200
        assert response.text == "ru"


class TestLocaleFromCookie:
    def test_success_if_default_locale(self, client):
        response = client.get("/locale/", cookies={"Language": "en"})
        assert response.status_code == 200
        assert response.text == "en"

    def test_success_if_custom_locale(self, client):
        response = client.get("/locale/", cookies={"Language": "ru"})
        assert response.status_code == 200
        assert response.text == "ru"

    def test_success_if_not_support_locale(self, client):
        response = client.get("/locale/", cookies={"Language": "es"})
        assert response.status_code == 200
        assert response.text == "en"

    def test_success_if_empty_locale(self, client):
        response = client.get("/locale/")
        assert response.status_code == 200
        assert response.text == "en"
