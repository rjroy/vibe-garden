"""Replicate-based video generation.

This module provides the ReplicateVideoGenerator class for generating videos
from input images using Replicate's cloud API. It supports image-to-video models
like Kling, Wan, and MiniMax.

The generator handles:
- Async prediction creation and polling with progress reporting
- Automatic timeout handling (default 10 minutes)
- Model-specific parameter naming (different models use different image param names)
- Multiple output formats (URLs, FileOutput objects, iterables)
- Path resolution and collision avoidance

Video generation is expensive ($0.10-$1.50+ per video) and slow (2-5 minutes),
so the generator supports progress callbacks to keep the user informed.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING, Any, Callable, Coroutine

if TYPE_CHECKING:
    from replicate import Client

from wyrd_gen_mcp.data import VIDEO_MODELS, VIDEO_PARAMETERS
from wyrd_gen_mcp.exceptions import (
    FileError,
    GenerationError,
    TimeoutError as WyrdTimeoutError,
    ValidationError,
)
from wyrd_gen_mcp.generators.base import GenerationResult
from wyrd_gen_mcp.utils.file_utils import (
    download_file,
    get_next_available_path,
    resolve_output_path,
)
from wyrd_gen_mcp.utils.image_utils import image_to_data_uri
from wyrd_gen_mcp.utils.logging_utils import RequestContext

logger = logging.getLogger("wyrd-gen-mcp.generators.replicate_video")

# Video generation timeout (10 minutes) - video models can take a long time
VIDEO_GENERATION_TIMEOUT_SECONDS = 600

# Progress reporting interval (seconds) - how often to poll and report status
PROGRESS_INTERVAL_SECONDS = 10

# Type alias for progress callback function signature
# Args: (progress_count, total_or_none, status_message)
ProgressCallback = Callable[[int, int | None, str], Coroutine[Any, Any, None]]


class ReplicateVideoGenerator:
    """Video generator using Replicate's cloud API.

    This class creates videos from input images using Replicate's image-to-video
    models. Unlike image generation which completes quickly, video generation
    requires polling for completion and can take several minutes.

    The generator uses Replicate's predictions API:
    1. Create a prediction with the model and inputs
    2. Poll for status until succeeded/failed/canceled
    3. Download the output video from the returned URL

    Different video models use different parameter names for the input image:
    - Kling models: 'start_image'
    - MiniMax/Hailuo models: 'first_frame_image'
    - Other models: 'image'

    Attributes:
        _client: The Replicate client instance for API calls.
        _invoke_dir: Base directory for resolving relative paths.

    Example:
        client = replicate.Client(api_token="...")
        generator = ReplicateVideoGenerator(client, "/home/user/project")

        async def on_progress(count, total, msg):
            print(f"Progress: {msg}")

        result = await generator.generate(
            image="input.png",
            prompt="A person walking forward",
            model="wan-video/wan-2.2-i2v-fast",
            output_file_name="output.mp4",
            progress_callback=on_progress
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
                API token. Uses predictions.async_create/async_get for video gen.
            invoke_dir: Base directory for resolving relative paths for both
                input images and output videos.
        """
        self._client = client
        self._invoke_dir = invoke_dir

    async def generate(
        self,
        image: str,
        prompt: str,
        model: str,
        output_file_name: str,
        progress_callback: ProgressCallback | None = None,
        parameters: dict[str, Any] | None = None,
        output_directory: str | None = None,
    ) -> GenerationResult:
        """Generate a video using Replicate.

        Args:
            image: Path to input image file
            prompt: Description of motion/action to apply to the image
            model: Replicate model ID
            output_file_name: File name to save the generated video
            progress_callback: Optional async callback for progress reporting
            parameters: Optional model-specific parameters
            output_directory: Directory to save the output file (overrides invoke_dir)

        Returns:
            GenerationResult with saved file paths

        Raises:
            ValidationError: If required parameters are missing or invalid.
            GenerationError: If video generation fails.
            FileError: If input image cannot be read or output cannot be saved.
            WyrdTimeoutError: If generation times out.
        """
        if parameters is None:
            parameters = {}

        # Validate inputs before starting
        self._validate_inputs(image, model, output_file_name)

        # Truncate prompt for logging
        log_prompt = prompt[:100] + "..." if len(prompt) > 100 else prompt

        # Determine base directory for output
        # If output_directory is provided and absolute, use it directly
        # If output_directory is relative, resolve it against invoke_dir
        # If not provided, use invoke_dir
        # Note: input image always resolves against invoke_dir
        if output_directory:
            if os.path.isabs(output_directory):
                output_base_dir = output_directory
            else:
                output_base_dir = os.path.join(self._invoke_dir, output_directory)
        else:
            output_base_dir = self._invoke_dir

        with RequestContext(
            operation="replicate_video_generation",
            logger=logger,
            model=model,
        ) as ctx:
            ctx.log_start(prompt=log_prompt, input_image=image, output=output_file_name)

            abs_output_path = resolve_output_path(output_file_name, output_base_dir)
            abs_image_path = resolve_output_path(image, self._invoke_dir)
            ctx.log_debug("Resolved paths", output=abs_output_path, input=abs_image_path)

            # Convert input image to data URI
            try:
                image_data_uri = self._convert_image(abs_image_path, ctx)
            except (FileError, ValidationError):
                raise  # Re-raise with original context
            except Exception as e:
                ctx.log_error(e)
                raise FileError(
                    "Failed to process input image",
                    path=abs_image_path,
                    operation="convert",
                    cause=e,
                )

            # Build model input
            model_input = self._build_model_input(model, image_data_uri, prompt, parameters)
            ctx.log_debug("Prepared model input", param_keys=list(model_input.keys()))

            # Run generation with progress reporting
            try:
                output = await self._run_with_progress(
                    model, model_input, progress_callback, ctx
                )
            except (GenerationError, WyrdTimeoutError):
                raise  # Re-raise with original context

            # Process output and save files
            try:
                saved_files = await self._process_output(output, abs_output_path, ctx)
            except FileError:
                raise
            except Exception as e:
                ctx.log_error(e)
                raise GenerationError(
                    "Failed to process and save video output",
                    operation="save_output",
                    model=model,
                    cause=e,
                )

            # Get model metadata from catalog
            model_info = next((m for m in VIDEO_MODELS if m["model"] == model), {})
            duration = model_info.get("duration_seconds", 5)
            resolution = model_info.get("resolution", "720p")

            result = GenerationResult(
                success=True,
                model=model,
                prompt=prompt,
                saved_files=saved_files,
                parameters=parameters,
                input_image=abs_image_path,
                duration_seconds=duration,
                resolution=resolution,
            )

            ctx.log_success(
                saved_files=len(saved_files),
                first_file=saved_files[0] if saved_files else None,
                duration=duration,
                resolution=resolution,
            )
            return result

    def _validate_inputs(self, image: str, model: str, output_file_name: str) -> None:
        """Validate required inputs.

        Args:
            image: Input image path (must be non-empty)
            model: Model ID (must be non-empty)
            output_file_name: Output file name (must be non-empty)

        Raises:
            ValidationError: If any required input is empty or None
        """
        if not model:
            raise ValidationError(
                "model is required - call list_video_models_replicate to see available models",
                parameter="model",
            )
        if not output_file_name:
            raise ValidationError(
                "output_file_name is required",
                parameter="output_file_name",
            )
        if not image:
            raise ValidationError(
                "image is required",
                parameter="image",
            )

    def _convert_image(self, abs_image_path: str, ctx: RequestContext) -> str:
        """Convert input image to base64 data URI for API submission.

        Replicate's API accepts images as data URIs (base64-encoded with MIME type).
        This method reads the image file and converts it to the required format.

        Args:
            abs_image_path: Absolute path to the input image file
            ctx: Request context for logging

        Returns:
            Data URI string (e.g., 'data:image/png;base64,...')

        Raises:
            FileError: If the image file doesn't exist or cannot be read.
            ValidationError: If the image format is not supported.
        """
        ctx.log_progress("Converting input image to data URI")
        # image_to_data_uri now raises FileError/ValidationError with context
        image_data_uri = image_to_data_uri(abs_image_path)
        ctx.log_debug("Image conversion successful", data_uri_length=len(image_data_uri))
        return image_data_uri

    def _build_model_input(
        self,
        model: str,
        image_data_uri: str,
        prompt: str,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """Build the model input dictionary with correct parameter names.

        Different video models expect the input image under different parameter names:
        - Kling models use 'start_image'
        - MiniMax/Hailuo models use 'first_frame_image'
        - Most other models use 'image'

        This method detects the correct parameter name from the model's parameter
        schema in VIDEO_PARAMETERS, falling back to heuristics based on model name.

        Args:
            model: The Replicate model ID
            image_data_uri: Base64-encoded image data URI
            prompt: The motion/action prompt
            parameters: Additional model-specific parameters

        Returns:
            Dictionary ready to pass to Replicate's prediction API
        """
        # Try to find the image parameter name from the model's schema
        model_params = VIDEO_PARAMETERS.get(model, {}).get("parameters", {})

        image_param_name = None
        for param_name, param_def in model_params.items():
            if param_def.get("type") == "string" and "image" in param_name.lower():
                if param_def.get("required"):
                    image_param_name = param_name
                    break

        # Fall back to heuristics based on model name if not found in schema
        if not image_param_name:
            if "kling" in model.lower():
                image_param_name = "start_image"
            elif "minimax" in model.lower() or "hailuo" in model.lower():
                image_param_name = "first_frame_image"
            else:
                image_param_name = "image"

        logger.info(f"Using image parameter name: {image_param_name}")

        return {
            image_param_name: image_data_uri,
            "prompt": prompt,
            **parameters,
        }

    async def _run_with_progress(
        self,
        model: str,
        model_input: dict[str, Any],
        progress_callback: ProgressCallback | None,
        ctx: RequestContext,
    ) -> Any:
        """Run prediction with progress reporting and timeout.

        Video generation is a long-running operation that requires:
        1. Creating a prediction request
        2. Polling until the prediction completes or times out
        3. Handling cancellation on timeout

        Progress is reported via the callback every PROGRESS_INTERVAL_SECONDS.

        Args:
            model: The Replicate model ID
            model_input: The input dictionary for the model
            progress_callback: Optional async callback for progress updates
            ctx: Request context for logging

        Returns:
            The prediction output (usually a URL to the generated video)

        Raises:
            GenerationError: If generation fails or is canceled.
            WyrdTimeoutError: If generation times out.
        """
        timeout_minutes = VIDEO_GENERATION_TIMEOUT_SECONDS // 60
        ctx.log_progress(
            "Creating prediction",
            timeout_seconds=VIDEO_GENERATION_TIMEOUT_SECONDS,
            timeout_minutes=timeout_minutes,
        )

        prediction = None
        prediction_id = None

        try:
            # Create prediction
            try:
                prediction = await self._client.predictions.async_create(
                    model=model, input=model_input
                )
                prediction_id = prediction.id
                ctx.log_progress(
                    "Prediction created",
                    prediction_id=prediction_id,
                    initial_status=prediction.status,
                )
            except Exception as e:
                ctx.log_error(e)
                raise GenerationError(
                    "Failed to create prediction",
                    operation="create_prediction",
                    model=model,
                    cause=e,
                )

            if progress_callback:
                await progress_callback(
                    0, None, f"Video generation started (prediction: {prediction_id})"
                )

            # Poll for completion
            start_time = asyncio.get_event_loop().time()
            poll_count = 0

            while True:
                elapsed = asyncio.get_event_loop().time() - start_time

                if elapsed > VIDEO_GENERATION_TIMEOUT_SECONDS:
                    raise asyncio.TimeoutError()

                try:
                    prediction = await self._client.predictions.async_get(prediction_id)
                except Exception as e:
                    ctx.log_warning("Failed to poll prediction status", error=str(e))
                    # Continue polling despite transient errors
                    await asyncio.sleep(PROGRESS_INTERVAL_SECONDS)
                    continue

                poll_count += 1
                ctx.log_debug(
                    f"Poll {poll_count}",
                    status=prediction.status,
                    elapsed_seconds=int(elapsed),
                )

                if progress_callback:
                    elapsed_min = int(elapsed // 60)
                    elapsed_sec = int(elapsed % 60)
                    await progress_callback(
                        poll_count,
                        None,
                        f"Status: {prediction.status} ({elapsed_min}m {elapsed_sec}s elapsed)",
                    )

                if prediction.status == "succeeded":
                    ctx.log_progress("Prediction succeeded", poll_count=poll_count)
                    break
                elif prediction.status == "failed":
                    error_msg = prediction.error or "Unknown error"
                    ctx.log_error(Exception(error_msg))
                    raise GenerationError(
                        f"Video generation failed: {error_msg}",
                        operation="video_generation",
                        model=model,
                        prediction_id=prediction_id,
                        replicate_error=error_msg,
                    )
                elif prediction.status == "canceled":
                    raise GenerationError(
                        "Video generation was canceled",
                        operation="video_generation",
                        model=model,
                        prediction_id=prediction_id,
                    )

                await asyncio.sleep(PROGRESS_INTERVAL_SECONDS)

            if progress_callback:
                await progress_callback(
                    poll_count, poll_count, "Video generation complete, downloading..."
                )

            return prediction.output

        except asyncio.TimeoutError:
            elapsed = asyncio.get_event_loop().time() - start_time if "start_time" in dir() else 0
            ctx.log_warning(
                "Generation timed out",
                timeout_seconds=VIDEO_GENERATION_TIMEOUT_SECONDS,
                elapsed_seconds=int(elapsed),
                prediction_id=prediction_id,
            )

            # Attempt to cancel the prediction
            if prediction_id:
                try:
                    ctx.log_progress("Attempting to cancel prediction", prediction_id=prediction_id)
                    await self._client.predictions.async_cancel(prediction_id)
                    ctx.log_progress("Prediction canceled successfully")
                except Exception as cancel_error:
                    ctx.log_warning("Failed to cancel prediction", error=str(cancel_error))

            raise WyrdTimeoutError(
                f"Video generation timed out after {timeout_minutes} minutes. "
                f"The prediction may still be running on Replicate's servers. "
                f"Check the Replicate dashboard for status.",
                timeout_seconds=VIDEO_GENERATION_TIMEOUT_SECONDS,
                elapsed_seconds=elapsed,
                model=model,
                prediction_id=prediction_id,
            )

    async def _process_output(
        self,
        output: Any,
        abs_output_path: str,
        ctx: RequestContext,
    ) -> list[str]:
        """Process Replicate output and save files.

        Video models typically return output as:
        1. String URL - download the video from this URL
        2. FileOutput object with read() method - read binary data directly
        3. Iterable of URLs or FileOutput objects - multiple outputs

        Args:
            output: The prediction output from Replicate
            abs_output_path: Absolute path template for output file
            ctx: Request context for logging

        Returns:
            List of absolute paths to saved video files

        Raises:
            FileError: If download or save fails.
        """
        ctx.log_debug("Processing output", output_type=type(output).__name__)

        saved_files: list[str] = []

        if isinstance(output, str):
            # Single URL output
            ctx.log_progress("Downloading video from URL")
            final_path, used_idx = get_next_available_path(abs_output_path)

            # download_file now raises FileError with context
            bytes_written = await download_file(output, final_path)
            ctx.log_progress(f"Downloaded video", path=final_path, bytes=bytes_written)
            saved_files.append(final_path)

        elif hasattr(output, "read"):
            # FileOutput object
            ctx.log_debug("Processing FileOutput object with read() method")
            final_path, _ = get_next_available_path(abs_output_path)

            try:
                with open(final_path, "wb") as f:
                    data = output.read()
                    f.write(data)
                ctx.log_progress(f"Saved video", path=final_path, bytes=len(data))
                saved_files.append(final_path)
            except OSError as e:
                raise FileError(
                    "Failed to save video file",
                    path=final_path,
                    operation="write",
                    cause=e,
                )

        elif hasattr(output, "__iter__") and not isinstance(output, (str, bytes)):
            ctx.log_debug("Processing iterable output (multiple files)")
            saved_files = await self._process_iterable_output(output, abs_output_path, ctx)

        else:
            ctx.log_warning(
                "Unexpected output type",
                output_type=type(output).__name__,
                output_value=str(output)[:200],
            )

        return saved_files

    async def _process_iterable_output(
        self,
        output: Any,
        abs_output_path: str,
        ctx: RequestContext,
    ) -> list[str]:
        """Process iterable output containing multiple files.

        Args:
            output: Iterable of URLs, FileOutput objects, or bytes
            abs_output_path: Absolute path template for output files
            ctx: Request context for logging

        Returns:
            List of absolute paths to saved files
        """
        saved_files: list[str] = []
        start_offset = self._find_start_offset(abs_output_path)
        name_parts = abs_output_path.rsplit(".", 1)

        for idx, item in enumerate(output):
            actual_idx = start_offset + idx
            if len(name_parts) == 2:
                file_path = f"{name_parts[0]}_{actual_idx}.{name_parts[1]}"
            else:
                file_path = f"{abs_output_path}_{actual_idx}"

            if isinstance(item, str):
                try:
                    bytes_written = await download_file(item, file_path)
                    ctx.log_debug(f"Downloaded file {idx + 1}", path=file_path, bytes=bytes_written)
                except FileError as e:
                    ctx.log_warning(f"Failed to download file {idx + 1}", error=str(e))
                    continue
            elif hasattr(item, "read"):
                try:
                    with open(file_path, "wb") as f:
                        data = item.read()
                        f.write(data)
                    ctx.log_debug(f"Saved file {idx + 1}", path=file_path, bytes=len(data))
                except OSError as e:
                    ctx.log_warning(f"Failed to save file {idx + 1}", error=str(e))
                    continue
            elif isinstance(item, bytes):
                try:
                    with open(file_path, "wb") as f:
                        f.write(item)
                    ctx.log_debug(f"Saved file {idx + 1}", path=file_path, bytes=len(item))
                except OSError as e:
                    ctx.log_warning(f"Failed to save file {idx + 1}", error=str(e))
                    continue
            else:
                ctx.log_warning(f"Unknown item type in output", item_type=type(item).__name__)
                continue

            saved_files.append(file_path)

        return saved_files

    def _find_start_offset(self, base_path: str) -> int:
        """Find the starting offset for indexed file names.

        Scans for existing files to avoid overwriting them.

        Args:
            base_path: Base file path template

        Returns:
            First available index where no file exists
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
