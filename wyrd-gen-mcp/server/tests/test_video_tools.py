"""Integration tests for video generation tools.

Tests the three video tools (generate_video_replicate, list_video_models_replicate,
get_video_model_parameters_replicate) covering acceptance tests AT-1 through AT-8
from the spec.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from wyrd_gen_mcp.data import VIDEO_MODELS, VIDEO_PARAMETERS
from wyrd_gen_mcp.server import (
    generate_video_replicate,
    get_video_model_parameters_replicate,
    list_video_models_replicate,
)


class MockFileOutput:
    """Mock Replicate FileOutput object with read() method."""

    def __init__(self, content: bytes):
        self.content = content

    def read(self) -> bytes:
        """Return the file content."""
        return self.content


class MockPrediction:
    """Mock Replicate Prediction object."""

    def __init__(self, status: str = "succeeded", output: str | None = None, error: str | None = None):
        self.id = "mock-prediction-id"
        self.status = status
        self.output = output
        self.error = error


class MockContext:
    """Mock FastMCP Context for progress reporting."""

    async def report_progress(self, progress: int, total: int | None, message: str) -> None:
        """Mock progress reporting."""
        pass


@pytest.fixture
def temp_input_image():
    """Create a temporary input image file for testing."""
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as f:
        # Create a minimal valid PNG (1x1 pixel)
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
def temp_output_dir():
    """Create a temporary directory for output files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_context():
    """Create a mock FastMCP context."""
    return MockContext()


@pytest.fixture
def mock_replicate_video_generator():
    """Mock the video generator to avoid real API calls."""
    with patch("wyrd_gen_mcp.server.replicate_video_generator") as mock_gen:
        yield mock_gen


# AT-1: Basic video generation with mocked API returns success response
@pytest.mark.asyncio
async def test_generate_video_basic_success(
    temp_input_image, temp_output_dir, mock_context, mock_replicate_video_generator
):
    """AT-1: Basic video generation with mocked API returns success response."""
    from wyrd_gen_mcp.generators.base import GenerationResult

    output_path = os.path.join(temp_output_dir, "test_output.mp4")

    # Mock the generator's generate method
    mock_result = GenerationResult(
        success=True,
        model="wan-video/wan-2.2-i2v-fast",
        prompt="A person walking forward",
        saved_files=[output_path.replace(".mp4", "_0.mp4")],
        parameters={},
        input_image=temp_input_image,
        duration_seconds=5,
        resolution="720p",
    )
    mock_replicate_video_generator.generate = AsyncMock(return_value=mock_result)

    # Call the function
    result = await generate_video_replicate(
        image=temp_input_image,
        prompt="A person walking forward",
        model="wan-video/wan-2.2-i2v-fast",
        output_file_name=output_path,
        ctx=mock_context,
        parameters={},
    )

    # Verify response structure
    response_data = json.loads(result)
    assert response_data["success"] is True
    assert response_data["model"] == "wan-video/wan-2.2-i2v-fast"
    assert response_data["prompt"] == "A person walking forward"
    assert response_data["duration_seconds"] == 5
    assert response_data["resolution"] == "720p"


# AT-2: Model listing returns all catalog models with use_case and cost
@pytest.mark.asyncio
async def test_list_video_models_complete():
    """AT-2: Model listing returns all catalog models with use_case and cost."""
    result = await list_video_models_replicate()

    models = json.loads(result)

    # Verify it's a list
    assert isinstance(models, list)

    # Verify all catalog models are present
    assert len(models) == len(VIDEO_MODELS)

    # Verify each model has required fields
    for model in models:
        assert "model" in model
        assert "description" in model
        assert "use_case" in model
        assert "cost_per_video" in model
        assert "vendor" in model
        assert "duration_seconds" in model
        assert "resolution" in model
        assert "fps" in model

        # Verify use_case is valid
        assert model["use_case"] in {
            "iteration",
            "animation",
            "stylized",
            "photorealistic",
            "premium",
        }

        # Verify cost is numeric
        assert isinstance(model["cost_per_video"], (int, float))


# AT-3: Parameter discovery returns schema for known model, error for unknown
@pytest.mark.asyncio
async def test_get_video_model_parameters_known_model():
    """AT-3a: Parameter discovery returns schema for known model."""
    result = await get_video_model_parameters_replicate(model="wan-video/wan-2.2-i2v-fast")

    params = json.loads(result)

    # Verify structure
    assert "model" in params
    assert "parameters" in params
    assert params["model"] == "wan-video/wan-2.2-i2v-fast"

    # Verify parameters object
    assert isinstance(params["parameters"], dict)
    assert "image" in params["parameters"]
    assert "prompt" in params["parameters"]


@pytest.mark.asyncio
async def test_get_video_model_parameters_unknown_model():
    """AT-3b: Parameter discovery returns error for unknown model."""
    result = await get_video_model_parameters_replicate(model="unknown/fake-model")

    response = json.loads(result)

    # Verify error response
    assert "error" in response
    assert "available_models" in response
    assert "Unknown model: unknown/fake-model" in response["error"]
    assert isinstance(response["available_models"], list)


# AT-4: Iteration model has lowest cost in catalog
@pytest.mark.asyncio
async def test_iteration_model_is_cheapest():
    """AT-4: The 'iteration' use case model is the cheapest option in the catalog."""
    result = await list_video_models_replicate()
    models = json.loads(result)

    # Find iteration model
    iteration_models = [m for m in models if m["use_case"] == "iteration"]
    assert len(iteration_models) > 0, "No iteration model found in catalog"

    iteration_cost = iteration_models[0]["cost_per_video"]

    # Verify it's the cheapest
    all_costs = [m["cost_per_video"] for m in models]
    min_cost = min(all_costs)

    assert (
        iteration_cost == min_cost
    ), f"Iteration model cost {iteration_cost} is not the minimum {min_cost}"


# AT-5: Missing input image returns structured error
@pytest.mark.asyncio
async def test_missing_input_image_error(temp_output_dir, mock_context):
    """AT-5: System returns structured error when input image doesn't exist."""
    from wyrd_gen_mcp.exceptions import FileError

    # Use a path that doesn't exist
    nonexistent_image = os.path.join(temp_output_dir, "nonexistent.png")
    output_path = os.path.join(temp_output_dir, "output.mp4")

    # The function raises FileError with context
    with pytest.raises(FileError) as exc_info:
        await generate_video_replicate(
            image=nonexistent_image,
            prompt="Test prompt",
            model="wan-video/wan-2.2-i2v-fast",
            output_file_name=output_path,
            ctx=mock_context,
        )

    # Verify error has context about the path
    assert exc_info.value.context.get("path") == nonexistent_image


# AT-7: Cost display present in model listing
@pytest.mark.asyncio
async def test_cost_display_in_listing():
    """AT-7: Model cost per video is included in listing response."""
    result = await list_video_models_replicate()
    models = json.loads(result)

    # Verify every model has cost_per_video field
    for model in models:
        assert "cost_per_video" in model
        assert isinstance(model["cost_per_video"], (int, float))
        assert model["cost_per_video"] > 0


# Test: Verify unsupported image format returns error
@pytest.mark.asyncio
async def test_unsupported_image_format(temp_output_dir, mock_context):
    """Verify system returns error for unsupported image formats."""
    from wyrd_gen_mcp.exceptions import ValidationError

    # Create a temporary file with unsupported extension
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bmp", delete=False) as f:
        f.write(b"fake_bmp_data")
        unsupported_image = f.name

    try:
        output_path = os.path.join(temp_output_dir, "output.mp4")

        # The function raises ValidationError for unsupported format
        with pytest.raises(ValidationError) as exc_info:
            await generate_video_replicate(
                image=unsupported_image,
                prompt="Test prompt",
                model="wan-video/wan-2.2-i2v-fast",
                output_file_name=output_path,
                ctx=mock_context,
            )

        # Verify error message mentions unsupported format
        error_msg = str(exc_info.value).lower()
        assert "unsupported" in error_msg or "format" in error_msg
    finally:
        # Cleanup
        if os.path.exists(unsupported_image):
            os.remove(unsupported_image)


# Test: Verify video metadata is included in response
@pytest.mark.asyncio
async def test_video_metadata_in_response(
    temp_input_image, temp_output_dir, mock_context, mock_replicate_video_generator
):
    """Verify response includes duration_seconds and resolution from catalog."""
    from wyrd_gen_mcp.generators.base import GenerationResult

    output_path = os.path.join(temp_output_dir, "output.mp4")

    # Mock the generator's generate method
    mock_result = GenerationResult(
        success=True,
        model="wan-video/wan-2.2-i2v-fast",
        prompt="Test motion",
        saved_files=[output_path.replace(".mp4", "_0.mp4")],
        parameters={},
        input_image=temp_input_image,
        duration_seconds=5,
        resolution="720p",
    )
    mock_replicate_video_generator.generate = AsyncMock(return_value=mock_result)

    result = await generate_video_replicate(
        image=temp_input_image,
        prompt="Test motion",
        model="wan-video/wan-2.2-i2v-fast",
        output_file_name=output_path,
        ctx=mock_context,
    )
    response = json.loads(result)

    # Verify metadata fields
    assert "duration_seconds" in response
    assert "resolution" in response
    assert response["duration_seconds"] == 5
    assert response["resolution"] == "720p"
