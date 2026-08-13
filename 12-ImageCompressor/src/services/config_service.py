import json
import os


class ConfigService:
    """
    Application configuration manager.

    Responsibilities:
        - Load application settings
        - Save application settings
        - Update individual settings
        - Reset settings to defaults
        - Validate configuration values
    """

    # ==========================================================
    # DEFAULT SETTINGS
    # ==========================================================

    DEFAULT_CONFIG = {
        # Compression
        "quality": 80,
        "output_format": "WEBP",

        # Optimization
        "smart_optimization": True,
        "auto_resize": False,
        "max_dimension": 1920,

        # Image handling
        "keep_exif": True,
        "preserve_transparency": True,

        # Output
        "overwrite_files": False,
        "auto_open_output": False,

        # Interface
        "show_preview": True,
        "show_statistics": True,

        # History
        "save_history": True,

        # Batch processing
        "batch_quality": 80,
        "batch_format": "WEBP",

        # Performance
        "use_fast_mode": False
    }

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        config_file=None
    ):
        """
        Initialize configuration service.
        """

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )
        )

        data_dir = os.path.join(
            base_dir,
            "data"
        )

        os.makedirs(
            data_dir,
            exist_ok=True
        )

        self.config_file = (
            config_file
            or os.path.join(
                data_dir,
                "config.json"
            )
        )

        self.config = {}

        self.load()

    # ==========================================================
    # LOAD
    # ==========================================================

    def load(self):
        """
        Load configuration from disk.

        Missing settings are automatically filled with
        default values.
        """

        if not os.path.exists(
            self.config_file
        ):

            self.config = (
                self.DEFAULT_CONFIG.copy()
            )

            self.save()

            return self.config.copy()

        try:

            with open(
                self.config_file,
                "r",
                encoding="utf-8"
            ) as file:

                stored_config = json.load(
                    file
                )

            if not isinstance(
                stored_config,
                dict
            ):

                stored_config = {}

        except (
            json.JSONDecodeError,
            OSError
        ):

            stored_config = {}

        # ------------------------------------------------------
        # Start with defaults.
        # ------------------------------------------------------

        self.config = (
            self.DEFAULT_CONFIG.copy()
        )

        # ------------------------------------------------------
        # Apply stored settings.
        # ------------------------------------------------------

        self.config.update(
            stored_config
        )

        # ------------------------------------------------------
        # Validate settings.
        # ------------------------------------------------------

        self.config = (
            self.validate_config(
                self.config
            )
        )

        # ------------------------------------------------------
        # Save normalized configuration.
        # ------------------------------------------------------

        self.save()

        return self.config.copy()

    # ==========================================================
    # SAVE
    # ==========================================================

    def save(self):
        """
        Save current configuration to disk.
        """

        directory = os.path.dirname(
            os.path.abspath(
                self.config_file
            )
        )

        os.makedirs(
            directory,
            exist_ok=True
        )

        temporary_file = (
            self.config_file
            + ".tmp"
        )

        try:

            with open(
                temporary_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.config,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            os.replace(
                temporary_file,
                self.config_file
            )

        except OSError:

            if os.path.exists(
                temporary_file
            ):

                os.remove(
                    temporary_file
                )

            raise

    # ==========================================================
    # GET
    # ==========================================================

    def get(
        self,
        key,
        default=None
    ):
        """
        Get a configuration value.
        """

        return self.config.get(
            key,
            default
        )

    # ==========================================================
    # SET
    # ==========================================================

    def set(
        self,
        key,
        value,
        save=True
    ):
        """
        Update one configuration value.

        Returns:
            Validated value.
        """

        if key not in self.DEFAULT_CONFIG:

            raise KeyError(
                f"Unknown configuration key: "
                f"{key}"
            )

        validated_value = (
            self.validate_value(
                key,
                value
            )
        )

        self.config[key] = (
            validated_value
        )

        if save:
            self.save()

        return validated_value

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        settings,
        save=True
    ):
        """
        Update multiple configuration values.
        """

        if not isinstance(
            settings,
            dict
        ):

            raise TypeError(
                "Settings must be a dictionary."
            )

        for key, value in settings.items():

            if key not in self.DEFAULT_CONFIG:

                continue

            self.config[key] = (
                self.validate_value(
                    key,
                    value
                )
            )

        self.config = (
            self.validate_config(
                self.config
            )
        )

        if save:
            self.save()

        return self.config.copy()

    # ==========================================================
    # GET ALL
    # ==========================================================

    def get_all(self):
        """
        Return a copy of the complete configuration.
        """

        return self.config.copy()

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(
        self,
        save=True
    ):
        """
        Reset all settings to default values.
        """

        self.config = (
            self.DEFAULT_CONFIG.copy()
        )

        if save:
            self.save()

        return self.config.copy()

    # ==========================================================
    # RESET SINGLE VALUE
    # ==========================================================

    def reset_key(
        self,
        key,
        save=True
    ):
        """
        Reset one setting to its default value.
        """

        if key not in self.DEFAULT_CONFIG:

            raise KeyError(
                f"Unknown configuration key: "
                f"{key}"
            )

        self.config[key] = (
            self.DEFAULT_CONFIG[key]
        )

        if save:
            self.save()

        return self.config[key]

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def validate_config(
        self,
        config
    ):
        """
        Validate the complete configuration.
        """

        validated = (
            self.DEFAULT_CONFIG.copy()
        )

        for key, value in config.items():

            if key not in self.DEFAULT_CONFIG:
                continue

            validated[key] = (
                self.validate_value(
                    key,
                    value
                )
            )

        return validated

    # ==========================================================
    # VALIDATE SINGLE VALUE
    # ==========================================================

    @staticmethod
    def validate_value(
        key,
        value
    ):
        """
        Validate and normalize a single setting.
        """

        # ------------------------------------------------------
        # Quality
        # ------------------------------------------------------

        if key in (
            "quality",
            "batch_quality"
        ):

            try:

                value = int(
                    value
                )

            except (
                ValueError,
                TypeError
            ):

                value = 80

            return max(
                1,
                min(
                    100,
                    value
                )
            )

        # ------------------------------------------------------
        # Output format
        # ------------------------------------------------------

        if key in (
            "output_format",
            "batch_format"
        ):

            value = str(
                value
            ).strip().upper()

            if value == "JPEG":
                value = "JPG"

            allowed = (
                "JPG",
                "PNG",
                "WEBP"
            )

            if value not in allowed:

                return "WEBP"

            return value

        # ------------------------------------------------------
        # Max dimension
        # ------------------------------------------------------

        if key == "max_dimension":

            try:

                value = int(
                    value
                )

            except (
                ValueError,
                TypeError
            ):

                value = 1920

            return max(
                1,
                value
            )

        # ------------------------------------------------------
        # Boolean settings
        # ------------------------------------------------------

        boolean_keys = (
            "smart_optimization",
            "auto_resize",
            "keep_exif",
            "preserve_transparency",
            "overwrite_files",
            "auto_open_output",
            "show_preview",
            "show_statistics",
            "save_history",
            "use_fast_mode"
        )

        if key in boolean_keys:

            return ConfigService._to_bool(
                value
            )

        return value

    # ==========================================================
    # BOOLEAN CONVERSION
    # ==========================================================

    @staticmethod
    def _to_bool(
        value
    ):
        """
        Convert common boolean representations
        to a real bool.
        """

        if isinstance(
            value,
            bool
        ):

            return value

        if isinstance(
            value,
            str
        ):

            normalized = (
                value.strip().lower()
            )

            if normalized in (
                "true",
                "1",
                "yes",
                "on",
                "enabled"
            ):

                return True

            if normalized in (
                "false",
                "0",
                "no",
                "off",
                "disabled"
            ):

                return False

        if isinstance(
            value,
            (int, float)
        ):

            return value != 0

        return False

    # ==========================================================
    # EXPORT CONFIG
    # ==========================================================

    def export_config(
        self,
        output_path
    ):
        """
        Export configuration to a JSON file.
        """

        if not output_path:

            raise ValueError(
                "Output path cannot be empty."
            )

        directory = os.path.dirname(
            os.path.abspath(
                output_path
            )
        )

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
                self.config,
                file,
                indent=4,
                ensure_ascii=False
            )

        return output_path

    # ==========================================================
    # IMPORT CONFIG
    # ==========================================================

    def import_config(
        self,
        input_path
    ):
        """
        Import configuration from a JSON file.
        """

        if not os.path.isfile(
            input_path
        ):

            raise FileNotFoundError(
                f"Configuration file not found: "
                f"{input_path}"
            )

        try:

            with open(
                input_path,
                "r",
                encoding="utf-8"
            ) as file:

                imported = json.load(
                    file
                )

        except json.JSONDecodeError:

            raise ValueError(
                "Invalid configuration JSON file."
            )

        if not isinstance(
            imported,
            dict
        ):

            raise ValueError(
                "Configuration must be a JSON object."
            )

        self.update(
            imported
        )

        return self.config.copy()

    # ==========================================================
    # CHECK KEY
    # ==========================================================

    def has(
        self,
        key
    ):
        """
        Check whether a configuration key exists.
        """

        return key in self.config

    # ==========================================================
    # GET DEFAULT
    # ==========================================================

    def get_default(
        self,
        key
    ):
        """
        Get the default value of a setting.
        """

        if key not in self.DEFAULT_CONFIG:

            raise KeyError(
                f"Unknown configuration key: "
                f"{key}"
            )

        return self.DEFAULT_CONFIG[
            key
        ]

    # ==========================================================
    # COMPARE WITH DEFAULTS
    # ==========================================================

    def is_default(
        self,
        key
    ):
        """
        Check whether a setting currently has
        its default value.
        """

        if key not in self.DEFAULT_CONFIG:

            raise KeyError(
                f"Unknown configuration key: "
                f"{key}"
            )

        return (
            self.config.get(key)
            == self.DEFAULT_CONFIG[key]
        )

    # ==========================================================
    # CHANGE DETECTION
    # ==========================================================

    def has_custom_settings(self):
        """
        Check whether the user changed any setting
        from its default value.
        """

        for key, default_value in (
            self.DEFAULT_CONFIG.items()
        ):

            if self.config.get(
                key
            ) != default_value:

                return True

        return False