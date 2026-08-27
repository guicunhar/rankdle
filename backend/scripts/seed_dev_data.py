"""Convenience script: seeds today's challenge for all 4 sample themes using the
placeholder CSVs in data/samples/. Run after `alembic upgrade head`.

    python scripts/seed_dev_data.py
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.db import SessionLocal
from scripts.import_ranking import import_ranking

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT.parent / "data" / "samples"
TODAY = date.today()

THEMES = [
    dict(
        theme_slug="musica",
        theme_name="Música",
        theme_icon="🎵",
        csv_path=SAMPLES / "musica_exemplo.csv",
        subtitle="[Exemplo] Músicas mais ouvidas em 2010",
        target_rank=34,
    ),
    dict(
        theme_slug="filmes",
        theme_name="Filmes",
        theme_icon="🎬",
        csv_path=SAMPLES / "filmes_exemplo.csv",
        subtitle="[Exemplo] Filmes mais assistidos de todos os tempos",
        target_rank=12,
    ),
    dict(
        theme_slug="esportes",
        theme_name="Esportes",
        theme_icon="⚽",
        csv_path=SAMPLES / "esportes_exemplo.csv",
        subtitle="[Exemplo] Times com mais títulos estaduais no Brasil",
        target_rank=5,
    ),
    dict(
        theme_slug="aleatorio",
        theme_name="Tema Aleatório",
        theme_icon="🎲",
        csv_path=SAMPLES / "aleatorio_exemplo.csv",
        subtitle="[Exemplo] Ranking aleatório de demonstração",
        target_rank=20,
    ),
]


def main() -> None:
    db = SessionLocal()
    try:
        for cfg in THEMES:
            challenge = import_ranking(db, challenge_date=TODAY, **cfg)
            print(
                f"Imported {len(challenge.items)} items for theme='{cfg['theme_slug']}' "
                f"date={challenge.date} (challenge_id={challenge.id}, target_rank={challenge.target_rank})"
            )
    finally:
        db.close()


if __name__ == "__main__":
    main()
