#!/bin/bash
# Translate chapters in batches using protected raw files from /tmp
set -e
cd "$(dirname "$0")/.."

BATCH_SIZE=10
START=390
END=515
RAW_SRC="/tmp/unwanted-undead-raw"
EN_DIR="$(pwd)/chapters/en"

mkdir -p "$EN_DIR"

echo "Batch translating chapters $START-$END from $RAW_SRC"
echo "Output: $EN_DIR"
echo ""

for ((batch_start=START; batch_start<=END; batch_start+=BATCH_SIZE)); do
    batch_end=$((batch_start + BATCH_SIZE - 1))
    if [ $batch_end -gt $END ]; then
        batch_end=$END
    fi

    echo "=== Batch: $batch_start-$batch_end ==="

    python3 -u -c "
import os, re
import argostranslate.translate

RAW_DIR = '$RAW_SRC'
EN_DIR = '$EN_DIR'
JP = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]')
TITLE = 'The Unwanted Undead Adventurer'

def needs(ch):
    p = os.path.join(EN_DIR, f'chapter_{ch}_en.txt')
    if not os.path.exists(p): return True
    with open(p) as f: c = f.read()
    b = c.split('\n\n', 1)[1] if '\n\n' in c else c
    return len(JP.findall(b)) / max(len(b), 1) > 0.2

def tr(text):
    if not JP.search(text): return text
    parts = []
    for p in text.split('\n\n'):
        p = p.strip()
        if not p: continue
        if not JP.search(p): parts.append(p); continue
        try: parts.append(argostranslate.translate.translate(p, 'ja', 'en'))
        except: parts.append(p)
    return '\n\n'.join(parts)

for ch in range($batch_start, $batch_end + 1):
    if not needs(ch): print(f'  [SKIP] {ch}', flush=True); continue
    raw = os.path.join(RAW_DIR, f'chapter_{ch}_raw.txt')
    if not os.path.exists(raw): print(f'  [MISS] {ch}', flush=True); continue
    with open(raw) as f: content = f.read()
    lines = content.strip().split('\n')
    tl = lines[0].lstrip('# ').strip()
    m = re.match(r'\d+\s+(.*)', tl)
    jt = m.group(1) if m else tl
    et = argostranslate.translate.translate(jt, 'ja', 'en')
    bs = next((i for i, l in enumerate(lines) if not l.startswith('#')), 0)
    body = '\n'.join(lines[bs:]).strip()
    eb = tr(body)
    with open(os.path.join(EN_DIR, f'chapter_{ch}_en.txt'), 'w') as f:
        f.write(f'Title: {TITLE}\nChapter: {et}\n\n{eb}')
    print(f'  [OK] {ch}: {et}', flush=True)
" 2>&1 | grep -v Warning | grep -v warn | grep -v resource_tracker

    echo ""
done

echo "=== Translation complete ==="
echo "Translated files: $(ls "$EN_DIR"/chapter_*_en.txt 2>/dev/null | wc -l)"
