import json
import os
from datetime import datetime


class HistoryService:
    """
    Manages image processing history.

    Stores operation records in a JSON file.

    Supported operations:
        - compression
        - optimization
        - conversion
        - resizing
    """

    DEFAULT_HISTORY_FILE = os.path.join(
        "data",
        "history.json"
    )

    MAX_HISTORY_ITEMS = 500

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        history_file=None,
        max_items=MAX_HISTORY_ITEMS
    ):
        """
        Initialize history service.

        Args:
            history_file:
                Path of the JSON history file.

            max_items:
                Maximum number of history records.
        """

        self.history_file = (
            history_file
            if history_file
            else self.DEFAULT_HISTORY_FILE
        )

        try:
            self.max_items = int(
                max_items
            )
        except (
            ValueError,
            TypeError
        ):
            self.max_items = (
                self.MAX_HISTORY_ITEMS
            )

        if self.max_items <= 0:
            self.max_items = (
                self.MAX_HISTORY_ITEMS
            )

        self._ensure_storage()

    # ==========================================================
    # STORAGE
    # ==========================================================

    def _ensure_storage(
        self
    ):
        """
        Create the history directory and file if necessary.
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

        if not os.path.exists(
            self.history_file
        ):
            self._write_history([])

    # ==========================================================
    # READ / WRITE
    # ==========================================================

    def _read_history(
        self
    ):
        """
        Read history records from JSON.
        """

        self._ensure_storage()

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

    def _write_history(
        self,
        history
    ):
        """
        Write history records to JSON.
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

                try:
                    os.remove(
                        temporary_file
                    )
                except OSError:
                    pass

            raise

    # ==========================================================
    # ID GENERATION
    # ==========================================================

    @staticmethod
    def _generate_id():
        """
        Generate a unique-ish history record ID.
        """

        timestamp = (
            datetime.now()
            .strftime(
                "%Y%m%d%H%M%S%f"
            )
        )

        return timestamp

    # ==========================================================
    # DATE
    # ==========================================================

    @staticmethod
    def _current_timestamp():
        """
        Return current timestamp in ISO format.
        """

        return datetime.now().isoformat(
            timespec="seconds"
        )

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    @staticmethod
    def _normalize_record(
        record
    ):
        """
        Ensure history record has a predictable structure.
        """

        if not isinstance(
            record,
            dict
        ):

            return None

        normalized = dict(
            record
        )

        if not normalized.get(
            "id"
        ):

            normalized[
                "id"
            ] = HistoryService._generate_id()

        if not normalized.get(
            "timestamp"
        ):

            normalized[
                "timestamp"
            ] = HistoryService._current_timestamp()

        if not normalized.get(
            "operation"
        ):

            normalized[
                "operation"
            ] = "unknown"

        if not normalized.get(
            "status"
        ):

            normalized[
                "status"
            ] = "success"

        return normalized

    # ==========================================================
    # ADD RECORD
    # ==========================================================

    def add_record(
        self,
        record
    ):
        """
        Add a new history record.

        Returns:
            The stored record.
        """

        normalized = (
            self._normalize_record(
                record
            )
        )

        if normalized is None:

            raise ValueError(
                "History record must be a dictionary."
            )

        history = self._read_history()

        history.append(
            normalized
        )

        if len(history) > self.max_items:

            history = history[
                -self.max_items:
            ]

        self._write_history(
            history
        )

        return normalized

    # ==========================================================
    # CONVENIENCE RECORD CREATION
    # ==========================================================

    def add_operation(
        self,
        operation,
        input_path=None,
        output_path=None,
        status="success",
        **details
    ):
        """
        Create and save an operation record.

        Example operations:
            compression
            optimization
            conversion
            resizing
        """

        record = {
            "id": self._generate_id(),
            "timestamp": self._current_timestamp(),
            "operation": str(
                operation
            ),
            "status": str(
                status
            ),
            "input_path": input_path,
            "output_path": output_path,
        }

        record.update(
            details
        )

        return self.add_record(
            record
        )

    # ==========================================================
    # GET ALL
    # ==========================================================

    def get_all(
        self,
        newest_first=True
    ):
        """
        Return all history records.
        """

        history = self._read_history()

        if newest_first:

            history.reverse()

        return history

    # ==========================================================
    # GET BY ID
    # ==========================================================

    def get_by_id(
        self,
        record_id
    ):
        """
        Find a history record by ID.
        """

        if not record_id:

            return None

        history = self._read_history()

        for record in history:

            if str(
                record.get("id")
            ) == str(
                record_id
            ):

                return record

        return None

    # ==========================================================
    # GET BY OPERATION
    # ==========================================================

    def get_by_operation(
        self,
        operation
    ):
        """
        Return records matching an operation type.
        """

        operation = str(
            operation
        ).strip().lower()

        history = self._read_history()

        return [
            record
            for record in history
            if str(
                record.get(
                    "operation",
                    ""
                )
            ).strip().lower()
            == operation
        ]

    # ==========================================================
    # GET BY STATUS
    # ==========================================================

    def get_by_status(
        self,
        status
    ):
        """
        Return records matching a status.
        """

        status = str(
            status
        ).strip().lower()

        history = self._read_history()

        return [
            record
            for record in history
            if str(
                record.get(
                    "status",
                    ""
                )
            ).strip().lower()
            == status
        ]

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(
        self,
        keyword
    ):
        """
        Search history records.

        Searches through:
            - operation
            - input_path
            - output_path
            - status
            - filename
        """

        if not keyword:

            return self.get_all()

        keyword = str(
            keyword
        ).strip().lower()

        history = self._read_history()

        results = []

        searchable_fields = [
            "operation",
            "input_path",
            "output_path",
            "status",
            "filename",
        ]

        for record in history:

            for field in searchable_fields:

                value = record.get(
                    field,
                    ""
                )

                if keyword in str(
                    value
                ).lower():

                    results.append(
                        record
                    )

                    break

        return list(
            reversed(
                results
            )
        )

    # ==========================================================
    # DELETE BY ID
    # ==========================================================

    def delete(
        self,
        record_id
    ):
        """
        Delete a history record by ID.

        Returns:
            True if deleted, otherwise False.
        """

        if not record_id:

            return False

        history = self._read_history()

        new_history = [
            record
            for record in history
            if str(
                record.get("id")
            ) != str(
                record_id
            )
        ]

        if len(
            new_history
        ) == len(
            history
        ):

            return False

        self._write_history(
            new_history
        )

        return True

    # ==========================================================
    # CLEAR HISTORY
    # ==========================================================

    def clear(
        self
    ):
        """
        Delete all history records.
        """

        self._write_history(
            []
        )

        return True

    # ==========================================================
    # COUNT
    # ==========================================================

    def count(
        self
    ):
        """
        Return number of history records.
        """

        return len(
            self._read_history()
        )

    # ==========================================================
    # LATEST
    # ==========================================================

    def latest(
        self,
        limit=10
    ):
        """
        Return the latest N records.
        """

        try:

            limit = int(
                limit
            )

        except (
            ValueError,
            TypeError
        ):

            limit = 10

        if limit <= 0:

            return []

        history = self._read_history()

        return list(
            reversed(
                history[-limit:]
            )
        )

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def get_statistics(
        self
    ):
        """
        Return basic statistics about operations.
        """

        history = self._read_history()

        total = len(
            history
        )

        successful = 0
        failed = 0

        operation_counts = {}

        for record in history:

            status = str(
                record.get(
                    "status",
                    ""
                )
            ).lower()

            operation = str(
                record.get(
                    "operation",
                    "unknown"
                )
            ).lower()

            if status == "success":

                successful += 1

            elif status == "failed":

                failed += 1

            operation_counts[
                operation
            ] = (
                operation_counts.get(
                    operation,
                    0
                )
                + 1
            )

        success_rate = (
            (
                successful
                / total
            )
            * 100
            if total > 0
            else 0
        )

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(
                success_rate,
                2
            ),
            "operation_counts": (
                operation_counts
            ),
        }

    # ==========================================================
    # EXPORT
    # ==========================================================

    def export_history(
        self,
        output_path
    ):
        """
        Export history to another JSON file.
        """

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

        history = self._read_history()

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                indent=4,
                ensure_ascii=False
            )

        return output_path

    # ==========================================================
    # IMPORT
    # ==========================================================

    def import_history(
        self,
        input_path,
        merge=True
    ):
        """
        Import records from another JSON file.

        Args:
            input_path:
                JSON file to import.

            merge:
                If True, append imported records.
                If False, replace current history.
        """

        if not input_path:

            raise ValueError(
                "Input path cannot be empty."
            )

        if not os.path.isfile(
            input_path
        ):

            raise FileNotFoundError(
                input_path
            )

        with open(
            input_path,
            "r",
            encoding="utf-8"
        ) as file:

            imported = json.load(
                file
            )

        if not isinstance(
            imported,
            list
        ):

            raise ValueError(
                "Imported history must be a JSON list."
            )

        normalized_records = []

        for record in imported:

            normalized = (
                self._normalize_record(
                    record
                )
            )

            if normalized:

                normalized_records.append(
                    normalized
                )

        if merge:

            history = self._read_history()

            existing_ids = {
                str(
                    record.get(
                        "id"
                    )
                )
                for record in history
            }

            for record in normalized_records:

                if str(
                    record.get(
                        "id"
                    )
                ) not in existing_ids:

                    history.append(
                        record
                    )

            history = history[
                -self.max_items:
            ]

        else:

            history = normalized_records[
                -self.max_items:
            ]

        self._write_history(
            history
        )

        return len(
            normalized_records
        )

    # ==========================================================
    # RESET
    # ==========================================================

    def reset(
        self
    ):
        """
        Reset history storage.
        """

        return self.clear()

    # ==========================================================
    # CHECK STORAGE
    # ==========================================================

    def storage_exists(
        self
    ):
        """
        Check whether history file exists.
        """

        return os.path.isfile(
            self.history_file
        )

    def get_storage_path(
        self
    ):
        """
        Return absolute history file path.
        """

        return os.path.abspath(
            self.history_file
        )


# ==============================================================
# SIMPLE TEST
# ==============================================================

if __name__ == "__main__":

    service = HistoryService()

    print(
        "HistoryService initialized."
    )

    print(
        "History file:",
        service.get_storage_path()
    )

    print(
        "Record count:",
        service.count()
    )

    print(
        "Statistics:",
        service.get_statistics()
    )