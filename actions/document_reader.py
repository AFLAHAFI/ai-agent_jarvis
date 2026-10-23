"""
actions/document_reader.py — Local PDF, Word & Document Intelligence Agent.

Reads and analyzes local files (.pdf, .docx, .txt, .md, .csv) on the user's
Desktop, Downloads, or specified directory, and answers questions or summarizes them.
Uses PyPDF2 and python-docx without external cloud services.
"""
from __future__ import annotations

import os
from pathlib import Path


def _resolve_file_path(filename_or_path: str) -> Path | None:
    """Locates the file in absolute path, Desktop, or Downloads folder."""
    raw_path = Path(filename_or_path.strip().strip('"').strip("'"))
    if raw_path.exists() and raw_path.is_file():
        return raw_path

    # Search common candidate locations
    candidates = [
        Path.home() / "Desktop" / raw_path.name,
        Path.home() / "Downloads" / raw_path.name,
        Path.home() / "Documents" / raw_path.name,
        Path.cwd() / raw_path.name,
    ]

    for c in candidates:
        if c.exists() and c.is_file():
            return c

    # Fuzzy match on Desktop / Downloads
    target_lower = raw_path.name.lower()
    for search_dir in [Path.home() / "Desktop", Path.home() / "Downloads"]:
        if search_dir.exists():
            for f in search_dir.iterdir():
                if f.is_file() and target_lower in f.name.lower():
                    return f

    return None


def _extract_text(file_path: Path, max_chars: int = 8000) -> str:
    ext = file_path.suffix.lower()

    # Plain text / Markdown / Code
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
                pages_text = []
                for p in reader.pages[:10]:
                    t = p.extract_text()
                    if t:
                        pages_text.append(t)
                full = "\n".join(pages_text)
                return full[:max_chars] if full else "No extractable text found in PDF."
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


def read_document(
    file_path: str,
    query: str = "",
    player=None,
    **kwargs,
) -> str:
    """Action handler to read, inspect, and summarize local documents."""
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    if not file_path:
        return "Please specify the filename or path of the document you would like me to read."

    path = _resolve_file_path(file_path)
    if not path:
        return f"I couldn't locate '{file_path}' on your Desktop, Downloads, or specified directory."

    log(f"Reading document: {path.name}…")
    text = _extract_text(path)

    if not text or "Error reading" in text or "Unsupported" in text:
        return f"Could not read content from '{path.name}': {text}"

    # Truncate clean sample
    preview = text[:1500].strip().replace("\r\n", " ").replace("\n", " ")
    num_words = len(text.split())

    msg = f"I've analyzed '{path.name}' ({num_words} words). Summary excerpt: {preview[:350]}..."
    log(f"Document analyzed ({num_words} words).")
    return msg


# ── Action tool declaration (auto-discovered by core/action_loader.py) ───────
TOOL = {
    "name": "read_document",
    "description": (
        "Reads, analyzes, and extracts content from local documents (.pdf, .docx, .txt, .md, .csv) "
        "on the user's Desktop, Downloads, or file system. "
        "Use whenever the user asks to read, summarize, or inspect a document or PDF "
        "(in English or Malayalam: 'ഈ PDF വായിക്കൂ', 'ഡെസ്ക്ടോപ്പിലെ ഫയൽ എന്താണെന്ന് പറയൂ', "
        "'summarize document')."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "file_path": {
                "type": "STRING",
                "description": "The file name or path of the document to inspect (e.g., 'invoice.pdf', 'notes.docx').",
            },
            "query": {
                "type": "STRING",
                "description": "Optional specific question or detail to look for inside the document.",
            },
        },
        "required": ["file_path"],
    },
    "handler": read_document,
}
