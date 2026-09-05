import os
import shutil
from typing import List, Optional, Tuple


class FileManager:
    """
    Utility class for file and directory operations used by
    the Image Compressor application.
    """

    SUPPORTED_IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tiff",
        ".tif"
    }

    # ------------------------------------------------------------------
    # Path Operations
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize and return an absolute path.
        """
        if not path:
            return ""

        return os.path.abspath(
            os.path.normpath(path)
        )

    @staticmethod
    def get_directory(path: str) -> str:
        """
        Return the directory portion of a path.
        """
        if not path:
            return ""

        return os.path.dirname(
            FileManager.normalize_path(path)
        )

    @staticmethod
    def get_filename(path: str) -> str:
        """
        Return filename including extension.
        """
        if not path:
            return ""

        return os.path.basename(path)

    @staticmethod
    def get_filename_without_extension(path: str) -> str:
        """
        Return filename without extension.
        """
        if not path:
            return ""

        filename = os.path.basename(path)

        return os.path.splitext(
            filename
        )[0]

    @staticmethod
    def get_extension(path: str) -> str:
        """
        Return file extension including the dot.
        """
        if not path:
            return ""

        return os.path.splitext(path)[1].lower()

    # ------------------------------------------------------------------
    # Existence Checks
    # ------------------------------------------------------------------

    @staticmethod
    def exists(path: str) -> bool:
        """
        Check whether a path exists.
        """
        return bool(
            path and os.path.exists(path)
        )

    @staticmethod
    def is_file(path: str) -> bool:
        """
        Check whether path is a file.
        """
        return bool(
            path and os.path.isfile(path)
        )

    @staticmethod
    def is_directory(path: str) -> bool:
        """
        Check whether path is a directory.
        """
        return bool(
            path and os.path.isdir(path)
        )

    # ------------------------------------------------------------------
    # Directory Operations
    # ------------------------------------------------------------------

    @staticmethod
    def create_directory(
        directory: str
    ) -> bool:
        """
        Create a directory recursively.
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

    @staticmethod
    def create_parent_directory(
        file_path: str
    ) -> bool:
        """
        Create the parent directory of a file.
        """
        if not file_path:
            return False

        directory = os.path.dirname(
            FileManager.normalize_path(file_path)
        )

        if not directory:
            return True

        return FileManager.create_directory(
            directory
        )

    @staticmethod
    def list_directory(
        directory: str,
        include_files: bool = True,
        include_directories: bool = False
    ) -> List[str]:
        """
        List items inside a directory.

        Returns full paths.
        """
        if not FileManager.is_directory(directory):
            return []

        results = []

        try:
            for item in os.listdir(directory):

                full_path = os.path.join(
                    directory,
                    item
                )

                if os.path.isfile(full_path):
                    if include_files:
                        results.append(full_path)

                elif os.path.isdir(full_path):
                    if include_directories:
                        results.append(full_path)

        except OSError:
            return []

        return sorted(results)

    # ------------------------------------------------------------------
    # File Operations
    # ------------------------------------------------------------------

    @staticmethod
    def copy_file(
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> bool:
        """
        Copy a file to another location.
        """
        if not FileManager.is_file(source):
            return False

        if (
            FileManager.exists(destination)
            and not overwrite
        ):
            return False

        if not FileManager.create_parent_directory(
            destination
        ):
            return False

        try:
            shutil.copy2(
                source,
                destination
            )
            return True

        except OSError:
            return False

    @staticmethod
    def move_file(
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> bool:
        """
        Move a file to another location.
        """
        if not FileManager.is_file(source):
            return False

        if (
            FileManager.exists(destination)
            and not overwrite
        ):
            return False

        if not FileManager.create_parent_directory(
            destination
        ):
            return False

        try:
            if overwrite and os.path.exists(destination):
                os.remove(destination)

            shutil.move(
                source,
                destination
            )

            return True

        except OSError:
            return False

    @staticmethod
    def delete_file(
        file_path: str
    ) -> bool:
        """
        Delete a file.
        """
        if not FileManager.is_file(file_path):
            return False

        try:
            os.remove(file_path)
            return True

        except OSError:
            return False

    @staticmethod
    def rename_file(
        file_path: str,
        new_name: str,
        overwrite: bool = False
    ) -> Optional[str]:
        """
        Rename a file.

        Returns:
            New path when successful, otherwise None.
        """
        if not FileManager.is_file(file_path):
            return None

        if not new_name:
            return None

        directory = FileManager.get_directory(
            file_path
        )

        destination = os.path.join(
            directory,
            new_name
        )

        if (
            FileManager.exists(destination)
            and not overwrite
        ):
            return None

        try:
            if overwrite and os.path.exists(destination):
                os.remove(destination)

            os.rename(
                file_path,
                destination
            )

            return destination

        except OSError:
            return None

    # ------------------------------------------------------------------
    # Unique File Names
    # ------------------------------------------------------------------

    @staticmethod
    def get_unique_path(
        file_path: str
    ) -> str:
        """
        Return a unique path without overwriting existing files.

        Example:
            image.jpg
            image_1.jpg
            image_2.jpg
        """
        if not file_path:
            return ""

        if not FileManager.exists(file_path):
            return file_path

        directory = FileManager.get_directory(
            file_path
        )

        filename = (
            FileManager.get_filename_without_extension(
                file_path
            )
        )

        extension = FileManager.get_extension(
            file_path
        )

        counter = 1

        while True:
            candidate = os.path.join(
                directory,
                f"{filename}_{counter}{extension}"
            )

            if not FileManager.exists(candidate):
                return candidate

            counter += 1

    # ------------------------------------------------------------------
    # Image File Operations
    # ------------------------------------------------------------------

    @staticmethod
    def is_supported_image(
        file_path: str
    ) -> bool:
        """
        Check whether a file has a supported image extension.
        """
        extension = FileManager.get_extension(
            file_path
        )

        return (
            extension
            in FileManager.SUPPORTED_IMAGE_EXTENSIONS
        )

    @staticmethod
    def get_image_files(
        directory: str,
        recursive: bool = False
    ) -> List[str]:
        """
        Return image files from a directory.
        """
        if not FileManager.is_directory(directory):
            return []

        results = []

        if recursive:

            for root, _, files in os.walk(directory):

                for filename in files:

                    full_path = os.path.join(
                        root,
                        filename
                    )

                    if FileManager.is_supported_image(
                        full_path
                    ):
                        results.append(full_path)

        else:

            for filename in os.listdir(directory):

                full_path = os.path.join(
                    directory,
                    filename
                )

                if (
                    os.path.isfile(full_path)
                    and FileManager.is_supported_image(
                        full_path
                    )
                ):
                    results.append(full_path)

        return sorted(results)

    @staticmethod
    def get_image_files_from_paths(
        paths: List[str]
    ) -> List[str]:
        """
        Filter a list of paths and return valid image files.
        """
        if not paths:
            return []

        return [
            path
            for path in paths
            if FileManager.is_file(path)
            and FileManager.is_supported_image(path)
        ]

    # ------------------------------------------------------------------
    # File Information
    # ------------------------------------------------------------------

    @staticmethod
    def get_file_size(
        file_path: str
    ) -> int:
        """
        Return file size in bytes.
        """
        if not FileManager.is_file(file_path):
            return 0

        try:
            return os.path.getsize(
                file_path
            )

        except OSError:
            return 0

    @staticmethod
    def get_file_info(
        file_path: str
    ) -> dict:
        """
        Return basic information about a file.
        """
        if not FileManager.is_file(file_path):
            return {}

        try:
            stat = os.stat(file_path)

            return {
                "path": FileManager.normalize_path(
                    file_path
                ),
                "filename": FileManager.get_filename(
                    file_path
                ),
                "extension": FileManager.get_extension(
                    file_path
                ),
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "is_image": FileManager.is_supported_image(
                    file_path
                )
            }

        except OSError:
            return {}

    # ------------------------------------------------------------------
    # File Validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_input_file(
        file_path: str
    ) -> Tuple[bool, str]:
        """
        Validate an image input file.

        Returns:
            (success, message)
        """
        if not file_path:
            return False, "No file path provided."

        if not FileManager.exists(file_path):
            return False, "File does not exist."

        if not FileManager.is_file(file_path):
            return False, "Path is not a file."

        if not FileManager.is_supported_image(file_path):
            return False, "Unsupported image format."

        if FileManager.get_file_size(file_path) <= 0:
            return False, "File is empty."

        return True, "File is valid."

    # ------------------------------------------------------------------
    # Batch Operations
    # ------------------------------------------------------------------

    @staticmethod
    def copy_files(
        files: List[str],
        output_directory: str,
        overwrite: bool = False
    ) -> dict:
        """
        Copy multiple files to a directory.

        Returns operation statistics.
        """
        result = {
            "total": len(files),
            "successful": 0,
            "failed": 0,
            "files": []
        }

        if not FileManager.create_directory(
            output_directory
        ):
            result["failed"] = len(files)
            return result

        for source in files:

            if not FileManager.is_file(source):
                result["failed"] += 1

                result["files"].append({
                    "source": source,
                    "success": False,
                    "destination": None
                })

                continue

            destination = os.path.join(
                output_directory,
                FileManager.get_filename(source)
            )

            if not overwrite:
                destination = FileManager.get_unique_path(
                    destination
                )

            success = FileManager.copy_file(
                source,
                destination,
                overwrite=overwrite
            )

            if success:
                result["successful"] += 1
            else:
                result["failed"] += 1

            result["files"].append({
                "source": source,
                "success": success,
                "destination": destination
            })

        return result

    # ------------------------------------------------------------------
    # Temporary / Cleanup Operations
    # ------------------------------------------------------------------

    @staticmethod
    def clear_directory(
        directory: str
    ) -> bool:
        """
        Remove all files and subdirectories inside a directory.
        The directory itself is preserved.
        """
        if not FileManager.is_directory(directory):
            return False

        try:
            for item in os.listdir(directory):

                path = os.path.join(
                    directory,
                    item
                )

                if os.path.isdir(path):
                    shutil.rmtree(path)

                else:
                    os.remove(path)

            return True

        except OSError:
            return False

    @staticmethod
    def delete_directory(
        directory: str
    ) -> bool:
        """
        Delete a directory and all its contents.
        """
        if not FileManager.is_directory(directory):
            return False

        try:
            shutil.rmtree(directory)
            return True

        except OSError:
            return False

    # ------------------------------------------------------------------
    # Path Generation
    # ------------------------------------------------------------------

    @staticmethod
    def build_path(
        directory: str,
        filename: str
    ) -> str:
        """
        Safely combine directory and filename.
        """
        if not directory:
            return filename

        if not filename:
            return directory

        return os.path.join(
            directory,
            filename
        )

    @staticmethod
    def change_extension(
        file_path: str,
        new_extension: str
    ) -> str:
        """
        Change the extension of a file path.

        Example:
            image.jpg -> image.webp
        """
        if not file_path or not new_extension:
            return file_path

        if not new_extension.startswith("."):
            new_extension = "." + new_extension

        base = os.path.splitext(
            file_path
        )[0]

        return base + new_extension.lower()

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    @staticmethod
    def get_supported_extensions() -> List[str]:
        """
        Return supported image extensions.
        """
        return sorted(
            FileManager.SUPPORTED_IMAGE_EXTENSIONS
        )

    @staticmethod
    def count_files(
        directory: str,
        images_only: bool = False,
        recursive: bool = False
    ) -> int:
        """
        Count files in a directory.
        """
        if images_only:
            return len(
                FileManager.get_image_files(
                    directory,
                    recursive=recursive
                )
            )

        if not FileManager.is_directory(directory):
            return 0

        if not recursive:
            return len([
                item
                for item in os.listdir(directory)
                if os.path.isfile(
                    os.path.join(
                        directory,
                        item
                    )
                )
            ])

        count = 0

        for _, _, files in os.walk(directory):
            count += len(files)

        return count


if __name__ == "__main__":
    print("FileManager test")
    print("-" * 40)

    test_path = "example.jpg"

    print(
        "Filename:",
        FileManager.get_filename(test_path)
    )

    print(
        "Filename without extension:",
        FileManager.get_filename_without_extension(
            test_path
        )
    )

    print(
        "Extension:",
        FileManager.get_extension(test_path)
    )

    print(
        "Supported image:",
        FileManager.is_supported_image(test_path)
    )

    print(
        "Normalized path:",
        FileManager.normalize_path(test_path)
    )

    print(
        "Unique path:",
        FileManager.get_unique_path(test_path)
    )

    print(
        "Supported extensions:",
        FileManager.get_supported_extensions()
    )import os
import shutil
from typing import List, Optional, Tuple


class FileManager:
    """
    Utility class for file and directory operations used by
    the Image Compressor application.
    """

    SUPPORTED_IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tiff",
        ".tif"
    }

    # ------------------------------------------------------------------
    # Path Operations
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize and return an absolute path.
        """
        if not path:
            return ""

        return os.path.abspath(
            os.path.normpath(path)
        )

    @staticmethod
    def get_directory(path: str) -> str:
        """
        Return the directory portion of a path.
        """
        if not path:
            return ""

        return os.path.dirname(
            FileManager.normalize_path(path)
        )

    @staticmethod
    def get_filename(path: str) -> str:
        """
        Return filename including extension.
        """
        if not path:
            return ""

        return os.path.basename(path)

    @staticmethod
    def get_filename_without_extension(path: str) -> str:
        """
        Return filename without extension.
        """
        if not path:
            return ""

        filename = os.path.basename(path)

        return os.path.splitext(
            filename
        )[0]

    @staticmethod
    def get_extension(path: str) -> str:
        """
        Return file extension including the dot.
        """
        if not path:
            return ""

        return os.path.splitext(path)[1].lower()

    # ------------------------------------------------------------------
    # Existence Checks
    # ------------------------------------------------------------------

    @staticmethod
    def exists(path: str) -> bool:
        """
        Check whether a path exists.
        """
        return bool(
            path and os.path.exists(path)
        )

    @staticmethod
    def is_file(path: str) -> bool:
        """
        Check whether path is a file.
        """
        return bool(
            path and os.path.isfile(path)
        )

    @staticmethod
    def is_directory(path: str) -> bool:
        """
        Check whether path is a directory.
        """
        return bool(
            path and os.path.isdir(path)
        )

    # ------------------------------------------------------------------
    # Directory Operations
    # ------------------------------------------------------------------

    @staticmethod
    def create_directory(
        directory: str
    ) -> bool:
        """
        Create a directory recursively.
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

    @staticmethod
    def create_parent_directory(
        file_path: str
    ) -> bool:
        """
        Create the parent directory of a file.
        """
        if not file_path:
            return False

        directory = os.path.dirname(
            FileManager.normalize_path(file_path)
        )

        if not directory:
            return True

        return FileManager.create_directory(
            directory
        )

    @staticmethod
    def list_directory(
        directory: str,
        include_files: bool = True,
        include_directories: bool = False
    ) -> List[str]:
        """
        List items inside a directory.

        Returns full paths.
        """
        if not FileManager.is_directory(directory):
            return []

        results = []

        try:
            for item in os.listdir(directory):

                full_path = os.path.join(
                    directory,
                    item
                )

                if os.path.isfile(full_path):
                    if include_files:
                        results.append(full_path)

                elif os.path.isdir(full_path):
                    if include_directories:
                        results.append(full_path)

        except OSError:
            return []

        return sorted(results)

    # ------------------------------------------------------------------
    # File Operations
    # ------------------------------------------------------------------

    @staticmethod
    def copy_file(
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> bool:
        """
        Copy a file to another location.
        """
        if not FileManager.is_file(source):
            return False

        if (
            FileManager.exists(destination)
            and not overwrite
        ):
            return False

        if not FileManager.create_parent_directory(
            destination
        ):
            return False

        try:
            shutil.copy2(
                source,
                destination
            )
            return True

        except OSError:
            return False

    @staticmethod
    def move_file(
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> bool:
        """
        Move a file to another location.
        """
        if not FileManager.is_file(source):
            return False

        if (
            FileManager.exists(destination)
            and not overwrite
        ):
            return False

        if not FileManager.create_parent_directory(
            destination
        ):
            return False

        try:
            if overwrite and os.path.exists(destination):
                os.remove(destination)

            shutil.move(
                source,
                destination
            )

            return True

        except OSError:
            return False

    @staticmethod
    def delete_file(
        file_path: str
    ) -> bool:
        """
        Delete a file.
        """
        if not FileManager.is_file(file_path):
            return False

        try:
            os.remove(file_path)
            return True

        except OSError:
            return False

    @staticmethod
    def rename_file(
        file_path: str,
        new_name: str,
        overwrite: bool = False
    ) -> Optional[str]:
        """
        Rename a file.

        Returns:
            New path when successful, otherwise None.
        """
        if not FileManager.is_file(file_path):
            return None

        if not new_name:
            return None

        directory = FileManager.get_directory(
            file_path
        )

        destination = os.path.join(
            directory,
            new_name
        )

        if (
            FileManager.exists(destination)
            and not overwrite
        ):
            return None

        try:
            if overwrite and os.path.exists(destination):
                os.remove(destination)

            os.rename(
                file_path,
                destination
            )

            return destination

        except OSError:
            return None

    # ------------------------------------------------------------------
    # Unique File Names
    # ------------------------------------------------------------------

    @staticmethod
    def get_unique_path(
        file_path: str
    ) -> str:
        """
        Return a unique path without overwriting existing files.

        Example:
            image.jpg
            image_1.jpg
            image_2.jpg
        """
        if not file_path:
            return ""

        if not FileManager.exists(file_path):
            return file_path

        directory = FileManager.get_directory(
            file_path
        )

        filename = (
            FileManager.get_filename_without_extension(
                file_path
            )
        )

        extension = FileManager.get_extension(
            file_path
        )

        counter = 1

        while True:
            candidate = os.path.join(
                directory,
                f"{filename}_{counter}{extension}"
            )

            if not FileManager.exists(candidate):
                return candidate

            counter += 1

    # ------------------------------------------------------------------
    # Image File Operations
    # ------------------------------------------------------------------

    @staticmethod
    def is_supported_image(
        file_path: str
    ) -> bool:
        """
        Check whether a file has a supported image extension.
        """
        extension = FileManager.get_extension(
            file_path
        )

        return (
            extension
            in FileManager.SUPPORTED_IMAGE_EXTENSIONS
        )

    @staticmethod
    def get_image_files(
        directory: str,
        recursive: bool = False
    ) -> List[str]:
        """
        Return image files from a directory.
        """
        if not FileManager.is_directory(directory):
            return []

        results = []

        if recursive:

            for root, _, files in os.walk(directory):

                for filename in files:

                    full_path = os.path.join(
                        root,
                        filename
                    )

                    if FileManager.is_supported_image(
                        full_path
                    ):
                        results.append(full_path)

        else:

            for filename in os.listdir(directory):

                full_path = os.path.join(
                    directory,
                    filename
                )

                if (
                    os.path.isfile(full_path)
                    and FileManager.is_supported_image(
                        full_path
                    )
                ):
                    results.append(full_path)

        return sorted(results)

    @staticmethod
    def get_image_files_from_paths(
        paths: List[str]
    ) -> List[str]:
        """
        Filter a list of paths and return valid image files.
        """
        if not paths:
            return []

        return [
            path
            for path in paths
            if FileManager.is_file(path)
            and FileManager.is_supported_image(path)
        ]

    # ------------------------------------------------------------------
    # File Information
    # ------------------------------------------------------------------

    @staticmethod
    def get_file_size(
        file_path: str
    ) -> int:
        """
        Return file size in bytes.
        """
        if not FileManager.is_file(file_path):
            return 0

        try:
            return os.path.getsize(
                file_path
            )

        except OSError:
            return 0

    @staticmethod
    def get_file_info(
        file_path: str
    ) -> dict:
        """
        Return basic information about a file.
        """
        if not FileManager.is_file(file_path):
            return {}

        try:
            stat = os.stat(file_path)

            return {
                "path": FileManager.normalize_path(
                    file_path
                ),
                "filename": FileManager.get_filename(
                    file_path
                ),
                "extension": FileManager.get_extension(
                    file_path
                ),
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "is_image": FileManager.is_supported_image(
                    file_path
                )
            }

        except OSError:
            return {}

    # ------------------------------------------------------------------
    # File Validation
    # ------------------------------------------------------------------

    @staticmethod
    def validate_input_file(
        file_path: str
    ) -> Tuple[bool, str]:
        """
        Validate an image input file.

        Returns:
            (success, message)
        """
        if not file_path:
            return False, "No file path provided."

        if not FileManager.exists(file_path):
            return False, "File does not exist."

        if not FileManager.is_file(file_path):
            return False, "Path is not a file."

        if not FileManager.is_supported_image(file_path):
            return False, "Unsupported image format."

        if FileManager.get_file_size(file_path) <= 0:
            return False, "File is empty."

        return True, "File is valid."

    # ------------------------------------------------------------------
    # Batch Operations
    # ------------------------------------------------------------------

    @staticmethod
    def copy_files(
        files: List[str],
        output_directory: str,
        overwrite: bool = False
    ) -> dict:
        """
        Copy multiple files to a directory.

        Returns operation statistics.
        """
        result = {
            "total": len(files),
            "successful": 0,
            "failed": 0,
            "files": []
        }

        if not FileManager.create_directory(
            output_directory
        ):
            result["failed"] = len(files)
            return result

        for source in files:

            if not FileManager.is_file(source):
                result["failed"] += 1

                result["files"].append({
                    "source": source,
                    "success": False,
                    "destination": None
                })

                continue

            destination = os.path.join(
                output_directory,
                FileManager.get_filename(source)
            )

            if not overwrite:
                destination = FileManager.get_unique_path(
                    destination
                )

            success = FileManager.copy_file(
                source,
                destination,
                overwrite=overwrite
            )

            if success:
                result["successful"] += 1
            else:
                result["failed"] += 1

            result["files"].append({
                "source": source,
                "success": success,
                "destination": destination
            })

        return result

    # ------------------------------------------------------------------
    # Temporary / Cleanup Operations
    # ------------------------------------------------------------------

    @staticmethod
    def clear_directory(
        directory: str
    ) -> bool:
        """
        Remove all files and subdirectories inside a directory.
        The directory itself is preserved.
        """
        if not FileManager.is_directory(directory):
            return False

        try:
            for item in os.listdir(directory):

                path = os.path.join(
                    directory,
                    item
                )

                if os.path.isdir(path):
                    shutil.rmtree(path)

                else:
                    os.remove(path)

            return True

        except OSError:
            return False

    @staticmethod
    def delete_directory(
        directory: str
    ) -> bool:
        """
        Delete a directory and all its contents.
        """
        if not FileManager.is_directory(directory):
            return False

        try:
            shutil.rmtree(directory)
            return True

        except OSError:
            return False

    # ------------------------------------------------------------------
    # Path Generation
    # ------------------------------------------------------------------

    @staticmethod
    def build_path(
        directory: str,
        filename: str
    ) -> str:
        """
        Safely combine directory and filename.
        """
        if not directory:
            return filename

        if not filename:
            return directory

        return os.path.join(
            directory,
            filename
        )

    @staticmethod
    def change_extension(
        file_path: str,
        new_extension: str
    ) -> str:
        """
        Change the extension of a file path.

        Example:
            image.jpg -> image.webp
        """
        if not file_path or not new_extension:
            return file_path

        if not new_extension.startswith("."):
            new_extension = "." + new_extension

        base = os.path.splitext(
            file_path
        )[0]

        return base + new_extension.lower()

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    @staticmethod
    def get_supported_extensions() -> List[str]:
        """
        Return supported image extensions.
        """
        return sorted(
            FileManager.SUPPORTED_IMAGE_EXTENSIONS
        )

    @staticmethod
    def count_files(
        directory: str,
        images_only: bool = False,
        recursive: bool = False
    ) -> int:
        """
        Count files in a directory.
        """
        if images_only:
            return len(
                FileManager.get_image_files(
                    directory,
                    recursive=recursive
                )
            )

        if not FileManager.is_directory(directory):
            return 0

        if not recursive:
            return len([
                item
                for item in os.listdir(directory)
                if os.path.isfile(
                    os.path.join(
                        directory,
                        item
                    )
                )
            ])

        count = 0

        for _, _, files in os.walk(directory):
            count += len(files)

        return count


if __name__ == "__main__":
    print("FileManager test")
    print("-" * 40)

    test_path = "example.jpg"

    print(
        "Filename:",
        FileManager.get_filename(test_path)
    )

    print(
        "Filename without extension:",
        FileManager.get_filename_without_extension(
            test_path
        )
    )

    print(
        "Extension:",
        FileManager.get_extension(test_path)
    )

    print(
        "Supported image:",
        FileManager.is_supported_image(test_path)
    )

    print(
        "Normalized path:",
        FileManager.normalize_path(test_path)
    )

    print(
        "Unique path:",
        FileManager.get_unique_path(test_path)
    )

    print(
        "Supported extensions:",
        FileManager.get_supported_extensions()
    )