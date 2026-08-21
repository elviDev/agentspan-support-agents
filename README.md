# Personal Assistant Agent

A lightweight command-line AI assistant built with Agentspan. It can answer everyday questions, call a local time tool, and keep recent conversation context between runs using local JSON-backed memory.

## Features

- Interactive terminal chat loop
- Agentspan `AgentRuntime` integration
- Local time tool
- Conversation memory persisted in `.agent_memory.json`
- Environment variables loaded from `.env`

## Requirements

- Python 3.14+
- `uv`
- An API key/provider configuration supported by Agentspan in your local `.env`

## Setup

```bash
uv sync
```

Create a `.env` file with the credentials required by your model provider. The `.env` file is ignored by Git.

## Run

```bash
uv run ai-agent
```

Type `q` to exit.

## Memory

The assistant stores recent conversation turns in `.agent_memory.json`. This local file lets it remember details, such as your name, after restarting the script. The memory file is ignored by Git so personal conversation history is not pushed to GitHub.
