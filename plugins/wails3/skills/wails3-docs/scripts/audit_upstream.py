#!/usr/bin/env python3
"""Audit the curated Wails v3 builder-doc inventory against upstream source."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


UPSTREAM_URL = "https://github.com/wailsapp/wails.git"
DOCS_RELATIVE = Path("docs/src/content/docs")
IN_SCOPE_ROOTS = (
    "quick-start",
    "getting-started",
    "concepts",
    "features",
    "guides",
    "reference",
    "tutorials",
    "experimental",
    "migration",
    "troubleshooting",
)
IN_SCOPE_FILES = {"faq.mdx", "status.mdx", "changelog.mdx"}


def run(command: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"command failed ({' '.join(command)}): {detail}")
    return result.stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_pages(docs: Path) -> set[str]:
    pages: set[str] = set()
    for root in IN_SCOPE_ROOTS:
        directory = docs / root
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and path.suffix in {".md", ".mdx"}:
                pages.add(path.relative_to(docs).as_posix())
    for filename in IN_SCOPE_FILES:
        if (docs / filename).is_file():
            pages.add(filename)
    return pages


def resolve_docs(source_dir: Path) -> tuple[Path, Path]:
    source_dir = source_dir.resolve()
    candidates = (source_dir / DOCS_RELATIVE, source_dir)
    for candidate in candidates:
        if (candidate / "concepts/architecture.mdx").is_file():
            return source_dir, candidate
    raise RuntimeError(
        f"{source_dir} is neither a Wails checkout nor its docs/src/content/docs directory"
    )


def clone_source(ref: str, destination: Path) -> tuple[Path, Path]:
    if not shutil.which("git"):
        raise RuntimeError("git is required when --source-dir is not supplied")
    run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--filter=blob:none",
            "--sparse",
            "--branch",
            ref,
            UPSTREAM_URL,
            str(destination),
        ]
    )
    run(["git", "sparse-checkout", "set", "docs"], cwd=destination)
    return destination, destination / DOCS_RELATIVE


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report Wails documentation additions, removals, changes, and mapping errors."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        help="Wails checkout or docs/src/content/docs directory; avoids network access.",
    )
    parser.add_argument(
        "--ref",
        default="master",
        help="Git branch/tag to clone when --source-dir is omitted (default: master).",
    )
    args = parser.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    manifest_path = skill_root / "references/source-manifest.json"

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest["pages"]
        recorded = {entry["source"]: entry for entry in entries}
        if len(recorded) != len(entries):
            print("ERROR: source-manifest.json contains duplicate source paths", file=sys.stderr)
            return 2

        with tempfile.TemporaryDirectory(prefix="wails3-doc-audit-") as temp:
            if args.source_dir:
                checkout, docs = resolve_docs(args.source_dir)
            else:
                checkout, docs = clone_source(args.ref, Path(temp) / "wails")

            current = discover_pages(docs)
            recorded_paths = set(recorded)
            added = sorted(current - recorded_paths)
            removed = sorted(recorded_paths - current)
            changed = sorted(
                source
                for source in current & recorded_paths
                if sha256(docs / source) != recorded[source]["sha256"]
            )

            missing_references: list[str] = []
            invalid_references: list[str] = []
            for source, entry in sorted(recorded.items()):
                reference = entry.get("reference", "")
                if not reference.startswith("references/") or not reference.endswith(".md"):
                    invalid_references.append(f"{source}: {reference!r}")
                elif not (skill_root / reference).is_file():
                    missing_references.append(f"{source}: {reference}")

            commit = "unknown"
            git_root = checkout if (checkout / ".git").exists() else None
            if git_root and shutil.which("git"):
                commit = run(["git", "rev-parse", "HEAD"], cwd=git_root)

            print(f"source commit: {commit}")
            print(f"recorded pages: {len(recorded_paths)}")
            print(f"current pages:  {len(current)}")

            sections = (
                ("ADDED upstream pages", added),
                ("REMOVED upstream pages", removed),
                ("CHANGED upstream pages", changed),
                ("MISSING local references", missing_references),
                ("INVALID reference mappings", invalid_references),
            )
            drift = False
            for title, items in sections:
                if not items:
                    continue
                drift = True
                print(f"\n{title} ({len(items)}):")
                for item in items:
                    print(f"  {item}")

            if drift:
                print("\nAudit found drift. Curate affected references, then update the manifest.")
                return 1

            print("Audit clean: upstream source and local coverage match the manifest.")
            return 0
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
