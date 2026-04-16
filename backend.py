"""
AutoStream – Inflx AI Agent
Backend: environment setup, agent invocation, helpers.
"""

import os
import sys
import time
import warnings
import threading
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

# ── Environment ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=True)

warnings.filterwarnings("ignore", category=FutureWarning)

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("❌ GOOGLE_API_KEY not found. Add it to your .env file.")
    sys.exit(1)

# ── Agent import ─────────────────────────────────────────────────────────────
from agent import compiled_graph  # noqa: E402

# ── Constants ────────────────────────────────────────────────────────────────
MODEL = os.getenv("GENAI_MODEL", "gemini-flash-latest").strip()
TEMPERATURE = float(os.getenv("GENAI_TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("GENAI_MAX_OUTPUT_TOKENS", "220"))
AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "20"))
LEAD_FIELDS = ("name", "email", "platform")


# ── Helpers ──────────────────────────────────────────────────────────────────
def extract_ai_text(messages: list) -> str | None:
    for msg in reversed(messages or []):
        if not isinstance(msg, AIMessage):
            continue

        content = msg.content

        if isinstance(content, str):
            text = content.strip()
        elif isinstance(content, list):
            text = " ".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            ).strip()
        else:
            text = str(content).strip()

        if text:
            return text

    return None


def _prepare_runtime_env() -> None:
    os.environ["GOOGLE_API_KEY"] = API_KEY
    os.environ["GENAI_MODEL"] = MODEL
    os.environ["GENAI_TEMPERATURE"] = str(TEMPERATURE)
    os.environ["GENAI_MAX_OUTPUT_TOKENS"] = str(MAX_TOKENS)


def _invoke_graph(payload: dict, config: dict, bucket: dict) -> None:
    try:
        bucket["result"] = compiled_graph.invoke(payload, config=config)
    except Exception as exc:
        bucket["error"] = exc


def invoke_agent(user_msg: str, config: dict, prior_state: dict | None = None):
    if not user_msg or not user_msg.strip():
        raise ValueError("User message is empty.")

    _prepare_runtime_env()

    prior_state = prior_state or {}

    payload = {
        "messages": [HumanMessage(content=user_msg.strip())],
        "intent": prior_state.get("intent"),
        "lead_info": prior_state.get("lead_info") or {},
        "lead_captured": prior_state.get("lead_captured", False),
        "rag_context": prior_state.get("rag_context", ""),
    }

    bucket: dict = {}
    start = time.time()

    thread = threading.Thread(
        target=_invoke_graph,
        args=(payload, config, bucket),
        daemon=True,
    )
    thread.start()
    thread.join(timeout=AGENT_TIMEOUT)

    elapsed = time.time() - start

    if thread.is_alive():
        raise TimeoutError(
            f"Agent timed out after {AGENT_TIMEOUT}s. "
            f"Model={MODEL}. Check model config, API quota, or graph routing."
        )

    if "error" in bucket:
        raise RuntimeError(f"Agent invocation failed: {bucket['error']}") from bucket["error"]

    result = bucket.get("result", {})
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected graph result type: {type(result).__name__}")

    ai_text = extract_ai_text(result.get("messages", []))
    if not ai_text:
        raise RuntimeError(
            "Agent returned no AI message. "
            "Check graph routing or response generation."
        )

    print("=" * 70)
    print("MODEL:", MODEL)
    print("Intent:", result.get("intent"))
    print("Lead info:", result.get("lead_info"))
    print("Lead captured:", result.get("lead_captured"))
    print("Latency:", f"{elapsed:.2f}s")
    print("AI text:", ai_text)
    print("=" * 70)

    return ai_text, result, elapsed