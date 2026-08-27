import time

from dotenv import load_dotenv

from agentspan.agents import Agent, AgentHandle, AgentRuntime, EventType, start, tool

load_dotenv(override=True)

MODE = "start" # start or resume
EXECUTION_ID = "" # paste the printed execution ID here for resume mode

@tool(timeout_seconds=30)
def slow_step(step: int) -> str:
    """Run one slow workflow step."""
    time.sleep(3)
    return f"Finished step {step}"

durable_agent = Agent(
    name="durable_demo_agent",
    model="openai/gpt-4o-mini",
    instructions=(
        "Run a 10-step workflow by calling slow_step once for each step, "
        "from 1 through 10, in order. Do not skip steps."
    ),
    tools=[slow_step],
    max_turns=20,
)

def stream_handle(handle: AgentHandle) -> None:
    print("Execution ID:", handle.execution_id)
    for event in handle.stream():
        print(event.type, getattr(event, "message", ""))
        if event.type == EventType.DONE:
            break

if __name__ == "__main__":
    with AgentRuntime() as runtime:
        if MODE == "start":
            handle = start(durable_agent, "Run the 10-step workflow.", runtime=runtime)
            stream_handle(handle)
        elif MODE == "resume":
            runtime.serve(durable_agent, blocking=False)
            handle = AgentHandle(execution_id=EXECUTION_ID, runtime=runtime)
            stream_handle(handle)
        else:
            raise ValueError(f"Unknown MODE: {MODE}")