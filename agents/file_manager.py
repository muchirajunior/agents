import asyncio
import os
import sys
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

@function_tool
def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return f"File contents of {path}:\n{content}"

@function_tool
def list_files(path: str = '../..') -> str:
    if not os.path.exists(path):
        return f"Path not found: {path}"

    items = []
    for item in sorted(os.listdir(path)):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            items.append(f"[DIR]  {item}/")
        else:
            items.append(f"[FILE] {item}")

    if not items:
        return f"Empty directory: {path}"

    return f"Contents of {path}:\n" + "\n".join(items)

@function_tool
def edit_file(path: str, old_text: str, new_text: str) -> str:
    if os.path.exists(path) and old_text:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        if old_text not in content:
            return f"Text not found in file: {old_text}"

        content = content.replace(old_text, new_text)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully edited {path}"
    else:
        # Only create directory if path contains subdirectories
        dir_name = os.path.dirname(path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)

        return f"Successfully created {path}"



agent = Agent(
    name="File managers",
    instructions="You are file manager, you can read or list files as per tools provided",
    tools=[list_files,read_file, edit_file],
)


async def main() -> None:
    load_dotenv()
    if os.getenv("OPENAI_API_KEY") == None:
        print('Missing openAI key')
        sys.exit()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY").encode("utf-8").decode("ascii", "ignore")
    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print("\nAssistant: ", end="", flush=True)
            response = await Runner.run(agent, user_input, )
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print()
   


if __name__ == "__main__":
    asyncio.run(main())