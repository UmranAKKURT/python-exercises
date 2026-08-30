import os

from PIL import Image


class ImageConverter:
    """
    Image format conversion engine.

    Supported formats:
        - JPG
        - PNG
        - WEBP
    """

    SUPPORTED_FORMATS = {
        "JPG",
        "JPEG",
        "PNG",
        "WEBP",
    }

    FORMAT_EXTENSIONS = {
        "JPG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
    }

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):
        """
        Initialize image converter.
        """

        pass

    # ==========================================================
    # FORMAT NORMALIZATION
    # ==========================================================

    @staticmethod
    def normalize_format(
        image_format
    ):
        """
        Normalize an image format.

        Examples:
            jpg  -> JPG
            .png -> PNG
            jpeg -> JPG
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
    # FORMAT VALIDATION
    # ==========================================================

    @classmethod
    def is_supported_format(
        cls,
        image_format
    ):
        """
        Check whether a format is supported.
        """

        normalized = cls.normalize_format(
            image_format
        )

        return normalized in {
            "JPG",
            "PNG",
            "WEBP",
        }

    @classmethod
    def validate_format(
        cls,
        image_format
    ):
        """
        Validate target image format.
        """

        normalized = cls.normalize_format(
            image_format
        )

        if not cls.is_supported_format(
            normalized
        ):

            raise ValueError(
                (
                    f"Unsupported image format: "
                    f"{image_format}. "
                    "Supported formats: JPG, PNG, WEBP."
                )
            )

        return normalized

    # ==========================================================
    # FILE VALIDATION
    # ==========================================================

    @staticmethod
    def validate_input(
        input_path
    ):
        """
        Validate input image path.
        """

        if not input_path:

            raise ValueError(
                "Input image path cannot be empty."
            )

        if not os.path.isfile(
            input_path
        ):

            raise FileNotFoundError(
                f"Input image not found: {input_path}"
            )

        return True

    # ==========================================================
    # IMAGE MODE PREPARATION
    # ==========================================================

    @staticmethod
    def prepare_for_jpeg(
        image
    ):
        """
        Prepare an image for JPEG conversion.

        JPEG does not support transparency.
        Transparent images are placed on a white background.
        """

        if image.mode == "RGB":

            return image

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

            return background

        if image.mode == "P":

            converted = image.convert(
                "RGBA"
            )

            background = Image.new(
                "RGB",
                converted.size,
                "white"
            )

            background.paste(
                converted,
                mask=converted.getchannel(
                    "A"
                )
            )

            return background

        return image.convert(
            "RGB"
        )

    @staticmethod
    def prepare_for_png(
        image
    ):
        """
        Prepare image for PNG conversion.

        PNG supports RGB, RGBA and palette modes.
        """

        if image.mode in (
            "RGB",
            "RGBA",
            "P",
            "L",
            "LA"
        ):

            return image

        return image.convert(
            "RGBA"
        )

    @staticmethod
    def prepare_for_webp(
        image
    ):
        """
        Prepare image for WebP conversion.
        """

        if image.mode in (
            "RGB",
            "RGBA",
            "L",
            "LA"
        ):

            return image

        return image.convert(
            "RGBA"
        )

    # ==========================================================
    # PREPARE IMAGE
    # ==========================================================

    def prepare_image(
        self,
        image,
        target_format
    ):
        """
        Prepare image according to target format.
        """

        target_format = self.validate_format(
            target_format
        )

        if target_format == "JPG":

            return self.prepare_for_jpeg(
                image
            )

        if target_format == "PNG":

            return self.prepare_for_png(
                image
            )

        if target_format == "WEBP":

            return self.prepare_for_webp(
                image
            )

        raise ValueError(
            f"Unsupported format: {target_format}"
        )

    # ==========================================================
    # SAVE OPTIONS
    # ==========================================================

    @staticmethod
    def get_save_options(
        target_format,
        quality=90,
        lossless=False
    ):
        """
        Return Pillow save options for target format.
        """

        target_format = (
            ImageConverter
            .validate_format(
                target_format
            )
        )

        try:

            quality = int(
                quality
            )

        except (
            ValueError,
            TypeError
        ):

            quality = 90

        quality = max(
            1,
            min(
                100,
                quality
            )
        )

        if target_format == "JPG":

            return {
                "format": "JPEG",
                "quality": quality,
                "optimize": True,
                "progressive": True,
            }

        if target_format == "PNG":

            return {
                "format": "PNG",
                "optimize": True,
            }

        if target_format == "WEBP":

            options = {
                "format": "WEBP",
                "method": 6,
            }

            if lossless:

                options[
                    "lossless"
                ] = True

            else:

                options[
                    "quality"
                ] = quality

            return options

        raise ValueError(
            f"Unsupported format: {target_format}"
        )

    # ==========================================================
    # OUTPUT PATH
    # ==========================================================

    def generate_output_path(
        self,
        input_path,
        output_directory,
        target_format,
        suffix="_converted"
    ):
        """
        Generate output path for converted image.
        """

        self.validate_input(
            input_path
        )

        target_format = self.validate_format(
            target_format
        )

        if not output_directory:

            raise ValueError(
                "Output directory cannot be empty."
            )

        os.makedirs(
            output_directory,
            exist_ok=True
        )

        filename = os.path.basename(
            input_path
        )

        name, _ = os.path.splitext(
            filename
        )

        extension = (
            self.FORMAT_EXTENSIONS[
                target_format
            ]
        )

        output_filename = (
            f"{name}"
            f"{suffix}"
            f"{extension}"
        )

        output_path = os.path.join(
            output_directory,
            output_filename
        )

        return self.get_unique_path(
            output_path
        )

    # ==========================================================
    # UNIQUE PATH
    # ==========================================================

    @staticmethod
    def get_unique_path(
        file_path
    ):
        """
        Prevent accidental file overwriting.
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
    # SINGLE CONVERSION
    # ==========================================================

    def convert(
        self,
        input_path,
        output_path,
        target_format,
        quality=90,
        lossless=False
    ):
        """
        Convert a single image.

        Returns:
            Dictionary containing conversion information.
        """

        self.validate_input(
            input_path
        )

        target_format = self.validate_format(
            target_format
        )

        if not output_path:

            raise ValueError(
                "Output path cannot be empty."
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

        original_size = os.path.getsize(
            input_path
        )

        with Image.open(
            input_path
        ) as image:

            source_format = (
                self.normalize_format(
                    image.format
                )
            )

            original_width = image.width
            original_height = image.height

            prepared_image = (
                self.prepare_image(
                    image,
                    target_format
                )
            )

            save_options = (
                self.get_save_options(
                    target_format,
                    quality,
                    lossless
                )
            )

            prepared_image.save(
                output_path,
                **save_options
            )

        new_size = os.path.getsize(
            output_path
        )

        size_difference = (
            original_size
            - new_size
        )

        saving_percentage = (
            (
                size_difference
                / original_size
            ) * 100
            if original_size > 0
            else 0
        )

        return {
            "success": True,
            "input_path": input_path,
            "output_path": output_path,
            "filename": os.path.basename(
                input_path
            ),
            "source_format": source_format,
            "target_format": target_format,
            "original_size": original_size,
            "new_size": new_size,
            "size_difference": size_difference,
            "saving_percentage": round(
                saving_percentage,
                2
            ),
            "width": original_width,
            "height": original_height,
        }

    # ==========================================================
    # BATCH CONVERSION
    # ==========================================================

    def convert_batch(
        self,
        input_files,
        output_directory,
        target_format,
        quality=90,
        lossless=False
    ):
        """
        Convert multiple images.
        """

        if not input_files:

            return []

        target_format = self.validate_format(
            target_format
        )

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

            try:

                output_path = (
                    self.generate_output_path(
                        input_path,
                        output_directory,
                        target_format
                    )
                )

                result = self.convert(
                    input_path=input_path,
                    output_path=output_path,
                    target_format=target_format,
                    quality=quality,
                    lossless=lossless
                )

                results.append(
                    result
                )

            except Exception as error:

                results.append(
                    {
                        "success": False,
                        "input_path": input_path,
                        "output_path": None,
                        "filename": os.path.basename(
                            input_path
                        ),
                        "target_format": target_format,
                        "error": str(
                            error
                        ),
                    }
                )

        return results

    # ==========================================================
    # FORMAT DETECTION
    # ==========================================================

    @staticmethod
    def detect_format(
        image_path
    ):
        """
        Detect actual image format using Pillow.
        """

        ImageConverter.validate_input(
            image_path
        )

        with Image.open(
            image_path
        ) as image:

            return ImageConverter.normalize_format(
                image.format
            )

    # ==========================================================
    # CONVERSION COMPATIBILITY
    # ==========================================================

    @classmethod
    def can_convert(
        cls,
        source_format,
        target_format
    ):
        """
        Check whether source and target formats are supported.
        """

        source = cls.normalize_format(
            source_format
        )

        target = cls.normalize_format(
            target_format
        )

        return (
            cls.is_supported_format(source)
            and
            cls.is_supported_format(target)
        )

    # ==========================================================
    # FORMAT LIST
    # ==========================================================

    @classmethod
    def get_supported_formats(
        cls
    ):
        """
        Return supported output formats.
        """

        return [
            "JPG",
            "PNG",
            "WEBP",
        ]

    # ==========================================================
    # CONVERSION SUMMARY
    # ==========================================================

    @staticmethod
    def summarize_results(
        results
    ):
        """
        Create summary information for batch conversion.
        """

        if not results:

            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "original_size": 0,
                "new_size": 0,
                "size_difference": 0,
                "saving_percentage": 0.0,
            }

        successful = [
            result
            for result in results
            if result.get(
                "success",
                False
            )
        ]

        failed = [
            result
            for result in results
            if not result.get(
                "success",
                False
            )
        ]

        original_size = sum(
            result.get(
                "original_size",
                0
            )
            for result in successful
        )

        new_size = sum(
            result.get(
                "new_size",
                0
            )
            for result in successful
        )

        size_difference = (
            original_size
            - new_size
        )

        saving_percentage = (
            (
                size_difference
                / original_size
            ) * 100
            if original_size > 0
            else 0
        )

        return {
            "total": len(
                results
            ),
            "successful": len(
                successful
            ),
            "failed": len(
                failed
            ),
            "original_size": original_size,
            "new_size": new_size,
            "size_difference": size_difference,
            "saving_percentage": round(
                saving_percentage,
                2
            ),
        }


# ==============================================================
# SIMPLE TEST
# ==============================================================

if __name__ == "__main__":

    converter = ImageConverter()

    print(
        "ImageConverter initialized."
    )

    print(
        "Supported formats:",
        ", ".join(
            converter.get_supported_formats()
        )
    )

    print(
        "Can convert JPG -> WEBP:",
        converter.can_convert(
            "JPG",
            "WEBP"
        )
    )

    print(
        "Can convert PNG -> JPG:",
        converter.can_convert(
            "PNG",
            "JPG"
        )
    )