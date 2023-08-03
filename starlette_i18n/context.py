import typing as t
from contextvars import ContextVar


class ContextStorage:
    DEFAULT_VALUE: t.Any = None
    CONTEXT_KEY_NAME: str = "default"

    def __init__(self):
        self._values: ContextVar = ContextVar(self.CONTEXT_KEY_NAME, default=self.DEFAULT_VALUE)
        self._token_id = None

    def get(self) -> t.Any:
        return self._values.get()

    def set(self, value: t.Any):
        self._token_id = self._values.set(value)
