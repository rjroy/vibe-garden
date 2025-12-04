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
from typing import Any

import torch
from diffusers import AutoPipelineForText2Image

from wyrd_gen_mcp.generators.base import GenerationResult
from wyrd_gen_mcp.utils.file_utils import get_next_available_path, resolve_output_path

logger = logging.getLogger("wyrd-gen-mcp")


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
    ) -> GenerationResult:
        """Generate an image using a local model via diffusers.

        Args:
            prompt: The text prompt describing the image to generate
            model: The Hugging Face model ID to use
            output_file_name: File name to save the generated image
            parameters: Additional model-specific parameters

        Returns:
            GenerationResult with saved file paths

        Raises:
            ValueError: If required parameters are missing
        """
        logger.info("=" * 80)
        logger.info("LocalImageGenerator.generate called")
        logger.info(f"prompt={prompt}, model={model}, output_file_name={output_file_name}")

        if parameters is None:
            parameters = {}

        if not model:
            raise ValueError(
                "model is required - call list_image_models_local to see available models"
            )

        if not output_file_name:
            raise ValueError("output_file_name is required")

        abs_output_path = resolve_output_path(output_file_name, self._invoke_dir)

        logger.info(f"Loading model: {model}")
        try:
            device = self._get_device()
            logger.info(f"Target device: {device}")

            pipe = self._load_pipeline(model, device)
            pipe = self._apply_optimizations(pipe, device)

            # Generate image
            logger.info("Generating image...")
            image = pipe(prompt, **parameters).images[0]

            # Save image
            final_path, _ = get_next_available_path(abs_output_path)
            image.save(final_path)
            logger.info(f"Saved local image to: {final_path}")

            result = GenerationResult(
                success=True,
                model=model,
                prompt=prompt,
                saved_files=[final_path],
                parameters=parameters,
            )

            logger.info(f"Returning result: {result.to_dict()}")
            logger.info("=" * 80)
            return result

        except Exception as e:
            logger.exception("Error in local generation")
            raise e

    def _get_device(self) -> str:
        """Determine the best available device."""
        if not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU (will be slow)")
            return "cpu"
        return "cuda"

    def _load_pipeline(self, model: str, device: str) -> AutoPipelineForText2Image:
        """Load the diffusers pipeline."""
        return AutoPipelineForText2Image.from_pretrained(
            model,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
        )

    def _apply_optimizations(
        self, pipe: AutoPipelineForText2Image, device: str
    ) -> AutoPipelineForText2Image:
        """Apply memory optimizations to the pipeline."""
        if device == "cuda":
            logger.info("Enabling memory optimizations for GPU")
            try:
                pipe.enable_vae_tiling()
            except AttributeError:
                logger.warning("Pipeline does not support enable_vae_tiling")

            try:
                pipe.enable_attention_slicing(1)
            except AttributeError:
                logger.warning("Pipeline does not support enable_attention_slicing")

            try:
                pipe.enable_model_cpu_offload()
            except AttributeError:
                logger.warning(
                    "Pipeline does not support enable_model_cpu_offload, "
                    "moving to device manually"
                )
                pipe = pipe.to(device)
        else:
            pipe = pipe.to(device)

        return pipe
