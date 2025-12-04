"""Shared pytest fixtures for wyrd-gen-mcp test suite.

Provides reusable fixtures for:
- Temporary directories and files
- Mock Replicate client and API responses
- Mock image data

These fixtures are auto-discovered by pytest and available to all test modules.
"""

import os
import tempfile
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs.

    The directory is automatically cleaned up after the test completes.

    Yields:
        str: Path to temporary directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_image_file():
    """Create a temporary image file with minimal valid PNG data.

    Creates a 1x1 pixel PNG file suitable for testing image processing.
    The file is automatically cleaned up after the test completes.

    Yields:
        str: Path to temporary PNG file
    """
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as f:
        # Minimal valid PNG (1x1 pixel, black)
        png_data = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        f.write(png_data)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def mock_replicate_client():
    """Create a mock Replicate client for testing without API calls.

    Returns a MagicMock configured with AsyncMock methods for:
    - async_run: For image generation
    - predictions.async_create: For video generation
    - predictions.async_get: For polling video status
    - predictions.async_cancel: For timeout handling

    Returns:
        MagicMock: Mock Replicate client
    """
    mock_client = MagicMock()

    # Mock async methods for image generation
    mock_client.async_run = AsyncMock()

    # Mock predictions API for video generation
    mock_client.predictions = MagicMock()
    mock_client.predictions.async_create = AsyncMock()
    mock_client.predictions.async_get = AsyncMock()
    mock_client.predictions.async_cancel = AsyncMock()

    return mock_client


@pytest.fixture
def mock_file_output():
    """Create a mock Replicate FileOutput object.

    FileOutput objects are returned by Replicate API for file-based outputs.
    They have a read() method that returns bytes.

    Returns:
        MagicMock: Mock FileOutput with read() method
    """
    mock_output = MagicMock()
    mock_output.read = MagicMock(return_value=b"fake_image_data")
    return mock_output


@pytest.fixture
def mock_prediction():
    """Create a mock Replicate Prediction object.

    Prediction objects track async generation status for video generation.

    Args:
        Can be customized in tests by accessing attributes:
        - id: Prediction ID
        - status: "starting", "processing", "succeeded", "failed", "canceled"
        - output: Output URL or FileOutput
        - error: Error message if failed

    Returns:
        MagicMock: Mock Prediction object
    """
    mock_pred = MagicMock()
    mock_pred.id = "test-prediction-id"
    mock_pred.status = "succeeded"
    mock_pred.output = "https://example.com/output.mp4"
    mock_pred.error = None
    return mock_pred
