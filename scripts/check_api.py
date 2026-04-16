#!/usr/bin/env python3
"""
Complete API Diagnostic Tool
Tests Google Generative AI API step-by-step with detailed explanations
"""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"✓ Loaded .env from {env_path}\n")
else:
    print(f"⚠️  No .env file found at {env_path}")
    print("   Create one with: GOOGLE_API_KEY=your_key_here\n")

def step(num, title):
    """Print a formatted step header"""
    print(f"\n{'='*70}")
    print(f"STEP {num}: {title}")
    print(f"{'='*70}\n")

def check_api_key():
    """Step 1: Verify API key exists and is properly formatted"""
    step(1, "Check API Key Environment Variable")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY is NOT set in environment")
        print("\nFix: Set it in your .env file:")
        print("   GOOGLE_API_KEY=AIza...")
        print("\nOr export it in terminal:")
        print("   export GOOGLE_API_KEY=AIza...")
        return False
    
    print(f"✓ API Key found: {api_key[:20]}...{api_key[-5:]}")
    
    if not api_key.startswith("AIza"):
        print("⚠️  Warning: API key should start with 'AIza' (Google Generative AI format)")
        return False
    
    if len(api_key) < 30:
        print("⚠️  Warning: API key seems too short (expected 40+ characters)")
        return False
    
    print("✓ API key format looks valid")
    return True

def check_python_packages():
    """Step 2: Verify required packages are installed"""
    step(2, "Check Required Python Packages")
    
    packages = {
        "google.genai": "google-genai",
        "langchain": "langchain",
        "langchain_google_genai": "langchain-google-genai",
        "langchain_core": "langchain-core",
    }
    
    all_ok = True
    for module_name, package_name in packages.items():
        try:
            __import__(module_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"❌ {package_name} is NOT installed")
            all_ok = False
    
    if not all_ok:
        print("\n❌ Missing packages! Install them:")
        print("   pip install google-genai langchain langchain-google-genai")
        return False
    
    print("\n✓ All packages installed")
    return True

def check_genai_client_import():
    """Step 3: Test importing Google GenAI client"""
    step(3, "Test Google GenAI Client Import")
    
    try:
        import google.genai as genai
        print(f"✓ Successfully imported google.genai (new client)")
        
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        print(f"✓ Configured GenAI client with API key")
        
        return True
    except AttributeError as e:
        # New client uses different API; try without configure
        try:
            import google.genai as genai
            from google.genai import models
            api_key = os.getenv("GOOGLE_API_KEY")
            
            # Create a simple client with API key
            os.environ["GOOGLE_API_KEY"] = api_key
            print(f"✓ Google GenAI client ready (new API style)")
            return True
        except Exception as e2:
            print(f"❌ Failed to initialize google.genai:")
            print(f"   Error: {e2}")
            return False
    except Exception as e:
        print(f"❌ Failed to import/configure google.genai:")
        print(f"   Error: {e}")
        return False

def list_available_models():
    """Step 4: List available models"""
    step(4, "List Available Models from API")
    
    try:
        import google.genai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        os.environ["GOOGLE_API_KEY"] = api_key
        
        print("Fetching available models...")
        models = genai.models.list()
        
        model_list = []
        for m in models:
            name = getattr(m, "name", "unknown")
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                model_list.append(name)
        
        if not model_list:
            print("❌ No models with generateContent support found")
            print("\nPossible reasons:")
            print("   • Invalid API key")
            print("   • API key doesn't have access to Generative AI")
            print("   • Account not activated")
            return False
        
        print(f"✓ Found {len(model_list)} available models:\n")
        for m in sorted(model_list)[:10]:
            print(f"   • {m}")
        
        if len(model_list) > 10:
            print(f"   ... and {len(model_list) - 10} more")
        
        return True
    except Exception as e:
        print(f"❌ Failed to list models:")
        print(f"   Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_generation():
    """Step 5: Test simple text generation"""
    step(5, "Test Simple Text Generation")
    
    try:
        import google.genai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        os.environ["GOOGLE_API_KEY"] = api_key
        
        model = "gemini-1.5-flash"
        print(f"Using model: {model}")
        print("Sending test prompt: 'Say hello in one word'")
        print("\nWaiting for response (max 30 seconds)...\n")
        
        start = time.time()
        response = genai.models.generate_content(
            model=f"models/{model}",
            contents="Say hello in one word",
        )
        elapsed = time.time() - start
        
        print(f"✓ Response received in {elapsed:.2f}s:")
        print(f"   {response.text}\n")
        return True
        
    except Exception as e:
        print(f"❌ Generation failed:")
        print(f"   Error: {type(e).__name__}: {e}")
        print(f"\nCommon issues:")
        print(f"   • Invalid API key → Get a new key from Google AI Studio")
        print(f"   • Quota exceeded → Wait or upgrade your plan")
        print(f"   • Rate limited → Wait a few seconds and retry")
        print(f"   • Network issue → Check your internet connection")
        import traceback
        traceback.print_exc()
        return False

def test_agent_invocation():
    """Step 6: Test full agent invocation"""
    step(6, "Test Full Agent Invocation (30 second timeout)")
    
    try:
        from langchain_core.messages import HumanMessage
        from agent import compiled_graph
        import threading
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not set")
            return False
        
        print("Invoking compiled agent graph...")
        print("Prompt: 'What is your pricing?'")
        print("Timeout: 30 seconds\n")
        
        bucket = {}
        
        def _run():
            try:
                config = {"configurable": {"thread_id": "test-thread"}}
                bucket["result"] = compiled_graph.invoke(
                    {"messages": [HumanMessage(content="What is your pricing?")]},
                    config=config,
                )
            except Exception as exc:
                bucket["error"] = exc
        
        thread = threading.Thread(target=_run, daemon=True)
        start = time.time()
        thread.start()
        thread.join(timeout=30)
        elapsed = time.time() - start
        
        if thread.is_alive():
            print(f"⏱️  Thread still running after {elapsed:.1f}s (stuck)")
            print("❌ Agent invocation timed out")
            print("\nPossible reasons:")
            print("   • LLM is slow or unresponsive")
            print("   • Network connectivity issue")
            print("   • API is rate-limited")
            return False
        
        if "error" in bucket:
            print(f"❌ Agent error: {bucket['error']}")
            return False
        
        result = bucket.get("result", {})
        from langchain_core.messages import AIMessage
        
        ai_text = None
        for m in reversed(result.get("messages", [])):
            if isinstance(m, AIMessage):
                ai_text = m.content
                break
        
        if ai_text:
            print(f"✓ Agent response received in {elapsed:.2f}s:")
            print(f"\n{ai_text[:200]}...")
            return True
        else:
            print(f"❌ No AI response in result")
            return False
            
    except Exception as e:
        print(f"❌ Agent test failed:")
        print(f"   Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostics"""
    print("\n" + "="*70)
    print(" "*15 + "AUTOSTREAM API DIAGNOSTIC TOOL")
    print("="*70)
    print("\nThis tool will check if your API is properly configured")
    print("and responsive. Follow the steps below.\n")
    
    results = []
    
    # Run all checks
    results.append(("API Key Check", check_api_key()))
    if not results[-1][1]:
        print("\n⚠️  Cannot proceed without valid API key")
        sys.exit(1)
    
    results.append(("Package Check", check_python_packages()))
    if not results[-1][1]:
        print("\n⚠️  Cannot proceed without required packages")
        sys.exit(1)
    
    results.append(("GenAI Import", check_genai_client_import()))
    if not results[-1][1]:
        print("\n⚠️  Issue with GenAI client")
        sys.exit(1)
    
    results.append(("Model Listing", list_available_models()))
    results.append(("Simple Generation", test_simple_generation()))
    results.append(("Agent Invocation", test_agent_invocation()))
    
    # Summary
    step("SUMMARY", "Diagnostic Results")
    print("Results:\n")
    all_pass = True
    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"  {status} — {name}")
        if not passed:
            all_pass = False
    
    print("\n" + "="*70)
    
    if all_pass:
        print("✅ ALL CHECKS PASSED")
        print("\nYour API is working correctly!")
        print("Try using the Streamlit app now:")
        print("   streamlit run app.py")
    else:
        print("❌ SOME CHECKS FAILED")
        print("\nFix the issues above and run this script again.")
        print("\nFor help:")
        print("   • Check your API key at: https://aistudio.google.com/app/apikey")
        print("   • Ensure API is enabled in Google Cloud Console")
        print("   • Try waiting 5 minutes if rate-limited")
    
    print("="*70 + "\n")
    
    sys.exit(0 if all_pass else 1)

if __name__ == "__main__":
    main()
