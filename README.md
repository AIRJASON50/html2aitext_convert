# html2aitext_convert

Convert arXiv HTML papers to AI-friendly text (Markdown + LaTeX math).

## Features

- Preserves LaTeX math formulas (`$inline$`, `$$block$$`)
- Converts structure to Markdown
- Cleans equation tables to proper LaTeX format
- 10-stage progressive HTML stripping

## Usage

```bash
python html_to_md.py input.html output.md
```

## Output Format

| Content | Format |
|---------|--------|
| Text | Plain text |
| Structure | Markdown (`##`, `###`, `**bold**`) |
| Math | LaTeX (`$x^2$`, `$$\sum_{i=1}^n$$`) |

## Workflow

1. Download HTML from arXiv ("View HTML" button)
2. Run converter
3. Feed output to AI (Claude, GPT, etc.)
