#!/usr/bin/env python3
"""
simulate_flows.py

Headless simulation of three conversation flows:
- pricing-only (KB fast-path)
- pricing -> intent shift (routes to lead qualification)
- full lead-capture flow (name -> email -> platform -> capture)

Prints timings, intents, RAG excerpts, AI replies, and lead capture status.
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import time
import concurrent.futures
from pathlib import Path
from pprint import pprint

# Ensure project root is on sys.path when running from scripts/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage, AIMessage
from agent import compiled_graph


def invoke_thread(message: str, thread_id: str, timeout_msg: int = 300):
    """Invoke the compiled graph for a single user message in the given thread.
    Returns (result, elapsed_seconds)
    """
    config = {"configurable": {"thread_id": thread_id}}
    state_in = {"messages": [HumanMessage(content=message)]}

    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(lambda: compiled_graph.invoke(state_in, config=config))
        try:
            result = future.result(timeout=timeout_msg)
            elapsed = time.time() - t0
            return result, elapsed
        except concurrent.futures.TimeoutError:
            return {"_error": "timeout"}, time.time() - t0
        except Exception as e:
            return {"_error": str(e)}, time.time() - t0


def summarize_result(result: dict):
    ai_text = None
    for m in reversed(result.get("messages", [])):
        if isinstance(m, AIMessage):
            ai_text = m.content
            break
    return {
        "intent": result.get("intent"),
        "rag_context_snippet": (result.get("rag_context") or "")[:500],
        "ai_text": (ai_text or ""),
        "lead_info": result.get("lead_info"),
        "lead_captured": result.get("lead_captured", False),
    }


if __name__ == '__main__':
    # Ensure model chosen for consistency
    model = os.environ.get("GENAI_MODEL") or "gemini-flash-latest"
    os.environ["GENAI_MODEL"] = model
    os.environ.setdefault("GENAI_MAX_OUTPUT_TOKENS", "256")
    os.environ.setdefault("GENAI_TEMPERATURE", "0.2")

    print("Simulation using model:", os.environ.get("GENAI_MODEL"))

    # Flow A: Pricing-only
    print("\n=== Flow A: Pricing-only (KB fast-path) ===")
    thread_a = "flow-pricing-1"
    msg_a = "Hi, tell me about your pricing."
    res_a, t_a = invoke_thread(msg_a, thread_a)
    summary_a = summarize_result(res_a)
    print(f"Elapsed: {t_a:.2f}s")
    pprint(summary_a)

    # Flow B: Pricing -> Intent shift
    print("\n=== Flow B: Pricing -> Intent shift ===")
    thread_b = "flow-intent-1"
    msg_b1 = "Hi, tell me about your pricing."
    res_b1, t_b1 = invoke_thread(msg_b1, thread_b)
    print(f"Step1 Elapsed: {t_b1:.2f}s")
    pprint(summarize_result(res_b1))

    # Now user expresses intent
    msg_b2 = "That sounds good, I want to try the Pro plan for my YouTube channel."
    res_b2, t_b2 = invoke_thread(msg_b2, thread_b)
    print(f"Step2 Elapsed: {t_b2:.2f}s")
    pprint(summarize_result(res_b2))

    # Flow C: Full lead capture
    print("\n=== Flow C: Full lead capture (name -> email -> platform) ===")
    thread_c = "flow-lead-1"
    msgs = [
        "That sounds good, I want to try the Pro plan for my YouTube channel.",
        "My name is Alice Example",
        "My email is alice@example.com",
        "I create on YouTube",
    ]

    for i, m in enumerate(msgs, start=1):
        res_c, t_c = invoke_thread(m, thread_c)
        print(f"Step {i} Elapsed: {t_c:.2f}s")
        pprint(summarize_result(res_c))

    print("\nSimulation complete.")
