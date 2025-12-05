#!/usr/bin/env python3
"""Wyrd-Gen MCP Server - AI image and video generation via MCP protocol.

This module implements the MCP (Model Context Protocol) server that exposes
AI generation capabilities as tools. It acts as the entry point and orchestration
layer, delegating actual generation work to specialized generator classes.

Architecture:
    The server follows a clean separation of concerns:

    1. Server Layer (this file):
       - MCP tool registration and descriptions
       - Input validation and error handling
       - Progress reporting via MCP Context
       - JSON serialization of results

    2. Generator Layer (generators/):
       - ReplicateImageGenerator: Cloud-based image generation
       - ReplicateVideoGenerator: Cloud-based video generation with polling
       - LocalImageGenerator: On-device generation via diffusers

    3. Utility Layer (utils/):
       - File path resolution and collision avoidance
       - Image encoding for API submission
       - Async file downloads

Available MCP Tools:
    Image Generation (Replicate):
        - generate_image_replicate: Generate images using cloud models
        - list_image_models_replicate: List available Replicate models
        - get_model_parameters_replicate: Get model-specific parameters

    Image Generation (Local):
        - generate_image_local: Generate images using local GPU
        - list_image_models_local: List recommended local models
        - get_model_parameters_local: Get model-specific parameters

    Video Generation (Replicate):
        - generate_video_replicate: Generate video from image
        - list_video_models_replicate: List available video models
        - get_video_model_parameters_replicate: Get model parameters

Environment Variables:
    REPLICATE_API_TOKEN: Required. API token for Replicate.com
    WYRD_INVOKE_DIR: Optional. Base directory for relative path resolution.
        Defaults to current working directory.

Usage:
    Run as MCP server (stdio transport):
        python -m wyrd_gen_mcp.server

    Or via the installed command:
        wyrd-gen-mcp
"""

import json
import logging
import os
import sys
from typing import Any

import replicate
from mcp.server.fastmcp import Context, FastMCP

from wyrd_gen_mcp.data import (
    LOCAL_MODELS,
    LOCAL_PARAMETERS,
    MODELS,
    PARAMETERS,
    VIDEO_MODELS,
    VIDEO_PARAMETERS,
)
from wyrd_gen_mcp.generators import (
    LocalImageGenerator,
    ReplicateImageGenerator,
    ReplicateVideoGenerator,
)

# =============================================================================
# Module Initialization
# =============================================================================

# The invoke directory determines where relative output paths are resolved.
# This allows users to specify "output.png" and have it saved in their project
# directory, regardless of where the MCP server process is running.
INVOKE_DIR = os.environ.get("WYRD_INVOKE_DIR", os.getcwd())

# Configure file-based logging for debugging. The log file is created in the
# current working directory (not invoke directory) since that's where the
# server process runs.
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

# Initialize Replicate client (has both sync and async methods)
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)
logger.info("Replicate client initialized")

# Initialize generators
replicate_image_generator = ReplicateImageGenerator(replicate_client, INVOKE_DIR)
replicate_video_generator = ReplicateVideoGenerator(replicate_client, INVOKE_DIR)
local_image_generator = LocalImageGenerator(INVOKE_DIR)

# Create FastMCP server instance
mcp = FastMCP("wyrd-gen-mcp")


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
    output_directory: str | None = None,
) -> str:
    """Generate an image using Replicate.

    Args:
        prompt: The text prompt describing the image to generate
        model: The Replicate model to use. Call list_image_models_replicate for options.
        output_file_name: File name to save the generated image (e.g., 'my-image.png')
        parameters: Additional model-specific parameters
        output_directory: Directory to save the output file (overrides default invoke dir)
    """
    result = await replicate_image_generator.generate(
        prompt=prompt,
        model=model,
        output_file_name=output_file_name,
        parameters=parameters,
        output_directory=output_directory,
    )
    return json.dumps(result.to_dict(), indent=2)


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
    output_directory: str | None = None,
) -> str:
    """Generate an image using a local model via diffusers.

    Args:
        prompt: The text prompt describing the image to generate
        model: The Hugging Face model ID to use. Call list_image_models_local for options.
        output_file_name: File name to save the generated image (e.g., 'my-image.png')
        parameters: Additional model-specific parameters (num_inference_steps, etc.)
        output_directory: Directory to save the output file (overrides default invoke dir)
    """
    result = await local_image_generator.generate(
        prompt=prompt,
        model=model,
        output_file_name=output_file_name,
        parameters=parameters,
        output_directory=output_directory,
    )
    return json.dumps(result.to_dict(), indent=2)


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
    output_directory: str | None = None,
) -> str:
    """Generate a video using Replicate with async API, timeout, and progress reporting.

    Args:
        image: Path to input image file (PNG, JPG, JPEG, or WebP)
        prompt: Description of motion/action to apply to the image
        model: Replicate model ID. Call list_video_models_replicate for options.
        output_file_name: File name to save the generated video (e.g., 'output.mp4')
        ctx: FastMCP context for progress reporting (injected automatically)
        parameters: Optional model-specific parameters
        output_directory: Directory to save the output file (overrides default invoke dir)
    """

    async def progress_callback(
        progress: int, total: int | None, message: str
    ) -> None:
        await ctx.report_progress(progress=progress, total=total, message=message)

    result = await replicate_video_generator.generate(
        image=image,
        prompt=prompt,
        model=model,
        output_file_name=output_file_name,
        progress_callback=progress_callback,
        parameters=parameters,
        output_directory=output_directory,
    )
    return json.dumps(result.to_dict(), indent=2)


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


def main() -> None:
    """Run the MCP server using stdio transport.

    This is the main entry point for the server. It starts the FastMCP
    server which communicates over stdin/stdout using the MCP protocol.

    The server runs indefinitely until the client disconnects or the
    process is terminated.
    """
    logger.info("Starting Wyrd-Gen MCP Server")
    print("Wyrd-Gen MCP Server running on stdio", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    logger.info("Main entry point - starting mcp.run()")
    main()
