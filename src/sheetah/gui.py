"""Graphical interface for searching documents created from Markdown."""

from __future__ import annotations
import argparse
import sys

from sheetah import Document, Segment

class DocSearchGUI():
    def __init__(self, document: Document):
        self.document = document
        self.results: list[Segment] = document.items

    def create_ui(self):
        self.openfiledialog = ui.dialog().classes('w-1/2')
        ui.page("/")
        with ui.header():
            with ui.row(wrap=False, align_items='stretch').classes('w-full'):
                with ui.button(icon='menu'):
                    with ui.menu() as menu:
                        ui.menu_item("Open File", self.openfiledialog.open)
                        ui.menu_item("Save File", self._download_document)
                        ui.menu_item("Clear List", self._clear_list)
                self.search_field = ui.input(label='Search', on_change=self._on_search_change, placeholder='Type to search...').classes('w-full')
        self.result_area = ui.column().classes('w-full').style('overflow-y: auto; padding: 10px; gap: 10px')
        with ui.footer():
            self.status_bar = ui.label("Ready.").classes('w-full text-left')
        with self.openfiledialog:
            with ui.card():
                ui.label("Upload a Markdown file to append to the current document.").classes('text-center')
                ui.upload(label="Choose File", on_upload=self._handle_file_upload).props('accept=.md').classes('w-full')
                ui.button("Close", on_click=lambda: self.openfiledialog.close()).classes('w-full')
        self._update_results()

    def _on_search_change(self, event):
        text = event.value
        self.results = self.document.search(text)
        self._update_results()
    
    def _update_results(self):
        self.result_area.clear()
        for element in self.results:
            with self.result_area.classes('h-100%'):
                with ui.card().classes('w-full'):
                    ui.label(element.name).style('font-size: 130%; font-weight: bold')
                    ui.markdown(element.markdown()).classes('whitespace-pre-wrap')
                    ui.button(icon='content_copy', on_click=lambda e, t=element.text(): self._copy_current(e, t)).classes('absolute bottom-2 right-2')

    def _copy_current(self, event, copytext: str):
        if self.results:
            ui.clipboard.write(copytext)  # copy the specified text
            self.status_bar.text = "Copied to clipboard!"

    async def _handle_file_upload(self, event: events.UploadEventArguments, append=False):
        file = event.file
        text = await file.text()
        other = Document.from_markdown(text)
        for seg in other.items:
            self.document.append(seg.name, seg._markdown)
        self.results = self.document.items
        self.search_field.value = ""  # clear search field to show all results
        self._update_results()
        self.status_bar.text = f"File '{file.name}' uploaded and added to Document."
        self.openfiledialog.close()

    def _download_document(self):
        markdown_content = self.document.to_markdown()
        ui.download.content(markdown_content, filename="sheetah_document.md")
        self.status_bar.text = "Document downloaded as 'sheetah_document.md'."
    
    def _clear_list(self):
        self.document.items.clear()
        self.results.clear()
        self._update_results()
        self.status_bar.text = "Document cleared."


def main(argv=None) -> None:
    try:
        from nicegui import ui, events
        run_gui_app(reload=False, argv=argv)
    except ImportError:
        # Fallback to CLI if NiceGUI is not installed, which allows the user to still use the application without the GUI features. It also provides a helpful message about how to install the GUI features.
        print("NiceGUI is not installed. Please install the 'gui' extra to use the GUI features with 'pip install niceguitest[gui]' .")
        from sheetah.cli import main as cli_main
        cli_main()

def run_gui_app(reload, argv=None) -> None:
    # Necessary workaround to allow the use of NiceGUI's reload feature which does not work when starting the app from an entry point in pyproject.toml.
    print("Starting NiceGUI app using a root function with reload =", reload)
    from sheetah.cli import load_document_upon_startup
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Search markdown document interactively.")
    parser.add_argument("--file", "-f", help="Path to markdown file")
    parser.add_argument("--separator", "-s", default="##",
                        help="Custom separator string that denotes segment headers (default: '##')")
    args = parser.parse_args(argv)
    doc = load_document_upon_startup(args.file, args.separator)
    ui.run(reload=reload, root=lambda: setup_gui(doc))

def setup_gui(doc:Document) -> None:
    # root function that sets up the GUI layout and components. Workaround for the fact that NiceGUI's reload feature only works with a root function. 
    DocSearchGUI(document=doc).create_ui()
    print("sheetah GUI initialized with document containing " + str(len(doc.items)) + " segments.")

if __name__ in {'__main__', '__mp_main__'}:
    #This is called when the user runs the command "python -m niceguitest.gui" to start the GUI application. Here you can use the reload feature of NiceGUI for development purposes, which allows you to see changes in real-time without restarting the app. In production, you would typically set reload to False for better performance.
    try:
        from nicegui import ui, events
        run_gui_app(reload=True, argv=sys.argv[1:])
    except ImportError:
        print("NiceGUI is not installed. Please install the 'gui' extra to use the GUI features with 'pip install niceguitest[gui]' .")
        from sheetah.cli import main as cli_main
        cli_main()