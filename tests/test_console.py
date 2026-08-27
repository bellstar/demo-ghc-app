import asyncio
import builtins
import sys
import types

import pytest

from demo_ghc_app.config import AppConfig
from demo_ghc_app import console


def _config(api_key=None):
    return AppConfig(
        endpoint="https://example.openai.azure.com",
        model="chat",
        api_version="2024-10-21",
        api_key=api_key,
        agent_name="test-agent",
        agent_instructions="test instructions",
    )


@pytest.mark.parametrize("command", ["exit", "quit", "q", " EXIT "])
def test_run_console_stops_on_exit_commands(monkeypatch, command, capsys):
    prompts = iter([command])
    monkeypatch.setattr(builtins, "input", lambda _: next(prompts))
    monkeypatch.setattr(console, "load_config", lambda: _config())
    agent = types.SimpleNamespace(run=_unexpected_run)
    monkeypatch.setattr(console, "_create_agent", lambda config: agent)

    asyncio.run(console.run_console())

    assert "Azure OpenAI Agent Console" in capsys.readouterr().out


def test_run_console_ignores_blank_input_and_prints_result(monkeypatch, capsys):
    prompts = iter(["", " hello ", "q"])
    calls = []

    async def run(prompt):
        calls.append(prompt)
        return "response"

    monkeypatch.setattr(builtins, "input", lambda _: next(prompts))
    monkeypatch.setattr(console, "load_config", lambda: _config())
    monkeypatch.setattr(console, "_create_agent", lambda config: types.SimpleNamespace(run=run))

    asyncio.run(console.run_console())

    output = capsys.readouterr().out
    assert calls == ["hello"]
    assert "Agent> response" in output


def test_run_console_returns_on_eof(monkeypatch, capsys):
    def input_with_eof(_):
        raise EOFError

    monkeypatch.setattr(builtins, "input", input_with_eof)
    monkeypatch.setattr(console, "load_config", lambda: _config())
    monkeypatch.setattr(console, "_create_agent", lambda config: types.SimpleNamespace(run=_unexpected_run))

    asyncio.run(console.run_console())

    assert capsys.readouterr().out.endswith("\n")


def test_run_console_propagates_api_failure(monkeypatch):
    async def run(_prompt):
        raise RuntimeError("API unavailable")

    monkeypatch.setattr(builtins, "input", lambda _: "hello")
    monkeypatch.setattr(console, "load_config", lambda: _config())
    monkeypatch.setattr(console, "_create_agent", lambda config: types.SimpleNamespace(run=run))

    with pytest.raises(RuntimeError, match="API unavailable"):
        asyncio.run(console.run_console())


def test_create_agent_uses_api_key(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, **kwargs):
            captured["client"] = kwargs

        def as_agent(self, **kwargs):
            captured["agent"] = kwargs
            return "agent"

    monkeypatch.setitem(sys.modules, "agent_framework", types.ModuleType("agent_framework"))
    openai = types.ModuleType("agent_framework.openai")
    openai.OpenAIChatClient = FakeClient
    monkeypatch.setitem(sys.modules, "agent_framework.openai", openai)

    result = console._create_agent(_config(api_key="secret"))

    assert result == "agent"
    assert captured["client"] == {
        "model": "chat",
        "azure_endpoint": "https://example.openai.azure.com",
        "api_version": "2024-10-21",
        "api_key": "secret",
    }
    assert captured["agent"] == {
        "name": "test-agent",
        "instructions": "test instructions",
    }


def test_create_agent_uses_azure_cli_credential_without_api_key(monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, **kwargs):
            captured["client"] = kwargs

        def as_agent(self, **kwargs):
            return kwargs

    class FakeCredential:
        pass

    monkeypatch.setitem(sys.modules, "agent_framework", types.ModuleType("agent_framework"))
    openai = types.ModuleType("agent_framework.openai")
    openai.OpenAIChatClient = FakeClient
    monkeypatch.setitem(sys.modules, "agent_framework.openai", openai)
    azure = types.ModuleType("azure")
    identity = types.ModuleType("azure.identity")
    identity.AzureCliCredential = FakeCredential
    monkeypatch.setitem(sys.modules, "azure", azure)
    monkeypatch.setitem(sys.modules, "azure.identity", identity)

    console._create_agent(_config())

    assert captured["client"]["credential"].__class__ is FakeCredential
    assert "api_key" not in captured["client"]


async def _unexpected_run(_prompt):
    raise AssertionError("agent.run should not be called")
