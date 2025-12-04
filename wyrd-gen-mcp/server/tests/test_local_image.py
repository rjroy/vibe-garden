"""Tests for local image generation using HuggingFace diffusers.

This module tests the LocalImageGenerator class, which generates images
using locally-running diffusion models. Tests cover:
- GPU detection and CUDA device selection
- CPU fallback when CUDA is unavailable
- Pipeline loading and failure scenarios
- Memory optimizations (VAE tiling, attention slicing)
- Input validation
- Error handling
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock torch and diffusers before importing the module
# ruff: noqa: E402 - These imports must happen after mocking torch/diffusers
sys.modules['torch'] = MagicMock()
sys.modules['diffusers'] = MagicMock()

from wyrd_gen_mcp.exceptions import GenerationError, ValidationError
from wyrd_gen_mcp.generators.base import GenerationResult
from wyrd_gen_mcp.generators.local_image import LocalImageGenerator


class TestLocalImageGenerator:
    """Tests for LocalImageGenerator class."""

    @pytest.mark.asyncio
    @patch("wyrd_gen_mcp.generators.local_image.AutoPipelineForText2Image")
    @patch("wyrd_gen_mcp.generators.local_image.torch")
    async def test_generate_success_cuda(self, mock_torch, mock_pipeline_class, temp_dir):
        """Test successful image generation with CUDA available.

        Verifies:
        - CUDA device detection
        - Pipeline loading with float16
        - Image generation and saving
        - GenerationResult returned
        """
        # Setup CUDA availability
        mock_torch.cuda.is_available.return_value = True
        mock_torch.float16 = "float16"
        mock_torch.float32 = "float32"

        # Setup mock pipeline
        mock_pipe = MagicMock()
        mock_image = MagicMock()
        mock_pipe.return_value.images = [mock_image]
        mock_pipeline_class.from_pretrained.return_value = mock_pipe

        # Setup optimizations - these should be called
        mock_pipe.enable_vae_tiling = MagicMock()
        mock_pipe.enable_attention_slicing = MagicMock()
        mock_pipe.enable_model_cpu_offload = MagicMock()

        # Generate
        generator = LocalImageGenerator(temp_dir)
        result = await generator.generate(
            prompt="A cyberpunk city at night",
            model="stabilityai/stable-diffusion-2-1",
            output_file_name="city.png",
            parameters={"num_inference_steps": 50}
        )

        # Verify CUDA was checked
        mock_torch.cuda.is_available.assert_called_once()

        # Verify pipeline loaded with correct parameters
        mock_pipeline_class.from_pretrained.assert_called_once_with(
            "stabilityai/stable-diffusion-2-1",
            torch_dtype="float16",
            low_cpu_mem_usage=True
        )

        # Verify optimizations were applied
        mock_pipe.enable_vae_tiling.assert_called_once()
        mock_pipe.enable_attention_slicing.assert_called_once_with(1)
        mock_pipe.enable_model_cpu_offload.assert_called_once()

        # Verify image generation was called
        mock_pipe.assert_called_once_with(
            "A cyberpunk city at night",
            num_inference_steps=50
        )

        # Verify image was saved
        mock_image.save.assert_called_once()
        saved_path = mock_image.save.call_args[0][0]
        assert "city" in saved_path and saved_path.endswith(".png")

        # Verify result
        assert isinstance(result, GenerationResult)
        assert result.success is True
        assert result.model == "stabilityai/stable-diffusion-2-1"
        assert result.prompt == "A cyberpunk city at night"
        assert len(result.saved_files) == 1
        assert result.parameters == {"num_inference_steps": 50}

    @pytest.mark.asyncio
    @patch("wyrd_gen_mcp.generators.local_image.AutoPipelineForText2Image")
    @patch("wyrd_gen_mcp.generators.local_image.torch")
    async def test_generate_success_cpu_fallback(self, mock_torch, mock_pipeline_class, temp_dir):
        """Test successful generation when CUDA is unavailable (CPU fallback).

        Verifies:
        - CPU device selection when CUDA unavailable
        - Pipeline loaded with float32
        - No GPU optimizations applied
        - Pipeline moved to CPU device
        """
        # Setup: CUDA not available
        mock_torch.cuda.is_available.return_value = False
        mock_torch.float16 = "float16"
        mock_torch.float32 = "float32"

        # Setup mock pipeline
        mock_pipe = MagicMock()
        mock_image = MagicMock()
        mock_pipe.return_value.images = [mock_image]
        mock_pipe.to.return_value = mock_pipe  # to() returns self
        mock_pipeline_class.from_pretrained.return_value = mock_pipe

        # Generate
        generator = LocalImageGenerator(temp_dir)
        result = await generator.generate(
            prompt="A serene landscape",
            model="runwayml/stable-diffusion-v1-5",
            output_file_name="landscape.png"
        )

        # Verify CUDA check
        mock_torch.cuda.is_available.assert_called_once()

        # Verify pipeline loaded with float32 (CPU dtype)
        mock_pipeline_class.from_pretrained.assert_called_once_with(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype="float32",
            low_cpu_mem_usage=True
        )

        # Verify pipeline moved to CPU
        mock_pipe.to.assert_called_once_with("cpu")

        # Verify result
        assert result.success is True
        assert result.model == "runwayml/stable-diffusion-v1-5"

    @pytest.mark.asyncio
    @patch("wyrd_gen_mcp.generators.local_image.AutoPipelineForText2Image")
    @patch("wyrd_gen_mcp.generators.local_image.torch")
    async def test_pipeline_load_failure(self, mock_torch, mock_pipeline_class, temp_dir):
        """Test error handling when pipeline loading fails.

        Verifies:
        - from_pretrained exceptions are caught
        - GenerationError raised with context
        """
        # Setup CUDA
        mock_torch.cuda.is_available.return_value = True
        mock_torch.float16 = "float16"
        mock_torch.float32 = "float32"

        # Setup pipeline to fail
        mock_pipeline_class.from_pretrained.side_effect = RuntimeError(
            "Model not found or download failed"
        )

        # Generate and expect error
        generator = LocalImageGenerator(temp_dir)
        with pytest.raises(GenerationError) as exc_info:
            await generator.generate(
                prompt="Test prompt",
                model="nonexistent/model",
                output_file_name="test.png"
            )

        # Verify error details
        error = exc_info.value
        assert "Failed to load model" in error.message
        assert error.context["model"] == "nonexistent/model"
        assert error.context["operation"] == "load_model"
        assert isinstance(error.cause, RuntimeError)

    @pytest.mark.asyncio
    async def test_validate_missing_model(self, temp_dir):
        """Test validation error when model parameter is missing.

        Verifies:
        - ValidationError raised for empty model
        - Error message includes helpful guidance
        """
        generator = LocalImageGenerator(temp_dir)

        with pytest.raises(ValidationError) as exc_info:
            await generator.generate(
                prompt="Test prompt",
                model="",  # Empty model
                output_file_name="test.png"
            )

        error = exc_info.value
        assert "model is required" in error.message
        assert "list_image_models_local" in error.message
        assert error.context.get("parameter") == "model"

    @pytest.mark.asyncio
    async def test_validate_missing_output_file(self, temp_dir):
        """Test validation error when output_file_name is missing.

        Verifies:
        - ValidationError raised for empty output_file_name
        """
        generator = LocalImageGenerator(temp_dir)

        with pytest.raises(ValidationError) as exc_info:
            await generator.generate(
                prompt="Test prompt",
                model="stabilityai/stable-diffusion-2-1",
                output_file_name=""  # Empty output
            )

        error = exc_info.value
        assert "output_file_name is required" in error.message
        assert error.context.get("parameter") == "output_file_name"

    @pytest.mark.asyncio
    @patch("wyrd_gen_mcp.generators.local_image.AutoPipelineForText2Image")
    @patch("wyrd_gen_mcp.generators.local_image.torch")
    async def test_optimizations_applied(self, mock_torch, mock_pipeline_class, temp_dir):
        """Test that all memory optimizations are applied when using CUDA.

        Verifies:
        - enable_vae_tiling() called
        - enable_attention_slicing(1) called
        - enable_model_cpu_offload() called
        """
        # Setup CUDA
        mock_torch.cuda.is_available.return_value = True
        mock_torch.float16 = "float16"
        mock_torch.float32 = "float32"

        # Setup mock pipeline with all optimization methods
        mock_pipe = MagicMock()
        mock_image = MagicMock()
        mock_pipe.return_value.images = [mock_image]
        mock_pipeline_class.from_pretrained.return_value = mock_pipe

        # Track optimization calls
        mock_pipe.enable_vae_tiling = MagicMock()
        mock_pipe.enable_attention_slicing = MagicMock()
        mock_pipe.enable_model_cpu_offload = MagicMock()

        # Generate
        generator = LocalImageGenerator(temp_dir)
        await generator.generate(
            prompt="Test",
            model="test/model",
            output_file_name="test.png"
        )

        # Verify all optimizations called in order
        mock_pipe.enable_vae_tiling.assert_called_once()
        mock_pipe.enable_attention_slicing.assert_called_once_with(1)
        mock_pipe.enable_model_cpu_offload.assert_called_once()

    @pytest.mark.asyncio
    @patch("wyrd_gen_mcp.generators.local_image.AutoPipelineForText2Image")
    @patch("wyrd_gen_mcp.generators.local_image.torch")
    async def test_optimization_not_supported(self, mock_torch, mock_pipeline_class, temp_dir):
        """Test graceful handling when pipeline doesn't support optimizations.

        Verifies:
        - AttributeError caught for missing optimization methods
        - Generation continues without crash
        - Pipeline manually moved to device when CPU offload unavailable
        """
        # Setup CUDA
        mock_torch.cuda.is_available.return_value = True
        mock_torch.float16 = "float16"
        mock_torch.float32 = "float32"

        # Setup pipeline that doesn't support optimizations
        mock_pipe = MagicMock()
        mock_image = MagicMock()
        mock_pipe.return_value.images = [mock_image]
        mock_pipe.to.return_value = mock_pipe
        mock_pipeline_class.from_pretrained.return_value = mock_pipe

        # Remove optimization methods to simulate unsupported pipeline
        del mock_pipe.enable_vae_tiling
        del mock_pipe.enable_attention_slicing
        del mock_pipe.enable_model_cpu_offload

        # Generate - should not crash
        generator = LocalImageGenerator(temp_dir)
        result = await generator.generate(
            prompt="Test",
            model="test/model",
            output_file_name="test.png"
        )

        # Verify pipeline was moved to device manually
        # (since enable_model_cpu_offload was not available)
        mock_pipe.to.assert_called_once_with("cuda")

        # Verify generation succeeded
        assert result.success is True

    @pytest.mark.asyncio
    @patch("wyrd_gen_mcp.generators.local_image.AutoPipelineForText2Image")
    @patch("wyrd_gen_mcp.generators.local_image.torch")
    async def test_partial_optimization_support(self, mock_torch, mock_pipeline_class, temp_dir):
        """Test when pipeline supports some but not all optimizations.

        Verifies:
        - Supported optimizations are applied
        - Unsupported optimizations are skipped
        - Generation completes successfully
        """
        # Setup CUDA
        mock_torch.cuda.is_available.return_value = True
        mock_torch.float16 = "float16"
        mock_torch.float32 = "float32"

        # Setup pipeline with partial support
        mock_pipe = MagicMock()
        mock_image = MagicMock()
        mock_pipe.return_value.images = [mock_image]
        mock_pipe.to.return_value = mock_pipe
        mock_pipeline_class.from_pretrained.return_value = mock_pipe

        # Support only VAE tiling, not attention slicing or CPU offload
        mock_pipe.enable_vae_tiling = MagicMock()
        del mock_pipe.enable_attention_slicing
        del mock_pipe.enable_model_cpu_offload

        # Generate
        generator = LocalImageGenerator(temp_dir)
        result = await generator.generate(
            prompt="Test",
            model="test/model",
            output_file_name="test.png"
        )

        # Verify VAE tiling was called (supported)
        mock_pipe.enable_vae_tiling.assert_called_once()

        # Verify fallback to manual device move (CPU offload not supported)
        mock_pipe.to.assert_called_once_with("cuda")

        # Verify generation succeeded
        assert result.success is True

    @pytest.mark.asyncio
    @patch("wyrd_gen_mcp.generators.local_image.AutoPipelineForText2Image")
    @patch("wyrd_gen_mcp.generators.local_image.torch")
    async def test_generation_failure_wraps_exception(
        self, mock_torch, mock_pipeline_class, temp_dir
    ):
        """Test that generation failures are wrapped in GenerationError.

        Verifies:
        - Runtime errors during generation are caught
        - Wrapped in GenerationError with context
        """
        # Setup
        mock_torch.cuda.is_available.return_value = True
        mock_torch.float16 = "float16"
        mock_torch.float32 = "float32"

        mock_pipe = MagicMock()
        mock_pipe.enable_vae_tiling = MagicMock()
        mock_pipe.enable_attention_slicing = MagicMock()
        mock_pipe.enable_model_cpu_offload = MagicMock()
        mock_pipeline_class.from_pretrained.return_value = mock_pipe

        # Make generation fail
        mock_pipe.side_effect = RuntimeError("CUDA out of memory")

        # Generate and expect error
        generator = LocalImageGenerator(temp_dir)
        with pytest.raises(GenerationError) as exc_info:
            await generator.generate(
                prompt="Test prompt",
                model="test/model",
                output_file_name="test.png"
            )

        error = exc_info.value
        assert "Local image generation failed" in error.message
        assert error.context["operation"] == "local_generation"
        assert error.context["model"] == "test/model"
        assert error.context["prompt"] == "Test prompt"
        assert isinstance(error.cause, RuntimeError)
        assert "CUDA out of memory" in str(error.cause)
