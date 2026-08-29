import os

from PIL import Image


class ImageOptimizer:
    """
    Image optimization engine.

    Handles format-specific optimization such as:
        - JPEG optimization
        - PNG optimization
        - WebP optimization
        - Metadata removal
        - EXIF handling
        - Progressive JPEG
        - Palette optimization
    """

    SUPPORTED_FORMATS = {
        "JPG",
        "JPEG",
        "PNG",
        "WEBP",
    }

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        remove_metadata=True,
        progressive=True
    ):
        """
        Initialize optimizer.

        Args:
            remove_metadata:
                Remove unnecessary image metadata.

            progressive:
                Use progressive JPEG when possible.
        """

        self.remove_metadata = (
            remove_metadata
        )

        self.progressive = (
            progressive
        )

    # ==========================================================
    # FORMAT HELPERS
    # ==========================================================

    @staticmethod
    def normalize_format(
        image_format
    ):
        """
        Normalize image format.
        """

        if not image_format:

            return ""

        normalized = str(
            image_format
        ).strip().upper()

        normalized = normalized.replace(
            ".",
            ""
        )

        if normalized == "JPEG":

            return "JPG"

        return normalized

    # ==========================================================
    # IMAGE VALIDATION
    # ==========================================================

    @staticmethod
    def validate_image(
        image_path
    ):
        """
        Validate whether a file can be opened as an image.
        """

        if not image_path:

            raise ValueError(
                "Image path cannot be empty."
            )

        if not os.path.isfile(
            image_path
        ):

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        try:

            with Image.open(
                image_path
            ) as image:

                image.verify()

            return True

        except Exception as error:

            raise ValueError(
                f"Invalid image file: {error}"
            )

    # ==========================================================
    # METADATA
    # ==========================================================

    @staticmethod
    def remove_image_metadata(
        image
    ):
        """
        Remove image metadata by creating a clean copy.

        This prevents unnecessary EXIF and application-specific
        metadata from being carried into the optimized image.
        """

        try:

            clean_image = Image.new(
                image.mode,
                image.size
            )

            clean_image.putdata(
                list(
                    image.getdata()
                )
            )

            return clean_image

        except Exception:

            return image.copy()

    # ==========================================================
    # JPEG OPTIMIZATION
    # ==========================================================

    def optimize_jpeg(
        self,
        image,
        quality=80
    ):
        """
        Prepare a JPEG image for optimized saving.
        """

        quality = self._validate_quality(
            quality
        )

        # JPEG does not support transparency.
        if image.mode in (
            "RGBA",
            "LA",
            "P"
        ):

            if image.mode == "P":

                image = image.convert(
                    "RGBA"
                )

            if image.mode in (
                "RGBA",
                "LA"
            ):

                background = Image.new(
                    "RGB",
                    image.size,
                    "white"
                )

                alpha = image.getchannel(
                    "A"
                )

                background.paste(
                    image,
                    mask=alpha
                )

                image = background

            else:

                image = image.convert(
                    "RGB"
                )

        elif image.mode != "RGB":

            image = image.convert(
                "RGB"
            )

        if self.remove_metadata:

            image = self.remove_image_metadata(
                image
            )

        save_options = {
            "format": "JPEG",
            "quality": quality,
            "optimize": True,
        }

        if self.progressive:

            save_options[
                "progressive"
            ] = True

        return image, save_options

    # ==========================================================
    # PNG OPTIMIZATION
    # ==========================================================

    def optimize_png(
        self,
        image
    ):
        """
        Prepare PNG image for optimized saving.

        PNG compression is lossless, so JPEG-style quality
        is intentionally not applied.
        """

        if self.remove_metadata:

            image = self.remove_image_metadata(
                image
            )

        save_options = {
            "format": "PNG",
            "optimize": True,
        }

        return image, save_options

    # ==========================================================
    # WEBP OPTIMIZATION
    # ==========================================================

    def optimize_webp(
        self,
        image,
        quality=80,
        lossless=False
    ):
        """
        Prepare WebP image for optimized saving.

        Args:
            quality:
                WebP quality from 1 to 100.

            lossless:
                Whether to use lossless WebP.
        """

        quality = self._validate_quality(
            quality
        )

        if self.remove_metadata:

            image = self.remove_image_metadata(
                image
            )

        save_options = {
            "format": "WEBP",
            "method": 6,
        }

        if lossless:

            save_options[
                "lossless"
            ] = True

        else:

            save_options[
                "quality"
            ] = quality

        return image, save_options

    # ==========================================================
    # GENERAL OPTIMIZATION
    # ==========================================================

    def optimize(
        self,
        image_path,
        output_path,
        output_format=None,
        quality=80,
        webp_lossless=False
    ):
        """
        Optimize and save an image.

        Args:
            image_path:
                Original image path.

            output_path:
                Destination path.

            output_format:
                JPG, PNG or WEBP.

            quality:
                Compression quality.

            webp_lossless:
                Use lossless WebP.

        Returns:
            Dictionary containing optimization information.
        """

        self.validate_image(
            image_path
        )

        if not output_path:

            raise ValueError(
                "Output path cannot be empty."
            )

        os.makedirs(
            os.path.dirname(
                os.path.abspath(
                    output_path
                )
            ),
            exist_ok=True
        )

        with Image.open(
            image_path
        ) as original_image:

            source_format = (
                self.normalize_format(
                    original_image.format
                )
            )

            if output_format:

                target_format = (
                    self.normalize_format(
                        output_format
                    )
                )

            else:

                target_format = (
                    source_format
                )

            if target_format == "JPG":

                image, save_options = (
                    self.optimize_jpeg(
                        original_image,
                        quality
                    )
                )

            elif target_format == "PNG":

                image, save_options = (
                    self.optimize_png(
                        original_image
                    )
                )

            elif target_format == "WEBP":

                image, save_options = (
                    self.optimize_webp(
                        original_image,
                        quality,
                        webp_lossless
                    )
                )

            else:

                raise ValueError(
                    (
                        "Unsupported output format: "
                        f"{target_format}"
                    )
                )

            image.save(
                output_path,
                **save_options
            )

        original_size = os.path.getsize(
            image_path
        )

        optimized_size = os.path.getsize(
            output_path
        )

        saved_bytes = max(
            0,
            original_size - optimized_size
        )

        saving_percentage = (
            (
                saved_bytes
                / original_size
            ) * 100
            if original_size > 0
            else 0
        )

        return {
            "success": True,
            "input_path": image_path,
            "output_path": output_path,
            "source_format": source_format,
            "output_format": target_format,
            "original_size": original_size,
            "optimized_size": optimized_size,
            "saved_bytes": saved_bytes,
            "saving_percentage": round(
                saving_percentage,
                2
            ),
            "metadata_removed": (
                self.remove_metadata
            ),
        }

    # ==========================================================
    # OPTIMIZATION LEVEL
    # ==========================================================

    def optimize_with_level(
        self,
        image_path,
        output_path,
        level="balanced"
    ):
        """
        Optimize an image using a predefined optimization level.

        Levels:
            light
            balanced
            aggressive
        """

        level = str(
            level
        ).strip().lower()

        levels = {
            "light": {
                "quality": 90,
                "webp_lossless": False,
            },

            "balanced": {
                "quality": 80,
                "webp_lossless": False,
            },

            "aggressive": {
                "quality": 60,
                "webp_lossless": False,
            },
        }

        if level not in levels:

            raise ValueError(
                (
                    "Invalid optimization level. "
                    "Choose: light, balanced or aggressive."
                )
            )

        settings = levels[
            level
        ]

        return self.optimize(
            image_path=image_path,
            output_path=output_path,
            quality=settings[
                "quality"
            ],
            webp_lossless=settings[
                "webp_lossless"
            ]
        )

    # ==========================================================
    # QUALITY VALIDATION
    # ==========================================================

    @staticmethod
    def _validate_quality(
        quality
    ):
        """
        Validate quality between 1 and 100.
        """

        try:

            quality = int(
                quality
            )

        except (
            ValueError,
            TypeError
        ):

            quality = 80

        return max(
            1,
            min(
                100,
                quality
            )
        )

    # ==========================================================
    # ESTIMATE COMPRESSION
    # ==========================================================

    @staticmethod
    def estimate_compression(
        original_size,
        quality=80
    ):
        """
        Estimate approximate output size.

        This is only an estimation and should not be treated
        as the actual compressed size.
        """

        try:

            original_size = float(
                original_size
            )

            quality = int(
                quality
            )

        except (
            ValueError,
            TypeError
        ):

            return 0

        quality = max(
            1,
            min(
                100,
                quality
            )
        )

        if original_size <= 0:

            return 0

        # Approximate relationship for UI previews.
        compression_factor = (
            0.15
            + (
                quality / 100
            ) * 0.65
        )

        estimated_size = (
            original_size
            * compression_factor
        )

        return int(
            estimated_size
        )

    # ==========================================================
    # COMPARE OPTIMIZATION
    # ==========================================================

    @staticmethod
    def compare_sizes(
        original_path,
        optimized_path
    ):
        """
        Compare original and optimized file sizes.
        """

        if not os.path.isfile(
            original_path
        ):

            raise FileNotFoundError(
                original_path
            )

        if not os.path.isfile(
            optimized_path
        ):

            raise FileNotFoundError(
                optimized_path
            )

        original_size = os.path.getsize(
            original_path
        )

        optimized_size = os.path.getsize(
            optimized_path
        )

        saved_bytes = (
            original_size
            - optimized_size
        )

        saving_percentage = (
            (
                saved_bytes
                / original_size
            ) * 100
            if original_size > 0
            else 0
        )

        return {
            "original_size": original_size,
            "optimized_size": optimized_size,
            "saved_bytes": saved_bytes,
            "saving_percentage": round(
                saving_percentage,
                2
            ),
        }

    # ==========================================================
    # BATCH OPTIMIZATION
    # ==========================================================

    def optimize_batch(
        self,
        image_paths,
        output_directory,
        output_format=None,
        quality=80
    ):
        """
        Optimize multiple images.
        """

        if not image_paths:

            return []

        if not output_directory:

            raise ValueError(
                "Output directory cannot be empty."
            )

        os.makedirs(
            output_directory,
            exist_ok=True
        )

        results = []

        for image_path in image_paths:

            filename = os.path.basename(
                image_path
            )

            name, extension = (
                os.path.splitext(
                    filename
                )
            )

            target_format = (
                self.normalize_format(
                    output_format
                )
                if output_format
                else self.normalize_format(
                    extension
                )
            )

            extension_map = {
                "JPG": ".jpg",
                "PNG": ".png",
                "WEBP": ".webp",
            }

            target_extension = (
                extension_map.get(
                    target_format,
                    extension
                )
            )

            output_filename = (
                f"{name}_optimized"
                f"{target_extension}"
            )

            output_path = os.path.join(
                output_directory,
                output_filename
            )

            output_path = (
                self._get_unique_path(
                    output_path
                )
            )

            try:

                result = self.optimize(
                    image_path=image_path,
                    output_path=output_path,
                    output_format=output_format,
                    quality=quality
                )

                results.append(
                    result
                )

            except Exception as error:

                results.append(
                    {
                        "success": False,
                        "input_path": image_path,
                        "output_path": output_path,
                        "error": str(
                            error
                        ),
                    }
                )

        return results

    # ==========================================================
    # UNIQUE PATH
    # ==========================================================

    @staticmethod
    def _get_unique_path(
        file_path
    ):
        """
        Return a unique path without overwriting files.
        """

        if not os.path.exists(
            file_path
        ):

            return file_path

        directory = os.path.dirname(
            file_path
        )

        filename = os.path.basename(
            file_path
        )

        name, extension = (
            os.path.splitext(
                filename
            )
        )

        counter = 1

        while True:

            candidate = os.path.join(
                directory,
                f"{name}_{counter}"
                f"{extension}"
            )

            if not os.path.exists(
                candidate
            ):

                return candidate

            counter += 1

    # ==========================================================
    # SUPPORTED FORMAT
    # ==========================================================

    @classmethod
    def is_supported_format(
        cls,
        image_format
    ):
        """
        Check if image format is supported.
        """

        normalized = cls.normalize_format(
            image_format
        )

        return normalized in (
            "JPG",
            "PNG",
            "WEBP"
        )


# ==============================================================
# SIMPLE TEST
# ==============================================================

if __name__ == "__main__":

    optimizer = ImageOptimizer()

    print(
        "ImageOptimizer initialized."
    )

    print(
        "Supported formats:",
        ", ".join(
            sorted(
                optimizer.SUPPORTED_FORMATS
            )
        )
    )

    print(
        "Estimated size for 10 MB at quality 80:",
        optimizer.estimate_compression(
            10 * 1024 * 1024,
            80
        ),
        "bytes"
    )