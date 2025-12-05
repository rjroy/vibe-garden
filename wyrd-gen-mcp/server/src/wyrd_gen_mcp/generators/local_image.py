"""Local image generation using HuggingFace diffusers.

This module provides the LocalImageGenerator class for generating images
using locally-running diffusion models via the HuggingFace diffusers library.

Unlike Replicate-based generation, local generation:
- Requires a GPU with sufficient VRAM (varies by model, typically 4-24GB)
- Has no per-image cost (beyond electricity)
- May be slower depending on hardware
- Keeps data on-device (better for privacy)

The generator automatically:
- Detects CUDA availability and falls back to CPU if needed
- Applies memory optimizations (VAE tiling, attention slicing, CPU offload)
- Downloads models from HuggingFace Hub on first use
"""

import logging
import os
from typing import Any

import torch
from diffusers import AutoPipelineForText2Image

from wyrd_gen_mcp.exceptions import GenerationError, ValidationError
from wyrd_gen_mcp.generators.base import GenerationResult
from wyrd_gen_mcp.utils.file_utils import get_next_available_path, resolve_output_path
from wyrd_gen_mcp.utils.logging_utils import RequestContext

logger = logging.getLogger("wyrd-gen-mcp.generators.local_image")


class LocalImageGenerator:
    """Image generator using local HuggingFace diffusers models.

    This class runs diffusion models locally using the HuggingFace diffusers
    library. Models are downloaded from HuggingFace Hub on first use and
    cached locally.

    The generator applies memory optimizations automatically when using CUDA:
    - VAE tiling: Process image in tiles to reduce VRAM
    - Attention slicing: Compute attention in slices to reduce VRAM
    - Model CPU offload: Keep model weights on CPU, move to GPU as needed

    Attributes:
        _invoke_dir: Base directory for resolving relative output paths.

    Example:
        generator = LocalImageGenerator("/home/user/project")
        result = await generator.generate(
            prompt="A cyberpunk city at night",
            model="stabilityai/stable-diffusion-2-1",
            output_file_name="city.png",
            parameters={"num_inference_steps": 50}
        )
    """

    def __init__(self, invoke_dir: str):
        """Initialize the generator.

        Args:
            invoke_dir: Base directory for resolving relative output paths.
                When output_file_name is relative, it will be resolved against
                this directory.
        """
        self._invoke_dir = invoke_dir

    async def generate(
        self,
        prompt: str,
        model: str,
        output_file_name: str,
        parameters: dict[str, Any] | None = None,
        output_directory: str | None = None,
    ) -> GenerationResult:
        """Generate an image using a local model via diffusers.

        Args:
            prompt: The text prompt describing the image to generate
            model: The Hugging Face model ID to use
            output_file_name: File name to save the generated image
            parameters: Additional model-specific parameters
            output_directory: Directory to save the output file (overrides invoke_dir)

        Returns:
            GenerationResult with saved file paths

        Raises:
            ValidationError: If required parameters are missing.
            GenerationError: If model loading or image generation fails.
        """
        if parameters is None:
            parameters = {}

        # Validate inputs
        self._validate_inputs(model, output_file_name)

        # Truncate prompt for logging
        log_prompt = prompt[:100] + "..." if len(prompt) > 100 else prompt

        # Determine base directory for output
        # If output_directory is provided and absolute, use it directly
        # If output_directory is relative, resolve it against invoke_dir
        # If not provided, use invoke_dir
        if output_directory:
            if os.path.isabs(output_directory):
                base_dir = output_directory
            else:
                base_dir = os.path.join(self._invoke_dir, output_directory)
        else:
            base_dir = self._invoke_dir

        with RequestContext(
            operation="local_image_generation",
            logger=logger,
            model=model,
        ) as ctx:
            ctx.log_start(prompt=log_prompt, output=output_file_name)

            abs_output_path = resolve_output_path(output_file_name, base_dir)
            ctx.log_debug("Resolved output path", path=abs_output_path)

            try:
                device = self._get_device()
                ctx.log_progress(f"Using device: {device}")

                ctx.log_progress("Loading model (this may take a while on first run)")
                pipe = self._load_pipeline(model, device, ctx)
                pipe = self._apply_optimizations(pipe, device, ctx)

                # Generate image
                ctx.log_progress("Generating image")
                image = pipe(prompt, **parameters).images[0]

                # Save image
                final_path, used_idx = get_next_available_path(abs_output_path)
                image.save(final_path)
                ctx.log_progress("Saved image", path=final_path, index=used_idx)

                result = GenerationResult(
                    success=True,
                    model=model,
                    prompt=prompt,
                    saved_files=[final_path],
                    parameters=parameters,
                )

                ctx.log_success(saved_file=final_path)
                return result

            except (ValidationError, GenerationError):
                raise  # Re-raise with original context
            except Exception as e:
                ctx.log_error(e)
                raise GenerationError(
                    "Local image generation failed",
                    operation="local_generation",
                    model=model,
                    prompt=prompt,
                    cause=e,
                )

    def _validate_inputs(self, model: str, output_file_name: str) -> None:
        """Validate required inputs.

        Args:
            model: The model ID to validate.
            output_file_name: The output file name to validate.

        Raises:
            ValidationError: If any required input is missing.
        """
        if not model:
            raise ValidationError(
                "model is required - call list_image_models_local to see available models",
                parameter="model",
            )

        if not output_file_name:
            raise ValidationError(
                "output_file_name is required",
                parameter="output_file_name",
            )

    def _get_device(self) -> str:
        """Determine the best available device."""
        if not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU (will be slow)")
            return "cpu"
        return "cuda"

    def _load_pipeline(
        self,
        model: str,
        device: str,
        ctx: RequestContext,
    ) -> AutoPipelineForText2Image:
        """Load the diffusers pipeline.

        Args:
            model: HuggingFace model ID.
            device: Target device ("cuda" or "cpu").
            ctx: Request context for logging.

        Returns:
            Loaded pipeline ready for inference.

        Raises:
            GenerationError: If model loading fails.
        """
        try:
            pipe = AutoPipelineForText2Image.from_pretrained(
                model,
                torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                low_cpu_mem_usage=True,
            )
            ctx.log_debug("Model loaded successfully")
            return pipe
        except Exception as e:
            ctx.log_error(e)
            raise GenerationError(
                f"Failed to load model: {model}",
                operation="load_model",
                model=model,
                cause=e,
            )

    def _apply_optimizations(
        self,
        pipe: AutoPipelineForText2Image,
        device: str,
        ctx: RequestContext,
    ) -> AutoPipelineForText2Image:
        """Apply memory optimizations to the pipeline.

        Args:
            pipe: The loaded pipeline.
            device: Target device ("cuda" or "cpu").
            ctx: Request context for logging.

        Returns:
            Pipeline with optimizations applied.
        """
        if device == "cuda":
            ctx.log_debug("Enabling memory optimizations for GPU")
            try:
                pipe.enable_vae_tiling()
                ctx.log_debug("Enabled VAE tiling")
            except AttributeError:
                ctx.log_debug("Pipeline does not support enable_vae_tiling")

            try:
                pipe.enable_attention_slicing(1)
                ctx.log_debug("Enabled attention slicing")
            except AttributeError:
                ctx.log_debug("Pipeline does not support enable_attention_slicing")

            try:
                pipe.enable_model_cpu_offload()
                ctx.log_debug("Enabled model CPU offload")
            except AttributeError:
                ctx.log_warning(
                    "Pipeline does not support enable_model_cpu_offload, "
                    "moving to device manually"
                )
                pipe = pipe.to(device)
        else:
            pipe = pipe.to(device)

        return pipe
