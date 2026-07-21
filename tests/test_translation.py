from starlette_i18n.catalog import TranslationCatalog
from starlette_i18n.context import get_locale, reset_locale, set_locale
from starlette_i18n.translation import gettext, gettext_lazy, ngettext


def test_context_token_restores_the_previous_locale(configured_catalog: TranslationCatalog) -> None:
    outer = set_locale(configured_catalog.get("en"))
    inner = set_locale(configured_catalog.get("ru"))
    reset_locale(inner)
    assert get_locale().code == "en"
    reset_locale(outer)
    assert get_locale().code == "en"


def test_gettext_uses_the_current_locale(configured_catalog: TranslationCatalog) -> None:
    token = set_locale(configured_catalog.get("ru"))
    try:
        assert gettext("Success") == "Успех"
    finally:
        reset_locale(token)


def test_ngettext_selects_a_plural_form(configured_catalog: TranslationCatalog) -> None:
    token = set_locale(configured_catalog.get("en"))
    try:
        assert ngettext("{count} item", "{count} items", 2, count=2) == "2 items"
    finally:
        reset_locale(token)


def test_gettext_lazy_uses_the_locale_at_evaluation_time(catalog: TranslationCatalog) -> None:
    lazy_success = gettext_lazy("Success")
    token = set_locale(catalog.get("ru"))
    try:
        assert str(lazy_success) == "Успех"
    finally:
        reset_locale(token)
