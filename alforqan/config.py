"""
Description:
This module provides a flexible configuration management system that supports loading, validating,
and saving configuration files in TOML and YAML formats. It allows for structured access to
configuration values using dot notation and includes validation against Pydantic schemas.

Usage:
    config = Config('config.yaml')
    config_value = config.get('some.key')

Authors:
    - M.Abdulrahman Alnaseer (GitHub: https://github.com/abdalrohman)

License: MIT

Requirements:
    - pydantic
    - toml
    - pyyaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError
import toml
import yaml


class Config:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self.config_data: dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load the configuration file based on its extension."""
        if self.config_path.suffix == ".toml":
            self.config_data = toml.load(self.config_path)
        elif self.config_path.suffix in (".yaml", ".yml"):
            with open(self.config_path) as file:
                self.config_data = yaml.safe_load(file)
        else:
            raise ValueError(f"Unsupported file format: {self.config_path.suffix}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the configuration using dot notation."""
        keys = key.split(".")
        value = self.config_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def validate_schema(self, schema: BaseModel) -> None:
        """Validate the configuration against a Pydantic schema."""
        try:
            schema(**self.config_data)
        except ValidationError as e:
            raise ValueError(f"Configuration validation failed: {e}")

    def get_version(self) -> str:
        """Get the version from the configuration file."""
        return self.get("package.version", "Unknown")

    def get_package_metadata(self) -> dict[str, Any]:
        """Get the package metadata from the configuration file."""
        return self.get("package", {})

    def set(self, key: str, value: Any) -> None:
        """Set a value in the configuration using dot notation."""
        keys = key.split(".")
        data = self.config_data
        for k in keys[:-1]:
            data = data.setdefault(k, {})
        data[keys[-1]] = value

    def save(self) -> None:
        """Save the current configuration back to the file."""
        if self.config_path.suffix == ".toml":
            with open(self.config_path, "w") as file:
                toml.dump(self.config_data, file)
        elif self.config_path.suffix in (".yaml", ".yml"):
            with open(self.config_path, "w") as file:
                yaml.dump(self.config_data, file)

    def get_all(self) -> dict[str, Any]:
        """Get the entire configuration as a dictionary."""
        return self.config_data

    def validate_types(self, type_schema: dict[str, type]) -> list[str]:
        """Validate types of configuration values against a schema."""
        errors = []
        for key, expected_type in type_schema.items():
            value = self.get(key)
            if value is not None and not isinstance(value, expected_type):
                errors.append(f"Type mismatch for '{key}': expected {expected_type}, got {type(value)}")
        return errors

    def get_nested(self, keys: list[str], default: Any = None) -> Any:
        """Get a nested value from the configuration."""
        value = self.config_data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value

    def has_key(self, key: str) -> bool:
        """Check if a key exists in the configuration."""
        return self.get(key) is not None

    def get_keys(self, prefix: str = "") -> list[str]:
        """Get all keys in the configuration, optionally filtered by prefix."""

        def traverse(data: dict[str, Any], current_prefix: str) -> list[str]:
            keys = []
            for key, value in data.items():
                full_key = f"{current_prefix}.{key}" if current_prefix else key
                if isinstance(value, dict):
                    keys.extend(traverse(value, full_key))
                else:
                    keys.append(full_key)
            return keys

        all_keys = traverse(self.config_data, "")
        return [key for key in all_keys if key.startswith(prefix)]
