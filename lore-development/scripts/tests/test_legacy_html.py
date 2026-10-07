from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from legacy_html import convert_html  # noqa: E402


def test_body_text_and_top_level_inline_content_are_retained() -> None:
    prose = convert_html(
        "<body>Critical warning <p>Details</p>Final decision</body>"
    )
    assert "Critical warning" in prose.markdown
    assert "Details" in prose.markdown
    assert "Final decision" in prose.markdown

    inline = convert_html(
        '<body><img src="diagram.png" alt="Architecture">'
        '<a href="runbook.md">Runbook</a></body>'
    )
    assert "![Architecture](diagram.png)" in inline.markdown
    assert "[Runbook](runbook.md)" in inline.markdown


def test_decoded_html_entities_stay_literal_in_prose_but_not_code() -> None:
    converted = convert_html(
        "<body><p>Paragraph: &lt;script&gt;alert(1)&lt;/script&gt;; "
        "&lt;b&gt;literal markup&lt;/b&gt;; A &amp; B; safe <em>emphasis</em>.</p>"
        "Body: &lt;script&gt;alert(2)&lt;/script&gt;. "
        "<code>&lt;script&gt;</code><pre>&lt;script&gt;</pre></body>"
    )

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in converted.markdown
    assert "&lt;script&gt;alert(2)&lt;/script&gt;" in converted.markdown
    assert "&lt;b&gt;literal markup&lt;/b&gt;" in converted.markdown
    assert "A &amp; B" in converted.markdown
    assert "safe *emphasis*" in converted.markdown
    assert "`<script>`" in converted.markdown
    assert "<script>" in converted.markdown.split("```", 1)[1]
    assert "<script>alert(1)</script>" not in converted.markdown
    assert not converted.warnings


def test_common_mixed_markup_code_and_deletion_semantics() -> None:
    converted = convert_html(
        '<h2 id="rationale">Why <em>this</em> decision</h2>'
        '<p>A <strong>strong</strong> link: <a href="guide.md">guide</a>; '
        '<del>obsolete</del>.</p><ul><li>first</li><li>second</li></ul>'
        '<pre><code>&lt;safe&gt;</code></pre>'
    )
    assert '<a id="rationale"></a>' in converted.markdown
    assert "## Why *this* decision" in converted.markdown
    assert "**strong**" in converted.markdown
    assert "[guide](guide.md)" in converted.markdown
    assert "~~obsolete~~" in converted.markdown
    assert "- first" in converted.markdown and "- second" in converted.markdown
    assert "<safe>" in converted.markdown


def test_generic_legacy_anchor_is_preserved() -> None:
    converted = convert_html('<p><a name="details"></a>Details follow.</p>')
    assert '<a id="details"></a>' in converted.markdown
    assert "Details follow." in converted.markdown


def test_blockquotes_render_children_and_nest_without_recursing() -> None:
    converted = convert_html(
        "<blockquote><p>Outer point</p>"
        "<blockquote><p>Inner point</p></blockquote></blockquote>"
    )
    assert "> Outer point" in converted.markdown
    assert "> > Inner point" in converted.markdown


def test_safe_complex_markup_is_retained_with_rendering_warning() -> None:
    converted = convert_html(
        '<svg viewBox="0 0 1 1"><text>Diagram label</text></svg>'
        '<table style="border: 1px"><tr><td>Cell</td></tr></table>'
    )
    assert '<svg viewBox="0 0 1 1">' in converted.markdown
    assert "Diagram label" in converted.markdown
    assert "<table style=\"border: 1px\">" in converted.markdown
    assert "Cell" in converted.markdown
    assert any(
        "rendering fidelity may vary" in warning for warning in converted.warnings
    )


def test_nested_script_in_inline_and_raw_fallback_is_fenced_inert_source() -> None:
    for source in (
        "<p><svg><script>alert(1)</script></svg></p>",
        "<custom><script>alert(1)</script></custom>",
    ):
        converted = convert_html(source)
        assert "```html" in converted.markdown
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in converted.markdown
        assert "<script>alert(1)</script>" not in converted.markdown
        assert any("nested script" in warning for warning in converted.warnings)
        assert any("do not execute" in warning for warning in converted.warnings)
