
import os
import concurrent.futures
from langchain_core.messages import HumanMessage

from agent.nodes import _get_llm


def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key and os.environ.get("MOCK_MODE", "0") not in {"1", "true", "yes"}:
        print("ERROR: GOOGLE_API_KEY not set. Set it in your environment or .env file, or enable MOCK_MODE=1 for local testing.")
        return

    print("Testing LLM (uses GENAI_MODEL / MOCK_MODE if set)")
    try:
        llm = _get_llm(temperature=0.2)
        # Debug info
        try:
            model_name = getattr(llm, "model", None) or getattr(llm, "_model", None)
        except Exception:
            model_name = None
        print("LLM instance:", type(llm), "model->", model_name)

        print("Invoking model (will timeout after 60s)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(lambda: llm.invoke([HumanMessage(content="Hello from AutoStream test")]))
            try:
                resp = future.result(timeout=60)
                content = getattr(resp, "content", None)
                if content is None:
                    content = str(resp)
                print("Response:", content)
            except concurrent.futures.TimeoutError:
                print("Error: LLM invocation timed out after 60 seconds. The call may be hanging or slow.")
            except Exception as e:
                print("Error calling model:", e)
    except Exception as e:
        print("Error configuring LLM:", e)


if __name__ == '__main__':
    main()
