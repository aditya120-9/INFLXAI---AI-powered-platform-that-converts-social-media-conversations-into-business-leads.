"""
rag.py
------
RAG (Retrieval-Augmented Generation) pipeline.

This module loads the AutoStream knowledge base from a JSON file and
returns the most relevant sections based on the user's query using
keyword-based retrieval.  For a production system you would replace
this with a vector database (Chroma, Pinecone, etc.), but for this
assignment a clean keyword approach over a small, structured KB is
perfectly valid and transparent.
"""

import json
import os
from pathlib import Path


# ── Load KB once at import time ──────────────────────────────────────────────
_KB_PATH = Path(__file__).parent.parent / "knowledge_base" / "autostream_kb.json"

with open(_KB_PATH, "r", encoding="utf-8") as f:
    _KB: dict = json.load(f)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_plans() -> str:
    lines = []
    for plan in _KB["plans"]:
        lines.append(f"### {plan['name']} — {plan['price']}")
        lines.append(f"- Videos/month: {plan['videos_per_month']}")
        lines.append(f"- Resolution: {plan['resolution']}")
        lines.append("- Features: " + ", ".join(plan["features"]))
        lines.append(f"- Best for: {plan['best_for']}")
        lines.append("")
    return "\n".join(lines)


def _format_policies() -> str:
    lines = []
    for p in _KB["policies"]:
        lines.append(f"**{p['topic']}**: {p['detail']}")
    return "\n".join(lines)


def _format_faqs() -> str:
    lines = []
    for faq in _KB["faqs"]:
        lines.append(f"Q: {faq['question']}\nA: {faq['answer']}")
    return "\n\n".join(lines)


def _format_company() -> str:
    c = _KB["company"]
    return f"{c['name']} — {c['tagline']}\n{c['description']}"


# ── Public API ────────────────────────────────────────────────────────────────

PRICING_KEYWORDS   = {"price", "pricing", "cost", "plan", "basic", "pro", "cheap",
                       "expensive", "per month", "subscription", "how much", "afford",
                       "upgrade", "tier", "package"}

POLICY_KEYWORDS    = {"refund", "cancel", "support", "policy", "policies", "trial",
                       "free", "days", "return", "money back", "billing", "upgrade",
                       "downgrade"}

FEATURE_KEYWORDS   = {"feature", "4k", "captions", "caption", "resolution", "video",
                       "unlimited", "720", "ai", "edit", "template", "export",
                       "collaboration", "team", "mobile", "platform"}

COMPANY_KEYWORDS   = {"what is", "about", "autostream", "company", "product",
                       "who are", "tell me"}


def retrieve_context(query: str) -> str:
    """
    Return a relevant context string from the knowledge base.

    Strategy
    --------
    1. Lower-case the query and split into tokens.
    2. Score each KB section by counting keyword hits.
    3. Return the highest-scoring sections (up to a cap).

    Returns an empty string if the query has no relevant keywords.
    """
    q_lower = query.lower()
    tokens  = set(q_lower.split())

    scores = {
        "pricing":  len(tokens & PRICING_KEYWORDS) + (2 if any(kw in q_lower for kw in PRICING_KEYWORDS) else 0),
        "policies": len(tokens & POLICY_KEYWORDS)  + (2 if any(kw in q_lower for kw in POLICY_KEYWORDS) else 0),
        "features": len(tokens & FEATURE_KEYWORDS) + (2 if any(kw in q_lower for kw in FEATURE_KEYWORDS) else 0),
        "company":  len(tokens & COMPANY_KEYWORDS) + (2 if any(kw in q_lower for kw in COMPANY_KEYWORDS) else 0),
    }

    # FIXED: Don't force policies - only return what's relevant to the query
    # For \"pro plan benefits\", return pricing + features, not cancellation policies
    
    sections = []
    if scores["company"]  > 0: sections.append(("company",  _format_company()))
    if scores["pricing"]  > 0: sections.append(("pricing",  _format_plans()))
    if scores["policies"] > 0: sections.append(("policies", _format_policies()))
    if scores["features"] > 0: sections.append(("faqs",     _format_faqs()))

    if not sections:
        # Fallback: return pricing only (most commonly asked)
        return _format_plans()

    # De-duplicate and join
    seen   = set()
    result = []
    for name, text in sections:
        if name not in seen:
            seen.add(name)
            result.append(text)

    return "\n\n---\n\n".join(result)


def get_full_kb() -> str:
    """Return the entire knowledge base as formatted text (used in system prompt)."""
    return (
        "## Company\n" + _format_company() + "\n\n" +
        "## Pricing Plans\n" + _format_plans() + "\n\n" +
        "## Policies\n" + _format_policies() + "\n\n" +
        "## FAQs\n" + _format_faqs()
    )
