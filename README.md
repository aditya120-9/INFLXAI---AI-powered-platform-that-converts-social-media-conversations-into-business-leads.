
```
  ___        _        ____  _                              
 / _ \ _   _| |_ ___ / ___|| |_ _ __ ___  __ _ _ __ ___  
| | | | | | | __/ _ \\___ \| __| '__/ _ \/ _` | '_ ` _ \ 
| |_| | |_| | || (_) |___) | |_| | |  __/ (_| | | | | | |
 \___/ \__,_|\__\___/|____/ \__|_|  \___|\__,_|_| |_| |_|
```

# 🎬 AutoStream — Inflx AI Agent

**A production-grade Social-to-Lead Agentic Workflow**  
*Converts social conversations into qualified business leads using RAG + LangGraph + Gemini*


---

## ✨ What This Does

> Inflx AI is a **conversational sales agent** built for AutoStream — a SaaS platform for content creators.  
> It understands user intent, answers questions from a knowledge base, detects high-intent buyers, and captures leads automatically.

```
User: "I want to buy the Pro plan for my YouTube channel"
         ↓
    Intent Detection  →  HIGH_INTENT
         ↓
    Lead Collection   →  Asks for name, email, platform
         ↓
    Tool Execution    →  mock_lead_capture("Alex", "alex@gmail.com", "YouTube")
         ↓
    🎉 Lead Captured & Stored
```

---

## 🗂️ Project Structure

```
autostream-agent/
│
├── app.py                    # 🔧 Backend — env, agent runner, helpers
├── ui.py                     # 🎨 Frontend — Streamlit cinematic UI
│
├── agent/
│   ├── __init__.py           # Exports compiled_graph
│   ├── graph.py              # LangGraph state machine definition
│   ├── nodes.py              # Agent nodes: intent, RAG, lead, response
│   ├── state.py              # TypedDict state schema
│   ├── tools.py              # mock_lead_capture() tool
│   └── rag.py                # RAG pipeline — retrieval + context building
│
├── knowledge_base/
│   └── autostream_kb.json    # 📚 Local knowledge base (pricing + policies)
│
├── .env                      # 🔑 API keys (not committed)
├── requirements.txt          # 📦 All dependencies
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/autostream-agent.git
cd autostream-agent
```

### 2. Create & activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your key:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

> 🔑 Get your free Gemini API key at [aistudio.google.com](https://aistudio.google.com)

### 5. Run the app

```bash
streamlit run ui.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🤖 Agent Capabilities

| Capability | Description |
|---|---|
| 🧠 **Intent Detection** | Classifies every message as `greeting`, `pricing_inquiry`, or `high_intent` |
| 📚 **RAG Retrieval** | Retrieves accurate answers from a local JSON knowledge base |
| 🎯 **Lead Capture** | Automatically collects name, email, and platform when high intent is detected |
| 🔧 **Tool Execution** | Calls `mock_lead_capture()` only after all three lead fields are collected |
| 🗃️ **State Memory** | Retains full conversation context across 5–6+ turns using LangGraph checkpointing |

---

## 🏗️ Architecture Explanation

### Why LangGraph?

LangGraph was chosen over AutoGen because it provides **explicit, inspectable state management** through a directed graph model. Each conversation turn is a node with defined transitions — making the agent's behavior deterministic, debuggable, and easy to extend. Unlike AutoGen's multi-agent conversation loops (which can be opaque), LangGraph lets you clearly define *when* the lead tool fires, *when* RAG is triggered, and *when* the agent should ask a follow-up — giving precise control required for a sales pipeline.

### How State Is Managed

The agent uses a `TypedDict` state schema (`AgentState`) that flows through every node in the graph:

```
AgentState {
  messages:      list[BaseMessage]   # Full conversation history
  intent:        str                 # Detected intent for current turn
  rag_context:   str | None          # Retrieved KB content
  lead_info:     dict                # Collected name/email/platform
  lead_captured: bool                # Whether mock_lead_capture() has fired
}
```

LangGraph's **MemorySaver checkpointer** persists this state across turns using a `thread_id`, giving the agent true multi-turn memory without an external database. The state is passed to every node, updated immutably, and returned — ensuring each step has full context of what came before.

### Conversation Flow

```
[User Message]
      │
      ▼
[Intent Detection Node]
      │
      ├──► greeting        → [Response Node] → reply warmly
      │
      ├──► pricing_inquiry → [RAG Node] → retrieve KB → [Response Node]
      │
      └──► high_intent     → [Lead Collection Node]
                                   │
                                   ├── missing fields? → ask for next field
                                   │
                                   └── all collected? → [Tool Node]
                                                              │
                                                              ▼
                                                   mock_lead_capture() ✅
```

---

## 📱 WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp, you would use the **WhatsApp Business Cloud API** (Meta) with a webhook server:

### Architecture

```
WhatsApp User
     │  (sends message)
     ▼
Meta WhatsApp Cloud API
     │  (POST webhook event)
     ▼
Your Webhook Server  (FastAPI / Flask)
     │  (extract message, call invoke_agent())
     ▼
LangGraph Agent  (same compiled_graph)
     │  (returns AI response)
     ▼
Meta Send Message API
     │  (POST reply back)
     ▼
WhatsApp User  ✅
```

### Step-by-Step Integration

**Step 1 — Set up Meta Developer App**
```
1. Go to developers.facebook.com → Create App → Business type
2. Add "WhatsApp" product to your app
3. Note your Phone Number ID and WhatsApp Business Account ID
```

**Step 2 — Create a webhook server**

```python
# webhook.py
from fastapi import FastAPI, Request
import httpx, os
from app import invoke_agent

app = FastAPI()

# Thread store: maps WhatsApp number → LangGraph thread_id
threads: dict = {}

@app.get("/webhook")
async def verify(request: Request):
    """Meta webhook verification handshake."""
    params = dict(request.query_params)
    if params.get("hub.verify_token") == os.getenv("WA_VERIFY_TOKEN"):
        return int(params["hub.challenge"])
    return {"error": "Invalid token"}, 403

@app.post("/webhook")
async def receive(request: Request):
    """Handle incoming WhatsApp messages."""
    body   = await request.json()
    change = body["entry"][0]["changes"][0]["value"]
    msg    = change["messages"][0]

    user_phone = msg["from"]
    user_text  = msg["text"]["body"]

    # Per-user thread for memory persistence
    if user_phone not in threads:
        import uuid
        threads[user_phone] = str(uuid.uuid4())

    config  = {"configurable": {"thread_id": threads[user_phone]}}
    ai_text, _, _ = invoke_agent(user_text, config)

    # Send reply via WhatsApp Cloud API
    await _send_whatsapp(user_phone, ai_text)
    return {"status": "ok"}

async def _send_whatsapp(to: str, text: str):
    url     = f"https://graph.facebook.com/v18.0/{os.getenv('WA_PHONE_ID')}/messages"
    headers = {"Authorization": f"Bearer {os.getenv('WA_TOKEN')}"}
    payload = {"messaging_product": "whatsapp", "to": to,
                "type": "text", "text": {"body": text}}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, headers=headers)
```

**Step 3 — Add to `.env`**
```env
WA_VERIFY_TOKEN=your_custom_verify_token
WA_TOKEN=your_whatsapp_api_token
WA_PHONE_ID=your_phone_number_id
```

**Step 4 — Deploy & expose publicly**
```bash
# Option A: ngrok (local dev)
ngrok http 8000

# Option B: deploy to Railway / Render / fly.io
# Railway example:
railway login
railway init
railway up
```

**Step 5 — Register webhook in Meta Dashboard**
```
WhatsApp → Configuration → Webhook URL:
  https://your-domain.com/webhook

Verify Token: (same as WA_VERIFY_TOKEN in .env)
Subscribe to: messages
```

---

## 🧪 Sample Conversation

```
You  → hi
Aria → Hi! I'm Aria, AutoStream's AI assistant. How can I help you today?

You  → what are your pricing plans?
Aria → AutoStream offers two plans:
       • Basic — $29/month (10 videos, 720p)
       • Pro   — $79/month (Unlimited, 4K, AI captions, 24/7 support)

You  → I want to try the Pro plan for my YouTube channel
Aria → Great choice! What's the best email address to reach you at?

You  → alex@gmail.com
Aria → Thanks! And what's your full name?

You  → Alex Rivera
Aria → Perfect Alex! You're all set. Our team will reach out shortly. 🎉

# ✅ mock_lead_capture("Alex Rivera", "alex@gmail.com", "YouTube") called
```

---

## 📦 Requirements

```txt
streamlit>=1.35.0
langchain>=0.2.0
langchain-core>=0.2.0
langchain-google-genai>=1.0.0
langgraph>=0.1.0
python-dotenv>=1.0.0
google-generativeai>=0.7.0
fastapi>=0.111.0          # for WhatsApp webhook
httpx>=0.27.0             # for WhatsApp webhook
uvicorn>=0.30.0           # for WhatsApp webhook
```

---

## ⬆️ How to Push to GitHub

```bash
# 1. Initialize git (if not already)
git init

# 2. Create .gitignore — never commit secrets!
echo ".env
__pycache__/
.venv/
*.pyc
.pytest_cache/" > .gitignore

# 3. Stage all files
git add .

# 4. First commit
git commit -m "🎬 feat: AutoStream Inflx AI Agent — LangGraph + Gemini + RAG"

# 5. Create repo on GitHub (via CLI)
gh repo create autostream-agent --public --source=. --push

# OR manually:
git remote add origin https://github.com/YOUR_USERNAME/autostream-agent.git
git branch -M main
git push -u origin main
```

---

## 🧰 Tech Stack

<div align="center">

| Layer | Technology |
|---|---|
| **LLM** | Google Gemini 1.5 Flash |
| **Agent Framework** | LangGraph (StateGraph) |
| **RAG** | Local JSON KB + keyword retrieval |
| **UI** | Streamlit (Cinematic Intelligence design) |
| **State Memory** | LangGraph MemorySaver checkpointer |
| **Tool Execution** | LangChain Tool + mock_lead_capture() |
| **WhatsApp** | Meta Cloud API + FastAPI webhook |
| **Language** | Python 3.10+ |

</div>



**Built for ServiceHive × Inflx ML Intern Assignment**  
*AutoStream AI Agent — Social-to-Lead Agentic Workflow*

</div>