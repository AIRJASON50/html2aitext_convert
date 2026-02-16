#!/usr/bin/env python3
"""
arxiv2html.py - Download arXiv paper HTML

Usage:
    python arxiv2html.py 2502.04307 output.html
    python arxiv2html.py 2502.04307  # → 2502.04307.html
"""

import sys
import ssl
import urllib.request
import urllib.error
from pathlib import Path


def download_arxiv_html(arxiv_id: str, output_path: str = None) -> str:
    """Download arXiv HTML and return output path."""
    # Clean arxiv_id
    arxiv_id = arxiv_id.replace("arXiv:", "").replace("arxiv:", "").strip()

    url = f"https://arxiv.org/html/{arxiv_id}"

    if output_path is None:
        output_path = f"{arxiv_id}.html"

    print(f"arXiv ID: {arxiv_id}")
    print(f"URL: {url}")

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read()
        except urllib.error.URLError as e:
            if isinstance(e.reason, ssl.SSLCertVerificationError):
                # Fallback: skip SSL verification (common on Windows / conda Python)
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
                    html = response.read()
            else:
                raise
    except urllib.error.HTTPError as e:
        print(f"Error: HTTP {e.code} - {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: {e.reason}")
        sys.exit(1)

    # Check if HTML is available
    if b"No HTML available" in html or b"not found" in html.lower():
        print("Error: No HTML version available for this paper")
        sys.exit(1)

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(html)

    size_kb = len(html) / 1024
    print(f"Downloaded: {output_path} ({size_kb:.0f}K)")

    return output_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python arxiv2html.py <arxiv_id> [output.html]")
        print("Example: python arxiv2html.py 2502.04307")
        sys.exit(1)

    arxiv_id = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    download_arxiv_html(arxiv_id, output_path)


if __name__ == "__main__":
    main()
