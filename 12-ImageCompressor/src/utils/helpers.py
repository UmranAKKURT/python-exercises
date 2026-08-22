import os
import re
from datetime import datetime


# ==========================================================
# FILE SIZE HELPERS
# ==========================================================

def format_bytes(
    size
):
    """
    Convert bytes to a human-readable string.

    Examples:
        1024       -> 1.00 KB
        1048576    -> 1.00 MB
    """

    try:
        size = float(size)
    except (
        ValueError,
        TypeError
    ):
        size = 0

    size = max(
        0,
        size
    )

    units = (
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    )

    for unit in units:

        if size < 1024:

            return (
                f"{size:.2f} {unit}"
            )

        size /= 1024

    return (
        f"{size:.2f} PB"
    )


def bytes_to_kb(
    size
):
    """
    Convert bytes to kilobytes.
    """

    try:
        size = float(size)
    except (
        ValueError,
        TypeError
    ):
        return 0.0

    return round(
        size / 1024,
        2
    )


def bytes_to_mb(
    size
):
    """
    Convert bytes to megabytes.
    """

    try:
        size = float(size)
    except (
        ValueError,
        TypeError
    ):
        return 0.0

    return round(
        size / (
            1024 * 1024
        ),
        2
    )


def mb_to_bytes(
    size
):
    """
    Convert megabytes to bytes.
    """

    try:
        size = float(size)
    except (
        ValueError,
        TypeError
    ):
        return 0

    return int(
        size * 1024 * 1024
    )


# ==========================================================
# COMPRESSION HELPERS
# ==========================================================

def calculate_saving_percentage(
    original_size,
    new_size
):
    """
    Calculate storage saving percentage.

    Example:
        Original = 10 MB
        New      = 7 MB

        Result = 30%
    """

    try:

        original_size = float(
            original_size
        )

        new_size = float(
            new_size
        )

    except (
        ValueError,
        TypeError
    ):

        return 0.0

    if original_size <= 0:

        return 0.0

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


def calculate_compression_ratio(
    original_size,
    new_size
):
    """
    Calculate compression ratio.

    Example:
        Original = 1000 KB
        New      = 250 KB

        Result = 4.0
    """

    try:

        original_size = float(
            original_size
        )

        new_size = float(
            new_size
        )

    except (
        ValueError,
        TypeError
    ):

        return 0.0

    if new_size <= 0:

        return 0.0

    return round(
        original_size / new_size,
        2
    )


# ==========================================================
# FILE NAME HELPERS
# ==========================================================

def get_filename(
    file_path
):
    """
    Return filename including extension.
    """

    if not file_path:

        return ""

    return os.path.basename(
        file_path
    )


def get_filename_without_extension(
    file_path
):
    """
    Return filename without extension.
    """

    if not file_path:

        return ""

    filename = os.path.basename(
        file_path
    )

    return os.path.splitext(
        filename
    )[0]


def get_extension(
    file_path
):
    """
    Return lowercase file extension.
    """

    if not file_path:

        return ""

    return (
        os.path.splitext(
            file_path
        )[1]
        .lower()
    )


def change_extension(
    file_path,
    extension
):
    """
    Change the extension of a file path.

    Does not modify the actual file.
    """

    if not file_path:

        return ""

    extension = str(
        extension
    ).strip().lower()

    if not extension.startswith(
        "."
    ):

        extension = (
            "."
            + extension
        )

    directory = os.path.dirname(
        file_path
    )

    filename = os.path.basename(
        file_path
    )

    name = os.path.splitext(
        filename
    )[0]

    return os.path.join(
        directory,
        f"{name}{extension}"
    )


# ==========================================================
# PATH HELPERS
# ==========================================================

def ensure_directory(
    directory
):
    """
    Create a directory if it does not exist.
    """

    if not directory:

        raise ValueError(
            "Directory cannot be empty."
        )

    os.makedirs(
        directory,
        exist_ok=True
    )

    return os.path.abspath(
        directory
    )


def get_unique_path(
    file_path
):
    """
    Generate a unique file path.

    Example:

        image.jpg

    becomes:

        image_1.jpg
        image_2.jpg
        ...
    """

    file_path = os.path.abspath(
        file_path
    )

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
# VALIDATION HELPERS
# ==========================================================

def is_valid_file(
    file_path
):
    """
    Check whether the given path points to a file.
    """

    if not file_path:

        return False

    return os.path.isfile(
        file_path
    )


def is_valid_directory(
    directory
):
    """
    Check whether the given path points to a directory.
    """

    if not directory:

        return False

    return os.path.isdir(
        directory
    )


def is_supported_image(
    file_path
):
    """
    Check whether a file has a supported image extension.
    """

    supported_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tiff",
        ".tif"
    }

    extension = get_extension(
        file_path
    )

    return (
        extension
        in supported_extensions
    )


# ==========================================================
# QUALITY HELPERS
# ==========================================================

def validate_quality(
    quality,
    default=80
):
    """
    Validate image quality.

    The result is always between 1 and 100.
    """

    try:

        quality = int(
            quality
        )

    except (
        ValueError,
        TypeError
    ):

        quality = default

    return max(
        1,
        min(
            100,
            quality
        )
    )


def quality_to_label(
    quality
):
    """
    Convert numerical quality into a readable label.
    """

    quality = validate_quality(
        quality
    )

    if quality >= 90:

        return "Very High"

    if quality >= 75:

        return "High"

    if quality >= 50:

        return "Medium"

    if quality >= 25:

        return "Low"

    return "Very Low"


# ==========================================================
# FORMAT HELPERS
# ==========================================================

def normalize_format(
    image_format
):
    """
    Normalize image format.

    Examples:
        jpg   -> JPG
        .png  -> PNG
        jpeg  -> JPG
        webp  -> WEBP
    """

    if not image_format:

        return ""

    image_format = str(
        image_format
    ).strip().lower()

    image_format = (
        image_format
        .replace(
            ".",
            ""
        )
    )

    if image_format == "jpeg":

        image_format = "jpg"

    return image_format.upper()


def format_to_extension(
    image_format
):
    """
    Convert image format to extension.

    Example:
        WEBP -> .webp
    """

    normalized = normalize_format(
        image_format
    )

    if not normalized:

        return ""

    return (
        "."
        + normalized.lower()
    )


def is_supported_format(
    image_format
):
    """
    Check whether an image format is supported.
    """

    supported_formats = {
        "JPG",
        "PNG",
        "WEBP"
    }

    return (
        normalize_format(
            image_format
        )
        in supported_formats
    )


# ==========================================================
# TEXT HELPERS
# ==========================================================

def sanitize_filename(
    filename
):
    """
    Remove characters that are unsafe for filenames.

    This is especially useful when generating output
    filenames automatically.
    """

    if not filename:

        return "image"

    filename = str(
        filename
    )

    # Remove extension temporarily.
    name, extension = (
        os.path.splitext(
            filename
        )
    )

    # Replace invalid Windows filename characters.
    name = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        name
    )

    # Remove control characters.
    name = re.sub(
        r"[\x00-\x1f]",
        "",
        name
    )

    # Replace multiple spaces.
    name = re.sub(
        r"\s+",
        " ",
        name
    )

    name = name.strip()

    if not name:

        name = "image"

    return (
        name
        + extension
    )


def truncate_text(
    text,
    max_length=50
):
    """
    Shorten text if it exceeds max_length.
    """

    if text is None:

        return ""

    text = str(
        text
    )

    if len(text) <= max_length:

        return text

    if max_length <= 3:

        return text[
            :max_length
        ]

    return (
        text[
            :(max_length - 3)
        ]
        + "..."
    )


# ==========================================================
# DATE / TIME HELPERS
# ==========================================================

def get_current_timestamp():
    """
    Return current date and time as a string.
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def get_current_date():
    """
    Return current date.
    """

    return datetime.now().strftime(
        "%Y-%m-%d"
    )


def get_current_time():
    """
    Return current time.
    """

    return datetime.now().strftime(
        "%H:%M:%S"
    )


# ==========================================================
# NUMBER HELPERS
# ==========================================================

def safe_int(
    value,
    default=0
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

        return default


def safe_float(
    value,
    default=0.0
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

        return default


def clamp(
    value,
    minimum,
    maximum
):
    """
    Keep a number between minimum and maximum.
    """

    value = safe_float(
        value
    )

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


# ==========================================================
# BOOLEAN HELPERS
# ==========================================================

def to_bool(
    value,
    default=False
):
    """
    Convert common values to boolean.
    """

    if isinstance(
        value,
        bool
    ):

        return value

    if isinstance(
        value,
        str
    ):

        normalized = (
            value.strip().lower()
        )

        if normalized in (
            "true",
            "1",
            "yes",
            "on",
            "enabled"
        ):

            return True

        if normalized in (
            "false",
            "0",
            "no",
            "off",
            "disabled"
        ):

            return False

    if isinstance(
        value,
        (int, float)
    ):

        return value != 0

    return default


# ==========================================================
# LIST HELPERS
# ==========================================================

def chunk_list(
    items,
    chunk_size
):
    """
    Split a list into smaller chunks.

    Example:

        [1,2,3,4,5], 2

        ->
        [[1,2], [3,4], [5]]
    """

    if not isinstance(
        items,
        list
    ):

        return []

    chunk_size = safe_int(
        chunk_size
    )

    if chunk_size <= 0:

        return []

    return [
        items[
            index:index + chunk_size
        ]
        for index in range(
            0,
            len(items),
            chunk_size
        )
    ]


# ==========================================================
# RESULT HELPERS
# ==========================================================

def create_success_result(
    **kwargs
):
    """
    Create a standardized successful operation result.
    """

    result = {
        "success": True,
        "error": None
    }

    result.update(
        kwargs
    )

    return result


def create_error_result(
    error,
    **kwargs
):
    """
    Create a standardized failed operation result.
    """

    result = {
        "success": False,
        "error": str(
            error
        )
    }

    result.update(
        kwargs
    )

    return result