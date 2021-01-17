starlette-i18n
=======================================================================

.. image:: https://github.com/bigbag/starlette-i18n/workflows/CI/badge.svg
   :target: https://github.com/bigbag/starlette-i18n/actions?query=workflow%3ACI
.. image:: https://img.shields.io/pypi/v/starlette-i18n.svg
   :target: https://pypi.python.org/pypi/starlette-i18n


**starlette-i18n** is a localisation helper for starlette.


Installation
------------
starlette-i18n is available on PyPI.
Use pip to install:

    $ pip install starlette-i18n

Basic Usage
-----------

.. code:: python

    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import PlainTextResponse

    from starlette_i18n import (
        DEFAULT_LOCALE,
        LANGUAGE_HEADER,
        LocaleMiddleware,
        load_gettext_translations,
    )

    BABEL_DOMAIN = "messages"
    BABEL_LOCALES_PATH = "locales"


    def init_app():
        load_gettext_translations(directory=BABEL_LOCALES_PATH, domain=BABEL_DOMAIN)

        app_ = Starlette()
        app_.add_middleware(
            LocaleMiddleware, language_header=LANGUAGE_HEADER, default_code=DEFAULT_LOCALE
        )

        @app_.route("/")
        def success(request):
            return PlainTextResponse("OK", status_code=200)

        return app_


    app = init_app()

    if __name__ == "__main__":
        uvicorn.run(app=app)


License
-------

starlette-i18n is developed and distributed under the Apache 2.0 license.