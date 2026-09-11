# Agents

This project contains examples of AI agents, including a file manager agent in the `agents/` folder.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set `OPENAI_API_KEY` in `.env` before running an agent.

## File manager agent

`agents/file_manager.py` defines a file manager agent using the OpenAI Agents SDK. It provides three tools:

- `list_files(path)`: lists files and directories.
- `read_file(path)`: reads a UTF-8 text file.
- `edit_file(path, old_text, new_text)`: replaces matching text or creates a file when `old_text` is empty.

Run it from the project root with:

```bash
python agents/file_manager.py
```

The agent supports interactive requests such as listing directories, reading files, and editing files. Type `exit` or `quit` to stop.

## Other agents

- `agents/files_agent.py`: standalone conversational file assistant.
- `agents/agent_runner.py`: simple history and math tutor handoff example.