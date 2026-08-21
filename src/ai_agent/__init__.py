import json
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from agentspan.agents import Agent, AgentRuntime, ConversationMemory, run, tool

load_dotenv()
logging.basicConfig(level=logging.WARNING)
logging.getLogger("agentspan").setLevel(logging.WARNING)
logging.getLogger("conductor").setLevel(logging.WARNING)

MEMORY_FILE = Path.cwd() / ".agent_memory.json"


def load_memory() -> ConversationMemory:
    memory = ConversationMemory(max_messages=50)
    if MEMORY_FILE.exists():
        try:
            memory.messages = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            memory.messages = []
    return memory


def save_memory(memory: ConversationMemory) -> None:
    MEMORY_FILE.write_text(
        json.dumps(memory.to_chat_messages(), indent=2),
        encoding="utf-8",
    )


@tool
def get_current_time(input: str) -> str:
    """Returns the current local date and time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


conversation_memory = load_memory()


assistant = Agent(
    name="personal_assistant",
    model="openai/gpt-4o-mini",
    instructions=(
        "You are a personal assistant that helps users with their daily tasks and provides information as needed."
        " Remember useful user details for future interactions."
    ),
    tools=[get_current_time],
    memory=conversation_memory,
)


def main() -> None:
    print("Starting the personal assistant agent...")

    with AgentRuntime() as runtime:
        while True:
            prompt = input("You: ").strip()
            if prompt.lower() == "q":
                break
            if not prompt:
                continue

            result = run(assistant, prompt, runtime=runtime)
            readable_result = (
                result.output.get("result") if isinstance(result.output, dict) else str(result.output)
            )
            conversation_memory.add_user_message(prompt)
            conversation_memory.add_assistant_message(readable_result)
            save_memory(conversation_memory)

            print(f"Assistant: {readable_result}")
