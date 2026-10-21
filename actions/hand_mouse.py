"""
actions/hand_mouse.py — Real-time Webcam Hand Tracking & Gesture Mouse Controller.

Features:
  1. Optical Hand & Finger Tracking: Uses Google MediaPipe HandLandmarker to track 21 hand landmarks in real time.
  2. Index Finger Cursor Control: Points with index fingertip (landmark 8) to steer the mouse across the screen.
  3. Pinch-to-Click & Drag: Pinch index finger and thumb together (< 0.05 distance) to left-click or drag-and-drop.
  4. Middle-Finger Pinch for Right Click: Pinch middle finger and thumb together to trigger a right-click.
  5. Exponential Moving Average (EMA): Filters out micro-jitters for buttery smooth mouse motion.
  6. Non-Blocking Background Daemon: Operates in a dedicated thread without lagging UI or audio pipelines.
  7. Voice Control: "Enable hand tracking", "Disable hand tracking", "Turn on hand mouse".
"""
from __future__ import annotations

import json
import math
import os
import threading
import time
import urllib.request
import winsound
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
import pyautogui

from core import outcome

# Safety settings for PyAutoGUI
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001


def _load_camera_index() -> int:
    config_path = Path(__file__).resolve().parent.parent / "config" / "api_keys.json"
    try:
        if config_path.exists():
            data = json.loads(config_path.read_text(encoding="utf-8"))
            return int(data.get("camera_index", 0))
    except Exception:
        pass
    return 0


def _get_model_path() -> Path:
    base = Path(__file__).resolve().parent.parent / "config"
    base.mkdir(parents=True, exist_ok=True)
    target = base / "hand_landmarker.task"
    if not target.exists() or target.stat().st_size < 1_000_000:
        url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        try:
            print("[HandMouse] Downloading hand_landmarker.task model…")
            urllib.request.urlretrieve(url, str(target))
        except Exception as e:
            print(f"[HandMouse] Model download error: {e}")
    return target


class HandMouseController:
    """Singleton background thread for real-time hand gesture mouse control."""

    _instance: Optional[HandMouseController] = None
    _lock = threading.Lock()

    def __new__(cls) -> HandMouseController:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_state()
            return cls._instance

    def _init_state(self) -> None:
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.camera_index = _load_camera_index()
        self.screen_w, self.screen_h = pyautogui.size()

        # Smoothing & Calibration
        self.alpha = 0.35  # EMA factor for responsive, smooth motion
        self.curr_x: float = float(self.screen_w / 2)
        self.curr_y: float = float(self.screen_h / 2)

        # Gesture State
        self.is_pinching = False
        self.is_middle_pinching = False
        self.last_click_time = 0.0

    def is_active(self) -> bool:
        return self.running and self.thread is not None and self.thread.is_alive()

    def start(self) -> tuple[bool, str]:
        with self._lock:
            if self.is_active():
                return True, "Hand tracking is already active."

            self.running = True
            self.thread = threading.Thread(target=self._run_loop, name="HandMouseThread", daemon=True)
            self.thread.start()
            return True, "Hand tracking mouse control started successfully."

    def stop(self) -> tuple[bool, str]:
        with self._lock:
            if not self.running:
                return True, "Hand tracking is not currently running."
            self.running = False
            if self.is_pinching:
                try:
                    pyautogui.mouseUp(button="left")
                except Exception:
                    pass
                self.is_pinching = False
            return True, "Hand tracking mouse control stopped."

    def _run_loop(self) -> None:
        import mediapipe as mp
        from mediapipe.tasks import python
        from mediapipe.tasks.python import vision

        model_path = _get_model_path()
        if not model_path.exists():
            print(f"[HandMouse] ❌ Model file missing at {model_path}")
            self.running = False
            return

        base_options = python.BaseOptions(model_asset_path=str(model_path))
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.55,
            min_hand_presence_confidence=0.55,
            min_tracking_confidence=0.55,
        )

        try:
            detector = vision.HandLandmarker.create_from_options(options)
        except Exception as e:
            print(f"[HandMouse] Failed to create HandLandmarker: {e}")
            self.running = False
            return

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print(f"[HandMouse] ⚠️ Could not open camera {self.camera_index}")
            self.running = False
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Active boundary in camera frame (percentage 0.0 to 1.0)
        margin_x_min, margin_x_max = 0.15, 0.85
        margin_y_min, margin_y_max = 0.15, 0.82

        mx, my = pyautogui.position()
        self.curr_x, self.curr_y = float(mx), float(my)

        print("[HandMouse] 🖐️ Hand tracking active. Point with index finger, pinch to click!")

        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                time.sleep(0.02)
                continue

            # Mirror frame horizontally so hand moves naturally
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            try:
                detection_result = detector.detect(mp_img)
            except Exception:
                time.sleep(0.01)
                continue

            if detection_result.hand_landmarks and len(detection_result.hand_landmarks) > 0:
                landmarks = detection_result.hand_landmarks[0]

                # Key landmarks:
                # 4 = Thumb tip, 8 = Index finger tip, 12 = Middle finger tip
                thumb = landmarks[4]
                index = landmarks[8]
                middle = landmarks[12]

                # 1. Cursor Navigation (Index Finger Tip)
                # Normalize within active margins
                norm_x = (index.x - margin_x_min) / (margin_x_max - margin_x_min)
                norm_y = (index.y - margin_y_min) / (margin_y_max - margin_y_min)

                # Clamp 0.0 to 1.0
                norm_x = max(0.0, min(1.0, norm_x))
                norm_y = max(0.0, min(1.0, norm_y))

                target_x = norm_x * self.screen_w
                target_y = norm_y * self.screen_h

                # Exponential smoothing
                self.curr_x = (self.alpha * target_x) + ((1.0 - self.alpha) * self.curr_x)
                self.curr_y = (self.alpha * target_y) + ((1.0 - self.alpha) * self.curr_y)

                try:
                    pyautogui.moveTo(int(self.curr_x), int(self.curr_y))
                except Exception:
                    pass

                # 2. Left Click / Drag (Index Tip to Thumb Tip pinch)
                pinch_dist = math.hypot(index.x - thumb.x, index.y - thumb.y)

                if pinch_dist < 0.052:
                    if not self.is_pinching:
                        try:
                            pyautogui.mouseDown(button="left")
                            winsound.MessageBeep(winsound.MB_ICONASTERISK)
                            self.is_pinching = True
                            self.last_click_time = time.time()
                        except Exception as e:
                            print(f"[HandMouse] Mouse down error: {e}")
                else:
                    if self.is_pinching:
                        try:
                            pyautogui.mouseUp(button="left")
                            self.is_pinching = False
                        except Exception as e:
                            print(f"[HandMouse] Mouse up error: {e}")

                # 3. Right Click (Middle Tip to Thumb Tip pinch)
                middle_dist = math.hypot(middle.x - thumb.x, middle.y - thumb.y)
                if middle_dist < 0.050:
                    if not self.is_middle_pinching:
                        now = time.time()
                        if now - self.last_click_time > 0.4:
                            try:
                                pyautogui.rightClick()
                                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                                self.is_middle_pinching = True
                                self.last_click_time = now
                            except Exception as e:
                                print(f"[HandMouse] Right click error: {e}")
                else:
                    if middle_dist > 0.070:
                        self.is_middle_pinching = False

            else:
                # Hand lost - release any active drag
                if self.is_pinching:
                    try:
                        pyautogui.mouseUp(button="left")
                    except Exception:
                        pass
                    self.is_pinching = False

            time.sleep(0.016)  # ~60 fps cap

        cap.release()
        if self.is_pinching:
            try:
                pyautogui.mouseUp(button="left")
            except Exception:
                pass
        print("[HandMouse] Camera released. Controller stopped.")


_controller = HandMouseController()


def hand_mouse(
    action: str = "enable",
    player=None,
    **kwargs,
) -> str:
    """Action handler to enable, disable, or query the hand tracking mouse controller."""
    act = (action or "enable").lower().strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    if act in ("enable", "start", "on"):
        ok, msg = _controller.start()
        log("Hand-tracking mouse enabled. Point with index finger, pinch to click.")
        return outcome.done(
            "hand_mouse",
            status="active",
            message="Hand tracking enabled. Point with your index finger to move the mouse, and pinch your index and thumb together to click.",
        )

    if act in ("disable", "stop", "off"):
        ok, msg = _controller.stop()
        log("Hand-tracking mouse disabled.")
        return outcome.done(
            "hand_mouse",
            status="inactive",
            message="Hand tracking mouse control disabled.",
        )

    if act in ("toggle",):
        if _controller.is_active():
            _controller.stop()
            log("Hand-tracking mouse turned off.")
            return outcome.done("hand_mouse", status="inactive")
        else:
            _controller.start()
            log("Hand-tracking mouse turned on.")
            return outcome.done("hand_mouse", status="active")

    active = _controller.is_active()
    return outcome.done("hand_mouse", active=active)


TOOL = {
    "name": "hand_mouse",
    "description": (
        "Controls the mouse cursor in real-time using webcam hand and finger gesture tracking. "
        "Point with your index finger to move the cursor smoothly across the screen, "
        "and pinch your index finger and thumb together to click or drag. "
        "Pinch middle finger and thumb for right-click. "
        "Use action='enable' when the user asks to control the mouse with hand gestures, "
        "turn on hand tracking, or enable hand mouse. "
        "Use action='disable' when the user asks to turn off, disable, or stop hand tracking."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "enable | disable | toggle | status",
            },
        },
        "required": ["action"],
    },
    "handler": hand_mouse,
}
