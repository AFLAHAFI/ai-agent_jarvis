"""
plugins/whatsapp_assistant.py — Native WhatsApp Desktop Assistant.

Sends messages, opens chats, and checks unread messages via the native
Windows WhatsApp Desktop application using the registered 'whatsapp://'
protocol and window telemetry.
"""
from __future__ import annotations

import os
import platform
import re
import subprocess
import time
import urllib.parse
import webbrowser
from typing import Optional

PLUGIN = {
    "name": "whatsapp_assistant",
    "description": (
        "Controls the native WhatsApp Desktop application on Windows. "
        "Actions: 'send' (send a message to a contact/phone), 'open' (open WhatsApp Desktop), "
        "or 'check_unread' (check for unread WhatsApp messages and conversations). "
        "Always prefers the native Windows desktop app over the web browser."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "send | open | check_unread",
            },
            "recipient": {
                "type": "STRING",
                "description": "Phone number with country code (e.g. '+919876543210' or '9876543210') or contact name.",
            },
            "message": {
                "type": "STRING",
                "description": "The message text to send.",
            },
        },
        "required": [],
    },
}


def _clean_phone(raw: str) -> str:
    """Strips formatting from phone number while preserving digits."""
    digits = re.sub(r"[^\d+]", "", raw.strip())
    if digits.startswith("+"):
        digits = digits[1:]
    return digits


def _open_native_whatsapp(uri: str) -> bool:
    """Launches the native WhatsApp Windows app via protocol or shell command."""
    try:
        if platform.system() == "Windows":
            os.startfile(uri)
            return True
        else:
            subprocess.run(["open", uri], check=True)
            return True
    except Exception as e:
        print(f"[WhatsApp] Native launch error: {e}")
        return False


def _check_unread_whatsapp() -> tuple[int, list[str]]:
    """Inspects running WhatsApp Desktop windows for unread message indicators."""
    unread_count = 0
    matched_titles = []
    try:
        import pygetwindow as gw
        for win in gw.getAllWindows():
            title = win.title.strip()
            if "whatsapp" in title.lower():
                matched_titles.append(title)
                # Look for unread patterns like '(3) WhatsApp' or '(12) WhatsApp'
                m = re.search(r"\((\d+)\)\s*whatsapp", title, re.IGNORECASE)
                if m:
                    unread_count += int(m.group(1))
    except Exception as e:
        print(f"[WhatsApp] Window inspection error: {e}")
    return unread_count, matched_titles


def _bring_whatsapp_to_front() -> bool:
    """Activates and brings the WhatsApp Desktop window to the foreground."""
    try:
        import pygetwindow as gw
        for win in gw.getAllWindows():
            if "whatsapp" in win.title.lower():
                win.restore()
                win.activate()
                return True
    except Exception:
        pass
    return False


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = str(parameters.get("action", "")).strip().lower()
    recipient = str(parameters.get("recipient", "")).strip()
    message = str(parameters.get("message", "")).strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    # Auto-detect action if not specified
    if not action:
        if recipient or message:
            action = "send"
        else:
            action = "open"

    # Action: Check Unread Messages
    if action == "check_unread":
        unread, titles = _check_unread_whatsapp()
        if unread > 0:
            _bring_whatsapp_to_front()
            return f"Sir, you have {unread} unread conversation(s) in WhatsApp Desktop. I have brought WhatsApp to the front for you."
        elif titles:
            return "Sir, WhatsApp Desktop is running with no unread messages at the moment."
        else:
            # WhatsApp isn't open; open it to allow syncing
            _open_native_whatsapp("whatsapp:")
            return "Sir, WhatsApp Desktop was closed. I have launched it in the background to check your latest messages."

    # Action: Open WhatsApp Desktop
    if action == "open" and not recipient and not message:
        log("Opening native WhatsApp Desktop…")
        if _open_native_whatsapp("whatsapp:"):
            time.sleep(0.5)
            _bring_whatsapp_to_front()
            unread, _ = _check_unread_whatsapp()
            if unread > 0:
                return f"Sir, I have opened WhatsApp Desktop. You have {unread} unread message(s)."
            return "Sir, I have opened WhatsApp Desktop."
        else:
            webbrowser.open("https://web.whatsapp.com")
            return "Sir, could not launch the native app directly, so I opened WhatsApp Web for you."

    # Action: Send / Draft Message
    if not recipient and not message:
        return "Sir, please tell me the contact name or phone number and the message you would like to send on WhatsApp."

    phone_clean = _clean_phone(recipient) if recipient else ""
    encoded_msg = urllib.parse.quote(message)

    if len(phone_clean) >= 7:
        native_uri = f"whatsapp://send?phone={phone_clean}&text={encoded_msg}"
        fallback_web = f"https://web.whatsapp.com/send?phone={phone_clean}&text={encoded_msg}"
    else:
        native_uri = f"whatsapp://send?text={encoded_msg}"
        fallback_web = f"https://web.whatsapp.com/send?text={encoded_msg}"

    log(f"Opening native WhatsApp for {recipient or 'contact'}…")

    # Priority 1: Native Desktop Application
    if _open_native_whatsapp(native_uri):
        time.sleep(0.8)
        _bring_whatsapp_to_front()
        target_name = recipient if recipient else "your contact"
        return f"Sir, I have opened WhatsApp Desktop to message {target_name}. Your message has been prepared."
    else:
        # Fallback 2: WhatsApp Web in browser
        webbrowser.open(fallback_web)
        target_name = recipient if recipient else "your contact"
        return f"Sir, I opened WhatsApp Web to message {target_name} with your text."
