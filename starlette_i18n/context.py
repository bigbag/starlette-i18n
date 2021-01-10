from contextvars import ContextVar
from typing import Any


class ContextStorage:
    DEFAULT_VALUE = ""
    CONTEXT_KEY_NAME = "default"

    def __init__(self):
        self._values: ContextVar = ContextVar(self.CONTEXT_KEY_NAME, default=self.DEFAULT_VALUE)
        self._token_id = None

    def get(self) -> Any:
        return self._values.get()

    def set(self, value: Any):
        self._token_id = self._values.set(value)
