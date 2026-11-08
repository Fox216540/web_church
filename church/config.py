"""Environment and Docker-secret helpers shared by all runtime processes."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


# Load local development values once. Docker-provided environment variables keep
# precedence because python-dotenv does not override existing values by default.
load_dotenv()


def get_env(name: str, default: str | None = None) -> str | None:
    """Read an environment variable, preferring its Docker ``*_FILE`` form."""
    file_name = os.environ.get(f"{name}_FILE")
    if file_name:
        try:
            return Path(file_name).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise RuntimeError(f"Unable to read secret file for {name}") from exc
    return os.environ.get(name, default)


def require_env(name: str) -> str:
    value = get_env(name)
    if not value:
        raise RuntimeError(f"{name} must be configured")
    return value


def get_bool(name: str, default: bool = False) -> bool:
    value = get_env(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
