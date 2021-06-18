# starlette-i18n application example

## Installation

Use pip to install:

    $ pip install -r requirements.txt

## Basic Usage

```bash
make run
```

```bash
curl http://127.0.0.1:8000/ --header 'accept-language: ru'

```

```html

<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Главная страница</title>
  </head>
  <body>
      <h1>Демо страница</h1>
      test
  </body>
</html>

```

```bash
curl http://127.0.0.1:8000/

```

```html
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Main page</title>
  </head>
  <body>
      <h1>Demo text</h1>
      test
  </body>
</html>

```