from dataclasses import dataclass
from typing import List, Optional
import re

# use established third-party libraries for conversions
try:
    import markdown as _markdown_lib
except ImportError:  # pragma: no cover
    _markdown_lib = None

from difflib import SequenceMatcher


@dataclass
class Segment:
    name: str
    _markdown: str

    def markdown(self) -> str:
        return self._markdown

    def text(self) -> str:
        """Return a plain-text version of the markdown content.

        If ``markdown`` is available we generate HTML first
        and then convert that to plain text; this gives a much better result
        than the simple regex stripping that was previously implemented.  A
        fallback regex stripper remains so that the method always returns
        something even when the optional dependency is missing.
        """
        md = self._markdown

        # lazy import to avoid module-level state problems when tests install
        # dependencies later.
        try:
            import markdown as _m
        except ImportError:
            _m = None

        if _m:
            html_text = _m.markdown(md)
            # strip HTML tags to get plain text; simple approach covers most
            # typical output from markdown.
            text = re.sub(r"<[^>]+>", "", html_text)
            return text.strip()

        # fallback: crude regex-based cleanup
        md = re.sub(r"```[\s\S]*?```", "", md)
        md = re.sub(r"`([^`]*)`", r"\1", md)
        md = re.sub(r"!\[.*?\]\(.*?\)", "", md)
        md = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", md)
        md = re.sub(r"\*\*(.*?)\*\*", r"\1", md)
        md = re.sub(r"\*(.*?)\*", r"\1", md)
        md = re.sub(r"__(.*?)__", r"\1", md)
        md = re.sub(r"_(.*?)_", r"\1", md)
        md = re.sub(r"^#+\s*", "", md, flags=re.MULTILINE)
        md = re.sub(r"^>\s?", "", md, flags=re.MULTILINE)
        md = re.sub(r"[-*_]{3,}", "", md)
        md = re.sub(r"^[\s]*[-*+]\s+", "", md, flags=re.MULTILINE)
        md = re.sub(r"\n{2,}", "\n\n", md)
        return md.strip()

    def html(self) -> str:
        """Return HTML generated from the markdown payload.

        When the ``markdown`` package is installed we use it directly, which
        is far more complete than our previous handwritten converter.  If the
        library isn't available we fall back to the old simple implementation
        just so the method never fails; the fallback path should only be hit in
        unit tests or extremely minimal installations.
        """
        md = self._markdown
        # lazy lookup to keep behaviour consistent if libs are installed later
        try:
            import markdown as _m
        except ImportError:
            _m = None

        if _m:
            return _m.markdown(md)

        # fallback minimal converter
        import html as _htmlmod

        text = md
        text = _htmlmod.escape(text)
        text = re.sub(r"```([\s\S]*?)```", lambda m: f"<pre><code>{_htmlmod.escape(m.group(1))}</code></pre>", text)
        text = re.sub(r"`([^`]*)`", lambda m: f"<code>{_htmlmod.escape(m.group(1))}</code>", text)
        text = re.sub(r"\[(.*?)\]\((.*?)\)", r"<a href=\"\2\">\1</a>", text)
        text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
        text = re.sub(r"^###\s*(.*?)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
        text = re.sub(r"^##\s*(.*?)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
        text = re.sub(r"^#\s*(.*?)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)
        # simple list handling remains as before
        def _ulify(text: str) -> str:
            lines = text.splitlines()
            out = []
            in_ul = False
            for line in lines:
                m = re.match(r"^[\s]*[-*+]\s+(.*)$", line)
                if m:
                    if not in_ul:
                        out.append("<ul>")
                        in_ul = True
                    out.append(f"<li>{m.group(1)}</li>")
                else:
                    if in_ul:
                        out.append("</ul>")
                        in_ul = False
                    out.append(line)
            if in_ul:
                out.append("</ul>")
            return "\n".join(out)

        text = _ulify(text)
        parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        html_parts = []
        for p in parts:
            if p.startswith("<h1>") or p.startswith("<h2>") or p.startswith("<h3>") or p.startswith("<ul>") or p.startswith("<pre>"):
                html_parts.append(p)
            else:
                html_parts.append(f"<p>{p}</p>")
        return "\n".join(html_parts)


class Document:
    def __init__(self, items: Optional[List[Segment]] = None, description: str = "", separator: str = "##"):
        self.items: List[Segment] = items or []
        self.description: str = description
        self.separator: str = separator

    @classmethod
    def from_markdown(cls, md: str, separator: str = "##") -> "Document":
        """Create a document from a markdown string.

        Everything **before** the first H2 header ("##") is treated as the
        document description; subsequent H2 sections become individual segments.
        """
        lines = md.splitlines(keepends=True)
        items: List[Segment] = []
        current_name: Optional[str] = None
        buffer: List[str] = []
        description_lines: List[str] = []
        seen_first_header = False

        # Build a regex that matches the exact separator at line start.
        # Escape the separator to treat characters like '#' literally.
        esc = re.escape(separator)
        header_re = re.compile(rf"^{esc}\s*(.*)")

        for line in lines:
            m = header_re.match(line)
            if m:
                if not seen_first_header:
                    # description collected so far
                    seen_first_header = True
                # start new segment
                if current_name is not None or buffer:
                    items.append(Segment(name=current_name or "", _markdown="".join(buffer).rstrip()))
                current_name = m.group(1).strip()
                buffer = []
            else:
                if not seen_first_header:
                    description_lines.append(line)
                else:
                    buffer.append(line)

        # finalize last
        if current_name is not None:
            items.append(Segment(name=current_name or "", _markdown="".join(buffer).rstrip()))
        elif not seen_first_header:
            # no H2 headers found: everything is description
            description_lines = lines

        desc = "".join(description_lines).strip()
        return cls(items, description=desc, separator=separator)

    def list(self, names_only: bool = True) -> List:
        return [it.name for it in self.items] if names_only else list(self.items)

    def search(self, query: str, limit: Optional[int] = None) -> List[Segment]:
        q = (query or "").strip().lower()
        if not q:
            return self.items[:limit] if limit else list(self.items)

        scored: List[tuple] = []
        for it in self.items:
            name = (it.name or "").lower()
            content = (it._markdown or "").lower()
            score = 0
            if q in name:
                score += 200
                score += max(0, 50 - name.index(q))
            if q in content:
                score += 100
                score += max(0, 25 - content.index(q))
            # fuzzy similarity
            score += int(SequenceMatcher(None, q, name).ratio() * 50)
            score += int(SequenceMatcher(None, q, content).ratio() * 10)

            if score > 0:
                scored.append((score, it))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = [it for _, it in scored]
        return results[:limit] if limit else results


# expose CLI entrypoint for setuptools
try:
    from . import cli
except ImportError:  # pragma: no cover - running without package context
    cli = None

def main():
    if cli is None:
        raise RuntimeError("CLI not available; install prompt_toolkit first")
    return cli.main()
