"""Lista os rankings (desafios diários) cadastrados no banco.

    python scripts/list_rankings.py                # todos, marcando passado/hoje/futuro
    python scripts/list_rankings.py --upcoming     # só de hoje em diante (os "programados")
    python scripts/list_rankings.py --theme aleatorio

Usa a mesma string de banco do publish_ranking.py (backend/.env.prod.local,
ou a variável RANKDLE_DATABASE_URL do ambiente).
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def _load_prod_db_url() -> None:
    """Garante RANKDLE_DATABASE_URL no ambiente ANTES de importar app.core.db.
    Ordem: variável já exportada > backend/.env.prod.local."""
    if os.environ.get("RANKDLE_DATABASE_URL"):
        return

    env_file = BACKEND / ".env.prod.local"
    if not env_file.exists():
        sys.exit(
            "Falta backend/.env.prod.local (ou a variável RANKDLE_DATABASE_URL).\n"
            "Veja backend/.env.prod.local.example"
        )

    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

    if not os.environ.get("RANKDLE_DATABASE_URL"):
        sys.exit("RANKDLE_DATABASE_URL não encontrada em backend/.env.prod.local")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--upcoming", action="store_true", help="Só datas de hoje em diante")
    p.add_argument("--theme", default=None, help="Filtra por slug de tema")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    _load_prod_db_url()

    from app.core.db import SessionLocal
    from app.models.daily_challenge import DailyChallenge
    from app.models.theme import Theme

    today = date.today()
    db = SessionLocal()
    try:
        q = (
            db.query(DailyChallenge)
            .join(Theme)
            .order_by(DailyChallenge.date, Theme.slug)
        )
        if args.theme:
            q = q.filter(Theme.slug == args.theme)
        if args.upcoming:
            q = q.filter(DailyChallenge.date >= today)

        rows = q.all()
        if not rows:
            print("Nenhum ranking encontrado.")
            return

        for c in rows:
            if c.date < today:
                mark, when = "  ", "passado"
            elif c.date == today:
                mark, when = "→ ", "hoje   "
            else:
                mark, when = "* ", "futuro "
            print(
                f"{mark}{c.date}  {when}  [{c.theme.slug}]  "
                f"{len(c.items):>3} itens  alvo={c.target_rank:<3}  {c.subtheme_title}"
            )

        upcoming = sum(1 for c in rows if c.date >= today)
        print(f"\n{len(rows)} no total · {upcoming} de hoje em diante (*, →)")
    finally:
        db.close()


if __name__ == "__main__":
    main()
