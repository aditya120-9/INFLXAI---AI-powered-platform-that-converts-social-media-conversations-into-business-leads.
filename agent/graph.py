from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    classify_intent_node,
    retrieve_context_node,
    update_lead_info_node,
    capture_lead_node,
    generate_response_node,
)


def route_after_classification(state: AgentState) -> str:
    intent = state.get("intent", "product_inquiry")

    if intent == "greeting":
        return "generate_response"

    if intent == "product_inquiry":
        return "retrieve_context"

    if intent in {"high_intent", "collecting_lead"}:
        return "update_lead_info"

    return "generate_response"


def route_after_lead_update(state: AgentState) -> str:
    lead = state.get("lead_info") or {}
    lead_captured = state.get("lead_captured", False)

    required = ("name", "email", "platform")
    all_present = all(lead.get(field) for field in required)

    if all_present and not lead_captured:
        return "capture_lead"

    return "generate_response"


builder = StateGraph(AgentState)

builder.add_node("classify_intent", classify_intent_node)
builder.add_node("retrieve_context", retrieve_context_node)
builder.add_node("update_lead_info", update_lead_info_node)
builder.add_node("capture_lead", capture_lead_node)
builder.add_node("generate_response", generate_response_node)

builder.set_entry_point("classify_intent")

builder.add_conditional_edges(
    "classify_intent",
    route_after_classification,
    {
        "retrieve_context": "retrieve_context",
        "update_lead_info": "update_lead_info",
        "generate_response": "generate_response",
    },
)

builder.add_edge("retrieve_context", "generate_response")

builder.add_conditional_edges(
    "update_lead_info",
    route_after_lead_update,
    {
        "capture_lead": "capture_lead",
        "generate_response": "generate_response",
    },
)

builder.add_edge("capture_lead", "generate_response")
builder.add_edge("generate_response", END)

compiled_graph = builder.compile()