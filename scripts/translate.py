#!/usr/bin/env python3
"""Translate raw Japanese chapters to English using Google Translate (free API)."""

import os
import re
import time
import requests
import json
import urllib.parse

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chapters", "raw")
EN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chapters", "en")
START_CHAPTER = 390
END_CHAPTER = 515

SERIES_TITLE = "The Unwanted Undead Adventurer"


def translate_text(text, src="ja", dest="en", max_retries=3):
    """Translate text using Google Translate (unofficial API endpoint).
    Uses POST method with smaller chunks to avoid URL length limits."""
    chunks = split_text(text, max_chars=1500)
    translated_chunks = []

    for chunk in chunks:
        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    "https://translate.googleapis.com/translate_a/single",
                    params={"client": "gtx", "sl": src, "tl": dest, "dt": "t"},
                    data={"q": chunk},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                translated = "".join(
                    sentence[0] for sentence in result[0] if sentence[0]
                )
                translated_chunks.append(translated)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                else:
                    print(f"    [WARN] Translation chunk failed after {max_retries} attempts: {e}")
                    translated_chunks.append(chunk)
        time.sleep(0.3)

    return "\n\n".join(translated_chunks)


def split_text(text, max_chars=1500):
    """Split text into chunks at paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > max_chars:
            if current:
                chunks.append(current)
            current = para
        else:
            current = current + "\n\n" + para if current else para

    if current:
        chunks.append(current)

    return chunks if chunks else [text]


def translate_chapter(chapter_num):
    """Translate a single chapter file."""
    raw_path = os.path.join(RAW_DIR, f"chapter_{chapter_num}_raw.txt")
    en_path = os.path.join(EN_DIR, f"chapter_{chapter_num}_en.txt")

    if os.path.exists(en_path):
        print(f"  [SKIP] Chapter {chapter_num} already translated")
        return True

    if not os.path.exists(raw_path):
        print(f"  [ERROR] Chapter {chapter_num}: Raw file not found")
        return False

    with open(raw_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")

    # Extract title from first line (format: "# 390 タイトル")
    title_line = lines[0].lstrip("# ").strip()
    match = re.match(r"\d+\s+(.*)", title_line)
    jp_title = match.group(1) if match else title_line

    # Translate title
    en_title = translate_text(jp_title)
    time.sleep(0.3)

    # Get body (skip header lines)
    body_start = 0
    for i, line in enumerate(lines):
        if not line.startswith("#"):
            body_start = i
            break

    body_text = "\n".join(lines[body_start:]).strip()

    # Translate body
    en_body = translate_text(body_text)

    # Write translated file
    with open(en_path, "w", encoding="utf-8") as f:
        f.write(f"Title: {SERIES_TITLE}\n")
        f.write(f"Chapter: {en_title}\n\n")
        f.write(en_body)

    print(f"  [OK] Chapter {chapter_num}: {en_title}")
    return True


def main():
    os.makedirs(EN_DIR, exist_ok=True)
    total = END_CHAPTER - START_CHAPTER + 1
    success = 0
    failed = []

    print(f"Translating chapters {START_CHAPTER}-{END_CHAPTER} ({total} chapters)")
    print(f"Input: {RAW_DIR}")
    print(f"Output: {EN_DIR}\n")

    for i, ch in enumerate(range(START_CHAPTER, END_CHAPTER + 1)):
        print(f"[{i+1}/{total}] Translating chapter {ch}...")
        if translate_chapter(ch):
            success += 1
        else:
            failed.append(ch)
        time.sleep(1)

    print(f"\nDone! {success}/{total} chapters translated.")
    if failed:
        print(f"Failed chapters: {failed}")


if __name__ == "__main__":
    main()
