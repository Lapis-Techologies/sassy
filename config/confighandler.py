import os
import json
from typing import Any, List, Union


class ConfigHandler:
    """
    Base Configuration Handler

    Manages configuration data with support for nested dictionary access,
    key validation, and configuration integrity verification.

    Attributes:
        _config (Dict): The internal configuration dictionary
    """

    class error:
        class ConfigError(Exception):
            """Exception raised for configuration integrity or access errors"""

            pass

    def __init__(self):
        """Initialize an empty configuration handler"""
        self._config = {}
        self._schema = None

    @property
    def config(self) -> dict:
        """
        Get the full configuration dictionary

        Returns:
            dict: The current configuration dictionary
        """
        return self._config

    def set_config(self, config_obj: Union[str, dict, Any]) -> None:
        """
        Set the configuration from a file path, dictionary, or another ConfigHandler

        Args:
            config_obj: Configuration source (file path, dictionary, or ConfigHandler)

        Raises:
            ConfigError: If the configuration is invalid or cannot be loaded
        """
        config = self._verify_config_integrity(config_obj)
        self._config = config

    def get(self, *args) -> Any:
        """
        Retrieve a value from the configuration

        Args:
            *args: A sequence of keys to traverse the configuration

        Returns:
            Any: The value at the specified path

        Raises:
            KeyError: If a key doesn't exist, with suggestions for available keys
        """
        result = self._config
        path = []

        for arg in args:
            path.append(arg)
            try:
                result = result[arg]
            except KeyError:
                available_keys = []
                if isinstance(result, dict):
                    available_keys = list(result.keys())

                path_str = ".".join(path[:-1]) if path[:-1] else "root"
                suggestions = (
                    f"Available keys: {', '.join(available_keys)}"
                    if available_keys
                    else "No keys available"
                )
                error_msg = f"Key '{arg}' not found at '{path_str}'. {suggestions}"
                raise KeyError(error_msg)

        return result

    def get_or_default(self, default: Any, *args) -> Any:
        """
        Get a configuration value or return a default if the path doesn't exist

        Args:
            default: The default value to return if the path doesn't exist
            *args: A sequence of keys to traverse the configuration

        Returns:
            Any: The value at the specified path or the default value
        """
        try:
            return self.get(*args)
        except KeyError:
            return default

    def set(self, *args, value: Any) -> None:
        """
        Set a value in the configuration at the specified path

        Args:
            *args: A sequence of keys defining the path
            value: The value to set

        Raises:
            ConfigError: If no keys are provided
        """
        if not args:
            raise self.error.ConfigError("At least one key must be provided")

        last_key = args[-1]
        config = self._config

        for key in args[:-1]:
            if key not in config:
                config[key] = {}
            elif not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]

        config[last_key] = value

    def keys(self, *args) -> List[str]:
        """
        Get available keys at a specific path in the configuration

        Args:
            *args: A sequence of keys defining the path

        Returns:
            List[str]: List of available keys at the specified path
        """
        if not args:
            return list(self._config.keys())

        try:
            result = self.get(*args)
            if isinstance(result, dict):
                return list(result.keys())
            else:
                return []
        except KeyError:
            return []

    def _verify_config_integrity(self, config_obj: Union[str, dict, Any]) -> dict:
        """
        Verify and load configuration from various sources

        Args:
            config_obj: Configuration source (file path, dictionary, or ConfigHandler)

        Returns:
            dict: Verified configuration dictionary

        Raises:
            ConfigError: If the configuration is invalid or cannot be loaded
        """
        if isinstance(config_obj, dict):
            return config_obj
        elif isinstance(config_obj, ConfigHandler):
            return config_obj.config
        if not os.path.exists(config_obj):
            raise self.error.ConfigError(f"Configuration file not found: {config_obj}")
        try:
            with open(config_obj, "r") as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise self.error.ConfigError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise self.error.ConfigError(f"Failed to load configuration: {e}")
