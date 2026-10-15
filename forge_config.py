"""Process and environment helpers shared by the app and the pipeline."""

import os
import sys

# Values copied straight from .env.example, plus obvious stand-ins.
# A copied example file must not count as a configured key.
_PLACEHOLDER_EXACT = {
    "your-anthropic-api-key-here",
    "your-google-maps-api-key-here",
    "your_api_key_here",
    "your-api-key-here",
    "your_api_key",
    "changeme",
    "placeholder",
    "todo",
    "xxx",
    "none",
    "null",
}


def key_is_configured(value: str | None) -> bool:
    """True only when a key looks like a real secret, not an example placeholder."""
    if value is None:
        return False
    text = value.strip().strip('"').strip("'")
    if not text:
        return False
    low = text.lower()
    if low in _PLACEHOLDER_EXACT:
        return False
    if "api-key-here" in low or "your-api-key" in low or low.startswith("your-"):
        return False
    if low.startswith("<") and low.endswith(">"):
        return False
    return True


def env_is_configured(name: str) -> bool:
    return key_is_configured(os.getenv(name))


def pipeline_argv() -> list[str]:
    """Launch the pipeline with the same interpreter that is running the app.

    The dashboard used to shell out to ``python``, which on a venv-based
    install is the system interpreter and does not see the app's dependencies.
    """
    root = os.path.dirname(os.path.abspath(__file__))
    return [sys.executable, os.path.join(root, "run_pipeline.py"), "--skip-scrape"]
