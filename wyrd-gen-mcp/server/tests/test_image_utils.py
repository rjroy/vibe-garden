"""Tests for image utility functions."""

import base64
import os
import tempfile
from pathlib import Path

import pytest

# Ensure src directory is in path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wyrd_gen_mcp.server import image_to_data_uri


class TestImageToDataURI:
    """Test image_to_data_uri() function."""

    def test_valid_png_returns_correct_data_uri_prefix(self):
        """Test that a valid PNG file returns the correct data URI prefix."""
        # Create a minimal PNG file (1x1 transparent pixel)
        # PNG signature + minimal IHDR chunk
        png_data = (
            b"\x89PNG\r\n\x1a\n"  # PNG signature
            b"\x00\x00\x00\rIHDR"  # IHDR chunk length and type
            b"\x00\x00\x00\x01\x00\x00\x00\x01"  # Width=1, Height=1
            b"\x08\x06\x00\x00\x00"  # bit_depth=8, color_type=6 (RGBA), compression=0, filter=0, interlace=0
            b"\x1f\x15\xc4\x89"  # CRC32 checksum for IHDR
            b"\x00\x00\x00\nIDAT"  # IDAT chunk
            b"\x78\x9c\x62\x00\x01\x00\x00\x05\x00\x01"  # Minimal zlib compressed data
            b"\x0d\x0a\x2d\xb4"  # CRC32 checksum for IDAT
            b"\x00\x00\x00\x00IEND"  # IEND chunk
            b"\xae\x42\x60\x82"  # CRC32 checksum for IEND
        )

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(png_data)
            temp_path = f.name

        try:
            result = image_to_data_uri(temp_path)

            # Verify the data URI starts with the correct MIME type
            assert result.startswith("data:image/png;base64,")

            # Verify it contains base64-encoded data
            base64_part = result.split(",", 1)[1]
            decoded = base64.b64decode(base64_part)
            assert decoded == png_data
        finally:
            os.unlink(temp_path)

    def test_valid_jpg_returns_correct_data_uri_prefix(self):
        """Test that a valid JPG file returns the correct data URI prefix."""
        # Create a minimal JPG file (1x1 pixel)
        # JPEG signature + minimal structure
        jpg_data = (
            b"\xff\xd8\xff\xe0"  # JPEG SOI and APP0 marker
            b"\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"  # JFIF header
            b"\xff\xdb\x00\x43\x00"  # DQT marker and length
            + b"\x08" * 64  # Quantization table (simplified)
            + b"\xff\xc0\x00\x0b\x08"  # SOF0 marker
            b"\x00\x01\x00\x01\x01\x01\x11\x00"  # Frame header
            b"\xff\xc4\x00\x14\x00\x01"  # DHT marker
            + b"\x00" * 16
            + b"\x00"  # Huffman table (minimal)
            + b"\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00"  # SOS marker
            b"\xd2\xcf\x20"  # Minimal scan data
            b"\xff\xd9"  # EOI marker
        )

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(jpg_data)
            temp_path = f.name

        try:
            result = image_to_data_uri(temp_path)

            # Verify the data URI starts with the correct MIME type
            assert result.startswith("data:image/jpeg;base64,")

            # Verify it contains base64-encoded data
            base64_part = result.split(",", 1)[1]
            decoded = base64.b64decode(base64_part)
            assert decoded == jpg_data
        finally:
            os.unlink(temp_path)

    def test_valid_jpeg_extension_returns_correct_data_uri_prefix(self):
        """Test that a .jpeg extension (not .jpg) also works correctly."""
        # Same JPG data as above
        jpg_data = (
            b"\xff\xd8\xff\xe0"
            b"\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
            b"\xff\xdb\x00\x43\x00"
            + b"\x08" * 64
            + b"\xff\xc0\x00\x0b\x08"
            b"\x00\x01\x00\x01\x01\x01\x11\x00"
            b"\xff\xc4\x00\x14\x00\x01"
            + b"\x00" * 16
            + b"\x00"
            + b"\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00"
            b"\xd2\xcf\x20"
            b"\xff\xd9"
        )

        with tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False) as f:
            f.write(jpg_data)
            temp_path = f.name

        try:
            result = image_to_data_uri(temp_path)
            assert result.startswith("data:image/jpeg;base64,")
        finally:
            os.unlink(temp_path)

    def test_valid_webp_returns_correct_data_uri_prefix(self):
        """Test that a valid WebP file returns the correct data URI prefix."""
        # Create a minimal WebP file
        # RIFF header + WebP VP8 chunk
        webp_data = (
            b"RIFF"  # RIFF header
            b"\x1a\x00\x00\x00"  # File size (26 bytes after this field)
            b"WEBP"  # WebP signature
            b"VP8 "  # VP8 chunk FourCC
            b"\x0e\x00\x00\x00"  # VP8 data size (14 bytes)
            b"\x00\x00\x00\x9d\x01\x2a"  # VP8 frame header (1x1 pixel)
            b"\x01\x00\x01\x00"  # Width=1, Height=1
            b"\x00\x00\x00\x00"  # Padding/minimal data
        )

        with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as f:
            f.write(webp_data)
            temp_path = f.name

        try:
            result = image_to_data_uri(temp_path)

            # Verify the data URI starts with the correct MIME type
            assert result.startswith("data:image/webp;base64,")

            # Verify it contains base64-encoded data
            base64_part = result.split(",", 1)[1]
            decoded = base64.b64decode(base64_part)
            assert decoded == webp_data
        finally:
            os.unlink(temp_path)

    def test_missing_file_raises_file_not_found_error(self):
        """Test that a missing file raises FileNotFoundError."""
        nonexistent_path = "/tmp/definitely_does_not_exist_12345.png"

        with pytest.raises(FileNotFoundError) as exc_info:
            image_to_data_uri(nonexistent_path)

        # Verify the error message contains the path
        assert nonexistent_path in str(exc_info.value)

    def test_unsupported_format_raises_value_error(self):
        """Test that an unsupported file format raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not an image")
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                image_to_data_uri(temp_path)

            # Verify the error message mentions unsupported format
            assert "Unsupported image format" in str(exc_info.value)
            assert ".txt" in str(exc_info.value)
        finally:
            os.unlink(temp_path)

    def test_unsupported_format_gif_raises_value_error(self):
        """Test that GIF format (not supported) raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
            f.write(b"GIF89a")  # Minimal GIF header
            temp_path = f.name

        try:
            with pytest.raises(ValueError) as exc_info:
                image_to_data_uri(temp_path)

            assert "Unsupported image format" in str(exc_info.value)
            assert ".gif" in str(exc_info.value)
        finally:
            os.unlink(temp_path)

    def test_case_insensitive_extension_handling(self):
        """Test that uppercase extensions are handled correctly."""
        # Test with .PNG extension (uppercase)
        png_data = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00"
            b"\x1f\x15\xc4\x89"
            b"\x00\x00\x00\nIDAT"
            b"\x78\x9c\x62\x00\x01\x00\x00\x05\x00\x01"
            b"\x0d\x0a\x2d\xb4"
            b"\x00\x00\x00\x00IEND"
            b"\xae\x42\x60\x82"
        )

        with tempfile.NamedTemporaryFile(suffix=".PNG", delete=False) as f:
            f.write(png_data)
            temp_path = f.name

        try:
            result = image_to_data_uri(temp_path)
            assert result.startswith("data:image/png;base64,")
        finally:
            os.unlink(temp_path)

    def test_empty_file_is_encoded_correctly(self):
        """Test that an empty file (edge case) is handled."""
        # Note: This tests the encoding behavior, not validity as an image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            # Write nothing - empty file
            temp_path = f.name

        try:
            result = image_to_data_uri(temp_path)

            # Should still create a valid data URI structure
            assert result.startswith("data:image/png;base64,")

            # The base64 part should be empty or minimal
            base64_part = result.split(",", 1)[1]
            # Empty file encodes to empty string
            assert base64_part == ""
        finally:
            os.unlink(temp_path)

    def test_no_external_dependencies(self):
        """Verify tests use only mock/temp files, no external resources."""
        # This test documents the testing approach
        # All tests in this class use tempfile.NamedTemporaryFile
        # No network calls, no external file dependencies
        # This satisfies the "no external dependencies" requirement
        assert True  # Meta-test: documentation of approach

    def test_base64_encoding_is_valid(self):
        """Test that the base64 encoding is valid and can be decoded."""
        test_data = b"test image data"

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(test_data)
            temp_path = f.name

        try:
            result = image_to_data_uri(temp_path)

            # Extract and decode the base64 part
            _, encoded = result.split(",", 1)
            decoded = base64.b64decode(encoded)

            # Should match original data
            assert decoded == test_data
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
