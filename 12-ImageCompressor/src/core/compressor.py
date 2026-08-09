import os
from PIL import Image


class ImageCompressor:
    SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp")

    def __init__(self, keep_exif=True):
        self.keep_exif = keep_exif

    # ==========================================================
    # BASIC COMPRESSION
    # ==========================================================

    def compress(
        self,
        input_path,
        output_path,
        quality=80,
        target_format=None,
        scale_percent=100
    ):
        """
        Compress an image.

        Parameters:
            input_path: Source image path
            output_path: Destination image path
            quality: Compression quality (1-100)
            target_format: Optional output format (.jpg, .png, .webp)
            scale_percent: Resize percentage
        """

        self._validate_input(input_path)

        quality = self._validate_quality(quality)
        scale_percent = self._validate_scale(scale_percent)

        with Image.open(input_path) as original_img:

            img = original_img.copy()

            exif = original_img.info.get("exif")

            extension = os.path.splitext(output_path)[1].lower()

            if target_format:
                extension = target_format.lower()

            extension = self._normalize_extension(extension)

            # --------------------------------------------------
            # RESIZE
            # --------------------------------------------------

            if scale_percent < 100:
                img = self._resize(img, scale_percent)

            # --------------------------------------------------
            # COLOR MODE
            # --------------------------------------------------

            img = self._prepare_image_for_format(img, extension)

            # --------------------------------------------------
            # SAVE OPTIONS
            # --------------------------------------------------

            save_kwargs = self._build_save_options(
                extension=extension,
                quality=quality,
                exif=exif
            )

            # --------------------------------------------------
            # SAVE
            # --------------------------------------------------

            img.save(
                output_path,
                **save_kwargs
            )

            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)

            return {
                "original_size": original_size,
                "compressed_size": compressed_size,
                "saved_bytes": max(0, original_size - compressed_size),
                "compression_ratio": self.compression_ratio(
                    original_size,
                    compressed_size
                ),
                "new_resolution": img.size,
                "format": extension.replace(".", "").upper()
            }

    # ==========================================================
    # TARGET SIZE COMPRESSION
    # ==========================================================

    def smart_compress(
        self,
        input_path,
        output_path,
        target_size_kb=500,
        min_quality=5,
        max_quality=100
    ):
        """
        Compress an image to the largest possible quality
        while staying below the requested target size.

        Example:

            target_size_kb = 500

        means:

            output <= 500 KB
        """

        self._validate_input(input_path)

        if target_size_kb <= 0:
            raise ValueError("Target size must be greater than 0 KB.")

        min_quality = self._validate_quality(min_quality)
        max_quality = self._validate_quality(max_quality)

        if min_quality > max_quality:
            raise ValueError(
                "min_quality cannot be greater than max_quality."
            )

        target_size_bytes = target_size_kb * 1024

        low = min_quality
        high = max_quality

        best_quality = min_quality
        best_size = None

        while low <= high:

            quality = (low + high) // 2

            self.compress(
                input_path,
                output_path,
                quality=quality
            )

            current_size = os.path.getsize(output_path)

            if current_size <= target_size_bytes:

                best_quality = quality
                best_size = current_size

                # Try a higher quality.
                low = quality + 1

            else:

                # File is too large.
                high = quality - 1

        # ------------------------------------------------------
        # Final compression
        # ------------------------------------------------------

        self.compress(
            input_path,
            output_path,
            quality=best_quality
        )

        final_size = os.path.getsize(output_path)

        return {
            "quality": best_quality,
            "target_size": target_size_bytes,
            "compressed_size": final_size,
            "target_reached": final_size <= target_size_bytes,
            "difference": final_size - target_size_bytes
        }

    # ==========================================================
    # RESIZE
    # ==========================================================

    def resize(
        self,
        input_path,
        output_path,
        scale_percent=100,
        quality=90,
        target_format=None
    ):
        """
        Resize an image while keeping its aspect ratio.
        """

        self._validate_input(input_path)

        scale_percent = self._validate_scale(scale_percent)
        quality = self._validate_quality(quality)

        with Image.open(input_path) as original_img:

            img = original_img.copy()

            if scale_percent != 100:
                img = self._resize(img, scale_percent)

            extension = os.path.splitext(output_path)[1].lower()

            if target_format:
                extension = target_format.lower()

            extension = self._normalize_extension(extension)

            img = self._prepare_image_for_format(
                img,
                extension
            )

            save_kwargs = self._build_save_options(
                extension=extension,
                quality=quality,
                exif=original_img.info.get("exif")
            )

            img.save(
                output_path,
                **save_kwargs
            )

            return {
                "original_resolution": original_img.size,
                "new_resolution": img.size,
                "original_size": os.path.getsize(input_path),
                "new_size": os.path.getsize(output_path)
            }

    # ==========================================================
    # FORMAT CONVERSION
    # ==========================================================

    def convert(
        self,
        input_path,
        output_path,
        quality=90,
        scale_percent=100
    ):
        """
        Convert an image to another format.

        Supported:
            JPG
            JPEG
            PNG
            WEBP
        """

        self._validate_input(input_path)

        quality = self._validate_quality(quality)
        scale_percent = self._validate_scale(scale_percent)

        extension = os.path.splitext(output_path)[1].lower()
        extension = self._normalize_extension(extension)

        with Image.open(input_path) as original_img:

            img = original_img.copy()

            if scale_percent != 100:
                img = self._resize(img, scale_percent)

            img = self._prepare_image_for_format(
                img,
                extension
            )

            save_kwargs = self._build_save_options(
                extension=extension,
                quality=quality,
                exif=original_img.info.get("exif")
            )

            img.save(
                output_path,
                **save_kwargs
            )

            return {
                "original_size": os.path.getsize(input_path),
                "new_size": os.path.getsize(output_path),
                "new_resolution": img.size,
                "format": extension.replace(".", "").upper()
            }

    # ==========================================================
    # BATCH COMPRESSION
    # ==========================================================

    def batch_compress(
        self,
        input_folder,
        output_folder,
        quality=80,
        scale_percent=100,
        target_format=None
    ):
        """
        Compress every supported image inside a folder.
        """

        if not os.path.isdir(input_folder):
            raise ValueError(
                f"Input folder does not exist: {input_folder}"
            )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        results = []

        for filename in os.listdir(input_folder):

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension not in self.SUPPORTED_FORMATS:
                continue

            input_path = os.path.join(
                input_folder,
                filename
            )

            output_extension = (
                target_format.lower()
                if target_format
                else extension
            )

            base_name = os.path.splitext(filename)[0]

            output_filename = (
                f"compressed_{base_name}"
                f"{output_extension}"
            )

            output_path = os.path.join(
                output_folder,
                output_filename
            )

            try:

                result = self.compress(
                    input_path,
                    output_path,
                    quality=quality,
                    target_format=target_format,
                    scale_percent=scale_percent
                )

                result["filename"] = filename
                result["success"] = True

                results.append(result)

            except Exception as error:

                results.append({
                    "filename": filename,
                    "success": False,
                    "error": str(error)
                })

        return results

    # ==========================================================
    # INTERNAL HELPERS
    # ==========================================================

    @staticmethod
    def _validate_input(input_path):

        if not input_path:
            raise ValueError(
                "Input path cannot be empty."
            )

        if not os.path.isfile(input_path):
            raise FileNotFoundError(
                f"Input file not found: {input_path}"
            )

        extension = os.path.splitext(
            input_path
        )[1].lower()

        if extension not in ImageCompressor.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported image format: {extension}"
            )

    @staticmethod
    def _validate_quality(quality):

        quality = int(quality)

        if quality < 1:
            return 1

        if quality > 100:
            return 100

        return quality

    @staticmethod
    def _validate_scale(scale_percent):

        scale_percent = float(scale_percent)

        if scale_percent <= 0:
            raise ValueError(
                "Scale percent must be greater than 0."
            )

        return scale_percent

    @staticmethod
    def _normalize_extension(extension):

        extension = extension.lower()

        if extension == ".jpeg":
            return ".jpg"

        return extension

    @staticmethod
    def _resize(img, scale_percent):

        new_width = max(
            1,
            int(img.width * scale_percent / 100)
        )

        new_height = max(
            1,
            int(img.height * scale_percent / 100)
        )

        return img.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )

    @staticmethod
    def _prepare_image_for_format(img, extension):

        # JPEG does not support RGBA / transparency.
        if extension in (".jpg", ".jpeg"):

            if img.mode in (
                "RGBA",
                "LA",
                "P"
            ):
                img = img.convert("RGB")

        return img

    def _build_save_options(
        self,
        extension,
        quality,
        exif=None
    ):

        # ------------------------------------------------------
        # JPEG
        # ------------------------------------------------------

        if extension in (".jpg", ".jpeg"):

            options = {
                "quality": quality,
                "optimize": True,
                "progressive": True
            }

            if self.keep_exif and exif:
                options["exif"] = exif

            return options

        # ------------------------------------------------------
        # WEBP
        # ------------------------------------------------------

        if extension == ".webp":

            options = {
                "quality": quality,
                "method": 6
            }

            if self.keep_exif and exif:
                options["exif"] = exif

            return options

        # ------------------------------------------------------
        # PNG
        # ------------------------------------------------------

        if extension == ".png":

            return {
                "optimize": True,
                "compress_level": 9
            }

        # ------------------------------------------------------
        # FALLBACK
        # ------------------------------------------------------

        options = {}

        if self.keep_exif and exif:
            options["exif"] = exif

        return options

    # ==========================================================
    # STATISTICS
    # ==========================================================

    @staticmethod
    def compression_ratio(
        original,
        compressed
    ):
        """
        Returns percentage of saved space.
        """

        if original <= 0:
            return 0

        return (
            (original - compressed)
            / original
        ) * 100

    @staticmethod
    def format_size(size):
        """
        Convert bytes into a human-readable string.
        """

        kb = size / 1024

        if kb < 1024:
            return f"{kb:.2f} KB"

        mb = kb / 1024

        if mb < 1024:
            return f"{mb:.2f} MB"

        gb = mb / 1024

        return f"{gb:.2f} GB"