"""Model catalog data loader with validation."""

import json
import logging
from importlib.resources import files
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def validate_model_catalog(data: Dict[str, Any]) -> None:
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

    required_model_fields = {"model", "description", "best_for", "cost", "quality", "cost_efficiency"}
    for idx, model in enumerate(models):
        if not isinstance(model, dict):
            raise ValueError(f"Model at index {idx} is not an object")

        if not required_model_fields.issubset(model.keys()):
            missing = required_model_fields - model.keys()
            raise ValueError(f"Model '{model.get('model', f'at index {idx}')}' missing fields: {missing}")

        # Validate types
        if not isinstance(model["model"], str):
            raise ValueError(f"Model '{model['model']}' has non-string model ID")
        if not isinstance(model["cost"], (int, float)):
            raise ValueError(f"Model '{model['model']}' has non-numeric cost")
        if not isinstance(model["quality"], (int, float)):
            raise ValueError(f"Model '{model['model']}' has non-numeric quality")

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


def load_model_catalog() -> Dict[str, Any]:
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

        logger.info(f"Loaded {len(data['models'])} models and {len(data['parameters'])} parameter definitions")
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
    MODELS: List[Dict[str, Any]] = _CATALOG["models"]
    PARAMETERS: Dict[str, Dict[str, Any]] = _CATALOG["parameters"]
    METADATA: Dict[str, str] = _CATALOG["metadata"]
except Exception as e:
    logger.critical(f"Failed to load model catalog: {e}")
    raise


__all__ = ["MODELS", "PARAMETERS", "METADATA", "load_model_catalog", "validate_model_catalog"]
