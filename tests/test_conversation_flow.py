import os
import time
import unittest
from dotenv import load_dotenv
load_dotenv()

import sys
from pathlib import Path

# Adjust sys.path so tests can import the package when run from tests/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage
from agent import compiled_graph


class ConversationFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure deterministic model for tests
        os.environ.setdefault("GENAI_MODEL", "gemini-flash-latest")
        os.environ.setdefault("GENAI_MAX_OUTPUT_TOKENS", "256")
        os.environ.setdefault("GENAI_TEMPERATURE", "0.2")

    def invoke(self, message: str, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        state_in = {"messages": [HumanMessage(content=message)]}
        result = compiled_graph.invoke(state_in, config=config)
        return result

    def test_pricing_fast_path(self):
        thread = "test-pricing"
        res = self.invoke("Hi, tell me about your pricing.", thread)
        intent = res.get("intent")
        ai_text = None
        for m in reversed(res.get("messages", [])):
            if hasattr(m, 'content'):
                ai_text = m.content
                break
        self.assertIn(intent, {"product_inquiry", "greeting"})
        self.assertTrue(ai_text and ("Basic Plan" in ai_text or "AutoStream" in ai_text))

    def test_intent_shift_routes_to_lead_collection(self):
        thread = "test-intent-shift"
        _ = self.invoke("Hi, tell me about your pricing.", thread)
        res2 = self.invoke("That sounds good, I want to try the Pro plan for my YouTube channel.", thread)
        intent = res2.get("intent")
        ai_text = None
        for m in reversed(res2.get("messages", [])):
            if hasattr(m, 'content'):
                ai_text = m.content
                break
        # Expect high intent and lead field prompt
        self.assertIn(intent, {"high_intent", "collecting_lead"})
        self.assertTrue(ai_text and ("name" in ai_text.lower() or "email" in ai_text.lower() or "platform" in ai_text.lower()))

    def test_full_lead_capture_flow(self):
        thread = "test-lead-capture"
        # Intent trigger (YouTube mentioned)
        _ = self.invoke("That sounds good, I want to try the Pro plan for my YouTube channel.", thread)
        # Name
        _ = self.invoke("My name is Alice Example", thread)
        # Email
        _ = self.invoke("My email is alice@example.com", thread)
        # Platform (should auto-detect YouTube, but provide anyway)
        res_final = self.invoke("I create on YouTube", thread)
        # Verify capture
        lead_captured = res_final.get("lead_captured", False)
        lead_info = res_final.get("lead_info") or {}
        lead_progress = lead_info.get("lead_progress", 0)
        self.assertTrue(lead_captured, "Lead capture should complete")
        self.assertIn("alice", (lead_info.get("name") or "").lower())
        self.assertIn("alice@example.com", lead_info.get("email", ""))
        self.assertIn("youtube", (lead_info.get("platform") or "").lower())
        self.assertGreaterEqual(lead_progress, 3, "Lead progress should be 3/3")


if __name__ == '__main__':
    unittest.main()
