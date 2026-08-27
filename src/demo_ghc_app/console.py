from __future__ import annotations

import asyncio
import sys

from dotenv import load_dotenv

from demo_ghc_app.config import AppConfig, ConfigError, load_config

EXIT_COMMANDS = {"exit", "quit", "q"}


def main() -> None:
    load_dotenv()
    try:
        asyncio.run(run_console())
    except KeyboardInterrupt:
        print("\nExiting.")
    except ConfigError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        raise SystemExit(2) from error


async def run_console() -> None:
    config = load_config()
    agent = _create_agent(config)

    print("Azure OpenAI Agent Console")
    print("Type a message, or type 'exit' to quit.")

    while True:
        try:
            prompt = input("You> ").strip()
        except EOFError:
            print()
            return

        if not prompt:
            continue

        if prompt.lower() in EXIT_COMMANDS:
            return

        result = await agent.run(prompt)
        print(f"Agent> {result}")


def _create_agent(config: AppConfig):
    from agent_framework.openai import OpenAIChatClient

    client_args: dict[str, object] = {
        "model": config.model,
        "azure_endpoint": config.endpoint,
    }

    if config.api_version:
        client_args["api_version"] = config.api_version

    if config.api_key:
        client_args["api_key"] = config.api_key
    else:
        from azure.identity import AzureCliCredential

        client_args["credential"] = AzureCliCredential()

    return OpenAIChatClient(**client_args).as_agent(
        name=config.agent_name,
        instructions=config.agent_instructions,
    )


if __name__ == "__main__":
    main()
