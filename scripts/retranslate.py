#!/usr/bin/env python3
"""Re-translate chapters using argostranslate (offline, no rate limits)."""

import os
import re
import sys
import argostranslate.translate

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(PROJECT_ROOT, "chapters", "raw")
EN_DIR = os.path.join(PROJECT_ROOT, "chapters", "en")
START_CHAPTER = 390
END_CHAPTER = 515

SERIES_TITLE = "The Unwanted Undead Adventurer"
JP_PATTERN = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]')


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


def translate_text(text):
    """Translate Japanese text to English using argostranslate."""
    if not JP_PATTERN.search(text):
        return text

    paragraphs = text.split("\n\n")
    translated = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if not JP_PATTERN.search(para):
            translated.append(para)
            continue

        try:
            result = argostranslate.translate.translate(para, "ja", "en")
            translated.append(result)
        except Exception as e:
            print(f"      Translation error: {e}", flush=True)
            translated.append(para)

    return "\n\n".join(translated)


def retranslate_chapter(chapter_num):
    raw_path = os.path.join(RAW_DIR, f"chapter_{chapter_num}_raw.txt")
    en_path = os.path.join(EN_DIR, f"chapter_{chapter_num}_en.txt")

    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Raw file not found: {raw_path}")

    with open(raw_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")

    # Extract title
    title_line = lines[0].lstrip("# ").strip()
    match = re.match(r"\d+\s+(.*)", title_line)
    jp_title = match.group(1) if match else title_line

    # Translate title
    en_title = argostranslate.translate.translate(jp_title, "ja", "en")

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
    os.makedirs(EN_DIR, exist_ok=True)
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
        print(f"[{i+1}/{len(to_translate)}] Translating chapter {ch}...", flush=True)
        try:
            if retranslate_chapter(ch):
                success += 1
        except Exception as e:
            print(f"  [ERROR] Chapter {ch}: {e}", flush=True)
            failed.append(ch)

    print(f"\nDone! {success}/{len(to_translate)} chapters translated.", flush=True)
    if failed:
        print(f"Failed: {failed}", flush=True)


if __name__ == "__main__":
    main()
