#!/usr/bin/env python3
"""Download Svelte LLM docs into a project's docs/svelte directory."""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

DOCS = {
    "svelte-llms.md": "https://svelte.dev/docs/svelte/llms.txt",
    "sveltekit-llms.md": "https://svelte.dev/docs/kit/llms.txt",
}


def download(url: str) -> str:
    """Fetch a UTF-8 documentation page with a small user agent."""
    request = urllib.request.Request(url, headers={"User-Agent": "codex-svelte-skill"})
    with urllib.request.urlopen(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset)


def write_doc(path: Path, url: str, body: str) -> None:
    """Write docs atomically with the source URL retained for future audits."""
    content = f"<!-- Source: {url} -->\n\n{body.rstrip()}\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Project root where docs/svelte should be created. Defaults to the current directory.",
    )
    args = parser.parse_args()

    docs_dir = Path(args.project_root).resolve() / "docs" / "svelte"
    docs_dir.mkdir(parents=True, exist_ok=True)

    for filename, url in DOCS.items():
        try:
            body = download(url)
        except (urllib.error.URLError, TimeoutError) as exc:
            print(f"failed to download {url}: {exc}", file=sys.stderr)
            return 1

        target = docs_dir / filename
        write_doc(target, url, body)
        print(target)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
