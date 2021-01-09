from starlette_i18n import constants


def test_const_default_locale():
    assert constants.DEFAULT_LOCALE == "en"


def test_language_header():
    assert constants.LANGUAGE_HEADER == "Accept-Language"
