"""Command-line interface for searching documents created from Markdown."""

from __future__ import annotations

import argparse
import sys
from typing import List

from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit
from prompt_toolkit.widgets import TextArea, Label, Frame

import pyperclip

from sheetah.sheetah import Document, Segment


class DocSearchUI:
    def __init__(self, document: Document):
        self.document = document
        self.results: List[Segment] = document.items
        self.selected = 0

        # description shown above search field (if available)
        desc_text = document.description or ""
        self.description_label = Label(text=desc_text)

        self.search_field = TextArea(height=1, prompt="Search: ", multiline=False)
        self.result_area = TextArea(focusable=False, scrollbar=True)
        self.detail_area = TextArea(focusable=False, scrollbar=True)
        self.status_bar = Label(text="Use up/down to navigate, Enter to copy, Ctrl-C to quit.")

        # bind events
        self.search_field.buffer.on_text_changed += self._on_search_change
        self._update_display()

        self.kb = KeyBindings()
        self.kb.add("up")(self._go_up)
        self.kb.add("down")(self._go_down)
        self.kb.add("enter")(self._copy_current)
        self.kb.add("c-c")(self._exit)
        self.kb.add("c-q")(self._exit)

        root = HSplit([
            self.description_label,
            self.search_field,
            VSplit([
                Frame(self.result_area, title="Segments", width=40),
                Frame(self.detail_area, title="Preview"),
            ]),
            self.status_bar,
        ])

        self.app = Application(layout=Layout(root), key_bindings=self.kb, full_screen=True)

    def _on_search_change(self, _):
        text = self.search_field.text
        self.results = self.document.search(text)
        self.selected = 0
        self._update_display()

    def _format_results(self) -> str:
        lines = []
        for i, seg in enumerate(self.results):
            prefix = "> " if i == self.selected else "  "
            lines.append(prefix + seg.name)
        return "\n".join(lines)

    def _update_display(self):
        self.result_area.text = self._format_results()
        if self.results:
            self.detail_area.text = self.results[self.selected].text()
        else:
            self.detail_area.text = "<no results>"

    def _go_up(self, event):
        if self.results:
            self.selected = max(0, self.selected - 1)
            self._update_display()

    def _go_down(self, event):
        if self.results:
            self.selected = min(len(self.results) - 1, self.selected + 1)
            self._update_display()

    def _copy_current(self, event):
        if self.results:
            pyperclip.copy(self.results[self.selected].text())
            # show a little confirmation in status
            self.status_bar.text = "Copied to clipboard! (Ctrl-C to quit)"

    def _exit(self, event):
        event.app.exit()

    def run(self):
        self.app.run()


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Search markdown document interactively.")
    parser.add_argument("file", help="Path to markdown file")
    parser.add_argument("--separator", "-s", default="##",
                        help="Custom separator string that denotes segment headers (default: '##')")
    args = parser.parse_args(argv)

    try:
        text = open(args.file, encoding="utf-8").read()
    except Exception as e:
        print(f"Unable to read {args.file}: {e}")
        sys.exit(1)

    doc = Document.from_markdown(text, separator=args.separator)
    ui = DocSearchUI(doc)
    ui.run()


if __name__ == "__main__":
    main()
