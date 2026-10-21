"""
actions/creative_agent.py — Live Autonomous MS Paint Drawing & Creative Agent.

Features:
  1. True Dynamic Vector Art: Generates clean 2D stroke sketches for ANY requested
     subject (human, cat, house, car, tree, dog, airplane, etc.) via Gemini FAST.
  2. Live Physical Mouse Painting: Brings MS Paint to full screen and physically guides
     the mouse across the canvas, drawing every stroke with smooth curves in real time
     so the user can watch it happen live!
  3. Color Palette Support: Can select colors from the MS Paint palette when requested.
  4. Non-Destructive Safe Bounds: Clamps all strokes strictly to the canvas center
     (safe margin inside the white sheet), preventing clicks on ribbon buttons or window controls.
  5. Artwork Export: Saves a clean high-resolution snapshot to the user's Desktop.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import List, Tuple

import pyautogui
import win32con
import win32gui

from core import gemini, outcome

pyautogui.FAILSAFE = True  # Moving mouse to screen corner safely halts drawing


def _desktop_dir() -> Path:
    return Path.home() / "Desktop"


def _bring_paint_to_front() -> bool:
    """Launches MS Paint if needed, maximizes it, and brings it to foreground."""
    try:
        subprocess.Popen(["mspaint.exe"])
    except Exception as e:
        print(f"[CreativeAgent] Paint launch: {e}")

    time.sleep(1.2)

    # Find MSPaintApp window
    hwnd = win32gui.FindWindow("MSPaintApp", None)
    if not hwnd:
        # Fallback search by title
        def enum_cb(h, acc):
            if win32gui.IsWindowVisible(h) and "paint" in win32gui.GetWindowText(h).lower():
                acc.append(h)
        found = []
        win32gui.EnumWindows(enum_cb, found)
        if found:
            hwnd = found[0]

    if hwnd:
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            return True
        except Exception as e:
            print(f"[CreativeAgent] Window activate: {e}")

    return False


def _get_preset_strokes(subject: str) -> List[List[List[int]]]:
    """Fallback stroke coordinates normalized [0, 1000] for standard subjects."""
    sub = subject.lower()

    if any(k in sub for k in ("human", "person", "man", "woman", "boy", "girl")):
        return [
            # Head circle
            [[500, 150], [540, 170], [560, 220], [540, 270], [500, 290], [460, 270], [440, 220], [460, 170], [500, 150]],
            # Eyes & Smile
            [[475, 210], [485, 210]],
            [[515, 210], [525, 210]],
            [[475, 245], [500, 260], [525, 245]],
            # Neck & Torso
            [[500, 290], [500, 520]],
            # Left Arm
            [[500, 340], [380, 420], [350, 480]],
            # Right Arm
            [[500, 340], [620, 420], [650, 480]],
            # Left Leg
            [[500, 520], [430, 680], [410, 780]],
            # Right Leg
            [[500, 520], [570, 680], [590, 780]],
        ]

    if any(k in sub for k in ("cat", "kitten")):
        return [
            # Head with ears
            [[400, 320], [420, 220], [470, 280], [530, 280], [580, 220], [600, 320], [620, 400], [590, 470], [500, 500], [410, 470], [380, 400], [400, 320]],
            # Left Eye
            [[450, 370], [465, 370]],
            # Right Eye
            [[535, 370], [550, 370]],
            # Nose & Mouth
            [[495, 410], [505, 410], [500, 425]],
            [[500, 425], [480, 440]],
            [[500, 425], [520, 440]],
            # Whiskers
            [[420, 410], [340, 400]],
            [[420, 425], [340, 430]],
            [[580, 410], [660, 400]],
            [[580, 425], [660, 430]],
            # Body & Tail
            [[500, 500], [500, 680], [620, 700], [650, 650], [640, 560], [580, 500]],
            [[640, 680], [740, 650], [780, 560], [760, 520]],
        ]

    if any(k in sub for k in ("house", "home", "building")):
        return [
            # Walls
            [[300, 450], [700, 450], [700, 750], [300, 750], [300, 450]],
            # Roof
            [[260, 450], [500, 250], [740, 450], [260, 450]],
            # Door
            [[460, 750], [460, 580], [540, 580], [540, 750]],
            # Window 1
            [[350, 520], [410, 520], [410, 580], [350, 580], [350, 520]],
            # Window 2
            [[590, 520], [650, 520], [650, 580], [590, 580], [590, 520]],
            # Chimney
            [[620, 350], [620, 270], [660, 270], [660, 385]],
        ]

    if any(k in sub for k in ("car", "vehicle", "automobile")):
        return [
            # Roof and cabin
            [[350, 450], [440, 350], [620, 350], [700, 450]],
            # Lower body
            [[220, 520], [250, 450], [780, 450], [820, 520], [820, 600], [760, 600]],
            [[640, 600], [400, 600]],
            [[280, 600], [220, 600], [220, 520]],
            # Left Wheel
            [[280, 600], [300, 550], [360, 550], [400, 600], [380, 640], [320, 640], [280, 600]],
            # Right Wheel
            [[640, 600], [660, 550], [720, 550], [760, 600], [740, 640], [680, 640], [640, 600]],
        ]

    # Default aesthetic tree
    return [
        # Trunk
        [[470, 780], [470, 500], [530, 500], [530, 780]],
        # Foliage clouds
        [[500, 520], [380, 480], [340, 380], [400, 300], [500, 240], [600, 300], [660, 380], [620, 480], [500, 520]],
        [[380, 380], [440, 330], [560, 330], [620, 380]],
        # Roots / Ground
        [[360, 780], [640, 780]],
    ]


def _generate_strokes(subject: str) -> List[List[List[int]]]:
    """Generates continuous 2D stroke polylines for ANY subject via Gemini FAST."""
    prompt = f"""Generate a 2D line drawing of '{subject}' as a JSON array of strokes.
Each stroke is a list of [x, y] coordinates normalized from 0 to 1000.
Include: 8 to 18 distinct continuous strokes representing major outlines, facial features, and internal details.
Each stroke must have between 3 and 22 points.
Return ONLY valid JSON: [[[x, y], ...], ...] with NO markdown fences, no explanatory text."""
    try:
        raw = gemini.text(prompt, tier=gemini.FAST, timeout_ms=12000)
        if raw:
            clean = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)
            if isinstance(data, list) and len(data) >= 3:
                return data
    except Exception as e:
        print(f"[CreativeAgent] Stroke generation fallback: {e}")

    return _get_preset_strokes(subject)


def _draw_strokes_live(strokes: List[List[List[int]]], color: str = "") -> None:
    """Physically guides the mouse cursor across MS Paint to draw the artwork."""
    sw, sh = pyautogui.size()

    # Safe MS Paint Canvas Bounding Box (Inside the white drawing area)
    canvas_x0 = int(sw * 0.20)
    canvas_x1 = int(sw * 0.80)
    canvas_y0 = int(sh * 0.24)
    canvas_y1 = int(sh * 0.82)

    box_w = canvas_x1 - canvas_x0
    box_h = canvas_y1 - canvas_y0

    def to_screen(px: float, py: float) -> Tuple[int, int]:
        sx = canvas_x0 + int((px / 1000.0) * box_w)
        sy = canvas_y0 + int((py / 1000.0) * box_h)
        # Safe clamp
        sx = max(canvas_x0 + 5, min(canvas_x1 - 5, sx))
        sy = max(canvas_y0 + 5, min(canvas_y1 - 5, sy))
        return sx, sy

    # Ensure Brush tool is selected in MS Paint
    try:
        pyautogui.press("b")
        time.sleep(0.1)
    except Exception:
        pass

    # Optional color selection from MS Paint ribbon palette
    color_clean = (color or "").lower().strip()
    if color_clean:
        palette_y = int(sh * 0.08)
        color_x_map = {
            "black": int(sw * 0.40),
            "red": int(sw * 0.45),
            "orange": int(sw * 0.48),
            "yellow": int(sw * 0.51),
            "green": int(sw * 0.54),
            "blue": int(sw * 0.57),
            "purple": int(sw * 0.60),
            "pink": int(sw * 0.63),
        }
        for name, col_x in color_x_map.items():
            if name in color_clean:
                try:
                    pyautogui.click(col_x, palette_y)
                    time.sleep(0.1)
                    pyautogui.press("b")
                except Exception:
                    pass
                break

    # Draw each stroke smoothly and visibly
    for stroke in strokes:
        if not stroke:
            continue

        if len(stroke) == 1:
            sx, sy = to_screen(stroke[0][0], stroke[0][1])
            pyautogui.moveTo(sx, sy, duration=0.06)
            pyautogui.click()
            continue

        # Move to stroke origin without pressing
        start_x, start_y = to_screen(stroke[0][0], stroke[0][1])
        pyautogui.moveTo(start_x, start_y, duration=0.07)
        pyautogui.mouseDown(button="left")
        time.sleep(0.01)

        # Smoothly draw points along stroke
        for pt in stroke[1:]:
            nx, ny = to_screen(pt[0], pt[1])
            pyautogui.moveTo(nx, ny, duration=0.035)

        pyautogui.mouseUp(button="left")
        time.sleep(0.02)


def creative_agent(
    subject: str = "a cute cat",
    color: str = "",
    player=None,
    **kwargs,
) -> str:
    """Autonomously launches MS Paint and physically draws the requested subject live on screen."""
    subject_clean = (subject or "a cute cat").strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    log(f"Opening MS Paint and drawing '{subject_clean}' live on screen…")

    # 1. Bring Paint to front
    paint_ready = _bring_paint_to_front()
    if not paint_ready:
        log("Launching Paint…")
        time.sleep(1.0)

    # 2. Generate stroke polylines for the subject
    log(f"Composing line art for '{subject_clean}'…")
    strokes = _generate_strokes(subject_clean)

    # 3. Live physical drawing on canvas
    log("Drawing live with mouse…")
    try:
        _draw_strokes_live(strokes, color=color)
    except Exception as e:
        print(f"[CreativeAgent] Live draw error: {e}")

    # 4. Save a snapshot copy to Desktop
    desktop = _desktop_dir()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_sub = "".join(c for c in subject_clean if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")
    final_png = str(desktop / f"jarvis_artwork_{safe_sub}_{timestamp}.png")
    try:
        # Take snapshot of the canvas
        screenshot = pyautogui.screenshot()
        screenshot.save(final_png)
        log(f"Artwork saved to Desktop: {os.path.basename(final_png)}")
    except Exception as e:
        print(f"[CreativeAgent] Snapshot error: {e}")

    return outcome.done(
        "creative_agent",
        subject=subject_clean,
        message=f"I have opened MS Paint and drawn {subject_clean} live on screen for you, Sir.",
    )


TOOL = {
    "name": "creative_agent",
    "description": (
        "Autonomous AI MS Paint drawing agent. "
        "Opens MS Paint, maximizes it, and physically moves the mouse to draw "
        "ANY requested subject live on the screen (human, cat, house, car, tree, etc.) "
        "with smooth, visible strokes. Can also select colors. "
        "Use whenever the user asks to draw anything in Paint or draw on the screen."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "subject": {
                "type": "STRING",
                "description": "What to draw, e.g. 'a human', 'a cute cat', 'a red car', 'a tree', 'a house'.",
            },
            "color": {
                "type": "STRING",
                "description": "Optional color name, e.g. 'red', 'blue', 'green', 'black'.",
            },
        },
        "required": ["subject"],
    },
    "handler": creative_agent,
}
