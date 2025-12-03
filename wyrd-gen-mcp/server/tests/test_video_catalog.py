"""Unit tests for validate_video_model_catalog() function."""

import pytest
from wyrd_gen_mcp.data import validate_video_model_catalog


class TestValidateVideoModelCatalog:
    """Test suite for video model catalog validation."""

    def test_valid_catalog_passes_validation(self):
        """Test that a valid catalog passes validation without errors."""
        valid_catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model description",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {
                "test/model-1": {
                    "model": "test/model-1",
                    "parameters": {
                        "prompt": {
                            "type": "string",
                            "description": "Test prompt"
                        }
                    }
                }
            }
        }

        # Should not raise any exception
        validate_video_model_catalog(valid_catalog)

    def test_missing_top_level_keys_raises_error(self):
        """Test that missing required top-level keys raises ValueError."""
        # Missing 'models' key
        catalog = {
            "metadata": {},
            "parameters": {}
        }

        with pytest.raises(ValueError, match="Missing required top-level keys"):
            validate_video_model_catalog(catalog)

    def test_missing_metadata_fields_raises_error(self):
        """Test that missing metadata fields raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02"
                # Missing 'data_source' and 'schema_version'
            },
            "models": [],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="Missing required metadata keys"):
            validate_video_model_catalog(catalog)

    def test_empty_models_array_raises_error(self):
        """Test that empty models array raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [],  # Empty array
            "parameters": {}
        }

        with pytest.raises(ValueError, match="'models' array cannot be empty"):
            validate_video_model_catalog(catalog)

    def test_models_not_array_raises_error(self):
        """Test that non-array models field raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": "not an array",  # Wrong type
            "parameters": {}
        }

        with pytest.raises(ValueError, match="'models' must be an array"):
            validate_video_model_catalog(catalog)

    def test_missing_required_model_fields_raises_error(self):
        """Test that missing required model fields raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    # Missing required fields: use_case, cost_per_video, duration_seconds,
                    # resolution, fps, vendor
                }
            ],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="missing fields"):
            validate_video_model_catalog(catalog)

    def test_invalid_use_case_raises_error(self):
        """Test that invalid use_case value raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "invalid_use_case",  # Invalid value
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="invalid use_case"):
            validate_video_model_catalog(catalog)

    def test_all_valid_use_cases_pass_validation(self):
        """Test that all valid use_case values pass validation."""
        valid_use_cases = ["iteration", "animation", "stylized", "photorealistic", "premium"]

        for use_case in valid_use_cases:
            catalog = {
                "metadata": {
                    "last_updated": "2025-12-02",
                    "data_source": "https://example.com",
                    "schema_version": "1.0"
                },
                "models": [
                    {
                        "model": f"test/model-{use_case}",
                        "description": "Test model",
                        "use_case": use_case,
                        "cost_per_video": 0.50,
                        "duration_seconds": 5,
                        "resolution": "720p",
                        "fps": 30,
                        "vendor": "TestVendor"
                    }
                ],
                "parameters": {
                    f"test/model-{use_case}": {
                        "model": f"test/model-{use_case}",
                        "parameters": {}
                    }
                }
            }

            # Should not raise any exception
            validate_video_model_catalog(catalog)

    def test_non_string_model_id_raises_error(self):
        """Test that non-string model ID raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": 12345,  # Should be string
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="non-string model ID"):
            validate_video_model_catalog(catalog)

    def test_non_string_description_raises_error(self):
        """Test that non-string description raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": 12345,  # Should be string
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="non-string description"):
            validate_video_model_catalog(catalog)

    def test_non_numeric_cost_raises_error(self):
        """Test that non-numeric cost_per_video raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": "expensive",  # Should be numeric
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="non-numeric cost_per_video"):
            validate_video_model_catalog(catalog)

    def test_non_numeric_duration_raises_error(self):
        """Test that non-numeric duration_seconds raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": "long",  # Should be numeric
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="non-numeric duration_seconds"):
            validate_video_model_catalog(catalog)

    def test_non_string_resolution_raises_error(self):
        """Test that non-string resolution raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": 720,  # Should be string
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="non-string resolution"):
            validate_video_model_catalog(catalog)

    def test_non_numeric_fps_raises_error(self):
        """Test that non-numeric fps raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": "fast",  # Should be numeric
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="non-numeric fps"):
            validate_video_model_catalog(catalog)

    def test_non_string_vendor_raises_error(self):
        """Test that non-string vendor raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": 12345  # Should be string
                }
            ],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="non-string vendor"):
            validate_video_model_catalog(catalog)

    def test_parameters_not_object_raises_error(self):
        """Test that non-object parameters field raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": "not an object"  # Should be object/dict
        }

        with pytest.raises(ValueError, match="'parameters' must be an object"):
            validate_video_model_catalog(catalog)

    def test_parameter_entry_missing_model_field_raises_error(self):
        """Test that parameter entry missing 'model' field raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {
                "test/model-1": {
                    # Missing 'model' field
                    "parameters": {}
                }
            }
        }

        with pytest.raises(ValueError, match="missing 'model' field"):
            validate_video_model_catalog(catalog)

    def test_parameter_entry_missing_parameters_field_raises_error(self):
        """Test that parameter entry missing 'parameters' field raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {
                "test/model-1": {
                    "model": "test/model-1"
                    # Missing 'parameters' field
                }
            }
        }

        with pytest.raises(ValueError, match="missing 'parameters' field"):
            validate_video_model_catalog(catalog)

    def test_multiple_models_pass_validation(self):
        """Test that catalog with multiple valid models passes validation."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model 1",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                },
                {
                    "model": "test/model-2",
                    "description": "Test model 2",
                    "use_case": "premium",
                    "cost_per_video": 1.50,
                    "duration_seconds": 10,
                    "resolution": "1080p",
                    "fps": 60,
                    "vendor": "AnotherVendor"
                }
            ],
            "parameters": {
                "test/model-1": {
                    "model": "test/model-1",
                    "parameters": {}
                },
                "test/model-2": {
                    "model": "test/model-2",
                    "parameters": {}
                }
            }
        }

        # Should not raise any exception
        validate_video_model_catalog(catalog)

    def test_numeric_values_can_be_integers_or_floats(self):
        """Test that numeric fields accept both int and float values."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,  # float
                    "duration_seconds": 5,  # int
                    "resolution": "720p",
                    "fps": 30.0,  # float
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {
                "test/model-1": {
                    "model": "test/model-1",
                    "parameters": {}
                }
            }
        }

        # Should not raise any exception
        validate_video_model_catalog(catalog)

    def test_model_not_object_raises_error(self):
        """Test that non-object model entry raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                "not an object"  # Should be dict
            ],
            "parameters": {}
        }

        with pytest.raises(ValueError, match="Model at index 0 is not an object"):
            validate_video_model_catalog(catalog)

    def test_parameter_entry_not_object_raises_error(self):
        """Test that non-object parameter entry raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {
                "test/model-1": "not an object"  # Should be dict
            }
        }

        with pytest.raises(ValueError, match="Parameters for 'test/model-1' is not an object"):
            validate_video_model_catalog(catalog)

    def test_parameter_parameters_field_not_object_raises_error(self):
        """Test that non-object 'parameters' field in parameter entry raises ValueError."""
        catalog = {
            "metadata": {
                "last_updated": "2025-12-02",
                "data_source": "https://example.com",
                "schema_version": "1.0"
            },
            "models": [
                {
                    "model": "test/model-1",
                    "description": "Test model",
                    "use_case": "iteration",
                    "cost_per_video": 0.50,
                    "duration_seconds": 5,
                    "resolution": "720p",
                    "fps": 30,
                    "vendor": "TestVendor"
                }
            ],
            "parameters": {
                "test/model-1": {
                    "model": "test/model-1",
                    "parameters": "not an object"  # Should be dict
                }
            }
        }

        with pytest.raises(ValueError, match="has non-object 'parameters' field"):
            validate_video_model_catalog(catalog)
