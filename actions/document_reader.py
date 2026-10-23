"""
actions/document_reader.py — Local PDF, Word & Document Intelligence Agent.

Reads and analyzes local files (.pdf, .docx, .txt, .md, .csv) on the user's
Desktop, Downloads, or specified directory. Generates authentic executive summaries
using Gemini LLM, with automatic visual scroll analysis fallback for scanned documents.
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from core import gemini


def _resolve_file_path(filename_or_path: str) -> Path | None:
    """Locates the file in absolute path, Desktop, Downloads, or Documents."""
    clean = filename_or_path.strip().strip('"').strip("'")
    raw_path = Path(clean)
    if raw_path.exists() and raw_path.is_file():
        return raw_path

    # Check Desktop, Downloads, Documents
    candidates = [
        Path.home() / "Desktop" / raw_path.name,
        Path.home() / "Downloads" / raw_path.name,
        Path.home() / "Documents" / raw_path.name,
        Path.cwd() / raw_path.name,
    ]

    for c in candidates:
        if c.exists() and c.is_file():
            return c

    # Fuzzy match on Desktop / Downloads (e.g., user said partial name)
    target_lower = raw_path.name.lower()
    for search_dir in [Path.home() / "Desktop", Path.home() / "Downloads"]:
        if search_dir.exists():
            for f in search_dir.iterdir():
                if f.is_file() and target_lower in f.name.lower():
                    return f

    return None


def _extract_text(file_path: Path, max_pages: int = 30, max_chars: int = 35000) -> str:
    """Extracts raw text from PDF, Word, or plain text documents."""
    ext = file_path.suffix.lower()

    # Plain text / Markdown / Code / CSV
    if ext in (".txt", ".md", ".py", ".json", ".csv", ".log", ".html"):
        try:
            return file_path.read_text(encoding="utf-8", errors="replace")[:max_chars]
        except Exception:
            return file_path.read_text(encoding="latin-1", errors="replace")[:max_chars]

    # PDF Document
    if ext == ".pdf":
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                num_pages = len(reader.pages)
                pages_text = []
                for p in reader.pages[:max_pages]:
                    t = p.extract_text()
                    if t and t.strip():
                        pages_text.append(t.strip())
                full = "\n\n".join(pages_text)
                if full and len(full.strip()) > 30:
                    return full[:max_chars]
                return "__SCANNED_OR_EMPTY__"
        except Exception as e:
            return f"Error reading PDF: {e}"

    # Word Document (.docx)
    if ext == ".docx":
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full = "\n".join(paragraphs)
            return full[:max_chars] if full else "No extractable text found in Word document."
        except Exception as e:
            return f"Error reading DOCX: {e}"

    return f"Unsupported file type: {ext}"


def _summarize_with_llm(text: str, filename: str, user_query: str = "") -> str:
    """Generates an executive, voice-friendly summary using the Gemini ladder."""
    focus = f"Specifically answer the user's inquiry: '{user_query}'" if user_query else "Provide a structured executive briefing"
    prompt = f"""You are J.A.R.V.I.S., Tony Stark's personal AI assistant.
Analyze and summarize the following document '{filename}'.
Goal: {focus}.

Document content:
\"\"\"
{text[:25000]}
\"\"\"

Requirements:
- Speak directly to the user (e.g. 'Sir, according to {filename}...').
- Highlight the core topic, 3-4 key factual bullet points or figures/dates, and the final conclusion.
- Keep the summary engaging, concise, and clear for voice readout.
"""
    try:
        summary = gemini.text(prompt, tier=gemini.FAST, timeout_ms=15000)
        if summary and len(summary.strip()) > 20:
            return summary.strip()
    except Exception as e:
        print(f"[DocumentReader] LLM summarization error: {e}")

    # Fallback if offline
    return f"Sir, I analyzed '{filename}'. Main excerpt: {text[:400].strip()}..."


def _visual_scroll_inspect(path: Path, log) -> str:
    """Opens document on screen, scrolls through, captures vision frames, and synthesizes."""
    log(f"Scanned document detected. Launching visual screen analysis for '{path.name}'…")
    try:
        import pyautogui
        os.startfile(str(path))
        time.sleep(2.0)

        # Capture first page view
        shot1 = pyautogui.screenshot()
        shot1_path = Path.home() / ".jarvis" / "temp_page1.jpg"
        shot1_path.parent.mkdir(parents=True, exist_ok=True)
        shot1.save(str(shot1_path), quality=80)

        # Scroll down to capture next section
        pyautogui.scroll(-700)
        time.sleep(0.8)
        shot2 = pyautogui.screenshot()
        shot2_path = Path.home() / ".jarvis" / "temp_page2.jpg"
        shot2.save(str(shot2_path), quality=80)

        # Use screen vision analysis
        prompt = f"Analyze and summarize this document '{path.name}' shown on screen. Detail what it contains, key headings, and text."
        from actions.screen_processor import screen_process
        return screen_process(query=prompt, angle="screen")
    except Exception as e:
        return f"Could not perform visual document scan: {e}"


def read_document(
    file_path: str,
    query: str = "",
    auto_scroll: bool = False,
    player=None,
    **kwargs,
) -> str:
    """Action handler to read, inspect, and summarize local documents with LLM intelligence."""
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    if not file_path:
        return "Please specify the filename or path of the document you would like me to read."

    path = _resolve_file_path(file_path)
    if not path:
        return f"I couldn't locate '{file_path}' on your Desktop, Downloads, or specified directory."

    log(f"Inspecting document: {path.name}…")
    text = _extract_text(path)

    if text == "__SCANNED_OR_EMPTY__" or auto_scroll:
        # Scanned PDF or requested visual scroll
        return _visual_scroll_inspect(path, log)

    if not text or "Error reading" in text or "Unsupported" in text:
        return f"Could not extract content from '{path.name}': {text}"

    num_words = len(text.split())
    log(f"Synthesizing intelligence briefing for {path.name} ({num_words} words)…")

    summary = _summarize_with_llm(text, path.name, query)
    log(f"Document briefing complete: {path.name}")
    return summary


# ── Action tool declaration (auto-discovered by core/action_loader.py) ───────
TOOL = {
    "name": "read_document",
    "description": (
        "Reads, analyzes, and synthesizes structured intelligence summaries of local documents "
        "(.pdf, .docx, .txt, .md, .csv) on the user's Desktop, Downloads, or file system. "
        "Understands full multi-page PDFs and Word documents, answering specific questions or providing "
        "executive briefings. For scanned PDFs or when asked to scroll through, it inspects pages visually. "
        "Use whenever the user asks to read, summarize, or inspect a document or PDF "
        "(in English or Malayalam: 'ഈ PDF വായിക്കൂ', 'സമ്മറൈസ് ചെയ്യൂ', 'ഡെസ്ക്ടോപ്പിലെ ഫയൽ എന്താണെന്ന് പറയൂ', "
        "'summarize document')."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "file_path": {
                "type": "STRING",
                "description": "The file name or path of the document to inspect (e.g., 'contract.pdf', 'invoice.pdf', 'notes.docx').",
            },
            "query": {
                "type": "STRING",
                "description": "Optional specific question or detail to look for inside the document.",
            },
            "auto_scroll": {
                "type": "BOOLEAN",
                "description": "If true, opens the document on screen and visually scrolls through pages to inspect scanned or visual elements.",
            },
        },
        "required": ["file_path"],
    },
    "handler": read_document,
}
