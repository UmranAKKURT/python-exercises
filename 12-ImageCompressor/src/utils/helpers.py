import os
import re
import time
from datetime import datetime
from typing import Any, Iterable, List, Optional, Tuple


# ----------------------------------------------------------------------
# File Helpers
# ----------------------------------------------------------------------

def get_file_extension(file_path: str) -> str:
    """
    Return file extension without the dot.

    Example:
        image.jpg -> jpg
    """
    if not file_path:
        return ""

    return os.path.splitext(file_path)[1].lower().lstrip(".")


def get_file_name(file_path: str) -> str:
    """
    Return file name without extension.
    """
    if not file_path:
        return ""

    return os.path.splitext(
        os.path.basename(file_path)
    )[0]


def get_full_file_name(file_path: str) -> str:
    """
    Return file name including extension.
    """
    if not file_path:
        return ""

    return os.path.basename(file_path)


def get_directory(file_path: str) -> str:
    """
    Return directory portion of a file path.
    """
    if not file_path:
        return ""

    return os.path.dirname(
        os.path.abspath(file_path)
    )


def is_file(path: str) -> bool:
    """
    Check whether the given path is a file.
    """
    return bool(
        path and os.path.isfile(path)
    )


def is_directory(path: str) -> bool:
    """
    Check whether the given path is a directory.
    """
    return bool(
        path and os.path.isdir(path)
    )


def ensure_directory(directory: str) -> bool:
    """
    Create a directory if it does not exist.
    """
    if not directory:
        return False

    try:
        os.makedirs(
            directory,
            exist_ok=True
        )
        return True
    except OSError:
        return False


def ensure_parent_directory(file_path: str) -> bool:
    """
    Create the parent directory of a file path.
    """
    if not file_path:
        return False

    directory = os.path.dirname(
        os.path.abspath(file_path)
    )

    if not directory:
        return True

    return ensure_directory(directory)


# ----------------------------------------------------------------------
# File Size Helpers
# ----------------------------------------------------------------------

def get_file_size(file_path: str) -> int:
    """
    Return file size in bytes.
    """
    try:
        return os.path.getsize(file_path)
    except (OSError, TypeError):
        return 0


def format_file_size(
    size_bytes: int,
    decimal_places: int = 2
) -> str:
    """
    Convert bytes into a human-readable file size.

    Example:
        1536 -> 1.50 KB
    """
    try:
        size = float(size_bytes)
    except (TypeError, ValueError):
        return "0 B"

    if size < 0:
        return "0 B"

    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ]

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.{decimal_places}f} {unit}"

        size /= 1024

    return f"{size:.{decimal_places}f} TB"


def calculate_size_reduction(
    original_size: int,
    compressed_size: int
) -> float:
    """
    Calculate percentage reduction in file size.

    Example:
        1000 -> 700 = 30%
    """
    if original_size <= 0:
        return 0.0

    reduction = (
        (original_size - compressed_size)
        / original_size
    ) * 100

    return round(
        max(0.0, reduction),
        2
    )


def calculate_size_ratio(
    original_size: int,
    compressed_size: int
) -> float:
    """
    Calculate compressed/original size ratio.
    """
    if original_size <= 0:
        return 0.0

    return round(
        compressed_size / original_size,
        4
    )


# ----------------------------------------------------------------------
# Image Helpers
# ----------------------------------------------------------------------

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif"
}


def is_supported_image(file_path: str) -> bool:
    """
    Check whether a file has a supported image extension.
    """
    if not file_path:
        return False

    extension = os.path.splitext(
        file_path
    )[1].lower()

    return extension in SUPPORTED_IMAGE_EXTENSIONS


def get_supported_image_extensions() -> List[str]:
    """
    Return supported image extensions.
    """
    return sorted(
        SUPPORTED_IMAGE_EXTENSIONS
    )


def normalize_extension(extension: str) -> str:
    """
    Normalize an extension.

    Examples:
        JPG -> .jpg
        .PNG -> .png
    """
    if not extension:
        return ""

    extension = extension.strip().lower()

    if not extension.startswith("."):
        extension = "." + extension

    return extension


# ----------------------------------------------------------------------
# Filename Helpers
# ----------------------------------------------------------------------

def sanitize_filename(
    filename: str,
    replacement: str = "_"
) -> str:
    """
    Remove characters that are invalid in file names.

    Works with Windows-compatible file names.
    """
    if not filename:
        return ""

    filename = str(filename).strip()

    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'

    filename = re.sub(
        invalid_chars,
        replacement,
        filename
    )

    filename = re.sub(
        rf"{re.escape(replacement)}+",
        replacement,
        filename
    )

    filename = filename.strip(
        " ."
    )

    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9"
    }

    name_without_extension = os.path.splitext(
        filename
    )[0]

    if name_without_extension.upper() in reserved_names:
        filename = (
            replacement
            + filename
        )

    return filename


def create_output_filename(
    input_path: str,
    suffix: str = "_compressed",
    extension: Optional[str] = None
) -> str:
    """
    Create an output file name based on an input path.

    Example:
        image.jpg
        -> image_compressed.jpg
    """
    if not input_path:
        return ""

    directory = os.path.dirname(input_path)
    filename = get_file_name(input_path)

    filename = sanitize_filename(filename)

    suffix = str(suffix)

    if extension:
        extension = normalize_extension(
            extension
        )
    else:
        extension = os.path.splitext(
            input_path
        )[1].lower()

    output_name = (
        filename
        + suffix
        + extension
    )

    if directory:
        return os.path.join(
            directory,
            output_name
        )

    return output_name


def create_unique_filename(
    file_path: str
) -> str:
    """
    Generate a unique file path without overwriting
    an existing file.

    Example:
        image.jpg
        image_1.jpg
        image_2.jpg
    """
    if not file_path:
        return ""

    if not os.path.exists(file_path):
        return file_path

    directory = os.path.dirname(file_path)

    filename = get_file_name(file_path)
    extension = os.path.splitext(
        file_path
    )[1]

    counter = 1

    while True:
        new_name = (
            f"{filename}_{counter}"
            f"{extension}"
        )

        new_path = os.path.join(
            directory,
            new_name
        )

        if not os.path.exists(new_path):
            return new_path

        counter += 1


# ----------------------------------------------------------------------
# Date / Time Helpers
# ----------------------------------------------------------------------

def get_timestamp() -> str:
    """
    Return current timestamp in ISO format.
    """
    return datetime.now().isoformat(
        timespec="seconds"
    )


def get_formatted_timestamp(
    fmt: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Return formatted current date/time.
    """
    return datetime.now().strftime(fmt)


def get_safe_timestamp() -> str:
    """
    Return timestamp suitable for file names.

    Example:
        2026-09-04_18-30-25
    """
    return datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )


# ----------------------------------------------------------------------
# Value Helpers
# ----------------------------------------------------------------------

def clamp(
    value: float,
    minimum: float,
    maximum: float
) -> float:
    """
    Restrict a value to a specific range.
    """
    return max(
        minimum,
        min(value, maximum)
    )


def safe_int(
    value: Any,
    default: int = 0
) -> int:
    """
    Safely convert a value to int.
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(
    value: Any,
    default: float = 0.0
) -> float:
    """
    Safely convert a value to float.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_bool(
    value: Any,
    default: bool = False
) -> bool:
    """
    Safely convert common values to bool.
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {
            "true",
            "1",
            "yes",
            "y",
            "on"
        }:
            return True

        if normalized in {
            "false",
            "0",
            "no",
            "n",
            "off"
        }:
            return False

    if isinstance(value, (int, float)):
        return value != 0

    return default


# ----------------------------------------------------------------------
# Collection Helpers
# ----------------------------------------------------------------------

def chunk_list(
    items: Iterable[Any],
    chunk_size: int
) -> List[List[Any]]:
    """
    Split an iterable into smaller lists.
    """
    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0"
        )

    items = list(items)

    return [
        items[index:index + chunk_size]
        for index in range(
            0,
            len(items),
            chunk_size
        )
    ]


def remove_duplicates(
    items: Iterable[Any]
) -> List[Any]:
    """
    Remove duplicates while preserving order.
    """
    result = []
    seen = set()

    for item in items:

        try:
            if item in seen:
                continue

            seen.add(item)
            result.append(item)

        except TypeError:
            if item not in result:
                result.append(item)

    return result


# ----------------------------------------------------------------------
# Text Helpers
# ----------------------------------------------------------------------

def truncate_text(
    text: str,
    max_length: int,
    suffix: str = "..."
) -> str:
    """
    Shorten text when it exceeds max_length.
    """
    if not text:
        return ""

    text = str(text)

    if len(text) <= max_length:
        return text

    if max_length <= len(suffix):
        return suffix[:max_length]

    return (
        text[:max_length - len(suffix)]
        + suffix
    )


def capitalize_words(text: str) -> str:
    """
    Convert text to title-style capitalization.
    """
    if not text:
        return ""

    return " ".join(
        word.capitalize()
        for word in str(text).split()
    )


# ----------------------------------------------------------------------
# Performance Helpers
# ----------------------------------------------------------------------

def measure_time(
    start_time: float
) -> float:
    """
    Calculate elapsed time from a perf_counter timestamp.
    """
    return round(
        time.perf_counter() - start_time,
        4
    )


# ----------------------------------------------------------------------
# Validation Helpers
# ----------------------------------------------------------------------

def is_valid_quality(quality: Any) -> bool:
    """
    Validate JPEG/WebP quality value.
    """
    return (
        isinstance(quality, int)
        and 1 <= quality <= 100
    )


def is_valid_percentage(
    percentage: Any
) -> bool:
    """
    Validate resize percentage.
    """
    return (
        isinstance(
            percentage,
            (int, float)
        )
        and percentage > 0
    )


def is_valid_dimension(
    dimension: Any
) -> bool:
    """
    Validate image dimension.
    """
    return (
        isinstance(dimension, int)
        and dimension > 0
    )


# ----------------------------------------------------------------------
# Application Helpers
# ----------------------------------------------------------------------

def build_operation_summary(
    input_path: str,
    output_path: str,
    original_size: int,
    output_size: int,
    operation: str = "compression"
) -> dict:
    """
    Build a standard operation result dictionary.
    """
    return {
        "operation": operation,
        "input_file": get_full_file_name(
            input_path
        ),
        "output_file": get_full_file_name(
            output_path
        ),
        "input_path": input_path,
        "output_path": output_path,
        "original_size": original_size,
        "output_size": output_size,
        "original_size_formatted": format_file_size(
            original_size
        ),
        "output_size_formatted": format_file_size(
            output_size
        ),
        "reduction_percent": calculate_size_reduction(
            original_size,
            output_size
        ),
        "timestamp": get_timestamp()
    }


if __name__ == "__main__":
    print("Helpers test")
    print("-" * 40)

    test_file = "example_image.jpg"

    print(
        "Extension:",
        get_file_extension(test_file)
    )

    print(
        "File name:",
        get_file_name(test_file)
    )

    print(
        "Full name:",
        get_full_file_name(test_file)
    )

    print(
        "Output name:",
        create_output_filename(test_file)
    )

    print(
        "Sanitized:",
        sanitize_filename(
            'my:image<>test?.jpg'
        )
    )

    print(
        "File size:",
        format_file_size(1536)
    )

    print(
        "Reduction:",
        calculate_size_reduction(
            1000,
            750
        ),
        "%"
    )

    print(
        "Quality valid:",
        is_valid_quality(85)
    )

    print(
        "Percentage valid:",
        is_valid_percentage(50)
    )

    print(
        "Timestamp:",
        get_timestamp()
    )