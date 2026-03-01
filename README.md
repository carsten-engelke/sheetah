# sheetah

sheetah is a lightweight Python library for working with Markdown documents.
It splits a Markdown file into segments based on H2 headers ("##"), provides
fuzzy search over segment titles and content, and includes an interactive
command-line interface with clipboard copy support.

## Installation

Install from PyPI:

```bash
pip install sheetah
```

Or install and develop locally in a virtual environment:

```bash
cd sheetah
python -m venv .venv
# Windows
. .venv/Scripts/activate
# macOS / Linux
source .venv/bin/activate
python -m pip install -e .[all]
```

The optional extras include `prompt_toolkit` and `pyperclip` for the
interactive UI.

## Usage

### Programmatic

```python
from sheetah import Document

md = """Introduction

## Section 1
Text1

## Section 2
Text2
"""

doc = Document.from_markdown(md)
print(doc.description)
for seg in doc.search("Text"):
    print(seg.name)
    print(seg.text())
```

### Command line

```bash
sheetah path/to/file.md
```

The interactive UI lets you:

1. Enter a search query at the top.
2. See results listed with the best match selected by default.
3. Navigate results with the arrow keys and preview the segment.
4. Press Enter to copy the selected segment's text to the clipboard.
5. Press Ctrl-C or Ctrl-Q to exit.

The document description (everything before the first `##`) is shown above
the search input.

## API

- `Document.from_markdown(markdown: str) -> Document` — create a document from
  a Markdown string.
- `Document.items` — list of `Segment` instances.
- `Document.description` — Markdown text before the first H2 header.
- `Document.search(query: str, limit: Optional[int] = None)` — fuzzy search.
- `Segment.name` — segment title (header).
- `Segment.text()` — plain-text representation of the segment.
- `Segment.html()` — HTML representation of the segment.

## Tests

Run the test suite with:

```bash
pytest
```

## Contributing

Contributions are welcome. Please open issues or pull requests on GitHub.

## License

MIT — see the `LICENSE` file for details.
