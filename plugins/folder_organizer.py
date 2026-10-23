"""
plugins/folder_organizer.py — Desktop & Downloads Auto-Organizer & File Sorter.

Automatically sorts cluttered directories (Downloads, Desktop) into organized
subcategories (Documents, Images, Videos, Installers, Archives, Code) with 100%
undo capability.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

CATEGORIES = {
    "Documents": {".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".csv", ".rtf"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico", ".tiff"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "Audio": {".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"},
    "Installers": {".exe", ".msi", ".iso"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".ts", ".html", ".css", ".json", ".cpp", ".c", ".java", ".sql", ".sh"},
}

_MANIFEST_NAME = "_jarvis_organize_manifest.json"


def _get_target_dir(folder_name: str) -> Path:
    f = folder_name.lower().strip()
    if f in ("desktop", "ഡെസ്ക്ടോപ്പ്"):
        return Path.home() / "Desktop"
    if f in ("documents", "ഡ്രൈവ്"):
        return Path.home() / "Documents"
    return Path.home() / "Downloads"


PLUGIN = {
    "name": "folder_organizer",
    "description": (
        "Organizes cluttered folders (Downloads or Desktop) by sorting loose files "
        "into neat categorized subfolders (Documents, Images, Videos, Audio, Installers, Archives, Code). "
        "Supports undoing the operation. Use whenever the user asks to clean up or organize "
        "their Downloads or Desktop (in English or Malayalam: "
        "'Downloads ഫോൾഡർ ക്ലീൻ ചെയ്യ്', 'ഡെസ്ക്ടോപ്പ് ഓർഗനൈസ് ചെയ്യൂ', 'clean downloads')."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "organize | undo (default: organize)",
            },
            "folder": {
                "type": "STRING",
                "description": "downloads | desktop (default: downloads)",
            },
        },
        "required": [],
    },
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = str(parameters.get("action", "organize")).lower().strip()
    folder_name = str(parameters.get("folder", "downloads")).strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    target_dir = _get_target_dir(folder_name)
    if not target_dir.exists():
        return f"Could not find directory '{target_dir}'."

    manifest_file = target_dir / _MANIFEST_NAME

    # Undo action
    if action in ("undo", "revert"):
        if not manifest_file.exists():
            return f"No previous organization manifest found in '{target_dir.name}' to undo."

        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                moves = json.load(f)
            restored = 0
            for item in moves:
                src = Path(item["to"])
                dst = Path(item["from"])
                if src.exists():
                    shutil.move(str(src), str(dst))
                    restored += 1
            manifest_file.unlink(missing_ok=True)
            log(f"Undid folder organization: {restored} files restored.")
            return f"Reverted organization in '{target_dir.name}'. Restored {restored} file(s) to original location."
        except Exception as e:
            return f"Could not complete undo: {e}"

    # Organize action
    log(f"Scanning and organizing '{target_dir.name}'…")
    moved_manifest = []
    stats = {}

    try:
        for entry in list(target_dir.iterdir()):
            if entry.is_file() and not entry.name.startswith((".", "_")) and entry.name != _MANIFEST_NAME:
                ext = entry.suffix.lower()
                # Skip shortcuts and ini files
                if ext in (".lnk", ".ini", ".url"):
                    continue

                category = None
                for cat_name, extensions in CATEGORIES.items():
                    if ext in extensions:
                        category = cat_name
                        break

                if not category:
                    category = "Miscellaneous"

                dest_dir = target_dir / category
                dest_dir.mkdir(parents=True, exist_ok=True)

                dest_path = dest_dir / entry.name
                # Avoid collision
                if dest_path.exists():
                    stem = entry.stem
                    dest_path = dest_dir / f"{stem}_{int(os.path.getmtime(entry))}{ext}"

                shutil.move(str(entry), str(dest_path))
                moved_manifest.append({"from": str(entry), "to": str(dest_path)})
                stats[category] = stats.get(category, 0) + 1

        if not moved_manifest:
            return f"'{target_dir.name}' is already clean and organized, sir. No loose files found."

        # Save manifest for undo
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(moved_manifest, f, indent=2)

        summary_parts = [f"{count} {cat}" for cat, count in stats.items()]
        summary_str = ", ".join(summary_parts)
        log(f"Organized {len(moved_manifest)} files into: {summary_str}.")
        return (
            f"Organized {len(moved_manifest)} files in '{target_dir.name}' into: {summary_str}. "
            "You can say 'Undo folder organization' anytime to revert."
        )
    except Exception as e:
        return f"Error organizing folder: {e}"
