"""
plugins/whatsapp_assistant.py — Native WhatsApp Desktop Assistant.

Sends messages, opens chats, checks unread messages, and visually clicks specific
conversations via the native Windows WhatsApp Desktop application.
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
        "Controls the native WhatsApp Desktop application on Windows with visual screen clicking. "
        "Actions: 'send' (send a message to a contact/phone), 'open' (open WhatsApp Desktop), "
        "'check_unread' (inspect unread conversation count), "
        "'open_chat' (visually click or search and open a specific contact's chat), "
        "or 'open_unread' (visually click and open the newest unread message on screen). "
        "Always prefers the native Windows desktop app over the web browser."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "send | open | check_unread | open_chat | open_unread",
            },
            "recipient": {
                "type": "STRING",
                "description": "Phone number with country code (e.g. '+919876543210' or '9876543210') or contact name (e.g. 'Amjad Ali').",
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


def _visual_click_whatsapp(description: str) -> bool:
    """Uses vision-based screen finding to click an element in WhatsApp."""
    try:
        from actions.computer_control import _screen_find, _click
        coords = _screen_find(description)
        if coords:
            time.sleep(0.15)
            _click(x=coords[0], y=coords[1])
            return True
    except Exception as e:
        print(f"[WhatsApp] Visual click error: {e}")
    return False


def _search_and_open_chat(contact_name: str) -> bool:
    """Uses native WhatsApp keyboard navigation to search and open a conversation."""
    try:
        import pyautogui
        import pyperclip
        _bring_whatsapp_to_front()
        time.sleep(0.3)
        # Ctrl + F to focus search in WhatsApp Desktop
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.2)
        pyperclip.copy(contact_name)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
        pyautogui.press("enter")
        return True
    except Exception as e:
        print(f"[WhatsApp] Search & open error: {e}")
        return False


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = str(parameters.get("action", "")).strip().lower()
    recipient = str(parameters.get("recipient", "")).strip()
    message = str(parameters.get("message", "")).strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    # Auto-detect action if not specified
    if not action:
        if message:
            action = "send"
        elif recipient:
            action = "open_chat"
        else:
            action = "open"

    # Action: Open a specific chat or contact
    if action in ("open_chat", "click_chat", "find_chat"):
        if not recipient:
            return "Sir, which contact's chat would you like me to open on WhatsApp?"
        log(f"Opening chat for {recipient}…")
        _open_native_whatsapp("whatsapp:")
        time.sleep(0.6)
        _bring_whatsapp_to_front()
        time.sleep(0.4)
        # 1. Vision click on chat item
        if _visual_click_whatsapp(f"chat item with {recipient} in WhatsApp"):
            return f"Sir, I visually located and opened your chat with {recipient} in WhatsApp."
        # 2. Native search & jump
        if _search_and_open_chat(recipient):
            return f"Sir, I searched and opened your chat with {recipient} in WhatsApp Desktop."
        return f"Sir, I opened WhatsApp Desktop but could not locate {recipient}."

    # Action: Open newest unread message
    if action in ("open_unread", "click_unread"):
        log("Opening newest unread WhatsApp message…")
        _open_native_whatsapp("whatsapp:")
        time.sleep(0.6)
        _bring_whatsapp_to_front()
        time.sleep(0.4)
        # Vision click on unread green badge or top unread chat
        if (_visual_click_whatsapp("green unread circle badge in WhatsApp chat list") or
            _visual_click_whatsapp("top unread chat row in WhatsApp")):
            return "Sir, I have visually located and opened your newest unread WhatsApp message."
        else:
            # Fallback keyboard navigation
            try:
                import pyautogui
                pyautogui.hotkey("ctrl", "f")
                time.sleep(0.2)
                pyautogui.press("escape")
                time.sleep(0.2)
                pyautogui.press("down")
                pyautogui.press("enter")
                return "Sir, I navigated to your latest WhatsApp chat on screen."
            except Exception:
                return "Sir, I opened WhatsApp Desktop for you."

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
        # Check contact memory for phone number
        try:
            from memory.memory_manager import get_contact
            c = get_contact(recipient)
            if c and c.get("phone"):
                phone_clean = _clean_phone(c["phone"])
                native_uri = f"whatsapp://send?phone={phone_clean}&text={encoded_msg}"
                fallback_web = f"https://web.whatsapp.com/send?phone={phone_clean}&text={encoded_msg}"
            else:
                native_uri = f"whatsapp://send?text={encoded_msg}"
                fallback_web = f"https://web.whatsapp.com/send?text={encoded_msg}"
        except Exception:
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
