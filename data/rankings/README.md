# data/rankings/

Salve aqui os CSVs **reais** que você for importar para o jogo (esta pasta é
diferente de `data/samples/`, que só tem dados fictícios de demonstração).

Cada arquivo precisa de duas colunas:

```csv
ranking,descrição
1,Item mais bem colocado
2,Segundo colocado
3,Terceiro colocado
```

Sugestão de nome de arquivo: `<tema>_<assunto>.csv`, ex. `musica_top100_2010.csv`.

Depois de salvar o CSV aqui, importe com:

```bash
cd backend
python scripts/import_ranking.py \
  --csv ../data/rankings/musica_top100_2010.csv \
  --date 2026-08-27 \
  --theme musica \
  --subtitle "Músicas mais ouvidas em 2010"
```

Não precisa passar `--target-rank`: a posição-gabarito do dia é sorteada
automaticamente dentro do tamanho do CSV. Veja o [README.md](../../README.md)
principal para mais detalhes.
