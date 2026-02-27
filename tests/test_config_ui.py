"""Tests for configuration UI functionality."""
import tempfile
from pathlib import Path

import pytest

from config_manager import ConfigManager


class TestConfigUI:
    """Test cases for configuration UI functionality."""

    def test_config_ui_initialization(self):
        """Test configuration UI initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = ConfigManager(config_path)
            
            # Test that config loads with default values
            assert config.default_path.exists()
            assert config.theme in ["light", "dark"]
            assert config.preview_size_limit > 0
            assert isinstance(config.ignored_patterns, list)

    def test_config_ui_get_all_settings(self):
        """Test getting all configuration settings as a dictionary."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = ConfigManager(config_path)
            
            settings = config.to_dict()
            
            # Check that all expected keys are present
            expected_keys = [
                "default_path",
                "theme",
                "preview_size_limit",
                "ignored_patterns",
                "show_hidden_files"
            ]
            
            for key in expected_keys:
                assert key in settings
                assert settings[key] is not None

    def test_config_ui_update_setting(self):
        """Test updating a single configuration setting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = ConfigManager(config_path)
            
            # Test updating theme
            original_theme = config.theme
            config.set("theme", "dark" if original_theme == "light" else "light")
            assert config.theme != original_theme
            
            # Test updating preview size limit
            config.set("preview_size_limit", 2000000)
            assert config.preview_size_limit == 2000000
            
            # Test updating ignored patterns
            new_patterns = ["*.tmp", "*.log", "*.cache"]
            config.set("ignored_patterns", new_patterns)
            assert config.ignored_patterns == new_patterns

    def test_config_ui_validate_theme(self):
        """Test theme validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = ConfigManager(config_path)
            
            # Valid themes
            for theme in ["light", "dark"]:
                config.set("theme", theme)
                assert config.theme == theme
            
            # Invalid theme should raise ValueError
            with pytest.raises(ValueError):
                config.set("theme", "invalid_theme")

    def test_config_ui_validate_preview_size_limit(self):
        """Test preview size limit validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = ConfigManager(config_path)
            
            # Valid sizes
            for size in [1000, 50000, 1000000, 5000000]:
                config.set("preview_size_limit", size)
                assert config.preview_size_limit == size
            
            # Invalid sizes should raise ValueError
            with pytest.raises(ValueError):
                config.set("preview_size_limit", -1)
            
            with pytest.raises(ValueError):
                config.set("preview_size_limit", 0)

    def test_config_ui_validate_ignored_patterns(self):
        """Test ignored patterns validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = ConfigManager(config_path)
            
            # Valid patterns
            valid_patterns = ["*.tmp", "*.log", "node_modules", ".git"]
            config.set("ignored_patterns", valid_patterns)
            assert config.ignored_patterns == valid_patterns
            
            # Invalid patterns should raise ValueError
            with pytest.raises(ValueError):
                config.set("ignored_patterns", "not_a_list")
            
            with pytest.raises(ValueError):
                config.set("ignored_patterns", ["", "valid_pattern"])

    def test_config_ui_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = ConfigManager(config_path)
            
            # Modify some settings
            config.set("theme", "dark")
            config.set("preview_size_limit", 2000000)
            config.set("ignored_patterns", ["*.custom"])
            
            # Reset all settings
            config.reset_all()
            
            # Verify defaults are restored
            assert config.theme == "dark"  # Default theme
            assert config.preview_size_limit == 1000000  # 1MB default
            assert ".git" in config.ignored_patterns  # Default patterns

    def test_config_ui_persistence(self):
        """Test that configuration changes are persisted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            
            # Create first config instance and modify
            config1 = ConfigManager(config_path)
            config1.set("theme", "dark")
            config1.set("preview_size_limit", 2000000)
            
            # Create second config instance and verify changes persisted
            config2 = ConfigManager(config_path)
            assert config2.theme == "dark"
            assert config2.preview_size_limit == 2000000

    def test_config_ui_invalid_key(self):
        """Test handling of invalid configuration keys."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = ConfigManager(config_path)
            
            # Getting invalid key should return None
            assert config.get("invalid_key") is None
            
            # Setting invalid key should raise ValueError
            with pytest.raises(ValueError):
                config.set("invalid_key", "some_value")

    def test_config_ui_get_setting_with_default(self):
        """Test getting setting with default value."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = ConfigManager(config_path)
            
            # Test getting existing setting
            theme = config.get("theme", "fallback")
            assert theme == config.theme
            
            # Test getting non-existent setting with default
            non_existent = config.get("non_existent_key", "fallback_value")
            assert non_existent == "fallback_value"
