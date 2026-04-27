#!/usr/bin/env python3
"""Crawl raw chapters from ncode.syosetu.com for 四度目は嫌な死属性魔術師 (n1745ct)."""

import os
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://ncode.syosetu.com/n1745ct"
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chapters", "raw")
START_CHAPTER = 390
END_CHAPTER = 515

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}


def crawl_chapter(chapter_num):
    """Fetch a single chapter and save raw text."""
    url = f"{BASE_URL}/{chapter_num}/"
    output_path = os.path.join(RAW_DIR, f"chapter_{chapter_num}_raw.txt")

    if os.path.exists(output_path):
        print(f"  [SKIP] Chapter {chapter_num} already exists")
        return True

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        resp.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"  [ERROR] Chapter {chapter_num}: {e}")
        return False

    soup = BeautifulSoup(resp.text, "html.parser")

    # Extract title
    title_elem = soup.find("p", class_="novel_subtitle") or soup.find("h1", class_="p-novel__title")
    title = title_elem.get_text(strip=True) if title_elem else f"Chapter {chapter_num}"

    # Extract body text
    body_elem = soup.find("div", id="novel_honbun") or soup.find("div", class_="p-novel__body")
    if not body_elem:
        print(f"  [ERROR] Chapter {chapter_num}: No body content found")
        return False

    # Get text preserving paragraph breaks
    paragraphs = []
    for p in body_elem.find_all("p"):
        text = p.get_text()
        if text.strip():
            paragraphs.append(text)

    body_text = "\n\n".join(paragraphs)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {chapter_num} {title}\n")
        f.write(f"# URL: {url}\n\n")
        f.write(body_text)

    print(f"  [OK] Chapter {chapter_num}: {title}")
    return True


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    total = END_CHAPTER - START_CHAPTER + 1
    success = 0
    failed = []

    print(f"Crawling chapters {START_CHAPTER}-{END_CHAPTER} ({total} chapters)")
    print(f"Output: {RAW_DIR}\n")

    for i, ch in enumerate(range(START_CHAPTER, END_CHAPTER + 1)):
        print(f"[{i+1}/{total}] Fetching chapter {ch}...")
        if crawl_chapter(ch):
            success += 1
        else:
            failed.append(ch)
        # Be polite to the server
        time.sleep(1.5)

    print(f"\nDone! {success}/{total} chapters crawled.")
    if failed:
        print(f"Failed chapters: {failed}")


if __name__ == "__main__":
    main()
