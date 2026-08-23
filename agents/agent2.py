import ast
import logging

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from agentspan.agents import (
    Agent,
    AgentRuntime,
    ConversationMemory,
    EventType,
    Guardrail,
    GuardrailResult,
    OnFail,
    Position,
    guardrail,
    start,
    tool,
)

load_dotenv(override=True)
logging.basicConfig(level=logging.WARNING, force=True)
logging.disable(logging.INFO)

MOCK_DB = {
    "orders": {"A100": {"status": "delivered", "total": 49.99}},
    "accounts": {"elvis@example.com": {"status": "active", "tier": "pro"}},
}

DOCS = {
    "refund policy": "Refunds are processed within 5 business days.",
    "shipping": "Standard shipping takes 3 to 7 business days.",
    "account": "Pro accounts include priority support.",
}


class SupportResponse(BaseModel):
    stage: str = Field(description="Stage like answered, refunded or rejected")
    successful: bool
    message: str


def read_cli_input(prompt: str) -> str | None:
    try:
        return input(prompt)
    except EOFError:
        return None


def get_response_message(output: SupportResponse | dict | str) -> str:
    if isinstance(output, SupportResponse):
        return output.message
    if isinstance(output, dict):
        if output.get("message"):
            return str(output["message"])
        if isinstance(output.get("result"), str):
            try:
                result = ast.literal_eval(output["result"])
            except (SyntaxError, ValueError):
                return output["result"]
            if isinstance(result, dict) and result.get("message"):
                return str(result["message"])
        return str(output.get("result") or output)
    return str(output)


@tool
def search_knowledge_base(query: str) -> str:
    """search support docs"""
    for title, body in DOCS.items():
        if title in query.lower():
            return body
    return "No matching support articles found."


@tool
def lookup_order(order_id: str) -> dict:
    """Lookup order in database by ID"""
    return MOCK_DB["orders"].get(order_id, {"error": "order not found"})


@tool(approval_required=True)
def process_refund(order_id: str, amount: float) -> str:
    """request a refund, pause for human approval think before you run this"""
    return f"refunded {amount:.2f} for order {order_id}"


@guardrail
def safe_support_request(prompt: str) -> GuardrailResult:
    """Block obvious prompt injection attempts"""
    blocked = ["ignore", "ignore previous", "system prompt", "jailbreak"]
    passed = not any(phrase in prompt.lower() for phrase in blocked)
    return GuardrailResult(passed=passed, message="Please ask a normal question, this is blocked.")


support_agent = Agent(
    name="support_agent",
    model="openai/gpt-4o-mini",
    instructions=(
        "You are a customer support agent. use the knowledge base first."
        "If the customer wants a refund: when you know the order ID, call "
        "lookup_order to get the amount. Before calling process_refund,"
        "write a shout plain-English sentence describing exactly what refund "
        "you are about to issue, for example: 'I am going to refund €50.50 "
        "for order A100.' Then call process_refund. The tool will pause for "
        "human approval automatically. If the order ID is missing, ask the "
        "customer for it. Always populate the message field with a clear reply."
    ),
    output_type=SupportResponse,
    tools=[search_knowledge_base, lookup_order, process_refund],
    memory=ConversationMemory(max_messages=50),
    guardrails=[Guardrail(safe_support_request, position=Position.INPUT, on_fail=OnFail.RAISE)],
    max_turns=10,
)


def run_interactive(prompt: str) -> None:
    with AgentRuntime() as runtime:
        handle = start(support_agent, prompt, runtime=runtime)
        stream = handle.stream()

        order_id, amount = None, None
        for event in stream:
            if event.type == EventType.TOOL_CALL and event.args:
                order_id = event.args.get("order_id") or order_id
            elif event.type == EventType.TOOL_RESULT and isinstance(event.result, dict):
                amount = event.result.get("total") or amount
            elif event.type == EventType.WAITING:
                refund_amount = f"${amount:.2f}" if isinstance(amount, int | float) else "the requested amount"
                print(f"\nApproval required: refund {refund_amount} for order {order_id or 'unknown'}")
                if read_cli_input("Press enter to review: ") is None:
                    handle.reject("approval input closed")
                    continue

                decision = read_cli_input("Approve? (y/n): ")
                if decision is None:
                    handle.reject("approval input closed")
                    continue

                decision = decision.lower().strip()
                if decision == "y":
                    handle.approve()
                else:
                    handle.reject("user rejected")

        result = stream.get_result()
        output = get_response_message(result.output)
        print(f"\n{output}\n")


def main() -> None:
    print("Support bot starting...")
    while True:
        raw_prompt = read_cli_input("You: ")
        if raw_prompt is None:
            print("\nNo input received; exiting.")
            break

        prompt = raw_prompt.strip()
        if prompt.lower() == "q":
            break
        if not prompt:
            continue
        run_interactive(prompt)


if __name__ == "__main__":
    main()
