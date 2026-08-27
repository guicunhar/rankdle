"""Imports a ranked list (CSV) as a daily challenge.

CSV columns: rank,name,image_url (image_url optional, may be blank)

Usage:
    python scripts/import_ranking.py \
        --csv ../data/samples/musica_2010.csv \
        --date 2026-08-26 \
        --theme musica --theme-name "Música" --theme-icon "🎵" \
        --subtitle "Músicas mais ouvidas em 2010" \
        --target-rank 34

If --theme doesn't exist yet it is created using --theme-name/--theme-icon.
Re-running with the same --date/--theme replaces that day's ranking items.
"""

import argparse
import csv
import sys
from datetime import date as date_type
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.daily_challenge import DailyChallenge
from app.models.ranking_item import RankingItem
from app.models.theme import Theme


def get_or_create_theme(db: Session, slug: str, name: str | None, icon: str) -> Theme:
    theme = db.query(Theme).filter(Theme.slug == slug).first()
    if theme is not None:
        return theme
    if not name:
        raise SystemExit(f"Theme '{slug}' doesn't exist yet; pass --theme-name to create it")
    theme = Theme(slug=slug, name=name, icon=icon, active=True)
    db.add(theme)
    db.commit()
    db.refresh(theme)
    return theme


def read_rows(csv_path: Path) -> list[dict]:
    with csv_path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = []
        for row in reader:
            rows.append(
                {
                    "rank": int(row["rank"]),
                    "name": row["name"].strip(),
                    "image_url": (row.get("image_url") or "").strip() or None,
                }
            )
    if not rows:
        raise SystemExit("CSV has no data rows")
    return rows


def import_ranking(
    db: Session,
    *,
    csv_path: Path,
    challenge_date: date_type,
    theme_slug: str,
    theme_name: str | None,
    theme_icon: str,
    subtitle: str,
    target_rank: int,
    lives: int | None = None,
) -> DailyChallenge:
    """Core import logic, callable directly from Python (no subprocess / argv involved,
    which avoids Windows console encoding issues with non-ASCII names)."""
    rows = read_rows(csv_path)
    ranks = {r["rank"] for r in rows}
    if target_rank not in ranks:
        raise SystemExit(f"--target-rank {target_rank} is not present in the CSV")

    theme = get_or_create_theme(db, theme_slug, theme_name, theme_icon)

    challenge = (
        db.query(DailyChallenge)
        .filter(DailyChallenge.date == challenge_date, DailyChallenge.theme_id == theme.id)
        .first()
    )
    if challenge is None:
        challenge = DailyChallenge(date=challenge_date, theme_id=theme.id)
        db.add(challenge)

    challenge.subtheme_title = subtitle
    challenge.target_rank = target_rank
    challenge.lives_override = lives
    db.flush()

    db.query(RankingItem).filter(RankingItem.daily_challenge_id == challenge.id).delete()
    for row in rows:
        db.add(RankingItem(daily_challenge_id=challenge.id, **row))

    db.commit()
    db.refresh(challenge)
    return challenge


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", required=True, help="Path to the CSV file (rank,name,image_url)")
    parser.add_argument("--date", required=True, help="Challenge date, YYYY-MM-DD")
    parser.add_argument("--theme", required=True, help="Theme slug, e.g. musica")
    parser.add_argument("--theme-name", default=None, help="Theme display name (needed to create a new theme)")
    parser.add_argument("--theme-icon", default="", help="Theme emoji icon")
    parser.add_argument("--subtitle", required=True, help='Subtheme title, e.g. "Músicas mais ouvidas em 2010"')
    parser.add_argument("--target-rank", required=True, type=int, help="Which rank is today's question")
    parser.add_argument("--lives", type=int, default=None, help="Override lives just for this challenge")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db = SessionLocal()
    try:
        challenge = import_ranking(
            db,
            csv_path=Path(args.csv),
            challenge_date=date_type.fromisoformat(args.date),
            theme_slug=args.theme,
            theme_name=args.theme_name,
            theme_icon=args.theme_icon,
            subtitle=args.subtitle,
            target_rank=args.target_rank,
            lives=args.lives,
        )
        print(
            f"Imported {len(challenge.items)} items for theme='{args.theme}' date={challenge.date} "
            f"(challenge_id={challenge.id}, target_rank={challenge.target_rank})"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
