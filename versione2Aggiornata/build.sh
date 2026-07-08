#!/bin/bash
# build.sh — Fase di produzione documentale: grafici + conversione Pandoc
# Newsletter "Scienza sotto pressione"
#
# Questa è la parte "pura" e deterministica della pipeline: non ha
# bisogno della rete se lanciata con --offline, e deve funzionare
# sempre, anche se la ricerca delle fonti (scripts/cerca.sh) non è
# stata rilanciata o è fallita per motivi di rete.
#
# La ricerca di nuovi candidati e la verifica delle fonti selezionate
# vivono invece in scripts/cerca.sh: uno script separato perché dipende
# dalla rete ed è la parte più "esplorativa" del progetto — ha senso
# poterla rilanciare da sola, a cadenza periodica, senza dover
# rigenerare tutta la newsletter ogni volta.
#
# Uso:
#   ./build.sh              genera i grafici dal vivo (richiede rete)
#   ./build.sh --offline    usa dati di esempio per i grafici, nessuna rete
#
# Per la fase di ricerca:
#   ./scripts/cerca.sh

set -e  # qui sì: se la conversione fallisce, meglio fermarsi ed è un errore vero

cd "$(dirname "$0")"
mkdir -p output/img

OFFLINE=false
[ "$1" = "--offline" ] && OFFLINE=true

echo "→ Generazione grafici..."
if [ "$OFFLINE" = true ]; then
  python3 scripts/make_chart.py --offline
else
  python3 scripts/make_chart.py --topic "artificial intelligence AND healthcare"
fi

echo "→ Generazione HTML..."
# --self-contained incorpora CSS e immagini come data URI in un unico file:
# risultato facilmente spostabile su blog/newsletter senza asset esterni rotti.
pandoc -s articolo.md \
  --metadata-file=metadati.yaml \
  --css=stile.css \
  --toc \
  --toc-depth=2 \
  --syntax-highlighting=kate \
  --embed-resources\
  -o output/articolo.html

echo "→ Generazione PDF..."
pandoc articolo.md \
  --metadata-file=metadati.yaml \
  --css=stile.css \
  --toc \
  --toc-depth=2 \
  --pdf-engine=weasyprint \
  -o output/articolo.pdf

echo "✓ Documento generato in ./output/ (articolo.html, articolo.pdf, img/*.png)"
