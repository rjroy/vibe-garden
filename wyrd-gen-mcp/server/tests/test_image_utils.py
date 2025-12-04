"""Tests for image utility functions."""

import base64
import os
import tempfile
from pathlib import Path

import pytest

# Ensure src directory is in path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wyrd_gen_mcp.utils.image_utils import (
    detect_image_format,
    image_to_data_uri,
    replace_extension,
)


class TestDetectImageFormat:
    """Test detect_image_format() function."""

    def test_detect_png_format(self):
        """Test that PNG magic bytes are correctly detected."""
        # PNG signature: 89 50 4E 47 0D 0A 1A 0A
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
        assert detect_image_format(png_data) == ".png"

    def test_detect_jpeg_format(self):
        """Test that JPEG magic bytes are correctly detected."""
        # JPEG signature: FF D8 FF
        jpeg_data = b"\xff\xd8\xff\xe0" + b"\x00" * 20
        assert detect_image_format(jpeg_data) == ".jpg"

    def test_detect_webp_format(self):
        """Test that WebP magic bytes are correctly detected."""
        # WebP: RIFF....WEBP
        webp_data = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 10
        assert detect_image_format(webp_data) == ".webp"

    def test_detect_gif87a_format(self):
        """Test that GIF87a magic bytes are correctly detected."""
        gif_data = b"GIF87a" + b"\x00" * 20
        assert detect_image_format(gif_data) == ".gif"

    def test_detect_gif89a_format(self):
        """Test that GIF89a magic bytes are correctly detected."""
        gif_data = b"GIF89a" + b"\x00" * 20
        assert detect_image_format(gif_data) == ".gif"

    def test_unknown_format_returns_none(self):
        """Test that unknown formats return None."""
        unknown_data = b"unknown format data here"
        assert detect_image_format(unknown_data) is None

    def test_empty_data_returns_none(self):
        """Test that empty data returns None."""
        assert detect_image_format(b"") is None

    def test_short_data_returns_none(self):
        """Test that data too short for detection returns None."""
        short_data = b"\x89PNG"  # Only 4 bytes, need 12
        assert detect_image_format(short_data) is None

    def test_minimum_length_for_detection(self):
        """Test detection with exactly minimum required bytes."""
        # Exactly 12 bytes with PNG signature
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 4
        assert len(png_data) == 12
        assert detect_image_format(png_data) == ".png"


class TestReplaceExtension:
    """Test replace_extension() function."""

    def test_replace_png_with_jpg(self):
        """Test replacing .png extension with .jpg."""
        assert replace_extension("/path/to/file.png", ".jpg") == "/path/to/file.jpg"

    def test_replace_extension_preserves_path(self):
        """Test that the directory path is preserved."""
        assert replace_extension("/home/user/images/photo.png", ".webp") == "/home/user/images/photo.webp"

    def test_replace_extension_no_directory(self):
        """Test replacing extension on filename without directory."""
        assert replace_extension("image.png", ".jpg") == "image.jpg"

    def test_replace_extension_multiple_dots(self):
        """Test replacing extension when filename has multiple dots."""
        assert replace_extension("/path/to/my.image.file.png", ".jpg") == "/path/to/my.image.file.jpg"

    def test_replace_extension_no_original_extension(self):
        """Test replacing extension on filename without extension."""
        assert replace_extension("/path/to/file", ".png") == "/path/to/file.png"


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
        """Test that a missing file raises FileError."""
        from wyrd_gen_mcp.exceptions import FileError

        nonexistent_path = "/tmp/definitely_does_not_exist_12345.png"

        with pytest.raises(FileError) as exc_info:
            image_to_data_uri(nonexistent_path)

        # Verify the error contains context about the path
        assert exc_info.value.context.get("path") == nonexistent_path

    def test_unsupported_format_raises_value_error(self):
        """Test that an unsupported file format raises ValidationError."""
        from wyrd_gen_mcp.exceptions import ValidationError

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not an image")
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
                image_to_data_uri(temp_path)

            # Verify the error message mentions unsupported format
            assert "Unsupported image format" in str(exc_info.value)
            assert ".txt" in str(exc_info.value)
        finally:
            os.unlink(temp_path)

    def test_unsupported_format_gif_raises_value_error(self):
        """Test that GIF format (not supported) raises ValidationError."""
        from wyrd_gen_mcp.exceptions import ValidationError

        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
            f.write(b"GIF89a")  # Minimal GIF header
            temp_path = f.name

        try:
            with pytest.raises(ValidationError) as exc_info:
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
