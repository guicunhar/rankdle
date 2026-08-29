from datetime import date, datetime, timedelta, timezone

# O jogo "vira o dia" no horário de Brasília. O servidor roda em UTC, então
# date.today() adiantaria o desafio em 3 horas (às 21h já mostraria o de
# amanhã). O Brasil aboliu o horário de verão em 2019, então UTC-3 fixo é
# suficiente e evita depender do banco de fusos (tzdata) na imagem slim.
GAME_TZ = timezone(timedelta(hours=-3))


def game_now() -> datetime:
    return datetime.now(GAME_TZ)


def game_today() -> date:
    return game_now().date()
