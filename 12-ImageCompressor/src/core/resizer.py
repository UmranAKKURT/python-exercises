import os

from PIL import Image


class ImageResizer:
    """
    Image resizing engine.

    Features:
        - Resize by exact dimensions
        - Resize while preserving aspect ratio
        - Resize by percentage
        - Fit image inside maximum dimensions
        - Create thumbnails
        - Batch resizing
    """

    RESAMPLING_FILTERS = {
        "nearest": Image.Resampling.NEAREST,
        "bilinear": Image.Resampling.BILINEAR,
        "bicubic": Image.Resampling.BICUBIC,
        "lanczos": Image.Resampling.LANCZOS,
    }

    DEFAULT_FILTER = "lanczos"

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        resampling="lanczos"
    ):
        """
        Initialize the image resizer.

        Args:
            resampling:
                Resampling algorithm.
        """

        self.resampling = (
            self._validate_resampling(
                resampling
            )
        )

    # ==========================================================
    # RESAMPLING
    # ==========================================================

    @classmethod
    def _validate_resampling(
        cls,
        resampling
    ):
        """
        Validate the resampling filter.
        """

        if not resampling:

            return cls.DEFAULT_FILTER

        resampling = str(
            resampling
        ).strip().lower()

        if resampling not in cls.RESAMPLING_FILTERS:

            return cls.DEFAULT_FILTER

        return resampling

    def set_resampling(
        self,
        resampling
    ):
        """
        Change the resampling algorithm.
        """

        self.resampling = (
            self._validate_resampling(
                resampling
            )
        )

    def get_resampling_filter(
        self
    ):
        """
        Return the Pillow resampling filter.
        """

        return self.RESAMPLING_FILTERS[
            self.resampling
        ]

    # ==========================================================
    # FILE VALIDATION
    # ==========================================================

    @staticmethod
    def validate_input(
        image_path
    ):
        """
        Validate input image path.
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

        return True

    # ==========================================================
    # DIMENSION VALIDATION
    # ==========================================================

    @staticmethod
    def validate_dimensions(
        width,
        height
    ):
        """
        Validate image dimensions.
        """

        try:

            width = int(
                width
            )

            height = int(
                height
            )

        except (
            ValueError,
            TypeError
        ):

            raise ValueError(
                "Width and height must be integers."
            )

        if width <= 0:

            raise ValueError(
                "Width must be greater than zero."
            )

        if height <= 0:

            raise ValueError(
                "Height must be greater than zero."
            )

        return width, height

    # ==========================================================
    # PERCENTAGE VALIDATION
    # ==========================================================

    @staticmethod
    def validate_percentage(
        percentage
    ):
        """
        Validate resize percentage.
        """

        try:

            percentage = float(
                percentage
            )

        except (
            ValueError,
            TypeError
        ):

            raise ValueError(
                "Percentage must be a number."
            )

        if percentage <= 0:

            raise ValueError(
                "Percentage must be greater than zero."
            )

        return percentage

    # ==========================================================
    # IMAGE INFO
    # ==========================================================

    @classmethod
    def get_image_size(
        cls,
        image_path
    ):
        """
        Return original image dimensions.
        """

        cls.validate_input(
            image_path
        )

        with Image.open(
            image_path
        ) as image:

            return image.width, image.height

    @classmethod
    def get_image_info(
        cls,
        image_path
    ):
        """
        Return basic image information.
        """

        cls.validate_input(
            image_path
        )

        file_size = os.path.getsize(
            image_path
        )

        with Image.open(
            image_path
        ) as image:

            return {
                "filename": os.path.basename(
                    image_path
                ),
                "path": image_path,
                "format": image.format,
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
                "size": file_size,
            }

    # ==========================================================
    # ASPECT RATIO
    # ==========================================================

    @staticmethod
    def calculate_aspect_ratio(
        width,
        height
    ):
        """
        Calculate width / height aspect ratio.
        """

        width, height = (
            ImageResizer.validate_dimensions(
                width,
                height
            )
        )

        return width / height

    @staticmethod
    def calculate_height_from_width(
        original_width,
        original_height,
        new_width
    ):
        """
        Calculate height while preserving aspect ratio.
        """

        original_width, original_height = (
            ImageResizer.validate_dimensions(
                original_width,
                original_height
            )
        )

        try:

            new_width = int(
                new_width
            )

        except (
            ValueError,
            TypeError
        ):

            raise ValueError(
                "New width must be an integer."
            )

        if new_width <= 0:

            raise ValueError(
                "New width must be greater than zero."
            )

        new_height = round(
            new_width
            * original_height
            / original_width
        )

        return max(
            1,
            new_height
        )

    @staticmethod
    def calculate_width_from_height(
        original_width,
        original_height,
        new_height
    ):
        """
        Calculate width while preserving aspect ratio.
        """

        original_width, original_height = (
            ImageResizer.validate_dimensions(
                original_width,
                original_height
            )
        )

        try:

            new_height = int(
                new_height
            )

        except (
            ValueError,
            TypeError
        ):

            raise ValueError(
                "New height must be an integer."
            )

        if new_height <= 0:

            raise ValueError(
                "New height must be greater than zero."
            )

        new_width = round(
            new_height
            * original_width
            / original_height
        )

        return max(
            1,
            new_width
        )

    # ==========================================================
    # ASPECT RATIO RESIZE
    # ==========================================================

    @staticmethod
    def calculate_contained_size(
        original_width,
        original_height,
        max_width,
        max_height
    ):
        """
        Calculate dimensions that fit inside maximum
        width and height while preserving aspect ratio.

        The image will never exceed either limit.
        """

        original_width, original_height = (
            ImageResizer.validate_dimensions(
                original_width,
                original_height
            )
        )

        max_width, max_height = (
            ImageResizer.validate_dimensions(
                max_width,
                max_height
            )
        )

        width_ratio = (
            max_width
            / original_width
        )

        height_ratio = (
            max_height
            / original_height
        )

        scale = min(
            width_ratio,
            height_ratio
        )

        new_width = max(
            1,
            round(
                original_width
                * scale
            )
        )

        new_height = max(
            1,
            round(
                original_height
                * scale
            )
        )

        return new_width, new_height

    @staticmethod
    def calculate_cover_size(
        original_width,
        original_height,
        target_width,
        target_height
    ):
        """
        Calculate dimensions required to completely cover
        the target area while preserving aspect ratio.

        Useful for thumbnails and previews.
        """

        original_width, original_height = (
            ImageResizer.validate_dimensions(
                original_width,
                original_height
            )
        )

        target_width, target_height = (
            ImageResizer.validate_dimensions(
                target_width,
                target_height
            )
        )

        width_ratio = (
            target_width
            / original_width
        )

        height_ratio = (
            target_height
            / original_height
        )

        scale = max(
            width_ratio,
            height_ratio
        )

        new_width = max(
            1,
            round(
                original_width
                * scale
            )
        )

        new_height = max(
            1,
            round(
                original_height
                * scale
            )
        )

        return new_width, new_height

    # ==========================================================
    # RESIZE IMAGE OBJECT
    # ==========================================================

    def resize_image(
        self,
        image,
        width,
        height,
        keep_aspect_ratio=False
    ):
        """
        Resize a Pillow Image object.

        Args:
            image:
                Pillow Image object.

            width:
                Target width.

            height:
                Target height.

            keep_aspect_ratio:
                Preserve original aspect ratio.
        """

        width, height = (
            self.validate_dimensions(
                width,
                height
            )
        )

        if keep_aspect_ratio:

            width, height = (
                self.calculate_contained_size(
                    image.width,
                    image.height,
                    width,
                    height
                )
            )

        return image.resize(
            (
                width,
                height
            ),
            self.get_resampling_filter()
        )

    # ==========================================================
    # EXACT RESIZE
    # ==========================================================

    def resize(
        self,
        input_path,
        output_path,
        width,
        height,
        keep_aspect_ratio=False
    ):
        """
        Resize an image to specified dimensions.
        """

        self.validate_input(
            input_path
        )

        width, height = (
            self.validate_dimensions(
                width,
                height
            )
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

            original_width = image.width
            original_height = image.height
            original_format = image.format

            resized_image = (
                self.resize_image(
                    image,
                    width,
                    height,
                    keep_aspect_ratio
                )
            )

            save_format = (
                original_format
                if original_format
                else self._format_from_extension(
                    output_path
                )
            )

            save_format = (
                self._normalize_save_format(
                    save_format
                )
            )

            resized_image = (
                self._prepare_for_save(
                    resized_image,
                    save_format
                )
            )

            save_options = (
                self._get_save_options(
                    save_format
                )
            )

            resized_image.save(
                output_path,
                **save_options
            )

        new_size = os.path.getsize(
            output_path
        )

        return {
            "success": True,
            "input_path": input_path,
            "output_path": output_path,
            "filename": os.path.basename(
                input_path
            ),
            "original_width": original_width,
            "original_height": original_height,
            "new_width": resized_image.width,
            "new_height": resized_image.height,
            "original_size": original_size,
            "new_size": new_size,
            "resampling": self.resampling,
            "keep_aspect_ratio": keep_aspect_ratio,
        }

    # ==========================================================
    # RESIZE BY PERCENTAGE
    # ==========================================================

    def resize_by_percentage(
        self,
        input_path,
        output_path,
        percentage
    ):
        """
        Resize an image by a percentage.

        Examples:
            50  -> half size
            100 -> original size
            200 -> double size
        """

        self.validate_input(
            input_path
        )

        percentage = (
            self.validate_percentage(
                percentage
            )
        )

        with Image.open(
            input_path
        ) as image:

            new_width = max(
                1,
                round(
                    image.width
                    * percentage
                    / 100
                )
            )

            new_height = max(
                1,
                round(
                    image.height
                    * percentage
                    / 100
                )
            )

        return self.resize(
            input_path=input_path,
            output_path=output_path,
            width=new_width,
            height=new_height,
            keep_aspect_ratio=False
        )

    # ==========================================================
    # RESIZE TO MAXIMUM DIMENSIONS
    # ==========================================================

    def resize_to_fit(
        self,
        input_path,
        output_path,
        max_width,
        max_height
    ):
        """
        Resize image so that it fits inside the given
        maximum dimensions while preserving aspect ratio.
        """

        self.validate_input(
            input_path
        )

        max_width, max_height = (
            self.validate_dimensions(
                max_width,
                max_height
            )
        )

        with Image.open(
            input_path
        ) as image:

            new_width, new_height = (
                self.calculate_contained_size(
                    image.width,
                    image.height,
                    max_width,
                    max_height
                )
            )

        return self.resize(
            input_path=input_path,
            output_path=output_path,
            width=new_width,
            height=new_height,
            keep_aspect_ratio=False
        )

    # ==========================================================
    # THUMBNAIL
    # ==========================================================

    def create_thumbnail(
        self,
        input_path,
        output_path,
        max_width=400,
        max_height=400
    ):
        """
        Create a thumbnail while preserving aspect ratio.
        """

        self.validate_input(
            input_path
        )

        max_width, max_height = (
            self.validate_dimensions(
                max_width,
                max_height
            )
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

        with Image.open(
            input_path
        ) as image:

            thumbnail = image.copy()

            thumbnail.thumbnail(
                (
                    max_width,
                    max_height
                ),
                self.get_resampling_filter()
            )

            save_format = (
                self._format_from_extension(
                    output_path
                )
            )

            save_format = (
                self._normalize_save_format(
                    save_format
                )
            )

            thumbnail = (
                self._prepare_for_save(
                    thumbnail,
                    save_format
                )
            )

            save_options = (
                self._get_save_options(
                    save_format
                )
            )

            thumbnail.save(
                output_path,
                **save_options
            )

            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "filename": os.path.basename(
                    input_path
                ),
                "width": thumbnail.width,
                "height": thumbnail.height,
                "max_width": max_width,
                "max_height": max_height,
            }

    # ==========================================================
    # BATCH RESIZE
    # ==========================================================

    def resize_batch(
        self,
        input_files,
        output_directory,
        width,
        height,
        keep_aspect_ratio=False
    ):
        """
        Resize multiple images.
        """

        if not input_files:

            return []

        width, height = (
            self.validate_dimensions(
                width,
                height
            )
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

            filename = os.path.basename(
                input_path
            )

            name, extension = (
                os.path.splitext(
                    filename
                )
            )

            output_filename = (
                f"{name}_resized"
                f"{extension}"
            )

            output_path = os.path.join(
                output_directory,
                output_filename
            )

            output_path = (
                self.get_unique_path(
                    output_path
                )
            )

            try:

                result = self.resize(
                    input_path=input_path,
                    output_path=output_path,
                    width=width,
                    height=height,
                    keep_aspect_ratio=keep_aspect_ratio
                )

                results.append(
                    result
                )

            except Exception as error:

                results.append(
                    {
                        "success": False,
                        "input_path": input_path,
                        "output_path": output_path,
                        "filename": filename,
                        "error": str(
                            error
                        ),
                    }
                )

        return results

    # ==========================================================
    # BATCH PERCENTAGE RESIZE
    # ==========================================================

    def resize_batch_by_percentage(
        self,
        input_files,
        output_directory,
        percentage
    ):
        """
        Resize multiple images by percentage.
        """

        if not input_files:

            return []

        percentage = (
            self.validate_percentage(
                percentage
            )
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

            filename = os.path.basename(
                input_path
            )

            name, extension = (
                os.path.splitext(
                    filename
                )
            )

            output_filename = (
                f"{name}_resized"
                f"{extension}"
            )

            output_path = os.path.join(
                output_directory,
                output_filename
            )

            output_path = (
                self.get_unique_path(
                    output_path
                )
            )

            try:

                result = (
                    self.resize_by_percentage(
                        input_path=input_path,
                        output_path=output_path,
                        percentage=percentage
                    )
                )

                results.append(
                    result
                )

            except Exception as error:

                results.append(
                    {
                        "success": False,
                        "input_path": input_path,
                        "output_path": output_path,
                        "filename": filename,
                        "error": str(
                            error
                        ),
                    }
                )

        return results

    # ==========================================================
    # SAVE HELPERS
    # ==========================================================

    @staticmethod
    def _format_from_extension(
        file_path
    ):
        """
        Detect output format from file extension.
        """

        extension = (
            os.path.splitext(
                file_path
            )[1]
            .lower()
        )

        extension_map = {
            ".jpg": "JPG",
            ".jpeg": "JPG",
            ".png": "PNG",
            ".webp": "WEBP",
        }

        return extension_map.get(
            extension,
            "PNG"
        )

    @staticmethod
    def _normalize_save_format(
        image_format
    ):
        """
        Normalize Pillow save format.
        """

        if not image_format:

            return "PNG"

        normalized = str(
            image_format
        ).strip().upper()

        if normalized == "JPEG":

            return "JPG"

        return normalized

    @staticmethod
    def _prepare_for_save(
        image,
        image_format
    ):
        """
        Prepare image mode for the target format.
        """

        if image_format == "JPG":

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

                    background.paste(
                        image,
                        mask=image.getchannel(
                            "A"
                        )
                    )

                    return background

            if image.mode != "RGB":

                return image.convert(
                    "RGB"
                )

        return image

    @staticmethod
    def _get_save_options(
        image_format
    ):
        """
        Return format-specific save options.
        """

        image_format = (
            ImageResizer
            ._normalize_save_format(
                image_format
            )
        )

        if image_format == "JPG":

            return {
                "format": "JPEG",
                "quality": 95,
                "optimize": True,
                "progressive": True,
            }

        if image_format == "PNG":

            return {
                "format": "PNG",
                "optimize": True,
            }

        if image_format == "WEBP":

            return {
                "format": "WEBP",
                "quality": 95,
                "method": 6,
            }

        return {
            "format": "PNG",
            "optimize": True,
        }

    # ==========================================================
    # UNIQUE PATH
    # ==========================================================

    @staticmethod
    def get_unique_path(
        file_path
    ):
        """
        Generate a unique file path.
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
    # CALCULATE NEW DIMENSIONS
    # ==========================================================

    @staticmethod
    def calculate_percentage_dimensions(
        width,
        height,
        percentage
    ):
        """
        Calculate new dimensions based on percentage.
        """

        width, height = (
            ImageResizer.validate_dimensions(
                width,
                height
            )
        )

        percentage = (
            ImageResizer.validate_percentage(
                percentage
            )
        )

        new_width = max(
            1,
            round(
                width
                * percentage
                / 100
            )
        )

        new_height = max(
            1,
            round(
                height
                * percentage
                / 100
            )
        )

        return new_width, new_height


# ==============================================================
# SIMPLE TEST
# ==============================================================

if __name__ == "__main__":

    resizer = ImageResizer()

    print(
        "ImageResizer initialized."
    )

    print(
        "Available resampling filters:",
        ", ".join(
            resizer.RESAMPLING_FILTERS.keys()
        )
    )

    print(
        "50% of 1920x1080:",
        resizer.calculate_percentage_dimensions(
            1920,
            1080,
            50
        )
    )

    print(
        "Fit 1920x1080 into 800x800:",
        resizer.calculate_contained_size(
            1920,
            1080,
            800,
            800
        )
    )