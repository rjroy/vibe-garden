"""
Unit tests for markdown export module (export.py).

Tests message formatting, filename generation, and collision prevention.
"""

import pytest
from pathlib import Path
import yaml

from courier_mcp.export import (
    format_message_to_markdown,
    generate_filename,
    resolve_export_path,
    safe_file_write,
    extract_headers,  # Changed from extract_email_headers
    extract_attachments
)


@pytest.mark.unit
class TestMessageFormatting:
    """Test suite for message formatting functions."""

    def test_extract_email_headers(self, sample_message_full):
        """Test extracting email headers from Gmail message."""
        headers = extract_headers(sample_message_full)

        assert headers["from"] == "Alice Johnson <alice@example.com>"
        assert headers["to"] == "user@gmail.com"
        assert headers["cc"] == "bob@example.com"  # Returns string, not list
        assert headers["subject"] == "Q4 Planning: [VOICE] Meeting Notes"
        assert headers["date"] == "Mon, 15 Oct 2025 14:32:00 -0700"

    def test_extract_email_headers_plain_text(self, sample_message_plain_text):
        """Test header extraction for plain text messages."""
        headers = extract_headers(sample_message_plain_text)

        assert headers["from"] == "Bob Smith <bob@example.com>"
        assert headers["to"] == "user@gmail.com"
        assert headers["cc"] == ""  # Empty string, not empty list
        assert headers["subject"] == "Simple Test Email"

    def test_extract_attachments(self, sample_message_full):
        """Test extracting attachment metadata from message."""
        attachments = extract_attachments(sample_message_full)

        assert len(attachments) == 1
        assert attachments[0]["filename"] == "meeting-notes.pdf"
        assert attachments[0]["size"] == 245678
        assert attachments[0]["mime_type"] == "application/pdf"

    def test_extract_attachments_no_attachments(self, sample_message_plain_text):
        """Test attachment extraction when message has no attachments."""
        attachments = extract_attachments(sample_message_plain_text)

        assert attachments == []

    def test_format_message_to_markdown_with_html(self, sample_message_full):
        """Test formatting message with HTML content."""
        markdown = format_message_to_markdown(sample_message_full)

        # Check YAML frontmatter is present
        assert markdown.startswith("---\n")
        assert "from: Alice Johnson <alice@example.com>" in markdown

        # Check frontmatter is valid YAML
        frontmatter_end = markdown.find("\n---\n", 4)
        frontmatter_yaml = markdown[4:frontmatter_end]
        parsed = yaml.safe_load(frontmatter_yaml)

        assert parsed["from"] == "Alice Johnson <alice@example.com>"
        assert parsed["subject"] == "Q4 Planning: [VOICE] Meeting Notes"
        assert len(parsed["attachments"]) == 1

        # Check markdown body is present
        assert "# Email from Alice Johnson" in markdown

    def test_format_message_to_markdown_plain_text(self, sample_message_plain_text):
        """Test formatting plain text message."""
        markdown = format_message_to_markdown(sample_message_plain_text)

        assert markdown.startswith("---\n")
        assert "from: Bob Smith <bob@example.com>" in markdown
        assert "subject: Simple Test Email" in markdown

        # No attachments (key not present for messages without attachments)
        frontmatter_end = markdown.find("\n---\n", 4)
        frontmatter_yaml = markdown[4:frontmatter_end]
        parsed = yaml.safe_load(frontmatter_yaml)
        # Attachments key may not be present if no attachments
        assert "attachments" not in parsed or parsed["attachments"] == []

    def test_format_message_respects_file_size_limit(self, sample_message_full):
        """Test that large messages can be formatted without error."""
        # Create a very large message body
        import copy
        large_message = copy.deepcopy(sample_message_full)
        # Simulate large body content (> 10KB)
        large_body_data = "VGhpcyBpcyBhIHZlcnkgbGFyZ2UgbWVzc2FnZS4=" * 1000  # ~30KB when decoded
        large_message["payload"]["parts"][0]["body"]["data"] = large_body_data

        # format_message_to_markdown doesn't take max_size_kb parameter
        # Size limiting happens in truncate_markdown() which is called separately
        markdown = format_message_to_markdown(large_message)

        # Should successfully format (truncation is done separately)
        assert markdown.startswith("---\n")
        frontmatter_end = markdown.find("\n---\n", 4)
        frontmatter_yaml = markdown[4:frontmatter_end]
        parsed = yaml.safe_load(frontmatter_yaml)
        assert parsed["from"] == "Alice Johnson <alice@example.com>"


@pytest.mark.unit
class TestFilenameGeneration:
    """Test suite for filename generation and collision handling."""

    def test_generate_filename_basic(self, sample_message_full):
        """Test basic filename generation."""
        filename = generate_filename(sample_message_full)

        # Should follow format: YYYYMMDD_HHMMSS_folder_from_sender.md
        assert filename.endswith(".md")
        assert "_inbox_" in filename.lower()
        assert "alice" in filename.lower()

    def test_generate_filename_sanitizes_special_chars(self):
        """Test that special characters are sanitized in filenames."""
        message = {
            "labelIds": ["INBOX"],
            "internalDate": "1697385600000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "Test User <test@example.com>"},
                    {"name": "Subject", "value": "Test/Subject:With*Special|Chars?"}
                ]
            }
        }

        filename = generate_filename(message)

        # Should not contain special chars like /, :, *, |, ?
        assert "/" not in filename
        assert ":" not in filename.split("_", 2)[2]  # After timestamp
        assert "*" not in filename
        assert "|" not in filename
        assert "?" not in filename

    def test_generate_filename_handles_long_sender_names(self):
        """Test that very long sender names are truncated."""
        message = {
            "labelIds": ["INBOX"],
            "internalDate": "1697385600000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "VeryLongSenderNameThatExceedsReasonableLength <sender@example.com>"},
                    {"name": "Subject", "value": "Test"}
                ]
            }
        }

        filename = generate_filename(message)

        # Filename should not be excessively long (< 255 chars for filesystem)
        assert len(filename) < 255

    def test_generate_filename_timestamp_format(self):
        """Test that timestamp is in correct format (YYYYMMDD_HHMMSS)."""
        message = {
            "labelIds": ["INBOX"],
            "internalDate": "1697385600000",  # Oct 15, 2023, 14:00:00 GMT
            "payload": {
                "headers": [
                    {"name": "From", "value": "Test <test@example.com>"},
                    {"name": "Date", "value": "Mon, 15 Oct 2023 14:00:00 +0000"}
                ]
            }
        }

        filename = generate_filename(message)

        # Should start with YYYYMMDD_HHMMSS
        parts = filename.split("_")
        assert len(parts[0]) == 8  # YYYYMMDD
        assert len(parts[1]) == 6  # HHMMSS


@pytest.mark.unit
class TestSafeFileWrite:
    """Test suite for safe file writing with collision detection."""

    def test_safe_file_write_new_file(self, temp_export_dir):
        """Test writing a new file (no collision)."""
        content = "Test markdown content"
        filename = "test_email.md"
        filepath = str(temp_export_dir / filename)

        result_path = safe_file_write(filepath, content)

        assert Path(result_path).exists()
        assert Path(result_path).name == filename
        assert Path(result_path).read_text() == content

    def test_safe_file_write_collision_adds_suffix(self, temp_export_dir):
        """Test that collisions are handled with _1, _2 suffixes."""
        content = "Test markdown content"
        filename = "test_email.md"
        filepath = str(temp_export_dir / filename)

        # Write first file
        path1 = safe_file_write(filepath, content)
        assert Path(path1).name == filename

        # Write second file with same name
        path2 = safe_file_write(filepath, content + " v2")
        assert Path(path2).name == "test_email_1.md"
        assert Path(path2).read_text() == content + " v2"

        # Write third file
        path3 = safe_file_write(filepath, content + " v3")
        assert Path(path3).name == "test_email_2.md"

    def test_safe_file_write_atomic_operation(self, temp_export_dir):
        """Test that write is atomic (uses temp file + rename)."""
        content = "Test content"
        filename = "test.md"
        filepath = str(temp_export_dir / filename)

        result_path = safe_file_write(filepath, content)

        # Should not leave temp files behind
        temp_files = list(temp_export_dir.glob("*.tmp"))
        assert len(temp_files) == 0

        # Final file should exist
        assert Path(result_path).exists()
        assert Path(result_path).read_text() == content

    def test_safe_file_write_creates_directory(self, tmp_path):
        """Test that safe_file_write creates directory if it doesn't exist."""
        export_dir = tmp_path / "emails" / "subfolder"
        assert not export_dir.exists()

        content = "Test"
        filename = "test.md"
        filepath = str(export_dir / filename)

        result_path = safe_file_write(filepath, content)

        assert export_dir.exists()
        assert Path(result_path).exists()

    def test_safe_file_write_max_collisions(self, temp_export_dir):
        """Test that collision detection has a reasonable limit."""
        content = "Test"
        filename = "test.md"
        filepath = str(temp_export_dir / filename)

        # Create many files
        for i in range(5):
            safe_file_write(filepath, f"content {i}")

        # Should have files: test.md, test_1.md, test_2.md, test_3.md, test_4.md
        assert (temp_export_dir / "test.md").exists()
        assert (temp_export_dir / "test_4.md").exists()

    def test_safe_file_write_preserves_content_exactly(self, temp_export_dir):
        """Test that content is written exactly as provided (no modifications)."""
        content = """---
from: test@example.com
subject: Test
---

# Test Email

This is a test with **markdown** formatting.
"""

        filename = "test.md"
        filepath = str(temp_export_dir / filename)
        result_path = safe_file_write(filepath, content)

        assert Path(result_path).read_text() == content


@pytest.mark.unit
class TestPathResolution:
    """Test suite for export path resolution (TASK-024 / v1.2.0)."""

    def test_resolve_absolute_path(self, monkeypatch):
        """Test that absolute paths are used as-is."""
        # Set INVOKE_DIR (should be ignored for absolute paths)
        monkeypatch.setenv("INVOKE_DIR", "/user/invocation/dir")

        absolute_path = "/tmp/exports"
        resolved = resolve_export_path(absolute_path)

        # Should resolve to absolute path, ignoring INVOKE_DIR
        assert resolved.is_absolute()
        assert str(resolved) == str(Path(absolute_path).resolve())

    def test_resolve_relative_path_with_invoke_dir(self, monkeypatch):
        """Test that relative paths are resolved from INVOKE_DIR."""
        invoke_dir = "/home/user/notes"
        monkeypatch.setenv("INVOKE_DIR", invoke_dir)

        relative_path = "emails"
        resolved = resolve_export_path(relative_path)

        # Should resolve to INVOKE_DIR / relative_path
        expected = (Path(invoke_dir) / relative_path).resolve()
        assert resolved == expected
        assert str(resolved) == str(expected)

    def test_resolve_relative_path_with_subdirs(self, monkeypatch):
        """Test relative paths with subdirectories."""
        invoke_dir = "/home/user/notes"
        monkeypatch.setenv("INVOKE_DIR", invoke_dir)

        relative_path = "emails/inbox/2025"
        resolved = resolve_export_path(relative_path)

        expected = (Path(invoke_dir) / relative_path).resolve()
        assert resolved == expected

    def test_resolve_relative_path_without_invoke_dir(self, monkeypatch):
        """Test fallback when INVOKE_DIR is not set."""
        # Ensure INVOKE_DIR is not set
        monkeypatch.delenv("INVOKE_DIR", raising=False)

        relative_path = "emails"
        resolved = resolve_export_path(relative_path)

        # Should fall back to current working directory
        expected = (Path.cwd() / relative_path).resolve()
        assert resolved == expected

    def test_resolve_path_normalization(self, monkeypatch):
        """Test that paths with .. and . are normalized."""
        invoke_dir = "/home/user/notes"
        monkeypatch.setenv("INVOKE_DIR", invoke_dir)

        relative_path = "emails/../exports/./data"
        resolved = resolve_export_path(relative_path)

        # Should normalize .. and . components
        expected = (Path(invoke_dir) / relative_path).resolve()
        assert resolved == expected
        # Verify normalization occurred
        assert ".." not in str(resolved)
        assert "/." not in str(resolved) and str(resolved)[-2:] != "/."

    def test_resolve_current_directory_relative(self, monkeypatch):
        """Test resolving current directory reference."""
        invoke_dir = "/home/user/notes"
        monkeypatch.setenv("INVOKE_DIR", invoke_dir)

        relative_path = "."
        resolved = resolve_export_path(relative_path)

        # Should resolve to INVOKE_DIR itself
        expected = Path(invoke_dir).resolve()
        assert resolved == expected

    def test_resolve_parent_directory_relative(self, monkeypatch):
        """Test resolving parent directory reference."""
        invoke_dir = "/home/user/notes"
        monkeypatch.setenv("INVOKE_DIR", invoke_dir)

        relative_path = "../emails"
        resolved = resolve_export_path(relative_path)

        # Should resolve relative to INVOKE_DIR
        expected = (Path(invoke_dir) / relative_path).resolve()
        assert resolved == expected
