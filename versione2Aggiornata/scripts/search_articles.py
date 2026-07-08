#!/usr/bin/env python3
"""
search_articles.py — Ricerca automatica di articoli scientifici open access

Sostituisce la ricerca manuale su Google Scholar con una query programmatica
all'API pubblica di OpenAlex (https://openalex.org), un indice bibliografico
aperto che copre le stesse fonti indicate nella traccia d'esame (PMC, Zenodo,
riviste open science) e restituisce direttamente lo stato di licenza open
access di ogni articolo.

Uso singolo:
    python3 search_articles.py "impact of artificial intelligence on healthcare" --oa-only --top 10

Uso batch (un file di argomenti, uno per riga -> una query ciascuno):
    python3 search_articles.py --batch data/argomenti.txt --oa-only --top 10

Verifica di fonti già selezionate (indipendente dal ranking testuale):
    python3 search_articles.py --verify data/fonti_selezionate.txt

Output:
    Per ogni argomento viene salvato un CSV in data/risultati_<slug>.csv
    con: titolo, autori, rivista, anno, citazioni, licenza OA, link diretto.
    Questi CSV sono la base da cui l'autore sceglie a mano i 2-3 articoli
    da sintetizzare in articolo.md — l'automazione copre la fase di
    reperimento delle fonti, non la scrittura editoriale.

IMPORTANTE — lingua delle query: l'API OpenAlex confronta il testo della
query con titolo/abstract dei lavori indicizzati così come sono stati
pubblicati (quasi sempre in inglese per le riviste scientifiche
internazionali). Query in italiano (es. "intelligenza artificiale sanità")
NON vengono tradotte automaticamente e restituiscono risultati poco o per
nulla pertinenti: scrivere le query in inglese, idealmente vicine al
lessico del titolo/abstract del tipo di articolo che si cerca.

Nota sul ranking: di default i risultati sono ordinati per rilevanza
testuale rispetto alla query (comportamento nativo di OpenAlex), non per
numero di citazioni — un articolo recente e pertinente ma poco citato
sarebbe altrimenti scavalcato da review molto più citate ma meno mirate.
Usare --sort cited_by_count per il comportamento opposto.

Nota rete: in ambienti con accesso a Internet limitato (sandbox, reti
universitarie filtrate) lo script segnala l'errore e suggerisce di
rilanciarlo da una rete aperta; make_chart.py può comunque generare grafici
di esempio in modalità --offline con dati già raccolti in data/.
"""

import argparse
import csv
import re
import sys
import time
from pathlib import Path

import requests

OPENALEX_API = "https://api.openalex.org/works"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[\s_-]+", "-", text)


def _normalize_work(work: dict) -> dict:
    authors = [
        a["author"]["display_name"]
        for a in work.get("authorships", [])[:3]
    ]
    if len(work.get("authorships", [])) > 3:
        authors.append("et al.")
    oa = work.get("open_access", {})
    best_loc = work.get("best_oa_location") or {}
    row = {
        "titolo": work.get("title", "").strip(),
        "autori": ", ".join(authors) or "n.d.",
        "rivista": ((work.get("primary_location") or {}).get("source", {}) or {}).get("display_name", "n.d."),
        "anno": work.get("publication_year"),
        "citazioni": work.get("cited_by_count", 0),
        "oa_status": oa.get("oa_status", "unknown"),
        "link": best_loc.get("landing_page_url") or best_loc.get("pdf_url") or work.get("id"),
        "doi": work.get("doi"),
    }
    return row


def search_openalex(query: str, top: int = 5, oa_only: bool = True, min_year: int | None = None,
                     sort: str = "relevance"):
    """Interroga OpenAlex e restituisce una lista di articoli normalizzati.

    sort="relevance" (default) lascia che sia OpenAlex a ordinare per
    pertinenza testuale rispetto alla query (nessun parametro 'sort' esplicito
    nella richiesta); sort="cited_by_count" ordina invece per numero di
    citazioni decrescente, utile per individuare le review più autorevoli
    su un argomento ampio ma meno efficace per ritrovare uno studio
    specifico e recente.
    """
    filters = []
    if oa_only:
        filters.append("is_oa:true")
    if min_year:
        filters.append(f"from_publication_date:{min_year}-01-01")

    params = {
        "search": query,
        "per-page": top,
        "mailto": "student@example.edu",  # buona pratica OpenAlex: identificarsi
    }
    if sort == "cited_by_count":
        params["sort"] = "cited_by_count:desc"
    if filters:
        params["filter"] = ",".join(filters)

    resp = requests.get(OPENALEX_API, params=params, timeout=15)
    resp.raise_for_status()
    return [_normalize_work(w) for w in resp.json().get("results", [])]


def verify_doi(doi: str) -> dict | None:
    """Interroga OpenAlex per un DOI specifico (lookup diretto, non ranking testuale).

    Serve a dimostrare che una fonte già selezionata a mano è effettivamente
    presente e open access nello stesso indice bibliografico usato dalla
    ricerca automatica, indipendentemente dal fatto che una query testuale
    generica la avrebbe fatta comparire tra i primi risultati.
    """
    doi = doi.strip()
    if not doi.startswith("10."):
        doi = doi.split("doi.org/")[-1]
    url = f"{OPENALEX_API}/doi:{doi}"
    resp = requests.get(url, params={"mailto": "student@example.edu"}, timeout=15)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return _normalize_work(resp.json())


CSV_FIELDS = ["titolo", "autori", "rivista", "anno", "citazioni", "oa_status", "link", "doi"]


def save_csv(query: str, rows: list[dict]):
    DATA_DIR.mkdir(exist_ok=True)
    out_path = DATA_DIR / f"risultati_{slugify(query)}.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return out_path


def print_table(query: str, rows: list[dict]):
    print(f"\n=== Risultati per: {query!r} ===")
    if not rows:
        print("  (nessun risultato open access trovato — verifica che la query sia in inglese)")
        return
    for i, r in enumerate(rows, 1):
        print(f"{i}. {r['titolo']}")
        print(f"   {r['autori']} — {r['rivista']} ({r['anno']}) — {r['citazioni']} citazioni — {r['oa_status']}")
        print(f"   {r['link']}")


def run_verify(list_path: Path):
    """Verifica diretta (per DOI) di una lista di fonti già selezionate."""
    dois = [line.strip() for line in list_path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    print(f"\n=== Verifica di {len(dois)} fonti selezionate (lookup diretto per DOI) ===")
    rows = []
    all_ok = True
    for doi in dois:
        try:
            row = verify_doi(doi)
        except requests.exceptions.RequestException as exc:
            print(f"[!] Impossibile verificare {doi}: {exc}", file=sys.stderr)
            all_ok = False
            continue
        if row is None:
            print(f"✗ {doi} — non trovato su OpenAlex")
            all_ok = False
            continue
        oa_flag = "✓ open access" if row["oa_status"] in ("gold", "green", "hybrid", "bronze") else f"✗ oa_status={row['oa_status']}"
        print(f"✓ {row['titolo']}")
        print(f"   {row['autori']} — {row['rivista']} ({row['anno']}) — {oa_flag}")
        print(f"   {row['link']}")
        rows.append(row)
        time.sleep(0.3)
    if rows:
        path = save_csv("fonti-verificate", rows)
        print(f"\n→ salvato in {path}")
    if not all_ok:
        print("\n[!] Una o più fonti non sono state verificate correttamente: controllare i DOI in", list_path, file=sys.stderr)
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="Ricerca automatica di articoli open access su OpenAlex")
    parser.add_argument("query", nargs="?", help="Argomento singolo da cercare (in inglese)")
    parser.add_argument("--batch", help="File con un argomento per riga (in inglese)")
    parser.add_argument("--verify", help="File con un DOI per riga: verifica diretta di fonti già selezionate")
    parser.add_argument("--top", type=int, default=10, help="Numero massimo di risultati per argomento")
    parser.add_argument("--oa-only", action="store_true", help="Restituisce solo articoli open access")
    parser.add_argument("--min-year", type=int, default=None, help="Anno minimo di pubblicazione")
    parser.add_argument("--sort", choices=["relevance", "cited_by_count"], default="relevance",
                         help="Criterio di ordinamento (default: rilevanza testuale rispetto alla query)")
    args = parser.parse_args()

    if args.verify:
        ok = run_verify(Path(args.verify))
        sys.exit(0 if ok else 1)

    if not args.query and not args.batch:
        parser.error("specifica un argomento, --batch <file> oppure --verify <file>")

    queries = [args.query] if args.query else [
        line.strip() for line in Path(args.batch).read_text(encoding="utf-8").splitlines() if line.strip()
    ]

    for q in queries:
        try:
            rows = search_openalex(q, top=args.top, oa_only=args.oa_only, min_year=args.min_year, sort=args.sort)
        except requests.exceptions.RequestException as exc:
            print(f"[!] Impossibile contattare OpenAlex per {q!r}: {exc}", file=sys.stderr)
            print("    Verifica la connessione di rete e riprova.", file=sys.stderr)
            continue
        print_table(q, rows)
        path = save_csv(q, rows)
        print(f"   → salvato in {path}")
        time.sleep(0.5)  # cortesia verso l'API pubblica


if __name__ == "__main__":
    main()
