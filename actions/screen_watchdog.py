"""
actions/screen_watchdog.py — 24/7 Proactive Visual Screen Watchdog for JARVIS.

Continuously observes screen state using perceptual difference hashing (0 token cost
when idle). When significant changes, error popups, or user queries occur, it inspects
the display via Gemini Vision to provide instant on-demand scene comprehension.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Optional

from core import gemini

_running = False
_thread: Optional[threading.Thread] = None
_lock = threading.Lock()
_interval_sec = 25.0
_last_summary = "Screen observation active. All systems nominal."
_last_thumb = None
_ui_ref = None


def bind_ui(ui):
    global _ui_ref
    _ui_ref = ui


def _compute_diff(img1, img2) -> float:
    """Computes percentage difference between two 64x64 grayscale thumbnails."""
    try:
        import numpy as np
        arr1 = np.array(img1, dtype=np.int16)
        arr2 = np.array(img2, dtype=np.int16)
        diff = np.abs(arr1 - arr2)
        return float(np.mean(diff) / 255.0)
    except Exception:
        return 0.25


def _analyze_screen_now(query: str = "") -> str:
    """Takes a live screenshot and analyzes it using Gemini Vision."""
    global _last_summary
    try:
        import io
        import pyautogui

        shot = pyautogui.screenshot()
        buf = io.BytesIO()
        shot.save(buf, format="JPEG", quality=75)
        img_bytes = buf.getvalue()

        user_inquiry = query.strip() or "Describe what the user is working on, any open applications, active errors, or notable content on screen."
        prompt = f"""You are J.A.R.V.I.S., Tony Stark's personal AI assistant.
Observe the user's computer screen shown in the image.
Task: {user_inquiry}

Provide a concise, direct, spoken-friendly report:
1. Active application(s) and context.
2. Any errors, warnings, code issues, or notable items.
3. Keep it to 2-3 short, clear sentences. Speak directly to the user (e.g. 'Sir, you have...').
"""
        from google.genai import types as gtypes
        part = gtypes.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")

        summary = gemini.text([prompt, part], tier=gemini.FAST, timeout_ms=16000)
        if summary and len(summary.strip()) > 10:
            _last_summary = summary.strip()
            return _last_summary
    except Exception as e:
        print(f"[ScreenWatchdog] Vision analysis error: {e}")

    return "Sir, I observed the screen, but couldn't complete the visual analysis."


def _watchdog_loop():
    global _running, _last_thumb, _last_summary
    import pyautogui
    from PIL import Image

    print("[ScreenWatchdog] 👁️ 24/7 Screen Observer active.")
    while _running:
        try:
            # Low-res thumbnail for zero-cost change detection
            shot = pyautogui.screenshot()
            thumb = shot.resize((64, 64)).convert("L")

            if _last_thumb is not None:
                diff = _compute_diff(_last_thumb, thumb)
                # If significant visual change detected (> 22% change across screen)
                if diff > 0.22:
                    print(f"[ScreenWatchdog] Significant screen change ({diff*100:.1f}%). Updating visual state…")
                    _analyze_screen_now("Check for any compiler errors, critical warnings, or major window switches.")
            _last_thumb = thumb
        except Exception as e:
            print(f"[ScreenWatchdog] Observation loop error: {e}")

        # Sleep interval
        for _ in range(int(_interval_sec)):
            if not _running:
                break
            time.sleep(1.0)

    print("[ScreenWatchdog] Screen Observer stopped.")


def start_watchdog(interval: float = 25.0) -> tuple[bool, str]:
    global _running, _thread, _interval_sec
    with _lock:
        if _running and _thread and _thread.is_alive():
            return True, "24/7 Screen Observer is already running."
        _interval_sec = max(10.0, float(interval))
        _running = True
        _thread = threading.Thread(target=_watchdog_loop, name="ScreenWatchdogThread", daemon=True)
        _thread.start()
        return True, "24/7 Screen Observer activated. I am now continuously monitoring your screen."


def stop_watchdog() -> tuple[bool, str]:
    global _running
    with _lock:
        if not _running:
            return True, "Screen Observer is not active."
        _running = False
        return True, "Screen Observer deactivated."


def screen_watchdog(
    action: str = "inspect",
    query: str = "",
    interval: float = 25.0,
    player=None,
    **kwargs,
) -> str:
    """Action handler to control or query the 24/7 Screen Vision Watchdog."""
    act = (action or "inspect").lower().strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    if act in ("start", "enable", "on", "watch"):
        ok, msg = start_watchdog(interval)
        log(msg)
        return msg

    if act in ("stop", "disable", "off"):
        ok, msg = stop_watchdog()
        log(msg)
        return msg

    if act in ("status",):
        state = "active" if _running else "inactive"
        return f"Screen Watchdog is currently {state}. Last observation: {_last_summary}"

    # On-demand inspect
    log("Inspecting current display frame…")
    report = _analyze_screen_now(query)
    log("Screen inspection complete.")
    return report


# ── Action tool declaration (auto-discovered by core/action_loader.py) ───────
TOOL = {
    "name": "screen_watchdog",
    "description": (
        "24/7 continuous screen vision observer and on-demand screen understanding. "
        "Allows JARVIS to watch your display in the background, detect changes or errors, "
        "and answer questions about what is on screen. "
        "Use whenever the user asks: 'What am I looking at right now?', 'Watch my screen', "
        "'Stop watching screen', 'Read the error on my screen', or in Malayalam: "
        "'ഇപ്പോൾ സ്ക്രീനിൽ എന്താണ് കാണുന്നത്?', 'എന്റെ സ്ക്രീൻ എപ്പോഴും വാച്ച് ചെയ്യൂ', 'സ്ക്രീൻ നോക്കൂ'."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "inspect | start | stop | status (default: inspect)",
            },
            "query": {
                "type": "STRING",
                "description": "Specific question about the screen (e.g. 'What is this error?', 'Summarize this webpage').",
            },
        },
    },
    "handler": screen_watchdog,
}
