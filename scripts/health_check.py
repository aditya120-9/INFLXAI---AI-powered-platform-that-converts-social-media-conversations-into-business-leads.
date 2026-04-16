#!/usr/bin/env python3
"""
Quick health check for AutoStream agent.
Tests: API key, LLM, agent, RAG, and lead capture.
Run: python3 scripts/health_check.py
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def check(condition, passed_msg, failed_msg):
    if condition:
        print(f"  ✅ {passed_msg}")
        return True
    else:
        print(f"  ❌ {failed_msg}")
        return False

# ═════════════════════════════════════════════════════════════════════════════
print_section("🏥 AutoStream Health Check")

all_pass = True

# 1. API Key Setup
print_section("1. API KEY SETUP")
from dotenv import load_dotenv
_root = Path(__file__).parent.parent
_env = _root / ".env"
if _env.exists():
    load_dotenv(_env, override=True)

api_key = os.getenv("GOOGLE_API_KEY")
all_pass &= check(
    api_key is not None,
    f"GOOGLE_API_KEY configured",
    "GOOGLE_API_KEY not set!"
)

# 2. Dependencies
print_section("2. DEPENDENCIES")
deps_ok = True
try:
    import langchain_core
    import langchain_google_genai
    import langgraph
    print("  ✅ langchain_core, langchain_google_genai, langgraph installed")
except ImportError as e:
    print(f"  ❌ Missing dependency: {e}")
    deps_ok = False
    all_pass = False

# 3. RAG System
print_section("3. RAG SYSTEM")
try:
    from agent.rag import retrieve_context, get_full_kb
    kb = get_full_kb()
    all_pass &= check(len(kb) > 500, "KB loaded (~3KB)", "KB too small")
    
    # Test retrieval
    pricing_context = retrieve_context("what is the pricing")
    all_pass &= check(
        "Pro Plan" in pricing_context,
        "RAG retrieves pricing correctly",
        "RAG pricing retrieval failed"
    )
except Exception as e:
    print(f"  ❌ RAG error: {e}")
    all_pass = False

# 4. State Management
print_section("4. STATE MANAGEMENT")
try:
    from agent.state import AgentState
    print("  ✅ AgentState TypedDict imported")
except Exception as e:
    print(f"  ❌ State error: {e}")
    all_pass = False

# 5. LLM Initialization
print_section("5. LLM INITIALIZATION")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=api_key,
        temperature=0.3,
        max_output_tokens=256,
        convert_system_message_to_human=True,
    )
    print("  ✅ ChatGoogleGenerativeAI initialized")
except Exception as e:
    print(f"  ❌ LLM init failed: {e}")
    all_pass = False

# 6. Graph Compilation
print_section("6. GRAPH COMPILATION")
try:
    from agent import compiled_graph
    print("  ✅ Agent graph compiled and imported")
except Exception as e:
    print(f"  ❌ Graph compilation failed: {e}")
    all_pass = False

# 7. Agent Test
print_section("7. AGENT TEST")
try:
    from langchain_core.messages import HumanMessage
    
    print("  ⏳ Testing agent with greeting...")
    result = compiled_graph.invoke(
        {"messages": [HumanMessage(content="hi")]},
        config={"configurable": {"thread_id": "health-check"}},
    )
    
    messages = result.get("messages", [])
    if messages and len(messages) > 0:
        last_msg = messages[-1]
        content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        print(f"  ✅ Agent responded: '{content[:60]}...'")
    else:
        print("  ❌ No response from agent")
        all_pass = False
        
except Exception as e:
    print(f"  ❌ Agent test failed: {e}")
    all_pass = False

# 8. Lead Extraction
print_section("8. LEAD EXTRACTION")
try:
    from agent.nodes import update_lead_info_node
    from agent.state import AgentState
    from langchain_core.messages import HumanMessage
    
    state = {
        "messages": [
            HumanMessage(content="my email is test@example.com"),
            HumanMessage(content="my name is John"),
            HumanMessage(content="I create on YouTube"),
        ],
        "intent": "collecting_lead",
        "lead_info": {},
        "lead_captured": False,
    }
    
    result = update_lead_info_node(state)
    lead_info = result.get("lead_info", {})
    
    has_email = bool(lead_info.get("email"))
    has_name = bool(lead_info.get("name"))
    has_platform = bool(lead_info.get("platform"))
    
    all_pass &= check(has_email, "Email extraction works", "Email extraction failed")
    all_pass &= check(has_name, "Name extraction works", "Name extraction failed")
    all_pass &= check(has_platform, "Platform extraction works", "Platform extraction failed")
    
except Exception as e:
    print(f"  ❌ Lead extraction test failed: {e}")
    all_pass = False

# 9. Tool Invocation
print_section("9. TOOL INVOCATION")
try:
    from agent.tools import mock_lead_capture
    
    result = mock_lead_capture(
        name="Test User",
        email="test@example.com",
        platform="YouTube",
    )
    
    all_pass &= check(
        result["status"] == "success",
        "Tool executes successfully",
        "Tool execution failed"
    )
except Exception as e:
    print(f"  ❌ Tool invocation failed: {e}")
    all_pass = False

# ═════════════════════════════════════════════════════════════════════════════
print_section("SUMMARY")

if all_pass:
    print("""
  ✅ ALL SYSTEMS OPERATIONAL
  
  Your AutoStream agent is ready for use!
  
  Start the UI with:
    streamlit run app.py
  
  Or run the simulation:
    python3 scripts/simulate_flows.py
    """)
    sys.exit(0)
else:
    print("""
  ⚠️  SOME CHECKS FAILED
  
  Please fix the issues above before running the application.
  """)
    sys.exit(1)
