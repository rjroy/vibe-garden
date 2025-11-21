#!/usr/bin/env python3
"""Wyrd-Gen MCP Server - AI image generation via Replicate."""

import asyncio
import json
import logging
import os
import sys
from typing import Any

import replicate
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

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
        name="generate_image",
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
                    "description": "The Replicate model to use (default: black-forest-labs/flux-schnell)",
                    "default": "black-forest-labs/flux-schnell",
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
            "required": ["prompt", "output_file_name"],
        },
    ),
    Tool(
        name="list_image_models",
        description="List popular image generation models available on Replicate with their descriptions",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="get_model_parameters",
        description="Get the available parameters for a specific image generation model",
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
]


async def generate_image(arguments: dict[str, Any]) -> list[TextContent]:
    """Generate an image using Replicate."""
    logger.info("=" * 80)
    logger.info("generate_image called")
    logger.info(f"Arguments: {json.dumps(arguments, indent=2)}")
    logger.info(f"Current working directory: {os.getcwd()}")

    prompt = arguments.get("prompt")
    model = arguments.get("model", "black-forest-labs/flux-schnell")
    output_file_name = arguments.get("output_file_name")
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


async def list_image_models(arguments: dict[str, Any]) -> list[TextContent]:
    """List popular image generation models."""
    logger.info("list_image_models called")
    return [TextContent(type="text", text=json.dumps(MODELS, indent=2))]


async def get_model_parameters(arguments: dict[str, Any]) -> list[TextContent]:
    """Get available parameters for a specific model."""
    logger.info(f"get_model_parameters called with model: {arguments.get('model')}")
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
            if name == "generate_image":
                return await generate_image(arguments)
            elif name == "list_image_models":
                return await list_image_models(arguments)
            elif name == "get_model_parameters":
                return await get_model_parameters(arguments)
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
