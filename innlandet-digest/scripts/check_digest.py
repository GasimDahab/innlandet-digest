#!/usr/bin/env python3
"""
Simple checker for the walking skeleton output.
Validates that the digest is well-formed and checkable.
"""
import json
import sys
from pathlib import Path

DIGEST = Path(__file__).parent.parent / "output" / "digest.json"

def check(d: dict) -> list[str]:
    errors = []
    if "items" not in d or not isinstance(d["items"], list):
        errors.append("Missing or invalid 'items' list")
        return errors
    if d.get("relevant_items", 0) != len(d["items"]):
        errors.append("relevant_items count does not match items length")
    for i, it in enumerate(d["items"]):
        for field in ["title", "link", "date", "plain_summary"]:
            if not it.get(field):
                errors.append(f"Item {i}: missing or empty '{field}'")
        if it.get("link") and not it["link"].startswith("http"):
            errors.append(f"Item {i}: link does not look like a URL")
        if len(it.get("plain_summary", "")) < 10:
            errors.append(f"Item {i}: summary too short")
    return errors

def main():
    if not DIGEST.exists():
        print("FAIL: digest.json not found. Run the pipeline first.")
        sys.exit(1)
    with open(DIGEST, encoding="utf-8") as f:
        data = json.load(f)
    errors = check(data)
    if errors:
        print("FAIL:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"PASS: {len(data['items'])} items validated successfully.")
    print(f"Source: {data.get('source_feed')}")
    print(f"Generated: {data.get('generated_at')}")

if __name__ == "__main__":
    main()
