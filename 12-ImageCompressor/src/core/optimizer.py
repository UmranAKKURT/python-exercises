
import os

from PIL import Image


class ImageOptimizer:
    """
    Intelligent image optimization engine.

    This class analyzes an image and generates
    compression recommendations.

    It does not perform the actual compression.
    Compression is handled by ImageCompressor.
    """

    SUPPORTED_FORMATS = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    )

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):
        pass

    # ==========================================================
    # IMAGE ANALYSIS
    # ==========================================================

    def analyze(self, image_path):
        """
        Analyze an image and return useful information.

        Returns:
            {
                "filename": ...,
                "format": ...,
                "width": ...,
                "height": ...,
                "resolution": ...,
                "file_size": ...,
                "file_size_mb": ...,
                "mode": ...,
                "has_transparency": ...,
                "megapixels": ...
            }
        """

        self._validate_image(image_path)

        file_size = os.path.getsize(
            image_path
        )

        with Image.open(image_path) as img:

            width, height = img.size

            return {
                "filename": os.path.basename(
                    image_path
                ),

                "format": (
                    img.format
                    or "UNKNOWN"
                ).upper(),

                "width": width,

                "height": height,

                "resolution": (
                    f"{width}x{height}"
                ),

                "file_size": file_size,

                "file_size_mb": round(
                    file_size / (1024 * 1024),
                    2
                ),

                "mode": img.mode,

                "has_transparency": (
                    self._has_transparency(img)
                ),

                "megapixels": round(
                    (width * height) / 1_000_000,
                    2
                )
            }

    # ==========================================================
    # SMART RECOMMENDATION
    # ==========================================================

    def recommend(
        self,
        image_path,
        target_size_kb=None
    ):
        """
        Generate an optimization recommendation.

        The recommendation considers:

            - File size
            - Image resolution
            - Current format
            - Transparency
            - Target size

        Returns:
            recommendation dictionary
        """

        analysis = self.analyze(
            image_path
        )

        current_format = (
            "." +
            analysis["format"].lower()
        )

        file_size_mb = analysis[
            "file_size_mb"
        ]

        width = analysis["width"]
        height = analysis["height"]

        has_transparency = analysis[
            "has_transparency"
        ]

        # ------------------------------------------------------
        # Determine recommended format
        # ------------------------------------------------------

        recommended_format = self._recommend_format(
            current_format,
            has_transparency
        )

        # ------------------------------------------------------
        # Determine recommended quality
        # ------------------------------------------------------

        recommended_quality = self._recommend_quality(
            file_size_mb,
            current_format
        )

        # ------------------------------------------------------
        # Determine recommended resize
        # ------------------------------------------------------

        recommended_scale = self._recommend_scale(
            width,
            height
        )

        # ------------------------------------------------------
        # Target size optimization
        # ------------------------------------------------------

        if target_size_kb is not None:

            recommended_quality = self._quality_for_target_size(
                file_size_mb,
                target_size_kb,
                recommended_quality
            )

            recommended_scale = self._scale_for_target_size(
                width,
                height,
                file_size_mb,
                target_size_kb,
                recommended_scale
            )

        # ------------------------------------------------------
        # Estimated size
        # ------------------------------------------------------

        estimated_size = self.estimate_output_size(
            original_size=analysis["file_size"],
            quality=recommended_quality,
            scale_percent=recommended_scale,
            source_format=current_format,
            target_format=recommended_format
        )

        estimated_saving = self.calculate_saving_percentage(
            analysis["file_size"],
            estimated_size
        )

        return {
            "recommended_format": (
                recommended_format
                .replace(".", "")
                .upper()
            ),

            "recommended_quality": (
                recommended_quality
            ),

            "recommended_scale": (
                recommended_scale
            ),

            "estimated_size": (
                estimated_size
            ),

            "estimated_size_kb": round(
                estimated_size / 1024,
                2
            ),

            "estimated_size_mb": round(
                estimated_size / (1024 * 1024),
                2
            ),

            "estimated_saving": round(
                estimated_saving,
                2
            ),

            "target_size_reached": (
                target_size_kb is None
                or estimated_size <= target_size_kb * 1024
            ),

            "message": self._build_recommendation_message(
                current_format=current_format,
                recommended_format=recommended_format,
                quality=recommended_quality,
                scale_percent=recommended_scale,
                estimated_saving=estimated_saving
            )
        }

    # ==========================================================
    # FORMAT RECOMMENDATION
    # ==========================================================

    def _recommend_format(
        self,
        current_format,
        has_transparency
    ):
        """
        Select the most suitable output format.

        Rules:

            PNG + transparency
                -> WEBP

            PNG without transparency
                -> WEBP

            JPG / JPEG
                -> WEBP

            WEBP
                -> WEBP

        WEBP is preferred for general-purpose
        lossy image optimization.
        """

        if current_format in (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        ):
            return ".webp"

        return current_format

    # ==========================================================
    # QUALITY RECOMMENDATION
    # ==========================================================

    def _recommend_quality(
        self,
        file_size_mb,
        current_format
    ):
        """
        Select a quality level according to
        current file size and format.
        """

        # Very large images
        if file_size_mb >= 10:

            return 65

        # Large images
        if file_size_mb >= 5:

            return 70

        # Medium-large images
        if file_size_mb >= 2:

            return 75

        # Medium images
        if file_size_mb >= 1:

            return 80

        # Small images
        return 85

    # ==========================================================
    # RESIZE RECOMMENDATION
    # ==========================================================

    def _recommend_scale(
        self,
        width,
        height
    ):
        """
        Recommend a resize percentage based
        on image dimensions.
        """

        largest_dimension = max(
            width,
            height
        )

        if largest_dimension >= 6000:

            return 50

        if largest_dimension >= 4000:

            return 60

        if largest_dimension >= 3000:

            return 70

        if largest_dimension >= 2500:

            return 75

        if largest_dimension >= 2000:

            return 85

        return 100

    # ==========================================================
    # TARGET SIZE QUALITY
    # ==========================================================

    def _quality_for_target_size(
        self,
        file_size_mb,
        target_size_kb,
        current_quality
    ):
        """
        Estimate a quality level for the requested
        target file size.
        """

        current_size_kb = (
            file_size_mb * 1024
        )

        if target_size_kb <= 0:
            return current_quality

        ratio = (
            target_size_kb
            / current_size_kb
            if current_size_kb > 0
            else 1
        )

        if ratio >= 0.8:

            return max(
                80,
                current_quality
            )

        if ratio >= 0.6:

            return 75

        if ratio >= 0.4:

            return 65

        if ratio >= 0.25:

            return 55

        if ratio >= 0.15:

            return 45

        return 35

    # ==========================================================
    # TARGET SIZE SCALE
    # ==========================================================

    def _scale_for_target_size(
        self,
        width,
        height,
        file_size_mb,
        target_size_kb,
        current_scale
    ):
        """
        Determine whether the image should also
        be resized to reach the target size.
        """

        if target_size_kb <= 0:
            return current_scale

        current_size_kb = (
            file_size_mb * 1024
        )

        if current_size_kb <= target_size_kb:
            return 100

        ratio = (
            target_size_kb
            / current_size_kb
        )

        # Target is relatively close.
        if ratio >= 0.7:

            return max(
                current_scale,
                85
            )

        # Moderate reduction.
        if ratio >= 0.5:

            return max(
                current_scale,
                75
            )

        # Strong reduction.
        if ratio >= 0.3:

            return max(
                current_scale,
                65
            )

        # Very strong reduction.
        if ratio >= 0.15:

            return max(
                current_scale,
                50
            )

        return max(
            current_scale,
            40
        )

    # ==========================================================
    # OUTPUT SIZE ESTIMATION
    # ==========================================================

    def estimate_output_size(
        self,
        original_size,
        quality,
        scale_percent=100,
        source_format=None,
        target_format=None
    ):
        """
        Estimate output file size.

        This is an approximation. Actual size depends
        heavily on image content.

        The estimation considers:

            - Quality
            - Resize percentage
            - Format efficiency
        """

        if original_size <= 0:
            return 0

        quality = max(
            1,
            min(
                100,
                int(quality)
            )
        )

        scale_percent = max(
            1,
            float(scale_percent)
        )

        # ------------------------------------------------------
        # Quality factor
        # ------------------------------------------------------

        quality_factor = (
            0.15 +
            0.85 *
            (quality / 100)
        )

        # ------------------------------------------------------
        # Resolution factor
        #
        # Image dimensions are scaled by X,
        # therefore pixel count is approximately
        # scaled by X².
        # ------------------------------------------------------

        scale_factor = (
            scale_percent / 100
        )

        resolution_factor = (
            scale_factor ** 2
        )

        # ------------------------------------------------------
        # Format factor
        # ------------------------------------------------------

        format_factor = 1.0

        if target_format:

            target_format = (
                target_format.lower()
            )

            if target_format == ".webp":

                format_factor = 0.65

            elif target_format in (
                ".jpg",
                ".jpeg"
            ):

                format_factor = 0.75

            elif target_format == ".png":

                format_factor = 1.0

        estimated = (
            original_size
            * quality_factor
            * resolution_factor
            * format_factor
        )

        return max(
            1,
            int(estimated)
        )

    # ==========================================================
    # SAVING CALCULATION
    # ==========================================================

    @staticmethod
    def calculate_saving_percentage(
        original_size,
        output_size
    ):
        """
        Calculate estimated space saving.
        """

        if original_size <= 0:
            return 0

        return (
            (
                original_size
                - output_size
            )
            / original_size
        ) * 100

    # ==========================================================
    # RECOMMENDATION MESSAGE
    # ==========================================================

    @staticmethod
    def _build_recommendation_message(
        current_format,
        recommended_format,
        quality,
        scale_percent,
        estimated_saving
    ):
        """
        Generate a human-readable recommendation.
        """

        current = (
            current_format
            .replace(".", "")
            .upper()
        )

        recommended = (
            recommended_format
            .replace(".", "")
            .upper()
        )

        if current != recommended:

            format_message = (
                f"Convert {current} to {recommended}"
            )

        else:

            format_message = (
                f"Keep {recommended} format"
            )

        if scale_percent < 100:

            resize_message = (
                f"resize to {scale_percent}%"
            )

        else:

            resize_message = (
                "keep original resolution"
            )

        return (
            f"{format_message}, "
            f"use quality {quality}%, "
            f"{resize_message}. "
            f"Estimated saving: "
            f"{estimated_saving:.1f}%."
        )

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def _validate_image(
        self,
        image_path
    ):
        """
        Validate image path and format.
        """

        if not image_path:

            raise ValueError(
                "Image path cannot be empty."
            )

        if not os.path.isfile(
            image_path
        ):

            raise FileNotFoundError(
                f"Image file not found: "
                f"{image_path}"
            )

        extension = os.path.splitext(
            image_path
        )[1].lower()

        if extension not in self.SUPPORTED_FORMATS:

            raise ValueError(
                f"Unsupported image format: "
                f"{extension}"
            )

    # ==========================================================
    # TRANSPARENCY
    # ==========================================================

    @staticmethod
    def _has_transparency(
        img
    ):
        """
        Detect whether an image has transparency.
        """

        if img.mode in (
            "RGBA",
            "LA"
        ):
            return True

        if img.mode == "P":

            return (
                "transparency"
                in img.info
            )

        return False

    # ==========================================================
    # TARGET SIZE QUALITY SEARCH
    # ==========================================================

    def find_best_quality_for_target(
        self,
        image_path,
        target_size_kb,
        compressor,
        output_path,
        min_quality=5,
        max_quality=100
    ):
        """
        Find the highest possible quality that
        satisfies the target size.

        This method delegates the actual compression
        to ImageCompressor.

        Parameters:

            image_path:
                Source image.

            target_size_kb:
                Maximum target size.

            compressor:
                ImageCompressor instance.

            output_path:
                Temporary/final output path.

        Returns:

            {
                "quality": ...,
                "size": ...,
                "target_reached": ...
            }
        """

        if target_size_kb <= 0:

            raise ValueError(
                "Target size must be greater than 0 KB."
            )

        target_bytes = (
            target_size_kb * 1024
        )

        low = max(
            1,
            int(min_quality)
        )

        high = min(
            100,
            int(max_quality)
        )

        best_quality = low
        best_size = None

        while low <= high:

            quality = (
                low + high
            ) // 2

            compressor.compress(
                image_path,
                output_path,
                quality=quality
            )

            current_size = os.path.getsize(
                output_path
            )

            if current_size <= target_bytes:

                best_quality = quality
                best_size = current_size

                low = quality + 1

            else:

                high = quality - 1

        # Final output with best quality
        compressor.compress(
            image_path,
            output_path,
            quality=best_quality
        )

        best_size = os.path.getsize(
            output_path
        )

        return {
            "quality": best_quality,
            "size": best_size,
            "size_kb": round(
                best_size / 1024,
                2
            ),
            "target_size_kb": target_size_kb,
            "target_reached": (
                best_size <= target_bytes
            ),
            "difference_kb": round(
                (
                    best_size
                    - target_bytes
                ) / 1024,
                2
            )
        }
