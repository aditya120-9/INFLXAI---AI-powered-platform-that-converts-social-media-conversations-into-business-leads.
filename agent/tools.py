"""
tools.py
--------
Tool functions that the agent can call.

In a real deployment these would hit a CRM (HubSpot, Salesforce, etc.)
via an API.  For this assignment we use a mock that prints to stdout
and returns a confirmation dict.
"""

import re
from datetime import datetime


# ── Mock Lead Capture ─────────────────────────────────────────────────────────

def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    """
    Simulates saving a qualified lead to a CRM / database.

    Parameters
    ----------
    name     : Full name of the lead.
    email    : Email address of the lead.
    platform : Social/content platform (YouTube, Instagram, TikTok, etc.)

    Returns
    -------
    A dict with status and a confirmation message.
    """
    # ── Validation ────────────────────────────────────────────────────────────
    if not name or not name.strip():
        return {"status": "error", "message": "Name is required."}

    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    if not re.match(email_pattern, email.strip()):
        return {"status": "error", "message": f"Invalid email address: {email}"}

    if not platform or not platform.strip():
        return {"status": "error", "message": "Platform is required."}

    # ── Mock save ─────────────────────────────────────────────────────────────
    lead_record = {
        "name":      name.strip(),
        "email":     email.strip().lower(),
        "platform":  platform.strip(),
        "captured_at": datetime.utcnow().isoformat() + "Z",
        "source":    "AutoStream AI Agent",
        "status":    "new",
    }

    # This print simulates the CRM write
    print("\n" + "=" * 55)
    print("  ✅  LEAD CAPTURED SUCCESSFULLY")
    print("=" * 55)
    print(f"  Name     : {lead_record['name']}")
    print(f"  Email    : {lead_record['email']}")
    print(f"  Platform : {lead_record['platform']}")
    print(f"  Time     : {lead_record['captured_at']}")
    print("=" * 55 + "\n")

    return {
        "status":  "success",
        "message": f"Lead captured successfully: {name}, {email}, {platform}",
        "record":  lead_record,
    }


# ── Email Extractor (helper used by nodes.py) ─────────────────────────────────

def extract_email_from_text(text: str) -> str | None:
    """Pull the first email address found in a string."""
    pattern = r"[\w\.-]+@[\w\.-]+\.\w{2,}"
    match   = re.search(pattern, text)
    return match.group(0) if match else None
