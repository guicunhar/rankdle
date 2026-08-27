"""Publica um ranking num passo só: importa o CSV e garante o tema ativo.

Uso (rode de dentro de `backend/`, com o venv ativo):

    python scripts/publish_ranking.py 2026-08-28 steam_pico_diario "Jogos da Steam com Maior Pico Diário de Jogadores"

Três argumentos, nessa ordem:
  1. data      AAAA-MM-DD  (aceita "hoje")
  2. arquivo   só o nome — sempre procurado em data/rankings/ (o ".csv" é
               opcional)
  3. subtítulo texto que aparece pro jogador

Padrões: tema = aleatorio ("Tema Aleatório", ícone 🎲), criado se não existir;
gabarito sorteado dentro do CSV. Sobrescreva com --theme, --theme-name,
--theme-icon, --target-rank.

Rodar de novo com a mesma data/tema substitui os itens daquele dia (e sorteia
novo gabarito, a menos que --target-rank seja passado).

A string do banco de produção sai de `backend/.env.prod.local` (fora do git);
se RANKDLE_DATABASE_URL já estiver no ambiente, ela tem prioridade.
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
RANKINGS_DIR = BACKEND.parent / "data" / "rankings"
sys.path.insert(0, str(BACKEND))

# O console do Windows costuma ser cp1252 e engasga com acento/emoji ao imprimir
# (inclusive o --help). Força UTF-8 na saída.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def _load_prod_db_url() -> None:
    """Garante RANKDLE_DATABASE_URL no ambiente ANTES de importar app.core.db
    (que cria o engine no import). Ordem: variável já exportada > arquivo."""
    if os.environ.get("RANKDLE_DATABASE_URL"):
        return

    env_file = BACKEND / ".env.prod.local"
    if not env_file.exists():
        sys.exit(
            "Falta backend/.env.prod.local (ou a variável RANKDLE_DATABASE_URL).\n"
            "Crie o arquivo com uma linha:\n"
            "  RANKDLE_DATABASE_URL=postgresql+psycopg://neondb_owner:SENHA@HOST/neondb?sslmode=require\n"
            "(veja backend/.env.prod.local.example)"
        )

    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

    if not os.environ.get("RANKDLE_DATABASE_URL"):
        sys.exit("RANKDLE_DATABASE_URL não encontrada em backend/.env.prod.local")


def resolve_date(value: str) -> date:
    if value.strip().lower() in {"hoje", "today"}:
        return date.today()
    try:
        return date.fromisoformat(value)
    except ValueError:
        sys.exit(f"Data inválida: {value!r} — use AAAA-MM-DD ou 'hoje'")


def resolve_csv(name: str) -> Path:
    # Aceita "arquivo", "arquivo.csv" ou um caminho; sempre resolve dentro de
    # data/rankings/ pelo nome do arquivo.
    filename = Path(name).name
    if not filename.lower().endswith(".csv"):
        filename += ".csv"
    path = RANKINGS_DIR / filename
    if not path.exists():
        existing = sorted(p.name for p in RANKINGS_DIR.glob("*.csv"))
        listing = "\n  ".join(existing) if existing else "(nenhum .csv em data/rankings/)"
        sys.exit(f"CSV não encontrado: {path}\nDisponíveis:\n  {listing}")
    return path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("date", help="AAAA-MM-DD (ou 'hoje')")
    p.add_argument("file", help="Nome do CSV em data/rankings/ (o .csv é opcional)")
    p.add_argument("subtitle", help='Subtítulo do dia, ex: "Músicas mais ouvidas em 2015"')
    p.add_argument("--theme", default="aleatorio")
    p.add_argument("--theme-name", default="Tema Aleatório")
    p.add_argument("--theme-icon", default="🎲")
    p.add_argument("--target-rank", type=int, default=None, help="Fixar a posição-gabarito (padrão: sorteia)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    challenge_date = resolve_date(args.date)
    csv_path = resolve_csv(args.file)

    _load_prod_db_url()

    # Importado só agora, depois que RANKDLE_DATABASE_URL está no ambiente.
    from app.core.db import SessionLocal
    from app.models.theme import Theme
    from scripts.import_ranking import import_ranking

    db = SessionLocal()
    try:
        challenge = import_ranking(
            db,
            csv_path=csv_path,
            challenge_date=challenge_date,
            theme_slug=args.theme,
            theme_name=args.theme_name,
            theme_icon=args.theme_icon,
            subtitle=args.subtitle,
            target_rank=args.target_rank,
        )

        theme = db.query(Theme).filter(Theme.slug == args.theme).first()
        if theme is not None and not theme.active:
            theme.active = True
            db.commit()

        print(
            f"OK: {len(challenge.items)} itens em {challenge.date} "
            f"(tema '{args.theme}', challenge_id={challenge.id}, "
            f"target_rank={challenge.target_rank}, ativo=True)"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
