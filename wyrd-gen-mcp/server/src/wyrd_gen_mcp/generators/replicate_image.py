"""Replicate-based image generation."""

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
    """Image generator using Replicate API."""

    def __init__(
        self,
        client: Client,
        invoke_dir: str,
    ):
        """Initialize the generator.

        Args:
            client: Replicate client for API calls
            invoke_dir: Directory from which the server was invoked
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

        Args:
            output: The output from Replicate API
            abs_output_path: Absolute path for output file

        Returns:
            List of saved file paths
        """
        saved_files: list[str] = []

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
            logger.warning(f"Unexpected output type: {type(output)}, value: {output}")

        return saved_files

    def _find_start_offset(self, base_path: str) -> int:
        """Find the starting offset for indexed file names."""
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
        """Create an indexed file path."""
        name_parts = base_path.rsplit(".", 1)
        if len(name_parts) == 2:
            return f"{name_parts[0]}_{idx}.{name_parts[1]}"
        return f"{base_path}_{idx}"
