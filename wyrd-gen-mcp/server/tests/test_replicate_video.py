"""Tests for Replicate video generation.

This module tests the ReplicateVideoGenerator class covering:
- Async prediction polling with immediate success
- Success after multiple polls
- Timeout handling and prediction cancellation
- Prediction failures and cancellations
- Input validation (missing image, missing model)
- Output processing (URL strings, FileOutput objects)
- Progress callback invocation during polling
"""

import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

# Ensure src directory is in path for imports
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wyrd_gen_mcp.exceptions import (
    FileError,
    GenerationError,
    TimeoutError as WyrdTimeoutError,
    ValidationError,
)
from wyrd_gen_mcp.generators.replicate_video import (
    PROGRESS_INTERVAL_SECONDS,
    VIDEO_GENERATION_TIMEOUT_SECONDS,
    ReplicateVideoGenerator,
)


class TestReplicateVideoGenerator:
    """Test suite for ReplicateVideoGenerator."""

    @pytest.fixture
    def generator(self, mock_replicate_client, temp_dir):
        """Create a ReplicateVideoGenerator instance with mocked client."""
        return ReplicateVideoGenerator(mock_replicate_client, temp_dir)

    @pytest.fixture
    def valid_params(self, temp_image_file):
        """Standard valid parameters for video generation."""
        return {
            "image": temp_image_file,
            "prompt": "A person walking forward",
            "model": "wan-video/wan-2.2-i2v-fast",
            "output_file_name": "output.mp4",
        }

    @pytest.mark.asyncio
    async def test_generate_success_immediate(
        self, generator, mock_replicate_client, mock_prediction, valid_params
    ):
        """Test video generation succeeding on first poll.

        Verifies that when a prediction succeeds immediately (status='succeeded'
        on first poll), the generator correctly downloads and saves the output.
        """
        # Set up prediction to succeed immediately
        mock_prediction.status = "succeeded"
        mock_prediction.output = "https://example.com/video.mp4"
        mock_replicate_client.predictions.async_create.return_value = mock_prediction
        mock_replicate_client.predictions.async_get.return_value = mock_prediction

        # Mock download_file
        with patch(
            "wyrd_gen_mcp.generators.replicate_video.download_file",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = 1024  # bytes written

            result = await generator.generate(**valid_params)

            # Verify prediction was created
            mock_replicate_client.predictions.async_create.assert_called_once()
            create_call = mock_replicate_client.predictions.async_create.call_args

            # Verify model and input
            assert create_call.kwargs["model"] == valid_params["model"]
            assert "prompt" in create_call.kwargs["input"]
            assert create_call.kwargs["input"]["prompt"] == valid_params["prompt"]

            # Verify prediction was polled
            assert mock_replicate_client.predictions.async_get.call_count >= 1

            # Verify download was called
            mock_download.assert_called_once()

            # Verify result
            assert result.success is True
            assert result.model == valid_params["model"]
            assert result.prompt == valid_params["prompt"]
            assert len(result.saved_files) == 1
            assert result.saved_files[0].endswith(".mp4")

    @pytest.mark.asyncio
    async def test_generate_success_after_polls(
        self, generator, mock_replicate_client, mock_prediction, valid_params
    ):
        """Test video generation succeeding after multiple polls.

        Verifies that the generator correctly polls multiple times, reporting
        progress, before the prediction succeeds.
        """
        # Set up prediction to succeed after 3 polls
        mock_prediction.id = "test-prediction-id"
        mock_replicate_client.predictions.async_create.return_value = mock_prediction

        # Create prediction objects for polling sequence
        processing_pred_1 = MagicMock()
        processing_pred_1.id = "test-prediction-id"
        processing_pred_1.status = "processing"
        processing_pred_1.error = None

        processing_pred_2 = MagicMock()
        processing_pred_2.id = "test-prediction-id"
        processing_pred_2.status = "processing"
        processing_pred_2.error = None

        success_pred = MagicMock()
        success_pred.id = "test-prediction-id"
        success_pred.status = "succeeded"
        success_pred.output = "https://example.com/video.mp4"
        success_pred.error = None

        # Set up polling sequence
        mock_replicate_client.predictions.async_get.side_effect = [
            processing_pred_1,
            processing_pred_2,
            success_pred,
        ]

        # Mock time to avoid actual delays
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep, patch(
            "wyrd_gen_mcp.generators.replicate_video.download_file",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = 2048

            result = await generator.generate(**valid_params)

            # Verify multiple polls occurred
            assert mock_replicate_client.predictions.async_get.call_count == 3

            # Verify sleep was called between polls
            assert mock_sleep.call_count >= 2

            # Verify successful result
            assert result.success is True
            assert len(result.saved_files) == 1

    @pytest.mark.asyncio
    async def test_generate_timeout(
        self, generator, mock_replicate_client, mock_prediction, valid_params
    ):
        """Test video generation timeout and prediction cancellation.

        Verifies that when generation exceeds the timeout limit, the generator:
        1. Raises WyrdTimeoutError
        2. Attempts to cancel the prediction on Replicate
        """
        # Set up prediction to never complete
        mock_prediction.id = "test-prediction-id"
        mock_prediction.status = "processing"
        mock_replicate_client.predictions.async_create.return_value = mock_prediction
        mock_replicate_client.predictions.async_get.return_value = mock_prediction

        # Mock time to simulate timeout - the code calls time() multiple times
        start_time = 1000.0
        # Track call count to return appropriate time
        call_count = [0]

        def mock_time():
            call_count[0] += 1
            if call_count[0] <= 2:
                return start_time  # First two calls: start_time and first elapsed
            else:
                # After that, time has exceeded timeout
                return start_time + VIDEO_GENERATION_TIMEOUT_SECONDS + 1

        with patch("asyncio.sleep", new_callable=AsyncMock), patch(
            "asyncio.get_event_loop"
        ) as mock_loop:
            mock_loop.return_value.time = mock_time

            # Expect timeout error
            with pytest.raises(WyrdTimeoutError) as exc_info:
                await generator.generate(**valid_params)

            # Verify timeout details in error
            error = exc_info.value
            assert "timed out" in str(error).lower()
            assert mock_prediction.id in str(error)

            # Verify cancellation was attempted
            mock_replicate_client.predictions.async_cancel.assert_called_once_with(
                mock_prediction.id
            )

    @pytest.mark.asyncio
    async def test_generate_prediction_failed(
        self, generator, mock_replicate_client, mock_prediction, valid_params
    ):
        """Test handling of prediction failure status.

        Verifies that when Replicate returns status='failed', the generator
        raises GenerationError with the error message from the prediction.
        """
        # Set up prediction to fail
        mock_prediction.id = "test-prediction-id"
        mock_prediction.status = "failed"
        mock_prediction.error = "Model execution failed: out of memory"
        mock_replicate_client.predictions.async_create.return_value = mock_prediction
        mock_replicate_client.predictions.async_get.return_value = mock_prediction

        # Expect generation error
        with pytest.raises(GenerationError) as exc_info:
            await generator.generate(**valid_params)

        # Verify error details
        error = exc_info.value
        assert "failed" in str(error).lower()
        assert "out of memory" in str(error)

    @pytest.mark.asyncio
    async def test_generate_prediction_canceled(
        self, generator, mock_replicate_client, mock_prediction, valid_params
    ):
        """Test handling of prediction cancellation status.

        Verifies that when Replicate returns status='canceled', the generator
        raises GenerationError indicating cancellation.
        """
        # Set up prediction to be canceled
        mock_prediction.id = "test-prediction-id"
        mock_prediction.status = "canceled"
        mock_replicate_client.predictions.async_create.return_value = mock_prediction
        mock_replicate_client.predictions.async_get.return_value = mock_prediction

        # Expect generation error
        with pytest.raises(GenerationError) as exc_info:
            await generator.generate(**valid_params)

        # Verify error indicates cancellation
        error = exc_info.value
        assert "canceled" in str(error).lower()

    @pytest.mark.asyncio
    async def test_validate_missing_image(self, generator, valid_params):
        """Test validation error when image parameter is missing.

        Verifies that ValidationError is raised when the image parameter
        is empty or None.
        """
        # Remove image parameter
        params = valid_params.copy()
        params["image"] = ""

        with pytest.raises(ValidationError) as exc_info:
            await generator.generate(**params)

        error = exc_info.value
        assert "image" in str(error).lower()
        assert "required" in str(error).lower()

    @pytest.mark.asyncio
    async def test_validate_missing_model(self, generator, valid_params):
        """Test validation error when model parameter is missing.

        Verifies that ValidationError is raised when the model parameter
        is empty or None, with helpful message about available models.
        """
        # Remove model parameter
        params = valid_params.copy()
        params["model"] = ""

        with pytest.raises(ValidationError) as exc_info:
            await generator.generate(**params)

        error = exc_info.value
        assert "model" in str(error).lower()
        assert "required" in str(error).lower()

    @pytest.mark.asyncio
    async def test_download_url_output(
        self, generator, mock_replicate_client, mock_prediction, valid_params
    ):
        """Test processing of URL string output.

        Verifies that when the prediction returns a URL string, the generator
        correctly downloads the file from that URL.
        """
        # Set up prediction with URL output
        mock_prediction.status = "succeeded"
        mock_prediction.output = "https://example.com/generated-video.mp4"
        mock_replicate_client.predictions.async_create.return_value = mock_prediction
        mock_replicate_client.predictions.async_get.return_value = mock_prediction

        with patch(
            "wyrd_gen_mcp.generators.replicate_video.download_file",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = 5000

            result = await generator.generate(**valid_params)

            # Verify download_file was called with the URL
            mock_download.assert_called_once()
            download_args = mock_download.call_args
            assert download_args[0][0] == "https://example.com/generated-video.mp4"

            # Verify file was saved
            assert len(result.saved_files) == 1
            assert result.saved_files[0].endswith(".mp4")

    @pytest.mark.asyncio
    async def test_download_file_output(
        self, generator, mock_replicate_client, mock_prediction, valid_params, temp_dir
    ):
        """Test processing of FileOutput object.

        Verifies that when the prediction returns a FileOutput object with
        a read() method, the generator correctly reads and saves the data.
        """
        # Set up prediction with FileOutput
        mock_file_output = MagicMock()
        mock_file_output.read.return_value = b"fake_video_data_12345"

        mock_prediction.status = "succeeded"
        mock_prediction.output = mock_file_output
        mock_replicate_client.predictions.async_create.return_value = mock_prediction
        mock_replicate_client.predictions.async_get.return_value = mock_prediction

        result = await generator.generate(**valid_params)

        # Verify read() was called
        mock_file_output.read.assert_called_once()

        # Verify file was saved
        assert len(result.saved_files) == 1
        saved_file = result.saved_files[0]
        assert os.path.exists(saved_file)

        # Verify file content
        with open(saved_file, "rb") as f:
            content = f.read()
            assert content == b"fake_video_data_12345"

    @pytest.mark.asyncio
    async def test_progress_callback_invoked(
        self, generator, mock_replicate_client, mock_prediction, valid_params
    ):
        """Test that progress callback is invoked during polling.

        Verifies that the progress callback is called at appropriate points:
        1. When generation starts
        2. During each polling iteration
        3. When generation completes
        """
        # Set up prediction to succeed after 2 polls
        mock_prediction.id = "test-prediction-id"
        mock_replicate_client.predictions.async_create.return_value = mock_prediction

        processing_pred = MagicMock()
        processing_pred.id = "test-prediction-id"
        processing_pred.status = "processing"
        processing_pred.error = None

        success_pred = MagicMock()
        success_pred.id = "test-prediction-id"
        success_pred.status = "succeeded"
        success_pred.output = "https://example.com/video.mp4"
        success_pred.error = None

        mock_replicate_client.predictions.async_get.side_effect = [
            processing_pred,
            success_pred,
        ]

        # Create mock callback to track invocations
        mock_callback = AsyncMock()

        with patch("asyncio.sleep", new_callable=AsyncMock), patch(
            "wyrd_gen_mcp.generators.replicate_video.download_file",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = 1024

            params = valid_params.copy()
            params["progress_callback"] = mock_callback

            await generator.generate(**params)

            # Verify callback was called multiple times
            assert mock_callback.call_count >= 3

            # Verify callback received expected arguments
            # First call: generation started
            first_call = mock_callback.call_args_list[0]
            assert first_call[0][0] == 0  # progress count
            assert "started" in first_call[0][2].lower()  # status message

            # Middle calls: polling status updates
            # Should contain status messages with "processing" or similar

            # Last call: completion message
            last_call = mock_callback.call_args_list[-1]
            assert (
                "complete" in last_call[0][2].lower()
                or "downloading" in last_call[0][2].lower()
            )


class TestReplicateVideoInputProcessing:
    """Test input image processing and parameter building."""

    @pytest.fixture
    def generator(self, mock_replicate_client, temp_dir):
        """Create a ReplicateVideoGenerator instance."""
        return ReplicateVideoGenerator(mock_replicate_client, temp_dir)

    @pytest.mark.asyncio
    async def test_image_parameter_name_kling(
        self, generator, mock_replicate_client, mock_prediction, temp_image_file
    ):
        """Test that Kling models use 'start_image' parameter name.

        Different video models expect the input image under different parameter
        names. Kling models should use 'start_image'.
        """
        mock_prediction.status = "succeeded"
        mock_prediction.output = "https://example.com/video.mp4"
        mock_replicate_client.predictions.async_create.return_value = mock_prediction
        mock_replicate_client.predictions.async_get.return_value = mock_prediction

        with patch(
            "wyrd_gen_mcp.generators.replicate_video.download_file",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = 1024

            await generator.generate(
                image=temp_image_file,
                prompt="Test prompt",
                model="kling-ai/kling-v1",
                output_file_name="output.mp4",
            )

            # Verify the input dict uses 'start_image'
            create_call = mock_replicate_client.predictions.async_create.call_args
            assert "start_image" in create_call.kwargs["input"]

    @pytest.mark.asyncio
    async def test_custom_parameters_passed(
        self, generator, mock_replicate_client, mock_prediction, temp_image_file
    ):
        """Test that custom parameters are passed through to the model.

        Verifies that additional parameters provided by the user are included
        in the model input dict.
        """
        mock_prediction.status = "succeeded"
        mock_prediction.output = "https://example.com/video.mp4"
        mock_replicate_client.predictions.async_create.return_value = mock_prediction
        mock_replicate_client.predictions.async_get.return_value = mock_prediction

        custom_params = {
            "duration": 10,
            "motion_strength": 0.8,
        }

        with patch(
            "wyrd_gen_mcp.generators.replicate_video.download_file",
            new_callable=AsyncMock,
        ) as mock_download:
            mock_download.return_value = 1024

            await generator.generate(
                image=temp_image_file,
                prompt="Test prompt",
                model="wan-video/wan-2.2-i2v-fast",
                output_file_name="output.mp4",
                parameters=custom_params,
            )

            # Verify custom parameters are in the input
            create_call = mock_replicate_client.predictions.async_create.call_args
            model_input = create_call.kwargs["input"]
            assert model_input["duration"] == 10
            assert model_input["motion_strength"] == 0.8
