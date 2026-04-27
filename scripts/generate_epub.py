#!/usr/bin/env python3
"""Generate EPUB for The Unwanted Undead Adventurer - Volume 5 (Ch. 390-515)."""

import os
import re
from ebooklib import epub

EN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chapters", "en")
EPUB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "epub")
START_CHAPTER = 390
END_CHAPTER = 515


def read_chapter(filepath):
    """Read a translated chapter file and return title + HTML content."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.strip().split("\n")

    # Extract chapter title from "Chapter: ..." line
    title_line = "Untitled"
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("Chapter:"):
            title_line = line.replace("Chapter:", "").strip()
            body_start = i + 1
            break

    if title_line == "Untitled" and lines:
        title_line = lines[0].lstrip("# ").strip()
        body_start = 1

    # Rest is body
    body_text = "\n".join(lines[body_start:]).strip()

    # Convert paragraphs to HTML
    paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
    body_html = "\n".join(f"<p>{p.replace(chr(10), '<br/>')}</p>" for p in paragraphs)

    return title_line, body_html


def main():
    os.makedirs(EPUB_DIR, exist_ok=True)

    book = epub.EpubBook()
    book.set_identifier("unwanted-undead-adventurer-vol5")
    book.set_title("The Unwanted Undead Adventurer - Volume 5 (Ch. 390-515)")
    book.set_language("en")
    book.add_author("Denden (七巻烏)")

    style = """
body { font-family: Georgia, serif; line-height: 1.8; margin: 2em; }
h1 { text-align: center; margin-bottom: 1.5em; font-size: 1.5em; }
p { text-indent: 1.5em; margin: 0.5em 0; }
"""
    css = epub.EpubItem(uid="style", file_name="style/default.css",
                        media_type="text/css", content=style.encode("utf-8"))
    book.add_item(css)

    epub_chapters = []

    for ch_num in range(START_CHAPTER, END_CHAPTER + 1):
        en_file = os.path.join(EN_DIR, f"chapter_{ch_num}_en.txt")

        if not os.path.exists(en_file):
            print(f"WARNING: Missing {en_file}, skipping")
            continue

        chapter_title, body_html = read_chapter(en_file)

        epub_ch = epub.EpubHtml(
            title=chapter_title,
            file_name=f"chapter_{ch_num}.xhtml",
            lang="en"
        )
        epub_ch.add_item(css)

        html_content = f"""<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{chapter_title}</title></head>
<body>
<h1>{chapter_title}</h1>
{body_html}
</body>
</html>"""
        epub_ch.content = html_content.encode("utf-8")

        book.add_item(epub_ch)
        epub_chapters.append(epub_ch)
        print(f"Added: Ch.{ch_num} - {chapter_title}")

    book.toc = epub_chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + epub_chapters

    output_path = os.path.join(EPUB_DIR, "Volume_5.epub")
    epub.write_epub(output_path, book)
    print(f"\nEPUB created: {output_path} ({len(epub_chapters)} chapters)")


if __name__ == "__main__":
    main()
