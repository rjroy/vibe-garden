"""Message export to markdown with YAML frontmatter.

Provides:
- Gmail message formatting to markdown
- HTML to markdown conversion
- YAML frontmatter generation
- File size limit enforcement
- Filename generation and collision prevention
- Safe file writing with atomic operations
"""

import os
import re
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import tempfile
import shutil

import yaml
import html2text

from courier_mcp.logger import get_logger
from courier_mcp.config import get_config
from courier_mcp.errors import ExportError

logger = get_logger(__name__)


def decode_payload(data: str) -> str:
    """Decode base64url encoded Gmail payload.

    Args:
        data: Base64url encoded string

    Returns:
        Decoded UTF-8 string

    Raises:
        ValueError: If decoding fails
    """
    # Replace - with + and _ with /
    data = data.replace("-", "+").replace("_", "/")
    # Add padding if needed
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.b64decode(data).decode("utf-8", errors="ignore")


def extract_email_address(email_str: str) -> str:
    """Extract email address from "Name <email@example.com>" format.

    Args:
        email_str: Email string in various formats

    Returns:
        Email address or original string if parsing fails
    """
    if not email_str:
        return ""

    # Try to extract from "Name <email>" format
    match = re.search(r"<([^>]+)>", email_str)
    if match:
        return match.group(1)

    return email_str.strip()


def extract_sender_name(email_str: str) -> str:
    """Extract display name from email string.

    Args:
        email_str: Email string like "Alice Smith <alice@example.com>"

    Returns:
        Display name or email address if no name
    """
    if not email_str:
        return "unknown"

    # Try to extract name from "Name <email>" format
    match = re.match(r"^([^<]+?)\s*<", email_str)
    if match:
        name = match.group(1).strip('"')
        return name

    # Return email address part
    return extract_email_address(email_str)


def get_message_body(message: Dict[str, Any]) -> str:
    """Extract message body from Gmail message payload.

    Tries to extract in order:
    1. Plain text (text/plain)
    2. HTML (text/html)
    3. Empty if no body found

    Args:
        message: Gmail message dict (from API)

    Returns:
        Message body as string
    """
    payload = message.get("payload", {})

    # Direct body (for simple messages)
    if "body" in payload and payload["body"].get("data"):
        try:
            return decode_payload(payload["body"]["data"])
        except Exception as e:
            logger.warning(f"Failed to decode direct body: {e}")

    # Multipart - search for text/plain or text/html
    parts = payload.get("parts", [])
    plain_text = None
    html_body = None

    for part in parts:
        mime_type = part.get("mimeType", "")
        body_data = part.get("body", {}).get("data")

        if not body_data:
            continue

        try:
            decoded = decode_payload(body_data)
            if mime_type == "text/plain":
                plain_text = decoded
            elif mime_type == "text/html":
                html_body = decoded
        except Exception as e:
            logger.debug(f"Failed to decode {mime_type}: {e}")

    # Return plain text if available, else HTML converted to text
    if plain_text:
        return plain_text
    if html_body:
        # Convert HTML to markdown
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.body_width = 0  # Don't wrap lines
        try:
            return h.handle(html_body)
        except Exception as e:
            logger.warning(f"HTML conversion failed: {e}, returning raw HTML")
            return html_body

    return ""


def extract_headers(message: Dict[str, Any]) -> Dict[str, Any]:
    """Extract email headers from Gmail message.

    Args:
        message: Gmail message dict

    Returns:
        Dict with from, to, cc, bcc, subject, date headers
    """
    headers = {}
    header_list = message.get("payload", {}).get("headers", [])

    # Build header map
    header_map = {}
    for header in header_list:
        name = header.get("name", "").lower()
        value = header.get("value", "")
        # Keep last value if duplicate headers
        header_map[name] = value

    return {
        "from": header_map.get("from", ""),
        "to": header_map.get("to", ""),
        "cc": header_map.get("cc", ""),
        "bcc": header_map.get("bcc", ""),
        "subject": header_map.get("subject", "(no subject)"),
        "date": header_map.get("date", ""),
    }


def parse_recipients(recipients_str: str) -> List[str]:
    """Parse comma-separated recipients into list.

    Handles "Name <email>" format.

    Args:
        recipients_str: Comma-separated string

    Returns:
        List of email addresses
    """
    if not recipients_str:
        return []

    # Simple split and clean
    return [r.strip() for r in recipients_str.split(",") if r.strip()]


def extract_attachments(message: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract attachment metadata from message.

    Returns metadata (filename, size, MIME type) but not binary data.

    Args:
        message: Gmail message dict

    Returns:
        List of attachment dicts with filename, size, mime_type
    """
    attachments = []
    parts = message.get("payload", {}).get("parts", [])

    for part in parts:
        filename = part.get("filename")
        if not filename:
            continue

        # Skip inline parts
        if part.get("mimeType", "").startswith("multipart/"):
            continue

        attachment = {
            "filename": filename,
            "size": int(part.get("body", {}).get("size", 0)),
            "mime_type": part.get("mimeType", "application/octet-stream"),
        }

        # Add download URL if available (Gmail attachment links)
        # Note: We don't download binary, just provide metadata
        if "attachmentId" in part.get("body", {}):
            attachment["attachment_id"] = part["body"]["attachmentId"]

        attachments.append(attachment)

    return attachments


def format_message_to_markdown(message: Dict[str, Any]) -> str:
    """Convert Gmail message to markdown with YAML frontmatter.

    Format:
    ---
    from: ...
    to: ...
    subject: ...
    date: ...
    message-id: ...
    labels: [...]
    attachments: [...]
    ---

    # Email Body

    Body content in markdown...

    Args:
        message: Gmail message dict (from API)

    Returns:
        Markdown string with frontmatter

    Raises:
        ExportError: If formatting fails
    """
    try:
        # Extract headers
        headers = extract_headers(message)

        # Parse recipients
        to_list = parse_recipients(headers["to"])
        cc_list = parse_recipients(headers["cc"])
        bcc_list = parse_recipients(headers["bcc"])

        # Extract body
        body = get_message_body(message)

        # Extract attachments
        attachments = extract_attachments(message)

        # Parse date to ISO format
        try:
            # Gmail date format: "Mon, 18 Oct 2025 14:30:00 +0000"
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(headers["date"])
            date_iso = dt.isoformat()
        except Exception as e:
            logger.debug(f"Failed to parse date '{headers['date']}': {e}")
            date_iso = headers["date"]

        # Extract labels from message
        labels = []
        label_ids = message.get("labelIds", [])
        # Map IDs to friendly names (basic mapping)
        for label_id in label_ids:
            if label_id == "INBOX":
                labels.append("INBOX")
            elif label_id == "SENT":
                labels.append("SENT")
            elif label_id == "DRAFT":
                labels.append("DRAFT")
            else:
                # Custom label - use ID for now
                labels.append(label_id)

        # Build YAML frontmatter
        frontmatter = {
            "from": headers["from"],
            "to": to_list[0] if to_list else "",
            "cc": cc_list if cc_list else [],
            "bcc": bcc_list if bcc_list else [],
            "subject": headers["subject"],
            "date": date_iso,
            "message-id": message.get("id", ""),
            "labels": labels,
        }

        if attachments:
            frontmatter["attachments"] = attachments

        # Format frontmatter
        yaml_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)

        # Build markdown
        markdown = f"""---
{yaml_str}---

# Email from {extract_sender_name(headers["from"])}

{body}
"""

        return markdown

    except Exception as e:
        logger.error(f"Failed to format message: {e}")
        raise ExportError(f"Failed to format message as markdown: {e}")


def truncate_markdown(content: str, max_size_kb: int = 10) -> str:
    """Truncate markdown content to max size, preserving frontmatter.

    If content exceeds max size, appends truncation note after frontmatter.

    Args:
        content: Full markdown content
        max_size_kb: Maximum size in kilobytes

    Returns:
        Possibly truncated markdown
    """
    max_bytes = max_size_kb * 1024

    if len(content.encode("utf-8")) <= max_bytes:
        return content

    # Find end of frontmatter
    parts = content.split("---", 2)  # Split at most 2 times
    if len(parts) < 3:
        # Malformed frontmatter, truncate from start
        truncation_note = "\n\n[Message truncated - exceeded size limit. Full message available in Gmail.]\n"
        available = max_bytes - len(truncation_note.encode("utf-8"))
        return content[:available] + truncation_note

    frontmatter = parts[0] + "---" + parts[1] + "---"
    body = parts[2]

    # Calculate space available for body
    available = max_bytes - len(frontmatter.encode("utf-8")) - 200  # 200 for truncation note

    if available > 0:
        # Truncate body
        body_truncated = body[:available]
        truncation_note = "\n\n[Message truncated - exceeded size limit. Full message available in Gmail.]\n"
        return frontmatter + body_truncated + truncation_note
    else:
        # Not enough space, just add note
        truncation_note = "\n\n[Message truncated - exceeded size limit. Full message available in Gmail.]\n"
        return frontmatter + truncation_note


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """Sanitize filename - remove special characters.

    Keeps: alphanumeric, underscore, hyphen
    Replaces spaces with underscores

    Args:
        name: Original filename
        max_length: Maximum length (truncate if longer)

    Returns:
        Sanitized filename
    """
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove special characters, keep alphanumeric, _, -
    name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
    # Truncate if needed
    if len(name) > max_length:
        name = name[:max_length]
    return name or "message"


def generate_filename(
    message: Dict[str, Any],
    folder: str = "inbox",
) -> str:
    """Generate filename for markdown export.

    Format: YYYYMMDD_HHMMSS_[folder]_from_[sender-name].md

    Example: 20251018_145032_inbox_from_alice.md

    Args:
        message: Gmail message dict
        folder: Folder/label name (default: "inbox")

    Returns:
        Filename (without directory path)
    """
    # Extract date from headers
    headers = extract_headers(message)
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(headers["date"])
        timestamp = dt.strftime("%Y%m%d_%H%M%S")
    except Exception:
        # Fallback to message ID timestamp or current time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Extract sender name
    sender_name = extract_sender_name(headers["from"])
    sender_name = sanitize_filename(sender_name, max_length=30)

    # Normalize folder name
    folder_normalized = sanitize_filename(folder, max_length=15)

    filename = f"{timestamp}_{folder_normalized}_from_{sender_name}.md"
    return filename


def safe_file_write(filepath: str, content: str) -> str:
    """Write file safely with collision detection.

    If file exists, appends _1, _2, etc. suffix.
    Uses atomic write (temp file + rename) to prevent corruption.

    Args:
        filepath: Target file path (absolute or relative)
        content: Content to write

    Returns:
        Path where file was actually written

    Raises:
        ExportError: If write fails or directory doesn't exist
    """
    try:
        # Resolve path
        path = Path(filepath).resolve()

        # Create directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file exists and find available name
        final_path = path
        if final_path.exists():
            # Find next available suffix
            stem = path.stem
            suffix = path.suffix
            parent = path.parent
            counter = 1
            while counter < 1000:
                final_path = parent / f"{stem}_{counter}{suffix}"
                if not final_path.exists():
                    break
                counter += 1

            if counter >= 1000:
                raise ExportError(f"Too many file collisions for {path}")

        # Write to temp file first (atomic write)
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Atomic rename
            shutil.move(tmp_path, str(final_path))
            logger.info(f"Wrote file: {final_path}")
            return str(final_path)
        except Exception as e:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            raise e

    except ExportError:
        raise
    except Exception as e:
        logger.error(f"Failed to write file {filepath}: {e}")
        raise ExportError(f"Failed to write file: {e}")


if __name__ == "__main__":
    print("✓ Export module loaded")
