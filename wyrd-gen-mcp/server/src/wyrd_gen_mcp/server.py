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
                    "description": "The Replicate model to use (default: black-forest-labs/flux-kontext-pro)",
                    "default": "black-forest-labs/flux-kontext-pro",
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
    model = arguments.get("model", "black-forest-labs/flux-kontext-pro")
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

    # Process the output and save to disk
    saved_files = []

    # Check if output has read method (FileOutput object)
    if hasattr(output, "read"):
        logger.info("Processing FileOutput object with read() method")
        logger.info(f"Saving to file: {output_file_name}")

        with open(output_file_name, "wb") as f:
            data = output.read()
            logger.info(f"Read {len(data)} bytes from output")
            f.write(data)

        logger.info(f"File saved successfully: {output_file_name}")
        saved_files.append(output_file_name)

    elif hasattr(output, "__iter__") and not isinstance(output, str):
        logger.info("Processing iterable output (multiple files)")
        # Multiple file outputs - save with numbered suffixes
        for idx, item in enumerate(output):
            logger.info(f"Processing item {idx}: type={type(item)}")

            # Split filename and extension
            name_parts = output_file_name.rsplit(".", 1)
            if len(name_parts) == 2:
                file_path = f"{name_parts[0]}_{idx}.{name_parts[1]}"
            else:
                file_path = f"{output_file_name}_{idx}"

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

    # Model pricing verified 2025-10-17 from Replicate pricing pages
    # Source: https://replicate.com/pricing and individual model pages
    # Recommended: Check quarterly for pricing updates
    # Quality ratings (1-10) are subjective developer assessments
    # Cost-efficiency = quality / cost (higher is better value)
    popular_models = [
        # Premium Quality Models
        {
            "model": "bytedance/seedream-4",
            "description": "State-of-the-art model with excellent prompt following, visual quality, and output diversity. Supports up to 4096x4096 resolution.",
            "best_for": "High-resolution outputs, complex compositions, multi-reference generation, and when you need the absolute best quality",
            "cost": 0.03,
            "quality": 9,
            "cost_efficiency": 300.0,
        },
        {
            "model": "google/imagen-4",
            "description": "Google's latest text-to-image model with exceptional photorealism and ease of prompting.",
            "best_for": "Photorealistic images, marketing materials, professional content, product photography, and architectural visualizations",
            "cost": 0.04,
            "quality": 8,
            "cost_efficiency": 200.0,
        },
        {
            "model": "black-forest-labs/flux-kontext-pro",
            "description": "Strong prompt following and style control for both photoreal and illustrated outputs with character consistency.",
            "best_for": "Character consistency across multiple scenes, visual storytelling, in-context editing, and style preservation",
            "cost": 0.04,
            "quality": 7,
            "cost_efficiency": 175.0,
        },

        # FLUX Model Family
        {
            "model": "black-forest-labs/flux-1.1-pro-ultra",
            "description": "Premium FLUX model supporting up to 4MP resolution with excellent image quality and prompt adherence.",
            "best_for": "Ultra high-resolution professional work, detailed compositions, and when maximum quality is needed",
            "cost": 0.06,
            "quality": 8,
            "cost_efficiency": 133.33,
        },
        {
            "model": "black-forest-labs/flux-1.1-pro",
            "description": "Improved FLUX model with more consistent image quality and diversity. Great all-around choice.",
            "best_for": "General-purpose high-quality generation, complex scenes with fine details, creative content, and e-commerce visuals",
            "cost": 0.055,
            "quality": 7,
            "cost_efficiency": 127.27,
        },
        {
            "model": "black-forest-labs/flux-dev",
            "description": "Development version of FLUX with strong capabilities at a mid-tier price point.",
            "best_for": "Development work, experimentation, and when you need good quality without premium pricing",
            "cost": 0.03,
            "quality": 6,
            "cost_efficiency": 200.0,
        },
        {
            "model": "black-forest-labs/flux-schnell",
            "description": "Fastest FLUX model optimized for speed and cost. Great for rapid iteration and local development.",
            "best_for": "Rapid prototyping, high-volume generation, personal projects, and when speed matters most",
            "cost": 0.003,
            "quality": 5,
            "cost_efficiency": 1666.67,
        },

        # Ideogram Model Family (Excellent for Text)
        {
            "model": "ideogram-ai/ideogram-v3-quality",
            "description": "Highest quality Ideogram model with stunning realism and exceptional text rendering capabilities.",
            "best_for": "Professional designs with text, posters, advertisements, and when text legibility is critical",
            "cost": 0.09,
            "quality": 8,
            "cost_efficiency": 88.89,
        },
        {
            "model": "ideogram-ai/ideogram-v3-balanced",
            "description": "Optimal balance between speed, cost, and quality with excellent text rendering.",
            "best_for": "General text-heavy designs, balanced quality/speed needs, and iterative design work",
            "cost": 0.06,
            "quality": 7,
            "cost_efficiency": 116.67,
        },
        {
            "model": "ideogram-ai/ideogram-v3-turbo",
            "description": "Fast, creative generation with strong text rendering capabilities at an economical price.",
            "best_for": "Text-heavy designs, posters, graphic design, advertising materials, and rapid iterations with text overlays",
            "cost": 0.03,
            "quality": 6,
            "cost_efficiency": 200.0,
        },

        # Specialized Models
        {
            "model": "recraft-ai/recraft-v3",
            "description": "Versatile model capable of generating long texts and images in a wide variety of styles. SOTA on text-to-image benchmarks.",
            "best_for": "Multi-style generation, long text rendering, creative compositions, and style-flexible projects",
            "cost": 0.08,
            "quality": 7,
            "cost_efficiency": 87.5,
        },
        {
            "model": "recraft-ai/recraft-v3-svg",
            "description": "First major text-to-image model with high-quality SVG output capability. Perfect for scalable graphics.",
            "best_for": "Logos, icons, vector graphics, scalable designs, and when you need SVG format output",
            "cost": 0.08,
            "quality": 6,
            "cost_efficiency": 75.0,
        },
        {
            "model": "google/imagen-3-fast",
            "description": "Faster, more economical version of Imagen when price or speed are more important than final image quality.",
            "best_for": "Quick iterations, high-volume work, prototyping, and when good quality at lower cost is acceptable",
            "cost": 0.03,
            "quality": 6,
            "cost_efficiency": 200.0,
        },

        # Budget-Friendly Options
        {
            "model": "stability-ai/sdxl",
            "description": "Stable Diffusion XL - highly cost-effective open-source model with good quality for the price.",
            "best_for": "Budget-conscious projects, high-volume generation, experimentation, and learning",
            "cost": 0.004,
            "quality": 5,
            "cost_efficiency": 1250.0,
        },
        {
            "model": "bria/fibo",
            "description": "State-of-the-art open-source 8B parameter model with precise control via JSON-native prompting. Enterprise-focused with licensed training data.",
            "best_for": "Iterative refinement workflows, precise control over lighting/composition/color/camera, enterprise applications requiring rights-clear data, both text-to-image and image-to-image",
            "cost": 0.04,
            "quality": 7,
            "cost_efficiency": 175.0,
        },
    ]

    return [TextContent(type="text", text=json.dumps(popular_models, indent=2))]


async def get_model_parameters(arguments: dict[str, Any]) -> list[TextContent]:
    """Get available parameters for a specific model."""
    logger.info(f"get_model_parameters called with model: {arguments.get('model')}")
    model = arguments.get("model")

    # Model parameter definitions
    model_params = {
        "google/imagen-4": {
            "model": "google/imagen-4",
            "parameters": {
                "aspect_ratio": {
                    "type": "string",
                    "description": "Aspect ratio of the generated image",
                    "options": ["1:1", "3:4", "4:3", "9:16", "16:9"],
                    "default": "1:1",
                },
                "output_format": {
                    "type": "string",
                    "description": "Format of the output image",
                    "options": ["jpg", "png", "webp"],
                    "default": "jpg",
                },
                "safety_filter_level": {
                    "type": "string",
                    "description": "Level of safety filtering",
                    "options": ["block_most", "block_medium_and_above", "block_only_high"],
                    "default": "block_medium_and_above",
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Text describing what to exclude from the image",
                    "optional": True,
                },
            },
        },
        "black-forest-labs/flux-kontext-pro": {
            "model": "black-forest-labs/flux-kontext-pro",
            "parameters": {
                "input_image": {
                    "type": "string",
                    "description": "URL of input image for in-context editing",
                    "optional": True,
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": "Aspect ratio of the generated image",
                    "options": ["1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21", "match_input_image"],
                    "default": "1:1",
                },
                "output_format": {
                    "type": "string",
                    "description": "Format of the output image",
                    "options": ["jpg", "png", "webp"],
                    "default": "jpg",
                },
                "safety_tolerance": {
                    "type": "integer",
                    "description": "Safety tolerance level (1-5, higher is less restrictive)",
                    "range": [1, 5],
                    "default": 2,
                },
                "prompt_upsampling": {
                    "type": "boolean",
                    "description": "Whether to automatically enhance the prompt",
                    "default": False,
                },
            },
        },
        "black-forest-labs/flux-1.1-pro": {
            "model": "black-forest-labs/flux-1.1-pro",
            "parameters": {
                "width": {
                    "type": "integer",
                    "description": "Width of the generated image",
                    "range": [256, 1440],
                    "default": 1024,
                },
                "height": {
                    "type": "integer",
                    "description": "Height of the generated image",
                    "range": [256, 1440],
                    "default": 1024,
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": "Aspect ratio (overrides width/height if set)",
                    "options": ["1:1", "16:9", "21:9", "2:3", "3:2", "4:5", "5:4", "9:16", "9:21"],
                    "optional": True,
                },
                "output_format": {
                    "type": "string",
                    "description": "Format of the output image",
                    "options": ["jpg", "png", "webp"],
                    "default": "jpg",
                },
                "safety_tolerance": {
                    "type": "integer",
                    "description": "Safety tolerance level (1-5)",
                    "range": [1, 5],
                    "default": 2,
                },
                "prompt_upsampling": {
                    "type": "boolean",
                    "description": "Whether to automatically enhance the prompt",
                    "default": False,
                },
            },
        },
        "ideogram-ai/ideogram-v3-turbo": {
            "model": "ideogram-ai/ideogram-v3-turbo",
            "parameters": {
                "aspect_ratio": {
                    "type": "string",
                    "description": "Aspect ratio of the generated image",
                    "options": ["1:1", "16:10", "3:2", "4:3", "16:9", "10:16", "2:3", "3:4", "9:16"],
                    "default": "1:1",
                },
                "resolution": {
                    "type": "string",
                    "description": "Resolution setting",
                    "options": ["None"],
                    "default": "None",
                },
                "style_type": {
                    "type": "string",
                    "description": "Style preset type",
                    "options": ["None", "General", "Realistic", "Design", "3D", "Anime"],
                    "default": "None",
                },
                "style_preset": {
                    "type": "string",
                    "description": "Specific style preset",
                    "options": ["None"],
                    "default": "None",
                },
                "magic_prompt_option": {
                    "type": "string",
                    "description": "Magic prompt enhancement option",
                    "options": ["Auto", "On", "Off"],
                    "default": "Auto",
                },
            },
        },
        "bria/fibo": {
            "model": "bria/fibo",
            "parameters": {
                "aspect_ratio": {
                    "type": "string",
                    "description": "Aspect ratio of the generated image",
                    "options": ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9"],
                    "default": "1:1",
                },
                "image": {
                    "type": "string",
                    "description": "Input image URL for refinement/inspiration (optional for text-to-image, required for image-to-image)",
                    "optional": True,
                },
                "seed": {
                    "type": "integer",
                    "description": "Random seed for reproducible generation",
                    "optional": True,
                },
                "guidance_scale": {
                    "type": "integer",
                    "description": "How strongly the model follows the prompt (3-5, higher = stronger adherence)",
                    "range": [3, 5],
                    "optional": True,
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "Elements to avoid in the generated image",
                    "optional": True,
                },
                "structured_prompt": {
                    "type": "string",
                    "description": "JSON-formatted detailed prompt for precise control over lighting, composition, color, camera settings",
                    "optional": True,
                    "default": "",
                },
            },
        },
    }

    if model not in model_params:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": f"Unknown model: {model}",
                "available_models": list(model_params.keys()),
            }, indent=2)
        )]

    return [TextContent(type="text", text=json.dumps(model_params[model], indent=2))]


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
