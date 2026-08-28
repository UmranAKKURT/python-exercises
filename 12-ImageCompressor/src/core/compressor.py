import os
import time

from PIL import Image


class ImageCompressor:
    """
    Core image compression engine.

    Supports:
        - JPEG compression
        - PNG optimization
        - WebP compression
        - Quality control
        - Output format conversion
        - Compression statistics
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
        quality=80
    ):
        """
        Initialize the compression engine.

        Args:
            quality: Compression quality from 1 to 100.
        """

        self.quality = self._validate_quality(
            quality
        )

    # ==========================================================
    # QUALITY
    # ==========================================================

    @staticmethod
    def _validate_quality(
        quality
    ):
        """
        Validate and normalize quality value.
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

    def set_quality(
        self,
        quality
    ):
        """
        Update compression quality.
        """

        self.quality = self._validate_quality(
            quality
        )

    # ==========================================================
    # FILE VALIDATION
    # ==========================================================

    @staticmethod
    def _validate_input_file(
        input_path
    ):
        """
        Validate input image path.
        """

        if not input_path:

            raise ValueError(
                "Input file path cannot be empty."
            )

        if not os.path.isfile(
            input_path
        ):

            raise FileNotFoundError(
                f"Image file not found: {input_path}"
            )

        return True

    # ==========================================================
    # DIRECTORY
    # ==========================================================

    @staticmethod
    def _ensure_output_directory(
        output_path
    ):
        """
        Create output directory if necessary.
        """

        directory = os.path.dirname(
            os.path.abspath(
                output_path
            )
        )

        if directory:

            os.makedirs(
                directory,
                exist_ok=True
            )

    # ==========================================================
    # FORMAT
    # ==========================================================

    @staticmethod
    def _normalize_format(
        image_format
    ):
        """
        Normalize image format.
        """

        if not image_format:

            return None

        image_format = str(
            image_format
        ).strip().upper()

        image_format = image_format.replace(
            ".",
            ""
        )

        if image_format == "JPEG":

            return "JPG"

        return image_format

    @staticmethod
    def _get_output_format(
        input_path,
        output_path,
        output_format=None
    ):
        """
        Determine output image format.
        """

        if output_format:

            normalized = (
                ImageCompressor
                ._normalize_format(
                    output_format
                )
            )

            if normalized in (
                "JPG",
                "PNG",
                "WEBP"
            ):

                return normalized

        extension = (
            os.path.splitext(
                output_path
            )[1]
            .lower()
        )

        extension_map = {
            ".jpg": "JPG",
            ".jpeg": "JPG",
            ".png": "PNG",
            ".webp": "WEBP",
        }

        if extension in extension_map:

            return extension_map[
                extension
            ]

        input_extension = (
            os.path.splitext(
                input_path
            )[1]
            .lower()
        )

        if input_extension in extension_map:

            return extension_map[
                input_extension
            ]

        return "JPG"

    # ==========================================================
    # IMAGE MODE
    # ==========================================================

    @staticmethod
    def _prepare_image_for_format(
        image,
        output_format
    ):
        """
        Prepare image mode for the target format.

        JPEG does not support RGBA or palette transparency,
        therefore such images are converted to RGB.
        """

        if output_format == "JPG":

            if image.mode in (
                "RGBA",
                "LA",
                "P"
            ):

                background = Image.new(
                    "RGB",
                    image.size,
                    "white"
                )

                if image.mode == "P":

                    image = image.convert(
                        "RGBA"
                    )

                if image.mode in (
                    "RGBA",
                    "LA"
                ):

                    background.paste(
                        image,
                        mask=image.getchannel(
                            "A"
                        )
                    )

                    return background

                return image.convert(
                    "RGB"
                )

            if image.mode != "RGB":

                return image.convert(
                    "RGB"
                )

        return image

    # ==========================================================
    # SAVE OPTIONS
    # ==========================================================

    def _get_save_options(
        self,
        output_format
    ):
        """
        Return format-specific Pillow save options.
        """

        if output_format == "JPG":

            return {
                "format": "JPEG",
                "quality": self.quality,
                "optimize": True,
                "progressive": True,
            }

        if output_format == "PNG":

            # PNG does not use the JPEG-style quality parameter.
            # optimize=True reduces unnecessary metadata and
            # improves compression efficiency.
            return {
                "format": "PNG",
                "optimize": True,
            }

        if output_format == "WEBP":

            return {
                "format": "WEBP",
                "quality": self.quality,
                "method": 6,
            }

        raise ValueError(
            f"Unsupported output format: {output_format}"
        )

    # ==========================================================
    # SINGLE IMAGE COMPRESSION
    # ==========================================================

    def compress(
        self,
        input_path,
        output_path,
        output_format=None
    ):
        """
        Compress a single image.

        Args:
            input_path:
                Path to original image.

            output_path:
                Path where compressed image will be saved.

            output_format:
                Optional target format.

        Returns:
            dict containing compression statistics.
        """

        start_time = time.perf_counter()

        self._validate_input_file(
            input_path
        )

        if not output_path:

            raise ValueError(
                "Output path cannot be empty."
            )

        output_format = (
            self._get_output_format(
                input_path,
                output_path,
                output_format
            )
        )

        original_size = os.path.getsize(
            input_path
        )

        self._ensure_output_directory(
            output_path
        )

        try:

            with Image.open(
                input_path
            ) as image:

                original_width, original_height = (
                    image.size
                )

                image = (
                    self._prepare_image_for_format(
                        image,
                        output_format
                    )
                )

                save_options = (
                    self._get_save_options(
                        output_format
                    )
                )

                image.save(
                    output_path,
                    **save_options
                )

            new_size = os.path.getsize(
                output_path
            )

            processing_time = (
                time.perf_counter()
                - start_time
            )

            saved_bytes = max(
                0,
                original_size - new_size
            )

            saving_percentage = (
                (
                    saved_bytes
                    / original_size
                ) * 100
                if original_size > 0
                else 0
            )

            compression_ratio = (
                original_size / new_size
                if new_size > 0
                else 0
            )

            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "filename": os.path.basename(
                    input_path
                ),
                "original_size": original_size,
                "new_size": new_size,
                "saved_bytes": saved_bytes,
                "saving_percentage": round(
                    saving_percentage,
                    2
                ),
                "compression_ratio": round(
                    compression_ratio,
                    2
                ),
                "processing_time": round(
                    processing_time,
                    4
                ),
                "quality": self.quality,
                "output_format": output_format,
                "original_width": original_width,
                "original_height": original_height,
            }

        except Exception as error:

            # Remove partially created output file.
            if os.path.exists(
                output_path
            ):

                try:

                    os.remove(
                        output_path
                    )

                except OSError:

                    pass

            processing_time = (
                time.perf_counter()
                - start_time
            )

            return {
                "success": False,
                "input_path": input_path,
                "output_path": output_path,
                "filename": os.path.basename(
                    input_path
                ),
                "error": str(
                    error
                ),
                "processing_time": round(
                    processing_time,
                    4
                ),
            }

    # ==========================================================
    # BATCH COMPRESSION
    # ==========================================================

    def compress_batch(
        self,
        input_files,
        output_directory,
        output_format=None
    ):
        """
        Compress multiple images.

        Args:
            input_files:
                Iterable of image paths.

            output_directory:
                Destination directory.

            output_format:
                Optional output format.

        Returns:
            List of compression result dictionaries.
        """

        if not input_files:

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

        for input_path in input_files:

            if not input_path:

                continue

            filename = os.path.basename(
                input_path
            )

            original_name = (
                os.path.splitext(
                    filename
                )[0]
            )

            selected_format = (
                output_format
                if output_format
                else self._get_output_format(
                    input_path,
                    input_path
                )
            )

            normalized_format = (
                self._normalize_format(
                    selected_format
                )
            )

            extension_map = {
                "JPG": ".jpg",
                "PNG": ".png",
                "WEBP": ".webp",
            }

            extension = extension_map.get(
                normalized_format,
                os.path.splitext(
                    filename
                )[1]
            )

            output_filename = (
                f"{original_name}"
                f"_compressed"
                f"{extension}"
            )

            output_path = os.path.join(
                output_directory,
                output_filename
            )

            # Avoid accidentally overwriting an existing
            # output file.
            output_path = (
                self._get_unique_output_path(
                    output_path
                )
            )

            result = self.compress(
                input_path=input_path,
                output_path=output_path,
                output_format=output_format
            )

            results.append(
                result
            )

        return results

    # ==========================================================
    # UNIQUE OUTPUT PATH
    # ==========================================================

    @staticmethod
    def _get_unique_output_path(
        output_path
    ):
        """
        Return a unique output path.

        Example:

            image_compressed.jpg

        becomes:

            image_compressed_1.jpg
        """

        if not os.path.exists(
            output_path
        ):

            return output_path

        directory = os.path.dirname(
            output_path
        )

        filename = os.path.basename(
            output_path
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
    # COMPRESSION STATISTICS
    # ==========================================================

    @staticmethod
    def calculate_statistics(
        results
    ):
        """
        Calculate aggregate compression statistics.

        Args:
            results:
                List returned by compress_batch().

        Returns:
            Dictionary containing aggregate statistics.
        """

        if not results:

            return {
                "total_files": 0,
                "successful_files": 0,
                "failed_files": 0,
                "original_size": 0,
                "new_size": 0,
                "saved_bytes": 0,
                "saving_percentage": 0.0,
                "compression_ratio": 0.0,
                "total_processing_time": 0.0,
            }

        successful_results = [
            result
            for result in results
            if result.get(
                "success",
                False
            )
        ]

        failed_results = [
            result
            for result in results
            if not result.get(
                "success",
                False
            )
        ]

        total_original = sum(
            result.get(
                "original_size",
                0
            )
            for result in successful_results
        )

        total_new = sum(
            result.get(
                "new_size",
                0
            )
            for result in successful_results
        )

        saved_bytes = max(
            0,
            total_original - total_new
        )

        saving_percentage = (
            (
                saved_bytes
                / total_original
            ) * 100
            if total_original > 0
            else 0
        )

        compression_ratio = (
            total_original / total_new
            if total_new > 0
            else 0
        )

        processing_time = sum(
            result.get(
                "processing_time",
                0
            )
            for result in results
        )

        return {
            "total_files": len(
                results
            ),
            "successful_files": len(
                successful_results
            ),
            "failed_files": len(
                failed_results
            ),
            "original_size": total_original,
            "new_size": total_new,
            "saved_bytes": saved_bytes,
            "saving_percentage": round(
                saving_percentage,
                2
            ),
            "compression_ratio": round(
                compression_ratio,
                2
            ),
            "total_processing_time": round(
                processing_time,
                4
            ),
        }

    # ==========================================================
    # PREVIEW
    # ==========================================================

    @staticmethod
    def get_image_info(
        input_path
    ):
        """
        Read basic information about an image.

        Returns:
            Dictionary containing image metadata.
        """

        ImageCompressor._validate_input_file(
            input_path
        )

        file_size = os.path.getsize(
            input_path
        )

        with Image.open(
            input_path
        ) as image:

            return {
                "filename": os.path.basename(
                    input_path
                ),
                "path": input_path,
                "format": image.format,
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
                "size": file_size,
            }

    # ==========================================================
    # SUPPORTED FORMAT CHECK
    # ==========================================================

    @classmethod
    def is_supported_format(
        cls,
        image_format
    ):
        """
        Check whether a format is supported.
        """

        normalized = cls._normalize_format(
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

    compressor = ImageCompressor(
        quality=80
    )

    print(
        "ImageCompressor engine initialized."
    )

    print(
        "Supported formats:",
        ", ".join(
            sorted(
                compressor.SUPPORTED_FORMATS
            )
        )
    )