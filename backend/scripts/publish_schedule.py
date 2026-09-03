"""Publica vários desafios de uma vez a partir de um JSON.

O calendário fica em `data/desafios.json` (fora de `backend/`):

    {
      "desafios": [
        {
          "data": "2026-09-03",
          "csv": "steam_pico_diario",
          "titulo": "Jogos da Steam com maior pico diário de jogadores",
          "fonte": "https://steamdb.info/charts/"
        }
      ]
    }

Campos obrigatórios por item: data (AAAA-MM-DD), csv (nome do arquivo em
data/rankings/, o ".csv" é opcional), titulo, fonte (URL mostrada ao
jogador no fim do jogo).

Opcionais: tema (slug, padrão "aleatorio"), tema_nome, tema_icone,
gabarito (fixa a posição-resposta; padrão sorteia), vidas.

Uso (rode de dentro de `backend/`, com o venv ativo):

    python scripts/publish_schedule.py              # publica o que ainda não existe
    python scripts/publish_schedule.py --dry-run    # só mostra o que faria
    python scripts/publish_schedule.py --only 2026-09-03
    python scripts/publish_schedule.py --force      # reimporta mesmo se já existe (re-sorteia o gabarito!)

Por padrão, itens cuja data+tema já têm desafio no banco são pulados, para
não re-sortear a resposta de um dia já publicado. Use --force para sobrepor.

A string do banco de produção sai de `backend/.env.prod.local` (fora do
git); se RANKDLE_DATABASE_URL já estiver no ambiente, ela tem prioridade.
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND.parent / "data"
RANKINGS_DIR = DATA_DIR / "rankings"
SCHEDULE_FILE = DATA_DIR / "desafios.json"
sys.path.insert(0, str(BACKEND))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def _load_prod_db_url() -> None:
    """Garante RANKDLE_DATABASE_URL no ambiente ANTES de importar app.core.db."""
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


def resolve_csv(name: str) -> Path:
    filename = Path(str(name)).name
    if not filename.lower().endswith(".csv"):
        filename += ".csv"
    path = RANKINGS_DIR / filename
    if not path.exists():
        existing = sorted(p.name for p in RANKINGS_DIR.glob("*.csv"))
        listing = "\n  ".join(existing) if existing else "(nenhum .csv em data/rankings/)"
        sys.exit(f"CSV não encontrado: {path}\nDisponíveis:\n  {listing}")
    return path


def load_schedule(path: Path) -> list[dict]:
    if not path.exists():
        sys.exit(f"Calendário não encontrado: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"JSON inválido em {path}: {e}")

    items = raw.get("desafios") if isinstance(raw, dict) else raw
    if not isinstance(items, list) or not items:
        sys.exit('O JSON precisa ter uma lista "desafios" com pelo menos um item.')

    for i, entry in enumerate(items, start=1):
        faltando = [k for k in ("data", "csv", "titulo", "fonte") if not str(entry.get(k, "")).strip()]
        if faltando:
            sys.exit(f"Item {i} do calendário sem campo(s) obrigatório(s): {', '.join(faltando)}")
        try:
            date.fromisoformat(entry["data"])
        except ValueError:
            sys.exit(f"Item {i}: data inválida {entry['data']!r} — use AAAA-MM-DD")
    return items


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--file", default=str(SCHEDULE_FILE), help=f"Caminho do JSON (padrão: {SCHEDULE_FILE})")
    p.add_argument("--only", default=None, help="Publica só a data AAAA-MM-DD informada")
    p.add_argument("--force", action="store_true", help="Reimporta mesmo se o dia já existe (re-sorteia o gabarito)")
    p.add_argument("--dry-run", action="store_true", help="Só mostra o que faria")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    entries = load_schedule(Path(args.file))
    if args.only:
        entries = [e for e in entries if e["data"] == args.only]
        if not entries:
            sys.exit(f"Nenhum item no calendário com data {args.only}")

    _load_prod_db_url()

    from app.core.db import SessionLocal
    from app.models.daily_challenge import DailyChallenge
    from app.models.theme import Theme
    from scripts.import_ranking import import_ranking

    db = SessionLocal()
    publicados = pulados = 0
    try:
        for entry in entries:
            challenge_date = date.fromisoformat(entry["data"])
            theme_slug = str(entry.get("tema") or "aleatorio")
            csv_path = resolve_csv(entry["csv"])

            theme = db.query(Theme).filter(Theme.slug == theme_slug).first()
            existing = (
                db.query(DailyChallenge)
                .filter(DailyChallenge.date == challenge_date, DailyChallenge.theme_id == theme.id)
                .first()
                if theme is not None
                else None
            )
            if existing is not None and not args.force:
                print(f"pula   {challenge_date} [{theme_slug}] — já existe (challenge_id={existing.id})")
                pulados += 1
                continue

            if args.dry_run:
                print(f"(dry)  {challenge_date} [{theme_slug}] {entry['csv']} :: {entry['titulo']}")
                publicados += 1
                continue

            challenge = import_ranking(
                db,
                csv_path=csv_path,
                challenge_date=challenge_date,
                theme_slug=theme_slug,
                theme_name=entry.get("tema_nome") or "Tema Aleatório",
                theme_icon=entry.get("tema_icone") or "🎲",
                subtitle=entry["titulo"],
                target_rank=entry.get("gabarito"),
                lives=entry.get("vidas"),
                source_url=entry["fonte"],
            )
            theme = db.query(Theme).filter(Theme.slug == theme_slug).first()
            if theme is not None and not theme.active:
                theme.active = True
                db.commit()

            print(
                f"OK     {challenge.date} [{theme_slug}] {len(challenge.items)} itens "
                f"(challenge_id={challenge.id}, target_rank={challenge.target_rank})"
            )
            publicados += 1
    finally:
        db.close()

    verbo = "seriam publicados" if args.dry_run else "publicados"
    print(f"\n{publicados} {verbo} · {pulados} pulados")


if __name__ == "__main__":
    main()
