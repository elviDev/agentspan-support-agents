from agentspan.agents.testing import MockEvent, expect, mock_run
from agents.agent2 import SupportResponse, support_agent

REFUND_POLICY = "Source: support-policy.txt\nRefunds are processed with 5 business days."


def test_support_bot_refund_policy() -> None:
    result = mock_run(
        support_agent,
        "What is the refund policy?",
        events=[
            MockEvent.tool_call("search_knowledge_base", {"query": "refund policy"}),
            MockEvent.tool_result("search_knowledge_base", REFUND_POLICY),
            MockEvent.done(
                SupportResponse(
                    stage="answered",
                    successful=True,
                    approval_required=False,
                    message="Based on our policy, refunds are processed within 5 business days.",
                )
            ),
        ],
    )

    expect(result).completed().output_contains("refund").used_tool(
        "search_knowledge_base", args={"query": "refund policy"}
    ).no_errors()


if __name__ == "__main__":
    test_support_bot_refund_policy()
    print("Mock test passed.")