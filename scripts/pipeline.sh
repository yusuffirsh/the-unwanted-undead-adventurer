#!/bin/bash
# Full pipeline: crawl -> translate -> epub
# Usage: ./scripts/pipeline.sh [step]
# Steps: crawl, translate, epub, all (default: all)

set -e
cd "$(dirname "$0")/.."

STEP="${1:-all}"

echo "=========================================="
echo "The Unwanted Undead Adventurer - Pipeline"
echo "Chapters 390-515 (126 chapters)"
echo "=========================================="
echo ""

if [[ "$STEP" == "crawl" || "$STEP" == "all" ]]; then
    echo ">>> STEP 1: Crawling raw chapters..."
    python3 scripts/crawl.py
    echo ""
fi

if [[ "$STEP" == "translate" || "$STEP" == "all" ]]; then
    echo ">>> STEP 2: Translating to English..."
    python3 scripts/translate.py
    echo ""
fi

if [[ "$STEP" == "epub" || "$STEP" == "all" ]]; then
    echo ">>> STEP 3: Generating EPUB..."
    python3 scripts/generate_epub.py
    echo ""
fi

echo "=========================================="
echo "Pipeline complete!"
echo "=========================================="
