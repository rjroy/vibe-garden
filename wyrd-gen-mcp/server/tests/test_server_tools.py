"""Unit tests for MCP tool functions in server.py.

This module tests the MCP tool functions exposed by the server, covering:
- generate_image_replicate: Success and validation error cases
- list_image_models_replicate: Returns catalog as JSON
- get_model_parameters_replicate: Known and unknown model cases
- generate_image_local: Success case
- list_image_models_local: Returns catalog as JSON
- get_model_parameters_local: Unknown model error case

The tests mock the module-level generator instances to avoid real API calls
or GPU operations.
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Ensure src directory is in path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wyrd_gen_mcp.exceptions import ValidationError
from wyrd_gen_mcp.generators.base import GenerationResult


class TestImageReplicateTools:
    """Test suite for Replicate image generation MCP tools."""

    @pytest.mark.asyncio
    async def test_generate_image_replicate_success(self, temp_dir):
        """Test generate_image_replicate returns valid JSON with success fields."""
        from wyrd_gen_mcp.server import generate_image_replicate

        # Mock the module-level generator instance
        with patch("wyrd_gen_mcp.server.replicate_image_generator") as mock_gen:
            # Setup mock result
            mock_result = GenerationResult(
                success=True,
                model="black-forest-labs/flux-schnell",
                prompt="A beautiful sunset",
                saved_files=[f"{temp_dir}/sunset_0.png"],
                parameters={"num_inference_steps": 4},
            )
            mock_gen.generate = AsyncMock(return_value=mock_result)

            # Call the tool function
            result_json = await generate_image_replicate(
                prompt="A beautiful sunset",
                model="black-forest-labs/flux-schnell",
                output_file_name="sunset.png",
                parameters={"num_inference_steps": 4},
            )

            # Parse and verify response
            result = json.loads(result_json)
            assert result["success"] is True
            assert result["model"] == "black-forest-labs/flux-schnell"
            assert result["prompt"] == "A beautiful sunset"
            assert "saved_files" in result
            assert len(result["saved_files"]) == 1
            assert result["parameters"] == {"num_inference_steps": 4}

            # Verify generator was called correctly
            mock_gen.generate.assert_called_once_with(
                prompt="A beautiful sunset",
                model="black-forest-labs/flux-schnell",
                output_file_name="sunset.png",
                parameters={"num_inference_steps": 4},
                output_directory=None,
            )

    @pytest.mark.asyncio
    async def test_generate_image_replicate_validation_error(self):
        """Test generate_image_replicate propagates validation errors."""
        from wyrd_gen_mcp.server import generate_image_replicate

        # Mock the module-level generator instance to raise ValidationError
        with patch("wyrd_gen_mcp.server.replicate_image_generator") as mock_gen:
            mock_gen.generate = AsyncMock(
                side_effect=ValidationError(
                    "Missing required parameter: model",
                    context={"parameter": "model"},
                )
            )

            # Verify the error is propagated
            with pytest.raises(ValidationError) as exc_info:
                await generate_image_replicate(
                    prompt="Test prompt",
                    model="",  # Empty model should cause validation error
                    output_file_name="output.png",
                )

            assert "model" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_list_image_models_replicate(self):
        """Test list_image_models_replicate returns catalog as JSON."""
        from wyrd_gen_mcp.server import list_image_models_replicate

        # Call the tool function
        result_json = await list_image_models_replicate()

        # Parse and verify response
        models = json.loads(result_json)
        assert isinstance(models, list)
        assert len(models) > 0

        # Verify first model has expected fields
        first_model = models[0]
        assert "model" in first_model
        assert "description" in first_model
        assert isinstance(first_model["model"], str)
        assert isinstance(first_model["description"], str)

    @pytest.mark.asyncio
    async def test_get_model_parameters_known_model(self):
        """Test get_model_parameters_replicate returns parameters for valid model."""
        from wyrd_gen_mcp.server import get_model_parameters_replicate

        # Call with a known model (using one from the catalog)
        result_json = await get_model_parameters_replicate(
            model="black-forest-labs/flux-schnell"
        )

        # Parse and verify response
        result = json.loads(result_json)
        assert "model" in result
        assert "parameters" in result
        assert result["model"] == "black-forest-labs/flux-schnell"
        assert isinstance(result["parameters"], dict)

    @pytest.mark.asyncio
    async def test_get_model_parameters_unknown_model(self):
        """Test get_model_parameters_replicate returns error with available models."""
        from wyrd_gen_mcp.server import get_model_parameters_replicate

        # Call with unknown model
        result_json = await get_model_parameters_replicate(model="unknown/fake-model")

        # Parse and verify error response
        result = json.loads(result_json)
        assert "error" in result
        assert "available_models" in result
        assert "Unknown model: unknown/fake-model" in result["error"]
        assert isinstance(result["available_models"], list)
        assert len(result["available_models"]) > 0


class TestImageLocalTools:
    """Test suite for local image generation MCP tools."""

    @pytest.mark.asyncio
    async def test_generate_image_local_success(self, temp_dir):
        """Test generate_image_local returns valid JSON with success fields."""
        from wyrd_gen_mcp.server import generate_image_local

        # Mock the module-level generator instance
        with patch("wyrd_gen_mcp.server.local_image_generator") as mock_gen:
            # Setup mock result
            mock_result = GenerationResult(
                success=True,
                model="black-forest-labs/FLUX.1-schnell",
                prompt="A scenic landscape",
                saved_files=[f"{temp_dir}/landscape_0.png"],
                parameters={"num_inference_steps": 4},
            )
            mock_gen.generate = AsyncMock(return_value=mock_result)

            # Call the tool function
            result_json = await generate_image_local(
                prompt="A scenic landscape",
                model="black-forest-labs/FLUX.1-schnell",
                output_file_name="landscape.png",
                parameters={"num_inference_steps": 4},
            )

            # Parse and verify response
            result = json.loads(result_json)
            assert result["success"] is True
            assert result["model"] == "black-forest-labs/FLUX.1-schnell"
            assert result["prompt"] == "A scenic landscape"
            assert "saved_files" in result
            assert len(result["saved_files"]) == 1
            assert result["parameters"] == {"num_inference_steps": 4}

            # Verify generator was called correctly
            mock_gen.generate.assert_called_once_with(
                prompt="A scenic landscape",
                model="black-forest-labs/FLUX.1-schnell",
                output_file_name="landscape.png",
                parameters={"num_inference_steps": 4},
                output_directory=None,
            )

    @pytest.mark.asyncio
    async def test_list_image_models_local(self):
        """Test list_image_models_local returns catalog as JSON."""
        from wyrd_gen_mcp.server import list_image_models_local

        # Call the tool function
        result_json = await list_image_models_local()

        # Parse and verify response
        models = json.loads(result_json)
        assert isinstance(models, list)
        assert len(models) > 0

        # Verify first model has expected fields
        first_model = models[0]
        assert "model" in first_model
        assert "description" in first_model
        assert isinstance(first_model["model"], str)
        assert isinstance(first_model["description"], str)

    @pytest.mark.asyncio
    async def test_get_model_parameters_local_unknown(self):
        """Test get_model_parameters_local returns error for unknown local model."""
        from wyrd_gen_mcp.server import get_model_parameters_local

        # Call with unknown model
        result_json = await get_model_parameters_local(model="unknown/fake-local-model")

        # Parse and verify error response
        result = json.loads(result_json)
        assert "error" in result
        assert "available_models" in result
        assert "Unknown model: unknown/fake-local-model" in result["error"]
        assert isinstance(result["available_models"], list)
        assert len(result["available_models"]) > 0
