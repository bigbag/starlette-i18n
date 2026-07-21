# Examples

All examples use the compiled catalogs in `examples/locales` and select Russian with:

```console
curl -H 'Accept-Language: ru' http://127.0.0.1:8000/
```

## Run

```console
uv run --with uvicorn examples/basic_usage.py
uv run --with 'uvicorn[standard]' uvicorn examples.uvicorn_runner:app --reload
uv run --with gunicorn --with uvicorn gunicorn -c examples/gunicorn_conf.py examples.gunicorn_runner:app
```

`jinja_app.py` demonstrates the safe template pattern: it passes `request.state.locale.translate` as `_` while rendering instead of mutating a shared Jinja gettext environment.

## Update catalogs

Extract messages, update locale files, and compile them from the repository root:

```console
uv run pybabel extract -F examples/babel.conf -o examples/locales/messages.pot examples
uv run pybabel update -i examples/locales/messages.pot -d examples/locales -D messages
uv run pybabel compile -d examples/locales -D messages
```

Keep the compiled `.mo` files alongside their `.po` sources because the examples load the compiled catalogs at startup.
