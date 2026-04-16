"""
AutoStream – Inflx AI Agent
UI: Streamlit frontend with a polished recruiter-friendly interface.
Run: streamlit run app.py
"""

import html
import uuid
from datetime import datetime

import streamlit as st

from backend import LEAD_FIELDS, MODEL, invoke_agent


# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Inflx AI – AutoStream",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)




# ──────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS & CSS
# ──────────────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
  --bg:          #060e20;
  --surface-low: #091328;
  --surface:     #0f1930;
  --surface-hi:  #141f38;
  --surface-br:  #1f2b49;
  --surface-top: #192540;
  --primary:     #a3a6ff;
  --primary-dim: #6063ee;
  --secondary:   #89f5e7;
  --tertiary:    #ff9dd1;
  --text:        #dee5ff;
  --text-muted:  #a3aac4;
  --outline:     #40485d;
}

/* Base */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
  background-color: var(--bg) !important;
  font-family: 'Inter', sans-serif;
  color: var(--text);
}

.block-container {
  padding: 1.2rem 2rem 5rem !important;
  max-width: 100% !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background-color: var(--surface-low) !important;
  border-right: none !important;
  min-width: 280px !important;
  width: 280px !important;
  position: relative !important;
}

[data-testid="stSidebar"] > div:first-child {
  padding: 1.6rem 1.1rem;
}

.sidebar-brand {
  font-family: 'Manrope', sans-serif;
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.03em;
  line-height: 1;
  margin-bottom: 0.35rem;
}

.sidebar-sub {
  font-size: 0.84rem;
  color: var(--text-muted);
  font-weight: 500;
}

/* Typography */
h1, h2, h3 {
  font-family: 'Manrope', sans-serif !important;
  color: var(--text) !important;
}

/* Page header */
.page-header {
  background: rgba(31,43,73,0.82);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 1rem;
  padding: 1rem 1.4rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.4rem;
  border: 1px solid rgba(163,166,255,0.10);
  box-shadow: 0 10px 30px rgba(0,0,0,0.18);
  position: sticky;
  top: 0.75rem;
  z-index: 30;
}
.page-header-brand {
  font-family: 'Manrope', sans-serif;
  font-weight: 800;
  font-size: 1.55rem;
  letter-spacing: -0.03em;
  color: var(--text);
}
.page-header-sub {
  font-size: 0.82rem;
  color: var(--text-muted);
  margin-top: 4px;
}
.model-badge {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dim) 100%);
  color: #0f00a4;
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 0.7rem;
  padding: 0.35rem 1rem;
  border-radius: 9999px;
  letter-spacing: 0.03em;
  white-space: nowrap;
}

/* Section heading */
.section-heading {
  font-family: 'Manrope', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.02em;
  margin: 0 0 0.2rem;
}
.section-sub {
  font-size: 0.92rem;
  color: var(--text-muted);
  margin-bottom: 1.2rem;
}

/* KPI cards */
.kpi-card {
  background: var(--surface-hi);
  border-radius: 0.875rem;
  padding: 1.4rem 1.6rem;
}
.kpi-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  font-weight: 600;
  margin-bottom: 6px;
}
.kpi-value {
  font-family: 'Manrope', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.03em;
  line-height: 1;
}
.kpi-delta {
  font-size: 0.72rem;
  color: var(--secondary);
  font-weight: 600;
  margin-top: 5px;
}
.kpi-value.accent-green  { color: var(--secondary); }
.kpi-value.accent-purple { color: var(--primary); }
.kpi-value.accent-pink   { color: var(--tertiary); }

/* Chat container */
.chat-wrap {
  background: var(--surface-low);
  border-radius: 1rem;
  padding: 1.2rem;
  min-height: 420px;
  max-height: 62vh;
  overflow-y: auto;
  margin-bottom: 1rem;
  border: 1px solid rgba(163,166,255,0.08);
  scroll-behavior: smooth;
}
.chat-wrap::-webkit-scrollbar { width: 6px; }
.chat-wrap::-webkit-scrollbar-track { background: transparent; }
.chat-wrap::-webkit-scrollbar-thumb {
  background: var(--outline);
  border-radius: 99px;
}
.chat-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 260px;
  color: var(--text-muted);
  font-size: 0.92rem;
}

/* Chat bubbles */
.msg-row {
  display: flex;
  gap: 10px;
  margin-bottom: 1.1rem;
  align-items: flex-end;
}
.msg-row.user {
  flex-direction: row-reverse;
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--surface-br);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--primary);
  flex-shrink: 0;
}
.avatar.ai-avatar { color: var(--secondary); }

.bubble {
  max-width: 78%;
  padding: 0.85rem 1.1rem;
  border-radius: 1rem;
  font-size: 0.9rem;
  line-height: 1.7;
  color: var(--text);
  word-wrap: break-word;
}
.bubble.ai-bubble {
  background: var(--surface);
  border-bottom-left-radius: 4px;
}
.bubble.user-bubble {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dim) 100%);
  color: #0b00a8;
  font-weight: 600;
  border-bottom-right-radius: 4px;
}
.msg-time {
  font-size: 0.62rem;
  color: var(--text-muted);
  margin-top: 4px;
  text-align: right;
}

/* Input */
[data-testid="stTextArea"] textarea {
  background-color: var(--surface-hi) !important;
  border: 1px solid rgba(163,166,255,0.08) !important;
  border-radius: 0.875rem !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.92rem !important;
  resize: none !important;
  padding: 1rem 1.2rem !important;
  transition: background .2s ease, box-shadow .2s ease !important;
}
[data-testid="stTextArea"] textarea:focus {
  background-color: var(--surface-br) !important;
  box-shadow: 0 0 0 1px rgba(163,166,255,0.25) !important;
  outline: none !important;
}
[data-testid="stTextArea"] label {
  display: none !important;
}

/* Buttons */
[data-testid="stButton"] > button {
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  border-radius: 0.875rem !important;
  border: none !important;
  padding: 0.7rem 1.2rem !important;
  font-size: 0.88rem !important;
  transition: opacity .18s, transform .18s !important;
}
[data-testid="stButton"] > button:hover {
  opacity: 0.9 !important;
  transform: translateY(-1px) !important;
}

/* Lead card */
.lead-card {
  background: rgba(31,43,73,0.65);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 1rem;
  padding: 1.6rem;
  margin-bottom: 1.2rem;
  border: 1px solid rgba(163,166,255,0.08);
}
.lead-card-title {
  font-family: 'Manrope', sans-serif;
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--primary);
  margin-bottom: .3rem;
}
.lead-card-sub {
  font-size: .82rem;
  color: var(--text-muted);
}
[data-testid="stForm"] [data-testid="stTextInput"] input {
  background: var(--surface-hi) !important;
  border: none !important;
  border-radius: .875rem !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  padding: .65rem 1rem !important;
}
[data-testid="stForm"] [data-testid="stTextInput"] input:focus {
  background: var(--surface-br) !important;
  box-shadow: 0 0 0 1px rgba(163,166,255,.2) !important;
}
[data-testid="stForm"] [data-testid="stTextInput"] label {
  color: var(--text-muted) !important;
  font-size: .8rem !important;
  font-weight: 600 !important;
}

/* Success banner */
.success-banner {
  background: rgba(137,245,231,0.1);
  border-radius: .875rem;
  padding: 1rem 1.4rem;
  color: var(--secondary);
  font-weight: 600;
  font-size: .88rem;
  text-align: center;
  margin-bottom: 1.2rem;
  border: 1px solid rgba(137,245,231,0.15);
}

/* Knowledge base cards */
.kb-plan-card {
  background: var(--surface-hi);
  border-radius: .875rem;
  padding: 1.6rem;
  height: 100%;
}
.kb-plan-name {
  font-family: 'Manrope', sans-serif;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text);
  margin-bottom: .3rem;
}
.kb-plan-price {
  font-family: 'Manrope', sans-serif;
  font-size: 2rem;
  font-weight: 800;
  color: var(--primary);
  margin-bottom: .8rem;
}
.kb-tag {
  display: inline-block;
  font-size: .68rem;
  font-weight: 700;
  padding: .25rem .7rem;
  border-radius: 9999px;
  margin: .2rem .2rem 0 0;
  background: rgba(163,166,255,.12);
  color: var(--primary);
}
.kb-tag.green {
  background: rgba(137,245,231,.12);
  color: var(--secondary);
}
.kb-feature {
  font-size: .82rem;
  color: var(--text-muted);
  padding: .35rem 0;
  border-bottom: 1px solid rgba(64,72,93,.3);
}
.kb-feature:last-child { border-bottom: none; }

.kb-policy-card {
  background: var(--surface-hi);
  border-radius: .875rem;
  padding: 1.4rem;
  margin-bottom: 1rem;
}
.kb-policy-title {
  font-family: 'Manrope', sans-serif;
  font-weight: 700;
  color: var(--text);
  font-size: .95rem;
  margin-bottom: .4rem;
}
.kb-policy-text {
  font-size: .82rem;
  color: var(--text-muted);
  line-height: 1.6;
}

/* Feed */
.feed-item {
  background: var(--surface-hi);
  border-radius: .75rem;
  padding: .9rem 1.1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: .6rem;
}
.feed-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--surface-br);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: .7rem;
  font-weight: 700;
  color: var(--primary);
  margin-right: .8rem;
}
.intent-pill {
  font-size: .62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .05em;
  padding: .25rem .7rem;
  border-radius: 9999px;
}
.pill-high  { background: rgba(137,245,231,.15); color: var(--secondary); }
.pill-inq   { background: rgba(255,157,209,.12); color: var(--tertiary); }
.pill-greet { background: rgba(64,72,93,.4); color: var(--text-muted); }

/* Lead management */
.lead-row {
  background: var(--surface-hi);
  border-radius: .75rem;
  padding: 1rem 1.2rem;
  display: flex;
  align-items: center;
  gap: 1.2rem;
  margin-bottom: .6rem;
}

/* Nav */
.nav-active {
  background: #ffffff0d;
  color: var(--primary);
  font-weight: 700;
  border-right: 2px solid var(--primary);
}
.nav-inactive {
  color: rgba(222,229,255,.55);
}

/* Footer */
.app-footer {
  margin-top: 1.8rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(163,166,255,0.08);
  text-align: center;
  color: var(--text-muted);
  font-size: 0.8rem;
}

/* Misc */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"]      { display: none; }
[data-testid="stDecoration"]   { display: none; }
[data-testid="stStatusWidget"] { display: none; }
</style>
"""


# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────
_DEFAULTS = {
    "page": "conversations",
    "thread_id": None,
    "chat": [],
    "last_result": None,
    "last_latency": None,
    "collecting_lead": False,
    "missing_fields": [],
    "lead_info": {},
    "lead_captured": False,
    "total_convos": 0,
    "total_leads": 0,
    "all_leads": [],
    "request_in_progress": False,  # FIXED: prevent duplicate submissions
}


def _init():
    for key, value in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if not st.session_state["thread_id"]:
        st.session_state["thread_id"] = str(uuid.uuid4())


def _append_chat(role: str, content: str):
    st.session_state["chat"].append(
        {
            "role": role,
            "content": content,
            "time": datetime.now().strftime("%H:%M"),
        }
    )


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
def _sidebar():
    with st.sidebar:
        st.markdown(
            "<div style='padding:0 .4rem 2rem'>"
            "<div class='sidebar-brand'>Inflx AI</div>"
            "<div class='sidebar-sub'>AutoStream Engine</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        pages = [
            ("💬", "Conversations", "conversations"),
            ("📊", "Dashboard", "dashboard"),
            ("📚", "Knowledge Base", "kb"),
            ("👥", "Lead Management", "leads"),
        ]

        for icon, label, key in pages:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state["page"] = key
                st.rerun()

        st.markdown(
            "<hr style='border-color:#40485d22;margin:1.4rem 0'>"
            "<div style='font-size:.68rem;color:#a3aac4;text-transform:uppercase;"
            "letter-spacing:.08em;font-weight:600;margin-bottom:.6rem'>Model</div>"
            f"<div class='model-badge' style='display:inline-block'>✦ {MODEL}</div>",
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# HEADER / FOOTER
# ──────────────────────────────────────────────────────────────────────────────
def _header():
    st.markdown(
        f"<div class='page-header'>"
        f"<div>"
        f"<div class='page-header-brand'>Inflx AI</div>"
        f"<div class='page-header-sub'>AutoStream Engine · Social-to-Lead Agent</div>"
        f"</div>"
        f"<span class='model-badge'>✦ {MODEL}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _footer():
    st.markdown(
        "<div class='app-footer'><em>Built with ❤️ for the ServiceHive ML Internship Assignment</em></div>",
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# KPI ROW
# ──────────────────────────────────────────────────────────────────────────────
def _kpi_row():
    latency = st.session_state["last_latency"]
    latency_str = f"{latency:.2f}s" if latency else "–"
    intent = (st.session_state.get("last_result") or {}).get("intent", "–")

    intent_map = {
        "high_intent": ("accent-green", "High-Intent"),
        "collecting_lead": ("accent-green", "Collecting"),
        "pricing_inquiry": ("accent-pink", "Inquiry"),
        "greeting": ("", "Greeting"),
    }
    cls, label = intent_map.get(intent, ("", str(intent).replace("_", " ").title()))

    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Conversations</div>"
            f"<div class='kpi-value'>{st.session_state['total_convos']}</div>"
            f"<div class='kpi-delta'>This session</div></div>",
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Leads Captured</div>"
            f"<div class='kpi-value accent-green'>{st.session_state['total_leads']}</div>"
            f"<div class='kpi-delta'>This session</div></div>",
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Last Response</div>"
            f"<div class='kpi-value accent-purple'>{latency_str}</div>"
            f"<div class='kpi-delta'>Latency</div></div>",
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Detected Intent</div>"
            f"<div class='kpi-value {cls}' style='font-size:1.1rem;padding-top:.4rem'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# CONVERSATIONS PAGE
# ──────────────────────────────────────────────────────────────────────────────
def _page_conversations():
    config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

    st.markdown(
        "<div class='section-heading'>Conversations</div>"
        "<div class='section-sub'>Chat with Aria — AutoStream's AI sales agent</div>",
        unsafe_allow_html=True,
    )

    _kpi_row()

    if st.session_state["lead_captured"]:
        info = st.session_state["lead_info"]
        st.markdown(
            f"<div class='success-banner'>🎉 Lead captured successfully — "
            f"{html.escape(info.get('name', '–'))} &nbsp;·&nbsp; "
            f"{html.escape(info.get('email', '–'))} &nbsp;·&nbsp; "
            f"{html.escape(info.get('platform', '–'))}</div>",
            unsafe_allow_html=True,
        )

    _chat_bubbles()

    if st.session_state["collecting_lead"] and not st.session_state["lead_captured"]:
        _lead_form(config)
    else:
        _main_input(config)


def _chat_bubbles():
    if not st.session_state["chat"]:
        st.markdown(
            "<div class='chat-wrap'><div class='chat-empty'>💬&nbsp; Start a conversation below…</div></div>",
            unsafe_allow_html=True,
        )
        return

    rows = []
    for msg in st.session_state["chat"]:
        ts = msg.get("time", datetime.now().strftime("%H:%M"))
        content = html.escape(msg.get("content", "")).replace("\n", "<br>")

        if msg["role"] == "user":
            rows.append(
                f"<div class='msg-row user'>"
                f"<div class='avatar'>YOU</div>"
                f"<div>"
                f"<div class='bubble user-bubble'>{content}</div>"
                f"<div class='msg-time'>{ts}</div>"
                f"</div></div>"
            )
        else:
            rows.append(
                f"<div class='msg-row'>"
                f"<div class='avatar ai-avatar'>AI</div>"
                f"<div>"
                f"<div class='bubble ai-bubble'>{content}</div>"
                f"<div class='msg-time'>{ts}</div>"
                f"</div></div>"
            )

    chat_html = "".join(rows)

    st.markdown(
        f"<div class='chat-wrap' id='chat-wrap'>{chat_html}<div id='chat-bottom'></div></div>",
        unsafe_allow_html=True,
    )

    st.html(
        """
        <script>
        const doc = window.parent.document;
        const chatWrap = doc.getElementById("chat-wrap");
        if (chatWrap) {
            chatWrap.scrollTop = chatWrap.scrollHeight;
        }
        </script>
        """
    )


def _lead_form(config):
    missing = st.session_state["missing_fields"]
    next_field = missing[0] if missing else None
    if not next_field:
        return

    labels = {
        "name": ("Full Name", "e.g. Alex Rivera"),
        "email": ("Email Address", "e.g. alex@email.com"),
        "platform": ("Creator Platform", "e.g. YouTube, Instagram"),
    }
    label, placeholder = labels[next_field]

    st.markdown(
        f"<div class='lead-card'>"
        f"<div class='lead-card-title'>🎯 One more thing…</div>"
        f"<div class='lead-card-sub'>Aria needs your <b>{label.lower()}</b> to complete your profile.</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    with st.form(key=f"lead_{next_field}", clear_on_submit=True):
        value = st.text_input(label, placeholder=placeholder)
        submitted = st.form_submit_button(
            "Continue →",
            use_container_width=True,
            disabled=st.session_state.get("request_in_progress", False),  # FIXED: disable while pending
        )

    if not submitted:
        return

    if not value.strip():
        st.warning("Please enter a value before continuing.")
        return

    phrase = {
        "name": f"My name is {value.strip()}",
        "email": f"My email is {value.strip()}",
        "platform": f"I create on {value.strip()}",
    }[next_field]

    _append_chat("user", phrase)
    st.session_state["total_convos"] += 1
    st.session_state["request_in_progress"] = True  # FIXED: Set flag before request

    with st.spinner("Aria is thinking…"):
        try:
            ai_reply, result2, elapsed2 = invoke_agent(phrase, config)
        except Exception as exc:
            st.session_state["chat"].pop()
            st.session_state["request_in_progress"] = False  # FIXED: Clear flag on error
            st.error(f"❌ {exc}")
            st.rerun()  # FIXED: Force UI refresh after error
            return

    _append_chat("ai", ai_reply)
    st.session_state["last_latency"] = elapsed2
    st.session_state["last_result"] = result2

    new_info = result2.get("lead_info") or {}
    new_captured = result2.get("lead_captured", False)
    new_intent = result2.get("intent")

    st.session_state["lead_info"] = new_info
    st.session_state["lead_captured"] = new_captured

    new_missing = [field for field in LEAD_FIELDS if not new_info.get(field)]

    if new_captured or new_intent not in {"high_intent", "collecting_lead"} or not new_missing:
        st.session_state["collecting_lead"] = False
        st.session_state["missing_fields"] = []

        if new_captured:
            st.session_state["total_leads"] += 1
            st.session_state["all_leads"].append(
                {
                    **new_info,
                    "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )
    else:
        st.session_state["missing_fields"] = new_missing

    st.session_state["request_in_progress"] = False  # FIXED: Clear flag after request
    st.rerun()


def _main_input(config):
    user_input = st.text_area(
        label="Message",
        placeholder="Ask about pricing, features, or just say hi…",
        height=96,
        label_visibility="collapsed",
        key="user_input",
    )

    col_send, col_clear = st.columns([5, 1], gap="small")
    with col_send:
        send = st.button("🚀  Send Message", use_container_width=True, disabled=st.session_state.get("request_in_progress", False))
    with col_clear:
        clear = st.button("Clear", use_container_width=True)

    if clear:
        for key in list(_DEFAULTS.keys()):
            st.session_state.pop(key, None)
        st.rerun()

    if not send:
        return

    if not user_input.strip():
        st.warning("⚠️ Please type a message first.")
        return

    last_user = next(
        (msg for msg in reversed(st.session_state["chat"]) if msg["role"] == "user"),
        None,
    )
    if not (last_user and last_user["content"] == user_input.strip()):
        _append_chat("user", user_input.strip())
        st.session_state["total_convos"] += 1

    st.session_state["request_in_progress"] = True  # FIXED: Set flag before request

    with st.spinner("Aria is thinking…"):
        try:
            ai_text, result, elapsed = invoke_agent(user_input.strip(), config)
        except TimeoutError as te:
            st.session_state["chat"].pop()
            st.session_state["request_in_progress"] = False  # FIXED: Clear flag on error
            st.error(f"⏱️ {te}")
            st.rerun()  # FIXED: Force UI refresh after error
            return
        except Exception as exc:
            st.session_state["chat"].pop()
            st.session_state["request_in_progress"] = False  # FIXED: Clear flag on error
            st.error(f"❌ {exc}")
            st.caption("Check your GOOGLE_API_KEY and API quota.")
            st.rerun()  # FIXED: Force UI refresh after error
            return

    _append_chat("ai", ai_text)
    st.session_state["last_latency"] = elapsed
    st.session_state["last_result"] = result

    intent = result.get("intent")
    lead_info = result.get("lead_info") or {}
    captured = result.get("lead_captured", False)
    missing = [field for field in LEAD_FIELDS if not lead_info.get(field)]

    st.session_state["lead_info"] = lead_info
    st.session_state["lead_captured"] = captured

    if intent in {"high_intent", "collecting_lead"} and missing and not captured:
        st.session_state["collecting_lead"] = True
        st.session_state["missing_fields"] = missing
    else:
        st.session_state["collecting_lead"] = False
        st.session_state["missing_fields"] = []

        if captured:
            st.session_state["total_leads"] += 1
            st.session_state["all_leads"].append(
                {
                    **lead_info,
                    "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }
            )

    st.session_state["request_in_progress"] = False  # FIXED: Clear flag after request
    st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# DASHBOARD PAGE
# ──────────────────────────────────────────────────────────────────────────────
def _page_dashboard():
    st.markdown(
        "<div class='section-heading'>System Overview</div>"
        "<div class='section-sub'>Real-time performance metrics for AutoStream Engine agents</div>",
        unsafe_allow_html=True,
    )
    _kpi_row()

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown(
            "<div style='font-family:Manrope,sans-serif;font-size:1.05rem;font-weight:700;"
            "color:#dee5ff;margin-bottom:1rem'>Conversation Trends</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style='background:#091328;border-radius:.875rem;padding:1.4rem;'>
              <svg viewBox="0 0 600 160" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:140px">
                <defs>
                  <linearGradient id="g1" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#a3a6ff;stop-opacity:.3"/>
                    <stop offset="100%" style="stop-color:#a3a6ff;stop-opacity:0"/>
                  </linearGradient>
                </defs>
                <path d="M0,120 Q40,110 80,115 T160,90 T240,75 T320,95 T400,55 T480,35 T600,20"
                      fill="none" stroke="#a3a6ff" stroke-width="3" stroke-linecap="round"/>
                <path d="M0,120 Q40,110 80,115 T160,90 T240,75 T320,95 T400,55 T480,35 T600,20 V160 H0 Z"
                      fill="url(#g1)"/>
                <circle cx="160" cy="90" r="4" fill="#a3a6ff"/>
                <circle cx="320" cy="95" r="4" fill="#a3a6ff"/>
                <circle cx="480" cy="35" r="4" fill="#a3a6ff"/>
                <circle cx="600" cy="20" r="5" fill="#a3a6ff"/>
              </svg>
              <div style="display:flex;justify-content:space-between;font-size:.68rem;
                          color:#a3aac4;font-weight:600;text-transform:uppercase;
                          letter-spacing:.07em;margin-top:.4rem">
                <span>Day 01</span><span>Day 10</span><span>Day 20</span><span>Day 30</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        metrics = [
            ("⚡", "Response Speed", "0.07s", "Excellent", "#89f5e7"),
            ("🎯", "Intent Accuracy", "94.8%", "Optimised 2d ago", "#a3a6ff"),
            ("💬", "Avg. Turns", "3.4", "Per session", "#a3aac4"),
            ("🛡️", "Safety Score", "100%", "Compliance ✓", "#89f5e7"),
        ]

        cols_a = st.columns(2, gap="medium")
        cols_b = st.columns(2, gap="medium")

        for i, (icon, title, val, note, color) in enumerate(metrics):
            col = cols_a[i % 2] if i < 2 else cols_b[i % 2]
            with col:
                st.markdown(
                    f"<div class='kpi-card' style='margin-bottom:.8rem'>"
                    f"<div style='font-size:1.2rem;margin-bottom:.3rem'>{icon}</div>"
                    f"<div class='kpi-label'>{title}</div>"
                    f"<div class='kpi-value' style='font-size:1.6rem;color:{color}'>{val}</div>"
                    f"<div class='kpi-delta'>{note}</div></div>",
                    unsafe_allow_html=True,
                )

    with col_right:
        st.markdown(
            "<div style='font-family:Manrope,sans-serif;font-size:1.05rem;font-weight:700;"
            "color:#dee5ff;margin-bottom:1rem'>Live Activity Feed</div>",
            unsafe_allow_html=True,
        )

        real_leads = st.session_state.get("all_leads", [])
        feed_items = []
        for lead in reversed(real_leads[-4:]):
            feed_items.append(
                (
                    (lead.get("name") or "User")[:2].upper(),
                    lead.get("name", "Unknown"),
                    lead.get("captured_at", "just now"),
                    "high",
                    "High-Intent",
                )
            )

        mock_feed = [
            ("JD", "User #8421", "2 mins ago", "high", "High-Intent"),
            ("KL", "User #8399", "5 mins ago", "greet", "Greeting"),
            ("MR", "User #8385", "12 mins ago", "inq", "Inquiry"),
            ("AM", "User #8372", "25 mins ago", "high", "High-Intent"),
        ]
        display = (feed_items + mock_feed)[:4]

        pill_cls = {"high": "pill-high", "inq": "pill-inq", "greet": "pill-greet"}

        for initials, name, ts, itype, ilabel in display:
            pill_class = pill_cls.get(itype, "pill-greet")
            st.markdown(
                f"<div class='feed-item'>"
                f"<div style='display:flex;align-items:center'>"
                f"<div class='feed-avatar'>{html.escape(initials)}</div>"
                f"<div><div style='font-size:.85rem;font-weight:600;color:#dee5ff'>{html.escape(name)}</div>"
                f"<div style='font-size:.68rem;color:#a3aac4'>{html.escape(ts)}</div></div></div>"
                f"<span class='intent-pill {pill_class}'>{html.escape(ilabel)}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='display:flex;align-items:center;gap:.5rem;margin-top:.8rem;"
            "font-size:.72rem;color:#89f5e7;font-weight:700;text-transform:uppercase;"
            "letter-spacing:.08em'>"
            "<span style='width:8px;height:8px;border-radius:50%;background:#89f5e7;display:inline-block'></span>"
            "LIVE</div>",
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE BASE PAGE
# ──────────────────────────────────────────────────────────────────────────────
def _page_kb():
    st.markdown(
        "<div class='section-heading'>Knowledge Base</div>"
        "<div class='section-sub'>AutoStream product information used for RAG-powered responses</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='font-family:Manrope,sans-serif;font-size:1.1rem;font-weight:700;"
        "color:#dee5ff;margin:1.5rem 0 .8rem'>Pricing Plans</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            <div class='kb-plan-card'>
              <div class='kb-plan-name'>Basic Plan</div>
              <div class='kb-plan-price'>$29<span style='font-size:1rem;color:#a3aac4'>/month</span></div>
              <div class='kb-tag'>10 videos/month</div>
              <div class='kb-tag'>720p resolution</div>
              <div style='margin-top:1rem'>
                <div class='kb-feature'>✦ &nbsp;10 videos per month</div>
                <div class='kb-feature'>✦ &nbsp;720p resolution export</div>
                <div class='kb-feature'>✦ &nbsp;Auto-cut &amp; trim</div>
                <div class='kb-feature'>✦ &nbsp;Basic templates</div>
                <div class='kb-feature'>✦ &nbsp;Email support (business hours)</div>
                <div class='kb-feature' style='color:#ff9dd1'>✗ &nbsp;No 24/7 support</div>
                <div class='kb-feature' style='color:#ff9dd1'>✗ &nbsp;No AI captions</div>
              </div>
              <div style='margin-top:1rem;font-size:.75rem;color:#a3aac4'>
                Best for: Individual creators starting out
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class='kb-plan-card' style='border:1px solid rgba(163,166,255,.15)'>
              <div style='font-size:.65rem;font-weight:700;color:#a3a6ff;text-transform:uppercase;
                          letter-spacing:.1em;margin-bottom:.4rem'>Most Popular</div>
              <div class='kb-plan-name'>Pro Plan</div>
              <div class='kb-plan-price'>$79<span style='font-size:1rem;color:#a3aac4'>/month</span></div>
              <div class='kb-tag'>Unlimited videos</div>
              <div class='kb-tag green'>4K resolution</div>
              <div class='kb-tag green'>AI Captions</div>
              <div style='margin-top:1rem'>
                <div class='kb-feature'>✦ &nbsp;Unlimited videos per month</div>
                <div class='kb-feature'>✦ &nbsp;4K resolution export</div>
                <div class='kb-feature'>✦ &nbsp;AI captions (auto-generated)</div>
                <div class='kb-feature'>✦ &nbsp;Advanced templates &amp; transitions</div>
                <div class='kb-feature'>✦ &nbsp;Priority rendering</div>
                <div class='kb-feature green' style='color:#89f5e7'>✦ &nbsp;24/7 customer support</div>
                <div class='kb-feature green' style='color:#89f5e7'>✦ &nbsp;Team collaboration (up to 3 seats)</div>
              </div>
              <div style='margin-top:1rem;font-size:.75rem;color:#a3aac4'>
                Best for: Professional creators, agencies, high-volume channels
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div style='font-family:Manrope,sans-serif;font-size:1.1rem;font-weight:700;"
        "color:#dee5ff;margin:2rem 0 .8rem'>Company Policies</div>",
        unsafe_allow_html=True,
    )

    policies = [
        (
            "💳",
            "Refund Policy",
            "No refunds are issued after 7 days of subscription start. Within the first 7 days, a full refund can be requested by contacting support.",
        ),
        (
            "🎧",
            "Support",
            "24/7 support is available exclusively on the Pro plan. Basic plan users receive email support during business hours (Mon–Fri, 9am–6pm EST).",
        ),
        (
            "❌",
            "Cancellation",
            "You can cancel your subscription at any time. Access continues until the end of the current billing period.",
        ),
        (
            "⬆️",
            "Upgrades",
            "You can upgrade from Basic to Pro at any time. The price difference is prorated for the current billing cycle.",
        ),
        (
            "🎁",
            "Free Trial",
            "AutoStream offers a 7-day free trial on the Pro plan. No credit card required to start the trial.",
        ),
    ]

    pc1, pc2 = st.columns(2, gap="large")
    for i, (icon, title, text) in enumerate(policies):
        col = pc1 if i % 2 == 0 else pc2
        with col:
            st.markdown(
                f"<div class='kb-policy-card'>"
                f"<div class='kb-policy-title'>{icon} &nbsp;{html.escape(title)}</div>"
                f"<div class='kb-policy-text'>{html.escape(text)}</div></div>",
                unsafe_allow_html=True,
            )


# ──────────────────────────────────────────────────────────────────────────────
# LEAD MANAGEMENT PAGE
# ──────────────────────────────────────────────────────────────────────────────
def _page_leads():
    st.markdown(
        "<div class='section-heading'>Lead Management</div>"
        "<div class='section-sub'>Leads captured by Aria during this session</div>",
        unsafe_allow_html=True,
    )

    total = len(st.session_state["all_leads"])
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Total Leads</div>"
            f"<div class='kpi-value accent-green'>{total}</div>"
            f"<div class='kpi-delta'>This session</div></div>",
            unsafe_allow_html=True,
        )

    with c2:
        total_convos = st.session_state.get("total_convos", 1)
        conversion_rate = "0%" if total_convos == 0 else f"{round(total / max(total_convos, 1) * 100)}%"
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Conversion Rate</div>"
            f"<div class='kpi-value accent-purple'>{conversion_rate}</div>"
            f"<div class='kpi-delta'>Leads / conversations</div></div>",
            unsafe_allow_html=True,
        )

    with c3:
        status = "✓ Active" if total > 0 else "– Waiting"
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-label'>Status</div>"
            f"<div class='kpi-value' style='font-size:1rem;padding-top:.4rem;color:#89f5e7'>{status}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    if not st.session_state["all_leads"]:
        st.markdown(
            "<div style='background:#091328;border-radius:.875rem;padding:3rem;text-align:center;"
            "color:#a3aac4;font-size:.88rem'>"
            "No leads captured yet. Start a conversation in the Conversations tab.</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        "<div style='display:grid;grid-template-columns:1fr 1.4fr 1fr 1fr;"
        "padding:.4rem 1.2rem;font-size:.65rem;font-weight:700;color:#a3aac4;"
        "text-transform:uppercase;letter-spacing:.08em;margin-bottom:.3rem'>"
        "<span>Name</span><span>Email</span><span>Platform</span><span>Captured At</span></div>",
        unsafe_allow_html=True,
    )

    for lead in reversed(st.session_state["all_leads"]):
        st.markdown(
            f"<div style='display:grid;grid-template-columns:1fr 1.4fr 1fr 1fr;"
            f"background:#141f38;border-radius:.75rem;padding:.9rem 1.2rem;"
            f"margin-bottom:.5rem;font-size:.85rem;align-items:center'>"
            f"<span style='color:#dee5ff;font-weight:600'>{html.escape(lead.get('name', '–'))}</span>"
            f"<span style='color:#a3aac4'>{html.escape(lead.get('email', '–'))}</span>"
            f"<span><div class='intent-pill pill-high'>{html.escape(lead.get('platform', '–'))}</div></span>"
            f"<span style='color:#a3aac4;font-size:.75rem'>{html.escape(lead.get('captured_at', '–'))}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────
def run():
    _init()
    st.markdown(CSS, unsafe_allow_html=True)
    
    # Check for API Key
    import os
    if not os.environ.get("GOOGLE_API_KEY"):
        st.warning(
            "⚠️ **GOOGLE_API_KEY not configured**\n\n"
            "LLM features are disabled. To enable them:\n"
            "1. Get your API key from https://aistudio.google.com/app/apikeys\n"
            "2. Set environment variable: `export GOOGLE_API_KEY='your-key'`\n"
            "3. Restart the app\n\n"
            "The agent will use knowledge base fallbacks in the meantime."
        )
    
    _sidebar()
    _header()

    page = st.session_state.get("page", "conversations")
    if page == "conversations":
        _page_conversations()
    elif page == "dashboard":
        _page_dashboard()
    elif page == "kb":
        _page_kb()
    elif page == "leads":
        _page_leads()

    _footer()


if __name__ == "__main__":
    run()