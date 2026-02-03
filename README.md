# html2aitext_convert

Convert arXiv HTML papers to AI-friendly text (Markdown + LaTeX math).

## Quick Start

```bash
./arxiv2md.sh 2502.04307
```

That's it! Output will be in `output/2502.04307.md`.

## Features

- One-command arXiv paper download and conversion
- Preserves LaTeX math formulas (`$inline$`, `$$block$$`)
- Converts structure to Markdown
- Cleans equation tables to proper LaTeX format
- 10-stage progressive HTML stripping

## Usage

### From arXiv ID (recommended)
```bash
./arxiv2md.sh 2502.04307
./arxiv2md.sh arXiv:2502.04307  # also works
```

### From local HTML file
```bash
python html_to_md.py input.html output.md
```

## Output Format

| Content | Format |
|---------|--------|
| Text | Plain text |
| Structure | Markdown (`##`, `###`, `**bold**`) |
| Math | LaTeX (`$x^2$`, `$$\sum_{i=1}^n$$`) |

## Requirements

- Python 3
- curl
