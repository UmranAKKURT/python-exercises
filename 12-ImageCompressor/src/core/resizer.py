```python
import os

from PIL import Image


class ImageResizer:
    """
    Image resizing engine.

    Responsible only for changing image dimensions.

    Features:
        - Resize by percentage
        - Resize by width
        - Resize by height
        - Resize to exact dimensions
        - Keep aspect ratio
        - Prevent unnecessary upscaling
        - Batch resizing
    """

    SUPPORTED_FORMATS = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    )

    # ==========================================================
    # RESIZE BY PERCENTAGE
    # ==========================================================

    def resize_by_percent(
        self,
        input_path,
        output_path,
        percent,
        keep_aspect_ratio=True
    ):
        """
        Resize an image according to a percentage.

        Example:

            50%

        converts:

            4000 x 3000

        into:

            2000 x 1500
        """

        self._validate_input(
            input_path
        )

        percent = self._validate_percent(
            percent
        )

        with Image.open(
            input_path
        ) as image:

            original_size = image.size

            new_width = max(
                1,
                int(
                    image.width
                    * percent
                    / 100
                )
            )

            new_height = max(
                1,
                int(
                    image.height
                    * percent
                    / 100
                )
            )

            resized = self._resize(
                image,
                new_width,
                new_height
            )

            resized.save(
                output_path
            )

            return self._build_result(
                input_path=input_path,
                output_path=output_path,
                original_size=original_size,
                new_size=resized.size
            )

    # ==========================================================
    # RESIZE BY WIDTH
    # ==========================================================

    def resize_by_width(
        self,
        input_path,
        output_path,
        width
    ):
        """
        Resize image to a specific width while
        preserving the aspect ratio.
        """

        self._validate_input(
            input_path
        )

        width = self._validate_dimension(
            width,
            "width"
        )

        with Image.open(
            input_path
        ) as image:

            original_size = image.size

            ratio = (
                width
                / image.width
            )

            height = max(
                1,
                int(
                    image.height
                    * ratio
                )
            )

            resized = self._resize(
                image,
                width,
                height
            )

            resized.save(
                output_path
            )

            return self._build_result(
                input_path=input_path,
                output_path=output_path,
                original_size=original_size,
                new_size=resized.size
            )

    # ==========================================================
    # RESIZE BY HEIGHT
    # ==========================================================

    def resize_by_height(
        self,
        input_path,
        output_path,
        height
    ):
        """
        Resize image to a specific height while
        preserving the aspect ratio.
        """

        self._validate_input(
            input_path
        )

        height = self._validate_dimension(
            height,
            "height"
        )

        with Image.open(
            input_path
        ) as image:

            original_size = image.size

            ratio = (
                height
                / image.height
            )

            width = max(
                1,
                int(
                    image.width
                    * ratio
                )
            )

            resized = self._resize(
                image,
                width,
                height
            )

            resized.save(
                output_path
            )

            return self._build_result(
                input_path=input_path,
                output_path=output_path,
                original_size=original_size,
                new_size=resized.size
            )

    # ==========================================================
    # EXACT SIZE
    # ==========================================================

    def resize_exact(
        self,
        input_path,
        output_path,
        width,
        height
    ):
        """
        Resize an image to exact dimensions.

        Aspect ratio is not preserved.
        """

        self._validate_input(
            input_path
        )

        width = self._validate_dimension(
            width,
            "width"
        )

        height = self._validate_dimension(
            height,
            "height"
        )

        with Image.open(
            input_path
        ) as image:

            original_size = image.size

            resized = self._resize(
                image,
                width,
                height
            )

            resized.save(
                output_path
            )

            return self._build_result(
                input_path=input_path,
                output_path=output_path,
                original_size=original_size,
                new_size=resized.size
            )

    # ==========================================================
    # FIT INSIDE
    # ==========================================================

    def fit_inside(
        self,
        input_path,
        output_path,
        max_width,
        max_height
    ):
        """
        Resize an image so that it fits inside
        the specified maximum dimensions.

        Aspect ratio is preserved.

        Example:

            Original:
            4000 x 3000

            Maximum:
            1920 x 1080

            Result:
            1440 x 1080
        """

        self._validate_input(
            input_path
        )

        max_width = self._validate_dimension(
            max_width,
            "max_width"
        )

        max_height = self._validate_dimension(
            max_height,
            "max_height"
        )

        with Image.open(
            input_path
        ) as image:

            original_size = image.size

            image_copy = image.copy()

            image_copy.thumbnail(
                (
                    max_width,
                    max_height
                ),
                Image.Resampling.LANCZOS
            )

            image_copy.save(
                output_path
            )

            return self._build_result(
                input_path=input_path,
                output_path=output_path,
                original_size=original_size,
                new_size=image_copy.size
            )

    # ==========================================================
    # SMART RESIZE
    # ==========================================================

    def smart_resize(
        self,
        input_path,
        output_path,
        max_dimension=1920
    ):
        """
        Automatically resize large images.

        The largest dimension will not exceed
        max_dimension.

        Smaller images are not enlarged.
        """

        self._validate_input(
            input_path
        )

        max_dimension = self._validate_dimension(
            max_dimension,
            "max_dimension"
        )

        with Image.open(
            input_path
        ) as image:

            original_size = image.size

            largest_dimension = max(
                image.width,
                image.height
            )

            # --------------------------------------------------
            # Image is already small enough.
            # --------------------------------------------------

            if largest_dimension <= max_dimension:

                image_copy = image.copy()

                image_copy.save(
                    output_path
                )

                return self._build_result(
                    input_path=input_path,
                    output_path=output_path,
                    original_size=original_size,
                    new_size=image_copy.size
                )

            # --------------------------------------------------
            # Calculate proportional dimensions.
            # --------------------------------------------------

            ratio = (
                max_dimension
                / largest_dimension
            )

            new_width = max(
                1,
                int(
                    image.width
                    * ratio
                )
            )

            new_height = max(
                1,
                int(
                    image.height
                    * ratio
                )
            )

            resized = self._resize(
                image,
                new_width,
                new_height
            )

            resized.save(
                output_path
            )

            return self._build_result(
                input_path=input_path,
                output_path=output_path,
                original_size=original_size,
                new_size=resized.size
            )

    # ==========================================================
    # BATCH RESIZE
    # ==========================================================

    def batch_resize(
        self,
        input_folder,
        output_folder,
        percent=100
    ):
        """
        Resize all supported images in a folder.
        """

        if not os.path.isdir(
            input_folder
        ):

            raise ValueError(
                f"Input folder does not exist: "
                f"{input_folder}"
            )

        percent = self._validate_percent(
            percent
        )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        results = []

        for filename in os.listdir(
            input_folder
        ):

            input_path = os.path.join(
                input_folder,
                filename
            )

            if not os.path.isfile(
                input_path
            ):
                continue

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension not in (
                self.SUPPORTED_FORMATS
            ):
                continue

            output_path = os.path.join(
                output_folder,
                filename
            )

            output_path = (
                self._unique_output_path(
                    output_path
                )
            )

            try:

                result = self.resize_by_percent(
                    input_path=input_path,
                    output_path=output_path,
                    percent=percent
                )

                result["filename"] = filename
                result["success"] = True

                results.append(
                    result
                )

            except Exception as error:

                results.append({
                    "filename": filename,
                    "success": False,
                    "error": str(error)
                })

        return results

    # ==========================================================
    # INTERNAL RESIZE
    # ==========================================================

    @staticmethod
    def _resize(
        image,
        width,
        height
    ):
        """
        Perform high-quality resizing.
        """

        return image.resize(
            (
                width,
                height
            ),
            Image.Resampling.LANCZOS
        )

    # ==========================================================
    # RESULT
    # ==========================================================

    @staticmethod
    def _build_result(
        input_path,
        output_path,
        original_size,
        new_size
    ):
        """
        Build a standardized resize result.
        """

        original_width, original_height = (
            original_size
        )

        new_width, new_height = (
            new_size
        )

        return {
            "input_path": input_path,
            "output_path": output_path,

            "original_resolution": (
                original_size
            ),

            "new_resolution": (
                new_size
            ),

            "original_width": (
                original_width
            ),

            "original_height": (
                original_height
            ),

            "new_width": (
                new_width
            ),

            "new_height": (
                new_height
            ),

            "original_size": (
                os.path.getsize(
                    input_path
                )
            ),

            "new_size": (
                os.path.getsize(
                    output_path
                )
            )
        }

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def _validate_input(
        self,
        input_path
    ):
        """
        Validate input image.
        """

        if not input_path:

            raise ValueError(
                "Input path cannot be empty."
            )

        if not os.path.isfile(
            input_path
        ):

            raise FileNotFoundError(
                f"Input file not found: "
                f"{input_path}"
            )

        extension = os.path.splitext(
            input_path
        )[1].lower()

        if extension not in (
            self.SUPPORTED_FORMATS
        ):

            raise ValueError(
                f"Unsupported image format: "
                f"{extension}"
            )

    # ==========================================================
    # VALIDATE DIMENSION
    # ==========================================================

    @staticmethod
    def _validate_dimension(
        value,
        name
    ):
        """
        Validate image dimension.
        """

        try:

            value = int(
                value
            )

        except (
            ValueError,
            TypeError
        ):

            raise ValueError(
                f"{name} must be an integer."
            )

        if value <= 0:

            raise ValueError(
                f"{name} must be greater than 0."
            )

        return value

    # ==========================================================
    # VALIDATE PERCENT
    # ==========================================================

    @staticmethod
    def _validate_percent(
        percent
    ):
        """
        Validate resize percentage.
        """

        try:

            percent = float(
                percent
            )

        except (
            ValueError,
            TypeError
        ):

            raise ValueError(
                "Percent must be a number."
            )

        if percent <= 0:

            raise ValueError(
                "Percent must be greater than 0."
            )

        return percent

    # ==========================================================
    # UNIQUE OUTPUT PATH
    # ==========================================================

    @staticmethod
    def _unique_output_path(
        path
    ):
        """
        Prevent overwriting an existing file.
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

            new_filename = (
                f"{name}_{counter}"
                f"{extension}"
            )

            new_path = os.path.join(
                directory,
                new_filename
            )

            if not os.path.exists(
                new_path
            ):

                return new_path

            counter += 1
```
