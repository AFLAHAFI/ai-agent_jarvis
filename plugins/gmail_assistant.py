"""
plugins/gmail_assistant.py — Gmail Assistant Plugin for JARVIS.

Features:
  1. Interactive Setup: Asks the user which email address to connect if not yet configured.
  2. Quick Actions: Open Inbox, Filter Unread, Search Emails, and Compose Drafts.
  3. Zero Setup Friction: Uses direct web browser protocols without fragile OAuth tokens.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import webbrowser
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"


def _get_configured_email() -> str:
    try:
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return str(data.get("user_email", "")).strip()
    except Exception:
        pass
    return ""


def _save_email(email: str) -> None:
    try:
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        else:
            data = {}
        data["user_email"] = email.strip()
        CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"[GmailAssistant] Error saving email: {e}")


PLUGIN = {
    "name": "gmail_assistant",
    "description": (
        "Assists with Gmail management: open inbox, check unread emails, search emails, "
        "compose new emails, and edit an existing open draft in-place without opening duplicate tabs. "
        "Use action='edit_draft' when the user wants to change, edit, or retype the body or content of the currently open email draft. "
        "Use whenever the user asks to check Gmail, open email, send an email, or modify a drafted email."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "open_inbox | unread | compose | edit_draft | search | set_email",
            },
            "email": {
                "type": "STRING",
                "description": "The user's email address to connect or update (e.g. 'user@gmail.com').",
            },
            "recipient": {
                "type": "STRING",
                "description": "Recipient email address for compose action.",
            },
            "subject": {
                "type": "STRING",
                "description": "Subject line for compose action.",
            },
            "body": {
                "type": "STRING",
                "description": "Body message for compose action.",
            },
            "query": {
                "type": "STRING",
                "description": "Search keyword for search action.",
            },
        },
        "required": [],
    },
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = str(parameters.get("action", "open_inbox")).lower().strip()
    email_param = str(parameters.get("email", "")).strip()
    recipient = str(parameters.get("recipient", "")).strip()
    subject = str(parameters.get("subject", "")).strip()
    body = str(parameters.get("body", "")).strip()
    query = str(parameters.get("query", "")).strip()

    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print
    configured_email = _get_configured_email()

    # 1. Setting or updating email
    if action == "set_email" or (email_param and "@" in email_param):
        email_clean = email_param if ("@" in email_param) else ""
        if not email_clean:
            match = re.search(r"[\w\.-]+@[\w\.-]+", str(parameters))
            if match:
                email_clean = match.group(0)

        if email_clean:
            _save_email(email_clean)
            log(f"Connected Gmail account: {email_clean}")
            return f"Sir, I have successfully connected {email_clean} to your Gmail Assistant."

    # 2. Check if email is missing — ask the user!
    if not configured_email and not email_param:
        log("Prompting for email configuration…")
        return (
            "Sir, which email address would you like to connect to Gmail Assistant? "
            "Please tell me your email address so I can configure it for you."
        )

    # 3. Actions with configured email
    try:
        if action in ("unread", "check_unread", "new"):
            log("Opening unread emails in Gmail…")
            webbrowser.open("https://mail.google.com/mail/u/0/#search/is%3Aunread")
            return f"Sir, I have opened your unread emails in Gmail for {configured_email or 'your account'}."

        elif action in ("compose", "send", "write"):
            log(f"Composing email to {recipient or 'recipient'}…")
            params = ["view=cm", "fs=1"]
            if recipient:
                params.append(f"to={urllib.parse.quote(recipient)}")
            if subject:
                params.append(f"su={urllib.parse.quote(subject)}")
            if body:
                params.append(f"body={urllib.parse.quote(body)}")
            url = f"https://mail.google.com/mail/u/0/?{'&'.join(params)}"
            webbrowser.open(url)
            return f"Sir, I have opened a new Gmail draft to {recipient or 'your recipient'} with your message ready."

        elif action in ("edit_draft", "replace_draft", "update_draft", "edit_body"):
            log("Editing active draft in-place without opening new tab…")
            import time
            try:
                import pyautogui
                import pyperclip
                # Focus the browser window if possible
                try:
                    import pygetwindow as gw
                    for w in gw.getAllWindows():
                        if any(b in w.title.lower() for b in ("gmail", "chrome", "edge", "brave", "firefox")):
                            w.restore()
                            w.activate()
                            break
                except Exception:
                    pass
                time.sleep(0.3)
                # Select all text in the active message field and replace cleanly
                pyautogui.hotkey("ctrl", "a")
                time.sleep(0.1)
                pyautogui.press("backspace")
                time.sleep(0.1)
                text_to_paste = body or subject or ""
                if text_to_paste:
                    pyperclip.copy(text_to_paste)
                    time.sleep(0.1)
                    pyautogui.hotkey("ctrl", "v")
                return "Sir, I have modified your active email draft in-place on your screen."
            except Exception as e:
                return f"Sir, in-place edit failed: {e}"

        elif action in ("search", "find") and query:
            log(f"Searching Gmail for '{query}'…")
            encoded_q = urllib.parse.quote(query)
            webbrowser.open(f"https://mail.google.com/mail/u/0/#search/{encoded_q}")
            return f"Sir, I have searched Gmail for '{query}'."

        else:  # open_inbox
            log(f"Opening Gmail Inbox ({configured_email or 'Primary account'})…")
            webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
            return f"Sir, I have opened your Gmail Inbox for {configured_email or 'your account'}."

    except Exception as e:
        return f"Sir, could not open Gmail: {e}"
