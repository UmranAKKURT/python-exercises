
import csv
import json
import os
from datetime import datetime

from PIL import Image, ImageTk


# ==========================================================
# PROJECT PATHS
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

HISTORY_FILE = os.path.join(
    DATA_DIR,
    "compression_history.json"
)

CSV_HISTORY_FILE = os.path.join(
    DATA_DIR,
    "compression_history.csv"
)


# Data klasörü yoksa oluştur
os.makedirs(
    DATA_DIR,
    exist_ok=True
)


# ==========================================================
# FILE SIZE
# ==========================================================

def readable_size(size):
    """
    Convert bytes to a human-readable size.

    Examples:
        512 -> 512 B
        2048 -> 2.00 KB
        1048576 -> 1.00 MB
    """

    if size is None:
        return "0 B"

    size = float(size)

    if size < 1024:
        return f"{size:.0f} B"

    size /= 1024

    if size < 1024:
        return f"{size:.2f} KB"

    size /= 1024

    if size < 1024:
        return f"{size:.2f} MB"

    size /= 1024

    return f"{size:.2f} GB"


def file_size(path):
    """
    Return file size in bytes.
    """

    if not os.path.exists(path):
        return 0

    return os.path.getsize(path)


# ==========================================================
# IMAGE INFORMATION
# ==========================================================

def image_resolution(path):
    """
    Return image resolution as:

        (width, height)
    """

    with Image.open(path) as img:
        return img.size


def image_format(path):
    """
    Return image format.

    Example:
        JPEG
        PNG
        WEBP
    """

    with Image.open(path) as img:
        return img.format or "Unknown"


def image_mode(path):
    """
    Return PIL image mode.

    Examples:
        RGB
        RGBA
        P
    """

    with Image.open(path) as img:
        return img.mode


def has_transparency(path):
    """
    Check whether the image contains transparency.
    """

    with Image.open(path) as img:

        if img.mode in ("RGBA", "LA"):
            return True

        if img.mode == "P":
            return "transparency" in img.info

        return False


# ==========================================================
# THUMBNAIL
# ==========================================================

def create_thumbnail(
    path,
    size=(250, 250)
):
    """
    Create a Tkinter-compatible thumbnail.
    """

    img = Image.open(path)

    img.thumbnail(
        size,
        Image.Resampling.LANCZOS
    )

    return ImageTk.PhotoImage(img)


# ==========================================================
# VALIDATION
# ==========================================================

SUPPORTED_FORMATS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".webp"
)


def validate_image(path):
    """
    Check whether the file has a supported extension.
    """

    if not path:
        return False

    if not os.path.isfile(path):
        return False

    extension = os.path.splitext(
        path
    )[1].lower()

    return extension in SUPPORTED_FORMATS


# ==========================================================
# COMPRESSION CALCULATIONS
# ==========================================================

def compression_ratio(
    original_size,
    compressed_size
):
    """
    Calculate saved space percentage.
    """

    if original_size <= 0:
        return 0

    return (
        (original_size - compressed_size)
        / original_size
    ) * 100


def saved_bytes(
    original_size,
    compressed_size
):
    """
    Return the amount of saved bytes.
    """

    return max(
        0,
        original_size - compressed_size
    )


def estimate_size(
    original_size,
    quality
):
    """
    Roughly estimate compressed size.

    NOTE:
    This is only an estimation.
    Actual image compression depends on
    image content and output format.
    """

    quality = max(
        1,
        min(
            100,
            int(quality)
        )
    )

    # A simple nonlinear approximation.
    factor = (
        0.15 +
        0.85 * (quality / 100)
    )

    return int(
        original_size * factor
    )


def estimate_saving(
    original_size,
    estimated_size
):
    """
    Estimate saved percentage.
    """

    if original_size <= 0:
        return 0

    return (
        (original_size - estimated_size)
        / original_size
    ) * 100


# ==========================================================
# HISTORY
# ==========================================================

def create_history_item(
    filename,
    original_size,
    compressed_size,
    ratio,
    quality=None,
    output_format=None,
    original_resolution=None,
    new_resolution=None,
    processing_time=None
):
    """
    Create a history record.

    New fields are optional so older parts of the
    application can still use this function.
    """

    original_size = int(
        original_size
    )

    compressed_size = int(
        compressed_size
    )

    record = {
        "filename": filename,
        "date": datetime.now().strftime(
            "%d.%m.%Y %H:%M:%S"
        ),
        "original": original_size,
        "compressed": compressed_size,
        "saved": max(
            0,
            original_size - compressed_size
        ),
        "ratio": round(
            ratio,
            2
        )
    }

    if quality is not None:
        record["quality"] = int(
            quality
        )

    if output_format:
        record["format"] = str(
            output_format
        ).upper()

    if original_resolution:
        record["original_resolution"] = (
            f"{original_resolution[0]}"
            f"x"
            f"{original_resolution[1]}"
        )

    if new_resolution:
        record["new_resolution"] = (
            f"{new_resolution[0]}"
            f"x"
            f"{new_resolution[1]}"
        )

    if processing_time is not None:
        record["processing_time"] = round(
            float(processing_time),
            3
        )

    return record


def load_history():
    """
    Load compression history from JSON.
    """

    if not os.path.exists(
        HISTORY_FILE
    ):
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(
                data,
                list
            ):
                return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        pass

    return []


def save_history(data):
    """
    Append a new history record.
    """

    history = load_history()

    history.append(
        data
    )

    try:

        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                indent=4,
                ensure_ascii=False
            )

    except OSError as error:

        raise OSError(
            f"Could not save history: {error}"
        )


def clear_history():
    """
    Delete all history records.
    """

    try:

        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [],
                file,
                indent=4
            )

    except OSError as error:

        raise OSError(
            f"Could not clear history: {error}"
        )


# ==========================================================
# HISTORY STATISTICS
# ==========================================================

def history_statistics():
    """
    Calculate general compression statistics.
    """

    history = load_history()

    if not history:

        return {
            "count": 0,
            "original_bytes": 0,
            "compressed_bytes": 0,
            "saved_bytes": 0,
            "average_ratio": 0,
            "average_processing_time": 0
        }

    total_original = 0
    total_compressed = 0
    total_saved = 0
    total_ratio = 0

    processing_times = []

    for item in history:

        original = int(
            item.get(
                "original",
                0
            )
        )

        compressed = int(
            item.get(
                "compressed",
                0
            )
        )

        saved = int(
            item.get(
                "saved",
                max(
                    0,
                    original - compressed
                )
            )
        )

        ratio = float(
            item.get(
                "ratio",
                0
            )
        )

        total_original += original
        total_compressed += compressed
        total_saved += saved
        total_ratio += ratio

        if "processing_time" in item:

            try:
                processing_times.append(
                    float(
                        item["processing_time"]
                    )
                )
            except (
                ValueError,
                TypeError
            ):
                pass

    average_time = (
        sum(processing_times)
        / len(processing_times)
        if processing_times
        else 0
    )

    return {
        "count": len(history),
        "original_bytes": total_original,
        "compressed_bytes": total_compressed,
        "saved_bytes": total_saved,
        "average_ratio": (
            total_ratio / len(history)
        ),
        "average_processing_time": average_time
    }


# ==========================================================
# FORMAT STATISTICS
# ==========================================================

def format_statistics():
    """
    Count how many times each output format was used.
    """

    history = load_history()

    statistics = {}

    for item in history:

        fmt = item.get(
            "format",
            "UNKNOWN"
        )

        fmt = str(
            fmt
        ).upper()

        statistics[fmt] = (
            statistics.get(
                fmt,
                0
            ) + 1
        )

    return statistics


# ==========================================================
# CSV EXPORT
# ==========================================================

def export_history_csv(
    output_path=None
):
    """
    Export compression history to CSV.

    Returns the generated CSV path.
    """

    history = load_history()

    if output_path is None:
        output_path = CSV_HISTORY_FILE

    if not history:
        raise ValueError(
            "There is no compression history to export."
        )

    # Collect all possible fields so older
    # and newer history records can coexist.
    fields = []

    for item in history:

        for key in item.keys():

            if key not in fields:
                fields.append(key)

    try:

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

            for item in history:
                writer.writerow(item)

    except OSError as error:

        raise OSError(
            f"Could not export CSV: {error}"
        )

    return output_path


# ==========================================================
# UNIQUE FILE NAME
# ==========================================================

def unique_filename(path):
    """
    Prevent overwriting an existing file.

    Example:

        image.jpg
        image(1).jpg
        image(2).jpg
    """

    if not os.path.exists(path):
        return path

    directory = os.path.dirname(
        path
    )

    name = os.path.splitext(
        os.path.basename(path)
    )[0]

    extension = os.path.splitext(
        path
    )[1]

    counter = 1

    while True:

        new_path = os.path.join(
            directory,
            f"{name}({counter}){extension}"
        )

        if not os.path.exists(
            new_path
        ):
            return new_path

        counter += 1


# ==========================================================
# PERFORMANCE HELPERS
# ==========================================================

def calculate_speed(
    processed_bytes,
    processing_time
):
    """
    Calculate processing speed in MB/s.
    """

    if processing_time <= 0:
        return 0

    megabytes = (
        processed_bytes
        / (1024 * 1024)
    )

    return megabytes / processing_time


# ==========================================================
# TARGET SIZE HELPERS
# ==========================================================

def target_size_status(
    current_size,
    target_size_kb
):
    """
    Compare current file size with target size.

    Returns:
        {
            "reached": bool,
            "current_kb": float,
            "target_kb": float,
            "difference_kb": float
        }
    """

    current_kb = (
        current_size / 1024
    )

    target_kb = float(
        target_size_kb
    )

    difference = (
        current_kb - target_kb
    )

    return {
        "reached": current_kb <= target_kb,
        "current_kb": round(
            current_kb,
            2
        ),
        "target_kb": round(
            target_kb,
            2
        ),
        "difference_kb": round(
            difference,
            2
        )
    }