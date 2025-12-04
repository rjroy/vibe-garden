"""Base classes and types for generators.

This module defines the common data structures used by all generator implementations.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenerationResult:
    """Result of a generation operation.

    This dataclass represents the outcome of an image or video generation request.
    It contains metadata about what was generated and where the output files are stored.

    Attributes:
        success: Whether the generation completed successfully.
        model: The model identifier used for generation (e.g., 'black-forest-labs/flux-schnell').
        prompt: The text prompt that was used to generate the content.
        saved_files: List of absolute paths to the generated output files.
            Files are named with incrementing indices (e.g., output_0.png, output_1.png).
        parameters: Additional model-specific parameters that were passed to the model.
        input_image: (Video only) Path to the input image used as the first frame.
        duration_seconds: (Video only) Duration of the generated video in seconds.
        resolution: (Video only) Resolution of the generated video (e.g., '720p').

    Example:
        result = GenerationResult(
            success=True,
            model="black-forest-labs/flux-schnell",
            prompt="A cat sitting on a windowsill",
            saved_files=["/output/cat_0.png"],
            parameters={"num_inference_steps": 4}
        )
    """

    success: bool
    model: str
    prompt: str
    saved_files: list[str]
    parameters: dict[str, Any] = field(default_factory=dict)

    # Video-specific fields (None for image generation)
    input_image: str | None = None
    duration_seconds: int | None = None
    resolution: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns a dictionary suitable for JSON serialization. Video-specific fields
        are only included if they have non-None values.

        Returns:
            Dictionary containing all generation result data.
        """
        result: dict[str, Any] = {
            "success": self.success,
            "model": self.model,
            "prompt": self.prompt,
            "saved_files": self.saved_files,
            "parameters": self.parameters,
        }
        if self.input_image is not None:
            result["input_image"] = self.input_image
        if self.duration_seconds is not None:
            result["duration_seconds"] = self.duration_seconds
        if self.resolution is not None:
            result["resolution"] = self.resolution
        return result
