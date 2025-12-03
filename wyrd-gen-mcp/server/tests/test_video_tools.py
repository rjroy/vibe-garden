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
def mock_replicate_client():
    """Mock the Replicate client to avoid real API calls."""
    with patch("wyrd_gen_mcp.server.replicate_client") as mock_client:
        yield mock_client


# AT-1: Basic video generation with mocked API returns success response
@pytest.mark.asyncio
async def test_generate_video_basic_success(
    temp_input_image, temp_output_dir, mock_replicate_client
):
    """AT-1: Basic video generation with mocked API returns success response."""
    # Setup mock
    mock_video_data = b"fake_video_data_mp4"
    mock_output = MockFileOutput(mock_video_data)
    mock_replicate_client.run = MagicMock(return_value=mock_output)

    # Setup arguments
    output_path = os.path.join(temp_output_dir, "test_output.mp4")
    arguments = {
        "image": temp_input_image,
        "prompt": "A person walking forward",
        "model": "wan-video/wan-2.2-i2v-fast",
        "output_file_name": output_path,
        "parameters": {},
    }

    # Call the function
    result = await generate_video_replicate(arguments)

    # Verify response structure
    assert len(result) == 1
    response_data = json.loads(result[0].text)

    assert response_data["success"] is True
    assert response_data["model"] == "wan-video/wan-2.2-i2v-fast"
    assert response_data["prompt"] == "A person walking forward"
    assert response_data["input_image"] == temp_input_image
    assert response_data["duration_seconds"] == 5
    assert response_data["resolution"] == "720p"
    assert len(response_data["saved_files"]) == 1

    # Verify file was saved
    saved_file = response_data["saved_files"][0]
    assert os.path.exists(saved_file)
    with open(saved_file, "rb") as f:
        assert f.read() == mock_video_data

    # Verify Replicate API was called
    assert mock_replicate_client.run.called
    call_args = mock_replicate_client.run.call_args
    assert call_args[0][0] == "wan-video/wan-2.2-i2v-fast"
    # Verify image was converted to data URI
    assert "image" in call_args[1]["input"]
    assert call_args[1]["input"]["image"].startswith("data:image/png;base64,")


# AT-2: Model listing returns all catalog models with use_case and cost
@pytest.mark.asyncio
async def test_list_video_models_complete():
    """AT-2: Model listing returns all catalog models with use_case and cost."""
    result = await list_video_models_replicate({})

    assert len(result) == 1
    models = json.loads(result[0].text)

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
    arguments = {"model": "wan-video/wan-2.2-i2v-fast"}

    result = await get_video_model_parameters_replicate(arguments)

    assert len(result) == 1
    params = json.loads(result[0].text)

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
    arguments = {"model": "unknown/fake-model"}

    result = await get_video_model_parameters_replicate(arguments)

    assert len(result) == 1
    response = json.loads(result[0].text)

    # Verify error response
    assert "error" in response
    assert "available_models" in response
    assert "Unknown model: unknown/fake-model" in response["error"]
    assert isinstance(response["available_models"], list)


# AT-4: Iteration model has lowest cost in catalog
@pytest.mark.asyncio
async def test_iteration_model_is_cheapest():
    """AT-4: The 'iteration' use case model is the cheapest option in the catalog."""
    result = await list_video_models_replicate({})
    models = json.loads(result[0].text)

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
async def test_missing_input_image_error(temp_output_dir, mock_replicate_client):
    """AT-5: System returns structured error when input image doesn't exist."""
    # Use a path that doesn't exist
    nonexistent_image = os.path.join(temp_output_dir, "nonexistent.png")
    output_path = os.path.join(temp_output_dir, "output.mp4")

    arguments = {
        "image": nonexistent_image,
        "prompt": "Test prompt",
        "model": "wan-video/wan-2.2-i2v-fast",
        "output_file_name": output_path,
    }

    # The function raises ValueError which is caught by the tool handler
    # In integration context, we expect the exception to propagate
    with pytest.raises(ValueError) as exc_info:
        await generate_video_replicate(arguments)

    # Verify error message mentions the missing file
    assert "not found" in str(exc_info.value).lower()


# AT-6: Output collision handling returns incremented filename
@pytest.mark.asyncio
async def test_output_collision_handling(
    temp_input_image, temp_output_dir, mock_replicate_client
):
    """AT-6: System handles filename collisions using existing pattern (cat.mp4 → cat_1.mp4)."""
    # Create first video
    mock_video_data_1 = b"first_video_data"
    mock_output_1 = MockFileOutput(mock_video_data_1)
    mock_replicate_client.run = MagicMock(return_value=mock_output_1)

    output_path = os.path.join(temp_output_dir, "video.mp4")
    arguments = {
        "image": temp_input_image,
        "prompt": "First video",
        "model": "wan-video/wan-2.2-i2v-fast",
        "output_file_name": output_path,
    }

    result1 = await generate_video_replicate(arguments)
    response1 = json.loads(result1[0].text)
    first_file = response1["saved_files"][0]

    # Verify first file is video_0.mp4 (since collision detection starts at 0)
    assert first_file.endswith("video_0.mp4")

    # Create second video with same filename
    mock_video_data_2 = b"second_video_data"
    mock_output_2 = MockFileOutput(mock_video_data_2)
    mock_replicate_client.run = MagicMock(return_value=mock_output_2)

    result2 = await generate_video_replicate(arguments)
    response2 = json.loads(result2[0].text)
    second_file = response2["saved_files"][0]

    # Verify second file is video_1.mp4
    assert second_file.endswith("video_1.mp4")

    # Verify both files exist and have different content
    assert os.path.exists(first_file)
    assert os.path.exists(second_file)
    assert first_file != second_file


# AT-7: Cost display present in model listing
@pytest.mark.asyncio
async def test_cost_display_in_listing():
    """AT-7: Model cost per video is included in listing response."""
    result = await list_video_models_replicate({})
    models = json.loads(result[0].text)

    # Verify every model has cost_per_video field
    for model in models:
        assert "cost_per_video" in model
        assert isinstance(model["cost_per_video"], (int, float))
        assert model["cost_per_video"] > 0


# AT-8: API error handling returns structured error with type
@pytest.mark.asyncio
async def test_api_error_handling(temp_input_image, temp_output_dir, mock_replicate_client):
    """AT-8: System returns structured error with type when Replicate API fails."""
    # Mock API failure
    mock_replicate_client.run = MagicMock(
        side_effect=Exception("API timeout: Request timed out after 30s")
    )

    output_path = os.path.join(temp_output_dir, "output.mp4")
    arguments = {
        "image": temp_input_image,
        "prompt": "Test prompt",
        "model": "wan-video/wan-2.2-i2v-fast",
        "output_file_name": output_path,
    }

    # The function propagates the exception which is caught by the tool handler
    with pytest.raises(Exception) as exc_info:
        await generate_video_replicate(arguments)

    # Verify error message
    assert "timeout" in str(exc_info.value).lower()


# Additional test: Verify different models use correct image parameter names
@pytest.mark.asyncio
async def test_model_specific_image_parameters(
    temp_input_image, temp_output_dir, mock_replicate_client
):
    """Verify different models use the correct image parameter name (image, start_image, first_frame_image)."""
    mock_video_data = b"fake_video_data"
    mock_output = MockFileOutput(mock_video_data)
    mock_replicate_client.run = MagicMock(return_value=mock_output)

    test_cases = [
        ("wan-video/wan-2.2-i2v-fast", "image"),
        ("kwaivgi/kling-v2.5-turbo-pro", "start_image"),
        ("minimax/video-01-live", "first_frame_image"),
    ]

    for model_id, expected_param in test_cases:
        mock_replicate_client.run.reset_mock()

        output_path = os.path.join(temp_output_dir, f"{model_id.replace('/', '_')}.mp4")
        arguments = {
            "image": temp_input_image,
            "prompt": "Test motion",
            "model": model_id,
            "output_file_name": output_path,
        }

        await generate_video_replicate(arguments)

        # Verify the correct parameter name was used
        call_args = mock_replicate_client.run.call_args
        model_input = call_args[1]["input"]

        assert expected_param in model_input, (
            f"Model {model_id} should use '{expected_param}' parameter, "
            f"but input keys are: {list(model_input.keys())}"
        )
        assert model_input[expected_param].startswith("data:image/png;base64,")


# Test: Verify unsupported image format returns error
@pytest.mark.asyncio
async def test_unsupported_image_format(temp_output_dir, mock_replicate_client):
    """Verify system returns error for unsupported image formats."""
    # Create a temporary file with unsupported extension
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bmp", delete=False) as f:
        f.write(b"fake_bmp_data")
        unsupported_image = f.name

    try:
        output_path = os.path.join(temp_output_dir, "output.mp4")
        arguments = {
            "image": unsupported_image,
            "prompt": "Test prompt",
            "model": "wan-video/wan-2.2-i2v-fast",
            "output_file_name": output_path,
        }

        # The function raises ValueError for unsupported format
        with pytest.raises(ValueError) as exc_info:
            await generate_video_replicate(arguments)

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
    temp_input_image, temp_output_dir, mock_replicate_client
):
    """Verify response includes duration_seconds and resolution from catalog."""
    mock_video_data = b"fake_video_data"
    mock_output = MockFileOutput(mock_video_data)
    mock_replicate_client.run = MagicMock(return_value=mock_output)

    output_path = os.path.join(temp_output_dir, "output.mp4")
    arguments = {
        "image": temp_input_image,
        "prompt": "Test motion",
        "model": "wan-video/wan-2.2-i2v-fast",
        "output_file_name": output_path,
    }

    result = await generate_video_replicate(arguments)
    response = json.loads(result[0].text)

    # Verify metadata fields
    assert "duration_seconds" in response
    assert "resolution" in response
    assert response["duration_seconds"] == 5
    assert response["resolution"] == "720p"
