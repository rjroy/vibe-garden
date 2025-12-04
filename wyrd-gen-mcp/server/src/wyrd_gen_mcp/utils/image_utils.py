"""Image handling utilities for Wyrd-Gen MCP Server."""

import base64
import os


# Map extensions to MIME types
MIME_TYPE_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def image_to_data_uri(file_path: str) -> str:
    """Convert local image file to base64 data URI for Replicate API submission.

    Args:
        file_path: Path to local image file (PNG, JPG, JPEG, or WebP)

    Returns:
        Data URI string in format: data:image/{format};base64,{encoded_data}

    Raises:
        FileNotFoundError: When the image file doesn't exist
        ValueError: When the image format is not supported
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input image not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()

    if ext not in MIME_TYPE_MAP:
        supported = ", ".join(MIME_TYPE_MAP.keys())
        raise ValueError(f"Unsupported image format: {ext}. Supported formats: {supported}")

    mime_type = MIME_TYPE_MAP[ext]

    try:
        with open(file_path, "rb") as f:
            image_data = f.read()
        encoded_data = base64.b64encode(image_data).decode("utf-8")
        return f"data:{mime_type};base64,{encoded_data}"
    except Exception as e:
        raise ValueError(f"Failed to read image file: {str(e)}")
