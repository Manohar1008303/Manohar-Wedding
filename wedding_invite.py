"""
Auto-update helper for the Manohar & Dhanashri wedding invite.

What it does:
  - Watches your Downloads folder.
  - When a new invite file arrives (index.html, index 2.html, index (1).html,
    wedding-invite.html ...), it moves it into your Manohar-Wedding folder
    as index.html, replacing the old one.
  - Then open GitHub Desktop and click "Commit to main" and "Push origin".

How to run (in Terminal):
  python3 ~/Documents/GitHub/auto_update_invite.py

Leave the Terminal window open while you work. Press Ctrl + C to stop.
"""

import re
import shutil
import time
from pathlib import Path

# ---- Change these two paths only if your folders are somewhere else ----
DOWNLOADS = Path.home() / "Downloads"
REPO = Path.home() / "Documents" / "GitHub" / "Manohar-Wedding"
# -------------------------------------------------------------------------

TARGET = REPO / "index.html"
SITE = "https://manohar1008303.github.io/Manohar-Wedding/"
NAME_PATTERN = re.compile(r"^(index|wedding-invite)( ?\(?\d+\)?|[-_ ]\d+)?\.html$", re.IGNORECASE)
CHECK_EVERY = 2  # seconds


def is_invite_file(path: Path) -> bool:
    return path.is_file() and bool(NAME_PATTERN.match(path.name))


def wait_until_finished(path: Path) -> bool:
    """Wait until the download has stopped growing."""
    last_size = -1
    for _ in range(30):
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return False
        if size == last_size and size > 0:
            return True
        last_size = size
        time.sleep(1)
    return False


def looks_like_the_invite(path: Path) -> bool:
    """Small safety check so we never replace the site with a random HTML file."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return "<!doctype html" in text.lower() and "Dhanashri" in text


def main() -> None:
    if not REPO.is_dir():
        print(f"Could not find your website folder:\n  {REPO}")
        print("Open GitHub Desktop > Repository > Show in Finder, then update REPO at the top of this file.")
        return

    print("Watching Downloads for a new invite file...")
    print(f"  Downloads: {DOWNLOADS}")
    print(f"  Website folder: {REPO}")
    print("Press Ctrl + C to stop.\n")

    started = time.time()
    seen = set()

    while True:
        for path in DOWNLOADS.iterdir():
            if not is_invite_file(path):
                continue
            try:
                modified = path.stat().st_mtime
            except FileNotFoundError:
                continue
            key = (path.name, modified)
            if modified < started or key in seen:
                continue
            seen.add(key)

            if not wait_until_finished(path):
                continue
            if not looks_like_the_invite(path):
                print(f"Skipped {path.name} (it doesn't look like the wedding invite).")
                continue

            shutil.move(str(path), str(TARGET))
            stamp = time.strftime("%H:%M:%S")
            print(f"[{stamp}] Updated index.html from '{path.name}'.")
            print("  Next: GitHub Desktop > Commit to main > Push origin")
            print(f"  Site: {SITE}\n")

        time.sleep(CHECK_EVERY)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")