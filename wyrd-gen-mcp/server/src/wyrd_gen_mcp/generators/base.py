"""Base classes and types for generators."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenerationResult:
    """Result of a generation operation."""

    success: bool
    model: str
    prompt: str
    saved_files: list[str]
    parameters: dict[str, Any] = field(default_factory=dict)

    # Video-specific fields
    input_image: str | None = None
    duration_seconds: int | None = None
    resolution: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
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
