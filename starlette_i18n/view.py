import logging

from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from . import constants
from .i18n import gettext_lazy as _
from .locale import gettext_translations

logger = logging.getLogger(__name__)


def SetLocale(language_cookie: str = constants.LANGUAGE_COOKIE, redirect: bool = True):
    """
    Creates a language cookie changer view which sets language cookie

    :param language_cookie: name of the language cookie, 'Language' by default
    :param redirect: whether to redirect when no explicit redirect_to is passed

    GET or POST parameters of the changer returned:
        - `locale` - name of the locale, exactly as returned by
          the gettext_translations.supported_locales
        - `redirect_to` - whether and where to redirect. If
          `redirect` is True, default is a referer page, or
          root '/', if the referer is not set

    Use the created language changer as a view (route) callable together
    with the LocaleFromCookieMiddleware like:
    ```
    app.add_middleware(LocaleFromCookieMiddleware, language_cookie="Language")
    ...
    app.add_route(
        "/lang/",
        route=view.SetLocale(language_cookie="Language", redirect=False),
        methods=["GET", "POST"]
    )
    ```

    or

    ```
    app = Starlette(
        middleware=[
            Middleware(middleware.LocaleFromCookieMiddleware, language_cookie="Language"),
            ...
        ]
        routes=[
            ...
            Route(
                "/lang/",
                route=view.SetLocale(language_cookie="Language", redirect=True),
                methods=["GET", "POST"]
            )
        ]
    )
    ```

    Notice, that the `language_cookie` parameter should be the same.
    """

    async def set_locale(request: Request) -> Response:
        logger.debug("SetLocale::set_locale")
        redirect_to = None
        if redirect:
            redirect_to = request.headers.get("referer", "/")
        if request.method.lower() == "get":
            locale_code = request.query_params.get("locale")
            redirect_to = request.query_params.get("redirect_to", redirect_to)
        elif request.method.lower() == "post":
            form = await request.form()
            locale_code = form.get("locale")
            redirect_to = form.get("redirect_to", redirect_to)
        else:
            return Response(_("Method is not appropriate: %s") % request.method, status_code=400)

        if not redirect_to:
            ret = Response(status_code=201)
        else:
            ret = RedirectResponse(redirect_to)

        if locale_code in gettext_translations.supported_locales:
            logger.debug("SetLocale::set_locale: %s=%s", language_cookie, locale_code)
            ret.set_cookie(language_cookie, locale_code)
        return ret

    return set_locale
