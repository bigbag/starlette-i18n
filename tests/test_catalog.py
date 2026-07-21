import shutil
from pathlib import Path

import pytest

from starlette_i18n.catalog import TranslationCatalog


def test_load_discovers_normalized_catalog_locale_names(catalog: TranslationCatalog) -> None:
    assert catalog.supported_locales == frozenset({"en", "ru", "zh-CN"})


def test_get_returns_the_default_catalog_for_unsupported_locale(
    catalog: TranslationCatalog,
) -> None:
    assert catalog.get("es").code == "en"


def test_catalog_resolves_complex_and_less_specific_locale_tags(
    catalog: TranslationCatalog,
) -> None:
    assert catalog.get("zh-CN").code == "zh-CN"
    assert catalog.get("ru-RU").code == "ru"


def test_load_skips_invalid_and_uncompiled_catalog_directories(tmp_path: Path) -> None:
    source_locales = Path(__file__).parent / "locales"
    shutil.copytree(source_locales / "en", tmp_path / "en")
    (tmp_path / "invalid name" / "LC_MESSAGES").mkdir(parents=True)
    (tmp_path / "invalid name" / "LC_MESSAGES" / "messages.mo").touch()
    (tmp_path / "fr" / "LC_MESSAGES").mkdir(parents=True)
    (tmp_path / "fr" / "LC_MESSAGES" / "messages.po").touch()

    catalog = TranslationCatalog.load(tmp_path, domain="messages", default_locale="en")

    assert catalog.supported_locales == frozenset({"en"})


def test_load_rejects_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="translation directory"):
        TranslationCatalog.load(tmp_path / "missing", domain="messages", default_locale="en")


def test_load_rejects_a_default_without_a_catalog() -> None:
    with pytest.raises(ValueError, match="default locale"):
        TranslationCatalog.load(
            Path(__file__).parent / "locales", domain="messages", default_locale="fr"
        )
