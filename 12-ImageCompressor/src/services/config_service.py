import json
import os
from copy import deepcopy
from typing import Any, Dict, Optional


class ConfigService:
    """
    Application configuration manager.

    Configuration is stored as JSON and automatically created with
    default values when it does not exist.
    """

    DEFAULT_CONFIG_FILE = os.path.join("data", "config.json")

    DEFAULT_CONFIG: Dict[str, Any] = {
        "application": {
            "name": "Image Compressor",
            "version": "1.0.0"
        },
        "compression": {
            "quality": 85,
            "optimize": True,
            "progressive": True
        },
        "conversion": {
            "format": "JPEG"
        },
        "resize": {
            "enabled": False,
            "width": None,
            "height": None,
            "percentage": 100,
            "keep_aspect_ratio": True
        },
        "output": {
            "directory": "output",
            "overwrite": False,
            "create_directory": True
        },
        "history": {
            "enabled": True,
            "max_items": 500
        },
        "interface": {
            "theme": "system",
            "show_preview": True,
            "show_file_size": True,
            "show_progress": True
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_FILE

        self._ensure_directory()
        self._ensure_config()

    # ------------------------------------------------------------------
    # File Management
    # ------------------------------------------------------------------

    def _ensure_directory(self) -> None:
        """
        Create the configuration directory if necessary.
        """
        directory = os.path.dirname(self.config_path)

        if directory:
            os.makedirs(directory, exist_ok=True)

    def _ensure_config(self) -> None:
        """
        Create the configuration file with default values if it
        does not already exist.
        """
        if not os.path.exists(self.config_path):
            self._write_config(deepcopy(self.DEFAULT_CONFIG))

    # ------------------------------------------------------------------
    # Read / Write
    # ------------------------------------------------------------------

    def _read_config(self) -> Dict[str, Any]:
        """
        Read configuration from JSON file.

        Returns:
            Configuration dictionary.
        """
        try:
            with open(
                self.config_path,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if not isinstance(data, dict):
                return deepcopy(self.DEFAULT_CONFIG)

            return self._merge_defaults(
                deepcopy(self.DEFAULT_CONFIG),
                data
            )

        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return deepcopy(self.DEFAULT_CONFIG)

    def _write_config(self, config: Dict[str, Any]) -> bool:
        """
        Write configuration to JSON file.

        Returns:
            True if successful, otherwise False.
        """
        try:
            self._ensure_directory()

            with open(
                self.config_path,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    config,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except (OSError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Default Management
    # ------------------------------------------------------------------

    def _merge_defaults(
        self,
        defaults: Dict[str, Any],
        current: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recursively merge current configuration with defaults.

        Missing settings are automatically restored from defaults.
        """
        for key, default_value in defaults.items():

            if key not in current:
                current[key] = deepcopy(default_value)

            elif isinstance(default_value, dict):

                if not isinstance(current[key], dict):
                    current[key] = deepcopy(default_value)

                else:
                    current[key] = self._merge_defaults(
                        default_value,
                        current[key]
                    )

        return current

    def get_defaults(self) -> Dict[str, Any]:
        """
        Return a copy of the default configuration.
        """
        return deepcopy(self.DEFAULT_CONFIG)

    def reset(self) -> bool:
        """
        Reset all settings to their default values.
        """
        return self._write_config(
            deepcopy(self.DEFAULT_CONFIG)
        )

    # ------------------------------------------------------------------
    # General Access
    # ------------------------------------------------------------------

    def get_all(self) -> Dict[str, Any]:
        """
        Return the complete configuration.
        """
        config = self._read_config()

        # Save automatically if missing default values were added.
        self._write_config(config)

        return config

    def get(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get a configuration value using dot notation.

        Example:
            config.get("compression.quality")
        """
        if not key:
            return default

        config = self.get_all()
        parts = key.split(".")

        current: Any = config

        for part in parts:

            if not isinstance(current, dict):
                return default

            if part not in current:
                return default

            current = current[part]

        return current

    def set(self, key: str, value: Any) -> bool:
        """
        Set a configuration value using dot notation.

        Example:
            config.set("compression.quality", 90)
        """
        if not key:
            return False

        parts = key.split(".")

        if any(not part.strip() for part in parts):
            return False

        config = self.get_all()
        current = config

        for part in parts[:-1]:

            if part not in current:
                current[part] = {}

            if not isinstance(current[part], dict):
                current[part] = {}

            current = current[part]

        current[parts[-1]] = value

        return self._write_config(config)

    def update(self, values: Dict[str, Any]) -> bool:
        """
        Update multiple configuration values.

        Supports nested dictionaries.
        """
        if not isinstance(values, dict):
            return False

        config = self.get_all()

        config = self._deep_update(
            config,
            values
        )

        return self._write_config(config)

    def _deep_update(
        self,
        target: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recursively update a dictionary.
        """
        for key, value in updates.items():

            if (
                isinstance(value, dict)
                and isinstance(target.get(key), dict)
            ):
                target[key] = self._deep_update(
                    target[key],
                    value
                )
            else:
                target[key] = value

        return target

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, key: str) -> bool:
        """
        Delete a configuration value.

        Example:
            config.delete("interface.show_preview")
        """
        if not key:
            return False

        parts = key.split(".")
        config = self.get_all()

        current = config

        for part in parts[:-1]:

            if not isinstance(current, dict):
                return False

            if part not in current:
                return False

            current = current[part]

        last_key = parts[-1]

        if not isinstance(current, dict):
            return False

        if last_key not in current:
            return False

        del current[last_key]

        return self._write_config(config)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate configuration values.

        Returns:
            True when configuration values are valid.
        """
        config = config or self.get_all()

        # Compression quality
        quality = config.get(
            "compression",
            {}
        ).get("quality")

        if not isinstance(quality, int):
            return False

        if not 1 <= quality <= 100:
            return False

        # Conversion format
        image_format = config.get(
            "conversion",
            {}
        ).get("format")

        if image_format not in {
            "JPEG",
            "PNG",
            "WEBP"
        }:
            return False

        # Resize percentage
        percentage = config.get(
            "resize",
            {}
        ).get("percentage")

        if not isinstance(percentage, (int, float)):
            return False

        if percentage <= 0:
            return False

        # History max items
        max_items = config.get(
            "history",
            {}
        ).get("max_items")

        if not isinstance(max_items, int):
            return False

        if max_items < 1:
            return False

        # Theme
        theme = config.get(
            "interface",
            {}
        ).get("theme")

        if theme not in {
            "system",
            "light",
            "dark"
        }:
            return False

        return True

    # ------------------------------------------------------------------
    # Convenience Methods
    # ------------------------------------------------------------------

    def get_compression_quality(self) -> int:
        """
        Return default compression quality.
        """
        return int(
            self.get(
                "compression.quality",
                85
            )
        )

    def set_compression_quality(
        self,
        quality: int
    ) -> bool:
        """
        Set compression quality.
        """
        if not isinstance(quality, int):
            return False

        if not 1 <= quality <= 100:
            return False

        return self.set(
            "compression.quality",
            quality
        )

    def get_output_directory(self) -> str:
        """
        Return configured output directory.
        """
        return str(
            self.get(
                "output.directory",
                "output"
            )
        )

    def set_output_directory(
        self,
        directory: str
    ) -> bool:
        """
        Set output directory.
        """
        if not isinstance(directory, str):
            return False

        directory = directory.strip()

        if not directory:
            return False

        return self.set(
            "output.directory",
            directory
        )

    def get_conversion_format(self) -> str:
        """
        Return default output format.
        """
        return str(
            self.get(
                "conversion.format",
                "JPEG"
            )
        )

    def set_conversion_format(
        self,
        image_format: str
    ) -> bool:
        """
        Set default conversion format.
        """
        if not isinstance(image_format, str):
            return False

        image_format = image_format.upper().strip()

        if image_format not in {
            "JPEG",
            "PNG",
            "WEBP"
        }:
            return False

        return self.set(
            "conversion.format",
            image_format
        )

    def is_history_enabled(self) -> bool:
        """
        Return whether history recording is enabled.
        """
        return bool(
            self.get(
                "history.enabled",
                True
            )
        )

    def set_history_enabled(
        self,
        enabled: bool
    ) -> bool:
        """
        Enable or disable history recording.
        """
        if not isinstance(enabled, bool):
            return False

        return self.set(
            "history.enabled",
            enabled
        )

    def get_theme(self) -> str:
        """
        Return interface theme.
        """
        return str(
            self.get(
                "interface.theme",
                "system"
            )
        )

    def set_theme(self, theme: str) -> bool:
        """
        Set interface theme.
        """
        if not isinstance(theme, str):
            return False

        theme = theme.lower().strip()

        if theme not in {
            "system",
            "light",
            "dark"
        }:
            return False

        return self.set(
            "interface.theme",
            theme
        )

    # ------------------------------------------------------------------
    # File Information
    # ------------------------------------------------------------------

    def get_config_path(self) -> str:
        """
        Return configuration file path.
        """
        return os.path.abspath(
            self.config_path
        )

    def exists(self) -> bool:
        """
        Check whether configuration file exists.
        """
        return os.path.isfile(
            self.config_path
        )

    def get_file_size(self) -> int:
        """
        Return configuration file size in bytes.
        """
        try:
            return os.path.getsize(
                self.config_path
            )
        except OSError:
            return 0

    # ------------------------------------------------------------------
    # Export / Import
    # ------------------------------------------------------------------

    def export_config(
        self,
        output_path: str
    ) -> bool:
        """
        Export current configuration to another JSON file.
        """
        if not output_path:
            return False

        config = self.get_all()

        try:
            directory = os.path.dirname(output_path)

            if directory:
                os.makedirs(
                    directory,
                    exist_ok=True
                )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    config,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            return True

        except (OSError, TypeError):
            return False

    def import_config(
        self,
        input_path: str
    ) -> bool:
        """
        Import configuration from a JSON file.
        """
        if not input_path:
            return False

        try:
            with open(
                input_path,
                "r",
                encoding="utf-8"
            ) as file:
                imported_config = json.load(file)

            if not isinstance(imported_config, dict):
                return False

            config = self._merge_defaults(
                deepcopy(self.DEFAULT_CONFIG),
                imported_config
            )

            if not self.validate(config):
                return False

            return self._write_config(config)

        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError
        ):
            return False

    # ------------------------------------------------------------------
    # Debug / Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"ConfigService("
            f"config_path='{self.get_config_path()}')"
        )


if __name__ == "__main__":
    config = ConfigService()

    print("ConfigService test")
    print("-" * 40)

    print("Config path:")
    print(config.get_config_path())

    print("\nCompression quality:")
    print(config.get_compression_quality())

    print("\nOutput directory:")
    print(config.get_output_directory())

    print("\nConversion format:")
    print(config.get_conversion_format())

    print("\nTheme:")
    print(config.get_theme())

    print("\nConfiguration valid:")
    print(config.validate())

    print("\nComplete configuration:")
    print(json.dumps(
        config.get_all(),
        indent=4,
        ensure_ascii=False
    ))