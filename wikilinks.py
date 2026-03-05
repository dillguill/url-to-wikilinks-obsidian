#!/usr/bin/env python3
"""
Obsidian URL → Wikilink Replacer
---------------------------------
Scans a folder of Obsidian clippings and replaces markdown links [alias](url)
with [[note filename|alias]] where the URL matches a note's YAML `source` field.

Usage:
    python replace_urls_with_wikilinks.py /path/to/your/clippings/folder
"""

import os
import re
import sys
import shutil
from datetime import datetime


# ── Regex patterns ────────────────────────────────────────────────────────────
MD_LINK_RE = re.compile(r'\[([^\]]+)\]\((https?://[^)]+)\)')
YAML_SOURCE_RE = re.compile(r'^source:\s*["\']?(https?://[^\s"\']+)["\']?', re.MULTILINE)
YAML_BLOCK_RE = re.compile(r'^---\s*\n(.*?)\n---', re.DOTALL)


def extract_source_url(content: str) -> str | None:
    """Pull the source URL out of a note's YAML frontmatter."""
    yaml_match = YAML_BLOCK_RE.match(content)
    if not yaml_match:
        return None
    source_match = YAML_SOURCE_RE.search(yaml_match.group(1))
    return source_match.group(1).rstrip('/') if source_match else None


def build_url_to_note_map(folder: str) -> dict[str, str]:
    """
    Walk the folder and return a dict of:
        { normalized_url: note_filename_without_extension }
    """
    url_map = {}
    for fname in os.listdir(folder):
        if not fname.endswith('.md'):
            continue
        fpath = os.path.join(folder, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        url = extract_source_url(content)
        if url:
            note_name = os.path.splitext(fname)[0]
            url_map[url.rstrip('/')] = note_name
    return url_map


def find_replacements(content: str, url_map: dict[str, str]) -> list[tuple]:
    """
    Return a list of (original_match, replacement_string) tuples.
    Only includes matches where the URL exists in url_map.
    """
    replacements = []
    for match in MD_LINK_RE.finditer(content):
        alias, url = match.group(1), match.group(2).rstrip('/')
        if url in url_map:
            note_name = url_map[url]
            wiki = f'[[{note_name}|{alias}]]'
            replacements.append((match.group(0), wiki, alias, url, note_name))
    return replacements


def preview(folder: str, url_map: dict[str, str]) -> dict[str, list]:
    """Print a preview of all planned changes. Returns changes dict."""
    all_changes = {}
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith('.md'):
            continue
        fpath = os.path.join(folder, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        replacements = find_replacements(content, url_map)
        if replacements:
            all_changes[fname] = replacements

    if not all_changes:
        print("\n✅ No replaceable links found — nothing to do.")
        return {}

    print(f"\n{'─'*60}")
    print(f"  PREVIEW — {sum(len(v) for v in all_changes.values())} replacement(s) across {len(all_changes)} note(s)")
    print(f"{'─'*60}")
    for fname, replacements in all_changes.items():
        print(f"\n📄 {fname}")
        for original, wiki, alias, url, note_name in replacements:
            print(f"   BEFORE: {original}")
            print(f"   AFTER:  {wiki}")
    print(f"\n{'─'*60}")
    return all_changes


def apply_changes(folder: str, all_changes: dict[str, list], backup: bool = True):
    """Apply replacements and optionally back up originals."""
    if backup:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(folder, f'_backup_{timestamp}')
        os.makedirs(backup_dir, exist_ok=True)
        print(f"\n💾 Backing up originals to: {backup_dir}")

    changed = 0
    for fname, replacements in all_changes.items():
        fpath = os.path.join(folder, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()

        if backup:
            shutil.copy2(fpath, os.path.join(backup_dir, fname))

        new_content = content
        for original, wiki, *_ in replacements:
            new_content = new_content.replace(original, wiki, 1)

        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        changed += 1
        print(f"   ✅ Updated: {fname} ({len(replacements)} replacement(s))")

    print(f"\n🎉 Done — {changed} file(s) updated.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python replace_urls_with_wikilinks.py /path/to/clippings")
        sys.exit(1)

    folder = sys.argv[1].rstrip('/')
    if not os.path.isdir(folder):
        print(f"❌ Folder not found: {folder}")
        sys.exit(1)

    print(f"🔍 Scanning: {folder}")
    url_map = build_url_to_note_map(folder)
    print(f"   Found {len(url_map)} note(s) with a source URL in frontmatter")

    if not url_map:
        print("❌ No notes with YAML 'source:' fields found. Nothing to do.")
        sys.exit(0)

    all_changes = preview(folder, url_map)
    if not all_changes:
        sys.exit(0)

    print("\nApply these changes? (yes/no/dry-run to preview again): ", end='')
    answer = input().strip().lower()

    if answer in ('yes', 'y'):
        apply_changes(folder, all_changes, backup=True)
    elif answer in ('dry-run', 'preview', 'p'):
        preview(folder, url_map)
    else:
        print("⏭️  Skipped — no files modified.")


if __name__ == '__main__':
    main()
