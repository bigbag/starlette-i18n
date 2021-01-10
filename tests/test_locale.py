from pathlib import Path

import mock

from starlette_i18n.i18n import get_locale
from starlette_i18n.locale import gettext_translations

from . import constants

TESTS_DIR = Path(__file__).parent
LOCALE_DIRECTORY = TESTS_DIR / "locales"


@mock.patch("starlette_i18n.locale.Translations.load")
def test_locale_load_file_count(mock_translations_load):
    gettext_translations.load_translations(LOCALE_DIRECTORY, constants.BABEL_DOMAIN)
    assert mock_translations_load.call_count == 2


@mock.patch("starlette_i18n.locale.Translations.load")
def test_locale_load_file_except(mock_translations_load):
    gettext_translations._translations = {}
    mock_translations_load.side_effect = ValueError("something wrong")

    gettext_translations.load_translations(LOCALE_DIRECTORY, constants.BABEL_DOMAIN)
    assert len(gettext_translations.supported_locales) == 1


def test_locale_except():
    locale = get_locale()
    assert locale.translate("test", plural_message="test", count=1) == "test"
    assert locale.translate("test", plural_message="test", count=2) == "test"
