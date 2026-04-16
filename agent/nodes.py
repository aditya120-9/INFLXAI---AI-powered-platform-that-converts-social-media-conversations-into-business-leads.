"""
nodes.py
--------
LangGraph node functions for the AutoStream agent.
"""

import json
import os
import re

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

from agent.state import AgentState
from agent.rag import (
    retrieve_context,
    get_full_kb,
    PRICING_KEYWORDS,
    POLICY_KEYWORDS,
    FEATURE_KEYWORDS,
)
from agent.tools import mock_lead_capture, extract_email_from_text


def _llm_to_text(resp) -> str:
    if resp is None:
        return ""
    if isinstance(resp, str):
        return resp

    if hasattr(resp, "content"):
        try:
            content = resp.content
            if isinstance(content, str):
                return content
            resp = content
        except Exception:
            return str(resp)

    if isinstance(resp, (list, tuple)):
        parts = []
        for item in resp:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if "text" in item:
                    parts.append(item.get("text") or "")
                elif "content" in item:
                    parts.append(item.get("content") or "")
                else:
                    parts.append(str(item))
            else:
                parts.append(str(item))
        return "\n".join([p for p in parts if p])

    if isinstance(resp, dict):
        for key in ("content", "text", "output"):
            if key in resp:
                value = resp[key]
                if isinstance(value, str):
                    return value
                if isinstance(value, (list, tuple)):
                    return "\n".join(str(x) for x in value)
        return json.dumps(resp)

    return str(resp)


def _get_llm(temperature: float = 0.3):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY environment variable is not set.")

    model = os.environ.get("GENAI_MODEL", "gemini-flash-latest").strip()

    temp_env = os.environ.get("GENAI_TEMPERATURE")
    if temp_env is not None:
        try:
            temperature = float(temp_env)
        except Exception:
            pass

    max_tokens_env = os.environ.get("GENAI_MAX_OUTPUT_TOKENS")
    try:
        max_output_tokens = int(max_tokens_env) if max_tokens_env is not None else 220
    except Exception:
        max_output_tokens = 220

    print(f"[autostream] Using model: {model}")

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        convert_system_message_to_human=True,
    )


_EXTRACT_PROMPT = """Extract structured data from the conversation below.
Return ONLY valid JSON with keys: name, email, platform.
Use null if not present.

Conversation:
{snippet}

JSON:"""

PLATFORMS = ["youtube", "yt", "instagram", "tiktok", "facebook", "linkedin", "twitter", "twitch", "snapchat"]


def _last_human_message(messages):
    for msg in reversed(messages or []):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


def _last_ai_message(messages):
    for msg in reversed(messages or []):
        if isinstance(msg, AIMessage):
            return msg.content if isinstance(msg.content, str) else str(msg.content)
    return ""


def classify_intent_node(state: AgentState) -> dict:
    messages = state.get("messages", [])
    if not messages:
        return {"intent": "greeting"}

    lead_info = state.get("lead_info") or {}
    lead_captured = state.get("lead_captured", False)

    latest = _last_human_message(messages).strip().lower()
    last_ai = _last_ai_message(messages).strip().lower()
    tokens = set(re.findall(r"\b\w+\b", latest))

    missing = [f for f in ("name", "email", "platform") if not lead_info.get(f)]

    # Strongest rule:
    # If the AI just asked for contact information OR we already have partial lead info,
    # stay in collecting_lead until all fields are filled.
    lead_prompt_markers = [
        "full name first",
        "best email address to reach you at",
        "which platform do you primarily create on",
    ]
    if not lead_captured and missing:
        if any(marker in last_ai for marker in lead_prompt_markers):
            return {"intent": "collecting_lead"}
        if any(lead_info.get(f) for f in ("name", "email", "platform")):
            return {"intent": "collecting_lead"}

    strong_high_intent_phrases = [
        "i want to sign up",
        "i want to subscribe",
        "i want to buy",
        "i want to purchase",
        "sign me up",
        "start a trial",
        "i want to try the pro plan",
        "buy pro plan",
        "i want to buy pro plan",
        "buy pro plan for youtube",
    ]

    question_phrases = [
        "tell me about",
        "tell me more about",
        "what is",
        "what are",
        "how much",
        "how does",
        "benefits of",
        "features of",
        "pricing",
        "price",
        "plans",
        "cost",
    ]

    if any(p in latest for p in strong_high_intent_phrases):
        return {"intent": "high_intent"}

    if (
        "?" in latest
        or any(q in latest for q in question_phrases)
        or any(tok in PRICING_KEYWORDS for tok in tokens)
        or any(tok in FEATURE_KEYWORDS for tok in tokens)
        or any(tok in POLICY_KEYWORDS for tok in tokens)
    ):
        return {"intent": "product_inquiry"}

    greeting_words = {"hi", "hello", "hey", "hii"}
    if tokens & greeting_words or latest.startswith(("good morning", "good afternoon", "good evening")):
        return {"intent": "greeting"}

    return {"intent": "product_inquiry"}


def retrieve_context_node(state: AgentState) -> dict:
    messages = state.get("messages", [])
    if not messages:
        return {"rag_context": ""}
    query = _last_human_message(messages)
    return {"rag_context": retrieve_context(query)}


def update_lead_info_node(state: AgentState) -> dict:
    messages = state.get("messages", [])
    lead = dict(state.get("lead_info") or {})

    for field in ("name", "email", "platform"):
        lead.setdefault(field, None)

    if not messages:
        lead["lead_progress"] = 0
        return {"lead_info": lead}

    # Only use USER messages, never AI messages.
    user_messages = [m for m in messages[-8:] if isinstance(m, HumanMessage)]
    if not user_messages:
        lead["lead_progress"] = sum(1 for f in ("name", "email", "platform") if lead.get(f))
        return {"lead_info": lead}

    recent_user_text = "\n".join(m.content for m in user_messages)
    full_user_text = recent_user_text.lower()
    latest_user_text = user_messages[-1].content

    # Name
    if not lead.get("name"):
        name_patterns = [
            r"\b(?:my name is|i am|i'm|call me|name is)\s+([A-Za-z][A-Za-z'\-\. ]{1,60})",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, recent_user_text, re.IGNORECASE)
            if match:
                lead["name"] = match.group(1).strip()
                break

    # Email
    if not lead.get("email"):
        found_email = extract_email_from_text(latest_user_text)
        if not found_email:
            found_email = extract_email_from_text(full_user_text)
        if found_email:
            lead["email"] = found_email

    # Platform
    if not lead.get("platform"):
        platform_map = {
            "youtube": "YouTube",
            "yt": "YouTube",
            "instagram": "Instagram",
            "tiktok": "TikTok",
            "facebook": "Facebook",
            "linkedin": "LinkedIn",
            "twitter": "Twitter",
            "twitch": "Twitch",
            "snapchat": "Snapchat",
        }
        for raw, normalized in platform_map.items():
            if re.search(rf"\b{re.escape(raw)}\b", full_user_text):
                lead["platform"] = normalized
                break

    # Optional fallback using LLM only if something is still missing.
    missing = [f for f in ("name", "email", "platform") if not lead.get(f)]
    if missing:
        snippet = "\n".join(f"User: {m.content}" for m in user_messages)
        try:
            llm = _get_llm(temperature=0.0)
            resp = llm.invoke([HumanMessage(content=_EXTRACT_PROMPT.format(snippet=snippet))])
            raw = _llm_to_text(resp)
            raw = re.sub(r"```(?:json)?|```", "", raw).strip()
            extracted = json.loads(raw)

            for field in ("name", "email", "platform"):
                val = extracted.get(field)
                if val and str(val).strip() and str(val).lower() != "null" and not lead.get(field):
                    lead[field] = str(val).strip()
        except Exception:
            pass

    lead["lead_progress"] = sum(1 for f in ("name", "email", "platform") if lead.get(f))
    return {"lead_info": lead}


def capture_lead_node(state: AgentState) -> dict:
    li = state.get("lead_info", {})
    result = mock_lead_capture(
        name=li.get("name", ""),
        email=li.get("email", ""),
        platform=li.get("platform", ""),
    )
    return {
        "lead_captured": result["status"] == "success",
        "rag_context": f"[LEAD_CAPTURED] {result['message']}",
    }


def generate_response_node(state: AgentState) -> dict:
    intent = state.get("intent", "product_inquiry")
    lead = state.get("lead_info") or {}
    lead_captured = state.get("lead_captured", False)
    rag_ctx = state.get("rag_context", "")
    messages = state.get("messages", [])

    if intent == "greeting":
        return {
            "messages": [
                AIMessage(content="Hi! I'm Aria, AutoStream's friendly assistant. How can I help you today?")
            ]
        }

    if intent in {"high_intent", "collecting_lead"}:
        missing = [f for f in ("name", "email", "platform") if not lead.get(f)]
        if missing and not lead_captured:
            prompts = {
                "name": "Great — could I have your full name first?",
                "email": "Thanks — what's the best email address to reach you at?",
                "platform": "Which platform do you primarily create on (YouTube, Instagram, TikTok, etc.)?",
            }
            return {"messages": [AIMessage(content=prompts[missing[0]])]}

        if lead_captured:
            name = lead.get("name", "there")
            return {
                "messages": [
                    AIMessage(
                        content=f"Awesome {name}! We've captured your information. "
                                f"Our team will reach out soon at {lead.get('email', '')}. Thanks for your interest!"
                    )
                ]
            }

    if intent == "product_inquiry":
        if not rag_ctx or rag_ctx.startswith("[LEAD_CAPTURED]"):
            rag_ctx = get_full_kb()

        try:
            llm = _get_llm(temperature=0.2)
            user_question = _last_human_message(messages)

            prompt = f"""
You are Aria, AutoStream's friendly AI sales assistant.

Answer the user's question using ONLY the knowledge base below.
Do not dump the full knowledge base.
Be concise, clear, and helpful.
Keep the answer under 90 words unless the user asks for more detail.

Knowledge Base:
{rag_ctx}

User Question:
{user_question}
""".strip()

            reply = llm.invoke([HumanMessage(content=prompt)])
            reply_text = _llm_to_text(reply).strip()

            if not reply_text:
                raise RuntimeError("Empty LLM response.")

            return {"messages": [AIMessage(content=reply_text)]}

        except Exception as e:
            print(f"[autostream] Product inquiry LLM failed: {type(e).__name__}: {e}")

            user_q = _last_human_message(messages).lower()
            if "pro" in user_q:
                fallback = (
                    "The Pro plan is $79/month and includes unlimited videos, 4K export, "
                    "AI captions, advanced templates and transitions, priority rendering, "
                    "24/7 support, analytics, and team collaboration for up to 3 seats."
                )
            elif "basic" in user_q:
                fallback = (
                    "The Basic plan is $29/month and includes 10 videos per month, "
                    "720p export, auto-cut and trim, basic templates, and email support during business hours."
                )
            else:
                fallback = (
                    "AutoStream offers a Basic plan at $29/month and a Pro plan at $79/month. "
                    "The Pro plan includes unlimited videos, 4K export, AI captions, and 24/7 support."
                )

            return {"messages": [AIMessage(content=fallback)]}

    return {
        "messages": [
            AIMessage(content="Could you clarify what you'd like to know about AutoStream?")
        ]
    }