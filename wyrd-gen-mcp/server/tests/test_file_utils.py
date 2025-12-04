"""Tests for file utility functions.

This module tests:
- get_next_available_path: collision avoidance for file names
- resolve_output_path: path resolution (relative, absolute, tilde)
- download_file: async file downloads with error handling
"""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import httpx
import pytest

# Ensure src directory is in path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wyrd_gen_mcp.exceptions import FileError
from wyrd_gen_mcp.utils.file_utils import (
    download_file,
    get_next_available_path,
    resolve_output_path,
)


class TestGetNextAvailablePath:
    """Test get_next_available_path() function for collision avoidance."""

    def test_get_next_available_path_no_collision(self):
        """Test that first index is returned when no collision exists."""
        with patch("os.path.exists") as mock_exists:
            # First path doesn't exist
            mock_exists.return_value = False

            result_path, result_idx = get_next_available_path("/tmp/output.png")

            # Should return the first candidate with index 0
            assert result_path == "/tmp/output_0.png"
            assert result_idx == 0
            mock_exists.assert_called_once_with("/tmp/output_0.png")

    def test_get_next_available_path_with_collision(self):
        """Test that function skips existing files and finds next available."""
        with patch("os.path.exists") as mock_exists:
            # First two paths exist, third doesn't
            mock_exists.side_effect = [True, True, False]

            result_path, result_idx = get_next_available_path("/tmp/output.png")

            # Should skip 0 and 1, return 2
            assert result_path == "/tmp/output_2.png"
            assert result_idx == 2
            assert mock_exists.call_count == 3

    def test_get_next_available_path_no_extension(self):
        """Test that function works with paths without file extensions."""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False

            result_path, result_idx = get_next_available_path("/tmp/output")

            # Should append index directly without extension separator
            assert result_path == "/tmp/output_0"
            assert result_idx == 0

    def test_get_next_available_path_custom_start_index(self):
        """Test that function respects custom starting index."""
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False

            result_path, result_idx = get_next_available_path(
                "/tmp/output.png", start_idx=5
            )

            # Should start checking from index 5
            assert result_path == "/tmp/output_5.png"
            assert result_idx == 5
            mock_exists.assert_called_once_with("/tmp/output_5.png")


class TestResolveOutputPath:
    """Test resolve_output_path() function for path resolution."""

    def test_resolve_output_path_relative(self):
        """Test that relative paths are joined with invoke_dir."""
        result = resolve_output_path("output.png", "/home/user/project")

        # Should join relative path with invoke_dir
        assert result == "/home/user/project/output.png"

    def test_resolve_output_path_relative_with_subdirs(self):
        """Test that relative paths with subdirectories work correctly."""
        result = resolve_output_path("images/output.png", "/home/user/project")

        # Should preserve subdirectory structure
        assert result == "/home/user/project/images/output.png"

    def test_resolve_output_path_absolute(self):
        """Test that absolute paths are returned normalized."""
        result = resolve_output_path("/tmp/output.png", "/home/user/project")

        # Should return absolute path unchanged (normalized)
        assert result == "/tmp/output.png"

    def test_resolve_output_path_tilde(self):
        """Test that tilde expansion is handled correctly."""
        # Note: tilde expansion is NOT automatically handled by resolve_output_path
        # This test verifies the current behavior (tilde treated as relative)
        result = resolve_output_path("~/output.png", "/home/user/project")

        # Tilde is treated as a relative path component
        # To support tilde expansion, user should expand before calling
        assert result == "/home/user/project/~/output.png"

    def test_resolve_output_path_dot_relative(self):
        """Test that dot-relative paths are resolved correctly."""
        result = resolve_output_path("./output.png", "/home/user/project")

        # Should resolve dot-relative path
        assert result == "/home/user/project/output.png"


class TestDownloadFile:
    """Test download_file() async function for file downloads."""

    @pytest.mark.asyncio
    async def test_download_file_success(self):
        """Test successful file download writes content to disk."""
        mock_response = MagicMock()
        mock_response.content = b"fake_video_data"
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        # Mock httpx.AsyncClient
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        # Mock file writing
        mock_file = mock_open()

        with patch("httpx.AsyncClient", return_value=mock_client):
            with patch("builtins.open", mock_file):
                bytes_written = await download_file(
                    "https://example.com/video.mp4", "/tmp/output.mp4"
                )

        # Should return correct byte count
        assert bytes_written == 15  # len(b"fake_video_data")

        # Should write content to file
        mock_file.assert_called_once_with("/tmp/output.mp4", "wb")
        mock_file().write.assert_called_once_with(b"fake_video_data")

        # Should make GET request with correct URL
        mock_client.get.assert_called_once_with(
            "https://example.com/video.mp4", follow_redirects=True
        )

    @pytest.mark.asyncio
    async def test_download_file_http_error(self):
        """Test that HTTP 4xx/5xx errors raise FileError."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "404 Not Found",
                request=MagicMock(),
                response=mock_response,
            )
        )

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(FileError) as exc_info:
                await download_file(
                    "https://example.com/missing.mp4", "/tmp/output.mp4"
                )

        # Should raise FileError with correct context
        error = exc_info.value
        assert "HTTP 404" in error.message
        assert error.context["operation"] == "download"
        assert error.context["path"] == "/tmp/output.mp4"
        assert error.context["status_code"] == 404

    @pytest.mark.asyncio
    async def test_download_file_network_error(self):
        """Test that network/connection errors raise FileError."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(FileError) as exc_info:
                await download_file(
                    "https://example.com/video.mp4", "/tmp/output.mp4"
                )

        # Should raise FileError with network error context
        error = exc_info.value
        assert "network error" in error.message.lower()
        assert error.context["operation"] == "download"
        assert error.context["path"] == "/tmp/output.mp4"

    @pytest.mark.asyncio
    async def test_download_file_timeout(self):
        """Test that timeout errors raise FileError."""
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        with patch("httpx.AsyncClient", return_value=mock_client):
            with pytest.raises(FileError) as exc_info:
                await download_file(
                    "https://example.com/video.mp4", "/tmp/output.mp4"
                )

        # Should raise FileError with timeout context
        error = exc_info.value
        assert "timed out" in error.message.lower()
        assert error.context["operation"] == "download"
        assert error.context["path"] == "/tmp/output.mp4"

    @pytest.mark.asyncio
    async def test_download_file_write_error(self):
        """Test that disk write failures raise FileError."""
        mock_response = MagicMock()
        mock_response.content = b"fake_video_data"
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client.get = AsyncMock(return_value=mock_response)

        # Mock file writing to raise OSError (e.g., disk full, permission denied)
        mock_file = mock_open()
        mock_file.return_value.write.side_effect = OSError("Disk full")

        with patch("httpx.AsyncClient", return_value=mock_client):
            with patch("builtins.open", mock_file):
                with pytest.raises(FileError) as exc_info:
                    await download_file(
                        "https://example.com/video.mp4", "/tmp/output.mp4"
                    )

        # Should raise FileError with write operation context
        error = exc_info.value
        assert "write" in error.message.lower()
        assert error.context["operation"] == "write"
        assert error.context["path"] == "/tmp/output.mp4"
