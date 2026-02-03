#!/bin/bash
# arxiv2md.sh - Download arXiv HTML and convert to Markdown
# Usage: ./arxiv2md.sh 2502.04307

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
HTML_DIR="$SCRIPT_DIR/html"
OUTPUT_DIR="$SCRIPT_DIR/output"

if [ -z "$1" ]; then
    read -p "Enter arXiv ID (e.g. 2502.04307): " ARXIV_ID
    if [ -z "$ARXIV_ID" ]; then
        echo "Error: No arXiv ID provided"
        exit 1
    fi
else
    ARXIV_ID="$1"
fi
# Remove 'arXiv:' prefix if present
ARXIV_ID="${ARXIV_ID#arXiv:}"
ARXIV_ID="${ARXIV_ID#arxiv:}"

HTML_FILE="$HTML_DIR/${ARXIV_ID}.html"
MD_FILE="$OUTPUT_DIR/${ARXIV_ID}.md"

# Step 1: Download HTML
python3 "$SRC_DIR/arxiv2html.py" "$ARXIV_ID" "$HTML_FILE"

# Step 2: Convert to Markdown
echo "Converting to Markdown..."
python3 "$SRC_DIR/html2md.py" "$HTML_FILE" "$MD_FILE"

echo ""
echo "Done! Output: $MD_FILE"
