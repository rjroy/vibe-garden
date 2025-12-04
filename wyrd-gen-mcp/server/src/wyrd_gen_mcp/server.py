#!/usr/bin/env python3
"""Wyrd-Gen MCP Server - AI image generation via Replicate."""

import asyncio
import base64
import json
import logging
import os
import sys
from typing import Any

import httpx
import replicate
import torch
from diffusers import AutoPipelineForText2Image
from mcp.server.fastmcp import Context, FastMCP

from wyrd_gen_mcp.data import (
    LOCAL_MODELS,
    LOCAL_PARAMETERS,
    MODELS,
    PARAMETERS,
    VIDEO_MODELS,
    VIDEO_PARAMETERS,
)

# Get the invoke directory (where the user ran the script from)
INVOKE_DIR = os.environ.get("WYRD_INVOKE_DIR", os.getcwd())

# Video generation timeout (10 minutes) - video models can take a long time
VIDEO_GENERATION_TIMEOUT_SECONDS = 600

# Set up logging to file
log_file = os.path.join(os.getcwd(), "wyrd-gen-mcp.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
    ],
)
logger = logging.getLogger("wyrd-gen-mcp")
logger.info(f"Logging to {log_file}")
logger.info(f"Invoke directory: {INVOKE_DIR}")
logger.info(f"Current working directory: {os.getcwd()}")

# Environment validation
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    logger.error("REPLICATE_API_TOKEN environment variable is required")
    print("Error: REPLICATE_API_TOKEN environment variable is required", file=sys.stderr)
    sys.exit(1)

logger.info("REPLICATE_API_TOKEN found")

# Initialize Replicate clients (sync for simple ops, async for generation)
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)
async_replicate_client = replicate.AsyncClient(api_token=REPLICATE_API_TOKEN)
logger.info("Replicate clients initialized (sync + async)")

# Create FastMCP server instance
mcp = FastMCP("wyrd-gen-mcp")


def image_to_data_uri(file_path: str) -> str:
    """Convert local image file to base64 data URI for Replicate API submission.

    Args:
        file_path: Path to local image file (PNG, JPG, JPEG, or WebP)

    Returns:
        Data URI string in format: data:image/{format};base64,{encoded_data}

    Raises:
        FileNotFoundError: When the image file doesn't exist
        ValueError: When the image format is not supported
    """
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input image not found: {file_path}")

    # Validate and map file extension to MIME type
    ext = os.path.splitext(file_path)[1].lower()

    # Map extensions to MIME types
    mime_type_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }

    if ext not in mime_type_map:
        supported = ", ".join(mime_type_map.keys())
        raise ValueError(f"Unsupported image format: {ext}. Supported formats: {supported}")

    mime_type = mime_type_map[ext]

    # Read and encode the image
    try:
        with open(file_path, "rb") as f:
            image_data = f.read()
        encoded_data = base64.b64encode(image_data).decode("utf-8")
        return f"data:{mime_type};base64,{encoded_data}"
    except Exception as e:
        raise ValueError(f"Failed to read image file: {str(e)}")


def get_next_available_path(base_path: str, start_idx: int = 0) -> tuple[str, int]:
    """Find next available filename by checking existing files.

    Returns:
        tuple of (next_available_path, index_used)
    """
    name_parts = base_path.rsplit(".", 1)
    idx = start_idx
    while True:
        if len(name_parts) == 2:
            candidate = f"{name_parts[0]}_{idx}.{name_parts[1]}"
        else:
            candidate = f"{base_path}_{idx}"
        if not os.path.exists(candidate):
            return candidate, idx
        idx += 1


async def download_file(url: str, dest_path: str) -> int:
    """Download a file from URL to destination path.

    Returns:
        Number of bytes written
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(response.content)
        return len(response.content)


# =============================================================================
# Image Generation Tools - Replicate
# =============================================================================


@mcp.tool(
    description="Generate an image using AI models via Replicate. Supports various models "
    "including Flux, Stable Diffusion, and more. Pass model-specific parameters via the "
    "'parameters' object. Images are automatically saved to disk."
)
async def generate_image_replicate(
    prompt: str,
    model: str,
    output_file_name: str,
    parameters: dict[str, Any] | None = None,
) -> str:
    """Generate an image using Replicate.

    Args:
        prompt: The text prompt describing the image to generate
        model: The Replicate model to use. Call list_image_models_replicate for options.
        output_file_name: File name to save the generated image (e.g., 'my-image.png')
        parameters: Additional model-specific parameters
    """
    logger.info("=" * 80)
    logger.info("generate_image_replicate called")
    logger.info(f"prompt={prompt}, model={model}, output_file_name={output_file_name}")

    if parameters is None:
        parameters = {}

    if not model:
        raise ValueError(
            "model is required - call list_image_models_replicate to see available models"
        )

    if not output_file_name:
        raise ValueError("output_file_name is required")

    # Convert to absolute path using INVOKE_DIR as base for relative paths
    abs_output_path = output_file_name
    if not os.path.isabs(abs_output_path):
        abs_output_path = os.path.join(INVOKE_DIR, abs_output_path)
    abs_output_path = os.path.abspath(abs_output_path)
    logger.info(f"Output file name (absolute): {abs_output_path}")

    # Combine prompt with any additional parameters
    model_input = {"prompt": prompt, **parameters}
    logger.info(f"Model input: {json.dumps(model_input, indent=2)}")

    # Run the model using async client
    logger.info(f"Calling async_replicate_client.run with model: {model}")
    output = await async_replicate_client.run(model, input=model_input)
    logger.info("Replicate API call completed")
    logger.info(f"Output type: {type(output)}")

    # Process the output and save to disk
    saved_files = []

    if hasattr(output, "read"):
        logger.info("Processing FileOutput object with read() method")
        final_path, used_idx = get_next_available_path(abs_output_path)
        logger.info(f"Saving to file: {final_path} (index: {used_idx})")

        with open(final_path, "wb") as f:
            data = output.read()
            logger.info(f"Read {len(data)} bytes from output")
            f.write(data)

        saved_files.append(final_path)

    elif hasattr(output, "__iter__") and not isinstance(output, str):
        logger.info("Processing iterable output (multiple files)")
        start_offset = 0
        name_parts = abs_output_path.rsplit(".", 1)
        while True:
            if len(name_parts) == 2:
                check_path = f"{name_parts[0]}_{start_offset}.{name_parts[1]}"
            else:
                check_path = f"{abs_output_path}_{start_offset}"
            if not os.path.exists(check_path):
                break
            start_offset += 1

        for idx, item in enumerate(output):
            actual_idx = start_offset + idx
            if len(name_parts) == 2:
                file_path = f"{name_parts[0]}_{actual_idx}.{name_parts[1]}"
            else:
                file_path = f"{abs_output_path}_{actual_idx}"

            if hasattr(item, "read"):
                with open(file_path, "wb") as f:
                    data = item.read()
                    f.write(data)
            elif isinstance(item, bytes):
                with open(file_path, "wb") as f:
                    f.write(item)
            else:
                logger.warning(f"Unknown item type: {type(item)}")
                continue

            saved_files.append(file_path)
    else:
        logger.warning(f"Unexpected output type: {type(output)}, value: {output}")

    result = {
        "success": True,
        "model": model,
        "prompt": prompt,
        "saved_files": saved_files,
        "parameters": parameters,
    }

    logger.info(f"Returning result: {json.dumps(result, indent=2)}")
    logger.info("=" * 80)
    return json.dumps(result, indent=2)


@mcp.tool(
    description="List popular image generation models available on Replicate with their "
    "descriptions"
)
async def list_image_models_replicate() -> str:
    """List popular image generation models on Replicate."""
    logger.info("list_image_models_replicate called")
    return json.dumps(MODELS, indent=2)


@mcp.tool(
    description="Get the available parameters for a specific image generation model on Replicate"
)
async def get_model_parameters_replicate(model: str) -> str:
    """Get available parameters for a specific model on Replicate.

    Args:
        model: The Replicate model ID (e.g., 'google/imagen-4')
    """
    logger.info(f"get_model_parameters_replicate called with model: {model}")

    if model not in PARAMETERS:
        return json.dumps(
            {
                "error": f"Unknown model: {model}",
                "available_models": list(PARAMETERS.keys()),
            },
            indent=2,
        )

    return json.dumps(PARAMETERS[model], indent=2)


# =============================================================================
# Image Generation Tools - Local
# =============================================================================


@mcp.tool(
    description="Generate an image using a local model via the diffusers library. "
    "Requires a GPU with sufficient VRAM."
)
async def generate_image_local(
    prompt: str,
    model: str,
    output_file_name: str,
    parameters: dict[str, Any] | None = None,
) -> str:
    """Generate an image using a local model via diffusers.

    Args:
        prompt: The text prompt describing the image to generate
        model: The Hugging Face model ID to use. Call list_image_models_local for options.
        output_file_name: File name to save the generated image (e.g., 'my-image.png')
        parameters: Additional model-specific parameters (num_inference_steps, etc.)
    """
    logger.info("=" * 80)
    logger.info("generate_image_local called")
    logger.info(f"prompt={prompt}, model={model}, output_file_name={output_file_name}")

    if parameters is None:
        parameters = {}

    if not model:
        raise ValueError(
            "model is required - call list_image_models_local to see available models"
        )

    if not output_file_name:
        raise ValueError("output_file_name is required")

    # Path handling
    abs_output_path = output_file_name
    if not os.path.isabs(abs_output_path):
        abs_output_path = os.path.join(INVOKE_DIR, abs_output_path)
    abs_output_path = os.path.abspath(abs_output_path)

    logger.info(f"Loading model: {model}")
    try:
        # Determine device
        if not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU (will be slow)")
            device = "cpu"
        else:
            device = "cuda"

        logger.info(f"Target device: {device}")

        # Load pipeline with memory optimizations
        pipe = AutoPipelineForText2Image.from_pretrained(
            model,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
        )

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
                    "Pipeline does not support enable_model_cpu_offload, moving to device manually"
                )
                pipe = pipe.to(device)
        else:
            pipe = pipe.to(device)

        # Generate image
        logger.info("Generating image...")
        image = pipe(prompt, **parameters).images[0]

        # Save image
        final_path, _ = get_next_available_path(abs_output_path)
        image.save(final_path)
        logger.info(f"Saved local image to: {final_path}")

        result = {
            "success": True,
            "model": model,
            "prompt": prompt,
            "saved_files": [final_path],
            "parameters": parameters,
        }
        return json.dumps(result, indent=2)

    except Exception as e:
        logger.exception("Error in local generation")
        raise e


@mcp.tool(description="List recommended local image generation models compatible with diffusers")
async def list_image_models_local() -> str:
    """List recommended local image generation models."""
    logger.info("list_image_models_local called")
    return json.dumps(LOCAL_MODELS, indent=2)


@mcp.tool(description="Get the available parameters for a specific local image generation model")
async def get_model_parameters_local(model: str) -> str:
    """Get available parameters for a specific local model.

    Args:
        model: The Hugging Face model ID (e.g., 'black-forest-labs/FLUX.1-schnell')
    """
    logger.info(f"get_model_parameters_local called with model: {model}")

    if model not in LOCAL_PARAMETERS:
        return json.dumps(
            {
                "error": f"Unknown model: {model}",
                "available_models": list(LOCAL_PARAMETERS.keys()),
            },
            indent=2,
        )

    return json.dumps(LOCAL_PARAMETERS[model], indent=2)


# =============================================================================
# Video Generation Tools - Replicate
# =============================================================================


@mcp.tool(
    description="Generate a 5-second 720p MP4 video from an input image using AI models via "
    "Replicate. The input image becomes the first frame of the video. WARNING: Video generation "
    "typically takes 2-5 minutes and costs $0.10-$1.50+ per video depending on the model. "
    "ALWAYS ask the user for confirmation before each generation attempt due to cost and time. "
    "Do not retry automatically on failure."
)
async def generate_video_replicate(
    image: str,
    prompt: str,
    model: str,
    output_file_name: str,
    ctx: Context,
    parameters: dict[str, Any] | None = None,
) -> str:
    """Generate a video using Replicate with async API, timeout, and progress reporting.

    Args:
        image: Path to input image file (PNG, JPG, JPEG, or WebP)
        prompt: Description of motion/action to apply to the image
        model: Replicate model ID. Call list_video_models_replicate for options.
        output_file_name: File name to save the generated video (e.g., 'output.mp4')
        ctx: FastMCP context for progress reporting (injected automatically)
        parameters: Optional model-specific parameters
    """
    logger.info("=" * 80)
    logger.info("generate_video_replicate called")
    logger.info(f"image={image}, prompt={prompt}, model={model}")
    logger.info(f"Current working directory: {os.getcwd()}")

    if parameters is None:
        parameters = {}

    if not model:
        raise ValueError(
            "model is required - call list_video_models_replicate to see available models"
        )

    if not output_file_name:
        raise ValueError("output_file_name is required")

    if not image:
        raise ValueError("image is required")

    # Convert to absolute path using INVOKE_DIR as base for relative paths
    abs_output_path = output_file_name
    if not os.path.isabs(abs_output_path):
        abs_output_path = os.path.join(INVOKE_DIR, abs_output_path)
    abs_output_path = os.path.abspath(abs_output_path)
    logger.info(f"Output file name (absolute): {abs_output_path}")

    abs_image_path = image
    if not os.path.isabs(abs_image_path):
        abs_image_path = os.path.join(INVOKE_DIR, abs_image_path)
    abs_image_path = os.path.abspath(abs_image_path)
    logger.info(f"Input image (absolute): {abs_image_path}")

    # Validate and convert input image to data URI
    logger.info("Converting input image to data URI")
    try:
        image_data_uri = image_to_data_uri(abs_image_path)
        logger.info(f"Image conversion successful, data URI length: {len(image_data_uri)}")
    except FileNotFoundError as e:
        logger.error(f"Input image not found: {e}")
        raise ValueError(f"Input image not found: {abs_image_path}")
    except ValueError as e:
        logger.error(f"Input image validation failed: {e}")
        raise

    # Determine the correct parameter name for the input image based on the model
    model_params = VIDEO_PARAMETERS.get(model, {}).get("parameters", {})

    image_param_name = None
    for param_name, param_def in model_params.items():
        if param_def.get("type") == "string" and "image" in param_name.lower():
            if param_def.get("required"):
                image_param_name = param_name
                break

    if not image_param_name:
        if "kling" in model.lower():
            image_param_name = "start_image"
        elif "minimax" in model.lower() or "hailuo" in model.lower():
            image_param_name = "first_frame_image"
        else:
            image_param_name = "image"

    logger.info(f"Using image parameter name: {image_param_name}")

    # Build model input with the correct image parameter name
    model_input = {
        image_param_name: image_data_uri,
        "prompt": prompt,
        **parameters
    }
    logger.info(f"Model input keys: {list(model_input.keys())}")

    # Run the model using async API with timeout
    logger.info(f"Creating prediction with model: {model}")
    timeout_minutes = VIDEO_GENERATION_TIMEOUT_SECONDS // 60
    logger.info(f"Timeout: {VIDEO_GENERATION_TIMEOUT_SECONDS}s ({timeout_minutes} min)")

    # Progress reporting interval (seconds)
    progress_interval = 10

    prediction = None
    try:
        # Create the prediction using async client
        prediction = await async_replicate_client.predictions.create(
            model=model,
            input=model_input
        )
        logger.info(f"Prediction created: {prediction.id}")
        logger.info(f"Prediction status: {prediction.status}")

        # Report initial progress
        await ctx.report_progress(
            progress=0,
            total=None,
            message=f"Video generation started (prediction: {prediction.id})"
        )

        # Poll for completion with progress reporting
        start_time = asyncio.get_event_loop().time()
        poll_count = 0

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time

            # Check timeout
            if elapsed > VIDEO_GENERATION_TIMEOUT_SECONDS:
                raise asyncio.TimeoutError()

            # Reload prediction to get current status using async client
            prediction = await async_replicate_client.predictions.get(prediction.id)
            poll_count += 1

            logger.info(f"Poll {poll_count}: status={prediction.status}, elapsed={elapsed:.0f}s")

            # Report progress with elapsed time
            elapsed_min = int(elapsed // 60)
            elapsed_sec = int(elapsed % 60)
            await ctx.report_progress(
                progress=poll_count,
                total=None,
                message=f"Status: {prediction.status} ({elapsed_min}m {elapsed_sec}s elapsed)"
            )

            # Check if completed
            if prediction.status == "succeeded":
                logger.info("Prediction succeeded!")
                break
            elif prediction.status == "failed":
                error_msg = prediction.error or "Unknown error"
                logger.error(f"Prediction failed: {error_msg}")
                raise ValueError(f"Video generation failed: {error_msg}")
            elif prediction.status == "canceled":
                logger.error("Prediction was canceled")
                raise ValueError("Video generation was canceled")

            # Wait before next poll
            await asyncio.sleep(progress_interval)

        output = prediction.output
        logger.info(f"Prediction output: {output}")

        # Report completion
        await ctx.report_progress(
            progress=poll_count,
            total=poll_count,
            message="Video generation complete, downloading..."
        )

    except asyncio.TimeoutError:
        logger.error(f"Timed out after {VIDEO_GENERATION_TIMEOUT_SECONDS} seconds")
        if prediction:
            try:
                logger.info(f"Attempting to cancel prediction {prediction.id}")
                await async_replicate_client.predictions.cancel(prediction.id)
                logger.info("Prediction canceled successfully")
            except Exception as cancel_error:
                logger.warning(f"Failed to cancel prediction: {cancel_error}")
        raise ValueError(
            f"Video generation timed out after {timeout_minutes} minutes. "
            f"The prediction may still be running on Replicate's servers. "
            f"Check the Replicate dashboard for status."
        )

    logger.info(f"Output type: {type(output)}")
    logger.info(f"Output is string: {isinstance(output, str)}")

    # Process the output and save to disk
    saved_files = []

    if isinstance(output, str):
        # Single URL output
        logger.info(f"Processing single URL output: {output}")
        final_path, used_idx = get_next_available_path(abs_output_path)
        logger.info(f"Downloading to file: {final_path} (index: {used_idx})")

        try:
            bytes_written = await download_file(output, final_path)
            logger.info(f"Downloaded {bytes_written} bytes to {final_path}")
            saved_files.append(final_path)
        except httpx.HTTPError as e:
            logger.error(f"Failed to download video: {e}")
            raise ValueError(f"Failed to download video from {output}: {e}")

    elif hasattr(output, "read"):
        # FileOutput object (fallback for sync-style output)
        logger.info("Processing FileOutput object with read() method")
        final_path, used_idx = get_next_available_path(abs_output_path)

        with open(final_path, "wb") as f:
            data = output.read()
            logger.info(f"Read {len(data)} bytes from output")
            f.write(data)

        saved_files.append(final_path)

    elif hasattr(output, "__iter__") and not isinstance(output, (str, bytes)):
        logger.info("Processing iterable output (multiple files)")
        start_offset = 0
        name_parts = abs_output_path.rsplit(".", 1)
        while True:
            if len(name_parts) == 2:
                check_path = f"{name_parts[0]}_{start_offset}.{name_parts[1]}"
            else:
                check_path = f"{abs_output_path}_{start_offset}"
            if not os.path.exists(check_path):
                break
            start_offset += 1

        for idx, item in enumerate(output):
            actual_idx = start_offset + idx
            if len(name_parts) == 2:
                file_path = f"{name_parts[0]}_{actual_idx}.{name_parts[1]}"
            else:
                file_path = f"{abs_output_path}_{actual_idx}"

            if isinstance(item, str):
                try:
                    bytes_written = await download_file(item, file_path)
                    logger.info(f"Downloaded {bytes_written} bytes to {file_path}")
                except httpx.HTTPError as e:
                    logger.error(f"Failed to download video: {e}")
                    continue
            elif hasattr(item, "read"):
                with open(file_path, "wb") as f:
                    data = item.read()
                    f.write(data)
            elif isinstance(item, bytes):
                with open(file_path, "wb") as f:
                    f.write(item)
            else:
                logger.warning(f"Unknown item type: {type(item)}")
                continue

            saved_files.append(file_path)
    else:
        logger.warning(f"Unexpected output type: {type(output)}, value: {output}")

    # Get model metadata from catalog
    model_info = next((m for m in VIDEO_MODELS if m["model"] == model), {})
    duration = model_info.get("duration_seconds", 5)
    resolution = model_info.get("resolution", "720p")

    result = {
        "success": True,
        "model": model,
        "prompt": prompt,
        "input_image": abs_image_path,
        "saved_files": saved_files,
        "duration_seconds": duration,
        "resolution": resolution,
        "parameters": parameters,
    }

    logger.info(f"Returning result: {json.dumps(result, indent=2)}")
    logger.info("=" * 80)
    return json.dumps(result, indent=2)


@mcp.tool(
    description="List available video generation models on Replicate with use-case categorization "
    "and cost information. Review cost_per_video carefully before selecting a model - video "
    "generation is expensive ($0.10-$1.50+ per video) and slow (2-5 minutes per generation)."
)
async def list_video_models_replicate() -> str:
    """List available video generation models on Replicate."""
    logger.info("list_video_models_replicate called")
    return json.dumps(VIDEO_MODELS, indent=2)


@mcp.tool(
    description="Get available parameters for a specific video generation model. Remember: "
    "video generation takes 2-5 minutes and costs $0.10-$1.50+ per attempt. Always confirm "
    "with user before generating."
)
async def get_video_model_parameters_replicate(model: str) -> str:
    """Get available parameters for a specific video model on Replicate.

    Args:
        model: The Replicate model ID (e.g., 'kuaishou/kling-v2.5-pro')
    """
    logger.info(f"get_video_model_parameters_replicate called with model: {model}")

    if model not in VIDEO_PARAMETERS:
        return json.dumps(
            {
                "error": f"Unknown model: {model}",
                "available_models": list(VIDEO_PARAMETERS.keys()),
            },
            indent=2,
        )

    return json.dumps(VIDEO_PARAMETERS[model], indent=2)


# =============================================================================
# Main Entry Point
# =============================================================================


def main():
    """Run the MCP server."""
    logger.info("Starting Wyrd-Gen MCP Server")
    print("Wyrd-Gen MCP Server running on stdio", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    logger.info("Main entry point - starting mcp.run()")
    main()
