import os
import time

from src.core.compressor import ImageCompressor
from src.core.converter import ImageConverter
from src.core.resizer import ImageResizer


class BatchService:
    """
    Service responsible for batch image processing.

    Supported operations:

        - Compression
        - Format conversion
        - Resizing
        - Smart optimization
        - Combined processing

    This service coordinates the core engines but does not
    contain low-level image processing logic.
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

    def __init__(
        self,
        compressor=None,
        converter=None,
        resizer=None
    ):
        """
        Initialize batch processing service.

        Core engines can optionally be injected. This makes
        the service easier to test and extend later.
        """

        self.compressor = (
            compressor
            or ImageCompressor()
        )

        self.converter = (
            converter
            or ImageConverter()
        )

        self.resizer = (
            resizer
            or ImageResizer()
        )

    # ==========================================================
    # COMPRESS FOLDER
    # ==========================================================

    def compress_folder(
        self,
        input_folder,
        output_folder,
        quality=80,
        output_format=None
    ):
        """
        Compress all supported images in a folder.
        """

        self._validate_input_folder(
            input_folder
        )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        files = self._get_image_files(
            input_folder
        )

        results = []

        for input_path in files:

            filename = os.path.basename(
                input_path
            )

            output_path = (
                self._build_output_path(
                    input_folder=input_folder,
                    output_folder=output_folder,
                    input_path=input_path,
                    output_format=output_format
                )
            )

            start_time = time.perf_counter()

            try:

                result = self._compress(
                    input_path=input_path,
                    output_path=output_path,
                    quality=quality
                )

                processing_time = (
                    time.perf_counter()
                    - start_time
                )

                result["filename"] = filename
                result["success"] = True
                result["operation"] = "compression"
                result["processing_time"] = round(
                    processing_time,
                    3
                )

                results.append(
                    result
                )

            except Exception as error:

                processing_time = (
                    time.perf_counter()
                    - start_time
                )

                results.append({
                    "filename": filename,
                    "success": False,
                    "operation": "compression",
                    "processing_time": round(
                        processing_time,
                        3
                    ),
                    "error": str(error)
                })

        return self._build_batch_summary(
            results
        )

    # ==========================================================
    # CONVERT FOLDER
    # ==========================================================

    def convert_folder(
        self,
        input_folder,
        output_folder,
        target_format,
        quality=90
    ):
        """
        Convert all supported images in a folder.
        """

        self._validate_input_folder(
            input_folder
        )

        target_format = (
            self._normalize_format(
                target_format
            )
        )

        if target_format not in (
            ".jpg",
            ".png",
            ".webp"
        ):

            raise ValueError(
                f"Unsupported target format: "
                f"{target_format}"
            )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        files = self._get_image_files(
            input_folder
        )

        results = []

        for input_path in files:

            filename = os.path.basename(
                input_path
            )

            output_path = (
                self._build_output_path(
                    input_folder=input_folder,
                    output_folder=output_folder,
                    input_path=input_path,
                    output_format=target_format
                )
            )

            start_time = time.perf_counter()

            try:

                result = self.converter.convert(
                    input_path=input_path,
                    output_path=output_path,
                    quality=quality
                )

                processing_time = (
                    time.perf_counter()
                    - start_time
                )

                result["filename"] = filename
                result["success"] = True
                result["operation"] = "conversion"
                result["processing_time"] = round(
                    processing_time,
                    3
                )

                results.append(
                    result
                )

            except Exception as error:

                processing_time = (
                    time.perf_counter()
                    - start_time
                )

                results.append({
                    "filename": filename,
                    "success": False,
                    "operation": "conversion",
                    "processing_time": round(
                        processing_time,
                        3
                    ),
                    "error": str(error)
                })

        return self._build_batch_summary(
            results
        )

    # ==========================================================
    # RESIZE FOLDER
    # ==========================================================

    def resize_folder(
        self,
        input_folder,
        output_folder,
        percent=50
    ):
        """
        Resize all supported images in a folder
        by percentage.
        """

        self._validate_input_folder(
            input_folder
        )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        files = self._get_image_files(
            input_folder
        )

        results = []

        for input_path in files:

            filename = os.path.basename(
                input_path
            )

            output_path = (
                self._build_output_path(
                    input_folder=input_folder,
                    output_folder=output_folder,
                    input_path=input_path
                )
            )

            start_time = time.perf_counter()

            try:

                result = (
                    self.resizer.resize_by_percent(
                        input_path=input_path,
                        output_path=output_path,
                        percent=percent
                    )
                )

                processing_time = (
                    time.perf_counter()
                    - start_time
                )

                result["filename"] = filename
                result["success"] = True
                result["operation"] = "resize"
                result["processing_time"] = round(
                    processing_time,
                    3
                )

                results.append(
                    result
                )

            except Exception as error:

                processing_time = (
                    time.perf_counter()
                    - start_time
                )

                results.append({
                    "filename": filename,
                    "success": False,
                    "operation": "resize",
                    "processing_time": round(
                        processing_time,
                        3
                    ),
                    "error": str(error)
                })

        return self._build_batch_summary(
            results
        )

    # ==========================================================
    # SMART PROCESS FOLDER
    # ==========================================================

    def smart_process_folder(
        self,
        input_folder,
        output_folder,
        quality=80,
        output_format="WEBP",
        max_dimension=1920
    ):
        """
        Perform a combined smart processing pipeline.

        Pipeline:

            Input
              ↓
            Resize if necessary
              ↓
            Format conversion
              ↓
            Compression
              ↓
            Output
        """

        self._validate_input_folder(
            input_folder
        )

        output_format = (
            self._normalize_format(
                output_format
            )
        )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        files = self._get_image_files(
            input_folder
        )

        results = []

        for input_path in files:

            filename = os.path.basename(
                input_path
            )

            start_time = time.perf_counter()

            try:

                result = (
                    self._smart_process_image(
                        input_path=input_path,
                        output_folder=output_folder,
                        quality=quality,
                        output_format=output_format,
                        max_dimension=max_dimension
                    )
                )

                processing_time = (
                    time.perf_counter()
                    - start_time
                )

                result["filename"] = filename
                result["success"] = True
                result["operation"] = "smart"
                result["processing_time"] = round(
                    processing_time,
                    3
                )

                results.append(
                    result
                )

            except Exception as error:

                processing_time = (
                    time.perf_counter()
                    - start_time
                )

                results.append({
                    "filename": filename,
                    "success": False,
                    "operation": "smart",
                    "processing_time": round(
                        processing_time,
                        3
                    ),
                    "error": str(error)
                })

        return self._build_batch_summary(
            results
        )

    # ==========================================================
    # SMART IMAGE PROCESSING
    # ==========================================================

    def _smart_process_image(
        self,
        input_path,
        output_folder,
        quality,
        output_format,
        max_dimension
    ):
        """
        Process one image using the smart pipeline.
        """

        filename = os.path.basename(
            input_path
        )

        name = os.path.splitext(
            filename
        )[0]

        temporary_folder = os.path.join(
            output_folder,
            ".temp"
        )

        os.makedirs(
            temporary_folder,
            exist_ok=True
        )

        temporary_path = os.path.join(
            temporary_folder,
            f"{name}_resized.png"
        )

        final_path = os.path.join(
            output_folder,
            f"{name}{output_format}"
        )

        final_path = (
            self._unique_output_path(
                final_path
            )
        )

        # ------------------------------------------------------
        # Step 1: Smart resize
        # ------------------------------------------------------

        resize_result = (
            self.resizer.smart_resize(
                input_path=input_path,
                output_path=temporary_path,
                max_dimension=max_dimension
            )
        )

        # ------------------------------------------------------
        # Step 2: Compression / format conversion
        # ------------------------------------------------------

        compression_result = self._compress(
            input_path=temporary_path,
            output_path=final_path,
            quality=quality
        )

        # ------------------------------------------------------
        # Cleanup temporary file
        # ------------------------------------------------------

        if os.path.exists(
            temporary_path
        ):

            os.remove(
                temporary_path
            )

        # Remove temporary directory if empty.
        try:

            if os.path.isdir(
                temporary_folder
            ) and not os.listdir(
                temporary_folder
            ):

                os.rmdir(
                    temporary_folder
                )

        except OSError:

            pass

        original_size = (
            os.path.getsize(
                input_path
            )
        )

        final_size = (
            os.path.getsize(
                final_path
            )
        )

        saved_bytes = max(
            0,
            original_size - final_size
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
            "input_path": input_path,
            "output_path": final_path,

            "original_size": original_size,
            "new_size": final_size,

            "saved_bytes": saved_bytes,

            "saving_percentage": round(
                saving_percentage,
                2
            ),

            "original_resolution": (
                resize_result.get(
                    "original_resolution"
                )
            ),

            "new_resolution": (
                resize_result.get(
                    "new_resolution"
                )
            ),

            "quality": quality,

            "output_format": (
                output_format
                .replace(
                    ".",
                    ""
                )
                .upper()
            ),

            "compression_result": (
                compression_result
            )
        }

    # ==========================================================
    # CORE COMPRESSOR ADAPTER
    # ==========================================================

    def _compress(
        self,
        input_path,
        output_path,
        quality
    ):
        """
        Call the currently available compressor API.

        This adapter keeps BatchService isolated from
        small API changes in ImageCompressor.
        """

        if hasattr(
            self.compressor,
            "compress"
        ):

            return self.compressor.compress(
                input_path=input_path,
                output_path=output_path,
                quality=quality
            )

        if hasattr(
            self.compressor,
            "compress_image"
        ):

            return self.compressor.compress_image(
                input_path=input_path,
                output_path=output_path,
                quality=quality
            )

        raise AttributeError(
            "ImageCompressor does not provide a supported "
            "compression method."
        )

    # ==========================================================
    # FILE DISCOVERY
    # ==========================================================

    def _get_image_files(
        self,
        folder
    ):
        """
        Return all supported image files in a folder.
        """

        files = []

        for filename in sorted(
            os.listdir(
                folder
            )
        ):

            path = os.path.join(
                folder,
                filename
            )

            if not os.path.isfile(
                path
            ):
                continue

            extension = (
                os.path.splitext(
                    filename
                )[1].lower()
            )

            if extension in (
                self.SUPPORTED_FORMATS
            ):

                files.append(
                    path
                )

        return files

    # ==========================================================
    # OUTPUT PATH
    # ==========================================================

    def _build_output_path(
        self,
        input_folder,
        output_folder,
        input_path,
        output_format=None
    ):
        """
        Build output path while preserving relative folder
        structure.
        """

        relative_path = os.path.relpath(
            input_path,
            input_folder
        )

        relative_directory = (
            os.path.dirname(
                relative_path
            )
        )

        filename = os.path.basename(
            relative_path
        )

        name, extension = (
            os.path.splitext(
                filename
            )
        )

        if output_format:

            output_extension = (
                self._normalize_format(
                    output_format
                )
            )

        else:

            output_extension = extension

        output_directory = os.path.join(
            output_folder,
            relative_directory
        )

        os.makedirs(
            output_directory,
            exist_ok=True
        )

        output_path = os.path.join(
            output_directory,
            f"{name}{output_extension}"
        )

        return self._unique_output_path(
            output_path
        )

    # ==========================================================
    # UNIQUE OUTPUT
    # ==========================================================

    @staticmethod
    def _unique_output_path(
        path
    ):
        """
        Prevent overwriting existing files.
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

            new_path = os.path.join(
                directory,
                f"{name}_{counter}"
                f"{extension}"
            )

            if not os.path.exists(
                new_path
            ):

                return new_path

            counter += 1

    # ==========================================================
    # FORMAT NORMALIZATION
    # ==========================================================

    @staticmethod
    def _normalize_format(
        image_format
    ):
        """
        Normalize image format.

        Examples:

            jpg
            .jpg
            JPEG

        become:

            .jpg
        """

        image_format = str(
            image_format
        ).strip().lower()

        if not image_format.startswith(
            "."
        ):

            image_format = (
                "."
                + image_format
            )

        if image_format == ".jpeg":

            return ".jpg"

        return image_format

    # ==========================================================
    # INPUT VALIDATION
    # ==========================================================

    @staticmethod
    def _validate_input_folder(
        folder
    ):
        """
        Validate input folder.
        """

        if not folder:

            raise ValueError(
                "Input folder cannot be empty."
            )

        if not os.path.isdir(
            folder
        ):

            raise FileNotFoundError(
                f"Input folder not found: "
                f"{folder}"
            )

    # ==========================================================
    # BATCH SUMMARY
    # ==========================================================

    @staticmethod
    def _build_batch_summary(
        results
    ):
        """
        Create a summary from individual results.
        """

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

        total_original = 0
        total_new = 0
        total_saved = 0
        total_processing_time = 0

        for result in successful:

            total_original += (
                BatchService._safe_int(
                    result.get(
                        "original_size",
                        0
                    )
                )
            )

            total_new += (
                BatchService._safe_int(
                    result.get(
                        "new_size",
                        result.get(
                            "compressed",
                            0
                        )
                    )
                )
            )

            total_saved += (
                BatchService._safe_int(
                    result.get(
                        "saved_bytes",
                        result.get(
                            "saved",
                            0
                        )
                    )
                )
            )

            total_processing_time += (
                BatchService._safe_float(
                    result.get(
                        "processing_time",
                        0
                    )
                )
            )

        saving_percentage = (
            (
                total_saved
                / total_original
            ) * 100
            if total_original > 0
            else 0
        )

        return {
            "results": results,

            "total_files": len(
                results
            ),

            "successful": len(
                successful
            ),

            "failed": len(
                failed
            ),

            "original_bytes": (
                total_original
            ),

            "new_bytes": (
                total_new
            ),

            "saved_bytes": (
                total_saved
            ),

            "saving_percentage": round(
                saving_percentage,
                2
            ),

            "processing_time": round(
                total_processing_time,
                3
            )
        }

    # ==========================================================
    # SAFE INTEGER
    # ==========================================================

    @staticmethod
    def _safe_int(
        value
    ):
        """
        Safely convert value to integer.
        """

        try:

            return int(
                float(
                    value
                )
            )

        except (
            ValueError,
            TypeError
        ):

            return 0

    # ==========================================================
    # SAFE FLOAT
    # ==========================================================

    @staticmethod
    def _safe_float(
        value
    ):
        """
        Safely convert value to float.
        """

        try:

            return float(
                value
            )

        except (
            ValueError,
            TypeError
        ):

            return 0.0