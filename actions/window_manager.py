"""
actions/window_manager.py — Smart Multi-Window & Desktop Workspace Controller.

Provides window focus, dual-pane snapping (left/right half), and desktop decluttering
using Windows User32 and Win32GUI APIs.
"""
from __future__ import annotations

import ctypes
import platform
from typing import Optional

_IS_WINDOWS = platform.system() == "Windows"

if _IS_WINDOWS:
    import win32con
    import win32gui
    import win32process

_ui_ref = None


def bind_ui(ui):
    global _ui_ref
    _ui_ref = ui


def _find_window_by_query(query: str) -> Optional[int]:
    """Finds top-level visible window matching a process name or window title."""
    if not _IS_WINDOWS:
        return None

    query_lower = query.lower().strip()
    matched_hwnds = []

    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd).strip()
            if title:
                # Match title
                if query_lower in title.lower():
                    matched_hwnds.append((hwnd, title, 2))
                else:
                    # Match process name
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        import psutil
                        proc = psutil.Process(pid)
                        if query_lower in proc.name().lower():
                            matched_hwnds.append((hwnd, title, 1))
                    except Exception:
                        pass
        return True

    try:
        win32gui.EnumWindows(enum_cb, None)
    except Exception:
        pass

    if not matched_hwnds:
        return None

    # Sort by priority score then length
    matched_hwnds.sort(key=lambda x: (x[2], -len(x[1])), reverse=True)
    return matched_hwnds[0][0]


def _get_work_area() -> tuple[int, int, int, int]:
    """Retrieves usable desktop screen area excluding the Windows taskbar."""
    user32 = ctypes.windll.user32
    class RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                    ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
    rect = RECT()
    SPI_GETWORKAREA = 0x0030
    user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top


def window_manager(
    action: str = "focus",
    app_name: str = "",
    side: str = "left",
    player=None,
    **kwargs,
) -> str:
    """Action handler to focus, snap, or organize application windows."""
    act = (action or "focus").lower().strip()
    app = (app_name or "").strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    if not _IS_WINDOWS:
        return "Window management is currently supported on Windows systems."

    if not app and act not in ("minimize_all", "show_desktop", "mini_hud", "full_hud", "switch_hud"):
        return "Please specify the application or window name (e.g. 'Chrome', 'WhatsApp', 'VS Code')."

    if act in ("mini_hud", "switch_hud", "mini_mode"):
        mode = (side or app or "mini").lower()
        if _ui_ref:
            _ui_ref.switch_mode(mode)
            desc = "Mini Assistant Companion" if mode in ("mini", "compact", "small") else "Full Stark Arc Reactor HUD"
            return f"Switched interface to {desc}."
        return "UI handle not bound."

    if act in ("full_hud", "restore_hud"):
        if _ui_ref:
            _ui_ref.switch_mode("full")
            return "Restored full Stark Arc Reactor HUD."
        return "UI handle not bound."

    if act in ("preset", "workspace"):
        preset_name = (app or side or "coding").lower()
        x, y, w, h = _get_work_area()
        if preset_name in ("coding", "code", "dev"):
            code_hwnd = _find_window_by_query("code") or _find_window_by_query("visual studio")
            chrome_hwnd = _find_window_by_query("chrome") or _find_window_by_query("edge")
            if code_hwnd:
                win32gui.ShowWindow(code_hwnd, win32con.SW_RESTORE)
                win32gui.MoveWindow(code_hwnd, x, y, int(w * 0.55), h, True)
                win32gui.SetForegroundWindow(code_hwnd)
            if chrome_hwnd:
                win32gui.ShowWindow(chrome_hwnd, win32con.SW_RESTORE)
                win32gui.MoveWindow(chrome_hwnd, x + int(w * 0.55), y, int(w * 0.45), h, True)
            return "Activated Coding Workspace preset (VS Code on left, browser on right)."
        elif preset_name in ("research", "study"):
            chrome_hwnd = _find_window_by_query("chrome") or _find_window_by_query("edge")
            doc_hwnd = _find_window_by_query("word") or _find_window_by_query("notepad") or _find_window_by_query("pdf")
            if chrome_hwnd:
                win32gui.ShowWindow(chrome_hwnd, win32con.SW_RESTORE)
                win32gui.MoveWindow(chrome_hwnd, x, y, w // 2, h, True)
                win32gui.SetForegroundWindow(chrome_hwnd)
            if doc_hwnd:
                win32gui.ShowWindow(doc_hwnd, win32con.SW_RESTORE)
                win32gui.MoveWindow(doc_hwnd, x + (w // 2), y, w // 2, h, True)
            return "Activated Research Workspace preset (Browser on left, document on right)."

    hwnd = _find_window_by_query(app) if app else None

    # 1. Focus Application Window
    if act in ("focus", "bring_to_front", "activate"):
        if not hwnd:
            return f"I couldn't find an open window for '{app}'. Make sure the application is running."

        try:
            # Restore if minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

            # Bring to foreground
            win32gui.SetForegroundWindow(hwnd)
            title = win32gui.GetWindowText(hwnd)
            log(f"Focused window: {title[:40]}")
            return f"Focused '{title[:35]}'."
        except Exception as e:
            return f"Could not focus '{app}': {e}"

    # 2. Minimize All Windows Except Target
    if act in ("minimize_all_except", "isolate"):
        if not hwnd:
            return f"I couldn't find an open window for '{app}' to isolate."

        count = 0
        def min_cb(h, _):
            nonlocal count
            if h != hwnd and win32gui.IsWindowVisible(h):
                t = win32gui.GetWindowText(h).strip()
                if t and not win32gui.IsIconic(h):
                    try:
                        win32gui.ShowWindow(h, win32con.SW_MINIMIZE)
                        count += 1
                    except Exception:
                        pass
            return True

        win32gui.EnumWindows(min_cb, None)
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass
        return f"Minimized {count} background window(s). Isolated '{app}' on screen."

    # 3. Snap Window to Left or Right Half
    if act in ("snap", "tile", "split"):
        if not hwnd:
            return f"I couldn't find an open window for '{app}' to snap."

        x, y, w, h = _get_work_area()
        s = side.lower().strip()

        # Restore from maximized/minimized state first
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        if s in ("left", "l"):
            # Left 50%
            new_x, new_y, new_w, new_h = x, y, w // 2, h
            pos_desc = "left half"
        elif s in ("right", "r"):
            # Right 50%
            new_x, new_y, new_w, new_h = x + (w // 2), y, w // 2, h
            pos_desc = "right half"
        elif s in ("maximize", "max"):
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return f"Maximized '{app}'."
        elif s in ("minimize", "min"):
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return f"Minimized '{app}'."
        else:
            new_x, new_y, new_w, new_h = x, y, w // 2, h
            pos_desc = "left half"

        try:
            win32gui.MoveWindow(hwnd, new_x, new_y, new_w, new_h, True)
            win32gui.SetForegroundWindow(hwnd)
            log(f"Snapped '{app}' to {pos_desc}.")
            return f"Snapped '{app}' to the {pos_desc} of the screen."
        except Exception as e:
            return f"Could not snap window: {e}"

    if act in ("minimize_all", "show_desktop"):
        ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)  # Win key down
        ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)  # 'D' key down
        ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)  # 'D' key up
        ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)  # Win key up
        return "Minimized all windows and showed desktop."

    return "Available window actions: 'focus', 'snap' (left/right/maximize), 'minimize_all_except'."


# ── Action tool declaration (auto-discovered by core/action_loader.py) ───────
TOOL = {
    "name": "window_manager",
    "description": (
        "Controls application windows and desktop workspace: focuses apps, snaps windows to the left or right, "
        "toggles between full Stark HUD and Mini Assistant Companion HUD (e.g. 'Switch to mini HUD', 'മിനി ഹബ്ബിലോട്ട് മാറ്', 'Open full HUD'), "
        "minimizes background windows, or activates workspace presets (e.g. 'Coding workspace', 'Research workspace')."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "focus | snap | mini_hud | full_hud | preset | minimize_all_except | minimize_all",
            },
            "app_name": {
                "type": "STRING",
                "description": "The name or title of the app (e.g. 'Chrome', 'WhatsApp', 'VS Code', 'Paint') or preset name ('coding', 'research').",
            },
            "side": {
                "type": "STRING",
                "description": "left | right | maximize | minimize | mini | full",
            },
        },
        "required": ["action"],
    },
    "handler": window_manager,
}
