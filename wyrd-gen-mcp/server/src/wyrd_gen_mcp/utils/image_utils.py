"""Image handling utilities for Wyrd-Gen MCP Server.

This module provides utilities for preparing images for API submission.
The primary function converts local image files to base64 data URIs,
which is the format required by Replicate's video generation API.

Supported formats:
    - PNG (.png)
    - JPEG (.jpg, .jpeg)
    - WebP (.webp)
"""

import base64
import logging
import os

from wyrd_gen_mcp.exceptions import FileError, ValidationError

logger = logging.getLogger("wyrd-gen-mcp.utils.image")


# Map file extensions to MIME types for data URI construction.
# Used to determine the correct MIME type when encoding images.
MIME_TYPE_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def detect_image_format(data: bytes) -> str | None:
    """Detect image format from magic bytes.

    Examines the first bytes of image data to determine the actual format,
    regardless of file extension. This is essential because Replicate models
    may return images in formats different from what the filename suggests.

    Args:
        data: Raw image bytes (at least first 12 bytes needed for detection)

    Returns:
        File extension string (e.g., ".png", ".jpg", ".webp") if recognized,
        None if format cannot be determined.

    Example:
        with open("image.png", "rb") as f:
            data = f.read()
        actual_format = detect_image_format(data)
        # Returns ".jpg" if file is actually JPEG despite .png extension
    """
    if len(data) < 12:
        return None

    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"

    # JPEG: FF D8 FF
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"

    # WebP: RIFF....WEBP (bytes 0-3 = RIFF, bytes 8-11 = WEBP)
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"

    # GIF: GIF87a or GIF89a
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"

    return None


def replace_extension(path: str, new_ext: str) -> str:
    """Replace the file extension in a path.

    Args:
        path: Original file path (e.g., "/path/to/file.png")
        new_ext: New extension including dot (e.g., ".jpg")

    Returns:
        Path with new extension (e.g., "/path/to/file.jpg")
    """
    base, _ = os.path.splitext(path)
    return base + new_ext


def image_to_data_uri(file_path: str) -> str:
    """Convert local image file to base64 data URI for Replicate API submission.

    Args:
        file_path: Path to local image file (PNG, JPG, JPEG, or WebP)

    Returns:
        Data URI string in format: data:image/{format};base64,{encoded_data}

    Raises:
        FileError: When the image file doesn't exist or cannot be read.
        ValidationError: When the image format is not supported.
    """
    logger.debug(f"Converting image to data URI: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"Input image not found: {file_path}")
        raise FileError(
            "Input image file not found",
            path=file_path,
            operation="read",
        )

    ext = os.path.splitext(file_path)[1].lower()

    if ext not in MIME_TYPE_MAP:
        supported = ", ".join(MIME_TYPE_MAP.keys())
        logger.error(f"Unsupported image format {ext} for file: {file_path}")
        raise ValidationError(
            f"Unsupported image format: {ext}",
            parameter="file_path",
            value=file_path,
            supported_formats=list(MIME_TYPE_MAP.keys()),
        )

    mime_type = MIME_TYPE_MAP[ext]

    try:
        with open(file_path, "rb") as f:
            image_data = f.read()

        file_size = len(image_data)
        logger.debug(f"Read {file_size} bytes from {file_path}")

        encoded_data = base64.b64encode(image_data).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{encoded_data}"

        logger.info(
            f"Converted image to data URI: {file_path} "
            f"({file_size} bytes -> {len(data_uri)} chars)"
        )
        return data_uri

    except OSError as e:
        logger.error(f"Failed to read image file {file_path}: {e}")
        raise FileError(
            "Failed to read image file",
            path=file_path,
            operation="read",
            cause=e,
        )
