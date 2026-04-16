"""
state.py
--------
Defines the shared state that flows through the entire LangGraph agent.
Every node reads from and writes to this state object.
"""

from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class LeadInfo(TypedDict):
    """Holds the three fields we need to qualify a lead."""
    name: Optional[str]
    email: Optional[str]
    platform: Optional[str]   # e.g. YouTube, Instagram, TikTok
    lead_progress: int        # NEW: 0-3 (count of filled fields)


class AgentState(TypedDict):
    """
    The central state object for the AutoStream agent.

    Fields
    ------
    messages      : Full conversation history (auto-appended by LangGraph).
    intent        : Latest classified intent from the user.
    lead_info     : Accumulated lead data (name / email / platform).
    lead_captured : True once mock_lead_capture() has been called.
    rag_context   : Relevant excerpt(s) fetched from the knowledge base.
    lead_progress : NEW: Tracks extraction progress (0-3 fields filled).
    """
    messages: Annotated[List[BaseMessage], add_messages]
    intent: str          # "greeting" | "product_inquiry" | "high_intent" | "collecting_lead"
    lead_info: LeadInfo
    lead_captured: bool
    rag_context: str
    lead_progress: int
