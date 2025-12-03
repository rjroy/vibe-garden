"""Tests for local model catalog validation and loading."""

import pytest

from wyrd_gen_mcp.data import (
    LOCAL_MODELS,
    LOCAL_PARAMETERS,
    LOCAL_METADATA,
    validate_local_model_catalog,
)


class TestValidateLocalModelCatalog:
    """Tests for validate_local_model_catalog function."""

    def test_valid_catalog_passes_validation(self):
        """A properly structured catalog should pass validation."""
        valid_catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://huggingface.co",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model",
                    "description": "Test model",
                    "vram_requirement_gb": 8,
                    "quality": 80,
                    "speed": 70,
                    "text_rendering": 60
                }
            ],
            "parameters": {
                "test/model": {
                    "model": "test/model",
                    "parameters": {
                        "test_param": {"type": "integer", "default": 10}
                    }
                }
            }
        }
        # Should not raise
        validate_local_model_catalog(valid_catalog)

    def test_missing_top_level_keys_raises_error(self):
        """Missing top-level keys should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": []
        }
        with pytest.raises(ValueError, match="Missing required top-level keys"):
            validate_local_model_catalog(invalid_catalog)

    def test_missing_metadata_fields_raises_error(self):
        """Missing metadata fields should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02"},
            "models": [],
            "parameters": {}
        }
        with pytest.raises(ValueError, match="Missing required metadata keys"):
            validate_local_model_catalog(invalid_catalog)

    def test_empty_models_array_raises_error(self):
        """Empty models array should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": [],
            "parameters": {}
        }
        with pytest.raises(ValueError, match="'models' array cannot be empty"):
            validate_local_model_catalog(invalid_catalog)

    def test_models_not_array_raises_error(self):
        """Non-array models should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": "not an array",
            "parameters": {}
        }
        with pytest.raises(ValueError, match="'models' must be an array"):
            validate_local_model_catalog(invalid_catalog)

    def test_missing_required_model_fields_raises_error(self):
        """Missing required model fields should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": [{"model": "test/model", "description": "Test"}],
            "parameters": {}
        }
        with pytest.raises(ValueError, match="missing fields"):
            validate_local_model_catalog(invalid_catalog)

    def test_non_string_model_id_raises_error(self):
        """Non-string model ID should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": [{
                "model": 123,
                "description": "Test",
                "vram_requirement_gb": 8,
                "quality": 80,
                "speed": 70,
                "text_rendering": 60
            }],
            "parameters": {}
        }
        with pytest.raises(ValueError, match="non-string model ID"):
            validate_local_model_catalog(invalid_catalog)

    def test_non_numeric_vram_raises_error(self):
        """Non-numeric VRAM requirement should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": [{
                "model": "test/model",
                "description": "Test",
                "vram_requirement_gb": "8GB",
                "quality": 80,
                "speed": 70,
                "text_rendering": 60
            }],
            "parameters": {}
        }
        with pytest.raises(ValueError, match="non-numeric vram_requirement_gb"):
            validate_local_model_catalog(invalid_catalog)

    def test_rating_out_of_range_raises_error(self):
        """Rating values outside 1-100 should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": [{
                "model": "test/model",
                "description": "Test",
                "vram_requirement_gb": 8,
                "quality": 150,
                "speed": 70,
                "text_rendering": 60
            }],
            "parameters": {}
        }
        with pytest.raises(ValueError, match="out of range"):
            validate_local_model_catalog(invalid_catalog)

    def test_rating_below_minimum_raises_error(self):
        """Rating values below 1 should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": [{
                "model": "test/model",
                "description": "Test",
                "vram_requirement_gb": 8,
                "quality": 0,
                "speed": 70,
                "text_rendering": 60
            }],
            "parameters": {}
        }
        with pytest.raises(ValueError, match="out of range"):
            validate_local_model_catalog(invalid_catalog)

    def test_parameters_not_object_raises_error(self):
        """Non-object parameters should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": [{
                "model": "test/model",
                "description": "Test",
                "vram_requirement_gb": 8,
                "quality": 80,
                "speed": 70,
                "text_rendering": 60
            }],
            "parameters": "not an object"
        }
        with pytest.raises(ValueError, match="'parameters' must be an object"):
            validate_local_model_catalog(invalid_catalog)

    def test_parameter_entry_missing_model_field_raises_error(self):
        """Parameter entry without model field should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": [{
                "model": "test/model",
                "description": "Test",
                "vram_requirement_gb": 8,
                "quality": 80,
                "speed": 70,
                "text_rendering": 60
            }],
            "parameters": {
                "test/model": {"parameters": {}}
            }
        }
        with pytest.raises(ValueError, match="missing 'model' field"):
            validate_local_model_catalog(invalid_catalog)

    def test_parameter_entry_missing_parameters_field_raises_error(self):
        """Parameter entry without parameters field should raise ValueError."""
        invalid_catalog = {
            "metadata": {"last_updated": "2025-12-02", "data_source": "test", "schema_version": "1.0"},
            "models": [{
                "model": "test/model",
                "description": "Test",
                "vram_requirement_gb": 8,
                "quality": 80,
                "speed": 70,
                "text_rendering": 60
            }],
            "parameters": {
                "test/model": {"model": "test/model"}
            }
        }
        with pytest.raises(ValueError, match="missing 'parameters' field"):
            validate_local_model_catalog(invalid_catalog)


class TestLoadedLocalCatalog:
    """Tests for the loaded LOCAL_MODELS and LOCAL_PARAMETERS."""

    def test_local_models_is_list(self):
        """LOCAL_MODELS should be a list."""
        assert isinstance(LOCAL_MODELS, list)

    def test_local_models_not_empty(self):
        """LOCAL_MODELS should not be empty."""
        assert len(LOCAL_MODELS) > 0

    def test_local_parameters_is_dict(self):
        """LOCAL_PARAMETERS should be a dict."""
        assert isinstance(LOCAL_PARAMETERS, dict)

    def test_local_metadata_has_required_fields(self):
        """LOCAL_METADATA should have required fields."""
        assert "last_updated" in LOCAL_METADATA
        assert "data_source" in LOCAL_METADATA
        assert "schema_version" in LOCAL_METADATA

    def test_all_models_have_parameters(self):
        """Each model should have corresponding parameters."""
        for model in LOCAL_MODELS:
            model_id = model["model"]
            assert model_id in LOCAL_PARAMETERS, f"Missing parameters for {model_id}"

    def test_flux_schnell_in_catalog(self):
        """FLUX.1-schnell should be in the catalog."""
        model_ids = [m["model"] for m in LOCAL_MODELS]
        assert "black-forest-labs/FLUX.1-schnell" in model_ids

    def test_all_models_have_vram_requirement(self):
        """All models should have VRAM requirements."""
        for model in LOCAL_MODELS:
            assert "vram_requirement_gb" in model
            assert isinstance(model["vram_requirement_gb"], (int, float))
            assert model["vram_requirement_gb"] > 0
