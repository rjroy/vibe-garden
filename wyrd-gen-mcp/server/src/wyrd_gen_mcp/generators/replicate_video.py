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

import httpx

if TYPE_CHECKING:
    from replicate import Client

from wyrd_gen_mcp.data import VIDEO_MODELS, VIDEO_PARAMETERS
from wyrd_gen_mcp.generators.base import GenerationResult
from wyrd_gen_mcp.utils.file_utils import (
    download_file,
    get_next_available_path,
    resolve_output_path,
)
from wyrd_gen_mcp.utils.image_utils import image_to_data_uri

logger = logging.getLogger("wyrd-gen-mcp")

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
    ) -> GenerationResult:
        """Generate a video using Replicate.

        Args:
            image: Path to input image file
            prompt: Description of motion/action to apply to the image
            model: Replicate model ID
            output_file_name: File name to save the generated video
            progress_callback: Optional async callback for progress reporting
            parameters: Optional model-specific parameters

        Returns:
            GenerationResult with saved file paths

        Raises:
            ValueError: If required parameters are missing or generation fails
        """
        logger.info("=" * 80)
        logger.info("ReplicateVideoGenerator.generate called")
        logger.info(f"image={image}, prompt={prompt}, model={model}")
        logger.info(f"Current working directory: {os.getcwd()}")

        if parameters is None:
            parameters = {}

        self._validate_inputs(image, model, output_file_name)

        abs_output_path = resolve_output_path(output_file_name, self._invoke_dir)
        abs_image_path = resolve_output_path(image, self._invoke_dir)
        logger.info(f"Output file name (absolute): {abs_output_path}")
        logger.info(f"Input image (absolute): {abs_image_path}")

        # Convert input image to data URI
        image_data_uri = self._convert_image(abs_image_path)

        # Build model input
        model_input = self._build_model_input(model, image_data_uri, prompt, parameters)
        logger.info(f"Model input keys: {list(model_input.keys())}")

        # Run generation with progress reporting
        output = await self._run_with_progress(model, model_input, progress_callback)

        # Process output and save files
        saved_files = await self._process_output(output, abs_output_path)

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

        logger.info(f"Returning result: {result.to_dict()}")
        logger.info("=" * 80)
        return result

    def _validate_inputs(self, image: str, model: str, output_file_name: str) -> None:
        """Validate required inputs.

        Args:
            image: Input image path (must be non-empty)
            model: Model ID (must be non-empty)
            output_file_name: Output file name (must be non-empty)

        Raises:
            ValueError: If any required input is empty or None
        """
        if not model:
            raise ValueError(
                "model is required - call list_video_models_replicate to see available models"
            )
        if not output_file_name:
            raise ValueError("output_file_name is required")
        if not image:
            raise ValueError("image is required")

    def _convert_image(self, abs_image_path: str) -> str:
        """Convert input image to base64 data URI for API submission.

        Replicate's API accepts images as data URIs (base64-encoded with MIME type).
        This method reads the image file and converts it to the required format.

        Args:
            abs_image_path: Absolute path to the input image file

        Returns:
            Data URI string (e.g., 'data:image/png;base64,...')

        Raises:
            ValueError: If the image file doesn't exist or has unsupported format
        """
        logger.info("Converting input image to data URI")
        try:
            image_data_uri = image_to_data_uri(abs_image_path)
            logger.info(f"Image conversion successful, data URI length: {len(image_data_uri)}")
            return image_data_uri
        except FileNotFoundError as e:
            logger.error(f"Input image not found: {e}")
            raise ValueError(f"Input image not found: {abs_image_path}")

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

        Returns:
            The prediction output (usually a URL to the generated video)

        Raises:
            ValueError: If generation fails, is canceled, or times out
        """
        timeout_minutes = VIDEO_GENERATION_TIMEOUT_SECONDS // 60
        logger.info(f"Creating prediction with model: {model}")
        logger.info(f"Timeout: {VIDEO_GENERATION_TIMEOUT_SECONDS}s ({timeout_minutes} min)")

        prediction = None
        try:
            prediction = await self._client.predictions.async_create(
                model=model, input=model_input
            )
            logger.info(f"Prediction created: {prediction.id}")
            logger.info(f"Prediction status: {prediction.status}")

            if progress_callback:
                await progress_callback(
                    0, None, f"Video generation started (prediction: {prediction.id})"
                )

            # Poll for completion
            start_time = asyncio.get_event_loop().time()
            poll_count = 0

            while True:
                elapsed = asyncio.get_event_loop().time() - start_time

                if elapsed > VIDEO_GENERATION_TIMEOUT_SECONDS:
                    raise asyncio.TimeoutError()

                prediction = await self._client.predictions.async_get(prediction.id)
                poll_count += 1

                logger.info(
                    f"Poll {poll_count}: status={prediction.status}, elapsed={elapsed:.0f}s"
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
                    logger.info("Prediction succeeded!")
                    break
                elif prediction.status == "failed":
                    error_msg = prediction.error or "Unknown error"
                    logger.error(f"Prediction failed: {error_msg}")
                    raise ValueError(f"Video generation failed: {error_msg}")
                elif prediction.status == "canceled":
                    logger.error("Prediction was canceled")
                    raise ValueError("Video generation was canceled")

                await asyncio.sleep(PROGRESS_INTERVAL_SECONDS)

            if progress_callback:
                await progress_callback(
                    poll_count, poll_count, "Video generation complete, downloading..."
                )

            return prediction.output

        except asyncio.TimeoutError:
            logger.error(f"Timed out after {VIDEO_GENERATION_TIMEOUT_SECONDS} seconds")
            if prediction:
                try:
                    logger.info(f"Attempting to cancel prediction {prediction.id}")
                    await self._client.predictions.async_cancel(prediction.id)
                    logger.info("Prediction canceled successfully")
                except Exception as cancel_error:
                    logger.warning(f"Failed to cancel prediction: {cancel_error}")
            raise ValueError(
                f"Video generation timed out after {timeout_minutes} minutes. "
                f"The prediction may still be running on Replicate's servers. "
                f"Check the Replicate dashboard for status."
            )

    async def _process_output(self, output: Any, abs_output_path: str) -> list[str]:
        """Process Replicate output and save files.

        Video models typically return output as:
        1. String URL - download the video from this URL
        2. FileOutput object with read() method - read binary data directly
        3. Iterable of URLs or FileOutput objects - multiple outputs

        Args:
            output: The prediction output from Replicate
            abs_output_path: Absolute path template for output file

        Returns:
            List of absolute paths to saved video files

        Raises:
            ValueError: If download fails
        """
        logger.info(f"Output type: {type(output)}")
        logger.info(f"Output is string: {isinstance(output, str)}")

        saved_files: list[str] = []

        if isinstance(output, str):
            # Single URL output
            logger.info(f"Processing single URL output: {output}")
            final_path, used_idx = get_next_available_path(abs_output_path)
            logger.info(f"Downloading to file: {final_path} (index: {used_idx})")

            try:
                bytes_written = await download_file(output, final_path)
                logger.info(f"Downloaded {bytes_written} bytes to {final_path}")
                saved_files.append(final_path)
            except httpx.HTTPError as e:
                logger.error(f"Failed to download video: {e}")
                raise ValueError(f"Failed to download video from {output}: {e}")

        elif hasattr(output, "read"):
            # FileOutput object
            logger.info("Processing FileOutput object with read() method")
            final_path, _ = get_next_available_path(abs_output_path)

            with open(final_path, "wb") as f:
                data = output.read()
                logger.info(f"Read {len(data)} bytes from output")
                f.write(data)

            saved_files.append(final_path)

        elif hasattr(output, "__iter__") and not isinstance(output, (str, bytes)):
            logger.info("Processing iterable output (multiple files)")
            saved_files = await self._process_iterable_output(output, abs_output_path)

        else:
            logger.warning(f"Unexpected output type: {type(output)}, value: {output}")

        return saved_files

    async def _process_iterable_output(
        self, output: Any, abs_output_path: str
    ) -> list[str]:
        """Process iterable output containing multiple files.

        Args:
            output: Iterable of URLs, FileOutput objects, or bytes
            abs_output_path: Absolute path template for output files

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
                    logger.info(f"Downloaded {bytes_written} bytes to {file_path}")
                except httpx.HTTPError as e:
                    logger.error(f"Failed to download video: {e}")
                    continue
            elif hasattr(item, "read"):
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
