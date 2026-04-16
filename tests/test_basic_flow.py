#!/usr/bin/env python3
"""
Quick test: Verify end-to-end agent flow with increased timeout
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)

print("Testing AutoStream Agent with 60-second timeout\n")

# Test 1: Simple greeting
print("="*60)
print("TEST 1: Simple Greeting")
print("="*60)

from backend import invoke_agent, AGENT_TIMEOUT

config = {"configurable": {"thread_id": "test-flow-1"}}

try:
    response, result, elapsed = invoke_agent("hi there", config)
    print(f"✓ Success ({elapsed:.2f}s)")
    print(f"   Agent: {response[:100]}...\n")
except TimeoutError as e:
    print(f"✗ Timeout: {e}\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

# Test 2: Pricing inquiry
print("="*60)
print("TEST 2: Pricing Inquiry")
print("="*60)

config2 = {"configurable": {"thread_id": "test-flow-2"}}

try:
    response, result, elapsed = invoke_agent("what are your pricing plans?", config2)
    print(f"✓ Success ({elapsed:.2f}s)")
    print(f"   Intent: {result.get('intent')}")
    print(f"   Response preview: {response[:100]}...\n")
except TimeoutError as e:
    print(f"✗ Timeout: {e}\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

# Test 3: High-intent inquiry with lead collection
print("="*60)
print("TEST 3: High-Intent (Pro Plan Purchase)")
print("="*60)

config3 = {"configurable": {"thread_id": "test-flow-3"}}

try:
    response, result, elapsed = invoke_agent(
        "i want to try the pro plan for my youtube channel",
        config3
    )
    print(f"✓ Success ({elapsed:.2f}s)")
    print(f"   Intent: {result.get('intent')}")
    print(f"   Lead Info: {result.get('lead_info')}")
    print(f"   Response: {response[:100]}...\n")
except TimeoutError as e:
    print(f"✗ Timeout: {e}\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

print("="*60)
print(f"Agent timeout setting: {AGENT_TIMEOUT} seconds")
print("="*60)
print("\n✅ If all tests passed, your API is working correctly!")
print("   Try the Streamlit app: streamlit run app.py")
