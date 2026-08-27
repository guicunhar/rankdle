"""Activates or deactivates a theme (shows/hides it in the theme picker) without
deleting any of its data — daily challenges, ranking items and game history
all stay put, ready to come back the moment you reactivate it.

Usage:
    python scripts/set_theme_active.py --theme musica --active false
    python scripts/set_theme_active.py --theme musica --active true
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.db import SessionLocal
from app.models.theme import Theme


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--theme", required=True, help="Theme slug, e.g. musica")
    parser.add_argument("--active", required=True, choices=["true", "false"])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db = SessionLocal()
    try:
        theme = db.query(Theme).filter(Theme.slug == args.theme).first()
        if theme is None:
            raise SystemExit(f"Theme '{args.theme}' not found")
        theme.active = args.active == "true"
        db.commit()
        print(f"Theme '{args.theme}' ({theme.name}) active={theme.active}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
