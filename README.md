# Simple URL to Wikilinks replacer for Obsidian

A Python script to convert markdown links to [Obsidian](https://github.com/obsidianmd) wikilinks in a folder of notes. Good for anyone who saves a lot of clippings from the web with [obsidian clipper](https://github.com/obsidianmd/obsidian-clipper) or similar tool and wants to quickly link them together.

## Description

This script scans a directory containing Obsidian Markdown notes and replaces standard markdown links `[alias](url)` with Obsidian-style wikilinks `[[note filename|alias]]` where the URL in the link matches the `source` field in the YAML frontmatter of another note in the same folder.

This is useful for converting web clippings or imported notes into interconnected Obsidian notes using wikilinks instead of external URLs.

## Features

- Scans all `.md` files in the specified folder
- Extracts `source` URLs from YAML frontmatter
- Identifies markdown links that match these source URLs
- Replaces links with wikilinks pointing to the corresponding note
- Interactive preview and confirmation before applying changes
- Automatic backup of original files before modification
- Dry-run mode for safe previewing

## Requirements

- Python 3.6+
- Access to the folder containing your Obsidian notes

## Installation

1. Download the `wikilinks.py` script to your local machine.
2. Ensure Python 3 is installed on your system.

## Usage

Run the script from the command line, providing the path to your Obsidian notes folder:

```bash
python wikilinks.py /path/to/your/obsidian/folder
```

### Example

Suppose you have notes like:

- `note1.md` with YAML:
  ```
  ---
  source: https://example.com/article1
  ---
  ```

- `note2.md` containing a link: `[Interesting Article](https://example.com/article1)`

After running the script, `note2.md` will be updated to: `[[note1|Interesting Article]]`

### Options

- **Preview Mode**: The script will show a preview of all changes before asking for confirmation.
- **Apply Changes**: Type `yes` or `y` to apply the changes with backups.
- **Dry Run**: Type `dry-run`, `preview`, or `p` to show the preview again without applying changes.
- **Skip**: Any other input will skip the changes.

## Backups

By default, the script creates backups of all modified files in a designated backup directory. Each backup is timestamped to avoid overwriting previous backups.

## Notes

- Only `.md` files are processed.
- The script normalizes URLs by removing trailing slashes for matching.
- Ensure your notes have proper YAML frontmatter with a `source` field containing the URL.

## License

This script is provided as-is. Use at your own risk.
