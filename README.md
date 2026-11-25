# Image Renamer by Date

Rename photos by the date they were taken. It reads the EXIF `DateTimeOriginal` tag when present and falls back to the file's modification time, producing names like `2026-11-25_10-30-00.jpg`.

## Requirements

- Python 3
- Pillow (`pip install -r requirements.txt`)

## How to run

```bash
pip install -r requirements.txt
python3 main.py --help
python3 main.py photos/
```

Dry-run is the default: the tool only shows what it would rename. Add `--confirm` to actually rename files.

Options:

- `--prefix` — optional prefix added before the date
- `--format` — strftime format for the new name (default: `%Y-%m-%d_%H-%M-%S`)
- `--confirm` — actually rename the files (disables dry-run)

## Example

```bash
$ python3 main.py photos/
Dry run -- no files will be renamed. Use --confirm to rename.
  IMG_1234.jpg -> 2026-11-25_10-30-00.jpg
  IMG_1235.jpg -> 2026-11-25_10-31-12.jpg
Would rename: 2 file(s).
```
