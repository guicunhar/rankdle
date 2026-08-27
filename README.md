# Rankdle

Jogo diário de adivinhar posições em rankings (estilo Wordle). Backend em Python
(FastAPI), frontend em React + TypeScript.

## Como funciona

- Todo dia, cada tema (Música, Filmes, Esportes, Tema Aleatório) tem um novo
  ranking (ex: "Músicas mais ouvidas em 2010") e uma posição-alvo (ex: 34ª).
- O jogador busca sua resposta numa barra de pesquisa (restrita aos itens
  daquele ranking) e dá um palpite.
- Score = `100 - |diferença de posições|` (mínimo 0). Por padrão, 5 tentativas
  (vidas); cada palpite errado mostra a diferença como dica. O score final é o
  **maior score entre todas as tentativas**.
- Compartilhamento de resultado em texto (estilo Wordle) para X, WhatsApp ou
  copiar.
- Jogo anônimo por padrão (identificado por um id salvo no navegador), com
  opção de criar conta para sincronizar entre dispositivos.
- Dias anteriores ficam disponíveis para jogar no "Arquivo" de cada tema.

## Estrutura

```
backend/    FastAPI + SQLAlchemy + Alembic (API do jogo)
frontend/   React + TypeScript + Vite (interface)
data/samples/   CSVs de exemplo (placeholder) para os 4 temas
docker-compose.yml   sobe Postgres + backend + frontend juntos
```

## Rodando localmente

### Opção A — Docker (recomendado, já usa Postgres)

```bash
docker compose up --build
```

- Backend: http://localhost:8000 (docs interativas em `/docs`)
- Frontend: http://localhost:5173

Na primeira vez, popule dados de exemplo para hoje:

```bash
docker compose exec backend python scripts/seed_dev_data.py
```

### Opção B — sem Docker (SQLite local, mais rápido para testar)

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
copy .env.example .env       # edite RANKDLE_DATABASE_URL para sqlite:///./dev.db
python -m alembic upgrade head
python scripts/seed_dev_data.py
uvicorn app.main:app --reload
```

Frontend (em outro terminal):

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## Adicionando o ranking de um novo dia

Prepare um CSV com colunas `rank,name,image_url` (veja exemplos em
`data/samples/`) e rode:

```bash
cd backend
python scripts/import_ranking.py \
  --csv ../data/samples/meu_ranking.csv \
  --date 2026-08-27 \
  --theme musica \
  --subtitle "Músicas mais ouvidas em 2015" \
  --target-rank 17
```

Se o tema (`--theme`) ainda não existir, passe também `--theme-name` e
`--theme-icon` para criá-lo — depois disso não precisa mais.
Rodar de novo com a mesma `--date`/`--theme` substitui os itens daquele dia.

> No Windows, se acentos saírem estranhos ao rodar pelo terminal, salve o CSV
> como UTF-8 e rode `chcp 65001` antes, ou prefira preparar os dados num
> script Python que chama `import_ranking()` diretamente (veja
> `scripts/seed_dev_data.py` como exemplo) — assim evita problemas de
> codificação da linha de comando do Windows.

## Ajustando a dificuldade (nº de vidas)

O padrão de vidas é lido da tabela `app_settings` (chave `default_lives`), com
fallback para `RANKDLE_DEFAULT_LIVES` no backend. Para mudar sem precisar de
deploy, insira/atualize a linha diretamente no banco:

```sql
INSERT INTO app_settings (key, value) VALUES ('default_lives', '4')
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;
```

Também dá pra sobrescrever só um desafio específico via `--lives` no
`import_ranking.py`.

## Testes

```bash
cd backend
pytest
```

## Monetização (Google AdSense)

O frontend já tem espaços reservados de anúncio (`AdSlot`), desligados por
padrão (`VITE_ENABLE_ADS=false`). Quando o domínio estiver aprovado no
AdSense:

1. Descomente o `<script>` do AdSense em `frontend/index.html`.
2. Defina `VITE_ENABLE_ADS=true` e `VITE_ADSENSE_CLIENT_ID=ca-pub-...` no
   `.env` do frontend.

## Próximos passos (fora do escopo desta primeira versão)

- Importação automática via API/scraping de fontes externas (por ora, a
  curadoria dos rankings é manual, via CSV).
- Painel admin visual (por ora, importação via linha de comando).
- Escolha definitiva de hospedagem — a estrutura com Docker roda tanto em
  Vercel/Render/Railway quanto em um único VPS, sem mudar código.
