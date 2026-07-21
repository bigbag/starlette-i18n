"""Run with: uv run --with 'uvicorn[standard]' uvicorn examples.uvicorn_runner:app --reload"""

from examples.runner_app import app

__all__ = ["app"]
