# PNG Character Card Check
Quick and dirty tool to scan and automatically rename Character Card PNG files with `.card.png` suffix.

## Installation
Requires Python 3.6 or above.
`python pip install pillow tqdm`
(tqdm is optional, but makes a nice progress bar while scanning images)

## Usage
`python cardcheck.py [path] [--depth N] [--dry-run]`

### Arguments
- `path`: Directory to scan (default: current directory)
- `--depth N`: How many subfolders deep to scan (default: 3)
- `--dry-run`: Simulate rename without changing files

## Features
- Detects character cards using metadata and PNG chunk analysis
- Smart renaming with automatic conflict resolution (`file(1).card.png`, etc.)
- Recursive folder scanning with depth limit
- Dry run mode to preview changes
- Progress tracking (basic or enhanced with tqdm)

## How It Works
1. Scans PNG files looking for character card signatures:
   - Checks metadata for `chara`/`char_name` fields
   - Analyzes PNG chunks for character data patterns
   - Explicitly ignores AI-generated images with `prompt` metadata
2. Renames valid cards to `.card.png` format while preserving originals

## Tips
- Run with `--dry-run` first to verify which files will be renamed
- Use `--depth 1` for faster scans of flat directories
- For large collections, `tqdm` provides nicer progress bars
