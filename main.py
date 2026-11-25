#!/usr/bin/env python3
"""Rename photos by the date they were taken.

Uses the EXIF DateTimeOriginal tag when present and falls back to the
file's modification time. Dry-run is the default: nothing is renamed
unless --confirm is given.
"""
import argparse
import os
import sys
from datetime import datetime

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".heic"}


def photo_date(path):
    """Return the date a photo was taken, or its modification time."""
    try:
        from PIL import Image

        with Image.open(path) as image:
            exif = image.getexif()
            if exif:
                # EXIF tag 36867 is DateTimeOriginal.
                raw = exif.get(36867) or exif.get(306)
                if raw:
                    try:
                        return datetime.strptime(str(raw), "%Y:%m:%d %H:%M:%S")
                    except ValueError:
                        pass
    except Exception:
        pass
    stamp = os.path.getmtime(path)
    return datetime.fromtimestamp(stamp)


def plan_renames(folder, prefix, date_format):
    names = sorted(
        name for name in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, name))
        and os.path.splitext(name)[1].lower() in IMAGE_EXTS
    )
    used = {}
    plan = []
    for name in names:
        src = os.path.join(folder, name)
        taken = photo_date(src)
        base = taken.strftime(date_format)
        if prefix:
            base = f"{prefix}_{base}"
        ext = os.path.splitext(name)[1].lower()
        candidate = f"{base}{ext}"
        count = used.get(candidate, 0)
        while candidate in used or (
            candidate != name and os.path.exists(os.path.join(folder, candidate))
        ):
            count += 1
            candidate = f"{base}_{count:02d}{ext}"
        used[candidate] = 1
        if candidate != name:
            plan.append((name, candidate))
    return plan


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Rename photos by the date they were taken."
    )
    parser.add_argument("folder", help="folder containing photos to rename")
    parser.add_argument("--prefix", default="",
                        help="optional prefix added before the date")
    parser.add_argument("--format", default="%Y-%m-%d_%H-%M-%S",
                        help="strftime format for the new name "
                             "(default: %%Y-%%m-%%d_%%H-%%M-%%S)")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="show what would be renamed without renaming (default)")
    parser.add_argument("--confirm", action="store_true",
                        help="actually rename the files (disables dry-run)")
    args = parser.parse_args(argv)

    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("Error: Pillow is not installed. Install it with: pip install Pillow",
              file=sys.stderr)
        return 1

    if not os.path.isdir(args.folder):
        print(f"Not a folder: {args.folder}", file=sys.stderr)
        return 1

    plan = plan_renames(args.folder, args.prefix, args.format)
    if not plan:
        print("Nothing to rename: no photos found, or names already match.")
        return 0

    dry_run = not args.confirm
    if dry_run:
        print("Dry run -- no files will be renamed. Use --confirm to rename.")
    for old, new in plan:
        if dry_run:
            print(f"  {old} -> {new}")
        else:
            os.rename(os.path.join(args.folder, old),
                      os.path.join(args.folder, new))
            print(f"Renamed: {old} -> {new}")

    action = "would rename" if dry_run else "renamed"
    print(f"{action.capitalize()}: {len(plan)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
