#!/bin/bash
# scripts/cerca.sh — Fase di ricerca: candidati nuovi + verifica fonti selezionate
#
# Isolata da build.sh perché dipende dalla rete ed è la fase più
# "esplorativa" del progetto: ha senso poterla rilanciare da sola, a
# cadenza periodica (es. una volta al mese per cercare nuovi argomenti),
# senza dover rigenerare tutta la newsletter ogni volta.
#
# Non blocca mai: se la rete non è disponibile, segnala l'errore e
# restituisce comunque codice di uscita 0, così build.sh può proseguire
# con la fase di produzione usando le fonti già scritte in articolo.md.
#
# Uso:
#   ./scripts/cerca.sh

cd "$(dirname "$0")/.."   # esegue sempre dalla root del progetto, non da scripts/
mkdir -p data

echo "→ Ricerca automatica di nuovi candidati su OpenAlex..."
python3 scripts/search_articles.py --batch data/argomenti.txt --oa-only --top 10 --min-year 2020 \
  || echo "   (ricerca non riuscita — probabilmente rete non disponibile; le fonti restano quelle già selezionate in articolo.md)"

echo "→ Verifica diretta delle fonti già sintetizzate in articolo.md..."
python3 scripts/search_articles.py --verify data/fonti_selezionate.txt \
  || echo "   (verifica non riuscita — probabilmente rete non disponibile)"
