"""Conservative standard-library conversion of legacy lore HTML to Markdown."""

from __future__ import annotations

import csv
import html
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser


@dataclass
class Node:
    tag: str | None
    attrs: dict[str, str]
    raw_start: str = ""
    children: list[Node | str] = field(default_factory=list)
    raw_end: str = ""


@dataclass(frozen=True)
class Conversion:
    markdown: str
    warnings: tuple[str, ...]


class _TreeParser(HTMLParser):
    VOID = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=False)
        self.root = Node(None, {})
        self.stack = [self.root]
        self.warnings: list[str] = []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        raw = self.get_starttag_text() or f"<{tag}>"
        node = Node(
            tag.lower(), {key.lower(): value or "" for key, value in attrs}, raw
        )
        self.stack[-1].children.append(node)
        if tag.lower() not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        raw = self.get_starttag_text() or f"<{tag}/ >"
        self.stack[-1].children.append(
            Node(tag.lower(), {key.lower(): value or "" for key, value in attrs}, raw)
        )

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                for node in reversed(self.stack[index:]):
                    node.raw_end = f"</{node.tag}>"
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)

    def handle_entityref(self, name: str) -> None:
        self.stack[-1].children.append(html.unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        self.stack[-1].children.append(html.unescape(f"&#{name};"))


def _text(node: Node) -> str:
    return "".join(
        child if isinstance(child, str) else _text(child) for child in node.children
    )


def _raw(node: Node) -> str:
    if node.tag is None:
        return _text(node)
    body = "".join(
        html.escape(child, quote=False) if isinstance(child, str) else _raw(child)
        for child in node.children
    )
    return f"{node.raw_start}{body}{node.raw_end}"


def _fence(code: str, language: str = "") -> str:
    longest = max((len(run) for run in re.findall(r"`+", code)), default=0)
    marker = "`" * max(3, longest + 1)
    return f"{marker}{language}\n{code}\n{marker}\n\n"


def _contains_script(node: Node) -> bool:
    return node.tag == "script" or any(
        isinstance(child, Node) and _contains_script(child) for child in node.children
    )


def _prose_text(text: str) -> str:
    """Keep decoded HTML text literal when emitted into Markdown source."""
    return html.escape(re.sub(r"\s+", " ", text), quote=False)


def _inline(node: Node, warnings: list[str]) -> str:
    pieces: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            pieces.append(_prose_text(child))
            continue
        tag = child.tag or ""
        if _contains_script(child):
            warnings.append(
                f"nested script in <{tag}> preserved inertly as escaped HTML source; "
                "scripts do not execute in the Markdown rendering"
            )
            pieces.append("\n" + _fence(html.escape(_raw(child), quote=False), "html"))
            continue
        value = (
            re.sub(r"\s+", " ", _text(child))
            if tag == "code"
            else _inline(child, warnings)
        )
        if tag in {"b", "strong"}:
            pieces.append(f"**{value.strip()}**")
        elif tag in {"i", "em"}:
            pieces.append(f"*{value.strip()}*")
        elif tag == "code":
            delimiter = "``" if "`" in value else "`"
            pieces.append(f"{delimiter}{value}{delimiter}")
        elif tag == "a":
            href = child.attrs.get("href", "")
            anchor = _anchor(child)
            pieces.append(anchor + (f"[{value.strip()}]({href})" if href else value))
        elif tag == "img":
            alt, src = child.attrs.get("alt", ""), child.attrs.get("src", "")
            pieces.append(f"![{alt}]({src})" if src else alt)
        elif tag == "br":
            pieces.append("  \n")
        elif tag == "svg" or "style" in child.attrs:
            warnings.append(f"preserved styled inline HTML element <{tag}>")
            pieces.append(_raw(child))
        elif tag == "del":
            pieces.append(f"~~{value.strip()}~~")
        elif tag in {"span", "small", "sub", "sup", "s", "u"}:
            pieces.append(value)
        elif tag in {"script", "style"}:
            warnings.append(
                f"preserved <{tag}> source inertly; rendering/behavior is not preserved"
            )
            source = html.escape(_raw(child), quote=False)
            pieces.append("\n" + _fence(source, "html"))
        else:
            warnings.append(f"preserved unsupported inline markup <{tag}> as raw HTML")
            pieces.append(_raw(child))
    return "".join(pieces)


def _anchor(node: Node) -> str:
    """Emit a stable Markdown-compatible target for legacy HTML anchors."""
    identifier = node.attrs.get("id", "") or node.attrs.get("name", "")
    return f'<a id="{html.escape(identifier, quote=True)}"></a>' if identifier else ""


def _render(node: Node | str, warnings: list[str], list_indent: int = 0) -> str:
    if isinstance(node, str):
        return _prose_text(node)
    tag = node.tag or ""
    if tag in {"html", "body"}:
        return "".join(
            _render(child, warnings, list_indent)
            for child in node.children
            if not isinstance(child, Node) or child.tag != "head"
        )
    if tag == "head":
        return ""
    if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        level = int(tag[1])
        heading = f"{'#' * level} {_inline(node, warnings).strip()}\n\n"
        anchor = _anchor(node)
        return f"{anchor}\n\n{heading}" if anchor else heading
    if tag in {"p", "div", "section", "article", "header", "footer", "main"}:
        return _inline(node, warnings).strip() + "\n\n"
    if tag in {"ul", "ol"}:
        ordered = tag == "ol"
        lines: list[str] = []
        items = (
            child
            for child in node.children
            if isinstance(child, Node) and child.tag == "li"
        )
        for number, child in enumerate(items, start=1):
            marker = f"{number}. " if ordered else "- "
            indent = " " * list_indent
            content = _render(child, warnings, list_indent + len(marker)).strip()
            content_lines = content.splitlines()
            if content_lines:
                lines.append(indent + marker + content_lines[0])
                lines.extend(content_lines[1:])
        return "\n".join(lines) + "\n\n"
    if tag == "li":
        parts: list[str] = []
        inline_children: list[Node | str] = []

        def flush_inline() -> None:
            if inline_children:
                parts.append(_inline(Node(None, {}, children=inline_children), warnings).strip())
                inline_children.clear()

        for child in node.children:
            if isinstance(child, Node) and child.tag in {"ul", "ol"}:
                flush_inline()
                parts.append(_render(child, warnings, list_indent))
            else:
                inline_children.append(child)
        flush_inline()
        return "\n".join(part for part in parts if part)
    if tag == "blockquote":
        text = "".join(
            _prose_text(child)
            if isinstance(child, str)
            else _render(child, warnings, list_indent)
            for child in node.children
        ).strip()
        return "\n".join(f"> {line}" for line in text.splitlines()) + "\n\n"
    if tag == "pre":
        code = _text(node).strip("\n")
        language = ""
        for child in node.children:
            if isinstance(child, Node) and child.tag == "code":
                classes = child.attrs.get("class", "").split()
                language = next(
                    (
                        item.removeprefix("language-")
                        for item in classes
                        if item.startswith("language-")
                    ),
                    "",
                )
        return _fence(code, language)
    if tag in {"table", "svg"} or "style" in node.attrs:
        warnings.append(
            f"preserved complex <{tag}> markup as inline HTML; "
            "rendering fidelity may vary"
        )
        if _contains_script(node):
            warnings.append(
                f"nested script in <{tag}> preserved inertly as escaped HTML source; "
                "scripts do not execute in the Markdown rendering"
            )
            return _fence(html.escape(_raw(node), quote=False), "html")
        return _raw(node) + "\n\n"
    if tag in {"script", "style"}:
        warnings.append(
            f"preserved <{tag}> source inertly; rendering/behavior is not preserved"
        )
        source = html.escape(_raw(node), quote=False)
        return _fence(source, "html")
    if tag in {"hr"}:
        return "---\n\n"
    if tag in {"br"}:
        return "  \n"
    if tag in {
        "a",
        "img",
        "code",
        "strong",
        "b",
        "em",
        "i",
        "span",
        "small",
        "sub",
        "sup",
        "del",
        "s",
        "u",
    }:
        return _inline(Node(None, {}, children=[node]), warnings)
    if tag in {"meta", "link", "title", "style", "script"}:
        return ""
    if _contains_script(node):
        warnings.append(
            f"nested script in <{tag}> preserved inertly as escaped HTML source; "
            "scripts do not execute in the Markdown rendering"
        )
        return _fence(html.escape(_raw(node), quote=False), "html")
    warnings.append(f"preserved unsupported <{tag}> markup inertly as source")
    return _fence(html.escape(_raw(node), quote=False), "html")


def _metadata(root: Node) -> tuple[dict[str, str], list[str], list[str]]:
    head = next(
        (
            child
            for child in root.children
            if isinstance(child, Node) and child.tag == "html"
        ),
        root,
    )
    if head is not root:
        head = next(
            (
                child
                for child in head.children
                if isinstance(child, Node) and child.tag == "head"
            ),
            head,
        )
    fields: dict[str, str] = {}
    warnings: list[str] = []
    inert_sources: list[str] = []

    def visit(node: Node) -> None:
        if node.tag in {"script", "style"}:
            inert_sources.append(_raw(node))
            warnings.append(
                f"preserved <{node.tag}> head source inertly; "
                "behavior/rendering is not preserved"
            )
            return
        if node.tag == "meta":
            key = node.attrs.get("name", node.attrs.get("property", "")).strip().lower()
            content = node.attrs.get("content", "")
            if key and content:
                fields[key] = content
                if key not in {
                    "title",
                    "date",
                    "status",
                    "tags",
                    "modules",
                    "related",
                    "source",
                    "sequence",
                    "req-prefix",
                    "fg-type",
                    "fg-status",
                    "fg-sources",
                    "fg-evidence-code",
                    "fg-evidence-tests",
                    "fg-evidence-symbols",
                } and not key.startswith("fg-"):
                    warnings.append(f"retained unrecognized metadata field {key!r}")
        for child in node.children:
            if isinstance(child, Node):
                visit(child)

    visit(head)
    title = next(
        (
            child
            for child in head.children
            if isinstance(child, Node) and child.tag == "title"
        ),
        None,
    )
    if "title" not in fields and title:
        fields["title"] = _text(title).strip()
    return fields, warnings, inert_sources


def _yaml_value(key: str, value: str) -> str:
    if key in {"tags", "modules", "related", "fg-sources"}:
        values = next(csv.reader([value], skipinitialspace=True))
        return json.dumps(values, ensure_ascii=False)
    if key == "sequence" and value.isdigit():
        return value
    return json.dumps(value, ensure_ascii=False)


def convert_html(text: str, source_path: str = "") -> Conversion:
    """Convert ordinary HTML prose; preserve complex constructs lossily-safe."""
    parser = _TreeParser(text)
    metadata, warnings, inert_sources = _metadata(parser.root)
    warnings.extend(parser.warnings)
    rendered = "".join(
        _render(child, warnings)
        for child in parser.root.children
        if not isinstance(child, Node) or child.tag != "head"
    ).strip()
    if not rendered:
        warnings.append("HTML document has no visible body content")
    metadata_lines = []
    for key, value in metadata.items():
        if value:
            yaml_key = (
                key
                if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key)
                else json.dumps(key)
            )
            metadata_lines.append(f"{yaml_key}: {_yaml_value(key, value)}")
    output = "---\n" + "\n".join(metadata_lines) + "\n---\n\n" if metadata_lines else ""
    for source in inert_sources:
        output += _fence(html.escape(source, quote=False), "html")
    output += rendered + ("\n" if rendered else "")
    return Conversion(output, tuple(dict.fromkeys(warnings)))
