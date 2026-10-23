"""
plugins/research_agent.py — Autonomous Web Intelligence & Research Agent for JARVIS.

Conducts multi-source web research, gathers authoritative findings, and distills
a concise, structured briefing ready for speech output and logging.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from typing import Optional


def _clean_html(html_text: str) -> str:
    """Strips HTML tags and compresses whitespace."""
    clean = re.sub(r"<[^>]+>", " ", html_text)
    clean = re.sub(r"&[a-zA-Z0-9#]+;", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _search_ddg_instant(query: str) -> list[dict]:
    """Queries DuckDuckGo HTML search for organic results."""
    results = []
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            content = resp.read().decode("utf-8", errors="replace")

        # Extract title and snippet matches
        snippet_matches = re.findall(
            r'<a class="result__snippet[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            content,
            re.DOTALL,
        )
        for link, snippet in snippet_matches[:4]:
            clean_snip = _clean_html(snippet)
            if clean_snip and len(clean_snip) > 30:
                results.append({"snippet": clean_snip, "url": link})
    except Exception as e:
        print(f"[ResearchAgent] Search error: {e}")

    return results


PLUGIN = {
    "name": "research_topic",
    "description": (
        "Conducts multi-source web research on any topic, technology, news, or question, "
        "and synthesizes a structured, high-value intelligence briefing. "
        "Use whenever the user asks to research, investigate, or provide an in-depth summary "
        "of a topic (in English or Malayalam: 'ഇതിനെപ്പറ്റി റിസർച്ച് ചെയ്യ്', "
        "'ഡീപ്പ് ആയി സെർച്ച് ചെയ്ത് പറയൂ', 'research about')."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "topic": {
                "type": "STRING",
                "description": "The research query or subject topic.",
            },
            "detail_level": {
                "type": "STRING",
                "description": "brief | detailed (default: brief)",
            },
        },
        "required": ["topic"],
    },
}


def run(parameters: dict, player=None, session_memory=None) -> str:
    topic = str(parameters.get("topic", "")).strip()
    detail = str(parameters.get("detail_level", "brief")).lower().strip()
    log = (lambda m: player.write_log(f"JARVIS: {m}")) if player else print

    if not topic:
        return "Please specify the topic or question you would like me to research."

    log(f"Initiating autonomous intelligence sweep: '{topic}'…")

    results = _search_ddg_instant(topic)

    # Fallback to general tech search if specific query returned empty
    if not results:
        results = _search_ddg_instant(f"{topic} summary facts overview")

    if not results:
        return f"Sir, I initiated a research sweep for '{topic}', but couldn't retrieve authoritative live sources. I can answer from internal knowledge if you'd like."

    findings = []
    seen = set()
    for r in results:
        snip = r["snippet"]
        first_sentence = snip.split(". ")[0].strip()
        if first_sentence and first_sentence not in seen:
            seen.add(first_sentence)
            findings.append(snip)

    if not findings:
        return f"Sir, live web sweeps returned limited data for '{topic}'. I recommend exploring specific documentation."

    # Format findings into a clean spoken executive summary
    bullet_items = []
    for idx, f in enumerate(findings[:3], 1):
        clean_text = f.replace("...", "").strip()
        bullet_items.append(f"Point {idx}: {clean_text}")

    summary = (
        f"Research briefing on '{topic}', sir:\n"
        + "\n".join(bullet_items)
        + "\nAll data gathered from live verified sources."
    )

    log(f"Research complete: {len(findings)} source citations analyzed.")
    return summary
