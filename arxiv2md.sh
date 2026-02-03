#!/bin/bash
# arxiv2md.sh - Download arXiv HTML and convert to Markdown
# Usage: ./arxiv2md.sh 2502.04307

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HTML_DIR="$SCRIPT_DIR/html"
OUTPUT_DIR="$SCRIPT_DIR/output"

if [ -z "$1" ]; then
    echo "Usage: $0 <arxiv_id>"
    echo "Example: $0 2502.04307"
    exit 1
fi

ARXIV_ID="$1"
# Remove 'arXiv:' prefix if present
ARXIV_ID="${ARXIV_ID#arXiv:}"
ARXIV_ID="${ARXIV_ID#arxiv:}"

HTML_URL="https://arxiv.org/html/${ARXIV_ID}"
HTML_FILE="$HTML_DIR/${ARXIV_ID}.html"
MD_FILE="$OUTPUT_DIR/${ARXIV_ID}.md"

echo "arXiv ID: $ARXIV_ID"
echo "Downloading from: $HTML_URL"

# Download HTML
curl -s -L -o "$HTML_FILE" "$HTML_URL"

# Check if download successful
if [ ! -s "$HTML_FILE" ]; then
    echo "Error: Failed to download HTML"
    rm -f "$HTML_FILE"
    exit 1
fi

# Check if it's a valid HTML (not an error page)
if grep -q "No HTML available" "$HTML_FILE" 2>/dev/null; then
    echo "Error: No HTML version available for this paper"
    rm -f "$HTML_FILE"
    exit 1
fi

echo "Downloaded: $HTML_FILE ($(du -h "$HTML_FILE" | cut -f1))"

# Convert to Markdown
echo "Converting to Markdown..."
python3 "$SCRIPT_DIR/html_to_md.py" "$HTML_FILE" "$MD_FILE"

echo ""
echo "Done! Output: $MD_FILE"
