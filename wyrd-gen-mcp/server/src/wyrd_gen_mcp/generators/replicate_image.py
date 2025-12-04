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

from wyrd_gen_mcp.exceptions import GenerationError, ValidationError
from wyrd_gen_mcp.generators.base import GenerationResult
from wyrd_gen_mcp.utils.file_utils import get_next_available_path, resolve_output_path
from wyrd_gen_mcp.utils.image_utils import detect_image_format, replace_extension
from wyrd_gen_mcp.utils.logging_utils import RequestContext

logger = logging.getLogger("wyrd-gen-mcp.generators.replicate_image")


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
            ValidationError: If required parameters are missing or invalid.
            GenerationError: If the Replicate API call fails.
        """
        if parameters is None:
            parameters = {}

        # Validate inputs before starting
        self._validate_inputs(model, output_file_name)

        # Truncate prompt for logging (keep full prompt for API)
        log_prompt = prompt[:100] + "..." if len(prompt) > 100 else prompt

        with RequestContext(
            operation="replicate_image_generation",
            logger=logger,
            model=model,
        ) as ctx:
            ctx.log_start(prompt=log_prompt, output=output_file_name)

            abs_output_path = resolve_output_path(output_file_name, self._invoke_dir)
            ctx.log_debug("Resolved output path", path=abs_output_path)

            model_input = {"prompt": prompt, **parameters}
            ctx.log_debug("Prepared model input", param_keys=list(model_input.keys()))

            # Call Replicate API with error handling
            try:
                ctx.log_progress("Calling Replicate API")
                output = await self._client.async_run(model, input=model_input)
                ctx.log_debug("API call completed", output_type=type(output).__name__)
            except Exception as e:
                ctx.log_error(e)
                raise GenerationError(
                    "Replicate API call failed",
                    operation="replicate_api_call",
                    model=model,
                    prompt=prompt,
                    cause=e,
                )

            # Process output and save files
            try:
                saved_files = self._process_output(output, abs_output_path, ctx)
            except Exception as e:
                ctx.log_error(e)
                raise GenerationError(
                    "Failed to process and save output",
                    operation="save_output",
                    model=model,
                    cause=e,
                )

            if not saved_files:
                ctx.log_warning("No files were saved from output")

            result = GenerationResult(
                success=True,
                model=model,
                prompt=prompt,
                saved_files=saved_files,
                parameters=parameters,
            )

            ctx.log_success(
                saved_files=len(saved_files),
                first_file=saved_files[0] if saved_files else None,
            )
            return result

    def _validate_inputs(self, model: str, output_file_name: str) -> None:
        """Validate required inputs.

        Args:
            model: The model ID to validate.
            output_file_name: The output file name to validate.

        Raises:
            ValidationError: If any required input is missing.
        """
        if not model:
            raise ValidationError(
                "model is required - call list_image_models_replicate to see available models",
                parameter="model",
            )

        if not output_file_name:
            raise ValidationError(
                "output_file_name is required",
                parameter="output_file_name",
            )

    def _process_output(
        self,
        output: Any,
        abs_output_path: str,
        ctx: RequestContext,
    ) -> list[str]:
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
            ctx: Request context for logging.

        Returns:
            List of absolute paths to saved files.
        """
        saved_files: list[str] = []

        # Case 1: Single FileOutput object with read() method
        if hasattr(output, "read"):
            ctx.log_debug("Processing FileOutput object with read() method")
            data = output.read()

            # Detect actual format and correct extension if needed
            actual_ext = detect_image_format(data)
            corrected_path = abs_output_path
            if actual_ext:
                requested_ext = os.path.splitext(abs_output_path)[1].lower()
                if requested_ext != actual_ext:
                    corrected_path = replace_extension(abs_output_path, actual_ext)
                    ctx.log_debug(
                        "Format mismatch - correcting extension",
                        requested=requested_ext,
                        actual=actual_ext,
                        corrected_path=corrected_path,
                    )

            final_path, used_idx = get_next_available_path(corrected_path)

            with open(final_path, "wb") as f:
                f.write(data)

            ctx.log_progress(f"Saved {len(data)} bytes", path=final_path, index=used_idx)
            saved_files.append(final_path)

        # Case 2: Iterable of outputs (multiple files)
        elif hasattr(output, "__iter__") and not isinstance(output, str):
            ctx.log_debug("Processing iterable output (multiple files)")

            # Collect all items first so we can detect format from first one
            items_data: list[bytes] = []
            for item in output:
                if hasattr(item, "read"):
                    items_data.append(item.read())
                elif isinstance(item, bytes):
                    items_data.append(item)
                else:
                    ctx.log_warning(f"Unknown item type in output", item_type=type(item).__name__)

            if not items_data:
                return saved_files

            # Detect format from first item and correct extension if needed
            corrected_path = abs_output_path
            actual_ext = detect_image_format(items_data[0])
            if actual_ext:
                requested_ext = os.path.splitext(abs_output_path)[1].lower()
                if requested_ext != actual_ext:
                    corrected_path = replace_extension(abs_output_path, actual_ext)
                    ctx.log_debug(
                        "Format mismatch - correcting extension",
                        requested=requested_ext,
                        actual=actual_ext,
                    )

            # Find starting offset once for the corrected path
            start_offset = self._find_start_offset(corrected_path)

            for idx, data in enumerate(items_data):
                file_path = self._make_indexed_path(corrected_path, start_offset + idx)

                with open(file_path, "wb") as f:
                    f.write(data)
                ctx.log_debug(f"Saved file {idx + 1}", path=file_path, bytes=len(data))
                saved_files.append(file_path)
        else:
            # Unexpected format - log for debugging
            ctx.log_warning(
                "Unexpected output type",
                output_type=type(output).__name__,
                output_value=str(output)[:200],
            )

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
