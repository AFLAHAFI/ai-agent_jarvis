"""
plugins/spotify_media.py — Windows & Spotify Media Playback Controller.

Controls media playback (Spotify, YouTube, browser media, Windows media player)
via native Windows virtual multimedia key codes.
"""
from __future__ import annotations

import ctypes
import time

# Windows Virtual-Key Codes for Multimedia
VK_MEDIA_NEXT_TRACK = 0xB0  # Next Track
VK_MEDIA_PREV_TRACK = 0xB1  # Previous Track
VK_MEDIA_PLAY_PAUSE = 0xB3  # Play / Pause toggle
VK_VOLUME_MUTE = 0xAD       # Volume Mute
VK_VOLUME_DOWN = 0xAE       # Volume Down
VK_VOLUME_UP = 0xAF         # Volume Up

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002


def _send_media_key(vk_code: int) -> None:
    """Simulates pressing a multimedia key at the OS level."""
    user32 = ctypes.windll.user32
    user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    time.sleep(0.05)
    user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)


PLUGIN = {
    "name": "spotify_media",
    "description": (
        "Controls music and video media playback (Spotify, YouTube, VLC, system media). "
        "Supports actions: 'play', 'pause', 'play_pause', 'next', 'previous', 'mute', "
        "'volume_up', 'volume_down'. Use whenever the user asks to pause/play music, "
        "skip track, go back, or adjust media volume."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "play_pause | play | pause | next | previous | mute | volume_up | volume_down",
            },
        },
        "required": ["action"],
    },
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = str(parameters.get("action", "play_pause")).lower().strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    try:
        if action in ("play", "pause", "play_pause", "toggle"):
            _send_media_key(VK_MEDIA_PLAY_PAUSE)
            msg = "Toggled media playback."
        elif action in ("next", "skip", "forward"):
            _send_media_key(VK_MEDIA_NEXT_TRACK)
            msg = "Skipped to next track."
        elif action in ("previous", "prev", "back"):
            _send_media_key(VK_MEDIA_PREV_TRACK)
            msg = "Returning to previous track."
        elif action in ("mute", "unmute"):
            _send_media_key(VK_VOLUME_MUTE)
            msg = "Toggled audio mute."
        elif action in ("volume_up", "louder"):
            for _ in range(3):
                _send_media_key(VK_VOLUME_UP)
                time.sleep(0.03)
            msg = "Increased media volume."
        elif action in ("volume_down", "quieter"):
            for _ in range(3):
                _send_media_key(VK_VOLUME_DOWN)
                time.sleep(0.03)
            msg = "Decreased media volume."
        else:
            _send_media_key(VK_MEDIA_PLAY_PAUSE)
            msg = f"Executed media command '{action}'."

        log(msg)
        return f"Sir, {msg.lower()}"
    except Exception as e:
        return f"Sir, media control encountered an error: {e}"
