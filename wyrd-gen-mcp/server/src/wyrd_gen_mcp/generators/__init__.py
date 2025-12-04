"""Generator implementations for Wyrd-Gen MCP Server."""

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
