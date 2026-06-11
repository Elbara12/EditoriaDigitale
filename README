# Scienza sotto pressione
**Newsletter di giornalismo scientifico**

Progetto realizzato per l'esame di **Editoria Digitale** (a.a. 2024/2025)
Università degli Studi di Milano — Appello dell'11/06/2026
Autore: Matteo Baraggini

---

## Descrizione

*Scienza sotto pressione* è una newsletter scientifica digitale rivolta a giornalisti, operatori dell'informazione e comunicatori della conoscenza. Il prodotto fornisce aggiornamenti rapidi e affidabili su temi scientifici di attualità, basandosi esclusivamente su articoli pubblicati con licenza open access.

I temi trattati in questo numero sono:
- **Intelligenza Artificiale in sanità** — opportunità e rischi
- **Disinformazione online** — misinformazione medica sui social media

---

## Struttura del repository

```
/
├── README.md            ← questo file
├── articolo.md          ← contenuto editoriale in formato Markdown
├── metadati.yaml        ← metadati Dublin Core-inspired in formato YAML
├── stile.css            ← foglio di stile per l'output HTML
├── build.sh             ← script di produzione con comandi Pandoc
└── output/
    ├── articolo.html    ← output HTML (newsletter/blog)
    └── articolo.pdf     ← output PDF (distribuzione formale)
```

---

## Flusso di produzione

Il flusso segue le buone pratiche del corso (DM2, DT6, DT8, DM7):

1. **Ricerca e selezione** degli articoli scientifici open access su PubMed Central
2. **Generazione dei contenuti** tramite LLM (Claude, Anthropic) con prompt strutturati
3. **Revisione e redazione** in Markdown con metadati YAML separati
4. **Conversione** con Pandoc in output multipli (HTML + PDF)
5. **Versioning** e distribuzione tramite questo repository GitHub

---

## Fonti scientifiche

Tutti gli articoli utilizzati sono open access con licenza Creative Commons.

| Autori | Titolo | Rivista | Anno | Link |
|--------|--------|---------|------|------|
| Saleem et al. | The Impact of Artificial Intelligence on Healthcare | Health Science Reports | 2025 | [PMC11702416](https://pmc.ncbi.nlm.nih.gov/articles/PMC11702416/) |
| Botha et al. | AI in Healthcare: Perceived Threats to Patient Rights and Safety | Archives of Public Health | 2024 | [PMC11515716](https://pmc.ncbi.nlm.nih.gov/articles/PMC11515716/) |
| Adebesin et al. | Role of Social Media in Health Misinformation During COVID-19 | JMIR Infodemiology | 2023 | [PMC10551800](https://pmc.ncbi.nlm.nih.gov/articles/PMC10551800/) |
| Yeung et al. | Medical and Health-Related Misinformation on Social Media | J Medical Internet Research | 2022 | [PMC8793917](https://pmc.ncbi.nlm.nih.gov/articles/PMC8793917/) |

---

## Requisiti

Per riprodurre il flusso di produzione è necessario avere installato:

- [Pandoc](https://pandoc.org/installing.html) (versione 3.x o superiore)
- [XeLaTeX](https://miktex.org) — incluso in MiKTeX o TeX Live

---

## Come riprodurre gli output

```bash
# Rendi lo script eseguibile (solo la prima volta)
chmod +x build.sh

# Lancia la build
./build.sh
```

Gli output vengono generati nella cartella `output/`.

---

## Licenza

Il contenuto editoriale è rilasciato con licenza **CC BY 4.0**.
Le fonti scientifiche citate mantengono le rispettive licenze originali (CC BY o CC BY-NC).