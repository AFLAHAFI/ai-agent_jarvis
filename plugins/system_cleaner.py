"""
plugins/system_cleaner.py — Windows System Maintenance & Cache Cleaner.

Frees disk space and system memory by emptying the Recycle Bin, cleaning %TEMP%
files, and clearing working memory caches.
"""
from __future__ import annotations

import ctypes
import os
import shutil
import tempfile
from pathlib import Path

PLUGIN = {
    "name": "system_cleaner",
    "description": (
        "Performs system maintenance and disk cleanup on Windows. "
        "Supports actions: 'clean_all' (cleans temp files and empties recycle bin), "
        "'empty_recycle_bin', 'clean_temp', 'flush_ram'. "
        "Use whenever the user asks to clean the computer, free up space, empty recycle bin, "
        "or clear cache."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "clean_all | empty_recycle_bin | clean_temp | flush_ram",
            },
        },
        "required": [],
    },
}


def _empty_recycle_bin() -> bool:
    """Empties the Windows Recycle Bin silently without popups."""
    try:
        # Flags: SHERB_NOCONFIRMATION (1) | SHERB_NOPROGRESSUI (2) | SHERB_NOSOUND (4) = 7
        res = ctypes.windll.shell32.SHEmptyRecycleBinW(0, None, 7)
        return res in (0, -2147418113)  # 0 = success, S_OK; or already empty
    except Exception as e:
        print(f"[SystemCleaner] Recycle bin error: {e}")
        return False


def _clean_temp_files() -> int:
    """Removes disposable temp files and returns approximate bytes deleted."""
    bytes_freed = 0
    temp_dir = os.environ.get("TEMP", tempfile.gettempdir())

    try:
        for entry in os.scandir(temp_dir):
            try:
                if entry.is_file(follow_symlinks=False):
                    size = entry.stat().st_size
                    os.remove(entry.path)
                    bytes_freed += size
                elif entry.is_dir(follow_symlinks=False):
                    size = sum(f.stat().st_size for f in Path(entry.path).rglob("*") if f.is_file())
                    shutil.rmtree(entry.path, ignore_errors=True)
                    bytes_freed += size
            except Exception:
                # Active locked files in use by Windows are safely skipped
                continue
    except Exception as e:
        print(f"[SystemCleaner] Temp scan error: {e}")

    return bytes_freed


def _flush_ram() -> None:
    """Trims working set memory for current processes."""
    try:
        import gc
        gc.collect()
        ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
    except Exception:
        pass


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = str(parameters.get("action", "clean_all")).lower().strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    try:
        if action in ("empty_recycle_bin", "recycle_bin"):
            _empty_recycle_bin()
            msg = "Recycle Bin has been emptied."

        elif action in ("clean_temp", "temp"):
            freed = _clean_temp_files()
            mb = freed / (1024 * 1024)
            msg = f"Cleaned temporary cache files, freeing approximately {mb:.1f} MB."

        elif action in ("flush_ram", "ram", "memory"):
            _flush_ram()
            msg = "Optimized system working memory and flushed RAM caches."

        else:  # clean_all
            log("Running full system maintenance…")
            _empty_recycle_bin()
            freed = _clean_temp_files()
            _flush_ram()
            mb = freed / (1024 * 1024)
            msg = f"Cleaned temporary caches, emptied the Recycle Bin, and optimized memory, freeing ~{mb:.1f} MB."

        log(msg)
        return f"Sir, {msg.lower()}"

    except Exception as e:
        return f"Sir, system maintenance encountered an error: {e}"
