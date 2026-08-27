import pytest

from demo_ghc_app.config import ConfigError, load_config


def test_load_config_requires_endpoint(monkeypatch):
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_CHAT_MODEL", "chat")

    with pytest.raises(ConfigError, match="AZURE_OPENAI_ENDPOINT"):
        load_config()


def test_load_config_requires_chat_model_or_legacy_model(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.delenv("AZURE_OPENAI_CHAT_MODEL", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_MODEL", raising=False)

    with pytest.raises(ConfigError, match="AZURE_OPENAI_CHAT_MODEL or AZURE_OPENAI_MODEL"):
        load_config()


def test_load_config_uses_legacy_model_fallback(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", " https://example.openai.azure.com ")
    monkeypatch.delenv("AZURE_OPENAI_CHAT_MODEL", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_MODEL", " legacy-chat ")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", " key ")

    config = load_config()

    assert config.endpoint == "https://example.openai.azure.com"
    assert config.model == "legacy-chat"
    assert config.api_key == "key"


def test_load_config_treats_blank_values_as_unset(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", " ")
    monkeypatch.setenv("AZURE_OPENAI_CHAT_MODEL", "\t")

    with pytest.raises(ConfigError, match="AZURE_OPENAI_ENDPOINT"):
        load_config()


def test_load_config_uses_defaults_for_blank_optional_values(monkeypatch):
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_CHAT_MODEL", "chat")
    monkeypatch.setenv("AGENT_NAME", "")
    monkeypatch.setenv("AGENT_INSTRUCTIONS", " ")

    config = load_config()

    assert config.agent_name == "AzureOpenAIConsoleAgent"
    assert config.agent_instructions == "You are a helpful assistant."
