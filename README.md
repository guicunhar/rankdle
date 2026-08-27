# Rankdle

Jogo diário de adivinhar posições em rankings (estilo Wordle). Backend em Python
(FastAPI), frontend em React + TypeScript.

> **Estado atual:** por enquanto só o tema "Tema Aleatório" está ativo — os
> outros 3 (Música, Filmes, Esportes) ficam desativados mas com todo o
> código/dados intactos, prontos pra voltar quando quiser (veja "Ativando ou
> desativando um tema" abaixo). Enquanto só houver 1 tema ativo, a Home pula
> direto pro jogo do dia, sem tela de escolha.

## Como funciona

- Todo dia, cada tema ativo tem um novo ranking (ex: "Músicas mais ouvidas em
  2010") e uma posição-alvo (ex: 34ª) — hoje isso é só o Tema Aleatório, mas
  o jogo suporta múltiplos temas simultâneos.
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
data/samples/    CSVs de exemplo (placeholder) para os 4 temas
data/rankings/   onde você salva os CSVs reais que for importar
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

Salve o CSV em **`data/rankings/`** (tem um `README.md` lá dentro com o
mesmo passo a passo). Ele precisa de duas colunas — `ranking` (a posição, um
número) e `descrição` (o que está naquela posição) — salvo como CSV UTF-8 (no
Excel: "Salvar como" → "CSV UTF-8 (Delimitado por vírgulas)"; no Google
Sheets: Arquivo → Fazer download → CSV, já sai em UTF-8). Exemplo:

```csv
ranking,descrição
1,Item mais bem colocado
2,Segundo colocado
3,Terceiro colocado
...
```

(Os nomes das colunas podem vir em português — `ranking`/`descrição` — ou em
inglês — `rank`/`name` —, tanto faz; o script aceita os dois. Uma coluna
opcional `image_url` também é aceita se você quiser mostrar uma imagem ao
lado de cada item na busca, mas não é obrigatória.)

Depois rode:

```bash
cd backend
python scripts/import_ranking.py \
  --csv ../data/rankings/meu_ranking.csv \
  --date 2026-08-27 \
  --theme musica \
  --subtitle "Músicas mais ouvidas em 2015"
```

- `--date`: dia em que esse desafio vai aparecer no jogo (`AAAA-MM-DD`).
- `--theme`: o "slug" do tema (`musica`, `filmes`, `esportes`, `aleatorio`, ou
  um novo que você queira criar).
- `--subtitle`: o texto que aparece pro jogador (ex: "Músicas mais ouvidas em
  2015").

**A posição-gabarito do dia é sempre sorteada automaticamente**, dentro do
tamanho do CSV — não precisa (e nem deve, normalmente) escolher você mesmo,
assim ninguém decora que "a pergunta é sempre perto do topo/fim da lista".
Se quiser forçar uma posição específica por algum motivo, ainda dá pra passar
`--target-rank 17`.

Se o tema (`--theme`) ainda não existir, passe também `--theme-name` e
`--theme-icon` para criá-lo — depois disso não precisa mais. Rodar de novo
com a mesma `--date`/`--theme` substitui os itens daquele dia e sorteia uma
nova posição (então dá pra corrigir um CSV e reimportar sem medo de
duplicar).

> No Windows, se acentos saírem estranhos ao rodar pelo terminal, salve o CSV
> como UTF-8 e rode `chcp 65001` antes, ou prefira preparar os dados num
> script Python que chama `import_ranking()` diretamente (veja
> `scripts/seed_dev_data.py` como exemplo) — assim evita problemas de
> codificação da linha de comando do Windows.

## Ativando ou desativando um tema

Um tema desativado some da tela inicial (e, se sobrar só 1 tema ativo, a
Home pula direto pro jogo, sem tela de escolha), mas nada é apagado —
desafios, rankings e histórico de quem já jogou ficam intactos.

```bash
cd backend
python scripts/set_theme_active.py --theme musica --active true   # reativa
python scripts/set_theme_active.py --theme esportes --active false  # desativa
```

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

O frontend já tem dois espaços reservados de anúncio (`AdSlot`, um em cima e
um embaixo do conteúdo, em `Layout.tsx`), desligados por padrão
(`VITE_ENABLE_ADS=false`) — não aparece nada até você configurar tudo abaixo.

### Pré-requisito: o site precisa estar no ar, num domínio de verdade

O Google **não aprova sites em `localhost`**. Antes de pedir aprovação no
AdSense, o Rankdle precisa estar publicado num domínio real (o
`docker-compose.yml` já deixa isso pronto pra rodar em qualquer VPS, ou você
pode usar Vercel/Render/Railway pro frontend/backend). Se você ainda não
decidiu onde hospedar, me avisa que eu ajudo a configurar quando chegar a
hora — por enquanto, só a etapa "criar a conta e ativar a verificação" já dá
pra fazer sem o site no ar.

### Passo a passo

1. **Crie a conta**: entre em [adsense.google.com](https://adsense.google.com)
   com uma conta Google, clique em "Começar" e informe a URL do seu site (o
   domínio, quando estiver no ar) e seu país/forma de pagamento.
2. **Verifique o site**: o Google te dá um `<script>` com seu ID de
   publisher (`ca-pub-XXXXXXXXXXXXXXXX`). Ele é o mesmo pra sua conta
   inteira — cole-o em `frontend/index.html`, descomentando a linha que já
   está preparada lá, substituindo `ca-pub-XXXXXXXXXXXXXXXX` pelo seu ID.
3. **Aguarde a revisão**: o Google analisa o site (conteúdo suficiente, sem
   conteúdo proibido, etc.) — costuma levar de alguns dias a poucas semanas.
   É comum pedirem uma página de política de privacidade; se pedirem, me
   avisa que eu crio uma.
4. **Depois de aprovado, crie os anúncios**: no painel do AdSense, vá em
   **Anúncios → Por unidade de anúncio → Anúncios display**, crie uma unidade
   pra cada posição (ex: "Rankdle - topo" e "Rankdle - rodapé") e copie o
   `data-ad-slot` (um número) de cada uma.
5. **Configure as variáveis de ambiente** no `.env` do frontend (no servidor
   de produção, não precisa no seu `.env` local):
   ```bash
   VITE_ENABLE_ADS=true
   VITE_ADSENSE_CLIENT_ID=ca-pub-XXXXXXXXXXXXXXXX
   VITE_ADSENSE_SLOT_TOP=1234567890
   VITE_ADSENSE_SLOT_BOTTOM=0987654321
   ```
6. Rode o build de novo (`npm run build` ou redeploy) — os anúncios aparecem
   automaticamente nos dois espaços reservados assim que essas variáveis
   estiverem definidas.

> Alternativa mais simples: em vez de criar unidades manuais, dá pra ativar
> "Anúncios automáticos" no painel do AdSense — aí o Google escolhe sozinho
> onde inserir anúncios na página, sem precisar dos `data-ad-slot` nem dos
> componentes `AdSlot`. Fica menos controlado (o Google pode inserir um
> anúncio no meio do jogo), mas é mais rápido de configurar — só o passo 2
> (o script no `index.html`) já basta.

## Próximos passos (fora do escopo desta primeira versão)

- Importação automática via API/scraping de fontes externas (por ora, a
  curadoria dos rankings é manual, via CSV).
- Painel admin visual (por ora, importação via linha de comando).
- Escolha definitiva de hospedagem — a estrutura com Docker roda tanto em
  Vercel/Render/Railway quanto em um único VPS, sem mudar código.
