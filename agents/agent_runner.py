import asyncio
import os
import sys
from agents import Agent, Runner
from dotenv import load_dotenv


history_tutor = Agent(
    name="History tutor",
    handoff_description="Specialist for history questions.",
    instructions="Answer history questions clearly and concisely.",
)

math_tutor = Agent(
    name="Math tutor",
    handoff_description="Specialist for math questions.",
    instructions="Explain math step by step and include worked examples.",
)

triage_agent = Agent(
    name="Homework triage",
    instructions="Route each homework question to the right specialist.",
    handoffs=[history_tutor, math_tutor],
)


async def main() -> None:
    load_dotenv()
    if os.getenv("OPENAI_API_KEY") == None:
        print('Missing openAI key')
        sys.exit()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY").encode("utf-8").decode(  "ascii", "ignore" )
    result = await Runner.run(
        triage_agent,
        "Who was the first president of the United States?",
    )
    print(result.final_output)
    print(result.last_agent.name)


if __name__ == "__main__":
    asyncio.run(main())