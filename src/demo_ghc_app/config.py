from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    endpoint: str
    model: str
    api_version: str | None
    api_key: str | None
    agent_name: str
    agent_instructions: str


class ConfigError(RuntimeError):
    """Raised when required application configuration is missing."""


def load_config() -> AppConfig:
    endpoint = _required_env("AZURE_OPENAI_ENDPOINT")
    model = _required_env("AZURE_OPENAI_CHAT_MODEL", fallback="AZURE_OPENAI_MODEL")

    return AppConfig(
        endpoint=endpoint,
        model=model,
        api_version=_optional_env("AZURE_OPENAI_API_VERSION"),
        api_key=_optional_env("AZURE_OPENAI_API_KEY"),
        agent_name=_optional_env("AGENT_NAME") or "AzureOpenAIConsoleAgent",
        agent_instructions=_optional_env("AGENT_INSTRUCTIONS")
        or "You are a helpful assistant.",
    )


def _required_env(name: str, *, fallback: str | None = None) -> str:
    value = _optional_env(name)
    if value:
        return value

    if fallback:
        value = _optional_env(fallback)
        if value:
            return value
        raise ConfigError(f"Set {name} or {fallback} in your environment or .env file.")

    raise ConfigError(f"Set {name} in your environment or .env file.")


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None

    value = value.strip()
    return value or None
