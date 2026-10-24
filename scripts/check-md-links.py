#!/usr/bin/env python3
"""
Markdown link checker for the llama-swap configuration repo.

Checks that all relative internal links in .md files resolve to existing
files. External links and anchor-only links are skipped.

Usage:
    python3 scripts/check-md-links.py
    python3 scripts/check-md-links.py --strict   # also fail on dead links
"""

import os
import re
import sys
from pathlib import Path

# Repos root = two levels up from this script's directory
REPO_ROOT = Path(__file__).resolve().parents[1]

# Directories to skip entirely
SKIP_DIRS = {
    ".venv",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    "htmlcov",
    ".direnv",
    "node_modules",
    "__pycache__",
}

# Extensions to skip
SKIP_EXTS = {".pyc", ".pyo", ".so", ".bin", ".dat", ".db", ".sqlite", ".md"}

# Link patterns: `[text](path)` and `![alt](path)`
LINK_RE = re.compile(r"!?\[.*?\]\(([^)]+)\)")


def should_skip_dir(dir_path: Path) -> bool:
    """Return True if this directory should be skipped."""
    return any(part in SKIP_DIRS for part in dir_path.relative_to(REPO_ROOT).parts)


def resolve_link(file_path: Path, link: str) -> Path | None:
    """Resolve a relative link against the directory of file_path."""
    # Skip external links
    if link.startswith("http") or link.startswith("//"):
        return None

    # Strip anchor fragments
    link = link.split("#", 1)[0].rstrip("/")

    if not link:
        return None

    # Resolve as relative to the file's directory
    target = (file_path.parent / link).resolve()
    return target


def check_file(md_file: Path) -> list[tuple[Path, str, str]]:
    """Return a list of (file, link, resolved_target) for broken links."""
    broken = []
    try:
        content = md_file.read_text(encoding="utf-8")
    except Exception:
        return broken

    for m in LINK_RE.finditer(content):
        link = m.group(1)
        resolved = resolve_link(md_file, link)
        if resolved is None:
            continue
        if not resolved.exists():
            broken.append((md_file, link, str(resolved)))

    return broken


def find_md_files(root: Path) -> list[Path]:
    """Recursively find all .md files, skipping hidden dirs."""
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirpath_path = Path(dirpath)
        if should_skip_dir(dirpath_path):
            dirnames[:] = []
            continue
        # Filter out hidden dirs in-place
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for f in filenames:
            if f.endswith(".md"):
                md_files.append(Path(dirpath) / f)
    return md_files


def main():
    strict = "--strict" in sys.argv
    md_files = find_md_files(REPO_ROOT)

    all_broken = []
    for md_file in sorted(md_files):
        broken = check_file(md_file)
        all_broken.extend(broken)

    if not all_broken:
        print("All internal links resolve correctly.")
        return 0

    print(f"\n{len(all_broken)} broken link(s) found:\n")
    for md_file, link, target in sorted(all_broken, key=lambda x: str(x[0])):
        rel = md_file.relative_to(REPO_ROOT)
        print(f"  {rel}/{link}")
        print(f"    -> resolves to: {target}\n")

    if strict:
        print("FAIL: broken links found.")
        return 1
    else:
        print("WARN: broken links found (non-strict mode).")
        return 0


if __name__ == "__main__":
    sys.exit(main())
