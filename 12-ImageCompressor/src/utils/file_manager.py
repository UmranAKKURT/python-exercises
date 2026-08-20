import os
import shutil
from pathlib import Path


class FileManager:
    """
    Centralized file and directory management service.

    Responsibilities:
        - Find image files
        - Validate files and directories
        - Create directories
        - Generate unique file names
        - Get file information
        - Copy files
        - Delete files
    """

    # ==========================================================
    # SUPPORTED IMAGE EXTENSIONS
    # ==========================================================

    SUPPORTED_IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tiff",
        ".tif"
    }

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        supported_extensions=None
    ):
        """
        Initialize FileManager.

        Args:
            supported_extensions:
                Optional custom set of image extensions.
        """

        if supported_extensions:

            self.supported_extensions = {
                self.normalize_extension(
                    extension
                )
                for extension in (
                    supported_extensions
                )
            }

        else:

            self.supported_extensions = (
                self.SUPPORTED_IMAGE_EXTENSIONS.copy()
            )

    # ==========================================================
    # FILE EXISTS
    # ==========================================================

    @staticmethod
    def file_exists(
        file_path
    ):
        """
        Check whether a file exists.
        """

        if not file_path:

            return False

        return os.path.isfile(
            file_path
        )

    # ==========================================================
    # DIRECTORY EXISTS
    # ==========================================================

    @staticmethod
    def directory_exists(
        directory_path
    ):
        """
        Check whether a directory exists.
        """

        if not directory_path:

            return False

        return os.path.isdir(
            directory_path
        )

    # ==========================================================
    # CREATE DIRECTORY
    # ==========================================================

    @staticmethod
    def create_directory(
        directory_path
    ):
        """
        Create a directory if it does not exist.

        Returns:
            Absolute directory path.
        """

        if not directory_path:

            raise ValueError(
                "Directory path cannot be empty."
            )

        os.makedirs(
            directory_path,
            exist_ok=True
        )

        return os.path.abspath(
            directory_path
        )

    # ==========================================================
    # CREATE DIRECTORIES
    # ==========================================================

    @staticmethod
    def create_directories(
        *directories
    ):
        """
        Create multiple directories.
        """

        created = []

        for directory in directories:

            if not directory:
                continue

            created.append(
                FileManager.create_directory(
                    directory
                )
            )

        return created

    # ==========================================================
    # GET FILE EXTENSION
    # ==========================================================

    @staticmethod
    def get_extension(
        file_path
    ):
        """
        Return the lowercase extension of a file.

        Example:
            image.JPG -> .jpg
        """

        if not file_path:

            return ""

        return (
            os.path.splitext(
                file_path
            )[1]
            .lower()
        )

    # ==========================================================
    # NORMALIZE EXTENSION
    # ==========================================================

    @staticmethod
    def normalize_extension(
        extension
    ):
        """
        Normalize an extension.

        Examples:

            jpg  -> .jpg
            JPEG -> .jpeg
            .PNG -> .png
        """

        if not extension:

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

        return extension

    # ==========================================================
    # IS IMAGE
    # ==========================================================

    def is_image(
        self,
        file_path
    ):
        """
        Check whether a file is a supported image.
        """

        if not self.file_exists(
            file_path
        ):

            return False

        extension = (
            self.get_extension(
                file_path
            )
        )

        return (
            extension
            in self.supported_extensions
        )

    # ==========================================================
    # FIND IMAGES
    # ==========================================================

    def find_images(
        self,
        directory,
        recursive=False
    ):
        """
        Find supported image files in a directory.

        Args:
            directory:
                Directory to search.

            recursive:
                If True, search subdirectories too.

        Returns:
            Sorted list of image paths.
        """

        if not self.directory_exists(
            directory
        ):

            raise FileNotFoundError(
                f"Directory not found: "
                f"{directory}"
            )

        image_files = []

        if recursive:

            for root, _, filenames in os.walk(
                directory
            ):

                for filename in filenames:

                    path = os.path.join(
                        root,
                        filename
                    )

                    if self.is_image(
                        path
                    ):

                        image_files.append(
                            os.path.abspath(
                                path
                            )
                        )

        else:

            for filename in os.listdir(
                directory
            ):

                path = os.path.join(
                    directory,
                    filename
                )

                if self.is_image(
                    path
                ):

                    image_files.append(
                        os.path.abspath(
                            path
                        )
                    )

        return sorted(
            image_files,
            key=lambda path: path.lower()
        )

    # ==========================================================
    # FIND FILES
    # ==========================================================

    @staticmethod
    def find_files(
        directory,
        recursive=False
    ):
        """
        Find all files in a directory.
        """

        if not os.path.isdir(
            directory
        ):

            raise FileNotFoundError(
                f"Directory not found: "
                f"{directory}"
            )

        files = []

        if recursive:

            for root, _, filenames in os.walk(
                directory
            ):

                for filename in filenames:

                    files.append(
                        os.path.abspath(
                            os.path.join(
                                root,
                                filename
                            )
                        )
                    )

        else:

            for filename in os.listdir(
                directory
            ):

                path = os.path.join(
                    directory,
                    filename
                )

                if os.path.isfile(
                    path
                ):

                    files.append(
                        os.path.abspath(
                            path
                        )
                    )

        return sorted(
            files,
            key=lambda path: path.lower()
        )

    # ==========================================================
    # GET FILE NAME
    # ==========================================================

    @staticmethod
    def get_filename(
        file_path,
        with_extension=True
    ):
        """
        Return file name.

        Examples:

            image.jpg -> image.jpg

            image.jpg -> image
        """

        if not file_path:

            return ""

        filename = os.path.basename(
            file_path
        )

        if with_extension:

            return filename

        return os.path.splitext(
            filename
        )[0]

    # ==========================================================
    # GET FILE NAME WITHOUT EXTENSION
    # ==========================================================

    @staticmethod
    def get_stem(
        file_path
    ):
        """
        Return file name without extension.
        """

        if not file_path:

            return ""

        return Path(
            file_path
        ).stem

    # ==========================================================
    # GET FILE SIZE
    # ==========================================================

    @staticmethod
    def get_file_size(
        file_path
    ):
        """
        Return file size in bytes.
        """

        if not os.path.isfile(
            file_path
        ):

            return 0

        try:

            return os.path.getsize(
                file_path
            )

        except OSError:

            return 0

    # ==========================================================
    # GET FILE SIZE MB
    # ==========================================================

    @staticmethod
    def get_file_size_mb(
        file_path
    ):
        """
        Return file size in megabytes.
        """

        size = (
            FileManager.get_file_size(
                file_path
            )
        )

        return round(
            size / (
                1024 * 1024
            ),
            2
        )

    # ==========================================================
    # FORMAT FILE SIZE
    # ==========================================================

    @staticmethod
    def format_file_size(
        size
    ):
        """
        Convert byte size to readable format.
        """

        try:

            size = float(
                size
            )

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
                    f"{size:.2f} "
                    f"{unit}"
                )

            size /= 1024

        return (
            f"{size:.2f} PB"
        )

    # ==========================================================
    # GET DIRECTORY
    # ==========================================================

    @staticmethod
    def get_directory(
        file_path
    ):
        """
        Return the directory containing a file.
        """

        if not file_path:

            return ""

        return os.path.dirname(
            os.path.abspath(
                file_path
            )
        )

    # ==========================================================
    # BUILD PATH
    # ==========================================================

    @staticmethod
    def build_path(
        directory,
        filename
    ):
        """
        Build an absolute path.
        """

        if not directory:

            raise ValueError(
                "Directory cannot be empty."
            )

        if not filename:

            raise ValueError(
                "Filename cannot be empty."
            )

        return os.path.abspath(
            os.path.join(
                directory,
                filename
            )
        )

    # ==========================================================
    # UNIQUE FILE PATH
    # ==========================================================

    @staticmethod
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
    # COPY FILE
    # ==========================================================

    @staticmethod
    def copy_file(
        source,
        destination,
        overwrite=False
    ):
        """
        Copy a file to another location.

        If overwrite=False, a unique destination path
        is automatically generated.
        """

        if not os.path.isfile(
            source
        ):

            raise FileNotFoundError(
                f"Source file not found: "
                f"{source}"
            )

        destination_directory = (
            os.path.dirname(
                os.path.abspath(
                    destination
                )
            )
        )

        if destination_directory:

            os.makedirs(
                destination_directory,
                exist_ok=True
            )

        if (
            os.path.exists(
                destination
            )
            and not overwrite
        ):

            destination = (
                FileManager.get_unique_path(
                    destination
                )
            )

        shutil.copy2(
            source,
            destination
        )

        return os.path.abspath(
            destination
        )

    # ==========================================================
    # MOVE FILE
    # ==========================================================

    @staticmethod
    def move_file(
        source,
        destination,
        overwrite=False
    ):
        """
        Move a file to another location.
        """

        if not os.path.isfile(
            source
        ):

            raise FileNotFoundError(
                f"Source file not found: "
                f"{source}"
            )

        destination_directory = (
            os.path.dirname(
                os.path.abspath(
                    destination
                )
            )
        )

        if destination_directory:

            os.makedirs(
                destination_directory,
                exist_ok=True
            )

        if (
            os.path.exists(
                destination
            )
            and not overwrite
        ):

            destination = (
                FileManager.get_unique_path(
                    destination
                )
            )

        shutil.move(
            source,
            destination
        )

        return os.path.abspath(
            destination
        )

    # ==========================================================
    # DELETE FILE
    # ==========================================================

    @staticmethod
    def delete_file(
        file_path
    ):
        """
        Delete a file.

        Returns:
            True if deleted, otherwise False.
        """

        if not os.path.isfile(
            file_path
        ):

            return False

        try:

            os.remove(
                file_path
            )

            return True

        except OSError:

            return False

    # ==========================================================
    # DELETE DIRECTORY
    # ==========================================================

    @staticmethod
    def delete_directory(
        directory_path,
        force=False
    ):
        """
        Delete a directory.

        Args:
            force:
                If True, delete directory recursively.
        """

        if not os.path.isdir(
            directory_path
        ):

            return False

        try:

            if force:

                shutil.rmtree(
                    directory_path
                )

            else:

                os.rmdir(
                    directory_path
                )

            return True

        except OSError:

            return False

    # ==========================================================
    # RENAME FILE
    # ==========================================================

    @staticmethod
    def rename_file(
        file_path,
        new_name,
        overwrite=False
    ):
        """
        Rename a file while keeping it in the same directory.
        """

        if not os.path.isfile(
            file_path
        ):

            raise FileNotFoundError(
                f"File not found: "
                f"{file_path}"
            )

        if not new_name:

            raise ValueError(
                "New filename cannot be empty."
            )

        directory = (
            os.path.dirname(
                os.path.abspath(
                    file_path
                )
            )
        )

        destination = os.path.join(
            directory,
            new_name
        )

        if (
            os.path.exists(
                destination
            )
            and not overwrite
        ):

            destination = (
                FileManager.get_unique_path(
                    destination
                )
            )

        os.rename(
            file_path,
            destination
        )

        return os.path.abspath(
            destination
        )

    # ==========================================================
    # PREPARE OUTPUT DIRECTORY
    # ==========================================================

    @staticmethod
    def prepare_output_directory(
        output_directory,
        clear=False
    ):
        """
        Prepare an output directory.

        If clear=True, existing files inside the directory
        are removed.
        """

        if not output_directory:

            raise ValueError(
                "Output directory cannot be empty."
            )

        output_directory = os.path.abspath(
            output_directory
        )

        os.makedirs(
            output_directory,
            exist_ok=True
        )

        if clear:

            for item in os.listdir(
                output_directory
            ):

                item_path = os.path.join(
                    output_directory,
                    item
                )

                try:

                    if os.path.isfile(
                        item_path
                    ):

                        os.remove(
                            item_path
                        )

                    elif os.path.isdir(
                        item_path
                    ):

                        shutil.rmtree(
                            item_path
                        )

                except OSError:

                    pass

        return output_directory

    # ==========================================================
    # GET FILE INFORMATION
    # ==========================================================

    def get_file_info(
        self,
        file_path
    ):
        """
        Return detailed information about a file.
        """

        if not self.file_exists(
            file_path
        ):

            return {
                "exists": False,
                "path": os.path.abspath(
                    file_path
                )
                if file_path
                else "",
                "filename": "",
                "extension": "",
                "size": 0,
                "size_formatted": "0.00 B",
                "is_image": False
            }

        size = (
            self.get_file_size(
                file_path
            )
        )

        return {
            "exists": True,

            "path": os.path.abspath(
                file_path
            ),

            "filename": self.get_filename(
                file_path
            ),

            "name": self.get_filename(
                file_path,
                with_extension=False
            ),

            "extension": self.get_extension(
                file_path
            ),

            "size": size,

            "size_formatted": (
                self.format_file_size(
                    size
                )
            ),

            "is_image": self.is_image(
                file_path
            )
        }

    # ==========================================================
    # GET DIRECTORY SIZE
    # ==========================================================

    @staticmethod
    def get_directory_size(
        directory
    ):
        """
        Calculate total size of all files in a directory.
        """

        if not os.path.isdir(
            directory
        ):

            return 0

        total_size = 0

        for root, _, filenames in os.walk(
            directory
        ):

            for filename in filenames:

                path = os.path.join(
                    root,
                    filename
                )

                try:

                    total_size += os.path.getsize(
                        path
                    )

                except OSError:

                    continue

        return total_size

    # ==========================================================
    # GET IMAGE COUNT
    # ==========================================================

    def get_image_count(
        self,
        directory,
        recursive=False
    ):
        """
        Return number of supported images in a directory.
        """

        return len(
            self.find_images(
                directory,
                recursive=recursive
            )
        )

    # ==========================================================
    # GET RELATIVE PATH
    # ==========================================================

    @staticmethod
    def get_relative_path(
        file_path,
        base_directory
    ):
        """
        Return file path relative to a base directory.
        """

        return os.path.relpath(
            os.path.abspath(
                file_path
            ),
            os.path.abspath(
                base_directory
            )
        )

    # ==========================================================
    # CHANGE EXTENSION
    # ==========================================================

    @staticmethod
    def change_extension(
        file_path,
        new_extension
    ):
        """
        Change the extension of a file path.

        This method does not modify the actual file.
        """

        if not file_path:

            raise ValueError(
                "File path cannot be empty."
            )

        new_extension = (
            FileManager.normalize_extension(
                new_extension
            )
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
            f"{name}{new_extension}"
        )

    # ==========================================================
    # VALIDATE IMAGE FILE
    # ==========================================================

    def validate_image(
        self,
        file_path
    ):
        """
        Validate that a file exists and has a supported
        image extension.
        """

        if not self.file_exists(
            file_path
        ):

            return {
                "valid": False,
                "reason": "File does not exist."
            }

        if not self.is_image(
            file_path
        ):

            return {
                "valid": False,
                "reason": "Unsupported image format."
            }

        return {
            "valid": True,
            "reason": None
        }

    # ==========================================================
    # GET SUPPORTED EXTENSIONS
    # ==========================================================

    def get_supported_extensions(
        self
    ):
        """
        Return supported image extensions.
        """

        return sorted(
            self.supported_extensions
        )

    # ==========================================================
    # GET SUPPORTED EXTENSIONS STRING
    # ==========================================================

    def get_supported_extensions_string(
        self
    ):
        """
        Return extensions in a readable format.
        """

        return ", ".join(
            self.get_supported_extensions()
        )