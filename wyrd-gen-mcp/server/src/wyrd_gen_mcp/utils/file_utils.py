"""File handling utilities for Wyrd-Gen MCP Server.

This module provides file system utilities for:
- Finding non-colliding file paths (collision avoidance)
- Resolving relative paths against a base directory
- Downloading files from URLs asynchronously
"""

import logging
import os

import httpx

from wyrd_gen_mcp.exceptions import FileError

logger = logging.getLogger("wyrd-gen-mcp.utils.file")


def get_next_available_path(base_path: str, start_idx: int = 0) -> tuple[str, int]:
    """Find next available filename by appending an index suffix.

    Generates filenames with incrementing indices until finding one that
    doesn't exist on disk. Used to avoid overwriting existing files when
    saving generated content.

    The index is inserted before the file extension:
        "output.png" -> "output_0.png", "output_1.png", etc.
        "output" -> "output_0", "output_1", etc. (no extension)

    Args:
        base_path: The base file path template (e.g., "/path/to/output.png")
        start_idx: Starting index to check from (default 0)

    Returns:
        Tuple of (path, index) where path is the first non-existing filename
        and index is the suffix number used.

    Example:
        # If output_0.png and output_1.png exist:
        path, idx = get_next_available_path("/path/output.png")
        # Returns: ("/path/output_2.png", 2)
    """
    name_parts = base_path.rsplit(".", 1)
    idx = start_idx
    while True:
        if len(name_parts) == 2:
            candidate = f"{name_parts[0]}_{idx}.{name_parts[1]}"
        else:
            candidate = f"{base_path}_{idx}"
        if not os.path.exists(candidate):
            return candidate, idx
        idx += 1


def resolve_output_path(output_file_name: str, invoke_dir: str) -> str:
    """Resolve output file name to absolute path.

    Handles both relative and absolute paths. Relative paths are resolved
    against the invoke directory (the directory from which the MCP server
    was started). This allows users to specify output paths relative to
    their project directory.

    Args:
        output_file_name: The output file name, either:
            - Relative path (e.g., "output.png", "images/result.png")
            - Absolute path (e.g., "/home/user/output.png")
        invoke_dir: The directory from which the server was invoked.
            This is typically passed from the MCP server context.

    Returns:
        Absolute, normalized path for the output file.

    Example:
        # Relative path resolution
        resolve_output_path("output.png", "/home/user/project")
        # Returns: "/home/user/project/output.png"

        # Absolute path passthrough
        resolve_output_path("/tmp/output.png", "/home/user/project")
        # Returns: "/tmp/output.png"
    """
    if os.path.isabs(output_file_name):
        return os.path.abspath(output_file_name)
    return os.path.abspath(os.path.join(invoke_dir, output_file_name))


async def download_file(url: str, dest_path: str) -> int:
    """Download a file from URL to destination path asynchronously.

    Downloads the file content into memory and writes it to disk. Used
    primarily for downloading generated content from Replicate's CDN.
    Follows redirects automatically.

    Args:
        url: URL to download from. Must be a valid HTTP/HTTPS URL.
        dest_path: Destination file path (should be absolute).

    Returns:
        Number of bytes written to the file.

    Raises:
        FileError: If the download fails (network error, 4xx/5xx response)
            or if the file cannot be written to disk.

    Example:
        bytes_written = await download_file(
            "https://replicate.delivery/xyz/output.mp4",
            "/home/user/project/video.mp4"
        )
        print(f"Downloaded {bytes_written} bytes")
    """
    # Truncate URL for logging (hide potential tokens in query params)
    log_url = url.split("?")[0] if "?" in url else url
    if len(log_url) > 80:
        log_url = log_url[:80] + "..."

    logger.debug(f"Starting download: {log_url} -> {dest_path}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            content_length = len(response.content)
            logger.debug(f"Downloaded {content_length} bytes from {log_url}")

            with open(dest_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Saved {content_length} bytes to {dest_path}")
            return content_length

    except httpx.TimeoutException as e:
        logger.error(f"Download timeout: {log_url}")
        raise FileError(
            "Download timed out",
            path=dest_path,
            operation="download",
            cause=e,
            url=log_url,
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} downloading {log_url}")
        raise FileError(
            f"Download failed with HTTP {e.response.status_code}",
            path=dest_path,
            operation="download",
            cause=e,
            url=log_url,
            status_code=e.response.status_code,
        )
    except httpx.HTTPError as e:
        logger.error(f"Network error downloading {log_url}: {e}")
        raise FileError(
            "Download failed due to network error",
            path=dest_path,
            operation="download",
            cause=e,
            url=log_url,
        )
    except OSError as e:
        logger.error(f"Failed to write file {dest_path}: {e}")
        raise FileError(
            "Failed to write downloaded file",
            path=dest_path,
            operation="write",
            cause=e,
        )
