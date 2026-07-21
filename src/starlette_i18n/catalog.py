"""Immutable gettext translation catalog loading."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from gettext import NullTranslations
from pathlib import Path
from types import MappingProxyType

from babel.support import Translations

from .locale import Locale, lookup_locale, normalize_locale


@dataclass(frozen=True, slots=True)
class TranslationCatalog:
    """Loaded gettext catalogs with deterministic locale lookup."""

    default_locale: str
    translations: Mapping[str, NullTranslations]

    @classmethod
    def load(cls, directory: str | Path, domain: str, default_locale: str) -> TranslationCatalog:
        """Load compiled gettext catalogs from ``directory``."""
        path = Path(directory)
        if not path.is_dir():
            raise FileNotFoundError(f"translation directory does not exist: {path}")

        catalogs: dict[str, NullTranslations] = {}
        for locale_path in sorted(child for child in path.iterdir() if child.is_dir()):
            normalized = normalize_locale(locale_path.name)
            message_file = locale_path / "LC_MESSAGES" / f"{domain}.mo"
            if normalized is None or not message_file.is_file():
                continue
            catalogs[normalized] = Translations.load(str(path), [locale_path.name], domain)

        normalized_default = normalize_locale(default_locale)
        if normalized_default is None or normalized_default not in catalogs:
            raise ValueError(f"default locale must have a loaded catalog: {default_locale}")
        return cls(normalized_default, MappingProxyType(catalogs))

    @property
    def supported_locales(self) -> frozenset[str]:
        """Return all normalized locale tags with a compiled catalog."""
        return frozenset(self.translations)

    def resolve(self, language_range: str) -> str | None:
        """Resolve a range to a loaded locale with RFC 4647 lookup."""
        return lookup_locale(language_range, set(self.translations))

    def get(self, code: str | None = None) -> Locale:
        """Return a matching locale or the configured default locale."""
        selected = self.resolve(code) if code is not None else self.default_locale
        selected = selected or self.default_locale
        return Locale(code=selected, translations=self.translations[selected])
