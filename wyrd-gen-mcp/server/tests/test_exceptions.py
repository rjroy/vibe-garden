"""Tests for custom exception classes.

This module tests all exception classes in wyrd_gen_mcp.exceptions without
requiring any mocks or external dependencies. Tests verify:
- Message formatting with context
- JSON serialization via to_dict()
- Parameter handling and value truncation
- Cause chaining
- Inheritance relationships
"""

import sys
from pathlib import Path

import pytest

# Ensure src directory is in path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wyrd_gen_mcp.exceptions import (
    FileError,
    GenerationError,
    TimeoutError,
    ValidationError,
    WyrdGenError,
)


class TestWyrdGenError:
    """Test base WyrdGenError class."""

    def test_wyrd_gen_error_message_formatting(self):
        """Test that WyrdGenError includes context in string representation."""
        error = WyrdGenError(
            "Something went wrong",
            operation="test_operation",
            model="test-model",
        )

        error_str = str(error)

        # Verify message is included
        assert "Something went wrong" in error_str

        # Verify context is included
        assert "operation='test_operation'" in error_str
        assert "model='test-model'" in error_str

    def test_wyrd_gen_error_to_dict(self):
        """Test that WyrdGenError.to_dict() produces JSON-serializable output."""
        error = WyrdGenError(
            "Test error",
            operation="test_op",
            model="test-model",
        )

        result = error.to_dict()

        # Verify structure
        assert isinstance(result, dict)
        assert result["error"] == "Test error"
        assert result["error_type"] == "WyrdGenError"
        assert result["context"] == {
            "operation": "test_op",
            "model": "test-model",
        }

        # Verify no 'cause' key when cause is None
        assert "cause" not in result

    def test_wyrd_gen_error_with_cause(self):
        """Test that WyrdGenError includes cause information in to_dict()."""
        original_error = ValueError("Original problem")
        error = WyrdGenError(
            "Wrapped error",
            cause=original_error,
        )

        error_str = str(error)
        result = error.to_dict()

        # Verify cause is in string representation
        assert "Caused by: ValueError: Original problem" in error_str

        # Verify cause is in dict representation
        assert "cause" in result
        assert result["cause"]["type"] == "ValueError"
        assert result["cause"]["message"] == "Original problem"


class TestValidationError:
    """Test ValidationError class."""

    def test_validation_error_with_parameter(self):
        """Test that ValidationError includes parameter name in context."""
        error = ValidationError(
            "Invalid parameter",
            parameter="model",
            value="unknown-model",
        )

        result = error.to_dict()

        # Verify parameter is in context
        assert result["context"]["parameter"] == "model"
        assert result["context"]["value"] == "unknown-model"

    def test_validation_error_truncates_long_value(self):
        """Test that ValidationError truncates values longer than 100 characters."""
        long_value = "x" * 150  # 150 character string

        error = ValidationError(
            "Value too long",
            parameter="prompt",
            value=long_value,
        )

        result = error.to_dict()

        # Verify value is truncated to 100 chars + "..."
        truncated_value = result["context"]["value"]
        assert len(truncated_value) == 103  # 100 chars + "..."
        assert truncated_value.endswith("...")
        assert truncated_value.startswith("x" * 100)

    def test_validation_error_without_parameter(self):
        """Test that ValidationError works without parameter/value."""
        error = ValidationError("General validation failure")

        result = error.to_dict()

        # Verify no context when not provided
        assert "context" not in result or result["context"] == {}


class TestGenerationError:
    """Test GenerationError class."""

    def test_generation_error_with_cause(self):
        """Test that GenerationError includes cause chain in representation."""
        original_error = RuntimeError("API timeout")
        error = GenerationError(
            "Image generation failed",
            operation="image_generation",
            model="flux-dev",
            cause=original_error,
        )

        error_str = str(error)
        result = error.to_dict()

        # Verify cause in string representation
        assert "Caused by: RuntimeError: API timeout" in error_str

        # Verify cause in dict representation
        assert result["cause"]["type"] == "RuntimeError"
        assert result["cause"]["message"] == "API timeout"

    def test_generation_error_truncates_prompt(self):
        """Test that GenerationError truncates prompts longer than 200 characters."""
        long_prompt = "a" * 250  # 250 character prompt

        error = GenerationError(
            "Generation failed",
            operation="image_generation",
            model="test-model",
            prompt=long_prompt,
        )

        result = error.to_dict()

        # Verify prompt is truncated to 200 chars + "..."
        truncated_prompt = result["context"]["prompt"]
        assert len(truncated_prompt) == 203  # 200 chars + "..."
        assert truncated_prompt.endswith("...")
        assert truncated_prompt.startswith("a" * 200)

    def test_generation_error_context(self):
        """Test that GenerationError includes all context fields."""
        error = GenerationError(
            "Generation failed",
            operation="video_generation",
            model="animatediff",
            prompt="test prompt",
            prediction_id="pred-123",
        )

        result = error.to_dict()

        # Verify all context fields are present
        assert result["context"]["operation"] == "video_generation"
        assert result["context"]["model"] == "animatediff"
        assert result["context"]["prompt"] == "test prompt"
        assert result["context"]["prediction_id"] == "pred-123"


class TestFileError:
    """Test FileError class."""

    def test_file_error_context(self):
        """Test that FileError includes path and operation in context."""
        error = FileError(
            "File not found",
            path="/tmp/missing.png",
            operation="read",
        )

        result = error.to_dict()

        # Verify context fields
        assert result["context"]["path"] == "/tmp/missing.png"
        assert result["context"]["operation"] == "read"

    def test_file_error_with_cause(self):
        """Test that FileError includes cause information."""
        original_error = FileNotFoundError("No such file")
        error = FileError(
            "Failed to read file",
            path="/tmp/missing.png",
            operation="read",
            cause=original_error,
        )

        result = error.to_dict()

        # Verify cause is included
        assert result["cause"]["type"] == "FileNotFoundError"
        assert result["cause"]["message"] == "No such file"


class TestTimeoutError:
    """Test TimeoutError class."""

    def test_timeout_error_inherits_generation(self):
        """Test that TimeoutError is a subclass of GenerationError."""
        # Verify inheritance
        assert issubclass(TimeoutError, GenerationError)
        assert issubclass(TimeoutError, WyrdGenError)

        # Verify instance relationship
        error = TimeoutError("Operation timed out")
        assert isinstance(error, GenerationError)
        assert isinstance(error, WyrdGenError)

    def test_timeout_error_context(self):
        """Test that TimeoutError includes timeout details in context."""
        error = TimeoutError(
            "Video generation timed out",
            timeout_seconds=300,
            elapsed_seconds=305.7,
        )

        result = error.to_dict()

        # Verify operation is automatically set
        assert result["context"]["operation"] == "timeout"

        # Verify timeout details
        assert result["context"]["timeout_seconds"] == 300
        assert result["context"]["elapsed_seconds"] == 305.7

    def test_timeout_error_elapsed_rounding(self):
        """Test that TimeoutError rounds elapsed_seconds to 1 decimal place."""
        error = TimeoutError(
            "Timed out",
            elapsed_seconds=123.456789,
        )

        result = error.to_dict()

        # Verify rounding to 1 decimal place
        assert result["context"]["elapsed_seconds"] == 123.5
