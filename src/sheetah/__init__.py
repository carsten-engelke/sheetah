"""Package entrypoint for :mod:`sheetah`.

The top-level ``main`` function is simply routed to the command‑line
implementation so installing the package and invoking ``sheetah`` will
launch the interactive search UI.  Helper classes are re-exported here as a
convenience for programmatic use.
"""

from __future__ import annotations

from .sheetah import Document, Segment
from . import cli

__all__ = ["Document", "Segment", "cli", "main"]


def main() -> None:
    """Run the command‑line interface."""
    cli.main()