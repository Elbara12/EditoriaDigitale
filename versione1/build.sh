#!/bin/bash
# build.sh — Script di produzione documentale
# Newsletter "Scienza sotto pressione"
# Flusso: Markdown + YAML → HTML + PDF via Pandoc

set -e  # interrompe lo script in caso di errore

# Crea la cartella output se non esiste
mkdir -p output

echo "→ Generazione HTML..."
pandoc -s articolo.md \
  --metadata-file=metadati.yaml \
  --css=stile.css \
  --toc \
  --toc-depth=2 \
  --syntax-highlighting=kate \
  -o output/articolo.html

echo "→ Generazione PDF..."
pandoc articolo.md \
  --metadata-file=metadati.yaml \
  --toc \
  --toc-depth=2 \
  --pdf-engine=xelatex \
  -V geometry:margin=2.5cm \
  -V fontsize=11pt \
  -V linestretch=1.4 \
  -V lang=it \
  -o output/articolo.pdf

echo "✓ Build completata. Output in ./output/"