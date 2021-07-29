import typing as t
from dataclasses import dataclass, field

from starlette.requests import Request

from .locale import gettext_translations


@dataclass
class LocaleInfo:
    code: str
    weight: float


def parse_language_header(language_header: str) -> t.List[LocaleInfo]:
    languages = language_header.split(",")

    locales: t.List[LocaleInfo] = []
    locales_code = set()
    for language in languages:
        language_info = language.split(";")

        if language_info[0] == language:
            # no q => q = 1
            locale_code = language.strip()
            weight = 1.0
        else:
            try:
                locale_code = language_info[0].strip()
                weight = float(language_info[1].split("=")[1])
            except (IndexError, ValueError):
                continue

        if not locale_code or locale_code in locales_code:
            continue

        locales.append(LocaleInfo(code=locale_code, weight=weight))
        locales_code.add(locale_code)

    return locales


@dataclass
class BaseLocaleCode:
    name: str
    request: Request
    supported_codes: t.Set[str] = field(init=False)

    def __post_init__(self):
        self.supported_codes = gettext_translations.supported_locales


@dataclass
class CookieLocale(BaseLocaleCode):
    @property
    def code(self) -> t.Optional[str]:
        locale_code = self.request.cookies.get(self.name)
        if locale_code in self.supported_codes:
            return str(locale_code)
        return None


@dataclass
class HeaderLocale(BaseLocaleCode):
    @property
    def code(self) -> t.Optional[str]:
        max_weight = 0.0
        locale_code = None

        language_header = self.request.headers.get(self.name)
        if not language_header:
            return locale_code

        for locale_info in parse_language_header(language_header):
            if locale_info.code in self.supported_codes and locale_info.weight > max_weight:
                max_weight = locale_info.weight
                locale_code = locale_info.code

        return str(locale_code) if locale_code else None
