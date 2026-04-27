#!/usr/bin/env python3
"""Re-translate chapters that still contain Japanese text.
Uses deep_translator's GoogleTranslator (web scraping, different from API)."""

import os
import re
import sys
import time
from deep_translator import GoogleTranslator

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chapters", "raw")
EN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chapters", "en")
START_CHAPTER = 390
END_CHAPTER = 515

SERIES_TITLE = "The Unwanted Undead Adventurer"
JP_PATTERN = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]')

translator = GoogleTranslator(source='ja', target='en')

# deep_translator GoogleTranslator has a 5000 char limit per request
MAX_CHARS = 4800


def needs_retranslation(chapter_num):
    en_path = os.path.join(EN_DIR, f"chapter_{chapter_num}_en.txt")
    if not os.path.exists(en_path):
        return True
    with open(en_path, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("\n\n", 1)
    body = parts[1] if len(parts) > 1 else content
    jp_chars = len(JP_PATTERN.findall(body))
    total = len(body)
    if total == 0:
        return True
    return (jp_chars / total) > 0.2


def translate_chunk(text):
    """Translate a chunk of text (max ~5000 chars)."""
    if not JP_PATTERN.search(text):
        return text

    for attempt in range(5):
        try:
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            err = str(e)
            if "429" in err or "Too Many" in err or "rate" in err.lower():
                wait = 15 * (attempt + 1)
                print(f"      Rate limited, waiting {wait}s...", flush=True)
                time.sleep(wait)
            else:
                print(f"      Error (attempt {attempt+1}): {err[:80]}", flush=True)
                time.sleep(3 * (attempt + 1))

    return text


def split_text(text, max_chars=MAX_CHARS):
    """Split text into chunks at paragraph boundaries."""
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 > max_chars:
            if current:
                chunks.append(current)
            # If single paragraph is too long, split by sentences
            if len(para) > max_chars:
                sentences = re.split(r'(?<=[。！？」』])', para)
                sub = ""
                for s in sentences:
                    if len(sub) + len(s) > max_chars and sub:
                        chunks.append(sub)
                        sub = s
                    else:
                        sub += s
                if sub:
                    current = sub
                else:
                    current = ""
            else:
                current = para
        else:
            current = current + "\n\n" + para if current else para

    if current:
        chunks.append(current)

    return chunks if chunks else [text]


def translate_text(text):
    """Translate full text, splitting into chunks as needed."""
    chunks = split_text(text)
    translated = []

    for i, chunk in enumerate(chunks):
        result = translate_chunk(chunk)
        translated.append(result)
        if i < len(chunks) - 1:
            time.sleep(0.5)

    return "\n\n".join(translated)


def retranslate_chapter(chapter_num):
    raw_path = os.path.join(RAW_DIR, f"chapter_{chapter_num}_raw.txt")
    en_path = os.path.join(EN_DIR, f"chapter_{chapter_num}_en.txt")

    with open(raw_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")

    # Extract title
    title_line = lines[0].lstrip("# ").strip()
    match = re.match(r"\d+\s+(.*)", title_line)
    jp_title = match.group(1) if match else title_line

    # Translate title
    en_title = translate_chunk(jp_title)
    time.sleep(0.3)

    # Get body
    body_start = 0
    for i, line in enumerate(lines):
        if not line.startswith("#"):
            body_start = i
            break
    body_text = "\n".join(lines[body_start:]).strip()

    # Translate body
    en_body = translate_text(body_text)

    # Write
    with open(en_path, "w", encoding="utf-8") as f:
        f.write(f"Title: {SERIES_TITLE}\n")
        f.write(f"Chapter: {en_title}\n\n")
        f.write(en_body)

    print(f"  [OK] Chapter {chapter_num}: {en_title}", flush=True)
    return True


def main():
    to_translate = []
    for ch in range(START_CHAPTER, END_CHAPTER + 1):
        if needs_retranslation(ch):
            to_translate.append(ch)

    print(f"Found {len(to_translate)} chapters needing (re)translation", flush=True)
    if not to_translate:
        print("All chapters are already translated!", flush=True)
        return

    success = 0
    failed = []
    for i, ch in enumerate(to_translate):
        print(f"[{i+1}/{len(to_translate)}] Re-translating chapter {ch}...", flush=True)
        try:
            if retranslate_chapter(ch):
                success += 1
        except Exception as e:
            print(f"  [ERROR] Chapter {ch}: {e}", flush=True)
            failed.append(ch)
        time.sleep(1)

    print(f"\nDone! {success}/{len(to_translate)} chapters re-translated.", flush=True)
    if failed:
        print(f"Failed: {failed}", flush=True)


if __name__ == "__main__":
    main()
