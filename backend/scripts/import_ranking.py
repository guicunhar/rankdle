"""Imports a ranked list (CSV) as a daily challenge.

CSV columns (in Portuguese or English, case-insensitive):
  ranking / rank        -> the position number
  descrição / descricao / name -> what's at that position
  image_url             -> optional, may be omitted entirely or left blank

Usage:
    python scripts/import_ranking.py \
        --csv ../data/rankings/musica_2010.csv \
        --date 2026-08-26 \
        --theme musica --theme-name "Música" --theme-icon "🎵" \
        --subtitle "Músicas mais ouvidas em 2010"

The target position (the day's question) is picked at random from the CSV's
own range unless you pass --target-rank explicitly.

If --theme doesn't exist yet it is created using --theme-name/--theme-icon.
Re-running with the same --date/--theme replaces that day's ranking items
(and, unless --target-rank is given, rerolls a new random target).
"""

import argparse
import csv
import random
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


# Accepts either the Portuguese column names (what you'll actually be sending)
# or the English ones (used by the existing sample CSVs), case-insensitively.
RANK_ALIASES = {"ranking", "rank", "posicao", "posição"}
NAME_ALIASES = {"descricao", "descrição", "name", "nome"}
IMAGE_ALIASES = {"image_url", "imagem", "foto"}


def _normalize_header(header: str) -> str:
    return header.strip().lower()


def read_rows(csv_path: Path) -> list[dict]:
    with csv_path.open(encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit("CSV has no header row")

        header_map = {_normalize_header(h): h for h in reader.fieldnames}
        rank_col = next((header_map[a] for a in RANK_ALIASES if a in header_map), None)
        name_col = next((header_map[a] for a in NAME_ALIASES if a in header_map), None)
        image_col = next((header_map[a] for a in IMAGE_ALIASES if a in header_map), None)

        if rank_col is None or name_col is None:
            raise SystemExit(
                "CSV must have a ranking/rank column and a descrição/descricao/name column. "
                f"Found columns: {', '.join(reader.fieldnames)}"
            )

        rows = []
        for line_no, row in enumerate(reader, start=2):  # 1 is the header
            if not row.get(rank_col, "").strip() or not row.get(name_col, "").strip():
                continue  # skip blank trailing rows some spreadsheet exports leave behind
            try:
                rank = int(row[rank_col].strip())
            except ValueError:
                raise SystemExit(
                    f"Linha {line_no}: posição (rank) inválida: {row[rank_col]!r} — precisa ser um número inteiro"
                )
            rows.append(
                {
                    "rank": rank,
                    "name": row[name_col].strip(),
                    "image_url": (row.get(image_col, "") if image_col else "").strip() or None,
                }
            )
    if not rows:
        raise SystemExit("CSV has no data rows")

    seen: dict[int, str] = {}
    dups: list[str] = []
    for r in rows:
        if r["rank"] in seen:
            dups.append(f"{r['rank']} ({seen[r['rank']]!r} e {r['name']!r})")
        seen[r["rank"]] = r["name"]
    if dups:
        raise SystemExit(
            "CSV tem posições (rank) repetidas — cada linha precisa de um número único:\n  "
            + "\n  ".join(dups)
        )
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
    target_rank: int | None = None,
    lives: int | None = None,
    source_url: str | None = None,
) -> DailyChallenge:
    """Core import logic, callable directly from Python (no subprocess / argv involved,
    which avoids Windows console encoding issues with non-ASCII names).

    `target_rank` is optional: leave it out (the normal case) and a position is
    picked at random from whatever range the CSV covers, so the answer isn't
    predictable just from always asking about the same spot."""
    rows = read_rows(csv_path)
    ranks = {r["rank"] for r in rows}
    if target_rank is None:
        target_rank = random.choice(sorted(ranks))
    elif target_rank not in ranks:
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
    challenge.source_url = (source_url or "").strip() or None
    db.flush()

    db.query(RankingItem).filter(RankingItem.daily_challenge_id == challenge.id).delete()
    for row in rows:
        db.add(RankingItem(daily_challenge_id=challenge.id, **row))

    db.commit()
    db.refresh(challenge)
    return challenge


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--csv", required=True, help="Path to the CSV file (columns: ranking, descrição)")
    parser.add_argument("--date", required=True, help="Challenge date, YYYY-MM-DD")
    parser.add_argument("--theme", required=True, help="Theme slug, e.g. musica")
    parser.add_argument("--theme-name", default=None, help="Theme display name (needed to create a new theme)")
    parser.add_argument("--theme-icon", default="", help="Theme emoji icon")
    parser.add_argument("--subtitle", required=True, help='Subtheme title, e.g. "Músicas mais ouvidas em 2010"')
    parser.add_argument("--source", default=None, help="URL da fonte dos dados, mostrada ao jogador no fim do jogo")
    parser.add_argument(
        "--target-rank",
        type=int,
        default=None,
        help="Which rank is today's question. Omit to pick one at random from the CSV.",
    )
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
            source_url=args.source,
        )
        print(
            f"Imported {len(challenge.items)} items for theme='{args.theme}' date={challenge.date} "
            f"(challenge_id={challenge.id}, target_rank={challenge.target_rank})"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
