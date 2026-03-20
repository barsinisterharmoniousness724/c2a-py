from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    port: int = int(os.getenv("PORT", "3010"))
    cursor_chat_api: str = os.getenv("CURSOR_CHAT_API", "https://cursor.com/api/chat")
    cursor_model: str = os.getenv("CURSOR_MODEL", "claude-4-5")
    request_timeout: float = float(os.getenv("REQUEST_TIMEOUT", "90"))
    auth_tokens: tuple[str, ...] = os.getenv("AUTH_TOKEN", "sk-123456")
    sanitize_response: bool = _env_bool("SANITIZE_RESPONSE", True)
    tools_passthrough: bool = _env_bool("TOOLS_PASSTHROUGH", False)
    tools_disabled: bool = _env_bool("TOOLS_DISABLED", False)
    user_agent: str = os.getenv(
        "USER_AGENT",
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        ),
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
