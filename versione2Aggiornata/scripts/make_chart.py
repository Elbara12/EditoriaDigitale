#!/usr/bin/env python3
"""
make_chart.py — Generazione automatica dei grafici della newsletter

Produce due visualizzazioni in output/img/, pensate per essere richiamate
da build.sh prima della conversione Pandoc:

1. trend_pubblicazioni.png
   Andamento delle pubblicazioni scientifiche su un tema (default:
   "artificial intelligence AND healthcare") per anno, ottenuto interrogando
   dal vivo l'API di OpenAlex (group_by publication_year). Se la rete non è
   raggiungibile, usa --offline e ricade su dati di esempio già inclusi in
   data/trend_sample.json (chiaramente etichettati come tali nel grafico).

2. corpus_studi.png
   Confronto tra la dimensione dei corpus analizzati dalle 4 rassegne
   citate in articolo.md (dati riportati nei rispettivi abstract, non
   generati automaticamente): un colpo d'occhio sulla scala delle fonti
   secondarie usate per la newsletter.

Uso:
    python3 make_chart.py --topic "artificial intelligence AND healthcare"
    python3 make_chart.py --offline
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import requests

ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "output" / "img"
DATA_DIR = ROOT / "data"
OPENALEX_API = "https://api.openalex.org/works"

# Colori coerenti con la palette di stile.css
COLOR_AI = "#2b6cb0"
COLOR_DISINFO = "#c0392b"
COLOR_INK = "#1a1a1a"


def fetch_trend_live(topic: str, start_year: int = 2014, end_year: int = 2024):
    params = {
        "search": topic,
        "filter": f"from_publication_date:{start_year}-01-01,to_publication_date:{end_year}-12-31",
        "group_by": "publication_year",
        "mailto": "student@example.edu",
    }
    resp = requests.get(OPENALEX_API, params=params, timeout=15)
    resp.raise_for_status()
    groups = {g["key"]: g["count"] for g in resp.json().get("group_by", [])}
    years = list(range(start_year, end_year + 1))
    counts = [groups.get(str(y), 0) for y in years]
    return years, counts, "OpenAlex API (dati live)"


def fetch_trend_offline():
    sample_path = DATA_DIR / "trend_sample.json"
    payload = json.loads(sample_path.read_text(encoding="utf-8"))
    return payload["years"], payload["counts"], "dati di esempio offline — vedi data/trend_sample.json"


def plot_trend(years, counts, source_label, topic):
    import textwrap
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.5, 3.6), dpi=200)
    ax.bar(years, counts, color=COLOR_AI, width=0.62)
    title = "\n".join(textwrap.wrap(f'Pubblicazioni scientifiche per anno — "{topic}"', width=48))
    ax.set_title(title, fontsize=10.5, fontweight="bold", loc="left", color=COLOR_INK)
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=45, ha="right", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylabel("N. articoli", fontsize=9)
    ax.text(0.0, -0.32, f"Fonte: {source_label}", transform=ax.transAxes, fontsize=7, color="#555555")
    fig.tight_layout()
    out_path = IMG_DIR / "trend_pubblicazioni.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[✓] {out_path}")


def plot_corpus_comparison():
    """Confronto dimensione corpus delle 4 rassegne citate in articolo.md (dati reali dagli abstract)."""
    studi = [
        ("Faiyazuddin et al.\n2025 — AI in sanità", 4403, COLOR_AI),
        ("Botha et al.\n2024 — rischi AI", 80, COLOR_AI),
        ("Adebesin et al.\n2023 — COVID-19", 943, COLOR_DISINFO),
        ("Yeung et al.\n2022 — piattaforme", 529, COLOR_DISINFO),
    ]
    labels = [s[0] for s in studi]
    values = [s[1] for s in studi]
    colors = [s[2] for s in studi]

    IMG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 3.4), dpi=200)
    bars = ax.barh(labels, values, color=colors)
    ax.invert_yaxis()
    ax.set_xlabel("Articoli analizzati nella rassegna", fontsize=9)
    ax.set_title("Quanti articoli stanno dietro ai 4 studi citati", fontsize=11, fontweight="bold", loc="left", color=COLOR_INK)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar, val in zip(bars, values):
        ax.text(val + 30, bar.get_y() + bar.get_height() / 2, str(val), va="center", fontsize=8, color=COLOR_INK)
    ax.text(0.0, -0.28, "Fonte: dati dichiarati negli abstract degli articoli citati ", transform=ax.transAxes, fontsize=7, color="#555555")
    fig.tight_layout()
    out_path = IMG_DIR / "corpus_studi.png"
    fig.savefig(out_path)
    plt.close(fig)
    print(f"[✓] {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Genera i grafici della newsletter")
    parser.add_argument("--topic", default="artificial intelligence AND healthcare", help="Argomento per il trend di pubblicazioni")
    parser.add_argument("--offline", action="store_true", help="Usa dati di esempio invece di interrogare OpenAlex")
    args = parser.parse_args()

    if args.offline:
        years, counts, source = fetch_trend_offline()
    else:
        try:
            years, counts, source = fetch_trend_live(args.topic)
        except requests.exceptions.RequestException as exc:
            print(f"[!] Rete non raggiungibile ({exc}). Uso dati offline di esempio.")
            years, counts, source = fetch_trend_offline()

    plot_trend(years, counts, source, args.topic)
    plot_corpus_comparison()


if __name__ == "__main__":
    main()
