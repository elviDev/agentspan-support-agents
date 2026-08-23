# AI Agent Examples

Lightweight command-line AI agents built with Agentspan.

## Features

- Agent 1: personal assistant with local time tool support
- Agent 2: customer support agent with RAG-style document lookup, input guardrails, and human-in-the-loop refund approval
- Agentspan `AgentRuntime` integration
- Conversation memory support
- Environment variables loaded from `.env`

## Agents

### Agent 1: Personal Assistant

Agent 1 is the default package entry point. It can answer everyday questions, call a local time tool, and keep recent conversation context between runs using local JSON-backed memory.

### Agent 2: Support Agent

Agent 2 is a customer support workflow that demonstrates three common agent patterns:

- RAG-style retrieval: `search_knowledge_base` searches local support docs for refund, shipping, and account answers.
- Guardrails: `safe_support_request` blocks obvious prompt-injection attempts before the request reaches the agent.
- Human-in-the-loop approval: `process_refund` requires approval before a refund tool call can complete.

Agent 2 also includes fixes for terminal stability:

- Handles closed input streams without crashing with `EOFError`.
- Handles structured output returned as either a Pydantic model, dictionary, or string.
- Safely rejects refund approval if the terminal input closes during review.

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

Run Agent 1:

```bash
uv run ai-agent
```

Run Agent 2:

```bash
uv run python agents/agent2.py
```

Type `q` to exit.

## Memory

The assistant stores recent conversation turns in `.agent_memory.json`. This local file lets it remember details, such as your name, after restarting the script. The memory file is ignored by Git so personal conversation history is not pushed to GitHub.
