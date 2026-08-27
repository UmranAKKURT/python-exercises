"""
Entry point for the ImageCompressor GUI package.

Allows the application to be started with:

    python -m src.gui
"""

from .app import ImageCompressorApp


def main():
    """
    Start the ImageCompressor GUI application.
    """

    app = ImageCompressorApp()

    app.run()


if __name__ == "__main__":
    main()