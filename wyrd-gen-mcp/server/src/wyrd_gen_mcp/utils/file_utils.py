"""File handling utilities for Wyrd-Gen MCP Server."""

import os

import httpx


def get_next_available_path(base_path: str, start_idx: int = 0) -> tuple[str, int]:
    """Find next available filename by checking existing files.

    Args:
        base_path: The base file path to check
        start_idx: Starting index to check from

    Returns:
        tuple of (next_available_path, index_used)
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

    Args:
        output_file_name: The output file name (relative or absolute)
        invoke_dir: The directory from which the server was invoked

    Returns:
        Absolute path for the output file
    """
    if os.path.isabs(output_file_name):
        return os.path.abspath(output_file_name)
    return os.path.abspath(os.path.join(invoke_dir, output_file_name))


async def download_file(url: str, dest_path: str) -> int:
    """Download a file from URL to destination path.

    Args:
        url: URL to download from
        dest_path: Destination file path

    Returns:
        Number of bytes written
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(response.content)
        return len(response.content)
