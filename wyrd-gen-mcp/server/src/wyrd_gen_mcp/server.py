#!/usr/bin/env python3
"""Wyrd-Gen MCP Server - AI image generation via Replicate."""

import asyncio
import json
import logging
import os
import sys
from typing import Any

import replicate
import torch
from diffusers import AutoPipelineForText2Image, DiffusionPipeline
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from wyrd_gen_mcp.data import MODELS, PARAMETERS

# Get the invoke directory (where the user ran the script from)
INVOKE_DIR = os.environ.get("WYRD_INVOKE_DIR", os.getcwd())

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

# Initialize Replicate client
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)
logger.info("Replicate client initialized")

# Define available tools
TOOLS = [
    Tool(
        name="generate_image_replicate",
        description="Generate an image using AI models via Replicate. Supports various models including Flux, Stable Diffusion, and more. Pass model-specific parameters via the 'parameters' object. Images are automatically saved to disk.",
        inputSchema={
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The text prompt describing the image to generate",
                },
                "model": {
                    "type": "string",
                    "description": "The Replicate model to use. Call list_image_models_replicate to see available models and their use cases.",
                },
                "output_file_name": {
                    "type": "string",
                    "description": "File name to save the generated image (e.g., 'my-image.png'). Required.",
                },
                "parameters": {
                    "type": "object",
                    "description": "Additional model-specific parameters (e.g., aspect_ratio, output_format, safety_filter_level, input_image, width, height, num_outputs, etc.)",
                    "default": {},
                },
            },
            "required": ["prompt", "model", "output_file_name"],
        },
    ),
    Tool(
        name="list_image_models_replicate",
        description="List popular image generation models available on Replicate with their descriptions",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="get_model_parameters_replicate",
        description="Get the available parameters for a specific image generation model on Replicate",
        inputSchema={
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "The Replicate model ID (e.g., 'google/imagen-4')",
                },
            },
            "required": ["model"],
        },
    ),
    Tool(
        name="list_image_models_local",
        description="List recommended local image generation models compatible with diffusers",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="generate_image_local",
        description="Generate an image using a local model via the diffusers library. Requires a GPU with sufficient VRAM.",
        inputSchema={
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The text prompt describing the image to generate",
                },
                "model": {
                    "type": "string",
                    "description": "The Hugging Face model ID to use (default: runwayml/stable-diffusion-v1-5)",
                    "default": "runwayml/stable-diffusion-v1-5",
                },
                "output_file_name": {
                    "type": "string",
                    "description": "File name to save the generated image (e.g., 'my-image.png'). Required.",
                },
                "parameters": {
                    "type": "object",
                    "description": "Additional model-specific parameters (e.g., num_inference_steps, guidance_scale, height, width)",
                    "default": {},
                },
            },
            "required": ["prompt", "output_file_name"],
        },
    ),
]


async def generate_image_replicate(arguments: dict[str, Any]) -> list[TextContent]:
    """Generate an image using Replicate."""
    logger.info("=" * 80)
    logger.info("generate_image_replicate called")
    logger.info(f"Arguments: {json.dumps(arguments, indent=2)}")
    logger.info(f"Current working directory: {os.getcwd()}")

    prompt = arguments.get("prompt")
    model = arguments.get("model")
    output_file_name = arguments.get("output_file_name")

    if not model:
        logger.error("model is required but not provided")
        raise ValueError("model is required - call list_image_models_replicate to see available models")
    parameters = arguments.get("parameters", {})

    logger.info(f"Prompt: {prompt}")
    logger.info(f"Model: {model}")
    logger.info(f"Output file name (raw): {output_file_name}")
    logger.info(f"Parameters: {parameters}")

    if not output_file_name:
        logger.error("output_file_name is required but not provided")
        raise ValueError("output_file_name is required")

    # Convert to absolute path using INVOKE_DIR as base for relative paths
    if not os.path.isabs(output_file_name):
        output_file_name = os.path.join(INVOKE_DIR, output_file_name)
    output_file_name = os.path.abspath(output_file_name)
    logger.info(f"Output file name (absolute): {output_file_name}")

    # Combine prompt with any additional parameters
    model_input = {"prompt": prompt, **parameters}
    logger.info(f"Model input: {json.dumps(model_input, indent=2)}")

    # Run the model
    logger.info(f"Calling replicate_client.run with model: {model}")
    output = replicate_client.run(model, input=model_input)
    logger.info(f"Replicate API call completed")
    logger.info(f"Output type: {type(output)}")
    logger.info(f"Output has __iter__: {hasattr(output, '__iter__')}")
    logger.info(f"Output is string: {isinstance(output, str)}")
    logger.info(f"Output has read: {hasattr(output, 'read')}")
    logger.info(f"Output has url: {hasattr(output, 'url')}")
    logger.info(f"Output repr: {repr(output)}")

    # Helper function to find next available filename with index
    def get_next_available_path(base_path: str, start_idx: int = 0) -> tuple[str, int]:
        """Find next available filename by checking existing files.

        Returns:
            tuple of (next_available_path, index_used)
        """
        # Split filename and extension
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

    # Process the output and save to disk
    saved_files = []

    # Check if output has read method (FileOutput object)
    if hasattr(output, "read"):
        logger.info("Processing FileOutput object with read() method")

        # Find next available filename to prevent overwrites
        final_path, used_idx = get_next_available_path(output_file_name)
        logger.info(f"Saving to file: {final_path} (index: {used_idx})")

        with open(final_path, "wb") as f:
            data = output.read()
            logger.info(f"Read {len(data)} bytes from output")
            f.write(data)

        logger.info(f"File saved successfully: {final_path}")
        saved_files.append(final_path)

    elif hasattr(output, "__iter__") and not isinstance(output, str):
        logger.info("Processing iterable output (multiple files)")

        # Find the starting offset to prevent overwrites
        start_offset = 0
        name_parts = output_file_name.rsplit(".", 1)
        while True:
            if len(name_parts) == 2:
                check_path = f"{name_parts[0]}_{start_offset}.{name_parts[1]}"
            else:
                check_path = f"{output_file_name}_{start_offset}"

            if not os.path.exists(check_path):
                break
            start_offset += 1

        logger.info(f"Starting index offset: {start_offset}")

        # Multiple file outputs - save with numbered suffixes
        for idx, item in enumerate(output):
            actual_idx = start_offset + idx
            logger.info(f"Processing item {idx}: type={type(item)}, using index {actual_idx}")

            # Split filename and extension
            if len(name_parts) == 2:
                file_path = f"{name_parts[0]}_{actual_idx}.{name_parts[1]}"
            else:
                file_path = f"{output_file_name}_{actual_idx}"

            logger.info(f"Saving to file: {file_path}")

            if hasattr(item, "read"):
                # FileOutput object
                with open(file_path, "wb") as f:
                    data = item.read()
                    logger.info(f"Read {len(data)} bytes from item")
                    f.write(data)
            elif isinstance(item, bytes):
                # Direct bytes
                with open(file_path, "wb") as f:
                    f.write(item)
                logger.info(f"Wrote {len(item)} bytes to {file_path}")
            else:
                logger.warning(f"Unknown item type: {type(item)}")
                continue

            logger.info(f"File saved successfully: {file_path}")
            saved_files.append(file_path)

    else:
        logger.warning(f"Unexpected output type: {type(output)}, value: {output}")

    logger.info(f"Saved files: {saved_files}")

    result = {
        "success": True,
        "model": model,
        "prompt": prompt,
        "saved_files": saved_files,
        "parameters": parameters,
    }

    logger.info(f"Returning result: {json.dumps(result, indent=2)}")
    logger.info("=" * 80)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def list_image_models_replicate(arguments: dict[str, Any]) -> list[TextContent]:
    """List popular image generation models on Replicate."""
    logger.info("list_image_models_replicate called")
    return [TextContent(type="text", text=json.dumps(MODELS, indent=2))]


async def get_model_parameters_replicate(arguments: dict[str, Any]) -> list[TextContent]:
    """Get available parameters for a specific model on Replicate."""
    logger.info(f"get_model_parameters_replicate called with model: {arguments.get('model')}")
    model = arguments.get("model")

    if model not in PARAMETERS:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {
                        "error": f"Unknown model: {model}",
                        "available_models": list(PARAMETERS.keys()),
                    },
                    indent=2,
                ),
            )
        ]

    return [TextContent(type="text", text=json.dumps(PARAMETERS[model], indent=2))]


async def generate_image_local(arguments: dict[str, Any]) -> list[TextContent]:
    """Generate an image using a local model via diffusers."""
    logger.info("=" * 80)
    logger.info("generate_image_local called")
    logger.info(f"Arguments: {json.dumps(arguments, indent=2)}")

    prompt = arguments.get("prompt")
    model_id = arguments.get("model", "runwayml/stable-diffusion-v1-5")
    output_file_name = arguments.get("output_file_name")
    parameters = arguments.get("parameters", {})

    if not output_file_name:
        raise ValueError("output_file_name is required")

    # Path handling
    if not os.path.isabs(output_file_name):
        output_file_name = os.path.join(INVOKE_DIR, output_file_name)
    output_file_name = os.path.abspath(output_file_name)

    logger.info(f"Loading model: {model_id}")
    try:
        # Determine device - for offloading we generally want to start on CPU
        # but we check for CUDA availability to ensure we can eventually run there
        if not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU (will be slow)")
            device = "cpu"
        else:
            device = "cuda"

        logger.info(f"Target device: {device}")

        # Load pipeline with memory optimizations
        lower_id = model_id.lower()
        diffusion_class = AutoPipelineForText2Image
        extra_args = {}
        if "qwen" in lower_id:
            logger.info("Setting Qwen model with trust_remote_code=True")
            diffusion_class = DiffusionPipeline
            extra_args = {"trust_remote_code": True}
        logger.info(f"Loading diffusion model: {model_id}")
        # Use AutoPipelineForText2Image for better compatibility across model types
        pipe = diffusion_class.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            low_cpu_mem_usage=True,
            *extra_args,
        )

        if device == "cuda":
            logger.info("Enabling memory optimizations for GPU")
            # Enable VAE tiling to reduce memory usage during decoding
            # Note: Some pipelines might not support all optimizations, so we wrap in try/except
            try:
                pipe.enable_vae_tiling()
            except AttributeError:
                logger.warning("Pipeline does not support enable_vae_tiling")

            try:
                pipe.enable_attention_slicing(1)
            except AttributeError:
                logger.warning("Pipeline does not support enable_attention_slicing")

            # Enable model CPU offload - keeps models on CPU and moves to GPU only when needed
            # This is critical for 8GB VRAM cards
            try:
                pipe.enable_model_cpu_offload()
            except AttributeError:
                logger.warning(
                    "Pipeline does not support enable_model_cpu_offload, moving to device manually"
                )
                pipe = pipe.to(device)
        else:
            # For CPU only, just move to device
            pipe = pipe.to(device)

        # Generate image
        logger.info("Generating image...")
        image = pipe(prompt, **parameters).images[0]

        # Save image
        # Helper function to find next available filename with index
        def get_next_available_path(base_path: str, start_idx: int = 0) -> tuple[str, int]:
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

        final_path, _ = get_next_available_path(output_file_name)
        image.save(final_path)
        logger.info(f"Saved local image to: {final_path}")

        result = {
            "success": True,
            "model": model_id,
            "prompt": prompt,
            "saved_files": [final_path],
            "parameters": parameters,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.exception("Error in local generation")
        raise e


async def list_image_models_local(arguments: dict[str, Any]) -> list[TextContent]:
    """List recommended local image generation models."""
    logger.info("list_image_models_local called")
    local_models = [
        {
            "model": "black-forest-labs/FLUX.1-schnell",
            "description": "FLUX.1 Schnell - State of the art speed and quality.",
        },
        {
            "model": "Qwen/Qwen-Image",
            "description": "Qwen-Image - 20B parameter model, high quality text rendering. Requires high VRAM (24GB+ recommended).",
        },
    ]
    return [TextContent(type="text", text=json.dumps(local_models, indent=2))]


async def main():
    """Run the MCP server."""
    # Create server instance
    server = Server("wyrd-gen-mcp")

    # Register list_tools handler
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return TOOLS

    # Register call_tool handler
    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        logger.info(f"Tool called: {name}")
        logger.debug(f"Tool arguments: {arguments}")
        try:
            if name == "generate_image_replicate":
                return await generate_image_replicate(arguments)
            elif name == "list_image_models_replicate":
                return await list_image_models_replicate(arguments)
            elif name == "get_model_parameters_replicate":
                return await get_model_parameters_replicate(arguments)
            elif name == "generate_image_local":
                return await generate_image_local(arguments)
            elif name == "list_image_models_local":
                return await list_image_models_local(arguments)
            else:
                logger.error(f"Unknown tool: {name}")
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.exception(f"Error in tool {name}: {e}")
            error_result = {
                "success": False,
                "error": str(e),
            }
            return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    # Run the server
    logger.info("Starting Wyrd-Gen MCP Server")
    print("Wyrd-Gen MCP Server running on stdio", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        logger.info("stdio_server started, beginning server.run")
        await server.run(read_stream, write_stream, server.create_initialization_options())
        logger.info("Server run completed")


if __name__ == "__main__":
    logger.info("Main entry point - starting asyncio.run(main())")
    asyncio.run(main())
