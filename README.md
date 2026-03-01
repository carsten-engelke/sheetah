# sheetah

`sheetah` ist ein einfaches Python-Paket zur Verarbeitung von Markdown-Dokumenten.
Es gliedert den Text an H2-Überschriften ("##") in **Segmente**, erlaubt fuzzy Suche
und bietet ein interaktives CLI mit Clipboard‑Kopie.

## Installation

```bash
pip install sheetah
```

Oder lokal im Quellcode (virtuellesenv):

```bash
cd sheetah
python -m venv .venv
. .venv/Scripts/activate  # oder source .venv/bin/activate
python -m pip install -e .[all]
```

> Die Extras umfassen `prompt_toolkit` und `pyperclip` für die interaktive UI.

## Nutzung

### Programmatisch

```python
from sheetah import Document

txt = """Einführung

## Abschnitt 1
Text1

## Abschnitt 2
Text2
"""

doc = Document.from_markdown(txt)
print(doc.description)
for seg in doc.search("Text"):
    print(seg.name)
    print(seg.text())
```

### Kommandozeile

```bash
sheetah pfad/zur/datei.md
```

Eine interaktive Oberfläche erscheint:

1. Eingabe der Suchanfrage oben
2. Ergebnisse werden aufgelistet, bester Treffer ist vorgeschlagen
3. Mit Pfeil hoch/runter navigieren; Vorschau rechts
4. `<Enter>` kopiert den Text des ausgewählten Segments in die Zwischenablage
5. `<Ctrl-C>` oder `<Ctrl-Q>` beendet das Programm

Die Beschreibung des Dokuments (alles vor dem ersten `##`) wird über der
Suchzeile angezeigt.

## API

- `Document.from_markdown(markdown: str) -> Document` – erstellt ein Dokument.
- `Document.items` – Liste der `Segment`-Instanzen.
- `Document.description` – Markdown-Text vor dem ersten Abschnitt.
- `Document.search(query: str, limit: Optional[int]=None)` – fuzzy Suche.
- `Segment.name` – Name (Header) des Segments.
- `Segment.text()` – reiner Text.
- `Segment.html()` – HTML-Konvertierung.

## Tests

```bash
pytest
```

## Lizenz

MIT, siehe `LICENSE`.
