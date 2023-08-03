from __future__ import annotations

import logging
import os
import typing as t
from dataclasses import dataclass

from babel.core import Locale as OriginLocale
from babel.support import NullTranslations, Translations

from . import constants

logger = logging.getLogger(__name__)


class _GettextTranslations:
    _translations: t.Dict[str, NullTranslations] = {}
    _default_locale: str = constants.DEFAULT_LOCALE
    _supported_locales: t.Set[str] = set()

    @property
    def translations(self) -> t.Dict[str, NullTranslations]:
        return self._translations

    @property
    def supported_locales(self) -> t.Set[str]:
        return self._supported_locales

    @property
    def default_locale(self) -> str:
        return self._default_locale

    def load_translations(self, directory: str, domain: str) -> None:
        for lang in os.listdir(directory):
            if os.path.isfile(os.path.join(directory, lang)):
                continue

            try:
                translation = Translations.load(directory, [lang], domain)
                if lang in self._translations:
                    self._translations[lang].merge(translation)  # type: ignore
                else:
                    self._translations[lang] = translation
            except Exception as e:
                logger.error("Cannot load translation for '%s': %s", lang, str(e))
                continue

        self._supported_locales = set(self._translations.keys())
        self._supported_locales.add(self.default_locale)

        logger.info("Supported locales: %s", sorted(self._supported_locales))


gettext_translations = _GettextTranslations()


@dataclass
class Locale:
    language: str
    translations: NullTranslations
    territory: t.Optional[str] = None
    script: t.Optional[str] = None
    variant: t.Optional[str] = None
    modifier: t.Optional[str] = None

    @classmethod
    def get(cls, code: str) -> "Locale":
        if code not in gettext_translations.supported_locales:
            code = gettext_translations.default_locale

        locale = OriginLocale.parse(code)
        return cls(
            language=locale.language,
            translations=gettext_translations.translations.get(code, NullTranslations()),
            territory=locale.territory,
            script=locale.script,
            variant=locale.variant,
            modifier=locale.modifier,
        )

    def translate(
        self,
        message: str,
        plural_message: t.Optional[str] = None,
        count: t.Optional[int] = None,
        **kwargs: str,
    ) -> str:
        if plural_message is not None and count is not None:
            message = self.translations.ungettext(message, plural_message, count)
        else:
            message = self.translations.ugettext(message)

        return message.format(**kwargs) if len(kwargs) else message
