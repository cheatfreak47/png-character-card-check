# cardcheck/main.py
import os
import json
import base64
import struct
import sys
import zlib
import argparse
from pathlib import Path

# Dependency check with helpful errors
try:
    from PIL import Image
except ImportError:
    sys.exit("Error: Pillow library required. Install with: pip install pillow")

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    class SimpleProgress:
        def __init__(self, iterable, desc=None, total=None, **kwargs):
            self.iterable = iter(iterable)
            self.total = total or len(iterable)
            self.desc = desc or "Processing"
            self.count = 0

        def __iter__(self):
            return self

        def __next__(self):
            item = next(self.iterable)
            self.count += 1
            if self.count % 10 == 0 or self.count == self.total:
                print(f"\r{self.desc}: {self.count}/{self.total}", end='', file=sys.stderr)
                if self.count == self.total:
                    print("", file=sys.stderr)  # Newline when done
            return item

def is_character_card(png_path):
    """Strict character card detection that ignores prompt metadata"""
    try:
        # Phase 1: Quick PIL Metadata Scan
        with Image.open(png_path) as img:
            # Skip anything with generic image-gen metadata
            if 'prompt' in img.info or 'parameters' in img.info:
                return False
            if any(key.lower() in ['chara', 'char_name', 'tavernai'] for key in img.info):
                return True

        # Phase 2: Raw Chunk Autopsy
        with open(png_path, 'rb') as f:
            if f.read(8) != b'\x89PNG\r\n\x1a\n':
                return False

            while True:
                length, chunk_type = struct.unpack('>I4s', f.read(8))
                data = f.read(length)
                f.read(4)  # CRC

                if chunk_type in [b'tEXt', b'zTXt', b'iTXt']:
                    decoded_data = data.lower()
                    if (b'chara' in decoded_data or
                        b'char_name' in decoded_data or
                        b'"name":' in decoded_data):
                        if b'prompt' not in decoded_data:
                            return True
                if length == 0:
                    break
    except Exception:
        return False
    return False

def rename_cards(root_dir=".", max_depth=3, dry_run=False):
    """Renames character cards with progress tracking and safety checks"""
    root_dir = os.path.abspath(root_dir)
    cards_renamed = 0

    print(f"{'DRY RUN - ' if dry_run else ''}Scanning: {root_dir} (max depth: {max_depth})", file=sys.stderr)
    if not HAS_TQDM:
        print("(Install 'tqdm' with 'pip install tqdm' for better progress bars)", file=sys.stderr)

    # Collect all candidate files first
    all_files = []
    for subdir, _, files in os.walk(root_dir):
        current_depth = subdir[len(root_dir):].count(os.sep)
        if current_depth > max_depth:
            continue
        all_files.extend(
            os.path.join(subdir, f)
            for f in files
            if f.lower().endswith('.png') and not f.lower().endswith('.card.png')
        )

    # Initialize progress tracker
    Progress = tqdm if HAS_TQDM else SimpleProgress
    progress = Progress(
        all_files,
        desc="Scanning PNGs",
        total=len(all_files),
        file=sys.stderr if HAS_TQDM else None
    )

    for filepath in progress:
        if not is_character_card(filepath):
            continue

        subdir, filename = os.path.split(filepath)
        base_name = os.path.splitext(filename)[0]
        new_name = f"{base_name}.card.png"
        new_path = os.path.join(subdir, new_name)

        if os.path.exists(new_path):
            counter = 1
            while True:
                numbered_name = f"{base_name}({counter}).card.png"
                numbered_path = os.path.join(subdir, numbered_name)
                if not os.path.exists(numbered_path):
                    new_name = numbered_name
                    new_path = numbered_path
                    break
                counter += 1

        action = "Would rename" if dry_run else "Renamed"
        msg = f"{action}: {filename[:20]}... → {new_name}"
        print(msg, file=sys.stderr)

        if not dry_run:
            os.rename(filepath, new_path)
        cards_renamed += 1

    # Final status
    if cards_renamed == 0:
        print("No cards found!", file=sys.stderr)
    elif dry_run:
        print(f"Dry run complete - would rename {cards_renamed} files", file=sys.stderr)
    return cards_renamed

def cli():
    """Command-line interface entry point"""
    parser = argparse.ArgumentParser(
        description='PNG Character Card checker/renamer',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('path', nargs='?', default='.', help='Directory to scan')
    parser.add_argument('--depth', type=int, default=3, help='Max folder depth (default: 3)')
    parser.add_argument('--dry-run', action='store_true', help='Simulate without renaming')
    args = parser.parse_args()

    rename_cards(
        root_dir=args.path,
        max_depth=args.depth,
        dry_run=args.dry_run
    )

if __name__ == "__main__":
    cli()
