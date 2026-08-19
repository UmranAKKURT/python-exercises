import os
from collections import Counter
from statistics import mean


class AnalysisService:
    """
    Service responsible for analyzing image compression results.

    Responsibilities:
        - Calculate compression statistics
        - Calculate size reduction
        - Analyze formats
        - Analyze processing times
        - Find best and worst results
        - Generate dashboard-ready statistics
    """

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):
        """
        Initialize analysis service.
        """

        pass

    # ==========================================================
    # ANALYZE SINGLE RESULT
    # ==========================================================

    def analyze_result(
        self,
        result
    ):
        """
        Analyze a single compression result.

        Returns a normalized analysis dictionary.
        """

        if not isinstance(
            result,
            dict
        ):

            raise TypeError(
                "Result must be a dictionary."
            )

        original_size = self._safe_int(
            result.get(
                "original_size",
                result.get(
                    "original",
                    0
                )
            )
        )

        new_size = self._safe_int(
            result.get(
                "new_size",
                result.get(
                    "compressed",
                    0
                )
            )
        )

        saved_bytes = max(
            0,
            original_size - new_size
        )

        saving_percentage = (
            self._calculate_saving_percentage(
                original_size,
                new_size
            )
        )

        compression_ratio = (
            self._calculate_compression_ratio(
                original_size,
                new_size
            )
        )

        return {
            "original_size": original_size,
            "new_size": new_size,
            "saved_bytes": saved_bytes,
            "saving_percentage": saving_percentage,
            "compression_ratio": compression_ratio,
            "original_size_mb": self._bytes_to_mb(
                original_size
            ),
            "new_size_mb": self._bytes_to_mb(
                new_size
            ),
            "saved_mb": self._bytes_to_mb(
                saved_bytes
            ),
            "processing_time": self._safe_float(
                result.get(
                    "processing_time",
                    0
                )
            ),
            "filename": result.get(
                "filename",
                ""
            ),
            "format": str(
                result.get(
                    "format",
                    result.get(
                        "output_format",
                        ""
                    )
                )
            ).upper()
        }

    # ==========================================================
    # ANALYZE BATCH
    # ==========================================================

    def analyze_batch(
        self,
        results
    ):
        """
        Analyze a list of compression results.

        Failed results are excluded from numerical
        compression calculations.
        """

        if not isinstance(
            results,
            list
        ):

            raise TypeError(
                "Results must be a list."
            )

        analyzed_results = []

        for result in results:

            if not isinstance(
                result,
                dict
            ):

                continue

            if result.get(
                "success",
                True
            ) is False:

                continue

            try:

                analyzed = (
                    self.analyze_result(
                        result
                    )
                )

                analyzed_results.append(
                    analyzed
                )

            except Exception:

                continue

        return {
            "total_files": len(
                results
            ),

            "successful_files": len(
                analyzed_results
            ),

            "failed_files": (
                len(results)
                - len(analyzed_results)
            ),

            "total_original_bytes": (
                sum(
                    item["original_size"]
                    for item in analyzed_results
                )
            ),

            "total_new_bytes": (
                sum(
                    item["new_size"]
                    for item in analyzed_results
                )
            ),

            "total_saved_bytes": (
                sum(
                    item["saved_bytes"]
                    for item in analyzed_results
                )
            ),

            "average_saving_percentage": (
                self._average(
                    [
                        item[
                            "saving_percentage"
                        ]
                        for item in analyzed_results
                    ]
                )
            ),

            "average_compression_ratio": (
                self._average(
                    [
                        item[
                            "compression_ratio"
                        ]
                        for item in analyzed_results
                    ]
                )
            ),

            "total_processing_time": round(
                sum(
                    item[
                        "processing_time"
                    ]
                    for item in analyzed_results
                ),
                3
            ),

            "average_processing_time": (
                self._average(
                    [
                        item[
                            "processing_time"
                        ]
                        for item in analyzed_results
                    ]
                )
            ),

            "total_original_mb": (
                self._bytes_to_mb(
                    sum(
                        item[
                            "original_size"
                        ]
                        for item in analyzed_results
                    )
                )
            ),

            "total_new_mb": (
                self._bytes_to_mb(
                    sum(
                        item[
                            "new_size"
                        ]
                        for item in analyzed_results
                    )
                )
            ),

            "total_saved_mb": (
                self._bytes_to_mb(
                    sum(
                        item[
                            "saved_bytes"
                        ]
                        for item in analyzed_results
                    )
                )
            ),

            "results": analyzed_results
        }

    # ==========================================================
    # SAVING PERCENTAGE
    # ==========================================================

    @staticmethod
    def calculate_saving_percentage(
        original_size,
        new_size
    ):
        """
        Calculate how much storage space was saved.
        """

        original_size = (
            AnalysisService._safe_int(
                original_size
            )
        )

        new_size = (
            AnalysisService._safe_int(
                new_size
            )
        )

        return (
            AnalysisService._calculate_saving_percentage(
                original_size,
                new_size
            )
        )

    # ==========================================================
    # COMPRESSION RATIO
    # ==========================================================

    @staticmethod
    def calculate_compression_ratio(
        original_size,
        new_size
    ):
        """
        Calculate compression ratio.

        Example:

            Original = 1000 KB
            New = 250 KB

            Ratio = 4.0
        """

        original_size = (
            AnalysisService._safe_int(
                original_size
            )
        )

        new_size = (
            AnalysisService._safe_int(
                new_size
            )
        )

        return (
            AnalysisService._calculate_compression_ratio(
                original_size,
                new_size
            )
        )

    # ==========================================================
    # FORMAT ANALYSIS
    # ==========================================================

    def analyze_formats(
        self,
        results
    ):
        """
        Analyze output image formats.

        Returns the number of files processed
        for each format.
        """

        counter = Counter()

        for result in results:

            if not isinstance(
                result,
                dict
            ):

                continue

            if result.get(
                "success",
                True
            ) is False:

                continue

            image_format = str(
                result.get(
                    "format",
                    result.get(
                        "output_format",
                        "UNKNOWN"
                    )
                )
            ).upper()

            if not image_format:

                image_format = "UNKNOWN"

            counter[
                image_format
            ] += 1

        return dict(
            counter
        )

    # ==========================================================
    # FORMAT SIZE ANALYSIS
    # ==========================================================

    def analyze_format_sizes(
        self,
        results
    ):
        """
        Compare compression performance by format.
        """

        format_data = {}

        for result in results:

            if not isinstance(
                result,
                dict
            ):

                continue

            if result.get(
                "success",
                True
            ) is False:

                continue

            image_format = str(
                result.get(
                    "format",
                    result.get(
                        "output_format",
                        "UNKNOWN"
                    )
                )
            ).upper()

            original_size = self._safe_int(
                result.get(
                    "original_size",
                    result.get(
                        "original",
                        0
                    )
                )
            )

            new_size = self._safe_int(
                result.get(
                    "new_size",
                    result.get(
                        "compressed",
                        0
                    )
                )
            )

            if image_format not in format_data:

                format_data[
                    image_format
                ] = {
                    "count": 0,
                    "original_bytes": 0,
                    "new_bytes": 0,
                    "saved_bytes": 0
                }

            format_data[
                image_format
            ]["count"] += 1

            format_data[
                image_format
            ]["original_bytes"] += (
                original_size
            )

            format_data[
                image_format
            ]["new_bytes"] += (
                new_size
            )

            format_data[
                image_format
            ]["saved_bytes"] += max(
                0,
                original_size - new_size
            )

        # ------------------------------------------------------
        # Calculate percentages.
        # ------------------------------------------------------

        for image_format, data in (
            format_data.items()
        ):

            data[
                "saving_percentage"
            ] = self._calculate_saving_percentage(
                data["original_bytes"],
                data["new_bytes"]
            )

            data[
                "original_mb"
            ] = self._bytes_to_mb(
                data["original_bytes"]
            )

            data[
                "new_mb"
            ] = self._bytes_to_mb(
                data["new_bytes"]
            )

            data[
                "saved_mb"
            ] = self._bytes_to_mb(
                data["saved_bytes"]
            )

        return format_data

    # ==========================================================
    # BEST RESULT
    # ==========================================================

    def get_best_result(
        self,
        results
    ):
        """
        Return the result with the highest
        storage saving percentage.
        """

        valid_results = (
            self._get_successful_results(
                results
            )
        )

        if not valid_results:

            return None

        return max(
            valid_results,
            key=lambda result: (
                self.calculate_saving_percentage(
                    result.get(
                        "original_size",
                        result.get(
                            "original",
                            0
                        )
                    ),
                    result.get(
                        "new_size",
                        result.get(
                            "compressed",
                            0
                        )
                    )
                )
            )
        )

    # ==========================================================
    # WORST RESULT
    # ==========================================================

    def get_worst_result(
        self,
        results
    ):
        """
        Return the result with the lowest
        storage saving percentage.
        """

        valid_results = (
            self._get_successful_results(
                results
            )
        )

        if not valid_results:

            return None

        return min(
            valid_results,
            key=lambda result: (
                self.calculate_saving_percentage(
                    result.get(
                        "original_size",
                        result.get(
                            "original",
                            0
                        )
                    ),
                    result.get(
                        "new_size",
                        result.get(
                            "compressed",
                            0
                        )
                    )
                )
            )
        )

    # ==========================================================
    # LARGEST FILE
    # ==========================================================

    def get_largest_file(
        self,
        results
    ):
        """
        Return the result with the largest
        original file size.
        """

        valid_results = (
            self._get_successful_results(
                results
            )
        )

        if not valid_results:

            return None

        return max(
            valid_results,
            key=lambda result: (
                self._safe_int(
                    result.get(
                        "original_size",
                        result.get(
                            "original",
                            0
                        )
                    )
                )
            )
        )

    # ==========================================================
    # FASTEST PROCESS
    # ==========================================================

    def get_fastest_process(
        self,
        results
    ):
        """
        Return the fastest processed image.
        """

        valid_results = (
            self._get_successful_results(
                results
            )
        )

        if not valid_results:

            return None

        return min(
            valid_results,
            key=lambda result: (
                self._safe_float(
                    result.get(
                        "processing_time",
                        0
                    )
                )
            )
        )

    # ==========================================================
    # SLOWEST PROCESS
    # ==========================================================

    def get_slowest_process(
        self,
        results
    ):
        """
        Return the slowest processed image.
        """

        valid_results = (
            self._get_successful_results(
                results
            )
        )

        if not valid_results:

            return None

        return max(
            valid_results,
            key=lambda result: (
                self._safe_float(
                    result.get(
                        "processing_time",
                        0
                    )
                )
            )
        )

    # ==========================================================
    # DASHBOARD STATISTICS
    # ==========================================================

    def get_dashboard_statistics(
        self,
        results
    ):
        """
        Generate statistics suitable for a GUI dashboard.
        """

        analysis = self.analyze_batch(
            results
        )

        best_result = (
            self.get_best_result(
                results
            )
        )

        largest_file = (
            self.get_largest_file(
                results
            )
        )

        fastest_process = (
            self.get_fastest_process(
                results
            )
        )

        return {
            "total_files": (
                analysis[
                    "total_files"
                ]
            ),

            "successful_files": (
                analysis[
                    "successful_files"
                ]
            ),

            "failed_files": (
                analysis[
                    "failed_files"
                ]
            ),

            "total_original_mb": (
                analysis[
                    "total_original_mb"
                ]
            ),

            "total_new_mb": (
                analysis[
                    "total_new_mb"
                ]
            ),

            "total_saved_mb": (
                analysis[
                    "total_saved_mb"
                ]
            ),

            "average_saving_percentage": (
                analysis[
                    "average_saving_percentage"
                ]
            ),

            "average_compression_ratio": (
                analysis[
                    "average_compression_ratio"
                ]
            ),

            "total_processing_time": (
                analysis[
                    "total_processing_time"
                ]
            ),

            "average_processing_time": (
                analysis[
                    "average_processing_time"
                ]
            ),

            "best_file": (
                self._get_filename(
                    best_result
                )
            ),

            "largest_file": (
                self._get_filename(
                    largest_file
                )
            ),

            "fastest_file": (
                self._get_filename(
                    fastest_process
                )
            ),

            "formats": (
                self.analyze_formats(
                    results
                )
            )
        }

    # ==========================================================
    # STORAGE REPORT
    # ==========================================================

    def generate_storage_report(
        self,
        results
    ):
        """
        Generate a human-readable storage report.
        """

        analysis = self.analyze_batch(
            results
        )

        return {
            "original_size": (
                self.format_bytes(
                    analysis[
                        "total_original_bytes"
                    ]
                )
            ),

            "compressed_size": (
                self.format_bytes(
                    analysis[
                        "total_new_bytes"
                    ]
                )
            ),

            "saved_space": (
                self.format_bytes(
                    analysis[
                        "total_saved_bytes"
                    ]
                )
            ),

            "saving_percentage": (
                analysis[
                    "average_saving_percentage"
                ]
            ),

            "files_processed": (
                analysis[
                    "successful_files"
                ]
            )
        }

    # ==========================================================
    # FORMAT BYTES
    # ==========================================================

    @staticmethod
    def format_bytes(
        size
    ):
        """
        Convert bytes into a readable string.

        Examples:

            1024
            -> 1.00 KB

            1048576
            -> 1.00 MB
        """

        size = max(
            0,
            AnalysisService._safe_int(
                size
            )
        )

        units = (
            "B",
            "KB",
            "MB",
            "GB",
            "TB"
        )

        value = float(
            size
        )

        for unit in units:

            if value < 1024:

                return (
                    f"{value:.2f} "
                    f"{unit}"
                )

            value /= 1024

        return (
            f"{value:.2f} PB"
        )

    # ==========================================================
    # GET SUCCESSFUL RESULTS
    # ==========================================================

    @staticmethod
    def _get_successful_results(
        results
    ):
        """
        Return only successful result dictionaries.
        """

        if not isinstance(
            results,
            list
        ):

            return []

        return [
            result
            for result in results
            if isinstance(
                result,
                dict
            )
            and result.get(
                "success",
                True
            ) is not False
        ]

    # ==========================================================
    # GET FILENAME
    # ==========================================================

    @staticmethod
    def _get_filename(
        result
    ):
        """
        Safely extract filename from a result.
        """

        if not result:

            return None

        filename = result.get(
            "filename"
        )

        if filename:

            return filename

        input_path = result.get(
            "input_path"
        )

        if input_path:

            return os.path.basename(
                input_path
            )

        return None

    # ==========================================================
    # SAVING PERCENTAGE INTERNAL
    # ==========================================================

    @staticmethod
    def _calculate_saving_percentage(
        original_size,
        new_size
    ):
        """
        Calculate percentage of storage saved.
        """

        original_size = (
            AnalysisService._safe_int(
                original_size
            )
        )

        new_size = (
            AnalysisService._safe_int(
                new_size
            )
        )

        if original_size <= 0:

            return 0

        saved = max(
            0,
            original_size - new_size
        )

        percentage = (
            saved
            / original_size
        ) * 100

        return round(
            percentage,
            2
        )

    # ==========================================================
    # COMPRESSION RATIO INTERNAL
    # ==========================================================

    @staticmethod
    def _calculate_compression_ratio(
        original_size,
        new_size
    ):
        """
        Calculate compression ratio.
        """

        original_size = (
            AnalysisService._safe_int(
                original_size
            )
        )

        new_size = (
            AnalysisService._safe_int(
                new_size
            )
        )

        if new_size <= 0:

            return 0

        ratio = (
            original_size
            / new_size
        )

        return round(
            ratio,
            2
        )

    # ==========================================================
    # BYTES TO MB
    # ==========================================================

    @staticmethod
    def _bytes_to_mb(
        value
    ):
        """
        Convert bytes to megabytes.
        """

        value = (
            AnalysisService._safe_int(
                value
            )
        )

        return round(
            value / (
                1024 * 1024
            ),
            2
        )

    # ==========================================================
    # AVERAGE
    # ==========================================================

    @staticmethod
    def _average(
        values
    ):
        """
        Calculate average safely.
        """

        if not values:

            return 0

        try:

            return round(
                mean(values),
                2
            )

        except (
            ValueError,
            TypeError
        ):

            return 0

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