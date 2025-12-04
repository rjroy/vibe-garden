"""Generator implementations for Wyrd-Gen MCP Server.

This module provides generator classes for AI image and video generation:

- ReplicateImageGenerator: Generate images using Replicate's cloud API
- ReplicateVideoGenerator: Generate videos from images using Replicate's cloud API
- LocalImageGenerator: Generate images locally using HuggingFace diffusers

All generators return GenerationResult objects containing the generated file paths
and metadata about the generation.

Example usage:
    from wyrd_gen_mcp.generators import ReplicateImageGenerator, GenerationResult

    generator = ReplicateImageGenerator(client, invoke_dir="/path/to/output")
    result = await generator.generate(
        prompt="A sunset over mountains",
        model="black-forest-labs/flux-schnell",
        output_file_name="sunset.png"
    )
    print(result.saved_files)  # ['/path/to/output/sunset_0.png']
"""

from wyrd_gen_mcp.generators.base import GenerationResult
from wyrd_gen_mcp.generators.local_image import LocalImageGenerator
from wyrd_gen_mcp.generators.replicate_image import ReplicateImageGenerator
from wyrd_gen_mcp.generators.replicate_video import ReplicateVideoGenerator

__all__ = [
    "GenerationResult",
    "LocalImageGenerator",
    "ReplicateImageGenerator",
    "ReplicateVideoGenerator",
]
