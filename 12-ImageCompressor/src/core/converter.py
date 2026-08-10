
import os

from PIL import Image


class ImageConverter:
    """
    Image format conversion engine.

    Supported formats:

        JPG / JPEG
        PNG
        WEBP

    This class is responsible only for format conversion.
    Compression and optimization are handled by other
    classes.
    """

    SUPPORTED_FORMATS = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    )

    # ==========================================================
    # CONVERSION
    # ==========================================================

    def convert(
        self,
        input_path,
        output_path,
        quality=90,
        keep_exif=True
    ):
        """
        Convert an image from one format to another.

        Parameters:
            input_path:
                Source image path.

            output_path:
                Destination image path.

            quality:
                Quality used for JPEG / WEBP.

            keep_exif:
                Preserve EXIF metadata when possible.

        Returns:
            Dictionary containing conversion information.
        """

        self._validate_input(
            input_path
        )

        self._validate_output(
            output_path
        )

        quality = self._validate_quality(
            quality
        )

        source_extension = (
            self._get_extension(
                input_path
            )
        )

        target_extension = (
            self._get_extension(
                output_path
            )
        )

        if target_extension not in self.SUPPORTED_FORMATS:

            raise ValueError(
                f"Unsupported output format: "
                f"{target_extension}"
            )

        # ------------------------------------------------------
        # Open source image
        # ------------------------------------------------------

        with Image.open(
            input_path
        ) as source_image:

            original_size = os.path.getsize(
                input_path
            )

            original_resolution = (
                source_image.size
            )

            original_format = (
                source_image.format
                or source_extension
            )

            exif = source_image.info.get(
                "exif"
            )

            # --------------------------------------------------
            # Copy image
            # --------------------------------------------------

            image = source_image.copy()

            # --------------------------------------------------
            # Prepare image according to target format
            # --------------------------------------------------

            image = self._prepare_image(
                image,
                target_extension
            )

            # --------------------------------------------------
            # Build save options
            # --------------------------------------------------

            save_options = (
                self._build_save_options(
                    target_extension,
                    quality,
                    exif,
                    keep_exif
                )
            )

            # --------------------------------------------------
            # Save
            # --------------------------------------------------

            image.save(
                output_path,
                **save_options
            )

        # ------------------------------------------------------
        # Result information
        # ------------------------------------------------------

        new_size = os.path.getsize(
            output_path
        )

        return {
            "input_path": input_path,
            "output_path": output_path,

            "source_format": (
                str(
                    original_format
                ).replace(
                    ".",
                    ""
                ).upper()
            ),

            "target_format": (
                target_extension
                .replace(
                    ".",
                    ""
                )
                .upper()
            ),

            "original_size": original_size,

            "new_size": new_size,

            "saved_bytes": max(
                0,
                original_size - new_size
            ),

            "saving_percentage": (
                self._calculate_saving(
                    original_size,
                    new_size
                )
            ),

            "original_resolution": (
                original_resolution
            ),

            "new_resolution": (
                image.size
            )
        }

    # ==========================================================
    # BATCH CONVERSION
    # ==========================================================

    def batch_convert(
        self,
        input_folder,
        output_folder,
        target_format,
        quality=90,
        keep_exif=True
    ):
        """
        Convert all supported images in a folder.

        Returns a list containing successful and failed
        conversion results.
        """

        if not os.path.isdir(
            input_folder
        ):

            raise ValueError(
                f"Input folder does not exist: "
                f"{input_folder}"
            )

        target_format = (
            self._normalize_extension(
                target_format
            )
        )

        if target_format not in self.SUPPORTED_FORMATS:

            raise ValueError(
                f"Unsupported target format: "
                f"{target_format}"
            )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        results = []

        for filename in os.listdir(
            input_folder
        ):

            input_path = os.path.join(
                input_folder,
                filename
            )

            if not os.path.isfile(
                input_path
            ):
                continue

            source_extension = (
                self._get_extension(
                    input_path
                )
            )

            if source_extension not in (
                self.SUPPORTED_FORMATS
            ):
                continue

            base_name = os.path.splitext(
                filename
            )[0]

            output_filename = (
                f"{base_name}"
                f"{target_format}"
            )

            output_path = os.path.join(
                output_folder,
                output_filename
            )

            # Prevent overwriting files.
            output_path = (
                self._unique_output_path(
                    output_path
                )
            )

            try:

                result = self.convert(
                    input_path=input_path,
                    output_path=output_path,
                    quality=quality,
                    keep_exif=keep_exif
                )

                result["filename"] = filename
                result["success"] = True

                results.append(
                    result
                )

            except Exception as error:

                results.append({
                    "filename": filename,
                    "success": False,
                    "error": str(error)
                })

        return results

    # ==========================================================
    # IMAGE PREPARATION
    # ==========================================================

    @staticmethod
    def _prepare_image(
        image,
        target_extension
    ):
        """
        Prepare image for the destination format.

        JPEG does not support alpha channels, therefore
        transparent images are converted to RGB.
        """

        if target_extension in (
            ".jpg",
            ".jpeg"
        ):

            if image.mode in (
                "RGBA",
                "LA",
                "P"
            ):

                # ------------------------------------------------
                # Handle transparency.
                #
                # Instead of blindly dropping alpha values,
                # composite the image onto a white background.
                # ------------------------------------------------

                if image.mode in (
                    "RGBA",
                    "LA"
                ):

                    rgba_image = image.convert(
                        "RGBA"
                    )

                    background = Image.new(
                        "RGB",
                        rgba_image.size,
                        "white"
                    )

                    background.paste(
                        rgba_image,
                        mask=rgba_image.getchannel(
                            "A"
                        )
                    )

                    image = background

                else:

                    image = image.convert(
                        "RGB"
                    )

        elif target_extension == ".png":

            # PNG supports RGB, RGBA and several other modes.
            #
            # We only convert unusual modes when necessary.
            if image.mode not in (
                "1",
                "L",
                "LA",
                "P",
                "RGB",
                "RGBA"
            ):

                image = image.convert(
                    "RGBA"
                )

        elif target_extension == ".webp":

            # WEBP supports RGB and RGBA.
            if image.mode not in (
                "RGB",
                "RGBA"
            ):

                if image.mode in (
                    "P",
                    "LA"
                ):

                    image = image.convert(
                        "RGBA"
                    )

                else:

                    image = image.convert(
                        "RGB"
                    )

        return image

    # ==========================================================
    # SAVE OPTIONS
    # ==========================================================

    @staticmethod
    def _build_save_options(
        target_extension,
        quality,
        exif,
        keep_exif
    ):
        """
        Create format-specific Pillow save options.
        """

        # ------------------------------------------------------
        # JPEG
        # ------------------------------------------------------

        if target_extension in (
            ".jpg",
            ".jpeg"
        ):

            options = {
                "format": "JPEG",
                "quality": quality,
                "optimize": True,
                "progressive": True
            }

            if keep_exif and exif:

                options["exif"] = exif

            return options

        # ------------------------------------------------------
        # WEBP
        # ------------------------------------------------------

        if target_extension == ".webp":

            options = {
                "format": "WEBP",
                "quality": quality,
                "method": 6
            }

            if keep_exif and exif:

                options["exif"] = exif

            return options

        # ------------------------------------------------------
        # PNG
        # ------------------------------------------------------

        if target_extension == ".png":

            return {
                "format": "PNG",
                "optimize": True,
                "compress_level": 9
            }

        raise ValueError(
            f"Unsupported format: "
            f"{target_extension}"
        )

    # ==========================================================
    # FORMAT HELPERS
    # ==========================================================

    @classmethod
    def is_supported(
        cls,
        path
    ):
        """
        Check whether a file uses a supported format.
        """

        extension = os.path.splitext(
            path
        )[1].lower()

        return extension in cls.SUPPORTED_FORMATS

    @staticmethod
    def _normalize_extension(
        extension
    ):
        """
        Normalize format names.

        Examples:

            jpg
            .jpg
            JPEG
            .JPEG

        all become:

            .jpg
        """

        extension = str(
            extension
        ).strip().lower()

        if not extension.startswith(
            "."
        ):

            extension = (
                "."
                + extension
            )

        if extension == ".jpeg":

            return ".jpg"

        return extension

    @staticmethod
    def _get_extension(
        path
    ):
        """
        Get normalized file extension.
        """

        extension = os.path.splitext(
            path
        )[1].lower()

        if extension == ".jpeg":

            return ".jpg"

        return extension

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def _validate_input(
        self,
        input_path
    ):
        """
        Validate source image.
        """

        if not input_path:

            raise ValueError(
                "Input path cannot be empty."
            )

        if not os.path.isfile(
            input_path
        ):

            raise FileNotFoundError(
                f"Input file not found: "
                f"{input_path}"
            )

        if not self.is_supported(
            input_path
        ):

            extension = self._get_extension(
                input_path
            )

            raise ValueError(
                f"Unsupported input format: "
                f"{extension}"
            )

    def _validate_output(
        self,
        output_path
    ):
        """
        Validate output path and format.
        """

        if not output_path:

            raise ValueError(
                "Output path cannot be empty."
            )

        extension = self._get_extension(
            output_path
        )

        if extension not in self.SUPPORTED_FORMATS:

            raise ValueError(
                f"Unsupported output format: "
                f"{extension}"
            )

        output_directory = os.path.dirname(
            os.path.abspath(
                output_path
            )
        )

        os.makedirs(
            output_directory,
            exist_ok=True
        )

    # ==========================================================
    # QUALITY VALIDATION
    # ==========================================================

    @staticmethod
    def _validate_quality(
        quality
    ):
        """
        Keep quality between 1 and 100.
        """

        try:

            quality = int(
                quality
            )

        except (
            ValueError,
            TypeError
        ):

            quality = 90

        return max(
            1,
            min(
                100,
                quality
            )
        )

    # ==========================================================
    # CALCULATIONS
    # ==========================================================

    @staticmethod
    def _calculate_saving(
        original_size,
        new_size
    ):
        """
        Calculate percentage of saved space.
        """

        if original_size <= 0:

            return 0

        saving = (
            (
                original_size
                - new_size
            )
            / original_size
        ) * 100

        return round(
            max(
                0,
                saving
            ),
            2
        )

    # ==========================================================
    # UNIQUE OUTPUT PATH
    # ==========================================================

    @staticmethod
    def _unique_output_path(
        path
    ):
        """
        Prevent overwriting an existing file.

        Example:

            image.webp
            image_1.webp
            image_2.webp
        """

        if not os.path.exists(
            path
        ):

            return path

        directory = os.path.dirname(
            path
        )

        filename = os.path.basename(
            path
        )

        name, extension = (
            os.path.splitext(
                filename
            )
        )

        counter = 1

        while True:

            new_filename = (
                f"{name}_{counter}"
                f"{extension}"
            )

            new_path = os.path.join(
                directory,
                new_filename
            )

            if not os.path.exists(
                new_path
            ):

                return new_path

            counter += 1

