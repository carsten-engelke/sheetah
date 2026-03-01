import pytest

from sheetah.sheetah import Document, Segment

SAMPLE = """# Top level title

## First section
Some *markdown* text.

## Second section
- item 1
- item 2
"""


def test_parse_segments():
    doc = Document.from_markdown(SAMPLE)
    assert len(doc.items) == 2
    assert doc.items[0].name == "First section"
    assert "markdown" in doc.items[0].markdown()


def test_text_and_html():
    doc = Document.from_markdown("## Section\nHello **world**")
    seg = doc.items[0]
    # text() should not contain markdown tokens; bold may be removed or kept
    # depending on available packages, but should include 'Hello' and 'world'
    txt = seg.text()
    assert "Hello" in txt and "world" in txt
    assert "<strong>world</strong>" in seg.html()

def test_description_extracted():
    md = "Intro text\n\n## Foo\nbar"
    doc = Document.from_markdown(md)
    assert doc.description.strip().startswith("Intro text")
    assert doc.items[0].name == "Foo"


def test_search_prioritizes_name():
    doc = Document.from_markdown("## name\ncontent with name \n## other\njust text")
    results = doc.search("name")
    assert results[0].name == "name"


def test_list_names():
    doc = Document.from_markdown("## a\n1\n## b\n2")
    assert doc.list() == ["a", "b"]
    assert len(doc.list(names_only=False)) == 2


def test_cli_invokes_ui(tmp_path, monkeypatch, capsys):
    # create a temporary markdown file
    mdfile = tmp_path / "doc.md"
    mdfile.write_text("## foo\nhello")

    called = {}
    def fake_run(self):
        called['run'] = True

    from sheetah import cli
    # stub Application so initialization doesn't try to use a real console
    class DummyApp:
        def __init__(self, *a, **k):
            pass
        def run(self):
            pass
    monkeypatch.setattr(cli, 'Application', DummyApp)

    monkeypatch.setattr(cli.DocSearchUI, 'run', fake_run)

    # call main with path
    cli.main([str(mdfile)])
    assert called.get('run')


def test_package_main_delegates(monkeypatch):
    called = {}
    import sheetah
    monkeypatch.setattr(sheetah.cli, 'main', lambda *a, **k: called.setdefault('ok', True))
    sheetah.main()
    assert called.get('ok')
