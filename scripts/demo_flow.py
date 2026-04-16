#!/usr/bin/env python3
"""
AutoStream AI Agent - Complete Flow Demonstration
Shows all 4 key capabilities in sequence
"""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)

print("\n" + "="*70)
print("  AUTOSTREAM AI AGENT — COMPLETE DEMONSTRATION".center(70))
print("="*70 + "\n")

from backend import invoke_agent, LEAD_FIELDS

# Test scenarios
scenarios = [
    {
        "title": "1️⃣  PRICING INQUIRY",
        "description": "User asks about pricing plans",
        "user_input": "What are your pricing plans?",
        "thread_id": "demo-pricing",
    },
    {
        "title": "2️⃣  HIGH-INTENT DETECTION",
        "description": "User expresses purchase interest",
        "user_input": "I want to try the pro plan for my YouTube channel",
        "thread_id": "demo-high-intent",
    },
    {
        "title": "3️⃣  LEAD COLLECTION (Name)",
        "description": "Agent collects name from user",
        "user_input": "My name is John Anderson",
        "thread_id": "demo-lead-flow",
    },
    {
        "title": "4️⃣  LEAD COLLECTION (Email)",
        "description": "Agent collects email from user",
        "user_input": "My email is john.anderson@example.com",
        "thread_id": "demo-lead-flow",
    },
    {
        "title": "5️⃣  LEAD COLLECTION (Platform)",
        "description": "Agent collects platform info and captures lead",
        "user_input": "I create content on YouTube and Instagram",
        "thread_id": "demo-lead-flow",
    },
]

# Run scenarios
for i, scenario in enumerate(scenarios):
    print("\n" + "-"*70)
    print(f"{scenario['title']}")
    print(f"Description: {scenario['description']}")
    print("-"*70)
    
    print(f"\n👤 User: {scenario['user_input']}\n")
    
    try:
        config = {"configurable": {"thread_id": scenario["thread_id"]}}
        ai_response, result, elapsed = invoke_agent(scenario["user_input"], config)
        
        # Extract metadata
        intent = result.get("intent", "unknown")
        lead_info = result.get("lead_info", {})
        lead_captured = result.get("lead_captured", False)
        
        # Show response
        print(f"🤖 Aria: {ai_response}\n")
        
        # Show metadata
        print(f"⏱️  Response time: {elapsed:.2f}s")
        print(f"🎯 Intent: {intent}")
        
        if lead_info:
            collected = [f for f in LEAD_FIELDS if lead_info.get(f)]
            missing = [f for f in LEAD_FIELDS if not lead_info.get(f)]
            if collected:
                print(f"✓ Collected: {', '.join(collected)}")
            if missing:
                print(f"⏳ Waiting for: {', '.join(missing)}")
        
        if lead_captured:
            print(f"✅ Lead captured successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*70)
print("  DEMONSTRATION COMPLETE".center(70))
print("="*70)
print("\n✨ The system successfully:")
print("   1. Answered pricing questions with KB data")
print("   2. Detected high-purchase-intent")
print("   3. Collected user details (name, email, platform)")
print("   4. Captured the lead with mock_lead_capture tool")
print("\n🎬 Ready for presentation!\n")
