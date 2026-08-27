"""Convenience script: seeds today's challenge for the active sample theme(s)
using the placeholder CSVs in data/samples/. Run after `alembic upgrade head`.

Each theme's target position is picked at random (same as a normal import),
so it changes every time you rerun this.

For now only "Tema Aleatório" is seeded — the other 3 sample themes
(música, filmes, esportes) are commented out below, not deleted. To bring
one back: uncomment its entry here, rerun this script, and (if it already
exists but is hidden) run
`python scripts/set_theme_active.py --theme <slug> --active true`.

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
    # dict(
    #     theme_slug="musica",
    #     theme_name="Música",
    #     theme_icon="🎵",
    #     csv_path=SAMPLES / "musica_exemplo.csv",
    #     subtitle="[Exemplo] Músicas mais ouvidas em 2010",
    # ),
    # dict(
    #     theme_slug="filmes",
    #     theme_name="Filmes",
    #     theme_icon="🎬",
    #     csv_path=SAMPLES / "filmes_exemplo.csv",
    #     subtitle="[Exemplo] Filmes mais assistidos de todos os tempos",
    # ),
    # dict(
    #     theme_slug="esportes",
    #     theme_name="Esportes",
    #     theme_icon="⚽",
    #     csv_path=SAMPLES / "esportes_exemplo.csv",
    #     subtitle="[Exemplo] Times com mais títulos estaduais no Brasil",
    # ),
    dict(
        theme_slug="aleatorio",
        theme_name="Tema Aleatório",
        theme_icon="🎲",
        csv_path=SAMPLES / "aleatorio_exemplo.csv",
        subtitle="[Exemplo] Ranking aleatório de demonstração",
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
