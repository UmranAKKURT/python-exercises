import os
from PIL import Image


class ImageCompressor:

    SUPPORTED_FORMATS = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    )

    def __init__(self, keep_exif=True):
        self.keep_exif = keep_exif

    def compress(
            self,
            input_path,
            output_path,
            quality=80,
            target_format=None
    ):

        img = Image.open(input_path)

        exif = img.info.get("exif")

        extension = os.path.splitext(output_path)[1].lower()

        if target_format is not None:
            extension = target_format.lower()

        if img.mode in ("RGBA", "P") and extension in (
                ".jpg",
                ".jpeg"
        ):
            img = img.convert("RGB")

        save_kwargs = {
            "optimize": True,
            "quality": quality
        }

        if self.keep_exif and exif is not None:
            save_kwargs["exif"] = exif

        img.save(
            output_path,
            **save_kwargs
        )

        return {
            "original_size": os.path.getsize(input_path),
            "compressed_size": os.path.getsize(output_path)
        }

    def convert(
            self,
            input_path,
            output_path,
            quality=90
    ):

        img = Image.open(input_path)

        extension = os.path.splitext(output_path)[1].lower()

        if extension in (".jpg", ".jpeg"):

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

        img.save(
            output_path,
            optimize=True,
            quality=quality
        )

    def batch_compress(
            self,
            input_folder,
            output_folder,
            quality=80
    ):

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        results = []

        for file in os.listdir(input_folder):

            ext = os.path.splitext(file)[1].lower()

            if ext not in self.SUPPORTED_FORMATS:
                continue

            input_path = os.path.join(
                input_folder,
                file
            )

            output_path = os.path.join(
                output_folder,
                file
            )

            result = self.compress(
                input_path,
                output_path,
                quality
            )

            result["filename"] = file

            results.append(result)

        return results

    def smart_compress(
            self,
            input_path,
            output_path,
            target_size_kb=500
    ):

        low = 5
        high = 100

        best_quality = 80

        while low <= high:

            quality = (low + high) // 2

            self.compress(
                input_path,
                output_path,
                quality
            )

            size = os.path.getsize(
                output_path
            ) / 1024

            if size <= target_size_kb:

                best_quality = quality
                low = quality + 1

            else:

                high = quality - 1

        self.compress(
            input_path,
            output_path,
            best_quality
        )

        return best_quality

    @staticmethod
    def compression_ratio(
            original,
            compressed
    ):

        if original == 0:
            return 0

        return (
                (original - compressed)
                / original
        ) * 100

    @staticmethod
    def format_size(size):

        kb = size / 1024

        if kb < 1024:
            return f"{kb:.2f} KB"

        mb = kb / 1024

        return f"{mb:.2f} MB"