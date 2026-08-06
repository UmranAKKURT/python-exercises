import os
import sys

# src klasörünü Python yoluna ekliyoruz ki import hataları yaşanmasın
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.gui import ImageCompressorApp

if __name__ == "__main__":
    app = ImageCompressorApp()
    app.run()