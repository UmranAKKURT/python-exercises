import csv
import json
import os
from datetime import datetime


class HistoryService:
    """
    Service responsible for managing compression history.

    Responsibilities:
        - Save compression records
        - Load compression records
        - Clear history
        - Delete individual records
        - Calculate statistics
        - Export history to CSV
    """

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        history_file=None,
        csv_file=None
    ):
        """
        Initialize history service.

        If no paths are provided, history files are stored
        inside the project's data directory.
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

        self.history_file = (
            history_file
            or os.path.join(
                data_dir,
                "compression_history.json"
            )
        )

        self.csv_file = (
            csv_file
            or os.path.join(
                data_dir,
                "compression_history.csv"
            )
        )

        self._ensure_history_file()

    # ==========================================================
    # INITIALIZATION HELPERS
    # ==========================================================

    def _ensure_history_file(self):
        """
        Create an empty history file if it does not exist.
        """

        if os.path.exists(
            self.history_file
        ):
            return

        directory = os.path.dirname(
            os.path.abspath(
                self.history_file
            )
        )

        os.makedirs(
            directory,
            exist_ok=True
        )

        with open(
            self.history_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [],
                file,
                indent=4,
                ensure_ascii=False
            )

    # ==========================================================
    # LOAD HISTORY
    # ==========================================================

    def load_history(self):
        """
        Load all compression records.

        Returns:
            list
        """

        if not os.path.exists(
            self.history_file
        ):
            return []

        try:

            with open(
                self.history_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if not isinstance(
                data,
                list
            ):
                return []

            return data

        except (
            json.JSONDecodeError,
            OSError
        ):

            return []

    # ==========================================================
    # SAVE HISTORY
    # ==========================================================

    def save_record(
        self,
        record
    ):
        """
        Add a new compression record to history.

        Returns:
            The saved record.
        """

        if not isinstance(
            record,
            dict
        ):

            raise TypeError(
                "History record must be a dictionary."
            )

        history = self.load_history()

        prepared_record = (
            self._prepare_record(
                record
            )
        )

        history.append(
            prepared_record
        )

        self._write_history(
            history
        )

        return prepared_record

    # ==========================================================
    # CREATE RECORD
    # ==========================================================

    def create_record(
        self,
        filename,
        original_size,
        compressed_size,
        quality=None,
        output_format=None,
        original_resolution=None,
        new_resolution=None,
        processing_time=None
    ):
        """
        Create and save a standardized compression record.
        """

        original_size = int(
            original_size
        )

        compressed_size = int(
            compressed_size
        )

        saved = max(
            0,
            original_size - compressed_size
        )

        ratio = self._calculate_ratio(
            original_size,
            compressed_size
        )

        record = {
            "filename": filename,

            "date": datetime.now().strftime(
                "%d.%m.%Y %H:%M:%S"
            ),

            "original": original_size,

            "compressed": compressed_size,

            "saved": saved,

            "ratio": ratio
        }

        if quality is not None:

            record["quality"] = int(
                quality
            )

        if output_format:

            record["format"] = (
                str(
                    output_format
                ).upper()
            )

        if original_resolution:

            record["original_resolution"] = (
                self._resolution_to_string(
                    original_resolution
                )
            )

        if new_resolution:

            record["new_resolution"] = (
                self._resolution_to_string(
                    new_resolution
                )
            )

        if processing_time is not None:

            record["processing_time"] = round(
                float(processing_time),
                3
            )

        return self.save_record(
            record
        )

    # ==========================================================
    # UPDATE RECORD
    # ==========================================================

    def update_record(
        self,
        index,
        updates
    ):
        """
        Update an existing history record.

        Parameters:
            index:
                Record index.

            updates:
                Dictionary containing fields to update.
        """

        history = self.load_history()

        if index < 0 or index >= len(
            history
        ):

            raise IndexError(
                "History index is out of range."
            )

        if not isinstance(
            updates,
            dict
        ):

            raise TypeError(
                "Updates must be a dictionary."
            )

        history[index].update(
            updates
        )

        history[index] = (
            self._prepare_record(
                history[index]
            )
        )

        self._write_history(
            history
        )

        return history[index]

    # ==========================================================
    # DELETE RECORD
    # ==========================================================

    def delete_record(
        self,
        index
    ):
        """
        Delete a history record by index.
        """

        history = self.load_history()

        if index < 0 or index >= len(
            history
        ):

            raise IndexError(
                "History index is out of range."
            )

        deleted = history.pop(
            index
        )

        self._write_history(
            history
        )

        return deleted

    # ==========================================================
    # CLEAR HISTORY
    # ==========================================================

    def clear_history(self):
        """
        Delete all history records.
        """

        self._write_history(
            []
        )

        return True

    # ==========================================================
    # HISTORY COUNT
    # ==========================================================

    def count(self):
        """
        Return number of history records.
        """

        return len(
            self.load_history()
        )

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def get_statistics(self):
        """
        Calculate general compression statistics.

        Returns:

            {
                "count": ...,
                "original_bytes": ...,
                "compressed_bytes": ...,
                "saved_bytes": ...,
                "total_saved_mb": ...,
                "average_ratio": ...,
                "average_processing_time": ...
            }
        """

        history = self.load_history()

        if not history:

            return {
                "count": 0,
                "original_bytes": 0,
                "compressed_bytes": 0,
                "saved_bytes": 0,
                "total_saved_mb": 0,
                "average_ratio": 0,
                "average_processing_time": 0
            }

        total_original = 0
        total_compressed = 0
        total_saved = 0
        total_ratio = 0

        processing_times = []

        for record in history:

            original = self._safe_int(
                record.get(
                    "original",
                    0
                )
            )

            compressed = self._safe_int(
                record.get(
                    "compressed",
                    0
                )
            )

            saved = self._safe_int(
                record.get(
                    "saved",
                    max(
                        0,
                        original - compressed
                    )
                )
            )

            ratio = self._safe_float(
                record.get(
                    "ratio",
                    0
                )
            )

            total_original += original
            total_compressed += compressed
            total_saved += saved
            total_ratio += ratio

            if "processing_time" in record:

                processing_time = (
                    self._safe_float(
                        record.get(
                            "processing_time"
                        )
                    )
                )

                processing_times.append(
                    processing_time
                )

        average_ratio = (
            total_ratio / len(history)
        )

        average_processing_time = (
            sum(processing_times)
            / len(processing_times)
            if processing_times
            else 0
        )

        return {
            "count": len(history),

            "original_bytes": (
                total_original
            ),

            "compressed_bytes": (
                total_compressed
            ),

            "saved_bytes": (
                total_saved
            ),

            "total_saved_mb": round(
                total_saved
                / (1024 * 1024),
                2
            ),

            "average_ratio": round(
                average_ratio,
                2
            ),

            "average_processing_time": round(
                average_processing_time,
                3
            )
        }

    # ==========================================================
    # FORMAT STATISTICS
    # ==========================================================

    def get_format_statistics(self):
        """
        Count compression operations by output format.

        Example:

            {
                "WEBP": 10,
                "JPEG": 5,
                "PNG": 3
            }
        """

        history = self.load_history()

        statistics = {}

        for record in history:

            image_format = str(
                record.get(
                    "format",
                    "UNKNOWN"
                )
            ).upper()

            statistics[image_format] = (
                statistics.get(
                    image_format,
                    0
                ) + 1
            )

        return statistics

    # ==========================================================
    # BEST COMPRESSION
    # ==========================================================

    def get_best_compression(
        self
    ):
        """
        Return the record with the highest saving percentage.
        """

        history = self.load_history()

        if not history:
            return None

        return max(
            history,
            key=lambda item: self._safe_float(
                item.get(
                    "ratio",
                    0
                )
            )
        )

    # ==========================================================
    # LARGEST FILE
    # ==========================================================

    def get_largest_original(
        self
    ):
        """
        Return the record with the largest original file.
        """

        history = self.load_history()

        if not history:
            return None

        return max(
            history,
            key=lambda item: self._safe_int(
                item.get(
                    "original",
                    0
                )
            )
        )

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(
        self,
        query
    ):
        """
        Search history by filename or format.
        """

        query = str(
            query
        ).strip().lower()

        if not query:
            return self.load_history()

        history = self.load_history()

        results = []

        for record in history:

            filename = str(
                record.get(
                    "filename",
                    ""
                )
            ).lower()

            image_format = str(
                record.get(
                    "format",
                    ""
                )
            ).lower()

            if (
                query in filename
                or query in image_format
            ):

                results.append(
                    record
                )

        return results

    # ==========================================================
    # SORT
    # ==========================================================

    def sort_history(
        self,
        field="date",
        reverse=True
    ):
        """
        Return history sorted by a selected field.
        """

        history = self.load_history()

        if not history:
            return []

        def sort_key(record):

            value = record.get(
                field,
                0
            )

            if field in (
                "original",
                "compressed",
                "saved"
            ):

                return self._safe_int(
                    value
                )

            if field in (
                "ratio",
                "processing_time"
            ):

                return self._safe_float(
                    value
                )

            return str(
                value
            )

        return sorted(
            history,
            key=sort_key,
            reverse=reverse
        )

    # ==========================================================
    # CSV EXPORT
    # ==========================================================

    def export_csv(
        self,
        output_path=None
    ):
        """
        Export all history records to CSV.

        Returns:
            Generated CSV path.
        """

        history = self.load_history()

        if not history:

            raise ValueError(
                "There is no compression history to export."
            )

        if output_path is None:

            output_path = self.csv_file

        output_directory = os.path.dirname(
            os.path.abspath(
                output_path
            )
        )

        os.makedirs(
            output_directory,
            exist_ok=True
        )

        fields = []

        for record in history:

            for key in record.keys():

                if key not in fields:

                    fields.append(
                        key
                    )

        with open(
            output_path,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields
            )

            writer.writeheader()

            for record in history:

                writer.writerow(
                    record
                )

        return output_path

    # ==========================================================
    # IMPORT CSV
    # ==========================================================

    def import_csv(
        self,
        input_path
    ):
        """
        Import history records from a CSV file.

        Existing history is preserved.
        Imported records are appended.
        """

        if not os.path.isfile(
            input_path
        ):

            raise FileNotFoundError(
                f"CSV file not found: "
                f"{input_path}"
            )

        imported_records = []

        with open(
            input_path,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(
                file
            )

            for row in reader:

                imported_records.append(
                    self._prepare_record(
                        dict(row)
                    )
                )

        if not imported_records:
            return 0

        history = self.load_history()

        history.extend(
            imported_records
        )

        self._write_history(
            history
        )

        return len(
            imported_records
        )

    # ==========================================================
    # INTERNAL WRITE
    # ==========================================================

    def _write_history(
        self,
        history
    ):
        """
        Write history list to JSON.
        """

        directory = os.path.dirname(
            os.path.abspath(
                self.history_file
            )
        )

        os.makedirs(
            directory,
            exist_ok=True
        )

        temporary_file = (
            self.history_file
            + ".tmp"
        )

        try:

            with open(
                temporary_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    history,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            os.replace(
                temporary_file,
                self.history_file
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
    # RECORD PREPARATION
    # ==========================================================

    @staticmethod
    def _prepare_record(
        record
    ):
        """
        Normalize a history record.
        """

        prepared = dict(
            record
        )

        if "original" in prepared:

            prepared["original"] = (
                HistoryService._safe_int(
                    prepared["original"]
                )
            )

        if "compressed" in prepared:

            prepared["compressed"] = (
                HistoryService._safe_int(
                    prepared["compressed"]
                )
            )

        if (
            "saved" not in prepared
            and "original" in prepared
            and "compressed" in prepared
        ):

            prepared["saved"] = max(
                0,
                prepared["original"]
                - prepared["compressed"]
            )

        if "ratio" not in prepared:

            if (
                "original" in prepared
                and "compressed" in prepared
            ):

                prepared["ratio"] = (
                    HistoryService._calculate_ratio(
                        prepared["original"],
                        prepared["compressed"]
                    )
                )

        if "quality" in prepared:

            try:

                prepared["quality"] = int(
                    prepared["quality"]
                )

            except (
                ValueError,
                TypeError
            ):

                pass

        if "processing_time" in prepared:

            try:

                prepared["processing_time"] = round(
                    float(
                        prepared["processing_time"]
                    ),
                    3
                )

            except (
                ValueError,
                TypeError
            ):

                pass

        return prepared

    # ==========================================================
    # RESOLUTION HELPER
    # ==========================================================

    @staticmethod
    def _resolution_to_string(
        resolution
    ):
        """
        Convert resolution tuple/list to string.
        """

        if isinstance(
            resolution,
            (tuple, list)
        ) and len(
            resolution
        ) >= 2:

            return (
                f"{resolution[0]}"
                f"x"
                f"{resolution[1]}"
            )

        return str(
            resolution
        )

    # ==========================================================
    # RATIO
    # ==========================================================

    @staticmethod
    def _calculate_ratio(
        original_size,
        compressed_size
    ):
        """
        Calculate compression saving percentage.
        """

        if original_size <= 0:
            return 0

        ratio = (
            (
                original_size
                - compressed_size
            )
            / original_size
        ) * 100

        return round(
            max(
                0,
                ratio
            ),
            2
        )

    # ==========================================================
    # SAFE INTEGER
    # ==========================================================

    @staticmethod
    def _safe_int(
        value
    ):
        """
        Safely convert a value to integer.
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
        Safely convert a value to float.
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