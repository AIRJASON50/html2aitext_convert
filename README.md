# html2aitext_convert

Convert arXiv HTML papers to AI-friendly text (Markdown + LaTeX math).

## Quick Start

```bash
./arxiv2md.sh 2502.04307
```

Output: `output/2502.04307.md`

## Project Structure

```
html2aitext_convert/
├── src/
│   ├── arxiv2html.py   # Download arXiv HTML
│   └── html2md.py      # Convert HTML to Markdown
├── html/               # Downloaded HTML files
├── output/             # Converted Markdown files
├── arxiv2md.sh         # Main entry script
└── README.md
```

## Usage

### One-command (recommended)
```bash
./arxiv2md.sh 2502.04307
./arxiv2md.sh arXiv:2502.04307
```

### Step by step
```bash
python src/arxiv2html.py 2502.04307 html/paper.html
python src/html2md.py html/paper.html output/paper.md
```

## Output Format

| Content | Format |
|---------|--------|
| Text | Plain text |
| Structure | Markdown (`##`, `###`, `**bold**`) |
| Math | LaTeX (`$x^2$`, `$$\sum_{i=1}^n$$`) |

## Requirements

- Python 3
