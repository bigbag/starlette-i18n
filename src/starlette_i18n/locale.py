"""Locale values and RFC 4647 lookup matching."""

from __future__ import annotations

import re
from dataclasses import dataclass
from gettext import NullTranslations
from typing import Any

_LOCALE_RE = re.compile(r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")


def normalize_locale(value: str) -> str | None:
    """Return a normalized BCP 47-style locale tag, or ``None`` if invalid."""
    candidate = value.strip().replace("_", "-")
    if not _LOCALE_RE.fullmatch(candidate):
        return None

    subtags = candidate.split("-")
    normalized = [subtags[0].lower()]
    for subtag in subtags[1:]:
        if len(subtag) == 4 and subtag.isalpha():
            normalized.append(subtag.title())
        elif (len(subtag) == 2 and subtag.isalpha()) or (len(subtag) == 3 and subtag.isdigit()):
            normalized.append(subtag.upper())
        else:
            normalized.append(subtag.lower())
    return "-".join(normalized)


def lookup_locale(language_range: str, supported_locales: set[str]) -> str | None:
    """Return the RFC 4647 lookup result for one non-wildcard language range."""
    if language_range.strip() == "*":
        return None
    candidate = normalize_locale(language_range)
    if candidate is None:
        return None

    supported_by_casefold = {locale.casefold(): locale for locale in supported_locales}
    while candidate:
        match = supported_by_casefold.get(candidate.casefold())
        if match is not None:
            return match
        candidate = candidate.rpartition("-")[0]
    return None


@dataclass(frozen=True, slots=True)
class Locale:
    """A selected locale and its gettext translations."""

    code: str
    translations: NullTranslations | None

    @property
    def language(self) -> str:
        """Return the primary language subtag."""
        return self.code.split("-", maxsplit=1)[0]

    def translate(
        self,
        message: str,
        plural_message: str | None = None,
        number: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Translate and optionally interpolate a singular or plural message."""
        translations = self.translations or NullTranslations()
        if plural_message is not None and number is not None:
            translated = translations.ngettext(message, plural_message, number)
        else:
            translated = translations.gettext(message)
        return translated.format(**kwargs) if kwargs else translated
