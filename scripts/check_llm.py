#!/usr/bin/env python3
"""
Diagnostic script to verify LLM and API integration.
Run: python3 scripts/check_llm.py
"""
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 70)
print("AutoStream LLM & API Diagnostic Check")
print("=" * 70)

# ═══ 1. Check API Key ═══════════════════════════════════════════════════════
print("\n1️⃣  CHECKING API KEY...")
from dotenv import load_dotenv
_root = Path(__file__).parent.parent
_env = _root / ".env"
if _env.exists():
    load_dotenv(_env, override=True)
    print(f"   ✅ .env file found: {_env}")
else:
    print(f"   ⚠️  No .env file at {_env}")

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    masked = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print(f"   ✅ GOOGLE_API_KEY set: {masked}")
else:
    print(f"   ❌ GOOGLE_API_KEY NOT SET - LLM will fail!")
    sys.exit(1)

# ═══ 2. Check Model Configuration ═══════════════════════════════════════════
print("\n2️⃣  CHECKING MODEL CONFIGURATION...")
model = os.getenv("GENAI_MODEL", "gemini-flash-latest")
temperature = os.getenv("GENAI_TEMPERATURE", "0.3")
max_tokens = os.getenv("GENAI_MAX_OUTPUT_TOKENS", "256")
print(f"   ✅ GENAI_MODEL: {model}")
print(f"   ✅ GENAI_TEMPERATURE: {temperature}")
print(f"   ✅ GENAI_MAX_OUTPUT_TOKENS: {max_tokens}")

# ═══ 3. Check Imports ═══════════════════════════════════════════════════════
print("\n3️⃣  CHECKING DEPENDENCIES...")
try:
    import langchain_core
    print("   ✅ langchain_core imported")
except ImportError as e:
    print(f"   ❌ langchain_core failed: {e}")

try:
    import langchain_google_genai
    print("   ✅ langchain_google_genai imported")
except ImportError as e:
    print(f"   ❌ langchain_google_genai failed: {e}")

try:
    import langgraph
    print("   ✅ langgraph imported")
except ImportError as e:
    print(f"   ❌ langgraph failed: {e}")

try:
    from langchain_core.messages import HumanMessage, AIMessage
    print("   ✅ langchain_core.messages imported")
except ImportError as e:
    print(f"   ❌ langchain_core.messages failed: {e}")

# ═══ 4. Test LLM Initialization ════════════════════════════════════════════
print("\n4️⃣  TESTING LLM INITIALIZATION...")
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=api_key,
        temperature=0.3,
        max_output_tokens=256,
        convert_system_message_to_human=True,
    )
    print("   ✅ ChatGoogleGenerativeAI initialized successfully")
except Exception as e:
    print(f"   ❌ LLM initialization failed: {e}")
    sys.exit(1)

# ═══ 5. Test LLM Invocation ════════════════════════════════════════════════
print("\n5️⃣  TESTING LLM INVOCATION...")
try:
    from langchain_core.messages import HumanMessage
    
    print("   ⏳ Sending test query to API...")
    response = llm.invoke([
        HumanMessage(content="Say 'Hello! LLM is working.' in exactly 5 words or less.")
    ])
    
    if hasattr(response, 'content'):
        result = response.content
    else:
        result = str(response)
    
    print(f"   ✅ LLM Response: {result}")
    
except Exception as e:
    print(f"   ❌ LLM invocation failed: {e}")
    sys.exit(1)

# ═══ 6. Test Agent Graph ══════════════════════════════════════════════════
print("\n6️⃣  TESTING AGENT GRAPH...")
try:
    from agent import compiled_graph
    print("   ✅ Agent graph imported successfully")
    
    # Try a simple invoke
    print("   ⏳ Testing agent with simple greeting...")
    result = compiled_graph.invoke(
        {"messages": [HumanMessage(content="hi")]},
        config={"configurable": {"thread_id": "test-diagnostic"}},
    )
    
    if result.get("messages"):
        last_msg = result["messages"][-1]
        if hasattr(last_msg, 'content'):
            content = last_msg.content
        else:
            content = str(last_msg)
        print(f"   ✅ Agent response: {content[:100]}...")
    else:
        print(f"   ⚠️  No messages in result")
    
except Exception as e:
    print(f"   ❌ Agent graph test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ═══ Summary ════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("✅ ALL CHECKS PASSED - LLM & API ARE WORKING!")
print("=" * 70)
print("\nYou can now run:")
print("  streamlit run app.py")
print("\n" + "=" * 70)
