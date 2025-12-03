"""Model catalog data loader with validation."""

import json
import logging
from importlib.resources import files
from typing import Any

logger = logging.getLogger(__name__)


def validate_model_catalog(data: dict[str, Any]) -> None:
    """Validate model catalog structure.

    Args:
        data: The loaded JSON data

    Raises:
        ValueError: If validation fails
    """
    # Validate top-level structure
    required_keys = {"metadata", "models", "parameters"}
    if not required_keys.issubset(data.keys()):
        missing = required_keys - data.keys()
        raise ValueError(f"Missing required top-level keys: {missing}")

    # Validate metadata
    metadata = data["metadata"]
    required_metadata = {"last_updated", "data_source", "schema_version"}
    if not required_metadata.issubset(metadata.keys()):
        missing = required_metadata - metadata.keys()
        raise ValueError(f"Missing required metadata keys: {missing}")

    # Validate models array
    models = data["models"]
    if not isinstance(models, list):
        raise ValueError("'models' must be an array")

    if not models:
        raise ValueError("'models' array cannot be empty")

    required_model_fields = {
        "model", "description", "cost", "cost_efficiency",
        "photorealism", "artistic_quality", "consistency", "speed", "style_versatility"
    }
    rating_fields = [
        "photorealism", "artistic_quality", "consistency", "speed", "style_versatility"
    ]

    for idx, model in enumerate(models):
        if not isinstance(model, dict):
            raise ValueError(f"Model at index {idx} is not an object")

        if not required_model_fields.issubset(model.keys()):
            missing = required_model_fields - model.keys()
            model_id = model.get('model', f'at index {idx}')
            raise ValueError(f"Model '{model_id}' missing fields: {missing}")

        # Validate types
        if not isinstance(model["model"], str):
            raise ValueError(f"Model '{model['model']}' has non-string model ID")
        if not isinstance(model["cost"], (int, float)):
            raise ValueError(f"Model '{model['model']}' has non-numeric cost")
        if not isinstance(model["cost_efficiency"], (int, float)):
            raise ValueError(f"Model '{model['model']}' has non-numeric cost_efficiency")

        # Validate dimensional ratings
        for rating_field in rating_fields:
            value = model[rating_field]
            if not isinstance(value, (int, float)):
                raise ValueError(f"Model '{model['model']}' has non-numeric {rating_field}")
            if not (1 <= value <= 100):
                raise ValueError(
                    f"Model '{model['model']}' has {rating_field}={value} "
                    f"out of range (must be 1-100)"
                )

    # Validate parameters
    parameters = data["parameters"]
    if not isinstance(parameters, dict):
        raise ValueError("'parameters' must be an object")

    for model_id, param_data in parameters.items():
        if not isinstance(param_data, dict):
            raise ValueError(f"Parameters for '{model_id}' is not an object")

        if "model" not in param_data:
            raise ValueError(f"Parameters for '{model_id}' missing 'model' field")

        if "parameters" not in param_data:
            raise ValueError(f"Parameters for '{model_id}' missing 'parameters' field")

        if not isinstance(param_data["parameters"], dict):
            raise ValueError(f"Parameters for '{model_id}' has non-object 'parameters' field")


def load_model_catalog() -> dict[str, Any]:
    """Load and validate model catalog from package data.

    Returns:
        The validated model catalog data

    Raises:
        FileNotFoundError: If the catalog file is not found
        ValueError: If validation fails
        json.JSONDecodeError: If the JSON is malformed
    """
    try:
        # Load the JSON file from package data
        catalog_file = files("wyrd_gen_mcp.data").joinpath("model_catalog.json")
        data = json.loads(catalog_file.read_text())

        # Validate the structure
        validate_model_catalog(data)

        logger.info(
            f"Loaded {len(data['models'])} models and "
            f"{len(data['parameters'])} parameter definitions"
        )
        logger.info(f"Catalog last updated: {data['metadata']['last_updated']}")

        return data

    except FileNotFoundError:
        logger.error("model_catalog.json not found in package data")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in model_catalog.json: {e}")
        raise
    except ValueError as e:
        logger.error(f"Model catalog validation failed: {e}")
        raise


# Load catalog once at module import time
try:
    _CATALOG = load_model_catalog()
    MODELS: list[dict[str, Any]] = _CATALOG["models"]
    PARAMETERS: dict[str, dict[str, Any]] = _CATALOG["parameters"]
    METADATA: dict[str, str] = _CATALOG["metadata"]
except Exception as e:
    logger.critical(f"Failed to load model catalog: {e}")
    raise


def validate_video_model_catalog(data: dict[str, Any]) -> None:
    """Validate video model catalog structure.

    Args:
        data: The loaded JSON data

    Raises:
        ValueError: If validation fails
    """
    # Validate top-level structure
    required_keys = {"metadata", "models", "parameters"}
    if not required_keys.issubset(data.keys()):
        missing = required_keys - data.keys()
        raise ValueError(f"Missing required top-level keys: {missing}")

    # Validate metadata
    metadata = data["metadata"]
    required_metadata = {"last_updated", "data_source", "schema_version"}
    if not required_metadata.issubset(metadata.keys()):
        missing = required_metadata - metadata.keys()
        raise ValueError(f"Missing required metadata keys: {missing}")

    # Validate models array
    models = data["models"]
    if not isinstance(models, list):
        raise ValueError("'models' must be an array")

    if not models:
        raise ValueError("'models' array cannot be empty")

    required_model_fields = {
        "model", "description", "use_case", "cost_per_video",
        "duration_seconds", "resolution", "fps", "vendor"
    }
    valid_use_cases = {"iteration", "animation", "stylized", "photorealistic", "premium"}

    for idx, model in enumerate(models):
        if not isinstance(model, dict):
            raise ValueError(f"Model at index {idx} is not an object")

        if not required_model_fields.issubset(model.keys()):
            missing = required_model_fields - model.keys()
            model_id = model.get('model', f'at index {idx}')
            raise ValueError(f"Model '{model_id}' missing fields: {missing}")

        # Validate types
        if not isinstance(model["model"], str):
            raise ValueError(f"Model '{model['model']}' has non-string model ID")
        if not isinstance(model["description"], str):
            raise ValueError(f"Model '{model['model']}' has non-string description")
        if not isinstance(model["use_case"], str):
            raise ValueError(f"Model '{model['model']}' has non-string use_case")
        if model["use_case"] not in valid_use_cases:
            raise ValueError(
                f"Model '{model['model']}' has invalid use_case '{model['use_case']}' "
                f"(must be one of: {valid_use_cases})"
            )
        if not isinstance(model["cost_per_video"], (int, float)):
            raise ValueError(f"Model '{model['model']}' has non-numeric cost_per_video")
        if not isinstance(model["duration_seconds"], (int, float)):
            raise ValueError(f"Model '{model['model']}' has non-numeric duration_seconds")
        if not isinstance(model["resolution"], str):
            raise ValueError(f"Model '{model['model']}' has non-string resolution")
        if not isinstance(model["fps"], (int, float)):
            raise ValueError(f"Model '{model['model']}' has non-numeric fps")
        if not isinstance(model["vendor"], str):
            raise ValueError(f"Model '{model['model']}' has non-string vendor")

    # Validate parameters
    parameters = data["parameters"]
    if not isinstance(parameters, dict):
        raise ValueError("'parameters' must be an object")

    for model_id, param_data in parameters.items():
        if not isinstance(param_data, dict):
            raise ValueError(f"Parameters for '{model_id}' is not an object")

        if "model" not in param_data:
            raise ValueError(f"Parameters for '{model_id}' missing 'model' field")

        if "parameters" not in param_data:
            raise ValueError(f"Parameters for '{model_id}' missing 'parameters' field")

        if not isinstance(param_data["parameters"], dict):
            raise ValueError(f"Parameters for '{model_id}' has non-object 'parameters' field")


def load_video_model_catalog() -> dict[str, Any]:
    """Load and validate video model catalog from package data.

    Returns:
        The validated video model catalog data

    Raises:
        FileNotFoundError: If the catalog file is not found
        ValueError: If validation fails
        json.JSONDecodeError: If the JSON is malformed
    """
    try:
        # Load the JSON file from package data
        catalog_file = files("wyrd_gen_mcp.data").joinpath("video_model_catalog.json")
        data = json.loads(catalog_file.read_text())

        # Validate the structure
        validate_video_model_catalog(data)

        logger.info(
            f"Loaded {len(data['models'])} video models and "
            f"{len(data['parameters'])} parameter definitions"
        )
        logger.info(f"Video catalog last updated: {data['metadata']['last_updated']}")

        return data

    except FileNotFoundError:
        logger.error("video_model_catalog.json not found in package data")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in video_model_catalog.json: {e}")
        raise
    except ValueError as e:
        logger.error(f"Video model catalog validation failed: {e}")
        raise


# Load video catalog once at module import time
try:
    _VIDEO_CATALOG = load_video_model_catalog()
    VIDEO_MODELS: list[dict[str, Any]] = _VIDEO_CATALOG["models"]
    VIDEO_PARAMETERS: dict[str, dict[str, Any]] = _VIDEO_CATALOG["parameters"]
    VIDEO_METADATA: dict[str, str] = _VIDEO_CATALOG["metadata"]
except Exception as e:
    logger.critical(f"Failed to load video model catalog: {e}")
    raise


def validate_local_model_catalog(data: dict[str, Any]) -> None:
    """Validate local model catalog structure.

    Args:
        data: The loaded JSON data

    Raises:
        ValueError: If validation fails
    """
    # Validate top-level structure
    required_keys = {"metadata", "models", "parameters"}
    if not required_keys.issubset(data.keys()):
        missing = required_keys - data.keys()
        raise ValueError(f"Missing required top-level keys: {missing}")

    # Validate metadata
    metadata = data["metadata"]
    required_metadata = {"last_updated", "data_source", "schema_version"}
    if not required_metadata.issubset(metadata.keys()):
        missing = required_metadata - metadata.keys()
        raise ValueError(f"Missing required metadata keys: {missing}")

    # Validate models array
    models = data["models"]
    if not isinstance(models, list):
        raise ValueError("'models' must be an array")

    if not models:
        raise ValueError("'models' array cannot be empty")

    required_model_fields = {
        "model", "description", "vram_requirement_gb",
        "quality", "speed", "text_rendering"
    }
    rating_fields = ["quality", "speed", "text_rendering"]

    for idx, model in enumerate(models):
        if not isinstance(model, dict):
            raise ValueError(f"Model at index {idx} is not an object")

        if not required_model_fields.issubset(model.keys()):
            missing = required_model_fields - model.keys()
            model_id = model.get('model', f'at index {idx}')
            raise ValueError(f"Model '{model_id}' missing fields: {missing}")

        # Validate types
        if not isinstance(model["model"], str):
            raise ValueError(f"Model '{model['model']}' has non-string model ID")
        if not isinstance(model["vram_requirement_gb"], (int, float)):
            raise ValueError(f"Model '{model['model']}' has non-numeric vram_requirement_gb")

        # Validate dimensional ratings
        for rating_field in rating_fields:
            value = model[rating_field]
            if not isinstance(value, (int, float)):
                raise ValueError(f"Model '{model['model']}' has non-numeric {rating_field}")
            if not (1 <= value <= 100):
                raise ValueError(
                    f"Model '{model['model']}' has {rating_field}={value} "
                    f"out of range (must be 1-100)"
                )

    # Validate parameters
    parameters = data["parameters"]
    if not isinstance(parameters, dict):
        raise ValueError("'parameters' must be an object")

    for model_id, param_data in parameters.items():
        if not isinstance(param_data, dict):
            raise ValueError(f"Parameters for '{model_id}' is not an object")

        if "model" not in param_data:
            raise ValueError(f"Parameters for '{model_id}' missing 'model' field")

        if "parameters" not in param_data:
            raise ValueError(f"Parameters for '{model_id}' missing 'parameters' field")

        if not isinstance(param_data["parameters"], dict):
            raise ValueError(f"Parameters for '{model_id}' has non-object 'parameters' field")


def load_local_model_catalog() -> dict[str, Any]:
    """Load and validate local model catalog from package data.

    Returns:
        The validated local model catalog data

    Raises:
        FileNotFoundError: If the catalog file is not found
        ValueError: If validation fails
        json.JSONDecodeError: If the JSON is malformed
    """
    try:
        # Load the JSON file from package data
        catalog_file = files("wyrd_gen_mcp.data").joinpath("local_model_catalog.json")
        data = json.loads(catalog_file.read_text())

        # Validate the structure
        validate_local_model_catalog(data)

        logger.info(
            f"Loaded {len(data['models'])} local models and "
            f"{len(data['parameters'])} parameter definitions"
        )
        logger.info(f"Local catalog last updated: {data['metadata']['last_updated']}")

        return data

    except FileNotFoundError:
        logger.error("local_model_catalog.json not found in package data")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in local_model_catalog.json: {e}")
        raise
    except ValueError as e:
        logger.error(f"Local model catalog validation failed: {e}")
        raise


# Load local catalog once at module import time
try:
    _LOCAL_CATALOG = load_local_model_catalog()
    LOCAL_MODELS: list[dict[str, Any]] = _LOCAL_CATALOG["models"]
    LOCAL_PARAMETERS: dict[str, dict[str, Any]] = _LOCAL_CATALOG["parameters"]
    LOCAL_METADATA: dict[str, str] = _LOCAL_CATALOG["metadata"]
except Exception as e:
    logger.critical(f"Failed to load local model catalog: {e}")
    raise


__all__ = [
    "MODELS", "PARAMETERS", "METADATA",
    "load_model_catalog", "validate_model_catalog",
    "VIDEO_MODELS", "VIDEO_PARAMETERS", "VIDEO_METADATA",
    "load_video_model_catalog", "validate_video_model_catalog",
    "LOCAL_MODELS", "LOCAL_PARAMETERS", "LOCAL_METADATA",
    "load_local_model_catalog", "validate_local_model_catalog"
]
