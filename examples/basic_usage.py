"""Run with: uv run --with uvicorn examples/basic_usage.py"""

import uvicorn

from examples.runner_app import app

if __name__ == "__main__":
    uvicorn.run(app)
