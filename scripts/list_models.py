import os
import sys

genai = None
genai_variant = None
try:
    import google.genai as genai
    genai_variant = "genai_new"
except Exception:
    try:
        from google import genai
        genai_variant = "genai_new"
    except Exception:
        try:
            # legacy package (not preferred) — avoid importing unless necessary
            import google.generativeai as genai
            genai_variant = "generativeai_legacy"
        except Exception as e:
            print("Please install google-genai (preferred) or google-generativeai (legacy).")
            raise


def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set. Set it in your environment or .env file.")
        sys.exit(1)

    print("Listing models that support generateContent (full name -> short name):\n")
    models = []
    if genai_variant == "generativeai_legacy":
        genai.configure(api_key=api_key)
        models = genai.list_models()
    else:
        try:
            models = genai.list_models()
        except Exception:
            try:
                resp = genai.models.list()
                models = getattr(resp, "models", resp)
            except Exception:
                models = []

    for m in models:
        # support both object and dict responses
        name = getattr(m, "name", None) or (m.get("name") if isinstance(m, dict) else None)
        methods = getattr(m, "supported_generation_methods", []) if not isinstance(m, dict) else m.get("supported_generation_methods", [])
        if not name:
            continue
        if "generateContent" in methods or not methods:
            full = name
            short = full.split("/", 1)[1] if "/" in full else full
            print(f"{full}  ->  {short}")

    print("\nDone.")


if __name__ == '__main__':
    main()
