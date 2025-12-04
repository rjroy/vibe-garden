"""Tests for Replicate image generation.

This module tests the ReplicateImageGenerator class, covering:
- Successful generation with single file output (FileOutput with read())
- Successful generation with multiple files (iterable output)
- API error handling
- Input validation
- Output processing for unknown formats
- File collision avoidance
"""

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure src directory is in path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wyrd_gen_mcp.exceptions import GenerationError, ValidationError
from wyrd_gen_mcp.generators.replicate_image import ReplicateImageGenerator


class TestReplicateImageGenerator:
    """Test suite for ReplicateImageGenerator."""

    @pytest.mark.asyncio
    async def test_generate_success_single_file(
        self, mock_replicate_client, mock_file_output, temp_dir
    ):
        """Test successful generation with single FileOutput.

        Verifies that when Replicate returns a FileOutput object with a read()
        method, the generator correctly saves it to disk and returns a result.
        """
        # Setup
        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)
        mock_replicate_client.async_run.return_value = mock_file_output

        # Execute
        result = await generator.generate(
            prompt="A beautiful sunset",
            model="black-forest-labs/flux-schnell",
            output_file_name="sunset.png",
            parameters={"num_inference_steps": 4},
        )

        # Verify API was called correctly
        mock_replicate_client.async_run.assert_called_once()
        call_args = mock_replicate_client.async_run.call_args
        assert call_args[0][0] == "black-forest-labs/flux-schnell"
        assert call_args[1]["input"]["prompt"] == "A beautiful sunset"
        assert call_args[1]["input"]["num_inference_steps"] == 4

        # Verify result
        assert result.success is True
        assert result.model == "black-forest-labs/flux-schnell"
        assert result.prompt == "A beautiful sunset"
        assert len(result.saved_files) == 1
        assert result.saved_files[0].endswith("sunset_0.png")
        assert result.parameters == {"num_inference_steps": 4}

        # Verify file was created
        assert os.path.exists(result.saved_files[0])
        with open(result.saved_files[0], "rb") as f:
            assert f.read() == b"fake_image_data"

    @pytest.mark.asyncio
    async def test_generate_success_multiple_files(
        self, mock_replicate_client, temp_dir
    ):
        """Test successful generation with multiple files (iterable output).

        Verifies that when Replicate returns an iterable of FileOutput objects
        (e.g., batch generation), all files are saved with proper indexing.
        """
        # Setup - create multiple mock FileOutput objects
        mock_output1 = MagicMock()
        mock_output1.read = MagicMock(return_value=b"fake_image_data_1")

        mock_output2 = MagicMock()
        mock_output2.read = MagicMock(return_value=b"fake_image_data_2")

        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)
        mock_replicate_client.async_run.return_value = [mock_output1, mock_output2]

        # Execute
        result = await generator.generate(
            prompt="Multiple cats",
            model="black-forest-labs/flux-schnell",
            output_file_name="cats.png",
        )

        # Verify result
        assert result.success is True
        assert len(result.saved_files) == 2
        assert result.saved_files[0].endswith("cats_0.png")
        assert result.saved_files[1].endswith("cats_1.png")

        # Verify files were created with correct content
        with open(result.saved_files[0], "rb") as f:
            assert f.read() == b"fake_image_data_1"
        with open(result.saved_files[1], "rb") as f:
            assert f.read() == b"fake_image_data_2"

    @pytest.mark.asyncio
    async def test_generate_api_error(self, mock_replicate_client, temp_dir):
        """Test handling of Replicate API errors.

        Verifies that when the Replicate SDK raises an exception, it's properly
        wrapped in a GenerationError with context.
        """
        # Setup - make async_run raise an exception
        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)
        mock_replicate_client.async_run.side_effect = RuntimeError("API rate limit exceeded")

        # Execute and verify exception
        with pytest.raises(GenerationError) as exc_info:
            await generator.generate(
                prompt="A sunset",
                model="black-forest-labs/flux-schnell",
                output_file_name="output.png",
            )

        # Verify error details
        error = exc_info.value
        assert "Replicate API call failed" in error.message
        assert error.context["operation"] == "replicate_api_call"
        assert error.context["model"] == "black-forest-labs/flux-schnell"
        assert error.context["prompt"] == "A sunset"
        assert isinstance(error.cause, RuntimeError)
        assert str(error.cause) == "API rate limit exceeded"

    @pytest.mark.asyncio
    async def test_validate_missing_model(self, mock_replicate_client, temp_dir):
        """Test validation error when model is missing.

        Verifies that an empty or None model parameter raises ValidationError
        before making any API calls.
        """
        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)

        # Test with empty string
        with pytest.raises(ValidationError) as exc_info:
            await generator.generate(
                prompt="A sunset",
                model="",
                output_file_name="output.png",
            )

        error = exc_info.value
        assert "model is required" in error.message
        assert error.context["parameter"] == "model"

        # Verify no API call was made
        mock_replicate_client.async_run.assert_not_called()

    @pytest.mark.asyncio
    async def test_validate_missing_output(self, mock_replicate_client, temp_dir):
        """Test validation error when output_file_name is missing.

        Verifies that an empty output_file_name parameter raises ValidationError
        before making any API calls.
        """
        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)

        # Test with empty string
        with pytest.raises(ValidationError) as exc_info:
            await generator.generate(
                prompt="A sunset",
                model="black-forest-labs/flux-schnell",
                output_file_name="",
            )

        error = exc_info.value
        assert "output_file_name is required" in error.message
        assert error.context["parameter"] == "output_file_name"

        # Verify no API call was made
        mock_replicate_client.async_run.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_output_unknown_format(
        self, mock_replicate_client, temp_dir, caplog
    ):
        """Test handling of unknown output format.

        Verifies that when Replicate returns an unexpected output type,
        a warning is logged and an empty result is returned (no crash).
        """
        # Setup - return an unexpected type (string URL, not FileOutput)
        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)
        mock_replicate_client.async_run.return_value = "https://example.com/image.png"

        # Execute
        with caplog.at_level("WARNING"):
            result = await generator.generate(
                prompt="A sunset",
                model="black-forest-labs/flux-schnell",
                output_file_name="output.png",
            )

        # Verify result is still successful but with no saved files
        assert result.success is True
        assert len(result.saved_files) == 0

        # Verify warning was logged
        assert any("Unexpected output type" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_collision_avoidance(
        self, mock_replicate_client, mock_file_output, temp_dir
    ):
        """Test that files don't overwrite existing files.

        Verifies that when an output file already exists, the generator uses
        collision avoidance to create a new file with an incremented name.
        """
        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)
        mock_replicate_client.async_run.return_value = mock_file_output

        # Create first file
        result1 = await generator.generate(
            prompt="First image",
            model="black-forest-labs/flux-schnell",
            output_file_name="image.png",
        )

        # Create second file with same name
        result2 = await generator.generate(
            prompt="Second image",
            model="black-forest-labs/flux-schnell",
            output_file_name="image.png",
        )

        # Verify both files exist with different names
        assert len(result1.saved_files) == 1
        assert len(result2.saved_files) == 1
        assert result1.saved_files[0] != result2.saved_files[0]

        # First file should be image_0.png, second should be image_1.png
        assert result1.saved_files[0].endswith("image_0.png")
        assert result2.saved_files[0].endswith("image_1.png")

        # Both files should exist
        assert os.path.exists(result1.saved_files[0])
        assert os.path.exists(result2.saved_files[0])

    @pytest.mark.asyncio
    async def test_collision_avoidance_multiple_files(
        self, mock_replicate_client, temp_dir
    ):
        """Test collision avoidance for multiple file generation.

        Verifies that when generating multiple files in a batch, and some files
        already exist, the indexing starts from the next available index.
        """
        # Setup - create multiple mock FileOutput objects
        mock_output1 = MagicMock()
        mock_output1.read = MagicMock(return_value=b"data_1")

        mock_output2 = MagicMock()
        mock_output2.read = MagicMock(return_value=b"data_2")

        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)

        # First generation: creates batch_0.png and batch_1.png
        mock_replicate_client.async_run.return_value = [mock_output1, mock_output2]
        result1 = await generator.generate(
            prompt="First batch",
            model="black-forest-labs/flux-schnell",
            output_file_name="batch.png",
        )

        assert len(result1.saved_files) == 2
        assert result1.saved_files[0].endswith("batch_0.png")
        assert result1.saved_files[1].endswith("batch_1.png")

        # Second generation: should create batch_2.png and batch_3.png
        result2 = await generator.generate(
            prompt="Second batch",
            model="black-forest-labs/flux-schnell",
            output_file_name="batch.png",
        )

        assert len(result2.saved_files) == 2
        assert result2.saved_files[0].endswith("batch_2.png")
        assert result2.saved_files[1].endswith("batch_3.png")

        # All four files should exist
        for file_path in result1.saved_files + result2.saved_files:
            assert os.path.exists(file_path)

    @pytest.mark.asyncio
    async def test_format_correction_jpeg_to_jpg(
        self, mock_replicate_client, temp_dir
    ):
        """Test that JPEG data is saved with .jpg extension even if user requested .png.

        This is critical because Replicate models often return JPEG data for efficiency,
        but users might specify .png as the output filename. If we save JPEG data with
        a .png extension, tools that read the file will fail due to format mismatch.
        """
        # Setup - create a mock that returns JPEG data (FF D8 FF signature)
        jpeg_data = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # JPEG magic bytes + padding
        mock_output = MagicMock()
        mock_output.read = MagicMock(return_value=jpeg_data)

        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)
        mock_replicate_client.async_run.return_value = mock_output

        # Execute - request .png but API returns JPEG
        result = await generator.generate(
            prompt="A sunset",
            model="black-forest-labs/flux-schnell",
            output_file_name="sunset.png",
        )

        # Verify file was saved with .jpg extension, not .png
        assert result.success is True
        assert len(result.saved_files) == 1
        assert result.saved_files[0].endswith(".jpg")
        assert "sunset_0.jpg" in result.saved_files[0]

        # Verify file exists and contains the JPEG data
        assert os.path.exists(result.saved_files[0])
        with open(result.saved_files[0], "rb") as f:
            assert f.read() == jpeg_data

    @pytest.mark.asyncio
    async def test_format_correction_webp_to_webp(
        self, mock_replicate_client, temp_dir
    ):
        """Test that WebP data is saved with .webp extension even if user requested .png."""
        # Setup - create a mock that returns WebP data (RIFF....WEBP signature)
        webp_data = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100
        mock_output = MagicMock()
        mock_output.read = MagicMock(return_value=webp_data)

        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)
        mock_replicate_client.async_run.return_value = mock_output

        # Execute - request .png but API returns WebP
        result = await generator.generate(
            prompt="A sunset",
            model="black-forest-labs/flux-schnell",
            output_file_name="sunset.png",
        )

        # Verify file was saved with .webp extension
        assert result.success is True
        assert len(result.saved_files) == 1
        assert result.saved_files[0].endswith(".webp")

    @pytest.mark.asyncio
    async def test_format_correction_png_stays_png(
        self, mock_replicate_client, temp_dir
    ):
        """Test that PNG data is saved with .png extension when user requested .png."""
        # Setup - create a mock that returns PNG data (89 PNG signature)
        png_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        mock_output = MagicMock()
        mock_output.read = MagicMock(return_value=png_data)

        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)
        mock_replicate_client.async_run.return_value = mock_output

        # Execute - request .png and API returns PNG
        result = await generator.generate(
            prompt="A sunset",
            model="black-forest-labs/flux-schnell",
            output_file_name="sunset.png",
        )

        # Verify file was saved with .png extension (no correction needed)
        assert result.success is True
        assert len(result.saved_files) == 1
        assert result.saved_files[0].endswith(".png")

    @pytest.mark.asyncio
    async def test_format_correction_multiple_files(
        self, mock_replicate_client, temp_dir
    ):
        """Test format correction works for multiple file output."""
        # Setup - create multiple mocks returning JPEG data
        jpeg_data = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        mock_output1 = MagicMock()
        mock_output1.read = MagicMock(return_value=jpeg_data)
        mock_output2 = MagicMock()
        mock_output2.read = MagicMock(return_value=jpeg_data)

        generator = ReplicateImageGenerator(mock_replicate_client, temp_dir)
        mock_replicate_client.async_run.return_value = [mock_output1, mock_output2]

        # Execute - request .png but API returns JPEG for all
        result = await generator.generate(
            prompt="Multiple sunsets",
            model="black-forest-labs/flux-schnell",
            output_file_name="sunset.png",
        )

        # Verify all files were saved with .jpg extension
        assert result.success is True
        assert len(result.saved_files) == 2
        assert all(f.endswith(".jpg") for f in result.saved_files)
        assert "sunset_0.jpg" in result.saved_files[0]
        assert "sunset_1.jpg" in result.saved_files[1]
