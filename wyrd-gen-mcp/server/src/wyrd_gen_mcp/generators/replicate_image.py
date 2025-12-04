"""Replicate-based image generation.

This module provides the ReplicateImageGenerator class for generating images
using Replicate's cloud API. It supports various models including Flux,
Stable Diffusion, and other image generation models available on Replicate.

The generator handles:
- Async API calls to Replicate
- Multiple output formats (FileOutput objects, iterables, URLs)
- Automatic file naming with collision avoidance
- Path resolution relative to the invoke directory
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from replicate import Client

from wyrd_gen_mcp.generators.base import GenerationResult
from wyrd_gen_mcp.utils.file_utils import get_next_available_path, resolve_output_path

logger = logging.getLogger("wyrd-gen-mcp")


class ReplicateImageGenerator:
    """Image generator using Replicate's cloud API.

    This class wraps the Replicate API to provide a simple interface for
    generating images from text prompts. It handles the complexity of
    different model output formats and file saving.

    Attributes:
        _client: The Replicate client instance for API calls.
        _invoke_dir: Base directory for resolving relative output paths.

    Example:
        client = replicate.Client(api_token="...")
        generator = ReplicateImageGenerator(client, "/home/user/project")
        result = await generator.generate(
            prompt="A beautiful sunset",
            model="black-forest-labs/flux-schnell",
            output_file_name="sunset.png"
        )
    """

    def __init__(
        self,
        client: Client,
        invoke_dir: str,
    ):
        """Initialize the generator.

        Args:
            client: Replicate client instance. Must be configured with a valid
                API token. The client's async_run method will be used for generation.
            invoke_dir: Base directory for resolving relative output paths.
                When output_file_name is relative, it will be resolved against
                this directory.
        """
        self._client = client
        self._invoke_dir = invoke_dir

    async def generate(
        self,
        prompt: str,
        model: str,
        output_file_name: str,
        parameters: dict[str, Any] | None = None,
    ) -> GenerationResult:
        """Generate an image using Replicate.

        Args:
            prompt: The text prompt describing the image to generate
            model: The Replicate model to use
            output_file_name: File name to save the generated image
            parameters: Additional model-specific parameters

        Returns:
            GenerationResult with saved file paths

        Raises:
            ValueError: If required parameters are missing
        """
        logger.info("=" * 80)
        logger.info("ReplicateImageGenerator.generate called")
        logger.info(f"prompt={prompt}, model={model}, output_file_name={output_file_name}")

        if parameters is None:
            parameters = {}

        if not model:
            raise ValueError(
                "model is required - call list_image_models_replicate to see available models"
            )

        if not output_file_name:
            raise ValueError("output_file_name is required")

        abs_output_path = resolve_output_path(output_file_name, self._invoke_dir)
        logger.info(f"Output file name (absolute): {abs_output_path}")

        model_input = {"prompt": prompt, **parameters}
        logger.info(f"Model input: {model_input}")

        # Run the model using client's async method
        logger.info(f"Calling client.async_run with model: {model}")
        output = await self._client.async_run(model, input=model_input)
        logger.info("Replicate API call completed")
        logger.info(f"Output type: {type(output)}")

        saved_files = self._process_output(output, abs_output_path)

        result = GenerationResult(
            success=True,
            model=model,
            prompt=prompt,
            saved_files=saved_files,
            parameters=parameters,
        )

        logger.info(f"Returning result: {result.to_dict()}")
        logger.info("=" * 80)
        return result

    def _process_output(self, output: Any, abs_output_path: str) -> list[str]:
        """Process Replicate output and save files.

        Replicate models can return output in several formats:
        1. FileOutput object with a read() method - single file output
        2. Iterable of FileOutput objects - multiple files (e.g., batch generation)
        3. Iterable of bytes - raw binary data
        4. String URL - needs to be downloaded separately (not handled here)

        This method detects the output type and saves the files appropriately.

        Args:
            output: The output from Replicate API. Can be FileOutput, iterable,
                or other types depending on the model.
            abs_output_path: Absolute path template for output file. Files will
                be saved with incrementing indices (e.g., output_0.png, output_1.png).

        Returns:
            List of absolute paths to saved files.
        """
        saved_files: list[str] = []

        # Case 1: Single FileOutput object with read() method
        if hasattr(output, "read"):
            logger.info("Processing FileOutput object with read() method")
            final_path, used_idx = get_next_available_path(abs_output_path)
            logger.info(f"Saving to file: {final_path} (index: {used_idx})")

            with open(final_path, "wb") as f:
                data = output.read()
                logger.info(f"Read {len(data)} bytes from output")
                f.write(data)

            saved_files.append(final_path)

        # Case 2: Iterable of outputs (multiple files)
        elif hasattr(output, "__iter__") and not isinstance(output, str):
            logger.info("Processing iterable output (multiple files)")
            start_offset = self._find_start_offset(abs_output_path)

            for idx, item in enumerate(output):
                file_path = self._make_indexed_path(abs_output_path, start_offset + idx)

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
            # Unexpected format - log for debugging
            logger.warning(f"Unexpected output type: {type(output)}, value: {output}")

        return saved_files

    def _find_start_offset(self, base_path: str) -> int:
        """Find the starting offset for indexed file names.

        Scans for existing files with the naming pattern (e.g., output_0.png,
        output_1.png) and returns the next available index to avoid overwriting.

        Args:
            base_path: Base file path (e.g., '/path/to/output.png')

        Returns:
            The first available index where no file exists.
        """
        name_parts = base_path.rsplit(".", 1)
        start_offset = 0
        while True:
            if len(name_parts) == 2:
                check_path = f"{name_parts[0]}_{start_offset}.{name_parts[1]}"
            else:
                check_path = f"{base_path}_{start_offset}"
            if not os.path.exists(check_path):
                break
            start_offset += 1
        return start_offset

    def _make_indexed_path(self, base_path: str, idx: int) -> str:
        """Create an indexed file path from a base path.

        Converts 'output.png' + index 3 into 'output_3.png'.
        Handles paths without extensions as well.

        Args:
            base_path: Base file path (e.g., '/path/to/output.png')
            idx: Index number to insert before the extension

        Returns:
            Indexed file path (e.g., '/path/to/output_3.png')
        """
        name_parts = base_path.rsplit(".", 1)
        if len(name_parts) == 2:
            return f"{name_parts[0]}_{idx}.{name_parts[1]}"
        return f"{base_path}_{idx}"
