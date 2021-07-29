import pytest

from starlette_i18n.helpers import parse_language_header


def test_double_locale_code():
    locales_info = parse_language_header("en,en")
    assert len(locales_info) == 1

    locale_info = locales_info[0]
    assert locale_info.code == "en"
    assert locale_info.weight == 1.0


def test_with_single_locale():
    locales_info = parse_language_header("en")
    assert len(locales_info) == 1

    locale_info = locales_info[0]
    assert locale_info.code == "en"
    assert locale_info.weight == 1.0


@pytest.mark.parametrize(
    ("header"),
    ["dfdfd;", ";", ";=", ";34=", "", ","],
)
def test_with_not_correct_header(header):
    locales_info = parse_language_header(header)
    assert len(locales_info) == 0


def test_with_full_header():
    locales_info = parse_language_header("en-US,en;q=0.5,fr;q=0.4")
    assert len(locales_info) == 3

    locale_info = locales_info[0]
    assert locale_info.code == "en-US"
    assert locale_info.weight == 1.0

    locale_info = locales_info[1]
    assert locale_info.code == "en"
    assert locale_info.weight == 0.5

    locale_info = locales_info[2]
    assert locale_info.code == "fr"
    assert locale_info.weight == 0.4
