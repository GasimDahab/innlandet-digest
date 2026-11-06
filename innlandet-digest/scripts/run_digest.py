#!/usr/bin/env python3
"""
Innlandet Public Announcements Digest - Walking Skeleton
Stage 1: Fetch and parse RSS
Stage 2: Filter and extract structured items
Stage 3: Generate plain-language digest (rule-based for skeleton; agent in full version)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

RSS_URL = "https://www.statsforvalteren.no/innlandet/nyheter/rss"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
CONTEXT_DIR = Path(__file__).parent.parent / "context"

# Relevance keywords for local public services (citizen-facing)
RELEVANT_KEYWORDS = [
    "høring", "høring", "plan", "regulering", "vei", "veg", "bru", "trafikk",
    "miljø", "natur", "landbruk", "skole", "barnehage", "bolig", "helse",
    "innlandet", "kommune", "fylke", "statsforvalteren", "offentlig",
    "arrangement", "møte", "tilskudd", "støtte"
]


def fetch_rss(url: str) -> str:
    """Stage 1: Fetch raw RSS."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_items(xml_text: str) -> list[dict]:
    """Stage 2: Parse into structured items."""
    root = ET.fromstring(xml_text)
    # Handle possible namespaces
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        # Prefer atom:updated if present
        updated = item.findtext("atom:updated", namespaces=ns) or item.findtext("pubDate") or ""
        items.append({
            "title": title,
            "link": link,
            "description": desc[:500],  # truncate
            "date": updated,
            "source": "Statsforvalteren i Innlandet"
        })
    return items


def is_relevant(item: dict) -> bool:
    text = (item["title"] + " " + item["description"]).lower()
    return any(kw in text for kw in RELEVANT_KEYWORDS)


def plain_summary(item: dict) -> str:
    """Stage 3: Produce short plain-language summary (deterministic for skeleton)."""
    desc = item["description"].strip()
    title = item["title"].strip()
    # Prefer description; fall back to title
    text = desc if len(desc) >= 20 else title
    # Take first sentence or first 250 chars
    first = text.split(".")[0].strip()
    if len(first) > 250:
        first = first[:247] + "..."
    if len(first) < 15:
        first = (title + ". " + desc)[:250]
    return first if first else title


def generate_digest(items: list[dict]) -> dict:
    relevant = [it for it in items if is_relevant(it)]
    digest_items = []
    for it in relevant[:10]:  # limit for skeleton
        digest_items.append({
            "title": it["title"],
            "link": it["link"],
            "date": it["date"],
            "plain_summary": plain_summary(it),
            "category": "public_announcement",  # placeholder; agent would classify
            "source": it["source"]
        })
    return {
        "generated_at": datetime.now(ZoneInfo("Europe/Oslo")).isoformat(),
        "source_feed": RSS_URL,
        "total_items_fetched": len(items),
        "relevant_items": len(digest_items),
        "items": digest_items
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Stage 1: Fetching RSS...")
    xml = fetch_rss(RSS_URL)
    print("Stage 2: Parsing items...")
    items = parse_items(xml)
    print(f"Parsed {len(items)} items")
    print("Stage 3: Filtering and summarizing...")
    digest = generate_digest(items)
    
    out_json = OUTPUT_DIR / "digest.json"
    out_md = OUTPUT_DIR / "digest.md"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=2)
    
    # Markdown for human reading
    md_lines = [
        f"# Innlandet Public Announcements Digest",
        f"*Generated: {digest['generated_at']}*",
        f"*Source: {digest['source_feed']}*",
        f"*Relevant items: {digest['relevant_items']} / {digest['total_items_fetched']}*",
        ""
    ]
    for i, it in enumerate(digest["items"], 1):
        md_lines.append(f"## {i}. {it['title']}")
        md_lines.append(f"- **Date:** {it['date']}")
        md_lines.append(f"- **Link:** {it['link']}")
        md_lines.append(f"- **Plain summary:** {it['plain_summary']}")
        md_lines.append("")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    
    print(f"Output written to {out_json} and {out_md}")
    print(json.dumps({"relevant_count": digest["relevant_items"], "output_files": [str(out_json), str(out_md)]}, indent=2))


if __name__ == "__main__":
    main()
