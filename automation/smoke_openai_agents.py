from agents import Agent


def main() -> None:
    agent = Agent(
        name="Local smoke test",
        instructions="Reply briefly.",
    )
    print(f"OpenAI Agents SDK import ok: {agent.name}")


if __name__ == "__main__":
    main()
