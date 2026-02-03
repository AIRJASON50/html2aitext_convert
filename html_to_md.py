#!/usr/bin/env python3
"""
HTML to Markdown Converter - Progressive Stripping Method

Converts arXiv LaTeXML HTML papers to clean Markdown by progressively
removing HTML features while preserving content.

Usage:
    python html_to_md.py input.html output.md
    python html_to_md.py input.html  # outputs to input.md
"""

import re
import sys
from pathlib import Path


def load_html(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def save_output(content: str, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {filepath}")


# ============================================================================
# Stage 1: Remove unwanted elements
# ============================================================================

def stage1_remove_unwanted(html: str) -> str:
    """Remove scripts, styles, nav, head, and other non-content elements."""
    html = re.sub(r'<head[^>]*>.*?</head>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    html = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'</?html[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'</?body[^>]*>', '', html, flags=re.IGNORECASE)
    return html


# ============================================================================
# Stage 2: Handle math expressions
# ============================================================================

def stage2_handle_math(html: str) -> str:
    """Extract LaTeX from <math> elements."""
    def math_replacer(m):
        content = m.group(0)
        is_block = 'display="block"' in content
        latex_match = re.search(
            r'<annotation[^>]*encoding="application/x-tex"[^>]*>(.*?)</annotation>',
            content, re.DOTALL
        )
        if latex_match:
            latex = latex_match.group(1).strip()
            latex = latex.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            if is_block:
                return f'\n\n$${latex}$$\n\n'
            else:
                return f'${latex}$'
        text = re.sub(r'<[^>]+>', '', content)
        return text.strip()

    html = re.sub(r'<math[^>]*>.*?</math>', math_replacer, html, flags=re.DOTALL)
    return html


# ============================================================================
# Stage 3: Convert semantic tags
# ============================================================================

def stage3_convert_semantic(html: str) -> str:
    """Convert semantic HTML tags to Markdown equivalents."""
    # Headings
    for i in range(1, 7):
        pattern = rf'<h{i}[^>]*>(.*?)</h{i}>'
        def heading_replacer(m, level=i):
            content = m.group(1)
            content = re.sub(r'<[^>]+>', '', content)
            content = ' '.join(content.split())
            if content:
                return f'\n\n{"#" * level} {content}\n\n'
            return ''
        html = re.sub(pattern, heading_replacer, html, flags=re.DOTALL | re.IGNORECASE)

    # Bold, italic, code
    html = re.sub(r'<(?:strong|b)[^>]*>(.*?)</(?:strong|b)>', r'**\1**', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<(?:em|i)[^>]*>(.*?)</(?:em|i)>', r'*\1*', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<hr\s*/?>', '\n\n---\n\n', html, flags=re.IGNORECASE)

    # Links
    def link_replacer(m):
        full_tag = m.group(0)
        href_match = re.search(r'href=["\']([^"\']+)["\']', full_tag)
        text = m.group(1)
        text = re.sub(r'<[^>]+>', '', text)
        text = ' '.join(text.split())
        if href_match and text:
            url = href_match.group(1)
            if 'arxiv.org/html' in url:
                anchor = url.split('#')[-1] if '#' in url else url
                return f'[{text}](#{anchor})'
            return f'[{text}]({url})'
        return text
    html = re.sub(r'<a[^>]*>(.*?)</a>', link_replacer, html, flags=re.DOTALL | re.IGNORECASE)

    # Citations
    def cite_replacer(m):
        content = m.group(1)
        refs = re.findall(r'ltx_ref_self">([^<]+)<', content)
        if refs:
            return '[' + ', '.join(refs) + ']'
        text = re.sub(r'<[^>]+>', '', content)
        return '[' + text.strip() + ']'
    html = re.sub(r'<cite[^>]*>(.*?)</cite>', cite_replacer, html, flags=re.DOTALL | re.IGNORECASE)

    return html


# ============================================================================
# Stage 4: Handle figures
# ============================================================================

def stage4_handle_figures(html: str) -> str:
    """Convert figures and images to markdown format."""
    def figure_replacer(m):
        content = m.group(0)
        result_parts = []
        for img_match in re.finditer(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*/?>',
                                      content, re.IGNORECASE):
            src = img_match.group(1)
            result_parts.append(f'![Figure]({src})')
        caption_match = re.search(r'<figcaption[^>]*>(.*?)</figcaption>',
                                   content, re.DOTALL | re.IGNORECASE)
        if caption_match:
            caption = caption_match.group(1)
            caption = re.sub(r'<[^>]+>', '', caption)
            caption = ' '.join(caption.split())
            if caption:
                result_parts.append(f'\n*{caption}*')
        return '\n\n' + '\n'.join(result_parts) + '\n\n' if result_parts else ''

    html = re.sub(r'<figure[^>]*>.*?</figure>', figure_replacer, html, flags=re.DOTALL | re.IGNORECASE)

    def img_replacer(m):
        src_match = re.search(r'src=["\']([^"\']+)["\']', m.group(0))
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', m.group(0))
        if src_match:
            src = src_match.group(1)
            alt = alt_match.group(1) if alt_match else "Image"
            return f'\n\n![{alt}]({src})\n\n'
        return ''
    html = re.sub(r'<img[^>]*/?>(?![^<]*</figure>)', img_replacer, html, flags=re.IGNORECASE)

    return html


# ============================================================================
# Stage 5: Handle tables
# ============================================================================

def stage5_handle_tables(html: str) -> str:
    """Convert tables to markdown format."""
    def table_replacer(m):
        table_html = m.group(0)
        rows = []
        for row_match in re.finditer(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE):
            row_content = row_match.group(1)
            cells = []
            for cell_match in re.finditer(r'<(?:th|td)[^>]*>(.*?)</(?:th|td)>',
                                           row_content, re.DOTALL | re.IGNORECASE):
                cell = cell_match.group(1)
                cell = re.sub(r'<[^>]+>', '', cell)
                cell = ' '.join(cell.split())
                cells.append(cell if cell else ' ')
            if cells:
                rows.append('| ' + ' | '.join(cells) + ' |')
        if len(rows) >= 1:
            num_cols = rows[0].count('|') - 1
            separator = '|' + '---|' * num_cols
            result = rows[0] + '\n' + separator
            if len(rows) > 1:
                result += '\n' + '\n'.join(rows[1:])
            return '\n\n' + result + '\n\n'
        return ''

    html = re.sub(r'<table[^>]*>.*?</table>', table_replacer, html, flags=re.DOTALL | re.IGNORECASE)
    return html


# ============================================================================
# Stage 6: Handle algorithms
# ============================================================================

def stage6_handle_algorithms(html: str) -> str:
    """Handle algorithm listing blocks."""
    def algorithm_replacer(m):
        content = m.group(0)
        caption_match = re.search(r'<figcaption[^>]*>(.*?)</figcaption>',
                                   content, re.DOTALL | re.IGNORECASE)
        title = ""
        if caption_match:
            title = re.sub(r'<[^>]+>', '', caption_match.group(1))
            title = ' '.join(title.split())
        lines = []
        for line_match in re.finditer(r'<div[^>]*class="ltx_listingline"[^>]*>(.*?)</div>',
                                       content, re.DOTALL):
            line = line_match.group(1)
            line = re.sub(r'<[^>]+>', '', line)
            line = line.strip()
            if line:
                lines.append(line)
        if lines:
            result = f'\n\n**{title}**\n\n```\n' if title else '\n\n```\n'
            result += '\n'.join(lines)
            result += '\n```\n\n'
            return result
        return ''

    html = re.sub(r'<figure[^>]*class="[^"]*ltx_float_algorithm[^"]*"[^>]*>.*?</figure>',
                  algorithm_replacer, html, flags=re.DOTALL | re.IGNORECASE)
    return html


# ============================================================================
# Stage 7: Handle definitions
# ============================================================================

def stage7_handle_definitions(html: str) -> str:
    """Handle definition, theorem blocks."""
    def def_replacer(m):
        content = m.group(0)
        title_match = re.search(r'<h6[^>]*>(.*?)</h6>', content, re.DOTALL | re.IGNORECASE)
        title = ""
        if title_match:
            title = re.sub(r'<[^>]+>', '', title_match.group(1))
            title = ' '.join(title.split())
        body_parts = []
        for para_match in re.finditer(r'<p[^>]*>(.*?)</p>', content, re.DOTALL):
            para = para_match.group(1)
            body_parts.append(para)
        if title:
            return f'\n\n**{title}**\n\n' + '\n\n'.join(body_parts) + '\n'
        return '\n' + '\n\n'.join(body_parts) + '\n'

    html = re.sub(r'<div[^>]*class="[^"]*ltx_theorem[^"]*"[^>]*>.*?</div>',
                  def_replacer, html, flags=re.DOTALL | re.IGNORECASE)
    return html


# ============================================================================
# Stage 8: Strip remaining tags
# ============================================================================

def stage8_strip_tags(html: str) -> str:
    """Remove all remaining HTML tags."""
    html = re.sub(r'</(?:p|div|section|article)>', '\n\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<(?:p|div|section|article)[^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<li[^>]*>', '\n- ', html, flags=re.IGNORECASE)
    html = re.sub(r'</li>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'</?(?:ul|ol)[^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'<span[^>]*class="[^"]*ltx_tag_equation[^"]*"[^>]*>\((\d+)\)</span>',
                  r'(\1)', html, flags=re.IGNORECASE)
    html = re.sub(r'<[^>]+>', '', html)
    return html


# ============================================================================
# Stage 9: Clean equation tables
# ============================================================================

def stage9_clean_equation_tables(text: str) -> str:
    """Convert equation tables to clean LaTeX display math."""
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect equation table row: | | $$...$$ | | (N) | or | | $\displaystyle...$ | ...
        eq_match = re.match(
            r'^\|\s*\|\s*\$\$([^$]+)\$\$\s*\|\s*\|\s*\((\d+)\)\s*\|$',
            line.strip()
        )
        if eq_match:
            formula = eq_match.group(1).strip()
            num = eq_match.group(2)
            result.append(f'$${formula}$$ \\tag{{{num}}}')
            # Skip separator line if present
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('|---'):
                i += 1
            i += 1
            continue

        # Detect multi-cell equation: | | $\displaystyle ... | $\displaystyle ... | | (N) |
        multi_eq_match = re.match(
            r'^\|\s*\|\s*\$\\displaystyle\s*([^$]+)\$\s*\|\s*\$\\displaystyle\s*([^$]+)\$\s*\|\s*\|\s*\((\d+)\)\s*\|',
            line.strip()
        )
        if multi_eq_match:
            # This is a multi-line equation block, collect all parts
            lhs = multi_eq_match.group(1).strip()
            rhs = multi_eq_match.group(2).strip()
            num = multi_eq_match.group(3)

            # Clean up % artifacts from LaTeX
            rhs = re.sub(r'%\s*', '', rhs)

            eq_lines = [(lhs, rhs, num)]
            i += 1

            # Skip separator
            if i < len(lines) and lines[i].strip().startswith('|---'):
                i += 1

            # Collect continuation lines: | | | $\displaystyle ... | | (N) |
            while i < len(lines):
                cont_match = re.match(
                    r'^\|\s*\|\s*\|\s*\$\\displaystyle\s*([^$]+)\$\s*\|\s*\|\s*\((\d+)\)\s*\|',
                    lines[i].strip()
                )
                if cont_match:
                    cont_formula = cont_match.group(1).strip()
                    cont_num = cont_match.group(2)
                    cont_formula = re.sub(r'%\s*', '', cont_formula)
                    eq_lines.append(('', cont_formula, cont_num))
                    i += 1
                else:
                    break

            # Format as aligned block
            result.append('$$')
            result.append('\\begin{aligned}')
            for j, (l, r, n) in enumerate(eq_lines):
                if j == 0:
                    result.append(f'{l} &{r} \\tag{{{n}}}' + (' \\\\' if len(eq_lines) > 1 else ''))
                else:
                    result.append(f'&{r} \\tag{{{n}}}' + (' \\\\' if j < len(eq_lines) - 1 else ''))
            result.append('\\end{aligned}')
            result.append('$$')
            continue

        # Detect single displaystyle equation: | | $\displaystyle...$ | | (N) |
        single_disp_match = re.match(
            r'^\|\s*\|\s*\$\\displaystyle\s*([^$]+)\$\s*\|\s*\|\s*\((\d+)\)\s*\|',
            line.strip()
        )
        if single_disp_match:
            formula = single_disp_match.group(1).strip()
            num = single_disp_match.group(2)
            formula = re.sub(r'%\s*', '', formula)
            result.append(f'$${formula}$$ \\tag{{{num}}}')
            # Skip separator
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('|---'):
                i += 1
            i += 1
            continue

        # Skip orphan separator lines (from equation tables)
        if line.strip().startswith('|---') and '|' in line:
            # Check if previous line was an equation we processed
            if result and ('\\tag{' in result[-1] or result[-1] == '$$'):
                i += 1
                continue

        result.append(line)
        i += 1

    return '\n'.join(result)


# ============================================================================
# Stage 10: Final cleanup
# ============================================================================

def stage10_cleanup(text: str) -> str:
    """Clean up whitespace and formatting."""
    entities = {
        '&nbsp;': ' ', '&lt;': '<', '&gt;': '>', '&amp;': '&', '&quot;': '"',
        '&#39;': "'", '&times;': '×', '&minus;': '−', '&plusmn;': '±',
        '&asymp;': '≈', '&ne;': '≠', '&le;': '≤', '&ge;': '≥',
        '&rarr;': '→', '&larr;': '←', '&uarr;': '↑', '&darr;': '↓',
        '&hellip;': '…', '&mdash;': '—', '&ndash;': '–',
        '&lsquo;': ''', '&rsquo;': ''', '&ldquo;': '"', '&rdquo;': '"',
        '&deg;': '°', '&infin;': '∞',
    }
    for entity, char in entities.items():
        text = text.replace(entity, char)
    text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
    text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
    text = re.sub(r'[^\S\n]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    text = text.strip()
    text = re.sub(r'\[\s*\]', '', text)
    text = re.sub(r'\(\s*\)', '', text)
    text = re.sub(r'\*\*\s*\*\*', '', text)
    text = re.sub(r'\n\.\n', '\n', text)
    return text


# ============================================================================
# Main
# ============================================================================

def convert_html_to_markdown(html: str, verbose: bool = True) -> str:
    """Convert HTML to Markdown by progressive stripping."""
    stages = [
        ("1. Remove unwanted elements", stage1_remove_unwanted),
        ("2. Handle math expressions", stage2_handle_math),
        ("3. Convert semantic tags", stage3_convert_semantic),
        ("4. Handle figures", stage4_handle_figures),
        ("5. Handle tables", stage5_handle_tables),
        ("6. Handle algorithms", stage6_handle_algorithms),
        ("7. Handle definitions", stage7_handle_definitions),
        ("8. Strip remaining tags", stage8_strip_tags),
        ("9. Clean equation tables", stage9_clean_equation_tables),
        ("10. Final cleanup", stage10_cleanup),
    ]

    content = html
    for name, func in stages:
        content = func(content)
        if verbose:
            tag_count = len(re.findall(r'<[^>]+>', content))
            print(f"  {name}: {len(content):,} chars, {tag_count} tags")

    return content


def main():
    if len(sys.argv) < 2:
        print("Usage: python html_to_md.py <input.html> [output.md]")
        print("\nConverts arXiv LaTeXML HTML papers to Markdown.")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_file = Path(sys.argv[2])
    else:
        output_file = input_file.with_suffix('.md')

    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()

    html_content = load_html(input_file)
    print(f"Loaded {len(html_content):,} characters\n")

    print("Converting:")
    markdown = convert_html_to_markdown(html_content)

    print(f"\nFinal: {len(markdown):,} characters")
    save_output(markdown, output_file)

    # Stats
    h2_count = len(re.findall(r'^## ', markdown, re.MULTILINE))
    h3_count = len(re.findall(r'^### ', markdown, re.MULTILINE))
    math_count = len(re.findall(r'\$[^$]+\$', markdown))
    print(f"\nStats: {h2_count} sections, {h3_count} subsections, {math_count} math expressions")


if __name__ == "__main__":
    main()
