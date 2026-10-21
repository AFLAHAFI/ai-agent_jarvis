"""
plugins/whatsapp_assistant.py — WhatsApp Messaging Assistant.

Sends messages or opens chats via WhatsApp Web / Desktop application
using direct URL protocols.
"""
from __future__ import annotations

import os
import re
import urllib.parse
import webbrowser

PLUGIN = {
    "name": "whatsapp_assistant",
    "description": (
        "Sends a WhatsApp message or opens a WhatsApp chat with a contact or phone number. "
        "Use whenever the user asks to send a WhatsApp message, message someone on WhatsApp, "
        "or open WhatsApp with a draft message."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "recipient": {
                "type": "STRING",
                "description": "Phone number with country code (e.g. '+919876543210' or '9876543210') or contact name.",
            },
            "message": {
                "type": "STRING",
                "description": "The message text to send.",
            },
        },
        "required": ["recipient", "message"],
    },
}


def _clean_phone(raw: str) -> str:
    """Strips formatting from phone number while preserving digits and leading '+'."""
    digits = re.sub(r"[^\d+]", "", raw.strip())
    if digits.startswith("+"):
        digits = digits[1:]
    return digits


def run(parameters: dict, player=None, session_memory=None) -> str:
    recipient = str(parameters.get("recipient", "")).strip()
    message = str(parameters.get("message", "")).strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    if not recipient:
        return "Sir, please specify who you would like to message on WhatsApp."

    phone_clean = _clean_phone(recipient)
    encoded_msg = urllib.parse.quote(message)

    try:
        # If valid digits found, use direct phone link
        if len(phone_clean) >= 7:
            wa_url = f"https://web.whatsapp.com/send?phone={phone_clean}&text={encoded_msg}"
        else:
            # Fallback search / general text draft
            wa_url = f"https://web.whatsapp.com/send?text={encoded_msg}"

        log(f"Opening WhatsApp for {recipient}…")
        webbrowser.open(wa_url)

        return f"Sir, I have opened WhatsApp to message {recipient} with your text."
    except Exception as e:
        return f"Sir, could not open WhatsApp: {e}"
