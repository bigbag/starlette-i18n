from starlette_i18n import (
    Locale,
    LocaleMiddleware,
    TranslationCatalog,
    get_locale,
    gettext,
    gettext_lazy,
    ngettext,
)


def test_public_api_exports_are_importable() -> None:
    assert Locale is not None
    assert LocaleMiddleware is not None
    assert TranslationCatalog is not None
    assert get_locale is not None
    assert gettext is not None
    assert gettext_lazy is not None
    assert ngettext is not None


def test_release_version_is_3() -> None:
    import starlette_i18n

    assert starlette_i18n.__version__ == "3.0.0"
