from starlette_i18n import constants
from starlette_i18n import gettext_lazy as _
from starlette_i18n.i18n import _language_ctx, get_locale_code, set_locale
from starlette_i18n.locale import Locale


def test_ctx_locale():
    assert isinstance(_language_ctx.get(), Locale)


def test_ctx_locale_language():
    locale = _language_ctx.get()
    assert locale.language == constants.DEFAULT_LOCALE


def test_set_locale_if_support_locale(load_translations):
    set_locale("ru")
    assert get_locale_code() == "ru"


def test_set_locale_if_not_support_locale(load_translations):
    set_locale("uk")
    assert get_locale_code() == "en"


def test_make_lazy_gettext(load_translations):
    set_locale(code="en")
    assert _("Success") == "Success"

    set_locale(code="ru")
    assert _("Success") == "Успех"
    assert _(_("Success")) == "Успех"
