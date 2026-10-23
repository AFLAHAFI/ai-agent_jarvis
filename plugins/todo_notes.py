"""
plugins/todo_notes.py — Persistent Voice Notes & To-Do Task Manager.

Stores notes and to-dos in memory/todo_notes.json (git-ignored, strictly private).
Supports natural voice commands in English and Malayalam:
- "Add a note: Buy groceries" / "കുറിച്ചു വെക്കൂ: മീറ്റിംഗ് ഉണ്ട്"
- "List my tasks" / "എന്റെ നോട്ട്സ് എന്തൊക്കെയാണ്?"
- "Mark task 1 as completed"
"""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

def _base_dir() -> Path:
    return Path(__file__).resolve().parent.parent


_MEMORY_DIR = _base_dir() / "memory"
_TODO_FILE = _MEMORY_DIR / "todo_notes.json"


def _load_todos() -> list[dict]:
    if not _TODO_FILE.exists():
        return []
    try:
        with open(_TODO_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_todos(todos: list[dict]) -> None:
    _MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with open(_TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=2, ensure_ascii=False)


PLUGIN = {
    "name": "todo_notes",
    "description": (
        "Manages personal voice notes and to-do tasks. "
        "Supports adding, listing, completing, or removing tasks. "
        "Use whenever the user asks to take a note, write down a reminder/task, "
        "check pending to-dos, or mark tasks done (in English or Malayalam: "
        "'കുറിച്ചു വെക്കൂ', 'നോട്ട് ചെയ്യ്', 'ഇന്നത്തെ നോട്ട്സുകൾ')."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "add | list | complete | delete | clear",
            },
            "task": {
                "type": "STRING",
                "description": "The note or task content when adding, or keyword/ID to match when completing/deleting.",
            },
            "priority": {
                "type": "STRING",
                "description": "high | medium | low (optional, default: medium)",
            },
        },
        "required": ["action"],
    },
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    action = str(parameters.get("action", "list")).lower().strip()
    task_text = str(parameters.get("task", "")).strip()
    priority = str(parameters.get("priority", "medium")).lower().strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    todos = _load_todos()

    if action in ("add", "create", "new", "save"):
        if not task_text:
            return "Please provide the note or task content you'd like me to save."

        new_id = len(todos) + 1
        now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        item = {
            "id": new_id,
            "task": task_text,
            "status": "pending",
            "priority": priority if priority in ("high", "low") else "medium",
            "created_at": now_str,
        }
        todos.append(item)
        _save_todos(todos)
        log(f"Added task #{new_id}: {task_text}")
        return f"Noted, sir. Added task #{new_id}: '{task_text}'."

    elif action in ("list", "show", "get", "view"):
        pending = [t for t in todos if t.get("status") == "pending"]
        if not pending:
            return "You have no pending tasks or notes on your list, sir."

        lines = [f"You have {len(pending)} pending task(s):"]
        for idx, t in enumerate(pending, 1):
            prio_tag = " [HIGH]" if t.get("priority") == "high" else ""
            lines.append(f"{idx}. {t.get('task')}{prio_tag}")
        result = "\n".join(lines)
        log(result)
        return result

    elif action in ("complete", "done", "finish"):
        if not task_text:
            return "Which task would you like to mark as completed?"

        matched = False
        target_name = ""
        # Check if task_text is numeric ID
        if task_text.isdigit():
            tid = int(task_text)
            for t in todos:
                if t.get("id") == tid:
                    t["status"] = "completed"
                    target_name = t.get("task")
                    matched = True
                    break
        if not matched:
            # Match by substring
            query = task_text.lower()
            for t in todos:
                if query in t.get("task", "").lower() and t.get("status") == "pending":
                    t["status"] = "completed"
                    target_name = t.get("task")
                    matched = True
                    break

        if matched:
            _save_todos(todos)
            return f"Completed task: '{target_name}'."
        return f"I couldn't find a pending task matching '{task_text}'."

    elif action in ("clear", "delete_completed"):
        before = len(todos)
        todos = [t for t in todos if t.get("status") == "pending"]
        cleared = before - len(todos)
        _save_todos(todos)
        return f"Cleared {cleared} completed task(s)."

    return "Available to-do actions: 'add', 'list', 'complete', or 'clear'."
