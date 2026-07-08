# Scienza sotto pressione — pipeline di produzione per newsletter scientifiche

Strumento per produrre newsletter scientifiche divulgative a partire da
Markdown + YAML, con Pandoc come motore di conversione verso HTML e PDF.
La pipeline copre l'intero processo di produzione di un numero: ricerca
automatica delle fonti open access, generazione dei grafici,
applicazione di uno stile editoriale dedicato e conversione in HTML e
PDF, riproducibile con due script indipendenti. Il tema, le fonti e il
testo di ogni numero sono contenuti in `articolo.md`: cambiando questo
file (e gli argomenti di ricerca in `data/argomenti.txt`) la stessa
pipeline produce un numero su un argomento scientifico diverso, senza
toccare script o stile.

Questo repository include, come esempio funzionante, un numero
dedicato a intelligenza artificiale in sanità e disinformazione medica
online (si veda "Fonti nell'esempio incluso" più sotto).

## Cosa fa il progetto

**1. Stile come identità editoriale**
`stile.css` non è un semplice foglio di formattazione ma costruisce una
vera identità editoriale: masthead con occhiello, numerazione
automatica delle sezioni via contatori CSS, accento colore configurabile
per ciascuna sezione tematica, badge "open access" sulle citazioni delle
fonti, capolettera sull'introduzione, riquadri per i grafici con
didascalia, indice generato da Pandoc ristilizzato come sommario. Vedi i
commenti in `stile.css` per il dettaglio di ogni blocco.

**2. Automazione della ricerca degli articoli**
`scripts/search_articles.py` interroga l'indice bibliografico aperto
**OpenAlex**, filtra per licenza open access e restituisce un CSV per
argomento in `data/`. Lo script ha due modalità distinte, con scopi
diversi:

- **Scoperta** (`--batch data/argomenti.txt`): query testuali generiche
  che propongono *nuovi candidati* su un argomento. Le query devono
  essere in inglese, perché l'API confronta il testo con titolo/abstract
  dei lavori indicizzati, quasi sempre pubblicati in inglese. I
  risultati sono ordinati per rilevanza testuale di default (non per
  numero di citazioni), perché altrimenti le review più citate
  scavalcano lo studio specifico che si sta cercando.
- **Verifica** (`--verify data/fonti_selezionate.txt`): lookup diretto
  per DOI delle fonti effettivamente sintetizzate in `articolo.md`. Non
  dipende da un ranking testuale: interroga OpenAlex per ciascun DOI e
  conferma titolo, autori e stato open access. È il modo corretto per
  dimostrare che le fonti citate nella newsletter sono le stesse
  indicizzate dall'API usata per la ricerca automatica, senza affidarsi
  alla fortuna di un ranking.

La selezione editoriale finale — quali articoli tra i candidati
sintetizzare — resta sempre una scelta umana: l'automazione copre il
reperimento e la verifica delle fonti, non la scrittura.

**Determinismo.** Le due modalità hanno garanzie diverse: la ricerca
libera (`--batch`) non è deterministica nel tempo — OpenAlex è un indice
in continuo aggiornamento, quindi la stessa query può restituire elenchi
diversi a distanza di settimane, e non garantisce che un articolo
specifico compaia tra i risultati. La verifica (`--verify`) invece è
deterministica: è un lookup diretto per DOI, non un ranking, quindi
finché il record esiste la risposta è sempre la stessa.

**3. Elementi visivi per il lettore**
`scripts/make_chart.py` genera grafici da inserire direttamente nella
newsletter: l'andamento delle pubblicazioni scientifiche su un
argomento (dati live da OpenAlex, con fallback offline) e un confronto
tra la dimensione dei corpus analizzati dagli studi citati. Non sono
decorazioni: aiutano il lettore a valutare a colpo d'occhio la portata
delle fonti prima di leggere le sintesi.

## Struttura del progetto

Ci sono due fasi indipendenti, separate perché hanno caratteristiche
diverse: la ricerca dipende dalla rete ed è la parte "esplorativa" (ha
senso rilanciarla da sola, periodicamente, per cercare nuovi
argomenti), mentre la generazione del documento è pura e deterministica
e deve funzionare sempre, anche offline. `build.sh`, nella root del
progetto, è la fase di generazione (grafici + Pandoc); `scripts/cerca.sh`
è la fase di ricerca, indipendente, da lanciare a parte quando serve.




## Come riprodurre il flusso

Per produrre un numero su un argomento diverso: sostituire il testo in
`articolo.md`, aggiornare `data/argomenti.txt` e `data/fonti_selezionate.txt`
con i nuovi temi/DOI, poi lanciare di nuovo `scripts/cerca.sh` e
`build.sh`. Stile, script e struttura restano invariati.

Richiede Pandoc, XeLaTeX (o WeasyPrint per PDF stilizzato con CSS),
Python 3 con `requests` e `matplotlib`.

**Consigliato — ambiente virtuale isolato.** Su macOS in particolare,
installare `matplotlib` con Homebrew (`brew install python-matplotlib`)
porta spesso con sé una versione di `numpy` incompatibile (errore tipico:
`ModuleNotFoundError: No module named 'numpy.exceptions'`); un ambiente
virtuale dedicato evita questi conflitti con pacchetti di sistema o di
Homebrew:

```bash
python3 -m venv .venv
source .venv/bin/activate      # da rifare a ogni nuova sessione di terminale
pip install --upgrade pip
pip install requests matplotlib pyyaml
```

In alternativa, senza venv (rischio di conflitti se `matplotlib` è già
installato da Homebrew):

```bash
pip install requests matplotlib pyyaml
```

Poi, in entrambi i casi:

```bash
./build.sh              # genera i grafici dal vivo (richiede rete) + build HTML/PDF
./build.sh --offline    # nessuna chiamata di rete, usa dati di esempio già inclusi
```

La ricerca delle fonti è una fase a parte, indipendente da `build.sh`,
comoda da rilanciare da sola (ad es. a cadenza periodica, per scoprire
nuovi candidati su un argomento) senza rigenerare tutto il documento:

```bash
# Fase di ricerca (rete): nuovi candidati + verifica delle fonti già citate
./scripts/cerca.sh

# Solo verifica delle fonti già citate (rapido, deterministico):
python3 scripts/search_articles.py --verify data/fonti_selezionate.txt

# Solo scoperta di nuovi candidati su un argomento a piacere:
python3 scripts/search_articles.py "argomento in inglese" --oa-only --top 10
```

Nota: lo script di ricerca e la generazione live dei grafici richiedono
accesso a Internet verso `api.openalex.org` (API pubblica, nessuna chiave
richiesta). In reti con restrizioni (proxy universitari, sandbox) usare
`--offline`: i grafici vengono comunque generati, a partire da dati
già raccolti in `data/trend_sample.json`.

## Fonti nell'esempio incluso

Il numero incluso in questo repository tratta intelligenza artificiale
in sanità e disinformazione medica online, sintetizzando queste fonti:

| # | Studio | Rivista | Anno | Corpus | Licenza |
|---|--------|---------|------|--------|---------|
| 1 | Faiyazuddin et al. | Health Science Reports | 2025 | 4.403 articoli | Open access |
| 2 | Botha et al. | Archives of Public Health | 2024 | 80 articoli | Open access |
| 3 | Adebesin et al. | JMIR Infodemiology | 2023 | 943 articoli | Open access |
| 4 | Yeung et al. | Journal of Medical Internet Research | 2022 | 529 articoli | Open access |

Tutti i link diretti sono in `articolo.md`.