"""
core/audio_effects.py — Authentic Tony Stark JARVIS Cinematic Sound Design.

Zero-latency, non-blocking acoustic cues synthesized using Windows native
frequency-modulated sound generation (winsound.Beep). Requires no audio assets
or third-party libraries.
"""
from __future__ import annotations

import platform
import threading
import time

_IS_WINDOWS = platform.system() == "Windows"


def _play_async(fn):
    """Executes sound synthesis on an unblocked daemon thread."""
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True, name="StarkAudioSFX")
        t.start()
    return wrapper


@_play_async
def play_wake_chime():
    """High-tech futuristic repulsor chime triggered on 'Hey Jarvis' detection."""
    if not _IS_WINDOWS:
        return
    try:
        import winsound
        # Futuristic ascending triad: A5 -> D6 -> A6
        frequencies = [880, 1175, 1760]
        for f in frequencies:
            winsound.Beep(f, 40)
            time.sleep(0.005)
    except Exception:
        pass


@_play_async
def play_action_blip():
    """Crisp cybernetic servo blip played when dispatching tools/plugins."""
    if not _IS_WINDOWS:
        return
    try:
        import winsound
        # Fast two-tone telemetry click: F#6 -> A#6
        for f in [1480, 1864]:
            winsound.Beep(f, 25)
            time.sleep(0.004)
    except Exception:
        pass


@_play_async
def play_success_chord():
    """Holographic confirmation chord played when a task completes successfully."""
    if not _IS_WINDOWS:
        return
    try:
        import winsound
        # Harmonic C-Major ascending arpeggio: C6 -> E6 -> G6 -> C7
        for f in [1046, 1318, 1568, 2093]:
            winsound.Beep(f, 35)
            time.sleep(0.008)
    except Exception:
        pass


@_play_async
def play_standby_tone():
    """Soft descending power-down tone played when returning to sleep/standby."""
    if not _IS_WINDOWS:
        return
    try:
        import winsound
        # Descending power-down sequence: E6 -> B5 -> E5
        for f in [1318, 987, 659]:
            winsound.Beep(f, 50)
            time.sleep(0.01)
    except Exception:
        pass


@_play_async
def play_alert_tone():
    """Tactical attention pulse for system alerts or proactive notifications."""
    if not _IS_WINDOWS:
        return
    try:
        import winsound
        for _ in range(2):
            winsound.Beep(1200, 60)
            time.sleep(0.03)
    except Exception:
        pass
